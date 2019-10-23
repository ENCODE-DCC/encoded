from pyramid.view import view_config

from snovault.elasticsearch.searches.interfaces import AUDIT_TITLE
from snovault.elasticsearch.searches.interfaces import MATRIX_TITLE
from snovault.elasticsearch.searches.interfaces import REPORT_TITLE
from snovault.elasticsearch.searches.interfaces import SEARCH_TITLE
from snovault.elasticsearch.searches.interfaces import SUMMARY
from snovault.elasticsearch.searches.interfaces import SUMMARY_TITLE
from snovault.elasticsearch.searches.fields import AuditMatrixWithFacetsResponseField
from snovault.elasticsearch.searches.fields import AllResponseField
from snovault.elasticsearch.searches.fields import BasicMatrixWithFacetsResponseField
from snovault.elasticsearch.searches.fields import BasicSearchResponseField
from snovault.elasticsearch.searches.fields import BasicSearchWithFacetsResponseField
from snovault.elasticsearch.searches.fields import BasicReportWithFacetsResponseField
from snovault.elasticsearch.searches.fields import ClearFiltersResponseField
from snovault.elasticsearch.searches.fields import ColumnsResponseField
from snovault.elasticsearch.searches.fields import ContextResponseField
from snovault.elasticsearch.searches.fields import DebugQueryResponseField
from snovault.elasticsearch.searches.fields import FiltersResponseField
from snovault.elasticsearch.searches.fields import IDResponseField
from snovault.elasticsearch.searches.fields import NotificationResponseField
from snovault.elasticsearch.searches.fields import NonSortableResponseField
from snovault.elasticsearch.searches.fields import RawMatrixWithAggsResponseField
from snovault.elasticsearch.searches.fields import RawSearchWithAggsResponseField
from snovault.elasticsearch.searches.fields import SearchBaseResponseField
from snovault.elasticsearch.searches.fields import SortResponseField
from snovault.elasticsearch.searches.fields import TitleResponseField
from snovault.elasticsearch.searches.fields import TypeOnlyClearFiltersResponseField
from snovault.elasticsearch.searches.fields import TypeResponseField
from snovault.elasticsearch.searches.parsers import ParamsParser
from snovault.elasticsearch.searches.responses import FieldedResponse


def includeme(config):
    config.add_route('search', '/search{slash:/?}')
    config.add_route('searchv2_raw', '/searchv2_raw{slash:/?}')
    config.add_route('searchv2_quick', '/searchv2_quick{slash:/?}')
    config.add_route('report', '/report{slash:/?}')
    config.add_route('matrixv2_raw', '/matrixv2_raw{slash:/?}')
    config.add_route('matrix', '/matrix{slash:/?}')
    config.add_route('target_matrix_tf_chip_seq', '/target_matrix/TF ChIP-seq{slash:/?}')
    config.add_route('target_matrix_histone', '/target_matrix/Histone ChIP-seq{slash:/?}')
    config.add_route('summary', '/summary{slash:/?}')
    config.add_route('audit', '/audit{slash:/?}')
    config.scan(__name__)


DEFAULT_ITEM_TYPES = [
    'AntibodyLot',
    'Award',
    'Biosample',
    'BiosampleType',
    'Dataset',
    'Donor',
    'GeneticModification',
    'Page',
    'Pipeline',
    'Publication',
    'Software',
    'Gene',
    'Target',
    'File',
    'Lab'
]


@view_config(route_name='search', request_method='GET', permission='search')
def search(context, request):
    # Note the order of rendering matters for some fields, e.g. AllResponseField and
    # NotificationResponseField depend on results from BasicSearchWithFacetsResponseField.
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(request)
        },
        response_fields=[
            TitleResponseField(
                title=SEARCH_TITLE
            ),
            TypeResponseField(
                at_type=[SEARCH_TITLE]
            ),
            IDResponseField(),
            ContextResponseField(),
            BasicSearchWithFacetsResponseField(
                default_item_types=DEFAULT_ITEM_TYPES
            ),
            AllResponseField(),
            NotificationResponseField(),
            FiltersResponseField(),
            ClearFiltersResponseField(),
            ColumnsResponseField(),
            SortResponseField(),
            DebugQueryResponseField()
        ]
    )
    return fr.render()


@view_config(route_name='searchv2_raw', request_method='GET', permission='search')
def searchv2_raw(context, request):
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(request)
        },
        response_fields=[
            RawSearchWithAggsResponseField(
                default_item_types=DEFAULT_ITEM_TYPES
            )
        ]
    )
    return fr.render()


@view_config(route_name='searchv2_quick', request_method='GET', permission='search')
def searchv2_quick(context, request):
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(request)
        },
        response_fields=[
            BasicSearchResponseField(
                default_item_types=DEFAULT_ITEM_TYPES
            )
        ]
    )
    return fr.render()


