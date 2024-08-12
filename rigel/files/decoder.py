import os
import re
from rigel.exceptions import RigelError, UndeclaredGlobalVariableError
from typing import Any, Dict


# Define supported data headers
HEADER_GLOBAL_VARIABLE = "vars"
HEADER_SHARED_DATA = "data"

SUPPORTED_HEADERS = [
    HEADER_GLOBAL_VARIABLE,
    HEADER_SHARED_DATA
]


class YAMLDataDecoder:
    """
    Decodes YAML files containing template variables and replaces them with actual
    values from a dictionary or environment variables. It recursively traverses
    the data structure, replacing template variables in strings and updating
    variable names to match the header.

    """

    def __extract_variable_name(self, match: str) -> str:
        """
        Removes specific characters from a given string (`match`) to extract a
        variable name. The characters '{', '}' and ' ' are removed, returning the
        cleaned-up string as the extracted variable name.

        """
        chars_to_remove = ['{', '}', ' ']
        variable_name = match
        for c in chars_to_remove:
            variable_name = variable_name.replace(c, '')
        return variable_name

    def __aux_decode(self, data: Any, vars: Dict[str, Any], header: str, path: str = '') -> None:
        """
        Recursively decodes nested dictionaries and lists within a given data
        structure, using provided variables, header information, and an optional
        path for debugging purposes.

        """
        if isinstance(data, dict):
            self.__aux_decode_dict(data, vars, header, path)
        elif isinstance(data, list):
            self.__aux_decode_list(data, vars, header, path)

    def __aux_decode_dict(self, data: Any, vars: Dict[str, Any], header: str, path: str = '') -> None:
        """
        Recursively decodes a dictionary-like data structure from YAML data. It
        calls two private methods to decode values and keys, then processes them
        according to a given header and path.

        """
        self.__aux_decode_dict_values(data, vars, header, path)
        self.__aux_decode_dict_keys(data, vars, header, path)

    def __aux_decode_dict_values(self, data: Any, vars: Dict[str, Any], header, path: str = '') -> None:
        """
        Recursively processes dictionary values to replace template variables with
        actual values from the input data, environment variables, or shared data.
        It handles string values containing delimiters and nested values such as
        lists and dictionaries.

        """
        for k, v in data.items():

            new_path = f'{path}.{k}' if path else k

            if isinstance(v, str):  # in order to contain delimiters the field must be of type str
                matches = re.findall(r'{{[a-zA-Z0-9_\s\-\!\?\.]+}}', v)

                for match in matches:
                    try:
                        extracted_variable_name = self.__extract_variable_name(match)
                        __header, variable_name = extracted_variable_name.split('.', 1)
                    except ValueError:
                        raise RigelError(f"Template variable '{extracted_variable_name}' declared without a header")

                    if __header not in SUPPORTED_HEADERS:
                        raise RigelError(f"Template variable declared with an unsupported header '{__header}'")

                    if __header == header:

                        if variable_name in vars:

                            value = vars[variable_name]

                            if isinstance(value, list) or isinstance(value, dict):
                                data[k] = value

                            else:
                                remainder = data[k].replace(match, '').strip()
                                if remainder:
                                    data[k] = data[k].replace(match, str(value))
                                else:
                                    data[k] = value

                        elif variable_name in os.environ and __header == HEADER_GLOBAL_VARIABLE:
                            data[k] = data[k].replace(match, os.environ[variable_name])

                        else:

                            if header == HEADER_GLOBAL_VARIABLE:
                                raise UndeclaredGlobalVariableError(new_path, variable_name)

                            elif header == HEADER_SHARED_DATA:
                                raise RigelError(f"Field '{new_path}' set to undeclared shared variable '{variable_name}'")

            else:
                self.__aux_decode(v, vars, header, new_path)

    def __aux_decode_dict_keys(self, data: Any, vars: Dict[str, Any], header: str, path: str = '') -> None:
        """
        Traverses the keys of a given data structure, replaces specific template
        variables with their corresponding values from predefined variables or
        environment variables, and updates the data structure accordingly.

        """
        keys = list(data.keys())
        for k in keys:

            new_path = f'{path}.{k}' if path else k

            if isinstance(k, str):  # in order to contain delimiters the field must be of type str
                matches = re.findall(r'{{[a-zA-Z0-9_\s\-\!\?\.]+}}', k)
                for match in matches:

                    try:
                        extracted_variable_name = self.__extract_variable_name(match)
                        __header, variable_name = extracted_variable_name.split('.', 1)
                    except ValueError:
                        raise RigelError(f"Template variable '{extracted_variable_name}' declared without a header")

                    if __header not in SUPPORTED_HEADERS:
                        raise RigelError(f"Template variable declared with an unsupported header '{__header}'")

                    if __header == header:

                        if variable_name in vars:
                            data[vars[variable_name]] = data.pop(k)

                        elif variable_name in os.environ and __header == HEADER_GLOBAL_VARIABLE:
                            data[os.environ[variable_name]] = data.pop(k)

                        else:

                            if header == HEADER_GLOBAL_VARIABLE:
                                raise UndeclaredGlobalVariableError(new_path, variable_name)

                            elif header == HEADER_SHARED_DATA:
                                raise RigelError(f"Field '{new_path}' set to undeclared shared variable '{variable_name}'")

    def __aux_decode_list(self, data: Any, vars: Dict[str, Any], header: str, path: str = '') -> None:
        """
        Recursively decodes a list of data elements by replacing template variables
        with actual values from variables or environment settings, based on the
        given header and path.

        """
        for idx, elem in enumerate(data):

            new_path = f'{path}[{idx}]'

            if isinstance(elem, str):  # in order to contain delimiters the field must be of type str
                matches = re.findall(r'{{[a-zA-Z0-9_\s\-\!\?\.]+}}', elem)
                for match in matches:

                    try:
                        extracted_variable_name = self.__extract_variable_name(match)
                        __header, variable_name = extracted_variable_name.split('.', 1)
                    except ValueError:
                        raise RigelError(f"Template variable '{extracted_variable_name}' declared without a header")

                    if __header not in SUPPORTED_HEADERS:
                        raise RigelError(f"Template variable declared with an unsupported header '{__header}'")

                    if __header == header:

                        if variable_name in vars:

                            value = vars[variable_name]

                            if isinstance(value, list) or isinstance(value, dict):
                                data[idx] = value

                            else:
                                remainder = data[idx].replace(match, '').strip()
                                if remainder:
                                    data[idx] = data[idx].replace(match, str(value))
                                else:
                                    data[idx] = value

                        elif variable_name in os.environ and __header == HEADER_GLOBAL_VARIABLE:
                            data[idx] = data[idx].replace(match, os.environ[variable_name])

                        else:

                            if header == HEADER_GLOBAL_VARIABLE:
                                raise UndeclaredGlobalVariableError(new_path, variable_name)

                            elif header == HEADER_SHARED_DATA:
                                raise RigelError(f"Field '{new_path}' set to undeclared shared variable '{variable_name}'")

            else:
                self.__aux_decode(elem, vars, header, new_path)

    def decode(
        self,
        data: Dict[str, Any],
        variables: Dict[str, Any],
        header: str
    ) -> Dict[str, Any]:
        """
        Decodes YAML data using the provided `variables` and `header`, then returns
        the decoded data as a dictionary. The decoding process is performed by the
        internal `_aux_decode` method.

        Args:
            data (Dict[str, Any]): Expected to contain key-value pairs where keys
                are strings and values can be any type.
            variables (Dict[str, Any]): Expected to be a collection of key-value
                pairs where keys are variable names and values are their corresponding
                values.
            header (str): Expected to be passed as an argument when calling this
                method. Its purpose is not explicitly stated, but it is likely
                related to decoding the data provided in the input dictionary.

        Returns:
            Dict[str, Any]: A dictionary where keys are strings and values can be
            any type. This returned dictionary is the input parameter `data`
            modified by the auxiliary method `__aux_decode`.

        """

        self.__aux_decode(data, variables, header)
        return data
