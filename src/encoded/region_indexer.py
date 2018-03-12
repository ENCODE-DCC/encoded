import urllib3
import io
import gzip
import csv
import logging
import collections
import json
import requests
import os
from pyramid.view import view_config
from sqlalchemy.sql import text
from elasticsearch.exceptions import (
    NotFoundError
)
from elasticsearch.helpers import scan
from snovault import DBSESSION, COLLECTIONS
#from snovault.storage import (
#    TransactionRecord,
#)
from snovault.elasticsearch.indexer import (
    Indexer
)
from snovault.elasticsearch.indexer_state import (
    SEARCH_MAX,
    IndexerState,
    all_uuids
)

from snovault.elasticsearch.interfaces import (
    ELASTIC_SEARCH,
    SNP_SEARCH_ES,
    INDEXER,
)

log = logging.getLogger(__name__)


# Region indexer 2.0
# What it does:
# 1) get list of uuids of primary indexer and filter down to datasets covered
# 2) walk through uuid list querying encoded for each doc[embedded]
#    3) Walk through embedded files
#       4) If file passes required tests (e.g. bed, released, DNase narrowpeak) AND not in regions_es, put in regions_es
#       5) If file does not pass tests                                          AND     IN regions_es, remove from regions_es
# TODO:
# *) Build similar path for regulome files
# - regulomeDb versions of ENCODED_ALLOWED_FILE_FORMATS, ENCODED_ALLOWED_STATUSES, add_encoded_to_regions_es()

# Species and references being indexed
SUPPORTED_ASSEMBLIES = ['hg19', 'mm10', 'mm9', 'GRCh38']

ENCODED_ALLOWED_FILE_FORMATS = ['bed']
ENCODED_ALLOWED_STATUSES = ['released']
RESIDENT_REGIONSET_KEY = 'resident_regionsets'  # in regions_es, keeps track of what datsets are resident in one place

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

REGULOME_REGION_REQUIREMENTS = {
    'file_format': ['bed']
}

# On local instance, these are the only files that can be downloaded and regionalizable.  Currently only one is!
TESTABLE_FILES = ['ENCFF002COS']  # '/static/test/peak_indexer/ENCFF002COS.bed.gz']
                                  # '/static/test/peak_indexer/ENCFF296FFD.tsv',     # tsv's some day?
                                  # '/static/test/peak_indexer/ENCFF000PAR.bed.gz']


def includeme(config):
    config.add_route('index_region', '/index_region')
    config.scan(__name__)
    config.add_route('_regionindexer_state', '/_regionindexer_state')
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
                    'type': 'keyword' # WARNING: to add local files this must be 'type': 'string'
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
            'number_of_shards': 1,
            'max_result_window': 99999
        }
    }


#def all_regionable_dataset_uuids(registry):
#    # NOTE: this old method needs postgres.  Avoid using postgres
#    return list(all_uuids(registry, types=["experiment"]))


def encoded_regionable_datasets(request, restrict_to_assays=[]):
    '''return list of all dataset uuids eligible for regions'''

    encoded_es = request.registry[ELASTIC_SEARCH]
    encoded_INDEX = request.registry.settings['snovault.elasticsearch.index']

    # basics... only want uuids of experiments that are released
    query = '/search/?type=Experiment&field=uuid&status=released&limit=all'
    # Restrict to just these assays
    for assay in restrict_to_assays:
        query += '&assay_title=' + assay
    results = request.embed(query)['@graph']
    return [ result['uuid'] for result in results ]

def regulome_regionable_datasets(request):

    encoded_es = request.registry[ELASTIC_SEARCH]
    encoded_INDEX = request.registry.settings['snovault.elasticsearch.index']

    # basics... only want uuids of experiments that are released
    query = '/search/?type=Experiment&field=uuid&status=released&internal_tags=RegulomeDB&limit=all'
    results = request.embed(query)['@graph']
    return [ result['uuid'] for result in results ]


