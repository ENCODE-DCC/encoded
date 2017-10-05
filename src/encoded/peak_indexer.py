import urllib3
import io
import gzip
import csv
import logging
import collections
from pyramid.view import view_config
from sqlalchemy.sql import text
from elasticsearch.exceptions import (
    NotFoundError
)
from snovault import DBSESSION, COLLECTIONS
#from snovault.storage import (
#    TransactionRecord,
#)
from snovault.elasticsearch.indexer import (
    IndexerState,
    Indexer
)

from snovault.elasticsearch.interfaces import (
    ELASTIC_SEARCH,
    SNP_SEARCH_ES,
    INDEXER,
)
#import copy

SEARCH_MAX = 99999  # OutOfMemoryError if too high
log = logging.getLogger(__name__)


# Species and references being indexed
SUPPORTED_ASSEMBLIES = ['hg19', 'mm10', 'mm9', 'GRCh38']

ENCODED_ALLOWED_FILE_FORMATS = [ 'bed']
ENCODED_ALLOWED_STATUSES = [ 'released' ]
RESIDENT_DATASETS_KEY = 'resident_datasets'  # in regions_es, keep track of what datsets are resident in one place

# assay_term_name: file_property: allowed list
ENCODED_REGION_REQUIREMENTS = {
    'ChIP-seq': {
        'output_type': ['optimal idr thresholded peaks'],
        'file_format': ['bed']
    },
    'DNase-seq': {
        'file_type': ['bed narrowPeak'],
        'file_format': ['bed']
    },
    'eCLIP': {
        'file_type': ['bed narrowPeak'],
        'file_format': ['bed']
    }
}


def includeme(config):
    config.add_route('index_file', '/index_file')
    #config.add_route('index_regions', '/index_regions')  # should rename to index_regions
    config.scan(__name__)
    registry = config.registry
    registry['region'+INDEXER] = RegionIndexer(registry)

def tsvreader(file):
    reader = csv.reader(file, delimiter='\t')
    for row in reader:
        yield row

# Mapping should be generated dynamically for each assembly type


def get_mapping(assembly_name='hg19'):
    return {
        assembly_name: {
            '_all': {
                'enabled': False
            },
            '_source': {
                'enabled': True
            },
            'properties': {
                'uuid': {
                    'type': 'string',
                    'index': 'not_analyzed'
                },
                'positions': {
                    'type': 'nested',
                    'properties': {
                        'start': {
                            'type': 'long'
                        },
                        'end': {
                            'type': 'long'
                        }
                    }
                }
            }
        }
    }


def index_settings():
    return {
        'index': {
            'number_of_shards': 1
        }
    }


# Region indexer 2.0
# Desired:  Cycle every 1 hour
# Plan:
# 1) get list of all uuids of datasets of ALLOWED_FILE_FORMATS
# 2) walk through uuid list querying encoded for each doc[embedded]
#    3) Walk through embedded files
#       4) If file passes required tests (e.g. bed, released, DNase narrowpeak) AND not in regions_es, put in regions_es
#       5) If file does not pass tests                                          AND     IN regions_es, remove from regions_es
# Needed:
# regulomeDb versions of ENCODED_ALLOWED_FILE_FORMATS, ENCODED_ALLOWED_STATUSES, add_encoded_to_regions_es()

class RegionsState(IndexerState):
    # Accepts handoff of uuids from primary indexer. Keeps track of uuids and secondary_indexer state by cycle.
    def __init__(self, es, key):
        super(RegionsState, self).__init__(es,key, title='regions')
        self.files_added_set    = self.title + '_files_added'
        self.files_dropped_set  = self.title + '_files_dropped'
        self.success_set        = self.files_added_set
        self.cleanup_last_cycle.extend([self.files_added_set,self.files_dropped_set])  # Clean up at beginning of next cycle
        # DO NOT INHERIT! These keys are for passing on to other indexers
        self.followup_prep_list = None                        # No followup to a following indexer
        self.staged_cycles_list = None                        # Nothing is passed from another indexer

    def file_added(self, uuid):
        self.list_extend(self.files_added_set, [uuid])

    def file_dropped(self, uuid):
        self.list_extend(self.files_added_set, [uuid])

    def finish_cycle(self, state, errors=None):
        '''Every indexing cycle must be properly closed.'''

        if errors:  # By handling here, we avoid overhead and concurrency issues of uuid-level accounting
            self.add_errors(errors)

        # cycle-level accounting so todo => done => last in this function
        #self.rename_objs(self.todo_set, self.done_set)
        #done_count = self.get_count(self.todo_set)
        cycle_count = state.pop('cycle_count', None)
        self.rename_objs(self.todo_set, self.last_set)

        added = self.get_count(self.files_added_set)
        dropped = self.get_count(self.files_dropped_set)
        state['indexed'] = added + dropped

        #self.rename_objs(self.done_set, self.last_set)   # cycle-level accounting so todo => done => last in this function
        self.delete_objs(self.cleanup_this_cycle)
        state['status'] = 'done'
        state['cycles'] = state.get('cycles', 0) + 1
        state['cycle_took'] = self.elapsed('cycle')

        self.put(state)

        return state


