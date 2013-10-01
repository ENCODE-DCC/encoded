from datetime import datetime
from jsonschema import NO_DEFAULT
from pyramid.security import effective_principals
from pyramid.threadlocal import get_current_request
import uuid

SERVER_DEFAULTS = {}

def server_default(func):
    SERVER_DEFAULTS[func.__name__] = func


@server_default
def userid(property, subschema):
    request = get_current_request()
    principals = effective_principals(request)
    for principal in principals:
        if principal.startswith('userid:'):
            return principal[7:]
    return NO_DEFAULT


@server_default
def now(property, subschema):
    return datetime.now().isoformat()


@server_default
def uuid4(property, subschema):
    return str(uuid.uuid4())
