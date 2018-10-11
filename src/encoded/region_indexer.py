import datetime
import urllib3
from urllib3.util.retry import Retry
from urllib3.exceptions import MaxRetryError, HTTPError
import io
import gzip
import csv
import logging
import json
import requests
import os
from pkg_resources import resource_filename
from pyramid.settings import asbool
from pyramid.view import view_config
from shutil import copyfileobj
from elasticsearch.exceptions import (
    NotFoundError
)
from elasticsearch.helpers import (
    bulk
)
from sqlalchemy.exc import StatementError
from snovault.elasticsearch.indexer import (
    Indexer
)
from snovault.elasticsearch.indexer_state import (
    SEARCH_MAX,
    IndexerState
)

from snovault.elasticsearch.interfaces import (
    ELASTIC_SEARCH,
    SNP_SEARCH_ES,
    INDEXER,
)

log = logging.getLogger(__name__)

# ##################################
# Region indexer 2.0
# What it does:
# 1) get list of uuids of primary indexer and filter down to datasets covered
# 2) walk through uuid list querying encoded for each doc[embedded]
#    3) Walk through embedded files
#       4) If file passes required tests (e.g. bed, released, ...)
#          AND not in regions_es, put in regions_es
#       5) If file does not pass tests
#          AND     IN regions_es, remove from regions_es
# TODO:
# Add score to snp indexing (takes a LONG time to calculate them all)
# Add nearby snps (with scores) to regulome-search, and means to select them!
#     only after scores are in index
# Update resident doc, even when file is already resident.
# ##################################
REGION_INDEXER_SHARDS = 2
RETRYABLE_STATUS = (500, 502, 504,)


# TEMPORARY: limit SNPs to major chroms
SUPPORTED_CHROMOSOMES = [
    'chr1', 'chr2', 'chr3', 'chr4', 'chr5', 'chr6', 'chr7', 'chr8', 'chr9', 'chr10',
    'chr11', 'chr12', 'chr13', 'chr14', 'chr15', 'chr16', 'chr17', 'chr18', 'chr19', 'chr20',
    'chr21', 'chr22', 'chrX', 'chrY']  # chroms are lower case

ALLOWED_FILE_FORMATS = ['bed']
RESIDENT_REGIONSET_KEY = 'resident_regionsets'  # keeps track of what datsets are resident
FOR_REGION_SEARCH = 'region_search'
FOR_REGULOME_DB = 'regulomedb'
FOR_DUAL_USE = 'region_regulomedb'  # doc_type = region*  or *regulomedb

ENCODED_SUPPORTED_ASSEMBLIES = ['hg19', 'mm10', 'mm9', 'GRCh38']
ENCODED_ALLOWED_STATUSES = ['released']
ENCODED_DATASET_TYPES = ['Experiment']
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

REGULOME_SUPPORTED_ASSEMBLIES = ['hg19', 'GRCh38']
REGULOME_ALLOWED_STATUSES = ['released', 'archived', 'in progress']  # no 'in progress' permission!
REGULOME_DATASET_TYPES = ['Experiment', 'Annotation', 'Reference']
REGULOME_COLLECTION_TYPES = ['assay_term_name', 'annotation_type', 'reference_type']
# NOTE: regDB requirements keyed on "collection_type": assay_term_name or else annotation_type
REGULOME_REGION_REQUIREMENTS = {
    'ChIP-seq': {
        'output_type': ['optimal idr thresholded peaks'],
        'file_format': ['bed']
    },
    'binding sites': {
        'output_type': ['curated binding sites'],
        'file_format': ['bed']
    },
    'DNase-seq': {
        'file_type': ['bed narrowPeak'],
        'file_format': ['bed']
    },
    'FAIRE-seq': {
        'file_type': ['bed narrowPeak'],
        'file_format': ['bed']
    },
    'chromatin state': {
        'file_format': ['bed']
    },
    'PWMs': {
        'output_type': ['PWMs'],
        'file_format': ['bed']
    },
    'Footprints': {
        'output_type': ['Footprints'],
        'file_format': ['bed']
    },
    'eQTLs': {
        'file_format': ['bed']
    },
    'dsQTLs': {
        'file_format': ['bed']
    },
    'curated SNVs': {
        'output_type': ['curated SNVs'],
        'file_format': ['bed']
    },
    'index': {  # TODO: reference of variant calls doesn't yet exist.  'index' is temporary
        'output_type': ['variant calls'],
        'file_format': ['bed']
    }
}
# Less than ideal way to recognize the SNP files by submitted_file_name
# SNP_DATASET_UUID = 'ff8dff4e-1de5-446b-8a13-bb6243bc64aa'  # works on demo, but...
SNP_FILES = [
    's3://regulomedb/snp141/snp141_hg19.bed.gz',
    's3://regulomedb/snp141/snp141_GRCh38.bed.gz'
]
SNP_INDEX_PREFIX = 'snp141_'

