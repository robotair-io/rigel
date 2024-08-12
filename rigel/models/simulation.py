from pydantic import BaseModel
from typing import List
from .plugin import PluginSection


class SimulationSection(BaseModel):
    """
    Defines a simulation section in a model, containing required and optional
    fields. It consists of a list of plugins (`plugins`) and has two optional
    attributes: an introspection list (`introspection`) and a timeout value (`timeout`).

    Attributes:
        plugins (List[PluginSection]): Required. It represents a list of plugin sections.
        introspection (List[str]): Optional. It represents a list of strings that
            provides additional information about the simulation. The default value
            for this attribute is an empty list if not provided.
        timeout (int): 60 seconds by default, indicating the maximum time allowed
            for a simulation to run before it times out.

    """
    # Required fields.
    plugins: List[PluginSection]

    # Optional fields
    introspection: List[str] = []
    timeout: int = 60  # seconds
