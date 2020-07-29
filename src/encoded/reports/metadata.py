import csv

from collections import defaultdict
from collections import OrderedDict
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


COLUMN_TO_FIELDS_MAPPING = OrderedDict(
    [
        ('File accession', ['files.title']),
        ('File format', ['files.file_type']),
        ('File type', ['files.file_format']),
        ('File format type', ['files.file_format_type']),
        ('Output type', ['files.output_type']),
        ('File assembly', ['files.assembly']),
        ('Experiment accession', ['accession']),
        ('Assay', ['assay_title']),
        ('Biosample term id', ['biosample_ontology.term_id']),
        ('Biosample term name', ['biosample_ontology.term_name']),
        ('Biosample type', ['biosample_ontology.classification']),
        ('Biosample organism', ['replicates.library.biosample.organism.scientific_name']),
        ('Biosample treatments', ['replicates.library.biosample.treatments.treatment_term_name']),
        (
            'Biosample treatments amount',
            [
                'replicates.library.biosample.treatments.amount',
                'replicates.library.biosample.treatments.amount_units'
            ]
        ),
        (
            'Biosample treatments duration',
            [
                'replicates.library.biosample.treatments.duration',
                'replicates.library.biosample.treatments.duration_units'
            ]
        ),
        ('Biosample genetic modifications methods', ['replicates.library.biosample.applied_modifications.method']),
        ('Biosample genetic modifications categories', ['replicates.library.biosample.applied_modifications.category']),                                   
        ('Biosample genetic modifications targets', ['replicates.library.biosample.applied_modifications.modified_site_by_target_id']),                                   
        ('Biosample genetic modifications gene targets', ['replicates.library.biosample.applied_modifications.modified_site_by_gene_id']),
        (
            'Biosample genetic modifications site coordinates', [
                'replicates.library.biosample.applied_modifications.modified_site_by_coordinates.assembly',
                'replicates.library.biosample.applied_modifications.modified_site_by_coordinates.chromosome',
                'replicates.library.biosample.applied_modifications.modified_site_by_coordinates.start',
                'replicates.library.biosample.applied_modifications.modified_site_by_coordinates.end'
            ]
        ),
        ('Biosample genetic modifications zygosity', ['replicates.library.biosample.applied_modifications.zygosity']), 
        ('Experiment target', ['target.name']),
        ('Library made from', ['replicates.library.nucleic_acid_term_name']),
        ('Library depleted in', ['replicates.library.depleted_in_term_name']),
        ('Library extraction method', ['replicates.library.extraction_method']),
        ('Library lysis method', ['replicates.library.lysis_method']),
        ('Library crosslinking method', ['replicates.library.crosslinking_method']),
        ('Library strand specific', ['replicates.library.strand_specificity']),
        ('Experiment date released', ['date_released']),
        ('Project', ['award.project']),
        (
            'RBNS protein concentration', [
                'files.replicate.rbns_protein_concentration',
                'files.replicate.rbns_protein_concentration_units'
            ]
        ),
        ('Library fragmentation method', ['files.replicate.library.fragmentation_method']),
        ('Library size range', ['files.replicate.library.size_range']),
        ('Biological replicate(s)', ['files.biological_replicates']),
        ('Technical replicate(s)', ['files.technical_replicates']),
        ('Read length', ['files.read_length']),
        ('Mapped read length', ['files.mapped_read_length']),
        ('Run type', ['files.run_type']),
        ('Paired end', ['files.paired_end']),
        ('Paired with', ['files.paired_with']),
        ('Derived from', ['files.derived_from']),
        ('Size', ['files.file_size']),
        ('Lab', ['files.lab.title']),
        ('md5sum', ['files.md5sum']),
        ('dbxrefs', ['files.dbxrefs']),
        ('File download URL', ['files.href']),
        ('Genome annotation', ['files.genome_annotation']),
        ('Platform', ['files.platform.title']),
        ('Controlled by', ['files.controlled_by']),
        ('File Status', ['files.status']),
        ('No File Available', ['files.no_file_available']),
        ('Restricted', ['files.restricted']),
        ('s3_uri', ['files.s3_uri']),
    ]
)


AUDIT_TO_AUDIT_COLUMN_MAPPING = [
    ('WARNING', 'Audit WARNING'),
    ('INTERNAL_ACTION', 'Audit INTERNAL_ACTION'),
    ('NOT_COMPLIANT', 'Audit NOT_COMPLIANT'),
    ('ERROR', 'Audit ERROR'),
]


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
    last = []
    for path in paths:
        cell_value = []
        for value in simple_path_ids(file_, path):
            cell_value.append(str(value))
        if path in ['paired_with', 'derived_from']:
            last = [
                at_id[7:-1]
                for at_id in cell_value
            ]
        elif last and cell_value:
            last = [
                v + ' ' + cell_value[0]
                for v in last
            ]
        else:
            last = cell_value
    return ', '.join(sorted(set(last)))


def file_matches_file_params(file_, file_param_list):
    for k, v in file_param_list.items():
        file_prop_value = file_.get(k[len('files.'):])
        if not file_prop_value or file_prop_value not in v:
            return False
    return True


def group_audits_by_files_and_type(audits):
    grouped_file_audits = defaultdict(lambda: defaultdict(list))
    grouped_other_audits = defaultdict(list)
    for audit_type, audit_column in AUDIT_TO_AUDIT_COLUMN_MAPPING:
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
        self.number_of_audits = len(AUDIT_TO_AUDIT_COLUMN_MAPPING)

    def _build_header(self):
        for column in COLUMN_TO_FIELDS_MAPPING:
            if column not in self.EXCLUDED_COLUMNS:
                self.header.append(column)
        for audit, column in AUDIT_TO_AUDIT_COLUMN_MAPPING:
            self.header.append(column)
        
    def _split_column_and_fields_by_experiment_and_file(self):
        for column, fields in COLUMN_TO_FIELDS_MAPPING.items():
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
        for column, fields in COLUMN_TO_FIELDS_MAPPING.items():
            self.param_list['field'].extend(fields)

    def _initialize_at_id_param(self):
        self.param_list['@id'] = self.param_list.get('@id', [])

    def _maybe_add_cart_elements_to_param_list(self):
        cart_uuids = self.param_list.get('cart', [])
        if cart_uuids:
            try:
                cart = self.request.embed(cart_uuid[0], '@@object')
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
            ) for audit_type, audit_column in AUDIT_TO_AUDIT_COLUMN_MAPPING
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


@view_config(route_name='metadata', request_method='GET')
def metadata_tsv(context, request):
    metadata_report = MetadataReport(request)
    return metadata_report.generate()
