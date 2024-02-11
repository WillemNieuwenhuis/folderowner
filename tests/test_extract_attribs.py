import os
from pathlib import Path
import pytest

from dirfunc.main_iterator import FolderIterator
from dirfunc.extract_functions import extract_attribs, extract_attribs_cmd

LOGIN_USER = '\\'.join(
    [os.environ.get('userdomain'), os.environ.get('username')])

# CMD strings
NAME_NO_SPACE_CMD = f'2024-01-19  16:48        52,651,341 {LOGIN_USER:23}         owner_rsdata.lst'  # noqa: E501
NAME_OVERLAP_CMD = r'2022-05-07  06:20            12,288 NT SERVICE\TrustedInstawinhlp32.exe'  # noqa: E501

# TCC strings
NAME_NO_SPACE = f'21-01-2023  17:04         <DIR>    {LOGIN_USER}  ExtrasCprorgramming'  # noqa: E501
NAME_WITH_SPACES = rf'06-03-2015  16:53      28,847,799  {LOGIN_USER}  The Art of Electronics 2nd ed - Horowitz & Hill.pdf'  # noqa: E501
ENTRY_NO_OWNER = r'06-03-2015  16:53      28,847,799  The Art of Electronics 2nd ed - Horowitz & Hill.pdf'  # noqa: E501

TEST_DIR = Path(__file__).parent


# CMD
def test_cmd_extract_attribs_owner_ok():
    *_, owner, _ = extract_attribs_cmd(NAME_NO_SPACE_CMD)
    assert owner == LOGIN_USER


def test_cmd_extract_attribs_overlap_owner():
    *_, owner, _ = extract_attribs_cmd(NAME_OVERLAP_CMD)
    assert r'NT SERVICE\TrustedInsta' == owner


def test_cmd_extract_attribs_overlap_name():
    *_, filename = extract_attribs_cmd(NAME_OVERLAP_CMD)
    assert 'winhlp32.exe' == filename


# TCC
def test_extract_attribs_owner_ok():
    *_, owner, _ = extract_attribs(NAME_NO_SPACE)
    assert owner == LOGIN_USER


def test_extract_attribs_date_ok():
    date, *_ = extract_attribs(NAME_NO_SPACE)
    assert date == '21-01-2023'


def test_extract_attribs_time_ok():
    _, time, *_ = extract_attribs(NAME_NO_SPACE)
    assert time == '17:04'


def test_extract_attribs_dir_ok():
    _, _, size, *_ = extract_attribs(NAME_NO_SPACE)
    assert size == '<DIR>'


def test_extract_attribs_file_with_spaces():
    *_, name = extract_attribs(NAME_WITH_SPACES)
    assert name == 'The Art of Electronics 2nd ed - Horowitz & Hill.pdf'


def test_extract_attribs_file_with_spaces_size_number():
    _, _, size, *_ = extract_attribs(NAME_WITH_SPACES)
    assert size == '28847799'


# dynamic TCC or CMD
@pytest.fixture
def file_list():
    with open(TEST_DIR / 'test_file_list_tcc.lst', encoding='utf8') as fil:
        lst = [line.strip() for line in fil.readlines()]

    return lst


@pytest.fixture
def file_list_cmd():
    with open(TEST_DIR / 'test_file_list_cmd.lst', encoding='utf8') as fil:
        lst = [line.strip() for line in fil.readlines()]

    return lst


def test_shell_type_tcc(file_list: list[str]):
    fi = FolderIterator(iter(file_list))
    assert fi.extractfunction == extract_attribs


def test_shell_type_cmd(file_list_cmd: list[str]):
    fi = FolderIterator(iter(file_list_cmd))
    assert fi.extractfunction == extract_attribs_cmd
