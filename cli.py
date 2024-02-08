import argparse


def define_cli() -> argparse.ArgumentParser:
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
