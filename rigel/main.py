import click
import os
import shutil
from pkg_resources import resource_filename
from rigel.cli.run import RunJobCommand
from rigel.loggers import get_logger


LOGGER = get_logger()


@click.group()
def cli() -> None:
    """
    Defines a Click command-line interface (CLI) group with no explicit commands
    or options, effectively creating an empty CLI namespace that can be extended
    later by adding subcommands and options using the Click decorators.

    """
    pass


@click.command()
@click.option('--force', 'force', type=bool, is_flag=True, help='Overwrite existing Rigelfile')
def init(force: bool) -> None:
    """
    Initializes a Rigelfile in the current directory by copying an existing template
    file if it does not already exist, or overwrites an existing one if the `--force`
    flag is provided. It informs the user of any existing files and provides
    instructions on how to use Rigel.

    Args:
        force (bool): Flag-like, indicating whether to overwrite an existing
            Rigelfile if it exists. It is used in conjunction with the `--force`
            command-line option.

    """

    if os.path.exists('./Rigelfile') and not force:
        LOGGER.info("""
        A Rigelfile already exists in this directory.
        To overwrite it with a new one rerun this command with the --force flag.
        """)

    else:
        rigelfile_path = resource_filename(__name__, 'assets/Rigelfile')
        shutil.copyfile(rigelfile_path, 'Rigelfile')
        LOGGER.info("""
        A Rigelfile has been placed in this directory.
        Please read the comments in the Rigelfile
        as well as documentation for more information on using Rigel.
        """)


def main() -> None:
    """
    Sets up a command-line interface (CLI) by adding a job command and an
    initialization command, then executes the CLI.

    """
    RunJobCommand().add_to_group(cli)

    cli.add_command(init)
    cli()


if __name__ == '__main__':
    main()
