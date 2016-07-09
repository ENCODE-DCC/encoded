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

from .search import _ASSEMBLY_MAPPER


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


def render(data):
    arr = []
    for i in range(len(data)):
        temp = list(data.popitem())
        str1 = ' '.join(temp)
        arr.append(str1)
    return arr


def get_parent_track(accession, label, visibility):
    parent = OrderedDict([
        ('sortOrder', 'view=+'),
        ('type', 'bed 3'),
        ('subGroup1', 'view Views PK=Peaks SIG=Signals'),
        ('dragAndDrop', 'subTracks'),
        ('visibility', visibility),
        ('compositeTrack', 'on'),
        ('longLabel', label),
        ('shortLabel', label),
        ('track', accession)
    ])
    parent_array = render(parent)
    return NEWLINE.join(parent_array)


def get_track(f, label, parent):
    '''Returns tracks for each file'''

    file_format = 'bigWig'
    sub_group = 'view=SIG'

    if f['file_format'] in BIGBED_FILE_TYPES:
        sub_group = 'view=PK'
        file_format = 'bigBed 6 +'
        if f.get('file_format_type') == 'gappedPeak':
            file_format = 'bigBed 12 +'

    label = label + ' - {title} {format} {output}'.format(
        title=f['title'],
        format=f.get('file_format_type', ''),
        output=f['output_type']
    )

    replicate_number = 'rep unknown'
    if len(f['biological_replicates']) == 1:
        replicate_number = 'rep {rep}'.format(
            rep=str(f['biological_replicates'][0])
        )
    elif len(f['biological_replicates']) > 1:
        replicate_number = 'pooled from reps{reps}'.format(
            reps=str(f['biological_replicates'])
        )

    track = OrderedDict([
        ('subGroups', sub_group),
        ('visibility', 'dense'),
        ('longLabel', label + ' ' + replicate_number),
        ('shortLabel', f['title']),
        ('parent', parent + ' on'),
        ('bigDataUrl', '{href}?proxy=true'.format(**f)),
        ('type', file_format),
        ('track', f['title']),
    ])

    if parent == '':
        del(track['parent'])
        del(track['subGroups'])
        track_array = render(track)
        return NEWLINE.join(track_array)
    track_array = render(track)
    return (NEWLINE + (2 * TAB)).join(track_array)


def get_peak_view(accession, view):
    s_label = view + 's'
    track_name = view + 'View'
    view_data = OrderedDict([
        ('autoScale', 'on'),
        ('type', 'bigBed 6 +'),
        ('viewUi', 'on'),
        ('visibility', 'dense'),
        ('view', 'PK'),
        ('shortLabel', s_label),
        ('parent', accession),
        ('track', track_name)
    ])
    view_array = render(view_data)
    return (NEWLINE + TAB).join(view_array)


def get_signal_view(accession, view):
    s_label = view + 's'
    track_name = view + 'View'
    view_data = OrderedDict([
        ('autoScale', 'on'),
        ('maxHeightPixels', '100:32:8'),
        ('type', 'bigWig'),
        ('viewUi', 'on'),
        ('visibility', 'dense'),
        ('view', 'SIG'),
        ('shortLabel', s_label),
        ('parent', accession),
        ('track', track_name)
    ])
    view_array = render(view_data)
    return (NEWLINE + TAB).join(view_array)


def get_genomes_txt(assembly):
    # UCSC shim
    ucsc_assembly = _ASSEMBLY_MAPPER.get(assembly, assembly)
    genome = OrderedDict([
        ('trackDb', assembly + '/trackDb.txt'),
        ('genome', ucsc_assembly)
    ])
    return render(genome)


def get_hub(label):
    hub = OrderedDict([
        ('email', 'encode-help@lists.stanford.edu'),
        ('genomesFile', 'genomes.txt'),
        ('longLabel', 'ENCODE Data Coordination Center Data Hub'),
        ('shortLabel', 'Hub (' + label + ')'),
        ('hub', 'ENCODE_DCC_' + label)
    ])
    return render(hub)

# static group defs are keyed by group title (or special token) and consist of
# tag: (optional) unique terse key for referencing group
# groups: (optional) { subgroups keyed by subgroup title }
# group_order: (optional) [ ordered list of subgroup titles ]
# other definitions

