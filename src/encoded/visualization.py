from pyramid.response import Response
from pyramid.view import view_config
from snovault import Item
from collections import OrderedDict
from copy import deepcopy
import json
import os
from urllib.parse import (
    parse_qs,
    urlencode,
)
from snovault.elasticsearch.interfaces import ELASTIC_SEARCH
import time
from pkg_resources import resource_filename

# Note: Required for Bek's cache priming solution.
from pyramid.events import subscriber
from .peak_indexer import AfterIndexedExperimentsAndDatasets

import logging

log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)
log.setLevel(logging.INFO)

# NOTE: Caching is turned on and off with this global AND TRACKHUB_CACHING in peak_indexer.py
USE_CACHE = True  # Use elasticsearch caching of individual acc_composite blobs


_ASSEMBLY_MAPPER = {
    'GRCh38-minimal': 'hg38',
    'GRCh38': 'hg38',
    'GRCh37': 'hg19',
    'mm10-minimal': 'mm10',
    'GRCm38': 'mm10',
    'NCBI37': 'mm9',
    'BDGP6': 'dm6',
    'BDGP5': 'dm3',
    'WBcel235': 'ce11'
}

_ASSEMBLY_MAPPER_FULL = {
    'GRCh38':         { 'species':          'Homo sapiens',     'assembly_reference': 'GRCh38',
                        'common_name':      'human',
                        'ucsc_assembly':    'hg38',
                        'ensembl_host':     'www.ensembl.org',
    },
    'GRCh38-minimal': { 'species':          'Homo sapiens',     'assembly_reference': 'GRCh38',
                        'common_name':      'human',
                        'ucsc_assembly':    'hg38',
                        'ensembl_host':     'www.ensembl.org',
    },
    'hg19': {           'species':          'Homo sapiens',     'assembly_reference': 'GRCh37',
                        'common_name':      'human',
                        'ucsc_assembly':    'hg19',
                        'ensembl_host':     'grch37.ensembl.org',
    },
    'mm10': {           'species':          'Mus musculus',     'assembly_reference': 'GRCm38',
                        'common_name':      'mouse',
                        'ucsc_assembly':    'mm10',
                        'ensembl_host':     'www.ensembl.org',
    },
    'mm10-minimal': {   'species':          'Mus musculus',     'assembly_reference': 'GRCm38',
                        'common_name':      'mouse',
                        'ucsc_assembly':    'mm10',
                        'ensembl_host':     'www.ensembl.org',
    },
    'mm9': {            'species':          'Mus musculus',     'assembly_reference': 'NCBI37',
                        'common_name':      'mouse',
                        'ucsc_assembly':    'mm9',
                        'ensembl_host':     'may2012.archive.ensembl.org',
    },
    'dm6': {    'species':          'Drosophila melanogaster',  'assembly_reference': 'BDGP6',
                'common_name':      'fruit fly',
                'ucsc_assembly':    'dm6',
                'ensembl_host':     'www.ensembl.org',
    },
    'dm3': {    'species':          'Drosophila melanogaster',  'assembly_reference': 'BDGP5',
                'common_name':      'fruit fly',
                'ucsc_assembly':    'dm3',
                'ensembl_host':     'dec2014.archive.ensembl.org',
    },
    'ce11': {   'species':          'Caenorhabditis elegans',   'assembly_reference': 'WBcel235',
                'common_name':      'worm',
                'ucsc_assembly':    'ce11',
                'ensembl_host':     'www.ensembl.org',
    },
    'ce10': {   'species':          'Caenorhabditis elegans',   'assembly_reference': 'WS220',
                'common_name':      'worm',
                'ucsc_assembly':    'ce10',
    },
    'ce6': {    'species':          'Caenorhabditis elegans',   'assembly_reference': 'WS190',
                'common_name':      'worm',
                'ucsc_assembly':    'ce6',
    },
    'J02459.1': {   'species':      'Escherichia virus Lambda', 'assembly_reference': 'J02459.1',
                    'common_name':  'lambda phage',
    },
}

def includeme(config):
    config.add_route('batch_hub', '/batch_hub/{search_params}/{txt}')
    config.add_route('batch_hub:trackdb', '/batch_hub/{search_params}/{assembly}/{txt}')
    config.scan(__name__)


PROFILE_START_TIME = 0  # For profiling within this module

TAB = '\t'
NEWLINE = '\n'
HUB_TXT = 'hub.txt'
GENOMES_TXT = 'genomes.txt'
TRACKDB_TXT = 'trackDb.txt'
BIGWIG_FILE_TYPES = ['bigWig']
BIGBED_FILE_TYPES = ['bigBed']

VISIBLE_DATASET_STATUSES = ["released"]
VISIBLE_FILE_STATUSES = ["released"]
VISIBLE_DATASET_TYPES = ["Experiment", "Annotation"]
VISIBLE_DATASET_TYPES_LC = ["experiment", "annotation"]

# ASSEMBLY_MAPPINGS is needed to ensure that mm10 and mm10-minimal will
#                   get combined into the same trackHub.txt
# This is necessary because mm10 and mm10-minimal are only mm10 at UCSC,
# so the 2 must be collapsed into one.
ASSEMBLY_MAPPINGS = {
    # any term:       [ set of encoded terms used ]
    "GRCh38":           ["GRCh38", "GRCh38-minimal"],
    "GRCh38-minimal":   ["GRCh38", "GRCh38-minimal"],
    "hg38":             ["GRCh38", "GRCh38-minimal"],
    "GRCh37":           ["hg19", "GRCh37"],  # Is GRCh37 ever in encoded?
    "hg19":             ["hg19", "GRCh37"],
    "GRCm38":           ["mm10", "mm10-minimal", "GRCm38"],  # Is GRCm38 ever in encoded?
    "mm10":             ["mm10", "mm10-minimal", "GRCm38"],
    "mm10-minimal":     ["mm10", "mm10-minimal", "GRCm38"],
    "GRCm37":           ["mm9", "GRCm37"],  # Is GRCm37 ever in encoded?
    "mm9":              ["mm9", "GRCm37"],
    "BDGP6":            ["dm4", "BDGP6"],
    "dm4":              ["dm4", "BDGP6"],
    "BDGP5":            ["dm3", "BDGP5"],
    "dm3":              ["dm3", "BDGP5"],
    # "WBcel235":         ["WBcel235"], # defaults to term: [ term ]
    }


# Supported tokens are the only tokens the code currently knows how to look up.
SUPPORTED_MASK_TOKENS = [
    "{replicate}",         # replicate that that will be displayed: ("rep1", "combined")
    "{rep_tech}",          # The rep_tech if desired ("rep1_1", "combined")
    "{replicate_number}",  # The replicate number displayed for visualized track: ("1", "0")
    "{biological_replicate_number}",
    "{technical_replicate_number}",
    "{assay_title}",
    "{assay_term_name}",                      # dataset.assay_term_name
    "{annotation_type}",                      # some datasets have annotation type and not assay
    "{output_type}",                          # files.output_type
    "{accession}", "{experiment.accession}",  # "{accession}" is assumed to be experiment.accession
    "{file.accession}",
    "{@id}", "{@type}",                       # dataset only
    "{target}", "{target.label}",             # Either is acceptible
    "{target.title}",
    "{target.name}",                          # Used in metadata URLs
    "{target.investigated_as}",
    "{biosample_term_name}", "{biosample_term_name|multiple}",  # "|multiple": none means multiple
    "{output_type_short_label}",                # hard-coded translation from output_type to very
                                                # short version
    "{replicates.library.biosample.summary}",   # Idan, Forrest and Cricket are conspiring to move
                                                # to dataset.biosample_summary & make it shorter
    "{replicates.library.biosample.summary|multiple}",   # "|multiple": none means multiple
    "{assembly}",                               # you don't need this in titles, but it is crucial
                                                # variable and seems to not be being applied
                                                # # correctly in the html generation
    "{lab.title}",                              # In metadata
    # TODO "{software? or pipeline?}",  # Cricket: "I am stumbling over the fact that we
    #                                   #    can't distinguish tophat and star produced files"
    # TODO "{phase}",                   # Cricket: "If we get to the point of being fancy
    #                                   #    in the replication timing, then we need this,
    #                                   #    otherwise it bundles up in the biosample summary now"
    ]

# Simple tokens are a straight lookup, no questions asked
SIMPLE_DATASET_TOKENS = ["{biosample_term_name}", "{accession}", "{assay_title}",
                         "{assay_term_name}", "{annotation_type}", "{@id}", "{@type}"]

# static group defs are keyed by group title (or special token) and consist of
# tag: (optional) unique terse key for referencing group
# groups: (optional) { subgroups keyed by subgroup title }
# group_order: (optional) [ ordered list of subgroup titles ]
# other definitions

# live group defs are keyed by tag and are the transformed in memory version of static defs
# title: (required) same as the static group's key
# groups: (if appropriate) { subgroups keyed by subgroup tag }
# group_order: (if appropriate) [ ordered list of subgroup tags ]

VIS_DEFS_FOLDER = "static/vis_defs/"
VIS_DEFS_BY_TYPE = {}
COMPOSITE_VIS_DEFS_DEFAULT = {}


def lookup_token(token, dataset, a_file=None):
    '''Encodes the string to swap special characters and remove spaces.'''

    if token not in SUPPORTED_MASK_TOKENS:
        log.warn("Attempting to look up unexpected token: '%s'" % token)
        return "unknown token"

    if token in SIMPLE_DATASET_TOKENS:
        term = dataset.get(token[1:-1])
        if term is None:
            term = "Unknown " + token[1:-1].split('_')[0].capitalize()
        return term
    elif token == "{experiment.accession}":
        return dataset['accession']
    elif token in ["{target}", "{target.label}", "{target.name}", "{target.title}"]:
        target = dataset.get('target', {})
        if isinstance(target, list):
            if len(target) > 0:
                target = target[0]
            else:
                target = {}
        if token.find('.') > -1:
            sub_token = token.strip('{}').split('.')[1]
        else:
            sub_token = "label"
        return target.get(sub_token, "Unknown Target")
    elif token in ["{target.name}", "{target.investigated_as}"]:
        target = dataset.get('target', {})
        if isinstance(target, list):
            if len(target) > 0:
                target = target[0]
            else:
                target = {}
        if token == "{target.name}":
            return target.get('label', "Unknown Target")
        elif token == "{target.investigated_as}":
            investigated_as = target.get('investigated_as', "Unknown Target")
            if not isinstance(investigated_as, list):
                return investigated_as
            elif len(investigated_as) > 0:
                return investigated_as[0]
            else:
                return "Unknown Target"
    elif token in ["{replicates.library.biosample.summary}",
                   "{replicates.library.biosample.summary|multiple}"]:
        term = None
        replicates = dataset.get("replicates", [])
        if replicates:
            term = replicates[0].get("library", {}).get("biosample", {}).get("summary")
        if term is None:
            term = dataset.get("{biosample_term_name}")
        if term is None:
            if token.endswith("|multiple}"):
                term = "multiple biosamples"
            else:
                term = "Unknown Biosample"
        return term
    elif token == "{lab.title}":
        return dataset['lab'].get('title', 'unknown')
    elif token == "{biosample_term_name|multiple}":
        return dataset.get("biosample_term_name", "multiple biosamples")
    # TODO: rna_species
    # elif token == "{rna_species}":
    #     if replicates.library.nucleic_acid = polyadenylated mRNA
    #        rna_species = polyA RNA
    #     elseif replicates.library.nucleic_acid = RNA
    #        if polyadenylated mRNA in replicates.library.depleted_in_term_name
    #                rna_species = polyA depleted RNA
    #        else
    #                rna_species = total RNA
    elif a_file is not None:
        if token == "{file.accession}":
            return a_file['accession']
        elif token == "{output_type}":
            return a_file['output_type']
        elif token == "{output_type_short_label}":
            output_type = a_file['output_type']
            return OUTPUT_TYPE_8CHARS.get(output_type, output_type)
        elif token == "{replicate}":
            rep_tag = a_file.get("rep_tag")
            if rep_tag is not None:
                while len(rep_tag) > 4:
                    if rep_tag[3] != '0':
                        break
                    rep_tag = rep_tag[0:3] + rep_tag[4:]
                return rep_tag
            rep_tech = a_file.get("rep_tech")
            if rep_tech is not None:
                return rep_tech.split('_')[0]  # Should truncate tech_rep
            rep_tech = rep_for_file(a_file)
            return rep_tech.split('_')[0]  # Should truncate tech_rep
        elif token == "{replicate_number}":
            rep_tag = a_file.get("rep_tag", a_file.get("rep_tech", rep_for_file(a_file)))
            if not rep_tag.startswith("rep"):
                return "0"
            return rep_tag[3:].split('_')[0]
        elif token == "{biological_replicate_number}":
            rep_tech = a_file.get("rep_tech", rep_for_file(a_file))
            if not rep_tech.startswith("rep"):
                return "0"
            return rep_tech[3:].split('_')[0]
        elif token == "{technical_replicate_number}":
            rep_tech = a_file.get("rep_tech", rep_for_file(a_file))
            if not rep_tech.startswith("rep"):
                return "0"
            return rep_tech.split('_')[1]
        elif token == "{rep_tech}":
            return a_file.get("rep_tech", rep_for_file(a_file))
        else:
            return ""
    else:
        log.warn('Untranslated token: "%s"' % token)
        return "unknown"


