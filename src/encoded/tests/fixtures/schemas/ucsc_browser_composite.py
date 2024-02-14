import pytest


@pytest.fixture
def ucsc_browser_composite_17(testapp, lab, award):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'schema_version': '17',
        'internal_tags': ['ENCYCLOPEDIAv3', 'ENCYCLOPEDIAv4', 'ENCYCLOPEDIAv5', 'ENCYCLOPEDIAv6']
    }
    return item
