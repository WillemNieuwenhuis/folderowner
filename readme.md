# Extract owner info from plain folder listing
The is for windows only. They expected input is the output
of one of the commands:

```shell
    dir /q <folder>
```

Or for a recursive listing

```shell
    dir /qs <folder>
```

It is assumed that the output of the command is captured in a file. This files can 
then be passed to the application.

## Syntax

```shell
python convert2csv.py -h
```

```text
usage: dirtocsv [-h] [-o] [-i] [-d | -f] [-e ENCODING] dirdump output_table

The function parses directory output from a terminal (Windows) using the /q option. The listing contains
information about the owner of each file/folder

positional arguments:
  dirdump               Specify the file containing the output of the dir /qs command
  output_table          Specify the output CSV table name

options:
  -h, --help            show this help message and exit
  -o, --overwrite       Overwrite existing output table
  -i, --ignore_dot_folders
                        Exclude . and .. folders from the output table
  -d, --dirs_only       Only extract folders into the output table
  -f, --files_only      Only extract files into the output table
  -e ENCODING, --encoding ENCODING
                        Specify the text encoding of the input file
```
