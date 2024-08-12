from pydantic.error_wrappers import ValidationError


class RigelError(Exception):
    """
    Defines a custom exception type, inheriting from Python's built-in `Exception`.
    It takes an optional base message and returns it as a string when converted
    to a string representation using `str()`. This allows for customized error
    messages in Rigel applications.

    Attributes:
        base (str): Initialized by default to 'Generic Rigel error.' It stores a
            descriptive message for each instance of the exception, providing
            additional information about the error.

    """
    base: str

    def __init__(self, base: str = 'Generic Rigel error.'):
        self.base = base

    def __str__(self) -> str:
        return self.base


# TODO: implemente tests for this error class
class ClientError(RigelError):
    """
    Instantiates an error with a custom message, including the name of the client
    and the underlying exception. It inherits from `RigelError`, which is not shown
    in this code snippet. The class sets instance variables for the client and exception.

    Attributes:
        client (str): Initialized with a string value passed to the __init__ method,
            which represents the name or identifier of the client that reported
            the error.
        exception (Exception): Initialized with a specific exception object during
            the construction of the error object. This exception object likely
            holds information about the error that occurred.

    """
    def __init__(self, client: str, exception: Exception) -> None:
        """
        Initializes an object with error information from a client and an exception.
        It sets the parent's `__init__` method with a formatted string, then assigns
        the client name and exception to instance variables.

        Args:
            client (str): Required to be passed when an instance of this class is
                created. It represents the name or description of the client
                reporting the error.
            exception (Exception): Used to pass an instance of an exception class,
                which provides detailed information about the error reported by
                the client.

        """
        super().__init__(f"An error was reported by the {client} client. {exception}")
        self.client = client
        self.exception = exception


# TODO: replace this exception by ClientError instances
class DockerAPIError(RigelError):
    """
    Inherits from the `RigelError` class and overrides its `__init__` method to
    create an error object with a custom message that includes the original exception
    raised while calling the Docker API, along with storing the exception for
    further reference.

    Attributes:
        exception (Exception): Used to store the exception that occurred while
            calling the Docker API. It is then included in the error message for
            further debugging purposes.

    """
    def __init__(self, exception: Exception) -> None:
        """
        Initializes an instance with a specified Exception object. It calls the
        superclass's `__init__` method, passing a formatted string including the
        exception message, and sets the 'exception' attribute to the provided
        Exception object.

        Args:
            exception (Exception): Not None. It represents an error that occurred
                during the call to the Docker API, which will be included in the
                initialization message for this exception object.

        """
        super().__init__(f"An error occured while calling the Docker API: {exception}")
        self.exception = exception


class PydanticValidationError(RigelError):
    """
    Represents an error that occurs when a Pydantic model fails to validate its
    data. It takes a `ValidationError` as input, stores it internally, and initializes
    with an error message describing the validation failure.

    Attributes:
        exception (ValidationError): Initialized to store the error details when
            a Pydantic model fails validation.

    """
    def __init__(self, exception: ValidationError) -> None:
        """
        Initializes an instance by calling its superclass's constructor with a
        custom error message, and then assigns the provided exception to the
        instance's `exception` attribute.

        Args:
            exception (ValidationError): Passed to this method during object
                initialization. It represents an error that occurred while validating
                a Pydantic model.

        """
        super().__init__(f"An error occurred while validating Pydantic model: {exception}.")
        self.exception = exception


class UndeclaredEnvironmentVariableError(RigelError):
    """
    Represents an error that occurs when an environment variable is not declared
    or defined. It initializes with a message indicating the undeclared environment
    variable and provides access to the variable name through the `env` attribute.

    Attributes:
        env (str): Initialized with a string value representing the name of the
            undeclared environment variable during object creation.

    """
    def __init__(self, env: str) -> None:
        """
        Initializes an instance with an error message and stores the name of the
        undeclared environment variable. It inherits from the `RigelError` class,
        indicating that it's a custom error type for handling undefined environment
        variables.

        Args:
            env (str): Used to initialize an instance variable `self.env` with the
                value of the environment variable provided as argument. It is a
                required parameter for the object's initialization.

        """
        super().__init__(f"Environment variable {env} is not declared.")
        self.env = env


class UndeclaredGlobalVariableError(RigelError):
    """
    Specifies an error that occurs when a field is set to have the value of an
    undeclared global variable, providing information about the affected field and
    the undefined global variable.

    Attributes:
        field (str): Used to store a string value representing the name of a field
            where an undeclared global variable has been set.
        var (str): Used to store the name of the undeclared global variable that
            is causing the error.

    """
    def __init__(self, field: str, var: str) -> None:
        """
        Initializes an instance with a given field and variable name, setting its
        parent class (RigelError) with an error message describing the undeclared
        global variable. It also assigns the provided field and variable to the
        instance's attributes.

        Args:
            field (str): Assigned to an instance variable with the same name, `self.field`.
            var (str): Assigned to an instance variable `self.var`. It represents
                the name of an undeclared global variable whose value is being
                used for the given field.

        """
        super().__init__(f"Field '{field}' set to have the value of undeclared global variable '{var}'.")
        self.field = field
        self.var = var


class RigelfileNotFoundError(RigelError):
    """
    Inherits from `RigelError` and defines a custom exception for when a Rigel
    file is not found. The `__init__` method initializes an instance with a specific
    error message, indicating that the user should use the 'rigel init' command
    to create a new Rigel file.

    """
    def __init__(self) -> None:
        super().__init__("Rigelfile was not found. Use 'rigel init' to create one.")


