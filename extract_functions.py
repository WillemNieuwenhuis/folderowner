from typing import Callable


BUILTIN_ADMIN = r'BUILTIN\Administrators'
SPECIAL_DOMAIN = '...'

ExtractFunction = Callable[[str], tuple[str]]


def extract_attribs_cmd(lin: str) -> tuple[str]:
    '''extract attributes at fixed starting positions in the line.
       expects output from console from CMD.exe
    '''
    datestr = lin[0:12].strip()
    timestr = lin[12:17].strip()
    sizestr = lin[17:36].strip().replace(',', '')
    owner = lin[36:59].strip()
    if owner.find('\\') > 0:
        filename = lin[59:].strip()
        if owner.find(SPECIAL_DOMAIN) > 0:
            owner = BUILTIN_ADMIN    # Probably, user account cannot know
    else:
        owner = '-'
        filename = lin[36:]

    return datestr, timestr, sizestr, owner, filename


def extract_attribs(lin: str) -> tuple[str]:
    '''extract attributes at fixed starting positions in the line
    '''
    datestr = lin[0:12].strip()
    timestr = lin[12:17].strip()
    sizestr = lin[17:35].strip().replace(',', '')
    own_name = lin[35:]
    if own_name.startswith(SPECIAL_DOMAIN):
        # special case of resticted access to file info
        owner = BUILTIN_ADMIN    # Probably, user account cannot know
        filename = own_name[3:].strip()

    if pos := own_name.find('\\') > 0:
        # there is owner info
        dom = own_name[0:pos]
        parts = own_name[pos+1:].split()
        owner = '\\'.join([dom, parts[0]])
        filename = ' '.join(parts[1:])
    else:
        owner = '-'
        filename = own_name

    return datestr, timestr, sizestr, owner, filename


_extract_functions: dict[str, ExtractFunction] = {
    'TCC': extract_attribs, 'CMD': extract_attribs_cmd}


def get_extract_function(shell: str) -> ExtractFunction:
    return _extract_functions[shell]
