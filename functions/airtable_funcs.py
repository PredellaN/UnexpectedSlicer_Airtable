from typing import Any


from pathlib import Path
import requests, base64, mimetypes, os, time

from ..constants import AT_PAT

def airtable_fetch(base_id: str, table_id: str, view: str|None = None, filterByFormula: str|None =None, fields : list[str] = []) -> dict[Any, Any]:
    url = f"https://api.airtable.com/v0/{base_id}/{table_id}"
        
    headers = {"Authorization": f"Bearer {AT_PAT}"}

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

        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.json()}")
            return {}

        data = response.json()
        for record in data.get("records", []):
            records[record['id']] = record

        offset = data.get("offset")
        if not offset:
            break

    return records

def airtable_fetch_record(base_id: str, table_name: str, record_id: str) -> dict[Any, Any]:
    url = f"https://api.airtable.com/v0/{base_id}/{table_name}/{record_id}"
    headers = {
        "Authorization": f"Bearer {AT_PAT}",
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.json()}")
        return {}

    record = response.json()
    return record

def airtable_update_record(base_id: str, table_name: str, record_id: str, fields: list[str]) -> dict[Any, Any]:
    url = f"https://api.airtable.com/v0/{base_id}/{table_name}/{record_id}"
    headers = {
        "Authorization": f"Bearer {AT_PAT}",
        "Content-Type": "application/json"
    }
    payload = {"fields": fields}

    response = requests.patch(url, headers=headers, json=payload)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.json()}")
        return {}

    record = response.json()
    return record

def airtable_upsert_records(base_id: str, table_name: str, records: list[dict[Any, Any]], fieldsToMergeOn: list[str],
                            typecast: bool = False, returnFieldsByFieldId: bool = False) -> list[dict[Any, Any]]:
    url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
    headers = {
        "Authorization": f"Bearer {AT_PAT}",
        "Content-Type": "application/json"
    }

    all_results = []
    
    for i in range(0, len(records), 10):
        batch = records[i:i+10]
        payload = {
            "records": [{'fields': r} for r in batch],
            "performUpsert": {
                "fieldsToMergeOn": fieldsToMergeOn
            },
            "typecast": typecast,
            "returnFieldsByFieldId": returnFieldsByFieldId,
        }
        
        response = requests.patch(url, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.json()}")
        else:
            result = response.json()
            all_results.append(result)
        
        time.sleep(1)

    return all_results

def airtable_create_record(base_id: str, table_name: str, fields: dict[str, str]) -> dict[Any, Any]:
    url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
    headers = {
        "Authorization": f"Bearer {AT_PAT}",
        "Content-Type": "application/json"
    }
    payload = {"fields": fields}

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.json()}")
        return {}

    record = response.json()
    return record

def airtable_upload_attachment(base_id: str, record_id: str, field_id: str, filepath: str | Path) -> dict[Any, Any]:
    url = f"https://content.airtable.com/v0/{base_id}/{record_id}/{field_id}/uploadAttachment"
    headers = {
        "Authorization": f"Bearer {AT_PAT}",
        "Content-Type": "application/json"
    }
    with open(filepath, "rb") as f:
        file_data = f.read()
    content_type, _ = mimetypes.guess_type(filepath)
    if not content_type:
        content_type = "application/octet-stream"
    encoded_file = base64.b64encode(file_data).decode("utf-8")

    payload: dict[str, str] = {
        "contentType": content_type,
        "file": encoded_file,
        "filename": os.path.basename(filepath),
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.json()}")
        return {}
    
    return response.json()