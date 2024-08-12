import shutil
from pkg_resources import resource_filename


class RigelfileCreator:
    """
    Copies a file named "Rigelfile" from a specific path within the project's
    assets to the current directory. The copying operation is done using the
    `shutil.copyfile` function, which ensures that all metadata (permissions,
    timestamp) of the source file are preserved in the destination file.

    """

    def create(self) -> None:
        """
        Creates a copy of the "Rigelfile" asset file from a resource directory to
        the current working directory, effectively duplicating the file at the
        specified location.

        """

        rigelfile_path = resource_filename(__name__, 'assets/Rigelfile')
        shutil.copyfile(rigelfile_path, 'Rigelfile')
