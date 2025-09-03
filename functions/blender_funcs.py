from bpy.types import Collection, Scene
from bpy.types import LayerCollection
import bpy

def coll_from_selection() -> Collection | None:
    for obj in bpy.context.selected_objects:
        return obj.users_collection[0]
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

def get_collection_parents(target_collection: Collection) -> list[Collection] | None:
    scene: Scene = bpy.context.scene #type: ignore

    def recursive_find(coll: Collection, path: list[Collection]) -> list[Collection] | None:
        if coll == target_collection:
            return path + [coll]
        for child in coll.children:
            result: list[Collection] | None = recursive_find(coll=child, path=path + [coll])
            if result is not None:
                return result
        return None

    return recursive_find(coll=scene.collection, path=[])

def get_inherited_prop(pg_name, coll_hierarchy, attr, conf_type = None):
    res = {}
    is_set = False
    config = ''
    source: None | int = None
    for idx, coll in enumerate(coll_hierarchy):
        pg = getattr(coll, pg_name)
        config: str = getattr(pg, attr, '')
        if config:
            is_set = True
            source = idx
            res['prop'] = config

    final_index = len(coll_hierarchy) - 1
    res['inherited'] = is_set and not (source == final_index)

    if conf_type:
        res['type'] = conf_type

    return res

def get_inherited_slicing_props(cx, pg_name) -> dict[str, [str, bool]]:
    result: dict[str, [str, bool]] = {}
    conf_map: list[tuple[str, str]] = [('printer_config_file', 'printer')]

    coll_hierarchy: list[Collection] | None = get_collection_parents(target_collection=cx)

    printer: dict[str, str] = get_inherited_prop(pg_name, coll_hierarchy, 'printer_config_file')
    
    for i in ['','_2','_3','_4','_5'][:5]:
        key: str = f'filament{i}_config_file'
        conf_map.append((key, 'filament'))
    
    conf_map.append(('print_config_file', 'print'))
    
    if not coll_hierarchy:
        return result
    
    for attr, conf_type in conf_map:
        result[attr] = get_inherited_prop(pg_name, coll_hierarchy, attr, conf_type)
    
    return result