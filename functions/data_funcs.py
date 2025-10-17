from typing import Any
import bpy
import re

from ..infra.blender_bridge import coll_from_selection, selected_top_level_objects
from .. import TYPES_NAME, US_TYPE_NAME

def prepare_data_record() -> tuple[str, dict[str, Any]]:
    coll = coll_from_selection()
    pg = getattr(coll, TYPES_NAME, None)
    pg_us = getattr(coll, US_TYPE_NAME, None)

    ao = bpy.context.active_object
    if ao is None or pg is None or pg_us is None:
        return "", {}

    def parse_weight(s: str) -> float:
        try:
            return round(sum(float(p.strip() or 0) for p in s.split(",")), 2)
        except Exception:
            return 0.0

    def time_to_hours(s: str) -> float:
        if not s:
            return 0.0
        matches = re.findall(r"(\d+)([hms])", s)
        factors = {"h": 1.0, "m": 1.0 / 60, "s": 1.0 / 3600}
        return round(sum(int(v) * factors.get(u, 0) for v, u in matches), 2)

    fp = bpy.data.filepath or ""
    i = fp.find("MOS-Project-Files")
    path = fp[i:] if i != -1 else ""

    printer = getattr(pg_us, 'printer_config_file')

    metadata = {
        "Customer": getattr(pg, "customer_name", ""),
        "Part ID / Name": ao.name.split(".")[0],
        "Weight per print": parse_weight(getattr(pg_us, "print_weight", "")),
        "Time per print": time_to_hours(getattr(pg_us, "print_time", "")),
        "Parts per print": len(selected_top_level_objects()),
        "Printer Profile": pg_us['preview_data']['config']['printer_settings_id'],
        "Notes": path,
        "GCODE": [],
    }

    fields: dict[str, Any] = {k: v for k, v in metadata.items() if v is not None and v != ""}

    record: dict[str, Any] = {'fields': fields}

    if id := getattr(pg, "order_record_id", ""): record['id'] = id

    filepath = getattr(pg_us, "print_gcode", "")

    return filepath, record