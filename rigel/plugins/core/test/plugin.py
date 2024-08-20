from rigel.clients import ROSBridgeClient
from rigel.loggers import get_logger
from rigel.models.application import Application
from rigel.models.builder import ModelBuilder
from rigel.models.plugin import PluginRawData
from rigel.models.rigelfile import RigelfileGlobalData
from rigel.plugins import Plugin as PluginBase
from typing import Any, Dict, List, Optional
from .models import PluginModel
from .introspection.command import CommandHandler
from .introspection.requirements.manager import SimulationRequirementsManager
from .introspection.parser import SimulationRequirementsParser

LOGGER = get_logger()


class Plugin(PluginBase):

    """
    Initializes and manages a plugin for a ROS (Robot Operating System) application,
    connecting to a ROS bridge server, parsing requirements, starting introspection,
    processing data, and stopping the process safely.

    Attributes:
        model (PluginModel): Initialized by calling `ModelBuilder(PluginModel).build([],
            self.raw_data)`. It represents a model for the plugin, used to configure
            the plugin's behavior.
        raw_data (PluginRawData): Passed as a parameter to its constructor. Its
            purpose is not explicitly defined within this code snippet.
        __rosbridge_client (Optional[ROSBridgeClient]): Used to ensure a safe stop
            at any moment by keeping track of the ROS bridge client connection
            status. It is initialized as None in the `__init__` method.
        __requirements_manager (Optional[SimulationRequirementsManager]): Initialized
            as None in the `__init__` method. It is used to manage simulation
            requirements, specifically for ROS bridge connections.

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
        Initializes the plugin with given data and builds a model using the
        ModelBuilder. It also sets up optional instances for ROSBridgeClient and
        SimulationRequirementsManager, ensuring safe stop at any moment. An assertion
        ensures that the built model is indeed a PluginModel.

        Args:
            raw_data (PluginRawData): Expected to be passed during object
                initialization. It seems to hold raw data related to plugins. The
                specific purpose or structure of this data is not directly mentioned
                in this code snippet.
            global_data (RigelfileGlobalData): Not explicitly used within this
                function. Its purpose is unknown from the provided code snippet.
            application (Application): Passed to the parent class (`super().__init__`).
                Its purpose is not explicitly stated but it is likely related to
                the application context or environment within which this plugin operates.
            providers_data (Dict[str, Any]): Passed as an argument to the class
                constructor. It represents data related to providers.
            shared_data (Dict[str, Any]): Optional, having a default value of an
                empty dictionary.

        """
        super().__init__(
            raw_data,
            global_data,
            application,
            providers_data,
            shared_data
        )

        # Ensure model instance was properly initialized
        self.model = ModelBuilder(PluginModel).build([], self.raw_data)

        # Ensure a reference exists to the ROS bridge client
        # to ensure safe stop at any moment
        self.__rosbridge_client: Optional[ROSBridgeClient] = None

        # Ensure a reference exists to the requirement introspection manager
        # to ensure safe stop at any moment
        self.__requirements_manager: Optional[SimulationRequirementsManager] = None

        assert isinstance(self.model, PluginModel)

    def connect_to_rosbridge_server(self) -> None:

        """
        Establishes a connection to a ROS bridge server at a specified hostname
        and port, then logs an informational message upon successful connection.

        """
        self.__rosbridge_client = ROSBridgeClient(self.model.hostname, self.model.port)
        self.__rosbridge_client.connect()
        LOGGER.info(f"Connected to ROS bridge server at '{self.model.hostname}:{self.model.port}'")

    def disconnect_from_rosbridge_server(self) -> None:
        """
        Disconnects from a ROS bridge server and resets its client instance if one
        exists, then logs an informational message indicating successful disconnection.

        """
        if self.__rosbridge_client:
            self.__rosbridge_client.close()
            LOGGER.info(f"Disconnected from ROS bridge server at '{self.model.hostname}:{self.model.port}'")
        self.__rosbridge_client = None

    def start_introspection(self) -> None:

        """
        Initializes and configures introspection requirements for a plugin. It
        parses requirements, adds them to a manager, and connects the manager to
        a ROSbridge client for handling communication with ROS nodes.

        """
        requirements: List[CommandHandler] = [
            self.__requirements_parser.parse(req) for req in self.model.requirements
        ]

        self.__requirements_manager.add_children(requirements)
        self.__requirements_manager.connect_to_rosbridge(self.__rosbridge_client)

    def stop_introspection(self) -> None:

        """
        Disconnects from ROSBridge if a requirements manager exists, indicating
        that introspection has been stopped or terminated. This function stops any
        ongoing communication with the ROSBridge component.

        """
        if self.__requirements_manager:
            self.__requirements_manager.disconnect_from_rosbridge()

    def setup(self) -> None:

        """
        Initializes the plugin by connecting to a ROSBridge server and creating
        instances of SimulationRequirementsManager and SimulationRequirementsParser,
        passing parameters from the model to these objects.

        """
        self.connect_to_rosbridge_server()

        self.__requirements_manager = SimulationRequirementsManager(
            self.model.timeout * 1.0,
            self.model.ignore * 1.0
        )
        self.__requirements_parser = SimulationRequirementsParser()

    def start(self) -> None:
        """
        Plugin entrypoint.
        Connect to the ROS system to be tested.
        """
        self.start_introspection()

    def process(self) -> None:
        """
        Logs an informational message, then enters a loop that continues until the
        requirements manager indicates it has finished processing. Once done, it
        prints the requirements manager's status.

        """
        LOGGER.info("Testing the application!")
        while not self.__requirements_manager.finished:
            pass
        print(self.__requirements_manager)

    def stop(self) -> None:
        """
        Stops introspection and disconnects from the ROSBridge server, indicating
        that the plugin's execution has been terminated.

        """
        self.stop_introspection()
        self.disconnect_from_rosbridge_server()
