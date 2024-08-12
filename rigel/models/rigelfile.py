from pydantic import BaseModel, Extra
from typing import Dict, Union
from .application import Application
from .data import ComplexDataModel, SimpleDataModel
from .plugin import PluginDataModel
from .provider import ProviderDataModel
from .sequence import Sequence

RigelfileGlobalData = Dict[str, Union[ComplexDataModel, SimpleDataModel]]


class Rigelfile(BaseModel, extra=Extra.forbid):
    """
    Defines a data model for Rigel configuration files. It has required fields for
    application and jobs, as well as optional fields for providers, sequences, and
    global variables. This class ensures that only necessary data is stored in the
    Rigel configuration file.

    Attributes:
        application (Application): Required.
        jobs (Dict[str, PluginDataModel]): Required. It represents a dictionary
            where each key is a string and the corresponding value is of type PluginDataModel.
        providers (Dict[str, ProviderDataModel]): Optional by default with a default
            value of an empty dictionary `{}`.
        sequences (Dict[str, Sequence]): Optional. It contains a dictionary where
            keys are strings and values are instances of the `Sequence` model.
        vars (RigelfileGlobalData): Initialized with an empty dictionary `{}` by
            default.

    """

    # Required fields.
    application: Application
    jobs: Dict[str, PluginDataModel]

    # Optional fields.
    providers: Dict[str, ProviderDataModel] = {}
    sequences: Dict[str, Sequence] = {}
    vars: RigelfileGlobalData = {}
