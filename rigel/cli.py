import click
import os
import signal
import sys
from pathlib import Path
from rigelcore.clients import DockerClient
from rigelcore.exceptions import RigelError
from rigelcore.loggers import ErrorLogger, MessageLogger
from rigelcore.simulations import SimulationRequirementsParser
from rigelcore.simulations.requirements import SimulationRequirementsManager
from rigel.exceptions import (
    RigelfileAlreadyExistsError,
    UnknownROSPackagesError
)
from rigel.files import (
    Renderer,
    RigelfileCreator,
    YAMLDataDecoder,
    YAMLDataLoader
)
from rigel.models import DockerSection, Rigelfile, PluginSection
from rigel.models.docker import SUPPORTED_PLATFORMS, DockerfileSection
from rigel.plugins import Plugin, PluginInstaller
from rigel.plugins.loader import PluginLoader
from rigelcore.models import ModelBuilder
from typing import Any, Dict, List, Tuple, Union


MESSAGE_LOGGER = MessageLogger()


def handle_rigel_error(err: RigelError) -> None:
    """
    Logs an instance of `RigelError` using an `ErrorLogger` object and then
    terminates the program with a specific exit code corresponding to the error.

    Args:
        err (RigelError): Required for the function to run successfully.

    """
    error_logger = ErrorLogger()
    error_logger.log(err)
    sys.exit(err.code)


def create_folder(path: str) -> None:
    """
    Create a folder in case it does not exist yet.

    :type path: string
    :param path: Path of the folder to be created.
    """
    Path(path).mkdir(parents=True, exist_ok=True)


# TODO: change return type to Rigelfile
def parse_rigelfile() -> Any:
    """
    Loads a YAML file named 'Rigelfile' using `YAMLDataLoader`, decodes its content
    with `YAMLDataDecoder`, and then uses it to build an object with `ModelBuilder`.
    The result is returned as the output of this function.

    Returns:
        Any: An instance of a class representing a model, built using data loaded
        from a YAML file and decoded by a YAML decoder.

    """
    loader = YAMLDataLoader('./Rigelfile')
    decoder = YAMLDataDecoder()

    yaml_data = decoder.decode(loader.load())

    builder = ModelBuilder(Rigelfile)
    return builder.build([], yaml_data)


def rigelfile_exists() -> bool:
    """
    Verify if a Rigelfile is present.

    :rtype: bool
    :return: True if a Rigelfile is found at the current directory. False otherwise.
    """
    return os.path.isfile('./Rigelfile')


def load_plugin(
        plugin: PluginSection,
        application_args: List[Any],
        application_kwargs: Dict[str, Any]
        ) -> Tuple[str, Plugin]:
    """
    Loads an external plugin into a Rigel application, overriding its command-line
    arguments and keyword arguments with those provided by the application if
    specified. It logs a warning message and handles errors during the loading process.

    Args:
        plugin (PluginSection): Expected to be an instance of a class representing
            a plugin.
        application_args (List[Any]): Used to pass command-line arguments to an
            external plugin. It allows the plugin to be initialized with additional
            values from the application's command line interface.
        application_kwargs (Dict[str, Any]): Used to specify keyword arguments for
            the plugin instance being loaded. These arguments are updated in the
            plugin's kwargs attribute.

    Returns:
        Tuple[str, Plugin]: A tuple containing two elements: the first element is
        a string representing the name of the loaded plugin and the second element
        is an instance of the loaded plugin.

    """
    MESSAGE_LOGGER.warning(f"Loading external plugin '{plugin.name}'.")
    try:

        loader = PluginLoader()

        if application_args:
            plugin.args = application_args + plugin.args

        if application_kwargs:
            plugin.kwargs.update(application_kwargs)

        plugin_instance = loader.load(plugin)

    except RigelError as err:
        handle_rigel_error(err)

    return (plugin.name, plugin_instance)


