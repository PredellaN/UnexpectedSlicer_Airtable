from bpy.types import Collection, Scene
from bpy.types import LayerCollection
import bpy

def coll_from_selection() -> Collection | None:
    for obj in bpy.context.selected_objects:
        return obj.users_collection[0]
    if not bpy.context.view_layer: return None
    active_layer_collection: LayerCollection | None = bpy.context.view_layer.active_layer_collection
    cx: Collection | None = active_layer_collection.collection if active_layer_collection else None
    
    return cx

def selected_top_level_objects():
    selected = bpy.context.selected_objects
    top_level_objects = []

    for obj in selected:
        if obj.parent is None or obj.parent not in selected:
            top_level_objects += [obj]

    return top_level_objects