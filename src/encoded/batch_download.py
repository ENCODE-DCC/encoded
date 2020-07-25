from collections import OrderedDict
from pyramid.compat import bytes_
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config
from pyramid.response import Response
from snovault import TYPES
from snovault.elasticsearch.searches.parsers import QueryString
from snovault.util import simple_path_ids
from urllib.parse import (
    parse_qs,
    urlencode,
    quote,
)
from encoded.search_views import search_generator
from .vis_defines import is_file_visualizable
import csv
import io
import json
import datetime
import re

# Maximum number of cart files to retrieve in a single request.
ELEMENT_CHUNK_SIZE = 1000
currenttime = datetime.datetime.now()


def includeme(config):
    config.add_route('batch_download', '/batch_download{slash:/?}')
    config.add_route('metadata', '/metadata{slash:/?}')
    config.add_route('peak_metadata', '/peak_metadata/{search_params}/{tsv}')
    config.add_route('report_download', '/report.tsv')
    config.scan(__name__)


# includes concatenated properties
_tsv_mapping = OrderedDict([
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
    ('Biosample treatments amount', ['replicates.library.biosample.treatments.amount',
                                     'replicates.library.biosample.treatments.amount_units']),
    ('Biosample treatments duration', ['replicates.library.biosample.treatments.duration',
                                       'replicates.library.biosample.treatments.duration_units']),
    ('Biosample genetic modifications methods', ['replicates.library.biosample.applied_modifications.method']),
    ('Biosample genetic modifications categories', ['replicates.library.biosample.applied_modifications.category']),                                   
    ('Biosample genetic modifications targets', ['replicates.library.biosample.applied_modifications.modified_site_by_target_id']),                                   
    ('Biosample genetic modifications gene targets', ['replicates.library.biosample.applied_modifications.modified_site_by_gene_id']),                                   
    ('Biosample genetic modifications site coordinates', ['replicates.library.biosample.applied_modifications.modified_site_by_coordinates.assembly',
                                                          'replicates.library.biosample.applied_modifications.modified_site_by_coordinates.chromosome',
                                                          'replicates.library.biosample.applied_modifications.modified_site_by_coordinates.start',
                                                          'replicates.library.biosample.applied_modifications.modified_site_by_coordinates.end']),                                   
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
    ('RBNS protein concentration', ['files.replicate.rbns_protein_concentration', 'files.replicate.rbns_protein_concentration_units']),
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
])

_audit_mapping = OrderedDict([
    ('Audit WARNING', ['audit.WARNING.path',
                       'audit.WARNING.category',
                       'audit.WARNING.detail']),
    ('Audit INTERNAL_ACTION', ['audit.INTERNAL_ACTION.path',
                               'audit.INTERNAL_ACTION.category',
                               'audit.INTERNAL_ACTION.detail']),
    ('Audit NOT_COMPLIANT', ['audit.NOT_COMPLIANT.path',
                             'audit.NOT_COMPLIANT.category',
                             'audit.NOT_COMPLIANT.detail']),
    ('Audit ERROR', ['audit.ERROR.path',
                     'audit.ERROR.category',
                     'audit.ERROR.detail'])
])

_audits = [
    'WARNING',
    'INTERNAL_ACTION',
    'NOT_COMPLIANT',
    'ERROR',
]

_tsv_mapping_annotation = OrderedDict([
    ('File accession', ['files.title']),
    ('File format', ['files.file_type']),
    ('Output type', ['files.output_type']),
    ('Assay term name', ['files.assay_term_name']),
    ('Dataset accession', ['accession']),
    ('Annotation type', ['annotation_type']),
    ('Software used', ['software_used.software.title']),
    ('Encyclopedia Version', ['encyclopedia_version']),
    ('Biosample term id', ['biosample_ontology.term_id']),
    ('Biosample term name', ['biosample_ontology.term_name']),
    ('Biosample type', ['biosample_ontology.classification']),
    ('Life stage', ['relevant_life_stage']),
    ('Age', ['relevant_timepoint']),
    ('Age units', ['relevant_timepoint_units']),
    ('Organism', ['organism.scientific_name']),
    ('Targets', ['targets.name']),
    ('Dataset date released', ['date_released']),
    ('Project', ['award.project']),
    ('Lab', ['files.lab.title']),
    ('md5sum', ['files.md5sum']),
    ('dbxrefs', ['files.dbxrefs']),
    ('File download URL', ['files.href']),
    ('Assembly', ['files.assembly']),
    ('Controlled by', ['files.controlled_by']),
    ('File Status', ['files.status']),
    ('Derived from', ['files.derived_from']),
    ('S3 URL', ['files.cloud_metadata.url']),
    ('Size', ['files.file_size']),
    ('No File Available', ['file.no_file_available']),
    ('Restricted', ['files.restricted'])
])

