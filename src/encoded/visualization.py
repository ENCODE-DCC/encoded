from pyramid.response import Response
from pyramid.view import view_config
from snovault import Item
from collections import OrderedDict
from copy import deepcopy
import cgi
import json
from urllib.parse import (
    parse_qs,
    urlencode,
)

import logging
from .search import _ASSEMBLY_MAPPER

log = logging.getLogger(__name__)

def includeme(config):
    config.add_route('batch_hub', '/batch_hub/{search_params}/{txt}')
    config.add_route('batch_hub:trackdb', '/batch_hub/{search_params}/{assembly}/{txt}')
    config.scan(__name__)


TAB = '\t'
NEWLINE = '\n'
HUB_TXT = 'hub.txt'
GENOMES_TXT = 'genomes.txt'
TRACKDB_TXT = 'trackDb.txt'
BIGWIG_FILE_TYPES = ['bigWig']
BIGBED_FILE_TYPES = ['bigBed']


# static group defs are keyed by group title (or special token) and consist of
# tag: (optional) unique terse key for referencing group
# groups: (optional) { subgroups keyed by subgroup title }
# group_order: (optional) [ ordered list of subgroup titles ]
# other definitions

# live group defs are keyed by tag and are the transformed in memory version of static defs
# title: (required) same as the static group's key
# groups: (if appropriate) { subgroups keyed by subgroup tag }
# group_order: (if appropriate) [ ordered list of subgroup tags ]
COMPOSITE_VIS_DEFS_DEFAULT = {
    "assay_composite": {
        "longLabel":  "Collection of Miscellaneous ENCODE datasets",
        "shortLabel": "ENCODE Misc.",
    },
    "longLabel":  "{assay_title} of {replicates.library.biosample.summary} - {accession}",
    "shortLabel": "{assay_title} of {biosample_term_name} {accession}",
    "color":      "{biosample_term_name}",
    "altColor":   "{biosample_term_name}",
    "pennantIcon": 'encodeThumbnail.jpg https://www.encodeproject.org/ "ENCODE: Encyclopedia of DNA Elements"',
    #"allButtonPair": "off"
    "sortOrder": [ "Biosample", "Targets", "Replicates", "Views" ],
    "Views":  {
        "tag": "view",
        "group_order": [ "Peaks", "Signals" ],
        "groups": {
            "Peaks": {
                "tag": "PK",
                "visibility": "dense",
                "type": "bigBed",
                "spectrum": "on",
            },
            "Signals": {
                "tag": "SIG",
                "visibility": "full",
                "type": "bigWig",
                "autoScale": "on",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
            },
        },
    },
    "other_groups":  {
        "dimensions": { "Biosample": "dimY", "Targets": "dimX", "Replicates": "dimA" },
        "filterComposite": { "Replicates": "multiple" },
        "groups": {
            "Replicates": {
                "tag": "REP",
                "group_order": "sort",
                "groups": {
                    "replicate": {
                        "title_mask": "Replicate_{replicate_number}",
                        "combined_title": "Pooled",
                    },
                },
            },
            "Biosample": {
                "tag": "BS",
                "sortable": True,
                "group_order": "sort",
                "groups": { "one": { "title_mask": "{biosample_term_name}" } },
            },
            "Targets": {
                "tag": "TARG",
                "group_order": "sort",
                "groups": { "one": { "title_mask": "{target.label}" } },
            },
        }
    },
    "file_defs": {
        "longLabel": "{assay_title} of {biosample_term_name} {output_type} {replicate} {experiment.accession} - {file.accession}",
        "shortLabel": "{replicate} {output_type_short_label}",
    },
}

LRNA_COMPOSITE_VIS_DEFS = {
    "assay_composite": {
        "longLabel":  "Collection of ENCODE long-RNA-seq experiments",
        "shortLabel": "ENCODE long-RNA-seq",
    },
    "longLabel":  "{assay_title} of {replicates.library.biosample.summary} - {accession}",
    "shortLabel": "{assay_title} of {biosample_term_name} {accession}",
    "color":      "{biosample_term_name}",
    "altColor":   "{biosample_term_name}",
    "pennantIcon": 'encodeThumbnail.jpg https://www.encodeproject.org/ "ENCODE: Encyclopedia of DNA Elements"',
    "sortOrder": [ "Biosample", "Targets", "Replicates", "Views" ],
    "Views": {
        "tag": "view",
        "group_order": [ "Signal of unique reads", "Signal of all reads", "Plus signal of unique reads", "Minus signal of unique reads", "Plus signal of all reads", "Minus signal of all reads", ],
        "groups": {
            "Signal of all reads": {
                "tag": "SIGA",
                "visibility": "hide",
                "type": "bigWig",
                "viewLimits": "0:1",
                "transformFunc": "LOG",
                "autoScale": "off",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "signal of all reads" ]
            },
            "Signal of unique reads": {
                "tag": "SIGU",
                "visibility": "full",
                "type": "bigWig",
                "viewLimits": "0:1",
                "transformFunc": "LOG",
                "autoScale": "off",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "signal of unique reads" ]
            },
            "Plus signal of all reads": {
                "tag": "PSIGA",
                "visibility": "hide",
                "type": "bigWig",
                "viewLimits": "0:1",
                "transformFunc": "LOG",
                "autoScale": "off",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "plus strand signal of all reads" ]
            },
            "Plus signal of unique reads": {
                "tag": "PSIGU",
                "visibility": "full",
                "type": "bigWig",
                "viewLimits": "0:1",
                "transformFunc": "LOG",
                "autoScale": "off",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "plus strand signal of unique reads" ]
            },
            "Minus signal of all reads": {
                "tag": "SIGMA",
                "visibility": "hide",
                "type": "bigWig",
                "viewLimits": "0:1",
                "transformFunc": "LOG",
                "autoScale": "off",
                "negateValues": "on",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "minus strand signal of all reads" ]
            },
            "Minus signal of unique reads": {
                "tag": "SIGMU",
                "visibility": "full",
                "type": "bigWig",
                "viewLimits": "0:1",
                "transformFunc": "LOG",
                "autoScale": "off",
                "negateValues": "on",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "minus strand signal of unique reads" ]
            },
        },
    },
    "other_groups": {
        "dimensions": { "Biosample": "dimY", "Targets": "dimX", "Replicates": "dimA" },
        "dimensionAchecked": "first", # or "all"
        "groups": {
            "Replicates": {
                "tag": "REP",
                "group_order": "sort",
                "groups": {
                "replicate": {
                    "title_mask": "Replicate_{replicate_number}", # Optional
                    #"tag_mask": "{replicate}", # Implicit
                    "combined_title": "Pooled", # "Combined"
                    }
                },
            },
            "Biosample": {
                "tag": "BS",
                "sortable": True,
                "group_order": "sort",
                "groups": { "one": { "title_mask": "{biosample_term_name}"} }
            },
            "Targets": {
                "tag": "TARG",
                "group_order": "sort",
                "groups": { "one": { "title_mask": "{target.label}" } },
            },
        }
    },
    "file_defs": {
        "longLabel": "{assay_title} of {biosample_term_name} {output_type} {replicate} {experiment.accession} - {file.accession}",
        "shortLabel": "{replicate} {output_type_short_label}",
    }
}

