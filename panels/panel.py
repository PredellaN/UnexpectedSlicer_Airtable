import bpy
import re

from ..registry import register_class
from .. import TYPES_NAME

from ..functions.blender_funcs import coll_from_selection
from ..functions.data_funcs import prepare_data

@register_class
class SlicerPanel(bpy.types.Panel):
    bl_label = "UnexpectedSlicer to Airtable"
    bl_idname = f"COLLECTION_PT_{TYPES_NAME}"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "collection"

    def draw(self, context):
        layout = self.layout

        coll = coll_from_selection()
        pg = getattr(coll, TYPES_NAME)

        row= layout.row()
        row.operator('collection.slicer_to_airtable')

        row = layout.row()
        row.prop(pg, 'customer_name', text="Customer Name")

        _, ds = prepare_data()

        for k, d in ds.items():
            row = layout.row()
            row.label(text=f"{k}: {d}")

        pass