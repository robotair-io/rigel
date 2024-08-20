from pydantic import BaseModel, Extra
from rigel.loggers import get_logger


LOGGER = get_logger()


class Application(BaseModel, extra=Extra.forbid):
    """
    Defines a model that inherits from `BaseModel`. It has two properties: `distro`,
    which is required, and `dir`, which is optional with a default value of `'.'`.
    The `extra=Extra.forbid` parameter ensures that no additional attributes can
    be defined for the object.

    Attributes:
        distro (str): Required, meaning it must be provided when instantiating an
            instance of the `Application` class.
        dir (str): Optional, meaning it can be omitted when creating an instance
            of the class. Its default value is '.'.

    """
    # Required fields.
    distro: str

    # Optional fields.
    dir: str = '.'