CHIP_COMPOSITE_VIS_DEFS = {
    "assay_composite": {
        "longLabel":  "Collection of ENCODE ChIP-seq experiments",
        "shortLabel": "ENCODE ChIP-seq",
    },
    "longLabel":  "{target} {assay_title} of {replicates.library.biosample.summary} - {accession}",
    "shortLabel": "{target} {assay_title} of {biosample_term_name} {accession}",
    "color":      "{biosample_term_name}",
    "altColor":   "{biosample_term_name}",
    "pennantIcon": "encodeThumbnail.jpg https://www.encodeproject.org/ \"ENCODE: Encyclopedia of DNA Elements\"",
    "sortOrder": [ "Biosample", "Targets", "Replicates", "Views" ],
    "Views":  {
        "tag": "view",
        "group_order": [ "Optimal IDR thresholded peaks", "Conservative IDR thresholded peaks", "Replicated peaks", "Peaks",  "Fold change over control", "Signal p-value",  ],
        "groups": {

            "Fold change over control": {
                "tag": "FCOC",
                "visibility": "full",
                "type": "bigWig",
                "viewLimits": "0:1",
                "autoScale": "off",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "fold change over control" ]
            },
            "Signal p-value": {
                "tag": "SPV",
                "visibility": "hide",
                "type": "bigWig",
                "viewLimits": "0:1",
                "autoScale": "off",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "signal p-value" ]
            },
            "Signal": {
                "tag": "SIG",
                "visibility": "hide",
                "type": "bigWig",
                "viewLimits": "0:1",
                "autoScale": "off",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "signal" ]
            },
            "Replicated peaks": {
                "tag": "RPKS",
                "visibility": "dense",
                "type": "bigBed",
                "file_format_type": [ "narrowPeak" ],
                "spectrum":"on",
                "scoreFilter": "0:1000",
                "output_type": [ "replicated peaks" ]
            },
            "Peaks": {
                "tag": "PKS",
                "visibility": "hide",
                "type": "bigBed",
                "file_format_type": [ "narrowPeak" ],
                "scoreFilter": "0:1000",
                "output_type": [ "peaks" ],
                # Tim, how complicated would it be to exclude "peaks" if other files are there?
            },
            "Conservative IDR thresholded peaks": {
                "tag": "CONSIDR",
                "visibility": "hide",
                "type": "bigBed",
                "file_format_type": [ "narrowPeak" ],
                "spectrum":"on",
                "scoreFilter": "0:1000",
                "output_type": [ "conservative idr thresholded peaks" ]
            },
            "Optimal IDR thresholded peaks": {
                "tag": "OPTIDR",
                "visibility": "dense",
                "type": "bigBed",
                "file_format_type": [ "narrowPeak" ],
                "spectrum":"on",
                "output_type": [ "optimal idr thresholded peaks" ]
            },
        },
    },
    "other_groups":  {
        "dimensions": { "Biosample": "dimY","Targets": "dimX","Replicates": "dimA" },
        "dimensionAchecked": "first", # or "all"
        #"filterComposite": { "Replicates": "multiple" },
        "groups": {
            "Replicates": {
                "tag": "REP",
                "group_order": "sort",
                "groups": {
                    "replicate": {
                        "title_mask": "Replicate_{replicate_number}", # Optional
                        "combined_title": "Pooled", # "Combined"
                         #We only want pooled replicates on
                    }
                },
            },
            "Biosample": {
                "tag": "BS",
                "sortable": True,
                "group_order": "sort",
                "groups": { "one": { "title_mask": "{biosample_term_name}"} }
            },
            "Targets": {
                "tag": "TARG",
                "group_order": "sort",
                "groups": { "one": { "title_mask": "{target.label}"} }
            }
        }
    },
    "file_defs": {
        "longLabel": "{target} {assay_title} of {biosample_term_name} {output_type} {replicate} {experiment.accession} - {file.accession}",
        "shortLabel": "{replicate} {output_type_short_label}",
    }
}

ECLIP_COMPOSITE_VIS_DEFS = {
    "longLabel":  "{target} {assay_title} of {replicates.library.biosample.summary} - {accession}",
    "shortLabel": "{target} {assay_title} of {biosample_term_name} {accession}",
    "color":      "{biosample_term_name}",
    "altColor":   "{biosample_term_name}",
    "pennantIcon": "encodeThumbnail.jpg https://www.encodeproject.org/ \"ENCODE: Encyclopedia of DNA Elements\"",
    "sortOrder": [ "Biosample", "Targets", "Replicates", "Views" ],
    "Views":  {
        "tag": "view",
        "group_order": [ "Signal", "Peaks" ],
        "groups": {
            "Signal": {
                "tag": "SIG",
                "visibility": "full",
                "type": "bigWig",
                "viewLimits": "0:1",
                "autoScale": "off",
                "maxHeightPixels": "32:16:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "signal" ]
            },
            "Peaks": {
                "tag": "PKS",
                "visibility": "dense",
                "type": "bigBed",
                "spectrum": "on",
                "output_type": [ "peaks" ]
            },
        },
    },
    "other_groups":  {
        "dimensions": { "Biosample": "dimY","Targets": "dimX","Replicates": "dimA" },
        "dimensionAchecked": "first", # or "all"
        "groups": {
            "Replicates": {
                "tag": "REP",
                "group_order": "sort",
                "groups": {
                    "replicate": {
                        "title_mask": "Replicate_{replicate_number}",
                        "combined_title": "Pooled",
                         #We only want pooled replicates on
                    }
                },
            },
            "Biosample": {
                "tag": "BS",
                "sortable": True,
                "group_order": "sort",
                "groups": { "one": { "title_mask": "{biosample_term_name}"} }
            },
            "Targets": {
                "tag": "TARG",
                "group_order": "sort",
                "groups": { "one": { "title_mask": "{target.label}"} }
            }
        }
    },
    "file_defs": {
        "longLabel": "{target} {assay_title} of {biosample_term_name} {output_type} {replicate} {experiment.accession} - {file.accession}",
        "shortLabel": "{replicate} {output_type_short_label}",
    }
}

VIS_DEFS_BY_ASSAY = {
    "LRNA":  LRNA_COMPOSITE_VIS_DEFS,
    "CHIP":  CHIP_COMPOSITE_VIS_DEFS,
    "eCLIP": ECLIP_COMPOSITE_VIS_DEFS
    }

def get_exp_vis_type(exp):
    '''returns the best static composite definition set, based upon exp.'''
    assay = str(exp.get("assay_term_name","unknown"))
    # This will be long AND small
    if assay in ["RNA-seq","shRNA knockdown followed by RNA-seq","CRISPR genome editing followed by RNA-seq","single cell isolation followed by RNA-seq"]:
        size_range = exp["replicates"][0]["library"]["size_range"]
        if size_range.startswith('>'):
            size_range = size_range[1:]
        try:
            min_size = int(size_range.split('-')[0])
        except:
            min_size = 0
        if min_size >= 149:
            return "LRNA"
        else:
            return "SRNA"
    elif assay in ["whole-genome shotgun bisulfite sequencing","shotgun bisulfite-seq assay"]:
        return "WGBS"
    elif assay.lower() in ["rampage","cage"]:
        return "RAMP"
    elif assay == "ChIP-seq":
        return "CHIP"
    elif assay == "eCLIP":
        return assay

    return "opaque" # This becomes a dict key later so None is not okay


def lookup_vis_defs(vis_type):
    '''returns the best static composite definition set, based upon exp.'''
    global COMPOSITE_VIS_DEFS_DEFAULT
    global VIS_DEFS_BY_ASSAY

    return VIS_DEFS_BY_ASSAY.get(vis_type, COMPOSITE_VIS_DEFS_DEFAULT )

