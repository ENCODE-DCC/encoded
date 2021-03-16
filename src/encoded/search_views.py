from pyramid.view import view_config

from .genomic_data_service import GenomicDataService

from encoded.cart_view import CartWithElements
from encoded.searches.fields import CartSearchResponseField
from encoded.searches.fields import CartSearchWithFacetsResponseField
from encoded.searches.fields import CartReportWithFacetsResponseField
from encoded.searches.fields import CartMatrixWithFacetsResponseField
from encoded.searches.fields import CartFiltersResponseField
from encoded.searches.fields import ClearFiltersResponseFieldWithCarts
from encoded.searches.fields import TypeOnlyClearFiltersResponseFieldWithCarts

from snovault.elasticsearch.searches.interfaces import AUDIT_TITLE
from snovault.elasticsearch.searches.interfaces import MATRIX_TITLE
from snovault.elasticsearch.searches.interfaces import REPORT_TITLE
from snovault.elasticsearch.searches.interfaces import SEARCH_TITLE
from snovault.elasticsearch.searches.interfaces import SUMMARY_MATRIX
from snovault.elasticsearch.searches.interfaces import SUMMARY_TITLE
from snovault.elasticsearch.searches.fields import AuditMatrixWithFacetsResponseField
from snovault.elasticsearch.searches.fields import AllResponseField
from snovault.elasticsearch.searches.fields import BasicMatrixWithFacetsResponseField
from snovault.elasticsearch.searches.fields import MissingMatrixWithFacetsResponseField
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
from snovault.elasticsearch.searches.fields import RawTopHitsResponseField
from snovault.elasticsearch.searches.fields import SearchBaseResponseField
from snovault.elasticsearch.searches.fields import SortResponseField
from snovault.elasticsearch.searches.fields import TitleResponseField
from snovault.elasticsearch.searches.fields import TypeOnlyClearFiltersResponseField
from snovault.elasticsearch.searches.fields import TypeResponseField
from snovault.elasticsearch.searches.parsers import ParamsParser
from snovault.elasticsearch.searches.responses import FieldedGeneratorResponse
from snovault.elasticsearch.searches.responses import FieldedResponse


def includeme(config):
    config.add_route('search', '/search{slash:/?}')
    config.add_route('series_search', '/series-search{slash:/?}')
    config.add_route('searchv2_raw', '/searchv2_raw{slash:/?}')
    config.add_route('searchv2_quick', '/searchv2_quick{slash:/?}')
    config.add_route('report', '/report{slash:/?}')
    config.add_route('matrixv2_raw', '/matrixv2_raw{slash:/?}')
    config.add_route('matrix', '/matrix{slash:/?}')
    config.add_route('reference-epigenome-matrix', '/reference-epigenome-matrix{slash:/?}')
    config.add_route('entex-matrix', '/entex-matrix{slash:/?}')
    config.add_route('sescc-stem-cell-matrix', '/sescc-stem-cell-matrix{slash:/?}')
    config.add_route('chip-seq-matrix', '/chip-seq-matrix{slash:/?}')
    config.add_route('mouse-development-matrix', '/mouse-development-matrix{slash:/?}')
    config.add_route('encore-matrix', '/encore-matrix{slash:/?}')
    config.add_route('encore-rna-seq-matrix', '/encore-rna-seq-matrix{slash:/?}')
    config.add_route('summary', '/summary{slash:/?}')
    config.add_route('audit', '/audit{slash:/?}')
    config.add_route('cart-search', '/cart-search{slash:/?}')
    config.add_route('cart-report', '/cart-report{slash:/?}')
    config.add_route('cart-matrix', '/cart-matrix{slash:/?}')
    config.add_route('top-hits-raw', '/top-hits-raw{slash:/?}')
    config.add_route('top-hits', '/top-hits{slash:/?}')
    config.add_route('rnaget', '/rnaget{slash:/?}')
    config.scan(__name__)


