import os
from pathlib import Path
from rigel.exceptions import RigelError
from rigel.loggers import get_logger
from rigel.models.application import Application
from rigel.models.builder import ModelBuilder
from rigel.models.plugin import PluginRawData
from rigel.models.rigelfile import RigelfileGlobalData
from rigel.providers.core import SSHProviderOutputModel
from rigel.plugins import Plugin as PluginBase
from typing import Any, Dict
from .models import PluginModel
from .renderer import Renderer

LOGGER = get_logger()


class Plugin(PluginBase):

    """
    Initializes and configures a plugin for Rigel, a software framework. It sets
    up an SSH provider, builds a model from raw data, and renders templates to
    create files in a specified directory. The plugin can be started, which creates
    Dockerfiles and entrypoint scripts.

    Attributes:
        raw_data (PluginRawData): Initialized with a value passed to its constructor.
            It is used as input for ModelBuilder's build method.
        model (PluginModel): Initialized with a new instance of ModelBuilder's
            build method, passing PluginModel as the first argument and raw_data
            as the second.
        __ssh_keys (SSHProviderOutputModel|None): Initialized in the `setup` method
            as a single instance of SSHProviderOutputModel if found, or None otherwise.

    """
    def __init__(
        self,
        raw_data: PluginRawData,
        global_data: RigelfileGlobalData,
        application: Application,
        providers_data: Dict[str, Any],
        shared_data: Dict[str, Any] = {}  # noqa
    ) -> None:
        """
        Initializes an instance with raw data, global data, application, and
        providers' data. It sets the 'distro' attribute to the application's distro
        and builds a model based on raw data.

        Args:
            raw_data (PluginRawData): Required to initialize an instance of this
                class. It contains raw data that is used as input for other parts
                of the initialization process.
            global_data (RigelfileGlobalData): Passed to the superclass's constructor,
                indicating that it represents global data related to the Rigelfile
                context.
            application (Application): Used to set the 'distro' key in the raw
                data dictionary with the value of the distro attribute from the
                application object.
            providers_data (Dict[str, Any]): Intended to hold data related to
                providers. It is expected to be passed as an argument when creating
                an instance of this class.
            shared_data (Dict[str, Any]): Optional with a default value of an empty
                dictionary `{}`. It represents additional data that can be shared
                among components.

        """
        super().__init__(
            raw_data,
            global_data,
            application,
            providers_data,
            shared_data
        )

        # Ensure model instance was properly initialized
        self.raw_data['distro'] = application.distro
        self.model = ModelBuilder(PluginModel).build([], self.raw_data)
        assert isinstance(self.model, PluginModel)

        self.__ssh_keys: SSHProviderOutputModel = None

    def setup(self) -> None:  # noqa
        """
        Initializes and sets up SSH key providers from the provided data. It checks
        for multiple providers, raises an error if found, and assigns the first
        provider to the `__ssh_keys` attribute if a single provider is found or present.

        """
        providers = [provider for _, provider in self.providers_data.items() if isinstance(provider, SSHProviderOutputModel)]
        if len(providers) > 1:
            raise RigelError(base='Multiple SSH key providers were found. Please specify which provider you want to use.')
        elif providers:
            self.__ssh_keys = providers[0]
        

    def start(self) -> None:

        """
        Initializes a directory, creates it if necessary, renders templates for a
        Dockerfile and entrypoint script, and logs the creation of these files.
        If SSH keys are present, it also renders a configuration file.

        """
        dir = self.application.dir

        workdir = os.path.abspath(dir).split('/')[-1]

        Path(dir).mkdir(parents=True, exist_ok=True)

        renderer = Renderer(self.application.distro, workdir, self.model, self.__ssh_keys)

        renderer.render('Dockerfile.j2', f'{dir}/Dockerfile')
        LOGGER.info(f"Created file {dir}/Dockerfile")

        renderer.render('entrypoint.j2', f'{dir}/dockerfile_entrypoint.sh')
        LOGGER.info(f"Created file {dir}/entrypoint.sh")

        if self.__ssh_keys:
            renderer.render('config.j2', f'{dir}/dockerfile_config')
            LOGGER.info(f"Created file {dir}/config")
