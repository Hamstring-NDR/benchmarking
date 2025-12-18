import datetime
from abc import abstractmethod
from typing import Optional

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt, ticker

from src.base.logging_config import get_logger
from src.base.utils import ReadWriteUtils

LOGGER = get_logger()


class PlotGenerator:
    """Plots given data and combines it into figures."""

    def __init__(self, plot_name: str, test_identifier: str):
        self.plot_name = plot_name
        self.test_identifier = test_identifier
        self.metadata = ReadWriteUtils.get_metadata(test_identifier)

        self.default_fig_size = (10, 5)

    @abstractmethod
    def plot(self, *args, **kwargs):
        raise NotImplementedError

    def save_to_file(self):
        output_filepath = ReadWriteUtils.get_plot_output_filepath(
            self.plot_name, self.test_identifier
        )
        output_filepath.parent.mkdir(parents=True, exist_ok=True)

        plt.savefig(output_filepath, dpi=300, bbox_inches="tight")
        LOGGER.info(f"File saved at {output_filepath}")

    def _get_start_time(self) -> datetime.datetime:
        return self.metadata["start_timestamp"]

    def _set_up_initial_figure(self, fig_size: Optional[tuple[float, float]]):
        if fig_size is None:
            fig_size = self.default_fig_size

        fig_width = fig_size[0]
        fig_height = fig_size[1]

        plt.figure(figsize=(fig_width, fig_height))

    @staticmethod
    def _determine_time_unit(max_value: int, input_unit: str) -> [str, int]:
        max_value_in_seconds = datetime.timedelta(
            **{input_unit: int(max_value)}
        ).total_seconds()
        max_value_in_microseconds = max_value_in_seconds * (10**6)

        units = [
            ("us", 1),
            ("ms", 10**3),
            ("s", 10**6),
            ("min", 60 * (10**6)),
            ("h", 60 * 60 * (10**6)),
            ("d", 24 * 60 * 60 * (10**6)),
        ]
        thresholds = [
            1.3 * (10**3),  # ms for over 1.3 ms
            1.3 * (10**6),  # s for over 1.3 s
            5 * 60 * (10**6),  # min for over 5 min
            3 * 60 * 60 * (10**6),  # h for over 3 h
            3 * 24 * 60 * 60 * (10**6),  # d for over 3 d
            float("inf"),  # d for everything above
        ]

        for (unit, factor), threshold in zip(units, thresholds):
            if max_value_in_microseconds < threshold:
                return unit, factor

    @staticmethod
    def _get_colors():
        return plt.rcParams["axes.prop_cycle"].by_key()["color"]


class GraphPlotGenerator(PlotGenerator):

    @staticmethod
    def _set_x_ticks(x_unit: str):
        if x_unit == "s":
            plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(30))

    @staticmethod
    def _add_interval_lines(intervals_in_sec: Optional[list[int]]):
        if intervals_in_sec is not None:
            x_values = [0]

            for i in intervals_in_sec:
                x_values.append(x_values[-1] + i)

            for x in x_values[1:]:
                plt.axvline(
                    x, color="gray", linestyle="--", linewidth=1
                )  # TODO: Check for different x_units

    @staticmethod
    @abstractmethod
    def _get_x_label() -> str:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _get_y_label() -> str:
        raise NotImplementedError