# If files are too large then they will be copied locally and read
MAX_IN_MEMORY_FILE_SIZE = (700 * 1024 * 1024)  # most files will be below this and index faster
TEMPORARY_REGIONS_FILE = '/tmp/region_temp.bed.gz'

# On local instance, these are the only files that can be downloaded and regionalizable.
# '/static/test/peak_indexer/ENCFF002COS.bed.gz']
# '/static/test/peak_indexer/ENCFF296FFD.tsv',     # tsv's some day?
# '/static/test/peak_indexer/ENCFF000PAR.bed.gz']
# Currently only one is!
TESTABLE_FILES = ['ENCFF002COS']


def includeme(config):
    config.add_route('index_region', '/index_region')
    config.scan(__name__)
    config.add_route('_regionindexer_state', '/_regionindexer_state')
    registry = config.registry
    registry['region' + INDEXER] = RegionIndexer(registry)


# Region mapping: index: chr*, doc_type: assembly, _id=uuid
def get_chrom_index_mapping(assembly_name='hg19'):
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
                    'type': 'keyword'  # WARNING: to add local files this must be 'type': 'string'
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


# Files are also put in the resident: index: RESIDENT_REGIONSET_KEY, doc_type: use_type, _id=uuid
def get_resident_mapping(use_type=FOR_DUAL_USE):
    return {use_type: {"enabled": False}}
    # True map: IF we ever want to query by anything other than uuid...
    # return {
    #     use_type: {
    #         '_all':    {'enabled': False},
    #         '_source': {'enabled': True},
    #         'properties': {
    #             'uuid':   {'type': 'keyword'},  # same as _id and file['uuid']
    #             'uses':   {'type': 'keyword'},  # e.g FOR_REGULOME_DB
    #             'chroms': {'type': 'keyword'},  # Used to remove from 'chr*' indices
    #             'snps':   {'type': 'boolean'},  # If present, then this is a file of SNPs
    #             'index':  {'type': 'keyword'},  # If present, the 1 index for this 1 SNP file
    #             'file': {
    #                 'properties': {
    #                     'uuid':     {'type': 'keyword'},  # Yes, redundant
    #                     '@id':      {'type': 'keyword'},
    #                     'assembly': {'type': 'keyword'},
    #                 }
    #             },
    #             'dataset': {
    #                 'properties': {
    #                     'uuid':            {'type': 'keyword'},
    #                     '@id':             {'type': 'keyword'},
    #                     'assay_term_name': {'type': 'keyword'},  # \
    #                     'annotation_type': {'type': 'keyword'},  # - only one will appear
    #                     'reference_type':  {'type': 'keyword'},  # /
    #                     'collection_type': {'type': 'keyword'},  # assay or else annotation
    #                     'target':          {'type': 'keyword'},  # could be array (PWM targets)
    #                     'dataset_type':    {'type': 'keyword'}   # 1st of *_PRIORITIZED_TYPES
    #                 }
    #             }
    #         }
    #     }
    # }


# SNP mapping index: snp141_hg19, doc_type: chr*, _id=rsid
def get_snp_index_mapping(chrom='chr1'):
    return {
        chrom: {
            '_all': {
                'enabled': False
            },
            '_source': {
                'enabled': True
            },
            'properties': {
                'rsid': {
                    'type': 'keyword'
                },
                'chrom': {
                    'type': 'keyword'
                },
                'start': {
                    'type': 'long'
                },
                'end': {
                    'type': 'long'
                }
            }
        }
    }
# This results in too much stress on elasticsearch: it crashes doring indexing of 60M rsids
#                'suggest' : {
#                    'type' : 'completion'
#                },


def snp_index_key(assembly):
    return SNP_INDEX_PREFIX + assembly.lower()


def index_settings():
    return {
        'index': {
            'number_of_shards': REGION_INDEXER_SHARDS,
            'max_result_window': SEARCH_MAX
        }
    }


def encoded_regionable_datasets(request, restrict_to_assays=[]):
    '''return list of all dataset uuids eligible for regions'''
    # basics... only want uuids of experiments that are released
    query = '/search/?type=Experiment&field=uuid&limit=all'
    for status in ENCODED_ALLOWED_STATUSES:
        query += '&status=' + status
    # Restrict to just these assays
    for assay in restrict_to_assays:
        query += '&assay_title=' + assay
    results = request.embed(query)['@graph']
    return [result['uuid'] for result in results]


def regulome_regionable_datasets(request):
    query = '/search/?type=Dataset&field=uuid&limit=all'
    query += '&internal_tags=RegulomeDB'
    for status in REGULOME_ALLOWED_STATUSES:
        query += '&status=' + status
    results = request.embed(query)['@graph']
    return [result['uuid'] for result in results]