class RegionIndexerState(IndexerState):
    # Accepts handoff of uuids from primary indexer. Keeps track of uuids and region_indexer state by cycle.
    def __init__(self, es, key):
        super(RegionIndexerState, self).__init__(es,key, title='region')
        self.files_added_set    = self.title + '_files_added'
        self.files_dropped_set  = self.title + '_files_dropped'
        self.success_set        = self.files_added_set
        self.cleanup_last_cycle.extend([self.files_added_set,self.files_dropped_set])  # Clean up at beginning of next cycle
        # DO NOT INHERIT! These keys are for passing on to other indexers
        self.followup_prep_list = None                        # No followup to a following indexer
        self.staged_cycles_list = None                        # Will take all of primary self.staged_for_regions_list

    def file_added(self, uuid):
        self.list_extend(self.files_added_set, [uuid])

    def file_dropped(self, uuid):
        self.list_extend(self.files_added_set, [uuid])

    def all_indexable_uuids_set(self, request):
        '''returns set of uuids. allowing intersections.'''
        assays = list(ENCODED_REGION_REQUIREMENTS.keys())
        uuids = set(encoded_regionable_datasets(request, assays))
        uuids |= set(regulome_regionable_datasets(request))
        return uuids  # Uses elasticsearch query

    def all_indexable_uuids(self, request):
        '''returns list of uuids pertinant to this indexer.'''
        return list(self.all_indexable_uuids_set(request))

    def priority_cycle(self, request):
        '''Initial startup, reindex, or interupted prior cycle can all lead to a priority cycle.
           returns (priority_type, uuids).'''
        # Not yet started?
        initialized = self.get_obj("indexing")  # http://localhost:9200/snovault/meta/indexing
        if not initialized:
            self.delete_objs([self.override, self.staged_for_regions_list])
            state = self.get()
            state['status'] = 'uninitialized'
            self.put(state)
            return ("uninitialized", [])  # primary indexer will know what to do and region indexer should do nothing yet

        # Is a full indexing underway
        primary_state = self.get_obj("primary_indexer")
        if primary_state.get('cycle_count',0) > SEARCH_MAX:
            return ("uninitialized", [])

        # Rare call for reindexing...
        reindex_uuids = self.reindex_requested(request)
        if reindex_uuids is not None and reindex_uuids != []:
            uuids_count = len(reindex_uuids)
            log.warn('%s reindex of %d uuids requested with force' % (self.state_id, uuids_count))
            return ("reindex", reindex_uuids)

        if self.get().get('status', '') == 'indexing':
            uuids = self.get_list(self.todo_set)
            log.info('%s restarting on %d datasets' % (self.state_id, len(uuids)))
            return ("restart", uuids)

        return ("normal", [])

    def get_one_cycle(self, request):
        '''Returns set of uuids to do this cycle and whether they should be forced.'''

        # never indexed, request for full reindex?
        (status, uuids) = self.priority_cycle(request)
        if status == 'uninitialized':
            return ([], False)            # Until primary_indexer has finished, do nothing!

        if len(uuids) > 0:
            if status == "reindex":
                return (uuids, True)
            if status == "restart":  # Restart is fine... just do the uuids over again
                return (uuids, False)
                #log.info('%s skipping this restart' % (self.state_id))
                #state = self.get()
                #state['status'] = "interrupted"
                #self.put(state)
                #return ([], False)
        assert(uuids == [])

        # Normal case, look for uuids staged by primary indexer
        staged_list = self.get_list(self.staged_for_regions_list)
        if not staged_list or staged_list == []:
            return ([], False)            # Nothing to do!
        self.delete_objs([self.staged_for_regions_list])  # TODO: tighten this by adding a locking semaphore

        # we don't need no stinking xmins... just take the whole set of uuids
        uuids = []
        for val in staged_list:
            if val.startswith("xmin:"):
                continue
            else:
                uuids.append(val)

        if len(uuids) > 500:  # some arbitrary cutoff.
            # There is an efficiency trade off examining many non-dataset uuids
            # # vs. the cost of eliminating those uuids from the list ahead of time.
            uuids = list(self.all_indexable_uuids_set(request).intersection(uuids))
            uuid_count = len(uuids)

        return (list(set(uuids)),False)  # Only unique uuids

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

    def display(self, uuids=None):
        display = super(RegionIndexerState, self).display(uuids=uuids)
        display['staged_to_process'] = self.get_count(self.staged_cycles_list)
        display['files_added'] = self.get_count(self.files_added_set)
        display['files_dropped'] = self.get_count(self.files_dropped_set)
        return display


