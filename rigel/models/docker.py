import os
from pydantic import BaseModel, validator
from rigelcore.exceptions import (
    UndeclaredEnvironmentVariableError
)
from rigel.exceptions import (
    UnsupportedCompilerError,
    UnsupportedPlatformError
)
from typing import Any, Dict, List, Optional, Tuple


SUPPORTED_PLATFORMS: List[Tuple[str, str, str]] = [
    # (docker_platform_name, qus_argument, qemu_file_name)
    ('linux/amd64', 'x86_64', ''),
    ('linux/arm64', 'arm', 'qemu-arm')
]


class SSHKey(BaseModel):
    """
    Validates the `value` field based on whether a `file` field is present or not.
    If `file` is False, it checks if the `value` corresponds to an existing
    environment variable; otherwise, it does nothing.

    Attributes:
        file (bool): Initially set to False. It represents a boolean value indicating
            whether the 'value' field concerns a file path rather than an environment
            variable.
        hostname (str): Required for the object. Its purpose is not explicitly
            described, but based on the context of SSH keys, it likely represents
            the hostname or host identifier associated with the key.
        value (str): Validated using a validator function `ensure_valid_value`.
            The validator checks if `value` refers to an environment variable when
            `file` is False, raising an error if the environment variable does not
            exist.

    """

    # NOTE: the validator for field 'value' assumes field 'file' to be already defined.
    # Therefore ensure that field 'file' is always declared before
    # field 'value' in the following list.

    file: bool = False
    hostname: str
    value: str

    @validator('value')
    def ensure_valid_value(cls, v: str, values: Dict[str, Any]) -> str:
        """
        Validates if a given value (v) represents an environment variable and if
        not, checks if it exists as an environment variable. If it does not exist,
        it raises an error. Otherwise, it returns the original value.

        Args:
            v (str): Bound to the value provided for the 'value' key in the input
                data during validation.
            values (Dict[str, Any]): Expected to be passed from the parent class
                or function. It contains key-value pairs where keys are variable
                names and values are their corresponding variable values.

        Returns:
            str: Either unchanged or raised an error, depending on whether it
            corresponds to a valid environment variable.

        """
        if not values['file']:  # ensure value concerns an environment variable
            if not os.environ.get(v):
                raise UndeclaredEnvironmentVariableError(env=v)
        return v


class Registry(BaseModel):
    """
    Defines a data model for storing registry information, comprising three
    attributes: `password`, `server`, and `username`. These attributes are likely
    used to authenticate connections to a server or database, specifying credentials
    and host details.

    Attributes:
        password (str): Required. It represents a string value that corresponds
            to a password for a registry server. The exact usage or validation of
            this password is not specified within the provided code snippet.
        server (str): A string that represents the name or address of a server,
            which is used to connect to for authentication purposes.
        username (str): A property of the model. It represents a string value that
            will be stored when creating or updating an instance of this model.

    """
    password: str
    server: str
    username: str