SUPPORTED_SUBGROUPS = [
    "Biosample", "Targets", "Replicates", "Views"
    ]

SUPPORTED_TRACK_SETTINGS = [
    "type","visibility","longLabel","shortLabel","color","altColor","allButtonPair",
    "scoreFilter","spectrum",
    "viewLimits","autoScale","negateValues","maxHeightPixels","windowingFunction","transformFunc",
    ]
COMPOSITE_SETTINGS = ["longLabel","shortLabel","visibility","pennantIcon","color","altColor","allButtonPair"]
VIEW_SETTINGS = SUPPORTED_TRACK_SETTINGS
TRACK_SETTINGS = ["bigDataUrl","longLabel","shortLabel","type","color","altColor"]


SUPPORTED_MASK_TOKENS = [
    "{replicate}",         # The replicate that that will be displayed for visualized track: ("rep1", "combined") (AKA rep_tag)
    "{rep_tech}",          # The rep_tech if desired ("rep1_1", "combined")
    "{replicate_number}",  # The replicate number displayed for visualized track: ("1", "0")
    "{biological_replicate_number}",
    "{technical_replicate_number}",
    "{assay_title}",
    "{assay_term_name}",                    # dataset.assay_term_name
    # TODO "{annotation_type}",             # some datasets have annotation type and not assay (higher end trickery)
    "{output_type}",                        # files.output_type
    "{accession}","{experiment.accession}", # "{accession}" is assumed to be experiment.accession

    "{file.accession}",
    "{target}","{target.label}",            # Either is acceptible
    "{biosample_term_name}",
    "{output_type_short_label}",                # hard-coded translation from output_type to very short version Do we want this in schema?
    "{replicates.library.biosample.summary}",   # Idan and Forrest and I are conspiring to move this to dataset.biosample_summary and make it much shorter
    "{assembly}",                               # you don't need this in titles, but it is crucial variable and seems to not be being applied correctly in the html generation
    # TODO "{software? or pipeline?}",          # I am stumbling over the fact that we can't distinguish tophat and star produced files
    # TODO "{phase}",                           # If we get to the point of being fancy in the replication timing, then we need this, otherwise it bundles up in the biosample summary now
    ]

OUTPUT_TYPE_7CHARS = {
    #"idat green channel": "idat gr",     # raw data
    #"idat red channel": "idat rd",       # raw data
    #"reads":"reads",                     # raw data
    #"intensity values": "intnsty",       # raw data
    #"reporter code counts": "rcc",       # raw data
    #"alignments":"aln",                  # our plan is not to visualize alignments for now
    #"unfiltered alignments":"unflt aln", # our plan is not to visualize alignments for now
    #"transcriptome alignments":"tr aln", # our plan is not to visualize alignments for now
    "minus strand signal of all reads":     "all -",
    "plus strand signal of all reads":      "all +",
    "signal of all reads":                  "all sig",
    "normalized signal of all reads":       "normsig",
    #"raw minus strand signal":"raw -",   # these are all now minus signal of all reads
    #"raw plus strand signal":"raw +",    # these are all now plus signal of all reads
    "raw signal":                           "raw sig",
    "raw normalized signal":                "nraw",
    "read-depth normalized signal":         "rdnorm",
    "control normalized signal":            "ctlnorm",
    "minus strand signal of unique reads":  "unq -",
    "plus strand signal of unique reads":   "unq +",
    "signal of unique reads":               "unq sig",
    "signal p-value":                       "pval sig",
    "fold change over control":             "foldchg",
    "exon quantifications":                 "exon qnt",
    "gene quantifications":                 "gene qnt",
    "microRNA quantifications":             "miRNA qnt",
    "transcript quantifications":           "trnscrpt qnt",
    "library fraction":                     "lib frac",
    "methylation state at CpG":             "mth CpG",
    "methylation state at CHG":             "mth CHG",
    "methylation state at CHH":             "mth CHH",
    "enrichment":                           "enrich",
    "replication timing profile":           "repli time",
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
    #"genome reference":"ref",           # references not to be viewed
    #"transcriptome reference":"tr ref", # references not to be viewed
    #"transcriptome index":"tr rix",     # references not to be viewed
    #"tRNA reference":"tRNA",            # references not to be viewed
    #"miRNA reference":"miRNA",          # references not to be viewed
    #"snRNA reference":"snRNA",          # references not to be viewed
    #"rRNA reference":"rRNA",            # references not to be viewed
    #"TSS reference":"TSS",              # references not to be viewed
    #"reference variants":"var",         # references not to be viewed
    #"genome index":"ref ix",            # references not to be viewed
    #"female genome reference":"XX ref", # references not to be viewed
    #"female genome index":"XX rix",     # references not to be viewed
    #"male genome reference":"XY ref",   # references not to be viewed
    #"male genome index":"XY rix",       # references not to be viewed
    #"spike-in sequence":"spike",        # references not to be viewed
    "optimal idr thresholded peaks":        "oIDR pk",
    "conservative idr thresholded peaks":   "cIDR pk",
    "enhancer validation":                  "enh val",
    "semi-automated genome annotation":     "saga"
    }

BIOSAMPLE_COLOR = {
    "brain": "105,105,105",
    #"skin of body": "",
    "heart": "153,38,0",
    "liver": "230,159,0",
    #"lung": "",
    "kidney": "204,121,167",
    "muscle organ": "102,50,200",  #This is limbs at UCSC
    "large intestine": "230,159,0",
    "stomach": "230,159,0",
    "extraembryonic structure": "153,38,0",
    #"blood vessel": "",
    "mammary gland": "0,158,115",
    "small intestine": "230,159,0",
    "adrenal gland": "189,0,157",
    #"pancreas": "",
    "spleen": "86,180,233",
    "gonad": "0,158,115",
    #"esophagus": "",
    "thymus": "86,180,233",
    "placenta": "153,38,0",
    "blood": "86,180,233",
    #"bone element": " ",
    "eye": "105,105,105",
    #"ureter": "",
    #"thyroid gland": "",
    "spinal cord": "105,105,105",
    #"urinary bladder": "",
    #"mouth": "",
    #"prostate gland": "",
    #"bronchus": "",
    #"lymphatic vessel": "",
    #"tongue": "",
    #"trachea": "",
    #"billary tree": "",
    "nose": "105,105,105",
    "olfactory organ": "105,105,105",
    }

def lookup_color(mask,exp,halfColor=False):
    '''Using the mask, determine which color table to use.'''
    global BIOSAMPLE_COLOR
    color = None
    if mask == "{biosample_term_name}":
        if len(mask.split(',')) == 3:
            color = mask
        else:
            biosample = exp.get('biosample_term_name', 'Unknown Biosample')
            color = BIOSAMPLE_COLOR.get(biosample)
    if halfColor and color is not None:
        shades = color.split(',')
        red = int(shades[0]) / 2
        green = int(shades[1]) / 2
        blue = int(shades[2]) / 2
        color = "%d,%d,%d" % (red,green,blue)
    return color

def add_living_color(live_settings, defs, exp):
    '''Adds color and altColor'''
    if "color" in defs:
        color = lookup_color(defs["color"],exp)
        if color is not None:
            live_settings["color"] = color
        if "altColor" in defs:
            if defs["altColor"].startswith("same"):
                live_settings["altColor"] = color
            else:
                color = lookup_color(defs["altColor"],exp)
                if color is not None:
                    live_settings["altColor"] = color
        else:
            live_settings["altColor"] = lookup_color(defs["color"],exp,halfColor=True)

