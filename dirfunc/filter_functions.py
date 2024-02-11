import re
from typing import Callable

# types
FilterFunction = Callable[[list[tuple]], list[tuple]]

# For filtering
REGEX_DOTS = r'[.]{1,2}$'
REGEX_IS_FOLDER = r'<DIR>'


def filter_files_only(files: list[tuple]) -> list[tuple]:
    return [f for f in files if len(
        re.findall(REGEX_IS_FOLDER, f[2])) == 0]


def filter_folder_only(files: list[tuple]) -> list[tuple]:
    return [f for f in files if len(
        re.findall(REGEX_IS_FOLDER, f[2])) > 0]


def filter_dot_folders(files: list[tuple]) -> list[tuple]:
    return [f for f in files if len(
        re.findall(REGEX_DOTS, f[-2])) == 0]


def exec_filter_chain(files: list[tuple],
                      exclude_parents: bool = False,
                      files_only: bool = False,
                      folders_only: bool = False) -> list[FilterFunction]:
    '''
    Filter the input list of file attributes, based on the filetype (file or folder)
    '''
    if files_only:
        files = filter_files_only(files)
    if folders_only and not files_only:
        files = filter_folder_only(files)
    if exclude_parents and not files_only:
        files = filter_dot_folders(files)

    return files