@view_config(route_name='_regionindexer_state', request_method='GET', permission="index")
def regionindexer_state_show(request):
    encoded_es = request.registry[ELASTIC_SEARCH]
    encoded_INDEX = request.registry.settings['snovault.elasticsearch.index']
    regions_es    = request.registry[SNP_SEARCH_ES]
    state = RegionIndexerState(encoded_es,encoded_INDEX)  # Consider putting this in regions es instead of encoded es

    # requesting reindex
    reindex = request.params.get("reindex")
    if reindex is not None:
        msg = state.request_reindex(reindex)
        if msg is not None:
            return msg

    # Requested notification
    who = request.params.get("notify")
    bot_token = request.params.get("bot_token")
    if who is not None or bot_token is not None:
        notices = state.set_notices(request.host_url, who, bot_token, request.params.get("which"))
        if notices is not None:
            return notices

    display = state.display(uuids=request.params.get("uuids"))

    try:
        count = regions_es.count(index=RESIDENT_REGIONSET_KEY, doc_type='default').get('count',0)
        if count:
            display['files_in_index'] = count
    except:
        display['files_in_index'] = 'Not Found'
        pass

    if not request.registry.settings.get('testing',False):  # NOTE: _indexer not working on local instances
        try:
            r = requests.get(request.host_url + '/_regionindexer')
            display['listener'] = json.loads(r.text)
            display['status'] = display['listener']['status']
        except:
            log.error('Error getting /_regionindexer', exc_info=True)

    # always return raw json
    if len(request.query_string) > 0:
        request.query_string = "&format=json"
    else:
        request.query_string = "format=json"
    return display


@view_config(route_name='index_region', request_method='POST', permission="index")
def index_regions(request):
    encoded_es = request.registry[ELASTIC_SEARCH]
    encoded_INDEX = request.registry.settings['snovault.elasticsearch.index']
    request.datastore = 'elasticsearch'  # Let's be explicit
    dry_run = request.json.get('dry_run', False)
    indexer = request.registry['region'+INDEXER]
    uuids = []


    # keeping track of state
    state = RegionIndexerState(encoded_es,encoded_INDEX)
    result = state.get_initial_state()

    (uuids, force) = state.get_one_cycle(request)

    # Note: if reindex=all_uuids then maybe we should delete the entire index
    # On the otherhand, that should probably be left for extreme cases done by hand
    # curl -XDELETE http://region-search-test-v5.instance.encodedcc.org:9200/resident_datasets/
    #if force == 'all':  # Unfortunately force is a simple boolean
    #    try:
    #        r = indexer.regions_es.indices.delete(index='chr*')  # Note region_es and encoded_es may be the same!
    #        r = indexer.regions_es.indices.delete(index=self.residents_index)
    #    except:
    #        pass

    uuid_count = len(uuids)
    if uuid_count > 0 and not dry_run:
        log.info("Region indexer started on %d uuid(s)" % uuid_count)

        result = state.start_cycle(uuids, result)
        errors = indexer.update_objects(request, uuids, force)
        result = state.finish_cycle(result, errors)
        if result['indexed'] == 0:
            log.info("Region indexer added %d file(s) from %d dataset uuids" % (result['indexed'], uuid_count))

        # cycle_took: "2:31:55.543311" reindex all with force (2017-10-16ish)

    state.send_notices()
    return result

NON_REGIONABLE = 0x00
ENCODED_REGIONS_TAG = 'ENCODE'
REGULOME_REGIONS_TAG = 'RegulomeDB'

