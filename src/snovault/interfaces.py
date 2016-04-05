# Tool names
AUDITOR = 'auditor'
BLOBS = 'blobs'
CALCULATED_PROPERTIES = 'calculated_properties'
COLLECTIONS = 'collections'
CONNECTION = 'connection'
DBSESSION = 'dbsession'
STORAGE = 'storage'
ROOT = 'root'
TYPES = 'types'
UPGRADER = 'upgrader'

# Constants
PHASE1_5_CONFIG = -15
PHASE2_5_CONFIG = -5


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


class AfterUpgrade(object):
    def __init__(self, object):
        self.object = object
