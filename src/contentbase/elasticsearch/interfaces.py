from zope.interface import Interface

# Registry tool id
ELASTIC_SEARCH = 'elasticsearch'


class ICachedItem(Interface):
    """ Marker for cached Item
    """
