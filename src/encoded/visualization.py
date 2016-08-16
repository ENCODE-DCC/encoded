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
from snovault.elasticsearch.interfaces import ELASTIC_SEARCH
import time

import logging
from .search import _ASSEMBLY_MAPPER

log = logging.getLogger(__name__)

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

INVISIBLE_FILE_STATUSES = ["revoked", "replaced", "deleted", "archived" ]

# ASSEMBLY_MAPPINGS is needed to ensure that mm10 and mm10-minimal will get combined into the same trackHub.txt
# This is necessary because mm10 and mm10-minimal are only mm10 at UCSC, so the 2 must be collapsed into one.
ASSEMBLY_MAPPINGS = {
    # any term:       [ set of encoded terms used ]
    "GRCh38":           [ "GRCh38", "GRCh38-minimal" ],
    "GRCh38-minimal":   [ "GRCh38", "GRCh38-minimal" ],
    "hg38":             [ "GRCh38", "GRCh38-minimal" ],
    "GRCh37":           [ "hg19", "GRCh37" ],  # Is GRCh37 ever in encoded?
    "hg19":             [ "hg19", "GRCh37" ],
    "GRCm38":           [ "mm10", "mm10-minimal", "GRCm38" ],  # Is GRCm38 ever in encoded?
    "mm10":             [ "mm10", "mm10-minimal", "GRCm38" ],
    "mm10-minimal":     [ "mm10", "mm10-minimal", "GRCm38" ],
    "GRCm37":           [ "mm9", "GRCm37" ],  # Is GRCm37 ever in encoded?
    "mm9":              [ "mm9", "GRCm37" ],
    "BDGP6":            [ "dm4", "BDGP6" ],
    "dm4":              [ "dm4", "BDGP6" ],
    "BDGP5":            [ "dm3", "BDGP5" ],
    "dm3":              [ "dm3", "BDGP5" ],
    #"WBcel235":         [ "WBcel235" ], # defaults to term: [ term ]
    }


# Supported tokens are the only tokens the code currently know how to look up and swap into text stings.
SUPPORTED_MASK_TOKENS = [
    "{replicate}",         # The replicate that that will be displayed for visualized track: ("rep1", "combined") (AKA rep_tag)
    "{rep_tech}",          # The rep_tech if desired ("rep1_1", "combined")
    "{replicate_number}",  # The replicate number displayed for visualized track: ("1", "0")
    "{biological_replicate_number}",
    "{technical_replicate_number}",
    "{assay_title}",
    "{assay_term_name}",                    # dataset.assay_term_name
    "{annotation_type}",                    # some datasets have annotation type and not assay (higher end trickery)
    "{output_type}",                        # files.output_type
    "{accession}","{experiment.accession}", # "{accession}" is assumed to be experiment.accession
    "{file.accession}",
    "{target}","{target.label}",            # Either is acceptible
    "{target.title}",
    "{target.name}",                        # Used in metadata URLs
    "{biosample_term_name}","{biosample_term_name|multiple}",  # "|multiple": none means multiple
    "{output_type_short_label}",                # hard-coded translation from output_type to very short version Do we want this in schema?
    "{replicates.library.biosample.summary}",   # Idan and Forrest and Cricket are conspiring to move this to dataset.biosample_summary and make it much shorter
    "{replicates.library.biosample.summary|multiple}",   # "|multiple": none means multiple
    "{assembly}",                               # you don't need this in titles, but it is crucial variable and seems to not be being applied correctly in the html generation
    # TODO "{software? or pipeline?}",          # Cricket: "I am stumbling over the fact that we can't distinguish tophat and star produced files"
    # TODO "{phase}",                           # Cricket: "If we get to the point of being fancy in the replication timing, then we need this, otherwise it bundles up in the biosample summary now"
    ]

# Simple tokens are a straight lookup, no questions asked
SIMPLE_DATASET_TOKENS = ["{biosample_term_name}","{accession}","{assay_title}","{assay_term_name}", "{annotation_type}"]

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
        "dimensionAchecked": "first", # or "all"
        "groups": {
            "Replicates": {
                "tag": "REP",
                "groups": {
                    "replicate": {
                        "title_mask": "Replicate_{replicate_number}",
                        "combined_title": "Pooled",
                    },
                },
            },
            "Biosample": {
                "tag": "BS",
                "groups": { "one": { "title_mask": "{biosample_term_name}" } },
            },
            "Targets": {
                "tag": "TARG",
                "groups": { "one": { "title_mask": "{target.label}", "url_mask": "targets/{target.name}" } },
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
    "sortOrder": [ "Biosample", "Targets", "Replicates", "Views" ],
    "Views": {
        "tag": "view",
        "group_order": [ "Signal of unique reads", "Signal of all reads",
                        "Plus signal of unique reads", "Minus signal of unique reads",
                        "Plus signal of all reads", "Minus signal of all reads" ],
        "groups": {
            "Signal of unique reads": {
                "tag": "SIGBL",
                "visibility": "full",
                "type": "bigWig",
                "viewLimits": "0:1",
                "transformFunc": "LOG",
                "autoScale": "off",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "signal of unique reads" ]
            },
            "Signal of all reads": {
                "tag": "SIGBM",
                "visibility": "hide",
                "type": "bigWig",
                "viewLimits": "0:1",
                "transformFunc": "LOG",
                "autoScale": "off",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "signal of all reads" ]
            },
            "Minus signal of unique reads": {
                "tag": "SIGLR",
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
            "Plus signal of unique reads": {
                "tag": "SIGLF",
                "visibility": "full",
                "type": "bigWig",
                "viewLimits": "0:1",
                "transformFunc": "LOG",
                "autoScale": "off",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "plus strand signal of unique reads" ]
            },
            "Plus signal of all reads": {
                "tag": "SIGMF",
                "visibility": "hide",
                "type": "bigWig",
                "viewLimits": "0:1",
                "transformFunc": "LOG",
                "autoScale": "off",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "plus strand signal of all reads" ]
            },
            "Minus signal of all reads": {
                "tag": "SIGMR",
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
        },
    },
    "other_groups": {
        "dimensions": { "Biosample": "dimY", "Targets": "dimX", "Replicates": "dimA" },
        "dimensionAchecked": "first", # or "all"
        "groups": {
            "Replicates": {
                "tag": "REP",
                "groups": {
                "replicate": {
                    "title_mask": "Replicate_{replicate_number}",
                    #"combined_title": "Pooled", # "Combined"
                    }
                },
            },
            "Biosample": {
                "tag": "BS",
                "groups": { "one": { "title_mask": "{biosample_term_name}"} }
            },
            "Targets": {
                "tag": "TARG",
                "groups": { "one": { "title_mask": "{target.label}", "url_mask": "targets/{target.name}" } },
            },
        }
    },
    "file_defs": {
        "longLabel": "{assay_title} of {biosample_term_name} {output_type} {replicate} {experiment.accession} - {file.accession}",
        "shortLabel": "{replicate} {output_type_short_label}",
    }
}

TKRNA_COMPOSITE_VIS_DEFS = {
    "assay_composite": {
        "longLabel":  "Collection of ENCODE targeted knockdowns RNA-seq experiments",
        "shortLabel": "ENCODE knockdown RNA-seq",
    },
    "longLabel":  "{assay_title} of {replicates.library.biosample.summary} - {accession}",
    "shortLabel": "{assay_title} of {biosample_term_name} {accession}",
    "sortOrder": [ "Biosample", "Targets", "Replicates",  "Assay", "Views" ],
    "Views": {
        "tag": "view",
        "group_order": [ "Signal of unique reads", "Signal of all reads", "Plus signal of unique reads", "Minus signal of unique reads", "Plus signal of all reads", "Minus signal of all reads", ],
        "groups": {
            "Signal of unique reads": {
                "tag": "SIGBL",
                "visibility": "full",
                "type": "bigWig",
                "viewLimits": "0:1",
                "transformFunc": "LOG",
                "autoScale": "off",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "signal of unique reads" ]
            },
            "Signal of all reads": {
                "tag": "SIGBM",
                "visibility": "hide",
                "type": "bigWig",
                "viewLimits": "0:1",
                "transformFunc": "LOG",
                "autoScale": "off",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "signal of all reads" ]
            },
            "Plus signal of unique reads": {
                "tag": "SIGLF",
                "visibility": "full",
                "type": "bigWig",
                "viewLimits": "0:1",
                "transformFunc": "LOG",
                "autoScale": "off",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "plus strand signal of unique reads" ]
            },
            "Minus signal of unique reads": {
                "tag": "SIGLR",
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
            "Plus signal of all reads": {
                "tag": "SIGMF",
                "visibility": "hide",
                "type": "bigWig",
                "viewLimits": "0:1",
                "transformFunc": "LOG",
                "autoScale": "off",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "plus strand signal of all reads" ]
            },
            "Minus signal of all reads": {
                "tag": "SIGMR",
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
                    "combined_title": "Pooled", # "Combined"
                    }
                },
            },
            "Biosample": {
                "tag": "BS",
                "groups": { "one": { "title_mask": "{biosample_term_name}"} }
            },
            "Targets": {
                "tag": "TARG",
                "groups": { "one": { "title_mask": "{target.label}" } },
            },
            "Assay": {
                "tag": "Assay",
                "groups": { "one": { "title_mask": "{target.title}" } },
            },
        }
    },
    "file_defs": {
        "longLabel": "{assay_title} of {biosample_term_name} {output_type} {replicate} {experiment.accession} - {file.accession}",
        "shortLabel": "{replicate} {output_type_short_label}",
    }
}