def convert_mask(mask, dataset, a_file=None):
    '''Given a mask with one or more known {term_name}s, replaces with values.'''
    working_on = mask
    chars = len(working_on)
    while chars > 0:
        beg_ix = working_on.find('{')
        if beg_ix == -1:
            break
        end_ix = working_on.find('}')
        if end_ix == -1:
            break
        term = lookup_token(working_on[beg_ix:end_ix+1], dataset, a_file=a_file)
        new_mask = []
        if beg_ix > 0:
            new_mask = working_on[0:beg_ix]
        new_mask += "%s%s" % (term, working_on[end_ix+1:])
        chars = len(working_on[end_ix+1:])
        working_on = ''.join(new_mask)

    return working_on


def load_vis_defs():
    '''Loads 'vis_defs' (visualization definitions by assay type) from a static file.'''
    global VIS_DEFS_FOLDER
    global VIS_DEFS_BY_TYPE
    global COMPOSITE_VIS_DEFS_DEFAULT
    folder = resource_filename(__name__, VIS_DEFS_FOLDER)
    files = os.listdir(folder)
    for filename in files:
        if filename.endswith('.json'):
            with open(folder + filename) as fh:
                log.debug('Preparing to load %s' % (filename))
                vis_def = json.load(fh)
                if vis_def:
                    VIS_DEFS_BY_TYPE.update(vis_def)
    COMPOSITE_VIS_DEFS_DEFAULT = vis_def.get("opaque",{})


def get_vis_type(dataset):
    '''returns the best static composite definition set, based upon dataset.'''
    global VIS_DEFS_BY_TYPE
    if not VIS_DEFS_BY_TYPE:
        load_vis_defs()

    assay = dataset.get("assay_term_name", 'none')

    if isinstance(assay, list):
        if len(assay) == 1:
            assay = assay[0]
        else:
            log.warn("assay_term_name for %s is unexpectedly a list %s" %
                     (dataset['accession'], str(assay)))
            return "opaque"

    # simple rule defined in most vis_defs
    for vis_type in sorted(VIS_DEFS_BY_TYPE.keys(), reverse=True):  # Reverse pushes anno to bottom
        if "rule" in VIS_DEFS_BY_TYPE[vis_type]:
            rule = VIS_DEFS_BY_TYPE[vis_type]["rule"].replace('{assay_term_name}', assay)
            if rule.find('{') != -1:
                rule = convert_mask(rule, dataset)
            if eval(rule):
                return vis_type

    # Ugly rules:
    if assay in ["RNA-seq", "single cell isolation followed by RNA-seq"]:
        reps = dataset.get("replicates", [])  # NOTE: overly cautious
        if len(reps) < 1:
            log.warn("Could not distinguish between long and short RNA for %s because there are "
                     "no replicates.  Defaulting to short." % (dataset.get("accession")))
            return "SRNA"  # this will be more noticed if there is a mistake
        size_range = reps[0].get("library", {}).get("size_range", "")
        if size_range.startswith('>'):
            try:
                min_size = int(size_range[1:])
                max_size = min_size
            except:
                log.warn("Could not distinguish between long and short RNA for %s.  "
                         "Defaulting to short." % (dataset.get("accession")))
                return "SRNA"  # this will be more noticed if there is a mistake
        elif size_range.startswith('<'):
            try:
                max_size = int(size_range[1:]) - 1
                min_size = 0
            except:
                log.warn("Could not distinguish between long and short RNA for %s.  "
                         "Defaulting to short." % (dataset.get("accession")))
                return "SRNA"  # this will be more noticed if there is a mistake
        else:
            try:
                sizes = size_range.split('-')
                min_size = int(sizes[0])
                max_size = int(sizes[1])
            except:
                log.warn("Could not distinguish between long and short RNA for %s.  "
                         "Defaulting to short." % (dataset.get("accession")))
                return "SRNA"  # this will be more noticed if there is a mistake
        if max_size <= 200 and max_size != min_size:
            return "SRNA"
        elif min_size >= 150:
            return "LRNA"
        elif (min_size + max_size)/2 >= 235:
            # This is some wicked voodoo (SRNA:108-347=227; LRNA:155-315=235)
            return "LRNA"
        else:
            return "SRNA"

    log.warn("%s (assay:'%s') has undefined vis_type" % (dataset['accession'], assay))
    return "opaque"  # This becomes a dict key later so None is not okay

# TODO:
# ENCSR000BBI (assay:'comparative genomic hybridization by array') has undefined vis_type
# ENCSR000DBZ (assay:'FAIRE-seq') has undefined vis_type
# ENCSR901QEL (assay:'protein sequencing by tandem mass spectrometry assay') has undefined vis_type
# ENCSR000AWN (assay:'transcription profiling by array assay') has undefined vis_type
# ENCSR066KKK (assay:'Repli-chip') has undefined vis_type
# ENCSR935ULX (assay:'Repli-seq') has undefined vis_type
# ENCSR000AYD (assay:'RIP-chip') has undefined vis_type
# ENCSR000CWU (assay:'RIP-seq') has undefined vis_type
# ENCSR000BCM (assay:'RNA-PET') has undefined vis_type


EXP_GROUP = "Experiment"
DEFAULT_EXPERIMENT_GROUP = {"tag": "EXP", "groups": {"one": {"title_mask": "{accession}",
                            "url_mask": "experiments/{accession}"}}}


def lookup_vis_defs(vis_type):
    '''returns the best static composite definition set, based upon dataset.'''
    global VIS_DEFS_BY_TYPE
    global COMPOSITE_VIS_DEFS_DEFAULT
    if not VIS_DEFS_BY_TYPE:
        load_vis_defs()
    vis_def = VIS_DEFS_BY_TYPE.get(vis_type, COMPOSITE_VIS_DEFS_DEFAULT)
    if EXP_GROUP not in vis_def["other_groups"]["groups"]:
        vis_def["other_groups"]["groups"][EXP_GROUP] = DEFAULT_EXPERIMENT_GROUP
    if "sortOrder" in vis_def and EXP_GROUP not in vis_def["sortOrder"]:
        vis_def["sortOrder"].append(EXP_GROUP)
    return vis_def


PENNANTS = {
    "NHGRI":     ("https://www.encodeproject.org/static/img/pennant-nhgri.png "
                  "https://www.encodeproject.org/ "
                  "\"This trackhub was automatically generated from the files and metadata found "
                  "at the ENCODE portal\""),
    "ENCODE":    ("https://www.encodeproject.org/static/img/pennant-encode.png "
                  "https://www.encodeproject.org/ "
                  "\"This trackhub was automatically generated from the ENCODE files and metadata "
                  "found at the ENCODE portal\""),
    "modENCODE": ("https://www.encodeproject.org/static/img/pennant-encode.png "
                  "https://www.encodeproject.org/ "
                  "\"This trackhub was automatically generated from the modENCODE files and "
                  "metadata found at the ENCODE portal\""),
    "GGR":       ("https://www.encodeproject.org/static/img/pennant-ggr.png "
                  "https://www.encodeproject.org/ "
                  "\"This trackhub was automatically generated from  the Genomics of "
                  "Gene Regulation files files and metadata found at the "
                  "ENCODE portal\""),
    "REMC":      ("https://www.encodeproject.org/static/img/pennant-remc.png "
                  "https://www.encodeproject.org/ "
                  "\"This trackhub was automatically generated from the Roadmap Epigentics files "
                  "and metadata found at the ENCODE portal\"")
    # "Roadmap":   "encodeThumbnail.jpg "
    #              "https://www.encodeproject.org/ "
    #              "\"This trackhub was automatically generated from the Roadmap files and "
    #              "metadata found at https://www.encodeproject.org/\"",
    # "modERN":   "encodeThumbnail.jpg "
    #             "https://www.encodeproject.org/ "
    #             "\"This trackhub was automatically generated from the modERN files and "
    #             "metadata found at https://www.encodeproject.org/\"",
    }


def find_pennent(dataset):
    '''Returns an appropriate pennantIcon given dataset's award'''
    project = dataset.get("award", {}).get("project", "NHGRI")
    return PENNANTS.get(project, PENNANTS.get("NHGRI"))


SUPPORTED_SUBGROUPS = ["Biosample", "Targets", "Assay", "Replicates", "Views", EXP_GROUP]

SUPPORTED_TRACK_SETTINGS = [
    "type", "visibility", "longLabel", "shortLabel", "color", "altColor", "allButtonPair", "html",
    "scoreFilter", "spectrum", "minGrayLevel", "itemRgb", "viewLimits",
    "autoScale", "negateValues", "maxHeightPixels", "windowingFunction", "transformFunc"]
COMPOSITE_SETTINGS = ["longLabel", "shortLabel", "visibility", "pennantIcon", "allButtonPair",
                      "html"]
VIEW_SETTINGS = SUPPORTED_TRACK_SETTINGS
TRACK_SETTINGS = ["bigDataUrl", "longLabel", "shortLabel", "type", "color", "altColor"]


OUTPUT_TYPE_8CHARS = {
    # "idat green channel": "idat gr",     # raw data
    # "idat red channel": "idat rd",       # raw data
    # "reads":"reads",                     # raw data
    # "intensity values": "intnsty",       # raw data
    # "reporter code counts": "rcc",       # raw data
    # "alignments":"aln",                  # our plan is not to visualize alignments for now
    # "unfiltered alignments":"unflt aln", # our plan is not to visualize alignments for now
    # "transcriptome alignments":"tr aln", # our plan is not to visualize alignments for now
    "minus strand signal of all reads":     "all -",
    "plus strand signal of all reads":      "all +",
    "signal of all reads":                  "all sig",
    "normalized signal of all reads":       "normsig",
    # "raw minus strand signal":"raw -",   # these are all now minus signal of all reads
    # "raw plus strand signal":"raw +",    # these are all now plus signal of all reads
    "raw signal":                           "raw sig",
    "raw normalized signal":                "nraw",
    "read-depth normalized signal":         "rdnorm",
    "control normalized signal":            "ctlnorm",
    "minus strand signal of unique reads":  "unq -",
    "plus strand signal of unique reads":   "unq +",
    "signal of unique reads":               "unq sig",
    "signal p-value":                       "pval sig",
    "fold change over control":             "foldchg",
    "exon quantifications":                 "exon qt",
    "gene quantifications":                 "gene qt",
    "microRNA quantifications":             "miRNA qt",
    "transcript quantifications":           "trsct qt",
    "library fraction":                     "lib frac",
    "methylation state at CpG":             "mth CpG",
    "methylation state at CHG":             "mth CHG",
    "methylation state at CHH":             "mth CHH",
    "enrichment":                           "enrich",
    "replication timing profile":           "repli tm",
    "variant calls":                        "vars",
    "filtered SNPs":                        "f SNPs",
    "filtered indels":                      "f indel",
    "hotspots":                             "hotspt",
    "long range chromatin interactions":    "lrci",
    "chromatin interactions":               "ch int",
    "topologically associated domains":     "tads",
    "genome compartments":                  "compart",
    "open chromatin regions":               "open ch",
    "filtered peaks":                       "filt pk",
    "filtered regions":                     "filt reg",
    "DHS peaks":                            "DHS pk",
    "peaks":                                "peaks",
    "replicated peaks":                     "rep pk",
    "RNA-binding protein associated mRNAs": "RBP RNA",
    "splice junctions":                     "splice",
    "transcription start sites":            "tss",
    "predicted enhancers":                  "pr enh",
    "candidate enhancers":                  "can enh",
    "candidate promoters":                  "can pro",
    "predicted forebrain enhancers":        "fb enh",    # plan to fix these
    "predicted heart enhancers":            "hrt enh",       # plan to fix these
    "predicted whole brain enhancers":      "wb enh",  # plan to fix these
    "candidate regulatory elements":        "can re",
    # "genome reference":"ref",           # references not to be viewed
    # "transcriptome reference":"tr ref", # references not to be viewed
    # "transcriptome index":"tr rix",     # references not to be viewed
    # "tRNA reference":"tRNA",            # references not to be viewed
    # "miRNA reference":"miRNA",          # references not to be viewed
    # "snRNA reference":"snRNA",          # references not to be viewed
    # "rRNA reference":"rRNA",            # references not to be viewed
    # "TSS reference":"TSS",              # references not to be viewed
    # "reference variants":"var",         # references not to be viewed
    # "genome index":"ref ix",            # references not to be viewed
    # "female genome reference":"XX ref", # references not to be viewed
    # "female genome index":"XX rix",     # references not to be viewed
    # "male genome reference":"XY ref",   # references not to be viewed
    # "male genome index":"XY rix",       # references not to be viewed
    # "spike-in sequence":"spike",        # references not to be viewed
    "optimal idr thresholded peaks":        "oIDR pk",
    "conservative idr thresholded peaks":   "cIDR pk",
    "enhancer validation":                  "enh val",
    "semi-automated genome annotation":     "saga"
    }

