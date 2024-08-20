from __future__ import annotations
from enum import Enum
from rigel.clients import ROSBridgeClient
from typing import Any, Dict, List, Optional


class CommandType(Enum):
    """
    Defines a set of enumerations that represent different types of commands. These
    commands are used to manage connections, status changes, and simulation control
    within a ROSBridge system. The enumeration values range from 1 to 5, each
    corresponding to a unique command type.

    Attributes:
        ROSBRIDGE_CONNECT (int): 1. It represents a command to connect to the ROS
            bridge.
        ROSBRIDGE_DISCONNECT (int): 2, indicating a command to disconnect from a
            ROS (Robot Operating System) bridge.
        STATUS_CHANGE (int): 3. It represents a command for status change, indicating
            a request to modify or update the current system state.
        STOP_SIMULATON (int): 4, indicating a stop command for simulation.
        TRIGGER (int): 5. It represents a command type for triggering an action
            or event in the system.

    """
    ROSBRIDGE_CONNECT: int = 1
    ROSBRIDGE_DISCONNECT: int = 2
    STATUS_CHANGE: int = 3
    STOP_SIMULATON: int = 4
    TRIGGER: int = 5


class Command:
    """
    Initializes an instance with a specified `type` and `data`, which is expected
    to be a dictionary. It sets these attributes for future use, providing a basic
    structure for commands that require type identification and data storage.

    Attributes:
        type (CommandType): Initialized with a value during object creation. It
            represents the type or classification of the command being defined.
        data (Dict[str,Any]): Initialized with a dictionary where keys are strings
            and values can be any type of data (e.g., numbers, strings, objects).
            It represents additional information specific to each command.

    """
    def __init__(self, type: CommandType, data: Dict[str, Any]) -> None:
        """
        Initializes two instance variables: `type`, which is an object of type
        CommandType, and `data`, which is a dictionary with string keys and values
        of any type.

        Args:
            type (CommandType): Assigned to an instance variable `self.type`. It
                represents the type or category of the object being initialized.
                The specific meaning and values of this type are not specified in
                the provided code.
            data (Dict[str, Any]): Used to store key-value pairs of data. The keys
                are strings (str) and the values can be any type (Any).

        """
        self.type = type
        self.data = data


class CommandHandler:
    """
    Represents a hierarchical tree structure for handling commands. It provides
    methods to handle and send upstream and downstream commands, allowing nodes
    to communicate with their parents and children respectively.

    Attributes:
        father (Optional[CommandHandler]): A reference to the parent node in the
            hierarchical tree, allowing commands to be sent upstream to it.
        children (List[CommandHandler]): Used to store a collection of child command
            handlers within the current handler's tree structure, forming a
            hierarchical relationship between nodes.

    """

    # Command handlers form a hierarchical tree.
    # For commands to be exchanged between tree layers
    # each node must have a local notion of the tree structure.
    father: Optional[CommandHandler]
    children: List[CommandHandler]

    # All command handlers must implement a mechanism
    # to handle upstream commands sent by their respective children nodes.
    def handle_upstream_command(self, command: Command) -> None:
        raise NotImplementedError("Please implement this method")

    # All command handlers must implement a mechanism
    # to handle downstream commands sent by their respective father node.
    def handle_downstream_command(self, command: Command) -> None:
        raise NotImplementedError("Please implement this method")

    # All command handlers may send upstream commands
    # to their respective father nodes.
    def send_upstream_cmd(self, command: Command) -> None:
        """
        Sends an upstream command to its father if it exists, allowing for
        hierarchical handling of commands. The method takes a `command` object as
        input and returns None.

        Args:
            command (Command): Expected to be passed as an argument. It represents
                the command that needs to be sent upstream for processing.

        """
        if self.father:
            self.father.handle_upstream_command(command)

    # All command handlers may send downstream commands
    # to all of their respective children nodes.
    def send_downstream_cmd(self, command: Command) -> None:
        """
        Iterates over its children, invoking their `handle_downstream_command`
        methods with the given command as an argument. This allows the command to
        be propagated and handled by downstream components.

        Args:
            command (Command): Expected to be an object that represents a command.
                It is passed as an argument to the function, which then iterates
                over its children and calls their `handle_downstream_command`
                method with this command.

        """
        for child in self.children:
            child.handle_downstream_command(command)

    # All command handlers may send downstream commands
    # to a single child node.
    def send_child_downstream_cmd(self, child: CommandHandler, command: Command) -> None:
        """
        Send a downstream command to a single child node.

        :type child: CommandHandler
        :param child: The child node.
        :type command: Command
        :param command: The downstream command to send to the child node.
        """
        child.handle_downstream_command(command)


