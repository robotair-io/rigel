from importlib import import_module
from rigel.exceptions import (
    PluginNotCompliantError,
    PluginNotFoundError
)
from rigel.loggers import get_logger
from rigel.models.builder import ModelBuilder
from rigel.models.provider import ProviderRawData
from rigel.models.rigelfile import RigelfileGlobalData
from typing import Any, Dict, Type
from .provider import Provider

LOGGER = get_logger()


class ProviderManager:

    """
    Loads and validates providers by checking their compliance with a base `Provider`
    class and instantiates them with necessary data to create instances of the
    providers. It handles errors during importation, checks for correct inheritance
    and returns the provider instance.

    """
    def is_provider_compliant(self, entrypoint: Type) -> bool:
        """Ensure that a given provider entrypoint class is an instance of
        rigel.providers.Provider.

        :type entrypoint: Type
        :param entrypoint: The provider entrypoint class.

        :rtype: bool
        :return: True if the provider entrypoint class is an instance of
        rigel.providers.Provider. False otherwise.
        """
        return issubclass(entrypoint, Provider)

    def load(
        self,
        entrypoint: str,
        identifier: str,
        provider_raw_data: ProviderRawData,
        global_data: RigelfileGlobalData,
        providers_data: Dict[str, Any]
    ) -> Provider:
        """
        Loads and configures a provider entrypoint, ensuring it is compliant with
        the 'Provider' class requirements. It returns a configured Provider object
        built from the loaded module, data, and identifier.

        Args:
            entrypoint (str): Required for loading the provider. It represents the
                full name of the module where the provider class is defined, with
                the package name and class name separated by a dot (e.g., "package.module:Provider").
            identifier (str): Used to identify a provider. It is one of the inputs
                required by the `ModelBuilder` class to build a `Provider` object.
            provider_raw_data (ProviderRawData): Used as input data for building
                the provider.
            global_data (RigelfileGlobalData): Used to pass global data that is
                required for loading the provider. The exact nature and usage of
                this data is not specified within this code snippet.
            providers_data (Dict[str, Any]): Expected to be a dictionary that
                contains data for providers. Its structure and content are not specified.

        Returns:
            Provider: An instance of a class that inherits from 'Provider' and
            provides connection and disconnection functionality.

        """
        provider_complete_name = entrypoint.strip()
        provider_name, provider_entrypoint = provider_complete_name.rsplit('.', 1)

        try:
            module = import_module(provider_name)
            cls: Type = getattr(module, provider_entrypoint)
        except ModuleNotFoundError:
            raise PluginNotFoundError(provider_complete_name)

        if not self.is_provider_compliant(cls):
            raise PluginNotCompliantError(
                provider_complete_name,
                "entrypoint class must inherit functions 'connect' and 'disconnect' from class 'Provider'."
            )

        provider = ModelBuilder(cls).build([
            identifier,
            provider_raw_data,
            global_data,
            providers_data
        ], {})

        assert isinstance(provider, Provider)
        return provider
