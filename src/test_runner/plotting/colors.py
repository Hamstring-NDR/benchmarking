from matplotlib import pyplot as plt


class Colors:
    _instance = None
    _colors = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Colors, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def get_color(self, key: str) -> str:
        color_palette = plt.rcParams["axes.prop_cycle"].by_key()["color"]

        if key not in self._colors:
            next_unused_index = len(self._colors) % len(color_palette)
            self._colors[key] = color_palette[next_unused_index]

        return self._colors[key]
