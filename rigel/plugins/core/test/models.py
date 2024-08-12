from pydantic import BaseModel
from typing import List


class PluginModel(BaseModel):

    # Required fields.
    """
    Defines a model for plugin configuration. It contains requirements, hostname,
    port number (defaulting to 9090), timeout period (defaulting to 300 seconds),
    and an ignore value (defaulting to 0). This class serves as a template for
    storing and managing plugin settings.

    Attributes:
        requirements (List[str]): Intended to hold a list of string values
            representing software requirements for the plugin.
        hostname (str): Initialized with no value. It represents a hostname which
            is usually the name of a host or server on a network, but it can also
            be any string.
        port (int): Set to a default value of 9090. This means that if no port
            number is specified when creating an instance of this model, it will
            automatically use port 9090.
        timeout (float): 300.0 by default, which specifies the time interval (in
            seconds) within which a connection or operation should be completed.
        ignore (float): 0.0 by default.

    """
    requirements: List[str]
    hostname: str

    # Optional fields
    port: int = 9090
    timeout: float = 300.0  # seconds
    ignore: float = 0.0  # seconds
