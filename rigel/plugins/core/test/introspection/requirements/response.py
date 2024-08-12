import threading
from math import inf
from rigel.plugins.core.test.introspection.command import (
    Command,
    CommandBuilder,
    CommandType
)
from .disjoint import DisjointSimulationRequirementNode
from .node import SimulationRequirementNode
from .simple import SimpleSimulationRequirementNode


class ResponseSimulationRequirementNode(SimulationRequirementNode):
    """
    Simulates a node in a simulation requirement tree, handling commands and
    timeouts to assess satisfaction of its children nodes and send appropriate
    upstream or downstream commands.

    Attributes:
        children (List[SimulationRequirementNode]): Initialized to an empty list
            during object creation. It holds references to child nodes that are
            managed by this node.
        father (SimulationRequirementNode|None): Used to represent the parent node
            in a hierarchical structure of requirement nodes.
        timeout (float|int): 0 by default. It represents the time limit for which
            the node should wait before sending a specific command when a child
            node becomes satisfied.
        __timer (threadingTimer): Initialized in the `__init__` method with a
            timeout period specified by the `timeout` parameter. It is responsible
            for triggering the `handle_timeout` method when the timer expires.
        handle_timeout (None): Defined as a method. It cancels the timer, assesses
            the satisfaction of child nodes based on their status, and sends
            appropriate commands to upstream or downstream nodes if necessary.

    """

    def __init__(self, timeout: float = inf) -> None:
        """
        Initializes an object with an empty list of children, no father node by
        default, a specified timeout period, and sets up a timer to trigger the
        handle_timeout method when the timeout expires.

        Args:
            timeout (float): Infinity (`inf`) by default. It represents the timeout
                value in seconds for which the timer will wait before calling the
                `handle_timeout` method if no event occurs.

        """
        self.children = []
        self.father = None
        self.timeout = timeout
        self.__timer = threading.Timer(timeout, self.handle_timeout)

    def __str__(self) -> str:
        """
        Converts its children nodes into strings and concatenates them into a
        single string representation, allowing for easy stringification of the
        node's contents.

        Returns:
            str: A string representation of the object, constructed by concatenating
            the string representations of all child objects in the list `self.children`.

        """
        repr = ''
        for child in self.children:
            repr += f'{str(child)}'
        return repr

    def assess_children_nodes(self) -> bool:
        """
        Checks if both child nodes, anterior and posterior, are satisfied, returning
        True only if they are both satisfied.

        Returns:
            bool: True if both child nodes (`anterior` and `posterio`) satisfy
            their conditions, otherwise it returns False.

        """
        anterior = self.children[0]
        posterior = self.children[1]

        # NOTE: the following assertions are required so that mypy
        # doesn't throw an error related with multiple inheritance.
        # All 'children' are of type CommandHandler and
        # 'satisfied' is a member of SimulationRequirementNode
        # that inherits from CommandHandler.
        assert isinstance(anterior, SimulationRequirementNode)
        assert isinstance(posterior, SimulationRequirementNode)

        return anterior.satisfied and posterior.satisfied

    def handle_timeout(self) -> None:
        """
        Assesses the satisfaction of its children nodes, then sends either status
        change, disconnect, or stop simulation commands upstream and downstream
        depending on whether the requirement is satisfied or not.

        """
        self.satisfied = self.assess_children_nodes()
        if self.satisfied:
            self.send_upstream_cmd(CommandBuilder.build_status_change_cmd())
            self.send_downstream_cmd(CommandBuilder.build_rosbridge_disconnect_cmd())
        else:
            # If the posterior requirement is satisfied before the anterior one
            # then a point of no return if reached and the assessment can be stopped.
            self.send_upstream_cmd(CommandBuilder.build_stop_simulation_cmd())

    def handle_children_status_change(self) -> None:
        """
        Monitors the status changes of its two child nodes, anterior and posterior,
        and updates the node's own status accordingly. It cancels a timer, sends
        disconnect and status change commands to downstream and upstream nodes
        respectively if the children are satisfied.

        """
        anterior = self.children[0]
        posterior = self.children[1]

        # NOTE: the following assertions are required by mypy.
        # Mypy has no notion of the inner structure of requirements ans must be
        # ensured that children to be of type SimpleSimulationRequirementNode
        # (so that fields 'trigger' and 'last_message' may be accessed).
        assert isinstance(anterior, (DisjointSimulationRequirementNode, SimpleSimulationRequirementNode))
        assert isinstance(posterior, (DisjointSimulationRequirementNode, SimpleSimulationRequirementNode))

        if not posterior.trigger:  # true right after anterior requirement was satisfied
            self.send_child_downstream_cmd(posterior, CommandBuilder.build_trigger_cmd(anterior.last_message))

        else:
            self.satisfied = self.assess_children_nodes()
            if self.satisfied:
                self.__timer.cancel()
                self.send_downstream_cmd(CommandBuilder.build_rosbridge_disconnect_cmd())
                self.send_upstream_cmd(CommandBuilder.build_status_change_cmd())

    def handle_trigger(self, command: Command) -> None:
        """
        Notifies the anterior requirement node of an incoming command, ensuring
        that only the anterior node is notified initially, while posterior nodes
        start listening for ROS messages after satisfying their requirements.

        Args:
            command (Command): Expected to be passed from outside the function.
                It represents some kind of instruction or request that needs to
                be handled by this function.

        """
        # Notify only the anterior requirement node.
        # Posterior node must only start listening for ROS messages after it being satisfied.
        anterior = self.children[0]
        self.send_child_downstream_cmd(anterior, command)

    def handle_rosbridge_connection_commands(self, command: Command) -> None:
        """
        Sends downstream commands and starts a timer if a timeout was specified.
        The timer will only be started after all ROS message handlers are registered.

        Args:
            command (Command): Expected to be an instance of a class representing
                ROS (Robot Operating System) commands, which are used for communication
                between ROS nodes.

        """
        self.send_downstream_cmd(command)

        # NOTE: code below will only execute after all ROS message handler were registered.
        if self.timeout != inf:  # start timer in case a time limit was specified
            self.__timer.start()

    def handle_rosbridge_disconnection_commands(self, command: Command) -> None:
        """
        Handles ROSBridge disconnection commands, cancels a timer if it's running,
        assesses the satisfaction of its children nodes, and sends upstream and
        downstream commands accordingly.

        Args:
            command (Command): Passed to the method during its invocation. It
                represents a command that is being handled or processed by the method.

        """
        self.__timer.cancel()  # NOTE: this method does not require previous call to 'start()'

        self.satisfied = self.assess_children_nodes()
        if self.satisfied:
            self.send_upstream_cmd(CommandBuilder.build_status_change_cmd())

        self.send_downstream_cmd(command)

    def handle_upstream_command(self, command: Command) -> None:
        """
        Handles incoming commands and executes specific actions based on the command
        type. If the received command is of type STATUS_CHANGE, it invokes the
        `handle_children_status_change` method to perform subsequent operations.

        Args:
            command (Command): An instance that represents a specific upstream
                command sent to this process or thread. Its type, CommandType,
                determines the action it needs to perform.

        """
        if command.type == CommandType.STATUS_CHANGE:
            self.handle_children_status_change()

    def handle_downstream_command(self, command: Command) -> None:
        """
        Processes downstream commands, specifically ROSBRIDGE connection and
        disconnection requests, as well as trigger events. It dispatches these
        commands to respective handling methods based on their types.

        Args:
            command (Command): Expected to hold data that can be processed by the
                method. The specific details and properties of this command depend
                on its type.

        """
        if command.type == CommandType.ROSBRIDGE_CONNECT:
            self.handle_rosbridge_connection_commands(command)
        elif command.type == CommandType.ROSBRIDGE_DISCONNECT:
            self.handle_rosbridge_disconnection_commands(command)
        elif command.type == CommandType.TRIGGER:
            self.handle_trigger(command)
