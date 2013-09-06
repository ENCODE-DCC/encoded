import re

REPLACE_CHARS = '<>&'
SUBS = {c: '\\u%04X' % ord(c) for c in REPLACE_CHARS}
json_script_escape_re = re.compile('[%s]' % ''.join(re.escape(c) for c in REPLACE_CHARS))


def json_u_escape(matchobj):
    return SUBS[matchobj.group(0)]


def json_script_escape(json_string):
    '''Escape JSON for script element content

    Works for both HTML (CDATA) and XHTML (PCDATA).
    '''
    return json_script_escape_re.subn(json_u_escape, json_string)[0]