SRNA_COMPOSITE_VIS_DEFS = {
    "assay_composite": {
        "longLabel":  "Collection of ENCODE small-RNA-seq experiments",
        "shortLabel": "ENCODE small-RNA-seq",
    },
    "longLabel":  "{assay_title} of {replicates.library.biosample.summary} - {accession}",
    "shortLabel": "{assay_title} of {biosample_term_name} {accession}",
    "sortOrder": [ "Biosample", "Targets", "Replicates", "Views" ],
    "Views": {
        "tag": "view",
        "group_order": [ "Plus signal of unique reads", "Minus signal of unique reads", "Plus signal of all reads", "Minus signal of all reads", ],
        "groups": {
            "Minus signal of unique reads": {
                "tag": "SIGLR",
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
            "Plus signal of unique reads": {
                "tag": "SIGLF",
                "visibility": "full",
                "type": "bigWig",
                "viewLimits": "0:1",
                "transformFunc": "LOG",
                "autoScale": "off",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "plus strand signal of unique reads" ]
            },
            "Plus signal of all reads": {
                "tag": "SIGMF",
                "visibility": "hide",
                "type": "bigWig",
                "viewLimits": "0:1",
                "transformFunc": "LOG",
                "autoScale": "off",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "plus strand signal of all reads" ]
            },
            "Minus signal of all reads": {
                "tag": "SIGMR",
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
        },
    },
    "other_groups": {
        "dimensions": { "Biosample": "dimY", "Replicates": "dimA" },
        "dimensionAchecked": "first", # or "all"
        "groups": {
            "Replicates": {
                "tag": "REP",
                "groups": {
                "replicate": {
                    "title_mask": "Replicate_{replicate_number}", # Optional
                    #"combined_title": "Pooled", # "Combined"
                    }
                },
            },
            "Biosample": {
                "tag": "BS",
                "groups": { "one": { "title_mask": "{biosample_term_name}"} }
            },
        }
    },
    "file_defs": {
        "longLabel": "{assay_title} of {biosample_term_name} {output_type} {replicate} {experiment.accession} - {file.accession}",
        "shortLabel": "{replicate} {output_type_short_label}",
    }
}

RAMPAGE_COMPOSITE_VIS_DEFS = {
    "assay_composite": {
        "longLabel":  "Collection of ENCODE Rampage/CAGE experiments",
        "shortLabel": "ENCODE Rampage/CAGE",
    },
    "longLabel":  "{assay_title} of {replicates.library.biosample.summary} - {accession}",
    "shortLabel": "{assay_title} of {biosample_term_name} - {accession}",
    "sortOrder": [ "Biosample", "Targets", "Replicates", "Views" ],
    "Views":  {
        "tag": "view",
        "group_order": [ "Replicated TSSs", "TSSs",
                         "Signal of unique reads", "Signal of all reads",
                         "Plus signal of unique reads", "Minus signal of unique reads",
                         "Plus signal of all reads", "Minus signal of all reads" ],
        "groups": {
          "Replicated TSSs": {
                "tag": "ARTSS",
                "visibility": "dense",
                "spectrum": "on",
                "type": "bigBed",
                "file_format_type": ["idr_peak"],
           },
          "TSSs": {
                "tag": "AZTSS",
                "visibility": "hide",
                "spectrum": "on",
                "type": "bigBed",
                "file_format_type": ["tss_peak"],
            },
            "Signal of unique reads": {
                "tag": "SIGBL",
                "visibility": "full",
                "type": "bigWig",
                "viewLimits": "0:1",
                "autoScale": "off",
                "maxHeightPixels": "32:16:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "signal of unique reads" ]
            },
            "Signal of all reads": {
                "tag": "SIGBM",
                "visibility": "hide",
                "type": "bigWig",
                "viewLimits": "0:1",
                "autoScale": "off",
                "maxHeightPixels": "32:16:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "signal of all reads" ]
            },
            "Plus signal of unique reads": {
                "tag": "SIGLF",
                "visibility": "full",
                "type": "bigWig",
                "viewLimits": "0:1",
                "autoScale": "off",
                "maxHeightPixels": "32:16:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "plus strand signal of unique reads" ]
            },
            "Minus signal of unique reads": {
                "tag": "SIGLR",
                "visibility": "full",
                "type": "bigWig",
                "viewLimits": "0:1",
                "autoScale": "off",
                "negateValues": "on",
                "maxHeightPixels": "32:16:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "minus strand signal of unique reads" ]
            },
            "Plus signal of all reads": {
                "tag": "SIGMF",
                "visibility": "hide",
                "type": "bigWig",
                "viewLimits": "0:1",
                "autoScale": "off",
                "maxHeightPixels": "32:16:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "plus strand signal of all reads" ]
            },
            "Minus signal of all reads": {
                "tag": "SIGMR",
                "visibility": "hide",
                "type": "bigWig",
                "viewLimits": "0:1",
                "autoScale": "off",
                "negateValues": "on",
                "maxHeightPixels": "32:16:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "minus strand signal of all reads" ]
            },
        }
    },
    "other_groups":  {
        "dimensions": { "Biosample": "dimY", "Replicates": "dimA" },
        "groups": {
            "Replicates": {
                "tag": "REP",
                "groups": {
                    "replicate": {
                        "title_mask": "Replicate_{replicate_number}",
                        "combined_title": "Pooled",
                    }
                },
            },
            "Biosample": {
                "tag": "BS",
                "groups": { "one": { "title_mask": "{biosample_term_name}"} }
            },
        }
    },
    "file_defs": {
        "longLabel": "{assay_title} of {biosample_term_name} {output_type} {replicate} {experiment.accession} - {file.accession}",
        "shortLabel": "{replicate} {output_type_short_label}",
    }
}

MICRORNA_COMPOSITE_VIS_DEFS = {
    "assay_composite": {
        "longLabel":  "Collection of ENCODE microRNA experiments",
        "shortLabel": "ENCODE microRNA",
    },
    "longLabel":  "{assay_title} of {replicates.library.biosample.summary} - {accession}",
    "shortLabel": "{assay_title} of {biosample_term_name} {accession}",
    "sortOrder": [ "Biosample", "Replicates", "Views", "Assay" ],
    "Views": {
        "tag": "view",
        "group_order": [ "microRNA quantifications", "Plus signal of unique reads", "Minus signal of unique reads", "Plus signal of all reads" ,  "Minus signal of all reads"],
        "groups": {
            "microRNA quantifications": {
                "tag": "QUANT",
                "visibility": "dense",
                "type": "bigBed",
                "useScore": "0",
                "output_type": [ "microRNA quantifications" ]
            },
            "Plus signal of unique reads": {
                "tag": "SIGLF",
                "visibility": "full",
                "type": "bigWig",
                "viewLimits": "0:1",
                "transformFunc": "LOG",
                "autoScale": "off",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "plus strand signal of unique reads" ]
            },
            "Minus signal of unique reads": {
                "tag": "SIGLR",
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
            "Plus signal of all reads": {
                "tag": "SIGMF",
                "visibility": "hide",
                "type": "bigWig",
                "viewLimits": "0:1",
                "transformFunc": "LOG",
                "autoScale": "off",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "plus strand signal of all reads" ]
            },
            "Minus signal of all reads": {
                "tag": "SIGMR",
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
        },
    },
    "other_groups": {
        "dimensions": { "Biosample": "dimY", "Assay": "dimX", "Replicates": "dimA" },
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
                "groups": { "one": { "title_mask": "{biosample_term_name}"} }
            },
            "Assay": {
                "tag": "ASSAY",
                "group_order": {"microRNA counts", "microRNA-seq"},
                "groups": { "one": { "title_mask": "{assay_term_name}" } },
            },
        }
    },
    "file_defs": {
        "longLabel": "{assay_title} of {biosample_term_name} {output_type} {replicate} {experiment.accession} - {file.accession}",
        "shortLabel": "{replicate} {output_type_short_label}",
    }
}

DNASE_COMPOSITE_VIS_DEFS = {
    "assay_composite": {
        "longLabel":  "Collection of ENCODE DNase-HS experiments",
        "shortLabel": "ENCODE DNase-HS",
    },
    "longLabel":  "{assay_title} of {replicates.library.biosample.summary} - {accession}",
    "shortLabel": "{assay_title} of {biosample_term_name} {accession}",
    "sortOrder": [ "Biosample", "Targets", "Replicates", "Views" ],
    "Views":  {
        "tag": "view",
        "group_order": [ "Signal", "Peaks", "Hotspots" ],
        "groups": {
            "Signal": {
                "tag": "aSIG",
                "visibility": "full",
                "type": "bigWig",
                "viewLimits": "0:1",
                "autoScale": "off",
                "maxHeightPixels": "32:16:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "signal of unique reads" ]
            },
            "Peaks": {
                "tag": "bPKS",
                "visibility": "hide",
                "type": "bigBed",
                "spectrum": "on",
                "scoreFilter": "100",
                "output_type": [ "peaks" ]
            },
            "Hotspots": {
                "tag": "cHOT",
                "visibility": "hide",
                "type": "bigBed",
                "spectrum": "on",
                "output_type": [ "hotspots" ]
            },
        },
    },
    "other_groups":  {
        "dimensions": { "Biosample": "dimY", "Replicates": "dimA" },
        "groups": {
            "Replicates": {
                "tag": "REP",
                "groups": {
                    "replicate": {
                        "title_mask": "Replicate_{replicate_number}",
                        "combined_title": "Pooled",
                    }
                },
            },
            "Biosample": {
                "tag": "BS",
                "groups": { "one": { "title_mask": "{biosample_term_name}"} }
            },
        }
    },
    "file_defs": {
        "longLabel": "{assay_title} of {biosample_term_name} {output_type} {replicate} {experiment.accession} - {file.accession}",
        "shortLabel": "{replicate} {output_type_short_label}",
    }
}