DEFAULT_ITEM_TYPES = [
    'Analysis',
    'AntibodyLot',
    'Award',
    'Biosample',
    'BiosampleType',
    'Dataset',
    'Document',
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


TOP_HITS_ITEM_TYPES = [
    'AntibodyLot',
    'Award',
    'Biosample',
    'BiosampleType',
    'Annotation',
    'Experiment',
    'Document',
    'HumanDonor',
    'FlyDonor',
    'WormDonor',
    'MouseDonor',
    'GeneticModification',
    'Page',
    'Pipeline',
    'Publication',
    'Software',
    'Gene',
    'Target',
    'File',
    'Lab',
    'GeneSilencingSeries',
    'ReferenceEpigenome',
    'OrganismDevelopmentSeries',
    'TreatmentTimeSeries',
    'ReplicationTimingSeries',
    'MatchedSet',
    'TreatmentConcentrationSeries',
    'AggregateSeries',
    'FunctionalCharacterizationExperiment',
    'TransgenicEnhancerExperiment',
    'Reference',
    'PublicationData',
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


@view_config(route_name='series_search', request_method='GET', permission='search')
def series_search(context, request):
    # Note the order of rendering matters for some fields, e.g. AllResponseField and
    # NotificationResponseField depend on results from BasicSearchWithFacetsResponseField.
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(request)
        },
        response_fields=[
            TitleResponseField(
                title="Series search"
            ),
            TypeResponseField(
                at_type=["SeriesSearch"]
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


def search_generator(request):
    '''
    For internal use (no view). Like search_quick but returns raw generator
    of search hits in @graph field.
    '''
    fgr = FieldedGeneratorResponse(
        _meta={
            'params_parser': ParamsParser(request)
        },
        response_fields=[
            BasicSearchResponseField(
                default_item_types=DEFAULT_ITEM_TYPES
            )
        ]
    )
    return fgr.render()


def cart_search_generator(request):
    '''
    For internal use (no view). Like search_quick but returns raw generator
    of cart search hits in @graph field.
    '''
    fgr = FieldedGeneratorResponse(
        _meta={
            'params_parser': ParamsParser(request)
        },
        response_fields=[
            CartSearchResponseField(
                default_item_types=DEFAULT_ITEM_TYPES,
                cart=CartWithElements(request),
            )
        ]
    )
    return fgr.render()


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


@view_config(route_name='matrix', request_method='GET', permission='search')
def matrix(context, request):
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(request)
        },
        response_fields=[
            TitleResponseField(
                title=MATRIX_TITLE
            ),
            TypeResponseField(
                at_type=[MATRIX_TITLE]
            ),
            IDResponseField(),
            SearchBaseResponseField(),
            ContextResponseField(),
            BasicMatrixWithFacetsResponseField(
                default_item_types=DEFAULT_ITEM_TYPES
            ),
            NotificationResponseField(),
            FiltersResponseField(),
            TypeOnlyClearFiltersResponseField(),
            DebugQueryResponseField()
        ]
    )
    return fr.render()


@view_config(route_name='sescc-stem-cell-matrix', request_method='GET', permission='search')
def sescc_stem_cell_matrix(context, request):
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(request)
        },
        response_fields=[
            TitleResponseField(
                title='Stem Cell Development Matrix (SESCC)'
            ),
            TypeResponseField(
                at_type=['SESCCStemCellMatrix']
            ),
            IDResponseField(),
            SearchBaseResponseField(),
            ContextResponseField(),
            BasicMatrixWithFacetsResponseField(
                default_item_types=DEFAULT_ITEM_TYPES,
                matrix_definition_name='sescc_stem_cell_matrix',
            ),
            NotificationResponseField(),
            FiltersResponseField(),
            TypeOnlyClearFiltersResponseField(),
            DebugQueryResponseField()
        ]
    )
    return fr.render()


@view_config(route_name='chip-seq-matrix', request_method='GET', permission='search')
def chip_seq_matrix(context, request):
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(request)
        },
        response_fields=[
            TitleResponseField(
                title='ChIP-seq Matrix'
            ),
            TypeResponseField(
                at_type=['ChipSeqMatrix']
            ),
            IDResponseField(),
            SearchBaseResponseField(),
            ContextResponseField(),
            BasicMatrixWithFacetsResponseField(
                default_item_types=DEFAULT_ITEM_TYPES,
                matrix_definition_name='chip_seq_matrix',
            ),
            NotificationResponseField(),
            FiltersResponseField(),
            TypeOnlyClearFiltersResponseField(),
            DebugQueryResponseField()
        ]
    )
    return fr.render()


@view_config(route_name='reference-epigenome-matrix', request_method='GET', permission='search')
def reference_epigenome_matrix(context, request):
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(request)
        },
        response_fields=[
            TitleResponseField(
                title='Reference Epigenome Matrix'
            ),
            TypeResponseField(
                at_type=['ReferenceEpigenomeMatrix']
            ),
            IDResponseField(),
            SearchBaseResponseField(),
            ContextResponseField(),
            BasicMatrixWithFacetsResponseField(
                default_item_types=DEFAULT_ITEM_TYPES,
                matrix_definition_name='reference_epigenome'
            ),
            NotificationResponseField(),
            FiltersResponseField(),
            TypeOnlyClearFiltersResponseField(),
            DebugQueryResponseField()
        ]
    )
    return fr.render()