def sanitize_char(c,exceptions=[ '_' ],htmlize=False,numeralize=False):
    '''Pass through for 0-9,A-Z.a-z,_, but then either html encodes, numeralizes or removes special characters.'''
    n = ord(c)
    if n >= 47 and n <= 57: # 0-9
        return c
    if n >= 65 and n <= 90: # A-Z
        return c
    if n >= 97 and n <= 122: # a-z
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
        new_s += sanitize_char(c,[ ' ', '_','.','-','(',')','+' ],htmlize=True)
    return new_s

def sanitize_title(s):
    '''Encodes the string to swap special characters and replace spaces with '_'.'''
    new_s = ""      # Titles appear in tag=title pairs and cannot have spaces
    for c in s:
        new_s += sanitize_char(c,[ '_','.','-','(',')','+' ],htmlize=True)
    return new_s

def sanitize_tag(s):
    '''Encodes the string to swap special characters and remove spaces.'''
    new_s = ""
    first = True
    for c in s:
        new_s += sanitize_char(c,numeralize=True)
        if first:
            if new_s.isdigit(): # tags cannot start with digit.
                new_s = 'z' + new_s
            first = False
    return new_s

def sanitize_name(s):
    '''Encodes the string to remove special characters swap spaces for underscores.'''
    new_s = ""
    first = True
    for c in s:
        new_s += sanitize_char(c)
    return new_s


def rep_for_file(a_file):
    '''Determines best rep_tech or rep for a file.'''
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
        if len(tech_reps) > 1:
            bio = 0
            for tech in tech_reps:
                if bio == 0:
                    bio = int(tech.split('_')[0])
                elif bio != int(tech.split('_')[0]):
                    bio = -1
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


def lookup_token(token,exp,a_file=None):
    '''Encodes the string to swap special characters and remove spaces.'''
    global SUPPORTED_MASK_TOKENS
    global OUTPUT_TYPE_7CHARS

    assert(token in SUPPORTED_MASK_TOKENS)
    if token in ["{biosample_term_name}","{accession}","{assay_title}","{assay_term_name}"]:
        term = exp.get(token[1:-1])
        if term is None:
            term = "Unknown " + token[1:-1].split('_')[0].capitalize()
        return term
    elif token == "{experiment.accession}":
        return exp['accession']
    elif token in ["{target}","{target.label}"]:
        target = exp.get('target',{})
        if isinstance(target,list):
            target = target[0]
        return target.get('label',"Unknown Target")
    elif token == "{replicates.library.biosample.summary}":
        term = None
        replicates = exp.get("replicates",[])
        if replicates:
            term = replicates[0].get("library",{}).get("biosample",{}).get("summary")
        if term is None:
            term = exp.get("{biosample_term_name}", "Unknown Biosample")
        return term
    elif a_file is not None:
        if token == "{file.accession}":
            return a_file['accession']
        elif token == "{output_type}":
            return a_file['output_type']
        elif token == "{output_type_short_label}":
            output_type = a_file['output_type']
            return OUTPUT_TYPE_7CHARS.get(output_type,output_type)
        elif token == "{replicate}":
            rep_tag = a_file.get("rep_tag")
            if rep_tag is not None:
                return rep_tag
            rep_tech = a_file.get("rep_tech")
            if rep_tech is not None:
                return rep_tech.split('_')[0]  # Should truncate tech_rep
            rep_tech = rep_for_file(a_file)
            return rep_tech.split('_')[0]  # Should truncate tech_rep
        elif token == "{replicate_number}":
            rep_tag = a_file.get("rep_tag",a_file.get("rep_tech",rep_for_file(a_file)))
            if not rep_tag.startswith("rep"):
                return "0"
            return rep_tag[3:].split('_')[0]
        elif token == "{biological_replicate_number}":
            rep_tech = a_file.get("rep_tech",rep_for_file(a_file))
            if not rep_tech.startswith("rep"):
                return "0"
            return rep_tech[3:].split('_')[0]
        elif token == "{technical_replicate_number}":
            rep_tech = a_file.get("rep_tech",rep_for_file(a_file))
            if not rep_tech.startswith("rep"):
                return "0"
            return rep_tech.split('_')[1]
        elif token == "{rep_tech}":
            return a_file.get("rep_tech",rep_for_file(a_file))
        else:
            return ""
    else:
        log.warn('Untranslated token: "%s"' % token)
        return "unknown"

def convert_mask(mask,exp,a_file=None):
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
        term = lookup_token(working_on[beg_ix:end_ix+1],exp,a_file=a_file)
        new_mask = []
        if beg_ix > 0:
            new_mask = working_on[0:beg_ix]
        new_mask += "%s%s" % (term,working_on[end_ix+1:])
        chars = len(working_on[end_ix+1:])
        working_on = ''.join(new_mask)

    return working_on


def handle_negateValues(live_settings, defs, exp, composite):
    '''If negateValues is set then adjust some settings like color'''
    if live_settings.get("negateValues","off") == "off":
        return

    # need to swap color and altColor
    color = live_settings.get("color",composite.get("color"))
    if color is not None:
        altColor = live_settings.get("altColor",composite.get("altColor",color))
        live_settings["color"] = altColor
        live_settings["altColor"] = color

    # view limits need to change because numbers are all negative
    viewLimits = live_settings.get("viewLimits")
    if viewLimits is not None:
        low_high = viewLimits.split(':')
        if len(low_high) == 2:
            live_settings["viewLimits"] = "%d:%d" % (int(low_high[1]) * -1,int(low_high[0]) * -1)
    viewLimitsMax = live_settings.get("viewLimitsMax")
    if viewLimitsMax is not None:
        low_high = viewLimitsMax.split(':')
        if len(low_high) == 2:
            live_settings["viewLimitsMax"] = "%d:%d" % (int(low_high[1]) * -1,int(low_high[0]) * -1)

def generate_live_groups(composite,title,group_defs,exp,rep_tags=[]):
    '''Recursively populates live (in memory) groups from static group definitions'''
    live_group = {}
    tag = group_defs.get("tag",title)
    live_group = deepcopy(group_defs) # makes sure all miscellaneous settings are transferred
    live_group["title"] = title
    live_group["tag"] = tag
    if "group_order" in live_group:
        del live_group["group_order"]

    if title == "replicate": # transform replicates into unique tags and titles
        if len(rep_tags) == 0:  # Replicates need special work after files are examined, so just stub.
            return (tag, live_group)
        # Inclusion of rep_tags occurs after files have been examined.
        live_group["groups"] = {}
        rep_title_mask = group_defs.get("title_mask","Replicate_{replicate_number}")
        for rep_tag in rep_tags:
            rep_title = rep_title_mask
            if "combined_title" in group_defs and rep_tag in ["pool","combined"]:
                rep_title = group_defs["combined_title"]
            elif rep_title_mask.find('{replicate}') != -1:
                rep_title = rep_title_mask.replace('{replicate}',rep_tag)
            elif rep_title_mask.find('{replicate_number}') != -1:
                if rep_tag in ["pool","combined"]:
                    rep_title = rep_title_mask.replace('{replicate_number}',"0")
                else:
                    rep_title = rep_title_mask.replace('{replicate_number}',rep_tag[3:])
            live_group["groups"][rep_tag] = { "title": rep_title, "tag": rep_tag }
        live_group["preferred_order"] = "sorted"

    elif title in ["Biosample", "Targets"]: # Single subGroup at experiment level.  No order
        del live_group["groups"] # Make sure there is only a subgroup when the property is found.
        groups = group_defs.get("groups",{})
        assert(len(groups) == 1)
        for (group_key,group) in groups.items():
            mask = group.get("title_mask")
            if mask is not None:
                term = convert_mask(mask,exp)
                if not term.startswith('Unknown '):
                    term_tag = sanitize_tag(term)
                    term_title = term
                    live_group["groups"] = {}
                    live_group["groups"][term_tag] = { "title": term_title, "tag": term_tag }
        live_group["preferred_order"] = "sorted"
        # No tag order since only one

    # simple swapping tag and title and creating subgroups set with order
    else: # "Views", "Replicates", etc:
        # if there are subgroups, they can be handled by recursion
        if "groups" in group_defs:
            live_group["groups"]  = {}
            groups = group_defs["groups"]
            group_order = group_defs.get("group_order")
            preferred_order = []  # have to create preferred order based upon tags, not titles
            if group_order is None or not isinstance(group_order, list):
                group_order = sorted( groups.keys() )
                preferred_order = "sorted"
            tag_order = []
            for subgroup_title in group_order:
                subgroup = groups.get(subgroup_title,{})
                (subgroup_tag, subgroup) = generate_live_groups(composite,subgroup_title,subgroup,exp) #recursive
                subgroup["tag"] = subgroup_tag
                if isinstance(preferred_order,list):
                    preferred_order.append(subgroup_tag)
                if title == "Views":
                    add_living_color(subgroup, subgroup, exp)
                    handle_negateValues(subgroup, subgroup, exp, composite)
                live_group["groups"][subgroup_tag] = subgroup
                tag_order.append(subgroup_tag)
            live_group["group_order"] = tag_order
            live_group["preferred_order"] = preferred_order

    return (tag, live_group)

