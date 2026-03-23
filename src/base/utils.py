from datetime import datetime, timezone
from pathlib import Path

import yaml

from src import BASE_DIR, DIRECTORY_STRUCTURE_FILEPATH
from src.base.logging_config import get_logger

LOGGER = get_logger()


class ReadWriteUtils:
    """Utility class for reading and writing files.

    Provides static methods for handling metadata and directory structure files,
    including file I/O and path resolution.
    """

    @staticmethod
    def write_metadata(metadata_filepath: Path, data: dict):
        """Writes metadata to a YAML file.

        Args:
            metadata_filepath (Path): Path to the metadata file.
            data (dict): Metadata dictionary to write.

        Raises:
            FileNotFoundError: If the file path does not exist.
        """
        try:
            with open(metadata_filepath, "w") as file:
                yaml.dump(data, file, default_flow_style=False)
        except FileNotFoundError:
            LOGGER.critical(f"File {metadata_filepath} does not exist. Aborting...")
            raise

    @staticmethod
    def get_metadata(test_identifier: str):
        """Retrieves metadata for a specific test identifier.

        Args:
            test_identifier (str): Unique identifier of the test run.

        Returns:
            dict: Parsed metadata content.

        Raises:
            FileNotFoundError: If the metadata file does not exist.
        """
        metadata_filepath = Path(
            BASE_DIR / "benchmark_results" / test_identifier / "metadata.yml"
        )

        try:
            with open(metadata_filepath, "r") as file:
                data = yaml.safe_load(file)
        except FileNotFoundError:
            LOGGER.critical(f"File {metadata_filepath} does not exist. Aborting...")
            raise

        return data

    @staticmethod
    def get_modules_to_csv_filepaths(for_plot: str, test_identifier: str):
        """Retrieves CSV file paths for a specific plot configuration.

        Resolves relative paths from the directory structure configuration to
        absolute system paths based on the test identifier.

        Args:
            for_plot (str): Name of the plot configuration to look up.
            test_identifier (str): Unique identifier of the test run.

        Returns:
            dict: Mapping of module names to their absolute CSV file paths.

        Raises:
            FileNotFoundError: If the directory structure config file is missing.
            KeyError: If the plot name or file structure is invalid.
        """
        try:
            with open(DIRECTORY_STRUCTURE_FILEPATH, "r") as file:
                data = yaml.safe_load(file)
        except FileNotFoundError:
            LOGGER.critical(
                f"File {DIRECTORY_STRUCTURE_FILEPATH} does not exist. Aborting..."
            )
            raise

        try:
            result = data[for_plot]["files"]
        except KeyError:
            LOGGER.critical(
                f"Invalid data directory structure configuration or given plot name does not exist"
            )
            raise

        for module in result.keys():
            filename = result[module]
            result[module] = str(
                Path(
                    BASE_DIR / "benchmark_results" / test_identifier / "data" / filename
                )
            )

        return result

    @staticmethod
    def get_plot_output_filepath(for_plot: str, file_identifier: str):
        """Determines the output path for a generated plot.

        Args:
            for_plot (str): Name of the plot configuration.
            file_identifier (str): Unique identifier for the output file/directory.

        Returns:
            Path: Absolute path where the plot should be saved.

        Raises:
            FileNotFoundError: If the directory structure config file is missing.
            KeyError: If the plot name configuration is missing.
        """
        try:
            with open(DIRECTORY_STRUCTURE_FILEPATH, "r") as file:
                data = yaml.safe_load(file)
        except FileNotFoundError:
            LOGGER.critical(
                f"File {DIRECTORY_STRUCTURE_FILEPATH} does not exist. Aborting..."
            )
            raise

        try:
            output_filename = data[for_plot]["output_filename"]
        except KeyError:
            LOGGER.critical(
                f"Invalid data directory structure configuration or given plot name does not exist"
            )
            raise

        output_filename = Path(
            BASE_DIR
            / "benchmark_results"
            / file_identifier
            / "graphs"
            / output_filename
        )
        return output_filename


class TimeUtils:
    @staticmethod
    def now() -> datetime.timestamp:
        """Returns the current UTC time as timezone-aware datetime timestamp.

        Must be used for all internal timestamps.

        Returns:
            datetime.timestamp: Current UTC timestamp.
        """
        return datetime.now(timezone.utc)
