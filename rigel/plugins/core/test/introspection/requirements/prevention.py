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


class PreventionSimulationRequirementNode(SimulationRequirementNode):
    """
    Represents a node in a simulation requirement tree, which assesses child nodes'
    satisfaction and sends commands based on their status to upstream or downstream
    nodes. It also handles timeout events and ROS bridge connection/disconnection
    commands.

    Attributes:
        children (List[SimulationRequirementNode]): Initialized in the constructor
            to be an empty list. It stores child nodes of the node.
        father (SimulationRequirementNode|None): Set to None by default. It seems
            that this attribute represents a reference to the parent node in the
            simulation requirement tree structure.
        timeout (float|inf): 0 by default, representing a timer that starts when
            a ROS bridge connection command is received and stops after the specified
            timeout has expired.
        __timer (threadingTimer): Initialized with a timeout value in its constructor.
            It starts when ROSbridge connection commands are received if a time
            limit was specified. The timer triggers the `handle_timeout` method
            after the timeout period.
        handle_timeout (None): Invoked by the timer when a timeout occurs. It
            assesses the status of child nodes, updates its own satisfied state
            based on their status, and sends relevant commands upstream or downstream
            accordingly.

    """

    def __init__(self, timeout: float = inf) -> None:
        """
        Initializes an object with its attributes, including children, father node,
        and timeout value. It also sets up a timer to handle timeouts using a
        separate thread. The timer is scheduled to trigger the `handle_timeout`
        method after the specified timeout period.

        Args:
            timeout (float): 0 by default, which indicates that no timeout should
                occur. The timer is set with this value, which means when the time
                exceeds this duration, the method `handle_timeout` will be called.

        """
        self.children = []
        self.father = None
        self.timeout = timeout
        self.__timer = threading.Timer(timeout, self.handle_timeout)

    def __str__(self) -> str:
        """
        Converts its children into strings and concatenates them, returning the
        resulting string representation. This allows for easy debugging or logging
        of the node's structure by converting it to a human-readable format.

        Returns:
            str: A string representation of the object, constructed by concatenating
            the string representations of all its children objects.

        """
        repr = ''
        for child in self.children:
            repr += f'{str(child)}'
        return repr

    def assess_children_nodes(self) -> bool:
        """
        Evaluates the satisfaction state of two child nodes, anterior and posterior,
        both being instances of SimulationRequirementNode. It returns True if the
        anterior node is satisfied and the posterior node is not, indicating a
        specific condition.

        Returns:
            bool: Determined by the satisfaction status of two children nodes
            (`anterior` and `posterior`) of a parent node. The return value is
            `True` if `anterior` is satisfied and `posterior` is not, otherwise
            it's `False`.

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

        return anterior.satisfied and not posterior.satisfied

    def handle_timeout(self) -> None:
        """
        Assesses satisfaction status by evaluating children nodes, and then sends
        appropriate commands to upstream and downstream based on this status,
        either for a normal simulation stop or for a simulation restart.

        """
        self.satisfied = self.assess_children_nodes()
        if self.satisfied:
            self.send_upstream_cmd(CommandBuilder.build_status_change_cmd())
            self.send_downstream_cmd(CommandBuilder.build_rosbridge_disconnect_cmd())
        else:
            self.send_upstream_cmd(CommandBuilder.build_stop_simulation_cmd())

    def handle_children_status_change(self) -> None:
        """
        Handles status changes in its child nodes, specifically
        DisjointSimulationRequirementNodes or SimpleSimulationRequirementNodes.

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

        # If the posterior requirement is satisfied after the anterior requirement
        # then a point of no return if reached and the assessment can be stopped.
        else:  # anterior.satisfied and posterior.satisfied
            self.send_upstream_cmd(CommandBuilder.build_stop_simulation_cmd())

    def handle_trigger(self, command: Command) -> None:
        """
        Notifies the first child node (`anterior`) of a command and sends it
        downstream, ensuring that only this node is triggered while posterior nodes
        start listening for ROS messages after their satisfaction requirements are
        met.

        Args:
            command (Command): Expected to be an instance of the Command class or
                its subclass. It represents a command that triggers a process, and
                it's used to notify and interact with the anterior requirement node.

        """
        # Notify only the anterior requirement node.
        # Posterior node must only start listening for ROS messages after it being satisfied.
        anterior = self.children[0]
        self.send_child_downstream_cmd(anterior, command)

    def handle_rosbridge_connection_commands(self, command: Command) -> None:
        """
        Sends a downstream command and starts a timer if a time limit has been
        specified, ensuring that subsequent code execution is conditional on ROS
        message handlers being registered.

        Args:
            command (Command): Expected to be an object representing a ROS (Robot
                Operating System) message command.

        """
        self.send_downstream_cmd(command)

        # NOTE: code below will only execute after all ROS message handler were registered.
        if self.timeout != inf:  # start timer in case a time limit was specified
            self.__timer.start()

    def handle_rosbridge_disconnection_commands(self, command: Command) -> None:
        """
        Cancels a timer, assesses the satisfaction status of child nodes, sends a
        command to update upstream simulation, and sends the received command
        downstream after ROS bridge disconnection commands are handled.

        Args:
            command (Command): Required for execution of this method. It is used
                as an argument to send_downstream_cmd method at the end of the
                function body.

        """
        self.__timer.cancel()  # NOTE: this method does not require previous call to 'start()'

        self.satisfied = self.assess_children_nodes()
        if self.satisfied:
            self.send_upstream_cmd(CommandBuilder.build_status_change_cmd())

        self.send_downstream_cmd(command)

    def handle_upstream_command(self, command: Command) -> None:
        """
        Processes incoming commands from an upstream component, specifically
        handling status change commands by invoking the `handle_children_status_change`
        method to handle changes in the children's statuses.

        Args:
            command (Command): Expected to hold an instance that represents an
                upstream command. The type of this command is specified by its
                attribute `type`.

        """
        if command.type == CommandType.STATUS_CHANGE:
            self.handle_children_status_change()

    def handle_downstream_command(self, command: Command) -> None:
        """
        Handles downstream commands by routing them to respective methods based
        on their command types: ROSBRIDGE connection, disconnection, and trigger
        actions.

        Args:
            command (Command): Expected to be an instance of a class that represents
                a command sent downstream. Its value determines which type of
                command handling logic should be executed.

        """
        if command.type == CommandType.ROSBRIDGE_CONNECT:
            self.handle_rosbridge_connection_commands(command)
        elif command.type == CommandType.ROSBRIDGE_DISCONNECT:
            self.handle_rosbridge_disconnection_commands(command)
        elif command.type == CommandType.TRIGGER:
            self.handle_trigger(command)