def encoded_experiment_uuids(request, restrict_to_assays=[]):
    query = "select distinct(resources.rid) from resources, propsheets where resources.rid = propsheets.rid and resources.item_type='experiment'"  # ?? 'dataset' ??
    if len(restrict_to_assays) == 1:
        query += " and propsheets.properties->>'assay_term_name' = '%s'" % restrict_to_assays[0]
    elif len(restrict_to_assays) > 1:
        assays = "('%s'" % (restrict_to_assays[0])
        for assay in restrict_to_assays[1:]:
            assays += ", '%s'" % assay
        assays += ")"
        query += " and propsheets.properties->>'assay_term_name' IN %s" % assays
    stmt = text(query + ";")
    connection = request.registry[DBSESSION].connection()
    uuids = connection.execute(stmt)
    return [str(item[0]) for item in uuids]

#@view_config(route_name='index_regions', request_method='POST', permission="index")  # Should rename to index_regions
@view_config(route_name='index_file', request_method='POST', permission="index")
def index_regions(request):
    encoded_es = request.registry[ELASTIC_SEARCH]
    encoded_INDEX = request.registry.settings['snovault.elasticsearch.index']
    #request.datastore = 'database'
    dry_run = request.json.get('dry_run', False)
    indexer = request.registry['region'+INDEXER]

    # keeping track of state
    state = RegionsState(encoded_es,encoded_INDEX)  # Consider putting this in regions es instead of encoded es
    result = state.get_initial_state()

    assays = list(ENCODED_REGION_REQUIREMENTS.keys())
    #log.debug("Regions indexer has begun...")

    uuids = encoded_experiment_uuids(request,assays)
    uuid_count = len(uuids)
    if uuid_count > 0 and not dry_run:

        result = state.start_cycle(uuids, result)
        errors = indexer.update_objects(request, uuids)
        result = state.finish_cycle(result, errors)
        if result['indexed'] > 0:
            log.warn("Regions indexer added %d file(s)" % result['indexed']) # TODO: change to info

    return result