class CommandBuilder:
    """
    Provides methods to create various commands for a system, including connecting
    and disconnecting to ROSBridge, changing status, stopping simulation, and
    triggering an event with a specified timestamp. Each method returns a `Command`
    object with the corresponding type and optional parameters.

    """

    @staticmethod
    def build_rosbridge_connect_cmd(rosbridge_client: ROSBridgeClient) -> Command:
        """
        Builds and returns a ROSBRIDGE_CONNECT command with a specified ROSBridgeClient
        object as its parameter, encapsulating it within a Command data structure.

        Args:
            rosbridge_client (ROSBridgeClient): Expected to be an instance of the
                ROSBridgeClient class, which is likely a client for connecting to
                a ROS (Robot Operating System) bridge.

        Returns:
            Command: An instance of a class representing a command with two
            properties: CommandType set to ROSBRIDGE_CONNECT and a dictionary
            containing the client property with the value of rosbridge_client.

        """
        return Command(
            CommandType.ROSBRIDGE_CONNECT,
            {'client': rosbridge_client}
        )

    @staticmethod
    def build_rosbridge_disconnect_cmd() -> Command:
        """
        Creates and returns a ROSBridge disconnect command, represented as an
        instance of the `Command` class, with type set to `ROSBRIDGE_DISCONNECT`
        and no additional data (i.e., an empty dictionary).

        Returns:
            Command: An instance of a class, specifically constructed with the
            following arguments: `CommandType.ROSBRIDGE_DISCONNECT` and an empty
            dictionary `{}` as its data.

        """
        return Command(
            CommandType.ROSBRIDGE_DISCONNECT,
            {}
        )

    @staticmethod
    def build_status_change_cmd() -> Command:
        """
        Constructs and returns an instance of the Command class, specifying its
        type as STATUS_CHANGE with an empty dictionary as its payload.

        Returns:
            Command: Initialized with CommandType.STATUS_CHANGE and an empty
            dictionary `{}` as its arguments.

        """
        return Command(
            CommandType.STATUS_CHANGE,
            {}
        )

    @staticmethod
    def build_stop_simulation_cmd() -> Command:
        """
        Creates and returns a Command object with the type STOP_SIMULATION and an
        empty dictionary as its payload. The purpose is to build a command that
        stops a simulation process.

        Returns:
            Command: Initialized with two parameters: the command type as
            STOP_SIMULATION and an empty dictionary `{}`.

        """
        return Command(
            CommandType.STOP_SIMULATON,
            {}
        )

    @staticmethod
    def build_trigger_cmd(timestamp: float = 0.0) -> Command:
        """
        Constructs a Trigger command with an optional timestamp parameter. The
        returned command has a CommandType of TRIGGER and a payload containing the
        specified timestamp. This command is used to trigger some action or event
        at the given time.

        Args:
            timestamp (float): 0.0 by default. It represents a time value that
                will be included as part of the `Command` object being returned.

        Returns:
            Command: Instantiated with two parameters: CommandType.TRIGGER and a
            dictionary containing a single key-value pair 'timestamp' with default
            value 0.0.

        """
        return Command(
            CommandType.TRIGGER,
            {'timestamp': timestamp}
        )