WGBS_COMPOSITE_VIS_DEFS = {
    "assay_composite": {
        "longLabel":  "Collection of ENCODE WGBS experiments",
        "shortLabel": "ENCODE WGBS",
    },
    "longLabel":  "{assay_title} of {replicates.library.biosample.summary} - {accession}",
    "shortLabel": "{assay_title} of {biosample_term_name} {accession}",
    "sortOrder": [ "Biosample", "Targets", "Replicates", "Views" ],
    "Views":  {
        "tag": "view",
        "group_order": [ "Optimal IDR thresholded peaks", "Conservative IDR thresholded peaks",
                        "Replicated peaks", "Peaks",  "Signal" ],
        "groups": {
            "Optimal IDR thresholded peaks": {
                "tag": "aOIDR",
                "visibility": "dense",
                "type": "bigBed",
                "file_format_type": [ "narrowPeak" ],
                "spectrum":"on",
                "scoreFilter":"0:1000",
                "output_type": [ "optimal idr thresholded peaks" ]
            },
            "Conservative IDR thresholded peaks": {
                "tag": "bCIDR",
                "visibility": "hide",
                "type": "bigBed",
                "file_format_type": [ "narrowPeak" ],
                "spectrum":"on",
                "scoreFilter": "0:1000",
                "output_type": [ "conservative idr thresholded peaks" ]
            },
            "Replicated peaks": {
                "tag": "cRPKS",
                "visibility": "dense",
                "type": "bigBed",
                "file_format_type": [ "narrowPeak" ],
                "spectrum":"on",
                "scoreFilter": "0:1000",
                "output_type": [ "replicated peaks" ]
            },
            "Peaks": {
                "tag": "dPKS",
                "visibility": "hide",
                "type": "bigBed",
                "file_format_type": [ "narrowPeak" ],
                "scoreFilter": "0:1000",
                "output_type": [ "peaks" ],
            },
            "Signal": {
                "tag": "eSIG",
                "visibility": "hide",
                "type": "bigWig",
                "viewLimits": "0:1",
                "autoScale": "off",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "signal" ]
            },
        },
    },
    "other_groups":  {
        "dimensions": { "Biosample": "dimY","Targets": "dimX","Replicates": "dimA" },
        "dimensionAchecked": "first", # or "all"
        "groups": {
            "Replicates": {
                "tag": "REP",
                "groups": {
                    "replicate": {
                        "title_mask": "Replicate_{replicate_number}",
                        "combined_title": "Pooled",  #We only want pooled replicates on
                    }
                },
            },
            "Biosample": {
                "tag": "BS",
                "groups": { "one": { "title_mask": "{biosample_term_name}"} }
            },
            "Targets": {
                "tag": "TARG",
                "groups": { "one": { "title_mask": "{target.label}"} }
            }
        }
    },
    "file_defs": {
        "longLabel": "{target} {assay_title} of {biosample_term_name} {output_type} {replicate} {experiment.accession} - {file.accession}",
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
    "sortOrder": [ "Biosample", "Targets", "Replicates", "Views" ],
    "Views":  {
        "tag": "view",
        "group_order": [ "Optimal IDR thresholded peaks", "Conservative IDR thresholded peaks",
                        "Replicated peaks", "Peaks",  "Fold change over control", "Signal p-value", "Signal" ],
        "groups": {
            "Optimal IDR thresholded peaks": {
                "tag": "aOIDR",
                "visibility": "dense",
                "type": "bigBed",
                "file_format_type": [ "narrowPeak" ],
                "spectrum":"on",
                "scoreFilter": "100:1000",
                "output_type": [ "optimal idr thresholded peaks" ]
            },
            "Conservative IDR thresholded peaks": {
                "tag": "bCIDR",
                "visibility": "hide",
                "type": "bigBed",
                "file_format_type": [ "narrowPeak" ],
                "spectrum":"on",
                "scoreFilter": "0:1000",
                "output_type": [ "conservative idr thresholded peaks" ]
            },
            "Replicated peaks": {
                "tag": "cRPKS",
                "visibility": "dense",
                "type": "bigBed",
                "file_format_type": [ "narrowPeak" ],
                "spectrum":"on",
                "scoreFilter": "0:1000",
                "output_type": [ "replicated peaks" ]
            },
            "Peaks": {
                "tag": "dPKS",
                "visibility": "hide",
                "type": "bigBed",
                "file_format_type": [ "narrowPeak" ],
                "scoreFilter": "0",
                "output_type": [ "peaks" ],
                # Tim, how complicated would it be to exclude "peaks" if other files are there?
            },
            "Fold change over control": {
                "tag": "eFCOC",
                "visibility": "full",
                "type": "bigWig",
                "viewLimits": "0:1",
                "autoScale": "off",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "fold change over control" ]
            },
            "Signal p-value": {
                "tag": "fSPV",
                "visibility": "hide",
                "type": "bigWig",
                "viewLimits": "0:1",
                "autoScale": "off",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "signal p-value" ]
            },
            "Signal": {
                "tag": "gSIG",
                "visibility": "hide",
                "type": "bigWig",
                "viewLimits": "0:1",
                "autoScale": "off",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "signal" ]
            },
        },
    },
    "other_groups":  {
        "dimensions": { "Biosample": "dimY","Targets": "dimX","Replicates": "dimA" },
        "dimensionAchecked": "first", # or "all"
        "groups": {
            "Replicates": {
                "tag": "REP",
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
                "groups": { "one": { "title_mask": "{biosample_term_name}"} }
            },
            "Targets": {
                "tag": "TARG",
                "groups": { "one": { "title_mask": "{target.label}", "url_mask": "targets/{target.name}"} }
            }
        }
    },
    "file_defs": {
        "longLabel": "{target} {assay_title} of {biosample_term_name} {output_type} {replicate} {experiment.accession} - {file.accession}",
        "shortLabel": "{replicate} {output_type_short_label}",
    }
}

ECLIP_COMPOSITE_VIS_DEFS = {
    "assay_composite": {
        "longLabel":  "Collection of ENCODE eCLIP experiments",
        "shortLabel": "ENCODE eCLIP",
    },
    "longLabel":  "{target} {assay_title} of {replicates.library.biosample.summary} - {accession}",
    "shortLabel": "{target} {assay_title} of {biosample_term_name} {accession}",
    "sortOrder": [ "Biosample", "Targets", "Replicates", "Views" ],
    "Views":  {
        "tag": "view",
        "group_order": [ "Signal", "Peaks" ],
        "groups": {
            "Signal": {
                "tag": "aSIG",
                "visibility": "full",
                "type": "bigWig",
                "viewLimits": "0:1",
                "autoScale": "off",
                "maxHeightPixels": "32:16:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "signal" ]
            },
            "Peaks": {
                "tag": "bPKS",
                "visibility": "dense",
                "type": "bigBed",
                "spectrum": "on",
                "scoreFilter": "100",
                "output_type": [ "peaks" ]
            },
        },
    },
    "other_groups":  {
        "dimensions": { "Biosample": "dimY","Targets": "dimX","Replicates": "dimA" },
        "dimensionAchecked": "all",
        "groups": {
            "Replicates": {
                "tag": "REP",
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
                "groups": { "one": { "title_mask": "{biosample_term_name}"} }
            },
            "Targets": {
                "tag": "TARG",
                "groups": { "one": { "title_mask": "{target.label}", "url_mask": "targets/{target.name}" } }
            }
        }
    },
    "file_defs": {
        "longLabel": "{target} {assay_title} of {biosample_term_name} {output_type} {replicate} {experiment.accession} - {file.accession}",
        "shortLabel": "{replicate} {output_type_short_label}",
    }
}

ANNO_COMPOSITE_VIS_DEFS = {
    "assay_composite": {
        "longLabel":  "Collection of ENCODE annotations",
        "shortLabel": "ENCODE annotations",
    },
    "longLabel":  "Encyclopedia annotation of {annotation_type} for {bisoample_term_name|multiple} - {accession}", #blank means "multiple biosamples"
    "shortLabel": "{annotation_type} of {biosample_term_name|multiple} {accession}", #blank means "multiple biosamples" not unknown
    "sortOrder": [ "Biosample","Replicates", "Views" ],
    "Views":  {
        "tag": "view",
        "group_order": [ "Candidate enhancers", "Candidate promoters",  "Chromatin state", "Peaks" ],
        "groups": {

            "Candidate enhancers": {
                "tag": "aENHAN",
                "type": "bigBed",
                "visibility": "dense",
                "output_type": [ "candidate enhancers" ]
            },
            "Candidate promoters": {
                "tag": "bPROMO",
                "type": "bigBed",
                "visibility": "dense",
                "output_type": [ "candidate promoters" ]
            },
            "Chromatin state": {
                "tag": "cSTATE",
                "type": "bigBed",
                "visibility": "dense",
                "output_type": [ "semi-automated genome annotation" ]
            },
            "Peaks": {
                "tag": "sPKS",
                "visibility": "hide",
                "type": "bigBed",
                "file_format_type": [ "narrowPeak" ],
                "scoreFilter": "0:1000",
                "output_type": [ "peaks" ],
            },
        },
    },
    "other_groups":  {
        "dimensions": { "Biosample": "dimY","Replicates": "dimA" },
        "dimensionAchecked": "all", # or "first"
        "groups": {
            "Replicates": {
                "tag": "REP",
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
                "groups": { "one": { "title_mask": "{biosample_term_name}"} }
            },
        }
    },
    "file_defs": {
        "longLabel": "Encyclopedia annotation of {biosample_term_name} {output_type} {replicate} {experiment.accession} - {file.accession}",
        "shortLabel": "{replicate} {output_type_short_label}",
    }
}

CHIA_COMPOSITE_VIS_DEFS = {
    "assay_composite": {
        "longLabel":  "Collection of ENCODE ChIA-PET experiments",
        "shortLabel": "ENCODE ChIA-PET",
    },
    "longLabel":  "{target} {assay_title} of {replicates.library.biosample.summary} - {accession}",
    "shortLabel": "{target} {assay_title} of {biosample_term_name} {accession}",
    "sortOrder": [ "Biosample", "Targets", "Replicates", "Views" ],
    "Views": {
        "tag": "view",
        "group_order": [ "Signal of unique reads", "Signal of all reads", "Plus signal of unique reads", "Minus signal of unique reads", "Plus signal of all reads", "Minus signal of all reads", ],
        "groups": {
            "Signal of unique reads": {
                "tag": "SIGBL",
                "visibility": "full",
                "type": "bigWig",
                "viewLimits": "0:1",
                "transformFunc": "LOG",
                "autoScale": "off",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "signal of unique reads" ]
            },
            "Signal of all reads": {
                "tag": "SIGBM",
                "visibility": "hide",
                "type": "bigWig",
                "viewLimits": "0:1",
                "transformFunc": "LOG",
                "autoScale": "off",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "signal of all reads" ]
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
                    "combined_title": "Pooled", # "Combined"
                    }
                },
            },
            "Biosample": {
                "tag": "BS",
                "groups": { "one": { "title_mask": "{biosample_term_name}"} }
            },
            "Targets": {
                "tag": "TARG",
                "groups": { "one": { "title_mask": "{target.label}" } },
            },
        }
    },
    "file_defs": {
        "longLabel": "{assay_title} of {biosample_term_name} {output_type} {replicate} {experiment.accession} - {file.accession}",
        "shortLabel": "{replicate} {output_type_short_label}",
    }
}

