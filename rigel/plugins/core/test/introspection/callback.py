from hpl.ast import HplBinaryOperator, HplFieldAccess, HplLiteral, HplThisMessage
from typing import Any, Dict, Callable, List, Union

ROSMessageValue = Any
ROSMessageType = Dict[str, Any]
ROSCallbackType = Callable[[ROSMessageType], bool]


class CallbackGenerator:

    """
    Generates callback functions for ROS (Robot Operating System) messages based
    on a specified operator and operands. The generated callbacks check whether
    the message's field value satisfies the specified condition, returning `True`
    or `False`.

    """
    def __field_path(self, content: Dict[str, Any], path: List[str]) -> Any:
        """
        Recursively traverses a nested dictionary-like object based on a provided
        path and returns the value at the specified location. If the key is missing,
        it raises a KeyError.

        """
        next = path[0]
        try:
            if len(path) == 1:
                return content[next]
            return self.__field_path(content[next], path[1:])
        except KeyError as err:
            raise err

    def generate_callback_equal(self, field: List[str], value: ROSMessageValue) -> ROSCallbackType:
        """
        Generates a callback function that checks if the value of a specified field
        in a ROS message equals to a given value. The callback returns True if the
        condition is met and False otherwise.

        Args:
            field (List[str]): Expected to be a list containing one or more field
                names as strings, which are used to access a value from a ROS message.
            value (ROSMessageValue): Used to compare with the result of
                `__field_path(msg, field)` for equality within the callback function.

        Returns:
            ROSCallbackType: A reference to an anonymous inner function `callback`.
            This callback function checks if the value returned by calling
            `__field_path` on a message with the given field name matches the
            provided value.

        """
        def callback(msg: ROSMessageType) -> bool:
            return bool(self.__field_path(msg, field) == value)
        return callback

    def generate_callback_different(self, field: List[str], value: ROSMessageValue) -> ROSCallbackType:
        """
        Generates a callback function that compares the value of a specified field
        in a ROS message with a given value. The callback returns True if the
        values are different and False otherwise.

        Args:
            field (List[str]): Expected to contain one or more strings representing
                the path to a field in a ROS message.
            value (ROSMessageValue): Expected to be used for comparison with the
                result of calling `self.__field_path(msg, field)` in the generated
                callback function.

        Returns:
            ROSCallbackType: A callback function named `callback`. This callback
            function checks if the message passed to it satisfies the condition
            specified by the input field and value. It returns True if the condition
            is not met, otherwise False.

        """
        def callback(msg: ROSMessageType) -> bool:
            return bool(self.__field_path(msg, field) != value)
        return callback

    def generate_callback_lesser(self, field: List[str], value: ROSMessageValue) -> ROSCallbackType:
        """
        Generates a callback function that checks if the value of a specified field
        in a ROS message is lesser than a given value, and returns True if this
        condition holds.

        Args:
            field (List[str]): Expected to contain a list of strings representing
                the path of a field within a ROS message. The field is used by the
                callback function to retrieve its value from the incoming ROS message.
            value (ROSMessageValue): Used as a comparison value for the lesser
                operator in the callback function. It determines whether the message
                path in the input message is less than the provided value.

        Returns:
            ROSCallbackType: A callback function that takes an argument of type
            ROSMessageType and returns a boolean value indicating whether the value
            of a specified field in a message is less than the given value.

        """
        def callback(msg: ROSMessageType) -> bool:
            return bool(self.__field_path(msg, field) < value)
        return callback

    def generate_callback_lesser_than(self, field: List[str], value: ROSMessageValue) -> ROSCallbackType:
        """
        Generates a callback function that checks if the value of a specified field
        in a ROS message is less than or equal to a given value, and returns True
        if this condition is met.

        Args:
            field (List[str]): Expected to be a list of strings. The strings are
                likely names of fields or paths within ROS messages that will be
                accessed during the callback processing.
            value (ROSMessageValue): Expected to hold a value that will be used
                for comparison with the result of the `__field_path` method.

        Returns:
            ROSCallbackType: A callable function that takes one argument of type
            ROSMessageType and returns a boolean value indicating whether the given
            message field's value is less than or equal to the specified value.

        """
        def callback(msg: ROSMessageType) -> bool:
            return bool(self.__field_path(msg, field) <= value)
        return callback

    def generate_callback_greater(self, field: List[str], value: ROSMessageValue) -> ROSCallbackType:
        """
        Generates a ROS callback function that checks if the value of a specified
        field in an incoming ROS message is greater than a provided value. The
        callback returns True if the condition is met, False otherwise.

        Args:
            field (List[str]): Expected to be a list of strings representing the
                path to a field within ROS messages. The path is used to extract
                a value from the message for comparison.
            value (ROSMessageValue): Expected to hold a comparison value for
                comparing with the result of the `__field_path` method.

        Returns:
            ROSCallbackType: A callable that takes an input message of type
            ROSMessageType and returns a boolean indicating whether the comparison
            between a field path in the message and a given value is greater than
            the value.

        """
        def callback(msg: ROSMessageType) -> bool:
            return bool(self.__field_path(msg, field) > value)
        return callback

    def generate_callback_greater_than(self, field: List[str], value: ROSMessageValue) -> ROSCallbackType:
        """
        Generates a callback function that checks if the value of a specified field
        (given as a list of strings) in a ROS message is greater than or equal to
        a given value, returning True if the condition is met and False otherwise.

        Args:
            field (List[str]): Expected to be a list of strings.
            value (ROSMessageValue): Used to compare with the value obtained from
                the message using the provided field path.

        Returns:
            ROSCallbackType: A callback function that takes a message of type
            ROSMessageType as input and returns a boolean indicating whether the
            specified field's value in the message is greater than or equal to a
            given value.

        """
        def callback(msg: ROSMessageType) -> bool:
            return bool(self.__field_path(msg, field) >= value)
        return callback

    def generate_callback_iff(self, anterior: ROSCallbackType, posterior: ROSCallbackType) -> ROSCallbackType:
        """
        Generates and returns a new callback function that applies two existing
        callback functions, anterior and posterior, with logical "if-then" semantics:
        if anterior is True for a message, then apply posterior to the same message;
        otherwise, return False.

        Args:
            anterior (ROSCallbackType): Expected to be a callback function that
                takes one argument (a message of type ROSMessageType) and returns
                a boolean value indicating whether the message satisfies certain
                conditions.
            posterior (ROSCallbackType): Expected to be a callback function that
                takes a message of type ROSMessageType as an argument and returns
                a value indicating whether the message should be processed further.

        Returns:
            ROSCallbackType: A callable object, specifically a function that takes
            an argument of type ROSMessageType and returns a boolean value. This
            returned function can be used as a callback.

        """
        def callback(msg: ROSMessageType) -> bool:
            """
            Evaluates whether a given message `msg` satisfies the condition specified
            by the `anterior` predicate. If true, it applies the `posterior`
            predicate to `msg`. If both conditions fail, the function returns
            `False`, indicating no match.

            Args:
                msg (ROSMessageType): Expected to be an instance of a message type
                    defined by ROS (Robot Operating System).

            Returns:
                bool: Either the result of calling `posterior` with `msg` as an
                argument or False, depending on whether the condition specified
                by `anterior` is met for `msg`.

            """
            if anterior(msg):
                return posterior(msg)
            return False
        return callback

    def generate_callback_and(self, anterior: ROSCallbackType, posterior: ROSCallbackType) -> ROSCallbackType:
        """
        Generates a new callback function by combining two existing ROS callbacks
        (`anterior` and `posterior`) using the logical AND operator. The resulting
        callback returns True if both input callbacks return True for a given message.

        Args:
            anterior (ROSCallbackType): Expected to be a callback function that
                takes one argument, namely a message of type ROSMessageType, and
                returns a boolean value.
            posterior (ROSCallbackType): Expected to be a function that takes a
                message of type ROSMessageType as input and returns a value of
                unknown type, which is then used in conjunction with the output
                of another callback function.

        Returns:
            ROSCallbackType: A higher-order function that takes messages of type
            ROSMessageType as input, applies two callbacks (anterior and posterior)
            to these messages, and returns the logical AND of their results.

        """
        def callback(msg: ROSMessageType) -> bool:
            """
            Takes a message of type `ROSMessageType`, applies functions `anterior`
            and `posterior` to it, and returns the logical AND (`and`) of the
            results, indicating whether both conditions are satisfied.

            Args:
                msg (ROSMessageType): Expected to be an object or value that
                    conforms to the ROS (Robot Operating System) message type,
                    which represents a data structure for exchanging information
                    between ROS nodes.

            Returns:
                bool: True if both `anterior_value` and `posterior_value` are true,
                otherwise it returns false.

            """
            anterior_value = anterior(msg)
            posterior_value = posterior(msg)
            return anterior_value and posterior_value

        return callback

    def generate_callback_vacuous(self) -> ROSCallbackType:
        """
        Generates a vacuous callback function. The returned function always returns
        True, regardless of its input. This means that it will not filter out any
        messages and will pass all incoming messages to the subscribed node without
        modification or filtering.

        Returns:
            ROSCallbackType: A callable function named `callback`. This returned
            function, when invoked, takes a message of type ROSMessageType as input
            and always returns True.

        """
        def callback(msg: ROSMessageType) -> bool:
            return True
        return callback

    def process_vacuous_truth(self) -> ROSCallbackType:
        """
        Retrieve a dummy callback function to be associated with HplVacuousTruth.
        HplVacuousTruth callbacks simply return True

        :return: A ROS message handler callback function.
        :rtype: ROSCallbackType
        """
        return self.generate_callback_vacuous()

    def process_binary_operator(self, operator: HplBinaryOperator) -> ROSCallbackType:
        """
        Processes binary operators and generates corresponding ROS callback functions
        based on the operator's type, taking into account two operands as arguments.

        Args:
            operator (HplBinaryOperator): Expected to be an instance of a binary
                operator class, representing a comparison or logical operation
                between two operands.

        Returns:
            ROSCallbackType: Generated based on the operation defined by the binary
            operator `operator`. The returned value represents a callback that can
            be used to perform the specified operation.

        """
        arg1 = self.__extract_argument(operator.operand1)
        arg2 = self.__extract_argument(operator.operand2)

        if operator.op == '=':
            return self.generate_callback_equal(arg1, arg2)
        elif operator.op == '!=':
            return self.generate_callback_different(arg1, arg2)
        elif operator.op == '<':
            return self.generate_callback_lesser(arg1, arg2)
        elif operator.op == '<=':
            return self.generate_callback_lesser_than(arg1, arg2)
        elif operator.op == '>':
            return self.generate_callback_greater(arg1, arg2)
        elif operator.op == '>=':
            return self.generate_callback_greater_than(arg1, arg2)
        elif operator.op in ['iff', 'implies']:
            return self.generate_callback_iff(arg2, arg1)
        elif operator.op == 'and':
            return self.generate_callback_and(arg1, arg2)
        else:
            # TODO: create proper exception.
            raise Exception(f'Unsupported operator "{operator}".')

    def __extract_argument(
            self,
            operand: Union[HplBinaryOperator, HplFieldAccess, HplLiteral]
            ) -> Any:
        """
        Extracts an argument from a given operand, which can be either a binary
        operator, a field access or a literal. The extraction process involves
        calling different methods depending on the type of operand.

        """
        if isinstance(operand, HplFieldAccess):
            return self.__extract_field_path(operand)
        else:
            return self.__extract_value(operand)

    def __extract_field_path(self, operand: HplFieldAccess) -> List[str]:
        """
        Extracts and concatenates field paths from an HplFieldAccess object, which
        represents an operand. It splits the message and field names by '.' and
        returns the resulting path as a list of strings.

        """
        path = []
        if operand.message and not isinstance(operand.message, HplThisMessage):
            path += operand.message.field.split('.')
        path += operand.field.split('.')
        return path

    def __extract_value(
            self,
            operand: Union[HplBinaryOperator, HplLiteral]
            ) -> Any:
        """
        Extracts the value from an operand, which can be either a HplLiteral or a
        HplBinaryOperator. For HplLiteral, it checks if the value is an integer,
        float, or boolean and returns it directly; otherwise, it removes quotes
        from the value string.

        """
        if isinstance(operand, HplLiteral):
            # NOTE: numerical primitive data values and 'bool'
            # have a different access mechanism than 'str'
            for t in [int, float, bool]:
                if isinstance(operand.value, t):
                    return operand.value
            return operand.value.value[1:-1]  # for 'str' typed values - remove quotation marks

        elif isinstance(operand, HplBinaryOperator):
            return self.process_binary_operator(operand)
