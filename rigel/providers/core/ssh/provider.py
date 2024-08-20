import os
from rigel.models.builder import ModelBuilder
from rigel.models.provider import ProviderRawData
from rigel.models.rigelfile import RigelfileGlobalData
from rigel.providers import Provider
from typing import Any, Dict
from .models import SSHKeyGroup, SSHProviderModel, SSHProviderOutputModel


class SSHProvider(Provider):

    """
    Initializes a SSH provider with its identifier, raw data, global data, and
    providers' data. It verifies SSH keys by checking environment variables or
    file existence, connects to SSH server using verified keys, and disconnects
    from the server.

    Attributes:
        model (SSHProviderModel): Initialized by calling `ModelBuilder(SSHProviderModel).build([],
            self.raw_data)`. It represents a model that describes the SSH provider's
            configuration.
        raw_data (ProviderRawData): Initialized during the object's instantiation.
            Its purpose and content are not explicitly described, but it is likely
            used to store raw data related to SSH provider connections or configuration.

    """
    def __init__(
        self,
        identifier: str,
        raw_data: ProviderRawData,
        global_data: RigelfileGlobalData,
        providers_data: Dict[str, Any]
    ) -> None:
        """
        Initializes an instance by calling its superclass's constructor and then
        builds an SSH provider model using raw data. The model is expected to be
        an instance of SSHProviderModel, as verified by an assertion.

        Args:
            identifier (str): Used to initialize the object with an identifier.
            raw_data (ProviderRawData): Expected to be an object that contains raw
                data related to providers.
            global_data (RigelfileGlobalData): Initialized with an instance of
                this data type. The purpose or contents of this global data are
                not specified within the provided code snippet.
            providers_data (Dict[str, Any]): Expected to contain data related to
                providers. The exact structure of this dictionary is not specified.

        """
        super().__init__(
            identifier,
            raw_data,
            global_data,
            providers_data
        )

        # Ensure model instance was properly initialized
        self.model = ModelBuilder(SSHProviderModel).build([], self.raw_data)
        assert isinstance(self.model, SSHProviderModel)

    def verify_env(self, key: SSHKeyGroup) -> SSHKeyGroup:
        """
        Checks if an environment variable exists for a given SSH key group. If the
        variable is set, it returns the key; otherwise, it raises an exception
        with an error message specifying the missing variable name.

        Args:
            key (SSHKeyGroup): Required for the function's execution. It represents
                an environment variable name to be checked in the operating system's
                environment.

        Returns:
            SSHKeyGroup: A reference to the original input object if the environment
            variable associated with it exists, otherwise it raises an exception.

        """
        if os.environ.get(key.env, None):
            return key
        else:
            raise Exception(f"Invalid SSH key value. Environment variable '{key.env}' is not set.")

    def verify_file(self, key: SSHKeyGroup) -> SSHKeyGroup:
        """
        Verifies if a given SSH key path exists as a file and returns it if true,
        otherwise raises an exception with an error message describing the invalid
        path.

        Args:
            key (SSHKeyGroup): Passed to the function when called. It represents
                an instance of SSHKeyGroup, which likely encapsulates information
                about a Secure Shell (SSH) key.

        Returns:
            SSHKeyGroup: The input key if the corresponding file exists and can
            be accessed, otherwise it raises an exception with an error message.

        """
        if os.path.isfile(key.path):
            return key
        else:
            raise Exception(f"Invalid SSH key path '{key.path}'. Either it does not exist or it is not a file.")

    def connect(self) -> None:
        """
        Iterates over its model keys, verifying environment settings for some and
        file paths for others. Then it constructs a new ModelBuilder object with
        the same content as the input model.

        """
        for key in self.model.keys:
            if key.env:
                self.verify_env(key)
            else:  # key.path is set:
                self.verify_file(key)

        # NOTE: using ModelBuilder is required for the instance to update its class type despite
        # having the same content as the input model.
        self.providers_data[self.identifier] = ModelBuilder(SSHProviderOutputModel).build([], self.model.dict())

    def disconnect(self) -> None:
        pass  # do nothing
