import bpy, os

### Constants
ADDON_FOLDER = os.path.dirname(os.path.abspath(__file__))
PG_NAME = "UnexpectedSlicer_Airtable"
TYPES_NAME = "unexpectedslicer_airtable"
US_TYPE_NAME = "blendertoprusaslicer"
PACKAGE: str = __package__ or "unexpectedslicer_airtable"

### Blender Addon Initialization
bl_info = {
    "name" : "UnexpectedSlicer_Airtable",
    "author" : "Nicolas Predella",
    "description" : "PrusaSlicer Airtable integration",
    "blender" : (4, 2, 0),
    "version" : (1, 0, 0),  
    "location" : "",
    "warning" : "",
}

### Initialization
from .preferences import prefs
from . import property_groups
from .panels import panel
from .functions import operators

### Load collected modules
from . import registry
modules = registry.get()
timers = registry.get_timers()

def register():
    registry.blender_register_classes()

    bpy.types.Collection.unexpectedslicer_airtable = bpy.props.PointerProperty(type=property_groups.Slicer_AirtablePropertyGroup, name=TYPES_NAME) #type: ignore

def unregister():
    registry.blender_unregister_classes()

    del bpy.types.Collection.unexpectedslicer_airtable #type: ignore

if __name__ == "__main__":
    register()