HIC_COMPOSITE_VIS_DEFS = {
    "assay_composite": {
        "longLabel":  "Collection of ENCODE Hi-C experiments",
        "shortLabel": "ENCODE HI-C",
    },
    "longLabel":  "{assay_title} of {replicates.library.biosample.summary} - {accession}",
    "shortLabel": "{assay_title} of {biosample_term_name} {accession}",
    "sortOrder": [ "Biosample", "Targets", "Replicates", "Views" ],
    "Views": {
        "tag": "view",
        "group_order": [ "Topologically associated domains", "Nested TADs", "Genome compartments" ],
        "groups": {
            "Topologically associated domains": {
                "tag": "aTADS",
                "visibility": "dense",
                "type": "bigBed 3+",
                "output_type": [ "topologically associated domains" ]
            },
            "Nested TADs": {
                "tag": "bTADS",
                "visibility": "hide",
                "type": "bigBed 3+",
                "output_type": [ "nested topologically associated domains" ]
            },
            "Genome compartments": {
                "tag": "cCOMPART",
                "visibility": "hide",
                "type": "bigWig",
                "viewLimits": "0:1",
                "transformFunc": "LOG",
                "autoScale": "off",
                "maxHeightPixels": "64:18:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "genome compartments" ]
            },
        },
    },
    "other_groups": {
        "dimensions": { "Biosample": "dimY", "Replicates": "dimA" },
        "dimensionAchecked": "first", # or "all"
        "groups": {
            "Replicates": {
                "tag": "REP",
                "group_order": "sort",
                "groups": {
                "replicate": {
                    "title_mask": "Replicate_{replicate_number}", # Optional
                    "combined_title": "Pooled", # "Combined"
                    }
                },
            },
            "Biosample": {
                "tag": "BS",
                "groups": { "one": { "title_mask": "{biosample_term_name}"} }
            },
        }
    },
    "file_defs": {
        "longLabel": "{assay_title} of {biosample_term_name} {output_type} {replicate} {experiment.accession} - {file.accession}",
        "shortLabel": "{replicate} {output_type_short_label}",
    }
}

VIS_DEFS_BY_ASSAY = {
    "LRNA":     LRNA_COMPOSITE_VIS_DEFS,
    "tkRNA":    TKRNA_COMPOSITE_VIS_DEFS,
    "SRNA":     SRNA_COMPOSITE_VIS_DEFS,
    "TSS":      RAMPAGE_COMPOSITE_VIS_DEFS,
    "miRNA":    MICRORNA_COMPOSITE_VIS_DEFS,
    "DNAse":    DNASE_COMPOSITE_VIS_DEFS,
    "WGBS":     WGBS_COMPOSITE_VIS_DEFS,
    "ChIP":     CHIP_COMPOSITE_VIS_DEFS,
    "eCLIP":    ECLIP_COMPOSITE_VIS_DEFS,
    "ANNO":     ANNO_COMPOSITE_VIS_DEFS,
    "ChIA":     CHIA_COMPOSITE_VIS_DEFS, # TODO: get_vis_type
    "HiC":      HIC_COMPOSITE_VIS_DEFS,  # TODO: get_vis_type
    }

def get_vis_type(dataset):
    '''returns the best static composite definition set, based upon dataset.'''
    assay = dataset.get("assay_term_name")
    if assay is None:
        type = dataset["@id"].split('/')[1]
        if type == "annotations":
            return "ANNO"

    # This will be long AND small
    elif assay in ["shRNA knockdown followed by RNA-seq","siRNA knockdown followed by RNA-seq","CRISPR genome editing followed by RNA-seq"]:
        return "tkRNA"
    elif assay in ["RNA-seq","single cell isolation followed by RNA-seq"]:
        size_range = dataset["replicates"][0]["library"]["size_range"]
        if size_range.startswith('>'):
            size_range = size_range[1:]
        try:
            sizes = size_range.split('-')
            min_size = int(sizes[0])
            max_size = int(sizes[1])
        except:
            log.warn("Could not distinguish between long and short RNA for %s.  Defaulting to short." % (dataset.get("accession")))
            return "SRNA"  # this will be more noticed if there is a mistake
        if max_size <= 200:
            return "SRNA"
        elif min_size >= 150:
            return "LRNA"
        elif (min_size + max_size)/2 >= 235: # This is some wicked voodoo (SRNA:108-347=227; LRNA:155-315=235)
            return "LRNA"
        else:
            return "SRNA"
    elif assay in ["microRNA-seq","microRNA counts"]:
        return "miRNA"
    elif assay in ["whole-genome shotgun bisulfite sequencing","shotgun bisulfite-seq assay"]:
        return "WGBS"
    elif assay.lower() in ["rampage","cage"]:
        return "TSS"
    elif assay == "ChIP-seq":
        return "ChIP"
    elif assay == "eCLIP":
        return assay
    elif assay.lower() == "dnase-seq":
        return "DNASE"
    elif assay == "ChIA-PET":
        return "ChIA"
    elif assay == "HiC":
        return "HiC"

    return "opaque" # This becomes a dict key later so None is not okay


def lookup_vis_defs(vis_type):
    '''returns the best static composite definition set, based upon dataset.'''
    return VIS_DEFS_BY_ASSAY.get(vis_type, COMPOSITE_VIS_DEFS_DEFAULT )

PENNANTS = {
    "NHGRI":  "https://www.encodeproject.org/static/img/pennant-nhgri.png https://www.encodeproject.org/ \"This trackhub was automatically generated from the files and metadata found at https://www.encodeproject.org/\"",
    "ENCODE": "https://www.encodeproject.org/static/img/pennant-encode.png https://www.encodeproject.org/ \"This trackhub was automatically generated from the ENCODE files and metadata found at https://www.encodeproject.org/\"",
    "modENCODE":"https://www.encodeproject.org/static/img/pennant-encode.png https://www.encodeproject.org/ \"This trackhub was automatically generated from the modENCODE files and metadata found at https://www.encodeproject.org/\"",
    "GGR":    "https://www.encodeproject.org/static/img/pennant-ggr.png https://www.encodeproject.org/ \"This trackhub was automatically generated from the GGR files and metadata found at https://www.encodeproject.org/\"",
    "REMC":   "https://www.encodeproject.org/static/img/pennant-remc.png https://www.encodeproject.org/ \"This trackhub was automatically generated from the REMC files and metadata found at https://www.encodeproject.org/\"",
    #"Roadmap":   "encodeThumbnail.jpg https://www.encodeproject.org/ \"This trackhub was automatically generated from the Roadmap files and metadata found at https://www.encodeproject.org/\"",
    #"modERN":   "encodeThumbnail.jpg https://www.encodeproject.org/ \"This trackhub was automatically generated from the modERN files and metadata found at https://www.encodeproject.org/\"",
    }