_tsv_mapping_publicationdata = OrderedDict([
    ('File accession', ['files.title']),
    ('File dataset', ['files.dataset']),
    ('File type', ['files.file_format']),
    ('File format', ['files.file_type']),
    ('File output type', ['files.output_type']),
    ('Assay term name', ['files.assay_term_name']),
    ('Biosample term id', ['files.biosample_ontology.term_id']),
    ('Biosample term name', ['files.biosample_ontology.term_name']),
    ('Biosample type', ['files.biosample_ontology.classification']),
    ('File target', ['files.target.label']),
    ('Dataset accession', ['accession']),
    ('Dataset date released', ['date_released']),
    ('Project', ['award.project']),
    ('Lab', ['files.lab.title']),
    ('md5sum', ['files.md5sum']),
    ('dbxrefs', ['files.dbxrefs']),
    ('File download URL', ['files.href']),
    ('Assembly', ['files.assembly']),
    ('File status', ['files.status']),
    ('Derived from', ['files.derived_from']),
    ('S3 URL', ['files.cloud_metadata.url']),
    ('Size', ['files.file_size']),
    ('No File Available', ['file.no_file_available']),
    ('Restricted', ['files.restricted'])
])

_excluded_columns = ('Restricted', 'No File Available')

# Attributes of files to extract for metadata.tsv.
default_file_attributes = [
    'files.title',
    'files.file_type',
    'files.file_format',
    'files.file_format_type',
    'files.output_type',
    'files.assembly'
]

# For extracting accession from @id paths
accession_re = re.compile(r'^/[a-z-]+/([A-Z0-9]+)/$')
# For extracting object type from @id paths
type_re = re.compile(r'^/([a-z-]+)/[A-Z0-9]+/$')


# Lowercased type={object type} query-string values allowed for download/metadata.
_allowed_types = [
    'experiment',
    'annotation',
    'functionalcharacterizationexperiment',
    'publicationdata',
]


def get_file_uuids(result_dict):
    file_uuids = []
    for item in result_dict['@graph']:
        for file in item['files']:
            file_uuids.append(file['uuid'])
    return list(set(file_uuids))

def get_biosample_accessions(file_json, experiment_json):
    for f in experiment_json['files']:
        if file_json['uuid'] == f['uuid']:
            accession = f.get('replicate', {}).get('library', {}).get('biosample', {}).get('accession')
            if accession:
                return accession
    accessions = []
    for replicate in experiment_json.get('replicates', []):
        accession = replicate['library']['biosample']['accession']
        accessions.append(accession)
    return ', '.join(list(set(accessions)))

def get_peak_metadata_links(request):
    if request.matchdict.get('search_params'):
        search_params = request.matchdict['search_params']
    else:
        search_params = request.query_string

    peak_metadata_tsv_link = '{host_url}/peak_metadata/{search_params}/peak_metadata.tsv'.format(
        host_url=request.host_url,
        search_params=quote(search_params)
    )
    peak_metadata_json_link = '{host_url}/peak_metadata/{search_params}/peak_metadata.json'.format(
        host_url=request.host_url,
        search_params=quote(search_params)
    )
    return [peak_metadata_tsv_link, peak_metadata_json_link]

def make_cell(header_column, row, exp_data_row):
    temp = []
    for column in _tsv_mapping[header_column]:
        c_value = []
        for value in simple_path_ids(row, column):
            if str(value) not in c_value:
                c_value.append(str(value))
        if column == 'replicates.library.biosample.post_synchronization_time' and len(temp):
            if len(c_value):
                temp[0] = temp[0] + ' + ' + c_value[0]
        elif len(temp):
            if len(c_value):
                temp = [x + ' ' + c_value[0] for x in temp]
        else:
            temp = c_value
    exp_data_row.append(', '.join(list(set(temp))))


