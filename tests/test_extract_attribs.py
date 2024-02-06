import pytest
import mock
import os
from pathlib import Path
from convert2csv import extract_attribs, extract_attribs_cmd, MissingOwner, ExtractFunction, FolderIterator

login_user = '\\'.join(
    [os.environ.get('userdomain'), os.environ.get('username')])

# CMD strings
NAME_NO_SPACE_CMD = f'2024-01-19  16:48        52,651,341 {login_user:23}         owner_rsdata.lst'
NAME_OVERLAP_CMD = r'2022-05-07  06:20            12,288 NT SERVICE\TrustedInstawinhlp32.exe'

# TCC strings
NAME_NO_SPACE = f'21-01-2023  17:04         <DIR>    {login_user}  ExtrasCprorgramming'
NAME_WITH_SPACES = rf'06-03-2015  16:53      28,847,799  {login_user}  The Art of Electronics 2nd ed - Horowitz & Hill.pdf'
ENTRY_NO_OWNER = r'06-03-2015  16:53      28,847,799  The Art of Electronics 2nd ed - Horowitz & Hill.pdf'

TEST_DIR = Path(__file__).parent


# CMD
def test_cmd_extract_attribs_owner_ok():
    *_, owner, _ = extract_attribs_cmd(NAME_NO_SPACE_CMD)
    assert owner == login_user


def test_cmd_extract_attribs_overlap_owner():
    *_, owner, _ = extract_attribs_cmd(NAME_OVERLAP_CMD)
    assert 'NT SERVICE\TrustedInsta' == owner


def test_cmd_extract_attribs_overlap_name():
    *_, filename = extract_attribs_cmd(NAME_OVERLAP_CMD)
    assert 'winhlp32.exe' == filename


# TCC
def test_extract_attribs_owner_ok():
    *_, owner, _ = extract_attribs(NAME_NO_SPACE)
    assert owner == login_user


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


def test_extract_no_owner():
    with pytest.raises(MissingOwner):
        all = extract_attribs(ENTRY_NO_OWNER)


# dynamic TCC or CMD
@pytest.fixture
def file_list():
    with open(TEST_DIR / 'test_file_list_tcc.lst') as fil:
        lst = [l.strip() for l in fil.readlines()]

    return lst


@mock.patch('convert2csv.extract_attribs')
def test_dynamic_extract(funmock, file_list):
    fi = FolderIterator(iter(file_list))
    files = next(fi)    # initiates calls to extract_attribs
    assert funmock.called
