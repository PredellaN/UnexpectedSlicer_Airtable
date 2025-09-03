from typing import Any

import bpy
import re

from .blender_funcs import coll_from_selection, selected_top_level_objects

from .. import TYPES_NAME, US_TYPE_NAME

def prepare_data() -> tuple[str, dict[str, Any]]:
    coll = coll_from_selection()
    pg = getattr(coll, TYPES_NAME)
    pg_us = getattr(coll, US_TYPE_NAME)

    # props = get_inherited_slicing_props(coll, US_TYPE_NAME)
    customer = getattr(pg, 'customer_name')
    # batch = getattr(pg, 'batch_name')

    #name
    name = getattr(bpy.context.active_object, 'name').split('.')[0]

    #weight
    weight = round(
    sum(
        float(p) if p.strip() else 0.0
        for p in getattr(pg_us, 'print_weight', '').split(',')
    ),
    2
)

    #time
    time = getattr(pg_us, 'print_time')
    if time:
        matches = re.findall(r'(\d+)([hms])', time)
        factors = {'h': 1, 'm': 1/60, 's': 1/3600}
        total_hours = round(sum(int(value) * factors[unit] for value, unit in matches), 2)
    else:
        total_hours = 0

    #count
    count = len(selected_top_level_objects())

    #notes-path
    path = bpy.data.filepath[bpy.data.filepath.find("MOS-Project-Files"):]
    if path == 'd': path = ''

    metadata = {
        'Customer': customer,
        'Part ID / Name': name,
        'Weight per print': weight,
        'Time per print': total_hours,
        'Parts per print': count,
        'Notes': path,
    }

    metadata = {k: v for k, v in metadata.items() if v}
    filepath = pg_us.print_gcode

    return filepath, metadata