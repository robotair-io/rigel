from pydantic import BaseModel, PrivateAttr
from typing import Any, Dict, List


class ApplicationComponent(BaseModel):
    """
    Validates and initializes application components with required fields (name,
    image) and optional fields (artifacts, introspection). It also allows for
    arbitrary keyword arguments to be stored as private attributes.

    Attributes:
        name (str): Required, indicating that it must be provided when instantiating
            an instance of the class.
        image (str): Required, meaning it must be provided when creating an instance
            of this class. It represents a string value representing the image
            associated with the application component.
        artifacts (List[str]): Optional by default. It can be initialized with a
            list of strings when an instance of the class is created, or it will
            default to an empty list if not provided.
        introspection (bool): Optional, defaulting to False. It represents a boolean
            flag for introspection purposes, possibly related to application
            inspection or debugging.
        _kwargs (Dict[str, Any]): Defined as a private attribute using PrivateAttr
            from the `dataclasses` module. It holds any additional keyword arguments
            passed to the `__init__` method that are not explicitly handled by
            other attributes.

    """
    # Required fields
    name: str
    image: str

    # Optional fields
    artifacts: List[str] = []
    introspection: bool = False

    # Private fields.
    _kwargs: Dict[str, Any] = PrivateAttr()

    def __init__(self, **data):
        """
        Initializes an object by calling the parent's `__init__` method with keyword
        arguments. It populates instance variables from input data and stores any
        remaining data in a private dictionary for later use.

        Args:
            **data (dict): Dictionary of keyword arguments

        """
        super().__init__(**{
            'name': data.pop('name', None),
            'image': data.pop('image', None),
            'artifacts': data.pop('artifacts', []),
            'introspection': data.pop('introspection', False)
        })
        self._kwargs = data


class PluginModel(BaseModel):

    # Required fields.
    """
    Defines a model with two attributes: `components`, a list of `ApplicationComponent`
    instances, and `timeout`, a floating-point value representing a time period
    set to zero by default. This class likely represents a plugin or an extension
    that can be composed of multiple components and has a timeout duration.

    Attributes:
        components (List[ApplicationComponent]): A collection of objects that are
            instances of the ApplicationComponent class, which means it can contain
            multiple components.
        timeout (float): 0.0 by default. It represents a timeout value, likely
            specifying the maximum time allowed for plugin operations to complete
            before considering them timed out or failed.

    """
    components: List[ApplicationComponent]

    # Optional fields.
    timeout: float = 0.0
