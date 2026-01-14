import datetime
from abc import abstractmethod
from pathlib import Path
from typing import Optional

import pymupdf

from src.test_runner.plotting.metadata_information import (
    SingleMetadataInformation,
)


class BaseBox(pymupdf.Rect):
    """Base class for layout boxes to be used in PDFs."""

    def __init__(
        self,
        page,
        page_margin: dict[str, float],
        width: float,
        height: float,
        top_padding: float = 0,
        left_padding: float = 0,
    ):
        """Initializes values for the box.

        Args:
            page (pymupdf.Page): The page to draw on.
            page_margin (dict[str, float]): The margins of the page.
            width (float): The width of the box.
            height (float): The height of the box.
            top_padding (float): The top padding of the box. Default: 0.
            left_padding (float): The left padding of the box. Default: 0.
        """
        self.page = page

        x0 = page_margin.get("left") + left_padding
        y0 = page_margin.get("top") + top_padding
        x1 = x0 + width
        y1 = y0 + height

        super().__init__(x0, y0, x1, y1)

    @abstractmethod
    def fill(self, *args) -> pymupdf.Rect:
        """Fills the box with content.

        Args:
            *args: Variable length argument list.

        Returns:
            pymupdf.Rect: The filled box.
        """
        raise NotImplementedError

    def _get_padded(self, horizontal_padding: int = 8, vertical_padding: int = 3) -> pymupdf.Rect:
        """Returns the same rectangle but with inner padding.

        Args:
            horizontal_padding (int): Padding in horizontal direction; default: 8.
            vertical_padding (int): Padding in vertical direction; default: 3.

        Returns:
            pymupdf.Rect: The padded rectangle.
        """
        return pymupdf.Rect(
            self.x0 + horizontal_padding,
            self.y0 + vertical_padding,
            self.x1 - horizontal_padding,
            self.y1 - vertical_padding,
        )


class MainTitleBox(BaseBox):
    """Contains the main title of a page, consisting of the test name and the date."""

    def fill(
        self,
        test_name: str,
        test_date: datetime.date,
        generation_date: datetime.date = datetime.date.today(),
    ):
        """Fills the box with the main title.

        Args:
            test_name (str): Name of the test.
            test_date (datetime.date): Date of the test.
            generation_date (datetime.date): Date of report generation. Default: today.

        Returns:
            self
        """
        self.page.draw_rect(self, fill=(0,), fill_opacity=0.1, width=0.5)  # border
        self.page.insert_htmlbox(  # title
            self._get_padded(),
            f"{test_name.title()} Benchmark Test",
            css="* {font-family: sans-serif; font-size: 13px}",
        )
        self.page.insert_htmlbox(  # subtitle
            self._get_padded(),
            "Benchmarking Report",
            css="* {"
            "font-family: sans-serif; font-size: 8px; font-weight: bold;"
            "padding: 8px 0}",
        )
        self.page.insert_htmlbox(  # benchmark test date
            self._get_padded(),
            str(test_date),
            css="* {font-family: sans-serif; font-size: 13px; text-align: right}",
        )
        if generation_date != test_date:
            self.page.insert_htmlbox(  # report generation date
                self._get_padded(),
                f"Report generated: {str(generation_date)}",
                css="* {font-family: sans-serif; font-size: 8px; padding: 8px 0;"
                "text-align: right; padding-right: .5px}",
            )

        return self


class SectionTitleBox(BaseBox):
    """Contains the section title."""

    def fill(self, text: str):
        """Fills the box with the section title.

        Args:
            text (str): Title text.

        Returns:
            self
        """
        self.page.draw_rect(self, fill=(0,), fill_opacity=0.3, width=0.5)  # border
        self.page.insert_htmlbox(  # title
            self._get_padded(vertical_padding=4),
            text,
            css="* {font-family: sans-serif; font-size: 8px}",
        )

        return self


