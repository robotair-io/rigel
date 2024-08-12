from rigelcore.exceptions import RigelError


class RigelfileNotFoundError(RigelError):
    """
    Defines a custom error type for Rigel applications, indicating that a Rigelfile
    was not found. It provides a base message and an error code (6) to be used
    when this error occurs, suggesting the use of the 'rigel init' command to
    create one.

    Attributes:
        base (str): Set with a default error message. It provides a brief description
            of the error, which will be used as the basis for constructing a
            detailed error message when this exception is raised.
        code (int): 6. It is likely used for error handling purposes, providing a
            unique identifier or code to distinguish this specific error from others.

    """
    base = "Rigelfile was not found. Use 'rigel init' to create one."
    code = 6


class RigelfileAlreadyExistsError(RigelError):
    """
    Defines a custom error type for when a Rigel file already exists. It inherits
    from the `RigelError` class and provides a base message describing the error
    along with an error code of 7. The error can be resolved by using the '--force'
    flag.

    Attributes:
        base (str): Set to a string that contains a default error message for this
            exception. This message explains why the error occurred (a Rigelfile
            already exists) and provides information on how to handle it.
        code (int): 7, which likely represents a specific error code used to
            identify this exception when it occurs.

    """
    base = "A Rigelfile already exists. Use '--force' flag to write over existing Rigelfile."
    code = 7


class UnformattedRigelfileError(RigelError):
    """
    Defines an error type that represents a Rigel file not being properly formatted.
    It inherits from the `RigelError` base class and overrides its `base` attribute
    to specify a custom error message with a `{trace}` placeholder for debugging
    purposes.

    Attributes:
        base (str): Used to define a template for error messages related to
            unformatted Rigelfile errors. The template includes a placeholder
            `{trace}` that can be replaced with actual error trace information.
        code (int): 8. It likely represents a unique error code that can be used
            to identify this specific type of Rigel file formatting error.

    """
    base = "Rigelfile is not properly formatted: {trace}."
    code = 8


class IncompleteRigelfileError(RigelError):
    """
    Defines a custom error type for Rigel, specifying that an incomplete Rigelfile
    is missing a required block. It inherits from `RigelError`, providing a base
    message and code (9) to be used when this error occurs.

    Attributes:
        base (str): Used to define a formatted error message. It takes one placeholder
            variable '{block}' which will be replaced with the actual value when
            the error is raised.
        code (int): 9, indicating a specific error code for this exception. This
            allows clients to handle and differentiate between different types of
            errors when exceptions are raised.

    """
    base = "Incomplete Rigelfile. Missing required block '{block}'."
    code = 9


class EmptyRigelfileError(RigelError):
    """
    Inherits from `RigelError`. It represents an error where a provided Rigel file
    is empty. The base message for this error is "Provided Rigelfile is empty."
    and the error code is 12. This class can be used to handle situations where
    an empty file is not expected or valid.

    Attributes:
        base (str): Set to the string "Provided Rigelfile is empty.". It seems to
            be a template message for error messages related to empty Rigel files.
        code (int): 12. This integer value represents a specific error code used
            to identify this particular error.

    """
    base = "Provided Rigelfile is empty."
    code = 12


class UnsupportedCompilerError(RigelError):
    """
    Defines an error type for RigelError. It represents an exception that occurs
    when an unsupported compiler is encountered, with a message formatted according
    to the `base` attribute and a specific code value of 13.

    Attributes:
        base (str): Set to a string that represents the message format for the
            error. It will be used as a template to construct the actual error
            message when the class is instantiated.
        code (int): 13, indicating the specific error code for this exception.

    """
    base = "Unsupported compiler '{compiler}'."
    code = 13