@view_config(route_name='entex-matrix', request_method='GET', permission='search')
def entex_matrix(context, request):
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(request)
        },
        response_fields=[
            TitleResponseField(
                title='Epigenomes from four individuals (ENTEx)'
            ),
            TypeResponseField(
                at_type=['EntexMatrix']
            ),
            IDResponseField(),
            SearchBaseResponseField(),
            ContextResponseField(),
            MissingMatrixWithFacetsResponseField(
                default_item_types=DEFAULT_ITEM_TYPES,
                matrix_definition_name='entex'
            ),
            NotificationResponseField(),
            FiltersResponseField(),
            TypeOnlyClearFiltersResponseField(),
            DebugQueryResponseField()
        ]
    )
    return fr.render()


@view_config(route_name='mouse-development-matrix', request_method='GET', permission='search')
def mouse_development(context, request):
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(request)
        },
        response_fields=[
            TitleResponseField(
                title='Mouse Development Matrix'
            ),
            TypeResponseField(
                at_type=['MouseDevelopmentMatrix']
            ),
            IDResponseField(),
            SearchBaseResponseField(),
            ContextResponseField(),
            BasicMatrixWithFacetsResponseField(
                default_item_types=DEFAULT_ITEM_TYPES,
                matrix_definition_name='mouse_development'
            ),
            NotificationResponseField(),
            FiltersResponseField(),
            TypeOnlyClearFiltersResponseField(),
            DebugQueryResponseField()
        ]
    )
    return fr.render()


@view_config(route_name='encore-matrix', request_method='GET', permission='search')
def encore_matrix(context, request):
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(request)
        },
        response_fields=[
            TitleResponseField(
                title='ENCORE Matrix'
            ),
            TypeResponseField(
                at_type=['EncoreMatrix']
            ),
            IDResponseField(),
            SearchBaseResponseField(),
            ContextResponseField(),
            BasicMatrixWithFacetsResponseField(
                default_item_types=DEFAULT_ITEM_TYPES,
                matrix_definition_name='encore_matrix'
            ),
            NotificationResponseField(),
            FiltersResponseField(),
            TypeOnlyClearFiltersResponseField(),
            DebugQueryResponseField()
        ]
    )
    return fr.render()


@view_config(route_name='encore-rna-seq-matrix', request_method='GET', permission='search')
def encore_rna_seq_matrix(context, request):
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(request)
        },
        response_fields=[
            TitleResponseField(
                title='ENCORE RNA-seq Matrix'
            ),
            TypeResponseField(
                at_type=['EncoreRnaSeqMatrix']
            ),
            IDResponseField(),
            SearchBaseResponseField(),
            ContextResponseField(),
            MissingMatrixWithFacetsResponseField(
                default_item_types=DEFAULT_ITEM_TYPES,
                matrix_definition_name='encore_rna_seq_matrix'
            ),
            NotificationResponseField(),
            FiltersResponseField(),
            TypeOnlyClearFiltersResponseField(),
            DebugQueryResponseField()
        ]
    )
    return fr.render()


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
                matrix_definition_name=SUMMARY_MATRIX
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


@view_config(route_name='cart-search', request_method='GET', permission='search')
def cart_search(context, request):
    '''
    Like search but takes cart params.
    '''
    # Note the order of rendering matters for some fields, e.g. AllResponseField and
    # NotificationResponseField depend on results from CartSearchWithFacetsResponseField.
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(request)
        },
        response_fields=[
            TitleResponseField(
                title='Cart search'
            ),
            TypeResponseField(
                at_type=[SEARCH_TITLE]
            ),
            IDResponseField(),
            ContextResponseField(),
            CartSearchWithFacetsResponseField(
                default_item_types=DEFAULT_ITEM_TYPES,
                cart=CartWithElements(request),
            ),
            AllResponseField(),
            NotificationResponseField(),
            CartFiltersResponseField(),
            ClearFiltersResponseFieldWithCarts(),
            ColumnsResponseField(),
            SortResponseField(),
            DebugQueryResponseField()
        ]
    )
    return fr.render()