class SectionDoubleTitleBox(BaseBox):
    """Contains the section titles for double-column sections."""

    def fill(self, text_1: str, text_2: str):
        """Fills the box with two section titles.

        Args:
            text_1 (str): First title text.
            text_2 (str): Second title text.

        Returns:
            self
        """
        self.page.draw_rect(self, fill=(0,), fill_opacity=0.3, width=0.5)  # border

        width = self.x1 - self.x0
        horizontal_padding = 8
        vertical_padding = 4
        self.page.insert_htmlbox(  # first title
            pymupdf.Rect(
                x0=self.x0 + horizontal_padding,
                y0=self.y0 + vertical_padding,
                x1=(self.x1 / 2) - horizontal_padding,
                y1=self.y1 - vertical_padding,
            ),
            text_1,
            css="* {font-family: sans-serif; font-size: 8px}",
        )
        self.page.insert_htmlbox(  # second title
            pymupdf.Rect(
                x0=self.x0 + (width / 2) + horizontal_padding,
                y0=self.y0 + vertical_padding,
                x1=self.x1 - horizontal_padding,
                y1=self.y1 - vertical_padding,
            ),
            text_2,
            css="* {font-family: sans-serif; font-size: 8px}",
        )

        return self


class SectionSubtitleBox(BaseBox):
    """Contains the section subtitle."""

    def fill(self, text: str):
        """Fills the box with the section subtitle.

        Args:
            text (str): Subtitle text.

        Returns:
            self
        """
        self.page.draw_rect(self, fill=(0,), fill_opacity=0.1, width=0.5)  # border
        self.page.insert_htmlbox(  # subtitle
            self._get_padded(vertical_padding=4),
            text,
            css="* {font-family: sans-serif; font-size: 7px; font-style: italic}",
        )

        return self


class SectionDoubleSubtitleBox(BaseBox):
    """Contains the section subtitles for double-column sections."""

    def fill(self, text_1: str, text_2: str):
        """Fills the box with two section subtitles.

        Args:
            text_1 (str): First subtitle text.
            text_2 (str): Second subtitle text.

        Returns:
            self
        """
        width = self.x1 - self.x0
        self.page.draw_rect(
            pymupdf.Rect(  # first border
                x0=self.x0,
                y0=self.y0,
                x1=self.x1 - (width / 2),
                y1=self.y1,
            ),
            fill=(0,),
            fill_opacity=0.1,
            width=0.5,
        )
        self.page.draw_rect(
            pymupdf.Rect(  # second border
                x0=self.x0 + (width / 2),
                y0=self.y0,
                x1=self.x1,
                y1=self.y1,
            ),
            fill=(0,),
            fill_opacity=0.1,
            width=0.5,
        )

        horizontal_padding = 8
        vertical_padding = 4
        self.page.insert_htmlbox(  # first subtitle
            pymupdf.Rect(
                x0=self.x0 + horizontal_padding,
                y0=self.y0 + vertical_padding,
                x1=self.x1 - (width / 2) - horizontal_padding,
                y1=self.y1 - vertical_padding,
            ),
            text_1,
            css="* {font-family: sans-serif; font-size: 7px; font-style: italic}",
        )
        self.page.insert_htmlbox(  # second subtitle
            pymupdf.Rect(
                x0=self.x0 + (width / 2) + horizontal_padding,
                y0=self.y0 + vertical_padding,
                x1=self.x1 - horizontal_padding,
                y1=self.y1 - vertical_padding,
            ),
            text_2,
            css="* {font-family: sans-serif; font-size: 7px; font-style: italic}",
        )

        return self


class SectionContentImageBox(BaseBox):
    """Contains the section content in the form of an image, e.g. a plotted graph."""

    def fill(self, file_path: Optional[Path] = None):
        """Fills the box with an image.

        Args:
            file_path (Optional[Path]): Path to the image file. Default: None.

        Returns:
            self
        """
        self.page.draw_rect(self, width=0.5)  # border
        if file_path is not None:  # content
            self.page.insert_image(
                self._get_padded(vertical_padding=4),
                filename=file_path,
            )

        return self