def funclog(func):
    def wrapper(*args, **kwargs):
        for i, arg in enumerate(args):
            print(i, arg)
        r = func(*args, **kwargs)
        print('return value:', r)
        return r
    return wrapper


@funclog
def make_audit_cell(header_column, experiment_json, file_json):
    categories = []
    paths = []
    for column in _audit_mapping[header_column]:
        for value in simple_path_ids(experiment_json, column):
            if 'path' in column:
                paths.append(value)
            elif 'category' in column:
                categories.append(value)
    data = []
    for i, path in enumerate(paths):
        if '/files/' in path and file_json.get('title', '') not in path:
            # Skip file audits that does't belong to the file
            continue
        else:
            data.append(categories[i])
    return ', '.join(list(set(data)))


from collections import defaultdict


def group_audits_by_file_and_type(audits):
    grouped_audits = defaultdict(lambda: defaultdict(list))
    for audit_type in _audits:
        for audit in audits.get(audit_type, []):
            path = audit.get('path')
            if '/files/' in path:
                grouped_audits[path][audit_type].append(audit.get('category'))
    return grouped_audits   


def _get_annotation_metadata(request, search_path, param_list):
    """
    Get anotation data.

        :param request: Pyramid request
        :param search_path: Search url
        :param param_list: Initial param_list
    """
    header = [header for header in _tsv_mapping_annotation if header not in _excluded_columns]
    header.extend([prop for prop in _audit_mapping])
    fout = io.StringIO()
    writer = csv.writer(fout, delimiter='\t')
    writer.writerow(header)
    param_list['limit'] = ['all']
    fields = ['field={}'.format(str(value[0])) for _, value in _tsv_mapping_annotation.items()] + ['field=audit']
    path = '{}?{}&{}'.format(
        search_path,
        quote(urlencode(param_list, True)),
        '&'.join(fields)
    )
    results = request.embed(path, as_user=True)
    for result_graph in results['@graph']:
        result_files = result_graph.get('files', {})
        if not result_files:
            continue
        software = [s for s in result_graph.get('software_used', {})]
        software_set = ', '.join([s['software']['title'] for s in software])
        for result_file in result_files:
            if restricted_files_present(result_file):
                continue
            if is_no_file_available(result_file):
                continue
            if param_list.get('files.file_type') and result_file['file_type'] not in param_list['files.file_type']:
                continue
            row = [
                result_file.get('title', ''),
                result_file.get('file_type', ''),
                result_file.get('output_type', ''),
                result_file.get('assay_term_name', ''),
                result_graph.get('accession', ''),
                result_graph.get('annotation_type', ''),
                software_set,
                result_graph.get('encyclopedia_version', ''),
                result_graph.get('biosample_ontology', {}).get('term_id', ''),
                result_graph.get('biosample_ontology', {}).get('term_name', ''),
                result_graph.get('biosample_ontology', {}).get('classification', ''),
                result_graph.get('relevant_life_stage', ''),
                result_graph.get('relevant_timepoint', ''),
                result_graph.get('relevant_timepoint_units', ''),
                result_graph.get('organism', {}).get('scientific_name', ''),
                ', '.join([target['name'] for target in result_graph.get('targets', {})]),
                result_graph.get('date_released', ''),
                result_graph.get('award', {}).get('project', ''),
                result_file.get('lab', {}).get('title', ''),
                result_file.get('md5sum', ''),
                ', '.join(result_file.get('dbxrefs', '')),
                ''.join([request.host_url, result_file.get('href', '')]),
                result_file.get('assembly', ''),
                result_file.get('controlled_by', ''),
                result_file.get('status', ''),
                ', '.join([derived_from[7:-1] for derived_from in result_file.get('derived_from', '')]),
                result_file.get('cloud_metadata', {}).get('url', ''),
                result_file.get('file_size', ''),
            ]
            # make_audit_cell() was designed just for experiment, but works too for annotation
            row.extend(
                [make_audit_cell(audit_type, result_graph, result_file) for audit_type in _audit_mapping]
            )
            writer.writerow(row)
    return Response(
        content_type='text/tsv',
        body=fout.getvalue(),
        content_disposition='attachment;filename="%s"' % 'metadata.tsv'
    )