# live group defs are keyed by tag and are the transformed in memory version of static defs
# title: (required) same as the static group's key
# groups: (if appropriate) { subgroups keyed by subgroup tag }
# group_order: (if appropriate) [ ordered list of subgroup tags ]
EXP_COMPOSITE_DEF_DEFAULT = {
    "longLabel":  "{assay_term_name} of {biosample_term_name} - {accession}",
    "shortLabel": "{accession}",
    "color":      "{biosample_term_name}",
    "altColor":   "{biosample_term_name}",
    "pennantIcon": "http://genome.cse.ucsc.edu/images/encodeThumbnail.jpg https://www.encodeproject.org/ \"ENCODE: Encyclopedia of DNA Elements\"",
    "sortOrder": [ "Biosample", "Targets", "Replicates", "Views" ],
    "Views":  {
        "tag": "view",
        "group_order": [ "Peaks", "Plus Signals", "Minus Signals" ],
        "groups": {
            "Peaks": {
                "tag": "PK",
                "visibility": "dense",
                "type": "bigBed",
                "file_format_type": "narrowPeak",
                "scoreFilter": "0:1",
                "spectrum": "on",
                #"output_type": [ "DHS peaks" ]
                "output_type": [ "optimal idr thresholded peaks" ]
            },
            "Plus Signals": {
                "tag": "PSIG",
                "visibility": "hide",
                "type": "bigWig",
                "viewLimits": "0:1",
                "autoScale": "off",
                "maxHeightPixels": "32:16:8",
                "windowingFunction": "mean+whiskers",
                #"output_type": [ "plus strand signal of unique reads" ]
                "output_type": [ "signal of all reads" ]
            },
            "Minus Signals": {
                "tag": "SIGM",
                "visibility": "hide",
                "type": "bigWig",
                "viewLimits": "0:1",
                "autoScale": "off",
                "negateValues": "on",
                "maxHeightPixels": "32:16:8",
                "windowingFunction": "mean+whiskers",
                "output_type": [ "minus strand signal of unique reads" ]
            }
        },
    },
    "other_groups":  {
        "dimensions": { "Biosample": "dimX", "Targets": "dimY", "Replicates": "dimA" },
        "filterComposite": { "Replicates": "multiple" }, # or "Replicates": "one"
        "groups": {
            "Replicates": {
                "tag": "REP",
                "group_order": "sort",
                "groups": {
                    "replicate": {
                        "title_mask": "Replicate_{replicate_number}", # Optional
                        #"title_mask": "{replicate}",
                        #"tag_mask": "{replicate}",  # Implicit
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
                "groups": { "one": { "title_mask": "{target.label}"} }
            }
        }
    },
    "file_defs": {
        "longLabel": "{assay_title} of {biosample_term_name} {output_type} {replicate} {experiment.accession} - {file.accession}",
        "shortLabel": "{replicate} {output_type_short_label}",
    }
}
EXP_DEFS_BY_ASSAY = {
    "RNA-seq": EXP_COMPOSITE_DEF_DEFAULT
    }

def lookup_exp_defs(exp):
    '''returns the best static composite definition set, based upon exp.'''
    assay = exp.get("assay_term_name","unknown")
    return EXP_DEFS_BY_ASSAY.get(assay, EXP_COMPOSITE_DEF_DEFAULT)

SUPPORTED_SUBGROUPS = [
    "Biosample", "Targets", "Replicates", "Views"
    ]

SUPPORTED_TRACK_SETTINGS = [
    "visibility","type","shortLabel","longLabel","scoreFilter","spectrum",
    "viewLimits","autoScale","negateValues","maxHeightPixels","windowingFunction"
    ]

SUPPORTED_MASK_TOKENS = [
    "{replicate}",         # The replicate that that will be displayed for visualized track: ("rep1", "combined") (AKA rep_tag)
    "{rep_TECH}",          # The rep_tech if desired ("rep1_1", "combined")
    "{replicate_number}",  # The replicate number displayed for visualized track: ("1", "0")
    "{biological_replicate_number}","{technical_replicate_number}",
    "{assay_title}","{assay_term_name}","{output_type}",
    "{accession}","{experiment.accession}","{file.accession}", # "{accession}" is assumed to be experiment.accession
    "{target.label}","{assay_term_name}","{biosample_term_name}",
    "{output_type_short_label}"  # hard-coded translation from output_type to very short version
    ]

OUTPUT_TYPE_7CHARS = {
    "idat green channel": "idat gr",
    "idat red channel": "idat rd",
    #"reads", # Don't bother
    "intensity values": "intense",
    "reporter code counts": "counts",
    "alignments":"aln",
    "unfiltered alignments":"unf aln",
    "transcriptome alignments":"tr aln",
    "minus strand signal of all reads":"all -",
    "plus strand signal of all reads":"all +",
    "signal of all reads":"all sig",
    "normalized signal of all reads":"normsig",
    "raw minus strand signal":"raw -",
    "raw plus strand signal":"raw +",
    "raw signal":"raw sig",
    "raw normalized signal":"nraw",
    "read-depth normalized signal":"rdnorm",
    "control normalized signal":"ctlnorm",
    "minus strand signal of unique reads":"uniq -",
    "plus strand signal of unique reads":"uniq +",
    "signal of unique reads":"uniqsig",
    "signal p-value":"pv sig",
    "fold change over control":"foldchg",
    "exon quantifications":"exon q",
    "gene quantifications":"gene q",
    "microRNA quantifications":"miRNA q",
    "transcript quantifications":"trans q",
    "library fraction":"lib fr",
    "methylation state at CpG":"mth CpG",
    "methylation state at CHG":"mth CHG",
    "methylation state at CHH":"mth CHH",
    "enrichment":"enrich",
    "replication timing profile":"rt prof",
    "variant calls":"vars",
    "filtered SNPs":"f SNPs",
    "filtered indels":"f indel",
    "hotspots":"hot sp",
    "long range chromatin interactions":"lr int",
    "chromatin interactions":"ch int",
    "topologically associated domains":"top dom",
    "genome compartments":"compart",
    "open chromatin regions":"open ch",
    "filtered peaks":"filt pk",
    "filtered regions":"filt reg",
    "DHS peaks":"DHS pk",
    #"peaks",
    "replicated peaks":"rep pk",
    "RNA-binding protein associated mRNAs":"filt reg",
    "splice junctions":"sp junk",
    "transcription start sites":"tss",
    "predicted enhancers":"pr enh",
    "candidate enhancers":"can enh",
    "candidate promoters":"can pro",
    "predicted forebrain enhancers":"fb enh",
    "predicted heart enhancers":"hrt enh",
    "predicted whole brain enhancers":"wb enh",
    "candidate regulatory elements":"can re",
    #"genome reference":"ref",
    #"transcriptome reference":"tr ref",
    #"transcriptome index":"tr rix",
    #"tRNA reference":"tRNA",
    #"miRNA reference":"miRNA",
    #"snRNA reference":"snRNA",
    #"rRNA reference":"rRNA",
    #"TSS reference":"TSS",
    #"reference variants":"var",
    #"genome index":"ref ix",
    #"female genome reference":"XX ref",
    #"female genome index":"XX rix",
    #"male genome reference":"XY ref",
    #"male genome index":"XY rix",
    #"spike-in sequence":"spike",
    "optimal idr thresholded peaks":"oIDR pk",
    "conservative idr thresholded peaks":"cIDR pk",
    "enhancer validation":"enh val",
    #"semi-automated genome annotation":"gene an"
    }

BIOSAMPLE_COLOR = {}

def lookup_color(mask,exp,altColor=False):
    '''Using the mask, determine which color table to use.'''
    color = None
    if mask == "{biosample_term_name}":
        biosample = exp.get('biosample_term_name', 'Unknown Biosample')
        color = BIOSAMPLE_COLOR.get(biosample)
    else:
        color = None
    if altColor and color is not None:
        shades = color.split('.')
        red = int(shades[0]) / 2
        green = int(shades[1]) / 2
        blue = int(shades[2]) / 2
        color = "%d.%d.%d" % (red,green.blue)
    return color


def htmlize_char(c,exceptions=[ ' ', '_' ]):
    n = ord(c)
    if n >= 47 and n <= 57: # 0-9
        return c
    if n >= 65 and n <= 90: # A-Z
        return c
    if n >= 97 and n <= 122: # a-z
        return c
    if c in exceptions:
        return c
    return "&#%s;" % n

def tag_char(c):
    n = ord(c)
    if n >= 47 and n <= 57: # 0-9
        return c
    if n >= 65 and n <= 90: # A-Z
        return c
    if n >= 97 and n <= 122: # a-z
        return c
    if n in [ 95 ]: # _
        return c
    return ""

def sanitize_label(s):
    '''Encodes the string to swap special characters and leaves spaces alone.'''
    new_s = ""
    for c in s:
        new_s += htmlize_char(c,[ ' ', '_','.','-' ])
    return new_s

def sanitize_title(s):
    '''Encodes the string to swap special characters and replace spaces with '_'.'''
    new_s = ""
    for c in s:
        if c == ' ':
            new_s += '_'
        else:
            new_s += htmlize_char(c)
    return new_s

def sanitize_tag(s):
    '''Encodes the string to swap special characters and remove spaces.'''
    #s = s.replace(" ","") # TODO: write this
    #return s
    new_s = ""
    for c in s:
        new_s += tag_char(c)
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
    assert(token in SUPPORTED_MASK_TOKENS)
    if token in ["{biosample_term_name}","{accession}","{assay_title}","{assay_term_name}"]:
        term = exp.get(token[1:-1])
        if term is None:
            term = "Unknown " + capitalize(token[1:-1].split('_')[0])
        return term
    elif token == "{experiment.accession}":
        return exp['accession']
    elif token == "{target.label}":
        return exp.get('target',{}).get('label',"Unknown Target")
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
        return "unknown" # should be an error

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
        new_mask = ""
        if beg_ix > 0:
            new_mask = working_on[0:beg_ix]
        new_mask += term + working_on[end_ix+1:]
        chars = len(working_on[end_ix+1:])
        working_on = new_mask

    return working_on


def generate_live_groups(title,group_defs,exp,rep_tags=[]):
    '''Recursively populates live (in memory) groups from static group definitions'''
    live_group = {}
    tag = group_defs.get("tag",title)
    live_group = deepcopy(group_defs) # makes sure all miscellaneous settings are transferred
    live_group["title"] = title
    live_group["tag"] = tag

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
        tag_order = sorted( rep_tags )
        live_group["group_order"] = tag_order

    elif title in ["Biosample", "Targets"]: # Single subGroup at experiment level.  No order
        live_group["groups"] = {}
        groups = group_defs.get("groups",{})
        for group_key in groups.keys():  # really should be only one
            group = group_defs["groups"][group_key]
            mask = group.get("title_mask","unknown")
            term = convert_mask(mask,exp)
            term_tag = sanitize_tag(term)
            term_title = term
            live_group["groups"][term_tag] = { "title": term_title, "tag": term_tag }
        # No tag order since only one

    # simple swapping tag and title and creating subgroups set with order
    else: # "Views", "Replicates", etc:
        # if there are subgroups, they can be handled by recursion
        if "groups" in group_defs:
            live_group["groups"]  = {}
            groups = group_defs["groups"]
            group_order = group_defs.get("group_order")
            if group_order is None or not isinstance(group_order, list):
                group_order = sorted( groups.keys() )
            tag_order = []
            for subgroup_title in group_order:
                subgroup = groups.get(subgroup_title,{})
                (subgroup_tag, subgroup) = generate_live_groups(subgroup_title,subgroup,exp) #recursive
                subgroup["tag"] = subgroup_tag
                live_group["groups"][subgroup_tag] = subgroup
                tag_order.append(subgroup_tag)
            live_group["group_order"] = tag_order

    return (tag, live_group)


def exp_composite_extend_with_tracks(composite, exp_defs, exp, assembly):
    '''Extends live experiment composite object with track definitions'''
    tracks = []
    rep_techs = {}
    files = []

    # first time through just to get rep_tech
    for view_tag in composite["view"]["group_order"]:
        view = composite["view"]["groups"][view_tag]
        output_types = view.get("output_type",[])
        file_format_types = view.get("file_format_type",[])
        file_format = view["type"]
        for a_file in exp["files"]:
            if 'assembly' not in a_file or a_file['assembly'] != assembly:
                continue
            #if file_format != a_file['file_format']:
            if a_file['file_format'] not in [ file_format, "bed" ]:
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
    if "Replicates" in exp_defs["other_groups"]["groups"]:
        group = exp_defs["other_groups"]["groups"]["Replicates"]
        group_tag = group["tag"]
        subgroups = group["groups"]
        if "replicate" in subgroups:
            (repgroup_tag, repgroup) = generate_live_groups("replicate",subgroups["replicate"],exp,rep_tags)
            # Now to hook them into the composite structure
            composite_rep_group = composite["subgroups"]["REP"]
            composite_rep_group["groups"] = repgroup.get("groups",{})
            composite_rep_group["group_order"] = repgroup.get("group_order",[])

    # second pass once all rep_techs are known
    for view_tag in composite["view"]["group_order"]:
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
            track["name"] = a_file['accession']
            track["type"] = view["type"]
            track["bigDataUrl"] = "%s?proxy=true" % a_file["href"]
            longLabel = exp_defs.get('file_defs',{}).get('longLabel')
            if longLabel is None:
                longLabel = "{assay_title} of {biosample_term_name} {output_type} {biological_replicate_number} {experiment.accession} - {file.accession}"
            track["longLabel"] = sanitize_label( convert_mask(longLabel,exp,a_file) )

            # Expecting short label to change when making assay based composites
            shortLabel = exp_defs.get('file_defs',{}).get('shortLabel')
            if shortLabel is None:
                shortLabel = "{biological_replicate_number} {output_type}"
            track["shortLabel"] = sanitize_label( convert_mask(shortLabel,exp,a_file) )
            # Inheritance should handle
            #for key in view:
            #    if key in SUPPORTED_TRACK_SETTINGS:
            #        track[key] = view[key]

            # How about subgroups!
            membership = {}
            membership["view"] = view["tag"]
            view["tracks"].append( track )  # <==== This is how we connect them to the views
            for group_tag in composite["subgroups"].keys():
                group = composite["subgroups"][group_tag]
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
                    for subgroup_tag in subgroups.keys():
                        membership[group_tag] = subgroups[subgroup_tag]["tag"]
                    #subgroups[0]["tracks"] = [ track ]
                else:
                    ### Help!
                    assert(group_tag == "Don't know this group!")

            track["membership"] = membership
            tracks.append(track)

    return tracks

def make_exp_composite(exp_defs, exp, assembly):
    '''Converts experiment composite static definitions to live composite object'''
    composite = {}
    composite["name"] = exp["accession"]

    longLabel = exp_defs.get('longLabel','{assay_term_name} of {biosample_term_name} - {accession}')
    composite['longLabel'] = sanitize_label( convert_mask(longLabel,exp) )
    shortLabel = exp_defs.get('shortLabel','{accession}')
    composite['shortLabel'] = sanitize_label( convert_mask(shortLabel,exp) )
    composite["visibility"] = exp_defs.get("visibility","full")
    composite['pennantIcon'] = exp_defs.get("pennantIcon", "encode.png")
    if "color" in exp_defs:
        color = lookup_color(exp_defs["color"],exp)
        if color is not None:
            composite["color"] = color
    if "altColor" in exp_defs:
        color = lookup_color(exp_defs["altColor"],exp,altColor=True)
        if color is not None:
            composite["altColor"] = color
    # views are always subGroup1
    composite["view"] = {}
    title_to_tag = {}
    if "Views" in exp_defs:
        ( tag, views ) = generate_live_groups("Views",exp_defs["Views"],exp)
        composite[tag] = views
        title_to_tag["Views"] = tag

    if "other_groups" in exp_defs:
        subgroups = exp_defs["other_groups"].get("groups",{})
        subgroup_ix = 2 # views are subgroup 1
        new_dimensions = {}
        new_filters = {}
        composite["subgroups_order"] = []
        composite["subgroups"] = {}
        for subgroup_title in sorted( subgroups.keys() ):
            assert(subgroup_title in SUPPORTED_SUBGROUPS)
            (subgroup_tag, subgroup) = generate_live_groups(subgroup_title,subgroups[subgroup_title],exp)
            title_to_tag[subgroup_title] = subgroup_tag
            subgroup["subgroup_ix"] = subgroup_ix
            subgroup_ix += 1
            composite["subgroups"][subgroup_tag] = subgroup
            composite["subgroups_order"].append(subgroup_tag)
            if "dimensions" in exp_defs["other_groups"]:
                dimension = exp_defs["other_groups"]["dimensions"].get(subgroup_title)
                if dimension is not None:
                    new_dimensions[dimension] = subgroup_tag
                    if "filterComposite" in exp_defs["other_groups"]:
                        filter = exp_defs["other_groups"]["filterComposite"].get(subgroup_title)
                        if filter is not None:
                            new_filters[dimension] = filter
        if len(new_dimensions) > 0:
            composite["dimensions"] = new_dimensions
        if len(new_filters) > 0:
            composite["filterComposite"] = new_filters
    if "sortOrder" in exp_defs:
        sort_order = []
        for title in exp_defs["sortOrder"]:
            sort_order.append(title_to_tag[title])
        composite["sortOrder"] = sort_order

    composite["tracks"] = exp_composite_extend_with_tracks(composite, exp_defs, exp, assembly)
    return composite

def ucsc_trackDb_composite_blob(composite):
    '''Given an in-memory composite object, prints a single UCSC trackDb.txt composite structure'''
    blob = ""
    # First the composite structure
    blob += "track %s\n" % composite["name"]
    blob += "compositeTrack on\n"
    blob += "type bed 3\n"
    for var in ["shortLabel","longLabel","visibility","pennantIcon","color","altColor"]:
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
    for group_tag in composite["subgroups_order"]:
        group = composite["subgroups"][group_tag]
        blob += "subGroup%d %s %s" % (group["subgroup_ix"], group_tag, sanitize_title(group["title"]))
        subgroup_order = group["group_order"]
        if subgroup_order is None or not isinstance(subgroup_order,list):
            subgroup_order = sorted( group["groups"].keys() )
        for subgroup_tag in subgroup_order:
            subgroup_title = group["groups"][subgroup_tag]["title"]
            blob += " %s=%s" % (subgroup_tag,sanitize_title(subgroup_title))
        blob += '\n'
    # sortOrder
    sort_order = composite.get("sortOrder")
    if sort_order:
        blob += "sortOrder"
        for sort_tag in sort_order:
            blob += " %s=+" % sort_tag
        blob += '\n'
    # dimensions
    dimensions = composite.get("dimensions")
    if dimensions:
        blob += "dimensions"
        for dim_tag in sorted( dimensions.keys() ):
            blob += " %s=%s" % (dim_tag, dimensions[dim_tag])
        blob += '\n'
    # filterComposite
    filter_composite = composite.get("filterComposite")
    if dimensions:
        blob += "filterComposite"
        for filter_tag in sorted( filter_composite.keys() ):
            blob += " %s" % filter_tag
            filter_opt = filter_composite[filter_tag]
            if filter_composite[filter_tag] == "one":
                blob += "=one"
        blob += '\n'
    blob += '\n'

    # Now cycle through views
    for view_tag in views["group_order"]:
        view = views["groups"][view_tag]
        tracks = view.get("tracks",[])
        if len(tracks) == 0:
            continue
        blob += "    track %s_%s_view\n" % (composite["name"],view["tag"])
        blob += "    parent %s\n" % composite["name"]
        blob += "    view %s\n" % view["tag"]
        for var in SUPPORTED_TRACK_SETTINGS:
            val = view.get(var)
            if val:
                blob += "    %s %s\n" % (var, val)
        blob += '\n'

        # Now cycle through tracks in view
        for track in tracks:
            blob += "        track %s\n" % (track["name"])
            blob += "        parent %s_%s_view\n" % (composite["name"],view["tag"])
            blob += "        bigDataUrl %s\n" % (track["bigDataUrl"])
            if "type" not in track:
                blob += "        type %s\n" % (view["type"])
            for var in SUPPORTED_TRACK_SETTINGS:
                val = track.get(var)
                if val:
                    blob += "        %s %s\n" % (var, val)
            # Now membership
            membership = track.get("membership")
            if membership:
                blob += "        subGroups"
                for member_tag in membership:
                    blob += " %s=%s" % (member_tag,membership[member_tag])
                blob += '\n'
            blob += '\n'
    blob += '\n'
    return blob

# Time to test test test, then...
# Next up, how to combine exp_composites

def generate_trackDb(embedded, visibility, assembly=None):

    ### local test: bigBed: curl http://localhost:8000/experiments/ENCSR000DZQ/@@hub/hg19/trackDb.txt
    ###             bigWig: curl http://localhost:8000/experiments/ENCSR000ADH/@@hub/mm9/trackDb.txt

    # Find the right defs
    exp_defs = lookup_exp_defs(embedded)
    exp_composite = make_exp_composite(exp_defs, embedded, assembly)

    ###return json.dumps(exp_composite,indent=4) + '\n'

    return ucsc_trackDb_composite_blob(exp_composite)

#    files = embedded.get('files', []) or embedded.get('related_files', [])
#
#    # checks if there is assembly specified for each experiment
#    new_files = []
#    if assembly is not None:
#        for f in files:
#            if 'assembly' in f and f['assembly'] == assembly:
#                new_files.append(f)
#    if len(new_files):
#        files = new_files
#
#    #   Datasets may have >1  assays, biosamples, or targets
#    if type(embedded.get('assay_term_name', 'Unknown')) == list:
#        assays = ', '.join(embedded['assay_term_name'])
#    else:
#        assays = embedded.get('assay_term_name', 'Unknown Assay')
#
#    #   Datasets may have >1  assays, biosamples, or targets
#    if type(embedded.get('biosample_term_name', 'Unknown')) == list:
#        biosamples = ', '.join(embedded['biosample_term_name'])
#    else:
#        biosamples = embedded.get('biosample_term_name', 'Unknown Biosample')
#
#    #   Datasets may have >1  assays, biosamples, or targets
#    if type(embedded.get('target', None)) == list:
#        targets = ', '.join([ t['label'] for t in embedded['target'] ])
#    elif embedded.get('target', None):
#        targets = embedded['target']['label']
#    else:
#        targets = ''
#
#    long_label = '{assay_term_name} of {biosample_term_name} - {accession}'.format(
#        assay_term_name=assays,
#        biosample_term_name=biosamples,
#        accession=embedded['accession']
#    )
#    if targets:
#        long_label = long_label + '(Target - {label})'.format(
#            label=targets
#        )
#    parent = get_parent_track(embedded['accession'], long_label, visibility)
#    track_label = '{assay} of {biosample} - {accession}'.format(
#        assay=assays,
#        biosample=biosamples,
#        accession=embedded['accession']
#    )
#    peak_view = ''
#    signal_view = ''
#    signal_count = 0
#    call_count = 0
#    for f in files:
#        if f['file_format'] in BIGBED_FILE_TYPES:
#            if call_count == 0:
#                peak_view = get_peak_view(
#                    embedded['accession'],
#                    embedded['accession'] + 'PK'
#                ) + NEWLINE + (2 * TAB)
#            else:
#                peak_view = peak_view + NEWLINE
#            peak_view = peak_view + NEWLINE + (2 * TAB) + get_track(
#                f, track_label,
#                embedded['accession'] + 'PKView'
#            )
#            call_count = call_count + 1
#        elif f['file_format'] == 'bigWig':
#            if signal_count == 0:
#                signal_view = get_signal_view(
#                    embedded['accession'],
#                    embedded['accession'] + 'SIG'
#                ) + NEWLINE + (2 * TAB)
#            else:
#                signal_view = signal_view + NEWLINE
#            signal_view = signal_view + NEWLINE + (2 * TAB) + get_track(
#                f, track_label,
#                embedded['accession'] + 'SIGView'
#            )
#            signal_count = signal_count + 1
#    if signal_view == '':
#        parent = parent + (NEWLINE * 2) + TAB + peak_view
#    elif peak_view == '':
#        parent = parent + (NEWLINE * 2) + TAB + signal_view
#    else:
#        parent = parent + (NEWLINE * 2) + TAB + peak_view + (NEWLINE * 2) + TAB + signal_view
#    if not parent.endswith('\n'):
#        parent = parent + '\n'
#    return parent


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
        for i, experiment in enumerate(results):
            if i < 5:
                if i == 0:
                    trackdb = generate_trackDb(experiment, 'full', None)
                else:
                    trackdb = trackdb + NEWLINE + generate_trackDb(experiment, 'full', None)
            else:
                trackdb = trackdb + NEWLINE + generate_trackDb(experiment, 'hide', None)
        return trackdb
    elif txt == HUB_TXT:
        return NEWLINE.join(get_hub('search'))
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
        return Response(
            NEWLINE.join(get_hub(embedded['accession'])),
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
        parent_track = generate_trackDb(embedded, 'full', url_ret[1][1:].split('/')[0])
        return Response(parent_track, content_type='text/plain')
    else:
        data_policy = '<br /><a href="http://encodeproject.org/ENCODE/terms.html">ENCODE data use policy</p>'
        return Response(generate_html(context, request) + data_policy, content_type='text/html')


@view_config(route_name='batch_hub')
@view_config(route_name='batch_hub:trackdb')
def batch_hub(context, request):
    ''' View for batch track hubs '''
    return Response(generate_batch_hubs(context, request), content_type='text/plain')
