from typing import Protocol, runtime_checkable


@runtime_checkable
class Plugin(Protocol):
    """
    Defines a protocol for plugins that can be executed and stopped. It consists
    of two methods: `run`, which initiates the plugin's execution, and `stop`,
    which terminates its operation.

    """

    def run(self) -> None:
        """
        Use this function as an entry point for your plugin.
        """
        ...

    def stop(self) -> None:
        """
        Use this function to gracefully clean plugin resources.
        """
        ...
