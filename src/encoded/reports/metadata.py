import csv

from collections import defaultdict
from collections import OrderedDict
from functools import wraps
from encoded.batch_download import _get_annotation_metadata
from encoded.batch_download import _get_publicationdata_metadata
from encoded.reports.constants import METADATA_ALLOWED_TYPES
from encoded.reports.constants import METADATA_COLUMN_TO_FIELDS_MAPPING
from encoded.reports.constants import METADATA_AUDIT_TO_AUDIT_COLUMN_MAPPING
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


def file_matches_file_params(file_, file_param_list):
    for k, v in file_param_list.items():
        if '.' in k:
            file_prop_value = list(simple_path_ids(file_, k[len('files.'):]))
        else:
            file_prop_value = file_.get(k[len('files.'):])
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
        self.file_param_list = {}
        self.header = []
        self.experiment_column_to_fields_mapping = OrderedDict()
        self.file_column_to_fields_mapping = OrderedDict()
        self.visualizable_only = self.query_string.is_param('option', 'visualizable')
        self.raw_only = self.query_string.is_param('option', 'raw')
        self.search_request = None
        self.csv = CSVGenerator()

    def _build_header(self):
        for column in METADATA_COLUMN_TO_FIELDS_MAPPING:
            if column not in self.EXCLUDED_COLUMNS:
                self.header.append(column)
        for audit, column in METADATA_AUDIT_TO_AUDIT_COLUMN_MAPPING:
            self.header.append(column)
        
    def _split_column_and_fields_by_experiment_and_file(self):
        for column, fields in METADATA_COLUMN_TO_FIELDS_MAPPING.items():
            if fields[0].startswith('files'):
                self.file_column_to_fields_mapping[column] = [
                    field.replace('files.', '')
                    for field in fields
                ]
            else:
                self.experiment_column_to_fields_mapping[column] = fields

    def _set_file_param_list(self):
        self.file_param_list = {
            k: v
            for k, v in self.param_list.items()
            if k.startswith('files.')
        }

    def _add_fields_to_param_list(self):
        self.param_list['field'] = []
        for column, fields in METADATA_COLUMN_TO_FIELDS_MAPPING.items():
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
        if 'referrer' in self.param_list:
            return '/{}/'.format(
                self.param_list.pop('referrer')[0]
            )
        return self.SEARCH_PATH

    def _validate_request(self):
        type_params = self.param_list.get('type', [])
        if len(type_params) != 1:
            raise HTTPBadRequest(explanation='URL requires one "type" parameter.')

    def _initialize_report(self):
        self._build_header()
        self._split_column_and_fields_by_experiment_and_file()
        self._set_file_param_list()

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
            not file_matches_file_params(file_, self.file_param_list),
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


def _get_metadata(context, request):
    metadata_report = MetadataReport(request)
    return metadata_report.generate()


def metadata_report_factory(context, request):
    qs = QueryString(request)
    specified_type = qs.get_one_value(
            params=qs.get_type_filters()
    )
    if specified_type == 'Annotation':
        return _get_annotation_metadata(context, request)
    elif specified_type == 'PublicationData':
        return _get_publicationdata_metadata(context, request)
    else:
        return _get_metadata(context, request)


@view_config(route_name='metadata', request_method='GET')
@allowed_types(METADATA_ALLOWED_TYPES)
def metadata_tsv(context, request):
    return metadata_report_factory(context, request)