class DockerSection(BaseModel):
    """
    Defines a model for representing Docker configuration options, including
    required fields like command, distro, and image, as well as optional fields
    like ros_image, apt packages, and compiler. It also provides validation for
    certain fields to ensure compliance with Rigel's supported compilers and platforms.

    Attributes:
        command (str): Required, indicating that it must be specified when creating
            an instance of the class.
        distro (str): Required. It represents a string indicating the Linux
            distribution, which is used to determine the ROS image if `ros_image`
            is not provided.
        image (str): Required. It represents the name or identifier of a Docker image.
        package (str): Required. It represents the name of a ROS package that needs
            to be installed inside the Docker image.
        ros_image (str): Optional. It defaults to the value of the `distro` attribute
            if not provided separately.
        apt (List[str]): Optional, which means it has a default value (an empty
            list). This attribute is used to specify packages that need to be
            installed via apt package manager in the Docker image.
        compiler (str): Initialized with a default value 'catkin_make'. Its
            validation ensures that the specified ROS package compiler is supported
            by Rigel, currently only 'catkin' and 'colcon' are allowed.
        dir (str): Optional, with a default value of an empty string ''. It
            represents the directory path where the Docker image should be created.
        entrypoint (List[str]): Optional. It allows multiple strings representing
            commands to be executed when running a Docker container. The order of
            these commands matters, as they will be executed one after another.
        env (List[Dict[str, Any]]): Optional. It represents a list of environment
            variables that are set within the Docker container. The variable name
            is a string key and the value can be any type (Any).
        hostname (List[str]): Optional. It represents a list of hostnames that can
            be used as environment variables for the Docker container.
        platforms (List[str]): Optional. It specifies a list of architectures for
            which to build the Docker image. The validator function ensures that
            all listed platforms are supported by the current default builder.
        rosinstall (List[str]): Optional. It allows specification of one or more
            ROS packages to install within a Docker container, which can be used
            for building and testing purposes.
        registry (Optional[Registry]): Optional, meaning it may or may not be
            present when creating a new instance of this class.
        run (List[str]): Optional. It represents a list of commands that should
            be executed when running the Docker image.
        ssh (List[SSHKey]): Optional. It represents a list of SSH keys used for
            secure communication with remote Docker registries or servers.
        username (str): Set to 'rigeluser' by default. It represents the username
            used when running commands inside a Docker container.

    """
    # Required fields.
    command: str
    distro: str
    image: str
    package: str

    # Optional fields.
    ros_image: str
    apt: List[str] = []
    compiler: str = 'catkin_make'
    dir: str = ''
    entrypoint: List[str] = []
    env: List[Dict[str, Any]] = []
    hostname: List[str] = []
    platforms: List[str] = []
    rosinstall: List[str] = []
    registry: Optional[Registry] = None
    run: List[str] = []
    ssh: List[SSHKey] = []
    username: str = 'rigeluser'

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initializes an object by calling its superclass's constructor with the
        provided arguments and keyword-arguments. It also sets a 'ros_image'
        attribute if it is not already set, based on a 'distro' argument.

        Args:
            *args (Any): List of positional arguments
            **kwargs (Any): Dictionary of keyword arguments

        """
        if not kwargs.get('ros_image') and kwargs.get('distro'):
            kwargs['ros_image'] = kwargs['distro']
        super().__init__(*args, **kwargs)

    @validator('compiler')
    def validate_compiler(cls, compiler: str) -> str:
        """
        Validates whether a given compiler name is either "catkin_make" or "colcon".
        If not, it raises an UnsupportedCompilerError with the provided compiler
        as an argument; otherwise, it returns the validated compiler name.

        Args:
            compiler (str): Validated to be either 'catkin_make' or 'colcon'. If
                not, an `UnsupportedCompilerError` is raised with the provided
                compiler as an argument.

        Returns:
            str: Either "catkin" or "colcon". The returned value is the validated
            compiler, and if it's valid then it remains unchanged; otherwise, an
            exception is raised.

        """
        # NOTE: At the moment only "catkin" and "colcon" are supported.
        if compiler not in ['catkin_make', 'colcon']:
            raise UnsupportedCompilerError(compiler=compiler)
        return compiler

    @validator('platforms')
    def validate_platforms(cls, platforms: List[str]) -> List[str]:
        """
        Validates a list of platform names against a predefined set of supported
        platforms. If an unsupported platform is found, it raises an
        UnsupportedPlatformError; otherwise, it returns the original list.

        Args:
            platforms (List[str]): Expected to be a list of strings representing
                platform names.

        Returns:
            List[str]: The input list of platforms after validation. If no exceptions
            are raised, it means that all elements in the list are valid platforms
            supported by the system, so the original list is returned unchanged.

        """
        supported_platforms = [p[0] for p in SUPPORTED_PLATFORMS]
        for platform in platforms:
            if platform not in supported_platforms:
                raise UnsupportedPlatformError(platform=platform)
        return platforms


class DockerfileSection(BaseModel):
    """
    Defines a model for representing a Dockerfile section, which is used to build
    an image from a package. It requires three fields: `dockerfile`, `image`, and
    `package`. The optional `registry` field allows specifying the registry where
    the image will be pushed.

    Attributes:
        dockerfile (str): Required. It represents the Dockerfile path or content
            as a string, which defines the instructions for building a Docker image.
        image (str): A required field, meaning it must be provided when creating
            an instance of this class. It represents a Docker image name or ID.
        package (str): Required. It represents a package name, indicating which
            package should be installed or built during the Docker image build process.
        registry (Optional[Registry]): Optional, meaning it can be present or
            absent when an instance of DockerfileSection is created.

    """
    # Required fields.
    dockerfile: str
    image: str
    package: str

    # Optional fields.
    registry: Optional[Registry] = None