class SectionContentMetadataBox(BaseBox):
    """Contains the section content for the metadata section, consisting of several boxes."""

    def fill(
        self,
        metadata_information: dict[tuple[int, int], SingleMetadataInformation],
        boxes_per_row: int = 5,
    ):
        """Fills the box with content.

        Args:
            metadata_information (dict[tuple[int, int], SingleMetadataInformation]): Dictionary of a
                tuple, containing the row and column in the grid to position the box in, and a
                SingleMetadataInformation.
                Row must be 1 or 2, column must be at least 1 and at most boxes_per_row.
                Per position, at most one information is allowed.
            boxes_per_row (int): Maximum number of boxes per row. Default: 5.

        Raises:
            ValueError: If position is invalid.

        Returns:
            self
        """
        for position in metadata_information.keys():
            if position[0] not in range(1, 3):  # row
                raise ValueError("Invalid row number")

            if position[1] not in range(1, boxes_per_row + 1):  # column
                raise ValueError("Invalid column number")

        self.page.draw_rect(self, width=0.5)  # outer border

        number_of_rows: int = 2
        row_height = (self.y1 - self.y0) / number_of_rows
        box_width = (self.x1 - self.x0) / boxes_per_row

        for row in range(0, number_of_rows):
            for column in range(0, boxes_per_row):
                if (row + 1, column + 1) in metadata_information.keys():
                    box = pymupdf.Rect(
                        x0=self.x0 + column * box_width,
                        y0=self.y0 + row * row_height,
                        x1=self.x0 + (column + 1) * box_width,
                        y1=self.y0 + (row + 1) * row_height,
                    )

                    self.page.draw_rect(box, width=0.5)

                    title_text = metadata_information[(row + 1, column + 1)].title
                    padded_box = self._get_padded_rectangle(box, vertical_padding=5)
                    available_width = padded_box.width - 4

                    final_title, _ = self._get_optimized_text_and_fontsize(
                        title_text, available_width, max_font_size=6, min_font_size=6,
                    )

                    self.page.insert_htmlbox(  # title
                        padded_box,
                        final_title,
                        css="* {font-family: sans-serif; font-size: 6px; text-align: center; white-space: nowrap}",
                    )

                    value_text = metadata_information[(row + 1, column + 1)].value

                    final_text, font_size = self._get_optimized_text_and_fontsize(
                        value_text, available_width, min_font_size=10
                    )

                    self.page.insert_htmlbox(  # value
                        padded_box,
                        final_text,
                        css=f"* {{font-family: sans-serif; font-size: {font_size}px; "
                            f"text-align: center; padding: 5px 0; white-space: nowrap}}",
                    )

        return self

    def _get_optimized_text_and_fontsize(
            self, text: str, max_width: float, max_font_size: int = 13, min_font_size: int = 6
    ) -> tuple[str, int]:
        """Calculates the best font size for the text to fit in the width.
        Truncates text if it doesn't fit even with minimum font size.

        Args:
            text (str): The text to check.
            max_width (float): The maximum available width.
            max_font_size (int): Max font size to start with. Default: 13.
            min_font_size (int): Min font size to go down to. Default: 6.

        Returns:
            tuple[str, int]: The (possibly truncated) text and the determined font size.
        """
        font = pymupdf.Font("helv")

        for size in range(max_font_size, min_font_size - 1, -1):
            if font.text_length(text, fontsize=size) <= max_width:
                return text, size

        # If way too big, truncate.
        ellipsis_width = font.text_length("...", fontsize=min_font_size)

        for i in range(len(text), 0, -1):
            truncated = text[:i]
            if (
                    font.text_length(truncated, fontsize=min_font_size) + ellipsis_width
                    <= max_width
            ):
                return truncated + "...", min_font_size

        return "...", min_font_size  # Should almost never happen unless box is tiny

    @staticmethod
    def _get_padded_rectangle(
        rect: pymupdf.Rect, horizontal_padding: int = 8, vertical_padding: int = 3
    ) -> pymupdf.Rect:
        """Returns the given rectangle with inner padding.

        Args:
            rect (pymupdf.Rect): The rectangle to pad.
            horizontal_padding (int): Padding in horizontal direction; default: 8.
            vertical_padding (int): Padding in vertical direction; default: 3.

        Returns:
            pymupdf.Rect: The padded rectangle.
        """
        return pymupdf.Rect(
            rect.x0 + horizontal_padding,
            rect.y0 + vertical_padding,
            rect.x1 - horizontal_padding,
            rect.y1 - vertical_padding,
        )
