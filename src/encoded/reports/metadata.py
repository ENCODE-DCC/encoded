from collections import defaultdict
from collections import OrderedDict
from itertools import chain
from encoded.cart_view import CartWithElements
from encoded.reports.constants import ANNOTATION_METADATA_COLUMN_TO_FIELDS_MAPPING
from encoded.reports.constants import METADATA_ALLOWED_TYPES
from encoded.reports.constants import METADATA_COLUMN_TO_FIELDS_MAPPING
from encoded.reports.constants import METADATA_AUDIT_TO_AUDIT_COLUMN_MAPPING
from encoded.reports.constants import PUBLICATION_DATA_METADATA_COLUMN_TO_FIELDS_MAPPING
from encoded.reports.constants import SERIES_METADATA_COLUMN_TO_FIELDS_MAPPING
from encoded.reports.constants import NEW_SERIES_METADATA_COLUMN_TO_FIELDS_MAPPING
from encoded.reports.constants import METADATA_SERIES_TYPES
from encoded.reports.csv import CSVGenerator
from encoded.reports.decorators import allowed_types
from encoded.reports.inequalities import map_param_values_to_inequalities
from encoded.reports.inequalities import try_to_evaluate_inequality
from encoded.reports.search import BatchedSearchGenerator
from encoded.reports.serializers import make_experiment_cell
from encoded.reports.serializers import make_file_cell
from encoded.reports.serializers import map_strings_to_booleans_and_ints
from encoded.search_views import search_generator
from encoded.vis_defines import is_file_visualizable
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response
from pyramid.view import view_config
from snosearch.interfaces import EXISTS
from snosearch.interfaces import MUST
from snosearch.interfaces import RANGES
from snosearch.parsers import QueryString
from snovault.util import simple_path_ids


def includeme(config):
    config.add_route('metadata', '/metadata{slash:/?}')
    config.scan(__name__)


def file_matches_file_params(file_, positive_file_param_set):
    # Expects file_param_set where FILES_PREFIX (e.g. 'files.') has been
    # stripped off of key (files.file_type -> file_type)
    # and params with field negation (i.e. file_type!=bigWig)
    # have been filtered out. Param values should be
    # coerced to ints ('2' -> 2) or booleans ('true' -> True)
    # and put into a set for comparison with file values.
    for field, set_of_param_values in positive_file_param_set.items():
        file_value = list(simple_path_ids(file_, field))
        if not file_value:
            return False
        if '*' in set_of_param_values:
            continue
        if not set_of_param_values.intersection(file_value):
            return False
    return True


def some_value_satisfies_inequalities(values, inequalities):
    return all(
        any(
            try_to_evaluate_inequality(inequality, value)
            for value in values
        )
        for inequality in inequalities
    )


def file_satisfies_inequality_constraints(file_, positive_file_inequalities):
    for field, inequalities in positive_file_inequalities.items():
        file_value = list(simple_path_ids(file_, field))
        if not file_value:
            return False
        if not some_value_satisfies_inequalities(file_value, inequalities):
            return False
    return True


def group_audits_by_files_and_type(audits):
    grouped_file_audits = defaultdict(lambda: defaultdict(list))
    grouped_other_audits = defaultdict(list)
    for audit_type, audit_column in METADATA_AUDIT_TO_AUDIT_COLUMN_MAPPING:
        for audit in audits.get(audit_type, []):
            path = audit.get('path')
            if '/files/' in path:
                grouped_file_audits[path][audit_type].append(audit.get('category'))
            else:
                grouped_other_audits[audit_type].append(audit.get('category'))
    return grouped_file_audits, grouped_other_audits


