from pydantic import BaseModel, Extra, validator
from rigel.exceptions import UnsupportedCompilerError
from typing import Any, Dict, List


class Compiler(BaseModel, extra=Extra.forbid):

    # Optional fields
    """
    Validates and represents a compiler, specifically for building packages using
    catkin or colcon. It has properties for the compiler's name and additional
    CMake arguments. The `validate_compiler` method checks if the provided name
    is either "catkin_make" or "colcon", raising an error otherwise.

    Attributes:
        name (str): Initialized with a default value of 'catkin_make'. It is
            validated using the `validate_compiler` method to ensure it is either
            'catkin_make' or 'colcon'.
        cmake_args (Dict[str, str]): Initialized with an empty dictionary. It
            allows storing key-value pairs as arguments for CMake commands.

    """
    name: str = 'catkin_make'
    cmake_args: Dict[str, str] = {}

    @validator('name')
    def validate_compiler(cls, name: str) -> str:
        """Ensure that the specified ROS package compiler used is supported by Rigel.

        :type name: string
        :param name: ROS package compiler.
        """
        # NOTE: At the moment only "catkin" and "colcon" are supported.
        if name not in ['catkin_make', 'colcon']:
            raise UnsupportedCompilerError(name)
        return name


class PluginModel(BaseModel, extra=Extra.forbid):
    """A plugin that creates a ready-to-use Dockerfile for an existing ROS package.

    :type command: string
    :cvar command: The command to be executed once a container starts executing.
    :type apt: List[string]
    :cvar apt: The name of dependencies to be installed using APT.
    :type compiler: Compiler
    :cvar compiler: The tool with which to compile the containerized ROS workspace. Default value is 'catkin_make'.
    :type entrypoint: List[string]
    :cvar entrypoint: A list of commands to be run while executing the entrypoint script.
    :type env: List[Dict[str, Any]]
    :cvar env: A list of environment variables to be set inside the Docker image.
    :type rosinstall: List[string]
    :cvar rosinstall: A list of all required .rosinstall files.
    :type ros_image: string
    :cvar ros_image: The official ROS Docker image to use as a base for the new Docker image.
    :type docker_run: List[string]
    :cvar docker_run: A list of commands to be executed while building the Docker image.
    :type pip: List[string]
    :cvar pip: A list of python dependencies to be installed using pip.
    :type python_requirements_files: List[string]
    :cvar python_requirements_files: A list of python requirements.txt file paths.
    :type username: string
    :cvar username: The desired username. Defaults to 'user'.
    """
    # Optional fields.
    compiler: Compiler
    command: str = ''
    apt: List[str] = []

    entrypoint: List[str] = []
    env: List[Dict[str, Any]] = []
    rosinstall: List[str] = []
    ros_image: str
    docker_run: List[str] = []
    pip: List[str] = []
    python_requirements_files: List[str] = []
    username: str = 'rigeluser'

    def __init__(self, *args: Any, **kwargs: Any) -> None:

        """
        Initializes an instance with optional keyword arguments. If no 'ros_image'
        argument is provided, it defaults to a string formatted from 'distro'. The
        'distro' keyword is then removed from the arguments. This initialization
        process calls the superclass's constructor (`super().__init__(*args, **kwargs)`).

        Args:
            *args (Any): List of positional arguments
            **kwargs (Any): Dictionary of keyword arguments

        """
        if not kwargs.get('ros_image'):
            kwargs['ros_image'] = f'ros:{kwargs["distro"]}'
        del kwargs['distro']

        super().__init__(*args, **kwargs)
