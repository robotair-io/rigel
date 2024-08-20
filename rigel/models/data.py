from pydantic import BaseModel, Extra, Field
from typing import Any, Dict, Union

SimpleDataModel = Union[bool, float, int, str]


class ComplexDataModel(BaseModel, extra=Extra.forbid):

    """
    Defines a data model that inherits from `BaseModel`. It has two attributes:
    `type` (a string) and `with_` (a dictionary with any value type, aliased as
    'with'). The `extra=Extra.forbid` parameter indicates that additional fields
    are not allowed.

    Attributes:
        type (str): Defined as part of the model's schema. It represents a string
            value that characterizes the type of data being modeled.
        with_ (Dict[str, Any]): Aliased as 'with'. The `Field` constructor is used
            to define this attribute with a default value of ... which implies
            that it is required.

    """
    type: str
    with_: Dict[str, Any] = Field(..., alias='with')
