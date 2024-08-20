from rigel.files.decoder import HEADER_SHARED_DATA, YAMLDataDecoder
from rigel.loggers import get_logger
from rigel.models.application import Application
from rigel.models.plugin import PluginRawData
from rigel.models.rigelfile import RigelfileGlobalData
from typing import Any, Dict

LOGGER = get_logger()


class Plugin:
    """
    Initializes and manages a plugin for a RigelFile application, providing access
    to raw data, global data, application instance, and shared data. It also decodes
    raw data using YAMLDataDecoder. The plugin implements setup, start, process,
    and stop methods for its execution life cycle.

    Attributes:
        global_data (RigelfileGlobalData): Initialized in the constructor (`__init__`)
            method with a value provided as argument to the class constructor.
        application (Application): Initialized during object creation. It seems
            to represent a reference to the main application instance, likely used
            for communication or access to its functionality within the plugin.
        providers_data (Dict[str,Any]): Initialized with a dictionary mapping
            strings to any type of object during the constructor.
        shared_data (Dict[str,Any]|Dict[str,Any]): Optional with a default value
            of `{}`. It represents data that can be shared among plugins.
        raw_data (PluginRawData): Set by decoding raw data from a YAML file using
            the YAMLDataDecoder class. It is initialized in the `__init__` method
            during object creation.

    """

    def __init__(
        self,
        raw_data: PluginRawData,
        global_data: RigelfileGlobalData,
        application: Application,
        providers_data: Dict[str, Any],
        shared_data: Dict[str, Any] = {}  # noqa
    ) -> None:

        """
        Initializes instances of its attributes: global data, application, providers
        data, and shared data. It also decodes raw data using YAMLDataDecoder and
        stores it as an instance variable.

        Args:
            raw_data (PluginRawData): Used as input for decoding by YAMLDataDecoder.
                It seems to represent raw data in some format, possibly YAML or
                similar. The decoded output is stored in self.raw_data.
            global_data (RigelfileGlobalData): Assigned to an instance variable
                with the same name. It represents data that has global scope and
                relevance.
            application (Application): Expected to be passed when initializing an
                instance of the class. Its purpose is not explicitly mentioned,
                but it could represent the main application or program that is
                being used in this context.
            providers_data (Dict[str, Any]): Expected to contain data related to
                providers. It is initialized with an empty dictionary.
            shared_data (Dict[str, Any]): Optional. It represents additional data
                that can be shared across different parts of the program and can
                be used during the decoding process.

        """
        self.global_data = global_data
        self.application = application
        self.providers_data = providers_data
        self.shared_data = shared_data

        decoder = YAMLDataDecoder()
        self.raw_data = decoder.decode(
            raw_data,
            shared_data,
            HEADER_SHARED_DATA
        )

    def setup(self) -> None:
        """Use this function to allocate plugin resoures.
        """
        pass

    def start(self) -> None:
        """Use this function to start executing business logic of your plugin.
        """
        pass

    def process(self) -> None:
        """Use this function to perform any evaluation of your plugin execution.
        """
        pass

    def stop(self) -> None:
        """Use this function to gracefully clean plugin resources.
        """
        pass
