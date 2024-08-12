from importlib import import_module
from rigel.exceptions import (
    PluginNotCompliantError,
    PluginNotFoundError
)
from rigel.loggers import get_logger
from rigel.models.application import Application
from rigel.models.builder import ModelBuilder
from rigel.models.plugin import PluginRawData
from rigel.models.rigelfile import RigelfileGlobalData
from typing import Any, Dict, Type
from .plugin import Plugin

LOGGER = get_logger()


class PluginManager:

    """
    Manages plugins by checking compliance with a base class and loading them from
    modules. It resolves module and class names, verifies the plugin's structure,
    and constructs the plugin object using provided data.

    """
    def is_plugin_compliant(self, entrypoint: Type) -> bool:
        """Ensure that a given plugin entrypoint class is an instance of
        rigel.plugins.Plugin.

        :type entrypoint: Type
        :param entrypoint: The plugin entrypoint class.

        :rtype: bool
        :return: True if the plugin entrypoint class is an instance of
        rigel.plugins.Plugin. False otherwise.
        """
        return issubclass(entrypoint, Plugin)

    def load(
        self,
        entrypoint: str,
        plugin_raw_data: PluginRawData,
        global_data: RigelfileGlobalData,
        application: Application,
        providers_data: Dict[str, Any],
        shared_data: Dict[str, Any]
    ) -> Plugin:
        """
        Loads and initializes a plugin based on an entrypoint, using raw data,
        global data, application data, providers data and shared data to construct
        the plugin instance. It also checks for compliance with specific requirements.

        Args:
            entrypoint (str): Expected to be a fully qualified class name of a
                plugin. It represents the entry point for loading the plugin.
            plugin_raw_data (PluginRawData): Likely used to provide raw data
                required for creating a plugin instance, including any necessary
                configuration or setup information.
            global_data (RigelfileGlobalData): Used to build the plugin instance
                with other data such as raw data, application, providers data, and
                shared data.
            application (Application): Not explicitly used within the function,
                but it seems to be an object representing a Rigelfile application.
            providers_data (Dict[str, Any]): Expected to be a dictionary that
                stores data about providers for plugins, where keys are provider
                names and values are their corresponding data.
            shared_data (Dict[str, Any]): Used to create an instance of the Plugin
                class using ModelBuilder. It contains shared data that can be
                accessed by the plugin.

        Returns:
            Plugin: A constructed plugin object built from the specified entrypoint
            class and data passed as arguments.

        """
        plugin_complete_name = entrypoint.strip()
        plugin_name, plugin_entrypoint = plugin_complete_name.rsplit('.', 1)

        try:
            module = import_module(plugin_name)
            cls: Type = getattr(module, plugin_entrypoint)
        except ModuleNotFoundError:
            raise PluginNotFoundError(plugin_complete_name)

        if not self.is_plugin_compliant(cls):
            raise PluginNotCompliantError(
                plugin_complete_name,
                "entrypoint class must inherit functions 'setup','run', and 'stop' from class 'Plugin'."
            )

        plugin = ModelBuilder(cls).build([
            plugin_raw_data,
            global_data,
            application,
            providers_data
        ], {'shared_data': shared_data})
        assert isinstance(plugin, Plugin)

        return plugin
