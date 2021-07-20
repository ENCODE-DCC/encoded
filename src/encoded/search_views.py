from pyramid.view import view_config

from encoded.cart_view import CartWithElements
from encoded.genomic_data_service import GenomicDataService
from encoded.searches.defaults import DEFAULT_ITEM_TYPES
from encoded.searches.defaults import RESERVED_KEYS
from encoded.searches.defaults import TOP_HITS_ITEM_TYPES
from encoded.searches.fields import CartSearchResponseField
from encoded.searches.fields import CartSearchWithFacetsResponseField
from encoded.searches.fields import CartReportWithFacetsResponseField
from encoded.searches.fields import CartMatrixWithFacetsResponseField
from encoded.searches.fields import CartFiltersResponseField
from encoded.searches.fields import ClearFiltersResponseFieldWithCarts
from encoded.searches.fields import TypeOnlyClearFiltersResponseFieldWithCarts
from encoded.searches.interfaces import RNA_CLIENT
from encoded.searches.interfaces import RNA_EXPRESSION

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
from snovault.elasticsearch.searches.fields import BasicSearchWithoutFacetsResponseField
from snovault.elasticsearch.searches.fields import BasicReportWithFacetsResponseField
from snovault.elasticsearch.searches.fields import BasicReportWithoutFacetsResponseField
from snovault.elasticsearch.searches.fields import CachedFacetsResponseField
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
    config.add_route('encyclopedia', '/encyclopedia{slash:/?}')
    config.add_route('encode_software', '/encode-software{slash:/?}')
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
    config.add_route('rnaget-autocomplete', '/rnaget-autocomplete{slash:/?}')
    config.add_route('rnaget-search', '/rnaget-search{slash:/?}')
    config.add_route('rnaget-report', '/rnaget-report{slash:/?}')
    config.scan(__name__)


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
                default_item_types=DEFAULT_ITEM_TYPES,
                reserved_keys=RESERVED_KEYS,
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
                default_item_types=DEFAULT_ITEM_TYPES,
                reserved_keys=RESERVED_KEYS,
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


@view_config(route_name='encyclopedia', request_method='GET', permission='search')
def encyclopedia(context, request):
    # Note the order of rendering matters for some fields, e.g. AllResponseField and
    # NotificationResponseField depend on results from BasicSearchWithFacetsResponseField.
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(request)
        },
        response_fields=[
            TitleResponseField(
                title="Encyclopedia"
            ),
            TypeResponseField(
                at_type=["Encyclopedia"]
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


@view_config(route_name='encode_software', request_method='GET', permission='search')
def encode_software(context, request):
    # Note the order of rendering matters for some fields, e.g. AllResponseField and
    # NotificationResponseField depend on results from BasicSearchWithFacetsResponseField.
    fr = FieldedResponse(
        _meta={
            'params_parser': ParamsParser(request)
        },
        response_fields=[
            TitleResponseField(
                title="Software"
            ),
            TypeResponseField(
                at_type=["EncodeSoftware"]
            ),
            IDResponseField(),
            ContextResponseField(),
            BasicSearchWithFacetsResponseField(
                default_item_types=DEFAULT_ITEM_TYPES,
                reserved_keys=RESERVED_KEYS,
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
                default_item_types=DEFAULT_ITEM_TYPES,
                reserved_keys=RESERVED_KEYS,
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
                default_item_types=DEFAULT_ITEM_TYPES,
                reserved_keys=RESERVED_KEYS,
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
                default_item_types=DEFAULT_ITEM_TYPES,
                reserved_keys=RESERVED_KEYS,
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
                reserved_keys=RESERVED_KEYS,
            )
        ]
    )
    return fgr.render()


def rna_expression_search_generator(request):
    '''
    For internal use (no view). Like search_quick but returns raw generator
    of search hits in @graph field.
    '''
    rna_client = request.registry[RNA_CLIENT]
    fgr = FieldedGeneratorResponse(
        _meta={
            'params_parser': ParamsParser(request)
        },
        response_fields=[
            BasicSearchResponseField(
                client=rna_client,
                default_item_types=[
                    RNA_EXPRESSION
                ],
                reserved_keys=RESERVED_KEYS,
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
            BasicReportWithFacetsResponseField(
                default_item_types=DEFAULT_ITEM_TYPES,
                reserved_keys=RESERVED_KEYS,
            ),
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
                default_item_types=DEFAULT_ITEM_TYPES,
                reserved_keys=RESERVED_KEYS,
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
                default_item_types=DEFAULT_ITEM_TYPES,
                reserved_keys=RESERVED_KEYS,
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
                reserved_keys=RESERVED_KEYS,
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
            MissingMatrixWithFacetsResponseField(
                default_item_types=DEFAULT_ITEM_TYPES,
                matrix_definition_name='chip_seq_matrix',
                reserved_keys=RESERVED_KEYS,
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
                matrix_definition_name='reference_epigenome',
                reserved_keys=RESERVED_KEYS,
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
                matrix_definition_name='entex',
                reserved_keys=RESERVED_KEYS,
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
                matrix_definition_name='mouse_development',
                reserved_keys=RESERVED_KEYS,
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
                matrix_definition_name='encore_matrix',
                reserved_keys=RESERVED_KEYS,
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
                matrix_definition_name='encore_rna_seq_matrix',
                reserved_keys=RESERVED_KEYS,
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
                matrix_definition_name=SUMMARY_MATRIX,
                reserved_keys=RESERVED_KEYS,
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
                default_item_types=DEFAULT_ITEM_TYPES,
                reserved_keys=RESERVED_KEYS,
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
                reserved_keys=RESERVED_KEYS,
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
                default_item_types=DEFAULT_ITEM_TYPES,
                cart=CartWithElements(request),
                reserved_keys=RESERVED_KEYS,
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
                reserved_keys=RESERVED_KEYS,
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
                default_item_types=TOP_HITS_ITEM_TYPES,
                reserved_keys=RESERVED_KEYS,
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
    data_service = GenomicDataService(context.registry, request)
    return data_service.rna_get()


@view_config(route_name='rnaget-autocomplete', request_method='GET', permission='search')
def rnaget_autocomplete(context, request):
    data_service = GenomicDataService(context.registry, request)
    return data_service.rna_get_autocomplete()


@view_config(route_name='rnaget-search', request_method='GET', permission='search')
def rnaget_search(context, request):
    # Note the order of rendering matters for some fields, e.g. AllResponseField and
    # NotificationResponseField depend on results from BasicSearchWithFacetsResponseField.
    rna_client = request.registry[RNA_CLIENT]
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
            CachedFacetsResponseField(
                client=rna_client,
                default_item_types=[
                    RNA_EXPRESSION
                ],
                reserved_keys=RESERVED_KEYS,
            ),
            BasicSearchWithoutFacetsResponseField(
                client=rna_client,
                default_item_types=[
                    RNA_EXPRESSION
                ],
                reserved_keys=RESERVED_KEYS,
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


@view_config(route_name='rnaget-report', request_method='GET', permission='search')
def rnaget_report(context, request):
    rna_client = request.registry[RNA_CLIENT]
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
            CachedFacetsResponseField(
                client=rna_client,
                default_item_types=[
                    RNA_EXPRESSION
                ],
                reserved_keys=RESERVED_KEYS,
            ),
            BasicReportWithoutFacetsResponseField(
                client=rna_client,
                default_item_types=[
                    RNA_EXPRESSION
                ],
                reserved_keys=RESERVED_KEYS,
            ),
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
