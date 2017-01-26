from snovault import (
    AuditFailure,
    audit_checker,
)


@audit_checker('ReferenceEpigenome', frame=['related_datasets',
                                            'related_datasets.replicates',
                                            'related_datasets.replicates.library',
                                            'related_datasets.replicates.library.biosample',
                                            'related_datasets.replicates.library.biosample.donor',
                                            'related_datasets.replicates.library.biosample.treatments'])
def audit_reference_epigenome_donor_biosample(value, system):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if 'related_datasets' not in value:
        return

    treatments_set = set()
    biosample_name_set = set()
    for assay in value['related_datasets']:
        if assay['status'] not in ['deleted', 'replaced', 'revoked']:
            if 'replicates' in assay:
                for rep in assay['replicates']:
                    if rep['status'] not in ['deleted'] and \
                       'library' in rep and 'biosample' in rep['library']:
                        biosample_object = rep['library']['biosample']
                        if 'biosample_term_name' in biosample_object:
                            biosample_name_set.add(biosample_object['biosample_term_name'])
                        if 'treatments' in biosample_object:
                            if len(biosample_object['treatments']) == 0:
                                treatments_set.add('untreated')
                            else:
                                treatments_to_add = []
                                for t in biosample_object['treatments']:
                                    treatments_to_add.append('treated with ' +
                                                             t['treatment_term_name'])
                                treatments_set.add(', '.join(sorted(treatments_to_add)))
                        else:
                            treatments_set.add('untreated')
    if len(treatments_set) > 1:
        detail = 'Reference Epigenome {} '.format(value['@id']) + \
                 ' has biosample associated with different tretments {}.'.format(treatments_set)
        yield AuditFailure('multiple biosample treatments in reference epigenome',
                           detail, level='WARNING')

    if len(biosample_name_set) > 1:
        detail = 'Reference Epigenome {} '.format(value['@id']) + \
                 ' has multiple biosample term names {}.'.format(biosample_name_set)
        yield AuditFailure('multiple biosample term names in reference epigenome',
                           detail, level='WARNING')
    return


@audit_checker('ReferenceEpigenome', frame=['award',
                                            'related_datasets',
                                            'related_datasets.target'])