class RegionIndexer(Indexer):
    def __init__(self, registry):
        super(RegionIndexer, self).__init__(registry)
        self.encoded_es    = registry[ELASTIC_SEARCH]    # yes this is self.es but we want clarity
        self.encoded_INDEX = registry.settings['snovault.elasticsearch.index']  # yes this is self.index, but clarity
        self.regions_es    = registry[SNP_SEARCH_ES]
        self.residents_index = RESIDENT_DATASETS_KEY
        self.state = RegionsState(self.encoded_es,self.encoded_INDEX)  # WARNING, race condition is avoided because there is only one worker

    def get_from_es(request, comp_id):
        '''Returns composite json blob from elastic-search, or None if not found.'''
        return None

    def update_objects(self, request, uuids):
        errors = []
        for i, uuid in enumerate(uuids):
            error = self.update_object(request, uuid)
            if error is not None:
                errors.append(error)
            if (i + 1) % 50 == 0:
                log.info('Indexing %d', i + 1)

        return errors

    def update_object(self, request, dataset_uuid):
        try:
            dataset_obj = self.encoded_es.get(index=self.encoded_INDEX, id=str(dataset_uuid)).get('_source',{}).get('embedded')
        except:
            #log.debug("dataset is not found??? %s",dataset_uuid)
            # Not an error if it wasn't found.
            return

        # TODO: add means to force full reindexing
        # TODO: add means to selectively reindex one dataset
        # TODO: add case where files are never dropped (when demos share test server this might be necessary)
        if not self.encoded_candidate_dataset(dataset_obj):
            #log.debug("dataset is not candidate: %s",dataset_uuid)
            return  # Note that if a dataset is no longer a candidate but it had files in regions es, they won't get removed.

        assay_term_name = dataset_obj.get('assay_term_name')
        if assay_term_name is None:
            return

        for file_obj in dataset_obj.get('files',[]):
            if file_obj.get('file_format') not in ENCODED_ALLOWED_FILE_FORMATS:
                #log.debug("file is not bed: %s",file_obj['@id'])
                continue  # Note: if file_format changed to not allowed but file already in regions es, it doesn't get removed.

            file_uuid = file_obj['uuid']

            if self.encoded_candidate_file(file_obj, assay_term_name):
                #log.warn("file is not candidate: %s",file_obj['@id'])
                if self.in_regions_es(file_uuid):
                    continue
                if self.add_encoded_file_to_regions_es(request, file_obj):
                    log.warn("added file: %s %s" % (dataset_obj['accession'],file_obj['href']))  # warn to see on demo
                    self.state.file_added(file_uuid)

            else:
                if not self.in_regions_es(file_uuid):
                    continue
                if self.remove_from_regions_es(file_uuid):
                    log.warn("dropped file: %s %s" % (dataset_obj['accession'],file_obj['@id']))  # warn to see on demo
                    self.state.file_dropped(file_uuid)

        # TODO: gather and return errors

    def encoded_candidate_file(self, file_obj, assay_term_name):
        '''returns True if an encoded file should be in regions es'''
        if file_obj.get('status', 'imagined') not in ENCODED_ALLOWED_STATUSES:
            return False
        if file_obj.get('href') is None:
            return False

        assembly = file_obj.get('assembly','unknown')
        if assembly == 'mm10-minimal':        # Treat mm10-minimal as mm10
            assembly = 'mm10'
        if assembly not in SUPPORTED_ASSEMBLIES:
            return False

        required = ENCODED_REGION_REQUIREMENTS.get(assay_term_name,{})
        if not required:
            return False

        for prop in list(required.keys()):
            val = file_obj.get(prop)
            if val is None:
                return False
            if val not in required[prop]:
                return False

        return True

    def encoded_candidate_dataset(self, dataset):
        '''returns True if an encoded dataset may have files that should be in regions es'''
        if 'Experiment' not in dataset['@type']:  # Only experiments?
            return False

        if dataset.get('assay_term_name','unknown') not in list(ENCODED_REGION_REQUIREMENTS.keys()):
            return False

        if len(dataset.get('files',[])) == 0:
            return False
        return True

    def in_regions_es(self, id):
        '''returns True if an id is in regions es'''
        #return False # DEBUG
        try:
            doc = self.regions_es.get(index=self.residents_index, doc_type='default', id=str(id)).get('_source',{})
            if doc:
                return True
        except NotFoundError:
            return False
        except:
            #raise
            pass

        return False


    def remove_from_regions_es(self, id):
        '''Removes all traces of an id (usually uuid) from region search elasticsearch index.'''
        #return True # DEBUG
        try:
            doc = self.regions_es.get(index=self.residents_index, doc_type='default', id=str(id)).get('_source',{})
            if not doc:
                return False
        except:
            # TODO: add a warning?
            return False  # Will try next cycle

        for chrom in doc['chroms']:
            try:
                self.regions_es.delete(index=chrom, doc_type=doc['assembly'], id=str(uuid))
            except:
                # TODO: add a warning.
                return False # Will try next cycle

        try:
            self.regions_es.delete(index=self.residents_index, doc_type='default', id=str(uuid))
        except:
            # TODO: add a warning.
            return False # Will try next cycle

        return True


    def add_to_regions_es(self, id, assembly, regions):
        '''Given regions from some source (most likely encoded file) loads the data into region search es'''
        #return True # DEBUG
        for key in regions:
            doc = {
                'uuid': str(id),
                'positions': regions[key]
            }
            # Could be a chrom never seen before!
            if not self.regions_es.indices.exists(key):
                self.regions_es.indices.create(index=key, body=index_settings())

            if not self.regions_es.indices.exists_type(index=key, doc_type=assembly):
                self.regions_es.indices.put_mapping(index=key, doc_type=assembly, body=get_mapping(assembly))

            self.regions_es.index(index=key, doc_type=assembly, body=doc, id=str(id))

        # Now add dataset to residency list
        doc = {
            'uuid': str(id),
            'assembly': assembly,
            'chroms': list(regions.keys())
        }
        # Make sure there is an index set up to handle whether uuids are resident
        if not self.regions_es.indices.exists(self.residents_index):
            self.regions_es.indices.create(index=self.residents_index, body=index_settings())

        if not self.regions_es.indices.exists_type(index=self.residents_index, doc_type='default'):
            mapping = {'default': {"_all":    {"enabled": False},"_source": {"enabled": True},}}
            self.regions_es.indices.put_mapping(index=self.residents_index, doc_type='default', body=mapping)

        self.regions_es.index(index=self.residents_index, doc_type='default', body=doc, id=str(id))
        return True

    def add_encoded_file_to_regions_es(self, request, file_obj):
        '''Given an encoded file object, reads the file to create regions data then loads that into region search es.'''
        #return True # DEBUG

        assembly = file_obj.get('assembly','unknown')
        if assembly == 'mm10-minimal':        # Treat mm10-minimal as mm10
            assembly = 'mm10'
        if assembly not in SUPPORTED_ASSEMBLIES:
            return False

        urllib3.disable_warnings()
        http = urllib3.PoolManager()
        r = http.request('GET', request.host_url + file_obj['href'])
        if r.status != 200:
            return False
        file_in_mem = io.BytesIO()
        file_in_mem.write(r.data)
        file_in_mem.seek(0)
        r.release_conn()

        file_data = {}
        if file_obj['file_format'] == 'bed':
            with gzip.open(file_in_mem, mode='rt') as file:
                for row in tsvreader(file):
                    chrom, start, end = row[0].lower(), int(row[1]), int(row[2])
                    if isinstance(start, int) and isinstance(end, int):
                        if chrom in file_data:
                            file_data[chrom].append({
                                'start': start + 1,
                                'end': end + 1
                            })
                        else:
                            file_data[chrom] = [{'start': start + 1, 'end': end + 1}]
                    else:
                        log.warn('positions are not integers, will not index file')
        ### else:  Other file types?

        if file_data:
            return self.add_to_regions_es(file_obj['uuid'], assembly, file_data)

        return False
