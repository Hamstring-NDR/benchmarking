from abc import abstractmethod

import pandas as pd

from src.base.utils import ReadWriteUtils
from src.test_runner.plotting.metadata_information import (
    DurationMetadataInformation,
    NumberPerTimeMetadataInformation,
    SingleMetadataInformation,
    HourMinuteSecondMetadataInformation,
    RangeNumberPerTimeMetadataInformation,
)


class MetadataConfiguration:

    @abstractmethod
    def get(self, *args) -> dict[tuple[int, int], SingleMetadataInformation]:
        """Retrieves and formats metadata for the overview page.

        Args:
           *args: Variable length argument list.

        Returns:
            dict[tuple[int, int], SingleMetadataInformation]: A dictionary mapping grid positions (row, col)
                                                              to metadata information objects.
        """
        raise NotImplementedError

    def _get_total_number_of_entering_loglines(self, test_identifier: str):
        """Calculates the total number of entering log lines for a specific test.

        Args:
            test_identifier (str): The identifier of the test.

        Returns:
            int: Total cumulative count of entering log lines. Returns None if no data.
        """
        modules_to_csv_paths = ReadWriteUtils.get_modules_to_csv_filepaths(
            "entering_processed_total", test_identifier
        )

        df = pd.read_csv(modules_to_csv_paths["Entering"])
        if df.empty:
            return

        df["timestamp_in"] = pd.to_datetime(df["timestamp_in"])
        latest_row = df.sort_values(by="timestamp_in").iloc[-1]
        return int(latest_row["cumulative_count"])


class BurstMetadata(MetadataConfiguration):

    def get(self, metadata: dict) -> dict[tuple[int, int], SingleMetadataInformation]:
        """Retrieves metadata for Burst tests.

        Args:
            metadata (dict): Dictionary containing test metadata.

        Returns:
            dict[tuple[int, int], SingleMetadataInformation]: Formatted metadata for the report.

        Raises:
            ValueError: If metadata is missing or malformed.
        """
        try:
            start_timestamp = metadata["start_timestamp"]
            end_timestamp = metadata["end_timestamp"]
            parameters = metadata["parameters"]

            # calculation
            total_duration = end_timestamp - start_timestamp

            number_of_bursts = len(parameters["interval_lengths_in_seconds"]) / 2
            normal_rate_msg_per_sec = min(
                parameters["messages_per_second_in_intervals"]
            )
            burst_rate_msg_per_sec = max(parameters["messages_per_second_in_intervals"])
            normal_rate_interval_length = max(parameters["interval_lengths_in_seconds"])
            burst_rate_interval_length = min(parameters["interval_lengths_in_seconds"])

        except Exception:
            raise ValueError("Malformed or missing metadata values")

        return {
            (1, 1): HourMinuteSecondMetadataInformation(
                title="Start time",
                value=start_timestamp.astimezone(),
                include_date=(start_timestamp.date() != end_timestamp.date()),
            ),
            (1, 2): DurationMetadataInformation(
                title="Total duration",
                value=total_duration,
            ),
            (1, 3): RangeNumberPerTimeMetadataInformation(
                title="Normal data rate",
                values=normal_rate_msg_per_sec,
                per="s",
            ),
            (1, 4): RangeNumberPerTimeMetadataInformation(
                title="Normal data rate",
                values=burst_rate_msg_per_sec,
                per="s",
            ),
            # second row
            (2, 1): HourMinuteSecondMetadataInformation(
                title="End time",
                value=end_timestamp.astimezone(),
                include_date=(start_timestamp.date() != end_timestamp.date()),
            ),
            (2, 2): SingleMetadataInformation(
                title="Normal rate interval length",
                value=f"{normal_rate_interval_length:,}s",
            ),
            (2, 3): SingleMetadataInformation(
                title="Burst rate interval length",
                value=f"{burst_rate_interval_length:,}s",
            ),
        }


