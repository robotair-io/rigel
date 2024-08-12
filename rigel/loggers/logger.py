import logging

BLUE = "\x1b[34;1m"
GREEN = "\x1b[32;1m"
RED = "\x1b[31;1m"
YELLOW = "\x1b[33;1m"
RESET = "\x1b[0m"


# Class extracted and adapted on Sergey Pleshakov's answer at:
# https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
class RigelFormatter(logging.Formatter):
    """
    Formats log messages based on their level (debug, info, warning, error,
    critical). It uses colorized strings to differentiate between levels and returns
    a formatted string for each message. The colors are defined by the `GREEN`,
    `BLUE`, `YELLOW`, and `RED` variables.

    Attributes:
        formats (Dict[int,str]): Used to store the format string for each logging
            level. The keys are integer values representing the different logging
            levels and the values are strings representing the format strings for
            those levels.

    """

    formats = {
        logging.DEBUG: f"{GREEN}%(message)s{RESET}",
        logging.INFO: f"{BLUE}%(message)s{RESET}",
        logging.WARNING: f"{YELLOW}%(levelname)s - %(message)s{RESET}",
        logging.ERROR: f"{RED}%(levelname)s - %(message)s{RESET}",
        logging.CRITICAL: f"{RED}%(levelname)s - %(message)s{RESET}"
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats a log record based on the format corresponding to its level,
        retrieved from a dictionary. It uses the provided log record and returns
        a formatted string.

        Args:
            record (logging.LogRecord): Passed to this method. This object represents
                an event recorded by a logger instance. It contains information
                such as timestamp, log level, message, etc.

        Returns:
            str: The formatted string representation of a log record. It is generated
            by the specified format for the log level of the record using a
            logging.Formatter object.

        """
        log_fmt = self.formats.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger() -> logging.Logger:
    """
    Returns a configured logger named "Rigel" with a debug level. If no handlers
    are attached, it adds a stream handler with a debug level and a custom formatter
    to the logger, enabling logging output to the console.

    Returns:
        logging.Logger: A logger object named "Rigel" that has been configured to
        output debug level logs to the console using a custom formatter.

    """
    logger = logging.getLogger("Rigel")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(RigelFormatter())
        logger.addHandler(ch)

    return logger
