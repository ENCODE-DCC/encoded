import urllib3
import io
import gzip
import csv
import logging
import json
import requests
from pyramid.view import view_config
from shutil import copyfileobj
import pyBigWig
from elasticsearch.exceptions import (
    NotFoundError
)
from elasticsearch.helpers import (
    bulk
)
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


# TEMPORARY: limit SNPs to major chroms
SUPPORTED_CHROMOSOMES = [
    'chr1', 'chr2', 'chr3', 'chr4', 'chr5', 'chr6', 'chr7', 'chr8', 'chr9', 'chr10',
    'chr11', 'chr12', 'chr13', 'chr14', 'chr15', 'chr16', 'chr17', 'chr18', 'chr19', 'chr20',
    'chr21', 'chr22', 'chrX', 'chrY']  # chroms are lower case

ALLOWED_FILE_FORMATS = ['bed', 'bigBed']
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
    #'Switchgear': {                ### TEMPORARY: ONLY FOR TESTING pyBigBed.  It works!
    #    'file_format': ['bigBed']  ### TEMPORARY: ONLY FOR TESTING pyBigBed.
    #},                             ### TEMPORARY: ONLY FOR TESTING pyBigBed.
    'index': {
        'output_type': ['variant calls'],
        'file_format': ['bed']
    }
}
#### TODO: Remove Switchgear which was ONLY added to test bigBed

# Less than ideal way to recognize the SNP files by submitted_file_name
# SNP_DATASET_UUID = 'ff8dff4e-1de5-446b-8a13-bb6243bc64aa'  # works on demo, but...
SNP_FILES = [
    's3://regulomedb/snp141/snp141_hg19.bed.gz',
    's3://regulomedb/snp141/snp141_GRCh38.bed.gz'
]
# Indexes have assembly.lower() appended to this prefix
SNP_INDEX_PREFIX = 'snp141_'

### TEMPORARY: This is only for testing pyBigWig bigWig reading!
### TEMPORARY: This is only for testing pyBigWig bigWig reading!
### TEMPORARY: This is only for testing pyBigWig bigWig reading!
#REGULOME_SCORE_FILE = '/tmp/ENCFF315EWM.bigWig'
### TEMPORARY: This is only for testing pyBigWig bigWig reading!
### TEMPORARY: This is only for testing pyBigWig bigWig reading!
### TEMPORARY: This is only for testing pyBigWig bigWig reading!

# Indexes have assembly.lower() appended to this prefix
REGULOME_SCORE_INDEX_PREFIX = 'reg_score_'

# If files are too large then they will be copied locally and read
MAX_IN_MEMORY_FILE_SIZE = (700 * 1024 * 1024)  # most files will be below this and index faster
TEMPORARY_REGIONS_FILE_PREFIX = '/tmp/region_temp'

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
# NOTE: the chrom, based indexes allows having single doc per file per chrom keyed on uuid
#       ES searches focus on numeric position, as assembly/chrom are already determined
# ALSO: nested positions allow quick search of any hit to get uuid, while pos details take longer
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


# REG score mapping index: rdb_score_hg19, doc_type: chr*, _id=str(start)
def get_reg_score_index_mapping(chrom='chr1'):
    return {
        chrom: {
            '_all': {
                'enabled': False
            },
            '_source': {
                'enabled': True
            },
            'properties': {
                'interval_id': {
                    'type': 'keyword'  # For lack of anything better this is the start position
                },
                'start': {
                    'type': 'long'
                },
                'end': {
                    'type': 'long'
                },
                'score': {
                    'type': 'integer'  # bigWigs might have double but this is for reg scores!
                }
            }
        }
    }


def snp_index_key(assembly):
    return SNP_INDEX_PREFIX + assembly.lower()

def reg_score_index_key(assembly):
    # TODO: make a genome-wide regulome score signal bigWig and try loading it into index
    return REGULOME_SCORE_INDEX_PREFIX + assembly.lower()


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


