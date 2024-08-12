import click
import inspect
from typing import Any, Callable, Optional


class CLICommand():

    """
    Facilitates the creation and management of commands for a command-line interface
    (CLI). It takes an optional command name and docstring, and automatically
    generates callback functions for each method in the class that can be used as
    CLI commands.

    Attributes:
        __click_group (clickGroup): Initialized with a new instance of a Click
            Group object.
        __class__ (type): A built-in Python attribute that holds the class of the
            object. It returns a reference to the class of the object, i.e., `CLICommand`.
        __generate_callback (Callable[[Callable,Any,Any],None]): Used to generate
            a new callback function from a given function f by adding self as its
            first argument.

    """
    def __init__(self, command: Optional[str] = None) -> None:

        """
        Initializes a Click group with commands and sets its name and help message.
        It also wraps the callback functions of commands with a wrapper function
        (`self.__generate_callback`) before adding them to the Click group.

        Args:
            command (Optional[str]): Optional by default. If provided, it sets the
                name for the click group; otherwise, it defaults to the lowercase
                class name.

        """
        self.__click_group = click.Group()
        self.__click_group.name = command or self.__class__.__name__.lower()
        self.__click_group.help = self.__class__.__dict__.get('__doc__')

        # Replace original callbacks with caller objects to support 'self'
        for name, command in inspect.getmembers(self):
            if isinstance(command, click.Command):
                if command.callback:
                    command.callback = self.__generate_callback(command.callback)
                    self.__click_group.add_command(command, name)

    def __generate_callback(self, f: Callable) -> Callable[[Any, Any], None]:
        """
        Generates a new callback function that can be used to execute an arbitrary
        function (`f`) with a custom context. The generated callback takes any
        number and type of arguments, and forwards them to the original function
        (`f`) after prepending its own instance as the first argument.

        """
        def callback(*f_args: Any, **f_kwargs: Any) -> None:
            f(self, *f_args, **f_kwargs)
        return callback

    def add_to_group(self, group: click.Group) -> None:
        group.add_command(self.__click_group)

# if __name__ == '__main__':

#     class GreeterCommand(CLICommand):
#         """ Speak to an user
#         """

#         def __init__(self, name: str, age: int):
#             super().__init__(command='greet')
#             self.name = name
#             self.age = age

#         @click.command()
#         @click.argument('name', type=str)
#         def hello(self, name: str) -> None:
#             """Greet user"""
#             print(f'Hello {name}, my name is {self.name} and I am {self.age} years old.')

#     # ==================================================================

#     cli = click.Group()
#     GreeterCommand('Bot Fred', 42).add_to_group(cli)
#     cli()
