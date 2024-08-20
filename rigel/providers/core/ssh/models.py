from pydantic import BaseModel, Extra, root_validator
from rigel.exceptions import RigelError
from typing import List, Optional


#
# INPUT MODELS
#

class SSHKeyGroup(BaseModel, extra=Extra.forbid):

    # Required fields
    """
    Validates the presence and exclusivity of two optional fields: `env` and `path`.
    It ensures that either one or neither field is provided, preventing both from
    being declared simultaneously.

    Attributes:
        hostname (str): Required by default, as indicated by its absence from the
            list of optional attributes. It is not directly validated or checked
            for validity within this code snippet.
        env (Optional[str]): Optional, meaning it can be None or a string representing
            an environment variable name.
        path (Optional[str]): Optional, meaning it can be set to `None`. It
            represents a path to a file containing SSH key information.

    """
    hostname: str
    env: Optional[str] = None
    path: Optional[str] = None

    @root_validator(allow_reuse=True)
    def check_mutually_exclusive_fields(cls, values):
        """
        Validates the presence and exclusivity of two fields ('env' and 'path')
        when declaring an SSH key. It ensures that either both or neither of these
        fields are declared, preventing contradictory configurations.

        Args:
            values (Dict[str, Any]): An instance of a Pydantic model's configuration
                class. It represents the input data that is being validated by
                this decorator.

        Returns:
            Dict[str,Any]: The input dictionary `values`.

        """
        env = values.get('env')
        path = values.get('path')
        if env and path:
            raise RigelError("Both mutually excusive fields 'env' and 'path' were declared for a same SSH key")
        if not env and not path:
            raise RigelError("SSH key found with neither field 'env' nor 'path' declared")
        return values


class SSHProviderModel(BaseModel, extra=Extra.forbid):

    # Required fields
    """
    Defines a data model for storing and validating SSH key information. It inherits
    from `BaseModel` and restricts extra attributes with `extra=Extra.forbid`. The
    `keys` attribute is a list of `SSHKeyGroup` objects, which represents the
    collection of SSH keys provided by this model.

    Attributes:
        keys (List[SSHKeyGroup]): Forbidden from having extra values through the
            `extra=Extra.forbid` argument, ensuring that only valid SSH key groups
            are assigned to it.

    """
    keys: List[SSHKeyGroup]


#
# OUTPUT MODELS
#

class SSHKeyGroup(BaseModel, extra=Extra.forbid):

    # Required fields
    """
    Validates whether a SSH key has either its `env` or `path` attribute set, but
    not both simultaneously. It also checks if either of these attributes is missing
    when validating model instances.

    Attributes:
        hostname (str): Required to be set when creating an instance of this class,
            as it is not marked as optional or nullable.
        env (Optional[str]): Optional, meaning it can be left undefined. It
            represents a environment variable for the SSH key.
        path (Optional[str]): Optional, meaning it can be either present or absent
            from a model instance.

    """
    hostname: str
    env: Optional[str] = None
    path: Optional[str] = None

    @root_validator
    def check_mutually_exclusive_fields(cls, values):
        """
        Validates whether 'env' and 'path' fields are declared simultaneously for
        an SSH key or not. If both fields are present, it raises an error; if
        neither is present, it also raises an error.

        Args:
            values (Dict[str, Any]): Obtained from the `@root_validator` decorator.
                It represents the input data that is being validated for an SSH
                key configuration.

        Returns:
            Dict[str,Any]: The validated values passed to it. If no errors are
            found during validation, the original input is returned.

        """
        env = values.get('env')
        path = values.get('path')
        if env and path:
            raise RigelError("Both mutually excusive fields 'env' and 'path' were declared for a same SSH key")
        if not env and not path:
            raise RigelError("SSH key found with neither field 'env' nor 'path' declared")
        return values


class SSHProviderOutputModel(SSHProviderModel):
    pass  # inherit all the the same fields
