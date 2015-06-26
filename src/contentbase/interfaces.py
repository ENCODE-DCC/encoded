# Tool names
BLOBS = 'blobs'
CALCULATED_PROPERTIES = 'calculated_properties'
COLLECTIONS = 'collections'
CONNECTION = 'connection'
DBSESSION = 'dbsession'
STORAGE = 'storage'
ROOT = 'root'
TYPES = 'types'

# Constants
PHASE1_5_CONFIG = -15


# Events
class Created(object):
    def __init__(self, object, request):
        self.object = object
        self.request = request


class BeforeModified(object):
    def __init__(self, object, request):
        self.object = object
        self.request = request


class AfterModified(object):
    def __init__(self, object, request):
        self.object = object
        self.request = request
