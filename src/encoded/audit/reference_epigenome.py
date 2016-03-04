from snowfort import (
    AuditFailure,
    audit_checker,
)


@audit_checker('ReferenceEpigenome', frame=['related_datasets',
                                            'related_datasets.replicates',
                                            'related_datasets.replicates.library',
                                            'related_datasets.replicates.library.biosample',
                                            'related_datasets.replicates.library.biosample.donor'])
def audit_reference_epigenome_donor_biosample(value, system):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if 'related_datasets' not in value:
        return

    biosample_name_set = set()
    donor_set = set()
    for assay in value['related_datasets']:
        if assay['status'] not in ['deleted', 'replaced', 'revoked']:
            if 'replicates' in assay:
                for rep in assay['replicates']:
                    if rep['status'] not in ['deleted'] and \
                       'library' in rep and 'biosample' in rep['library']:
                        biosample_object = rep['library']['biosample']
                        if 'biosample_term_name' in biosample_object:
                            biosample_name_set.add(biosample_object['biosample_term_name'])
                        if 'donor' in biosample_object:
                            donor_set.add(biosample_object['donor']['accession'])
    if len(biosample_name_set) > 1:
        detail = 'Reference Epigenome {} '.format(value['@id']) + \
                 ' has multiple biosample term names {}.'.format(biosample_name_set)
        yield AuditFailure('multiple biosample term names in reference epigenome',
                           detail, level='WARNING')
    if len(donor_set) > 1:
        detail = 'Reference Epigenome {} '.format(value['@id']) + \
                 ' has multiple donors {}.'.format(donor_set)
        yield AuditFailure('multiple donors in reference epigenome', detail, level='WARNING')
    return


@audit_checker('ReferenceEpigenome', frame=['related_datasets',
                                            'related_datasets.target'])
def audit_reference_epigenome_assay_types_requirments(value, system):
    if 'related_datasets' not in value:
        detail = 'Reference Epigenome {} '.format(value['@id']) + \
                 'has no related datasets. It lacks all IHEC required ' + \
                 'assays.'
        yield AuditFailure('missing IHEC required assay', detail, level='WARNING')
        return
    required_assays = {('ChIP-seq', 'Control'): 0,
                       ('ChIP-seq', 'H3K27me3'): 0,
                       ('ChIP-seq', 'H3K36me3'): 0,
                       ('ChIP-seq', 'H3K4me1'): 0,
                       ('ChIP-seq', 'H3K4me3'): 0,
                       ('ChIP-seq', 'H3K27ac'): 0,
                       ('ChIP-seq', 'H3K9me3'): 0,
                       'whole-genome shotgun bisulfite sequencing': 0,
                       'RNA-seq': 0}

    for assay in value['related_datasets']:
        assay_name = assay['assay_term_name']
        if (assay_name == 'ChIP-seq'):
            if 'target' in assay:
                assay_taget = assay['target']['label']
                key = (assay_name, assay_taget)
                if key in required_assays:
                    required_assays[key] = 1
        elif assay_name in required_assays:
                required_assays[assay_name] = 1
    if required_assays[('ChIP-seq', 'Control')] == 0:
        detail = 'Reference Epigenome {} '.format(value['@id']) + \
                 'missing IHEC required control ChIP-seq assay.'
        yield AuditFailure('missing IHEC required assay', detail, level='WARNING')
    if required_assays[('ChIP-seq', 'H3K27me3')] == 0:
        detail = 'Reference Epigenome {} '.format(value['@id']) + \
                 'missing IHEC required H3K27me3 ChIP-seq assay.'
        yield AuditFailure('missing IHEC required assay', detail, level='WARNING')
    if required_assays[('ChIP-seq', 'H3K36me3')] == 0:
        detail = 'Reference Epigenome {} '.format(value['@id']) + \
                 'missing IHEC required H3K36me3 ChIP-seq assay.'
        yield AuditFailure('missing IHEC required assay', detail, level='WARNING')
    if required_assays[('ChIP-seq', 'H3K4me1')] == 0:
        detail = 'Reference Epigenome {} '.format(value['@id']) + \
                 'missing IHEC required H3K4me1 ChIP-seq assay.'
        yield AuditFailure('missing IHEC required assay', detail, level='WARNING')
    if required_assays[('ChIP-seq', 'H3K4me3')] == 0:
        detail = 'Reference Epigenome {} '.format(value['@id']) + \
                 'missing IHEC required H3K4me3 ChIP-seq assay.'
    if required_assays[('ChIP-seq', 'H3K27ac')] == 0:
        detail = 'Reference Epigenome {} '.format(value['@id']) + \
                 'missing IHEC required H3K27ac ChIP-seq assay.'
        yield AuditFailure('missing IHEC required assay', detail, level='WARNING')
    if required_assays[('ChIP-seq', 'H3K9me3')] == 0:
        detail = 'Reference Epigenome {} '.format(value['@id']) + \
                 'missing IHEC required H3K9me3 ChIP-seq assay.'
        yield AuditFailure('missing IHEC required assay', detail, level='WARNING')
    if required_assays['whole-genome shotgun bisulfite sequencing'] == 0:
        detail = 'Reference Epigenome {} '.format(value['@id']) + \
                 'missing IHEC required WGBS assay.'
        yield AuditFailure('missing IHEC required assay', detail, level='WARNING')
    if required_assays['RNA-seq'] == 0:
        detail = 'Reference Epigenome {} '.format(value['@id']) + \
                 'missing IHEC required RNA-seq assay.'
        yield AuditFailure('missing IHEC required assay', detail, level='WARNING')
    return