def _get_publicationdata_metadata(request):
    """
    Generate PublicationData metadata.tsv.

        :param request: Pyramid request
    """
    qs = QueryString(request)
    param_list = qs.group_values_by_key()

    # Get the required "dataset={path}" parameter.
    dataset_path = param_list.get('dataset', [''])[0]

    # Open the metadata.tsv file for writing.
    fout = io.StringIO()
    writer = csv.writer(fout, delimiter='\t')

    # Build the column-title header row and write it to the file.
    header = [header for header in _tsv_mapping_publicationdata if header not in _excluded_columns]
    writer.writerow(header)

    # Load the specified PublicationData object and extract its files to build the rows.
    dataset = request.embed(dataset_path, as_user=True)
    file_ids = dataset.get('files', [])
    if file_ids:
        for file_id in file_ids:
            # Load the file object and disqualify those we don't handle.
            file = request.embed(file_id, as_user=True)

            # Load the file object and disqualify those we don't handle.
            biosample_ontology = file.get('biosample_ontology', {})
            if restricted_files_present(file):
                continue
            if is_no_file_available(file):
                continue

            # Extract the file's dataset accession from the @id; avoids loading the dataset object.
            dataset_accession = ''
            accession_match = accession_re.match(file.get('dataset', ''))
            if accession_match:
                dataset_accession = accession_match.group(1)

            # Extract the file's derived_from accessions from their @id.
            derived_from_accessions = []
            derived_from_file_ids = file.get('derived_from', '')
            for derived_from_file_id in derived_from_file_ids:
                accession_match = accession_re.match(derived_from_file_id)
                if accession_match:
                    derived_from_accessions.append(accession_match.group(1))

            # Build the row's data; must sync with _tsv_mapping_publicationdata.
            row = [
                file.get('title', ''),
                dataset_accession,
                file.get('file_format', ''),
                file.get('file_type', ''),
                file.get('output_type', ''),
                file.get('assay_term_name', ''),
                biosample_ontology.get('term_id'),
                biosample_ontology.get('term_name'),
                biosample_ontology.get('classification'),
                file.get('target', {}).get('label', ''),
                dataset.get('accession', ''),
                dataset.get('date_released', ''),
                dataset.get('award', {}).get('project', ''),
                file.get('lab', {}).get('title', ''),
                file.get('md5sum', ''),
                ', '.join(file.get('dbxrefs', '')),
                file.get('href', ''),
                file.get('assembly', ''),
                file.get('status', ''),
                ', '.join(derived_from_accessions),
                file.get('cloud_metadata', {}).get('url', ''),
                file.get('file_size', ''),
            ]
            writer.writerow(row)

        # All rows collected; write to the metadata.tsv file and download.
        return Response(
            content_type='text/tsv',
            body=fout.getvalue(),
            content_disposition='attachment;filename="%s"' % 'metadata.tsv'
        )


def _batch_download_publicationdata(request):
    """
    Generate PublicationData files.txt.

        :param request: Pyramid request
    """

    # Parse the batch_download request query string.
    qs = QueryString(request)
    param_list = qs.group_values_by_key()

    # Get the required "dataset={path}" parameter.
    dataset_path = param_list.get('dataset', [''])[0]

    # Retrieve the files property of the requested PublicationData object.
    object = request.embed(dataset_path, as_user=True)
    file_ids = object.get('files', [])

    # Generate the metadata link that heads the file.
    metadata_link = '{host_url}/metadata/?{search_params}'.format(
        host_url=request.host_url,
        search_params=qs._get_original_query_string()
    )

    # Generate the content of files.txt starting with the metadata.tsv download line and then each
    # file's download URL.
    files = [metadata_link]
    dataset_type = ''
    if file_ids:
        for file_id in file_ids:
            # Request individual file object from its path.
            file = request.embed(file_id, as_user=True)

            # All file datasets need to belong to the same type of dataset.
            if dataset_type:
                # See if subsequent dataset types match the first one we found.
                file_dataset_type_match = type_re.match(file.get('dataset', ''))
                if file_dataset_type_match and file_dataset_type_match.group(1) != dataset_type:
                    raise HTTPBadRequest(explanation='File dataset types must be homogeneous')
            else:
                # Establish the first dataset type we find.
                dataset_type_match = type_re.match(file.get('dataset', ''))
                if dataset_type_match:
                    dataset_type = dataset_type_match.group(1)

            # Other disqualifying conditions.
            if restricted_files_present(file):
                continue
            if is_no_file_available(file):
                continue

            # Finally append file to files.txt.
            files.append(
                '{host_url}{href}'.format(
                    host_url=request.host_url,
                    href=file['href']
                )
            )

    # Initiate the files.txt download.
    return Response(
        content_type='text/plain',
        body='\n'.join(files),
        content_disposition='attachment; filename="%s"' % 'files.txt'
    )


