import bpy

from ..registry import register_class
from .. import TYPES_NAME

from ..infra.blender_bridge import coll_from_selection
from ..functions.data_funcs import prepare_data_record

@register_class
class SlicerPanel(bpy.types.Panel):
    bl_label = "UnexpectedSlicer to Airtable"
    bl_idname = f"COLLECTION_PT_{TYPES_NAME}"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "collection"

    def draw(self, context) -> None:
        layout = self.layout
        if not layout: return

        coll = coll_from_selection()
        pg = getattr(coll, TYPES_NAME)

        row= layout.row()
        row.operator('collection.slicer_to_airtable')

        row= layout.row()
        row.operator('collection.airtable_stl_to_blender')

        row = layout.row()
        row.prop(pg, 'customer_name', text="Customer Name")
        row = layout.row()
        row.prop(pg, 'order_record_id', text="Order Record ID")
        pass