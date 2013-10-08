from datetime import datetime
from jsonschema import NO_DEFAULT
from pyramid.security import effective_principals
from pyramid.threadlocal import get_current_request
from string import (
    digits,
    ascii_uppercase,
    )
import random
import uuid

SERVER_DEFAULTS = {}

def server_default(func):
    SERVER_DEFAULTS[func.__name__] = func


ACCESSION_FACTORY = __name__ + ':accession_factory'

def includeme(config):
    from pyramid.path import DottedNameResolver
    accession_factory = config.registry.settings.get('accession_factory')
    if accession_factory:
        factory = DottedNameResolver().resolve(accession_factory)
    else:
        factory = enc_accession
    config.registry[ACCESSION_FACTORY] = factory


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


@server_default
def accession(property, subschema):
    request = get_current_request()
    factory = request.registry[ACCESSION_FACTORY]
    # With 17 576 000 options
    ATTEMPTS = 10
    for attempt in xrange(ATTEMPTS):
        new_accession = factory(subschema['accessionType'])
        if new_accession in request.root:
            continue
        return new_accession
    raise AssertionError("Free accession not found in %d attempts" % ATTEMPTS)


ENC_ACCESSION_FORMAT = (digits, digits, digits, ascii_uppercase, ascii_uppercase, ascii_uppercase,
)


def enc_accession(accession_type):
    random_part = ''.join(random.choice(s) for s in ENC_ACCESSION_FORMAT)
    return 'ENC' + accession_type + random_part


TEST_ACCESSION_FORMAT = (digits, ) * 6

def test_accession(accession_type):
    """ Test accessions are generated on test.encodedcc.org
    """
    random_part = ''.join(random.choice(s) for s in TEST_ACCESSION_FORMAT)
    return 'TST' + accession_type + random_part
