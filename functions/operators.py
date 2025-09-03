import bpy

from .data_funcs import prepare_data
from .airtable_funcs import airtable_create_record, airtable_upload_attachment

from ..registry import register_class
from .. import PACKAGE

@register_class
class Slicer_AirtableOperator(bpy.types.Operator):
    bl_idname = "collection.slicer_to_airtable"
    bl_label = "Send data to Airtable"

    def execute(self, context) -> set[str]: #type: ignore
        prefs = bpy.context.preferences.addons[PACKAGE].preferences #type: ignore
        print_gcode, metadata = prepare_data()

        res = airtable_create_record(
            prefs.airtable_base,
            prefs.orders_table,
            metadata
        )

        record_id = res['id']

        res2 = airtable_upload_attachment(
            prefs.airtable_base,
            record_id,
            'GCODE',
            print_gcode
        )  

        return {'FINISHED'}