BIOSAMPLE_COLOR = {
    "induced pluripotent stem cell line":       {"color": "80,49,120",
                                                 "altColor": "107,95,102"},  # Purple
    "stem cell":        {"color": "0,107,27",    "altColor": "0.0,77,20"},   # Dark Green
    "GM12878":          {"color": "153,38,0",    "altColor": "115,31,0"},    # Dark Orange-Red
    "H1-hESC":          {"color": "0,107,27",    "altColor": "0,77,20"},     # Dark Green
    "K562":             {"color": "46,0,184",    "altColor": "38,0,141"},    # Dark Blue
    "keratinocyte":     {"color": "179,0,134",   "altColor": "154,0,113"},   # Darker Pink-Purple
    "HepG2":            {"color": "189,0,157",   "altColor": "189,76,172"},  # Pink-Purple
    "HeLa-S3":          {"color": "0,119,158",   "altColor": "0,94,128"},    # Greenish-Blue
    "HeLa":             {"color": "0,119,158",   "altColor": "0,94,128"},    # Greenish-Blue
    "A549":             {"color": "204,163,0",   "altColor": "218,205,22"},  # Dark Yellow
    "endothelial cell of umbilical vein":       {"color": "224,75,0",
                                                 "altColor": "179,60,0"},    # Pink
    "MCF-7":            {"color": "22,219,206",  "altColor": "18,179,168"},  # Cyan
    "SK-N-SH":          {"color": "255,115,7",   "altColor": "218,98,7"},    # Orange
    "IMR-90":           {"color": "6,62,218",    "altColor": "5,52,179"},    # Blue
    "CH12.LX":          {"color": "86,180,233",  "altColor": "76,157,205"},  # Dark Orange-Red
    "MEL cell line":    {"color": "46,0,184",    "altColor": "38,0,141"},    # Dark Blue
    "brain":            {"color": "105,105,105", "altColor": "77,77,77"},    # Grey
    "eye":              {"color": "105,105,105", "altColor": "77,77,77"},    # Grey
    "spinal cord":      {"color": "105,105,105", "altColor": "77,77,77"},    # Grey
    "olfactory organ":  {"color": "105,105,105", "altColor": "77,77,77"},    # Grey
    "esophagus":        {"color": "230,159,0",   "altColor": "179,125,0"},   # Mustard
    "stomach":          {"color": "230,159,0",   "altColor": "179,125,0"},   # Mustard
    "liver":            {"color": "230,159,0",   "altColor": "179,125,0"},   # Mustard
    "pancreas":         {"color": "230,159,0",   "altColor": "179,125,0"},   # Mustard
    "large intestine":  {"color": "230,159,0",   "altColor": "179,125,0"},   # Mustard
    "small intestine":  {"color": "230,159,0",   "altColor": "179,125,0"},   # Mustard
    "gonad":            {"color": "0.0,158,115", "altColor": "0.0,125,92"},  # Darker Aquamarine
    "mammary gland":    {"color": "0.0,158,115", "altColor": "0.0,125,92"},  # Darker Aquamarine
    "prostate gland":   {"color": "0.0,158,115", "altColor": "0.0,125,92"},  # Darker Aquamarine
    "ureter":           {"color": "204,121,167", "altColor": "166,98,132"},  # Grey-Pink
    "urinary bladder":  {"color": "204,121,167", "altColor": "166,98,132"},  # Grey-Pink
    "kidney":           {"color": "204,121,167", "altColor": "166,98,132"},  # Grey-Pink
    "muscle organ":     {"color": "102,50,200 ", "altColor": "81,38,154"},   # Violet
    "tongue":           {"color": "102,50,200",  "altColor": "81,38,154"},   # Violet
    "adrenal gland":    {"color": "189,0,157",   "altColor": "154,0,128"},   # Pink-Purple
    "thyroid gland":    {"color": "189,0,157",   "altColor": "154,0,128"},   # Pink-Purple
    "lung":             {"color": "145,235,43",  "altColor": "119,192,35"},  # Mossy green
    "bronchus":         {"color": "145,235,43",  "altColor": "119,192,35"},  # Mossy green
    "trachea":          {"color": "145,235,43",  "altColor": "119,192,35"},  # Mossy green
    "nose":             {"color": "145,235,43",  "altColor": "119,192,35"},  # Mossy green
    "placenta":         {"color": "153,38,0",    "altColor": "102,27,0"},    # Orange-Brown
    "extraembryonic structure":                 {"color": "153,38,0",
                                                 "altColor": "102,27,0"},    # Orange-Brown
    "thymus":           {"color": "86,180,233",  "altColor": "71,148,192"},  # Baby Blue
    "spleen":           {"color": "86,180,233",  "altColor": "71,148,192"},  # Baby Blue
    "bone element":     {"color": "86,180,233",  "altColor": "71,148,192"},  # Baby Blue
    "blood":            {"color": "86,180,233",  "altColor": "71,148,192"},  # Baby Blue (red?)
    "blood vessel":     {"color": "214,0,0",     "altColor": "214,79,79"},   # Red
    "heart":            {"color": "214,0,0",     "altColor": "214,79,79"},   # Red
    "lymphatic vessel": {"color": "214,0,0",     "altColor": "214,79,79"},   # Red
    "skin of body":     {"color": "74,74,21",    "altColor": "102,102,44"},   # Brown
    }


def lookup_colors(dataset):
    '''Using the mask, determine which color table to use.'''
    color = None
    altColor = None
    coloring = {}
    biosample_term = dataset.get('biosample_type')
    if biosample_term is not None:
        if isinstance(biosample_term, list):
            if len(biosample_term) == 1:
                biosample_term = biosample_term[0]
            else:
                log.warn("%s has biosample_type %s that is unexpectedly a list" %
                         (dataset['accession'], str(biosample_term)))
                biosample_term = "unknown"  # really only seen in test data!
        coloring = BIOSAMPLE_COLOR.get(biosample_term, {})
    if not coloring:
        biosample_term = dataset.get('biosample_term_name')
        if biosample_term is not None:
            if isinstance(biosample_term, list):
                if len(biosample_term) == 1:
                    biosample_term = biosample_term[0]
                else:
                    log.warn("%s has biosample_term_name %s that is unexpectedly a list" %
                             (dataset['accession'], str(biosample_term)))
                    biosample_term = "unknown"  # really only seen in test data!
            coloring = BIOSAMPLE_COLOR.get(biosample_term, {})
    if not coloring:
        organ_slims = dataset.get('organ_slims', [])
        if len(organ_slims) > 1:
            coloring = BIOSAMPLE_COLOR.get(organ_slims[1])
    if coloring:
        assert("color" in coloring)
        if "altColor" not in coloring:
            color = coloring["color"]
            shades = color.split(',')
            red = int(shades[0]) / 2
            green = int(shades[1]) / 2
            blue = int(shades[2]) / 2
            altColor = "%d,%d,%d" % (red, green, blue)
            coloring["altColor"] = altColor

    return coloring


def add_living_color(live_settings, dataset):
    '''Adds color and altColor.  Note that altColor is only added if color is found.'''
    colors = lookup_colors(dataset)
    if colors and "color" in colors:
        live_settings["color"] = colors["color"]
        if "altColor" in colors:
            live_settings["altColor"] = colors["altColor"]


def sanitize_char(c, exceptions=['_'], htmlize=False, numeralize=False):
    '''Pass through for 0-9,A-Z.a-z,_, but then either html encodes, numeralizes or removes special
       characters.'''
    n = ord(c)
    if n >= 47 and n <= 57:  # 0-9
        return c
    if n >= 65 and n <= 90:  # A-Z
        return c
    if n >= 97 and n <= 122:  # a-z
        return c
    if c in exceptions:
        return c
    if n == 32:              # space
        return '_'
    if htmlize:
        return "&#%d;" % n
    if numeralize:
        return "%d" % n

    return ""


def sanitize_label(s):
    '''Encodes the string to swap special characters and leaves spaces alone.'''
    new_s = ""      # longLabel and shorLabel can have spaces and some special characters
    for c in s:
        new_s += sanitize_char(c, [' ', '_', '.', '-', '(', ')', '+'], htmlize=True)
    return new_s


def sanitize_title(s):
    '''Encodes the string to swap special characters and replace spaces with '_'.'''
    new_s = ""      # Titles appear in tag=title pairs and cannot have spaces
    for c in s:
        new_s += sanitize_char(c, ['_', '.', '-', '(', ')', '+'], htmlize=True)
    return new_s


def sanitize_tag(s):
    '''Encodes the string to swap special characters and remove spaces.'''
    new_s = ""
    first = True
    for c in s:
        new_s += sanitize_char(c, numeralize=True)
        if first:
            if new_s.isdigit():  # tags cannot start with digit.
                new_s = 'z' + new_s
            first = False
    return new_s


def sanitize_name(s):
    '''Encodes the string to remove special characters swap spaces for underscores.'''
    new_s = ""
    for c in s:
        new_s += sanitize_char(c)
    return new_s


def add_to_es(request, comp_id, composite):
    '''Adds a composite json blob to elastic-search'''
    key = "vis_composite"
    es = request.registry.get(ELASTIC_SEARCH, None)
    if not es:
        return
    if not es.indices.exists(key):
        es.indices.create(index=key, body={'index': {'number_of_shards': 1}})
        mapping = {'default': {"_all":    {"enabled": False},
                               "_source": {"enabled": True},
                               # "_id":     {"index": "not_analyzed", "store": True},
                               # "_ttl":    {"enabled": True, "default": "1d"},
                               }}
        es.indices.put_mapping(index=key, doc_type='default', body=mapping)
        log.debug("created %s index" % key)
    es.index(index=key, doc_type='default', body=composite, id=comp_id)


def get_from_es(request, comp_id):
    '''Returns composite json blob from elastic-search, or None if not found.'''
    key = "vis_composite"
    es = request.registry.get(ELASTIC_SEARCH, None)
    if es and es.indices.exists(key):
        try:
            result = es.get(index=key, doc_type='default', id=comp_id)
            return result['_source']
        except:
            pass
    return None


def search_es(request, ids):
    '''Returns a list of composites from elastic-search, or None if not found.'''
    key = "vis_composite"
    es = request.registry.get(ELASTIC_SEARCH, None)
    if es and es.indices.exists(key):
        try:
            query = {"query": {"ids": {"values": ids}}}
            res = es.search(body=query, index=key, doc_type='default', size=99999)  # size=200?
            hits = res.get("hits", {}).get("hits", [])
            results = {}
            for hit in hits:
                results[hit["_id"]] = hit["_source"]  # make this a generator? No... len(results)
            log.debug("ids found: %d   %.3f secs" %
                      (len(results), (time.time() - PROFILE_START_TIME)))
            return results
        except:
            pass
    return {}


def rep_for_file(a_file):
    '''Determines best rep_tech or rep for a file.'''

    # Starting with a little cheat for rare cases where techreps are compared instead of bioreps
    if a_file.get("file_format_type", "none") in ["idr_peak"]:
        return "combined"
    if a_file['output_type'].endswith("idr thresholded peaks"):
        return "combined"

    bio_rep = 0
    tech_rep = 0
    if "replicate" in a_file:
        bio_rep = a_file["replicate"]["biological_replicate_number"]
        tech_rep = a_file["replicate"]["technical_replicate_number"]

    elif "tech_replicates" in a_file:
        # Do we want to make rep1_1.2.3 ?  Not doing it now
        tech_reps = a_file["tech_replicates"]
        if len(tech_reps) == 1:
            bio_rep = int(tech_reps[0].split('_')[0])
            tech_reps = tech_reps[0][2:]
            if len(tech_reps) == 1:
                tech_rep = int(tech_reps)
        elif len(tech_reps) > 1:
            bio = 0
            for tech in tech_reps:
                if bio == 0:
                    bio = int(tech.split('_')[0])
                elif bio != int(tech.split('_')[0]):
                    bio = 0
                    break
            if bio > 0:
                bio_rep = bio

    elif "biological_replicates" in a_file:
        bio_reps = a_file["biological_replicates"]
        if len(bio_reps) == 1:
            bio_rep = bio_reps[0]

    if bio_rep == 0:
        return "combined"

    rep = "rep%d" % bio_rep
    if tech_rep > 0:
        rep += "_%d" % tech_rep
    return rep


