import yaml

from src.base import CONFIG_FILEPATH
from src.base.logging_config import get_logger

logger = get_logger()


def setup_config():
    """
    Loads the configuration data from the configuration file and returns it as the corresponding Python object.

    Returns:
         Configuration data as corresponding Python object

    Raises:
        FileNotFoundError: Configuration file could not be opened
    """
    try:
        logger.debug(
            f"Opening benchmark test configuration file at {CONFIG_FILEPATH}..."
        )
        with open(CONFIG_FILEPATH, "r") as file:
            configuration = yaml.safe_load(file)
    except FileNotFoundError:
        logger.critical(f"File {CONFIG_FILEPATH} does not exist. Aborting...")
        raise

    logger.debug("Configuration file successfully opened and information returned.")
    return configuration