def regulome_collection_type(dataset):
    for prop in REGULOME_COLLECTION_TYPES:
        if prop in dataset:
            return dataset[prop]
    return None


class RemoteReader(object):
    # Tools for reading remote files

    def __init__(self):
        self.temp_file = TEMPORARY_REGIONS_FILE
        self.max_memory = MAX_IN_MEMORY_FILE_SIZE

    def readable_file(self, request, afile):
        '''returns either an in memory file or a temp file'''

        # Special case local instance so that tests can work...
        if asbool(request.registry.settings.get('testing')):
            filedir = resource_filename('encoded', 'tests/data/files/')
            filename = os.path.basename(afile['href'])
            file_to_read = os.path.join(filedir, filename)
            if not os.path.isfile(file_to_read):
                log.warn("File (%s or %s) not found" % (
                    afile.get('accession', id), afile['href']
                ))
                return False
            return file_to_read

        href = request.host_url + afile['href']
        # TODO: support for remote access for big files (could do bam and vcf as well)
        # if afile.get('file_format') in ['bigBed', 'bigWig']:
        #     return href
        # assert(afile.get('file_format') == 'bed')

        # Note: this reads the file into an in-memory byte stream.  If files get too large,
        # We could replace this with writing a temp file, then reading it via gzip and tsvreader.
        urllib3.disable_warnings()
        http = urllib3.PoolManager()

        # use afile.get(file_size) to decide between in mem file or temp file
        file_to_read = None
        if afile.get('file_size', 0) > self.max_memory:
            with http.request('GET', href, preload_content=False) \
                    as r, open(self.temp_file, 'wb') as out_file:
                copyfileobj(r, out_file)
            file_to_read = self.temp_file
            log.warn('Wrote %s to %s', href, file_to_read)
        else:
            try:
                r = http.request('GET', href, retries=Retry(status_forcelist=RETRYABLE_STATUS,
                                                            backoff_factor=1))
            except MaxRetryError as e:
                log.warn(e.reason)
                log.warn("File (%s or %s) not found" % (afile['@id'], href))
                raise
            else:
                if r.status != 200:
                    http_error_msg = "STATUS %s: File (%s or %s) not found" % (r.status, afile['@id'], href)
                    log.warn(http_error_msg)
                    raise HTTPError(http_error_msg)
            file_in_mem = io.BytesIO()
            file_in_mem.write(r.data)
            file_in_mem.seek(0)
            file_to_read = file_in_mem
        r.release_conn()

        return file_to_read

    @staticmethod
    def tsv(file_handle):
        reader = csv.reader(file_handle, delimiter='\t')
        for row in reader:
            yield row

    @staticmethod
    def region(row):
        '''Read a region from an in memory row and returns chrom and document to index.'''
        chrom, start, end = row[0], int(row[1]), int(row[2])
        return (chrom, {'start': start + 1, 'end': end})  # bed loc 'half-open', but we close it !

    @staticmethod
    def snp(row):
        '''Read a SNP from an in memory row and returns chrom and document to index.'''
        chrom, start, end, rsid = row[0], int(row[1]), int(row[2]), row[3]
        if start == end:
            end = end + 1
        return (chrom, {'rsid': rsid, 'chrom': chrom, 'start': start + 1, 'end': end})

    # TODO: support bigBeds
    # def bb_region(self, row):
    #     '''Read a region from a bigBed file read with "pyBigWig" and returns document to index.'''
    #     start, end = int(row[0]), int(row[1])
    #     return {'start': start + 1, 'end': end}  # bed loc 'half-open', but we will close it

    # TODO: support bigBeds
    # def bb_snp(self, row):
    #     '''Read a SNP from a bigBed file read with "pyBigWig"  and returns document to index.'''
    #     start, end = int(row[0]), int(row[1])
    #     extras = row[3].split('\t')
    #     rsid = extras[0]
    #     num_score = int(extras[1])
    #     score = extras[2]
    #     start, end, rsid = row[0], int(row[0]), int(row[2]), row[3]
    #     return {'rsid': rsid, 'chrom': chrom, 'start': start + 1, 'end': end,
    #             'num_score': num_score, 'score': score}