def handle_negateValues(live_settings, defs, dataset, composite):
    '''If negateValues is set then adjust some settings like color'''
    if live_settings.get("negateValues", "off") == "off":
        return

    # need to swap color and altColor
    color = live_settings.get("color", composite.get("color"))
    if color is not None:
        altColor = live_settings.get("altColor", composite.get("altColor", color))
        live_settings["color"] = altColor
        live_settings["altColor"] = color

    # view limits need to change because numbers are all negative
    viewLimits = live_settings.get("viewLimits")
    if viewLimits is not None:
        low_high = viewLimits.split(':')
        if len(low_high) == 2:
            live_settings["viewLimits"] = "%d:%d" % (int(low_high[1]) * -1, int(low_high[0]) * -1)
    viewLimitsMax = live_settings.get("viewLimitsMax")
    if viewLimitsMax is not None:
        low_high = viewLimitsMax.split(':')
        if len(low_high) == 2:
            live_settings["viewLimitsMax"] = ("%d:%d" %
                                              (int(low_high[1]) * -1, int(low_high[0]) * -1))


def generate_live_groups(composite, title, group_defs, dataset, rep_tags=[]):
    '''Recursively populates live (in memory) groups from static group definitions'''
    live_group = {}
    tag = group_defs.get("tag", title)
    live_group["title"] = title
    live_group["tag"] = tag
    for key in group_defs.keys():
        if key not in ["groups", "group_order"]:  # leave no trace of subgroups keyed by title
            live_group[key] = deepcopy(group_defs[key])

    if title == "replicate":  # transform replicates into unique tags and titles
        if len(rep_tags) == 0:  # reps need special work after files are examined, so just stub.
            return (tag, live_group)
        # Inclusion of rep_tags occurs after files have been examined.
        live_group["groups"] = {}
        rep_title_mask = group_defs.get("title_mask", "Replicate_{replicate_number}")
        for rep_tag in rep_tags:
            rep_title = rep_title_mask
            if "combined_title" in group_defs and rep_tag in ["pool", "combined"]:
                rep_title = group_defs["combined_title"]
            elif rep_title_mask.find('{replicate}') != -1:
                rep_title = rep_title_mask.replace('{replicate}', rep_tag)
            elif rep_title_mask.find('{replicate_number}') != -1:
                if rep_tag in ["pool", "combined"]:
                    rep_title = rep_title_mask.replace('{replicate_number}', "0")
                else:
                    rep_no = int(rep_tag[3:])  # tag might be rep01 but we want replicate 1
                    rep_title = rep_title_mask.replace('{replicate_number}', str(rep_no))
            live_group["groups"][rep_tag] = {"title": rep_title, "tag": rep_tag}
        live_group["preferred_order"] = "sorted"

    elif title in ["Biosample", "Targets", "Assay", EXP_GROUP]:
        groups = group_defs.get("groups", {})
        assert(len(groups) == 1)
        for (group_key, group) in groups.items():
            mask = group.get("title_mask")
            if mask is not None:
                term = convert_mask(mask, dataset)
                if not term.startswith('Unknown '):
                    term_tag = sanitize_tag(term)
                    term_title = term
                    live_group["groups"] = {}
                    live_group["groups"][term_tag] = {"title": term_title, "tag": term_tag}
                    mask = group.get("url_mask")
                    if mask is not None:
                        term = convert_mask(mask, dataset)
                        live_group["groups"][term_tag]["url"] = term
        live_group["preferred_order"] = "sorted"
        # No tag order since only one

    # simple swapping tag and title and creating subgroups set with order
    else:  # "Views", "Replicates", etc:
        # if there are subgroups, they can be handled by recursion
        if "groups" in group_defs:
            live_group["groups"] = {}
            groups = group_defs["groups"]
            group_order = group_defs.get("group_order")
            preferred_order = []  # have to create preferred order based upon tags, not titles
            if group_order is None or not isinstance(group_order, list):
                group_order = sorted(groups.keys())
                preferred_order = "sorted"
            tag_order = []
            for subgroup_title in group_order:
                subgroup = groups.get(subgroup_title, {})
                (subgroup_tag, subgroup) = generate_live_groups(composite, subgroup_title, subgroup,
                                                                dataset)  # recursive
                subgroup["tag"] = subgroup_tag
                if isinstance(preferred_order, list):
                    preferred_order.append(subgroup_tag)
                if title == "Views":
                    assert(subgroup_title != subgroup_tag)
                    handle_negateValues(subgroup, subgroup, dataset, composite)
                live_group["groups"][subgroup_tag] = subgroup
                tag_order.append(subgroup_tag)
            # assert(len(live_group["groups"]) == len(groups))
            if len(live_group['groups']) != len(groups):
                log.warn("len(live_group['groups']):%d != len(groups):%d" %
                         (len(live_group['groups']), len(groups)))
                log.debug(json.dumps(live_group, indent=4))
            live_group["group_order"] = tag_order
            live_group["preferred_order"] = preferred_order

    return (tag, live_group)


def insert_live_group(live_groups, new_tag, new_group):
    '''Inserts new group into a set of live groups during composite remodelling.'''
    old_groups = live_groups.get("groups", {})
    preferred_order = live_groups.get("preferred_order")
    # Note: all cases where group is dynamically added should be in sort order!
    if preferred_order is None or not isinstance(preferred_order, list):
        old_groups[new_tag] = new_group
        live_groups["groups"] = old_groups
        # log.debug("Added %s to %s in sort order" % (new_tag,live_groups.get("tag","a group")))
        return live_groups

    # well we are going to have to generate s new order
    new_order = []
    old_order = live_groups.get("group_order", [])
    if old_order is None:
        old_order = sorted(old_groups.keys())
    for preferred_tag in preferred_order:
        if preferred_tag == new_tag:
            new_order.append(new_tag)
        elif preferred_tag in old_order:
            new_order.append(preferred_tag)

    old_groups[new_tag] = new_group
    live_groups["groups"] = old_groups
    # log.debug("Added %s to %s in preferred order" % (new_tag,live_groups.get("tag","a group")))
    return live_groups


def biosamples_for_file(a_file, dataset):
    '''Returns a dict of biosamples for file.'''
    biosamples = {}
    replicates = dataset.get("replicates")
    if replicates is None:
        return[]

    for bio_rep in a_file.get("biological_replicates", []):
        for replicate in replicates:
            if replicate.get("biological_replicate_number", -1) != bio_rep:
                continue
            biosample = replicate.get("library", {}).get("biosample", {})
            if not biosample:
                continue
            biosamples[biosample["accession"]] = biosample
            break  # If multiple techical replicates then the one should do

    return biosamples


def replicates_pair(a_file):
    if "replicate" in a_file:
        bio_rep = a_file["replicate"]["biological_replicate_number"]
        tech_rep = a_file["replicate"]["technical_replicate_number"]
        # metadata_pairs['replicate&#32;biological'] = str(bio_rep)
        # metadata_pairs['replicate&#32;technical'] = str(tech_rep)
        return ('replicate&#32;(bio_tech)', "%d_%d" % (bio_rep, tech_rep))

    bio_reps = a_file.get('biological_replicates')
    tech_reps = a_file.get('technical_replicates')
    if not bio_reps or len(bio_reps) == 0:
        return ("", "")
    rep_key = ""
    rep_val = ""
    for bio_rep in bio_reps:
        found = False
        br = "%s" % (bio_rep)
        if tech_reps:
            for tech_rep in tech_reps:
                if tech_rep.startswith(br + '_'):
                    found = True
                    rep_key = '&#32;(bio_tech)'
                    if len(rep_val) > 0:
                        rep_val += ', '
                    rep_val += tech_rep
                    break
        if not found:
            if len(rep_val) > 0:
                rep_val += ', '
            rep_val += br
    if ',' in rep_val:
        rep_key = 'replicates' + rep_key
    else:
        rep_key = 'replicate' + rep_key
    # TODO handle tech_reps only?
    return (rep_key, rep_val)