def run_plugin(plugin: Tuple[str, Plugin]) -> None:
    """
    Executes an external plugin, runs it until its termination, and handles any
    interruptions or termination requests. It logs messages at different stages
    of plugin execution and termination, and catches any RigelError exceptions for
    further processing.

    Args:
        plugin (Tuple[str, Plugin]): Expected to contain exactly two elements: a
            string representing the name of the plugin, and an instance of the
            Plugin class.

    """
    try:

        plugin_name, plugin_instance = plugin

        def stop_plugin(*args: Any) -> None:
            """
            Terminates a plugin instance and logs a message indicating graceful
            shutdown. It then exits the program with exit code 0, indicating
            successful termination. The function accepts any number of arguments,
            but does not use them.

            Args:
                *args (Any): List of positional arguments

            """
            plugin_instance.stop()
            MESSAGE_LOGGER.info(f"Plugin '{plugin_name}' stopped executing gracefully.")
            sys.exit(0)

        signal.signal(signal.SIGINT, stop_plugin)
        signal.signal(signal.SIGTSTP, stop_plugin)

        MESSAGE_LOGGER.warning(f"Executing external plugin '{plugin_name}'.")
        plugin_instance.run()

        plugin_instance.stop()
        MESSAGE_LOGGER.info(f"Plugin '{plugin_name}' finished execution with success.")

    except RigelError as err:
        handle_rigel_error(err)


def run_simulation_plugin(
    plugin: Tuple[str, Plugin],
    manager: SimulationRequirementsManager,
) -> None:
    """
    Runs a plugin in an external process, managing its execution and shutdown. It
    catches any exceptions raised by the plugin, logs relevant messages, and stops
    the plugin gracefully when interrupted or finished executing.

    Args:
        plugin (Tuple[str, Plugin]): Unpacked into two variables: `plugin_name`
            and `plugin_instance`. It represents an external plugin with its name
            and instance.
        manager (SimulationRequirementsManager): Used to monitor the state of the
            simulation, specifically whether it has finished or not.

    """
    try:

        plugin_name, plugin_instance = plugin

        def stop_plugin(*args: Any) -> None:
            """
            Terminates a plugin instance and logs a message to indicate graceful
            termination. It takes any number of arguments, stops the plugin using
            its `stop` method, and then exits the program with exit code 0.

            Args:
                *args (Any): List of positional arguments

            """
            plugin_instance.stop()
            MESSAGE_LOGGER.info(f"Plugin '{plugin_name}' stopped executing gracefully.")
            sys.exit(0)

        signal.signal(signal.SIGINT, stop_plugin)
        signal.signal(signal.SIGTSTP, stop_plugin)

        MESSAGE_LOGGER.warning(f"Executing external plugin '{plugin_name}'.")
        plugin_instance.run()
        MESSAGE_LOGGER.warning("Simulation started.")

        while True:  # wait for test stage to finish
            if manager.finished:
                break

        print(manager)
        plugin_instance.stop()
        MESSAGE_LOGGER.info(f"Plugin '{plugin_name}' finished executing.")

    except RigelError as err:
        handle_rigel_error(err)


@click.group()
def cli() -> None:
    """
    Defines a command-line interface using the Click library. It is a group decorator
    that wraps multiple commands and sub-commands together, allowing users to
    access them from the terminal with a single prefix.

    """
    pass


@click.command()
@click.option('--force', is_flag=True, default=False, help='Write over an existing Rigelfile.')
def init(force: bool) -> None:
    """
    Initializes a Rigelfile by creating it if it does not exist or overwriting it
    if it already exists and the `--force` option is specified. It logs success
    messages and handles any errors that occur during the process.

    Args:
        force (bool): A flag that controls whether to overwrite an existing Rigelfile
            or not. When set to True, it allows writing over an existing file;
            when False (default), it raises an error if the file already exists.

    """
    try:

        if rigelfile_exists() and not force:
            raise RigelfileAlreadyExistsError()

        rigelfile_creator = RigelfileCreator()
        rigelfile_creator.create()
        MESSAGE_LOGGER.info('Rigelfile created with success.')

    except RigelError as err:
        handle_rigel_error(err)


