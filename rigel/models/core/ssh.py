from pydantic import Extra
from rigel.models.data import ComplexDataModel


class SSHPrivateKeyFile(ComplexDataModel, extra=Extra.forbid):
    """
    Defines a complex data model for representing SSH private key files. It has
    two attributes: `hostname` and `path`, which specify the hostname associated
    with the key file and its path, respectively. This class enforces strict schema
    validation by forbidding extra attributes.

    Attributes:
        hostname (str): Part of the class's definition, allowing it to be used
            within the context of SSH private key files, likely representing a
            hostname associated with the key.
        path (str): Used to store a string value representing the file path where
            the SSH private key is located.

    """

    hostname: str
    path: str


class SSHPrivateKey(ComplexDataModel, extra=Extra.forbid):

    """
    Represents an SSH private key data model, inheriting from `ComplexDataModel`.
    It has two attributes: `hostname` and `value`, both of type `str`, which likely
    represent the hostname and the private key value respectively.

    Attributes:
        hostname (str): A part of the inherited `ComplexDataModel`.
        value (str): Part of the class definition. It represents the private key
            value itself, which is a string representation of the SSH private key
            data.

    """

    hostname: str
    value: str
