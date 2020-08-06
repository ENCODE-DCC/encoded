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
    config.add_route('peak_metadata', '/peak_metadata/{search_params}/{tsv}')
    config.add_route('report_download', '/report.tsv')
    config.scan(__name__)


_excluded_columns = ('Restricted', 'No File Available')

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
