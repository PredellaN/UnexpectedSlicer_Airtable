from typing import cast

import bpy

from ..infra.airtable import AirtableInterface, AirtableRecord

from .data_funcs import prepare_data_record
from ..registry import register_class
from ..preferences.prefs import get_pref_value
from .. import TYPES_NAME

@register_class
class Slicer_AirtableSubmitOperator(bpy.types.Operator):
    bl_idname = "collection.slicer_to_airtable"
    bl_label = "Send data to Airtable"

    def execute(self, context) -> set[str]: #type: ignore
        print_gcode, record = prepare_data_record()

        airtable = AirtableInterface(get_pref_value('airtable_pat'))

        base_id=get_pref_value('airtable_base')
        table_name=get_pref_value('orders_table')

        if record.get('id'):
            match = airtable.fetch(base_id, table_name, filterByFormula=f"ID = {record['id']}", fields=['ID', 'Record ID'])

            if not match: return {'CANCELED'}

            record['id'] = list(match)[0]
            res = airtable.update_records(
                base_id, table_name,
                records=[cast(AirtableRecord, record)],
            )
            record_id = record['id']
        else:
            res = airtable.create_record(
                base_id, table_name,
                fields=record['fields']
            )
            record_id = res['id']
        

        _ = airtable.upload_attachment(
            base_id=get_pref_value('airtable_base'),
            record_id=record_id,
            field_id='GCODE',
            filepath=print_gcode
        )  

        return {'FINISHED'}

@register_class
class Slicer_AirtableGetSTLOperator(bpy.types.Operator):
    bl_idname = "collection.airtable_stl_to_blender"
    bl_label = "Get STL from Airtable"

    def execute(self, context) -> set[str]: #type: ignore
        from ..infra.blender_bridge import coll_from_selection

        airtable = AirtableInterface(get_pref_value('airtable_pat'))
        coll = coll_from_selection()
        pg = getattr(coll, TYPES_NAME, None)

        if not (id := getattr(pg, "order_record_id", "")): return {'CANCELED'}

        base_id=get_pref_value('airtable_base')
        table_name=get_pref_value('orders_table')

        match = airtable.fetch(base_id, table_name, filterByFormula=f"ID = {id}", fields=['MODEL'])

        record = match[list(match)[0]]
        model = record['fields']['MODEL'][0]

        import requests, tempfile, pathlib
        with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp_file:
            with requests.get(model['url'], stream=True) as r:
                r.raise_for_status()
                for chunk in r.iter_content(chunk_size=8192):
                    tmp_file.write(chunk)

            stl_path: str = tmp_file.name

            assert bpy.context.scene
            cursor_loc = bpy.context.scene.cursor.location.copy()
            before = set(bpy.data.objects)

            bpy.ops.wm.stl_import(filepath=stl_path, global_scale=0.001)

            new_objs = [o for o in bpy.data.objects if o not in before]
            for o in new_objs:
                o.name = pathlib.Path(model['filename']).stem
                o.location = cursor_loc

            if new_objs:
                assert bpy.context.view_layer
                bpy.context.view_layer.objects.active = new_objs[0]

        return {'FINISHED'}