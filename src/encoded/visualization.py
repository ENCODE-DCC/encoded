from pyramid.response import Response
from pyramid.view import view_config
from pyramid.compat import bytes_
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
from .vis_defines import (
    ASSEMBLY_TO_UCSC_ID,
    VISIBLE_DATASET_STATUSES,
    VISIBLE_FILE_FORMATS,
    IHEC_DEEP_DIG,
    Sanitize,
    VisDefines,
    IhecDefines,
    VisCache,
    object_is_visualizable
)
import time
from pkg_resources import resource_filename

import logging

log = logging.getLogger(__name__)
#log.setLevel(logging.DEBUG)
log.setLevel(logging.INFO)

def includeme(config):
    config.add_route('batch_hub', '/batch_hub/{search_params}/{txt}')
    config.add_route('batch_hub:trackdb', '/batch_hub/{search_params}/{assembly}/{txt}')
    config.scan(__name__)

PROFILE_START_TIME = 0  # For profiling within this module

# ASSEMBLY_FAMILIES is needed to ensure that mm10 and mm10-minimal will
#                   get combined into the same trackHub.txt
# This is necessary because mm10 and mm10-minimal are only mm10 at UCSC,
# so the 2 must be collapsed into one.
ASSEMBLY_FAMILIES = {
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

sanitize = Sanitize()

def urlpage(url):
    '''returns (page,suffix,cmd) from url: as ('track','json','regen') from ./../track.regen.json'''
    url_end = url.split('/')[-1]
    parts = url_end.split('.')
    page = parts[0]
    suffix = parts[-1] if len(parts) > 1 else 'txt'
    cmd = parts[1]     if len(parts) > 2 else ''
    return (page, suffix, cmd)


class VisCollections(object):
    # Gathers vis_datasets for remodelling and output

    def __init__(self, request, vis_datasets=None, accessions=None, assembly=None):
        self.vis_datasets = {}    # dict of vis_datasets
        self.vis_by_types = {}   # dict of assay based composites of files from vis_datasets
        self.found = 0
        self.built = 0
        self.regen_requested = False
        self.request = request
        self.page_requested = self.request.url.split('/')[-1]
        self.vis_cache = VisCache(self.request)
        self.host = self.request.host_url
        if self.host is None or self.host.find("localhost") > -1:
            self.host = "https://www.encodeproject.org"

        if vis_datasets is not None:
            self.add_to_collection(vis_datasets)
        elif accessions is not None and assembly is not None:
            self.find(accessions, assembly)

    def add_one(self, accession, vis_dataset):
        # key on accession, not vis_id... collections are always for one assembly
        self.vis_datasets[accession] = vis_dataset

    def add_to_collection(self, vis_datasets):
        if isinstance(vis_datasets, dict):
            self.vis_datasets.update(vis_datasets)
        elif isinstance(vis_datasets, list) or isinstance(vis_datasets, set):
            for vis_dataset in vis_datasets:
                if 'accession' in vis_dataset:  # NOTE: Can't add empty vis_datasets this way
                    self.add_one(vis_dataset['accession'], vis_dataset)

    def find(self, accessions, assembly):
        self.vis_by_types = {}
        self.vis_datasets = self.vis_cache.search(accessions, assembly)
        return self.vis_datasets

    def find_or_build(self, accessions, assembly, hide=False, must_build=False):
        self.vis_by_types = {}
        self.found = 0
        self.built = 0

        if not must_build:
            (page, suffix, cmd) = urlpage(self.page_requested)
            must_build = (cmd == 'regen')
        self.regen_requested = must_build

        if not must_build:
            self.vis_datasets = self.find(accessions, assembly)
            self.found = self.len()
            if self.found > 0:
                accessions = []
            # Don't bother if cache is primed.
            # if self.found < (len(accessions) * 3 / 4):  # some heuristic to decide when too few means regenerate
            #     missing = list(set(accs) - set(self.vis_datasets.keys()))

        if len(accessions) > 0:  # accessions not found in cache... try generating (for pre-primed-cache access)
            vis_factory = VisDataset(self.request)
            for accession in accessions:
                vis_dataset = vis_factory.find_or_build(accession, assembly, dataset=None, hide=hide, must_build=True)
                # vis_dataset could legitimately be {}... no visualizable files.
                if vis_factory.built:
                    self.built += 1
                else:
                    self.found += 1  # Not expecting this since find turned up empty!
                self.add_one(accession, vis_dataset)
        return self.vis_datasets

    def found_or_built(self, assays=True):
        if assays:
            return "vis_by_types: %d from %d (%d found, %d built)" % \
                    (len(self.vis_by_types), len(self.vis_datasets), self.found, self.built)
        return "%d gathered: %d found, %d built" % (len(self.vis_datasets), self.found, self.built)

    def insert_live_group(self, live_groups, new_tag, new_group):
        '''Inserts new group into a set of live groups during remodelling to vis_asset coolections.'''
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

    def remodel_to_type_collections(self, hide_after=None, prefix=None):
        '''Remoddels collection of vis_datasets to vis_by_type 'composites'.'''
        # self.vis_by_types = remodel_acc_to_set_composites(self.vis_datasets, hide_after=None)
        if not self.vis_datasets:
            return {}

        self.vis_by_types = {}
        vis_defines = VisDefines()

        for accession in sorted(self.vis_datasets.keys()):
            vis_dataset = self.vis_datasets[accession]
            if vis_dataset is None or len(vis_dataset) == 0:
                # log.debug("Found empty vis_dataset for %s" % (accession))
                self.vis_by_types[accession] = {}  # wounded vis_datasets are retained for evidence
                continue

            # Only show the first n datasets
            if hide_after is not None:
                if hide_after <= 0:
                    for track in vis_dataset.get("tracks", {}):
                        track["checked"] = "off"
                else:
                    hide_after -= 1

            # color must move to tracks because it' i's from biosample and we can mix biosample exps
            acc_color = vis_dataset.get("color")
            acc_altColor = vis_dataset.get("altColor")
            acc_view_groups = vis_dataset.get("view", {}).get("groups", {})
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

            # If vis_by_type of this vis_type doesn't exist, create it
            vis_type = vis_dataset["vis_type"]
            vis_def = vis_defines.get_vis_def(vis_type)

            assert(vis_type is not None)
            if vis_type not in self.vis_by_types.keys():  # First one so just drop in place
                vis_by_type = vis_dataset  # Don't bother with deep copy.
                set_defs = vis_def.get("assay_composite", {})
                vis_by_type["name"] = vis_type.lower()  # is there something more elegant?
                for tag in ["longLabel", "shortLabel", "visibility"]:
                    if tag in set_defs:
                        vis_by_type[tag] = set_defs[tag]  # Not expecting any token substitutions!!!
                vis_by_type['html'] = vis_type
                self.vis_by_types[vis_type] = vis_by_type

            else:  # Adding an vis_dataset to an existing vis_by_type
                vis_by_type = self.vis_by_types[vis_type]
                vis_by_type['composite_type'] = 'set'

                if vis_by_type.get("project", "unknown") != "NHGRI":
                    acc_pennant = vis_dataset["pennantIcon"]
                    set_pennant = vis_by_type["pennantIcon"]
                    if acc_pennant != set_pennant:
                        vis_by_type["project"] = "NHGRI"
                        vis_by_type["pennantIcon"] = vis_defines.pennants("NHGRI")

                # combine views
                set_views = vis_by_type.get("view", [])
                acc_views = vis_dataset.get("view", {})
                for view_tag in acc_views["group_order"]:
                    acc_view = acc_views["groups"][view_tag]
                    if view_tag not in set_views["groups"].keys():  # Should never happen
                        # log.debug("Surprise: view %s not found before" % view_tag)
                        self.insert_live_group(set_views, view_tag, acc_view)
                    else:  # View is already defined but tracks need to be appended.
                        set_view = set_views["groups"][view_tag]
                        if "tracks" not in set_view:
                            set_view["tracks"] = acc_view.get("tracks", [])
                        else:
                            set_view["tracks"].extend(acc_view.get("tracks", []))

                # All tracks in one set: not needed.

                # Combine subgroups:
                for group_tag in vis_dataset["group_order"]:
                    acc_group = vis_dataset["groups"][group_tag]
                    if group_tag not in vis_by_type["groups"].keys():  # Should never happen
                        # log.debug("Surprise: group %s not found before" % group_tag)
                        self.insert_live_group(vis_by_type, group_tag, acc_group)
                    else:  # Need to handle subgroups which definitely may not be there.
                        set_group = vis_by_type["groups"].get(group_tag, {})
                        acc_subgroups = acc_group.get("groups", {})
                        # acc_subgroup_order = acc_group.get("group_order")
                        for subgroup_tag in acc_subgroups.keys():
                            if subgroup_tag not in set_group.get("groups", {}).keys():
                                # Adding biosamples, targets, and reps
                                self.insert_live_group(set_group, subgroup_tag, acc_subgroups[subgroup_tag])

                # dimensions and filterComposite should not need any extra care:
                # they get dynamically scaled down during printing
                # log.debug("       Added.")

        if prefix is not None:
            return self.prepend_assay_labels(prefix)
        return self.vis_by_types

    def len(self, count_datasets=False):
        if count_datasets or not self.vis_by_types:
            return len(self.vis_datasets)
        return len(self.vis_by_types)

    def prepend_assay_labels(self, prefix):
        if not self.vis_by_types:
            return {}

        for vis_type in self.vis_by_types.keys():
            vis_by_type = self.vis_by_types[vis_type]
            if vis_by_type:  # could be {}
                vis_by_type['longLabel']  = "%s %s" % (prefix, vis_by_type['longLabel'])
                if vis_by_type['shortLabel'].startswith('ENCODE '):
                    vis_by_type['shortLabel'] = "ENCODE %s %s" % (prefix, vis_by_type['shortLabel'].split(None,1)[1])
                else:
                    vis_by_type['shortLabel'] = "%s %s" % (prefix, vis_by_type['shortLabel'])
        return self.vis_by_types

    def remodel_to_ihec_json(self):
        '''Formats this collection of vis_datasets into IHEC hub json structure.'''
        if not self.vis_datasets:
            return {}
        ihec = IhecDefines()
        return ihec.remodel_to_json(self.host, self.vis_datasets)

    def ucsc_trackDb(self):
        '''Formats collection into UCSC trackDb.ra text'''
        trackdb_txt = ""

        vis_defines = VisDefines()

        if self.vis_by_types:
            for tag in sorted(self.vis_by_types.keys()):
                trackdb_txt += vis_defines.ucsc_single_composite_trackDb(self.vis_by_types[tag], tag)
        else:
            for tag in sorted(self.vis_datasets.keys()):
                trackdb_txt += vis_defines.ucsc_single_composite_trackDb(self.vis_datasets[tag], tag)
        return trackdb_txt

    def stringify(self, prepend_label=None):
        '''returns string of trakDb.txt or json as appropriate.'''

        (page, suffix, cmd) = urlpage(self.page_requested)
        json_out = (suffix == 'json')                 # .../trackDb.json
        vis_json = (page == 'vis_blob' and json_out)  # .../vis_blob.json
        ihec_out = (page == 'ihec' and json_out)      # .../ihec.json

        if self.len():
            if ihec_out:
                return json.dumps(self.remodel_to_ihec_json(), indent=4, sort_keys=True)
            if vis_json:
                return json.dumps(self.vis_datasets, indent=4, sort_keys=True)
            else:
                vis_by_types = self.remodel_to_type_collections(hide_after=100)
                if prepend_label is not None:
                    vis_by_types = self.prepend_assay_labels(prepend_label)

                if json_out:
                    return json.dumps(vis_by_types, indent=4, sort_keys=True)
                else:
                    return self.ucsc_trackDb()
        return ""

class VisDataset(object):
    # Finds, builds, stores, remodels vis_blobs

    def __init__(self, request, vis_dataset=None):
        self.found = False
        self.built = False
        self.request = request
        self.page_requested = self.request.url.split('/')[-1]
        self.vis_cache = VisCache(self.request)
        self.vis_defines = None
        self.ihec = None
        self.host = self.request.host_url
        self.regen_requested = False
        if self.host is None or self.host.find("localhost") > -1:
            self.host = "https://www.encodeproject.org"

        self.vis_dataset = vis_dataset
        if self.vis_dataset:
            self.accession = self.vis_dataset['accession']
            self.assembly = self.vis_dataset['assembly']
            self.ucsc_assembly = self.vis_dataset['ucsc_assembly']
            self.vis_id = self.vis_dataset['vis_id']

    def find_or_build(self, accession, assembly, dataset=None, hide=False, must_build=False):
        self.found = False
        self.built = False
        self.vis_dataset = None
        self.dataset = dataset
        self.accession = accession
        self.assembly = assembly
        self.ucsc_assembly = ASSEMBLY_TO_UCSC_ID.get(self.assembly, self.assembly)
        self.vis_id = "%s_%s" % (self.accession, self.ucsc_assembly)  # key on normalized assembly!

        if not must_build:
            (page, suffix, cmd) = urlpage(self.page_requested)
            must_build = (cmd == 'regen')
        self.regen_requested = must_build

        # Find vis_dataset?
        if not must_build:
            self.vis_dataset = self.vis_cache.get(self.vis_id)
            if self.vis_dataset is not None:
                self.found = True
                return self.vis_dataset

        # Find dataset in order to build vis_dataset?
        if self.dataset is None:
            self.dataset = self.request.embed("/datasets/" + self.accession + '/', as_user=True)

        # Build vis_dataset?
        if self.dataset is not None:
            assert(self.accession == self.dataset['accession'])

            self.vis_dataset = self.build(hide)
            self.vis_cache.add(self.vis_id, self.vis_dataset)  # Added even if empty (valid state)
            if self.vis_dataset:
                self.built = True

        return self.vis_dataset

    def found_or_built(self, accession, assembly):
        if accession == self.accession and assembly == self.assembly:
            if self.found:
                return "found"
            elif self.built:
                return "built"
            elif self.vis_dataset == {}:
                return "built empty"
        return "unknown"

    def handle_negate_values(self, live_format, vis_dataset):
        '''If negateValues is set then adjust some settings like color'''
        if live_format.get("negateValues", "off") == "off":
            return

        # need to swap color and altColor
        color = live_format.get("color", vis_dataset.get("color"))
        if color is not None:
            altColor = live_format.get("altColor", vis_dataset.get("altColor", color))
            live_format["color"] = altColor
            live_format["altColor"] = color

        # view limits need to change because numbers are all negative
        view_limits = live_format.get("viewLimits")
        if view_limits is not None:
            low_high = view_limits.split(':')
            if len(low_high) == 2:
                live_format["viewLimits"] = "%d:%d" % (int(low_high[1]) * -1, int(low_high[0]) * -1)
        view_limits_max = live_format.get("viewLimitsMax")
        if view_limits_max is not None:
            low_high = view_limits_max.split(':')
            if len(low_high) == 2:
                live_format["viewLimitsMax"] = ("%d:%d" %
                                                (int(low_high[1]) * -1, int(low_high[0]) * -1))

    def format_groups(self, title, group_defs, rep_tags=[]):
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

        elif title in ["Biosample", "Targets", "Assay", "Experiment"]:
            groups = group_defs.get("groups", {})
            assert(len(groups) == 1)
            for (group_key, group) in groups.items():
                mask = group.get("title_mask")
                if mask is not None:
                    term = self.vis_defines.convert_mask(mask)
                    if not term.startswith('Unknown '):
                        term_tag = sanitize.tag(term)
                        term_title = term
                        live_group["groups"] = {}
                        live_group["groups"][term_tag] = {"title": term_title, "tag": term_tag}
                        mask = group.get("url_mask")
                        if mask is not None:
                            term = self.vis_defines.convert_mask(mask)
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
                    (subgroup_tag, subgroup) = self.format_groups(subgroup_title, subgroup)  # recursive
                    subgroup["tag"] = subgroup_tag
                    if isinstance(preferred_order, list):
                        preferred_order.append(subgroup_tag)
                    if title == "Views":
                        assert(subgroup_title != subgroup_tag)
                        self.handle_negate_values(subgroup, self.vis_dataset)
                    live_group["groups"][subgroup_tag] = subgroup
                    tag_order.append(subgroup_tag)
                # assert(len(live_group["groups"]) == len(groups))
                if len(live_group['groups']) != len(groups):
                    log.debug("len(live_group['groups']):%d != len(groups):%d" %
                            (len(live_group['groups']), len(groups)))
                    log.debug(json.dumps(live_group, indent=4))
                live_group["group_order"] = tag_order
                live_group["preferred_order"] = preferred_order

        return (tag, live_group)

    def build_views_and_groups(self):
        '''Extends vis_dataset with formatted views and groups'''

        groupings = {}
        groupings["view"] = {}
        title_to_tag = {}
        if "Views" in self.vis_def:
            (tag, views) = self.format_groups("Views", self.vis_def["Views"])
            groupings[tag] = views
            title_to_tag["Views"] = tag

        if "other_groups" in self.vis_def:
            groups = self.vis_def["other_groups"].get("groups", {})
            new_dimensions = {}
            new_filters = {}
            groupings["group_order"] = []
            groupings["groups"] = {}
            group_order = self.vis_def["other_groups"].get("group_order")
            preferred_order = []  # have to create preferred order based upon tags, not titles
            if group_order is None or not isinstance(group_order, list):
                group_order = sorted(groups.keys())
                preferred_order = "sorted"
            for subgroup_title in group_order:  # Replicates, Targets, Biosamples
                if subgroup_title not in groups:
                    continue
                assert(subgroup_title in self.vis_defines.supported_subgroups())
                (subgroup_tag, subgroup) = self.format_groups(subgroup_title,
                                                                groups[subgroup_title])
                if isinstance(preferred_order, list):
                    preferred_order.append(subgroup_tag)
                if "groups" in subgroup and len(subgroup["groups"]) > 0:
                    title_to_tag[subgroup_title] = subgroup_tag
                    groupings["groups"][subgroup_tag] = subgroup
                    groupings["group_order"].append(subgroup_tag)
                if "dimensions" in self.vis_def["other_groups"]:  # (empty) "Targets" dim will be included
                    dimension = self.vis_def["other_groups"]["dimensions"].get(subgroup_title)
                    if dimension is not None:
                        new_dimensions[dimension] = subgroup_tag
                        if "filterComposite" in self.vis_def["other_groups"]:
                            filterfish = self.vis_def["other_groups"]["filterComposite"].get(subgroup_title)
                            if filterfish is not None:
                                new_filters[dimension] = filterfish
            groupings["preferred_order"] = preferred_order
            if len(new_dimensions) > 0:
                groupings["dimensions"] = new_dimensions
            if len(new_filters) > 0:
                groupings["filterComposite"] = new_filters
            if "dimensionAchecked" in self.vis_def["other_groups"]:
                groupings["dimensionAchecked"] = self.vis_def["other_groups"]["dimensionAchecked"]

        if "sortOrder" in self.vis_def:
            sort_order = []
            for title in self.vis_def["sortOrder"]:
                if title in title_to_tag:
                    sort_order.append(title_to_tag[title])
            groupings["sortOrder"] = sort_order

        return groupings

    def biosamples_for_file(self, a_file, file_dataset):
        '''Returns a dict of biosamples for file.'''
        biosamples = {}
        replicates = file_dataset.get("replicates")
        if not replicates or not isinstance(replicates[0], dict):
            return []

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

    def replicates_pair(self, a_file):
        '''Returns (title, value) for file's replicate ("replicates (bio_tech)","1_1, 2_1")'''
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
        return (rep_key, rep_val)

    def gather_files_and_reps(self):
        '''Returns visulaizable files and replicate tags from a first pass through dataset's files.'''
        files = []
        rep_techs = {}
        ucsc_assembly = self.vis_dataset['ucsc_assembly']

        group_order = self.vis_dataset["view"].get("group_order", [])
        for view_tag in group_order:
            view = self.vis_dataset["view"]["groups"][view_tag]
            output_types = view.get("output_type", [])
            file_format_types = view.get("file_format_type", [])
            file_format = view["type"].split()[0]
            if file_format == "bigBed":
                format_type = view.get('file_format_type','')
                if format_type == 'bedMethyl' or "itemRgb" in view:
                    view["type"] = "bigBed 9 +"  # itemRgb implies at least 9 +
                elif format_type  == 'narrowPeak':
                    view["type"] = "bigNarrowPeak"
                elif format_type == 'broadPeak' or "scoreFilter" in view:
                    view["type"] = "bigBed 6 +"  # scoreFilter implies score so 6 +
            #log.debug("%d files looking for type %s" % (len(dataset["files"]),view["type"]))
            for a_file in self.dataset["files"]:
                if a_file['status'] not in self.vis_defines.visible_file_statuses():
                    continue
                if file_format != a_file['file_format']:
                    continue
                if len(output_types) > 0 and a_file.get('output_type', 'unknown') not in output_types:
                    continue
                if len(file_format_types) > 0 and \
                a_file.get('file_format_type', 'unknown') not in file_format_types:
                    continue
                if 'assembly' not in a_file or \
                    ASSEMBLY_TO_UCSC_ID.get(a_file['assembly'], a_file['assembly']) != ucsc_assembly:
                    continue
                if "rep_tech" not in a_file:
                    rep_tech = self.vis_defines.rep_for_file(a_file)
                    a_file["rep_tech"] = rep_tech
                else:
                    rep_tech = a_file["rep_tech"]
                rep_techs[rep_tech] = rep_tech
                files.append(a_file)
        if len(files) == 0:
            log.debug("No visualizable files for %s %s" % (self.dataset["accession"], self.vis_dataset["vis_type"]))
            return (None, None)

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
        other_groups = self.vis_def.get("other_groups", []).get("groups", [])
        if "Replicates" in other_groups:
            group = other_groups["Replicates"]
            group_tag = group["tag"]
            subgroups = group["groups"]
            if "replicate" in subgroups:
                (repgroup_tag, repgroup) = self.format_groups("replicate", subgroups["replicate"], rep_tags)
                # Now to hook them into the vis_dataset structure
                self.vis_dataset["groups"]["REP"]["groups"] = repgroup.get("groups", {})
                self.vis_dataset["groups"]["REP"]["group_order"] = repgroup.get("group_order", [])

        return (files, rep_techs)

    def build_file_tracks(self):
        '''Extends vis_dataset with formatted files (aka tracks)'''

        # first gather just the relevant files from the dataset and distill the replicate tags
        (files, rep_techs) = self.gather_files_and_reps()
        if files is None:
            return None

        if IHEC_DEEP_DIG:
            self.gather_pipeline_details()  # for IHEC

        # No we can go through the files again to build tracks
        tracks = []
        if self.host is None:
            self.host = "https://www.encodeproject.org"
        for view_tag in self.vis_dataset["view"].get("group_order", []):
            view = self.vis_dataset["view"]["groups"][view_tag]
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
                files_dataset = self.dataset
                if 'dataset' in a_file and isinstance(a_file['dataset'],dict):
                    files_dataset = a_file['dataset']
                track["name"] = a_file['accession']
                format_type = a_file.get('file_format_type','?')
                if format_type == 'bedMethyl' or "itemRgb" in view:
                    view["type"] = "bigBed 9 +"  # itemRgb implies at least 9 +
                elif format_type  == 'narrowPeak':
                    view["type"] = "bigNarrowPeak"
                elif format_type == 'broadPeak' or "scoreFilter" in view:
                    view["type"] = "bigBed 6 +"  # scoreFilter implies score so 6 +
                track["type"] = view["type"]
                track["bigDataUrl"] = "%s?proxy=true" % a_file["href"]
                longLabel = self.vis_def.get('file_defs', {}).get('longLabel')
                if longLabel is None:
                    longLabel = ("{assay_title} of {biosample_term_name} {output_type} "
                                "{biological_replicate_number}")
                longLabel += " {experiment.accession} - {file.accession}"  # Always add the accessions
                track["longLabel"] = sanitize.label(self.vis_defines.convert_mask(longLabel, files_dataset, a_file))
                # Specialized addendum comments because subtle details alway get in the way of elegance.
                addendum = ""
                submitted_name = a_file.get('submitted_file_name', "none")
                if "_tophat" in submitted_name:
                    addendum = addendum + 'TopHat,'
                if a_file.get('assembly', self.assembly) == 'mm10-minimal':
                    addendum = addendum + 'mm10-minimal,'
                if len(addendum) > 0:
                    track["longLabel"] = track["longLabel"] + " (" + addendum[0:-1] + ")"

                metadata_pairs = {}
                metadata_pairs['file&#32;download'] = ( \
                    '"<a href=\'%s%s\' title=\'Download this file from the ENCODE portal\'>%s</a>"' %
                    (self.host, a_file["href"], a_file["accession"]))
                lab = self.vis_defines.convert_mask("{lab.title}")
                if len(lab) > 0 and not lab.startswith('unknown'):
                    metadata_pairs['laboratory'] = '"' + sanitize.label(lab) + '"'  # 'lab' is UCSC word
                (rep_key, rep_val) = self.replicates_pair(a_file)
                if rep_key != "":
                    metadata_pairs[rep_key] = '"' + rep_val + '"'

                # Expecting short label to change when making assay based vis formats
                shortLabel = self.vis_def.get('file_defs', {}).get('shortLabel',
                                                            "{replicate} {output_type_short_label}")
                track["shortLabel"] = sanitize.label(self.vis_defines.convert_mask(shortLabel, files_dataset, a_file))

                # How about subgroups!
                membership = {}
                membership["view"] = view["tag"]
                view["tracks"].append(track)  # <==== This is how we connect them to the views
                if view['type'] == 'bigNarrowPeak':
                    view.pop('scoreFilter',None)  # TODO The vis_defs should be changed
                    # TODO indivudual vis_defs should have signalFilter, pValueFilter and qValueFilter added as appropriate
                    if 'signalFilter' not in view:  # NOTE: UCSC is giving warning if no signalFilter!
                        view['signalFilter'] = "0"
                    #view['signalFilterLimits'] = "0:18241"  # DEBUG DEBUG

                for (group_tag, group) in self.vis_dataset["groups"].items():
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
                    elif group_title in ["Biosample", "Targets", "Assay", "Experiment"]:
                        assert(len(subgroups) == 1)
                        # if len(subgroups) == 1:
                        for (subgroup_tag, subgroup) in subgroups.items():
                            membership[group_tag] = subgroup["tag"]
                            if "url" in subgroup:
                                metadata_pairs[group_title] = ( \
                                    '"<a href=\'%s/%s/\' TARGET=\'_blank\' title=\'%s details at the ENCODE portal\'>%s</a>"' %
                                    (self.host, subgroup["url"], group_title, subgroup["title"]))
                            elif group_title == "Biosample":
                                bs_value = sanitize.label(files_dataset.get("biosample_summary", ""))
                                if len(bs_value) == 0:
                                    bs_value = subgroup["title"]
                                biosamples = self.biosamples_for_file(a_file, files_dataset)
                                if len(biosamples) > 0:
                                    for bs_acc in sorted(biosamples.keys()):
                                        bs_value += ( \
                                            " <a href=\'%s%s\' TARGET=\'_blank\' title=\' %s details at the ENCODE portal\'>%s</a>" %
                                            (self.host, biosamples[bs_acc]["@id"], group_title,
                                                    bs_acc))
                                metadata_pairs[group_title] = '"%s"' % (bs_value)
                            else:
                                metadata_pairs[group_title] = '"%s"' % (subgroup["title"])
                    else:
                        assert(group_tag == "Don't know this group!")

                if IHEC_DEEP_DIG:
                    self.add_pipeline_details(a_file, track)  # pipeline details per track for IHEC
                track['md5sum'] = a_file['md5sum']

                track["membership"] = membership
                if len(metadata_pairs):
                    track["metadata_pairs"] = metadata_pairs

                tracks.append(track)

        return tracks

    def gather_pipeline_details(self):
        '''At the dataset level, gathers all pipeline and aligner deets needed for IHEC'''
        self.aligners = {}
        self.pipelines = {}
        ucsc_assembly = self.vis_dataset['ucsc_assembly']
        software_files = {}  # { sw_key: {file_accession: rep_tech} }
        pipeline_files = {}  # { pipe_key: {file_accession: rep_tech} }
        for a_file in self.dataset["files"]:
            if a_file['status'] not in self.vis_defines.visible_file_statuses():
                continue
            if 'assembly' not in a_file or \
                ASSEMBLY_TO_UCSC_ID.get(a_file['assembly'], a_file['assembly']) != ucsc_assembly:
                continue
            step_ver = a_file.get("analysis_step_version")  # this embedding could evaporate
            file_acc = a_file['accession']
            if not step_ver:
                continue  # can't tell anything without step versions!
            if isinstance(step_ver, str):
                continue  # TODO: Lookup step_version?

            if 'bam' == a_file['file_format']:
                # now we should have a relevant file
                sw_versions = step_ver.get('software_versions')
                if sw_versions is not None:
                    if "rep_tech" not in a_file:
                        rep_tech = self.vis_defines.rep_for_file(a_file)
                        a_file["rep_tech"] = rep_tech
                    for swv_key in sw_versions:
                        if swv_key not in software_files:
                            software_files[swv_key] = { a_file['@id']: a_file["rep_tech"] }
                        else:
                            software_files[swv_key][a_file['@id']] = a_file["rep_tech"]
            if a_file['file_format'] in VISIBLE_FILE_FORMATS:
                # Looking for pipeline details
                a_step = step_ver['analysis_step']
                if not isinstance(a_step, dict):
                    continue # TODO: Lookup analysis_step?
                pipes = a_step.get("pipelines")
                if not pipes or not isinstance(pipes, list) or len(pipes) == 0:
                    continue # TODO: Lookup pipeline?
                for a_pipe in pipes:
                    pipe_key = a_pipe['@id']
                    pipe = {}
                    if pipe_key not in pipeline_files:
                        pipe['title'] = a_pipe.get('title')
                        pipe['version'] = '1'
                        pipe['lab'] = a_file.get('lab',{}).get('title','unknown')
                        #pipe['lab'] = a_pipe.get("lab",'unknown')
                        #if pipe['lab'].startswith('/labs/'):
                        #    pipe['lab'] = pipe['lab'][6:-1]
                        if pipe['title']:
                            if 'version' in pipe['title'].lower():  # REALLY LESS THAN IDEAL
                                pipe['version'] = pipe['title'].lower().split('version')[-1].strip()
                        pipe['files'] = [ a_file['@id'] ]
                        pipeline_files[pipe_key] = pipe
                    else:
                        pipeline_files[pipe_key]['files'].append(a_file['@id'])

        if software_files:
            aligners = {'files': {}, 'rep_techs': {}}
            # TODO: software_type='aligner' is weakly associated!
            # Note: lab!=/labs/encode-processing-pipeline/ should eliminate analysis_steps themselves
            params = { 'type': 'SoftwareVersion', 'software.software_type': 'aligner', '@id': software_files.keys() }
            path = '/search/?%s&software.lab!=/labs/encode-processing-pipeline/&frame=embedded' % (urlencode(params, True))
            results = self.request.embed(path, as_user=True)['@graph']
            # More than one for some: LRNA (star v. tophat)
            for sw_version in results:
                swv_key = sw_version['@id']
                #sw_files = software_files[swv_key].keys()
                aligner = { 'name':sw_version['software']['name'], 'version': sw_version['version']}
                aligner_key = aligner['name'].lower()
                if 'default' not in aligners:
                    aligners['default'] = { aligner_key: aligner }
                elif aligner_key not in aligners['default'] or \
                     aligners['default'][aligner_key]['version'] < aligner['version']:
                    aligners['default'][aligner_key] = aligner
                for file_id in software_files[swv_key].keys():
                    rep_tech = software_files[swv_key][file_id]
                    if file_id not in aligners['files']:
                        aligners['files'][file_id] = aligner
                    elif aligners['files'][file_id]['name'] == aligner['name']:
                        if aligners['files'][file_id]['version'] < aligner['version']:
                            aligners['files'][file_id] = aligner
                    #else:  # one bam file 2 aligners, not likely
                    if rep_tech not in aligners['rep_techs']:
                        aligners['rep_techs'][rep_tech] = { aligner_key: aligner }
                    elif aligner_key not in aligners['rep_techs'][rep_tech] or \
                         aligners['rep_techs'][rep_tech][aligner_key]['version'] < aligner['version']:
                        aligners['rep_techs'][rep_tech][aligner_key] = aligner

            self.aligners = aligners
            #aligners = { 'file': {ENCFF000AAA: {name:'STAR': version:'2.5.1a'},..., 'rep_tech': rep1_1: {'star': {'STAR': '2.5.1a'},'tophat':...} }
        if pipeline_files:
            pipelines =  {}
            for pipe_key in pipeline_files.keys():
                pipe = pipeline_files[pipe_key]
                pipe_files = pipe.pop('files')
                for file_id in pipe_files:
                    if file_id not in pipelines or pipe['version'] > pipelines[file_id]['version']:
                        pipelines[file_id] = pipe
            #pipelines = {ENCFF000AAA: {title: 'RNA pipeline', version: 2, lab:'ENCODE DCC'},...}
            self.pipelines = pipelines

    def add_pipeline_details(self, a_file, track):
        '''At the track level, look up previously gathered details for IHEC'''
        # plumbing for ihec
        if self.aligners:
            # go through derived_from to find aligner, if not found then hope rep_tech works
            for file_id in a_file.get('derived_from',[]):
                # easy way: when bam is in derived_from and aligner is associated with bam
                if file_id in self.aligners['files']:
                    track['aligner'] = self.aligners['files'][file_id]
                    break
            if 'aligner' not in track:
                # hard way: more than one possibility so match on first or if submitted name helps
                possible_aligners = {}
                if a_file['rep_tech'] in self.aligners['rep_techs']:
                    possible_aligners = self.aligners['rep_techs'][a_file['rep_tech']]
                elif 'default' in self.aligners:
                    possible_aligners = self.aligners['default']
                if possible_aligners:
                    submitted_name = a_file.get('submitted_file_name', "none")
                    for aligner_key in possible_aligners.keys():  # e.g. 'tophat' in '..._tophat.bw'
                        if 'aligner' not in track or aligner_key in submitted_name:
                            track['aligner'] = possible_aligners[aligner_key]
            if 'aligner' in track:
                # after all this: IHEC only allows one aligner per experiment!
                self.vis_dataset['aligner'] = track['aligner']
            if 'aligner' not in self.vis_dataset and 'default' in self.aligners \
                and len(self.aligners['default'].keys()) >= 1:
                    track['aligner'] = self.aligners['default'][self.aligners['default'].keys()[0]]

        if self.pipelines:
            for file_id in self.pipelines.keys():
                pipe = self.pipelines[file_id]
                if file_id == a_file['@id']:
                    track['pipeline'] = pipe
                if 'pipeline' not in self.vis_dataset or \
                    pipe['version'] > self.vis_dataset['pipeline']['version']:
                    self.vis_dataset['pipeline'] = pipe

        # Use step_ver to get at pipeline, but different files may be from different steps!
        step_ver = a_file.get("analysis_step_version")  # this embedding could evaporate
        if not step_ver:
            return  # We tried
        if isinstance(step_ver, str):
            track['step_version'] = step_ver.split('/')[1]
            return

        # Use analysis_step to get at pipeline, but different files may be from different steps!
        track['step_version'] = step_ver.get('name','')
        analysis_step = step_ver.get("analysis_step")
        if not analysis_step:
            return  # oh well
        if not isinstance(analysis_step, dict):
            track['analysis_step'] = analysis_step.split('/')[1]
        else:
            track['analysis_step'] = analysis_step.get('title','')
        return

    def build(self, hide):
        '''Converts embedded dataset into a vis_dataset'''

        if self.dataset["status"] not in VISIBLE_DATASET_STATUSES:
            log.debug("%s can't be visualized because it's not unreleased status:%s." %
                    (self.dataset["accession"], self.dataset["status"]))
            return {}
        self.vis_defines = VisDefines(self.dataset)
        vis_type = self.vis_defines.get_vis_type()
        self.vis_def = self.vis_defines.get_vis_def(vis_type)
        if self.vis_def is None:
            log.debug("%s (vis_type: %s) has undiscoverable vis_defs." %
                    (self.dataset["accession"], vis_type))
            return {}
        self.vis_dataset = {}
        # log.debug("%s has vis_type: %s." % (self.dataset["accession"],vis_type))
        self.vis_dataset["vis_type"] = vis_type
        self.vis_dataset["name"] = self.accession

        self.vis_dataset['assembly'] = self.assembly
        self.vis_dataset['ucsc_assembly'] = self.ucsc_assembly
        self.vis_dataset["vis_id"]  = self.vis_id

        for term in self.vis_defines.encoded_dataset_terms():
            val = self.vis_defines.lookup_embedded_token(term, self.dataset)
            if val is not None:
                self.vis_dataset[term] = val

        if self.ihec is None:
            self.ihec = IhecDefines()
        ihec_exp_type = self.ihec.exp_type(vis_type, self.dataset)
        if ihec_exp_type is not None:
            self.vis_dataset['ihec_exp_type'] = ihec_exp_type
            self.vis_dataset['ihec_sample'] = self.ihec.sample(self.dataset, self.vis_defines)
        #self.vis_dataset['molecule'] = self.ihec.molecule(self.dataset)
        #biosample = self.vis_defines.lookup_embedded_token('replicates.library.biosample', self.dataset)
        #if biosample is not None:
        #    lineage = self.ihec.lineage(biosample)
        #    if lineage is not None:
        #        self.vis_dataset['lineage'] = lineage
        #    differentiation = self.ihec.differentiation(biosample)
        #    if differentiation is not None:
        #        self.vis_dataset['differentiation'] = differentiation

        longLabel = self.vis_def.get('longLabel','{assay_term_name} of {biosample_term_name} - {accession}')
        self.vis_dataset['longLabel'] = sanitize.label(self.vis_defines.convert_mask(longLabel))
        shortLabel = self.vis_def.get('shortLabel', '{accession}')
        self.vis_dataset['shortLabel'] = sanitize.label(self.vis_defines.convert_mask(shortLabel))
        if hide:
            self.vis_dataset["visibility"] = "hide"
        else:
            self.vis_dataset["visibility"] = self.vis_def.get("visibility", "full")
        self.vis_dataset['pennantIcon'] = self.vis_defines.find_pennent()
        self.vis_defines.add_living_color(self.vis_dataset)

        # Add in all the messy grouping
        groupings = self.build_views_and_groups()
        self.vis_dataset.update(groupings)

        tracks = self.build_file_tracks()
        if tracks is None or len(tracks) == 0:
            # Already warned about files log.debug("No tracks for %s" % self.dataset["accession"])
            return {}
        self.vis_dataset["tracks"] = tracks
        return self.vis_dataset

    def len(self):
        if self.vis_dataset:
            return len(json.dumps(self.vis_dataset))
        return 0

    def vis_type(self):
        if self.vis_dataset:
            vis_type = self.vis_dataset.get("vis_type")
        if vis_type is None and self.dataset is not None:
            vis_type = VisDefines(self.dataset).get_vis_type()
        if vis_type is None:
            vis_type = 'unknown'
        return vis_type

    def as_collection(self):
        # formats the single vis_dataset dict as a collection dict
        if self.vis_dataset is not None:
            return {self.accession: self.vis_dataset} # NOTE: accession not vis_id, collections are always  one assembly
        return {}

    def remodel_to_ihec_json(self):
        '''Formats single vis_dataset into IHEC json'''
        # TODO: make ihec json work!
        collection_of_one = self.as_collection()
        if collection_of_one:
            return VisCollections(self.request, collection_of_one).remodel_to_ihec_json()
        return {}

    def ucsc_trackDb(self):
        '''Formats single vis_dataset into UCSC trackDb.ra text'''
        if self.vis_defines is None:
            self.vis_defines = VisDefines()
        return self.vis_defines.ucsc_single_composite_trackDb(self.vis_dataset, self.accession)
        #vis_collection = VisCollections(self.request, {self.accession: self.vis_dataset})
        #return vis_collection.ucsc_trackDb()

    def stringify(self):
        '''returns string of trakDb.txt or json as appropriate.'''

        (page, suffix, cmd) = urlpage(self.page_requested)
        json_out = (suffix == 'json')                 # .../trackDb.json
        vis_json = (page == 'vis_blob' and json_out)  # .../vis_blob.json
        ihec_out = (page == 'ihec' and json_out)      # .../ihec.json

        if ihec_out:
            return json.dumps(self.remodel_to_ihec_json(), indent=4, sort_keys=True)
        if vis_json:
            return json.dumps(self.vis_dataset, indent=4, sort_keys=True)
        elif json_out:
            return json.dumps(self.as_collection(), indent=4, sort_keys=True)

        return self.ucsc_trackDb()


def vis_cache_add(request, dataset):
    '''For a single embedded dataset, builds and adds vis_dataset to es cache for each relevant assembly.'''
    if not object_is_visualizable(dataset, exclude_quickview=True):
        return []

    accession = dataset['accession']
    assemblies = dataset['assembly']

    vis_datasets = []
    vis_factory = VisDataset(request)
    for assembly in assemblies:
        vis_dataset = vis_factory.find_or_build(accession, assembly, dataset, must_build=True)
        if vis_dataset:  # Don't bother caching empties (e.g. {} == no visualizable files).
            vis_datasets.append(vis_dataset)
            log.debug("primed vis_cache with vis_dataset %s '%s'" %
                        (vis_factory.vis_id, vis_factory.vis_type))

    return vis_datasets


def generate_trackDb(request, dataset, assembly, hide=False, regen=False):
    '''Returns string content for a requested  single experiment trackDb.txt.'''
    # local test: bigBed: curl http://localhost:8000/experiments/ENCSR000DZQ/@@hub/hg19/trackDb.txt
    #             bigWig: curl http://localhost:8000/experiments/ENCSR000ADH/@@hub/mm9/trackDb.txt
    # CHIP: https://.../experiments/ENCSR645BCH/@@hub/GRCh38/trackDb.txt
    # LRNA: curl https://.../experiments/ENCSR000AAA/@@hub/GRCh38/trackDb.txt

    accession = dataset['accession']

    # If we could detect this as a series dataset, then we could treat this as a batch_trackDb
    if set(['Experiment', 'Annotation']).isdisjoint(dataset['@type']) and \
          not set(['Series', 'FileSet']).isdisjoint(dataset['@type']):
        return generate_set_trackDb(request, accession, dataset, assembly, hide, regen)

    vis_factory = VisDataset(request)
    vis_dataset = vis_factory.find_or_build(accession, assembly, dataset, hide, must_build=regen)

    msg = "%s vis_dataset %s %s len(json):%d %.3f" % (vis_factory.found_or_built(accession, assembly),
                 vis_factory.vis_id, vis_factory.vis_type, vis_factory.len(),
                 (time.time() - PROFILE_START_TIME))
    if vis_factory.regen_requested:  # Want to see message if regen was requested
        log.info(msg)
    else:
        log.debug(msg)

    return vis_factory.stringify()


def generate_by_accessions(request, accessions, assembly, hide, regen, prepend_label=None):
    '''Actual generation of trackDb for collections (batch and file_sets).'''

    vis_collection = VisCollections(request)
    vis_datasets = vis_collection.find_or_build(accessions, assembly, hide, must_build=regen)

    blob = vis_collection.stringify(prepend_label)

    msg = "%s. len(txt):%s  %.3f secs" % \
                 (vis_collection.found_or_built(), len(blob), (time.time() - PROFILE_START_TIME))
    if vis_collection.regen_requested:  # Want to see message if regen was requested
        log.info(msg)
    else:
        log.debug(msg)

    return blob


def generate_set_trackDb(request, accession, dataset, assembly, hide=False, regen=False):
    '''Handles 'Series' and 'FileSet' dataset types similar to search results.'''

    sub_accessions = []
    related_datasets = []
    if 'FileSet' in dataset['@type'] and 'files' in dataset:
        files = dataset['files']
        if len(files) > 0 and not isinstance(files[0],str):
            try:
                related_datasets = [ file['dataset'] for file in files ]
            except:
                pass # caught below
            # Note: should be able to get
    elif 'Series' in dataset['@type'] and 'related_datasets' in dataset:
        # Note that 'Series' don't actually reach here yet because they are rejected higher up for having no files.
        related_datasets = dataset['related_datasets']
    if len(related_datasets) > 0:
        try:
            if isinstance(related_datasets[0],dict):
                sub_accessions = [ related['accession'] for related in related_datasets ]
            else:
                sub_accessions = [ related.split('/')[1] for related in related_datasets ]
        except:
            pass # caught below
    sub_accessions = list(set(sub_accessions)) # Only unique accessions need apply
    if len(sub_accessions) == 0:
        log.error("failed to find true datasets for files in collection %s" % accession)
        return ""

    return generate_by_accessions(request, sub_accessions, assembly, hide, regen, prepend_label=accession)


def generate_batch_trackDb(request, hide=False, regen=False):
    '''Returns string content for a requested multi-experiment trackDb.txt.'''
    # local test: RNA-seq: curl https://../batch_hub/type=Experiment,,assay_title=RNA-seq,,award.rfa=ENCODE3,,status=released,,assembly=GRCh38,,replicates.library.biosample.biosample_type=induced+pluripotent+stem+cell+line/GRCh38/trackDb.txt

    assembly = str(request.matchdict['assembly'])
    log.debug("Request for %s trackDb begins   %.3f secs" %
              (assembly, (time.time() - PROFILE_START_TIME)))
    param_list = parse_qs(request.matchdict['search_params'].replace(',,', '&'))

    # Have to make it.
    assemblies = ASSEMBLY_FAMILIES.get(assembly, [assembly])
    params = {
        'files.file_format': VISIBLE_FILE_FORMATS,
    }
    params.update(param_list)
    params.update({
        'assembly': assemblies,
        'limit': ['all'],
    })
    params['frame'] = ['object']

    view = 'search'
    if 'region' in param_list:
        view = 'region-search'
    path = '/%s/?%s' % (view, urlencode(params, True))
    results = request.embed(path, as_user=True)['@graph']
    # Note: better memory usage to get accession array from non-embedded results,
    # since acc_composites should be in cache
    accessions = [result['accession'] for result in results]
    del results

    return generate_by_accessions(request, accessions, assembly, hide, regen)


#def readable_time(secs_float):
#    '''Return string of days, hours, minutes, seconds'''
#    intervals = [1, 60, 60*60, 60*60*24]
#    terms = [('second', 'seconds'), ('minute', 'minutes'), ('hour', 'hours'), ('day', 'days')]
#
#    amount = int(secs_float)
#    msecs = int(round(secs_float * 1000) - (amount * 1000))
#
#    result = ""
#    for ix in range(len(terms)-1, -1, -1):  # 3,2,1,0
#        interval = intervals[ix]
#        a = amount // interval
#        if a > 0 or interval == 1:
#            result += "%d %s, " % (a, terms[ix][a % 1])
#            amount -= a * interval
#    if msecs > 0:
#        result += "%d msecs" % (msecs)
#    else:
#        result = result[:-2]
#
#    return result


def ordereddict_to_str(data):
    arr = []
    for i in range(len(data)):
        temp = list(data.popitem())
        str1 = ' '.join(temp)
        arr.append(str1)
    return arr


def get_one_genome_txt(ucsc_assembly):
    # UCSC shim
    genome = OrderedDict([
        ('trackDb', ucsc_assembly + '/trackDb.txt'),
        ('genome', ucsc_assembly)
    ])
    return ordereddict_to_str(genome)


def get_genomes_txt(assemblies):
    blob = ''
    ucsc_assemblies = set()
    for assembly in assemblies:
        ucsc_assemblies.add(ASSEMBLY_TO_UCSC_ID.get(assembly, assembly))
    for ucsc_assembly in ucsc_assemblies:
        if blob == '':
            blob = '\n'.join(get_one_genome_txt(ucsc_assembly))
        else:
            blob += 2 * '\n' + '\n'.join(get_one_genome_txt(ucsc_assembly))
    return blob


def get_hub(label, comment=None, name=None):
    if name is None:
        name = sanitize.name(label.split()[0])
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
    return ordereddict_to_str(hub)


def generate_html(context, request):
    ''' Generates and returns HTML for the track hub'''

    # First determine if single dataset or collection
    # log.debug("HTML request: %s" % request.url)

    html_requested = request.url.split('/')[-1].split('.')[0]
    if html_requested.startswith('ENCSR'):
        embedded = request.embed(request.resource_path(context))
        accession = embedded['accession']
        log.debug("generate_html for %s   %.3f secs" % (accession, (time.time() - PROFILE_START_TIME)))
        assert(html_requested == accession)

        vis_defines = VisDefines(embedded)
        vis_type = vis_defines.get_vis_type()
        vis_def = vis_defines.get_vis_def(vis_type)
        longLabel = vis_def.get('longLabel',
                                 '{assay_term_name} of {biosample_term_name} - {accession}')
        longLabel = sanitize.label(vis_defines.convert_mask(longLabel))

        link = request.host_url + '/experiments/' + accession + '/'
        acc_link = '<a href={link}>{accession}<a>'.format(link=link, accession=accession)
        if longLabel.find(accession) != -1:
            longLabel = longLabel.replace(accession, acc_link)
        else:
            longLabel += " - " + acc_link
        page = '<h2>%s</h2>' % longLabel

    else:  # collection
        vis_type = html_requested
        vis_def = VisDefines().get_vis_def(vis_type)
        longLabel = vis_def.get('assay_composite', {}).get('longLabel',
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

    details = vis_def.get("html_detail")
    if details is not None:
        page += details

    return page  # data_description + header + file_table


def generate_batch_hubs(context, request):
    '''search for the input params and return the trackhub'''
    global PROFILE_START_TIME
    PROFILE_START_TIME = time.time()

    results = {}
    (page, suffix, cmd) = urlpage(request.url)
    log.debug('Requesting %s.%s#%s' % (page,suffix,cmd))

    if (suffix == 'txt' and page == 'trackDb') or \
         (suffix == 'json' and page in ['trackDb','ihec','vis_blob']):

        return generate_batch_trackDb(request)

    elif page == 'hub' and suffix == 'txt':
        terms = request.matchdict['search_params'].replace(',,', '&')
        pairs = terms.split('&')
        label = "search:"
        for pair in sorted(pairs):
            (var, val) = pair.split('=')
            if var not in ["type", "assembly", "status", "limit"]:
                label += " %s" % val.replace('+', ' ')
        return '\n'.join(get_hub(label, request.url))
    elif page == 'genomes' and suffix == 'txt':
        search_params = request.matchdict['search_params']
        if search_params.find('bed6+') > -1:
            search_params = search_params.replace('bed6+,,','bed6%2B,,')
        log.debug('search_params: %s' % (search_params))
        #param_list = parse_qs(request.matchdict['search_params'].replace(',,', '&'))
        param_list = parse_qs(search_params.replace(',,', '&'))
        log.debug('parse_qs: %s' % (param_list))

        view = 'search'
        if 'region' in param_list:
            view = 'region-search'
        path = '/%s/?%s' % (view, urlencode(param_list, True))
        log.debug('Path in hunt for assembly %s' % (path))
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
            if g_text == '':
                assembly_set = {
                    result['assemblies']
                    for result in results['@graph']
                    if 'assemblies' in result
                }
                if len(assembly_set) > 0:
                    g_text = get_genomes_txt(list(assembly_set))
                    log.debug(
                        'Requesting %s.%s#%s NO ASSEMBLY !!!  Found %d anyway' %
                        (page, suffix, cmd, len(assembly_set))
                    )
                else:
                    g_text = json.dumps(results, indent=4)
                    log.debug('Found 0 ASSEMBLIES !!!')
        return g_text

    else:
        # Should generate a HTML page for requests other than those supported
        data_policy = ('<br /><a href="http://encodeproject.org/ENCODE/terms.html">'
                       'ENCODE data use policy</p>')
        return generate_html(context, request) + data_policy

def respond_with_text(request, text, content_mime):
    '''Resonse that can handle range requests.'''
    # UCSC broke trackhubs and now we must handle byterange requests on these CGI files
    response = request.response
    response.content_type = content_mime
    response.charset = 'UTF-8'
    response.body = bytes_(text, 'utf-8')
    response.accept_ranges = "bytes"
    response.last_modified = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
    if 'Range' in request.headers:
        range_request = True
        range = request.headers['Range']
        if range.startswith('bytes'):
            range = range.split('=')[1]
        range = range.split('-')
        # One final present... byterange '0-' with no end in sight
        if range[1] == '':
            range[1] = len(response.body) - 1
        response.content_range = 'bytes %d-%d/%d' % (int(range[0]),int(range[1]),len(response.body))
        response.app_iter = request.response.app_iter_range(int(range[0]),int(range[1]) + 1)
        response.status_code = 206
    return response

@view_config(name='hub', context=Item, request_method='GET', permission='view')
def hub(context, request):
    ''' Creates trackhub on fly for a given experiment '''
    global PROFILE_START_TIME
    PROFILE_START_TIME = time.time()

    embedded = request.embed(request.resource_path(context))

    (page,suffix,cmd) = urlpage(request.url)
    content_mime = 'text/plain'
    if page == 'hub' and suffix == 'txt':
        typeof = embedded.get("assay_title")
        if typeof is None:
            typeof = embedded["@id"].split('/')[1]

        label = "%s %s" % (typeof, embedded['accession'])
        name = sanitize.name(label)
        text = '\n'.join(get_hub(label, request.url, name))
    elif page == 'genomes' and suffix == 'txt':
        assemblies = ''
        if 'assembly' in embedded:
            assemblies = embedded['assembly']

        text = get_genomes_txt(assemblies)

    elif (suffix == 'txt' and page == 'trackDb') or \
         (suffix == 'json' and page in ['trackDb','ihec','vis_blob']):
        url_ret = (request.url).split('@@hub')
        url_end = url_ret[1][1:]
        text = generate_trackDb(request, embedded, url_end.split('/')[0])
    else:
        data_policy = ('<br /><a href="http://encodeproject.org/ENCODE/terms.html">'
                       'ENCODE data use policy</p>')
        text = generate_html(context, request) + data_policy
        content_mime = 'text/html'

    return respond_with_text(request, text, content_mime)


@view_config(route_name='batch_hub')
@view_config(route_name='batch_hub:trackdb')
def batch_hub(context, request):
    ''' View for batch track hubs '''

    text = generate_batch_hubs(context, request)
    return respond_with_text(request, text, 'text/plain')
