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


@upgrade_step('experiment', '20', '21')
def dataset_21_22(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-4107
    value['experiment_classification']=["functional genomics assay"]
    return


@upgrade_step('experiment', '21', '22')
@upgrade_step('annotation', '19', '20')
def dataset_22_23(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-3555
    if value.get('biosample_type') == 'induced pluripotent stem cell line':
        value['biosample_type'] = 'cell line'
    if value.get('biosample_type') == 'stem cell':
        if value.get('biosample_term_name') in ['MSiPS', 'E14TG2a.4', 'UCSF-4', 'HUES9', 'HUES8', 'HUES66', 'HUES65',
            'HUES64', 'HUES63', 'HUES62', 'HUES6', 'HUES53', 'HUES49', 'HUES48', 'HUES45', 'HUES44', 'HUES3', 'HUES28',
            'HUES13', 'ES-I3', 'ES-E14', 'CyT49', 'BG01', 'ES-CJ7', 'WW6', 'ZHBTc4-mESC', 'ES-D3', 'H7-hESC', 'ELF-1',
            'TT2', '46C', 'ES-Bruce4', 'HUES1', 'H9', 'H1-hESC', 'BG02', 'R1', 'G1E-ER4', 'G1E']:
            value['biosample_type'] = 'cell line'
        elif value.get('biosample_term_name') in ['hematopoietic stem cell', 'embryonic stem cell',
            'mammary stem cell', 'mesenchymal stem cell of the bone marrow', "mesenchymal stem cell of Wharton's jelly",
            'mesenchymal stem cell of adipose', 'amniotic stem cell', 'stem cell of epidermis', 'mesenchymal stem cell',
            'dedifferentiated amniotic fluid mesenchymal stem cell', 'leukemia stem cell', 'neuronal stem cell',
            'neuroepithelial stem cell', 'neural stem progenitor cell']:
            value['biosample_type'] = 'primary cell'


@upgrade_step('experiment', '22', '23')
@upgrade_step('annotation', '20', '21')
def dataset_23_24(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-4360
    classification = value.get('biosample_type')
    term_id = value.get('biosample_term_id')
    if classification and term_id:
        biosample_type_name = u'{}_{}'.format(
            value['biosample_type'], value['biosample_term_id']
        ).replace(' ', '_').replace(':', '_')
        value['biosample_ontology'] = str(
            find_root(system['context'])['biosample-types'][biosample_type_name].uuid
        )


@upgrade_step('experiment', '23', '24')
@upgrade_step('annotation', '21', '22')
@upgrade_step('reference', '15', '16')
@upgrade_step('project', '14', '15')
@upgrade_step('matched_set', '14', '15')
@upgrade_step('publication_data', '14', '15')
@upgrade_step('ucsc_browser_composite', '14', '15')
@upgrade_step('organism_development_series', '14', '15')
@upgrade_step('reference_epigenome', '15', '16')
@upgrade_step('replication_timing_series', '14', '15')
@upgrade_step('treatment_time_series', '15', '16')
@upgrade_step('treatment_concentration_series', '14', '15')
def dataset_24_25(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-4435
    internal_tags = value.get('internal_tags')
    try:
        internal_tags[internal_tags.index('cre_inputv10')] = 'ccre_inputv1'
    except ValueError:
        pass
    try:
        internal_tags[internal_tags.index('cre_inputv11')] = 'ccre_inputv2'
    except ValueError:
        pass


@upgrade_step('experiment', '24', '25')
@upgrade_step('annotation', '22', '23')
def dataset_25_26(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-4420
    value.pop('biosample_type', None)
    value.pop('biosample_term_id', None)
    value.pop('biosample_term_name', None)


@upgrade_step('annotation', '23', '24')
def annotation_23_24(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-4489
    if 'annotation_type' not in value:
        value['annotation_type'] = 'other'


@upgrade_step('experiment', '25', '26')
def dataset_26_27(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-4384
    if value.get('assay_term_name') == 'ISO-seq':
        value['assay_term_name'] = 'long read RNA-seq'
    return


@upgrade_step('annotation', '24', '25')
def annotation_24_25(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-4613
    if value.get('annotation_type') == 'candidate regulatory elements':
        value['annotation_type'] = 'candidate Cis-Regulatory Elements'
    return


@upgrade_step('experiment', '26', '27')
def experiment_26_27(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-4711
    if value.get('assay_term_name') == 'single-nuclei ATAC-seq':
        value['assay_term_name'] = 'single-nucleus ATAC-seq'

@upgrade_step('experiment', '27', '28')
def experiment_27_28(value, system):
    #https://encodedcc.atlassian.net/browse/ENCD-4838
    value.pop('experiment_classification', None)


@upgrade_step('annotation', '25', '26')
def annotation_25_26(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-4488
    enc_ver = value.get('encyclopedia_version')
    ver_dict = {
        '1': 'ENCODE v1',
        '2': 'ENCODE v2',
        'ENCODE2': 'ENCODE v2',
        '3': 'ENCODE v3',
        '4': 'ENCODE v4',
        '5': 'ENCODE v5',
        'ROADMAP': 'Roadmap',
    }
    if enc_ver in ver_dict:
        value['encyclopedia_version'] = ver_dict[enc_ver]
    elif enc_ver == 'Blacklists':
        value.pop('encyclopedia_version', None)
    return


@upgrade_step('aggregate_series', '1', '2')
@upgrade_step('annotation', '26', '27')
@upgrade_step('experiment_series', '1', '2')
@upgrade_step('functional_characterization_experiment', '1', '2')
@upgrade_step('functional_characterization_series', '1', '2')
@upgrade_step('matched_set', '15', '16')
@upgrade_step('organism_development_series', '15', '16')
@upgrade_step('project', '15', '16')
@upgrade_step('publication_data', '15', '16')
@upgrade_step('reference_epigenome', '16', '17')
@upgrade_step('reference', '16', '17')
@upgrade_step('replication_timing_series', '15', '16')
@upgrade_step('single_cell_rna_series', '1', '2')
@upgrade_step('treatment_concentration_series', '15', '16')
@upgrade_step('treatment_time_series', '16', '17')
@upgrade_step('ucsc_browser_composite', '15', '16')
def dataset_27_28(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-5068
    if not value.get('dbxrefs'):
        return
    new_dbxrefs = set()
    for dbxref in value['dbxrefs']:
        if not dbxref.startswith('IHEC:IHECRE'):
            new_dbxrefs.add(dbxref)
            continue
        new_dbxrefs.add(dbxref.rsplit('.', 1)[0])
    value['dbxrefs'] = sorted(new_dbxrefs)


@upgrade_step('aggregate_series', '2', '3')
@upgrade_step('experiment_series', '2', '3')
@upgrade_step('functional_characterization_experiment', '3', '4')
@upgrade_step('functional_characterization_series', '2', '3')
@upgrade_step('matched_set', '16', '17')
@upgrade_step('organism_development_series', '16', '17')
@upgrade_step('project', '16', '17')
@upgrade_step('publication_data', '16', '17')
@upgrade_step('reference', '17', '18')
@upgrade_step('replication_timing_series', '16', '17')
@upgrade_step('single_cell_rna_series', '2', '3')
@upgrade_step('treatment_concentration_series', '16', '17')
@upgrade_step('treatment_time_series', '17', '18')
@upgrade_step('ucsc_browser_composite', '16', '17')
def dataset_28_29(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-5083
    if not value.get('dbxrefs'):
        return
    new_dbxrefs = set()
    for dbxref in value['dbxrefs']:
        if not dbxref.startswith('IHEC:IHECRE'):
            new_dbxrefs.add(dbxref)
            continue
        else:
            if 'notes' in value:
                value['notes'] += '\t' + dbxref
            else:
                value['notes'] = dbxref
    if len(new_dbxrefs) == 0:
        value.pop('dbxrefs', None)
    else:
        value['dbxrefs'] = sorted(new_dbxrefs)


@upgrade_step('annotation', '27', '28')
def annotation_27_28(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-5232
    annotation_type = value.get('annotation_type', None)

    if annotation_type == "representative DNase hypersensitivity sites":
        value['annotation_type'] = 'representative DNase hypersensitivity sites (rDHSs)'
    return


@upgrade_step('reference', '18', '19')
def reference_18_19(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-5259
    if 'examined_loci' in value:
        examined_loci = value.get('examined_loci', None)
        if examined_loci == []:
            value.pop('examined_loci', None)


@upgrade_step('annotation', '28', '29')
def annotation_28_29(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-4438
    units = value.get('relevant_timepoint_units')
    if units == 'stage':
        info = f'{value.get("relevant_timepoint")} {units}'
        value.pop('relevant_timepoint', None)
        value.pop('relevant_timepoint_units', None)
        if 'notes' in value:
            value['notes'] = f'{value.get("notes")}. Removed timepoint metadata: {info}'
        else:
            value['notes'] = info
    return


@upgrade_step('experiment', '28', '29')
def experiment_28_29(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-5343
    unrunnable = f'Previous internal_status claimed this experiment was unrunnable on a pipeline'
    if 'pipeline_error_detail' in value:
        error_detail = f'Previous internal_status claimed a pipeline error: {value.get("pipeline_error_detail")}'
        value.pop('pipeline_error_detail')
        if 'notes' in value:
            value['notes'] = f'{value.get("notes")}. {error_detail}'
        else:
            value['notes'] = error_detail
    if value.get('internal_status') == 'unrunnable':
        if 'notes' in value:
            value['notes'] = f'{value.get("notes")}. {unrunnable}'
        else:
            value['notes'] = unrunnable

    value['internal_status'] = 'unreviewed'
    return


@upgrade_step('experiment', '29', '30')
def experiment_29_30(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-5304
    if value.get('assay_term_name') == 'single cell isolation followed by RNA-seq':
        value['assay_term_name'] = 'single-cell RNA sequencing assay'


@upgrade_step('experiment', '30', '31')
def experiment_30_31(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-5354
    if not value.get('analyses'):
        return
    analyses_files = ';'.join(
        sorted(
            ','.join(sorted(a['files'])) for a in value['analyses']
        )
    )
    value['notes'] = f'{value.get("notes", "")}. [Experiment.analyses] {analyses_files}'
    value.pop('analyses')


@upgrade_step('annotation', '29', '30')
def annotation_29_30(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-5573
    annotation_type = value.get('annotation_type', None)

    if annotation_type == "representative DNase hypersensitivity sites (rDHSs)":
        value['annotation_type'] = 'representative DNase hypersensitivity sites'
    return


@upgrade_step('annotation', '30', '31')
def annotation_30_31(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-5657
    annotation_type = value.get('annotation_type', None)

    if annotation_type == "blacklist":
        value['annotation_type'] = 'exclusion list'
    return


@upgrade_step('experiment', '31', '32')
def experiment_31_32(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-5787
    if value.get('assay_term_name') == 'single-nucleus RNA-seq':
        value['assay_term_name'] = 'single-cell RNA sequencing assay'
        if 'notes' in value:
            value['notes'] = f'{value.get("notes")}. This assay was previously labeled single-nucleus RNA-seq.'
        else:
            value['notes'] = 'This assay was previously labeled single-nucleus RNA-seq.'
    if value.get('assay_term_name') == 'genotyping by high throughput sequencing assay':
        value['assay_term_name'] = 'whole genome sequencing assay'
        if 'notes' in value:
            value['notes'] = f'{value.get("notes")}. This assay was previously labeled genotyping HTS.'
        else:
            value['notes'] = 'This assay was previously labeled genotyping HTS.'
    return


@upgrade_step('experiment', '32', '33')
def experiment_32_33(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-5828
    if value.get('assay_term_name') == 'single-cell ATAC-seq':
        value['assay_term_name'] = 'single-nucleus ATAC-seq'
        if 'notes' in value:
            value['notes'] = f'{value.get("notes")}. This assay was previously labeled single-cell ATAC-seq.'
        else:
            value['notes'] = 'This assay was previously labeled single-cell ATAC-seq.'
    return

@upgrade_step('experiment', '33', '34')
@upgrade_step('annotation', '31', '32')
@upgrade_step('functional_characterization_experiment', '6', '7')
@upgrade_step('single_cell_unit', '1', '2')
def dataset_29_30(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-5840
    if not value.get('analysis_objects'):
        return
    value['analyses'] = value['analysis_objects']
    value.pop('analysis_objects')

@upgrade_step('experiment', '34', '35')
@upgrade_step('annotation', '32', '33')
@upgrade_step('reference', '19', '20')
def dataset_30_31(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-5932
    if  'RegulomeDB' in value['internal_tags']:
            value['internal_tags'].remove('RegulomeDB')
            value['internal_tags'].append('RegulomeDB_1_0')


@upgrade_step('experiment', '35', '36')
def experiment_35_36(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-5964
    if value.get('assay_term_name') == 'Capture Hi-C':
        value['assay_term_name'] = 'capture Hi-C'


@upgrade_step('reference', '20', '21')
def reference_20_21(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-6134
    new_elements_selection_method = []
    new_notes = []
    old_to_new = {
        'ATAC-seq': 'accessible genome regions',
        'DNase-seq': 'DNase hypersensitive sites',
        'GRO-cap': 'transcription start sites',
        'point mutations': 'sequence variants',
        'single nucleotide polymorphisms': 'sequence variants',
        'transcription factors': 'TF binding sites'
    }
    if 'elements_selection_method' in value:
        for element_selection_method in value['elements_selection_method']:
            if element_selection_method in old_to_new:
                new_elements_selection_method.append(old_to_new[element_selection_method])
                new_notes.append(f"This elements_selection_method was previously {element_selection_method} but now has been renamed to be {old_to_new[element_selection_method]}.")
            else:
                new_elements_selection_method.append(element_selection_method)
    if len(new_elements_selection_method) >= 1:
        value['elements_selection_method'] = list(set(new_elements_selection_method))
        if 'notes' in value:
            value['notes'] = f"{value['notes']} {' '.join(new_notes)}"
        else:
            value['notes'] = ' '.join(new_notes)


@upgrade_step('annotation', '33', '34')
def annotation_33_34(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-6143
    if 'encyclopedia_version' in value:
        if value['encyclopedia_version'] == 'ENCODE v1':
            value['encyclopedia_version'] = 'ENCODE v0.1'
        elif value['encyclopedia_version'] == 'ENCODE v2':
            value['encyclopedia_version'] = 'ENCODE v0.2'
        elif value['encyclopedia_version'] == 'ENCODE v3':
            value['encyclopedia_version'] = 'ENCODE v0.3'
        elif value['encyclopedia_version'] == 'ENCODE v4':
            value['encyclopedia_version'] = 'ENCODE v1'
        elif value['encyclopedia_version'] == 'ENCODE v5':
            value['encyclopedia_version'] = 'ENCODE v2'
        elif value['encyclopedia_version'] == 'ENCODE v6':
            value['encyclopedia_version'] = 'ENCODE v3'