def acc_composite_extend_with_tracks(composite, vis_defs, dataset, assembly, host=None):
    '''Extends live experiment composite object with track definitions'''
    tracks = []
    rep_techs = {}
    files = []
    ucsc_assembly = composite['ucsc_assembly']

    # first time through just to get rep_tech
    group_order = composite["view"].get("group_order", [])
    for view_tag in group_order:
        view = composite["view"]["groups"][view_tag]
        output_types = view.get("output_type", [])
        file_format_types = view.get("file_format_type", [])
        file_format = view["type"].split()[0]
        if file_format == "bigBed" and "scoreFilter" in view:
            view["type"] = "bigBed 6 +"  # scoreFilter implies score so 6 +
        # log.debug("%d files looking for type %s" % (len(dataset["files"]),view["type"]))
        for a_file in dataset["files"]:
            if a_file['status'] not in VISIBLE_FILE_STATUSES:
                continue
            if file_format != a_file['file_format']:
                continue
            if len(output_types) > 0 and a_file.get('output_type', 'unknown') not in output_types:
                continue
            if len(file_format_types) > 0 and \
               a_file.get('file_format_type', 'unknown') not in file_format_types:
                continue
            if 'assembly' not in a_file or \
               _ASSEMBLY_MAPPER.get(a_file['assembly'], a_file['assembly']) != ucsc_assembly:
                continue
            if "rep_tech" not in a_file:
                rep_tech = rep_for_file(a_file)
                a_file["rep_tech"] = rep_tech
            else:
                rep_tech = a_file["rep_tech"]
            rep_techs[rep_tech] = rep_tech
            files.append(a_file)
    if len(files) == 0:
        log.debug("No visualizable files for %s %s" % (dataset["accession"], composite["vis_type"]))
        return None

    # convert rep_techs to simple reps
    rep_ix = 1
    rep_tags = []
    for rep_tech in sorted(rep_techs.keys()):  # ordered by a simple sort
        if rep_tech == "combined":
            rep_tag = "pool"
        else:
            rep_tag = "rep%02d" % rep_ix
            rep_ix += 1
        rep_techs[rep_tech] = rep_tag
        rep_tags.append(rep_tag)

    # Now we can fill in "Replicate" subgroups with with "replicate"
    other_groups = vis_defs.get("other_groups", []).get("groups", [])
    if "Replicates" in other_groups:
        group = other_groups["Replicates"]
        group_tag = group["tag"]
        subgroups = group["groups"]
        if "replicate" in subgroups:
            (repgroup_tag, repgroup) = generate_live_groups(composite, "replicate",
                                                            subgroups["replicate"], dataset,
                                                            rep_tags)
            # Now to hook them into the composite structure
            composite_rep_group = composite["groups"]["REP"]
            composite_rep_group["groups"] = repgroup.get("groups", {})
            composite_rep_group["group_order"] = repgroup.get("group_order", [])

    # second pass once all rep_techs are known
    if host is None:
        host = "https://www.encodeproject.org"
    for view_tag in composite["view"].get("group_order", []):
        view = composite["view"]["groups"][view_tag]
        output_types = view.get("output_type", [])
        file_format_types = view.get("file_format_type", [])
        file_format = view["type"].split()[0]
        for a_file in files:
            if a_file['file_format'] not in [file_format, "bed"]:
                continue
            if len(output_types) > 0 and a_file.get('output_type', 'unknown') not in output_types:
                continue
            if len(file_format_types) > 0 and a_file.get('file_format_type',
                                                         'unknown') not in file_format_types:
                continue
            rep_tech = a_file["rep_tech"]
            rep_tag = rep_techs[rep_tech]
            a_file["rep_tag"] = rep_tag

            if "tracks" not in view:
                view["tracks"] = []
            track = {}
            track["name"] = a_file['accession']
            track["type"] = view["type"]
            track["bigDataUrl"] = "%s?proxy=true" % a_file["href"]
            longLabel = vis_defs.get('file_defs', {}).get('longLabel')
            if longLabel is None:
                longLabel = ("{assay_title} of {biosample_term_name} {output_type} "
                             "{biological_replicate_number}")
            longLabel += " {experiment.accession} - {file.accession}"  # Always add the accessions
            track["longLabel"] = sanitize_label(convert_mask(longLabel, dataset, a_file))
            # Specialized addendum comments because subtle details alway get in the way of elegance.
            addendum = ""
            submitted_name = a_file.get('submitted_file_name', "none")
            if "_tophat" in submitted_name:
                addendum = addendum + 'TopHat,'
            if a_file.get('assembly', assembly) == 'mm10-minimal':
                addendum = addendum + 'mm10-minimal,'
            if len(addendum) > 0:
                track["longLabel"] = track["longLabel"] + " (" + addendum[0:-1] + ")"

            metadata_pairs = {}
            metadata_pairs['file&#32;download'] = ( \
                '"<a href=\'%s%s\' title=\'Download this file from the ENCODE portal\'>%s</a>"' %
                (host, a_file["href"], a_file["accession"]))
            lab = convert_mask("{lab.title}", dataset)
            if len(lab) > 0 and not lab.startswith('unknown'):
                metadata_pairs['laboratory'] = '"' + sanitize_label(lab) + '"'  # 'lab' is UCSC word
            (rep_key, rep_val) = replicates_pair(a_file)
            if rep_key != "":
                metadata_pairs[rep_key] = '"' + rep_val + '"'

            # Expecting short label to change when making assay based composites
            shortLabel = vis_defs.get('file_defs', {}).get('shortLabel',
                                                           "{replicate} {output_type_short_label}")
            track["shortLabel"] = sanitize_label(convert_mask(shortLabel, dataset, a_file))

            # How about subgroups!
            membership = {}
            membership["view"] = view["tag"]
            view["tracks"].append(track)  # <==== This is how we connect them to the views
            for (group_tag, group) in composite["groups"].items():
                # "Replicates", "Biosample", "Targets", "Assay", ... member?
                group_title = group["title"]
                subgroups = group["groups"]
                if group_title == "Replicates":
                    # Must figure out membership
                    # Generate rep_tag for track, then
                    subgroup = subgroups.get(rep_tag)
                    # if subgroup is None:
                    #    subgroup = { "tag": rep_tag, "title": rep_tag }
                    #    group["groups"][rep_tag] = subgroup
                    if subgroup is not None:
                        membership[group_tag] = rep_tag
                        if "tracks" not in subgroup:
                            subgroup["tracks"] = []
                        subgroup["tracks"].append(track)  # <==== also connected to replicate
                elif group_title in ["Biosample", "Targets", "Assay", EXP_GROUP]:
                    assert(len(subgroups) == 1)
                    # if len(subgroups) == 1:
                    for (subgroup_tag, subgroup) in subgroups.items():
                        membership[group_tag] = subgroup["tag"]
                        if "url" in subgroup:
                            metadata_pairs[group_title] = ( \
                                '"<a href=\'%s/%s/\' TARGET=\'_blank\' title=\'%s details at the ENCODE portal\'>%s</a>"' %
                                (host, subgroup["url"], group_title, subgroup["title"]))
                        elif group_title == "Biosample":
                            bs_value = sanitize_label(dataset.get("biosample_summary", ""))
                            if len(bs_value) == 0:
                                bs_value = subgroup["title"]
                            biosamples = biosamples_for_file(a_file, dataset)
                            if len(biosamples) > 0:
                                for bs_acc in sorted(biosamples.keys()):
                                    bs_value += ( \
                                        " <a href=\'%s%s\' TARGET=\'_blank\' title=\' %s details at the ENCODE portal\'>%s</a>" %
                                        (host, biosamples[bs_acc]["@id"], group_title,
                                                  bs_acc))
                            metadata_pairs[group_title] = '"%s"' % (bs_value)
                        else:
                            metadata_pairs[group_title] = '"%s"' % (subgroup["title"])
                else:
                    assert(group_tag == "Don't know this group!")

            # plumbing for ihec:
            if 'pipeline' not in composite:
                as_ver = a_file.get("analysis_step_version")  # this embedding could evaporate
                if as_ver and isinstance(as_ver, dict):
                    a_step = as_ver.get("analysis_step")
                    if a_step and isinstance(a_step, dict):
                        pipelines = a_step.get("pipelines")
                        if pipelines and isinstance(pipelines, list) and len(pipelines) > 0:
                            pipeline = pipelines[0].get("title")
                            pipeline_group = pipelines[0].get("lab")
                            if pipeline:
                                composite['pipeline'] = pipeline
                                if pipeline_group:
                                    composite['pipeline_group'] = pipeline_group
            track['md5sum'] = a_file['md5sum']

            track["membership"] = membership
            if len(metadata_pairs):
                track["metadata_pairs"] = metadata_pairs

            tracks.append(track)

    return tracks


def make_acc_composite(dataset, assembly, host=None, hide=False):
    '''Converts experiment composite static definitions to live composite object'''
    if dataset["status"] not in VISIBLE_DATASET_STATUSES:
        log.debug("%s can't be visualized because it's not unreleased status:%s." %
                  (dataset["accession"], dataset["status"]))
        return {}
    vis_type = get_vis_type(dataset)
    vis_defs = lookup_vis_defs(vis_type)
    if vis_defs is None:
        log.warn("%s (vis_type: %s) has undiscoverable vis_defs." %
                 (dataset["accession"], vis_type))
        return {}
    composite = {}
    # log.debug("%s has vis_type: %s." % (dataset["accession"],vis_type))
    composite["vis_type"] = vis_type
    composite["name"] = dataset["accession"]

    ucsc_assembly = _ASSEMBLY_MAPPER.get(assembly, assembly)
    if assembly != ucsc_assembly:  # Sometimes 'assembly' is hg38 already.
        composite['assembly'] = assembly
    composite['ucsc_assembly'] = ucsc_assembly

    # plumbing for ihec, among other things:
    for term in ['biosample_term_name', 'biosample_term_id', 'biosample_summary',
                 'biosample_type', 'assay_term_id', 'assay_term_name']:
        if term in dataset:
            composite[term] = dataset[term]
    replicates = dataset.get("replicates", [])
    molecule = "DNA"  # default
    if len(replicates) > 0:
        taxon_id = replicates[0].get("library", {}).get("biosample", {}).get("organism",
                                                                             {}).get("taxon_id")
        if taxon_id:
            composite['taxon_id'] = taxon_id
        molecule = replicates[0].get("library", {}).get("nucleic_acid_term_name")
        if molecule:
            if molecule == "RNA":
                descr = dataset.get('description', '').lower()
                if 'total' in descr:
                    molecule = "total RNA"
                elif 'poly' in descr:
                    molecule = "polyA RNA"
    composite['molecule'] = molecule

    longLabel = vis_defs.get('longLabel',
                             '{assay_term_name} of {biosample_term_name} - {accession}')
    composite['longLabel'] = sanitize_label(convert_mask(longLabel, dataset))
    shortLabel = vis_defs.get('shortLabel', '{accession}')
    composite['shortLabel'] = sanitize_label(convert_mask(shortLabel, dataset))
    if hide:
        composite["visibility"] = "hide"
    else:
        composite["visibility"] = vis_defs.get("visibility", "full")
    composite['pennantIcon'] = find_pennent(dataset)
    add_living_color(composite, dataset)
    # views are always subGroup1
    composite["view"] = {}
    title_to_tag = {}
    if "Views" in vis_defs:
        (tag, views) = generate_live_groups(composite, "Views", vis_defs["Views"], dataset)
        composite[tag] = views
        title_to_tag["Views"] = tag

    if "other_groups" in vis_defs:
        groups = vis_defs["other_groups"].get("groups", {})
        new_dimensions = {}
        new_filters = {}
        composite["group_order"] = []
        composite["groups"] = {}  # subgroups def by groups and group_order directly off composite
        group_order = vis_defs["other_groups"].get("group_order")
        preferred_order = []  # have to create preferred order based upon tags, not titles
        if group_order is None or not isinstance(group_order, list):
            group_order = sorted(groups.keys())
            preferred_order = "sorted"
        for subgroup_title in group_order:  # Replicates, Targets, Biosamples
            if subgroup_title not in groups:
                continue
            assert(subgroup_title in SUPPORTED_SUBGROUPS)
            (subgroup_tag, subgroup) = generate_live_groups(composite, subgroup_title,
                                                            groups[subgroup_title], dataset)
            if isinstance(preferred_order, list):
                preferred_order.append(subgroup_tag)
            if "groups" in subgroup and len(subgroup["groups"]) > 0:
                title_to_tag[subgroup_title] = subgroup_tag
                composite["groups"][subgroup_tag] = subgroup
                composite["group_order"].append(subgroup_tag)
            if "dimensions" in vis_defs["other_groups"]:  # (empty) "Targets" dim will be included
                dimension = vis_defs["other_groups"]["dimensions"].get(subgroup_title)
                if dimension is not None:
                    new_dimensions[dimension] = subgroup_tag
                    if "filterComposite" in vis_defs["other_groups"]:
                        filterfish = vis_defs["other_groups"]["filterComposite"].get(subgroup_title)
                        if filterfish is not None:
                            new_filters[dimension] = filterfish
        composite["preferred_order"] = preferred_order
        if len(new_dimensions) > 0:
            composite["dimensions"] = new_dimensions
        if len(new_filters) > 0:
            composite["filterComposite"] = new_filters
        if "dimensionAchecked" in vis_defs["other_groups"]:
            composite["dimensionAchecked"] = vis_defs["other_groups"]["dimensionAchecked"]

    if "sortOrder" in vis_defs:
        sort_order = []
        for title in vis_defs["sortOrder"]:
            if title in title_to_tag:
                sort_order.append(title_to_tag[title])
        composite["sortOrder"] = sort_order

    tracks = acc_composite_extend_with_tracks(composite, vis_defs, dataset, assembly, host=host)
    if tracks is None or len(tracks) == 0:
        # Already warned about files log.debug("No tracks for %s" % dataset["accession"])
        return {}
    composite["tracks"] = tracks
    return composite


def remodel_acc_to_set_composites(acc_composites, hide_after=None):
    '''Given a set of (search result) acc based composites, remodel them to set based composites.'''
    if acc_composites is None or len(acc_composites) == 0:
        return {}

    set_composites = {}

    for acc in sorted(acc_composites.keys()):
        acc_composite = acc_composites[acc]
        if acc_composite is None or len(acc_composite) == 0:
            # log.debug("Found empty acc_composite for %s" % (acc))
            set_composites[acc] = {}  # wounded composite are added for evidence
            continue

        # Only show the first n datasets
        if hide_after is not None:
            if hide_after <= 0:
                for track in acc_composite.get("tracks", {}):
                    track["checked"] = "off"
            else:
                hide_after -= 1

        # color must move to tracks because it' i's from biosample and we can mix biosample exps
        acc_color = acc_composite.get("color")
        acc_altColor = acc_composite.get("altColor")
        acc_view_groups = acc_composite.get("view", {}).get("groups", {})
        for (view_tag, acc_view) in acc_view_groups.items():
            acc_view_color = acc_view.get("color", acc_color)  # color may be at view level
            acc_view_altColor = acc_view.get("altColor", acc_altColor)
            if acc_view_color is None and acc_view_altColor is None:
                continue
            for track in acc_view.get("tracks", []):
                if "color" not in track.keys():
                    if acc_view_color is not None:
                        track["color"] = acc_view_color
                    if acc_view_altColor is not None:
                        track["altColor"] = acc_view_altColor

        # If set_composite of this vis_type doesn't exist, create it
        vis_type = acc_composite["vis_type"]
        vis_defs = lookup_vis_defs(vis_type)
        assert(vis_type is not None)
        if vis_type not in set_composites.keys():  # First one so just drop in place
            set_composite = acc_composite  # Don't bother with deep copy.
            set_defs = vis_defs.get("assay_composite", {})
            set_composite["name"] = vis_type.lower()  # is there something more elegant?
            for tag in ["longLabel", "shortLabel", "visibility"]:
                if tag in set_defs:
                    set_composite[tag] = set_defs[tag]  # Not expecting any token substitutions!!!
            set_composite['html'] = vis_type
            set_composites[vis_type] = set_composite

        else:  # Adding an acc_composite to an existing set_composite
            set_composite = set_composites[vis_type]
            set_composite['composite_type'] = 'set'

            if set_composite.get("project", "unknown") != "NHGRI":
                acc_pennant = acc_composite["pennantIcon"]
                set_pennant = set_composite["pennantIcon"]
                if acc_pennant != set_pennant:
                    set_composite["project"] = "NHGRI"
                    set_composite["pennantIcon"] = PENNANTS["NHGRI"]

            # combine views
            set_views = set_composite.get("view", [])
            acc_views = acc_composite.get("view", {})
            for view_tag in acc_views["group_order"]:
                acc_view = acc_views["groups"][view_tag]
                if view_tag not in set_views["groups"].keys():  # Should never happen
                    # log.debug("Surprise: view %s not found before" % view_tag)
                    insert_live_group(set_views, view_tag, acc_view)
                else:  # View is already defined but tracks need to be appended.
                    set_view = set_views["groups"][view_tag]
                    if "tracks" not in set_view:
                        set_view["tracks"] = acc_view.get("tracks", [])
                    else:
                        set_view["tracks"].extend(acc_view.get("tracks", []))

            # All tracks in one set: not needed.

            # Combine subgroups:
            for group_tag in acc_composite["group_order"]:
                acc_group = acc_composite["groups"][group_tag]
                if group_tag not in set_composite["groups"].keys():  # Should never happen
                    # log.debug("Surprise: group %s not found before" % group_tag)
                    insert_live_group(set_composite, group_tag, acc_group)
                else:  # Need to handle subgroups which definitely may not be there.
                    set_group = set_composite["groups"].get(group_tag, {})
                    acc_subgroups = acc_group.get("groups", {})
                    # acc_subgroup_order = acc_group.get("group_order")
                    for subgroup_tag in acc_subgroups.keys():
                        if subgroup_tag not in set_group.get("groups", {}).keys():
                            # Adding biosamples, targets, and reps
                            insert_live_group(set_group, subgroup_tag, acc_subgroups[subgroup_tag])

            # dimensions and filterComposite should not need any extra care:
            # they get dynamically scaled down during printing
            # log.debug("       Added.")

    return set_composites


