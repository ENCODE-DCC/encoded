import csv

from collections import defaultdict
from collections import OrderedDict
from functools import wraps
from encoded.reports.constants import ANNOTATION_METADATA_COLUMN_TO_FIELDS_MAPPING
from encoded.reports.constants import METADATA_ALLOWED_TYPES
from encoded.reports.constants import METADATA_COLUMN_TO_FIELDS_MAPPING
from encoded.reports.constants import METADATA_AUDIT_TO_AUDIT_COLUMN_MAPPING
from encoded.reports.constants import PUBLICATION_DATA_METADATA_COLUMN_TO_FIELDS_MAPPING
from encoded.search_views import search_generator
from encoded.vis_defines import is_file_visualizable
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response
from pyramid.view import view_config
from snovault.elasticsearch.searches.parsers import QueryString
from snovault.util import simple_path_ids


def includeme(config):
    config.add_route('metadata', '/metadata{slash:/?}')
    config.scan(__name__)


def allowed_types(types):
    def decorator(func):
        @wraps(func)
        def wrapper(context, request):
            qs = QueryString(request)
            type_filters = qs.get_type_filters()
            if len(type_filters) != 1:
                raise HTTPBadRequest(
                    explanation='URL requires one type parameter.'
                )
            if type_filters[0][1] not in types:
                raise HTTPBadRequest(
                    explanation=f'{type_filters[0][1]} not a valid type for endpoint.'
                )
            return func(context, request)
        return wrapper
    return decorator


def make_experiment_cell(paths, experiment):
    last = []
    for path in paths:
        cell_value = []
        for value in simple_path_ids(experiment, path):
            if str(value) not in cell_value:
                cell_value.append(str(value))
        if last and cell_value:
            last = [
                v + ' ' + cell_value[0]
                for v in last
            ]
        else:
            last = cell_value
    return ', '.join(set(last))


def make_file_cell(paths, file_):
    # Quick return if one level deep.
    if len(paths) == 1 and '.' not in paths[0]:
        value = file_.get(paths[0], '')
        if isinstance(value, list):
            return ', '.join([str(v) for v in value])
        return value
    # Else crawl nested objects.
    last = []
    for path in paths:
        cell_value = []
        for value in simple_path_ids(file_, path):
            cell_value.append(str(value))
        if last and cell_value:
            last = [
                v + ' ' + cell_value[0]
                for v in last
            ]
        else:
            last = cell_value
    return ', '.join(sorted(set(last)))


