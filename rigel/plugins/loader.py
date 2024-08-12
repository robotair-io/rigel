import inspect
from importlib import import_module
from rigel.exceptions import (
    PluginNotCompliantError,
    PluginNotFoundError,
)
from rigelcore.models import ModelBuilder
from rigel.models import PluginSection
from .plugin import Plugin
from typing import Any, Type


class PluginLoader:
    """
    Validates and loads plugins. It checks if a plugin's entrypoint is compliant
    with specified methods, then imports and initializes it using the `ModelBuilder`.
    If not compliant, it raises an error.

    """

    def is_plugin_compliant(self, entrypoint: Type) -> bool:
        """
        Ensure that a given plugin entrypoint class is compliant with the
        rigel.plugins.Plugin protocol. All compliant entrypoint classes have
        a 'run' and 'stop' functions.

        :type entrypoint: Type
        :param entrypoint: The external plugin entrypoint class.

        :rtype: bool
        :return: True if the external plugin entrypoint class is compatible with the
        rigle.plugins.Plugin protocol. False otherwise.
        """
        return issubclass(entrypoint, Plugin)

    def is_run_compliant(self, entrypoint: Type) -> bool:
        """
        Checks whether an entrypoint's run method complies with the requirement
        that it has exactly one parameter, excluding the implicit 'self' parameter.
        It returns True if compliant and False otherwise.

        Args:
            entrypoint (Type): An object representing a callable Python function,
                specifically the entry point to be checked for compliance with the
                Run protocol.

        Returns:
            bool: True if the entrypoint's run method has exactly one parameter,
            excluding 'self', and False otherwise.

        """
        signature = inspect.signature(entrypoint.run)
        return not len(signature.parameters) != 1  # allows for no parameter besides self

    def is_stop_compliant(self, entrypoint: Type) -> bool:
        """
        Checks if an entrypoint's stop method conforms to the stop protocol, i.e.,
        it takes exactly one argument besides self.

        Args:
            entrypoint (Type): An object that represents a class, which has a
                method named `stop`. This method's signature is inspected to
                determine if it complies with certain requirements.

        Returns:
            bool: True if the `stop` method of the `entrypoint` object has exactly
            one parameter (excluding `self`), and False otherwise.

        """
        signature = inspect.signature(entrypoint.stop)
        return not len(signature.parameters) != 1  # allows for no parameter besides self

    # TODO: set return type to Plugin
    def load(self, plugin: PluginSection) -> Any:
        """
        Loads and validates a plugin by importing its module, checking its compliance
        with required attributes and methods, and then building an instance of the
        plugin using its arguments and keyword arguments.

        Args:
            plugin (PluginSection): Expected to have a name attribute which is a
                string representing the path of the plugin module followed by the
                entrypoint class, for example "path/to/plugin/my_plugin".

        Returns:
            Any: An instance of a class built by `ModelBuilder`. The instance is
            constructed with arguments and keyword arguments passed from the
            `plugin.args` and `plugin.kwargs`.

        """
        _, plugin_name = plugin.name.strip().split('/')
        complete_plugin_name = f'{plugin.name}.{plugin.entrypoint}'

        try:
            module = import_module(plugin_name)
            entrypoint = plugin.entrypoint
            cls: Type = getattr(module, entrypoint)
        except ModuleNotFoundError:
            raise PluginNotFoundError(plugin=complete_plugin_name)

        if not self.is_plugin_compliant(cls):
            raise PluginNotCompliantError(
                plugin=plugin.name,
                cause="entrypoint class must implement functions 'run' and 'stop'."
            )

        if not self.is_run_compliant(cls):
            raise PluginNotCompliantError(
                plugin=plugin.name,
                cause=f"attribute function '{complete_plugin_name}.run' must not receive any parameters."
            )

        if not self.is_stop_compliant(cls):
            raise PluginNotCompliantError(
                plugin=plugin.name,
                cause=f"attribute function '{complete_plugin_name}.stop' must not receive any parameters."
            )

        builder = ModelBuilder(cls)
        return builder.build(plugin.args, plugin.kwargs)
