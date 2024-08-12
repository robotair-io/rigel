from pydantic import BaseModel, validator
from rigel.exceptions import InvalidPluginNameError
from typing import Any, Dict, List


class PluginSection(BaseModel):
    """
    Defines a model for a plugin, which includes required and optional fields. The
    required field is `name`, while `args`, `entrypoint`, and `kwargs` are optional.
    It also contains a validator to ensure the format of the plugin name is in the
    format `<AUTHOR>/<PACKAGE>`.

    Attributes:
        name (str): Required to be filled. It must conform to the format <AUTHOR>/<PACKAGE>.
        args (List[Any]): Initialized with a default value of an empty list. This
            means it can be used to store any number of arguments that are passed
            when using this plugin.
        entrypoint (str): Initialized with a default value 'Plugin'. This means
            that when an instance of `PluginSection` is created, the `entrypoint`
            attribute will be set to 'Plugin' unless otherwise specified.
        kwargs (Dict[str, Any]): Initialized to an empty dictionary. It allows for
            arbitrary keyword arguments that can be passed when creating a plugin
            section.

    """
    # Required fields.
    name: str

    # Optional fields.
    args: List[Any] = []
    entrypoint: str = 'Plugin'
    kwargs: Dict[str, Any] = {}

    @validator('name')
    def validate_name(cls, name: str) -> str:
        """
        Validates the input 'name' as follows: if the length of the name, after
        stripping leading and trailing whitespace and splitting by '/', is not
        equal to 2, it raises an InvalidPluginNameError; otherwise, it returns the
        original name.

        Args:
            name (str): Validated by this method. The validation checks if the
                name contains exactly one slash (`/`) and returns the original
                name if valid, or raises an exception otherwise.

        Returns:
            str: The validated input name. If the validation fails, it raises an
            exception and doesn't return any result.

        """
        if not len(name.strip().split('/')) == 2:
            raise InvalidPluginNameError(plugin=name)
        return name
