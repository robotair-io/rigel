from pydantic import BaseModel, Extra, Field
from typing import Any, Dict

ProviderRawData = Dict[str, Any]


class ProviderDataModel(BaseModel, extra=Extra.forbid):

    """
    Validates and defines a data model for storing provider information. It inherits
    from `BaseModel`, which provides validation capabilities. The class has two
    attributes: `provider`, a string field, and `with_`, an alias of `ProviderRawData`
    that is not allowed to have extra values.

    Attributes:
        provider (str): A required field, meaning that it must be provided when
            creating or updating instances of this model.
        with_ (ProviderRawData): Aliased as 'with'. The ellipsis (...) in its
            definition indicates that it is a required field, but no value is provided.

    """
    provider: str
    with_: ProviderRawData = Field(..., alias='with')
