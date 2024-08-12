import click
from rigel.cli.command import CLICommand
from rigel.exceptions import RigelError
from rigel.loggers import get_logger
from rigel.orchestrator import Orchestrator
from sys import exit

LOGGER = get_logger()


class RunJobCommand(CLICommand):
    """
    Wraps two commands: 'run job' and 'run sequence'. Each command takes a string
    argument (job or sequence name). The class orchestrates jobs and sequences by
    instantiating an `Orchestrator` object, which runs the specified job or sequence.

    """

    def __init__(self) -> None:
        super().__init__(command='run')

    @click.command()
    @click.argument('job', type=str)
    def job(self, job: str) -> None:
        """
        Executes a job from the Rigelfile and orchestrates its execution using an
        Orchestrator object. If any error occurs during execution, it logs the
        error with a severity level of ERROR and terminates the program.

        Args:
            job (str): Defined by @click.argument decorator. It expects a string
                input from the user when calling the command.

        """
        try:
            orchestrator = Orchestrator('./Rigelfile')
            orchestrator.run_job(job)
        except RigelError as err:
            LOGGER.error(err)
            exit(1)

    @click.command()
    @click.argument('sequence', type=str)
    def sequence(self, sequence: str) -> None:
        """
        Runs a sequence of commands defined by a given string. The command
        orchestrator is initialized with an Rigel file, and the sequence is executed
        using the orchestrator's run_sequence method. If any error occurs during
        execution, it logs the error and exits.

        Args:
            sequence (str): Obtained from an argument passed to the command-line
                interface by click. It is used as input for the Orchestrator's
                `run_sequence` method.

        """
        try:
            orchestrator = Orchestrator('./Rigelfile')
            orchestrator.run_sequence(sequence)
        except RigelError as err:
            LOGGER.error(err)
            exit(1)
