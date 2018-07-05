from elasticsearch.exceptions import (
    NotFoundError
)
from snovault.elasticsearch.indexer_state import SEARCH_MAX

from .region_indexer import (
    snp_index_key,
    RESIDENT_REGIONSET_KEY,
    FOR_REGION_SEARCH,
    FOR_REGULOME_DB,
    FOR_DUAL_USE,
    ENCODED_ALLOWED_STATUSES,
    ENCODED_DATASET_TYPES,
    REGULOME_ALLOWED_STATUSES,
    REGULOME_DATASET_TYPES
)
import logging

log = logging.getLogger(__name__)

# ##################################
# RegionAtlas and RegulomeAtlas classes encapsulate the methods
# for querying regions and SNPs from the region_index.
# ##################################

# when iterating scored snps or bases, chunk calls to index for efficiency
# NOTE: failures seen when chunking is too large
REGDB_SCORE_CHUNK_SIZE = 30000

# RegulomeDB scores for bigWig (bedGraph) are converted to numeric and can be converted back
REGDB_STR_SCORES = ['1a', '1b', '1c', '1d', '1e', '1f', '2a', '2b', '2c', '3a', '3b', '4', '5', '6']
REGDB_NUM_SCORES = [1000, 950, 900, 850, 800, 750, 600, 550, 500, 450, 400, 300, 200, 100]

NEARBY_SNP_WINDOW = 1600

CHROM_SIZES = {
    'chr1':  {'hg19': 249250621, 'GRCh38': 248956422},
    'chr2':  {'hg19': 243199373, 'GRCh38': 242193529},
    'chr3':	 {'hg19': 198022430, 'GRCh38': 198295559},
    'chr4':  {'hg19': 191154276, 'GRCh38': 190214555},
    'chr5':  {'hg19': 180915260, 'GRCh38': 181538259},
    'chr6':  {'hg19': 171115067, 'GRCh38': 170805979},
    'chr7':  {'hg19': 159138663, 'GRCh38': 159345973},
    'chr8':  {'hg19': 146364022, 'GRCh38': 145138636},
    'chr9':  {'hg19': 141213431, 'GRCh38': 138394717},
    'chr10': {'hg19': 135534747, 'GRCh38': 133797422},
    'chr11': {'hg19': 135006516, 'GRCh38': 135086622},
    'chr12': {'hg19': 133851895, 'GRCh38': 133275309},
    'chr13': {'hg19': 115169878, 'GRCh38': 114364328},
    'chr14': {'hg19': 107349540, 'GRCh38': 107043718},
    'chr15': {'hg19': 102531392, 'GRCh38': 101991189},
    'chr16': {'hg19': 90354753,  'GRCh38': 90338345},
    'chr17': {'hg19': 81195210,  'GRCh38': 83257441},
    'chr18': {'hg19': 78077248,  'GRCh38': 80373285},
    'chr19': {'hg19': 59128983,  'GRCh38': 58617616},
    'chr20': {'hg19': 63025520,  'GRCh38': 64444167},
    'chr21': {'hg19': 48129895,  'GRCh38': 46709983},
    'chr22': {'hg19': 51304566,  'GRCh38': 50818468},
    'chrX':  {'hg19': 155270560, 'GRCh38': 156040895},
    'chrY':  {'hg19': 59373566,  'GRCh38': 57227415}
}