class RemoteBedReader(object):
    # Tools for reading remote files

    def __init__(self, request, afile, test_instance=False):
        self.temp_file = TEMPORARY_REGIONS_FILE_PREFIX + '.bed.gz'
        self.max_memory = MAX_IN_MEMORY_FILE_SIZE
        self.test_instance = test_instance
        self.file_abstract = self.readable_file(request, afile)
        self.file_handle = None

    def _copy_to_local(self, http, href, local_name=None):
        '''Copies the file locally and returns the local name'''
        if local_name is None:
            local_name = self.temp_file
        with http.request('GET', href, preload_content=False) \
                as r, open(local_name, 'wb') as out_file:
            copyfileobj(r, out_file)
        log.warn('Wrote %s to %s', href, local_name)
        return local_name

    def readable_file(self, request, afile):
        '''returns either an in memory file or a temp file'''

        # Special case local instance so that tests can work...
        if self.test_instance:
            href = 'http://www.encodeproject.org' + afile['href']  # test files read from production
        else:
            href = request.host_url + afile['href']

        # TODO: support for remote access for big files (could do bam and vcf as well)
        if afile['file_format'] != 'bed':
            log.error("Can't make RemoteBedReader without a 'bed' file.  Format found: '%s'" %
                      (afile['file_format']))
            raise Exception

        urllib3.disable_warnings()
        http = urllib3.PoolManager()

        # use afile.get(file_size) to decide between in mem file or temp file
        file_to_read = None
        if afile.get('file_size', 0) > self.max_memory:
            file_to_read = self._copy_to_local(http, href)
        else:
            # Note: this reads the file into an in-memory byte stream.
            r = http.request('GET', href)
            if r.status != 200:
                log.warn("File (%s or %s) not found" % (afile['@id'], href))
                return False
            file_in_mem = io.BytesIO()
            file_in_mem.write(r.data)
            file_in_mem.seek(0)
            file_to_read = file_in_mem
            r.release_conn()

        return file_to_read

    def open(self):
        self.file_handle = gzip.open(self.file_abstract, mode='rt')
        return self.file_handle

    def read(self, with_details=False):
        # TODO: support with_details like BigBedOrWigReader
        if not self.file_handle:
            self.open()
        reader = csv.reader(self.file_handle, delimiter='\t')
        for row in reader:
            if row[0].startswith('#'):
                continue
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
        return (chrom, {'rsid': rsid, 'chrom': chrom, 'start': start + 1, 'end': end})

    def close(self, file_handle=None):
        assert(file_handle is None or file_handle == self.file_handle)
        if self.file_handle:
            self.file_handle.close()
        self.file_handle = None

    def __del__(self):
        self.close()


