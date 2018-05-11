from pyramid.traversal import find_root
from uuid import UUID
from snovault import upgrade_step
import re
from .shared import ENCODE2_AWARDS, REFERENCES_UUID


@upgrade_step('experiment', '', '2')
@upgrade_step('annotation', '', '2')
@upgrade_step('matched_set', '', '2')
@upgrade_step('project', '', '2')
@upgrade_step('publication_data', '', '2')
@upgrade_step('reference', '', '2')
@upgrade_step('ucsc_browser_composite', '', '2')
def dataset_0_2(value, system):
    # http://redmine.encodedcc.org/issues/650
    context = system['context']
    root = find_root(context)
    if 'files' in value:
        value['related_files'] = []
        for file_uuid in value['files']:
            item = root.get_by_uuid(file_uuid)
            if UUID(item.properties['dataset']) != context.uuid:
                value['related_files'].append(file_uuid)
        del value['files']


@upgrade_step('experiment', '2', '3')
@upgrade_step('annotation', '2', '3')
@upgrade_step('matched_set', '2', '3')
@upgrade_step('project', '2', '3')
@upgrade_step('publication_data', '2', '3')
@upgrade_step('reference', '2', '3')
@upgrade_step('ucsc_browser_composite', '2', '3')
def dataset_2_3(value, system):
    # http://redmine.encodedcc.org/issues/817
    value['dbxrefs'] = []

    if 'encode2_dbxrefs' in value:
        for encode2_dbxref in value['encode2_dbxrefs']:
            if re.match('.*wgEncodeEH.*', encode2_dbxref):
                new_dbxref = 'UCSC-ENCODE-hg19:' + encode2_dbxref
            elif re.match('.*wgEncodeEM.*', encode2_dbxref):
                new_dbxref = 'UCSC-ENCODE-mm9:' + encode2_dbxref
            value['dbxrefs'].append(new_dbxref)
        del value['encode2_dbxrefs']

    if 'geo_dbxrefs' in value:
        for geo_dbxref in value['geo_dbxrefs']:
            new_dbxref = 'GEO:' + geo_dbxref
            value['dbxrefs'].append(new_dbxref)
        del value['geo_dbxrefs']

    if 'aliases' in value:
        for alias in value['aliases']:
            if re.match('ucsc_encode_db:hg19-', alias):
                new_dbxref = alias.replace(
                    'ucsc_encode_db:hg19-', 'UCSC-GB-hg19:')
            elif re.match('ucsc_encode_db:mm9-', alias):
                new_dbxref = alias.replace(
                    'ucsc_encode_db:mm9-', 'UCSC-GB-mm9:')
            elif re.match('.*wgEncodeEH.*', alias):
                new_dbxref = alias.replace(
                    'ucsc_encode_db:', 'UCSC-ENCODE-hg19:')
            elif re.match('.*wgEncodeEM.*', alias):
                new_dbxref = alias.replace(
                    'ucsc_encode_db:', 'UCSC-ENCODE-mm9:')
            else:
                continue
            value['dbxrefs'].append(new_dbxref)
            value['aliases'].remove(alias)


@upgrade_step('experiment', '3', '4')
@upgrade_step('annotation', '3', '4')
@upgrade_step('matched_set', '3', '4')
@upgrade_step('project', '3', '4')
@upgrade_step('publication_data', '3', '4')
@upgrade_step('reference', '3', '4')
@upgrade_step('ucsc_browser_composite', '3', '4')
def dataset_3_4(value, system):
    # http://redmine.encodedcc.org/issues/1074
    if 'status' in value:
        if value['status'] == 'DELETED':
            value['status'] = 'deleted'
        elif value['status'] == 'CURRENT':
            if value['award'] in ENCODE2_AWARDS:
                value['status'] = 'released'
            elif value['award'] not in ENCODE2_AWARDS:
                value['status'] = 'submitted'

    else:
        if value['award'] in ENCODE2_AWARDS:
            value['status'] = 'released'
        elif value['award'] not in ENCODE2_AWARDS:
            value['status'] = 'submitted'


@upgrade_step('experiment', '4', '5')
@upgrade_step('annotation', '4', '5')
@upgrade_step('matched_set', '4', '5')
@upgrade_step('project', '4', '5')
@upgrade_step('publication_data', '4', '5')
@upgrade_step('reference', '4', '5')
@upgrade_step('ucsc_browser_composite', '4', '5')
def experiment_4_5(value, system):
    # http://redmine.encodedcc.org/issues/1393
    if value.get('biosample_type') == 'primary cell line':
        value['biosample_type'] = 'primary cell'


