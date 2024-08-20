import yaml
from rigel.exceptions import (
    EmptyRigelfileError,
    RigelfileNotFoundError,
    UnformattedRigelfileError
)
from typing import Any


class YAMLDataLoader:
    """
    Loads YAML data from a file and returns it as a Python object. It handles
    exceptions for missing files, invalid YAML syntax, and empty files.

    Attributes:
        filepath (str): Initialized in the constructor method with a string parameter
            representing the path to the YAML file that needs to be loaded.

    """

    def __init__(self, filepath: str) -> None:
        """
        :type filepath: string
        :param filepath: The path for the YAML path.
        """
        self.filepath = filepath

    def load(self) -> Any:
        """
        Attempts to load a YAML configuration file at a specified filepath. If
        successful, it returns the loaded data as a Python object. If an error
        occurs (e.g., file not found or corrupted), it raises a corresponding exception.

        Returns:
            Any: An object containing data loaded from a YAML file at the specified
            filepath, or raises an exception if the file cannot be found, is empty,
            or contains invalid YAML formatting.

        """

        try:

            with open(self.filepath, 'r') as configuration_file:
                yaml_data = yaml.full_load(configuration_file.read())

            # Ensure that the file contains some data.
            if not yaml_data:
                raise EmptyRigelfileError()

            return yaml_data

        except FileNotFoundError:
            raise RigelfileNotFoundError()

        except yaml.YAMLError as err:

            # Collect the error details from the original error before
            # raising proper RigelError.
            message = []
            for arg in err.args:
                if isinstance(arg, str):
                    message.append(arg)
                else:
                    message.append(f'(line: {arg.line}, column: {arg.column})')
            raise UnformattedRigelfileError(' '.join(message))
