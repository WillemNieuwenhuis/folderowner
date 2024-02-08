import re
from typing import Iterable, Optional

from extract_functions import get_extract_function
from filter_functions import exec_filter_chain

# For parsing
REGEX_VOLUME_SERIAL_CMD = 'Volume Serial'
REGEX_VOLUME_SERIAL_TCC = ' Serial number'
REGEX_directory_line = 'Directory of'
REGEX_folder_pattern = r'[ \*]'
REGEX_bytes_in_folder = ' bytes in '


class FolderIterator(Iterable):
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
        self.files_only = files_only
        self.folders_only = folders_only and not files_only
        self.exclude_parents = skip_dot_folders and not files_only

    def __iter__(self):
        return self

    def __next__(self):
        folder = self.find_folder_name()
        files = self.find_file_list(folder)
        # files contains a list of tuples:
        #  (datestr, timestr, sizestr or DIR, owner, filename, containing folder)
        # Apply filters if any
        files = exec_filter_chain(files, self.exclude_parents,
                                  self.files_only, self.folders_only)

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
