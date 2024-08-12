import python_on_whales
import time
from rigel.exceptions import DockerAPIError
from rigel.loggers import get_logger
from typing import Any, Iterable, Optional, Tuple, Union


MESSAGE_LOGGER = get_logger()


class DockerClient:
    """
    Wraps the Python-on-whales library, providing a set of methods for interacting
    with Docker containers, networks, and builders. It allows managing, creating,
    inspecting, and removing these entities, as well as waiting for specific
    container statuses.

    Attributes:
        DOCKER_CONTAINER_ID_DISPLAY_SIZE (int): 12 by default. It determines the
            number of characters to display for a container ID when logging messages.
        DOCKER_RUN_TIMEOUT (int): 120 seconds, which represents the maximum time
            to wait for a Docker container's status to become a certain state when
            running the `wait_for_container_status` method.
        DOCKER_RUN_WAIT_STATUS (int): 3 seconds. It represents the time interval
            to wait before checking the status of a container after a Docker run
            operation, if the expected status has not been reached yet.
        client (python_on_whales.docker_client.DockerClient): Initialized in the
            constructor (`__init__`) with `python_on_whales.docker`. It provides
            a wrapper around the Docker client.

    """

    DOCKER_CONTAINER_ID_DISPLAY_SIZE: int = 12
    DOCKER_RUN_TIMEOUT: int = 120  # seconds
    DOCKER_RUN_WAIT_STATUS: int = 3  # seconds

    # A Docker client instance.
    client: python_on_whales.docker_client.DockerClient

    def __init__(self) -> None:
        """
        Create a Docker client instance.

        :type client: Optional[python_on_whales.docker_client.DockerClient]
        :param client: A Docker client instance.
        """
        self.client = python_on_whales.docker

    def __getattribute__(self, __name: str) -> Any:

        # Wrapper for 'python_on_whales.docker_client.DockerClient'.
        # Look for arguments inside wrapped class before throwing an AttributeError.

        """
        Retrieves an attribute from either the DockerClient object or its client
        attribute, and returns it if found. If not found in both places, it raises
        an AttributeError with a custom message indicating that no 'DockerClient'
        object has the specified attribute.

        Args:
            __name (str): An attribute name to be accessed. It is used as a key
                to access attributes from either the object itself or its client,
                if not found in the object.

        Returns:
            Any: Either an attribute from itself or from its client, depending on
            whether it exists in one or both objects. If not found in both, it
            raises an AttributeError with a custom message.

        """
        try:
            return object.__getattribute__(self, __name)
        except AttributeError:
            pass

        try:
            return object.__getattribute__(self.client, __name)
        except AttributeError:
            pass

        raise AttributeError(f"No 'DockerClient' object has attribute '{__name}'")

    def get_builder(self, name: str) -> Optional[python_on_whales.components.buildx.cli_wrapper.Builder]:
        """
        Attempts to retrieve a Buildx Builder instance by name from the client's
        buildx inspect method, and returns it if successful; otherwise, it catches
        any DockerException that may occur during the retrieval process and returns
        None instead.

        Args:
            name (str): Expected to be a string that represents the name of a
                builder, which can be inspected or retrieved from Docker.

        Returns:
            Optional[python_on_whales.components.buildx.cli_wrapper.Builder]:
            Either an instance of class Builder or None. The value depends on
            whether a DockerException occurs during the inspection of a builder
            with the given name.

        """
        try:
            return self.client.buildx.inspect(name)
        except python_on_whales.exceptions.DockerException:
            return None

    def create_builder(
        self,
        name: str,
        use: bool = True,
        driver: str = 'docker-container'
    ) -> python_on_whales.components.buildx.cli_wrapper.Builder:
        """
        Creates a new buildx builder with the specified name, use flag, and driver
        type. If the builder already exists, it returns the existing one; otherwise,
        it creates a new one and returns it.

        Args:
            name (str): Required. It represents the name of the builder to be
                created or retrieved, which uniquely identifies a builder instance.
            use (bool): True by default. Its purpose is not explicitly specified,
                but based on its position among other parameters related to Docker
                buildx, it likely controls whether a builder should be used or not.
            driver (str): Set to 'docker-container' by default. It determines the
                driver used for building images with Buildx, such as Docker container
                or Kubernetes cluster.

        Returns:
            python_on_whales.components.buildx.cli_wrapper.Builder: Either an
            existing builder or a newly created one if no matching name is found.

        """
        builder = self.get_builder(name)
        if not builder:
            try:
                return self.client.buildx.create(name=name, use=use, driver=driver)
            except python_on_whales.exceptions.DockerException as exception:
                raise DockerAPIError(exception)
        return builder  # return already existing builder

    def remove_builder(self, name: str) -> None:
        """
        Removes a builder with the given name from the buildx system using the
        client's buildx remove command. If the removal fails, it raises a
        DockerAPIError exception.

        Args:
            name (str): Required to uniquely identify the builder that needs to
                be removed from the Docker environment.

        """
        builder = self.get_builder(name)
        if builder:
            try:
                self.client.buildx.remove(builder)
            except python_on_whales.exceptions.DockerException as exception:
                raise DockerAPIError(exception)

    def get_network(self, name: str) -> Optional[python_on_whales.components.network.cli_wrapper.Network]:
        """
        Retrieves a network with a given name from the Docker client, returns it
        if successful, or None if an exception occurs while inspecting the network.

        Args:
            name (str): Required to be specified when calling this function. It
                represents the name of the network that needs to be retrieved or
                inspected.

        Returns:
            Optional[python_on_whales.components.network.cli_wrapper.Network]: A
            network object if it exists, or None if an exception occurs during its
            retrieval.

        """
        try:
            return self.client.network.inspect(name)
        except python_on_whales.exceptions.DockerException:
            return None

    def create_network(self, name: str, driver: str) -> python_on_whales.components.network.cli_wrapper.Network:
        """
        Creates or retrieves a Docker network with a specified name and driver,
        and returns a CLI wrapper object for interacting with that network.

        Args:
            name (str): Required. It specifies the name of the network to create
                or retrieve. If the network with this name already exists, it will
                be retrieved; otherwise, a new network with this name will be created.
            driver (str): Used to specify the driver for the network, such as
                'bridge' or 'host', depending on the Docker networking mode desired.

        Returns:
            python_on_whales.components.network.cli_wrapper.Network: Either a
            created network object or an already existing network object if it was
            found by its name.

        """
        network = self.get_network(name)
        if not network:
            try:
                return self.client.network.create(name, driver=driver)
            except python_on_whales.exceptions.DockerException as exception:
                raise DockerAPIError(exception)
        return network  # return already existing network

    def remove_network(self, name: str) -> None:
        """
        Removes a network with the given name from Docker. If the network does not
        exist, it raises an exception; if there's a Docker-related error during
        removal, it propagates the original exception.

        Args:
            name (str): Used to specify the name of a network that needs to be
                removed from the system.

        """
        network = self.get_network(name)
        if network:
            try:
                self.client.network.remove(network)
            except python_on_whales.exceptions.DockerException as exception:
                raise DockerAPIError(exception)

    def get_container(self, name: str) -> Optional[python_on_whales.components.container.cli_wrapper.Container]:
        """
        Retrieves information about a container with the given name. If the container
        exists, it returns the inspected container object; otherwise, it returns
        None. If an error occurs during the operation, it raises a DockerAPIError
        exception.

        Args:
            name (str): Required for identifying a specific container. It is used
                to check if the container exists with the given name and to inspect
                the container if it does exist.

        Returns:
            Optional[python_on_whales.components.container.cli_wrapper.Container]:
            Either a Container object or None, depending on whether the container
            with the given name exists in Docker or not.

        """
        try:
            if self.client.container.exists(name):
                return self.client.container.inspect(name)
            else:
                return None
        except python_on_whales.exceptions.DockerException as exception:
            raise DockerAPIError(exception)

    def run_container(
        self,
        name: str,
        image: str,
        **kwargs: Any
    ) -> Union[python_on_whales.components.container.cli_wrapper.Container, str, Iterable[Tuple[str, bytes]]]:
        """
        Runs a new Docker container from an image or returns an existing one with
        the given name. If no container exists, it creates and starts a new one;
        otherwise, it returns the existing one.

        Args:
            name (str): Required. It represents the name of the container to be
                run or created. If the container with this name already exists,
                it returns an existing container instance; otherwise, it creates
                a new one.
            image (str): Used to specify the name or ID of an image from which a
                new container is created when running the container for the first
                time.
            **kwargs (Any): Dictionary of keyword arguments

        Returns:
            Union[python_on_whales.components.container.cli_wrapper.Container,
            str, Iterable[Tuple[str, bytes]]]: Either an instance of Container, a
            string or an iterable of tuples containing strings and bytes.

        """
        container = self.get_container(name)
        if not container:
            kwargs['name'] = name
            try:
                return self.client.container.run(image, **kwargs)
            except python_on_whales.exceptions.DockerException as exception:
                raise DockerAPIError(exception)
        return container  # return already existing container

    def remove_container(self, name: str) -> None:
        """
        Removes a container with the specified name from the system, forcing its
        removal if necessary and deleting any attached volumes. If an error occurs
        during removal, it raises a DockerAPIError exception.

        Args:
            name (str): Required to specify the name of a container that needs to
                be removed from the system.

        """
        container = self.get_container(name)
        if container:
            try:
                container.remove(force=True, volumes=True)
            except python_on_whales.exceptions.DockerException as exception:
                raise DockerAPIError(exception)

    def wait_for_container_status(
            self,
            name: str,
            status: str
            ) -> None:
        """
        Waits for the status of a specified container to become a certain status,
        within a defined timeout period. If the container does not exist, it raises
        an exception.

        Args:
            name (str): Required. It specifies the name of the container for which
                to wait for its status to become a specified status.
            status (str): Expected as a string representing the desired status of
                the container.

        """

        elapsed_time = 0  # seconds
        while True:
            container = self.get_container(name)
            if container:
                if elapsed_time < self.DOCKER_RUN_TIMEOUT:
                    if container.state.status == status:
                        return
                    time.sleep(self.DOCKER_RUN_WAIT_STATUS)
                    elapsed_time = elapsed_time + self.DOCKER_RUN_WAIT_STATUS
                    MESSAGE_LOGGER.info('Waiting for status of container {} to become "{}". Current status is "{}".'.format(
                        container.id[:self.DOCKER_CONTAINER_ID_DISPLAY_SIZE],
                        status,
                        container.state.status
                    ))
                else:
                    raise DockerAPIError(Exception(
                        'Timeout while waiting for status of container {} to become "{}".'.format(
                            container.id[:self.DOCKER_CONTAINER_ID_DISPLAY_SIZE],
                            status
                        )
                    ))
            else:
                raise DockerAPIError(Exception(
                    f'Unable to watch over status of container "{name}" since it does not exist.'
                ))