@view_config(route_name='peak_metadata', request_method='GET')
def peak_metadata(context, request):
    param_list = parse_qs(request.matchdict['search_params'])
    param_list['field'] = []
    header = ['assay_term_name', 'coordinates', 'target.label', 'biosample.accession', 'file.accession', 'experiment.accession']
    param_list['limit'] = ['all']
    path = '/region-search/?{}&{}'.format(quote(urlencode(param_list, True)),'referrer=peak_metadata')
    results = request.embed(path, as_user=True)
    uuids_in_results = get_file_uuids(results)
    rows = []
    json_doc = {}
    for row in results['peaks']:
        if row['_id'] in uuids_in_results:
            file_json = request.embed(row['_id'])
            experiment_json = request.embed(file_json['dataset'])
            for hit in row['inner_hits']['positions']['hits']['hits']:
                data_row = []
                coordinates = '{}:{}-{}'.format(row['_index'], hit['_source']['start'], hit['_source']['end'])
                file_accession = file_json['accession']
                experiment_accession = experiment_json['accession']
                assay_name = experiment_json['assay_term_name']
                target_name = experiment_json.get('target', {}).get('label') # not all experiments have targets
                biosample_accession = get_biosample_accessions(file_json, experiment_json)
                data_row.extend([assay_name, coordinates, target_name, biosample_accession, file_accession, experiment_accession])
                rows.append(data_row)
                if assay_name not in json_doc:
                    json_doc[assay_name] = []
                else:
                    json_doc[assay_name].append({
                        'coordinates': coordinates,
                        'target.name': target_name,
                        'biosample.accession': list(biosample_accession.split(', ')),
                        'file.accession': file_accession,
                        'experiment.accession': experiment_accession
                    })
    if 'peak_metadata.json' in request.url:
        return Response(
            content_type='text/plain',
            body=json.dumps(json_doc),
            content_disposition='attachment;filename="%s"' % 'peak_metadata.json'
        )
    fout = io.StringIO()
    writer = csv.writer(fout, delimiter='\t')
    writer.writerow(header)
    writer.writerows(rows)
    return Response(
        content_type='text/tsv',
        body=fout.getvalue(),
        content_disposition='attachment;filename="%s"' % 'peak_metadata.tsv'
    )


