from python_on_whales.exceptions import DockerException
from rigel.clients import DockerClient
from rigel.exceptions import DockerAPIError
from rigel.loggers import get_logger
from rigel.models.builder import ModelBuilder
from rigel.models.provider import ProviderRawData
from rigel.models.rigelfile import RigelfileGlobalData
from rigel.providers import Provider
from typing import Any, Dict
from .models import ContainerRegistryProviderModel

LOGGER = get_logger()


class ContainerRegistryProvider(Provider):

    """
    Provides a connection to a container registry, such as Docker Hub, and manages
    the login and logout process for accessing the registry's resources. It utilizes
    a `ModelBuilder` to construct a model of the registry provider and a `DockerClient`
    to interact with the registry.

    Attributes:
        model (ContainerRegistryProviderModel): Initialized during the `__init__`
            method by using the ModelBuilder class to build a model based on the
            raw data provided.
        raw_data (ProviderRawData): Initialized in the constructor. Its purpose
            is not explicitly described, but it likely contains raw data or
            configuration needed for building the ContainerRegistryProviderModel
            instance.
        __docker (DockerClient): Initialized in the constructor (`__init__`) method.
            It represents a Docker client object used for interactions with a
            Docker registry during login and logout operations.

    """
    def __init__(
        self,
        identifier: str,
        raw_data: ProviderRawData,
        global_data: RigelfileGlobalData,
        providers_data: Dict[str, Any]
    ) -> None:
        """
        Initializes an instance with provided identifier, raw data, global data,
        and providers' data. It also constructs a model using the ModelBuilder and
        DockerClient, verifying that the model is an instance of ContainerRegistryProviderModel.

        Args:
            identifier (str): Likely used to uniquely identify an instance of the
                class. It is passed to the superclass's `__init__` method along
                with other parameters.
            raw_data (ProviderRawData): Used to initialize the object. Its exact
                usage depends on the class definition, but it may contain raw data
                relevant for initialization.
            global_data (RigelfileGlobalData): Used to initialize an object. The
                exact nature and purpose of this data are not specified by the
                provided code snippet.
            providers_data (Dict[str, Any]): Used to store data related to providers.
                It allows for storing arbitrary key-value pairs which are later
                referenced as `self.providers_data`.

        """
        super().__init__(
            identifier,
            raw_data,
            global_data,
            providers_data
        )

        # Ensure model instance was properly initialized
        self.model = ModelBuilder(ContainerRegistryProviderModel).build([], self.raw_data)
        assert isinstance(self.model, ContainerRegistryProviderModel)

        self.__docker: DockerClient = DockerClient()

    def connect(self) -> None:

        """
        Logs into a Docker registry using provided credentials and server URL,
        attempting to establish a connection for further Docker operations.

        """
        server = self.model.server
        username = self.model.username
        LOGGER.debug(f"Attempting login '{username}' with registry '{server}'")

        try:
            self.__docker.login(
                username=username,
                password=self.model.password,
                server=server
            )
        except DockerException as exception:
            raise DockerAPIError(exception)

        LOGGER.info(f"Logged in with success as user '{username}' with registry '{server}'")

    def disconnect(self) -> None:

        """
        Logs out from a Docker server and handles any exceptions that might occur
        during the process, reporting success or failure accordingly.

        """
        server = self.model.server

        try:
            self.__docker.logout(server)
        except DockerException as exception:
            raise DockerAPIError(exception)

        LOGGER.info(f"Logged out with success from registry '{server}'")
