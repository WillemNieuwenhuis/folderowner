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


def exec_filter_chain(files: list[tuple],
                      exclude_parents: bool,
                      files_only: bool,
                      folders_only: bool) -> list[FilterFunction]:
    if files_only:
        files = filter_files_only(files)
    if folders_only and not files_only:
        files = filter_folder_only(files)
    if exclude_parents and not files_only:
        files = filter_dot_folders(files)

    return files