@view_config(route_name='metadata', request_method='GET')
def metadata_tsv(context, request):
    qs = QueryString(request)
    param_list = qs.group_values_by_key()
    if 'referrer' in param_list:
        search_path = '/{}/'.format(param_list.pop('referrer')[0])
    else:
        search_path = '/search/'
    type_param = param_list.get('type', [''])[0]
    cart_uuids = param_list.get('cart', [])

    # Only allow specific type= query-string values, or cart=.
    if not type_param and not cart_uuids:
        raise HTTPBadRequest(explanation='URL must include a "type" or "cart" parameter.')
    if not type_param.lower() in _allowed_types:
        raise HTTPBadRequest(explanation='"{}" not a valid type for metadata'.format(type_param))

    # Handle special-case metadata.tsv generation.
    if type_param:
        if type_param.lower() == 'annotation':
            return _get_annotation_metadata(request, search_path, param_list)
        if type_param.lower() == 'publicationdata':
            return _get_publicationdata_metadata(request)

    param_list['field'] = []
    header = []
    file_attributes = []
    for prop in _tsv_mapping:
        if prop not in _excluded_columns:
            header.append(prop)
            if _tsv_mapping[prop][0].startswith('files'):
                file_attributes = file_attributes + [_tsv_mapping[prop][0]]
        param_list['field'] = param_list['field'] + _tsv_mapping[prop]

    # Handle metadata.tsv lines from cart-generated files.txt.
    if cart_uuids:
        # metadata.tsv line includes cart UUID, so load the specified cart and
        # get its "elements" property for a list of items to retrieve.
        cart_uuid = cart_uuids.pop()
        del param_list['cart']
        try:
            cart = request.embed(cart_uuid, '@@object')
        except KeyError:
            raise HTTPBadRequest(explanation='Specified cart does not exist.')
        else:
            if cart.get('elements'):
                param_list['@id'] = cart['elements']
    else:
        # If the metadata.tsv line includes a JSON payload, get its "elements"
        # property for a list of items to retrieve.
        try:
            elements = request.json.get('elements')
        except ValueError:
            pass
        else:
            param_list['@id'] = elements
    default_params = [
        ('field', 'audit'),
        ('field', 'files.@id'),
        ('limit', 'all'),
    ]
    field_params = [
        ('field', p)
        for p in param_list.get('field', [])
    ]
    at_id_params = [
        ('@id', p)
        for p in param_list.get('@id', [])
    ]
    qs.drop('limit')

    # Check for the "visualizable" and/or "raw" options in the query string for file filtering.
    visualizable_only = qs.is_param('option', 'visualizable')
    raw_only = qs.is_param('option', 'raw')
    qs.drop('option')

    qs.extend(
        default_params + field_params + at_id_params
    )
    path = '{}?{}'.format(search_path, str(qs))
    results = request.embed(quote(path), as_user=True)
    rows = []
    for experiment_json in results['@graph']:
        print(experiment_json.get('audit'))
        grouped_audits = group_audits_by_file_and_type(
            experiment_json.get('audit', {})
        )
        print(grouped_audits)
        if experiment_json.get('files', []):
            exp_data_row = []
            for column in header:
                if not _tsv_mapping[column][0].startswith('files'):
                    make_cell(column, experiment_json, exp_data_row)

            f_attributes = ['files.title', 'files.file_type', 'files.file_format',
                            'files.file_format_type', 'files.output_type', 'files.assembly']

            for f in experiment_json['files']:
                print(f.get('@id'))
                if not files_prop_param_list(f, param_list):
                    continue
                if visualizable_only and not is_file_visualizable(f):
                    continue
                if raw_only and f.get('assembly'):
                    # "raw" option only allows files w/o assembly.
                    continue
                if restricted_files_present(f):
                    continue
                if is_no_file_available(f):
                    continue
                f['href'] = request.host_url + f['href']
                f_row = []
                for attr in f_attributes:
                    f_row.append(f.get(attr[6:], ''))
                data_row = f_row + exp_data_row
                for prop in file_attributes:
                    if prop in f_attributes:
                        continue
                    path = prop[6:]
                    temp = []
                    for value in simple_path_ids(f, path):
                        temp.append(str(value))
                    if prop == 'files.replicate.rbns_protein_concentration':
                        if 'replicate' in f and 'rbns_protein_concentration_units' in f['replicate']:
                            temp[0] = temp[0] + ' ' + f['replicate']['rbns_protein_concentration_units']
                    if prop in ['files.paired_with', 'files.derived_from']:
                        # chopping of path to just accession
                        if len(temp):
                            new_values = [t[7:-1] for t in temp]
                            temp = new_values
                    data = list(set(temp))
                    data.sort()
                    data_row.append(', '.join(data))
                file_id = f.get('@id')
                print('f:', file_id)
                grouped_audits_for_file = grouped_audits.get(file_id, {})
                audit_info = [
                    ', '.join(set(grouped_audits_for_file.get(audit_type, [])))
                    for audit_type in _audits
                ]
                print(audit_info)
                data_row.extend(audit_info)
                rows.append(data_row)
    fout = io.StringIO()
    writer = csv.writer(fout, delimiter='\t', lineterminator='\n')
    header.extend([prop for prop in _audit_mapping])
    writer.writerow(header)
    writer.writerows(rows)
    return Response(
        content_type='text/tsv',
        body=fout.getvalue(),
        content_disposition='attachment;filename="%s"' % 'metadata.tsv'
    )