class RegionIndexerState(IndexerState):
    # Accepts handoff of uuids from primary indexer. Keeps track of uuids and state by cycle.
    def __init__(self, es, key):
        super(RegionIndexerState, self).__init__(es, key, title='region')
        self.files_added_set = self.title + '_files_added'
        self.files_dropped_set = self.title + '_files_dropped'
        self.success_set = self.files_added_set
        # Clean these at beginning of next cycle:
        self.cleanup_last_cycle.extend([self.files_added_set, self.files_dropped_set])
        # DO NOT INHERIT! These keys are for passing on to other indexers
        self.followup_prep_list = None  # No followup to a following indexer
        self.staged_cycles_list = None  # Will take all of primary self.staged_for_regions_list

    def file_added(self, uuid):
        self.list_extend(self.files_added_set, [uuid])

    def file_dropped(self, uuid):
        self.list_extend(self.files_added_set, [uuid])

    @staticmethod
    def all_indexable_uuids_set(request):
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
            self.delete_objs([self.override])
            staged_count = self.get_count(self.staged_for_regions_list)
            if staged_count > 0:
                log.warn('Initial indexing handoff almost dropped %d staged uuids' % (staged_count))
            state = self.get()
            state['status'] = 'uninitialized'
            self.put(state)
            return ("uninitialized", [])
            # primary indexer will know what to do and region indexer should do nothing yet

        # Is a full indexing underway
        primary_state = self.get_obj("primary_indexer")
        if primary_state.get('cycle_count', 0) > SEARCH_MAX:
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
        assert(uuids == [])

        # Normal case, look for uuids staged by primary indexer
        staged_list = self.get_list(self.staged_for_regions_list)
        if not staged_list or staged_list == []:
            return ([], False)            # Nothing to do!
        self.delete_objs([self.staged_for_regions_list])  # TODO: tighten with locking semaphore

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

        return (list(set(uuids)), False)  # Only unique uuids

    def finish_cycle(self, state, errors=None):
        '''Every indexing cycle must be properly closed.'''

        if errors:  # By handling here, we avoid overhead/concurrency issues of uuid-level accting
            self.add_errors(errors)

        # cycle-level accounting so todo => done => last in this function
        # self.rename_objs(self.todo_set, self.done_set)
        # done_count = self.get_count(self.todo_set)
        state.pop('cycle_count', None)
        self.rename_objs(self.todo_set, self.last_set)

        added = self.get_count(self.files_added_set)
        dropped = self.get_count(self.files_dropped_set)
        state['indexed'] = added + dropped

        # self.rename_objs(self.done_set, self.last_set)
        # cycle-level accounting so todo => done => last in this function
        self.delete_objs(self.cleanup_this_cycle)
        state['status'] = 'done'
        state['cycles'] = state.get('cycles', 0) + 1
        state['cycle_took'] = self.elapsed('cycle')

        self.put(state)

        return state

    @staticmethod
    def counts(region_es, assemblies=None):
        '''returns counts (region files, regulome files, snp files and all files)'''
        counts = {'all_files': 0}
        for use in [FOR_REGION_SEARCH, FOR_REGULOME_DB, FOR_DUAL_USE]:
            try:
                counts[use] = region_es.count(index=RESIDENT_REGIONSET_KEY,
                                              doc_type=use).get('count', 0)
            except Exception:
                counts[use] = 0
            counts['all_files'] += counts[use]
        counts[FOR_REGION_SEARCH] += counts[FOR_DUAL_USE]
        counts[FOR_REGULOME_DB] += counts[FOR_DUAL_USE]
        counts.pop(FOR_DUAL_USE, None)

        if assemblies:
            counts['SNPs'] = {}
            for assembly in assemblies:
                try:
                    counts['SNPs'][assembly] = \
                        region_es.count(index=snp_index_key(assembly)).get('count', 0)
                except Exception:
                    counts['SNPs'][assembly] = 0

        return counts

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
    regions_es = request.registry[SNP_SEARCH_ES]
    state = RegionIndexerState(encoded_es, encoded_INDEX)
    if not state.get():
        return "%s is not in service." % (state.state_id)
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
    # Note: if reindex=all then maybe we should delete the entire region_index
    # On the otherhand, that should probably be left for extreme cases done by hand
    # curl -XDELETE http://localhost:9201/resident_datasets/
    # curl -XDELETE http://localhost:9201/chr*/

    display = state.display(uuids=request.params.get("uuids"))
    counts = state.counts(regions_es, REGULOME_SUPPORTED_ASSEMBLIES)
    display['files_for_region_search'] = counts.get(FOR_REGION_SEARCH, 0)
    display['files_for_regulomedb'] = counts.get(FOR_REGULOME_DB, 0)
    display['files_in_index'] = counts.get('all_files', 0)
    display['snps_in_index'] = counts.get('SNPs', 0)

    if not request.registry.settings.get('testing', False):  # NOTE: _indexer not working on local
        try:
            r = requests.get(request.host_url + '/_regionindexer')
            display['listener'] = json.loads(r.text)
            display['status'] = display['listener']['status']
        except Exception:
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
    indexer = request.registry['region' + INDEXER]
    uuids = []

    # keeping track of state
    state = RegionIndexerState(encoded_es, encoded_INDEX)
    result = state.get_initial_state()

    (uuids, force) = state.get_one_cycle(request)

    uuid_count = len(uuids)
    if uuid_count > 0 and not dry_run:
        log.info("Region indexer started on %d uuid(s)" % uuid_count)

        result = state.start_cycle(uuids, result)
        errors = indexer.update_objects(request, uuids, force)
        result = state.finish_cycle(result, errors)
        if errors:
            result['errors'] = errors
        if result['indexed'] == 0:  # not unexpected, but worth logging otherwise silent cycle
            log.warn("Region indexer added %d file(s) from %d dataset uuids",
                     result['indexed'], uuid_count)
        else:
            regions_es = request.registry[SNP_SEARCH_ES]
            try:
                regions_es.indices.flush_synced(index='chr*')
                regions_es.indices.flush_synced(index=SNP_INDEX_PREFIX + '*')
                regions_es.indices.flush_synced(index=RESIDENT_REGIONSET_KEY)
            except Exception:
                pass

    state.send_notices()
    return result


