from future.standard_library import install_aliases
install_aliases()

from contentbase.resources import *  # noqa


def includeme(config):
    config.include('pyramid_tm')
    config.include('.stats')
    config.include('.calculated')
    config.include('.embedding')
    config.include('.json_renderer')
    config.include('.validation')
    config.include('.predicates')
    config.include('.invalidation')
    config.include('.upgrader')
    config.include('.auditor')
    config.include('.resources')
    config.include('.attachment')
    config.include('.schema_graph')
    config.include('.jsonld_context')
    config.include('.schema_views')
