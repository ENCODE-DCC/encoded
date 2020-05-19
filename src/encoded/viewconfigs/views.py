"""
Elasticsearch Based View Configs
"""
from urllib.parse import (
    parse_qs,
    urlencode,
)
from pyramid.view import view_config  # pylint: disable=import-error

from encoded.helpers.helper import (
    View_Item,
    search_result_actions,
)
from encoded.viewconfigs.auditview import AuditView
from encoded.viewconfigs.matrix import MatrixView
from encoded.viewconfigs.summary import SummaryView

from snovault import AbstractCollection  # pylint: disable=import-error
from snovault.resource_views import collection_view_listing_db  # pylint: disable=import-error
from snovault.viewconfigs.report import ReportView   # pylint: disable=import-error
from snovault.viewconfigs.searchview import SearchView   # pylint: disable=import-error


DEFAULT_DOC_TYPES = [
    'AntibodyLot',
    'Award',
    'Biosample',
    'BiosampleType',
    'Dataset',
    'GeneticModification',
    'Page',
    'Pipeline',
    'Publication',
    'Software',
    'Gene',
    'Target',
    'Patient',
    'Biospecimen',
    'Bioexperiment',
    'Biofile',
    'PathologyReport',
    'Surgery',
    'Bioexperiment'
]


def includeme(config):
    '''Associated views routes'''
    config.add_route('search', '/search{slash:/?}')
    config.add_route('search_elements', '/search_elements/{search_params}')
    config.add_route('report', '/report{slash:/?}')
    config.add_route('matrix', '/matrix{slash:/?}')
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


def _get_search_views(view_instance, context, request):
    doc_types = _get_doc_types(context, request)
    views = []
    # TODO: Fix using protected members
    # pylint: disable=protected-access
    view_item = View_Item(view_instance._request, view_instance._search_base)
    # TODO: Move into SearchView after doc_types check
    if len(doc_types) == 1:
        if doc_types[0] in view_instance._types:
            type_info = view_instance._types[doc_types[0]]
            views.append(view_item.tabular_report)
            if hasattr(type_info.factory, 'matrix'):
                views.append(view_item.summary_matrix)
            if hasattr(type_info.factory, 'summary_data'):
                views.append(view_item.summary_report)
    return views


@view_config(context=AbstractCollection, permission='list', request_method='GET', name='listing')
def collection_view_listing_es(context, request):
    '''Switch to change summary page loading options'''
    if request.datastore != 'elasticsearch':
        return collection_view_listing_db(context, request)
    return search(context, request)


@view_config(route_name='audit', request_method='GET', permission='search')
def audit(context, request):
    '''
    Audit Page Endpoint
    /audit/?type=Experiment
    '''
    audit_view = AuditView(context, request)
    return audit_view.preprocess_view()


@view_config(route_name='matrix', request_method='GET', permission='search')
def matrix(context, request):
    '''
    Matrix Page Endpoint
    /matrix/?type=Experiment
    '''
    matrix_view = MatrixView(context, request)
    return matrix_view.preprocess_view()


@view_config(route_name='report', request_method='GET', permission='search')
def report(context, request):
    '''
    Report Page Endpoint
    /report/?type=Experiment
    '''
    report_view = ReportView(context, request)
    views = _get_search_views(report_view, context, request)
    res = report_view.preprocess_view(
        views=views,
        search_result_actions=search_result_actions,
    )
    # TODO: Fix using protected members
    # pylint: disable=protected-access
    report_download_route = report_view._request.route_path('report_download')
    res['download_tsv'] = report_download_route + report_view._search_base
    return res

@view_config(route_name='search', request_method='GET', permission='search')
def search(context, request, search_type=None, return_generator=False):
    '''
    Search Page Endpoint
    /search/?type=Experiment
    /search/?type=Publication&published_by=mouseENCODE&published_by=modENCODE&published_by=ENCODE
    '''
    search_view = SearchView(
        context,
        request,
        search_type=search_type,
        return_generator=return_generator,
        default_doc_types=DEFAULT_DOC_TYPES
    )
    views = _get_search_views(search_view, context, request)
    return search_view.preprocess_view(
        views=views,
        search_result_actions=search_result_actions,
    )


@view_config(route_name='search_elements', request_method='POST')
def search_elements(context, request):  # pylint: disable=unused-argument
    '''Same as search but takes JSON payload of search filters'''
    param_list = parse_qs(request.matchdict['search_params'])
    param_list.update(request.json_body)
    path = '/search/?%s' % urlencode(param_list, True)
    results = request.embed(path, as_user=True)
    return results


@view_config(route_name='summary', request_method='GET', permission='search')
def summary(context, request):
    '''
    Summary Page Endpoint
    /summary/?type=Experiment
    '''
    summary_view = SummaryView(context, request)
    return summary_view.preprocess_view()
