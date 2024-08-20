from jinja2 import Template
from pkg_resources import resource_string
from rigel.models.builder import ModelBuilder
from rigel.providers.core import SSHProviderOutputModel
from typing import Optional
from .models import PluginModel


class Renderer:
    """
    Initializes a renderer with distro, workdir, and configuration file, then
    renders a Dockerfile template to an output file based on input parameters,
    including cmake args and ssh keys.

    Attributes:
        distro (str): Initialized during the object's creation. It represents the
            distribution or operating system used by the application.
        workdir (str): Initialized with a string value during object creation. It
            stores the directory path where the rendering process will take place.
        configuration_file (PluginModel): Initialized with a value passed to it
            during object creation. It represents configuration settings for
            rendering Dockerfiles or other build scripts.
        ssh_keys (Dict|None): Initialized with the given `ssh_keys`. If it's
            provided, it initializes the attribute directly; otherwise, it creates
            a default instance using `ModelBuilder`.

    """

    def __init__(
        self,
        distro: str,
        workdir: str,
        configuration_file: PluginModel,
        ssh_keys: Optional[SSHProviderOutputModel]
    ) -> None:
        """
        Initializes an object with four parameters: distro, workdir, configuration_file,
        and ssh_keys. If ssh_keys are provided, it converts them to a dictionary;
        otherwise, it creates empty SSH keys. The method sets these values as
        attributes of the object.

        Args:
            distro (str): Used to initialize an instance variable named `self.distro`.
                It represents a string value that describes the Linux distribution.
            workdir (str): Assigned to an instance variable named `self.workdir`.
                It seems to represent a directory path for working.
            configuration_file (PluginModel): Assigned to an instance variable
                with the same name. This suggests that it represents a configuration
                file for plugins.
            ssh_keys (Optional[SSHProviderOutputModel]): Optional. If provided,
                it is converted to a dictionary; otherwise, an empty dictionary
                is created using ModelBuilder.

        """
        self.distro = distro
        self.workdir = workdir
        self.configuration_file = configuration_file
        if ssh_keys:
            self.ssh_keys = ssh_keys.dict()
        else:
            self.ssh_keys = ModelBuilder(SSHProviderOutputModel).build([], {'keys': []}).dict()

    def render(self, template: str, output: str) -> None:
        """
        Processes and writes a Dockerfile template to a file based on provided
        parameters, such as distribution, working directory, configuration settings,
        CMake arguments, and SSH keys, using a templating engine.

        Args:
            template (str): Required to be passed. It represents a string that
                specifies the name of the Dockerfile template to be used for rendering.
            output (str): Used to specify the name of the file where the rendered
                Dockerfile template will be written.

        """

        # Process CMake arguments for compiler, if any.
        cmake_args = ''
        if self.configuration_file.compiler.cmake_args:
            cmake_args = '--cmake-args'
            for name, value in self.configuration_file.compiler.cmake_args.items():
                cmake_args = cmake_args + f' {name}={value}'

        # Open file template.
        dockerfile_template = resource_string(__name__, f'assets/{template}').decode('utf-8')
        dockerfile_templater = Template(dockerfile_template)

        with open(output, 'w+') as output_file:
            output_file.write(dockerfile_templater.render(
                distro=self.distro,
                workdir=self.workdir,
                configuration=self.configuration_file.dict(),
                cmake_args=cmake_args,
                ssh_keys=self.ssh_keys
            ))