class BigBedOrWigReader(RemoteBedReader):
    # Tools for reading 'bigBed' and 'bigWig' files

    def __init__(self, request, afile, test_instance=False):
        super(BigBedOrWigReader, self).__init__(request, afile, test_instance)

    def readable_file(self, request, afile):
        '''returns a URL to the bigBed or bigWig file'''

        # Special case local instance so that tests can work...
        if self.test_instance:
            href = 'http://www.encodeproject.org' + afile['href']  # test files read from production
        else:
            href = request.host_url + afile['href']

        # TODO: add support for bam and vcf files?
        if afile['file_format'] not in ['bigBed', 'bigWig']:
            log.error("Can't make BigBedOrWigReader without a bigBed or bigWig")
            raise Exception

        ### TEMPORARY: test biWig signal loading
        ### TEMPORARY: test biWig signal loading
        ### TEMPORARY: test biWig signal loading
        #if afile['accession'] == 'ENCFF000VCE':
        #    return REGULOME_SCORE_FILE
        ### TEMPORARY: test biWig signal loading
        ### TEMPORARY: test biWig signal loading
        ### TEMPORARY: test biWig signal loading

        urllib3.disable_warnings()
        http = urllib3.PoolManager()

        # return href + '?proxy=true' # TODO: This does not work with or without proxy=true
        # WARNING: pyBigWig is not reading remote files like advertised
        #          open will saturate and hangs the apache threads, then cause a strange restart
        #          of all indexers.  TODO: TO BE INVESTIGATED

        # AWLAYS copying bigBed loacally.
        self.temp_file = TEMPORARY_REGIONS_FILE_PREFIX + '.bigBed'
        return self._copy_to_local(http, href)

    def open(self):
        self.file_handle = pyBigWig.open(self.file_abstract)
        if not self.file_handle:
            log.warn('Failure to pyBigWig.open: %s' % self.file_abstract)
            raise Exception
        return self.file_handle

    def _read_one_chrom(self, chrom, with_details):
        self.cur_chrom = chrom
        chrom_end = self.file_chroms[chrom]
        chunk_size = 1000000  # chunks in bases... because bb.entries does not yield
        start = 0
        while start < chrom_end:
            end = min(start + chunk_size, chrom_end)
            if self.bigWig:
                rows = self.file_handle.intervals(chrom, start, end)
            else:
                rows = self.file_handle.entries(chrom, start, end, withString=with_details)
            if rows:
                for row in rows:
                    yield row
            start += chunk_size

    def read(self, with_details=False):
        '''Yields all regions in 'bigBed' or 'bigWig' file. Include details by request.'''
        if not self.file_handle:
            self.open()
        self.file_chroms = self.file_handle.chroms()
        self.bigWig = self.file_handle.isBigWig()
        for chrom in sorted(self.file_chroms.keys()):
            yield from self._read_one_chrom(chrom, with_details)

    def region(self, row):
        '''Read a region from a bigBed file read with "pyBigWig" and returns document to index.'''
        start, end = int(row[0]), int(row[1])
        #                                 bed loc 'half-open', but we will close it
        return (self.cur_chrom, {'start': start + 1, 'end': end})

    def score_interval(self, row):
        '''Read score interval from bigWig file read with "pyBigWig" and returns doc to index.'''
        start, end, score = int(row[0]) + 1, int(row[1]), int(row[2])
        return (self.cur_chrom,       # bed loc 'half-open', but we will close it
                {'interval_id': str(start), 'start': start, 'end': end, 'score': score})

    def snp(self, row):
        '''Read a SNP from a bigBed file read with "pyBigWig"  and returns document to index.'''
        start, end = int(row[0]), int(row[1])
        extras = row[3].split('\t')
        rsid = extras[0]
        num_score = int(extras[1])
        score = extras[2]
        start, end, rsid = row[0], int(row[0]), int(row[2]), row[3]
        return (self.cur_chrom, {'rsid': rsid, 'chrom': chrom, 'start': start + 1, 'end': end,
                'num_score': num_score, 'score': score})


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
            counts['score_intervals'] = {}
            for assembly in assemblies:
                try:
                    counts['SNPs'][assembly] = \
                        region_es.count(index=snp_index_key(assembly)).get('count', 0)
                except Exception:
                    counts['SNPs'][assembly] = 0
                try:
                    counts['score_intervals'][assembly] = \
                        region_es.count(index=reg_score_index_key(assembly)).get('count', 0)
                except Exception:
                    counts['score_intervals'][assembly] = 0

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
    display['score_intervals_in_index'] = counts.get('score_intervals', 0)

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
        self.test_instance = registry.settings.get('testing', False)

    def update_object(self, request, dataset_uuid, force):
        request.datastore = 'elasticsearch'  # Let's be explicit

        try:
            # less efficient than going to es directly but keeps methods in one place
            dataset = request.embed(str(dataset_uuid), as_user=True)
        except Exception:
            log.warn("dataset is not found for uuid: %s", dataset_uuid)
            # Not an error if it wasn't found.
            return

        dataset_region_uses = self.candidate_dataset(dataset)
        if not dataset_region_uses:
            return  # Note if dataset is NO LONGER a candidate its files won't get removed.
        # log.warn('Candidate dataset: %s' % (dataset['@id']))

        files = dataset.get('files', [])
        for afile in files:
            # files may not be embedded
            if isinstance(afile, str):
                file_id = afile
                try:
                    afile = request.embed(file_id, as_user=True)
                except Exception:
                    log.warn("file is not found for: %s", file_id)
                    continue

            if afile.get('file_format') not in ALLOWED_FILE_FORMATS:
                continue  # Note: if file_format changed, it doesn't get removed from region index.

            file_uuid = afile['uuid']

            file_doc = self.candidate_file(request, afile, dataset, dataset_region_uses)
            if file_doc:
                # log.warn('Candidate file: %s' % (afile['@id']))

                using = ""
                if force:
                    using = "with FORCE"
                    self.remove_from_regions_es(file_uuid)  # remove all regions first
                else:
                    if self.in_regions_es(file_uuid):
                        # TODO: update residence doc but not file!
                        continue

                if self.add_file_to_regions_es(request, afile, file_doc):
                    log.info("added file: %s %s %s", dataset['accession'], afile['href'], using)
                    self.state.file_added(file_uuid)

            else:
                if self.remove_from_regions_es(file_uuid):
                    log.warn("dropped file: %s %s", dataset['accession'], afile['@id'])
                    self.state.file_dropped(file_uuid)

        # TODO: gather and return errors

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
                    label = targ.get('label')
                    if label:
                        target_labels.append(label)
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
        ### TEMPORARY: test biWig signal loading
        ### TEMPORARY: test biWig signal loading
        ### TEMPORARY: test biWig signal loading
        #if afile['accession'] == 'ENCFF000VCE':
        #    log.warn('Calling %s a score set' % (afile['accession']))  ### DEBUG
        #    meta_doc['regulome_scores'] = True
        ### TEMPORARY: test biWig signal loading
        ### TEMPORARY: test biWig signal loading
        ### TEMPORARY: test biWig signal loading

        return meta_doc

    def candidate_file(self, request, afile, dataset, dataset_uses):
        '''returns None or a document with file details to save in the residence index'''
        if afile.get('href') is None:
            return None
        if afile['file_format'] not in ALLOWED_FILE_FORMATS:
            return None

        if self.test_instance:
            if afile['accession'] not in TESTABLE_FILES:
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
    def bulk_item_iterator(target_index, chrom, items_for_chrom, item_key):
        '''Given many items (SNPs or score intervals) yields doc packaged for bulk indexing'''
        for item in items_for_chrom:
            yield {'_index': target_index, '_type': chrom, '_id': item[item_key], '_source': item}

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
                 self.bulk_item_iterator(snp_index, chrom, snps[chrom], 'rsid'),
                 chunk_size=500000)
            file_doc['chroms'].append(chrom)

            try:  # likely millions per chrom, so
                self.regions_es.indices.flush_synced(index=snp_index)
            except Exception:
                pass
            log.warn('Added %s/%s %d snps', snp_index, chrom, len(snps[chrom]))

        return True

    def index_scores(self, assembly, scores, file_doc, chroms=None):
        '''Given signal intervals from file loads the data into region search es'''
        # TODO: make a genome-wide regulome score signal bigWig and try loading it into index
        score_index = reg_score_index_key(assembly)
        file_doc['index'] = score_index

        if not self.regions_es.indices.exists(score_index):
            self.regions_es.indices.create(index=score_index, body=index_settings())

        if chroms is None:
            chroms = list(scores.keys())
        for chrom in chroms:
            if len(scores[chrom]) == 0:
                continue
            if not self.regions_es.indices.exists_type(index=score_index, doc_type=chrom):
                mapping = get_reg_score_index_mapping(chrom)
                self.regions_es.indices.put_mapping(index=score_index, doc_type=chrom,
                                                    body=mapping)
            # indexing in bulk 500K snps at a time...
            bulk(self.regions_es,
                 self.bulk_item_iterator(score_index, chrom, scores[chrom], 'interval_id'),
                 chunk_size=500000)
            file_doc['chroms'].append(chrom)

            try:  # likely hundeds of thousands per chrom, so
                self.regions_es.indices.flush_synced(index=score_index)
            except Exception:
                pass
            log.warn('Added %s/%s %d score intervals', score_index, chrom, len(scores[chrom]))

        return True

    def add_file_to_regions_es(self, request, afile, file_doc, snp=False):
        '''Given an encoded file object, reads the file to create regions data
           then loads that into region search es.'''

        # log.warn('add_file_to_regions_es(%s)' % (afile['@id']))
        assembly = file_doc['file']['assembly']
        snp_set = file_doc.get('snps', False)
        reg_scores = file_doc.get('regulome_scores', False)
        chrom_by_chrom = (afile.get('file_size', 0) > MAX_IN_MEMORY_FILE_SIZE)
        file_doc['chroms'] = []

        if afile['file_format'] == 'bed':
            reader = RemoteBedReader(request, afile, self.test_instance)
        elif afile['file_format'] in ['bigBed', 'bigWig']:
            reader = BigBedOrWigReader(request, afile, self.test_instance)
            chrom_by_chrom = True
        else:
            log.warn('unknown file_format: %s' % (afile['file_format']))
            raise Exception

        file_data = {}
        chroms = []
        try:
            reader.open()
        except Exception:
            log.warn("Unable to open reader for file: %s" % (afile['@id']))
            return False

        for row in reader.read(with_details=snp_set):
            try:
                if snp_set:
                    (chrom, doc) = reader.snp(row)
                elif reg_scores:
                    (chrom, doc) = reader.score_interval(row)
                else:
                    (chrom, doc) = reader.region(row)
            except Exception:
                log.error('%s - failure to parse row: <%s>, skipping row', afile['href'], str(row))
                continue
            if (snp_set or reg_scores) and chrom not in SUPPORTED_CHROMOSOMES:
                continue   # TEMPORARY: limit SNPs to major chroms
            if chrom not in file_data:
                # 1 chrom at a time saves memory (but assumes the files are in chrom order!)
                if chrom_by_chrom and file_data and len(chroms) > 0:
                    if snp_set:
                        self.index_snps(assembly, file_data, file_doc, list(file_data.keys()))
                    elif reg_scores:
                        self.index_scores(assembly, file_data, file_doc, list(file_data.keys()))
                    else:
                        self.index_regions(assembly, file_data, file_doc, list(file_data.keys()))
                    file_data = {}  # Don't hold onto data already indexed
                file_data[chrom] = []
                chroms.append(chrom)
            file_data[chrom].append(doc)
        reader.close()

        if len(chroms) == 0 or not file_data:
            return False

        # Note if indexing chrom_by_chrom, file_data only has last chrom, yet to be indexed
        if snp_set:
            self.index_snps(assembly, file_data, file_doc, list(file_data.keys()))
        elif reg_scores:
            self.index_scores(assembly, file_data, file_doc, list(file_data.keys()))
        else:
            self.index_regions(assembly, file_data, file_doc, list(file_data.keys()))

        if chrom_by_chrom and file_doc['chroms'] != chroms:
            log.error('%s chromosomes %s indexed out of order!  Indexing requires sorted file.',
                      file_doc['file']['@id'], ('SNPs' if snp_set else 'regions'))
        return self.add_to_residence(file_doc)
