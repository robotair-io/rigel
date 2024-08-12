from pydantic import Extra
from rigel.models.data import ComplexDataModel


class ContainerRegistry(ComplexDataModel, extra=Extra.forbid):

    """
    Defines a complex data model for storing information about container servers.
    It inherits from `ComplexDataModel` and is configured to disallow additional
    attributes. The class has three instance variables: `server`, `password`, and
    `username`, which represent the server details.

    Attributes:
        server (str): A component of the complex data model. It represents the
            server address or hostname where container registry services are hosted.
        password (str): Part of a class definition that inherits from `ComplexDataModel`.
            It appears to be a private attribute, as it does not have a corresponding
            setter method.
        username (str): Part of its definition as a subclass of `ComplexDataModel`.
            Its presence in the class definition suggests that it is expected to
            be present in instances of this class.

    """
    server: str
    password: str
    username: str