def insert_live_group(live_groups,new_tag,new_group):
    '''Inserts new group into a set of live groups during composite remodelling.'''
    old_groups = live_groups.get("groups",{})
    preferred_order = live_groups.get("preferred_order") # Note: all cases where group is dynamically added should be in sort order!
    if preferred_order is None or not isinstance(preferred_order,list):
        old_groups[new_tag] = new_group
        live_groups["groups"] = old_groups
        log.warn("Added %s to %s in sort order" % (new_tag,live_groups.get("tag","a group")))
        return live_groups

    # well we are going to have to generate s new order
    new_order = []
    old_order = live_groups.get("group_order",[])
    if old_order is None:
        old_order = sorted( old_groups.keys() )
    for preferred_tag in preferred_order:
        if preferred_tag == new_tag:
            new_order.append(new_tag)
        elif preferred_tag in old_order:
            new_order.append(preferred_tag)

    old_groups[new_tag] = new_group
    live_groups["groups"] = old_groups
    log.warn("Added %s to %s in preferred order" % (new_tag,live_groups.get("tag","a group")))
    return live_groups

def exp_composite_extend_with_tracks(composite, vis_defs, exp, assembly, host=None):
    '''Extends live experiment composite object with track definitions'''
    tracks = []
    rep_techs = {}
    files = []

    # first time through just to get rep_tech
    group_order = composite["view"].get("group_order",[])
    for view_tag in group_order:
        view = composite["view"]["groups"][view_tag]
        output_types = view.get("output_type",[])
        file_format_types = view.get("file_format_type",[])
        file_format = view["type"]
        for a_file in exp["files"]:
            if 'assembly' not in a_file or a_file['assembly'] != assembly:
                continue
            if file_format != a_file['file_format']:
                continue
            if len(output_types) > 0 and a_file.get('output_type','unknown') not in output_types:
                continue
            if len(file_format_types) > 0 and a_file.get('file_format_type','unknown') not in file_format_types:
                continue
            if "rep_tech" not in a_file:
                rep_tech = rep_for_file(a_file)
                a_file["rep_tech"] = rep_tech
            else:
                rep_tech = a_file["rep_tech"]
            rep_techs[rep_tech] = rep_tech
            files.append(a_file)
    if len(files) == 0:
        log.warn("No visualizable files for %s" % exp["accession"])
        return None

    # convert rep_techs to simple reps
    rep_ix = 1
    rep_tags = []
    for rep_tech in sorted( rep_techs.keys() ): # ordered by a simple sort
        if rep_tech == "combined":
            rep_tag = "pool"
        else:
            rep_tag = "rep%d" % rep_ix
            rep_ix += 1
        rep_techs[rep_tech] = rep_tag
        rep_tags.append(rep_tag)

    # Now we can fill in "Replicate" subgroups with with "replicate"
    other_groups = vis_defs.get("other_groups",[]).get("groups",[])
    if "Replicates" in other_groups:
        group = other_groups["Replicates"]
        group_tag = group["tag"]
        subgroups = group["groups"]
        if "replicate" in subgroups:
            (repgroup_tag, repgroup) = generate_live_groups(composite,"replicate",subgroups["replicate"],exp,rep_tags)
            # Now to hook them into the composite structure
            composite_rep_group = composite["groups"]["REP"]
            composite_rep_group["groups"] = repgroup.get("groups",{})
            composite_rep_group["group_order"] = repgroup.get("group_order",[])

    # second pass once all rep_techs are known
    if host is None:
        host = "https://www.encodeproject.org"
    for view_tag in composite["view"].get("group_order",[]):
        view = composite["view"]["groups"][view_tag]
        output_types = view.get("output_type",[])
        file_format_types = view.get("file_format_type",[])
        file_format = view["type"]
        for a_file in files:
            #if file_format != a_file['file_format']:
            if a_file['file_format'] not in [ file_format, "bed" ]:
                continue
            if len(output_types) > 0 and a_file.get('output_type','unknown') not in output_types:
                continue
            if len(file_format_types) > 0 and a_file.get('file_format_type','unknown') not in file_format_types:
                continue
            rep_tech = a_file["rep_tech"]
            rep_tag = rep_techs[rep_tech]
            a_file["rep_tag"] = rep_tag

            if "tracks" not in view:
                view["tracks"] = []
            track = {}
            #track["name"] = "%s_%s" % (exp['accession'][3:],a_file['accession'][3:]) # Trimming too cute?
            track["name"] = a_file['accession']
            track["type"] = view["type"]
            track["bigDataUrl"] = "%s?proxy=true" % a_file["href"]
            longLabel = vis_defs.get('file_defs',{}).get('longLabel')
            if longLabel is None:
                longLabel = "{assay_title} of {biosample_term_name} {output_type} {biological_replicate_number} {experiment.accession} - {file.accession}"
            track["longLabel"] = sanitize_label( convert_mask(longLabel,exp,a_file) )
            metadata_pairs = {}
            metadata_pairs['file&#32;download'] = '"<a href=\"%s%s\" title=\'Download this file from the ENCODE portal\'>%s</a>"' % (host,a_file["href"],a_file["accession"])
            metadata_pairs["experiment"] = '"<a href=\"%s/experiments/%s\" TARGET=\'encode\' title=\'Experiment details from the ENCODE portal\'>%s</a>"' % (host,exp["accession"],exp["accession"])

            # Expecting short label to change when making assay based composites
            shortLabel = vis_defs.get('file_defs',{}).get('shortLabel',"{replicate} {output_type_short_label}")
            track["shortLabel"] = sanitize_label( convert_mask(shortLabel,exp,a_file) )

            # How about subgroups!
            membership = {}
            membership["view"] = view["tag"]
            view["tracks"].append( track )  # <==== This is how we connect them to the views
            for (group_tag,group) in composite["groups"].items():
                # "Replicates", "Biosample", "Targets", ... member?
                group_title = group["title"]
                subgroups = group["groups"]
                if group_title == "Replicates":
                    # Must figure out membership
                    ### Generate rep_tag for track, then
                    subgroup = subgroups.get(rep_tag)
                    #if subgroup is None:
                    #    subgroup = { "tag": rep_tag, "title": rep_tag }
                    #    group["groups"][rep_tag] = subgroup
                    if subgroup is not None:
                        membership[group_tag] = rep_tag
                        if "tracks" not in subgroup:
                            subgroup["tracks"] = []
                        subgroup["tracks"].append( track )  # <==== also connected to replicate
                elif group_title in ["Biosample", "Targets"]:
                    assert(len(subgroups) == 1)
                    #if len(subgroups) == 1:
                    for (subgroup_tag,subgroup) in subgroups.items():
                        membership[group_tag] = subgroup["tag"]
                        metadata_pairs[group_title] = '"%s"' % (subgroup["title"])
                        #subgroups[0]["tracks"] = [ track ]
                else:
                    ### Help!
                    assert(group_tag == "Don't know this group!")

            track["membership"] = membership
            if len(metadata_pairs):
                track["metadata_pairs"] = metadata_pairs

            tracks.append(track)

    return tracks