@view_config(route_name='report', request_method='GET', permission='search')
def report(context, request):
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(request)
        },
        response_fields=[
            TitleResponseField(
                title=REPORT_TITLE
            ),
            TypeResponseField(
                at_type=[REPORT_TITLE]
            ),
            IDResponseField(),
            ContextResponseField(),
            BasicReportWithFacetsResponseField(),
            AllResponseField(),
            NotificationResponseField(),
            FiltersResponseField(),
            TypeOnlyClearFiltersResponseField(),
            ColumnsResponseField(),
            NonSortableResponseField(),
            SortResponseField(),
            DebugQueryResponseField()
        ]
    )
    return fr.render()


@view_config(route_name='matrixv2_raw', request_method='GET', permission='search')
def matrixv2_raw(context, request):
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(request)
        },
        response_fields=[
            RawMatrixWithAggsResponseField(
                default_item_types=DEFAULT_ITEM_TYPES
            )
        ]
    )
    return fr.render()


def add_to_request_query_string(request, **params):
    """
    Add query strings to request.

        :param request: Request object
        :param **params: Query string key/value pairs to add to request
    """
    if not request:
        return request
    query_string_addition = [''.join(['&', param[0], '=', param[1]]) for param in params.items()]
    request.query_string = 'type=Experiment' + ''.join(query_string_addition)
    return request


def matrix_renderer(request, title, at_type, response_field_params=None):
    """
    Render a matrix.

        :param request: Pyramid request
        :param title:  Title
        :param at_type: a_type
        :param response_field_params: Response field parameters as a dictionary
    """
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(request)
        },
        response_fields=[
            ContextResponseField(),
            BasicMatrixWithFacetsResponseField(**response_field_params),
            DebugQueryResponseField(),
            IDResponseField(),
            NotificationResponseField(),
            SearchBaseResponseField(),
            TitleResponseField(
                title=title,
            ),
            TypeResponseField(
                at_type=at_type,
            ),
            FiltersResponseField(),
            TypeOnlyClearFiltersResponseField(),
        ]
    )
    return fr.render()


@view_config(route_name='matrix', request_method='GET', permission='search')
def matrix(context, request):
    """
    Matrix view.

        :param context: Pyramid context
        :param request: Pyramid Request
    """
    return matrix_renderer(
        request,
        MATRIX_TITLE,
        [MATRIX_TITLE],
        response_field_params={
            'default_item_type' : DEFAULT_ITEM_TYPES
        },
    )


@view_config(route_name='target_matrix_tf_chip_seq', request_method='GET', permission='search')
def target_matrix_tf(context, request):
    """
    Matrix view.

        :param context: Pyramid context
        :param request: Pyramid Request
    """
    request = add_to_request_query_string(request, assay_title='TF ChIP-seq')
    return matrix_renderer(
        request,
        'Target Matrix',
        [MATRIX_TITLE],
        response_field_params={
            'default_item_types': DEFAULT_ITEM_TYPES,
            'matrix_definition_name': 'target_matrix',
            'facets': [
                ('status', {'title': 'Status'}),
                ('award.project', {'title': 'Project'}),
                ('target.investigated_as', {'title': 'Target category'}),
                ('replicates.library.biosample.donor.organism.scientific_name', {'title': 'Organism'}),
            ],
        }
    )


@view_config(route_name='target_matrix_histone', request_method='GET', permission='search')
def target_matrix_histone(context, request):
    """
    Matrix view.

        :param context: Pyramid context
        :param request: Pyramid Request
    """
    request = add_to_request_query_string(request, assay_title='Histone ChIP-seq')
    return matrix_renderer(
        request,
        'Target Matrix',
        [MATRIX_TITLE],
        response_field_params={
            'default_item_types': DEFAULT_ITEM_TYPES,
            'matrix_definition_name': 'target_matrix',
            'facets': [
                ('status', {'title': 'Status'}),
                ('award.project', {'title': 'Project'}),
                ('target.investigated_as', {'title': 'Target category'}),
                ('replicates.library.biosample.donor.organism.scientific_name', {'title': 'Organism'}),
            ],
        }
    )


@view_config(route_name='summary', request_method='GET', permission='search')
def summary(context, request):
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(request)
        },
        response_fields=[
            TitleResponseField(
                title=SUMMARY_TITLE
            ),
            TypeResponseField(
                at_type=[SUMMARY_TITLE]
            ),
            IDResponseField(),
            SearchBaseResponseField(),
            ContextResponseField(),
            BasicMatrixWithFacetsResponseField(
                default_item_types=DEFAULT_ITEM_TYPES,
                matrix_definition_name=SUMMARY
            ),
            NotificationResponseField(),
            FiltersResponseField(),
            TypeOnlyClearFiltersResponseField(),
            DebugQueryResponseField()
        ]
    )
    return fr.render()


@view_config(route_name='audit', request_method='GET', permission='search')
def audit(context, request):
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(request)
        },
        response_fields=[
            TitleResponseField(
                title=AUDIT_TITLE
            ),
            TypeResponseField(
                at_type=[AUDIT_TITLE]
            ),
            IDResponseField(),
            SearchBaseResponseField(),
            ContextResponseField(),
            AuditMatrixWithFacetsResponseField(
                default_item_types=DEFAULT_ITEM_TYPES
            ),
            NotificationResponseField(),
            FiltersResponseField(),
            TypeOnlyClearFiltersResponseField(),
            DebugQueryResponseField()
        ]
    )
    return fr.render()
