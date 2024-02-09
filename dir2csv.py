import os
from pathlib import Path
import sys
from typing import Optional

import pandas as pd

from cli import define_cli
from file_iterator import FileIterator
from main_iterator import FolderIterator


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
    r""" The function parses directory output from a console (Windows)
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
    df = pd.DataFrame(columns=data_columns)  # initialise empty dataframe
    for _, files in filfol:
        dflocal = pd.DataFrame(files, columns=data_columns)
        df = pd.concat([df, dflocal])

    df = split_dir_from_size(df)
    return df


if __name__ == '__main__':
    args = define_cli().parse_args()

    dirdump_file = Path(args.dirdump)
    if not dirdump_file.exists:
        print(f'File {args.dirdump} does not exist')
        sys.exit(1)

    outtable = Path(args.output_table)
    if outtable.exists() and (not args.overwrite):
        print(f'File {args.output_table} already exists')
        sys.exit(2)

    if outtable.exists() and args.overwrite:
        os.remove(outtable)

    df = read_dirlist(args.dirdump,
                      ignore_dot_folders=args.ignore_dot_folders,
                      files_only=args.files_only,
                      folders_only=args.dirs_only,
                      encoding=args.encoding,
                      )

    df.to_csv(args.output_table, index=False, encoding='utf-8')