class RegionAtlas(object):
    '''Methods for getting stuff out of the region_index.'''

    def __init__(self, region_es):
        self.region_es = region_es
        self.expected_use = FOR_REGION_SEARCH

    @staticmethod
    def type():
        return 'region search'

    @staticmethod
    def allowed_statuses():
        return ENCODED_ALLOWED_STATUSES

    @staticmethod
    def set_type():
        return ENCODED_DATASET_TYPES

    @staticmethod
    def set_indices():
        indices = [set_type.lower() for set_type in ENCODED_DATASET_TYPES]
        return indices

    @staticmethod
    def chrom_size(assembly, chrom):
        '''Return the size of a chrom.'''
        return CHROM_SIZES[chrom][assembly]

    @staticmethod
    def cap_at_chrom_size(assembly, chrom, pos):
        '''Return the lessor of pos or end of chrom.'''
        chrom_size = CHROM_SIZES[chrom][assembly]
        if pos < 0 or pos > chrom_size:
            return chrom_size
        return pos

    def snp(self, assembly, rsid):
        '''Return single SNP by rsid and assembly'''
        try:
            res = self.region_es.get(index=snp_index_key(assembly), doc_type='_all', id=rsid)
        except Exception:
            return None

        return res['_source']

    @staticmethod
    def _range_query(start, end, snps=False, with_inner_hits=False, max_results=SEARCH_MAX):
        '''private: return peak query'''
        # get all peaks that overlap requested region:
        #     peak.start <= requested.end and peak.end >= requested.start
        prefix = 'positions.'
        if snps:
            prefix = ''

        range_clause = {
            'bool': {
                'must': [
                    {'range': {prefix + 'start': {'lte': end}}},
                    {'range': {prefix + 'end':   {'gte': start}}}
                ]
            }
        }
        if snps:
            filter_fish = {'bool': {'should': [range_clause]}}
        else:
            filter_fish = {
                'nested': {
                    'path': 'positions',
                    'query': {
                        'bool': {'should': [range_clause]}
                    }
                }
            }

        query = {
            'query': {
                'bool': {
                    'filter': filter_fish
                }
            },
            '_source': snps,  # True is snps, False if regions
        }
        # special SLOW query will return inner_hits positions
        if with_inner_hits:
            query['query']['bool']['filter']['nested']['inner_hits'] = {'size': max_results}
        return query

    def find_snps(self, assembly, chrom, start, end, max_results=SEARCH_MAX):
        '''Return all SNPs in a region.'''
        range_query = self._range_query(start, end, snps=True)

        try:
            results = self.region_es.search(index=snp_index_key(assembly), doc_type=chrom,
                                            _source=True, body=range_query, size=max_results)
        except NotFoundError:
            return []
        except Exception:
            log.error('Error: find_snps()', exc_info=True)
            return []

        return [hit['_source'] for hit in results['hits']['hits']]

    # def snp_suggest(self, assembly, text):
    # Using suggest with 60M of rsids leads to es crashing during SNP indexing

    def find_peaks(self, assembly, chrom, start, end, peaks_too=False, max_results=SEARCH_MAX):
        '''Return all peaks in a region.  NOTE: peaks are not filtered by use.'''
        range_query = self._range_query(start, end, False, peaks_too, max_results)

        try:
            results = self.region_es.search(index=chrom.lower(), doc_type=assembly, _source=False,
                                            body=range_query, size=max_results)
        except NotFoundError:
            return None
        except Exception:
            log.error('Error: find_peaks()', exc_info=True)
            return None

        return list(results['hits']['hits'])

    def _resident_details(self, uuids, use=None, max_results=SEARCH_MAX):
        '''private: returns resident details filtered by use.'''
        if use is None:
            use = self.expected_use
        use_types = [FOR_DUAL_USE, use]
        try:
            id_query = {"query": {"ids": {"values": uuids}}}
            res = self.region_es.search(index=RESIDENT_REGIONSET_KEY, body=id_query,
                                        doc_type=use_types, size=max_results)
        except Exception:
            log.error('Error: _resident_details()', exc_info=True)
            return None

        details = {}
        hits = res.get("hits", {}).get("hits", [])
        for hit in hits:
            details[hit["_id"]] = hit["_source"]

        return details

    def _filter_peaks_by_use(self, peaks, use=None):
        '''private: returns peaks and resident details, both filtered by use'''
        uuids = list(set([peak['_id'] for peak in peaks]))
        details = self._resident_details(uuids, use)
        if not details:
            return ([], details)
        filtered_peaks = []
        while peaks:
            peak = peaks.pop(0)
            uuid = peak['_id']
            if uuid in details:
                filtered_peaks.append(peak)
        return (filtered_peaks, details)

    def find_peaks_filtered(self, assembly, chrom, start, end, peaks_too=False, use=None):
        '''Return peaks in a region and resident details, both filtered by use'''
        peaks = self.find_peaks(assembly, chrom, start, end, peaks_too=peaks_too)
        if not peaks:
            return (peaks, None)
        return self._filter_peaks_by_use(peaks, use=use)

    @staticmethod
    def _peak_uuids_in_overlap(peaks, chrom, start, end=None):
        '''private: returns set of only the uuids for peaks that overlap a given location'''
        if end is None:
            end = start

        overlap = []  # for comparisons below: list in deterministic order and faster than a set
        for peak in peaks:
            for hit in peak['inner_hits']['positions']['hits']['hits']:
                if chrom == peak['_index'] and start <= hit['_source']['end'] \
                   and end >= hit['_source']['start']:
                    overlap.append(peak['_id'])
                    break

        return overlap

    @staticmethod
    def _filter_details(details, uuids=None, peaks=None):
        '''private: returns only the details that match the uuids'''
        if uuids is None:
            assert(peaks is not None)
            uuids = list(set([peak['_id'] for peak in peaks]))
        filtered = {}
        for uuid in uuids:
            if uuid in details:  # region peaks may not be in regulome only details
                filtered[uuid] = details[uuid]
        return filtered

    @staticmethod
    def details_breakdown(details, uuids=None):
        '''Return dataset and file dicts from resident details dicts.'''
        if not details:
            log.warn('Warning: details_breakdown(), no details provided.')
            return (None, None)
        file_dets = {}
        dataset_dets = {}
        if uuids is None:
            uuids = details.keys()
        for uuid in uuids:
            if uuid not in details:
                continue
            afile = details[uuid]['file']
            file_dets[afile['@id']] = afile
            dataset = details[uuid]['dataset']
            dataset_dets[dataset['@id']] = dataset
        return (dataset_dets, file_dets)


