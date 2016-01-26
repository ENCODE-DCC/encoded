import sys
if sys.version_info.major == 2:
    from future.standard_library import install_aliases
    install_aliases()
    import functools
    from backports.functools_lru_cache import lru_cache
    functools.lru_cache = lru_cache

from .auditor import (  # noqa
    AuditFailure,
    audit_checker,
)
from .calculated import calculated_property  # noqa
from .config import (  # noqa
    abstract_collection,
    collection,
    root,
)
from .interfaces import *  # noqa
from .resources import (  # noqa
    AbstractCollection,
    Collection,
    Item,
    Resource,
    Root,
)
from .schema_utils import load_schema  # noqa
from .upgrader import upgrade_step  # noqa


def includeme(config):
    config.include('pyramid_tm')
    config.include('.util')
    config.include('.stats')
    config.include('.batchupgrade')
    config.include('.calculated')
    config.include('.config')
    config.include('.connection')
    config.include('.embed')
    config.include('.json_renderer')
    config.include('.validation')
    config.include('.predicates')
    config.include('.invalidation')
    config.include('.upgrader')
    config.include('.auditor')
    config.include('.storage')
    config.include('.typeinfo')
    config.include('.resources')
    config.include('.attachment')
    config.include('.schema_graph')
    config.include('.jsonld_context')
    config.include('.schema_views')
    config.include('.crud_views')
    config.include('.indexing_views')
    config.include('.resource_views')