class MetadataReport:

    SEARCH_PATH = '/search/'
    EXCLUDED_COLUMNS = (
        'Restricted',
        'No File Available',
    )
    DEFAULT_PARAMS = [
        ('field', 'audit'),
        ('field', 'files.@id'),
        ('field', 'files.restricted'),
        ('field', 'files.no_file_available'),
        ('field', 'files.file_format'),
        ('field', 'files.file_format_type'),
        ('field', 'files.status'),
        ('field', 'files.assembly'),
        ('limit', 'all'),
    ]
    CONTENT_TYPE = 'text/tsv'
    CONTENT_DISPOSITION = 'attachment; filename="metadata.tsv"'
    FILES_PREFIX = 'files.'

    def __init__(self, request):
        self.request = request
        self.query_string = QueryString(request)
        self.param_list = self.query_string.group_values_by_key()
        self.split_file_filters = {}
        self.positive_file_param_set = {}
        self.positive_file_inequalities = {}
        self.header = []
        self.experiment_column_to_fields_mapping = OrderedDict()
        self.file_column_to_fields_mapping = OrderedDict()
        self.visualizable_only = self.query_string.is_param('option', 'visualizable')
        self.raw_only = self.query_string.is_param('option', 'raw')
        self.csv = CSVGenerator()

    def _get_column_to_fields_mapping(self):
        return METADATA_COLUMN_TO_FIELDS_MAPPING

    def _build_header(self):
        for column in self._get_column_to_fields_mapping():
            if column not in self.EXCLUDED_COLUMNS:
                self.header.append(column)
        for audit, column in METADATA_AUDIT_TO_AUDIT_COLUMN_MAPPING:
            self.header.append(column)
        
    def _split_column_and_fields_by_experiment_and_file(self):
        for column, fields in self._get_column_to_fields_mapping().items():
            if fields[0].startswith(self.FILES_PREFIX):
                self.file_column_to_fields_mapping[column] = [
                    field.replace(self.FILES_PREFIX, '')
                    for field in fields
                ]
            else:
                self.experiment_column_to_fields_mapping[column] = fields

    def _set_split_file_filters(self):
        file_params = self.query_string.get_filters_by_condition(
            key_and_value_condition=lambda k, _: k.startswith(self.FILES_PREFIX)
        )
        self.split_file_filters = self.query_string.split_filters(
            params=file_params
        )

    def _set_positive_file_param_set(self):
        grouped_positive_file_params = self.query_string.group_values_by_key(
            params=self.split_file_filters[MUST] + self.split_file_filters[EXISTS]
        )
        self.positive_file_param_set = {
            k.replace(self.FILES_PREFIX, ''): set(map_strings_to_booleans_and_ints(v))
            for k, v in grouped_positive_file_params.items()
        }

    def _set_positive_file_inequalities(self):
        grouped_positive_file_inequalities = self.query_string.group_values_by_key(
            params=self.split_file_filters[RANGES]
        )
        self.positive_file_inequalities = {
            k.replace(self.FILES_PREFIX, ''): map_param_values_to_inequalities(v)
            for k, v in grouped_positive_file_inequalities.items()
        }

    def _add_positive_file_filters_as_fields_to_param_list(self):
        self.param_list['field'] = self.param_list.get('field', [])
        self.param_list['field'].extend(
            (
                k
                for k, v in self.query_string._get_original_params()
                if k.startswith(self.FILES_PREFIX) and '!' not in k
            )
        )

    def _add_fields_to_param_list(self):
        self.param_list['field'] = self.param_list.get('field', [])
        for column, fields in self._get_column_to_fields_mapping().items():
            self.param_list['field'].extend(fields)
        self._add_positive_file_filters_as_fields_to_param_list()

    def _initialize_at_id_param(self):
        self.param_list['@id'] = self.param_list.get('@id', [])

    def _maybe_add_cart_elements_to_param_list(self):
        # Don't need to limit max_cart_elements here since
        # search is batched.
        cart = CartWithElements(
            self.request,
            max_cart_elements=None
        )
        self.param_list['@id'].extend(cart.elements)
        self.param_list.pop('cart', None)

    def _get_json_elements_or_empty_list(self):
        try:
            return self.request.json.get('elements', [])
        except ValueError:
            return []

    def _maybe_add_json_elements_to_param_list(self):
        self.param_list['@id'].extend(
            self._get_json_elements_or_empty_list()
        )

    def _get_field_params(self):
        return [
            ('field', p)
            for p in self.param_list.get('field', [])
        ]

    def _get_at_id_params(self):
        return [
            ('@id', p)
            for p in self.param_list.get('@id', [])
        ]

    def _get_default_params(self):
        return self.DEFAULT_PARAMS

    def _build_query_string(self):
        self.query_string.drop('limit')
        self.query_string.drop('option')
        self.query_string.extend(
            self._get_default_params()
            + self._get_field_params()
            + self._get_at_id_params()
        )

    def _get_search_path(self):
        return self.SEARCH_PATH

    def _build_new_request(self):
        self._build_query_string()
        request = self.query_string.get_request_with_new_query_string()
        request.path_info = self._get_search_path()
        return request

    def _get_search_results_generator(self):
        return BatchedSearchGenerator(
            self._build_new_request()
        ).results()

    def _should_not_report_file(self, file_):
        conditions = [
            not file_matches_file_params(file_, self.positive_file_param_set),
            not file_satisfies_inequality_constraints(file_, self.positive_file_inequalities),
            self.visualizable_only and not is_file_visualizable(file_),
            self.raw_only and file_.get('assembly'),
            file_.get('restricted'),
            file_.get('no_file_available'),
        ]
        return any(conditions)

    def _get_experiment_data(self, experiment):
        return {
            column: make_experiment_cell(fields, experiment)
            for column, fields in self.experiment_column_to_fields_mapping.items()
        }

    def _get_file_data(self, file_):
        file_['href'] = self.request.host_url + file_['href']
        return {
            column: make_file_cell(fields, file_)
            for column, fields in self.file_column_to_fields_mapping.items()
        }

    def _get_audit_data(self, grouped_audits_for_file, grouped_other_audits):
        return {
            audit_column: ', '.join(
                set(
                    grouped_audits_for_file.get(audit_type, [])
                    + grouped_other_audits.get(audit_type, [])
                )
            ) for audit_type, audit_column in METADATA_AUDIT_TO_AUDIT_COLUMN_MAPPING
        }

    def _output_sorted_row(self, experiment_data, file_data):
        row = []
        for column in self.header:
            row.append(
                file_data.get(
                    column,
                    experiment_data.get(column)
                )
            )
        return row

    def _generate_rows(self):
        yield self.csv.writerow(self.header)
        for experiment in self._get_search_results_generator():
            if not experiment.get('files', []):
                continue
            grouped_file_audits, grouped_other_audits = group_audits_by_files_and_type(
                experiment.get('audit', {})
            )
            experiment_data = self._get_experiment_data(experiment)
            for file_ in experiment.get('files', []):
                if self._should_not_report_file(file_):
                    continue
                file_data = self._get_file_data(file_)
                audit_data = self._get_audit_data(
                    grouped_file_audits.get(file_.get('@id'), {}),
                    grouped_other_audits
                )
                file_data.update(audit_data)
                yield self.csv.writerow(
                    self._output_sorted_row(experiment_data, file_data)
                )

    def _validate_request(self):
        type_params = self.param_list.get('type', [])
        if len(type_params) != 1:
            raise HTTPBadRequest(explanation='URL requires one "type" parameter.')
        return True

    def _initialize_report(self):
        self._build_header()
        self._split_column_and_fields_by_experiment_and_file()
        self._set_split_file_filters()
        self._set_positive_file_param_set()
        self._set_positive_file_inequalities()

    def _build_params(self):
        self._add_fields_to_param_list()
        self._initialize_at_id_param()
        self._maybe_add_cart_elements_to_param_list()
        self._maybe_add_json_elements_to_param_list()

    def generate(self):
        self._validate_request()
        self._initialize_report()
        self._build_params()
        return Response(
             content_type=self.CONTENT_TYPE,
             app_iter=self._generate_rows(),
             content_disposition=self.CONTENT_DISPOSITION,
        )


