from pydantic import BaseModel, Extra


class ContainerRegistryProviderModel(BaseModel, extra=Extra.forbid):

    # Required fields
    """
    Defines a model for managing container registry providers' settings. It consists
    of three attributes: `server`, `username`, and `password`, which store the
    details required to connect to a container registry server, such as Docker Hub
    or Amazon ECR.

    Attributes:
        server (str): Expected to contain a string representing the server name
            or URL for container registry.
        username (str): Part of the data model for a container registry provider.
            It represents the username required to access the registry.
        password (str): Part of the model definition, which is used for serializing
            and deserializing JSON data.

    """
    server: str
    username: str
    password: str