def make_exp_composite(exp, assembly, host=None, hide=False):
    '''Converts experiment composite static definitions to live composite object'''
    vis_type = get_exp_vis_type(exp)
    vis_defs = lookup_vis_defs(vis_type)
    if vis_defs is None:
        return None
    composite = {}
    composite["vis_type"] = vis_type
    composite["name"] = exp["accession"]

    longLabel = vis_defs.get('longLabel','{assay_term_name} of {biosample_term_name} - {accession}')
    composite['longLabel'] = sanitize_label( convert_mask(longLabel,exp) )
    shortLabel = vis_defs.get('shortLabel','{accession}')
    composite['shortLabel'] = sanitize_label( convert_mask(shortLabel,exp) )
    if hide:
        composite["visibility"] = "hide"
    else:
        composite["visibility"] = vis_defs.get("visibility","full")
    composite['pennantIcon'] = vis_defs.get("pennantIcon", 'http://genome.cse.ucsc.edu/images/encodeThumbnail.jpg https://www.encodeproject.org/ "ENCODE: Encyclopedia of DNA Elements"')
    add_living_color(composite, vis_defs, exp)
    # views are always subGroup1
    composite["view"] = {}
    title_to_tag = {}
    if "Views" in vis_defs:
        ( tag, views ) = generate_live_groups(composite,"Views",vis_defs["Views"],exp)
        composite[tag] = views
        title_to_tag["Views"] = tag

    global SUPPORTED_SUBGROUPS
    if "other_groups" in vis_defs:
        groups = vis_defs["other_groups"].get("groups",{})
        new_dimensions = {}
        new_filters = {}
        composite["group_order"] = []
        composite["groups"] = {} # subgroups are defined by groups and group_order directly off of composite
        group_order = vis_defs["other_groups"].get("group_order")
        preferred_order = []  # have to create preferred order based upon tags, not titles
        if group_order is None or not isinstance(group_order,list):
            group_order = sorted( groups.keys() )
            preferred_order = "sorted"
        for subgroup_title in group_order: # Replicates, Targets, Biosamples
            if subgroup_title not in groups:
                continue
            assert(subgroup_title in SUPPORTED_SUBGROUPS)
            (subgroup_tag, subgroup) = generate_live_groups(composite,subgroup_title,groups[subgroup_title],exp)
            if isinstance(preferred_order,list):
                preferred_order.append(subgroup_tag)  # "Targets" will get in, even if there are no targets in exp
            if "groups" in subgroup and len(subgroup["groups"]) > 0: # This means "Targets" may not get in
                title_to_tag[subgroup_title] = subgroup_tag
                #subgroup["subgroup_ix"] = subgroup_ix # Only matters when printing out and remodelling requires not setting now
                composite["groups"][subgroup_tag] = subgroup
                composite["group_order"].append(subgroup_tag)
            if "dimensions" in vis_defs["other_groups"]: # "Targets" dimension will be included, whether there is a target group or not
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

    tracks = exp_composite_extend_with_tracks(composite, vis_defs, exp, assembly, host=host)
    if tracks is None or len(tracks) == 0:
        # Already warned about files log.warn("No tracks for %s" % exp["accession"])
        return None
    composite["tracks"] = tracks
    return composite

def ucsc_trackDb_composite_blob(composite,title):
    '''Given an in-memory composite object, prints a single UCSC trackDb.txt composite structure'''
    if composite is None or len(composite) == 0:
        return "# Empty composite for %s\n" % title

    blob = ""
    # First the composite structure
    blob += "track %s\n" % composite["name"]
    blob += "compositeTrack on\n"
    blob += "type bed 3\n"
    global COMPOSITE_SETTINGS
    for var in COMPOSITE_SETTINGS:
        val = composite.get(var)
        if val:
            blob += "%s %s\n" % (var, val)
    views = composite.get("view",[])
    if len(views) > 0:
        blob += "subGroup1 view %s" % views["title"]
        for view_tag in views["group_order"]:
            view_title = views["groups"][view_tag]["title"]
            blob += " %s=%s" % (view_tag,sanitize_title(view_title))
        blob += '\n'
    dimA_checked = composite.get("dimensionAchecked","all")
    dimA_tag = ""
    if dimA_checked == "first": # All will leave dimA_tag and dimA_checked empty, thus defaulting to all on
        dimA_tag = composite.get("dimensions",{}).get("dimA","")
    dimA_checked = None
    subgroup_ix = 2
    for group_tag in composite["group_order"]:
        group = composite["groups"][group_tag]
        blob += "subGroup%d %s %s" % (subgroup_ix, group_tag, sanitize_title(group["title"]))
        subgroup_ix += 1
        subgroup_order = None # group.get("group_order")
        if subgroup_order is None or not isinstance(subgroup_order,list):
            subgroup_order = sorted( group["groups"].keys() )
        for subgroup_tag in subgroup_order:
            subgroup_title = group["groups"][subgroup_tag]["title"]
            blob += " %s=%s" % (subgroup_tag,sanitize_title(subgroup_title))
            if group_tag == dimA_tag and dimA_checked is None:
                dimA_checked = subgroup_tag

        blob += '\n'
    # sortOrder
    sort_order = composite.get("sortOrder")
    if sort_order:
        blob += "sortOrder"
        for sort_tag in sort_order:
            blob += " %s=+" % sort_tag
        blob += '\n'
    # dimensions
    actual_group_tags = [ "view" ] # Not all groups will be used in composite, depending upon subgroup content
    dimensions = composite.get("dimensions")
    if dimensions:
        pairs = ""
        for dim_tag in sorted( dimensions.keys() ):
            group = composite["groups"].get(dimensions[dim_tag])
            if group is None: # e.g. "Targets" may not exist
                continue
            #if len(group.get("groups",{})) <= 1: # TODO get hui.js line 262 fixed!  If matXY.length == 0 then need to call subCBs.each( function (i) { matSubCBcheckOne(this,state); });
            #    continue
            pairs += " %s=%s" % (dim_tag, dimensions[dim_tag])
            actual_group_tags.append(dimensions[dim_tag])
        if len(pairs) > 0:
            blob += "dimensions%s\n" % pairs
    # filterComposite
    filter_composite = composite.get("filterComposite")
    if filter_composite:
        filterfish = ""
        for filter_tag in sorted( filter_composite.keys() ):
            group = composite["groups"].get(filter_composite[filter_tag])
            if group is None and len(group.get("groups",{})) <= 1: # e.g. "Targets" may not exist
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
    global VIEW_SETTINGS
    global TRACK_SETTINGS
    for view_tag in views["group_order"]:
        view = views["groups"][view_tag]
        tracks = view.get("tracks",[])
        if len(tracks) == 0:
            continue
        blob += "    track %s_%s_view\n" % (composite["name"],view["tag"])
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
            blob += "        parent %s_%s_view" % (composite["name"],view["tag"])
            dimA_subgroup = track.get("membership",{}).get(dimA_tag)
            if dimA_subgroup is not None and dimA_subgroup != dimA_checked:
                blob += " off\n"
            else:
                blob += " %s\n" % track.get("checked","on") # Can set individual tracks off. Used when remodelling
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
                for member_tag in membership:
                    if member_tag in actual_group_tags: # TODO: remove when it is proved to be not needed.
                        blob += " %s=%s" % (member_tag,membership[member_tag])
                blob += '\n'
            # metadata line?
            metadata_pairs = track.get("metadata_pairs")
            if metadata_pairs is not None:
                metadata_line = ""
                for meta_tag in metadata_pairs.keys():
                    metadata_line += ' %s=%s' % (meta_tag.lower(),metadata_pairs[meta_tag])
                if len(metadata_line) > 0:
                    blob += "        metadata%s\n" % metadata_line

            blob += '\n'
    blob += '\n'
    return blob

