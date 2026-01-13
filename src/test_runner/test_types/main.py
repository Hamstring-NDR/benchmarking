from src.base.logging_config import get_logger
from src.test_runner.plotting.metadata_configuration import (
    MetadataConfiguration,
    RampUpMetadata,
    MaximumThroughputMetadata,
    LongTermMetadata,
    BurstMetadata,
)
from src.test_runner.test_types.extended import (
    SingleIntervalTest,
    IntervalBasedTest,
)

LOGGER = get_logger("test_runner.test_types")


class BurstTest(IntervalBasedTest):
    """Starts with a normal rate, sends a high rate for a short period, then returns to normal rate.
    Repeats the process for a defined number of times."""

    def __init__(
        self,
        normal_rate_msg_per_sec: float | int,
        burst_rate_msg_per_sec: float | int,
        normal_rate_interval_length: float | int,
        burst_rate_interval_length: float | int,
        number_of_repetitions: int = 1,
    ):
        """Initializes a burst test.

        Args:
            normal_rate_msg_per_sec (float | int): Message rate during normal periods.
            burst_rate_msg_per_sec (float | int): Message rate during burst periods.
            normal_rate_interval_length (float | int): Duration of normal periods in seconds.
            burst_rate_interval_length (float | int): Duration of burst periods in seconds.
            number_of_repetitions (int): Number of burst cycles to repeat. Default: 1.
        """
        interval_lengths_in_seconds = [normal_rate_interval_length]
        messages_per_second_in_intervals = [normal_rate_msg_per_sec]

        for _ in range(number_of_repetitions):
            messages_per_second_in_intervals.append(burst_rate_msg_per_sec)
            messages_per_second_in_intervals.append(normal_rate_msg_per_sec)

            interval_lengths_in_seconds.append(burst_rate_interval_length)
            interval_lengths_in_seconds.append(normal_rate_interval_length)

        super().__init__(
            name="Burst",
            interval_lengths_in_seconds=interval_lengths_in_seconds,
            messages_per_second_in_intervals=messages_per_second_in_intervals,
        )

    def _BaseTest__get_metadata_configuration(self) -> MetadataConfiguration:
        return BurstMetadata()


class LongTermTest(SingleIntervalTest):
    def __init__(
        self, full_length_in_minutes: float | int, messages_per_second: float | int
    ):
        """Initializes a long-term test.

        Args:
            full_length_in_minutes (float | int): Duration in minutes for which to send messages.
            messages_per_second (float | int): Number of messages per second when sending messages.
        """
        self.messages_per_second = messages_per_second
        self.full_length_in_minutes = full_length_in_minutes

        super().__init__(
            "Long Term",
            full_length_in_minutes,
            messages_per_second,
        )

    def _BaseTest__get_metadata_configuration(self) -> MetadataConfiguration:
        return LongTermMetadata()


class MaximumThroughputTest(SingleIntervalTest):
    """Keeps a consistent rate that is too high to be handled."""

    def __init__(
        self,
        full_length_in_seconds: float | int,
        messages_per_second: float | int = 10000,
    ):
        """Initializes a maximum throughput test.

        Args:
            full_length_in_seconds (float | int): Duration in seconds for which to send messages.
            messages_per_second (float | int): Number of messages per second when sending messages.
                                               Default: 10000.
        """
        super().__init__(
            name="Maximum Throughput",
            full_length_in_minutes=full_length_in_seconds / 60,
            messages_per_second=messages_per_second,
        )

    def _BaseTest__get_metadata_configuration(self) -> MetadataConfiguration:
        return MaximumThroughputMetadata()


class RampUpTest(IntervalBasedTest):
    """Starts with a low rate and increases the rate in fixed intervals."""

    def __init__(
        self,
        interval_lengths_in_seconds: int | float | list[int | float],
        messages_per_second_in_intervals: list[float | int],
    ):
        """Initializes a ramp-up test.

        Args:
            interval_lengths_in_seconds (int | float | list[int | float]): Single value to use for each interval,
                                                                           or list of lengths for each interval.
            messages_per_second_in_intervals (list[float | int]): List of message rates per interval.
        """
        super().__init__(
            "Ramp Up",
            interval_lengths_in_seconds,
            messages_per_second_in_intervals,
        )

    def _BaseTest__get_metadata_configuration(self) -> MetadataConfiguration:
        return RampUpMetadata()