def ucsc_trackDb_composite_blob(composite, title):
    '''Given an in-memory composite object, prints a single UCSC trackDb.txt composite structure'''
    if composite is None or len(composite) == 0:
        return "# Empty composite for %s.  It cannot be visualized at this time.\n" % title
    # TODO provide more detail about different possible reasons (should already be in errorlog)

    blob = ""
    # First the composite structure
    blob += "track %s\n" % composite["name"]
    blob += "compositeTrack on\n"
    blob += "type bed 3\n"
    for var in COMPOSITE_SETTINGS:
        val = composite.get(var)
        if val:
            blob += "%s %s\n" % (var, val)
    views = composite.get("view", [])
    if len(views) > 0:
        blob += "subGroup1 view %s" % views["title"]
        for view_tag in views["group_order"]:
            view_title = views["groups"][view_tag]["title"]
            blob += " %s=%s" % (view_tag, sanitize_title(view_title))
        blob += '\n'
    dimA_checked = composite.get("dimensionAchecked", "all")
    dimA_tag = ""
    if dimA_checked == "first":  # All will leave dimA_tag & dimA_checked empty, default to all on
        dimA_tag = composite.get("dimensions", {}).get("dimA", "")
    dimA_checked = None
    subgroup_ix = 2
    for group_tag in composite["group_order"]:
        group = composite["groups"][group_tag]
        blob += "subGroup%d %s %s" % (subgroup_ix, group_tag, sanitize_title(group["title"]))
        subgroup_ix += 1
        subgroup_order = None  # group.get("group_order")
        if subgroup_order is None or not isinstance(subgroup_order, list):
            subgroup_order = sorted(group["groups"].keys())
        for subgroup_tag in subgroup_order:
            subgroup_title = group["groups"][subgroup_tag]["title"]
            blob += " %s=%s" % (subgroup_tag, sanitize_title(subgroup_title))
            if group_tag == dimA_tag and dimA_checked is None:
                dimA_checked = subgroup_tag

        blob += '\n'
    # sortOrder
    sort_order = composite.get("sortOrder")
    if sort_order:
        blob += "sortOrder"
        for sort_tag in sort_order:
            if title.startswith("ENCSR") and sort_tag == "EXP":
                continue  # Single exp composites do not need to sort on EMP
            blob += " %s=+" % sort_tag
        blob += '\n'
    # dimensions
    actual_group_tags = ["view"]  # Not all groups will be used in composite, depending upon content
    dimensions = composite.get("dimensions", {})
    if dimensions:
        pairs = ""
        XY_skipped = []
        XY_added = []
        for dim_tag in sorted(dimensions.keys()):
            group = composite["groups"].get(dimensions[dim_tag])
            if group is None:  # e.g. "Targets" may not exist
                continue
            if dimensions[dim_tag] != "REP":
                if len(group.get("groups", {})) <= 1:
                    if dim_tag[-1] in ['X', 'Y']:
                        XY_skipped.append(dim_tag)
                    continue
                elif dim_tag[-1] in ['X', 'Y']:
                    XY_added.append(dim_tag)
            pairs += " %s=%s" % (dim_tag, dimensions[dim_tag])
            actual_group_tags.append(dimensions[dim_tag])
        # Getting too fancy for our own good:
        # If one XY dimension has more than one member then we must add both X and Y
        if len(XY_skipped) > 0 and len(XY_added) > 0:
            for dim_tag in XY_skipped:
                pairs += " %s=%s" % (dim_tag, dimensions[dim_tag])
                actual_group_tags.append(dimensions[dim_tag])
        if len(pairs) > 0:
            blob += "dimensions%s\n" % pairs
    # filterComposite
    filter_composite = composite.get("filterComposite")
    if filter_composite:
        filterfish = ""
        for filter_tag in sorted(filter_composite.keys()):
            group = composite["groups"].get(filter_composite[filter_tag])
            if group is None or len(group.get("groups", {})) <= 1:  # e.g. "Targets" may not exist
                continue
            filterfish += " %s" % filter_tag
            if filter_composite[filter_tag] == "one":
                filterfish += "=one"
        if len(filterfish) > 0:
            blob += 'filterComposite%s\n' % filterfish
    elif dimA_checked is not None:
        blob += 'dimensionAchecked %s\n' % dimA_checked
    blob += '\n'

    # Now cycle through views
    for view_tag in views["group_order"]:
        view = views["groups"][view_tag]
        tracks = view.get("tracks", [])
        if len(tracks) == 0:
            continue
        blob += "    track %s_%s_view\n" % (composite["name"], view["tag"])
        blob += "    parent %s on\n" % composite["name"]
        blob += "    view %s\n" % view["tag"]
        for var in VIEW_SETTINGS:
            val = view.get(var)
            if val:
                blob += "    %s %s\n" % (var, val)
        blob += '\n'

        # Now cycle through tracks in view
        for track in tracks:
            blob += "        track %s\n" % (track["name"])
            blob += "        parent %s_%s_view" % (composite["name"], view["tag"])
            dimA_subgroup = track.get("membership", {}).get(dimA_tag)
            if dimA_subgroup is not None and dimA_subgroup != dimA_checked:
                blob += " off\n"
            else:
                # Can set individual tracks off. Used when remodelling
                blob += " %s\n" % track.get("checked", "on")
            if "type" not in track:
                blob += "        type %s\n" % (view["type"])
            for var in TRACK_SETTINGS:
                val = track.get(var)
                if val:
                    blob += "        %s %s\n" % (var, val)
            # Now membership
            membership = track.get("membership")
            if membership:
                blob += "        subGroups"
                for member_tag in sorted(membership):
                    blob += " %s=%s" % (member_tag, membership[member_tag])
                blob += '\n'
            # metadata line?
            metadata_pairs = track.get("metadata_pairs")
            if metadata_pairs is not None:
                metadata_line = ""
                for meta_tag in sorted(metadata_pairs.keys()):
                    metadata_line += ' %s=%s' % (meta_tag.lower(), metadata_pairs[meta_tag])
                if len(metadata_line) > 0:
                    blob += "        metadata%s\n" % metadata_line

            blob += '\n'
    blob += '\n'
    return blob


def remodel_acc_to_ihec_json(acc_composites, request=None):
    '''TODO: remodels 1+ acc_composites into an IHEC hub json structure.'''
    if acc_composites is None or len(acc_composites) == 0:
        return {}

    if request:
        host = request.host_url
    else:
        host = "https://www.encodeproject.org"
    # {
    # "hub_description": { ... },  similar to hub.txt/genome.txt
    # "datasets": { ... },         one per experiment, contains "browser" objects, one per track
    # "samples": { ... }           one per biosample
    # }
    ihec_json = {}

    # "hub_description": {     similar to hub.txt/genome.txt
    #     "taxon_id": ...,           Species taxonomy id. (e.g. human = 9606, Mus mus. 10090)
    #     "assembly": "...",         UCSC: hg19, hg38
    #     "publishing_group": "...", ENCODE
    #     "email": "...",            encode-help@lists.stanford.edu
    #     "date": "...",             ISO 8601 format: YYYY-MM-DD
    #     "description": "...",      (optional)
    #     "description_url": "...",  (optional) If single composite: html  (e.g. ANNO.html)
    # }
    hub_description = {}
    hub_description["publishing_group"] = "ENCODE"
    hub_description["email"] = "encode-help@lists.stanford.edu"
    hub_description["date"] = time.strftime('%Y-%m-%d', time.gmtime())
    # hub_description["description"] = "...",      (optional)
    # hub_description["description_url"] = "...",  (optional)
    #                                    If single composite: html (e.g. ANNO.html)
    ihec_json["hub_description"] = hub_description

    # "samples": {             one per biosample
    #     "sample_id_1": {                   biosample term
    #         "sample_ontology_uri": "...",  UBERON or CL
    #         "molecule": "...",             ["total RNA", "polyA RNA", "cytoplasmic RNA",
    #                                         "nuclear RNA", "genomic DNA", "protein", "other"]
    #         "disease": "...",              optional?
    #         "disease_ontology_uri": "...", optional?
    #         "biomaterial_type": "...",     ["Cell Line", "Primary Cell", "Primary Cell Culture",
    #                                         "Primary Tissue"]
    #     },
    #     "sample_id_2": { ... }
    # }
    samples = {}
    ihec_json["samples"] = samples

    # "datasets": {
    #    "experiment_1": {    one per experiment    accession
    #        "sample_id": "...",                    biosample_term
    #        "experiment_attributes": {
    #            "experiment_type": "...",
    #            "assay_type": "...",               assay_term_name  Match ontology URI
    #                                                           (e.g. 'DNA Methylation')
    #            "experiment_ontology_uri": "...",  assay_term_id (e.g. OBI:0000716)
    #            "reference_registry_id": "..."     IHEC Reference Epigenome registry ID,
    #                                                 assigned after submitting to EpiRR
    #        },
    #        "analysis_attributes": {
    #            "analysis_group": "...",              metadata_pairs['laboratory']
    #            "alignment_software": "...",          pipeline?
    #            "alignment_software_version": "...",
    #            "analysis_software": "...",
    #            "analysis_software_version": "..."
    #        },
    #        "browser": {
    #            "signal_forward": [               view
    #                {
    #                    "big_data_url": "...",    obvious
    #                    "description_url": "...", Perhaps not
    #                    "md5sum": "...",          Add this to metadata pairs?
    #                    "subtype": "...",         More details?
    #                    "sample_source": "...",   pooled,rep1,rep2
    #                    "primary":                pooled or rep1 ?
    #                },
    #                { ... }
    #            ],
    #            "signal_reverse": [ { ... } ]
    #        }
    #    },
    #    "experiment_2": {
    #        ...
    #    },
    # }
    datasets = {}
    ihec_json["datasets"] = datasets

    # Other collections
    assays = {}
    pipelines = {}

    for acc in acc_composites.keys():
        acc_composite = acc_composites[acc]
        if acc_composite is None or len(acc_composite) == 0:
            # log.debug("Found empty acc_composite for %s" % (acc))
            continue  # wounded composite can be dropped or added for evidence

        # From any acc_composite, update these:
        if "assembly" not in hub_description:
            ucsc_assembly = acc_composite.get('ucsc_assembly')
            if ucsc_assembly:
                hub_description["assembly"] = ucsc_assembly
            taxon_id = acc_composite.get('taxon_id')
            if taxon_id:
                hub_description["taxon_id"] = taxon_id

        dataset = {}
        datasets[acc] = dataset

        # Find/create sample:
        biosample_name = acc_composite.get('biosample_term_name', 'none')
        if biosample_name == 'none':
            log.warn("acc_composite %s is missing biosample_name", acc)
        molecule = acc_composite.get('molecule', 'none')  # ["total RNA", "polyA RNA", ...
        if molecule == 'none':
            log.warn("acc_composite %s is missing molecule", acc)
        sample_id = "%s; %s" % (biosample_name, molecule)
        if sample_id not in samples:
            sample = {}
            biosample_term_id = acc_composite.get('biosample_term_id')
            if biosample_term_id:
                sample["sample_ontology_uri"] = biosample_term_id
            biosample_type = acc_composite.get('biosample_type')  # ["Cell Line","Primary Cell", ...
            if biosample_type:
                sample["biomaterial_type"] = biosample_type
            sample["molecule"] = molecule
            # sample["disease"] =
            # sample["disease_ontology_uri"] =
            samples[sample_id] = sample
        dataset["sample_id"] = sample_id

        # find/create experiment_attributes:
        assay_id = acc_composite.get('assay_term_id')
        if assay_id:
            if assay_id in assays:
                experiment_attributes = deepcopy(assays[assay_id])  # deepcopy needed?
            else:
                experiment_attributes = {}
                experiment_attributes["experiment_ontology_uri"] = assay_id
                assay_name = acc_composite.get('assay_term_name')
                if assay_name:
                    experiment_attributes["assay_type"] = assay_name
                # "experiment_type": assay_name # EpiRR
                # "reference_registry_id": "..."     IHEC Reference Epigenome registry ID,
                #                                     assigned after submitting to EpiRR
                assays[assay_id] = experiment_attributes
            dataset["experiment_attributes"] = experiment_attributes

        # find/create analysis_attributes:
        # WARNING: This could go crazy!
        pipeline_title = acc_composite.get('pipeline')
        if pipeline_title:
            if pipeline_title in pipelines:
                analysis_attributes = deepcopy(pipelines[pipeline_title])  # deepcopy needed?
            else:
                analysis_attributes = {}
                pipeline_group = acc_composite.get('pipeline_group')
                if pipeline_group:
                    analysis_attributes["analysis_group"] = pipeline_group     # "ENCODE DCC"
                analysis_attributes["analysis_software"] = pipeline_title
                # "analysis_software_version": "..."  # NOTE: version is hard for the whole exp
                # "alignment_software": "...",        # NOTE: sw *could* be found but not worth it
                # "alignment_software_version": "...",
                #        },
                pipelines[pipeline_title] = analysis_attributes
            dataset["analysis_attributes"] = analysis_attributes

        # create browser, which holds views, which hold tracks:
        browser = {}
        dataset["browser"] = browser

        # create views, which will hold tracks
        # ihec_views = {}
        views = acc_composite.get("view", [])
        for view_tag in views["group_order"]:
            view = views["groups"][view_tag]

            # Add tracks to views
            tracks = view.get("tracks", [])
            if len(tracks) == 0:
                continue
            ihec_view = []

            for track in tracks:
                ihec_track = {}
                # ["bigDataUrl","longLabel","shortLabel","type","color","altColor"]
                ihec_track["big_data_url"] = host + track["bigDataUrl"]  # contains ?proxy=true
                ihec_track["description_url"] = '%s/%s/' % (host, acc)
                if request:
                    url = '/'.join(request.url.split('/')[0:-1])
                    url += '/' + acc + '.html'
                    ihec_track["description_url"] = url
                md5sum = track.get('md5sum')
                if md5sum:
                    ihec_track["md5sum"] = md5sum
                ihec_track["subtype"] = track["longLabel"]
                rep_membership = track.get("membership", {}).get("REP")
                rep_group = acc_composite.get("groups", {}).get("REP")
                if rep_membership and rep_group:
                    if rep_membership in rep_group:
                        ihec_track["sample_source"] = rep_group[rep_membership]["title"]
                        subgroup_order = sorted(rep_group["groups"].keys())
                        ihec_track["primary"] = (rep_membership == subgroup_order[0])

                # extra fields
                for term in ["type", "color", "altColor"]:
                    if term in track:
                        ihec_track[term] = track[term]
                ihec_track["view"] = view["title"]
                metadata_pairs = track.get("metadata_pairs", {})
                for meta_key in metadata_pairs:
                    ihec_track[meta_key.replace('&#32;', ' ')] = metadata_pairs[meta_key][1:-1]
                # Could refine download link:
                # if metadata_pairs:
                #     file_download = metadata_pairs.get('file&#32;download')
                #     if file_download:
                #         file_download = file_download.split()[1][6:-1]
                #         ihec_track["file download"] = file_download
                ihec_view.append(ihec_track)
            if len(ihec_view) > 0:
                browser[view["title"]] = ihec_view

    return ihec_json


