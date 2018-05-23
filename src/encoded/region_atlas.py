import logging
import json
from elasticsearch.exceptions import (
    NotFoundError
)
from .region_indexer import (
    snp_index_key,
    RESIDENT_REGIONSET_KEY,
    FOR_REGION_SEARCH,
    FOR_REGULOME_DB,
    FOR_MULTIPLE_USES,
    ENCODED_ALLOWED_STATUSES,
    ENCODED_DATASET_TYPES,
    REGULOME_ALLOWED_STATUSES,
    REGULOME_DATASET_TYPES
)

log = logging.getLogger(__name__)

# ##################################
# RegionAtlas and RegulomeAtlas classes encapsulate the methods
# for querying regions and SNPs from the region_index.
# ##################################


# RegulomeDB scores for bigWig (bedGraph) are converted to numeric and can be converted back
REGDB_STR_SCORES = ['1a','1b','1c','1d','1e','1f','2a','2b','2c','3a','3b','4','5','6']
REGDB_NUM_SCORES = [1000, 950, 900, 850, 800, 750, 600, 550, 500, 450, 400,300,200,100]

#def includeme(config):
#    config.scan(__name__)
#    registry = config.registry
#    registry['region'+INDEXER] = RegionIndexer(registry)

class RegionAtlas(object):
    '''Methods for getting stuff out of the region_index.'''

    def __init__(self, region_es):
        self.region_es = region_es
        self.expected_use=FOR_REGULOME_DB

    def type(self):
        return 'region search'

    def allowed_statuses(self):
        return ENCODED_ALLOWED_STATUSES

    def set_type(self):
        return ENCODED_DATASET_TYPES

    def set_indices(self):
        indices = [ set_type.lower() for set_type in ENCODED_DATASET_TYPES ]
        return indices

    def snp(self, assembly, rsid):
        '''Return single SNP by rsid and assembly'''
        try:
            res = self.region_es.get(index=snp_index_key(assembly), doc_type='_all', id=rsid)
        except Exception:
            return None

        return res['_source']

    def _range_query(self, start, end, snps=False, with_inner_hits=False):
        '''private: return peak query'''
        # get all peaks that overlap requested region:
        #     peak.start <= requested.end and peak.end >= requested.start
        prefix = 'positions.'
        if snps:
            prefix = ''

        range_clause = {
            'bool': {
                'must': [
                    {'range': {prefix + 'start': {'lte': end  }}},
                    {'range': {prefix + 'end':   {'gte': start}}}
                ]
            }
        }
        if snps:
            filter = {'bool': {'should': [ range_clause ]}}
        else:
            filter = {
                'nested': {
                    'path': 'positions',
                    'query': {
                        'bool': {'should': [ range_clause ]}
                    }
                }
            }

        query = {
            'query': {
                'bool': {
                    'filter': filter
                }
            },
            '_source': snps,  # True is snps, False if regions
        }
        # special SLOW query will return inner_hits positions
        if with_inner_hits:
            query['query']['bool']['filter']['nested']['inner_hits'] = {'size': 99999}
        return query

    def find_snps(self, assembly, chrom, start, end):
        '''Return all SNPs in a region.'''
        range_query = self._range_query(start, end, snps=True)

        try:
            results = self.region_es.search(index=snp_index_key(assembly), doc_type=chrom,
                                            _source=True, body=range_query, size=99999)
        except NotFoundError:
            return []
        except Exception as e:
            return []  # TODO: andle errors?
        #log.warn('Find SNPS in %s:%d-%d found %d', chrom, start, end, len(results['hits']['hits']))

        return [ hit['_source'] for hit in results['hits']['hits'] ]

    #def snp_suggest(self, assembly, text):
    # Using suggest with 60M of rsids leads to es crashing during SNP indexing

    def find_peaks(self, assembly, chrom, start, end, peaks_too=False):
        '''Return all peaks in a region.  NOTE: peaks are not filtered by use.'''
        range_query = self._range_query(start, end, False, peaks_too)

        try:
            results = self.region_es.search(index=chrom.lower(), doc_type=assembly, _source=False,
                                        body=range_query, size=99999)
        except NotFoundError:
            return None
        except Exception as e:
            return None

        return list(results['hits']['hits'])

    def _resident_details(self, uuids, use=None):
        '''private: returns resident details filtered by use.'''
        if use is None:
            use = self.expected_use
        use_types = [FOR_MULTIPLE_USES, use]
        try:
            id_query = {"query": {"ids": {"values": uuids}}}
            res = self.region_es.search(index=RESIDENT_REGIONSET_KEY, body=id_query, doc_type=use_types, size=99999)
        except Exception:
            return None

        details = {}
        hits = res.get("hits", {}).get("hits", [])
        for hit in hits:
            details[hit["_id"]] = hit["_source"]

        return details

    def _filter_peaks_by_use(self, peaks, use=None):
        '''private: returns peaks and resident details, both filtered by use'''
        uuids = list(set([ peak['_id'] for peak in peaks ]))
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

    def _peak_uuids_in_overlap(self, peaks, chrom, start, end=None):
        '''private: returns the only the uuids for peaks that overlap a given location'''
        if end is None:
            end = start

        overlap = []
        for peak in peaks:
            for hit in peak['inner_hits']['positions']['hits']['hits']:
                if chrom == peak['_index'] and start <= hit['_source']['end'] and end >= hit['_source']['start']:
                    overlap.append(peak)
                    break

        return list(set([ peak['_id'] for peak in overlap ]))

    def _filter_details(self, details, uuids=None, peaks=None):
        '''private: returns only the details that match the uuids'''
        if uuids is None:
            assert(peaks is not None)
            uuids = list(set([ peak['_id'] for peak in peaks ]))
        filtered = {}
        for uuid in uuids:
            if uuid in details:  # region peaks may not be in regulome only details
                filtered[uuid] = details[uuid]
        return filtered

    def details_breakdown(self, details, uuids=None):
        '''Return dataset and file dicts from resident details dicts.'''
        if not details:
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
        self.expected_use=FOR_REGULOME_DB

    def type(self):
        return 'regulome'

    def allowed_statuses(self):
        return REGULOME_ALLOWED_STATUSES

    def set_type(self):
        return ['Dataset']

    def set_indices(self):
        indices = [ set_type.lower() for set_type in REGULOME_DATASET_TYPES ]
        return indices

    #def snp_suggest(self, assembly, text):
    # Using suggest with 60M of rsids leads to es crashing during SNP indexing

    def evidence_categories(self):
        '''Returns a list of regulome evidence categories'''
        # TODO: Fix ategories to be collection_types!!!
        return ['eQTL', 'ChIP', 'DNase', 'PWM', 'Footprint', 'PWM_matched', 'Footprint_matched']

    def _score_category(self, dataset):
        '''private: returns one of the categories of evidence that are needed for scoring.'''
        # score categories are slighly different from regulome categories
        collection_type = dataset.get('collection_type')  # resident_regionset dataset
        if collection_type == 'ChIP-seq':
            return 'ChIP'
        if collection_type in ['DNase-seq', 'FAIRE-seq']:  # TODO: confirm FAIRE is lumped in
            return 'DNase'                                 #       aka Chromatin_Structure
        if collection_type == 'transcription factor motifs':
            return 'PWM'
        if collection_type == 'representative DNase hypersensitivity sites':
             return 'Footprint'
        if collection_type in ['eQTLs','dsQTLs']:
            return 'eQTL'
        return None

    def _regulome_category(self, score_category=None, dataset=None):
        '''private: returns one of the categories used to present evidence in a bed file.'''
        # regulome category 'Motifs' contains score categories 'PWM' and 'Footprint'
        if score_category is None:
            if dataset is None:
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
                targets[character].append(target)

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
        # Regulome: Chromatin_Structure|DNase-seq|Chorion|, Chromatin_Structure|DNase-seq|Adultcd4th1|, Protein_Binding|ChIP-seq|E2F1|MCF-7|, ...
        # Us: Chromatin_Structure:DNase-seq:|ENCSR...|Chorion|,|ENCSR...|Adultcd4th1| (tab) Protein_Binding/ChIP-seq:|ENCSR...|E2F1|MCF-7|,|ENCSR...|SP4|H1-hESC|
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
            except:
                brief += '|'
            target = dataset.get('target')
            if target:
                brief += target.replace(' ', '') + '|'
            biosample = dataset.get('biosample_term_name',dataset.get('biosample_summary'))
            if biosample:
                brief += biosample.replace(' ', '') + '|'
            brief += ','
        return brief[:-1] # remove last comma

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

    def _score(self, charactization):
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

    def _snp_window(self, snps, window, center_pos=None):
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
        '''For a region, get all SNPs with scores'''
        snps = self.find_snps(assembly, chrom, start, end)
        if not snps:
            return snps
        if window > 0:
            snps = self._snp_window(snps, window, center_pos)

        start = snps[0]['start']  # SNPs must be in location order!
        end = snps[-1]['end']                                        # MUST do SLOW peaks_too
        (peaks, details) = self.find_peaks_filtered(assembly, chrom, start, end, peaks_too=True)
        if not peaks or not details:
            for snp in snps:
                snp['score'] = None
            return snps

        for snp in snps:
            snp['assembly'] = assembly
            snp_uuids = self._peak_uuids_in_overlap(peaks, snp['chrom'], snp['start'])
            if len(snp_uuids) == 0:
                snp['score'] = None  # 'no overlap'
                continue
            snp_details = self._filter_details(details, uuids=snp_uuids)
            if not snp_details:
                log.warn('Unexpected empty details for SNP: %s', snp['rsid'])
                snp['score'] = None
                continue
            (snp_datasets, snp_files) = self.details_breakdown(snp_details)
            if not snp_datasets:
                log.warn('Unexpected failure to breakdown snp details for SNP: %s', snp['rsid'])
                snp['score'] = None
                continue
            snp_evidence = self.regulome_evidence(snp_datasets)
            if not snp_evidence:
                snp['score'] = None  # 'no overlap'
                continue
            snp['score'] = self.regulome_score(snp_datasets, snp_evidence)
            snp['evidence'] = snp_evidence
            #snp['datasets'] = snp_datasets
            #snp['files'] = snp_files
        return snps

    def nearby_snps(self, assembly, chrom, pos, rsid=None, max_snps=10, scores=False):
        '''Return SNPs nearby to the chosen SNP.'''
        if rsid:
            max_snps += 1

        range_start = pos - 800
        range_end = pos + 800
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

    def iter_scored_snps(self, assembly, chrom, start, end):
        '''For a region, iteratively get all SNPs with scores'''
        if end < start:
            return
        chunk_size = 100000
        chunk_start = start
        #all_snps = []
        while chunk_start <= end:
            chunk_end = chunk_start + chunk_size
            if chunk_end > end:
                chunk_end = end
            snps = self._scored_snps(assembly, chrom, chunk_start, chunk_end)
            if snps:
                for snp in snps:
                    yield snp      # yeild yielded a 504 gateway timeout!
                #if all_snps:
                #    all_snps.extend(snps)
                #else:
                #    all_snps = snps
            chunk_start += chunk_size
        #return all_snps

    def live_score(self, assembly, chrom, pos):
        '''Returns score knowing single position and nothing more.'''
        (peaks, details) = self.find_peaks_filtered(assembly, chrom, pos, pos)
        if not peaks or not details:
            return None
        (datasets, files) = self.details_breakdown(details)
        return self.regulome_score(datasets)

    def numeric_score(self, alpha_score):
        '''converst str score to numeric representation (for bedGraph)'''
        try:
            return REGDB_NUM_SCORES[REGDB_STR_SCORES.index(alpha_score)]
        except:
            return 0

    def str_score(self, int_score):
        '''converst numeric representation of score to standard string score'''
        try:
            return REGDB_STR_SCORES[REGDB_NUM_SCORES.index(int_score)]
        except:
            return ''
