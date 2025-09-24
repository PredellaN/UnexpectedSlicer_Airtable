import bpy
from .registry import register_class

@register_class
class Slicer_AirtablePropertyGroup(bpy.types.PropertyGroup):
    customer_name: bpy.props.StringProperty() #type: ignore
    order_record_id: bpy.props.StringProperty() #type: ignore