@upgrade_step('experiment', '5', '6')
@upgrade_step('annotation', '5', '6')
@upgrade_step('matched_set', '5', '6')
@upgrade_step('project', '5', '6')
@upgrade_step('publication_data', '5', '6')
@upgrade_step('reference', '5', '6')
@upgrade_step('ucsc_browser_composite', '5', '6')
def experiment_5_6(value, system):
    # http://redmine.encodedcc.org/issues/2591
    context = system['context']
    root = find_root(context)
    publications = root['publications']
    if 'references' in value:
        new_references = []
        for ref in value['references']:
            if re.match('doi', ref):
                new_references.append(REFERENCES_UUID[ref])
            else:
                item = publications[ref]
                new_references.append(str(item.uuid))
        value['references'] = new_references


@upgrade_step('experiment', '6', '7')
@upgrade_step('annotation', '6', '7')
@upgrade_step('matched_set', '6', '7')
@upgrade_step('project', '6', '7')
@upgrade_step('publication_data', '6', '7')
@upgrade_step('reference', '6', '7')
@upgrade_step('ucsc_browser_composite', '6', '7')
def dataset_6_7(value, system):
    if 'dataset_type' in value:
        if value['dataset_type'] == 'paired set':
            value.pop('related_files', None)
            value.pop('contributing_files', None)
            value.pop('revoked_files', None)
            value['related_datasets'] = []
        del value['dataset_type']


@upgrade_step('experiment', '7', '8')
@upgrade_step('annotation', '7', '8')
@upgrade_step('reference', '7', '8')
@upgrade_step('project', '7', '8')
@upgrade_step('publication_data', '7', '8')
@upgrade_step('matched_set', '7', '8')
@upgrade_step('ucsc_browser_composite', '7', '8')
@upgrade_step('organism_development_series', '7', '8')
@upgrade_step('reference_epigenome', '7', '8')
@upgrade_step('replication_timing_series', '7', '8')
@upgrade_step('treatment_time_series', '7', '8')
@upgrade_step('treatment_concentration_series', '7', '8')
def dataset_7_8(value, system):
    # http://redmine.encodedcc.org/issues/3063
    if 'possible_controls' in value:
        value['possible_controls'] = list(set(value['possible_controls']))

    if 'targets' in value:
        value['targets'] = list(set(value['targets']))

    if 'software_used' in value:
        value['software_used'] = list(set(value['software_used']))

    if 'dbxrefs' in value:
        value['dbxrefs'] = list(set(value['dbxrefs']))

    if 'aliases' in value:
        value['aliases'] = list(set(value['aliases']))

    if 'references' in value:
        value['references'] = list(set(value['references']))

    if 'documents' in value:
        value['documents'] = list(set(value['documents']))

    if 'related_files' in value:
        value['related_files'] = list(set(value['related_files']))


@upgrade_step('experiment', '8', '9')
@upgrade_step('annotation', '8', '9')
@upgrade_step('reference', '8', '9')
@upgrade_step('project', '8', '9')
@upgrade_step('matched_set', '8', '9')
@upgrade_step('publication_data', '8', '9')
@upgrade_step('ucsc_browser_composite', '8', '9')
@upgrade_step('organism_development_series', '8', '9')
@upgrade_step('reference_epigenome', '8', '9')
@upgrade_step('replication_timing_series', '8', '9')
@upgrade_step('treatment_time_series', '8', '9')
@upgrade_step('treatment_concentration_series', '8', '9')
def dataset_8_9(value, system):
    if value['status'] == "in progress":
        value['status'] = "started"
    elif value['status'] == "in review":
        value['status'] = "revoked"
    elif value['status'] == "release ready":
        value['status'] = "ready for review"
    elif value['status'] == "verified":
        value['status'] = "submitted"
    elif value['status'] == "preliminary":
        value['status'] = "proposed"

    if 'annotation_type' in value:
        if value['annotation_type'] == 'segmentation':
            value['annotation_type'] = 'chromatin state'
        elif value['annotation_type'] == 'SAGA':
            value['annotation_type'] = 'chromatin state'
        elif value['annotation_type'] == 'enhancer prediction':
            value['annotation_type'] = 'enhancer predictions'
        elif value['annotation_type'] == 'encyclopedia':
            value['annotation_type'] = 'other'
        elif value['annotation_type'] == 'candidate enhancers':
            value['annotation_type'] = 'enhancer-like regions'
        elif value['annotation_type'] == 'candidate promoters':
            value['annotation_type'] = 'promoter-like regions'


@upgrade_step('experiment', '9', '10')
@upgrade_step('annotation', '9', '10')
@upgrade_step('reference', '9', '10')
@upgrade_step('project', '9', '10')
@upgrade_step('matched_set', '9', '10')
@upgrade_step('publication_data', '9', '10')
@upgrade_step('ucsc_browser_composite', '9', '10')
@upgrade_step('organism_development_series', '9', '10')
@upgrade_step('reference_epigenome', '9', '10')
@upgrade_step('replication_timing_series', '9', '10')
@upgrade_step('treatment_time_series', '9', '10')
@upgrade_step('treatment_concentration_series', '9', '10')
def dataset_9_10(value, system):
    # http://redmine.encodedcc.org/issues/1384
    if 'description' in value:
        if value['description']:
            value['description'] = value['description'].strip()
        else:
            del value['description']

    if 'notes' in value:
        if value['notes']:
            value['notes'] = value['notes'].strip()
        else:
            del value['notes']

    if 'submitter_comment' in value:
        if value['submitter_comment']:
            value['submitter_comment'] = value['submitter_comment'].strip()
        else:
            del value['submitter_comment']

    # http://redmine.encodedcc.org/issues/2491
    if 'assay_term_id' in value:
        del value['assay_term_id']


