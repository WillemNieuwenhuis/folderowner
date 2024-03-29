# Extract owner info from plain folder listing
This works for windows only. They expected input is the output
of one of the commands:

```shell
    dir /q <folder>
```

Or for a recursive listing

```shell
    dir /qs <folder>
```

> [!Note]
> Depending on the shell being used the formatting of the list can differ. TCC and CMD are now supported

It is assumed that the output of the command is captured in a file. This file can 
then be passed to the application.

> [!Note]
> To avoid language error messages you can change the default codepage in the console (CP437-Ansi) to UTF-8 (CP65001) with the command: `chcp 65001`.

> [!Warning]
> Retrieving the owner information is a slow operation and for folders with a large number of files this can take considerable time.


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
                        Specify the text encoding of the input file (default=UTF-8)
```
