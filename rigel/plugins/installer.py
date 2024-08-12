import sys
from rigel.exceptions import (
    InvalidPluginNameError,
    PluginInstallationError
)
from subprocess import CalledProcessError, check_call


class PluginInstaller:
    """
    Installs an external plugin by downloading and installing it using pip. It
    takes a plugin name, host, and a boolean indicating whether to use SSH or HTTPS
    protocol as input parameters.

    Attributes:
        plugin (str): Initialized with a plugin name passed to the constructor.
            It is further processed by splitting it into a user name and a plugin
            name.
        plugin_user (str|None): Calculated during the initialization process by
            splitting the provided plugin string using '/' as a separator and
            taking the first part. It represents the user part of the plugin name.
        plugin_name (str): Obtained by splitting the `plugin` string with '/' as
            a delimiter, provided that the plugin name can be split correctly;
            otherwise, it raises an error.
        host (str): Initialized by passing a value to its constructor. It represents
            the host where the plugin resides, and it can be either an SSH or HTTPS
            URL depending on the `private` attribute.
        protocol (str|ssh|https): Determined by the value of the `private` parameter
            passed during initialization. If `private` is True, it defaults to
            'ssh', otherwise it defaults to 'https'.

    """

    def __init__(self, plugin: str, host: str, private: bool) -> None:
        """
        Initializes an instance by setting plugin, host, and protocol properties.
        It splits the plugin name from the input string, raises an error if not
        valid, sets the default protocol as 'ssh' for private plugins or 'https'
        otherwise.

        Args:
            plugin (str): Used to initialize an object with plugin information.
                It is expected to be in the format `/plugin_name` or `/user/plugin_name`,
                where `plugin_name` is the name of the plugin.
            host (str): Assigned to an instance variable named `self.host`. It is
                expected to be a string value representing a host or server name.
            private (bool): Used to specify whether the connection should be made
                using SSH or HTTPS protocols, depending on its value being True
                or False.

        """
        self.plugin = plugin
        try:
            self.plugin_user, self.plugin_name = plugin.strip().split('/')
        except ValueError:
            raise InvalidPluginNameError(plugin=plugin)
        self.host = host
        self.protocol = 'ssh' if private else 'https'

    def install(self) -> None:
        """
        Installs a plugin from a Git repository using pip. The URL for the repository
        is constructed based on the protocol and other attributes of the class.
        If installation fails, it raises a PluginInstallationError exception.

        """
        url = f"{self.protocol}://{'git@' if self.protocol == 'ssh' else ''}{self.host}/{self.plugin_user}/{self.plugin_name}"

        try:
            check_call([sys.executable, '-m', 'pip', 'install', f'git+{url}'])
        except CalledProcessError:
            raise PluginInstallationError(plugin=self.plugin)
