import yaml

from src import CONFIG_FILEPATH
from src.base.logging_config import get_logger

LOGGER = get_logger()


def setup_config():
    """Loads configuration data from the configuration file.
    
    Returns:
        dict: Configuration data as corresponding Python object.

    Raises:
        FileNotFoundError: If the configuration file could not be opened.
    """
    try:
        LOGGER.debug(
            f"Opening benchmark test configuration file at {CONFIG_FILEPATH}..."
        )
        with open(CONFIG_FILEPATH, "r") as file:
            configuration = yaml.safe_load(file)
    except FileNotFoundError:
        LOGGER.critical(f"File {CONFIG_FILEPATH} does not exist. Aborting...")
        raise

    LOGGER.debug("Configuration file successfully opened and information returned.")
    return configuration
