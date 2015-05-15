from future.standard_library import install_aliases
install_aliases()

import sys
PY2 = sys.version_info.major == 2

from contentbase.resources import *  # noqa


def includeme(config):
    settings = config.registry.settings
    settings.setdefault('contentbase.elasticsearch.index', 'contentbase')

    config.include('pyramid_tm')
    config.include('.stats')
    config.include('.calculated')
    config.include('.embedding')
    config.include('.json_renderer')
    config.include('.validation')
    config.include('.predicates')
    config.include('.invalidation')
    config.include('.indexing')
    config.include('.es_storage')
    config.include('.upgrader')
    config.include('.auditor')
    config.include('.resources')
    config.include('.attachment')
    config.include('.schema_graph')
    config.include('.jsonld_context')
    config.include('.schema_views')

    if asbool(settings.get('indexer')) and not PY2:
        config.include('.mp_indexing')
