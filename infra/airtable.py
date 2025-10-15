from datetime import timezone
from pathlib import Path
import requests, base64, mimetypes, os, time

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

    def fetch_record_by_id(self, base_id: str, table_name: str, record_id: str):
        url = f"https://api.airtable.com/v0/{base_id}/{table_name}/{record_id}"
        headers = {
            "Authorization": f"Bearer {self.pat}",
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        record = response.json()
        return record

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