def create_package_files(package: DockerSection) -> None:
    """
    Creates build files for a Docker package by rendering templates into actual
    files using a Renderer object. It generates a Dockerfile, an entrypoint script,
    and optionally a configuration file based on input parameters from the `package`
    object.

    Args:
        package (DockerSection): Expected to contain information about the package
            being processed, including its name (`package`) and optional directory
            path (`dir`).

    """
    MESSAGE_LOGGER.warning(f"Creating build files for package {package.package}.")

    if package.dir:
        path = os.path.abspath(f'{package.dir}/.rigel_config')
    else:
        path = os.path.abspath(f'.rigel_config/{package.package}')

    create_folder(path)

    renderer = Renderer(package)

    renderer.render('Dockerfile.j2', f'{path}/Dockerfile')
    MESSAGE_LOGGER.info(f"Created file {path}/Dockerfile")

    renderer.render('entrypoint.j2', f'{path}/entrypoint.sh')
    MESSAGE_LOGGER.info(f"Created file {path}/entrypoint.sh")

    if package.ssh:
        renderer.render('config.j2', f'{path}/config')
        MESSAGE_LOGGER.info(f"Created file {path}/config")


@click.command()
@click.option('--pkg', multiple=True, help='A list of desired packages.')
def create(pkg: Tuple[str]) -> None:
    """
    Generates a list of desired packages from command-line options and filters
    them based on a configuration file. It creates package files for selected
    packages and handles errors if any packages are not found or invalid.

    Args:
        pkg (Tuple[str]): Optional with multiple values, allowing the user to
            specify a list of desired packages when calling the command.

    """
    list_packages = list(pkg)
    try:
        rigelfile = parse_rigelfile()
        if not list_packages:  # consider all declared packages
            desired_packages = rigelfile.packages
        else:
            desired_packages = []
            for package in rigelfile.packages:
                if package.package in list_packages:
                    desired_packages.append(package)
                    list_packages.remove(package.package)
            if list_packages:  # check if an unknown package was referenced
                raise UnknownROSPackagesError(packages=', '.join(list_packages))

        for package in desired_packages:
            if isinstance(package, DockerSection):
                create_package_files(package)

    except RigelError as err:
        handle_rigel_error(err)


def login_registry(package: Union[DockerSection, DockerfileSection]) -> None:
    """
    Authenticates a Docker registry for a given package by logging into the registry
    server with provided credentials, and logs any authentication errors.

    Args:
        package (Union[DockerSection, DockerfileSection]): Expected to be either
            an instance of DockerSection or DockerfileSection class. This indicates
            that it accepts different types of objects related to Docker package
            registries.

    """
    docker = DockerClient()

    # Authenticate with registry
    if package.registry:

        server = package.registry.server
        username = package.registry.username
        password = package.registry.password

        try:

            MESSAGE_LOGGER.info(f'Authenticating with registry {server}')
            docker.login(
                server,
                username,
                password
            )

        except RigelError as err:
            handle_rigel_error(err)


def generate_paths(package: DockerSection) -> Tuple[str, str]:
    """
    Generates two absolute paths for a given `DockerSection` package. If the package
    has a directory, it returns the directory and its `.rigel_config` subdirectory.
    Otherwise, it returns the package name with `.rigel_config/` prefix in both cases.

    Args:
        package (DockerSection): Referred to as package throughout the code.

    Returns:
        Tuple[str, str]: A pair of absolute paths. The first path is to a directory
        and its corresponding '.rigel_config' file if 'package.dir' exists.
        Otherwise, the path is to '.rigel_config/{package.package}' and its own self.

    """
    if package.dir:
        return (
            os.path.abspath(f'{package.dir}'),                      # package root
            os.path.abspath(f'{package.dir}/.rigel_config')         # Dockerfile folder
        )
    else:
        return (
            os.path.abspath(f'.rigel_config/{package.package}'),    # package root
            os.path.abspath(f'.rigel_config/{package.package}')     # Dockerfile folder
        )