class RegulomeAtlas(RegionAtlas):
    '''Methods for getting stuff out of the region_index.'''

    def __init__(self, region_es):
        super(RegulomeAtlas, self).__init__(region_es)
        self.expected_use = FOR_REGULOME_DB

    @staticmethod
    def type():
        return 'regulome'

    @staticmethod
    def allowed_statuses():
        return REGULOME_ALLOWED_STATUSES

    @staticmethod
    def set_type():
        return ['Dataset']

    @staticmethod
    def set_indices():
        indices = [set_type.lower() for set_type in REGULOME_DATASET_TYPES]
        return indices

    # def snp_suggest(self, assembly, text):
    # Using suggest with 60M of rsids leads to es crashing during SNP indexing

    @staticmethod
    def evidence_categories():
        '''Returns a list of regulome evidence categories'''
        return ['eQTL', 'ChIP', 'DNase', 'PWM', 'Footprint', 'PWM_matched', 'Footprint_matched']

    @staticmethod
    def _score_category(dataset):
        '''private: returns one of the categories of evidence that are needed for scoring.'''
        # score categories are slighly different from regulome categories
        collection_type = dataset.get('collection_type')  # resident_regionset dataset
        if collection_type == 'ChIP-seq':
            return 'ChIP'
        if collection_type in ['DNase-seq', 'FAIRE-seq']:  # TODO: confirm FAIRE is lumped in
            return 'DNase'                                       # aka Chromatin_Structure
        if collection_type == 'PWMs':
            return 'PWM'
        if collection_type == 'Footprints':
            return 'Footprint'
        if collection_type in ['eQTLs', 'dsQTLs']:
            return 'eQTL'
        return None

    def _regulome_category(self, score_category=None, dataset=None):
        '''private: returns one of the categories used to present evidence in a bed file.'''
        # regulome category 'Motifs' contains score categories 'PWM' and 'Footprint'
        if score_category is None:
            if dataset is None:
                log.warn('Warning: _regulome_category(), no score_category or dataset provided.')
                return '???'
            score_category = self._score_category(dataset)
        if score_category == 'ChIP':
            return 'Protein_Binding'
        if score_category == 'DNase':
            return 'Chromatin_Structure'
        if score_category in ['PWM', 'Footprint']:
            return 'Motifs'
        if score_category == 'eQTL':
            return 'Single_Nucleotides'
        return '???'

    def regulome_evidence(self, datasets):
        '''Returns evidence for scoring: datasets in a characterized dict'''
        evidence = {}
        targets = {'ChIP': [], 'PWM': [], 'Footprint': []}
        for dataset in datasets.values():
            character = self._score_category(dataset)
            if character is None:
                continue
            if character not in evidence:
                evidence[character] = []
            evidence[character].append(dataset)
            target = dataset.get('target')
            if target and character in ['ChIP', 'PWM', 'Footprint']:
                if isinstance(target, str):
                    targets[character].append(target)
                elif isinstance(target, list):  # rare but PWM targets might be list
                    for targ in target:
                        targets[character].append(targ)

        # Targets... For each ChIP target, there could be a PWM and/or Footprint to match
        for target in targets['ChIP']:
            if target in targets['PWM']:
                if 'PWM_matched' not in evidence:
                    evidence['PWM_matched'] = []
                evidence['PWM_matched'].append(target)
            if target in targets['Footprint']:
                if 'Footprint_matched' not in evidence:
                    evidence['Footprint_matched'] = []
                evidence['Footprint_matched'].append(target)

        return evidence

    def _write_a_brief(self, category, snp_evidence):
        '''private: given evidence for a category make a string that summarizes it'''
        snp_evidence_category = snp_evidence[category]

        # What do we want the brief to look like?
        # Regulome: Chromatin_Structure|DNase-seq|Chorion|,
        #           Chromatin_Structure|DNase-seq|Adultcd4th1|,
        #           Protein_Binding|ChIP-seq|E2F1|MCF-7|, ...
        # Us: Chromatin_Structure:DNase-seq:|ENCSR...|Chorion|,|ENCSR...|Adultcd4th1| (tab)
        #           Protein_Binding/ChIP-seq:|ENCSR...|E2F1|MCF-7|,|ENCSR...|SP4|H1-hESC|
        brief = ''
        cur_score_category = ''
        cur_regdb_category = ''
        for dataset in snp_evidence_category:
            new_score_category = self._score_category(dataset)
            if cur_score_category != new_score_category:
                cur_score_category = new_score_category
                new_regdb_category = self._regulome_category(cur_score_category)
                if cur_regdb_category != new_regdb_category:
                    cur_regdb_category = new_regdb_category
                    if brief != '':  # 'PWM' and 'Footprint' are both 'Motif'
                        brief += ';'
                    brief += '%s:' % cur_regdb_category
                brief += '%s:|' % cur_score_category
            try:
                brief += dataset.get('@id', '').split('/')[-2] + '|'  # accession is buried in @id
            except Exception:
                brief += '|'
            target = dataset.get('target')
            if target:
                if isinstance(target, list):
                    target = '/'.join(target)
                brief += target.replace(' ', '') + '|'
            biosample = dataset.get('biosample_term_name', dataset.get('biosample_summary'))
            if biosample:
                brief += biosample.replace(' ', '') + '|'
            brief += ','
        return brief[:-1]   # remove last comma

    def make_a_case(self, snp):
        '''Convert evidence json to list of evidence strings for bed batch downloads.'''
        case = {}
        if 'evidence' in snp:
            for category in snp['evidence'].keys():
                if category.endswith('_matched'):
                    case[category] = ','.join(snp['evidence'][category])
                else:
                    case[category] = self._write_a_brief(category, snp['evidence'])
        return case

    @staticmethod
    def _score(charactization):
        '''private: returns regulome score from characterization set'''
        if 'eQTL' in charactization:
            if 'ChIP' in charactization:
                if 'DNase':
                    if 'PWM_matched' in charactization and 'Footprint_matched' in charactization:
                        return '1a'
                    if 'PWM' in charactization and 'Footprint' in charactization:
                        return '1b'
                    if 'PWM_matched' in charactization:
                        return '1c'
                    if 'PWM' in charactization:
                        return '1d'
                elif 'PWM_matched' in charactization:
                    return '1e'
                return '1f'
            if 'DNase' in charactization:
                return '1f'
        if 'ChIP' in charactization:
            if 'DNase':
                if 'PWM_matched' in charactization and 'Footprint_matched' in charactization:
                    return '2a'
                if 'PWM' in charactization and 'Footprint' in charactization:
                    return '2b'
                if 'PWM_matched' in charactization:
                    return '2c'
                if 'PWM' in charactization:
                    return '3a'
            elif 'PWM_matched' in charactization:
                return '3b'
            if 'DNase' in charactization:
                return '4'
            return '5'
        if 'DNase' in charactization:
            return '5'
        if 'PWM' in charactization or 'Footprint' in charactization or 'eQTL' in charactization:
            return '6'

        return None  # "Found: " + str(characterize)

    def regulome_score(self, datasets, evidence=None):
        '''Calculate RegulomeDB score based upon hits and voodoo'''
        if not evidence:
            evidence = self.regulome_evidence(datasets)
            if not evidence:
                return None
        return self._score(set(evidence.keys()))

    @staticmethod
    def _snp_window(snps, window, center_pos=None):
        '''Reduce a list of snps to a set number of snps centered around position'''
        if len(snps) <= window:
            return snps

        # find ix of pos NOTE: luckily these are sorted on start!
        ix = 0
        for snp in snps:
            if snp['start'] >= center_pos:
                break
            ix += 1

        first_ix = int(ix - (window / 2))
        if first_ix > 0:
            snps = snps[first_ix:]
        return snps[:window]

    def _scored_snps(self, assembly, chrom, start, end, window=-1, center_pos=None):
        '''For a region, yields all SNPs with scores'''
        snps = self.find_snps(assembly, chrom, start, end)
        if not snps:
            return
        if window > 0:
            snps = self._snp_window(snps, window, center_pos)

        start = snps[0]['start']  # SNPs must be in location order!
        end = snps[-1]['end']                                        # MUST do SLOW peaks_too
        (peaks, details) = self.find_peaks_filtered(assembly, chrom, start, end, peaks_too=True)
        if not peaks or not details:
            for snp in snps:
                snp['score'] = None
                yield snp
                return

        last_uuids = tuple()  # for comparison below: list in deterministic order and faster than a set
        last_snp = {}
        for snp in snps:
            snp['score'] = None  # default
            snp['assembly'] = assembly
            snp_uuids = tuple(self._peak_uuids_in_overlap(peaks, snp['chrom'], snp['start']))
            if snp_uuids:
                if snp_uuids == last_uuids:  # evidence hasn't changed since last snp
                    if last_snp:
                        snp['score'] = last_snp['score']
                        if 'evidence' in last_snp:
                            snp['evidence'] = last_snp['evidence']
                    yield snp
                    continue
                else:
                    last_uuids = snp_uuids
                    snp_details = self._filter_details(details, uuids=list(snp_uuids))
                    if snp_details:
                        (snp_datasets, _snp_files) = self.details_breakdown(snp_details)
                        if snp_datasets:
                            snp_evidence = self.regulome_evidence(snp_datasets)
                            if snp_evidence:
                                snp['score'] = self.regulome_score(snp_datasets, snp_evidence)
                                snp['evidence'] = snp_evidence
                                # snp['datasets'] = snp_datasets
                                # snp['files'] = snp_files
                                last_snp = snp
                                yield snp
                                continue
            # if we are here this snp had no score
            last_snp = {}
            yield snp

    def _scored_regions(self, assembly, chrom, start, end):
        '''For a region, yields sub-regions (start, end, score) of contiguous numeric score > 0'''
        (peaks, details) = self.find_peaks_filtered(assembly, chrom, start, end, peaks_too=True)
        if not peaks or not details:
            # Not an unexpected case
            return

        last_uuids = tuple()  # for comparison below: list in deterministic order and faster than a set
        region_start = 0
        region_end = 0
        region_score = 0
        num_score = 0
        for base in range(start, end):
            base_uuids = tuple(self._peak_uuids_in_overlap(peaks, chrom, base))
            if base_uuids:
                if base_uuids == last_uuids:  # set() == set() Is there a more efficient way?
                    region_end = base  # extend region
                    continue
                else:
                    last_uuids = base_uuids
                    base_details = self._filter_details(details, uuids=list(base_uuids))
                    if base_details:
                        (base_datasets, _base_files) = self.details_breakdown(base_details)
                        if base_datasets:
                            base_evidence = self.regulome_evidence(base_datasets)
                            if base_evidence:
                                score = self.regulome_score(base_datasets, base_evidence)
                                if score:
                                    num_score = self.numeric_score(score)
                                    if num_score == region_score:
                                        region_end = base
                                        continue
                                    if region_score > 0:  # end previous region?
                                        yield (region_start, region_end, region_score)
                                    # start new region
                                    region_score = num_score
                                    region_start = base
                                    region_end = base
                                    continue
            # if we are here this base had no score
            if region_score > 0:  # end previous region?
                yield (region_start, region_end, region_score)
                region_score = 0
                last_uuids = base_uuids  # zero score so don't try these uuids again!

        if region_score > 0:  # end previous region?
            yield (region_start, region_end, region_score)

    def nearby_snps(self, assembly, chrom, pos, rsid=None, max_snps=10, scores=False):
        '''Return SNPs nearby to the chosen SNP.'''
        if rsid:
            max_snps += 1

        range_end = self.cap_at_chrom_size(assembly, chrom, (pos + int(NEARBY_SNP_WINDOW / 2)))
        range_start = range_end - NEARBY_SNP_WINDOW
        if range_start < 0:
            range_end += 0 - range_start
            range_start = 0

        if scores:
            snps = self._scored_snps(assembly, chrom, range_start, range_end, max_snps, pos)
            for snp in snps:
                snp.pop('evidence', None)  # don't need this much detail
        else:
            snps = self.find_snps(assembly, chrom, range_start, range_end)
            snps = self._snp_window(snps, max_snps, pos)

        return snps

    def iter_scored_snps(self, assembly, chrom, start, end, base_level=False):
        '''For a region, iteratively yields all SNPs with scores.'''
        end = self.cap_at_chrom_size(assembly, chrom, end)
        if end < start:
            log.warn('Warning: iter_scored_snps() called for invalid region %s %s:%d-%d' %
                     (assembly, chrom, start, end))
            return
        chunk_size = REGDB_SCORE_CHUNK_SIZE
        chunk_start = start
        while chunk_start <= end:
            chunk_end = chunk_start + chunk_size
            if chunk_end > end:
                chunk_end = end
            yield from self._scored_snps(assembly, chrom, chunk_start, chunk_end)
            chunk_start += chunk_size

    def iter_scored_signal(self, assembly, chrom, start, end):
        '''For a region, iteratively yields all bedGraph styled regions
           of contiguous numeric score.'''
        end = self.cap_at_chrom_size(assembly, chrom, end)
        if end < start:
            log.warn('Warning: iter_scored_signal() called for invalid region %s %s:%d-%d' %
                     (assembly, chrom, start, end))
            return
        chunk_size = REGDB_SCORE_CHUNK_SIZE
        chunk_start = start
        while chunk_start <= end:
            chunk_end = chunk_start + chunk_size
            if chunk_end > end:
                chunk_end = end
            yield from self._scored_regions(assembly, chrom, chunk_start, chunk_end)
            chunk_start += chunk_size

    def live_score(self, assembly, chrom, pos):
        '''Returns score knowing single position and nothing more.'''
        (peaks, details) = self.find_peaks_filtered(assembly, chrom, pos, pos)
        if not peaks or not details:
            return None
        (datasets, _files) = self.details_breakdown(details)
        return self.regulome_score(datasets)

    @staticmethod
    def numeric_score(alpha_score):
        '''converst str score to numeric representation (for bedGraph)'''
        try:
            return REGDB_NUM_SCORES[REGDB_STR_SCORES.index(alpha_score)]
        except Exception:
            return 0

    @staticmethod
    def str_score(int_score):
        '''converst numeric representation of score to standard string score'''
        try:
            return REGDB_STR_SCORES[REGDB_NUM_SCORES.index(int_score)]
        except Exception:
            return ''

