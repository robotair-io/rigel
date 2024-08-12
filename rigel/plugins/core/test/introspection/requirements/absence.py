import threading
from math import inf
from rigel.plugins.core.test.introspection.command import (
    Command,
    CommandBuilder,
    CommandType
)
from .node import SimulationRequirementNode


class AbsenceSimulationRequirementNode(SimulationRequirementNode):
    """
    Simulates absence by monitoring its child nodes for satisfaction and sends
    commands to downstream or upstream nodes based on their status and a specified
    timeout.

    Attributes:
        children (List[SimulationRequirementNode]): Initialized to an empty list
            during object creation. It stores child nodes, which are instances of
            SimulationRequirementNode or its subclasses.
        father (SimulationRequirementNode|None): Initialized to None. It is used
            to store the parent node of the current node, if any, in a tree-like
            structure.
        timeout (float|int): 0 by default. It represents the time limit for which
            a simulation requirement should be satisfied, after which it will
            automatically stop if not met.
        __timer (threadingTimer|None): Initialized with a timer that calls the
            `handle_timeout` method after a specified timeout period when started.
        handle_timeout (NoneNone): A method that gets called when a timer set in
            the node times out. It cancels any ongoing simulation if it has not
            been satisfied by then.
        satisfied (bool): Initially set to True when an instance of this class is
            created. It indicates whether all child nodes have satisfied their
            requirements or not.

    """

    def __init__(self, timeout: float = inf) -> None:
        """
        Initializes an instance by setting up attributes for children, father,
        timeout, and timer. It also sets the initial satisfaction state to True
        and creates a timer that will call the handle_timeout method after the
        specified timeout period.

        Args:
            timeout (float): 0 by default, which specifies the time after which
                an action should be performed. The value `inf` means that no timeout
                will occur. It is set to `self.__timer`, which triggers a timeout
                event when it expires.

        """
        self.children = []
        self.father = None
        self.timeout = timeout
        self.__timer = threading.Timer(timeout, self.handle_timeout)

        # By default an absence requirement is considered satisfied.
        # Change of state requires a prior reception of ROS messages by children nodes.
        self.satisfied = True

    def __str__(self) -> str:
        """
        Returns a string representation of itself and its child nodes by recursively
        concatenating their string representations. This is used to provide a
        human-readable output for the node and its children.

        Returns:
            str: A string representation of the object, consisting of the string
            representations of its children. The returned string is created by
            concatenating the strings of all child objects.

        """
        repr = ''
        for child in self.children:
            repr += f'{str(child)}'
        return repr

    def assess_children_nodes(self) -> bool:
        """
        Iterates over its child nodes, checks if any are satisfied, and returns
        False if found; otherwise, it returns True, indicating that none of the
        children are satisfied.

        Returns:
            bool: True if all children nodes are not satisfied and False otherwise,
            indicating whether there are any child nodes that are already satisfied.

        """
        for child in self.children:

            # NOTE: the following assertions is required so that mypy
            # doesn't throw an error related with multiple inheritance.
            # All 'children' are of type CommandHandler and
            # 'satisfied' is a member of SimulationRequirementNode
            # that inherits from CommandHandler.
            assert isinstance(child, SimulationRequirementNode)
            if child.satisfied:
                return False

        return True

    def handle_children_status_change(self) -> None:
        """
        Handles changes in the status of children nodes and triggers corresponding
        actions, such as disconnecting from Rosbridge, stopping simulation, and
        updating internal state variables.

        """
        if not self.assess_children_nodes():  # only consider state changes
            self.satisfied = False

            self.__timer.cancel()

            # Issue children to stop receiving incoming ROS messages.
            self.send_downstream_cmd(CommandBuilder.build_rosbridge_disconnect_cmd())

            # Inform father node about state change.
            self.send_upstream_cmd(CommandBuilder.build_stop_simulation_cmd())

    def handle_timeout(self) -> None:
        """
        Checks if the node's satisfaction status (`self.satisfied`) is not met,
        and if so, sends a stop simulation command upstream using the provided
        `CommandBuilder`. This likely handles a timeout condition in an absence
        simulation requirement.

        """
        if not self.satisfied:
            self.send_upstream_cmd(CommandBuilder.build_stop_simulation_cmd())

    def handle_rosbridge_connection_commands(self, command: Command) -> None:
        """
        Sends a command downstream and starts a timer if a time limit was specified,
        allowing execution to be limited by a timeout.

        Args:
            command (Command): Required.

        """
        self.send_downstream_cmd(command)

        # NOTE: code below will only execute after all ROS message handler were registered.
        if self.timeout != inf:  # start timer in case a time limit was specified
            self.__timer.start()

    def handle_rosbridge_disconnection_commands(self, command: Command) -> None:
        """
        Cancels any pending timer and sends downstream command when ROS bridge
        disconnection commands are received.

        Args:
            command (Command): Required for the method invocation. Its exact nature
                is not specified by this code snippet, but it likely represents a
                command related to ROSBridge disconnection.

        """
        self.__timer.cancel()  # NOTE: this method does not require previous call to 'start()'
        self.send_downstream_cmd(command)

    def handle_upstream_command(self, command: Command) -> None:
        """
        Processes an upstream command, specifically checking if the command is of
        type STATUS_CHANGE. If so, it calls the `handle_children_status_change`
        method to handle status changes for its children nodes.

        Args:
            command (Command): Expected to hold an instance of a class representing
                a command with a specific type, namely CommandType.STATUS_CHANGE.

        """
        if command.type == CommandType.STATUS_CHANGE:
            self.handle_children_status_change()

    def handle_downstream_command(self, command: Command) -> None:
        """
        Handles downstream commands received from other nodes or systems. It
        dispatches the commands based on their type, processing ROSbridge connection
        and disconnection requests, and triggering specific actions for other
        command types.

        Args:
            command (Command): Required to be processed by the function. Its type
                attribute determines which specific handling method should be executed.

        """
        if command.type == CommandType.ROSBRIDGE_CONNECT:
            self.handle_rosbridge_connection_commands(command)
        if command.type == CommandType.ROSBRIDGE_DISCONNECT:
            self.handle_rosbridge_disconnection_commands(command)
        if command.type == CommandType.TRIGGER:
            self.send_downstream_cmd(command)