def remodel_exp_to_assay_composites(exp_composites,hide_after=None):
    '''Given a set of (search result) exp based composites, remodel them to assay based composites.'''
    if exp_composites is None or len(exp_composites) == 0:
        return {}

    assay_composites = {}

    for accession in sorted( exp_composites.keys() ):
        exp_composite = exp_composites[accession]
        if exp_composite is None or len(exp_composite) == 0: # wounded composite can be dropped or added for evidence
            assay_composites[acc] = exp_composite

        # Only show the first n experiments
        if hide_after != None:
            if hide_after <= 0:
                for track in exp_composite.get("tracks",{}):
                    track["checked"] = "off"
            else:
                hide_after -= 1

        # color must move to tracks becuse it is likely biosample based and we are likely mixing biosample exps
        exp_color = exp_composite.get("color")
        exp_altColor = exp_composite.get("altColor")
        exp_view_groups = exp_composite.get("view",{}).get("groups",{})
        for (view_tag,exp_view) in exp_view_groups.items():
            exp_view_color = exp_view.get("color",exp_color)
            exp_view_altColor = exp_view.get("altColor",exp_altColor)
            if exp_view_color is None and exp_view_altColor is None:
                continue
            for track in exp_view.get("tracks",[]):
                if "color" not in track.keys():
                    if exp_view_color is not None:
                        track["color"] = exp_view_color
                    if exp_view_altColor is not None:
                        track["altColor"] = exp_view_altColor

        # If assay_composite of this vis_type doesn't exist, create it
        vis_type = exp_composite["vis_type"]
        vis_defs = lookup_vis_defs(vis_type)
        assert(vis_type is not None)
        if vis_type not in assay_composites.keys():  # First one so just drop in place
            log.warn("Remodelling %s into %s composite" % (exp_composite.get("name"," a composite"),vis_type))
            assay_composite = exp_composite # Don't bother with deep copy... we aren't needing the exp_composites any more
            assay_defs = vis_defs.get("assay_composite",{})
            assay_composite["name"] = vis_type.lower()  # TODO: something more elegant?
            for tag in ["longLabel","shortLabel","visibility"]:
                if tag in assay_defs:
                    assay_composite[tag] = assay_defs[tag] # Not expecting any token substitutions!!!
            assay_composites[vis_type] = assay_composite

        else: # Adding an exp_composite to an existing assay_composite
            log.warn("Adding %s into %s composite" % (exp_composite.get("name"," a composite"),vis_type))
            assay_composite = assay_composites[vis_type]

            # combine views
            assay_views = assay_composite.get("view",[])
            exp_views = exp_composite.get("view",{})
            for view_tag in exp_views["group_order"]:
                exp_view = exp_views["groups"][view_tag]
                if view_tag not in assay_views["groups"].keys():  # Should never happen
                    log.warn("Surprise: view %s not found before" % view_tag)
                    insert_live_group(assay_views,view_tag,exp_view)
                else: # View is already defined but tracks need to be appended.
                    assay_view = assay_views["groups"][view_tag]
                    if "tracks" not in assay_view:
                        assay_view["tracks"] = exp_view.get("tracks",[])
                    else:
                        assay_view["tracks"].extend(exp_view.get("tracks",[]))

            # All tracks in one set: not needed.

            # Combine subgroups:
            for group_tag in exp_composite["group_order"]:
                exp_group = exp_composite["groups"][group_tag]
                if group_tag not in assay_composite["groups"].keys(): # Should never happen
                    log.warn("Surprise: group %s not found before" % group_tag)
                    insert_live_group(assay_composite,group_tag,exp_group)
                else: # Need to handle subgroups which definitely may not be there.
                    assay_group = assay_composite["groups"].get(group_tag,{})
                    exp_subgroups = exp_group.get("groups",{})
                    exp_subgroup_order = exp_group.get("group_order")
                    for subgroup_tag in exp_subgroups.keys():
                        if subgroup_tag not in assay_group.get("groups",{}).keys():
                            insert_live_group(assay_group,subgroup_tag,exp_subgroups[subgroup_tag]) # Adding biosamples, targets, and reps

            # dimensions and filterComposite should not need any extra care: they get dynamically scaled down during printing

    return assay_composites

def generate_trackDb(experiment, assembly, host=None, hide=False):

    ### local test: bigBed: curl http://localhost:8000/experiments/ENCSR000DZQ/@@hub/hg19/trackDb.txt
    ###             bigWig: curl http://localhost:8000/experiments/ENCSR000ADH/@@hub/mm9/trackDb.txt
    ### CHIP: https://4217-trackhub-spa-ab9cd63-tdreszer.demo.encodedcc.org/experiments/ENCSR645BCH/@@hub/GRCh38/trackDb.txt
    ### LRNA: curl https://4217-trackhub-spa-ab9cd63-tdreszer.demo.encodedcc.org/experiments/ENCSR000AAA/@@hub/GRCh38/trackDb.txt

    # Find the right defs
    exp_composite = make_exp_composite(experiment, assembly, host=host, hide=hide)

    ###return json.dumps(exp_composite,indent=4) + '\n'

    return ucsc_trackDb_composite_blob(exp_composite,experiment['accession'])


def generate_batch_trackDb(results, assembly, host=None):

    ### local test: RNA-seq: curl https://4217-trackhub-spa-ab9cd63-tdreszer.demo.encodedcc.org/batch_hub/type=Experiment,,assay_title=RNA-seq,,award.rfa=ENCODE3,,status=released,,assembly=GRCh38,,replicates.library.biosample.biosample_type=induced+pluripotent+stem+cell+line/GRCh38/trackDb.txt

    exp_composites = {}
    for (i, experiment) in enumerate(results):
        if i < 5:
            exp_composite = make_exp_composite(experiment, assembly, host=host)
        else:
            exp_composite = make_exp_composite(experiment, assembly, host=host, hide=True)
        if exp_composite is not None:
            exp_composites[experiment['accession']] = exp_composite

    assay_composites = remodel_exp_to_assay_composites(exp_composites,hide_after=5)

    blob = ""
    for composite_tag in sorted( assay_composites.keys() ):
        blob += ucsc_trackDb_composite_blob(assay_composites[composite_tag],composite_tag)

    return blob