class UnformattedRigelfileError(RigelError):
    """
    Inherits from `RigelError`. It takes a `trace` string as input, formats it
    into an error message, and initializes itself with that error message.

    Attributes:
        trace (str): Initialized with a specific string value in the `__init__`
            method. This attribute stores a detailed error message describing what
            went wrong during the process of parsing the Rigelfile, which is used
            to construct the error message displayed to the user.

    """
    def __init__(self, trace: str) -> None:
        """
        Initializes an instance with a message indicating that a rigelfile is not
        properly formatted, and it stores the trace information leading to this error.

        Args:
            trace (str): Passed to the superclass's constructor. It is expected
                to contain information about why the Rigelfile is not properly
                formatted, which is then included in the error message.

        """
        super().__init__(f"Rigelfile is not properly formatted: {trace}.")
        self.trace = trace


class EmptyRigelfileError(RigelError):
    """
    Inherits from `RigelError`. It represents an error that occurs when a `Rigelfile`
    is provided but contains no data. The `__init__` method initializes the error
    with a custom message "Provided Rigelfile is empty."

    """
    def __init__(self) -> None:
        super().__init__("Provided Rigelfile is empty.")


# TODO: implemen tests for this class
class InvalidValueError(RigelError):
    """
    Inherits from `RigelError` and initializes an error object with a specific
    message, including the invalid field name and value. It sets instance variables
    for the field and value to be used later.

    Attributes:
        field (str): Initialized by the constructor to store the name of the field
            that has passed an invalid value.
        value (str): Initialized with a string that represents the invalid value
            passed for a specific field. This value is used to construct the error
            message and provide additional context about the invalid input.

    """
    def __init__(self, field: str, value: str) -> None:
        """
        Initializes an object with information about an invalid field value. It
        sets the parent's (RigelError) message with the specified field and value,
        then assigns these values as instance variables for further use.

        Args:
            field (str): Required for initializing an object, representing the
                name or label of a field that has passed an invalid value.
            value (str): Used to assign an instance variable of the same name,
                which represents the invalid value that was passed for a given field.

        """
        super().__init__(f"Field '{field}' has passed invalid value '{value}'.")
        self.field = field
        self.value = value


# TODO: replace by InvalidValueError
class UnsupportedCompilerError(RigelError):
    """
    Defines an error type that represents an unsupported compiler. It inherits
    from `RigelError` and provides an initialization method to set the specific
    compiler name, which is used in the error message.

    Attributes:
        compiler (str): Initialized during the `__init__` method with the value
            passed to the constructor, which represents the name of the unsupported
            compiler that raised the error.

    """
    def __init__(self, compiler: str) -> None:
        """
        Initializes an instance with a specified compiler and sets its parent
        class, RigelError, to raise an error message describing the unsupported
        compiler. The method assigns the provided compiler to the instance variable.

        Args:
            compiler (str): Used to set the value of the instance variable
                `self.compiler`. It represents an unsupported compiler.

        """
        super().__init__(f"Unsupported compiler '{compiler}'.")
        self.compiler = compiler


# TODO: replace by InvalidValueError
class UnsupportedPlatformError(RigelError):
    """
    Raises an exception when a specified platform is not supported by the system,
    providing an error message that includes the name of the unsupported platform.
    It inherits from the `RigelError` class and initializes with the platform name.

    Attributes:
        platform (str): Initialized in the constructor (`__init__`) with a value
            passed as an argument to the constructor, representing the platform
            that is unsupported by the system.

    """
    def __init__(self, platform: str) -> None:
        """
        Initializes an instance, taking a platform string as input. It calls the
        parent class's `__init__` with a formatted error message and sets the
        `self.platform` attribute to the provided platform name.

        Args:
            platform (str): Intended to represent the specific operating system
                or device on which the program will run. It is initialized as an
                attribute of the class instance.

        """
        super().__init__(f"Unsupported platform '{platform}'.")
        self.platform = platform


class PluginNotFoundError(RigelError):
    """
    Handles exceptions raised when a plugin cannot be loaded due to its absence
    from the system. It takes the name of the missing plugin as an argument and
    provides a descriptive error message, suggesting installation through the
    command 'rigel install --help'.

    Attributes:
        plugin (str): Initialized with a value passed to the `__init__` method,
            which represents the name of the plugin that could not be loaded.

    """
    def __init__(self, plugin: str) -> None:
        """
        Initializes an instance with a specific error message related to the given
        plugin, then calls the superclass's constructor with this message and
        stores the plugin name for further use.

        Args:
            plugin (str): Expected to be a string representing a specific plugin
                name or identifier.

        """
        base = (f"Unable to load plugin '{plugin}'. Make sure plugin is installed in your system.\n"
                "For more information on plugin installation run command 'rigel install --help'.")
        super().__init__(base)
        self.plugin = plugin


class PluginNotCompliantError(RigelError):
    """
    Raises an exception when a plugin fails to comply with the Rigel plugin protocol,
    providing the name of the non-compliant plugin and the reason for the failure
    as error messages.

    Attributes:
        plugin (str): Initialized during object creation with a string value passed
            as an argument to the class constructor, representing the name of the
            non-compliant plugin.
        cause (str): Initialized during the object creation. It provides additional
            information about why the plugin does not comply with Rigel's plugin
            protocol.

    """
    def __init__(self, plugin: str, cause: str) -> None:
        """
        Initializes an object with two attributes: plugin and cause, setting it
        up to inherit from RigelError's initialization with a specific error message.

        Args:
            plugin (str): Assigned to the instance variable `self.plugin`. It
                represents the name of the plugin that does not comply with the
                Rigel plugin protocol.
            cause (str): Used to specify the reason why the specified plugin does
                not comply with Rigel plugin protocol. It provides additional
                information about the issue.

        """
        super().__init__(f"Plugin '{plugin}' does not comply with Rigel plugin protocol: {cause}")
        self.plugin = plugin
        self.cause = cause