class LongTermMetadata(MetadataConfiguration):

    def get(self, metadata: dict) -> dict[tuple[int, int], SingleMetadataInformation]:
        """Retrieves metadata for Long Term tests.

        Args:
            metadata (dict): Dictionary containing test metadata.

        Returns:
            dict[tuple[int, int], SingleMetadataInformation]: Formatted metadata for the report.

        Raises:
            ValueError: If metadata is missing or malformed.
        """
        try:
            start_timestamp = metadata["start_timestamp"]
            end_timestamp = metadata["end_timestamp"]
            parameters = metadata["parameters"]

            # calculation
            total_duration = end_timestamp - start_timestamp

        except Exception:
            raise ValueError("Malformed or missing metadata values")

        return {
            (1, 1): HourMinuteSecondMetadataInformation(
                title="Start time",
                value=start_timestamp.astimezone(),
                include_date=(start_timestamp.date() != end_timestamp.date()),
            ),
            (1, 2): RangeNumberPerTimeMetadataInformation(
                title="Input data rate",
                values=parameters["messages_per_second"],
                per="s",
            ),
            # second row
            (2, 1): HourMinuteSecondMetadataInformation(
                title="End time",
                value=end_timestamp.astimezone(),
                include_date=(start_timestamp.date() != end_timestamp.date()),
            ),
            (2, 2): DurationMetadataInformation(
                title="Total duration",
                value=total_duration,
            ),
        }


class MaximumThroughputMetadata(MetadataConfiguration):

    def get(self, metadata: dict) -> dict[tuple[int, int], SingleMetadataInformation]:
        """Retrieves metadata for Maximum Throughput tests.

        Args:
            metadata (dict): Dictionary containing test metadata.

        Returns:
            dict[tuple[int, int], SingleMetadataInformation]: Formatted metadata for the report.

        Raises:
            ValueError: If metadata is missing or malformed.
        """
        try:
            start_timestamp = metadata["start_timestamp"]
            end_timestamp = metadata["end_timestamp"]
            parameters = metadata["parameters"]

            # calculation
            total_duration = end_timestamp - start_timestamp

        except Exception:
            raise ValueError("Malformed or missing metadata values")

        return {
            (1, 1): HourMinuteSecondMetadataInformation(
                title="Start time",
                value=start_timestamp.astimezone(),
                include_date=(start_timestamp.date() != end_timestamp.date()),
            ),
            (1, 2): RangeNumberPerTimeMetadataInformation(
                title="Input data rate",
                values=parameters["messages_per_second"],
                per="s",
            ),
            # second row
            (2, 1): HourMinuteSecondMetadataInformation(
                title="End time",
                value=end_timestamp.astimezone(),
                include_date=(start_timestamp.date() != end_timestamp.date()),
            ),
            (2, 2): DurationMetadataInformation(
                title="Total duration",
                value=total_duration,
            ),
        }


class RampUpMetadata(MetadataConfiguration):

    def get(self, metadata: dict, test_identifier: str) -> dict[tuple[int, int], SingleMetadataInformation]:
        """Retrieves metadata for Ramp Up tests.

        Args:
            metadata (dict): Dictionary containing test metadata.
            test_identifier (str): The identifier of the test.

        Returns:
            dict[tuple[int, int], SingleMetadataInformation]: Formatted metadata for the report.

        Raises:
            ValueError: If metadata is missing or malformed.
        """
        try:
            start_timestamp = metadata["start_timestamp"]
            end_timestamp = metadata["end_timestamp"]
            parameters = metadata["parameters"]
            total_ingoing_loglines = self._get_total_number_of_entering_loglines(test_identifier)

            # calculation
            total_duration = end_timestamp - start_timestamp

            number_of_intervals = len(parameters["interval_lengths_in_seconds"])
            min_interval_length = min(parameters["interval_lengths_in_seconds"])
            max_interval_length = max(parameters["interval_lengths_in_seconds"])

            if min_interval_length == max_interval_length:
                interval_str = f"{number_of_intervals}, {min_interval_length:,}s"
            else:
                interval_str = f"{number_of_intervals}, {min_interval_length:,}s - {max_interval_length:,}s"

        except Exception:
            raise ValueError("Malformed or missing metadata values")

        return {
            (1, 1): HourMinuteSecondMetadataInformation(
                title="Start time",
                value=start_timestamp.astimezone(),
                include_date=(start_timestamp.date() != end_timestamp.date()),
            ),
            (1, 2): DurationMetadataInformation(
                title="Total duration",
                value=total_duration,
            ),
            (1, 3): RangeNumberPerTimeMetadataInformation(
                title="Input data rate",
                values=parameters["messages_per_second_in_intervals"],
                per="s",
            ),
            # second row
            (2, 1): HourMinuteSecondMetadataInformation(
                title="End time",
                value=end_timestamp.astimezone(),
                include_date=(start_timestamp.date() != end_timestamp.date()),
            ),
            (2, 2): NumberPerTimeMetadataInformation(
                title="Ingoing logline rate",
                value=total_ingoing_loglines / total_duration.total_seconds(),
                per="s",
            ),
            (2, 3): SingleMetadataInformation(
                title="#Intervals, interval length",
                value=interval_str,
            ),
        }
