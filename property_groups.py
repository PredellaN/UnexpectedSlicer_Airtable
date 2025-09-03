import bpy
from .registry import register_class

@register_class
class Slicer_AirtablePropertyGroup(bpy.types.PropertyGroup):
    customer_name: bpy.props.StringProperty() #type: ignore