@view_config(route_name='batch_download', request_method=('GET', 'POST'))
def batch_download(context, request):
    default_params = [
        ('limit', 'all'),
        ('field', 'files.href'),
        ('field', 'files.restricted'),
        ('field', 'files.file_format'),
        ('field', 'files.file_format_type'),
        ('field', 'files.status'),
        ('field', 'files.assembly'),
    ]
    qs = QueryString(request)
    param_list = qs.group_values_by_key()
    file_filters = qs.param_keys_to_list(
        params=qs.get_filters_by_condition(
            key_and_value_condition=lambda k, _: k.startswith('files.')
        )
    )

    # Process PublicationData batch downloads separately.
    type_param = param_list.get('type', [''])[0]
    if type_param and type_param.lower() == 'publicationdata':
        return _batch_download_publicationdata(request)

    file_fields = [
        ('field', k)
        for k in file_filters
    ]
    qs.drop('limit')
    type_param = param_list.get('type', [''])[0]
    cart_uuids = param_list.get('cart', [])

    # Only allow specific type= query-string values, or cart=.
    if not type_param and not cart_uuids:
        raise HTTPBadRequest(explanation='URL must include a "type" or "cart" parameter.')
    if not type_param.lower() in _allowed_types:
        raise HTTPBadRequest(explanation='"{}" not a valid type for metadata'.format(type_param))

    # Check for the "visualizable" and/or "raw" options in the query string for file filtering.
    visualizable_only = qs.is_param('option', 'visualizable')
    raw_only = qs.is_param('option', 'raw')
    qs.drop('option')

    qs.extend(
        default_params + file_fields
    )
    experiments = []
    if request.method == 'POST':
        metadata_link = ''
        cart_uuid = qs.get_one_value(
            params=qs.get_key_filters(
                key='cart'
            )
        )
        try:
            elements = request.json.get('elements', [])
        except ValueError:
            elements = []

        if cart_uuid:
            try:
                request.embed(cart_uuid, '@@object')
            except KeyError:
                raise HTTPBadRequest(explanation='Specified cart does not exist.')

            # metadata.tsv link includes a cart UUID
            metadata_link = '{host_url}/metadata/?{search_params}'.format(
                host_url=request.host_url,
                search_params=qs._get_original_query_string()
            )
        else:
            metadata_link = '{host_url}/metadata/?{search_params} -X GET -H "Accept: text/tsv" -H "Content-Type: application/json" --data \'{{"elements": [{elements_json}]}}\''.format(
                host_url=request.host_url,
                search_params=qs._get_original_query_string(),
                elements_json=','.join('"{0}"'.format(element) for element in elements)
            )

        # Because of potential number of datasets in the cart, break search
        # into multiple searches of ELEMENT_CHUNK_SIZE datasets each.
        for i in range(0, len(elements), ELEMENT_CHUNK_SIZE):
            qs.drop('@id')
            qs.extend(
                [
                    ('@id', e)
                    for e in elements[i:i + ELEMENT_CHUNK_SIZE]
                ]
            )
            path = '/search/?{}'.format(str(qs))
            results = request.embed(quote(path), as_user=True)
            experiments.extend(results['@graph'])
    else:
        # Make sure regular batch download doesn't include a cart parameter; error if it does.
        if cart_uuids:
            raise HTTPBadRequest(explanation='You must download cart file manifests from the portal.')

        # Regular batch download has single simple call to request.embed
        metadata_link = '{host_url}/metadata/?{search_params}'.format(
            host_url=request.host_url,
            search_params=qs._get_original_query_string()
        )
        path = '/search/?{}'.format(str(qs))
        results = request.embed(quote(path), as_user=True)
        experiments = results['@graph']

    exp_files = (
            exp_file
            for exp in experiments
            for exp_file in exp.get('files', [])
    )

    files = [metadata_link]
    param_list = qs.group_values_by_key()
    for exp_file in exp_files:
        if not files_prop_param_list(exp_file, param_list):
            continue
        elif visualizable_only and not is_file_visualizable(exp_file):
            continue
        elif raw_only and exp_file.get('assembly'):
            # "raw" option only allows files w/o assembly.
            continue
        elif restricted_files_present(exp_file):
            continue
        files.append(
            '{host_url}{href}'.format(
                host_url=request.host_url,
                href=exp_file['href'],
            )
        )

    return Response(
        content_type='text/plain',
        body='\n'.join(files),
        content_disposition='attachment; filename="%s"' % 'files.txt'
    )


def files_prop_param_list(exp_file, param_list):
    """Does a file in experiment search results match query-string parms?

    Keyword arguments:
    exp_file -- file object from experiment search results
    param_list -- grouped query-string parameters for experiment search
    """
    for k, v in param_list.items():
        if k.startswith('files.'):
            file_prop = k[len('files.'):]
            if file_prop not in exp_file:
                return False
            if exp_file[file_prop] not in v:
                return False
    return True