@view_config(route_name='cart-report', request_method='GET', permission='search')
def cart_report(context, request):
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(request)
        },
        response_fields=[
            TitleResponseField(
                title='Cart report'
            ),
            TypeResponseField(
                at_type=[REPORT_TITLE]
            ),
            IDResponseField(),
            ContextResponseField(),
            CartReportWithFacetsResponseField(
                cart=CartWithElements(request)
            ),
            AllResponseField(),
            NotificationResponseField(),
            CartFiltersResponseField(),
            TypeOnlyClearFiltersResponseFieldWithCarts(),
            ColumnsResponseField(),
            NonSortableResponseField(),
            SortResponseField(),
            DebugQueryResponseField()
        ]
    )
    return fr.render()


@view_config(route_name='cart-matrix', request_method='GET', permission='search')
def cart_matrix(context, request):
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(request)
        },
        response_fields=[
            TitleResponseField(
                title='Cart matrix'
            ),
            TypeResponseField(
                at_type=[MATRIX_TITLE]
            ),
            IDResponseField(),
            SearchBaseResponseField(
                search_base='/cart-search/'
            ),
            ContextResponseField(),
            CartMatrixWithFacetsResponseField(
                default_item_types=DEFAULT_ITEM_TYPES,
                cart=CartWithElements(request),
            ),
            NotificationResponseField(),
            CartFiltersResponseField(),
            TypeOnlyClearFiltersResponseFieldWithCarts(),
            DebugQueryResponseField()
        ]
    )
    return fr.render()


@view_config(route_name='top-hits-raw', request_method='GET', permission='search')
def top_hits_raw(context, request):
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(request)
        },
        response_fields=[
            RawTopHitsResponseField(
                default_item_types=TOP_HITS_ITEM_TYPES
            )
        ]
    )
    return fr.render()


@view_config(route_name='top-hits', request_method='GET', permission='search')
def top_hits(context, request):
    fr = FieldedResponse(
        response_fields=[
            TypeResponseField(
                at_type=['TopHitsSearch']
            )
        ]
    )
    return fr.render()


@view_config(route_name='rnaget', request_method='GET', permission='search')
def rnaget(context, request):
    genes = request.params.get('genes')
    units = request.params.get('units', 'tpm')
    sort  = request.params.get('sort')
    page  = request.params.get('page')

    filters = {
        'assayType': request.params.get('assayType'),
        'annotation': request.params.get('annotation')
    }

    filters_data = [{'field': 'type', 'term': 'Rna Get', 'remove': '/rnaget'}]

    for f in filters:
        if filters.get(f):
            query_string = []

            for param in request.params:
                if param != f:
                    query_string.append(f'{param}={request.params.get(param)}')

            filters_data.append({
                'field': f,
                'term': filters[f],
                'remove': f'{request.path}?{"&".join(query_string)}'
            })

    # table JS component orders columns by "the position" in the hash map
    columns = {
        'featureID': {'title': 'Feature ID'},
        'tpm': {'title': 'Counts (TPM)'},
        'fpkm': {'title': 'Counts (FPKM)'},
        'assayType': {'title': 'Assay (RNA SubType)'},
        'libraryPrepProtocol': {'title': 'Experiment'},
        'expressionID': {'title': 'File'},
        'annotation': {'title': 'Genome Annotation'}
    }

    if units == 'tpm':
        columns.pop('fpkm')
    elif units == 'fpkm':
        columns.pop('tpm')

    data_service = GenomicDataService(context.registry, default_search='ENSG00000088320.3')
    expressions, facets, total = data_service.rna_get(genes, sort, units, page, filters)

    facets_data = []
    for facet in facets:
        facet_data = {
            'field': facet,
            'title': columns[facet]['title'],
            'terms': [{'key': term[0], 'doc_count': term[1]} for term in facets[facet]],
            'type': 'terms'
        }
        facet_data['total'] = sum([term['doc_count'] for term in facet_data['terms']])
        facets_data.append(facet_data)

    # this forces the current components to show an empty state
    if total == 0:
        for facet in facets_data:
            facet['total'] += 1

    response = {
        'title': 'RNA Get',
        '@type': ['rnaseq'],
        '@id': request.path_qs,
        'total': total,
        'non_sortable': ['annotation'],
        'columns': columns,
        'filters': filters_data,
        'facets': facets_data,
        '@graph': expressions
    }

    if sort:
        response['sort'] = {}

        order = 'asc'
        if sort[0] == '-':
            order = 'desc'
            sort = sort[1:]

        response['sort'][sort] = {
            'order': order,
            'unmapped_type': 'keyword'
        }

    return response
