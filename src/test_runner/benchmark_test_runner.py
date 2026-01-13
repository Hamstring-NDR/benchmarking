import argparse

from src.base.logging_config import get_logger
from src.base.setup_config import setup_config
from src.test_runner.test_types.main import (
    BurstTest,
    RampUpTest,
    MaximumThroughputTest,
    LongTermTest,
)

LOGGER = get_logger("test_runner.benchmark_test_runner")
CONFIG = setup_config()

CONFIG_TESTS = CONFIG["tests"]


class BenchmarkTestRunner:
    """Manages the execution of different benchmark tests based on command line arguments.

    Parses command line arguments to select and run specific benchmark tests
    (burst, long_term, maximum_throughput, ramp_up) with configured parameters.
    """
    def __init__(self):
        """Initializes the argument parser and sub-parsers for each test type."""
        self.parser = argparse.ArgumentParser(
            description="Execute with given test parameters. "
            "By default, configuration file values are used."
        )
        self.subparsers = self.parser.add_subparsers(
            dest="test_type",
            required=True,
            help="Available benchmark tests to execute...",
        )

        self.__add_burst_parser()
        self.__add_long_term_parser()
        self.__add_maximum_throughput_parser()
        self.__add_ramp_up_parser()

    def run(self):
        """Parses arguments and executes the selected test function."""
        args = self.parser.parse_args()
        args.func(args)

    @staticmethod
    def _execute_burst_with_report(args):
        """Executes the burst test and generates a report.

        Args:
             args: Parsed command line arguments containing test configuration.
        """
        burst_test = BurstTest(
            normal_rate_interval_length=args.normal_interval_length,
            normal_rate_msg_per_sec=args.normal_data_rate,
            burst_rate_interval_length=args.burst_interval_length,
            burst_rate_msg_per_sec=args.burst_data_rate,
            number_of_repetitions=args.number_of_repetitions,
        )
        burst_test.execute_and_generate_report()

    @staticmethod
    def _execute_long_term_with_report(args):
        """Executes the long-term test and generates a report.

        Args:
             args: Parsed command line arguments containing test configuration.
        """
        long_term_test = LongTermTest(
            full_length_in_minutes=args.length,
            messages_per_second=args.data_rate,
        )
        long_term_test.execute_and_generate_report()

    @staticmethod
    def _execute_maximum_throughput_with_report(args):
        """Executes the maximum throughput test and generates a report.

        Args:
             args: Parsed command line arguments containing test configuration.
        """
        maximum_throughput_test = MaximumThroughputTest(
            full_length_in_seconds=args.length,
        )
        maximum_throughput_test.execute_and_generate_report()

    @staticmethod
    def _execute_ramp_up_with_report(args):
        """Executes the ramp-up test and generates a report.

        Args:
             args: Parsed command line arguments containing test configuration.
        """
        ramp_up_test = RampUpTest(
            messages_per_second_in_intervals=[
                int(e) for e in args.data_rates.split(",")
            ],
            interval_lengths_in_seconds=[int(e) for e in args.durations.split(",")],
        )
        ramp_up_test.execute_and_generate_report()

    def __add_burst_parser(self):
        """Configures the argument parser for the burst test."""
        parser = self.subparsers.add_parser("burst", help="Burst benchmark test")
        parser.add_argument(
            "--normal_data_rate",
            type=float,
            help=f"Normal Rate Test: data rate in msg/s [float | int], "
                 f"default: {CONFIG_TESTS['burst']['normal_rate']['data_rate']}",
            default=CONFIG_TESTS["burst"]["normal_rate"]["data_rate"],
        )
        parser.add_argument(
            "--normal_interval_length",
            type=float,
            help=f"Normal Rate Test: interval length in seconds [float | int], "
                 f"default: {CONFIG_TESTS['burst']['normal_rate']['interval_length']}",
            default=CONFIG_TESTS["burst"]["normal_rate"]["interval_length"],
        )
        parser.add_argument(
            "--burst_data_rate",
            type=float,
            help=f"Burst Rate Test: data rate in msg/s [float | int], "
                 f"default: {CONFIG_TESTS['burst']['burst_rate']['data_rate']}",
            default=CONFIG_TESTS["burst"]["burst_rate"]["data_rate"],
        )
        parser.add_argument(
            "--burst_interval_length",
            type=float,
            help=f"Burst Rate Test: interval length in seconds [float | int], "
                 f"default: {CONFIG_TESTS['burst']['burst_rate']['interval_length']}",
            default=CONFIG_TESTS["burst"]["burst_rate"]["interval_length"],
        )
        parser.add_argument(
            "--number_of_repetitions",
            type=int,
            help=f"number of intervals [int], default: {CONFIG_TESTS['burst']['number_of_repetitions']}",
            default=CONFIG_TESTS["burst"]["number_of_repetitions"],
        )
        parser.set_defaults(func=self._execute_burst_with_report)

    def __add_long_term_parser(self):
        """Configures the argument parser for the long-term test."""
        parser = self.subparsers.add_parser(
            "long_term", help="Long-term benchmark test"
        )
        parser.add_argument(
            "--data_rate",
            type=float,
            help=f"Data rate in msg/s [float | int], default: {CONFIG_TESTS['long_term']['data_rate']}",
            default=CONFIG_TESTS["long_term"]["data_rate"],
        )
        parser.add_argument(
            "--length",
            type=float,
            help=f"Full length/duration in minutes [float | int], default: {CONFIG_TESTS['long_term']['length']}",
            default=CONFIG_TESTS["long_term"]["length"],
        )
        parser.set_defaults(func=self._execute_long_term_with_report)

    def __add_maximum_throughput_parser(self):
        """Configures the argument parser for the maximum throughput test."""
        parser = self.subparsers.add_parser(
            "maximum_throughput", help="Maximum-throughput benchmark test"
        )
        parser.add_argument(
            "--length",
            type=float,
            help=f"Full length/duration in minutes [float | int], default: {CONFIG_TESTS['maximum_throughput']['length'] / 60}",
            default=CONFIG_TESTS["maximum_throughput"]["length"] / 60,
        )
        parser.set_defaults(func=self._execute_maximum_throughput_with_report)

    def __add_ramp_up_parser(self):
        """Configures the argument parser for the ramp-up test."""
        parser = self.subparsers.add_parser("ramp_up", help="Ramp-up benchmark test")
        default_data_rates = []
        default_durations = []

        for e in CONFIG_TESTS["ramp_up"]["intervals"]:
            default_data_rates.append(e[0])
            default_durations.append(e[1])

        parser.add_argument(
            "--data_rates",
            help=f"Data rates per interval in msg/s [List[float | int], "
            f"default: {','.join(str(i) for i in default_data_rates)}",
            default=",".join(str(i) for i in default_data_rates),
        )

        parser.add_argument(
            "--durations",
            help=f"Length/duration per interval in minutes [float | int | List[float | int]], "
            f"single value applies to all intervals, "
            f"default: {','.join(str(i) for i in default_durations)}",
            default=",".join(str(i) for i in default_data_rates),
        )
        parser.set_defaults(func=self._execute_ramp_up_with_report)


if __name__ == "__main__":
    runner = BenchmarkTestRunner()
    runner.run()
