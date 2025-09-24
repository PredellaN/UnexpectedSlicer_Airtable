from datetime import timezone
from pathlib import Path
import requests, base64, mimetypes, os, time

from .network_funcs import measure_performance

from typing import Callable, TypeAlias, TypeVar, Any
F = TypeVar('F', bound=Callable[..., Any])

from typing import TypedDict, Any

AirtableFields: TypeAlias = dict[str, Any]

class AirtableRecord(TypedDict):
    id: str
    fields: AirtableFields

class AirtableInterface:
    def __init__(self, pat: str, log_base_id: str | None = None, log_table_id: str | None = None) -> None:
        self.pat: str = pat
        self.log_base_id: str | None = log_base_id
        self.log_table_id: str | None = log_table_id

    @measure_performance
    def fetch(self, base_id: str, table_id: str, view: str|None = None, filterByFormula: str | None =None, fields : list[str] = []) -> dict[Any, Any]:
        url = f"https://api.airtable.com/v0/{base_id}/{table_id}"
            
        headers = {"Authorization": f"Bearer {self.pat}"}

        records = {}
        offset = None

        while True:
            params = {}
            if offset:
                params["offset"] = offset
            if view:
                params["view"] = view
            if filterByFormula:
                params["filterByFormula"] = filterByFormula
            if len(fields):
                params["fields[]"] = fields

            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()
            for record in data.get("records", []):
                records[record['id']] = record

            offset = data.get("offset")
            if not offset:
                break

        return records

    @measure_performance
    def fetch_record_by_id(self, base_id: str, table_name: str, record_id: str):
        url = f"https://api.airtable.com/v0/{base_id}/{table_name}/{record_id}"
        headers = {
            "Authorization": f"Bearer {self.pat}",
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        record = response.json()
        return record

    @measure_performance
    def update_records(self, base_id: str, table_name: str, records: list[AirtableRecord],
                                typecast: bool=False, returnFieldsByFieldId: bool=False) -> list[dict[Any, Any]]:
        url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
        headers = {
            "Authorization": f"Bearer {self.pat}",
            "Content-Type": "application/json"
        }

        all_results = []
        
        for i in range(0, len(records), 10):
            batch = records[i:i+10]
            payload = {
                "records": batch,
                "typecast": typecast,
                "returnFieldsByFieldId": returnFieldsByFieldId,
            }
            
            response = requests.patch(url, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()
            all_results += result['records']
            
            time.sleep(1)

        return all_results

    @measure_performance
    def upsert_records(self, base_id: str, table_name: str, records: list[AirtableFields], fieldsToMergeOn: list[str] | None = None,
                                typecast: bool=False, returnFieldsByFieldId: bool=False) -> list[dict[Any, Any]]:
        url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
        headers = {
            "Authorization": f"Bearer {self.pat}",
            "Content-Type": "application/json"
        }

        all_results = []
        
        for i in range(0, len(records), 10):
            batch = records[i:i+10]
            payload = {
                "records": [{'fields': r} for r in batch],
                "typecast": typecast,
                "returnFieldsByFieldId": returnFieldsByFieldId,
            }
            if fieldsToMergeOn: payload['performUpsert'] = {
                    "fieldsToMergeOn": fieldsToMergeOn
                }
            
            response = requests.patch(url, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()
            all_results += result['records']
            
            time.sleep(1)

        return all_results

    @measure_performance
    def create_record(self, base_id: str, table_name: str, fields: AirtableFields):
        url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
        headers = {
            "Authorization": f"Bearer {self.pat}",
            "Content-Type": "application/json"
        }
        payload = {"fields": fields}

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        record = response.json()
        return record

    @measure_performance
    def upload_attachment(self, base_id: str, record_id: str, field_id: str, filepath: str | Path):
        url = f"https://content.airtable.com/v0/{base_id}/{record_id}/{field_id}/uploadAttachment"
        headers = {
            "Authorization": f"Bearer {self.pat}",
            "Content-Type": "application/json"
        }
        with open(filepath, "rb") as f:
            file_data = f.read()
        content_type, _ = mimetypes.guess_type(filepath)
        if content_type is None:
            content_type = "application/octet-stream"
        encoded_file = base64.b64encode(file_data).decode("utf-8")

        payload = {
            "contentType": content_type,
            "file": encoded_file,
            "filename": os.path.basename(filepath),
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        return response.json()

    @measure_performance
    def delete_attachment(self, base_id: str, record_id: str, field_id: str, attachment_id: str):
        url = f"https://content.airtable.com/v0/{base_id}/{record_id}/{field_id}/{attachment_id}"
        headers = {
            "Authorization": f"Bearer {self.pat}"
        }

        response = requests.delete(url, headers=headers)
        response.raise_for_status()

        return response.json()

    def _log_execution(self, log_key: str, time_delta: float = 0, error: str = '') -> None:
        if not self.log_base_id or not self.log_table_id: return
        
        import datetime

        self.upsert_records(self.log_base_id, self.log_table_id, [{
            'Name': log_key,
            'Last Run': datetime.datetime.now(timezone.utc).isoformat(),
            'Next Run': (datetime.datetime.now(timezone.utc) + datetime.timedelta(minutes=time_delta)).isoformat() if time_delta else '',
            'Error Log': error if error else 'OK',
        }], ['Name'])

    def with_log(self, log_key: str, time_delta: float = 0) -> Callable[[F], F]:
        import functools
        def decorator(func: F) -> F:
            @functools.wraps(func)
            def wrapper(*args: dict[Any, Any], **kwargs: dict[Any, Any]) -> Any:
                try:
                    res = func(*args, **kwargs)
                    self._log_execution(log_key, time_delta)
                    return res
                except Exception:
                    import traceback
                    full_trace = traceback.format_exc()
                    self._log_execution(log_key, time_delta, error=str(full_trace))
                    raise
            return wrapper # type: ignore
        return decorator