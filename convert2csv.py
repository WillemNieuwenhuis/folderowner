import argparse
import os
from pathlib import Path
import pandas as pd
import re
from typing import Optional, Callable, Iterable

from extract_functions import get_extract_function
from filter_functions import (FilterFunction,
                              filter_files_only,
                              filter_folder_only,
                              filter_dot_folders)

# For parsing
REGEX_VOLUME_SERIAL_CMD = 'Volume Serial'
REGEX_VOLUME_SERIAL_TCC = ' Serial number'
REGEX_directory_line = 'Directory of'
REGEX_folder_pattern = r'[ \*]'
REGEX_bytes_in_folder = ' bytes in '


class FileIterator(Iterable):
    ''' Turn file read generator into an iterator
        This allows to handle the special end of file case (empty line)
        A regular empty line contains a single '\n', which is stripped off
    '''

    def __init__(self, filename: str) -> None:
        self.fil = open(filename)

    def __next__(self) -> str:
        line = self.fil.readline()
        if line:
            return line.strip()

        raise StopIteration

    def __iter__(self):
        return self

    def __del__(self) -> None:
        self.fil.close()


class FolderIterator:
    ''' Extract all listed files from a dump of the command:
         `dir <root folder> /qs`
        This to get a list of files, each with the owner
        Two shells can be used to generate the lists: CMD and TCC.
        The list of CMD is formatted different from TCC. The iterator tries
    '''

    def __init__(self,
                 source: Iterable,
                 skip_dot_folders: bool = False,
                 files_only: bool = False,
                 folders_only: bool = False,
                 encoding: Optional[str] = 'utf-8',
                 ) -> None:
        self.source = source
        # files_only takes precedence over folders_only or skip_dot_folders,
        # they cannot all be true
        self.extractfunction = get_extract_function(self._detect_shell())
        self.filters: list[FilterFunction] = []
        if files_only:
            self.filters.append[filter_files_only]
        if folders_only and not files_only:
            self.filters.append[filter_folder_only]
        if skip_dot_folders and not files_only:
            self.filters.append[filter_dot_folders]

    def __iter__(self):
        return self

    def __next__(self):
        folder = self.find_folder_name()
        files = self.find_file_list(folder)
        # files contains a list of tuples:
        #  (datestr, timestr, sizestr or DIR, owner, filename, containing folder)
        # Apply filters if any
        for func in self.filters:
            files = func(files)

        return (folder, files)

    def _detect_shell(self) -> str:
        ''' Try to detect the shell the dir list is from
            to detect which has created the list by testing the first lines.
            For TCC the list should start with something similar to:
              `Volume in drive C is unlabeled    Serial number is be92:c251`
            For CMD the list should start with something similar to:
              `Volume in drive C has no label.\n`
              `Volume Serial Number is BE92-C251`
        '''
        # skip potential empty lines
        while True:
            lin = next(self.source)
            if len(re.findall(REGEX_VOLUME_SERIAL_CMD, lin)) > 0:
                return 'CMD'
            if len(re.findall(REGEX_VOLUME_SERIAL_TCC, lin)) > 0:
                return 'TCC'

            if not lin:
                break

        return 'TCC'

    def find_folder_name(self) -> str:
        ''' Read lines from the file until a line with folder name is found
            extract and return the folder name
        '''
        while True:
            lin = next(self.source)
            if len(re.findall(REGEX_directory_line, lin)) > 0:
                break

        # lin looks like:
        # ` Directory of  \\dikke.itc.utwente.nl\RS_Data\Willem\darvish\Planet\*`
        parts = re.split(REGEX_folder_pattern, lin.strip())
        if len(parts) < 3:
            raise StopIteration

        return ' '.join(parts[3:-1])

    def find_file_list(self, folder: str) -> list[str]:
        ''' Skip empty lines and read a list of file names
            add field with full path
            return as list of tuples
        '''
        while True:
            lin = next(self.source)
            if len(lin) > 0:
                break

        # at first line of list
        # collect lines until first summary line
        # (fe: `297,678,077 bytes in 41 files and 2 dirs`)
        folder_list = [(*self.extractfunction(lin), folder)]     # add the first
        while True:
            lin = next(self.source)
            if len(re.findall(REGEX_bytes_in_folder, lin)) > 0:
                return folder_list

            folder_list.append((*self.extractfunction(lin), folder))

        raise StopIteration


