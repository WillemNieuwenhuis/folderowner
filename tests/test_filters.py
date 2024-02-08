from filter_functions import (
    filter_dot_folders, filter_files_only, filter_folder_only, exec_filter_chain)

FILES_TO_FILTER = [
    ('2023-11-01', '11:32', '<DIR>', 'NT AUTHORITY\SYSTEM', '.', r'c:\\'),  # noqa: W605, E501
    ('2023-11-01', '11:32', '<DIR>', 'NT AUTHORITY\SYSTEM', '..', r'c:\\'),  # noqa: W605, E501
    ('2023-11-01', '10:59', '<DIR>', r'AD\nieuwenhuis', 'Data', r'c:\\'),  # noqa: W605, E501
    ('2024-01-08', '10:31', '<DIR>', 'BUILTIN\Administrators', 'NewFollowMe', r'c:\\'),  # noqa: W605, E501
    ('2022-05-07', '6:24 ', '<DIR>', 'NT AUTHORITY\SYSTEM', 'PerfLogs', r'c:\\'),  # noqa: W605, E501
    ('2024-01-25', '13:51', '<DIR>', 'NT SERVICE\TrustedInstaller', 'Program Files', r'c:\\'),  # noqa: W605, E501
    ('2024-01-08', '17:06', '<DIR>', 'NT SERVICE\TrustedInstaller',  # noqa: W605, E501
     'Program Files (x86)', r'c:\\'),
    ('2023-10-30', '14:32', '<DIR>', 'NT AUTHORITY\SYSTEM', 'Users', r'c:\\'),  # noqa: W605, E501
    ('2024-01-11', '10:05', '<DIR>', 'NT SERVICE\TrustedInstaller', 'Windows', r'c:\\'),  # noqa: W605, E501
    ('2023-09-30', '6:47', '112240', 'NT AUTHORITY\SYSTEM', 'appverifUI.dll', r'c:\\'),  # noqa: W605, E501
    ('2023-12-15', '9:50', '12288', '...', 'DumpStack.log', r'c:\\'),
    ('2023-09-30', '6:46', '66216', 'NT AUTHORITY\SYSTEM', 'vfcompat.dll', r'c:\\'),  # noqa: W605, E501
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


# Test the filter chain. Possible scenarios: 56.
# Only a subset is selected
def test_filter_chain_files_only_takes_precedence():
    lst = exec_filter_chain(FILES_TO_FILTER, True, True, True)
    assert len(lst) == 3


def test_filter_chain_files_all_by_default():
    sz = len(FILES_TO_FILTER)
    lst = exec_filter_chain(FILES_TO_FILTER)
    assert len(lst) == sz


def test_filter_chain_files_all_explicit():
    sz = len(FILES_TO_FILTER)
    lst = exec_filter_chain(FILES_TO_FILTER, False, False, False)
    assert len(lst) == sz


def test_filter_chain_files_all_explit_keyword():
    sz = len(FILES_TO_FILTER)
    lst = exec_filter_chain(FILES_TO_FILTER, exclude_parents=False,
                            files_only=False, folders_only=False)
    assert len(lst) == sz


def test_filter_chain_files_all_explit_keyword_mixed():
    sz = len(FILES_TO_FILTER)
    lst = exec_filter_chain(FILES_TO_FILTER, False,
                            files_only=False, folders_only=False)
    assert len(lst) == sz


def test_filter_chain_files_only():
    lst = exec_filter_chain(FILES_TO_FILTER, files_only=True)
    assert len(lst) == 3


def test_filter_chain_files_only_no_keyword():
    lst = exec_filter_chain(FILES_TO_FILTER, False, True)
    assert len(lst) == 3


def test_filter_chain_folders_only():
    lst = exec_filter_chain(FILES_TO_FILTER, folders_only=True)
    assert len(lst) == 9


def test_filter_chain_folders_only_no_keyword():
    lst = exec_filter_chain(FILES_TO_FILTER, False, False, True)
    assert len(lst) == 9


def test_filter_chain_folders_only_no_parents():
    lst = exec_filter_chain(FILES_TO_FILTER, folders_only=True, exclude_parents=True)
    assert len(lst) == 7


def test_filter_chain_folders_only_no_parents_no_keywords():
    lst = exec_filter_chain(FILES_TO_FILTER, True, False, True)
    assert len(lst) == 7
