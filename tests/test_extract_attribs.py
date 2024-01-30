import pytest
from convert2csv import extract_attribs, MissingOwner
import os

login_user = '\\'.join(
    [os.environ.get('userdomain'), os.environ.get('username')])

NAME_NO_SPACE = '21-01-2023  17:04         <DIR>    SPEEDY\Wim  ExtrasCprorgramming'
NAME_WITH_SPACES = r'06-03-2015  16:53      28,847,799  SPEEDY\Wim  The Art of Electronics 2nd ed - Horowitz & Hill.pdf'
ENTRY_NO_OWNER = r'06-03-2015  16:53      28,847,799  The Art of Electronics 2nd ed - Horowitz & Hill.pdf'


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