def restricted_files_present(exp_file):
    if exp_file.get('restricted', False) is True:
        return True
    return False


def is_no_file_available(exp_file):
    return exp_file.get('no_file_available', False)
    

def lookup_column_value(value, path):
    nodes = [value]
    names = path.split('.')
    for name in names:
        nextnodes = []
        for node in nodes:
            if name not in node:
                continue
            value = node[name]
            if isinstance(value, list):
                nextnodes.extend(value)
            else:
                nextnodes.append(value)
        nodes = nextnodes
        if not nodes:
            return ''
    # if we ended with an embedded object, show the @id
    if nodes and hasattr(nodes[0], '__contains__') and '@id' in nodes[0]:
        nodes = [node['@id'] for node in nodes]
    deduped_nodes = []
    for n in nodes:
        if isinstance(n, dict):
            n = str(n)
        if n not in deduped_nodes:
            deduped_nodes.append(n)
    return u','.join(u'{}'.format(n) for n in deduped_nodes)


def format_row(columns):
    """Format a list of text columns as a tab-separated byte string."""
    return b'\t'.join([bytes_(" ".join(c.strip('\t\n\r').split()), 'utf-8') for c in columns]) + b'\r\n'


def _convert_camel_to_snake(type_str):
    tmp = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', type_str)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', tmp).lower()


@view_config(route_name='report_download', request_method='GET')
def report_download(context, request):
    downloadtime = datetime.datetime.now()

    types = request.params.getall('type')
    if len(types) != 1:
        msg = 'Report view requires specifying a single type.'
        raise HTTPBadRequest(explanation=msg)

    # Make sure we get all results
    request.GET['limit'] = 'all'
    type_str = types[0]
    schemas = [request.registry[TYPES][type_str].schema]
    columns = list_visible_columns_for_schemas(request, schemas)
    snake_type = _convert_camel_to_snake(type_str).replace("'", '')

    def format_header(seq):
        newheader="%s\t%s%s?%s\r\n" % (downloadtime, request.host_url, '/report/', request.query_string)
        return(bytes(newheader, 'utf-8'))
       

    # Work around Excel bug; can't open single column TSV with 'ID' header
    if len(columns) == 1 and '@id' in columns:
        columns['@id']['title'] = 'id'

    header = [column.get('title') or field for field, column in columns.items()]

    def generate_rows():
        yield format_header(header)
        yield format_row(header)
        for item in search_generator(request)['@graph']:
            values = [lookup_column_value(item, path) for path in columns]
            yield format_row(values)

    
    # Stream response using chunked encoding.
    request.response.content_type = 'text/tsv'
    request.response.content_disposition = 'attachment;filename="{}_report_{}_{}_{}_{}h_{}m.tsv"'.format(
        snake_type,
        downloadtime.year,
        downloadtime.month,
        downloadtime.day,
        downloadtime.hour,
        downloadtime.minute
    )
    request.response.app_iter = generate_rows()
    return request.response


def list_visible_columns_for_schemas(request, schemas):
    """
    Returns mapping of default columns for a set of schemas.
    """
    columns = OrderedDict({'@id': {'title': 'ID'}})
    for schema in schemas:
        if 'columns' in schema:
            columns.update(schema['columns'])
        else:
            # default columns if not explicitly specified
            columns.update(OrderedDict(
                (name, {
                    'title': schema['properties'][name].get('title', name)
                })
                for name in [
                    '@id', 'title', 'description', 'name', 'accession',
                    'aliases'
                ] if name in schema['properties']
            ))
    fields_requested = request.params.getall('field')
    if fields_requested:
        limited_columns = OrderedDict()
        for field in fields_requested:
            if field in columns:
                limited_columns[field] = columns[field]
            else:
                # We don't currently traverse to other schemas for embedded
                # objects to find property titles. In this case we'll just
                # show the field's dotted path for now.
                limited_columns[field] = {'title': field}
                for schema in schemas:
                    if field in schema['properties']:
                        limited_columns[field] = {
                            'title': schema['properties'][field]['title']
                        }
                        break
        columns = limited_columns
    return columns