class AnnotationMetadataReport(MetadataReport):

    def _get_column_to_fields_mapping(self):
        return ANNOTATION_METADATA_COLUMN_TO_FIELDS_MAPPING


class PublicationDataMetadataReport(MetadataReport):
    '''
    PublicationData objects don't embed file attributes so
    we have to get file metadata with separate search request.
    We try to get all the file metadata together in a batched request
    instead of making a request for every file. This requires some
    extra machinery compared to normal MetdataReport.
    '''

    DEFAULT_PARAMS = [
        ('limit', 'all'),
        ('field', 'files')
    ]
    DEFAULT_FILE_PARAMS = [
        ('type', 'File'),
        ('limit', 'all'),
        ('field', '@id'),
        ('field', 'href'),
        ('field', 'restricted'),
        ('field', 'no_file_available'),
        ('field', 'file_format'),
        ('field', 'file_format_type'),
        ('field', 'status'),
        ('field', 'assembly'),
    ]

    def __init__(self, request):
        super().__init__(request)
        self.file_query_string = QueryString(request)
        self.file_params = []
        self.file_at_ids = []

    # Overrides parent.
    def _get_column_to_fields_mapping(self):
        return PUBLICATION_DATA_METADATA_COLUMN_TO_FIELDS_MAPPING

    # Overrides parent.
    def _build_header(self):
        for column in self._get_column_to_fields_mapping():
            if column not in self.EXCLUDED_COLUMNS:
                self.header.append(column)

    # Overrides parent.
    def _add_fields_to_param_list(self):
        self.param_list['field'] = []
        for column, fields in self.experiment_column_to_fields_mapping.items():
            self.param_list['field'].extend(fields)

    def _add_default_file_params_to_file_params(self):
        self.file_params.extend(self.DEFAULT_FILE_PARAMS)

    def _add_report_file_fields_to_file_params(self):
        for column, fields in self.file_column_to_fields_mapping.items():
            self.file_params.extend(
                [
                    ('field', field)
                    for field in fields
                ]
            )

    def _convert_experiment_params_to_file_params(self):
        return [
            (k.replace(self.FILES_PREFIX, ''), v)
            for k, v in self.query_string._get_original_params()
            if k.startswith(self.FILES_PREFIX)
        ]

    def _add_experiment_file_filters_as_fields_to_file_params(self):
        self.file_params.extend(
            ('field', k)
            for k, v in self._convert_experiment_params_to_file_params()
        )

    def _add_experiment_file_filters_to_file_params(self):
        self.file_params.extend(
            self._convert_experiment_params_to_file_params()
        )

    def _build_file_params(self):
        self._add_default_file_params_to_file_params()
        self._add_report_file_fields_to_file_params()
        self._add_experiment_file_filters_as_fields_to_file_params()
        self._add_experiment_file_filters_to_file_params()

    def _filter_file_params_from_query_string(self):
        self.query_string.params = [
            (k, v)
            for k, v in self.query_string.params
            if not k.startswith(self.FILES_PREFIX)
        ]

    # Overrides parent.
    def _build_params(self):
        super()._build_params()
        self._build_file_params()
        self._filter_file_params_from_query_string()

    def _get_at_id_file_params(self):
        return [
            ('@id', file_at_id)
            for file_at_id in self.file_at_ids
        ]

    def _build_new_file_request(self):
        self.file_query_string.params = (
            self.file_params + self._get_at_id_file_params()
        )
        request = self.file_query_string.get_request_with_new_query_string()
        request.path_info = self._get_search_path()
        return request

    def _get_file_search_results_generator(self):
        request = self._build_new_file_request()
        bsg = BatchedSearchGenerator(request)
        return bsg.results()

    # Overrides parent.
    def _generate_rows(self):
        yield self.csv.writerow(self.header)
        for experiment in self._get_search_results_generator():
            self.file_at_ids = experiment.get('files', [])
            if not self.file_at_ids:
                continue
            experiment_data = self._get_experiment_data(experiment)
            for file_ in self._get_file_search_results_generator():
                if self._should_not_report_file(file_):
                    continue
                file_data = self._get_file_data(file_)
                yield self.csv.writerow(
                    self._output_sorted_row(experiment_data, file_data)
                )


