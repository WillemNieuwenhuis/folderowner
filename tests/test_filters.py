import pytest
from convert2csv import filter_dot_folders, filter_files_only, filter_folder_only

FILES_TO_FILTER = [
    ('2023-11-01', '11:32', '<DIR>', 'NT AUTHORITY\SYSTEM', '.', r'c:\\'),
    ('2023-11-01', '11:32', '<DIR>', 'NT AUTHORITY\SYSTEM', '..', r'c:\\'),
    ('2023-11-01', '10:59', '<DIR>', r'AD\nieuwenhuis', 'Data', r'c:\\'),
    ('2024-01-08', '10:31', '<DIR>', 'BUILTIN\Administrators', 'NewFollowMe', r'c:\\'),
    ('2022-05-07', '6:24 ', '<DIR>', 'NT AUTHORITY\SYSTEM', 'PerfLogs', r'c:\\'),
    ('2024-01-25', '13:51', '<DIR>', 'NT SERVICE\TrustedInstaller', 'Program Files', r'c:\\'),
    ('2024-01-08', '17:06', '<DIR>', 'NT SERVICE\TrustedInstaller',
     'Program Files (x86)', r'c:\\'),
    ('2023-10-30', '14:32', '<DIR>', 'NT AUTHORITY\SYSTEM', 'Users', r'c:\\'),
    ('2024-01-11', '10:05', '<DIR>', 'NT SERVICE\TrustedInstaller', 'Windows', r'c:\\'),
    ('2023-09-30', '6:47', '112240', 'NT AUTHORITY\SYSTEM', 'appverifUI.dll', r'c:\\'),
    ('2023-12-15', '9:50', '12288', '...', 'DumpStack.log', r'c:\\'),
    ('2023-09-30', '6:46', '66216', 'NT AUTHORITY\SYSTEM', 'vfcompat.dll', r'c:\\'),
]


def test_filter_dot_folders():
    sz = len(FILES_TO_FILTER)
    lst = filter_dot_folders(FILES_TO_FILTER)
    assert len(lst) == sz-2


def test_files_only():
    lst = filter_files_only(FILES_TO_FILTER)
    assert len(lst) == 3


def test_folders_only():
    lst = filter_folder_only(FILES_TO_FILTER)
    assert len(lst) == 9