@upgrade_step('experiment', '11', '12')
@upgrade_step('annotation', '11', '12')
@upgrade_step('matched_set', '11', '12')
@upgrade_step('project', '11', '12')
@upgrade_step('publication_data', '11', '12')
@upgrade_step('reference', '11', '12')
@upgrade_step('reference_epigenome', '11', '12')
@upgrade_step('organism_development_series', '11', '12')
@upgrade_step('replication_timing_series', '11', '12')
@upgrade_step('treatment_time_series', '11', '12')
@upgrade_step('treatment_concentration_series', '11', '12')
@upgrade_step('ucsc_browser_composite', '11', '12')
def dataset_11_12(value, system):
    # http://redmine.encodedcc.org/issues/5049
    return


@upgrade_step('annotation', '12', '13')
def dataset_12_13(value, system):
    # http://redmine.encodedcc.org/issues/5178
    annotation_type = value.get('annotation_type')
    if annotation_type and annotation_type == 'candidate regulatory regions':
        value['annotation_type'] = 'candidate regulatory elements'


@upgrade_step('annotation', '13', '14')
@upgrade_step('experiment', '12', '13')
def dataset_13_14(value, system):
    # http://redmine.encodedcc.org/issues/4925
    # http://redmine.encodedcc.org/issues/4900
    return


@upgrade_step('experiment', '13', '14')
@upgrade_step('annotation', '14', '15')
@upgrade_step('reference', '12', '13')
@upgrade_step('project', '12', '13')
@upgrade_step('matched_set', '12', '13')
@upgrade_step('publication_data', '12', '13')
@upgrade_step('ucsc_browser_composite', '12', '13')
@upgrade_step('organism_development_series', '12', '13')
@upgrade_step('reference_epigenome', '12', '13')
@upgrade_step('replication_timing_series', '12', '13')
@upgrade_step('treatment_time_series', '12', '13')
@upgrade_step('treatment_concentration_series', '12', '13')
def dataset_14_15(value, system):
    if value['status'] == "proposed":
        value['status'] = "started"


@upgrade_step('annotation', '15', '16')
def annotation_15_16(value, system):
    if 'annotation_type' in value:
        if value['annotation_type'] in ['enhancer-like regions', 'promoter-like regions']:
            value['annotation_type'] = 'candidate regulatory elements'
        if value['annotation_type'] == 'DNase master peaks':
            value['annotation_type'] = 'representative DNase hypersensitivity sites'


@upgrade_step('experiment', '14', '15')
def experiment_14_15(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3721
    if value['biosample_type'] == 'in vitro sample':
        value['biosample_type'] = 'cell-free sample'
        value['biosample_term_id'] = 'NTR:0000471'
        value['biosample_term_name'] = 'none'


@upgrade_step('experiment', '15', '16')
@upgrade_step('annotation', '16', '17')
def dataset_15_16(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3848
    if value.get('biosample_type') == 'immortalized cell line':
        value['biosample_type'] = "cell line"


@upgrade_step('experiment', '16', '17')
@upgrade_step('reference', '13', '14')
@upgrade_step('treatment_time_series', '13', '14')
def dataset_16_17(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3780
    if value['status'] == "ready for review":
        value['status'] = "submitted"


@upgrade_step('experiment', '17', '18')
@upgrade_step('annotation', '17', '18')
@upgrade_step('reference', '14', '15')
@upgrade_step('project', '13', '14')
@upgrade_step('matched_set', '13', '14')
@upgrade_step('publication_data', '13', '14')
@upgrade_step('ucsc_browser_composite', '13', '14')
@upgrade_step('organism_development_series', '13', '14')
@upgrade_step('reference_epigenome', '13', '14')
@upgrade_step('replication_timing_series', '13', '14')
@upgrade_step('treatment_time_series', '14', '15')
@upgrade_step('treatment_concentration_series', '13', '14')
def dataset_17_18(value, system):
    if value['status'] == "started":
        value['status'] = "in progress"


@upgrade_step('experiment', '18', '19')
def dataset_18_19(value, system):
    if (value['status'] == 'submitted' and
        not value.get('date_submitted')):
        value['status'] = 'in progress'


@upgrade_step('annotation', '18', '19')
@upgrade_step('experiment', '19', '20')
def dataset_19_20(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3974
    return


@upgrade_step('reference_epigenome', '14', '15')
def dataset_20_21(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3889
    return
