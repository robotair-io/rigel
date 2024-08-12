import threading
from math import inf
from rigel.plugins.core.test.introspection.command import (
    Command,
    CommandBuilder,
    CommandType
)
from .node import SimulationRequirementNode


class RequirementSimulationRequirementNode(SimulationRequirementNode):
    """
    Simulates a requirement node that monitors and responds to ROS bridge
    connection/disconnection, status changes, and timeouts. It assesses its children
    nodes' statuses, sends commands upstream and downstream accordingly, and handles
    timer events.

    Attributes:
        children (List[SimulationRequirementNode]|List[CommandHandler]): Initialized
            to an empty list during object creation.
        father (SimulationRequirementNode|None): Set to None by default. It
            represents a reference to the parent node in the simulation requirement
            tree structure.
        timeout (float|inf): Set by default to infinity (inf). It represents the
            maximum time allowed for a simulation requirement node to remain unsatisfied.
        __timer (threadingTimer|None): Initialized with a timeout value specified
            during initialization. It starts when a ROSBRIDGE connection command
            is received, canceling itself when a disconnection or status change occurs.
        handle_timeout (None): A method that cancels any ongoing simulation if a
            timeout has occurred but the requirement has not been satisfied. It
            sends an upstream command to stop the simulation.

    """

    def __init__(self, timeout: float = inf) -> None:
        """
        Initializes an instance with a list to store children, a reference to its
        father node, a timeout value, and starts a timer that calls the handle_timeout
        method when the specified timeout is reached.

        Args:
            timeout (float): 0 by default. It represents the time in seconds after
                which the handle_timeout method will be executed if no other
                operation has been performed on the object during this period.

        """
        self.children = []
        self.father = None
        self.timeout = timeout
        self.__timer = threading.Timer(timeout, self.handle_timeout)

    def __str__(self) -> str:
        """
        Recursively concatenates the string representations of its child nodes
        into a single string, providing a human-readable representation of the
        node's subtree.

        Returns:
            str: A string representation of the object, constructed by concatenating
            the string representations of its child objects.

        """
        repr = ''
        for child in self.children:
            repr += f'{str(child)}'
        return repr

    def assess_children_nodes(self) -> bool:
        """
        Checks the satisfaction status of two child nodes, anterior and posterior,
        and sends an upstream command to stop simulation if only one is satisfied.
        It returns a boolean indicating whether both children are satisfied or not.

        Returns:
            bool: True if both `anterior` and `posterior` nodes are satisfied,
            False otherwise. The satisfaction status determines whether to send a
            stop simulation command upstream or not.

        """
        posterior = self.children[0]
        anterior = self.children[1]

        # NOTE: the following assertions are required so that mypy
        # doesn't throw an error related with multiple inheritance.
        # All 'children' are of type CommandHandler and
        # 'satisfied' is a member of SimulationRequirementNode
        # that inherits from CommandHandler.
        assert isinstance(anterior, SimulationRequirementNode)
        assert isinstance(posterior, SimulationRequirementNode)

        if anterior.satisfied and not posterior.satisfied:
            self.send_upstream_cmd(CommandBuilder.build_stop_simulation_cmd())
        return posterior.satisfied and anterior.satisfied

    def handle_children_status_change(self) -> None:
        """
        Updates its own state and sends commands to other nodes when there are
        changes in the status of its child nodes. It cancels a timer, disconnects
        from a Rosbridge server, and sends commands to upstream and downstream nodes.

        """
        if self.assess_children_nodes():  # only consider state changes
            self.satisfied = True

            self.__timer.cancel()
            self.send_downstream_cmd(CommandBuilder.build_rosbridge_disconnect_cmd())
            self.send_upstream_cmd(CommandBuilder.build_status_change_cmd())

    def handle_timeout(self) -> None:
        """
        Sends a stop simulation command to an upstream component if the requirement
        has not been satisfied. This action is triggered when a timeout occurs.

        """
        if not self.satisfied:
            self.send_upstream_cmd(CommandBuilder.build_stop_simulation_cmd())

    def handle_rosbridge_connection_commands(self, command: Command) -> None:
        """
        Processes ROS bridge connection commands and sends downstream commands to
        unknown destinations. If a timeout is set, it starts a timer. This method
        executes after all ROS message handlers are registered.

        Args:
            command (Command): Expected to be an instance of a class that represents
                a command. The exact nature of this command is not specified.

        """
        self.send_downstream_cmd(command)

        # NOTE: code below will only execute after all ROS message handler were registered.
        if self.timeout != inf:  # start timer in case a time limit was specified
            self.__timer.start()

    def handle_rosbridge_disconnection_commands(self, command: Command) -> None:
        """
        Cancels an ongoing timer and sends a downstream command when ROSBridge
        disconnection commands are received.

        Args:
            command (Command): Passed as an argument. Its exact definition or
                implementation is not provided, but it appears to represent some
                kind of command or instruction being handled by this method.

        """
        self.__timer.cancel()  # NOTE: this method does not require previous call to 'start()'

        self.send_downstream_cmd(command)

    def handle_upstream_command(self, command: Command) -> None:
        """
        Processes an upstream command, specifically handling commands of type
        STATUS_CHANGE by calling the `handle_children_status_change` method.

        Args:
            command (Command): Expected to be an object that represents a command
                of some kind, specifically one with a type attribute.

        """
        if command.type == CommandType.STATUS_CHANGE:
            self.handle_children_status_change()

    def handle_downstream_command(self, command: Command) -> None:
        """
        Handles incoming downstream commands by delegating processing to specific
        methods based on the command type, which can be ROSBRIDGE_CONNECT,
        ROSBRIDGE_DISCONNECT, or TRIGGER.

        Args:
            command (Command): Expected to contain information about an incoming
                command from downstream, such as its type and possibly additional
                data specific to that type of command.

        """
        if command.type == CommandType.ROSBRIDGE_CONNECT:
            self.handle_rosbridge_connection_commands(command)
        if command.type == CommandType.ROSBRIDGE_DISCONNECT:
            self.handle_rosbridge_disconnection_commands(command)
        elif command.type == CommandType.TRIGGER:
            self.send_downstream_cmd(command)
