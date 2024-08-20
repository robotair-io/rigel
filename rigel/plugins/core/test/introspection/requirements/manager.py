import threading
from .node import SimulationRequirementNode
from rigel.clients import ROSBridgeClient
from rigel.plugins.core.test.introspection.command import (
    Command,
    CommandBuilder,
    CommandType
)
from typing import List


class SimulationRequirementsManager(SimulationRequirementNode):
    """
    Manages simulation requirements and their children, connecting to a ROSBridge
    client, starting/stopping timers, sending commands downstream, assessing child
    nodes' satisfaction, and handling state changes and stop simulations requests.

    Attributes:
        children (List[SimulationRequirementNode]): Initialized as an empty list
            during object creation.
        father (SimulationRequirementNode|None): Initialized to None. It represents
            the parent node in a tree-like structure, where children are added
            using the add_child method.
        finished (bool): Initially set to False. It indicates whether a simulation
            has finished or not, which can be changed by calling the stop_simulation
            method.
        __introspection_started (bool): Initially set to False when a simulation
            starts. It tracks whether the introspection process has been started
            or not.
        __start_timer (threadingTimer|None): Initialized to a Timer object that
            calls the `handle_start_timeout` method after a specified time
            (min_timeout) has passed.
        handle_start_timeout (NoneNone): Scheduled to be called after a certain
            period (min_timeout) has passed. It sets `__introspection_started` to
            True, sends a trigger command downstream, and calls the
            `handle_children_status_change` method.
        __stop_timer (threadingTimer|None): Initialized with a timeout value equal
            to `max_timeout`. It triggers the `handle_stop_timeout` method when
            the timer expires, which stops the simulation.
        handle_stop_timeout (None): Associated with a timer that starts after a
            certain timeout period (max_timeout).

    """

    def __init__(self, max_timeout: float, min_timeout: float = 0.0) -> None:
        """
        Initializes an instance by setting up timers for starting and stopping
        timeouts, maintaining lists of children nodes and a father node, tracking
        whether the simulation has finished, and keeping track of introspection
        start status.

        Args:
            max_timeout (float): Passed to the Timer object for stopping the
                execution after a maximum allowed time.
            min_timeout (float): 0.0 by default. It represents the minimum timeout
                period for starting a timer that will trigger the `handle_start_timeout`
                method.

        """
        self.children = []
        self.father = None
        self.finished = False

        self.__introspection_started = False

        self.__start_timer = threading.Timer(min_timeout, self.handle_start_timeout)
        self.__stop_timer = threading.Timer(max_timeout, self.handle_stop_timeout)

    def add_child(self, child: SimulationRequirementNode) -> None:
        """
        Adds a new child node to its list of children, establishing a hierarchical
        relationship between parent and child nodes by setting the father attribute
        of the child node to itself (the manager).

        Args:
            child (SimulationRequirementNode): Expected to be an instance of this
                class. It represents the child node that will be added to the
                current object's list of children.

        """
        child.father = self
        self.children.append(child)

    def add_children(self, children: List[SimulationRequirementNode]) -> None:
        """
        Iterates over a list of child nodes, each representing a simulation
        requirement, and adds each one as a direct child to its parent node using
        the inherited `add_child` method.

        Args:
            children (List[SimulationRequirementNode]): Expected to contain multiple
                SimulationRequirementNode objects that are going to be added as
                child nodes to the current node.

        """
        for child in children:
            self.add_child(child)

    def __str__(self) -> str:
        """
        Constructs a string representation of its own simulation requirements by
        recursively calling itself on child nodes, appending each result with a
        newline character, and returning the combined string if there are children;
        otherwise, it returns a default message.

        Returns:
            str: Either a formatted string representation of all child objects
            indented with newline characters, if `self.children` is not empty, or
            the message 'No simulation requirements were provided.' otherwise.

        """
        if self.children:
            repr = ''
            for child in self.children:
                repr += f'{str(child)}\n'
            return repr
        else:
            return 'No simulation requirements were provided.'

    def connect_to_rosbridge(self, rosbridge_client: ROSBridgeClient) -> None:
        """
        Establishes a connection to a ROSBridge client by sending a command through
        downstream communication, and then starts two timers: start_timer and stop_timer.

        Args:
            rosbridge_client (ROSBridgeClient): Expected to be an instance of the
                ROSBridgeClient class, which represents a client that connects to
                a ROS bridge.

        """
        # self.send_downstream_cmd(CommandBuilder.build_trigger_cmd())
        self.send_downstream_cmd(CommandBuilder.build_rosbridge_connect_cmd(rosbridge_client))

        self.__start_timer.start()
        self.__stop_timer.start()

    def disconnect_from_rosbridge(self) -> None:
        """
        Disconnects from a ROS bridge by building a command to do so using
        CommandBuilder and sending it downstream through send_downstream_cmd.

        """
        command = CommandBuilder.build_rosbridge_disconnect_cmd()
        self.send_downstream_cmd(command)

    def stop_timers(self) -> None:
        """
        Cancels two timers, __start_timer and __stop_timer, likely used to manage
        simulation timing requirements.

        """
        self.__start_timer.cancel()
        self.__stop_timer.cancel()

    def stop_simulation(self) -> None:
        """
        Disconnects from ROSBridge and sets the `finished` flag to True, indicating
        the simulation has been stopped.

        """
        self.disconnect_from_rosbridge()
        self.finished = True

    def handle_start_timeout(self) -> None:
        """
        Triggers a command to start the simulation, sets an introspection flag to
        True, and then handles changes in child status when the simulation starts
        or times out.

        """
        # Ensure that manager detects if all children requirements are
        # already satisfied whenever the simulation starts.
        # For this emulate reception of a STATUS_CHANGE command.

        self.__introspection_started = True
        self.send_downstream_cmd(CommandBuilder.build_trigger_cmd())
        self.handle_children_status_change()

    def handle_stop_timeout(self) -> None:
        self.stop_simulation()

    def assess_children_nodes(self) -> bool:
        """
        Checks if all child nodes (CommandHandler instances) have been satisfied,
        returning True only if all are satisfied; otherwise, it returns False. The
        satisfaction state is determined by the `satisfied` attribute of each child
        node.

        Returns:
            bool: True if all children nodes are satisfied, i.e., their `satisfied`
            property is True; otherwise, it returns False.

        """
        # if self.children:
        if self.children and self.__introspection_started:
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

            # return False not in [child.satisfied for child in self.children]
        return False  # when no requirements are specified run simulation until timeout is reached.

    def handle_children_status_change(self) -> None:
        """
        Updates its internal state (`satisfied`) based on changes in child nodes'
        statuses and performs corresponding actions: stopping timers if satisfied,
        and simulation if previously unsatisfied.

        """
        if self.assess_children_nodes() != self.satisfied:  # only consider state changes

            self.satisfied = not self.satisfied
            # Stop simulation once all requirements are satisfied.
            if self.satisfied:
                self.stop_timers()
                self.stop_simulation()

    def handle_stop_simulation(self) -> None:
        """
        Stops all timers and simulation processes.

        """
        self.stop_timers()
        self.stop_simulation()

    def handle_upstream_command(self, command: Command) -> None:
        """
        Handles incoming commands from an upstream source, executing specific
        actions based on the command type: either updating children's statuses if
        the command is a STATUS_CHANGE or stopping the simulation if it's a STOP_SIMULATION.

        Args:
            command (Command): Expected to be an instance of the `Command` class,
                representing an upstream command that has been received by the
                system or application.

        """
        if command.type == CommandType.STATUS_CHANGE:
            self.handle_children_status_change()
        elif command.type == CommandType.STOP_SIMULATON:
            self.handle_stop_simulation()
