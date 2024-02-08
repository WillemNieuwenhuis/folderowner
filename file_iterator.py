from typing import Iterable


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