class LatencyComparisonPlotGenerator(GraphPlotGenerator):

    def __init__(
        self,
        test_identifier: str,
        intervals_in_sec: Optional[list[int]] = None,
        data_rates_per_interval: Optional[list[int]] = None,
    ):
        plot_name = "latency_comparison"
        super().__init__(plot_name=plot_name, test_identifier=test_identifier)

        self.intervals_in_sec = intervals_in_sec
        self.data_rates_per_interval = data_rates_per_interval

        self.default_fig_size = (12.5, 4.5)

    def plot(
        self,
        fig_size: tuple[float, float] = None,
        median_smooth: bool = True,
        y_input_unit: str = "microseconds",
        color_start_index: int = 0,
    ):
        """TODO
        Creates a figure and plots the given latency data as graphs. All graphs are plotted into the same figure,
                which is then stored as a file.

                Args:
                    median_smooth (bool): True if the data should be smoothed, False by default
                    y_input_unit (str): Unit of the data given as input, "microseconds" by default
                    color_start_index (int): First index of the color palette to be used, 0 by default
        """
        self._set_up_initial_figure(fig_size)
        start_time = self._get_start_time()

        colors = self._get_colors()  # initialize color palette for graphs
        cur_color_index = color_start_index

        total_max_time = 0  # seconds
        total_max_value = 0

        dataframes = {}
        modules_to_csv_paths = ReadWriteUtils.get_modules_to_csv_filepaths(
            self.plot_name, self.test_identifier
        )

        for name, file in modules_to_csv_paths.items():
            df = pd.read_csv(file, parse_dates=["time"]).sort_values(by="time")

            if df.empty:
                continue  # skip empty datafiles

            df["time"] = (
                df["time"] - start_time.replace(tzinfo=None)
            ).dt.total_seconds()

            if median_smooth:
                window_size = max(1, len(df) // 100)
                df["value"] = (
                    df["value"]
                    .rolling(window=window_size, center=True, min_periods=1)
                    .median()
                )

            dataframes[name] = df
            df.loc[df["time"].diff() > 2, "value"] = np.nan  # fill gaps

            df_max_time = df["time"].max()
            if df_max_time > total_max_time:
                total_max_time = df_max_time

            df_max_value = df["value"].max()
            if df_max_value > total_max_value:
                total_max_value = df_max_value

        x_unit, x_scale = self._determine_time_unit(total_max_time, "seconds")
        y_unit, y_scale = self._determine_time_unit(total_max_value, y_input_unit)

        for name, df in dataframes.items():
            self.__plot_core(name, df, x_scale, y_scale, colors[cur_color_index])
            cur_color_index += 1

        self._add_interval_lines(self.intervals_in_sec)
        self._add_interval_markings()

        plt.xlim(left=0)
        self._set_x_ticks(x_unit)

        self._activate_grid()
        self._set_labels(x_unit, y_unit, median_smooth)

        if len(modules_to_csv_paths) > 1:
            plt.legend()

        self.save_to_file()

    def __plot_core(
        self, name: str, df: pd.DataFrame, x_scale: int, y_scale: int, color
    ):
        plt.yscale("log")
        plt.plot(
            df["time"] / x_scale * (10**6),
            df["value"] / y_scale,
            marker="o",
            markersize=1,
            label=name,
            color=color,
        )

    @staticmethod
    def _get_x_label():
        return "Time"

    @staticmethod
    def _get_y_label():
        return "Latency"

    def _set_labels(self, x_unit: str, y_unit: str, median_smooth: bool):
        plt.xlabel(f"{self._get_x_label()} [{x_unit}]", labelpad=10)
        plt.ylabel(
            f"{self._get_y_label()} [{y_unit}]"
            + (" (median-smoothed)" if median_smooth else "")
        )

    @staticmethod
    def _activate_grid():
        plt.grid(color="lightgray")

    def _add_interval_markings(self):
        if (
            self.intervals_in_sec is not None
            and self.data_rates_per_interval is not None
            and len(self.intervals_in_sec) == len(self.data_rates_per_interval)
        ):
            # prepare list of interval starting times
            interval_starts_in_sec = [
                sum(self.intervals_in_sec[:i])
                for i in range(len(self.intervals_in_sec))
            ]
            interval_starts_in_sec.append(
                sum(self.intervals_in_sec[: len(self.intervals_in_sec)])
            )  # add interval after the test

            # prepare list of data rates
            data_rates_per_interval = self.data_rates_per_interval.copy()
            data_rates_per_interval.append(0)  # add 0 after the test

            y_max = plt.ylim()[1]

            for rate, interval_start in zip(
                data_rates_per_interval, interval_starts_in_sec
            ):
                plt.annotate(
                    f"{rate:,}/s \u2192",  # arrow to the right
                    xy=(interval_start, y_max),
                    xytext=(0, 9),
                    textcoords="offset points",
                    ha="left",
                    va="top",
                    fontsize=7,
                    color="gray",
                )


class FillLevelsComparisonPlotGenerator(GraphPlotGenerator):

    def __init__(
        self,
        test_identifier: str,
        intervals_in_sec: Optional[list[int]] = None,
    ):
        plot_name = "fill_levels_comparison"
        super().__init__(plot_name=plot_name, test_identifier=test_identifier)

        self.intervals_in_sec = intervals_in_sec

        self.default_fig_size = (8.35, 4.3)

    def plot(
        self,
        fig_size: tuple[float, float] = None,
        median_smooth: bool = True,
        color_start_index: int = 0,
    ):
        """TODO
        Creates a figure and plots the given fill level data as graphs. All graphs are plotted into the same figure,
        which is then stored as a file.

        Args:
            median_smooth (bool): True if the data should be smoothed, False by default
            color_start_index (int): First index of the color palette to be used, 0 by default
        """
        self._set_up_initial_figure(fig_size)
        start_time = self._get_start_time()

        colors = self._get_colors()  # initialize color palette for graphs
        cur_color_index = color_start_index

        total_max_time = 0  # seconds
        total_max_value = 0

        dataframes = {}
        modules_to_csv_paths = ReadWriteUtils.get_modules_to_csv_filepaths(
            self.plot_name, self.test_identifier
        )

        for name, file in modules_to_csv_paths.items():
            df = pd.read_csv(file, parse_dates=["timestamp"]).sort_values(
                by="timestamp"
            )

            if df.empty:
                continue  # skip empty datafiles

            df["timestamp"] = (
                df["timestamp"] - start_time.replace(tzinfo=None)
            ).dt.total_seconds()

            if median_smooth:
                window_size = max(1, len(df) // 100)
                df["entry_count"] = (
                    df["entry_count"]
                    .rolling(window=window_size, center=True, min_periods=1)
                    .median()
                )

            dataframes[name] = df
            df.loc[df["timestamp"].diff() > 2, "entry_count"] = np.nan  # fill gaps

            df_max_time = df["timestamp"].max()
            if df_max_time > total_max_time:
                total_max_time = df_max_time

            df_max_value = df["entry_count"].max()
            if df_max_value > total_max_value:
                total_max_value = df_max_value

        x_unit, x_scale = self._determine_time_unit(total_max_time, "seconds")

        for name, df in dataframes.items():
            self.__plot_core(name, df, x_scale, colors[cur_color_index])
            cur_color_index += 1

        self._add_interval_lines(self.intervals_in_sec)

        plt.xlim(left=0)
        self._set_x_ticks(x_unit)

        self._activate_grid()
        self._set_labels(x_unit, median_smooth)

        if len(modules_to_csv_paths) > 1:
            plt.legend()

        self.save_to_file()

    def __plot_core(self, name: str, df: pd.DataFrame, x_scale: int, color):
        plt.yscale("log")
        plt.plot(
            df["timestamp"] / x_scale * (10**6),
            df["entry_count"],
            marker="o",
            markersize=1,
            label=name,
            color=color,
        )

    @staticmethod
    def _get_x_label():
        return "Time"

    @staticmethod
    def _get_y_label():
        return "Fill Level"

    def _set_labels(self, x_unit: str, median_smooth: bool):
        plt.xlabel(f"{self._get_x_label()} [{x_unit}]", labelpad=10)
        plt.ylabel(
            f"{self._get_y_label()}" + (" (median-smoothed)" if median_smooth else "")
        )

    @staticmethod
    def _activate_grid():
        plt.grid(color="lightgray")


class EnteringProcessedTotalPlotGenerator(GraphPlotGenerator):

    def __init__(
        self,
        test_identifier: str,
        intervals_in_sec: Optional[list[int]] = None,
    ):
        plot_name = "entering_processed_total"
        super().__init__(plot_name=plot_name, test_identifier=test_identifier)

        self.intervals_in_sec = intervals_in_sec

        self.default_fig_size = (8.35, 4.8)

    def plot(
        self,
        fig_size: tuple[float, float] = None,
        color_start_index: int = 0,
        downsample_factor: int = 500,
    ):
        """TODO
        Creates a figure and plots the entering and processed log lines data. All graphs are plotted into the
        same figure, which is then stored as a file.

        Args:
            color_start_index (int): First index of the color palette to be used, 0 by default
            downsample_factor (int): Factor for downsampling data points, 500 by default
        """
        self._set_up_initial_figure(fig_size)
        start_time = self._get_start_time()

        colors = self._get_colors()  # initialize color palette for graphs
        cur_color_index = color_start_index

        modules_to_csv_paths = ReadWriteUtils.get_modules_to_csv_filepaths(
            self.plot_name, self.test_identifier
        )

        for name, file in modules_to_csv_paths.items():
            df = pd.read_csv(file)

            if df.empty:
                continue  # skip empty datafiles

            if "timestamp_in" in df.columns:
                timestamp_col = (
                    "timestamp_in"  # entering_total.csv contains "timestamp_in" column
                )
            elif "timestamp" in df.columns:
                timestamp_col = (
                    "timestamp"  # processed_total.csv contains "timestamp" column
                )
            else:
                LOGGER.warning(f"No valid timestamp column found in {file}")
                continue

            df[timestamp_col] = pd.to_datetime(df[timestamp_col])
            df = df.sort_values(by=timestamp_col)
            df["time"] = (
                df[timestamp_col] - start_time.replace(tzinfo=None)
            ).dt.total_seconds()

            self.__plot_core(name, df, downsample_factor, colors[cur_color_index])
            cur_color_index += 1

        self._add_interval_lines(self.intervals_in_sec)

        plt.xlim(left=0)
        self._set_x_ticks("s")  # TODO: Make more flexible

        self._activate_grid()
        self._set_labels()

        plt.legend()

        self.save_to_file()

    def __plot_core(self, name: str, df: pd.DataFrame, downsample_factor: int, color):
        n = max(1, len(df) // downsample_factor)  # downsample for better performance
        plt.plot(
            df["time"][::n],
            df["cumulative_count"][::n],
            linestyle="-",
            label=name,
            color=color,
        )

    @staticmethod
    def _get_x_label():
        return "Time"

    @staticmethod
    def _get_y_label():
        return "Accumulated number of log lines"

    def _set_labels(self):
        plt.xlabel(f"{self._get_x_label()} [s]", labelpad=10)
        plt.ylabel(self._get_y_label())

    @staticmethod
    def _activate_grid():
        plt.grid(color="lightgray")


class EnteringProcessedPerTimePlotGenerator(PlotGenerator):

    def __init__(
        self,
        test_identifier: str,
        intervals_in_sec: Optional[list[int]] = None,
            min_minutes_for_minute_buckets: float = 5,
            min_hours_for_hour_buckets: float = 2,
    ):
        """Initialize the plot generator with adaptive time bucket support.
        
        Args:
            test_identifier: Test identifier for the plot
            intervals_in_sec: Optional list of intervals in seconds
            min_minutes_for_minute_buckets: Minimum duration in minutes to use minute buckets (default: 5)
            min_hours_for_hour_buckets: Minimum duration in hours to use hour buckets (default: 2)
        """
        plot_name = "entering_processed_per_time"
        super().__init__(plot_name=plot_name, test_identifier=test_identifier)

        self.intervals_in_sec = intervals_in_sec
        self.min_minutes_for_minute_buckets = min_minutes_for_minute_buckets
        self.min_hours_for_hour_buckets = min_hours_for_hour_buckets

        self.default_fig_size = (8.35, 4.8)

    def plot(
        self,
        fig_size: tuple[float, float] = None,
        bar_width: float = 0.7,
            x_major_locator: Optional[int] = None,
        y_major_locator: int = 2500,
    ):
        """Creates a bar chart showing entering and processed log lines per time bucket.
        Time bucket size is determined adaptively based on data duration.
        Processed data is displayed as negative bars for mirror effect.

        Args:
            bar_width (float): Width of the bars, 0.7 by default
            x_major_locator (Optional[int]): Major tick interval for x-axis, auto-determined if None
            y_major_locator (int): Major tick interval for y-axis, 2500 by default
        """
        self._set_up_initial_figure(fig_size)
        start_time = self._get_start_time()

        modules_to_csv_paths = ReadWriteUtils.get_modules_to_csv_filepaths(
            self.plot_name, self.test_identifier
        )

        # 1. Determine duration and bucket unit
        duration_check_file = modules_to_csv_paths.get("Entering Second")
        if not duration_check_file:
            # Fallback to any file if specific key not present
            duration_check_file = next(iter(modules_to_csv_paths.values()))

        df_check = pd.read_csv(duration_check_file)
        if df_check.empty:
            LOGGER.warning("Data file for duration check is empty.")
            return

        time_col_check = self._get_time_column_name(df_check, str(duration_check_file))
        df_check[time_col_check] = pd.to_datetime(df_check[time_col_check])
        duration_seconds = (df_check[time_col_check].max() - df_check[time_col_check].min()).total_seconds()

        bucket_unit = self._determine_bucket_unit(duration_seconds)
        LOGGER.debug(f"Determined bucket unit: {bucket_unit} for duration {duration_seconds}s")

        # 2. Select files based on bucket unit
        if bucket_unit == "second":
            entering_key = "Entering Second"
            processed_key = "Processed Second"
        elif bucket_unit == "minute":
            entering_key = "Entering Minute"
            processed_key = "Processed Minute"
        else:  # hour
            entering_key = "Entering Hour"
            processed_key = "Processed Hour"

        files_to_plot = {
            entering_key: modules_to_csv_paths.get(entering_key),
            processed_key: modules_to_csv_paths.get(processed_key)
        }

        # 3. Plot
        for name, file in files_to_plot.items():
            if not file:
                LOGGER.warning(f"File for {name} not found in configuration.")
                continue

            df = pd.read_csv(file)
            if df.empty:
                continue  # skip empty datafiles

            time_col = self._get_time_column_name(df, str(file))
            df[time_col] = pd.to_datetime(df[time_col])
            df = df.sort_values(by=time_col)

            # Calculate time since start in the appropriate unit
            df["time_since_start"] = self._calculate_time_since_start(
                df[time_col], start_time, bucket_unit
            )

            # Filter out negative time values (before start)
            df = df[df["time_since_start"] >= 0]

            count_col = self._get_count_column_name(df, str(file))

            time_data = df["time_since_start"]
            count_data = df[count_col]

            label_name = "Entering" if "Entering" in name else "Processed"
            if "Entering" in name:
                self.__plot_core(label_name, time_data, count_data, bar_width)
            else:
                self.__plot_core(label_name, time_data, -count_data, bar_width)

        # Set x_major_locator based on bucket unit if not explicitly provided
        if x_major_locator is None:
            x_major_locator = self._get_default_x_major_locator(bucket_unit)
        
        plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(x_major_locator))
        plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(y_major_locator))

        self._set_labels(bucket_unit)

        plt.legend()
        self._activate_grid()

        self.save_to_file()

    def __plot_core(
        self,
        name: str,
        time_data: pd.DataFrame,
        count_data: pd.DataFrame,
        bar_width: float,
    ):
        plt.bar(
            time_data,
            count_data,
            width=bar_width,
            align="edge",
            label=name,
        )

    @staticmethod
    def _get_x_label(bucket_unit: str) -> str:
        """Get x-axis label based on bucket unit."""
        match bucket_unit:
            case "second":
                return "Seconds since start"
            case "minute":
                return "Minutes since start"
            case "hour":
                return "Hours since start"
            case _:
                return "Time since start"

    @staticmethod
    def _get_y_label(bucket_unit: str) -> str:
        """Get y-axis label based on bucket unit."""
        match bucket_unit:
            case "second":
                return "Log lines per second"
            case "minute":
                return "Log lines per minute"
            case "hour":
                return "Log lines per hour"
            case _:
                return "Log lines per time unit"

    def _set_labels(self, bucket_unit: str):
        plt.xlabel(self._get_x_label(bucket_unit), labelpad=10)
        plt.ylabel(self._get_y_label(bucket_unit))

    @staticmethod
    def _activate_grid():
        plt.grid(axis="y", linestyle="--")

    def _determine_bucket_unit(self, duration_seconds: float) -> str:
        """Determine the appropriate bucket unit based on data duration using match statement.
        
        Args:
            duration_seconds: Total duration of the data in seconds
            
        Returns:
            Bucket unit: "second", "minute", or "hour"
        """
        duration_minutes = duration_seconds / 60
        duration_hours = duration_minutes / 60

        match True:
            case _ if duration_hours >= self.min_hours_for_hour_buckets:
                return "hour"
            case _ if duration_minutes >= self.min_minutes_for_minute_buckets:
                return "minute"
            case _:
                return "second"

    @staticmethod
    def _calculate_time_since_start(
            timestamps: pd.Series, start_time: datetime.datetime, bucket_unit: str
    ) -> pd.Series:
        """Calculate time since start in the appropriate unit.
        
        Args:
            timestamps: Series of timestamps
            start_time: Start time of the test
            bucket_unit: Unit for the bucket ("second", "minute", or "hour")
            
        Returns:
            Series with time values in the appropriate unit
        """
        time_diff_seconds = (
                timestamps - start_time.replace(tzinfo=None)
        ).dt.total_seconds()

        match bucket_unit:
            case "second":
                return time_diff_seconds
            case "minute":
                return time_diff_seconds / 60
            case "hour":
                return time_diff_seconds / 3600
            case _:
                return time_diff_seconds

    @staticmethod
    def _get_floor_frequency(bucket_unit: str) -> str:
        """Get the pandas frequency string for floor operation.
        
        Args:
            bucket_unit: Unit for the bucket ("second", "minute", or "hour")
            
        Returns:
            Pandas frequency string
        """
        match bucket_unit:
            case "second":
                return "s"
            case "minute":
                return "min"
            case "hour":
                return "h"
            case _:
                return "min"

    @staticmethod
    def _get_default_x_major_locator(bucket_unit: str) -> int:
        """Get default x-axis major locator based on bucket unit.
        
        Args:
            bucket_unit: Unit for the bucket ("second", "minute", or "hour")
            
        Returns:
            Default interval for x-axis ticks
        """
        match bucket_unit:
            case "second":
                return 10  # Every 10 seconds
            case "minute":
                return 1  # Every minute
            case "hour":
                return 1  # Every hour
            case _:
                return 1

    @staticmethod
    def _get_time_column_name(df: pd.DataFrame, filename: str) -> str:
        if "time_bucket" in df.columns:
            return "time_bucket"
        elif "timestamp_in" in df.columns:
            return "timestamp_in"
        elif "timestamp" in df.columns:
            return "timestamp"
        else:
            raise ValueError(f"No recognized time column in {filename}")

    @staticmethod
    def _get_count_column_name(df: pd.DataFrame, filename: str) -> str:
        if "count" in df.columns:
            return "count"
        elif "count()" in df.columns:
            return "count()"
        elif "total_count" in df.columns:
            return "total_count"
        else:
            raise ValueError(f"No recognized count column in {filename}, found columns: {df.columns}")


class LatenciesBoxplotGenerator(PlotGenerator):

    def __init__(
        self,
        test_identifier: str,
    ):
        plot_name = "latencies_boxplot"
        super().__init__(plot_name=plot_name, test_identifier=test_identifier)

        self.default_fig_size = (8.35, 4.8)

    def plot(
        self,
        fig_size: tuple[float, float] = None,
        y_input_unit: str = "microseconds",
    ):
        """Creates a boxplot figure showing latency distributions for different modules.

        Args:
            y_input_unit (str): Unit of the data given as input, "microseconds" by default
        """
        self._set_up_initial_figure(fig_size)

        modules_to_csv_paths = ReadWriteUtils.get_modules_to_csv_filepaths(
            self.plot_name, self.test_identifier
        )

        data = []
        labels = []

        for name, file in modules_to_csv_paths.items():
            df = pd.read_csv(file, parse_dates=["time"]).sort_values(by="time")

            if df.empty:
                continue  # skip empty datafiles

            # convert to seconds based on input unit
            if y_input_unit == "microseconds":
                data.append(df["value"] / (10**6))
            elif y_input_unit == "milliseconds":
                data.append(df["value"] / (10**3))
            elif y_input_unit == "seconds":
                data.append(df["value"])
            else:
                data.append(df["value"])

            labels.append(name)

        self.__plot_core(data, labels)
        self._activate_grid()
        self._set_labels()

        self.save_to_file()

    def __plot_core(self, data: list, labels: list):
        boxplot_style = self._get_boxplot_style()

        plt.yscale("log")
        plt.tight_layout()
        plt.boxplot(
            data,
            labels=labels,
            vert=True,
            patch_artist=False,  # no filled boxes
            boxprops=boxplot_style.get("boxprops"),
            whiskerprops=boxplot_style.get("whiskerprops"),
            capprops=boxplot_style.get("capprops"),
            medianprops=boxplot_style.get("medianprops"),
            flierprops=boxplot_style.get("flierprops"),
        )

    @staticmethod
    def _get_y_label():
        return "Latency in module [s]"  # TODO: Make more flexible

    def _set_labels(self):
        plt.ylabel(self._get_y_label())

    @staticmethod
    def _get_boxplot_style() -> dict:
        return {
            "boxprops": dict(
                color="black",
                linewidth=1,
            ),
            "whiskerprops": dict(
                color="black",
                linewidth=1,
            ),
            "capprops": dict(
                color="black",
                linewidth=1,
            ),
            "medianprops": dict(
                color="black",
                linewidth=1.5,
            ),
            "flierprops": dict(
                marker="x",
                markerfacecolor="lightgray",
                markeredgecolor="lightgray",
                markersize=4,
                linestyle="none",
            ),
        }

    @staticmethod
    def _activate_grid():
        plt.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.7)

    @staticmethod
    def _set_x_ticks():
        plt.xticks(rotation=30, ha="right")
