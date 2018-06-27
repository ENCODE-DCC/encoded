from collections import OrderedDict
from pyramid.compat import bytes_
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config
from pyramid.response import Response
from snovault import TYPES
from snovault.util import simple_path_ids
from snovault.elasticsearch.interfaces import SNP_SEARCH_ES
from urllib.parse import (
    parse_qs,
    urlencode,
)
from .search import iter_search_results
from .search import list_visible_columns_for_schemas
import csv
import io
import json
import time  # DEBUG: timing
import datetime
from .region_atlas import RegulomeAtlas

import logging
log = logging.getLogger(__name__)

currenttime = datetime.datetime.now()


def includeme(config):
    config.add_route('batch_download', '/batch_download/{search_params}')
    config.add_route('metadata', '/metadata/{search_params}/{tsv}')
    config.add_route('peak_metadata', '/peak_metadata/{search_params}/{tsv}')
    config.add_route('regulome_download', '/regulome_download/{tsv}')
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
    ('Biosample organism', ['replicates.library.biosample.organism.scientific_name']),
    ('Biosample treatments', ['replicates.library.biosample.treatments.treatment_term_name']),
    ('Biosample treatments amount', ['replicates.library.biosample.treatments.amount',
                                     'replicates.library.biosample.treatments.amount_units']),
    ('Biosample treatments duration', ['replicates.library.biosample.treatments.duration',
                                       'replicates.library.biosample.treatments.duration_units']),
    ('Experiment target', ['target.name']),
    ('Library made from', ['replicates.library.nucleic_acid_term_name']),
    ('Library depleted in', ['replicates.library.depleted_in_term_name']),
    ('Library extraction method', ['replicates.library.extraction_method']),
    ('Library lysis method', ['replicates.library.lysis_method']),
    ('Library crosslinking method', ['replicates.library.crosslinking_method']),
    ('Library strand specific', ['replicates.library.strand_specificity']),
    ('Experiment date released', ['date_released']),
    ('Project', ['award.project']),
    ('RBNS protein concentration', ['files.replicate.rbns_protein_concentration',
                                    'files.replicate.rbns_protein_concentration_units']),
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
    bio_reps = None
    for f in experiment_json['files']:
        if file_json['uuid'] == f['uuid']:
            bio_reps = f.get('biological_replicates')
    accessions = set()
    for replicate in experiment_json.get('replicates', []):
        if bio_reps and replicate.get('biological_replicate_number', 0) not in bio_reps:
            continue
        try:
            accession = replicate['library']['biosample']['accession']
            if accession:
                accessions.add(accession)
        except Exception:
            accessions = set()  # pass
    return ', '.join(list(accessions))


def get_regulome_evidence_links(request, assembly, chrom, start, end):
    regulome_link = '{host_url}/regulome_download/regulome_evidence_{assembly}_{chrom}_{start}_{end}'.format(
        host_url=request.host_url,
        assembly=assembly,
        chrom=chrom,
        start=start,
        end=end
    )
    return [regulome_link + '.bed', regulome_link + '.json']


def get_peak_metadata_links(request, assembly, chrom, start, end):
    page = request.path.split('/')[1]
    if page.startswith('regulome'):
        return get_regulome_evidence_links(request, assembly, chrom, start, end)

    if request.matchdict.get('search_params'):
        search_params = request.matchdict['search_params']
    else:
        search_params = request.query_string
    # if regulome:
    #    search_params += '&regulome=1'

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
    regulome = param_list.pop('regulome', None)
    target_page = 'region-search'
    if regulome:
        target_page = 'regulome-search'

    param_list['field'] = []
    header = ['assay_term_name', 'coordinates', 'target.label', 'biosample.accession',
              'file.accession', 'experiment.accession']
    param_list['limit'] = ['all']
    path = '/{}/?{}&{}'.format(target_page, urlencode(param_list, True), 'referrer=peak_metadata')
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
                coordinates = '{}:{}-{}'.format(row['_index'], hit['_source']['start'],
                                                hit['_source']['end'])
                file_accession = file_json['accession']
                experiment_accession = experiment_json['accession']
                assay_name = experiment_json.get('assay_term_name', '')
                if assay_name == '' and regulome:
                    assay_name = experiment_json.get('annotation_type', '')
                target_name = experiment_json.get('target', {}).get('label', '')
                biosample_accession = get_biosample_accessions(file_json, experiment_json)
                data_row.extend([assay_name, coordinates, target_name, biosample_accession,
                                 file_accession, experiment_accession])
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


