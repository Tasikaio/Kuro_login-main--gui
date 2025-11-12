import os
from pathlib import Path

PROJECT_PATH = Path(__file__).resolve().parent.parent
STATIC_PATH = PROJECT_PATH.joinpath("static")
PICTURE_PATH = STATIC_PATH.joinpath("pictures")
TMP_PATH = STATIC_PATH.joinpath("tmp")
TMP_BACKGROUND_PATH = TMP_PATH.joinpath("background")


def mk_dir(file_path: str):
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