def find_or_make_acc_composite(request, assembly, acc, dataset=None, hide=False, regen=False):
    '''Returns json for a single experiment 'acc_composite'.'''
    acc_composite = None
    es_key = acc + "_" + assembly
    found_or_made = "found"
    if USE_CACHE and not regen:  # Find composite?
        acc_composite = get_from_es(request, es_key)

    if acc_composite is None:
        request_dataset = (dataset is None)
        if request_dataset:
            dataset = request.embed("/datasets/" + acc + '/', as_user=True)
            # log.debug("find_or_make_acc_composite len(results) = %d   %.3f secs" %
            #           (len(results),(time.time() - PROFILE_START_TIME)))
        host=request.host_url
        if host is None or host.find("localhost") > -1:
            host = "https://www.encodeproject.org"

        acc_composite = make_acc_composite(dataset, assembly, host=host, hide=hide)
        if USE_CACHE:
            add_to_es(request, es_key, acc_composite)
        found_or_made = "made"

        if request_dataset:  # Manage meomory
            del dataset

    return (found_or_made, acc_composite)


def generate_trackDb(request, dataset, assembly, hide=False, regen=False):
    '''Returns string content for a requested  single experiment trackDb.txt.'''
    # local test: bigBed: curl http://localhost:8000/experiments/ENCSR000DZQ/@@hub/hg19/trackDb.txt
    #             bigWig: curl http://localhost:8000/experiments/ENCSR000ADH/@@hub/mm9/trackDb.txt
    # CHIP: https://4217-trackhub-spa-ab9cd63-tdreszer.demo.encodedcc.org/experiments/ENCSR645BCH/@@hub/GRCh38/trackDb.txt
    # LRNA: curl https://4217-trackhub-spa-ab9cd63-tdreszer.demo.encodedcc.org/experiments/ENCSR000AAA/@@hub/GRCh38/trackDb.txt

    if not regen:
        regen = ("regenvis" in request.url)
        # @@hub/GRCh38/regenvis/trackDb.txt regenvis/GRCh38 causes and error
        if not regen:  # TODO temporary
            regen = (request.url.find("ihecjson") > -1)
            # @@hub/GRCh38/ihecjson/trackDb.txt  regenvis/GRCh38 causes and error

    acc = dataset['accession']
    ucsc_assembly = _ASSEMBLY_MAPPER.get(assembly, assembly)
    (found_or_made, acc_composite) = find_or_make_acc_composite(request, ucsc_assembly,
                                                                dataset["accession"], dataset,
                                                                hide=hide, regen=regen)

    vis_type = acc_composite.get("vis_type", get_vis_type(dataset))
    if regen:  # Want to see message if regen was requested
        log.info("%s composite %s_%s %s len(json):%d %.3f" % (found_or_made, dataset['accession'],
                 ucsc_assembly, vis_type, len(json.dumps(acc_composite)),
                 (time.time() - PROFILE_START_TIME)))
    else:
        log.debug("%s composite %s_%s %s len(json):%d %.3f" % (found_or_made, dataset['accession'],
                  ucsc_assembly, vis_type, len(json.dumps(acc_composite)),
                  (time.time() - PROFILE_START_TIME)))
    # del dataset
    json_out = (request.url.find("jsonout") > -1)
    ihec_out = (request.url.find("ihecjson") > -1)
    if json_out:
        return json.dumps(acc_composite, indent=4, sort_keys=True)
    elif ihec_out:
        ihec_json = remodel_acc_to_ihec_json({acc: acc_composite}, request)
        return json.dumps(ihec_json, indent=4, sort_keys=True)
    return ucsc_trackDb_composite_blob(acc_composite, acc)


def generate_batch_trackDb(request, hide=False, regen=False):
    '''Returns string content for a requested multi-experiment trackDb.txt.'''
    # local test: RNA-seq: curl https://../batch_hub/type=Experiment,,assay_title=RNA-seq,,award.rfa=ENCODE3,,status=released,,assembly=GRCh38,,replicates.library.biosample.biosample_type=induced+pluripotent+stem+cell+line/GRCh38/trackDb.txt

    # Special logic to force remaking of trackDb
    if not regen:
        regen = (request.url.find("regenvis") > -1)
        # ...&assembly=hg19&regenvis/hg19/trackDb.txt  regenvis=1 causes an error
        if not regen:  # TODO temporary
            regen = (request.url.find("ihecjson") > -1)  # ...&bly=hg19&ihecjson/hg19/trackDb.txt

    assembly = str(request.matchdict['assembly'])
    log.debug("Request for %s trackDb begins   %.3f secs" %
              (assembly, (time.time() - PROFILE_START_TIME)))
    param_list = parse_qs(request.matchdict['search_params'].replace(',,', '&'))

    set_composites = None

    # Have to make it.
    assemblies = ASSEMBLY_MAPPINGS.get(assembly, [assembly])
    params = {
        'files.file_format': BIGBED_FILE_TYPES + BIGWIG_FILE_TYPES,
    }
    params.update(param_list)
    params.update({
        'assembly': assemblies,
        'limit': ['all'],
    })
    if USE_CACHE:
        params['frame'] = ['object']
    else:
        params['frame'] = ['embedded']

    view = 'search'
    if 'region' in param_list:
        view = 'region-search'
    path = '/%s/?%s' % (view, urlencode(params, True))
    results = request.embed(path, as_user=True)['@graph']
    if not USE_CACHE:
        log.debug("len(results) = %d   %.3f secs" %
                  (len(results), (time.time() - PROFILE_START_TIME)))
    else:
        # Note: better memory usage to get acc array from non-embedded results,
        # since acc_composites should be in cache
        accs = [result['accession'] for result in results]
        del results

    acc_composites = {}
    found = 0
    made = 0
    if USE_CACHE and not regen:
        es_keys = [acc + "_" + assembly for acc in accs]
        acc_composites = search_es(request, es_keys)
        found = len(acc_composites.keys())

    missing_accs = []
    if found == 0:
        missing_accs = accs
    # Don't bother if cache is primed.
    # elif found < (len(accs) * 3 / 4):  # some heuristic to decide when too few means regenerate
    #     missing_accs = list(set(accs) - set(acc_composites.keys()))

    if len(missing_accs) > 0:  # if 0 were found in cache try generating (for pre-primed-cache access)
        if not USE_CACHE: # already have dataset
            for dataset in results:
                acc = dataset['accession']
                if acc not in missing_accs:
                    continue
                (found_or_made, acc_composite) = find_or_make_acc_composite(request, assembly, acc,
                                                                            dataset, hide=hide,
                                                                            regen=True)
                made += 1
                acc_composites[acc] = acc_composite
        else:       # will have to fetch embedded dataset
            for acc in missing_accs:
                (found_or_made, acc_composite) = find_or_make_acc_composite(request, assembly, acc,
                                                                            None, hide=hide,
                                                                            regen=regen)
                if found_or_made == "made":
                    made += 1
                    # log.debug("%s composite %s" % (found_or_made,acc))
                else:
                    found += 1
                acc_composites[acc] = acc_composite

    blob = ""
    set_composites = {}
    if found > 0 or made > 0:
        ihec_out = (request.url.find("ihecjson") > -1)  # ...&ambly=hg19&ihecjson/hg19/trackDb.txt
        if ihec_out:
            ihec_json = remodel_acc_to_ihec_json(acc_composites, request)
            blob = json.dumps(ihec_json, indent=4, sort_keys=True)
        else:
            set_composites = remodel_acc_to_set_composites(acc_composites, hide_after=100)

            json_out = (request.url.find("jsonout") > -1)  # ...&bly=hg19&jsonout/hg19/trackDb.txt
            if json_out:
                blob = json.dumps(set_composites, indent=4, sort_keys=True)
            else:
                for composite_tag in sorted(set_composites.keys()):
                    blob += ucsc_trackDb_composite_blob(set_composites[composite_tag],
                                                        composite_tag)

    if regen:  # Want to see message if regen was requested
        log.info("acc_composites: %s generated, %d found, %d set(s). len(txt):%s  %.3f secs" %
                 (made, found, len(set_composites), len(blob), (time.time() - PROFILE_START_TIME)))
    else:
        log.debug("acc_composites: %s generated, %d found, %d set(s). len(txt):%s  %.3f secs" %
                  (made, found, len(set_composites), len(blob), (time.time() - PROFILE_START_TIME)))

    return blob


