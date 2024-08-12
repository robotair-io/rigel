from pydantic import BaseModel, Extra, validator
from rigel.exceptions import UnsupportedCompilerError
from typing import Any, Dict, List


class Compiler(BaseModel, extra=Extra.forbid):

    # Optional fields
    """
    Defines a model for compiler settings with validation. It has two attributes:
    `name`, which must be either `'catkin_make'` or `'colcon'`, and `cmake_args`,
    a dictionary for additional arguments. The `validate_compiler` method ensures
    the correctness of the `name`.

    Attributes:
        name (str): Initialized with a default value of 'catkin_make'. It is
            validated by the `validate_compiler` method to ensure that it is either
            'catkin_make' or 'colcon'.
        cmake_args (Dict[str, str]): Initialized as an empty dictionary. It allows
            the user to specify key-value pairs for CMake arguments specific to
            each compiler instance.

    """
    name: str = 'catkin_make'
    cmake_args: Dict[str, str] = {}

    @validator('name')
    def validate_compiler(cls, name: str) -> str:
        """
        Validates the given compiler name against a list of supported names
        ("catkin_make" and "colcon"). If the name is not supported, it raises an
        UnsupportedCompilerError; otherwise, it returns the validated name.

        Args:
            name (str): Required for validation. It represents the name of a
                compiler, specifically referring to "catkin" or "colcon".

        Returns:
            str: The validated compiler name, i.e., either 'catkin' or 'colcon'.
            If the input name is not supported, it raises an exception.

        """
        # NOTE: At the moment only "catkin" and "colcon" are supported.
        if name not in ['catkin_make', 'colcon']:
            raise UnsupportedCompilerError(name)
        return name


class PluginModel(BaseModel, extra=Extra.forbid):
    """
    Defines a data model for plugins with various optional fields representing
    configuration settings and dependencies. It sets default values for certain
    fields, such as `ros_image`, based on other parameters provided during initialization.

    Attributes:
        compiler (Compiler): Optional.
        command (str): Initialized with a default value of an empty string. It
            allows optional specification of a command for the plugin.
        apt (List[str]): Used to store a list of package names that can be installed
            using the Advanced Package Tool (APT).
        entrypoint (List[str]): Used to store a list of entry points for a plugin.
        env (List[Dict[str, Any]]): Optional. It represents a list of environment
            variables, where each variable is represented as a dictionary with
            keys 'name' and 'value'.
        rosinstall (List[str]): Used to store a list of strings representing ROS
            (Robot Operating System) installable packages.
        ros_image (str): Initialized with a default value when no explicit value
            is provided for it in the model's constructor. The default value is
            constructed based on the 'distro' attribute.
        docker_run (List[str]): Used to specify a list of strings representing
            Docker run commands.
        python_dependencies (List[str]): Used to store a list of Python dependencies
            required by the plugin. It is initialized as an empty list during
            object creation.
        python_requirements_file (List[str]): Optional. It represents a list of
            file paths to Python requirements files for the plugin.
        username (str): Set to 'rigeluser' by default. It can be overridden when
            initializing an instance of the model if a different value is provided.

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
    python_dependencies: List[str] = []
    python_requirements_file: List[str] = []
    username: str = 'rigeluser'

    def __init__(self, *args: Any, **kwargs: Any) -> None:

        """
        Initializes its object by calling the parent's `__init__` method with the
        provided arguments and keyword arguments. It modifies the keyword arguments
        to ensure a 'ros_image' is present and removes the 'distro' keyword argument.

        Args:
            *args (Any): List of positional arguments
            **kwargs (Any): Dictionary of keyword arguments

        """
        if not kwargs.get('ros_image'):
            kwargs['ros_image'] = f'ros:{kwargs["distro"]}'
        del kwargs['distro']

        super().__init__(*args, **kwargs)
