import os
import re
from typing import Callable


# possible system domains
NTAUTH_DOMAIN = 'NT AUTHORITY'
BUILTIN_DOMAIN = 'BUILTIN'
NTSERV_DOMAIN = 'NT SERVICE'
LOCAL_DOMAIN = os.environ.get('userdomain')
SPECIAL_DOMAIN = '...'
all_domains = [NTAUTH_DOMAIN, BUILTIN_DOMAIN,
               NTSERV_DOMAIN, LOCAL_DOMAIN, SPECIAL_DOMAIN]


class MissingOwner(Exception):
    pass


ExtractFunction = Callable[[str], tuple[str]]


def get_valid_domain_from(name: str) -> str | None:
    checked = [dom for dom in all_domains if name.find(dom) >= 0]
    if checked:
        return checked[0]

    return None


def extract_attribs_cmd(lin: str) -> tuple[str]:
    '''extract attributes at fixed starting positions in the line.
       expects output from console from CMD.exe
    '''
    dom = get_valid_domain_from(lin)
    if not dom:
        raise MissingOwner(
            'Could not find valid owner field, did you use "/Q"')
    datestr = lin[0:12].strip()
    timestr = lin[12:17].strip()
    sizestr = lin[17:36].strip().replace(',', '')
    owner = lin[36:59].strip()
    filename = lin[59:].strip()
    if owner.find('...') > 0:
        owner = r'BUILTIN\Administrators'    # Probably, user account cannot know

    return datestr, timestr, sizestr, owner, filename


def extract_attribs(lin: str) -> tuple[str]:
    '''extract attributes at fixed starting positions in the line
    '''
    dom = get_valid_domain_from(lin)
    if not dom:
        raise MissingOwner(
            'Could not find valid owner field, did you use "/Q"')
    datestr = lin[0:12].strip()
    timestr = lin[12:17].strip()
    sizestr = lin[17:35].strip().replace(',', '')
    own_name = lin[35:]
    if own_name.find('...') == -1:
        pat = rf'({dom}\\.*)\b\s{{2}}(.*)'
        res = re.search(pat, lin).groups()
        owner, filename = res
    else:
        owner = r'BUILTIN\Administrators'    # Probably, user account cannot know
        filename = own_name[3:].strip()

    return datestr, timestr, sizestr, owner, filename


_extract_functions: dict[str, ExtractFunction] = {
    'TCC': extract_attribs, 'CMD': extract_attribs_cmd}


def get_extract_function(shell: str) -> ExtractFunction:
    return _extract_functions[shell]
