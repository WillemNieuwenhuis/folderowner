import re
from typing import Callable

# types
FilterFunction = Callable[[list[tuple]], list[tuple]]

# For filtering
REGEX_dots = r'[.]{1,2}$'
REGEX_is_folder = r'<DIR>'


def filter_files_only(files: list[tuple]) -> list[tuple]:
    return [f for f in files if len(
        re.findall(REGEX_is_folder, f[2])) == 0]


def filter_folder_only(files: list[tuple]) -> list[tuple]:
    return [f for f in files if len(
        re.findall(REGEX_is_folder, f[2])) > 0]


def filter_dot_folders(files: list[tuple]) -> list[tuple]:
    return [f for f in files if len(
        re.findall(REGEX_dots, f[-2])) == 0]