def audit_reference_epigenome_assay_types_requirments(value, system):
    detail_prefix = 'Reference Epigenome {} '.format(value['@id'])
    if 'related_datasets' not in value:
        detail = detail_prefix + \
            'has no related datasets. It lacks all of the IHEC required ' + \
            'assays.'
        yield AuditFailure('partial reference epigenome', detail, level='WARNING')
        return

    roadmap_flag = False
    if 'award' in value and \
       value['award']['rfa'] == 'Roadmap':
        roadmap_flag = True
        required_assays = {('OBI:0000716', 'Control'): 0,
                           ('OBI:0000716', 'H3K27me3'): 0,
                           ('OBI:0000716', 'H3K36me3'): 0,
                           ('OBI:0000716', 'H3K4me1'): 0,
                           ('OBI:0000716', 'H3K4me3'): 0,
                           ('OBI:0000716', 'H3K9me3'): 0,
                           'OBI:0001271': 0,  # RNA-seq
                           'OBI:0001463': 0,  # Arrays

                           'OBI:0000693': 0,  # MeDIP
                           'OBI:0001861': 0,  # MRE-seq
                           'OBI:0001863': 0,  # MethylCap-seq
                           'OBI:0001862': 0}  # RRBS
        project_detail = 'required according to standards of NIH ' + \
                         'Roadmap Minimal Reference Epigenome'
    else:
        required_assays = {('OBI:0000716', 'Control'): 0,
                           ('OBI:0000716', 'H3K27me3'): 0,
                           ('OBI:0000716', 'H3K36me3'): 0,
                           ('OBI:0000716', 'H3K4me1'): 0,
                           ('OBI:0000716', 'H3K4me3'): 0,
                           ('OBI:0000716', 'H3K27ac'): 0,
                           ('OBI:0000716', 'H3K9me3'): 0,
                           'OBI:0001863': 0,  # WGBS
                           'OBI:0001271': 0}  # RNA-seq
        project_detail = 'required according to standards of Minimal IHEC Reference Epigenome.'

    for assay in value['related_datasets']:
        assay_id = assay['assay_term_id']
        if (assay_id == 'OBI:0000716'):
            if 'target' in assay:
                assay_taget = assay['target']['label']
                key = (assay_id, assay_taget)
                if key in required_assays:
                    required_assays[key] = 1
        elif assay_id in required_assays:
                required_assays[assay_id] = 1

    if required_assays[('OBI:0000716', 'Control')] == 0:
        detail = detail_prefix + \
            'is missing control ChIP-seq assay, ' + \
            project_detail
        yield AuditFailure('partial reference epigenome', detail, level='WARNING')
    if required_assays[('OBI:0000716', 'H3K27me3')] == 0:
        detail = detail_prefix + \
            'is missing H3K27me3 ChIP-seq assay, ' + \
            project_detail
        yield AuditFailure('partial reference epigenome', detail, level='WARNING')
    if required_assays[('OBI:0000716', 'H3K36me3')] == 0:
        detail = detail_prefix + \
            'is missing H3K36me3 ChIP-seq assay, ' + \
            project_detail
        yield AuditFailure('partial reference epigenome', detail, level='WARNING')
    if required_assays[('OBI:0000716', 'H3K4me1')] == 0:
        detail = detail_prefix + \
            'is missing H3K4me1 ChIP-seq assay, ' + \
            project_detail
        yield AuditFailure('partial reference epigenome', detail, level='WARNING')
    if required_assays[('OBI:0000716', 'H3K4me3')] == 0:
        detail = detail_prefix + \
            'is missing H3K4me3 ChIP-seq assay, ' + \
            project_detail
        yield AuditFailure('partial reference epigenome', detail, level='WARNING')

    if required_assays[('OBI:0000716', 'H3K9me3')] == 0:
        detail = detail_prefix + \
            'is missing H3K9me3 ChIP-seq assay, ' + \
            project_detail
        yield AuditFailure('partial reference epigenome', detail, level='WARNING')

    if roadmap_flag is True:
        rna_assays = required_assays['OBI:0001271'] + \
            required_assays['OBI:0001463']

        methylation_assays = required_assays['OBI:0000693'] + \
            required_assays['OBI:0001861'] + \
            required_assays['OBI:0001863'] + \
            required_assays['OBI:0001862']

        if methylation_assays == 0:
            detail = detail_prefix + \
                'is missing MeDIP-seq, MRE-seq, RRBS, or MethylCap-seq assays. ' + \
                'At least one is ' + project_detail
            yield AuditFailure('partial reference epigenome', detail, level='WARNING')
        if rna_assays == 0:
            detail = detail_prefix + \
                'is missing RNA-seq or array based transcription assays. ' + \
                'At least one is ' + project_detail
            yield AuditFailure('partial reference epigenome', detail, level='WARNING')
    else:
        if required_assays[('OBI:0000716', 'H3K27ac')] == 0:
            detail = detail_prefix + \
                'is missing H3K27ac ChIP-seq assay, ' + \
                project_detail
            yield AuditFailure('partial reference epigenome', detail, level='WARNING')
        if required_assays['OBI:0001863'] == 0:
            detail = detail_prefix + \
                'is missing WGBS assay, ' + \
                project_detail
            yield AuditFailure('partial reference epigenome', detail, level='WARNING')
        if required_assays['OBI:0001271'] == 0:
            detail = detail_prefix + \
                'is missing RNA-seq assay, ' + \
                project_detail
            yield AuditFailure('partial reference epigenome', detail, level='WARNING')
    return