class RegionIndexer(Indexer):
    def __init__(self, registry):
        super(RegionIndexer, self).__init__(registry)
        self.encoded_es    = registry[ELASTIC_SEARCH]    # yes this is self.es but we want clarity
        self.encoded_INDEX = registry.settings['snovault.elasticsearch.index']  # yes this is self.index, but clarity
        self.regions_es    = registry[SNP_SEARCH_ES]
        self.residents_index = RESIDENT_REGIONSET_KEY
        self.state = RegionIndexerState(self.encoded_es,self.encoded_INDEX)  # WARNING, race condition is avoided because there is only one worker
        self.test_instance = registry.settings.get('testing',False)

    def get_from_es(request, comp_id):
        '''Returns composite json blob from elastic-search, or None if not found.'''
        return None

    def update_object(self, request, dataset_uuid, force):
        request.datastore = 'elasticsearch'  # Let's be explicit

        try:
            # less efficient than going to es directly but keeps methods in one place
            dataset = request.embed(str(dataset_uuid), as_user=True)
        except:
            log.warn("dataset is not found for uuid: %s",dataset_uuid)
            # Not an error if it wasn't found.
            return

        # TODO: add case where files are never dropped (when demos share test server this might be necessary)
        dataset_region_tags = self.candidate_dataset(dataset)
        if not dataset_region_tags:
            return  # Note that if a dataset is no longer a candidate but it had files in regions es, they won't get removed.
        #log.debug("dataset is a candidate: %s", dataset['accession'])

        assay_term_name = dataset.get('assay_term_name')
        if assay_term_name is None:
            return

        files = dataset.get('files',[])
        for afile in files:
            if afile.get('file_format') not in ENCODED_ALLOWED_FILE_FORMATS:
                continue  # Note: if file_format changed to not allowed but file already in regions es, it doesn't get removed.

            file_uuid = afile['uuid']

            file_region_tags = self.candidate_file(afile, assay_term_name, dataset_region_tags)
            if file_region_tags:

                using = ""
                if force:
                    using = "with FORCE"
                    #log.debug("file is a candidate: %s %s", afile['accession'], using)
                    self.remove_from_regions_es(file_uuid)  # remove all regions first
                else:
                    #log.debug("file is a candidate: %s", afile['accession'])
                    if self.in_regions_es(file_uuid):
                        continue

                if self.add_file_to_regions_es(request, assay_term_name, afile, file_region_tags):
                    log.info("added file: %s %s %s", dataset['accession'], afile['href'], using)
                    self.state.file_added(file_uuid)

            else:
                if self.remove_from_regions_es(file_uuid):
                    log.info("dropped file: %s %s %s", dataset['accession'], afile['@id'], using)
                    self.state.file_dropped(file_uuid)

        # TODO: gather and return errors


    def candidate_file(self, afile, assay_term_name, dataset_tags):
        '''returns True if an encoded file should be in regions es'''
        if afile.get('status', 'imagined') not in ENCODED_ALLOWED_STATUSES:
            return None
        if afile.get('href') is None:
            return None

        if self.test_instance:
            if afile['accession'] not in TESTABLE_FILES:
                return None

        assembly = afile.get('assembly','unknown')
        if assembly == 'mm10-minimal':        # Treat mm10-minimal as mm10
            assembly = 'mm10'
        if assembly not in SUPPORTED_ASSEMBLIES:
            return None

        file_tags = []
        if ENCODED_REGIONS_TAG in dataset_tags:  # encoded datasets must have encoded files
            required_enc_props = ENCODED_REGION_REQUIREMENTS.get(assay_term_name,{})
            if required_enc_props:
                failed = False
                for prop in list(required_enc_props.keys()):
                    val = afile.get(prop)
                    if val is None:
                        failed = True
                        break
                    if val not in required_enc_props[prop]:
                        failed = True
                        break
                if not failed:
                    file_tags.append(ENCODED_REGIONS_TAG)

        if REGULOME_REGIONS_TAG in dataset_tags:  # regulome datasets must have regulome files
            failed = False
            for prop in list(ENCODED_REGION_REQUIREMENTS.keys()):
                val = afile.get(prop)
                if val is None:
                    failed = True
                    break
                if val not in ENCODED_REGION_REQUIREMENTS[prop]:
                    failed = True
                    break
            if not failed:
                file_tags.append(REGULOME_REGIONS_TAG)

        return file_tags

    def candidate_dataset(self, dataset):
        '''returns True if an encoded dataset may have files that should be in regions es'''
        if 'Experiment' not in dataset['@type']:  # Only experiments?
            return None

        if len(dataset.get('files',[])) == 0:
            return NON_REGIONABLE

        assay_term_name = dataset.get('assay_term_name')
        if assay_term_name is None:
            return None  # TODO: Regulome has to have assay???

        dataset_tags = []
        if assay_term_name in list(ENCODED_REGION_REQUIREMENTS.keys()):
            dataset_tags.append(ENCODED_REGIONS_TAG)

        if 'RegulomeDB' not in dataset.get('internal_tags',[]):
            dataset_tags.append(REGULOME_REGIONS_TAG)

        return dataset_tags

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
            return False  # Not an error: remove may be called without looking first

        for chrom in doc['chroms']:
            try:
                self.regions_es.delete(index=chrom, doc_type=doc['assembly'], id=str(uuid))
            except:
                #log.error("Region indexer failed to remove %s regions of %s" % (chrom,id))
                return False # Will try next full cycle

        try:
            self.regions_es.delete(index=self.residents_index, doc_type='default', id=str(uuid))
        except:
            log.error("Region indexer failed to remove %s from %s" % (id, self.residents_index))
            return False # Will try next full cycle

        return True


    def add_to_regions_es(self, id, assembly, assay_term_name, regions, region_tags):
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
            'source': region_tags,
            'assay_term_name': assay_term_name,
            'assembly': assembly,
            'chroms': list(regions.keys())
        }
        # Make sure there is an index set up to handle whether uuids are resident
        if not self.regions_es.indices.exists(self.residents_index):
            self.regions_es.indices.create(index=self.residents_index, body=index_settings())

        if not self.regions_es.indices.exists_type(index=self.residents_index, doc_type='default'):
            mapping = {'default': {"enabled": False}}
            self.regions_es.indices.put_mapping(index=self.residents_index, doc_type='default', body=mapping)

        self.regions_es.index(index=self.residents_index, doc_type='default', body=doc, id=str(id))
        return True

    def add_file_to_regions_es(self, request, assay_term_name, afile, region_tags):
        '''Given an encoded file object, reads the file to create regions data then loads that into region search es.'''
        #return True # DEBUG

        assembly = afile.get('assembly','unknown')
        if assembly == 'mm10-minimal':        # Treat mm10-minimal as mm10
            assembly = 'mm10'
        if assembly not in SUPPORTED_ASSEMBLIES:
            return False

        # Special case local instace so that tests can work...
        if self.test_instance:
            #if request.host_url == 'http://localhost':
            # assume we are running in dev-servers
            #href = request.host_url + ':8000' + afile['submitted_file_name']
            href = 'http://www.encodeproject.org' + afile['href']
        else:
            href = request.host_url + afile['href']

        ### Works with localhost:8000
        # NOTE: Using requests instead of http.request which works locally and doesn't require gzip.open
        #r = requests.get(href)
        #if not r or r.status_code != 200:
        #    log.warn("File (%s or %s) not found" % (afile.get('accession', id), href))
        #    return False
        #file_in_mem = io.StringIO()
        #file_in_mem.write(r.text)
        #file_in_mem.seek(0)
        #
        #file_data = {}
        #if afile['file_format'] == 'bed':
        #    for row in tsvreader(file_in_mem):
        #        chrom, start, end = row[0].lower(), int(row[1]), int(row[2])
        #        if isinstance(start, int) and isinstance(end, int):
        #            if chrom in file_data:
        #                file_data[chrom].append({
        #                    'start': start + 1,
        #                    'end': end + 1
        #                })
        #            else:
        #                file_data[chrom] = [{'start': start + 1, 'end': end + 1}]
        #        else:
        #            log.warn('positions are not integers, will not index file')
        ##else:  Other file types?

        ### Works with http://www.encodeproject.org
        # Note: this reads the file into an in-memory byte stream.  If files get too large,
        # We could replace this with writing a temp file, then reading it via gzip and tsvreader.
        urllib3.disable_warnings()
        http = urllib3.PoolManager()
        r = http.request('GET', href)
        if r.status != 200:
            log.warn("File (%s or %s) not found" % (afile.get('accession', id), href))
            return False
        file_in_mem = io.BytesIO()
        file_in_mem.write(r.data)
        file_in_mem.seek(0)
        r.release_conn()

        file_data = {}
        if afile['file_format'] == 'bed':
            # NOTE: requests doesn't require gzip but http.request does.
            with gzip.open(file_in_mem, mode='rt') as file:  # localhost:8000 would not require localhost
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
        #else:  Other file types?

        if file_data:
            return self.add_to_regions_es(afile['uuid'], assembly, assay_term_name, file_data, region_tags)

        return False
