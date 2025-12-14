from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # project root directory

CONFIG_FILEPATH = BASE_DIR / "config.yaml"
DIRECTORY_STRUCTURE_FILEPATH = BASE_DIR / "resources" / "data_directory_structure.yaml"
