from collections import OrderedDict
from pyramid.compat import bytes_
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config
from pyramid.response import Response
from snovault import TYPES
from snovault.util import simple_path_ids
from urllib.parse import (
    parse_qs,
    urlencode,
)
from .search import iter_search_results
from .search import list_visible_columns_for_schemas
import csv
import io
import json
import datetime

currenttime = datetime.datetime.now()


def includeme(config):
    config.add_route('batch_download', '/batch_download/{search_params}')
    config.add_route('metadata', '/metadata/{search_params}/{tsv}')
    config.add_route('peak_metadata', '/peak_metadata/{search_params}/{tsv}')
    config.add_route('report_download', '/report.tsv')
    config.scan(__name__)


# includes concatenated properties
_tsv_mapping = OrderedDict([
    ('File accession', ['files.title']),
    ('File format', ['files.file_type']),
    ('Output type', ['files.output_type']),
    ('Experiment accession', ['accession']),
    ('Assay', ['assay_term_name']),
    ('Biosample term id', ['biosample_term_id']),
    ('Biosample term name', ['biosample_term_name']),
    ('Biosample type', ['biosample_type']),
    ('Biosample life stage', ['replicates.library.biosample.life_stage']),
    ('Biosample sex', ['replicates.library.biosample.sex']),
    ('Biosample Age', ['replicates.library.biosample.age',
                       'replicates.library.biosample.age_units']),
    ('Biosample organism', ['replicates.library.biosample.organism.scientific_name']),
    ('Biosample treatments', ['replicates.library.biosample.treatments.treatment_term_name']),
    ('Biosample subcellular fraction term name', ['replicates.library.biosample.subcellular_fraction_term_name']),
    ('Biosample phase', ['replicates.library.biosample.phase']),
    ('Biosample synchronization stage', ['replicates.library.biosample.fly_synchronization_stage',
                                         'replicates.library.biosample.worm_synchronization_stage',
                                         'replicates.library.biosample.post_synchronization_time',
                                         'replicates.library.biosample.post_synchronization_time_units']),
    ('Experiment target', ['target.name']),
    ('Antibody accession', ['replicates.antibody.accession']),
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
    ('Technical replicate', ['files.replicate.technical_replicate_number']),
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
    ('Assembly', ['files.assembly']),
    ('Platform', ['files.platform.title']),
    ('Controlled by', ['files.controlled_by']),
    ('File Status', ['files.status'])
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
        search_params=search_params
    )
    peak_metadata_json_link = '{host_url}/peak_metadata/{search_params}/peak_metadata.json'.format(
        host_url=request.host_url,
        search_params=search_params
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


@view_config(route_name='peak_metadata', request_method='GET')
def peak_metadata(context, request):
    param_list = parse_qs(request.matchdict['search_params'])
    param_list['field'] = []
    header = ['assay_term_name', 'coordinates', 'target.label', 'biosample.accession', 'file.accession', 'experiment.accession']
    param_list['limit'] = ['all']
    path = '/region-search/?{}&{}'.format(urlencode(param_list, True),'referrer=peak_metadata')
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
    param_list = parse_qs(request.matchdict['search_params'])
    if 'referrer' in param_list:
        search_path = '/{}/'.format(param_list.pop('referrer')[0])
    else:
        search_path = '/search/'
    param_list['field'] = []
    header = []
    file_attributes = []
    for prop in _tsv_mapping:
        header.append(prop)
        param_list['field'] = param_list['field'] + _tsv_mapping[prop]
        if _tsv_mapping[prop][0].startswith('files'):
            file_attributes = file_attributes + [_tsv_mapping[prop][0]]
    param_list['limit'] = ['all']
    path = '{}?{}'.format(search_path, urlencode(param_list, True))
    results = request.embed(path, as_user=True)
    rows = []
    for experiment_json in results['@graph']:
        if experiment_json['files']:
            exp_data_row = []
            for column in header:
                if not _tsv_mapping[column][0].startswith('files'):
                    make_cell(column, experiment_json, exp_data_row)

            f_attributes = ['files.title', 'files.file_type',
                            'files.output_type']

            for f in experiment_json['files']:
                if 'files.file_type' in param_list:
                    if f['file_type'] not in param_list['files.file_type']:
                        continue
                f['href'] = request.host_url + f['href']
                f_row = []
                for attr in f_attributes:
                    f_row.append(f[attr[6:]])
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
                audit_info = [make_audit_cell(audit_type, experiment_json, f) for audit_type in _audit_mapping]
                data_row.extend(audit_info)
                rows.append(data_row)
    fout = io.StringIO()
    writer = csv.writer(fout, delimiter='\t')
    header.extend([prop for prop in _audit_mapping])
    writer.writerow(header)
    writer.writerows(rows)
    return Response(
        content_type='text/tsv',
        body=fout.getvalue(),
        content_disposition='attachment;filename="%s"' % 'metadata.tsv'
    )


@view_config(route_name='batch_download', request_method='GET')
def batch_download(context, request):
    # adding extra params to get required columns
    param_list = parse_qs(request.matchdict['search_params'])
    param_list['field'] = ['files.href', 'files.file_type', 'files']
    param_list['limit'] = ['all']
    path = '/search/?%s' % urlencode(param_list, True)
    results = request.embed(path, as_user=True)
    metadata_link = '{host_url}/metadata/{search_params}/metadata.tsv'.format(
        host_url=request.host_url,
        search_params=request.matchdict['search_params']
    )
    files = [metadata_link]
    if 'files.file_type' in param_list:
        for exp in results['@graph']:
            for f in exp['files']:
                if f['file_type'] in param_list['files.file_type']:
                    files.append('{host_url}{href}'.format(
                        host_url=request.host_url,
                        href=f['href']
                    ))
    else:
        for exp in results['@graph']:
            for f in exp['files']:
                files.append('{host_url}{href}'.format(
                    host_url=request.host_url,
                    href=f['href']
                ))
    return Response(
        content_type='text/plain',
        body='\n'.join(files),
        content_disposition='attachment; filename="%s"' % 'files.txt'
    )


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
    seen = set()
    deduped_nodes = [n for n in nodes if not (n in seen or seen.add(n))]
    return u','.join(u'{}'.format(n) for n in deduped_nodes)


def format_row(columns):
    """Format a list of text columns as a tab-separated byte string."""
    return b'\t'.join([bytes_(c, 'utf-8') for c in columns]) + b'\r\n'


@view_config(route_name='report_download', request_method='GET')
def report_download(context, request):
    types = request.params.getall('type')
    if len(types) != 1:
        msg = 'Report view requires specifying a single type.'
        raise HTTPBadRequest(explanation=msg)

    # Make sure we get all results
    request.GET['limit'] = 'all'

    type = types[0]
    schemas = [request.registry[TYPES][type].schema]
    columns = list_visible_columns_for_schemas(request, schemas)
    type = type.replace("'", '')

    def format_header(seq):
        newheader="%s\t%s%s?%s\r\n" % (currenttime, request.host_url, '/report/', request.query_string)
        return(bytes(newheader, 'utf-8'))
       

    # Work around Excel bug; can't open single column TSV with 'ID' header
    if len(columns) == 1 and '@id' in columns:
        columns['@id']['title'] = 'id'

    header = [column.get('title') or field for field, column in columns.items()]

    def generate_rows():
        yield format_header(header)
        yield format_row(header)
        for item in iter_search_results(context, request):
            values = [lookup_column_value(item, path) for path in columns]
            yield format_row(values)

    # Stream response using chunked encoding.
    request.response.content_type = 'text/tsv'
    request.response.content_disposition = 'attachment;filename="%s"' % '%(doctype)s Report %(yyyy)s/%(mm)s/%(dd)s.tsv' % {'yyyy': currenttime.year, 'mm': currenttime.month, 'dd': currenttime.day, 'doctype': type} #change file name
    request.response.app_iter = generate_rows()
    return request.response
