from typing import cast

import bpy

from ..infra.airtable import AirtableInterface, AirtableRecord, AirtableFields

from .data_funcs import prepare_data_record
from ..registry import register_class
from ..preferences.prefs import get_pref_value

@register_class
class Slicer_AirtableOperator(bpy.types.Operator):
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