class UnsupportedPlatformError(RigelError):
    """
    Defines an error type for when a program encounters a platform that is not
    supported. It inherits from the `RigelError` class and takes a `{platform}`
    string as a parameter to create an error message with a specific code number,
    in this case, 14.

    Attributes:
        base (str): Used to define a format string for error messages. It specifies
            the base template for constructing an error message, which includes
            the platform name.
        code (int): 14, which represents a specific error code for this exception.

    """
    base = "Unsupported platform '{platform}'."
    code = 14


class InvalidPlatformError(RigelError):
    """
    Defines an exception that is raised when an invalid platform is used. It
    inherits from the `RigelError` class and has a formatted base string and a
    code attribute. The base string includes the invalid platform name, which is
    passed as a parameter.

    Attributes:
        base (str): Assigned a default error message when an invalid platform is
            detected. The error message includes the '{platform}' placeholder for
            dynamic substitution.
        code (int): 15, which is a unique identifier for this specific error. It
            can be used to handle exceptions in a more organized way.

    """
    base = "An invalid platform was used: '{platform}'."
    code = 15


class PluginNotFoundError(RigelError):
    """
    Defines an exception that is raised when a plugin cannot be loaded due to its
    absence from the system or incorrect installation. It provides a message with
    error details and a corresponding error code (17).

    Attributes:
        base (str): Defined as a template for error messages. It contains a formatted
            string that will be used to generate error messages when a plugin
            cannot be loaded, including the name of the plugin.
        code (int): 17, which represents a specific error code for this exception.
            It is used to identify the type of error that has occurred.

    """
    base = ("Unable to load plugin '{plugin}'. Make sure plugin is installed in your system.\n"
            "For more information on external plugin installation run command 'rigel install --help'.")
    code = 17


class PluginInstallationError(RigelError):
    """
    Defines a custom exception for handling errors during the installation of
    external plugins in Rigel applications. It inherits from the `RigelError` class
    and provides a base message with a placeholder `{plugin}` that can be replaced
    with the specific plugin name at runtime.

    Attributes:
        base (str): Part of its definition, representing a base or generic error
            message that can be used when reporting an error during installation
            of external plugins.
        code (int): 18, indicating a specific error code for the exception raised
            by the plugin installation process.

    """
    base = "An error occurred while installing external plugin {plugin}."
    code = 18


class PluginNotCompliantError(RigelError):
    """
    Specifies an error that occurs when a plugin fails to comply with the Rigel
    plugin protocol. It takes two parameters: the name of the non-compliant plugin
    and the cause of the failure, then formats them into an error message.

    Attributes:
        base (str): Used to define a base message format for error messages, which
            includes placeholders for `{plugin}` and `{cause}` to be replaced with
            actual values.
        code (int): 19. It likely represents a specific error code for this
            exception, which can be used to differentiate it from other exceptions
            or errors.

    """
    base = "Plugin '{plugin}' does not comply with Rigel plugin protocol: {cause}"
    code = 19


class InvalidPluginNameError(RigelError):
    """
    Inherits from `RigelError`. It represents an exception that occurs when a
    plugin name is invalid, and provides a descriptive message with the invalid
    name inserted as a placeholder. The error code is set to 20.

    Attributes:
        base (str): Used as a template for the error message when an instance of
            this class is raised. It contains a placeholder '{plugin}' that will
            be replaced with the actual invalid plugin name.
        code (int): 20, which likely represents a specific error code or status
            code for this custom exception.

    """
    base = "Invalid plugin name '{plugin}'."
    code = 20


class UnknownROSPackagesError(RigelError):
    """
    Defines an error type for Rigel software, which is triggered when certain ROS
    packages are not declared in a Rigelfile. The error message includes the list
    of missing packages and returns a code value of 21.

    Attributes:
        base (str): Used to define a message template for this error type. It
            contains a formatted string with placeholders for variable data,
            specifically a list of packages that were not declared in the Rigelfile.
        code (int): 21, indicating a specific error status or return value for the
            exception raised by this error class.

    """
    base = "The following packages were not declared in the Rigelfile: {packages}."
    code = 21