def render(data):
    arr = []
    for i in range(len(data)):
        temp = list(data.popitem())
        str1 = ' '.join(temp)
        arr.append(str1)
    return arr


def get_genomes_txt(assembly):
    # UCSC shim
    ucsc_assembly = _ASSEMBLY_MAPPER.get(assembly, assembly)
    genome = OrderedDict([
        ('trackDb', assembly + '/trackDb.txt'),
        ('genome', ucsc_assembly)
    ])
    return render(genome)


def get_hub(label,comment=None,name=None):
    if name is None:
        name = sanitize_name( label.split()[0] )
    if comment is None:
        comment = "Generated by the ENCODE portal"
    hub = OrderedDict([
        ('email', 'encode-help@lists.stanford.edu'),
        ('genomesFile', 'genomes.txt'),
        ('longLabel', 'ENCODE Data Coordination Center Data Hub'),
        ('shortLabel', 'Hub (' + label + ')'),
        ('hub', 'ENCODE_DCC_' + name ),
        ('#', comment )
    ])
    return render(hub)

def generate_html(context, request):
    ''' Generates and returns HTML for the track hub'''

    url_ret = (request.url).split('@@hub')
    embedded = {}
    if url_ret[0] == request.url:
        item = request.root.__getitem__((request.url.split('/')[-1])[:-5])
        embedded = request.embed(request.resource_path(item))
    else:
        embedded = request.embed(request.resource_path(context))
    link = request.host_url + '/experiments/' + embedded['accession']
    files_json = embedded.get('files', None)
    data_accession = '<a href={link}>{accession}<a></p>' \
        .format(link=link, accession=embedded['accession'])
    data_description = '<h2>{description}</h2>' \
        .format(description=cgi.escape(embedded['description']))
    data_files = ''
    for f in files_json:
        if f['file_format'] in BIGBED_FILE_TYPES + BIGWIG_FILE_TYPES:
            replicate_number = 'rep unknown'
            if len(f['biological_replicates']) == 1:
                replicate_number = str(f['biological_replicates'][0])
            elif len(f['biological_replicates']) > 1:
                replicate_number = 'pooled from reps {reps}'.format(
                    reps=str(f['biological_replicates'])
                )
            data_files = data_files + \
                '<tr><td>{title}</batch_hub/type%3Dexperiment/hub.txt/td><td>{file_type}</td><td>{output_type}</td><td>{replicate_number}</td><td><a href="{request.host_url}{href}">Click here</a></td></tr>'\
                .format(replicate_number=replicate_number, request=request, **f)

    file_table = '<table><tr><th>Accession</th><th>File type</th><th>Output type</th><th>Biological replicate</th><th>Download link</th></tr>{files}</table>' \
        .format(files=data_files)
    header = '<p>This trackhub was automatically generated from the files and metadata for the experiment - ' + \
        data_accession
    return data_description + header + file_table


def generate_batch_hubs(context, request):
    '''search for the input params and return the trackhub'''

    results = {}
    txt = request.matchdict['txt']
    param_list = parse_qs(request.matchdict['search_params'].replace(',,', '&'))

    view = 'search'
    if 'region' in param_list:
        view = 'region-search'

    if len(request.matchdict) == 3:

        # Should generate a HTML page for requests other than trackDb.txt
        if txt != TRACKDB_TXT:
            data_policy = '<br /><a href="http://encodeproject.org/ENCODE/terms.html">ENCODE data use policy</p>'
            return generate_html(context, request) + data_policy

        assembly = str(request.matchdict['assembly'])
        params = {
            'files.file_format': BIGBED_FILE_TYPES + BIGWIG_FILE_TYPES,
            'status': ['released'],
        }
        params.update(param_list)
        params.update({
            'assembly': [assembly],
            'limit': ['all'],
            'frame': ['embedded'],
        })
        path = '/%s/?%s' % (view, urlencode(params, True))
        results = request.embed(path, as_user=True)['@graph']
        # if files.file_format is a input param
        if 'files.file_format' in param_list:
            results = [
                result
                for result in results
                if any(
                    f['file_format'] in BIGWIG_FILE_TYPES + BIGBED_FILE_TYPES
                    for f in result.get('files', [])
                )
            ]
        trackdb = ''
        return generate_batch_trackDb(results, assembly,host=request.host_url)

    elif txt == HUB_TXT:
        terms = request.matchdict['search_params'].replace(',,', '&')
        pairs = terms.split('&')
        label = "search:"
        for pair in sorted( pairs ):
            (var,val) = pair.split('=')
            if var not in ["type","assembly","status","limit"]:
                label += " %s" % val.replace('+',' ')
        return NEWLINE.join(get_hub(label,request.url)) # TODO: Decide if this is acceptible
        #return NEWLINE.join(get_hub('search'))
    elif txt == GENOMES_TXT:
        path = '/%s/?%s' % (view, urlencode(param_list, True))
        results = request.embed(path, as_user=True)
        g_text = ''
        if 'assembly' in param_list:
            for assembly in param_list.get('assembly'):
                if g_text == '':
                    g_text = NEWLINE.join(get_genomes_txt(assembly))
                else:
                    g_text = g_text + 2 * NEWLINE + NEWLINE.join(get_genomes_txt(assembly))
        else:
            for facet in results['facets']:
                if facet['field'] == 'assembly':
                    for term in facet['terms']:
                        if term['doc_count'] != 0:
                            if g_text == '':
                                g_text = NEWLINE.join(get_genomes_txt(term['key']))
                            else:
                                g_text = g_text + 2 * NEWLINE + NEWLINE.join(get_genomes_txt(term['key']))
        return g_text


@view_config(name='hub', context=Item, request_method='GET', permission='view')
def hub(context, request):
    ''' Creates trackhub on fly for a given experiment '''

    url_ret = (request.url).split('@@hub')
    embedded = request.embed(request.resource_path(context))

    assemblies = ''
    if 'assembly' in embedded:
        assemblies = embedded['assembly']

    if url_ret[1][1:] == HUB_TXT:
        label = "%s %s" % (embedded.get("assay_title",""), embedded['accession'])
        name = sanitize_name( label )
        return Response(
            NEWLINE.join(get_hub(label,request.url, name )),
            content_type='text/plain'
        )
    elif url_ret[1][1:] == GENOMES_TXT:
        g_text = ''
        for assembly in assemblies:
            if g_text == '':
                g_text = NEWLINE.join(get_genomes_txt(assembly))
            else:
                g_text = g_text + 2 * NEWLINE + NEWLINE.join(get_genomes_txt(assembly))
        return Response(g_text, content_type='text/plain')
    elif url_ret[1][1:].endswith(TRACKDB_TXT):
        parent_track = generate_trackDb(embedded, url_ret[1][1:].split('/')[0],host=request.host_url)
        return Response(parent_track, content_type='text/plain')
    else:
        data_policy = '<br /><a href="http://encodeproject.org/ENCODE/terms.html">ENCODE data use policy</p>'
        return Response(generate_html(context, request) + data_policy, content_type='text/html')


@view_config(route_name='batch_hub')
@view_config(route_name='batch_hub:trackdb')
def batch_hub(context, request):
    ''' View for batch track hubs '''
    return Response(generate_batch_hubs(context, request), content_type='text/plain')