def find_pennent(dataset):
    '''Returns an appropriate pennantIcon given dataset's award'''
    # ZZZ3, ZNF592, ZNF384, ZNF318, ZNF274, ZNF263
    # rabbit-IgG-control, mouse-IgG-control
    # eGFP-ZNF83, eGFP-ZNF766, eGFP-ZNF740, eGFP-ZNF644, eGFP-ZNF639, eGFP-ZNF589, eGFP-ZNF584, eGFP-ZNF24, eGFP-ZNF197, eGFP-ZNF175, eGFP-ZKSCAN8
    # eGFP-ZFX, eGFP-ZBTB11, eGFP-USF2, eGFP-TSC22D4, eGFP-TFDP1, eGFP-TEAD2, eGFP-TAF7, eGFP-RELA, eGFP-PYGO2, eGFP-PTTG1, eGFP-PTRF, eGFP-NR4A1,
    # eGFP-NR2C2, eGFP-NFE2L1, eGFP-MAFG, eGFP-KLF9, eGFP-KLF4, eGFP-KLF13, eGFP-KLF1, eGFP-JUND, eGFP-JUNB, eGFP-IRF9, eGFP-IRF1, eGFP-ILK,
    # eGFP-ID3, eGFP-HINFP, eGFP-HDAC8, eGFP-GTF2E2, eGFP-GATA2, eGFP-GABPA, eGFP-FOXJ2, eGFP-FOSL2, eGFP-FOSL1, eGFP-FOS, eGFP-ETV1, eGFP-ELK1,
    # eGFP-ELF1, eGFP-E2F5, eGFP-E2F5, eGFP-E2F4, eGFP-DIDO1, eGFP-E2F4, eGFP-DDX20, eGFP-CUX1, eGFP-CREB3, eGFP-CEBPG, eGFP-CEBPB, eGFP-BACH1,
    # eGFP-ATF1, eGFP-ADNP

    #ZNF263=ZNF263 ZNF274=ZNF274 ZNF318=ZNF318 ZNF384=ZNF384 ZNF592=ZNF592 ZZZ3=ZZZ3
    # eGFP45ADNP=eGFP-ADNP eGFP45ATF1=eGFP-ATF1 eGFP45BACH1=eGFP-BACH1 eGFP45CEBPB=eGFP-CEBPB eGFP45CEBPG=eGFP-CEBPG eGFP45CREB3=eGFP-CREB3 eGFP45CUX1=eGFP-CUX1 eGFP45DDX20=eGFP-DDX20 eGFP45DIDO1=eGFP-DIDO1 eGFP45E2F4=eGFP-E2F4 eGFP45E2F5=eGFP-E2F5 eGFP45ELF1=eGFP-ELF1 eGFP45ELK1=eGFP-ELK1 eGFP45ETV1=eGFP-ETV1 eGFP45FOS=eGFP-FOS eGFP45FOSL1=eGFP-FOSL1 eGFP45FOSL2=eGFP-FOSL2 eGFP45FOXJ2=eGFP-FOXJ2 eGFP45GABPA=eGFP-GABPA eGFP45GATA2=eGFP-GATA2 eGFP45GTF2E2=eGFP-GTF2E2 eGFP45HDAC8=eGFP-HDAC8 eGFP45HINFP=eGFP-HINFP eGFP45ID3=eGFP-ID3 eGFP45ILK=eGFP-ILK eGFP45IRF1=eGFP-IRF1 eGFP45IRF9=eGFP-IRF9 eGFP45JUNB=eGFP-JUNB eGFP45JUND=eGFP-JUND eGFP45KLF1=eGFP-KLF1 eGFP45KLF13=eGFP-KLF13 eGFP45KLF4=eGFP-KLF4 eGFP45KLF9=eGFP-KLF9 eGFP45MAFG=eGFP-MAFG eGFP45NFE2L1=eGFP-NFE2L1 eGFP45NR2C2=eGFP-NR2C2 eGFP45NR4A1=eGFP-NR4A1 eGFP45PTRF=eGFP-PTRF eGFP45PTTG1=eGFP-PTTG1 eGFP45PYGO2=eGFP-PYGO2 eGFP45RELA=eGFP-RELA eGFP45TAF7=eGFP-TAF7 eGFP45TEAD2=eGFP-TEAD2 eGFP45TFDP1=eGFP-TFDP1 eGFP45TSC22D4=eGFP-TSC22D4 eGFP45USF2=eGFP-USF2 eGFP45ZBTB11=eGFP-ZBTB11 eGFP45ZFX=eGFP-ZFX eGFP45ZKSCAN8=eGFP-ZKSCAN8 eGFP45ZNF175=eGFP-ZNF175 eGFP45ZNF197=eGFP-ZNF197 eGFP45ZNF24=eGFP-ZNF24 eGFP45ZNF584=eGFP-ZNF584 eGFP45ZNF589=eGFP-ZNF589 eGFP45ZNF639=eGFP-ZNF639 eGFP45ZNF644=eGFP-ZNF644 eGFP45ZNF740=eGFP-ZNF740 eGFP45ZNF766=eGFP-ZNF766 eGFP45ZNF83=eGFP-ZNF83
    # goat45IgG45control=goat-IgG-control mouse45IgG45control=mouse-IgG-control rabbit45IgG45control=rabbit-IgG-control
    project = dataset.get("award",{}).get("project","NHGRI")
    return PENNANTS.get(project,PENNANTS.get("NHGRI"))


SUPPORTED_SUBGROUPS = [ "Biosample", "Targets", "Assay", "Replicates", "Views" ]

SUPPORTED_TRACK_SETTINGS = [
    "type","visibility","longLabel","shortLabel","color","altColor","allButtonPair","html"
    "scoreFilter","spectrum",
    "viewLimits","autoScale","negateValues","maxHeightPixels","windowingFunction","transformFunc",
    ]
COMPOSITE_SETTINGS = ["longLabel","shortLabel","visibility","pennantIcon","allButtonPair","html"]
VIEW_SETTINGS = SUPPORTED_TRACK_SETTINGS
TRACK_SETTINGS = ["bigDataUrl","longLabel","shortLabel","type","color","altColor"]


OUTPUT_TYPE_8CHARS = {
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
    "induced pluripotent stem cell line":   {"color":"80,49,120",   "altColor": "107,95,102" }, # Purple
    "stem cell":                            { "color":"0,107,27",   "altColor": "0.0,77,20"  }, # Dark Green
    "GM12878":                              { "color":"153,38,0",   "altColor": "115,31,0"   }, # Dark Orange-Red
    "H1-hESC":                              { "color":"0,107,27",   "altColor": "0,77,20"    },  # Dark Green
    "K562":                                 { "color":"46,0,184",   "altColor": "38,0,141"   }, # Dark Blue
    "keratinocyte":                         { "color":"179,0,134",  "altColor": "154,0,113"  }, # Darker Pink-Purple
    "HepG2":                                { "color":"189,0,157",  "altColor": "189,76,172" }, # Pink-Purple
    "HeLa-S3":                              { "color":"0,119,158",  "altColor": "0,94,128"   }, # Greenish-Blue
    "HeLa":                                 { "color":"0,119,158",  "altColor": "0,94,128"   }, # Greenish-Blue
    "A549":                                 { "color":"255,241,26", "altColor": "218,205,22" }, # Yellow
    "endothelial cell of umbilical vein":   { "color":"224,75,0",   "altColor": "179,60,0"   },  # Pink
    "MCF-7":                                { "color":"22,219,206", "altColor": "18,179,168" }, # Cyan
    "SK-N-SH":                              { "color":"255,115,7",  "altColor": "218,98,7"   },  # Orange
    "IMR-90":                               { "color":"6,62,218",   "altColor": "5,52,179"   },  # Blue
    "CH12.LX":                              { "color":"86,180,233", "altColor": "76,157,205" }, # Dark Orange-Red
    "MEL cell line":                        { "color":"46,0,184",   "altColor": "38,0,141"   }, # Dark Blue
    "brain":                                { "color":"105,105,105","altColor": "77,77,77"   }, # Grey
    "eye":                                  { "color":"105,105,105","altColor": "77,77,77"   }, # Grey
    "spinal cord":                          { "color":"105,105,105","altColor": "77,77,77"   }, # Grey
    "olfactory organ":                      { "color":"105,105,105","altColor": "77,77,77"   }, # Grey
    "esophagus":                            { "color":"230,159,0",  "altColor": "179,125,0"  }, # Mustard
    "stomach":                              { "color":"230,159,0",  "altColor": "179,125,0"  }, # Mustard
    "liver":                                { "color":"230,159,0",  "altColor": "179,125,0"  }, # Mustard
    "pancreas":                             { "color":"230,159,0",  "altColor": "179,125,0"  }, # Mustard
    "large intestine":                      { "color":"230,159,0",  "altColor": "179,125,0"  }, # Mustard
    "small intestine":                      { "color":"230,159,0",  "altColor": "179,125,0"  }, # Mustard
    "gonad":                                { "color":"0.0,158,115","altColor": "0.0,125,92" }, # Darker Aquamarine
    "mammary gland":                        { "color":"0.0,158,115","altColor": "0.0,125,92" }, # Darker Aquamarine
    "prostate gland":                       { "color":"0.0,158,115","altColor": "0.0,125,92" }, # Darker Aquamarine
    "ureter":                               { "color":"204,121,167","altColor": "166,98,132" }, # Grey-Pink
    "urinary bladder":                      { "color":"204,121,167","altColor": "166,98,132" }, # Grey-Pink
    "kidney":                               { "color":"204,121,167","altColor": "166,98,132" }, # Grey-Pink
    "muscle organ":                         { "color":"102,50,200 ","altColor": "81,38,154"  }, # Violet
    "tongue":                               { "color":"102,50,200", "altColor": "81,38,154"  }, # Violet
    "adrenal gland":                        { "color":"189,0,157",  "altColor": "154,0,128"  }, # Pink-Purple
    "thyroid gland":                        { "color":"189,0,157",  "altColor": "154,0,128"  }, # Pink-Purple
    "lung":                                 { "color":"145,235,43", "altColor": "119,192,35" }, # Mossy green
    "bronchus":                             { "color":"145,235,43", "altColor": "119,192,35" }, # Mossy green
    "trachea":                              { "color":"145,235,43", "altColor": "119,192,35" }, # Mossy green
    "nose":                                 { "color":"145,235,43", "altColor": "119,192,35" }, # Mossy green
    "placenta":                             { "color":"153,38,0",   "altColor": "102,27,0"   }, # Orange-Brown
    "extraembryonic structure":             { "color":"153,38,0",   "altColor": "102,27,0"   }, # Orange-Brown
    "thymus":                               { "color":"86,180,233", "altColor": "71,148,192" }, # Baby Blue
    "spleen":                               { "color":"86,180,233", "altColor": "71,148,192" }, # Baby Blue
    "bone element":                         { "color":"86,180,233", "altColor": "71,148,192" }, # Baby Blue
    "blood":                                { "color":"86,180,233", "altColor": "71,148,192" },  # Baby Blue This follows UCSC but I want it to be red
    "blood vessel":                         { "color":"214,0,0",    "altColor": "214,79,79"  }, # Red
    "heart":                                { "color":"214,0,0",    "altColor": "214,79,79"  }, # Red
    "lymphatic vessel":                     { "color":"214,0,0",    "altColor": "214,79,79"  }, # Red
    "skin of body":                         { "color":"74,74,21",   "altColor": "102,102,44" } # Brown
    }

def lookup_colors(dataset):
    '''Using the mask, determine which color table to use.'''
    color = None
    altColor = None
    coloring = {}
    biosample_term = dataset.get('biosample_type')
    if biosample_term is not None:
        coloring = BIOSAMPLE_COLOR.get(biosample_term,{})
    if not coloring:
        biosample_term = dataset.get('biosample_term_name')
        if biosample_term is not None:
            coloring = BIOSAMPLE_COLOR.get(biosample_term,{})
    if not coloring:
        organ_slims = dataset.get('organ_slims',[])
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
            altColor = "%d,%d,%d" % (red,green,blue)
            coloring["altColor"] = altColor

    return coloring

def add_living_color(live_settings, dataset):
    '''Adds color and altColor.  Note that altColor is only added if color is found.'''
    colors = lookup_colors(dataset)
    if colors and "color" in colors:
        live_settings["color"] = colors["color"]
        if "altColor" in colors:
            live_settings["altColor"] = colors["altColor"]

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

