from pydantic.error_wrappers import ValidationError
from rigel.exceptions import PydanticValidationError
from typing import Any, Dict, List, Type


class ModelBuilder:
    """
    Initializes an instance type and uses it to create a new instance based on
    provided arguments and keyword arguments. It also catches any `ValidationError`
    exceptions and re-raises them as `PydanticValidationError`.

    Attributes:
        instance_type (Type): Initialized with a specific instance type during
            object creation.

    """

    def __init__(self, instance_type: Type) -> None:
        """
        Set the class to instantiate.

        :type instance_type: Type
        :param instance_type: The class to instantiate.
        """
        self.instance_type = instance_type

    # TODO: change return type from Any to a proper type.
    def build(self, args: List[Any], kwargs: Dict[str, Any]) -> Any:
        """
        Attempts to create an instance of `self.instance_type` using provided
        arguments and keyword arguments. If successful, it returns the created
        instance. In case of a ValidationError, it wraps the exception with
        PydanticValidationError and re-raises it.

        Args:
            args (List[Any]): Expected to be a list of arguments that will be
                passed to the `instance_type` method.
            kwargs (Dict[str, Any]): Expected to be a dictionary where keys are
                strings (parameter names) and values are arbitrary types. It
                represents keyword arguments passed to the instance_type function.

        Returns:
            Any: The result of calling `self.instance_type` with `*args` and
            `**kwargs`. If an exception occurs during this call, it catches the
            ValidationError and raises a PydanticValidationError instead.

        """
        try:
            return self.instance_type(*args, **kwargs)

        except ValidationError as exception:
            raise PydanticValidationError(exception)
