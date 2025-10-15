from bpy.types import AddonPreferences
import bpy
from ..registry import register_class
from .. import PACKAGE

try:
    from .. import constants
except ImportError:
    class _Fallback:
        AT_PAT = ""
        AT_BASE_ID = ""
        AT_ORDERS_TABLE_ID = ""
    constants = _Fallback()


@register_class
class Slicer_AirtablePreferences(AddonPreferences):
    bl_idname = PACKAGE

    airtable_pat: bpy.props.StringProperty(
        name="Airtable PAT", default=getattr(constants, "AT_PAT", "")
    )  # type: ignore
    airtable_base: bpy.props.StringProperty(
        name="Airtable Base", default=getattr(constants, "AT_BASE_ID", "")
    )  # type: ignore
    orders_table: bpy.props.StringProperty(
        name="Orders table ID", default=getattr(constants, "AT_ORDERS_TABLE_ID", "")
    )  # type: ignore

    def draw(self, context):
        layout = self.layout
        for prop in ("airtable_pat", "airtable_base", "orders_table"):
            layout.prop(self, prop)


def get_pref_value(key: str):
    assert bpy.context.preferences
    prefs = bpy.context.preferences.addons[PACKAGE].preferences
    return getattr(prefs, key, "")
