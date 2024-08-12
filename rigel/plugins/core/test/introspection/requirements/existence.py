import threading
from math import inf
from rigel.plugins.core.test.introspection.command import (
    Command,
    CommandBuilder,
    CommandType
)
from .node import SimulationRequirementNode


class ExistenceSimulationRequirementNode(SimulationRequirementNode):
    """
    Simulates a node for existence-based requirements in a simulation. It maintains
    a list of child nodes, checks their satisfaction status, and handles timer
    events, ROS bridge connections/disconnections, and upstream commands to manage
    the simulation according to its timeout and status.

    Attributes:
        children (List[SimulationRequirementNode]): Initialized as an empty list
            during object creation. It stores child nodes that are part of the
            simulation requirement tree structure.
        father (SimulationRequirementNode|None): Initialized as None in its
            constructor. It represents a reference to the parent node, if any, in
            the tree-like structure.
        timeout (float|inf): 0 seconds by default, which means no timeout for
            handling commands or status changes.
        __timer (threadingTimer|None): Initialized with a Timer object that calls
            the `handle_timeout` method when it expires after the specified timeout
            period, if the node's satisfaction status remains unchanged.
        handle_timeout (NoneNone): Called when the timer associated with the node
            times out. If the satisfaction status of the node is False, it sends
            a stop simulation command upstream.

    """

    def __init__(self, timeout: float = inf) -> None:
        """
        Initializes an instance of the node with optional timeout. It sets up lists
        to hold child nodes, references its father node, and schedules a timer to
        call the `handle_timeout` method after the specified timeout period if
        it's not infinite.

        Args:
            timeout (float): 0 by default. It sets the time limit for the timer.
                If this value is not provided, it defaults to infinity. This means
                that if no timeout is specified, the thread will run indefinitely.

        """
        self.children = []
        self.father = None
        self.timeout = timeout
        self.__timer = threading.Timer(timeout, self.handle_timeout)

    def __str__(self) -> str:
        """
        Recursively concatenates the string representations of its child nodes and
        returns the result as a string, representing the node's hierarchical structure.

        Returns:
            str: A string representation of an object. The returned string is
            constructed by concatenating the string representations of all child
            objects stored in the `self.children` list.

        """
        repr = ''
        for child in self.children:
            repr += f'{str(child)}'
        return repr

    def assess_children_nodes(self) -> bool:
        """
        Traverses its children nodes, checks if each child node's `satisfied`
        attribute is True, and returns False as soon as it finds a non-satisfied
        child node; otherwise, it returns True.

        Returns:
            bool: `True` if all children nodes are satisfied and `False` otherwise.
            It checks each child node's `satisfied` attribute, returning immediately
            if any node is not satisfied. If all nodes are satisfied, it returns
            `True`.

        """
        for child in self.children:

            # NOTE: the following assertion is required so that mypy
            # doesn't throw an error related with multiple inheritance.
            # All 'children' are of type CommandHandler and
            # 'satisfied' is a member of SimulationRequirementNode
            # that inherits from CommandHandler.
            assert isinstance(child, SimulationRequirementNode)

            if not child.satisfied:
                return False
        return True

    def handle_children_status_change(self) -> None:
        """
        Updates the node's status when its children nodes change their status,
        cancels any ongoing timers, and sends commands to stop receiving ROS
        messages and notify upstream nodes about the status change.

        """
        if self.assess_children_nodes():
            self.satisfied = True

            self.__timer.cancel()

            # Issue children to stop receiving incoming ROS messages.
            self.send_downstream_cmd(CommandBuilder.build_rosbridge_disconnect_cmd())

            # Inform father node about state change.
            self.send_upstream_cmd(CommandBuilder.build_status_change_cmd())

    def handle_timeout(self) -> None:
        """
        Stops a simulation when a timeout occurs if the requirement is not already
        satisfied.

        """
        if not self.satisfied:
            self.send_upstream_cmd(CommandBuilder.build_stop_simulation_cmd())

    def handle_rosbridge_connection_commands(self, command: Command) -> None:
        """
        Handles ROS bridge connection commands, sending them downstream and starting
        a timer if a time limit is specified.

        Args:
            command (Command): Passed to this function. The actual details about
                the structure or content of the `Command` are not provided here,
                but it seems to be related to ROS (Robot Operating System) commands.

        """
        self.send_downstream_cmd(command)

        # NOTE: code below will only execute after all ROS message handler were registered.
        if self.timeout != inf:  # start timer in case a time limit was specified
            self.__timer.start()

    def handle_rosbridge_disconnection_commands(self, command: Command) -> None:
        """
        Handles ROSBridge disconnection commands by canceling any existing timer
        and sending a downstream command to handle the disconnection event.

        Args:
            command (Command): Passed into this function. The exact nature and
                structure of the Command object are not provided, but it appears
                to be some sort of input or data that the function operates on.

        """
        self.__timer.cancel()  # NOTE: this method does not require previous call to 'start()'
        self.send_downstream_cmd(command)

    def handle_upstream_command(self, command: Command) -> None:
        """
        Handles an upstream command by checking its type. If the command type is
        STATUS_CHANGE, it calls the `handle_children_status_change` method to
        handle the status change of children nodes.

        Args:
            command (Command): Expected to be an instance of the class or one of
                its subclasses, representing some type of command with specific
                properties and methods.

        """
        if command.type == CommandType.STATUS_CHANGE:
            self.handle_children_status_change()

    def handle_downstream_command(self, command: Command) -> None:
        """
        Processes incoming commands from downstream systems. Based on the command
        type, it dispatches to separate methods for handling rosbridge
        connection/disconnection and trigger events.

        Args:
            command (Command): Used to determine which specific handling method
                should be invoked based on its type.

        """
        if command.type == CommandType.ROSBRIDGE_CONNECT:
            self.handle_rosbridge_connection_commands(command)
        elif command.type == CommandType.ROSBRIDGE_DISCONNECT:
            self.handle_rosbridge_disconnection_commands(command)
        elif command.type == CommandType.TRIGGER:
            self.send_downstream_cmd(command)