class SeriesMetadataReport(MetadataReport):

    DEFAULT_PARAMS = [
        ('limit', 'all'),
        ('field', 'related_datasets.files.@id'),
        ('field', 'related_datasets.files.href'),
        ('field', 'related_datasets.files.restricted'),
        ('field', 'related_datasets.files.no_file_available'),
        ('field', 'related_datasets.files.file_format'),
        ('field', 'related_datasets.files.file_format_type'),
        ('field', 'related_datasets.files.preferred_default'),
        ('field', 'related_datasets.files.status'),
        ('field', 'related_datasets.files.assembly'),
        ('field', 'related_datasets.files.related_datasets'),
    ]
    FILES_PREFIX = 'related_datasets.files.'

    def _get_column_to_fields_mapping(self):
        return SERIES_METADATA_COLUMN_TO_FIELDS_MAPPING

    def _generate_rows(self):
        yield self.csv.writerow(self.header)
        for series in self._get_search_results_generator():
            related_datasets = series.get('related_datasets', [])
            if not related_datasets:
                continue
            series_data = self._get_experiment_data(series)
            for related_dataset in related_datasets:
                files = related_dataset.get('files', [])
                if not files:
                    continue
                for file_ in files:
                    if self._should_not_report_file(file_):
                        continue
                    file_data = self._get_file_data(file_)
                    yield self.csv.writerow(
                        self._output_sorted_row(series_data, file_data)
                    )


