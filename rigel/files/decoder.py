import os
import re
from rigelcore.exceptions import UndeclaredGlobalVariableError
from typing import Any, Dict


class YAMLDataDecoder:
    """
    Decodes YAML data by replacing template variables enclosed between `{{ }}`
    delimiters with their corresponding values from a dictionary or environment
    variables. It recursively traverses dictionaries and lists to process nested
    structures.

    """

    def __extract_variable_name(self, match: str) -> str:
        """
        Removes curly braces and spaces from a given string, effectively extracting
        a variable name from a YAML-like format.

        """
        chars_to_remove = ['{', '}', ' ']
        variable_name = match
        for c in chars_to_remove:
            variable_name = variable_name.replace(c, '')
        return variable_name

    def __aux_decode(self, data: Any, vars: Any, path: str = '') -> None:
        """
        Recursively decodes complex data structures such as dictionaries and lists
        from their encoded form to their original structure.

        """
        if isinstance(data, dict):
            self.__aux_decode_dict(data, vars, path)
        elif isinstance(data, list):
            self.__aux_decode_list(data, vars, path)

    def __aux_decode_dict(self, data: Any, vars: Any, path: str = '') -> None:
        """
        Recursively decodes a dictionary by replacing placeholder variables with
        actual values from environment variables or an input dictionary, ensuring
        that string fields contain delimiters and raising an error for undeclared
        global variables.

        """
        for k, v in data.items():

            new_path = f'{path}.{k}' if path else k

            if isinstance(v, str):  # in order to contain delimiters the field must be of type str
                matches = re.findall(r'{{[a-zA-Z0-9_\s\-\!\?]+}}', v)
                for match in matches:
                    variable_name = self.__extract_variable_name(match)
                    if variable_name in vars:
                        data[k] = data[k].replace(match, vars[variable_name])
                    elif variable_name in os.environ:
                        data[k] = data[k].replace(match, os.environ[variable_name])
                    else:
                        raise UndeclaredGlobalVariableError(field=new_path, var=variable_name)
            else:
                self.__aux_decode(v, vars, new_path)

    def __aux_decode_list(self, data: Any, vars: Dict[str, Any], path: str = '') -> None:
        """
        Recursively decodes a list by replacing placeholders ({{}}) with actual
        values from variables or environment variables, and then calls itself for
        each element in the list if it's not a string.

        """

        for idx, elem in enumerate(data):

            new_path = f'{path}[{idx}]'

            if isinstance(elem, str):  # in order to contain delimiters the field must be of type str
                matches = re.findall(r'{{[a-zA-Z0-9_\s\-\!\?]+}}', elem)
                for match in matches:
                    variable_name = self.__extract_variable_name(match)
                    if variable_name in vars:
                        data[idx] = data[idx].replace(match, vars[variable_name])
                    elif variable_name in os.environ:
                        data[idx] = data[idx].replace(match, os.environ[variable_name])
                    else:
                        raise UndeclaredGlobalVariableError(field=new_path, var=variable_name)
            else:
                self.__aux_decode(elem, vars, new_path)

    def decode(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes a dictionary-like object as input and decodes its contents. It
        extracts variables from the input, calls an auxiliary decoding function,
        and returns the decoded data. The method is part of a process that involves
        parsing YAML data into a structured format.

        Args:
            data (Dict[str, Any]): Expected to be a dictionary with at least one
                key-value pair where 'vars' is the key and its value is an iterable
                list of variables.

        Returns:
            Dict[str, Any]: Modified version of input data after calling another
            internal method `__aux_decode`. The returned dictionary preserves its
            original structure but may contain decoded values.

        """

        # Function entry point.
        variables = data.get('vars') or []
        self.__aux_decode(data, variables)
        return data