class RegionIndexer(Indexer):
    def __init__(self, registry):
        super(RegionIndexer, self).__init__(registry)
        self.encoded_es = registry[ELASTIC_SEARCH]    # yes this is self.es but we want clarity
        self.encoded_INDEX = registry.settings['snovault.elasticsearch.index']
        self.regions_es = registry[SNP_SEARCH_ES]
        self.residents_index = RESIDENT_REGIONSET_KEY
        # WARNING: updating 'state' could lead to race conditions if more than 1 worker
        self.state = RegionIndexerState(self.encoded_es, self.encoded_INDEX)
        self.reader = RemoteReader()

    def update_object(self, request, dataset_uuid, force):
        request.datastore = 'elasticsearch'  # Let's be explicit

        last_exc = None
        try:
            # less efficient than going to es directly but keeps methods in one place
            dataset = request.embed(str(dataset_uuid), as_user=True)
        except StatementError:
            # Can't reconnect until invalid transaction is rolled back
            raise
        except Exception as e:
            log.warn("dataset is not found for uuid: %s", dataset_uuid)
            last_exc = repr(e)

        if last_exc is None:
            dataset_region_uses = self.candidate_dataset(dataset)
            if not dataset_region_uses:
                return  # Note if dataset is NO LONGER a candidate its files won't get removed.

        if last_exc is None:
            files = dataset.get('files', [])
            for afile in files:
                # files may not be embedded
                if isinstance(afile, str):
                    file_id = afile
                    try:
                        afile = request.embed(file_id, as_user=True)
                    except StatementError:
                        # Can't reconnect until invalid transaction is rolled back
                        raise
                    except Exception as e:
                        log.warn("file %s of dataset %s is not found; "
                                 "skip the rest of files in this dataset.",
                                 file_id, dataset_uuid)
                        last_exc = repr(e)
                        break

                if afile.get('file_format') not in ALLOWED_FILE_FORMATS:
                    continue  # Note: if file_format changed, it doesn't get removed from region index.

                file_uuid = afile['uuid']

                file_doc = self.candidate_file(request, afile, dataset, dataset_region_uses)
                if file_doc:

                    using = ""
                    if force:
                        using = "with FORCE"
                        self.remove_from_regions_es(file_uuid)  # remove all regions first
                    else:
                        if self.in_regions_es(file_uuid):
                            # TODO: update residence doc but not file!
                            continue

                    try:
                        self.add_file_to_regions_es(request, afile, file_doc)
                    except Exception as e:
                        log.warn("Fail to index file %s of dataset %s; "
                                 "skip the rest of files in this dataset.",
                                 file_uuid, dataset_uuid)
                        last_exc = repr(e)
                        break
                    else:
                        log.info("added file: %s %s %s", dataset['accession'], afile['href'], using)
                        self.state.file_added(file_uuid)

                else:
                    if self.remove_from_regions_es(file_uuid):
                        log.warn("dropped file: %s %s", dataset['accession'], afile['@id'])
                        self.state.file_dropped(file_uuid)

        if last_exc is not None:
            timestamp = datetime.datetime.now().isoformat()
            return {'error_message': last_exc, 'timestamp': timestamp, 'uuid': str(dataset_uuid)}

    @staticmethod
    def check_embedded_targets(request, dataset):
        '''Make sure taget or targets is embedded.'''
        # Not all datasets will have a target but if they do it must be embeeded
        target = dataset.get('target')
        if target is not None:
            if not isinstance(target, str):
                return target
            else:
                try:
                    return request.embed(target, as_user=True)
                except Exception:
                    log.warn("Target is not found for: %s", dataset['@id'])
                    return None
        else:
            targets = dataset.get('targets', [])
            if len(targets) > 0:
                if isinstance(targets[0], dict):
                    return targets
                target_objects = []
                for targ in targets:
                    if isinstance(targets[0], str):
                        try:
                            target_objects.append(request.embed(targ, as_user=True))
                        except Exception:
                            log.warn("Target %s is not found for: %s" % (targ, dataset['@id']))
                return target_objects

        return None

    @staticmethod
    def candidate_dataset(dataset):
        '''returns None, or a list of uses which may include region search and/or regulome.'''
        if 'Experiment' not in dataset['@type'] and 'FileSet' not in dataset['@type']:
            return None

        if len(dataset.get('files', [])) == 0:
            return None

        dataset_uses = []
        assay = dataset.get('assay_term_name')
        if assay is not None and assay in list(ENCODED_REGION_REQUIREMENTS.keys()):
            dataset_uses.append(FOR_REGION_SEARCH)
        if 'RegulomeDB' in dataset.get('internal_tags', []):
            collection_type = regulome_collection_type(dataset)
            if collection_type is not None and \
               collection_type in list(REGULOME_REGION_REQUIREMENTS.keys()):
                dataset_uses.append(FOR_REGULOME_DB)

        return dataset_uses

    @staticmethod
    def metadata_doc(afile, dataset, assembly, uses):
        '''returns file and dataset metadata document'''
        meta_doc = {
            'uuid': str(afile['uuid']),
            'uses': uses,
            'file': {
                'uuid': str(afile['uuid']),
                '@id': afile['@id'],
                'assembly': assembly
            },
            'dataset': {
                'uuid': str(dataset['uuid']),
                '@id': dataset['@id']
            }
        }

        # collection_type may be the first of these that are actually found
        for prop in REGULOME_COLLECTION_TYPES:
            prop_value = dataset.get(prop)
            if prop_value:
                meta_doc['dataset'][prop] = prop_value
                if 'collection_type' not in meta_doc['dataset']:
                    meta_doc['dataset']['collection_type'] = prop_value
        target = dataset.get('target', {})
        if target:  # overloaded target with potential list of target objects
            if isinstance(target, dict):
                target = [target]
            if isinstance(target, list):
                target_labels = []
                for targ in target:
                    label = targ.get('gene_name')
                    if label:
                        target_labels.append(label.upper())
                if len(target_labels) > 0:
                    meta_doc['dataset']['target'] = target_labels
        biosample = dataset.get('biosample_term_name')
        if biosample:
            meta_doc['dataset']['biosample_term_name'] = biosample

        for dataset_type in REGULOME_DATASET_TYPES:  # prioritized
            if dataset_type in dataset['@type']:
                meta_doc['dataset_type'] = dataset_type
                break
        if afile['submitted_file_name'] in SNP_FILES:
            meta_doc['snps'] = True
        return meta_doc

    def candidate_file(self, request, afile, dataset, dataset_uses):
        '''returns None or a document with file details to save in the residence index'''
        if afile.get('href') is None:
            return None
        if afile['file_format'] not in ALLOWED_FILE_FORMATS:
            return None

        file_status = afile.get('status', 'imagined')
        assembly = afile.get('assembly', 'unknown')
        if assembly == 'mm10-minimal':        # Treat mm10-minimal as mm10
            assembly = 'mm10'

        # dataset passed in can be file's dataset OR file_set, with each file pointing elsewhere
        if isinstance(afile['dataset'], dict) and afile['dataset']['@id'] != dataset['@id']:
            dataset = afile['dataset']
        elif isinstance(afile['dataset'], str) and afile['dataset'] != dataset['@id']:
            try:
                dataset = request.embed(afile['dataset'], as_user=True)
            except Exception:
                log.warn("dataset is not found: %s", afile['dataset'])
                return None
        target = self.check_embedded_targets(request, dataset)
        if target is not None:
            dataset['target'] = target

        assay_term_name = dataset.get('assay_term_name')

        file_uses = []
        if FOR_REGION_SEARCH in dataset_uses:  # encoded datasets must have encoded files
            if assay_term_name is not None and \
               file_status in ENCODED_ALLOWED_STATUSES and \
               assembly in ENCODED_SUPPORTED_ASSEMBLIES:
                required_properties = ENCODED_REGION_REQUIREMENTS.get(assay_term_name, {})
                if required_properties:
                    failed = False
                    for prop in list(required_properties.keys()):
                        val = afile.get(prop)
                        if val is None:
                            failed = True
                            break
                        if val not in required_properties[prop]:
                            failed = True
                            break
                    if not failed:
                        file_uses.append(FOR_REGION_SEARCH)

        if FOR_REGULOME_DB in dataset_uses:  # regulome datasets must have regulome files
            if file_status in REGULOME_ALLOWED_STATUSES \
               and assembly in REGULOME_SUPPORTED_ASSEMBLIES:
                collection_type = regulome_collection_type(dataset)
                if collection_type is not None:
                    required_properties = REGULOME_REGION_REQUIREMENTS[collection_type]
                    if required_properties:
                        failed = False
                        for prop in list(required_properties.keys()):
                            val = afile.get(prop)
                            if val is None:
                                failed = True
                                break
                            if val not in required_properties[prop]:
                                failed = True
                                break
                        if not failed:
                            file_uses.append(FOR_REGULOME_DB)

        if not file_uses:
            return None

        return self.metadata_doc(afile, dataset, assembly, file_uses)

    def in_regions_es(self, uuid, use_type=None):
        '''returns True if a uuid is in regions es'''
        try:
            if use_type is not None:
                doc = self.regions_es.get(index=self.residents_index, doc_type=use_type,
                                          id=str(uuid)).get('_source', {})
            else:
                doc = self.regions_es.get(index=self.residents_index, id=str(uuid)).get('_source', {})
            if doc:
                return True
        except NotFoundError:
            return False
        except Exception:
            pass

        return False

    def remove_from_regions_es(self, uuid):
        '''Removes all traces of a uuid (from file) from region search elasticsearch index.'''
        try:
            result = self.regions_es.get(index=self.residents_index, id=str(uuid))
            doc = result.get('_source', {})
            use_type = result.get('_type', FOR_DUAL_USE)
            if not doc:
                log.warn("Trying to drop file: %s  NOT FOUND", uuid)
                return False
        except Exception:
            return False  # Not an error: remove may be called without looking first

        if 'index' in doc:
            try:
                self.regions_es.delete(index=doc['index'])
            except Exception:
                log.error("Region indexer failed to delete %s index" % (doc['index']))
                return False   # Will try next full cycle
        else:
            for chrom in doc['chroms']:  # Could just try index='chr*'
                try:
                    self.regions_es.delete(index=chrom.lower(), doc_type=doc['assembly'],
                                           id=str(uuid))
                except Exception:
                    # log.error("Region indexer failed to remove %s regions of %s" % (chrom, uuid))
                    # return False # Will try next full cycle
                    pass

        try:
            self.regions_es.delete(index=self.residents_index, doc_type=use_type, id=str(uuid))
        except Exception:
            log.error("Region indexer failed to remove %s from %s" % (uuid, self.residents_index))
            return False  # Will try next full cycle

        return True

    def add_to_residence(self, file_doc):
        '''Adds a file into residence index.'''
        uuid = file_doc['uuid']

        # Only splitting on doc_type=use in order to easily count them
        use_type = FOR_DUAL_USE
        if len(file_doc['uses']) == 1:
            use_type = file_doc['uses'][0]

        # Make sure there is an index set up to handle whether uuids are resident
        if not self.regions_es.indices.exists(self.residents_index):
            self.regions_es.indices.create(index=self.residents_index, body=index_settings())

        if not self.regions_es.indices.exists_type(index=self.residents_index, doc_type=use_type):
            mapping = get_resident_mapping(use_type)
            self.regions_es.indices.put_mapping(index=self.residents_index, doc_type=use_type,
                                                body=mapping)

        self.regions_es.index(index=self.residents_index, doc_type=use_type, body=file_doc,
                              id=str(uuid))
        return True

    def index_regions(self, assembly, regions, file_doc, chroms):
        '''Given regions from some source (most likely encoded file)
           loads the data into region search es'''
        uuid = file_doc['uuid']

        if chroms is None:
            chroms = list(regions.keys())
        for chrom in list(regions.keys()):
            if len(regions[chrom]) == 0:
                continue
            doc = {
                'uuid': uuid,
                'positions': regions[chrom]
            }
            chrom_lc = chrom.lower()
            # Could be a chrom never seen before!
            if not self.regions_es.indices.exists(chrom_lc):
                self.regions_es.indices.create(index=chrom_lc, body=index_settings())

            if not self.regions_es.indices.exists_type(index=chrom_lc, doc_type=assembly):
                mapping = get_chrom_index_mapping(assembly)
                self.regions_es.indices.put_mapping(index=chrom_lc, doc_type=assembly, body=mapping)

            self.regions_es.index(index=chrom_lc, doc_type=assembly, body=doc, id=uuid)
            file_doc['chroms'].append(chrom)

        return True

    @staticmethod
    def snps_bulk_iterator(snp_index, chrom, snps_for_chrom):
        '''Given SNPs yields snps packaged for bulk indexing'''
        for snp in snps_for_chrom:
            yield {'_index': snp_index, '_type': chrom, '_id': snp['rsid'], '_source': snp}

    def index_snps(self, assembly, snps, file_doc, chroms=None):
        '''Given SNPs from file loads the data into region search es'''
        snp_index = snp_index_key(assembly)
        file_doc['index'] = snp_index

        if not self.regions_es.indices.exists(snp_index):
            self.regions_es.indices.create(index=snp_index, body=index_settings())

        if chroms is None:
            chroms = list(snps.keys())
        for chrom in chroms:
            if len(snps[chrom]) == 0:
                continue
            if not self.regions_es.indices.exists_type(index=snp_index, doc_type=chrom):
                mapping = get_snp_index_mapping(chrom)
                self.regions_es.indices.put_mapping(index=snp_index, doc_type=chrom, body=mapping)
            # indexing in bulk 500K snps at a time...
            bulk(self.regions_es,
                 self.snps_bulk_iterator(snp_index, chrom, snps[chrom]), chunk_size=500000)
            file_doc['chroms'].append(chrom)

            try:  # likely millions per chrom, so
                self.regions_es.indices.flush_synced(index=snp_index)
            except Exception:
                pass
            log.warn('Added %s/%s %d docs', snp_index, chrom, len(snps[chrom]))

        return True

    def add_file_to_regions_es(self, request, afile, file_doc, snp=False):
        '''Given an encoded file object, reads the file to create regions data
           then loads that into region search es.'''

        assembly = file_doc['file']['assembly']
        snp_set = file_doc.get('snps', False)
        # ############### TEMPORARY  because snps take so long!
        # if snp_set:
        #     file_doc['chroms'] = SUPPORTED_CHROMOSOMES
        #     file_doc['index'] = snp_index_key(assembly)
        #     return self.add_to_residence(file_doc)
        # ############### TEMPORARY
        big_file = (afile.get('file_size', 0) > MAX_IN_MEMORY_FILE_SIZE)
        file_doc['chroms'] = []

        readable_file = self.reader.readable_file(request, afile)

        file_data = {}
        chroms = []
        if afile['file_format'] == 'bed':
            # NOTE: requests doesn't require gzip but http.request does.
            with gzip.open(readable_file, mode='rt') as file_handle:
                for row in self.reader.tsv(file_handle):
                    if row[0].startswith('#'):
                        continue
                    try:
                        if snp_set:
                            (chrom, doc) = self.reader.snp(row)
                        else:
                            (chrom, doc) = self.reader.region(row)
                    except Exception:
                        log.error('%s - failure to parse row %s:%s:%s, skipping row',
                                  afile['href'], row[0], row[1], row[2])
                        continue
                    if snp_set and chrom not in SUPPORTED_CHROMOSOMES:
                        continue   # TEMPORARY: limit SNPs to major chroms
                    if chrom not in file_data:
                        # 1 chrom at a time saves memory (but assumes the files are in chrom order!)
                        if big_file and file_data and len(chroms) > 0:
                            if snp_set:
                                self.index_snps(assembly, file_data, file_doc,
                                                list(file_data.keys()))
                            else:
                                self.index_regions(assembly, file_data, file_doc,
                                                   list(file_data.keys()))
                            file_data = {}  # Don't hold onto data already indexed
                        file_data[chrom] = []
                        chroms.append(chrom)
                    file_data[chrom].append(doc)
        # TODO: Handle bigBeds...
        # elif afile['file_format'] == 'bedBed':  # Use pyBigWig?
        #    import pyBigWig  # https://github.com/deeptools/pyBigWig
        #    with pyBigWig.open(readable_file) as bb:
        #              # reader.readable_file must return remote url for bb files
        #        chroms = bb.chroms()
        #        for chrom in chroms.keys():  # should sort
        #            for row in bb.entries(chrom, 0, chroms[chrom], withString=snp_set):
        #                try:
        #                    if snp_set:
        #                        doc = self.reader.bb_snp(row)
        #                    else:
        #                        doc = self.reader.bb_region(row)
        #                except Exception:
        #                    log.error('%s - failure to parse row %s:%s:%s, skipping row', \
        #                                                    afile['href'], chrom, row[0], row[1])
        # Could redesign with reader class, so this function is entirely ignorant of bed v. bigBed
        # However, probably not worth as much as just abstracting the file_data building/indexing

        if len(chroms) == 0 or not file_data:
            raise IOError('Error parsing file %s' % afile['href'])

        # Note if indexing by chrom (snp_set or big_file) then file_data will only have one chrom
        if snp_set:
            self.index_snps(assembly, file_data, file_doc, list(file_data.keys()))
        else:
            self.index_regions(assembly, file_data, file_doc, list(file_data.keys()))

        if big_file and file_doc['chroms'] != chroms:
            log.error('%s chromosomes %s indexed out of order!', file_doc['file']['@id'],
                      ('SNPs' if snp_set else 'regions'))
        return self.add_to_residence(file_doc)