def readable_time(secs_float):
    '''Return string of days, hours, minutes, seconds'''
    intervals = [1, 60, 60*60, 60*60*24]
    terms = [('second', 'seconds'), ('minute', 'minutes'), ('hour', 'hours'), ('day', 'days')]

    amount = int(secs_float)
    msecs = int(round(secs_float * 1000) - (amount * 1000))

    result = ""
    for ix in range(len(terms)-1, -1, -1):  # 3,2,1,0
        interval = intervals[ix]
        a = amount // interval
        if a > 0 or interval == 1:
            result += "%d %s, " % (a, terms[ix][a % 1])
            amount -= a * interval
    if msecs > 0:
        result += "%d msecs" % (msecs)
    else:
        result = result[:-2]

    return result


# Note: Required for Bek's cache priming solution.
@subscriber(AfterIndexedExperimentsAndDatasets)
def prime_vis_es_cache(event):
    '''Priming occurs whenever es objects are invalidated but after _indexer is done with them.'''
    global PROFILE_START_TIME
    PROFILE_START_TIME = time.time()
    # NOTE: should not be called unless peak_indexer.py::TRACKHUB_CACHING == True
    request = event.request
    uuids = event.object  # unordered set of unique ids that have been invalidated
    if not uuids:
        return

    # logging is not at visualization.py module level.  The logger is the scubscribed to one.
    log.setLevel(logging.INFO)  # NOTE: Change here to show debug messages
    verbose_threshold = 100     # Only be verbose if this is a big set
    raw_count = len(uuids)
    if raw_count >= verbose_threshold:  # If enough, then want this framed
        log.info("Starting prime_vis_es_cache: %d uuids" % (raw_count))
    else:
        log.debug("Starting prime_vis_es_cache: %d uuids" % (raw_count))

    visualizabe_types = set(VISIBLE_DATASET_TYPES)
    count = 0
    for uuid in uuids:
        dataset = request.embed(uuid)
        # Try to limit the sets we are interested in
        if dataset.get('status', 'none') not in VISIBLE_DATASET_STATUSES:
            continue
        if visualizabe_types.isdisjoint(dataset['@type']):
            continue
        acc = dataset['accession']
        assemblies = dataset.get('assembly', [])
        for assembly in assemblies:
            ucsc_assembly = _ASSEMBLY_MAPPER.get(assembly, assembly)
            (made, acc_composite) = find_or_make_acc_composite(request, ucsc_assembly,
                                                               acc, dataset, regen=True)
            if acc_composite:
                count += 1
                log.debug("primed vis_es_cache with acc_composite %s_%s '%s'  %.3f secs" %
                          (acc, ucsc_assembly,
                           acc_composite.get('vis_type', ''), (time.time() - PROFILE_START_TIME)))
            # Took 12h32m on initial
            # else:
            #    log.debug("prime_vis_es_cache for %s_%s unvisualizable '%s'" % \
            #                                (acc,ucsc_assembly,get_vis_type(dataset)))
    # if count == 0:
    if raw_count >= verbose_threshold or count >= verbose_threshold/10:
        log.info("prime_vis_es_cache made %d acc_composites  %s" %
                 (count, readable_time(time.time() - PROFILE_START_TIME)))
    else:
        log.debug("prime_vis_es_cache made %d acc_composites  %s" %
                  (count, readable_time(time.time() - PROFILE_START_TIME)))
    log.setLevel(logging.NOTSET)  # Not sure if this is needed.


def render(data):
    arr = []
    for i in range(len(data)):
        temp = list(data.popitem())
        str1 = ' '.join(temp)
        arr.append(str1)
    return arr


def get_genome_txt(assembly):
    # UCSC shim
    ucsc_assembly = _ASSEMBLY_MAPPER.get(assembly, assembly)
    genome = OrderedDict([
        ('trackDb', ucsc_assembly + '/trackDb.txt'),
        ('genome', ucsc_assembly)
    ])
    return render(genome)


def get_genomes_txt(assemblies):
    blob = ''
    ucsc_assemblies = set()
    for assembly in assemblies:
        ucsc_assemblies.add(_ASSEMBLY_MAPPER.get(assembly, assembly))
    for ucsc_assembly in ucsc_assemblies:
        if blob == '':
            blob = NEWLINE.join(get_genome_txt(ucsc_assembly))
        else:
            blob += 2 * NEWLINE + NEWLINE.join(get_genome_txt(ucsc_assembly))
    return blob


def get_hub(label, comment=None, name=None):
    if name is None:
        name = sanitize_name(label.split()[0])
    if comment is None:
        comment = "Generated by the ENCODE portal"
    hub = OrderedDict([
        ('email', 'encode-help@lists.stanford.edu'),
        ('genomesFile', 'genomes.txt'),
        ('longLabel', 'ENCODE Data Coordination Center Data Hub'),
        ('shortLabel', 'Hub (' + label + ')'),
        ('hub', 'ENCODE_DCC_' + name),
        ('#', comment)
    ])
    return render(hub)


def vis_format_external_url(browser, hub_url, assembly, position=None):
    '''Given a url to hub.txt, returns the url to an external browser or None.'''
    mapped_assembly = _ASSEMBLY_MAPPER_FULL[assembly]
    if not mapped_assembly:
        return None
    if browser == "ucsc":
        ucsc_assembly = mapped_assembly.get('ucsc_assembly')
        if ucsc_assembly is not None:
            external_url = 'http://genome.ucsc.edu/cgi-bin/hgTracks?hubClear='
            external_url += hub_url + '&db=' + ucsc_assembly
            if position is not None:
                external_url += '&position={}'.format(position)
            return external_url
    elif browser == "ensembl":
        ensembl_host = mapped_assembly.get('ensembl_host')
        if ensembl_host is not None:
            external_url = 'http://' + ensembl_host + '/Trackhub?url='
            external_url += hub_url + ';species=' + species
            if position is not None:
                if position.startswith('chr'):
                    position = position[3:]  # ensembl position r=19:7069444-7087968
                external_url += '&r={}'.format(position)
            # GRCh38:   http://www.ensembl.org/Trackhub?url=https://www.encodeproject.org/experiments/ENCSR596NOF/@@hub/hub.txt
            # GRCh38:   http://www.ensembl.org/Trackhub?url=https://www.encodeproject.org/experiments/ENCSR596NOF/@@hub/hub.txt;species=Homo_sapiens
            # hg19/GRCh37:     http://grch37.ensembl.org/Trackhub?url=https://www.encodeproject.org/experiments/ENCSR596NOF/@@hub/hub.txt;species=Homo_sapiens
            # mm10/GRCm38:     http://www.ensembl.org/Trackhub?url=https://www.encodeproject.org/experiments/ENCSR475TDY@@hub/hub.txt;species=Mus_musculus
            # mm9/NCBIM37:      http://may2012.archive.ensembl.org/Trackhub?url=https://www.encodeproject.org/experiments/ENCSR000CNV@@hub/hub.txt;species=Mus_musculus
            # BDGP6:    http://www.ensembl.org/Trackhub?url=https://www.encodeproject.org/experiments/ENCSR040UNE@@hub/hub.txt;species=Drosophila_melanogaster
            # BDGP5:    http://dec2014.archive.ensembl.org/Trackhub?url=https://www.encodeproject.org/experiments/ENCSR040UNE@@hub/hub.txt;species=Drosophila_melanogaster
            # ce11/WBcel235: http://www.ensembl.org/Trackhub?url=https://www.encodeproject.org/experiments/ENCSR475TDY@@hub/hub.txt;species=Caenorhabditis_elegans
            return external_url
    #else:
        # ERROR: not supported at this time
    return None


def generate_html(context, request):
    ''' Generates and returns HTML for the track hub'''

    # First determine if single dataset or collection
    # log.debug("HTML request: %s" % request.url)

    html_requested = request.url.split('/')[-1].split('.')[0]
    if html_requested.startswith('ENCSR'):
        embedded = request.embed(request.resource_path(context))
        acc = embedded['accession']
        log.debug("generate_html for %s   %.3f secs" % (acc, (time.time() - PROFILE_START_TIME)))
        assert(html_requested == acc)

        vis_type = get_vis_type(embedded)
        vis_defs = lookup_vis_defs(vis_type)
        longLabel = vis_defs.get('longLabel',
                                 '{assay_term_name} of {biosample_term_name} - {accession}')
        longLabel = sanitize_label(convert_mask(longLabel, embedded))

        link = request.host_url + '/experiments/' + acc + '/'
        acc_link = '<a href={link}>{accession}<a>'.format(link=link, accession=acc)
        if longLabel.find(acc) != -1:
            longLabel = longLabel.replace(acc, acc_link)
        else:
            longLabel += " - " + acc_link
        page = '<h2>%s</h2>' % longLabel

    else:  # collection
        vis_type = html_requested
        vis_defs = lookup_vis_defs(vis_type)
        longLabel = vis_defs.get('assay_composite', {}).get('longLabel',
                                                            "Unknown collection of experiments")
        page = '<h2>%s</h2>' % longLabel

        # TO IMPROVE: limit the search url to this assay only.
        # Not easy since vis_def is not 1:1 with assay
        try:
            param_list = parse_qs(request.matchdict['search_params'].replace(',,', '&'))
            search_url = '%s/search/?%s' % (request.host_url, urlencode(param_list, True))
            # search_url = (request.url).split('@@hub')[0]
            search_link = '<a href=%s>Original search<a><BR>' % search_url
            page += search_link
        except:
            pass

    # TODO: Extend page with assay specific details
    details = vis_defs.get("html_detail")
    if details is not None:
        page += details

    return page  # data_description + header + file_table


def generate_batch_hubs(context, request):
    '''search for the input params and return the trackhub'''
    global PROFILE_START_TIME
    PROFILE_START_TIME = time.time()

    results = {}
    txt = request.matchdict['txt']

    if len(request.matchdict) == 3:

        # Should generate a HTML page for requests other than trackDb.txt
        if txt != TRACKDB_TXT:
            data_policy = ('<br /><a href="http://encodeproject.org/ENCODE/terms.html">'
                           'ENCODE data use policy</p>')
            return generate_html(context, request) + data_policy

        return generate_batch_trackDb(request)

    elif txt == HUB_TXT:
        terms = request.matchdict['search_params'].replace(',,', '&')
        pairs = terms.split('&')
        label = "search:"
        for pair in sorted(pairs):
            (var, val) = pair.split('=')
            if var not in ["type", "assembly", "status", "limit"]:
                label += " %s" % val.replace('+', ' ')
        return NEWLINE.join(get_hub(label, request.url))
    elif txt == GENOMES_TXT:
        param_list = parse_qs(request.matchdict['search_params'].replace(',,', '&'))

        view = 'search'
        if 'region' in param_list:
            view = 'region-search'
        path = '/%s/?%s' % (view, urlencode(param_list, True))
        results = request.embed(path, as_user=True)
        # log.debug("generate_batch(genomes) len(results) = %d   %.3f secs" %
        #           (len(results),(time.time() - PROFILE_START_TIME)))
        g_text = ''
        if 'assembly' in param_list:
            g_text = get_genomes_txt(param_list.get('assembly'))
        else:
            for facet in results['facets']:
                if facet['field'] == 'assembly':
                    assemblies = []
                    for term in facet['terms']:
                        if term['doc_count'] != 0:
                            assemblies.append(term['key'])
                    if len(assemblies) > 0:
                        g_text = get_genomes_txt(assemblies)
        return g_text


@view_config(name='hub', context=Item, request_method='GET', permission='view')
def hub(context, request):
    ''' Creates trackhub on fly for a given experiment '''
    global PROFILE_START_TIME
    PROFILE_START_TIME = time.time()

    url_ret = (request.url).split('@@hub')
    embedded = request.embed(request.resource_path(context))

    if url_ret[1][1:] == HUB_TXT:
        typeof = embedded.get("assay_title")
        if typeof is None:
            typeof = embedded["@id"].split('/')[1]

        label = "%s %s" % (typeof, embedded['accession'])
        name = sanitize_name(label)
        return Response(NEWLINE.join(get_hub(label, request.url, name)),
                        content_type='text/plain')
    elif url_ret[1][1:] == GENOMES_TXT:
        assemblies = ''
        if 'assembly' in embedded:
            assemblies = embedded['assembly']

        g_text = get_genomes_txt(assemblies)
        return Response(g_text, content_type='text/plain')

    elif url_ret[1][1:].endswith(TRACKDB_TXT):
        trackDb = generate_trackDb(request, embedded, url_ret[1][1:].split('/')[0])
        return Response(trackDb, content_type='text/plain')
    else:
        data_policy = ('<br /><a href="http://encodeproject.org/ENCODE/terms.html">'
                       'ENCODE data use policy</p>')
        return Response(generate_html(context, request) + data_policy, content_type='text/html')


@view_config(route_name='batch_hub')
@view_config(route_name='batch_hub:trackdb')
def batch_hub(context, request):
    ''' View for batch track hubs '''
    return Response(generate_batch_hubs(context, request), content_type='text/plain')