def containerize_package(package: DockerSection, load: bool, push: bool) -> None:
    """
    Containerizes a package by building and optionally pushing a Docker image using
    various configuration files, handles SSH keys, and creates QEMU configurations
    for supported platforms.

    Args:
        package (DockerSection): Required for containerizing a package. It contains
            information such as SSH keys, .rosinstall file, platforms, and image
            name.
        load (bool): Used to specify whether to load the Docker image after it has
            been built.
        push (bool): Optional. It controls whether to push the built Docker image
            to the registry after building it. If set to True, the image will be
            pushed; otherwise, it won't.

    """
    MESSAGE_LOGGER.warning(f"Containerizing package {package.package}.")
    if package.ssh and not package.rosinstall:
        MESSAGE_LOGGER.warning('No .rosinstall file was declared. Recommended to remove unused SSH keys from Dockerfile.')

    buildargs: Dict[str, str] = {}
    for key in package.ssh:
        if not key.file:
            value = os.environ[key.value]  # NOTE: SSHKey model ensures that environment variable is declared.
            buildargs[key.value] = value

    path = generate_paths(package)

    docker = DockerClient()

    login_registry(package)

    platforms = package.platforms or None

    docker.create_builder('rigel-builder', use=True)
    MESSAGE_LOGGER.info("Created builder 'rigel-builder'")

    # Ensure that QEMU is properly configured before building an image.
    for docker_platform, _, qemu_config_file in SUPPORTED_PLATFORMS:
        if not os.path.exists(f'/proc/sys/fs/binfmt_misc/{qemu_config_file}'):
            docker.run_container(
                'qus',
                'aptman/qus',
                command=['-s -- -c -p'],
                privileged=True,
                remove=True,
            )
            MESSAGE_LOGGER.info(f"Created QEMU configuration file for '{docker_platform}'")

    # Build the Docker image.
    MESSAGE_LOGGER.info(f"Building Docker image '{package.image}'")
    try:

        kwargs = {
            "file": f'{path[1]}/Dockerfile',
            "tags": package.image,
            "load": load,
            "push": push
        }

        if buildargs:
            kwargs["build_args"] = buildargs

        if platforms:
            kwargs["platforms"] = platforms

        docker.build_image(path[0], **kwargs)

        MESSAGE_LOGGER.info(f"Docker image '{package.image}' built with success.")
        if push:
            MESSAGE_LOGGER.info(f"Docker image '{package.image}' pushed with success.")

    except RigelError as err:
        handle_rigel_error(err)

    finally:
        # In all situations make sure to remove the builder if existent
        docker.remove_builder('rigel-builder')
        MESSAGE_LOGGER.info("Removed builder 'rigel-builder'")


def build_image(package: DockerfileSection, load: bool, push: bool) -> None:
    """
    Creates a Docker image using a provided Dockerfile and registry login information.
    It builds an image from the specified path, optionally loads it into memory,
    and pushes it to a registry if necessary, logging informational messages
    throughout the process.

    Args:
        package (DockerfileSection): Expected to hold information about a Docker
            package, including its Dockerfile location (`dockerfile`) and image
            name (`image`).
        load (bool): Used to specify whether the Docker image should be loaded
            into memory during the build process or not.
        push (bool): Used to specify whether the Docker image should be pushed
            after building or not. The default behavior depends on the value
            assigned to this variable.

    """
    MESSAGE_LOGGER.warning(f"Creating Docker image using provided Dockerfile at {package.dockerfile}")

    login_registry(package)

    path = os.path.abspath(package.dockerfile)

    MESSAGE_LOGGER.info(f"Building Docker image {package.image}")
    builder = DockerClient()
    kwargs = {
        "tags": package.image,
        "load": load,
        "push": push
    }
    builder.build_image(path, **kwargs)

    MESSAGE_LOGGER.info(f"Docker image '{package.image}' built with success.")


