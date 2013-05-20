from base64 import (
    b64decode,
    b64encode,
)
from hashlib import sha384
from pyramid.view import view_config
from .contentbase import Root
from .schema_utils import (
    schema_validator,
)
from .storage import (
    DBSession,
    EDWKey,
    Key,
)
from .validation import ValidationFailure

EDW_SETTINGS = __name__ + ':edw_settings'
DEFAULT_SALTS = {
    'salt_before': "186ED79BAEXzeusdioIsdklnw88e86cd73",
    'salt_after': "<*#$*(#)!DSDFOUIHLjksdf",
    'salt_base': b64decode("""\
Kf8r/S37L/kh9yP1JfMn8TnvO+096z/pMecz5TXjN+EJ3wvdDdsP2QHXA9UF0wfRGc8bzR3LH8kR
xxPFFcMXwWm/a71tu2+5YbdjtWWzZ7F5r3utfat/qXGnc6V1o3ehSZ9LnU2bT5lBl0OVRZNHkVmP
W41di1+JUYdThVWDV4Gpf6t9rXuveaF3o3Wlc6dxuW+7bb1rv2mxZ7NltWO3YYlfi12NW49ZgVeD
VYVTh1GZT5tNnUufSZFHk0WVQ5dB6T/rPe077znhN+M15TPnMfkv+y39K/8p8SfzJfUj9yHJH8sd
zRvPGcEXwxXFE8cR2Q/bDd0L3wnRB9MF1QPXASn/K/0t+y/5Ifcj9SXzJ/E57zvtPes/6THnM+U1
4zfhCd8L3Q3bD9kB1wPVBdMH0RnPG80dyx/JEccTxRXDF8Fpv2u9bbtvuWG3Y7Vls2exea97rX2r
f6lxp3OldaN3oUmfS51Nm0+ZQZdDlUWTR5FZj1uNXYtfiVGHU4VVg1eBqX+rfa17r3mhd6N1pXOn
cblvu229a79psWezZbVjt2GJX4tdjVuPWYFXg1WFU4dRmU+bTZ1Ln0mRR5NFlUOXQek/6z3tO+85
4TfjNeUz5zH5L/st/Sv/KfEn8yX1I/chyR/LHc0bzxnBF8MVxRPHEdkP2w3dC98J0QfTBdUD1wE=
"""),
}


def includeme(config):
    config.scan(__name__)
    prefix = 'edw.'
    settings = DEFAULT_SALTS.copy()
    for k, v in config.registry.settings.items():
        if k.startswith(prefix):
            settings[k[len(prefix):]] = v
    config.registry[EDW_SETTINGS] = settings


@view_config(name='edw_key_create', context=Root, subpath_segments=0,
             request_method='POST', permission='edw_key_create',
             validators=[schema_validator('edw_key.json')])
def edw_key_create(context, request):
    email = request.validated['email']
    username = request.validated['username']
    pwhash = request.validated['pwhash']

    session = DBSession()
    key = session.query(Key).get(('user:email', email))
    if key is None:
        msg = "User not found for %r" % email
        request.errors.add('body', ['email'], msg)
    else:
        userid = key.rid

    if not username:
        msg = "username must not be blank"
        request.errors.add('body', ['username'], msg)
    else:
        existing = session.query(EDWKey).get(username)
        if existing is not None:
            msg = "username already exists"
            request.errors.add('body', ['username'], msg)

    if request.errors:
        raise ValidationFailure()

    edw_key = EDWKey(
        username=username,
        pwhash=pwhash,
        userid=userid,
    )
    session.add(edw_key)
    request.response.status = 201
    return {'status': 'success'}


@view_config(name='edw_key_update', context=Root, subpath_segments=0,
             request_method='POST', permission='edw_key_update',
             validators=[schema_validator('edw_key.json')])
def edw_key_update(context, request):
    email = request.validated['email']
    username = request.validated['username']
    pwhash = request.validated['pwhash']

    session = DBSession()
    key = session.query(Key).get(('user:email', email))
    if key is None:
        msg = "User not found for %r" % email
        request.errors.add('body', ['email'], msg)
    else:
        userid = key.rid

    existing = session.query(EDWKey).get(username)
    if existing is None:
        msg = "username not found"
        request.errors.add('body', ['username'], msg)

    if request.errors:
        raise ValidationFailure()

    existing.pwhash = pwhash
    existing.userid = userid
    session.add(existing)
    return {'status': 'success'}


def basic_auth_check(username, password, request):
    session = DBSession()
    edw_key = session.query(EDWKey).get(username)
    if edw_key is None:
        return None

    pwhash = edw_key.pwhash

    salts = request.registry[EDW_SETTINGS]
    valid = verify(password, pwhash, edw_hash, salts=salts)
    if not valid:
        return None

    return []


def verify(attempt, pwhash, hash_func, **hash_func_args):
    """ Constant time string comparison
    """
    attempt_hash = hash_func(attempt, **hash_func_args)
    if len(pwhash) != len(attempt_hash):
        return False
    ok = True
    for a, b in zip(pwhash, attempt_hash):
        if a != b:
            ok = False
    return ok


def edw_hash(password, salts=DEFAULT_SALTS):
    """ EDW's password hashing scheme

    Cryptographic strength of the hashing function is less of a concern for
    randomly generated passwords.
    """
    password = password.encode('utf-8')
    salted = salts['salt_before'] + password + salts['salt_after'] + '\0'
    if len(salted) > len(salts['salt_base']):
        raise ValueError("Password too long")
    salted += salts['salt_base'][len(salted):]
    return b64encode(sha384(salted).digest())
