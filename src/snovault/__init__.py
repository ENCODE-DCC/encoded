import sys
if sys.version_info.major == 2:
    from future.standard_library import install_aliases
    install_aliases()
    import functools
    from backports.functools_lru_cache import lru_cache
    functools.lru_cache = lru_cache
import netaddr
from pyramid.config import Configurator
from pyramid.settings import (
    asbool,
)


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
from .app import (
    app_version,
    session,
    configure_dbsession,
    static_resources,
    changelogs,
    json_from_path,
    )


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


def main(global_config, **local_config):
    """ This function returns a Pyramid WSGI application.
    """
    settings = global_config
    settings.update(local_config)

    # TODO - these need to be set for dummy app
    # settings['snovault.jsonld.namespaces'] = json_asset('snovault:schemas/namespaces.json')
    # settings['snovault.jsonld.terms_namespace'] = 'https://www.encodeproject.org/terms/'
    settings['snovault.jsonld.terms_prefix'] = 'snovault'
    settings['snovault.elasticsearch.index'] = 'snovault'

    config = Configurator(settings=settings)
    from snovault.elasticsearch import APP_FACTORY
    config.registry[APP_FACTORY] = main  # used by mp_indexer
    config.include(app_version)

    config.include('pyramid_multiauth')  # must be before calling set_authorization_policy
    from pyramid_localroles import LocalRolesAuthorizationPolicy
    # Override default authz policy set by pyramid_multiauth
    config.set_authorization_policy(LocalRolesAuthorizationPolicy())
    config.include(session)

    config.include(configure_dbsession)
    config.include('snovault')
    config.commit()  # commit so search can override listing

    # Render an HTML page to browsers and a JSON document for API clients
    config.include('snowflakes.renderers')
    # these two should be application specific
    config.include('.authentication')
    config.include('snowflakes.root')

    if 'elasticsearch.server' in config.registry.settings:
        config.include('snovault.elasticsearch')
        # needed for /search/?
        config.include('snowflakes.search')

    config.include(static_resources)
    config.include(changelogs)

    # TODO This is optional AWS only - possibly move to a plug-in
    aws_ip_ranges = json_from_path(settings.get('aws_ip_ranges_path'), {'prefixes': []})
    config.registry['aws_ipset'] = netaddr.IPSet(
        record['ip_prefix'] for record in aws_ip_ranges['prefixes'] if record['service'] == 'AMAZON')

    if asbool(settings.get('testing', False)):
        config.include('.tests.testing_views')

    # Load upgrades last so that all views (including testing views) are
    # registered.
    # TODO we would need a generic upgrade audit PACKAGE (__init__)
    # config.include('.audit)
    # config.include('.upgrade')

    app = config.make_wsgi_app()

    return app