def split_dir_from_size(df: pd.DataFrame) -> pd.DataFrame:
    '''
        The size columns can contain both numbers to indicate the size of a
        file, or it contains the text`<DIR>` to indicate the item is a folder.
        Two new columns are generated:
          - one to indicate if an item is a folder
    '''
    ser = df['size']
    df['isfolder'] = ser.str.contains('<DIR>')
    df['size (bytes)'] = pd.to_numeric(ser, 'coerce').fillna(0)
    df = df.drop(columns=['size'])
    cols = df.columns
    ncols = [*cols[:2], *cols[-2:], *cols[2:-2]]
    return df.reindex(columns=ncols)


def read_dirlist(fn: str,
                 ignore_dot_folders: bool,
                 files_only: bool,
                 folders_only: bool,
                 encoding: Optional[str],
                 ) -> pd.DataFrame:
    """ The function parses directory output from a console (Windows)
        The listing contains information about the owner of each file/folder
        A typical entry looks like:
            `2023-10-13  12:53             643  AD\nieuwenhuis  readme.txt`
        A block contains a list of these entries, but does not contain the
        folder name. This folder name is listed above the block with filenames,
        and looks similar to:
            ` Directory of  \\dikke.itc.utwente.nl\RS_Data\Willem\darvish\Planet\*`
        (notice the space in front)
        After the block one or more lines follow containing summary data, such as:
            `         297,678,077 bytes in 41 files and 2 dirs`, and
            `    Total for:  \\dikke.itc.utwente.nl\RS_Data\Willem\darvish\Planet\`
            `         595,396,857 bytes in 45 files and 5 dirs    595,488,768 bytes allocated`
    """   # noqa: E501, W605
    # loop until end
    #   find folder name
    #   find file list
    #   using pandas format file list and folder name as table
    #   return pandas dataframe
    source = FileIterator(fn)
    filfol = FolderIterator(source,
                            skip_dot_folders=ignore_dot_folders,
                            files_only=files_only,
                            folders_only=folders_only,
                            encoding=encoding,
                            )
    data_columns = ('date', 'time', 'size', 'owner', 'name', 'folder')
    df = pd.DataFrame(columns=data_columns)  # initialise empty
    for _, files in filfol:
        dflocal = pd.DataFrame(files, columns=data_columns)
        df = pd.concat([df, dflocal])

    df = split_dir_from_size(df)
    return df


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='dirtocsv',
        description='''The function parses directory output from a terminal (Windows)
        using the /q option.
        The listing contains information about the owner of each file/folder'''
    )
    parser.add_argument(
        'dirdump',
        help='Specify the file containing the output of the dir /qs command')
    parser.add_argument(
        'output_table',
        help='Specify the output CSV table name')
    parser.add_argument(
        '-o', '--overwrite',
        action='store_true',
        help='Overwrite existing output table'
    )
    parser.add_argument(
        '-i', '--ignore_dot_folders',
        action='store_true',
        help='Exclude . and .. folders from the output table'
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-d', '--dirs_only',
        action='store_true',
        help='Only extract folders into the output table'
    )
    group.add_argument(
        '-f', '--files_only',
        action='store_true',
        help='Only extract files into the output table'
    )
    parser.add_argument(
        '-e', '--encoding',
        default='utf-8',
        help='Specify the text encoding of the input file'
    )
    return parser


if __name__ == '__main__':
    args = create_parser().parse_args()

    dirdump_file = Path(args.dirdump)
    if not dirdump_file.exists:
        print(f'File {args.dirdump} does not exist')
        exit()

    outtable = Path(args.output_table)
    if outtable.exists() and (not args.overwrite):
        print(f'File {args.output_table} already exists')
        exit()

    if outtable.exists() and args.overwrite:
        os.remove(outtable)

    df = read_dirlist(args.dirdump,
                      ignore_dot_folders=args.ignore_dot_folders,
                      files_only=args.files_only,
                      folders_only=args.dirs_only,
                      encoding=args.encoding,
                      )
    df.to_csv(args.output_table, index=False, encoding='utf-8')
