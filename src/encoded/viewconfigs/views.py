"""
Elasticsearch Based View Configs
"""
from pyramid.view import view_config  # pylint: disable=import-error

from encoded.helpers.helper import (
    View_Item,
    search_result_actions,
)
from encoded.viewconfigs.auditview import AuditView
from encoded.viewconfigs.matrix import MatrixView
from encoded.viewconfigs.news import NewsView
from encoded.viewconfigs.summary import SummaryView

from snovault import AbstractCollection  # pylint: disable=import-error
from snovault.resource_views import collection_view_listing_db  # pylint: disable=import-error
from snovault.viewconfigs.report import ReportView   # pylint: disable=import-error
from snovault.viewconfigs.searchview import SearchView   # pylint: disable=import-error


DEFAULT_DOC_TYPES = [
    'AntibodyLot',
    'Award',
    'Biosample',
    'Dataset',
    'GeneticModification',
    'Page',
    'Pipeline',
    'Publication',
    'Software',
    'Target',
]


def includeme(config):
    '''Associated views routes'''
    config.add_route('search', '/search{slash:/?}')
    config.add_route('report', '/report{slash:/?}')
    config.add_route('matrix', '/matrix{slash:/?}')
    config.add_route('news', '/news/')
    config.add_route('audit', '/audit/')
    config.add_route('summary', '/summary{slash:/?}')
    config.scan(__name__)


def _get_doc_types(context, request):
    doc_types = []
    if (hasattr(context, 'type_info') and
            hasattr(context.type_info, 'name') and
            context.type_info.name):
        doc_types = [context.type_info.name]
    else:
        doc_types = request.params.getall('type')
    if '*' in doc_types:
        doc_types = ['Item']
    return doc_types


@view_config(context=AbstractCollection, permission='list', request_method='GET', name='listing')
def collection_view_listing_es(context, request):
    '''Switch to change summary page loading options'''
    if request.datastore != 'elasticsearch':
        return collection_view_listing_db(context, request)
    return search(context, request)


@view_config(route_name='audit', request_method='GET', permission='search')
def audit(context, request):
    '''Audit Page Endpoint'''
    audit_view = AuditView(context, request)
    return audit_view.preprocess_view()


@view_config(route_name='matrix', request_method='GET', permission='search')
def matrix(context, request):
    '''Matrix Page Endpoint'''
    matrix_view = MatrixView(context, request)
    return matrix_view.preprocess_view()


@view_config(route_name='news', request_method='GET', permission='search')
def news(context, request):
    '''News Page Endpoint'''
    news_view = NewsView(context, request)
    return news_view.preprocess_view()


@view_config(route_name='report', request_method='GET', permission='search')
def report(context, request):
    '''Report Page Endpoint'''
    report_view = ReportView(context, request)
    return report_view.preprocess_view()


@view_config(route_name='search', request_method='GET', permission='search')
def search(context, request, search_type=None, return_generator=False):
    '''Search Page Endpoint'''
    search_view = SearchView(
        context,
        request,
        search_type=search_type,
        return_generator=return_generator,
        default_doc_types=DEFAULT_DOC_TYPES
    )
    doc_types = _get_doc_types(context, request)
    views = []
    view_item = View_Item(search_view.request, search_view.search_base)
    if len(doc_types) == 1:
        type_info = search_view.types[doc_types[0]]
        views.append(view_item.tabular_report)
        if hasattr(type_info.factory, 'matrix'):
            views.append(view_item.summary_matrix)
        if hasattr(type_info.factory, 'summary_data'):
            views.append(view_item.summary_report)
    return search_view.preprocess_view(views=views, search_result_actions=search_result_actions)


@view_config(route_name='summary', request_method='GET', permission='search')
def summary(context, request):
    '''
    Summary Page Endpoint
    - /summary/?type=Experiment
    '''
    summary_view = SummaryView(context, request)
    return summary_view.preprocess_view()
