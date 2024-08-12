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
    errors, including non-existent files, invalid YAML syntax, and empty files.
    It also provides specific error messages for each type of error encountered.

    Attributes:
        filepath (str): Initialized during object creation with a file path that
            points to a YAML configuration file.

    """

    def __init__(self, filepath: str) -> None:
        """
        :type filepath: string
        :param filepath: The path for the YAML path.
        """
        self.filepath = filepath

    def load(self) -> Any:
        """
        Attempts to load YAML data from a file at a specified filepath. If successful,
        it returns the loaded data; otherwise, it raises various exceptions depending
        on the nature of the error encountered during loading.

        Returns:
            Any: The parsed YAML data loaded from a file specified by `self.filepath`,
            if the loading process is successful. If not, it raises various
            exceptions depending on the error encountered during the loading process.

        """

        try:

            with open(self.filepath, 'r') as configuration_file:
                yaml_data = yaml.safe_load(configuration_file)

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

            raise UnformattedRigelfileError(trace=' '.join(message))
