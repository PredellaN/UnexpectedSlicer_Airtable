import bpy

from ..registry import register_class
from .. import PACKAGE
from .. import constants

@register_class
class Slicer_AirtablePreferences(bpy.types.AddonPreferences):
    bl_idname = PACKAGE

    airtable_pat: bpy.props.StringProperty(name='Airtable PAT', default=constants.AT_PAT) #type: ignore
    airtable_base: bpy.props.StringProperty(name='Airtable Base', default=constants.AT_BASE_ID) #type: ignore
    orders_table: bpy.props.StringProperty(name='Orders table ID', default=constants.AT_ORDERS_TABLE_ID) #type: ignore

    def draw(self, context):
        layout = self.layout
        layout.label(text='Settings:')
        layout.prop(self, "airtable_pat")
        layout.prop(self, "airtable_base")
        layout.prop(self, "orders_table")