@view_config(route_name='regulome_download', request_method='GET')
def regulome_download(context, request):
    begin = time.time()  # DEBUG: timing
    format_json = request.url.endswith('.json')
    atlas = RegulomeAtlas(request.registry[SNP_SEARCH_ES])
    try:
        page_parts = request.url.split('/')[-1].split('.')[0].split('_')
        reg_format = page_parts[1]
        assembly = page_parts[2]
        chrom = page_parts[3]
        start = int(page_parts[4])
        end = int(page_parts[5])
    except Exception:
        log.error('Could not parse: ' + request.url)
        return None
    if assembly is None or chrom is None or start == 0 or end == 0:
        log.error('Requesting regulome_download without assembly, chrom, start, end')
        return

    def iter_snps(format_json):
        if format_json:
            header = '{\n'
        else:
            columns = ['#chrom', 'start', 'end', 'rsid', 'num_score', 'score']  # bed 5 +
            columns.extend(atlas.evidence_categories())
            header = '\t'.join(columns) + '\n'
        yield bytes(header, 'utf-8')
        count = 0
        for snp in atlas.iter_scored_snps(assembly, chrom, start, end):
            count += 1
            coordinates = '{}:{}-{}'.format(snp['chrom'], snp['start'], snp['end'])
            if format_json:
                formatted_snp = json.dumps({snp.get('rsid', coordinates): snp},
                                           sort_keys=True)[1:-1] + ','
            else:
                score = snp.get('score', '')
                num_score = atlas.numeric_score(score)    # - 1 because bed format is 'half open'
                formatted_snp = "%s\t%d\t%d\t%s\t%d\t%s" % \
                                (snp['chrom'], snp['start'] - 1, snp['end'],
                                 snp.get('rsid', coordinates), num_score, score)
                case = atlas.make_a_case(snp)
                for category in atlas.evidence_categories():  # in order
                    formatted_snp += '\t%s' % case.get(category, '')
            yield bytes(formatted_snp + '\n', 'utf-8')
        took = '%.3f' % (time.time() - begin)    # DEBUG: timing
        if format_json:
            yield bytes('"took": %s,\n"count": %d\n}\n' % (took, count), 'utf-8')
        else:
            yield bytes('# took: %s, count: %d\n' % (took, count), 'utf-8')

    def iter_regions(format_json):
        if format_json:
            header = '{\n'
        else:
            header = '\t'.join(['#chrom', 'start', 'end', 'num_score']) + '\n'  # bedGraph
        yield bytes(header, 'utf-8')
        count = 0
        for (sig_start, sig_end, sig_score) in atlas.iter_scored_signal(assembly, chrom,
                                                                        start, end):
            count += 1
            if format_json:
                sig_json = {'chrom': chrom, 'start': sig_start, 'end': sig_end,
                            'num_score': sig_score}
                formatted_sig = json.dumps(sig_json, sort_keys=True)[1:-1] + ','
            else:                                          # - 1 because bed format is 'half open'
                formatted_sig = "%s\t%d\t%d\t%d" % (chrom, sig_start - 1, sig_end, sig_score)
            yield bytes(formatted_sig + '\n', 'utf-8')
        took = '%.3f' % (time.time() - begin)    # DEBUG: timing
        if format_json:
            yield bytes('"took": %s,\n"count": %d\n}\n' % (took, count), 'utf-8')
        else:
            yield bytes('# took: %s, count: %d\n' % (took, count), 'utf-8')

    file_root = 'regulome_%s_%s_%s_%d_%d' % (reg_format, assembly, chrom, start, end)

    # Stream response using chunked encoding.
    if format_json:
        request.response.content_type = 'text/plain'   # ?? 'application/json'
        request.response.content_disposition = 'attachment;filename="%s.json"' % (file_root)
    else:
        request.response.content_type = 'text/tsv'
        request.response.content_disposition = 'attachment;filename="%s.bed"' % (file_root)
    if reg_format == 'signal':
        request.response.app_iter = iter_regions(format_json)
    else:  # reg_format == 'evidence'
        request.response.app_iter = iter_snps(format_json)
    return request.response


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
        if experiment_json.get('files', []):
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

    exp_files = (
            exp_file
            for exp in results['@graph']
            for exp_file in exp.get('files', [])
    )

    for exp_file in exp_files:
        if not file_type_param_list(exp_file, param_list):
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


def file_type_param_list(exp_file, param_list):
    if 'files.file_type' in param_list:
        if not exp_file['file_type'] in param_list.get('files.file_type', []):
            return False
    return True


def restricted_files_present(exp_file):
    if exp_file.get('restricted', False) is True:
        return True
    return False


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
        newheader = "%s\t%s%s?%s\r\n" % (currenttime, request.host_url, '/report/',
                                         request.query_string)
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
    request.response.content_disposition = 'attachment;filename="%s"' % \
                                           '%(doctype)s Report %(yyyy)s/%(mm)s/%(dd)s.tsv' % \
                                           {'yyyy': currenttime.year, 'mm': currenttime.month,
                                            'dd': currenttime.day, 'doctype': type}
    request.response.app_iter = generate_rows()
    return request.response