def add_to_es(request,comp_id,composite):
    '''Adds a composite json blob to elastic-search'''
    #return
    key="vis_composite"
    es = request.registry.get(ELASTIC_SEARCH, None)
    if not es.indices.exists(key):
        es.indices.create(index=key, body={ 'index': { 'number_of_shards': 1 } })
        mapping = { 'default': {    "_all" :    { "enabled": False },
                                    "_source":  { "enabled": True },
        #                            "_id":      { "index":  "not_analyzed", "store" : True },
        #                            "_ttl":     { "enabled": True, "default" : "1d" },
                               } }
        es.indices.put_mapping(index=key, doc_type='default', body=mapping )
        log.warn("created %s index" % key)
    es.index(index=key, doc_type='default', body=composite, id=comp_id)

def get_from_es(request,comp_id):
    '''Returns composite json blob from elastic-search, or None if not found.'''
    #return None
    key="vis_composite"
    es = request.registry.get(ELASTIC_SEARCH, None)
    if es.indices.exists(key):
        try:
            result = es.get(index=key, doc_type='default', id=comp_id)
            return result['_source']
        except:
            pass
    return None

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


def lookup_token(token,dataset,a_file=None):
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
    elif token in ["{target}","{target.label}","{target.name}","{target.title}"]:
        target = dataset.get('target',{})
        if isinstance(target,list):
            target = target[0]
        if token.find('.') > -1:
            sub_token = token.strip('{}').split('.')[0]
        else:
            sub_token = "label"
        return target.get(sub_token,"Unknown Target")
        #if token == "{target.name}":
        #    return target.get('name',"Unknown Target")
        #return target.get('label',"Unknown Target")
    elif token in ["{target.name}"]:
        target = dataset.get('target',{})
        if isinstance(target,list):
            target = target[0]
        return target.get('label',"Unknown Target")
    elif token in ["{replicates.library.biosample.summary}","{replicates.library.biosample.summary|multiple}"]:
        term = None
        replicates = dataset.get("replicates",[])
        if replicates:
            term = replicates[0].get("library",{}).get("biosample",{}).get("summary")
        if term is None:
            term = dataset.get("{biosample_term_name}")
        if term is None:
            if token.endswith("|multiple}"):
                term = "multiple biosamples"
            else:
                term = "Unknown Biosample"
        return term
    elif token == "{biosample_term_name|multiple}":
        return dataset.get("biosample_term_name","multiple biosamples")
    elif a_file is not None:
        if token == "{file.accession}":
            return a_file['accession']
        elif token == "{output_type}":
            return a_file['output_type']
        elif token == "{output_type_short_label}":
            output_type = a_file['output_type']
            return OUTPUT_TYPE_8CHARS.get(output_type,output_type)
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

def convert_mask(mask,dataset,a_file=None):
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
        term = lookup_token(working_on[beg_ix:end_ix+1],dataset,a_file=a_file)
        new_mask = []
        if beg_ix > 0:
            new_mask = working_on[0:beg_ix]
        new_mask += "%s%s" % (term,working_on[end_ix+1:])
        chars = len(working_on[end_ix+1:])
        working_on = ''.join(new_mask)

    return working_on


def handle_negateValues(live_settings, defs, dataset, composite):
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

def generate_live_groups(composite,title,group_defs,dataset,rep_tags=[]):
    '''Recursively populates live (in memory) groups from static group definitions'''
    live_group = {}
    tag = group_defs.get("tag",title)
    live_group["title"] = title
    live_group["tag"] = tag
    for key in group_defs.keys():
        if key not in ["groups","group_order"]: # leave no trace of subgroups keyed by title
            live_group[key] = deepcopy(group_defs[key])

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
                    rep_no = int(rep_tag[3:]) # tag might be rep01 but we want replicate 1
                    rep_title = rep_title_mask.replace('{replicate_number}',str(rep_no))
            live_group["groups"][rep_tag] = { "title": rep_title, "tag": rep_tag }
        live_group["preferred_order"] = "sorted"

    elif title in ["Biosample", "Targets", "Assay" ]: # Single subGroup at experiment level.  No order
        groups = group_defs.get("groups",{})
        assert(len(groups) == 1)
        for (group_key,group) in groups.items():
            mask = group.get("title_mask")
            if mask is not None:
                term = convert_mask(mask,dataset)
                if not term.startswith('Unknown '):
                    term_tag = sanitize_tag(term)
                    term_title = term
                    live_group["groups"] = {}
                    live_group["groups"][term_tag] = { "title": term_title, "tag": term_tag }
                    mask = group.get("url_mask")
                    if mask is not None:
                        term = convert_mask(mask,dataset)
                        live_group["groups"][term_tag]["url"] = term
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
                (subgroup_tag, subgroup) = generate_live_groups(composite,subgroup_title,subgroup,dataset) #recursive
                subgroup["tag"] = subgroup_tag
                if isinstance(preferred_order,list):
                    preferred_order.append(subgroup_tag)
                if title == "Views":
                    assert(subgroup_title != subgroup_tag)
                    handle_negateValues(subgroup, subgroup, dataset, composite)
                live_group["groups"][subgroup_tag] = subgroup
                tag_order.append(subgroup_tag)
            #assert(len(live_group["groups"]) == len(groups))
            if len(live_group["groups"]) != len(groups):
                log.warn(json.dumps(live_group,indent=4))
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
        #log.warn("Added %s to %s in sort order" % (new_tag,live_groups.get("tag","a group"))) # DEBUG: remodelling
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
    #log.warn("Added %s to %s in preferred order" % (new_tag,live_groups.get("tag","a group"))) # DEBUG: remodelling
    return live_groups

def biosamples_for_file(a_file,dataset):
    '''Returns a dict of biosamples for file.'''
    biosamples = {}
    replicates = dataset.get("replicates")
    if replicates is None:
        return[]

    for bio_rep in a_file.get("biological_replicates",[]):
        for replicate in replicates:
            if replicate.get("biological_replicate_number",-1) != bio_rep:
                continue
            biosample = replicate.get("library",{}).get("biosample",{})
            if biosample is None:
                continue
            biosamples[biosample["accession"]] = biosample
            break  # If multiple techical replicates then the one should do

    return biosamples

def acc_composite_extend_with_tracks(composite, vis_defs, dataset, assembly, host=None):
    '''Extends live experiment composite object with track definitions'''
    tracks = []
    rep_techs = {}
    files = []
    ucsc_assembly = _ASSEMBLY_MAPPER.get(assembly, assembly)

    # first time through just to get rep_tech
    group_order = composite["view"].get("group_order",[])
    for view_tag in group_order:
        view = composite["view"]["groups"][view_tag]
        output_types = view.get("output_type",[])
        file_format_types = view.get("file_format_type",[])
        #if "type" not in view:
        #    log.warn(json.dumps(composite)) # DEBUG: basics
        file_format = view["type"].split()[0]
        if file_format == "bigBed" and "scoreFilter" in view:
            view["type"] = "bigBed 6 +" # be more discriminating as to what bigBeds are 6 + ?  Just rely on scoreFilter
        for a_file in dataset["files"]:
            if a_file['status'] in INVISIBLE_FILE_STATUSES:
                continue
            if 'assembly' not in a_file or _ASSEMBLY_MAPPER.get(a_file['assembly'], a_file['assembly']) != ucsc_assembly:
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
        log.warn("No visualizable files for %s" % dataset["accession"])
        return None

    # convert rep_techs to simple reps
    rep_ix = 1
    rep_tags = []
    for rep_tech in sorted( rep_techs.keys() ): # ordered by a simple sort
        if rep_tech == "combined":
            rep_tag = "pool"
        else:
            rep_tag = "rep%02d" % rep_ix
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
            (repgroup_tag, repgroup) = generate_live_groups(composite,"replicate",subgroups["replicate"],dataset,rep_tags)
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
        file_format = view["type"].split()[0]
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
            #track["name"] = "%s_%s" % (dataset['accession'][3:],a_file['accession'][3:]) # Trimming too cute?
            track["name"] = a_file['accession']
            track["type"] = view["type"]
            track["bigDataUrl"] = "%s?proxy=true" % a_file["href"]
            longLabel = vis_defs.get('file_defs',{}).get('longLabel')
            if longLabel is None:
                longLabel = "{assay_title} of {biosample_term_name} {output_type} {biological_replicate_number} {experiment.accession} - {file.accession}"
            track["longLabel"] = sanitize_label( convert_mask(longLabel,dataset,a_file) )
            metadata_pairs = {}
            metadata_pairs['file&#32;download'] = '"<a href=\"%s%s\" title=\'Download this file from the ENCODE portal\'>%s</a>"' % (host,a_file["href"],a_file["accession"])
            metadata_pairs["experiment"] = '"<a href=\"%s/experiments/%s\" TARGET=\'_blank\' title=\'Experiment details from the ENCODE portal\'>%s</a>"' % (host,dataset["accession"],dataset["accession"])
            lab_title = a_file.get("lab",dataset.get("lab",{})).get("title")
            if lab_title is not None:
                metadata_pairs["source"] = '"%s"' % lab_title


            # Expecting short label to change when making assay based composites
            shortLabel = vis_defs.get('file_defs',{}).get('shortLabel',"{replicate} {output_type_short_label}")
            track["shortLabel"] = sanitize_label( convert_mask(shortLabel,dataset,a_file) )

            # How about subgroups!
            membership = {}
            membership["view"] = view["tag"]
            view["tracks"].append( track )  # <==== This is how we connect them to the views
            for (group_tag,group) in composite["groups"].items():
                # "Replicates", "Biosample", "Targets", "Assay", ... member?
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
                elif group_title in ["Biosample", "Targets", "Assay"]:
                    assert(len(subgroups) == 1)
                    #if len(subgroups) == 1:
                    for (subgroup_tag,subgroup) in subgroups.items():
                        membership[group_tag] = subgroup["tag"]
                        if "url" in subgroup:
                            metadata_pairs[group_title] = '"<a href=\"%s/%s/\" TARGET=\'_blank\' title=\'%s details\'>%s</a>"' % (host,subgroup["url"],group_title,subgroup["title"])
                        elif group_title == "Biosample":
                            bs_value = subgroup["title"]
                            biosamples = biosamples_for_file(a_file,dataset)
                            if len(biosamples) > 0:
                                for bs_acc in sorted( biosamples.keys() ):
                                    bs_value += " <a href=\"%s%s\" TARGET=\'_blank\' title=\'%s details\'>%s</a>" % (host,biosamples[bs_acc]["@id"],group_title,bs_acc)
                            metadata_pairs[group_title] = '"%s"' % (bs_value)
                        else:
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