def file_matches_file_params(file_, positive_file_param_list):
    # Expects file_param_list where 'files.' has been
    # stripped off of key (files.file_type -> file_type)
    # and params with field negation (i.e. file_type!=bigWig)
    # have been filtered out.
    for k, v in positive_file_param_list.items():
        if '.' in k:
            file_prop_value = list(simple_path_ids(file_, k))
        else:
            file_prop_value = file_.get(k)
        if not file_prop_value:
            return False
        if isinstance(file_prop_value, list):
            return any([str(x) in v for x in file_prop_value])
        if str(file_prop_value) not in v:
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
        ('limit', 'all'),
    ]

    def __init__(self, request):
        self.request = request
        self.query_string = QueryString(request)
        self.param_list = self.query_string.group_values_by_key()
        self.positive_file_param_list = {}
        self.header = []
        self.experiment_column_to_fields_mapping = OrderedDict()
        self.file_column_to_fields_mapping = OrderedDict()
        self.visualizable_only = self.query_string.is_param('option', 'visualizable')
        self.raw_only = self.query_string.is_param('option', 'raw')
        self.search_request = None
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
            if fields[0].startswith('files'):
                self.file_column_to_fields_mapping[column] = [
                    field.replace('files.', '')
                    for field in fields
                ]
            else:
                self.experiment_column_to_fields_mapping[column] = fields

    def _set_positive_file_param_list(self):
        self.positive_file_param_list = {
            k.replace('files.', ''): v
            for k, v in self.param_list.items()
            if k.startswith('files.') and '!' not in k
        }

    def _add_fields_to_param_list(self):
        self.param_list['field'] = []
        for column, fields in self._get_column_to_fields_mapping().items():
            self.param_list['field'].extend(fields)

    def _initialize_at_id_param(self):
        self.param_list['@id'] = self.param_list.get('@id', [])

    def _maybe_add_cart_elements_to_param_list(self):
        cart_uuids = self.param_list.get('cart', [])
        if cart_uuids:
            try:
                cart = self.request.embed(cart_uuids[0], '@@object')
                del self.param_list['cart']
            except KeyError:
                raise HTTPBadRequest(explanation='Specified cart does not exist.')
            else:
                self.param_list['@id'].extend(
                    cart.get('elements', [])
                )

    def _maybe_add_json_elements_to_param_list(self):
        try:
            self.param_list['@id'].extend(
                self.request.json.get('elements', [])
            )
        except ValueError:
            pass

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

    def _validate_request(self):
        type_params = self.param_list.get('type', [])
        if len(type_params) != 1:
            raise HTTPBadRequest(explanation='URL requires one "type" parameter.')
        return True

    def _initialize_report(self):
        self._build_header()
        self._split_column_and_fields_by_experiment_and_file()
        self._set_positive_file_param_list()

    def _build_params(self):
        self._add_fields_to_param_list()
        self._initialize_at_id_param()
        self._maybe_add_cart_elements_to_param_list()
        self._maybe_add_json_elements_to_param_list()

    def _build_new_request(self):
        self._build_query_string()
        request = self.query_string.get_request_with_new_query_string()
        request.path_info = self._get_search_path()
        request.registry = self.request.registry
        return request

    def _get_search_results_generator(self):
        return search_generator(
            self._build_new_request()
        )

    def _should_not_report_file(self, file_):
        conditions = [
            not file_matches_file_params(file_, self.positive_file_param_list),
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
        for experiment in self._get_search_results_generator()['@graph']:
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

    def generate(self):
        self._validate_request()
        self._initialize_report()
        self._build_params()
        return Response(
             content_type='text/tsv',
             app_iter=self._generate_rows(),
             content_disposition='attachment;filename=metadata.tsv'
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
        ('field', '@id')
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
            (k.replace('files.', ''), v)
            for k, v in self.query_string._get_original_params()
            if k.startswith('files.')
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
            if not k.startswith('files.')
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
        request.registry = self.request.registry
        return request

    def _get_file_search_results_generator(self):
        request = self._build_new_file_request()
        bsg = BatchedSearchGenerator(request)
        return bsg.results()

    # Overrides parent.
    def _generate_rows(self):
        yield self.csv.writerow(self.header)
        for experiment in self._get_search_results_generator()['@graph']:
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


class CSVGenerator:

    def __init__(self, delimiter='\t', lineterminator='\n'):
        self.writer = csv.writer(
            self,
            delimiter=delimiter,
            lineterminator=lineterminator
        )

    def writerow(self, row):
        self.writer.writerow(row)
        return self.row

    def write(self, row):
        self.row = row.encode('utf-8')


class BatchedSearchGenerator:

    SEARCH_PATH = '/search/'
    DEFAULT_PARAMS = [
        ('limit', 'all')
    ]

    def __init__(self, request, batch_field='@id', batch_size=5000):
        self.request = request
        self.batch_field = batch_field
        self.batch_size = batch_size
        self.query_string = QueryString(request)
        self.param_list = self.query_string.group_values_by_key()
        self.batch_param_values = self.param_list.get(batch_field, []).copy()

    def _make_batched_values_from_batch_param_values(self):
        end = len(self.batch_param_values)
        for start in range(0, end, self.batch_size):
            yield self.batch_param_values[start:min(start + self.batch_size, end)]

    def _make_batched_params_from_batched_values(self, batched_values):
        return [
            (self.batch_field, batched_value)
            for batched_value in batched_values
        ]

    def _build_new_request(self, batched_params):
        self.query_string.drop('limit')
        self.query_string.drop(self.batch_field)
        self.query_string.extend(
            batched_params + self.DEFAULT_PARAMS
        )
        request = self.query_string.get_request_with_new_query_string()
        request.path_info = self.SEARCH_PATH
        request.registry = self.request.registry
        return request

    def results(self):
        if not self.batch_param_values:
            yield from search_generator(self._build_new_request([]))['@graph']
        for batched_values in self._make_batched_values_from_batch_param_values():
            batched_params = self._make_batched_params_from_batched_values(batched_values)
            request = self._build_new_request(batched_params)
            yield from search_generator(request)['@graph']


def _get_metadata(context, request):
    metadata_report = MetadataReport(request)
    return metadata_report.generate()


def _get_annotation_metadata(context, request):
    annotation_metadata_report = AnnotationMetadataReport(request)
    return annotation_metadata_report.generate()


def _get_publication_data_metadata(context, request):
    publication_data_metadata_report = PublicationDataMetadataReport(request)
    return publication_data_metadata_report.generate()


def metadata_report_factory(context, request):
    qs = QueryString(request)
    specified_type = qs.get_one_value(
            params=qs.get_type_filters()
    )
    if specified_type == 'Annotation':
        return _get_annotation_metadata(context, request)
    elif specified_type == 'PublicationData':
        return _get_publication_data_metadata(context, request)
    else:
        return _get_metadata(context, request)


@view_config(route_name='metadata', request_method='GET')
@allowed_types(METADATA_ALLOWED_TYPES)
def metadata_tsv(context, request):
    return metadata_report_factory(context, request)