class NewSeriesMetadataReport():

    _multireports = [
        SeriesMetadataReport,
        MetadataReport,
    ]

    def __init__(self, request):
        self.request = request

    def _get_column_to_fields_mapping(self):
        return NEW_SERIES_METADATA_COLUMN_TO_FIELDS_MAPPING

    def _bind_custom_methods(self, instance):
        # Use common headers/columns for all reports.
        instance._get_column_to_fields_mapping = self._get_column_to_fields_mapping
        return instance

    def _skip_header(self, generator):
        next(generator)
        yield from generator

    def _skip_headers(self, reports):
        # Use header line from first report, skip the rest.
        for i, report in enumerate(reports):
            if i != 0:
                yield self._skip_header(report)
            else:
                yield report

    def generate(self):
        reports = (
            self._bind_custom_methods(
                report(self.request)
            ).generate().app_iter
            for report in self._multireports
        )
        responses = self._skip_headers(reports)
        return Response(
             content_type=self._multireports[0].CONTENT_TYPE,
             app_iter=chain(*responses),
             content_disposition=self._multireports[0].CONTENT_DISPOSITION,
        )


def _get_metadata(context, request):
    metadata_report = MetadataReport(request)
    return metadata_report.generate()


def _get_annotation_metadata(context, request):
    annotation_metadata_report = AnnotationMetadataReport(request)
    return annotation_metadata_report.generate()


def _get_publication_data_metadata(context, request):
    publication_data_metadata_report = PublicationDataMetadataReport(request)
    return publication_data_metadata_report.generate()


def _get_series_metadata(context, request):
    new_series_metadata_report = NewSeriesMetadataReport(request)
    return new_series_metadata_report.generate()


def metadata_report_factory(context, request):
    qs = QueryString(request)
    specified_type = qs.get_one_value(
            params=qs.get_type_filters()
    )
    if specified_type == 'Annotation':
        return _get_annotation_metadata(context, request)
    elif specified_type == 'PublicationData':
        return _get_publication_data_metadata(context, request)
    elif specified_type in METADATA_SERIES_TYPES:
        return _get_series_metadata(context, request)
    else:
        return _get_metadata(context, request)


@view_config(route_name='metadata', request_method=['GET', 'POST'])
@allowed_types(METADATA_ALLOWED_TYPES)
def metadata_tsv(context, request):
    return metadata_report_factory(context, request)
