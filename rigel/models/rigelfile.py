from pydantic import BaseModel
from typing import Any, Dict, List, Optional, Union
from .docker import DockerSection, DockerfileSection
from .plugin import PluginSection
from .simulation import SimulationSection


class Rigelfile(BaseModel):
    """
    Defines a model for a Rigel configuration file. It consists of required and
    optional sections. The required section is "packages", which accepts at least
    one declaration from either `DockerSection` or `DockerfileSection`. Optional
    sections include "deploy", "simulate", and "vars".

    Attributes:
        packages (List[Union[DockerSection, DockerfileSection]]): Required to have
            at least one package declaration.
        deploy (List[PluginSection]): Optional. It represents a list of plugin
            sections that are used for deployment purposes, and can be empty if
            no plugins are required.
        simulate (Optional[SimulationSection]): Optional. It represents a Simulation
            Section that can be used to simulate deployment operations.
        vars (Dict[str, Any]): Optional. It represents a dictionary that maps
            strings to any data type, allowing for flexible storage and retrieval
            of variables with string keys.

    """
    # Required sections.
    packages: List[Union[DockerSection, DockerfileSection]]  # at least one package declaration is required

    # Optional sections.
    deploy: List[PluginSection] = []
    simulate: Optional[SimulationSection] = None
    vars: Dict[str, Any] = {}
