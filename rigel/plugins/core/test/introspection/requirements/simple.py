import time
from rigel.clients import ROSBridgeClient
from rigel.plugins.core.test.introspection.command import (
    Command,
    CommandBuilder,
    CommandType
)
from typing import Any, Callable, Dict

from .absence import AbsenceSimulationRequirementNode
from .disjoint import DisjointSimulationRequirementNode
from .node import SimulationRequirementNode

ROS_MESSAGE_TYPE = Dict[str, Any]


class SimpleSimulationRequirementNode(SimulationRequirementNode):
    """
    Represents a node in a simulation requirement graph, managing connections to
    ROSBridge, handling messages from a specific topic, and triggering events based
    on message reception and predicates. It also handles upstream and downstream
    commands for connection/disconnection and status changes.

    Attributes:
        children (List[object]): Initialized as an empty list in its constructor.
            It does not have any specific functionality mentioned in this code snippet.
        father (SimpleSimulationRequirementNode|None): Used to store the parent
            node for this requirement, allowing it to track its hierarchical
            relationship with other nodes.
        ros_topic (str): Used to represent a topic name from the Robot Operating
            System (ROS). It stores the name of the ROS topic that this node is
            subscribed to.
        ros_message_type (str): Used to specify the type of ROS message being
            handled. It corresponds to a string representing the fully qualified
            name of the ROS message type, such as 'std_msgs/msg/String'.
        ros_message_callback (Callable): Expected to be a callback function that
            will be invoked whenever a ROS message matching the specified topic
            and message type is received by the node's associated ROS bridge client.
        predicate (str): Not clearly described as what it does. However, based on
            its use in the `__str__` method, it seems to be a string describing a
            condition or requirement that needs to be satisfied by the node.
        last_message (float|int): 0 by default. It represents the timestamp of the
            last received ROS message for this node, updated upon successful
            processing of a message by the associated callback function.
        trigger (bool): Initially set to False. It is used to track whether a
            trigger event has occurred, and it is updated by the `handle_trigger`
            method when a trigger event is detected.

    """

    def __init__(
            self,
            ros_topic: str,
            ros_message_type: str,
            ros_message_callback: Callable,
            predicate: str
            ) -> None:
        """
        Initializes an object with parameters for ROS topic, message type, callback
        function, and predicate. It also sets up attributes for children nodes,
        parent node, last received message timestamp, trigger status, and stores
        these values internally.

        Args:
            ros_topic (str): Used to initialize the ros topic attribute of the
                class instance. This string represents the name of the ROS topic
                that this instance is subscribed to.
            ros_message_type (str): Used to specify the message type for a ROS
                (Robot Operating System) topic.
            ros_message_callback (Callable): Expected to be a callback function
                that handles ROS messages.
            predicate (str): Used to specify a condition that determines when the
                callback function should be triggered.

        """
        self.children = []
        self.father = None

        self.ros_topic = ros_topic
        self.ros_message_type = ros_message_type
        self.ros_message_callback = ros_message_callback
        self.predicate = predicate

        # Store the timestamp when the last message that satisfy this requirement was received.
        self.last_message: float = 0.0

        # Flag that signals when to stop listening for incoming ROS messages.
        self.trigger: bool = False

    def __str__(self) -> str:

        """
        Generates a string representation of an object, describing its ROS topic,
        satisfaction status, and predicate. It uses labels to indicate whether the
        node is satisfied or unsatisfied based on the presence of its father node.

        Returns:
            str: A formatted string representing an instance of the class, describing
            its state and properties.

        """
        if self.father and isinstance(self.father, AbsenceSimulationRequirementNode):
            labels = {False: 'SATISFIED', True: 'UNSATISFIED'}
        else:
            labels = {True: 'SATISFIED', False: 'UNSATISFIED'}

        # TODO: use logger to make a more readable output.
        satisfied_msg = str(self.last_message) if self.last_message else "no ROS message received"
        return f'\n[{self.ros_topic}]\t- {labels[self.satisfied]}\t({satisfied_msg}): {self.predicate}'

    def handle_upstream_command(self, command: Command) -> None:
        pass  # NOTE: nodes of this type don't have children and therefore will never receive upstream commands.

    def handle_downstream_command(self, command: Command) -> None:
        """
        Handles incoming downstream commands by dispatching them to respective
        handlers based on their types: ROSBRIDGE_CONNECT, ROSBRIDGE_DISCONNECT,
        and TRIGGER. Each handler processes the command's data accordingly,
        connecting/disconnecting to a rosbridge or triggering an event.

        Args:
            command (Command): Passed as an argument to this function. It is
                expected to contain information about the command being handled,
                including its type and possibly additional data.

        """
        if command.type == CommandType.ROSBRIDGE_CONNECT:
            self.connect_to_rosbridge(command.data['client'])
        elif command.type == CommandType.ROSBRIDGE_DISCONNECT:
            self.disconnect_from_rosbridge()
        elif command.type == CommandType.TRIGGER:
            self.handle_trigger(command.data['timestamp'])

    def connect_to_rosbridge(self, rosbridge_client: ROSBridgeClient) -> None:
        """
        Registers a message handler with a ROSBridgeClient instance to receive
        messages from a specified topic and handle them using the provided message
        type and handler function.

        Args:
            rosbridge_client (ROSBridgeClient): Expected to be an instance of a
                class representing a ROS (Robot Operating System) bridge client.

        """
        self.__rosbridge_client = rosbridge_client
        if self.__rosbridge_client:
            self.__rosbridge_client.register_message_handler(
                self.ros_topic,
                self.ros_message_type,
                self.message_handler
            )

    def disconnect_from_rosbridge(self) -> None:
        """
        Removes a message handler from a ROSBridge client, indicating that the
        node no longer wants to receive messages from a specific topic with a
        certain type of message.

        """
        if self.__rosbridge_client:
            self.__rosbridge_client.remove_message_handler(
                self.ros_topic,
                self.ros_message_type,
                self.message_handler
            )

    def handle_trigger(self, timestamp: float) -> None:
        """
        Sets a flag indicating a trigger event and, if a recent message was older
        than the current timestamp, disconnects from the ROS bridge and sends a
        command to upstream nodes.

        Args:
            timestamp (float): Required for the function to run. Its purpose is
                to pass a timestamp value that triggers an action within the function.

        """
        self.trigger = True
        if self.last_message > timestamp:
            self.disconnect_from_rosbridge()
            self.send_upstream_cmd(CommandBuilder.build_status_change_cmd())

    def message_handler(self, message: ROS_MESSAGE_TYPE) -> None:
        """
        Processes an incoming ROS message and triggers a series of actions: it
        sets flags indicating satisfaction of requirements, updates timestamps,
        disconnects from the ROS bridge, and sends an upstream command to change
        status.

        Args:
            message (ROS_MESSAGE_TYPE): Passed to the function when it is called.
                It represents the ROS message that triggered this function call.

        """
        if self.ros_message_callback(message):

            self.satisfied = True
            self.last_message = time.time()

            if self.trigger:

                if isinstance(self.father, DisjointSimulationRequirementNode):
                    self.father.last_message = self.last_message

                self.disconnect_from_rosbridge()
                self.send_upstream_cmd(CommandBuilder.build_status_change_cmd())
