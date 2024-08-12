from pydantic import BaseModel, Extra, Field
from typing import Any, Dict, List, Union


class SequenceJobEntry(BaseModel, extra=Extra.forbid):

    # Required fields.
    """
    Validates and serializes data for a sequence job entry. It inherits from
    `BaseModel`, enforcing strict schema validation with `extra=Extra.forbid`. The
    class has two attributes: `name` (a string) and `with_` (a dictionary alias
    for the `with` field, initialized to an empty dictionary).

    Attributes:
        name (str): A required field.
        with_ (Dict[str, Any]): Aliased as 'with'. It represents a dictionary where
            keys are strings and values can be any type. The name with underscores
            at the beginning indicates that it might have been used to avoid
            conflict with Python's built-in keyword `with`.

    """
    name: str
    with_: Dict[str, Any] = Field(..., alias='with')


class StageBaseModel(BaseModel, extra=Extra.forbid):

    # Optional fields.
    """
    Inherits from `BaseModel` and defines a `description` attribute as a string
    with a default value of an empty string. The `extra=Extra.forbid` parameter
    prevents additional attributes from being created for the model instance.

    Attributes:
        description (str): Initialized to an empty string. It inherits from
            BaseModel, a base model class that provides basic functionality for
            data models.

    """
    description: str = ''


class SequentialStage(StageBaseModel, extra=Extra.forbid):

    # Required fields.
    """
    Is a model that inherits from `StageBaseModel`. It has a property `jobs`, which
    is a list that can contain either a string or an instance of `SequenceJobEntry`.
    This indicates that the stage can process either single-job or multi-job sequences.

    Attributes:
        jobs (List[Union[str, SequenceJobEntry]]): Defined by the parent class
            `StageBaseModel`. It can contain a list of string values or objects
            of type `SequenceJobEntry`.

    """
    jobs: List[Union[str, SequenceJobEntry]]


class ConcurrentStage(StageBaseModel, extra=Extra.forbid):

    # Required fields.
    """
    Defines a stage that can execute multiple jobs concurrently, inheriting
    properties from its base model. It contains two attributes: `jobs`, which holds
    a list of job entries (strings or instances of `SequenceJobEntry`), and
    `dependencies`, which stores a list of dependencies for those jobs.

    Attributes:
        jobs (List[Union[str, SequenceJobEntry]]): Used to represent a list of
            jobs that can be either strings or instances of SequenceJobEntry.
        dependencies (List[Union[str, SequenceJobEntry]]): Used to store a list
            of either string (job names) or SequenceJobEntry objects that represent
            jobs which must be completed before this job can start.

    """
    jobs: List[Union[str, SequenceJobEntry]]
    dependencies: List[Union[str, SequenceJobEntry]]


class ParallelStage(StageBaseModel, extra=Extra.forbid):

    # Required fields.
    """
    Inherits from `StageBaseModel`. It contains a list of parallel stages (`parallel`)
    and a dictionary for storing matrices with string keys and values that can be
    strings or lists of any type (`matrix`).

    Attributes:
        parallel (List[Union[SequentialStage, ConcurrentStage]]): Not nullable.
        matrix (Dict[str, Union[str, List[Any]]]): Initialized as an empty dictionary.
            It allows for key-value pairs where keys are strings, and values can
            be either strings or lists of any type (Any).

    """
    parallel: List[Union[SequentialStage, ConcurrentStage]]

    # Optional fields.
    matrix: Dict[str, Union[str, List[Any]]] = {}


SequenceStage = Union[SequentialStage, ParallelStage, ConcurrentStage]


class Sequence(BaseModel, extra=Extra.forbid):

    # Required fields.
    """
    Defines a model with two attributes: `stages`, which is a list of `SequenceStage`
    objects, and `matrix`, which is a dictionary that can contain any type of
    value. The `extra=Extra.forbid` parameter restricts additional fields from
    being added to the model.

    Attributes:
        stages (List[SequenceStage]): Mandatory to be defined.
        matrix (Dict[str, Any]): Initialized as an empty dictionary (`{}`). This
            suggests that it will store key-value pairs with string keys and values
            of any data type.

    """
    stages: List[SequenceStage]

    # Optional fields.
    matrix: Dict[str, Any] = {}