def make_acc_composite(dataset, assembly, host=None, hide=False):
    '''Converts experiment composite static definitions to live composite object'''
    vis_type = get_vis_type(dataset)
    vis_defs = lookup_vis_defs(vis_type)
    if vis_defs is None:
        return {}
    composite = {}
    composite["vis_type"] = vis_type
    composite["name"] = dataset["accession"]

    longLabel = vis_defs.get('longLabel','{assay_term_name} of {biosample_term_name} - {accession}')
    composite['longLabel'] = sanitize_label( convert_mask(longLabel,dataset) )
    shortLabel = vis_defs.get('shortLabel','{accession}')
    composite['shortLabel'] = sanitize_label( convert_mask(shortLabel,dataset) )
    if hide:
        composite["visibility"] = "hide"
    else:
        composite["visibility"] = vis_defs.get("visibility","full")
    composite['pennantIcon'] = find_pennent(dataset)
    add_living_color(composite, dataset)
    # views are always subGroup1
    composite["view"] = {}
    title_to_tag = {}
    if "Views" in vis_defs:
        ( tag, views ) = generate_live_groups(composite,"Views",vis_defs["Views"],dataset)
        composite[tag] = views
        title_to_tag["Views"] = tag

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
            (subgroup_tag, subgroup) = generate_live_groups(composite,subgroup_title,groups[subgroup_title],dataset)
            if isinstance(preferred_order,list):
                preferred_order.append(subgroup_tag)  # "Targets" will get in, even if there are no targets in dataset
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

    #log.warn(json.dumps(composite)) # DEBUG: basics
    tracks = acc_composite_extend_with_tracks(composite, vis_defs, dataset, assembly, host=host)
    if tracks is None or len(tracks) == 0:
        # Already warned about files log.warn("No tracks for %s" % dataset["accession"])
        return {}
    composite["tracks"] = tracks
    #log.warn(json.dumps(composite["view"]["groups"]["REPTSS"])) # DEBUG: basics
    return composite

def remodel_acc_to_set_composites(acc_composites,hide_after=None):
    '''Given a set of (search result) acc based composites, remodel them to set based composites.'''
    if acc_composites is None or len(acc_composites) == 0:
        return {}

    set_composites = {}

    for acc in sorted( acc_composites.keys() ):
        acc_composite = acc_composites[acc]
        if acc_composite is None or len(acc_composite) == 0: # wounded composite can be dropped or added for evidence
            #log.warn("Found empty acc_composite for %s" % (acc)) # DEBUG: remodelling
            set_composites[acc] = {}
            continue

        # Only show the first n datasets
        if hide_after != None:
            if hide_after <= 0:
                for track in acc_composite.get("tracks",{}):
                    track["checked"] = "off"
            else:
                hide_after -= 1

        # color must move to tracks becuse it is likely biosample based and we are likely mixing biosample exps
        acc_color = acc_composite.get("color")
        acc_altColor = acc_composite.get("altColor")
        acc_view_groups = acc_composite.get("view",{}).get("groups",{})
        for (view_tag,acc_view) in acc_view_groups.items():
            acc_view_color = acc_view.get("color",acc_color) # color may be at view level if negateValues os on
            acc_view_altColor = acc_view.get("altColor",acc_altColor)
            if acc_view_color is None and acc_view_altColor is None:
                continue
            for track in acc_view.get("tracks",[]):
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
            #log.warn("Remodelling %s into %s composite" % (acc_composite.get("name"," a composite"),vis_type)) # DEBUG: remodelling
            set_composite = acc_composite # Don't bother with deep copy... we aren't needing the acc_composites any more
            set_defs = vis_defs.get("assay_composite",{})
            set_composite["name"] = vis_type.lower()  # is there something more elegant?
            for tag in ["longLabel","shortLabel","visibility"]:
                if tag in set_defs:
                    set_composite[tag] = set_defs[tag] # Not expecting any token substitutions!!!
            set_composite['html'] = vis_type
            set_composites[vis_type] = set_composite

        else: # Adding an acc_composite to an existing set_composite
            #log.warn("Adding %s into %s composite" % (acc_composite.get("name"," a composite"),vis_type)) # DEBUG: remodelling
            set_composite = set_composites[vis_type]

            if set_composite.get("project","unknown") != "NHGRI":
                acc_pennant = acc_composite["pennantIcon"]
                set_pennant = set_composite["pennantIcon"]
                if acc_pennant != set_pennant:
                    set_composite["project"] = "NHGRI"
                    set_composite["pennantIcon"] = PENNANTS["NHGRI"]

            # combine views
            set_views = set_composite.get("view",[])
            acc_views = acc_composite.get("view",{})
            for view_tag in acc_views["group_order"]:
                acc_view = acc_views["groups"][view_tag]
                if view_tag not in set_views["groups"].keys():  # Should never happen
                    #log.warn("Surprise: view %s not found before" % view_tag) # DEBUG: remodelling
                    insert_live_group(set_views,view_tag,acc_view)
                else: # View is already defined but tracks need to be appended.
                    set_view = set_views["groups"][view_tag]
                    if "tracks" not in set_view:
                        set_view["tracks"] = acc_view.get("tracks",[])
                    else:
                        set_view["tracks"].extend(acc_view.get("tracks",[]))

            # All tracks in one set: not needed.

            # Combine subgroups:
            for group_tag in acc_composite["group_order"]:
                acc_group = acc_composite["groups"][group_tag]
                if group_tag not in set_composite["groups"].keys(): # Should never happen
                    #log.warn("Surprise: group %s not found before" % group_tag) # DEBUG: remodelling
                    insert_live_group(set_composite,group_tag,acc_group)
                else: # Need to handle subgroups which definitely may not be there.
                    set_group = set_composite["groups"].get(group_tag,{})
                    acc_subgroups = acc_group.get("groups",{})
                    acc_subgroup_order = acc_group.get("group_order")
                    for subgroup_tag in acc_subgroups.keys():
                        if subgroup_tag not in set_group.get("groups",{}).keys():
                            insert_live_group(set_group,subgroup_tag,acc_subgroups[subgroup_tag]) # Adding biosamples, targets, and reps

            # dimensions and filterComposite should not need any extra care: they get dynamically scaled down during printing
            #log.warn("       Added.") # DEBUG: remodelling

    return set_composites

def ucsc_trackDb_composite_blob(composite,title):
    '''Given an in-memory composite object, prints a single UCSC trackDb.txt composite structure'''
    if composite is None or len(composite) == 0:
        return "# Empty composite for %s.  It cannot be visualized at this time.\n" % title

    blob = ""
    # First the composite structure
    blob += "track %s\n" % composite["name"]
    blob += "compositeTrack on\n"
    blob += "type bed 3\n"
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
            if group is None or len(group.get("groups",{})) <= 1: # e.g. "Targets" may not exist
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
                for member_tag in sorted( membership ):
                    #if member_tag in actual_group_tags: # TODO: remove when it is proved to be not needed.
                    blob += " %s=%s" % (member_tag,membership[member_tag])
                blob += '\n'
            # metadata line?
            metadata_pairs = track.get("metadata_pairs")
            if metadata_pairs is not None:
                metadata_line = ""
                for meta_tag in sorted( metadata_pairs.keys() ):
                    metadata_line += ' %s=%s' % (meta_tag.lower(),metadata_pairs[meta_tag])
                if len(metadata_line) > 0:
                    blob += "        metadata%s\n" % metadata_line

            blob += '\n'
    blob += '\n'
    return blob

def find_or_make_acc_composite(request, assembly, acc, dataset=None, hide=False, regen=False):

    ### local test: bigBed: curl http://localhost:8000/experiments/ENCSR000DZQ/@@hub/hg19/trackDb.txt
    ###             bigWig: curl http://localhost:8000/experiments/ENCSR000ADH/@@hub/mm9/trackDb.txt
    ### CHIP: https://4217-trackhub-spa-ab9cd63-tdreszer.demo.encodedcc.org/experiments/ENCSR645BCH/@@hub/GRCh38/trackDb.txt
    ### LRNA: curl https://4217-trackhub-spa-ab9cd63-tdreszer.demo.encodedcc.org/experiments/ENCSR000AAA/@@hub/GRCh38/trackDb.txt

    if not regen:
        regen = (request.url.find("regenvis") > -1) # @@hub/GRCh38/regenvis/trackDb.txt  regenvis/GRCh38 causes and error

    acc_composite = None
    es_key = acc + "_" + assembly
    if not regen: # Find composite?
        acc_composite = get_from_es(request,es_key)

    if acc_composite is None:
        if dataset is None:
            dataset = request.embed("/datasets/" + acc + '/', as_user=True)  # TODO: lower but better memory usage
            #log.warn("find_or_make_acc_composite len(results) = %d   %.3f secs" % (len(results),(time.time() - PROFILE_START_TIME)))  # DEBUG

        acc_composite = make_acc_composite(dataset, assembly, host=request.host_url, hide=hide)  # DEBUG: batch trackDb
        #if acc_composite: # TODO: force retrying empty composites
        add_to_es(request,es_key,acc_composite)
        found_or_made = "made"
    else:
        found_or_made = "found"

    ###log.warn(json.dumps(acc_composite,indent=4))

    return (found_or_made, acc_composite)


def generate_trackDb(request, dataset, assembly, hide=False, regen=False):

    acc = dataset['accession']
    (found_or_made, acc_composite) = find_or_make_acc_composite(request, assembly, dataset["accession"], dataset, hide=hide, regen=regen)
    log.warn("%s composite %s %.3f" % (found_or_made,dataset['accession'],(time.time() - PROFILE_START_TIME)))
    #del dataset
    return ucsc_trackDb_composite_blob(acc_composite,acc)

