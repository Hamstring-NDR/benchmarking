from matplotlib import pyplot as plt


class Colors:
    """Singleton class for managing consistent plot colors across the application."""
    _instance = None
    _colors = {}

    def __new__(cls, *args, **kwargs):
        """Ensures that only one instance of the class is created.

        Args:
           *args: Variable length argument list.
           **kwargs: Arbitrary keyword arguments.

        Returns:
            Colors: The singleton instance of the Colors class.
        """
        if not cls._instance:
            cls._instance = super(Colors, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def get_color(self, key: str) -> str:
        """Retrieves or assigns a color for a given key.

        If the key already has an assigned color, it returns that color.
        Otherwise, it assigns the next available color from the cycle.

        Args:
            key (str): The identifier for which to get the color.

        Returns:
            str: The color code associated with the key.
        """
        color_palette = plt.rcParams["axes.prop_cycle"].by_key()["color"]

        if key not in self._colors:
            next_unused_index = len(self._colors) % len(color_palette)
            self._colors[key] = color_palette[next_unused_index]

        return self._colors[key]
