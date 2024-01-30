import argparse
import os
from pathlib import Path
import re
import typing

import pandas as pd

# For parsing
REGEX_directory_line = r'Directory of'
REGEX_folder_pattern = r'[ \*]'
REGEX_bytes_in_folder = r' bytes in '

# For filtering
REGEX_dots = r'[.]{1,2}$'
REGEX_is_folder = r'<DIR>'

# possible system domains
NTAUTH_DOMAIN = 'NT AUTHORITY'
BUILTIN_DOMAIN = 'BUILTIN'
NTSERV_DOMAIN = 'NT SERVICE'
LOCAL_DOMAIN = os.environ.get('userdomain')
SPECIAL_DOMAIN = '...'
all_domains = [NTAUTH_DOMAIN, BUILTIN_DOMAIN,
               NTSERV_DOMAIN, LOCAL_DOMAIN, SPECIAL_DOMAIN]


class MissingOwner(Exception):
    pass


def has_valid_domain(name: str):
    checked = [name.find(dom) >= 0 for dom in all_domains]
    return any(checked)


def extract_attribs(lin: str) -> tuple[str]:
    '''extract attributes at fixed starting positions in the line
    '''
    datestr = lin[0:12].strip()
    timestr = lin[12:17].strip()
    sizestr = lin[17:35].strip().replace(',', '')
    own_name = lin[35:]
    parts = own_name.split()
    owner = parts[0].strip()
    name = ' '.join(parts[1:])
    if not has_valid_domain(owner):
        raise MissingOwner('Could not find valid owner, did you use "/Q"')
    return (datestr, timestr, sizestr, owner, name)


class FolderIterator:
    ''' Extract all listed files from a dump of the command:
         `dir <root folder> /qs`
        This to get a list of files, each with the owner
    '''

    def __init__(self, fn: str,
                 skip_dot_folders: bool = False,
                 files_only: bool = False,
                 folders_only: bool = False,
                 encoding: typing.Optional[str] = 'utf-8',
                 ) -> None:
        self.fil = open(fn, encoding=encoding)
        self.files_only = files_only
        # files_only takes precedence over folders_only or skip_dot_folders,
        # they cannot all be true
        self.skip_dot_folders = skip_dot_folders and not files_only
        self.folders_only = folders_only and not files_only

    def __del__(self):
        self.fil.close()

    def __iter__(self):
        return self

    def __next__(self):
        folder = self.find_folder_name()
        files = self.find_file_list(folder)
        if self.files_only:
            files = [f for f in files if len(
                re.findall(REGEX_is_folder, f[2])) == 0]
        if self.folders_only:
            files = [f for f in files if len(
                re.findall(REGEX_is_folder, f[2])) > 0]
        if self.skip_dot_folders:
            files = [f for f in files if len(
                re.findall(REGEX_dots, f[-2])) == 0]
        return (folder, files)

    def find_folder_name(self) -> str:
        ''' Read lines from the file until a line with folder name is found
            extract and return the folder name
        '''
        while lin := self.fil.readline():
            if len(re.findall(REGEX_directory_line, lin.strip())) > 0:
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
        while lin := self.fil.readline():
            if len(lin.strip()) > 0:
                break

        # at first line of list
        # collect lines until first summary line
        # (fe: `297,678,077 bytes in 41 files and 2 dirs`)
        folder_list = [(*extract_attribs(lin), folder)]     # add the first
        while lin := self.fil.readline():
            if len(re.findall(REGEX_bytes_in_folder, lin)) > 0:
                return folder_list

            folder_list.append((*extract_attribs(lin), folder))

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
                 encoding: typing.Optional[str],
                 ) -> pd.DataFrame:
    ''' The function parses directory output from a console (Windows)
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
    '''   # noqa: E501, W605
    # loop until end
    #   find folder name
    #   find file list
    #   using pandas format file list and folder name as table
    #   return pandas dataframe
    filfol = FolderIterator(fn,
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