@click.command()
@click.option('--pkg', multiple=True, help='A list of desired packages.')
@click.option("--load", is_flag=True, show_default=True, default=False, help="Store built image locally.")
@click.option("--push", is_flag=True, show_default=True, default=False, help="Store built image in a remote registry.")
def build(pkg: Tuple[str], load: bool, push: bool) -> None:
    """
    Constructs a list of desired packages based on command-line options and parses
    a configuration file to determine which packages to install, then installs or
    builds them accordingly, storing results locally or remotely as specified by
    user input.

    Args:
        pkg (Tuple[str]): Specified with multiple=True, allowing users to pass a
            list of desired packages as separate arguments.
        load (bool): Flag-like. When set to True, it indicates that the built image
            should be stored locally. It defaults to False and has a default value
            of False when not specified.
        push (bool): An option for the command. It indicates whether to store built
            images in a remote registry when set to True, or not (default False)
            otherwise.

    """
    list_packages = list(pkg)
    rigelfile = parse_rigelfile()
    try:
        if not list_packages:  # consider all declared packages
            desired_packages = rigelfile.packages
        else:
            desired_packages = []
            for package in rigelfile.packages:
                if package.package in list_packages:
                    desired_packages.append(package)
                    list_packages.remove(package.package)
            if list_packages:  # check if an unknown package was referenced
                raise UnknownROSPackagesError(packages=', '.join(list_packages))

        for package in desired_packages:
            if isinstance(package, DockerSection):
                containerize_package(package, load, push)
            else:  # DockerfileSection
                build_image(package, load, push)

    except RigelError as err:
        handle_rigel_error(err)


@click.command()
def deploy() -> None:
    """
    Deploys a containerized ROS package by parsing a Rigelfile, loading and running
    plugins defined in it, if any. If no deployment plugin is found, it logs a
    warning message.

    """
    MESSAGE_LOGGER.info('Deploying containerized ROS package.')

    rigelfile = parse_rigelfile()
    if rigelfile.deploy:

        # Run external deployment plugins.
        for plugin_section in rigelfile.deploy:
            plugin = load_plugin(plugin_section, [], {})
            run_plugin(plugin)

    else:
        MESSAGE_LOGGER.warning('No deployment plugin declared inside Rigelfile.')


@click.command()
def run() -> None:
    """
    Initializes a ROS application and runs a simulation based on the contents of
    a rigelfile, which defines plugins to simulate. It parses the file, loads
    plugins, and executes them with specified requirements and timeout.

    """
    MESSAGE_LOGGER.info('Starting containerized ROS application.')

    rigelfile = parse_rigelfile()
    if rigelfile.simulate:

        for plugin_section in rigelfile.simulate.plugins:

            requirements_manager = SimulationRequirementsManager(rigelfile.simulate.timeout)

            # Parse simulation requirements.
            requirements_parser = SimulationRequirementsParser()
            for hpl_statement in rigelfile.simulate.introspection:
                requirement = requirements_parser.parse(hpl_statement)
                requirement.father = requirements_manager
                requirements_manager.children.append(requirement)

            # Run external simulation plugins.
            plugin = load_plugin(plugin_section, [requirements_manager], {})
            run_simulation_plugin(plugin, requirements_manager)

    else:
        MESSAGE_LOGGER.warning('No simulation plugin declared inside Rigelfile.')


@click.command()
@click.argument('plugin', type=str)
@click.option('--host', default='github.com', help="URL of the hosting platform. Default is 'github.com'.")
@click.option('--ssh', is_flag=True, default=False, help='Whether the plugin is public or private. Use flag when private.')
def install(plugin: str, host: str, ssh: bool) -> None:
    """
    Installs a plugin on a hosting platform specified by the user. It takes three
    parameters: the name of the plugin, the URL of the hosting platform (default
    is 'github.com'), and a boolean indicating whether the plugin is public or private.

    Args:
        plugin (str): Passed to the function by the user through command-line
            input. It specifies the name or identifier of the plugin to be installed.
        host (str): Optional. It defaults to 'github.com' and specifies the URL
            of the hosting platform for the plugin. The user can override this
            default by providing a different value at command invocation time.
        ssh (bool): 0 by default, meaning it's set to False. When True, it indicates
            that the plugin is private or not public. It can be enabled or disabled
            using a flag option.

    """
    try:
        installer = PluginInstaller(plugin, host, ssh)
        installer.install()
    except RigelError as err:
        handle_rigel_error(err)


# Add commands to CLI
cli.add_command(init)
cli.add_command(build)
cli.add_command(create)
cli.add_command(deploy)
cli.add_command(install)
cli.add_command(run)


def main() -> None:
    """
    Rigel application entry point.
    """
    cli()


if __name__ == '__main__':
    main()
