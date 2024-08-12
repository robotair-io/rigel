from rigel.loggers import get_logger
from rigel.models.provider import ProviderRawData
from rigel.models.rigelfile import RigelfileGlobalData
from typing import Any, Dict

LOGGER = get_logger()


class Provider:
    """
    Initializes and manages connections to a resource, represented by an identifier.
    It holds three types of data: raw provider data, global data, and providers'
    data. The class provides two methods: `connect` and `disconnect`, which are
    currently empty but can be implemented to establish and terminate the connection.

    Attributes:
        identifier (str): Set during initialization with a provided value. It does
            not have any specific functionality or connection to other attributes,
            but it provides a unique identifier for each instance of the class.
        raw_data (ProviderRawData): Initialized during object creation with a value
            of ProviderRawData.
        global_data (RigelfileGlobalData): Initialized with a value during object
            creation. Its purpose is not explicitly stated, but it may contain
            global data related to the provider or the system.
        providers_data (Dict[str,Any]): Initialized during object creation with
            the value provided as argument.

    """

    def __init__(
        self,
        identifier: str,
        raw_data: ProviderRawData,
        global_data: RigelfileGlobalData,
        providers_data: Dict[str, Any],
    ) -> None:
        """
        Initializes an object with four parameters: identifier, raw data, global
        data, and providers' data. It sets these parameters as instance variables
        for future use.

        Args:
            identifier (str): Assigned to the instance variable `self.identifier`.
            raw_data (ProviderRawData): Assigned to the instance variable `self.raw_data`.
            global_data (RigelfileGlobalData): Assigned to an instance variable
                named `global_data`.
            providers_data (Dict[str, Any]): Expected to be a dictionary where
                keys are strings and values can be any data type (Any). It represents
                the provider-related data.

        """
        self.identifier = identifier
        self.raw_data = raw_data
        self.global_data = global_data
        self.providers_data = providers_data

    def connect(self) -> None:
        """Use this function to connect to required provider services.
        """
        pass

    def disconnect(self) -> None:
        """Use this function to gracefully diconnect from provider services.
        """
        pass
