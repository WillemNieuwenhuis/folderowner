import pandas as pd
import argparse
import re

REGEX_directory_line = r'Directory of'
REGEX_folder_pattern = r'[ \*]'
REGEX_bytes_in_folder = r' bytes in '

def extract_attribs(lin:str) -> list[str]:
    '''extract attributes at fixed starting positions in the line
    '''
    datestr = lin[0:12].strip()
    timestr = lin[12:17].strip()
    sizestr = lin[17:35].strip().replace(',', '')
    owner = lin[35:50].strip()
    name = lin[50:].strip()
    return (datestr, timestr, sizestr, owner, name)

def add_abs_path(lin:str, folder:str) -> tuple[str]:
    rel_path = extract_attribs(lin)
    return (*rel_path, folder + rel_path[-1])

class FolderIterator:
    ''' Extract all listed files from a dump of the command:
         `dir <root folder> /qs`
        This to get a list of files, each with the owner
    '''
    def __init__(self, fn : str) -> None:
        self.fil = open(fn, encoding='utf-8')
    
    def __iter__(self):
        return self
    
    def __next__(self):
        folder = self.find_folder_name()
        files = self.find_file_list(folder)
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
        
        return parts[3]

    def find_file_list(self, folder:str) -> list[str]:
        ''' Skip empty lines and read a list of file names
            return the list
        '''
        while lin := self.fil.readline():
            if len(lin.strip()) > 0:
                break

        # at first line of list
        # collect lines until first summary line (fe: `297,678,077 bytes in 41 files and 2 dirs`)
        folder_list = [add_abs_path(lin, folder)]     # add the first
        while lin := self.fil.readline():
            if len(re.findall(REGEX_bytes_in_folder, lin)) > 0:
                return folder_list
            
            folder_list.append(add_abs_path(lin, folder))

        raise StopIteration

def read_dirlist(fn:str) -> pd.DataFrame:
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
    '''
    # loop until end
    #   find folder name
    #   find file list
    #   format file list and folder name as table
    #   return pandas dataframe
    filfol = FolderIterator(fn)
    df = pd.DataFrame(columns=('date','time','size', 'owner', 'name', 'fullname'))
    for _, files in filfol:
        dflocal = pd.DataFrame(files, columns=('date','time','size', 'owner', 'name', 'fullname'))
        df = pd.concat([df,dflocal])

    return df

if __name__ == '__main__':
    fn = r'E:\Projects\extract_owner\owner_rsdata.lst'
    fnout = r'E:\Projects\extract_owner\owner_rsdata.csv'
    df = read_dirlist(fn)
    df.to_csv(fnout, index=False)
