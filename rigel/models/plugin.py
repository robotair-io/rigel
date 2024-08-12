from pydantic import BaseModel, Extra, Field
from typing import Any, Dict

PluginRawData = Dict[str, Any]


class PluginDataModel(BaseModel, extra=Extra.forbid):

    """
    Defines a data model for storing plugin-related information. It inherits from
    `BaseModel` and forbids extra attributes. The model consists of two properties:
    `plugin`, which is a string, and `with_`, an alias for `PluginRawData` field.

    Attributes:
        plugin (str): A required field, meaning it cannot be omitted when creating
            an instance of this model.
        with_ (PluginRawData): Aliased as 'with'. It is not directly assigned a
            value, instead it uses the `Field(..., alias='with')` syntax to create
            a field.

    """
    plugin: str
    with_: PluginRawData = Field(..., alias='with')