def make_set_key(param_list,assembly):
    '''Returns a key for es cache for a set of search parameters'''
    es_set_key = "assembly=%s" % assembly
    for param_key in sorted( param_list.keys() ):  # Most important to sort, to ensure 2 identical (but different order) searches) resolve
        params = sorted( param_list[param_key] )
        es_set_key += ',,' + param_key + '=' + params[0]
        if len(params) > 1:
            for param in params[1:]:
                es_set_key += '|' + str(param)
    return es_set_key

#def reduce_results(results,param_list):
    # NOTE: Not worth doing...
    # Handle file_type selections
    #if 'files.file_type' in param_list:
    #    file_types_requested = param_list['files.file_type']
    #    log.warn("Requesting file types: " + str(file_types_requested))
    #    if not isinstance(file_types_requested,list):
    #        file_types_requested = [ file_types_requested ]
    #    file_formats_requested = []
    #    for file_type in file_types_requested:
    #        file_formats_requested.append( file_type.split()[0] )
    #    log.warn("Requesting file formats: " + str(file_formats_requested))
    #    results = [
    #        result
    #        for result in results
    #        if any(
    #            f['file_format'] in file_formats_requested
    #            for f in result.get('files', [])
    #        )
    #    ]
    #return results


def generate_batch_trackDb(request, hide=False, regen=False):

    ### local test: RNA-seq: curl https://4217-trackhub-spa-ab9cd63-tdreszer.demo.encodedcc.org/batch_hub/type=Experiment,,assay_title=RNA-seq,,award.rfa=ENCODE3,,status=released,,assembly=GRCh38,,replicates.library.biosample.biosample_type=induced+pluripotent+stem+cell+line/GRCh38/trackDb.txt

    # Special logic to force remaking of trackDb
    if not regen:
        regen = (request.url.find("regenvis") > -1) # ...&assembly=hg19&regenvis/hg19/trackDb.txt  regenvis=1 causes an error
    find_or_make = "find or make"
    #regen = 5 # DEBUG
    if not regen: # Find composite?
        find_or_make = "make"

    assembly = str(request.matchdict['assembly'])
    log.warn("Request for %s trackDb begins   %.3f secs" % (assembly,(time.time() - PROFILE_START_TIME)))  # DEBUG: batch trackDb
    param_list = parse_qs(request.matchdict['search_params'].replace(',,', '&'))

    # Create an appropriate cache key
    es_set_key = make_set_key(param_list,assembly)

    # Find it?
    set_composites = None
    if not regen: # Force regeneration?
        set_composites = get_from_es(request,es_set_key)
    if set_composites is None:

        # Have to make it.
        assemblies = ASSEMBLY_MAPPINGS.get(assembly,[assembly])
        params = {
            'files.file_format': BIGBED_FILE_TYPES + BIGWIG_FILE_TYPES,
            #'status': ['released'], # TODO: Not just released!
        }
        params.update(param_list)
        params.update({
            'assembly': assemblies,
            'limit': ['all'],
            #'frame': ['embedded'], # TODO: better memory usage, but slower for acc_composites not in es (220.632secs/4.563GB for 990 exps, 73.655secs/8.210GB 1 request, 0.285 secs cache)
        })
        view = 'search'
        if 'region' in param_list:
            view = 'region-search'
        path = '/%s/?%s' % (view, urlencode(params, True))
        results = request.embed(path, as_user=True)['@graph']
        #results = reduce_results(results,param_list) # Not worth doing

        log.warn("len(results) = %d   %.3f secs" % (len(results),(time.time() - PROFILE_START_TIME)))  # DEBUG: batch trackDb

        accs = [result['accession'] for result in results] # TODO: better memory usage, but slower if acc_composite not in es
        del results                                        # TODO: better memory usage, but slower if acc_composite not in es

        acc_composites = {}
        found = 0
        made = 0
        #for dataset in results:
        #    acc = dataset['accession']
        for acc in accs:   # TODO: better memory usage, but slower if acc_composite not in es
            dataset = None # TODO: better memory usage, but slower if acc_composite not in es

            (found_or_made, acc_composite) = find_or_make_acc_composite(request, assembly, acc, dataset, hide=hide, regen=regen)
            if found_or_made == "made":
                made += 1
                #log.warn("%s composite %s" % (found_or_made,acc))
            else:
                found += 1

            acc_composites[acc] = acc_composite

            if dataset is not None:
                del dataset

        log.warn("len(acc_comosites) =  %d   %.3f secs" % (len(acc_composites),(time.time() - PROFILE_START_TIME)))  # DEBUG: batch trackDb
        set_composites = remodel_acc_to_set_composites(acc_composites, hide_after=100) # TODO: set a reasonable hide_after
        add_to_es(request,es_set_key,set_composites)
        log.warn("generated %d, found %d acc_composites   %.3f secs" % (made,found,(time.time() - PROFILE_START_TIME)))

    else:
        log.warn("Found with key %s   %.3f secs" % (es_set_key,(time.time() - PROFILE_START_TIME)))

    blob = ""
    for composite_tag in sorted( set_composites.keys() ):
        blob += ucsc_trackDb_composite_blob(set_composites[composite_tag],composite_tag)
    log.warn("Length of trackDb %d   %.3f secs" % (len(blob),(time.time() - PROFILE_START_TIME)))  # DEBUG: batch trackDb

    return blob


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
        #('trackDb', assembly + '/trackDb.txt'),  # TODO: make a decision on mm10-minimal/trackdDb.txt vs. mm10/trackDb.txt
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

    # First determine if single dataset or collection
    #log.warn("HTML request: %s" % request.url)

    html_requested = request.url.split('/')[-1].split('.')[0]
    if html_requested.startswith('ENCSR'):
        embedded = request.embed(request.resource_path(context))
        acc = embedded['accession']
        log.warn("generate_html for %s   %.3f secs" % (acc,(time.time() - PROFILE_START_TIME)))  # DEBUG
        assert( html_requested == acc)

        vis_type = get_vis_type(embedded)
        vis_defs = lookup_vis_defs(vis_type)
        longLabel = vis_defs.get('longLabel','{assay_term_name} of {biosample_term_name} - {accession}')
        longLabel = sanitize_label( convert_mask(longLabel,embedded) )

        link = request.host_url + '/experiments/' + acc + '/'
        acc_link = '<a href={link}>{accession}<a>'.format(link=link, accession=acc)
        if longLabel.find(acc) != -1:
            longLabel = longLabel.replace(acc,acc_link)
        else:
            longLabel += " - " + acc_link
        page = '<h2>%s</h2>' % longLabel

    else: # collection
        vis_type = html_requested
        vis_defs = lookup_vis_defs(vis_type)
        longLabel = vis_defs.get('assay_composite',{}).get('longLabel',"Unknown collection of experiments")
        page = '<h2>%s</h2>' % longLabel

        # TO IMPROVE: limit the search url to this assay only.  Not easy since vis_def is not 1:1 with assay
        try:
            param_list = parse_qs(request.matchdict['search_params'].replace(',,', '&'))
            search_url = '%s/search/?%s' % (request.host_url,urlencode(param_list, True))
            #search_url = (request.url).split('@@hub')[0]
            search_link = '<a href=%s>Original search<a><BR>' % search_url
            page += search_link
        except:
            pass

    # TODO: Extend page with assay specific details
    details = vis_defs.get("html_detail")
    if details is not None:
        page += details

    return page # data_description + header + file_table


def generate_batch_hubs(context, request):
    '''search for the input params and return the trackhub'''
    global PROFILE_START_TIME
    PROFILE_START_TIME = time.time()

    results = {}
    txt = request.matchdict['txt']

    if len(request.matchdict) == 3:

        # Should generate a HTML page for requests other than trackDb.txt
        if txt != TRACKDB_TXT:
            data_policy = '<br /><a href="http://encodeproject.org/ENCODE/terms.html">ENCODE data use policy</p>'
            return generate_html(context, request) + data_policy

        return generate_batch_trackDb(request)

    elif txt == HUB_TXT:
        terms = request.matchdict['search_params'].replace(',,', '&')
        pairs = terms.split('&')
        label = "search:"
        for pair in sorted( pairs ):
            (var,val) = pair.split('=')
            if var not in ["type","assembly","status","limit"]:
                label += " %s" % val.replace('+',' ')
        return NEWLINE.join(get_hub(label,request.url))
    elif txt == GENOMES_TXT:
        param_list = parse_qs(request.matchdict['search_params'].replace(',,', '&'))

        view = 'search'
        if 'region' in param_list:
            view = 'region-search'
        path = '/%s/?%s' % (view, urlencode(param_list, True))
        results = request.embed(path, as_user=True)
        log.warn("generate_batch(genomes) len(results) = %d   %.3f secs" % (len(results),(time.time() - PROFILE_START_TIME)))  # DEBUG
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

    assemblies = ''
    if 'assembly' in embedded:
        assemblies = embedded['assembly']

    if url_ret[1][1:] == HUB_TXT:
        typeof = embedded.get("assay_title")
        if typeof is None:
            typeof = embedded["@id"].split('/')[1]

        label = "%s %s" % (typeof, embedded['accession'])
        name = sanitize_name( label )
        return Response(
            NEWLINE.join(get_hub(label,request.url, name )),
            content_type='text/plain'
        )
    elif url_ret[1][1:] == GENOMES_TXT:
        g_text = get_genomes_txt(assemblies)
        return Response(g_text, content_type='text/plain')

    elif url_ret[1][1:].endswith(TRACKDB_TXT):
        parent_track = generate_trackDb(request, embedded, url_ret[1][1:].split('/')[0])
        return Response(parent_track, content_type='text/plain')
    else:
        data_policy = '<br /><a href="http://encodeproject.org/ENCODE/terms.html">ENCODE data use policy</p>'
        return Response(generate_html(context, request) + data_policy, content_type='text/html')


@view_config(route_name='batch_hub')
@view_config(route_name='batch_hub:trackdb')
def batch_hub(context, request):
    ''' View for batch track hubs '''
    return Response(generate_batch_hubs(context, request), content_type='text/plain')
