from ..auditor import (
    AuditFailure,
    audit_checker,
)

current_statuses = ['released', 'in progress']
not_current_statuses = ['revoked', 'obsolete', 'deleted']


@audit_checker('file')
def audit_file_status(value, system):

    file_status = value.get('status')

    if file_status == 'deleted':
        return

    if 'dataset' not in value:
        detail = 'missing dataset'
        raise AuditFailure('missing dataset', detail, level='ERROR')

#    dataset_status = value['dataset']
#    if 'status' not in dataset_status:
#        return

#    if file_status == 'released' and dataset_status != 'released':
#        detail = '{} file - {} dataset'.format(file_status, dataset_status)
#        raise AuditFailure('status mismatch', detail, level='ERROR')

#    if file_status in current_statuses and dataset_status in not_current_statuses:
#        detail = '{} file - {} dataset'.format(file_status, dataset_status)
#        raise AuditFailure('status mismatch', detail, level='ERROR')


@audit_checker('file')
def audit_file_ownership(value, system):

    if value.get('status') == 'deleted':
        return

    for term in ['submitted_by', 'award', 'lab']:
        if term not in value:
            detail = 'missing {}'.format(term)
            yield AuditFailure('missing {}'.format(term), detail, level='ERROR')

    # submitter_lab = value['submitted_by']['lab']['name']
    # dataset_lab = value['dataset']['lab']['name']
    # submitter_award= value['submitted_by']['award']['name']
    # dataset_award = value['dataset']['award']['name']

#    if submitter_lab != dataset_lab:
#        detail = '{} file - {} dataset'.format(submitter_lab, dataset_lab)
#        raise AuditFailure('lab mismatch', detail, level='ERROR')

#    if submitter_award != dataset_award:
#        detail = '{} file - {} dataset'.format(submitter_award, dataset_award)
#        raise AuditFailure('award mismatch', detail, level='ERROR')


@audit_checker('file')
def audit_file_output_type(value, system):

    if value.get('status') == 'deleted':
        return

    undesirable_output_type = ["Alignability",
                                "Base_Overlap_Signal",
                                "enhancers_forebrain",
                                "enhancers_heart",
                                "enhancers_wholebrain",
                                "Excludable",
                                "ExonsDeNovo",
                                "ExonsEnsV65IAcuff",
                                "ExonsGencV10",
                                "ExonsGencV3c",
                                "ExonsGencV7",
                                "FiltTransfrags",
                                "GeneDeNovo",
                                "GeneEnsV65IAcuff",
                                "GeneGencV10",
                                "GeneGencV3c",
                                "GeneGencV7",
                                "HMM",
                                "Junctions",
                                "library_fraction",
                                "Matrix",
                                "minus signal",
                                "mPepMapGcFt",
                                "mPepMapGcUnFt"
                                "PctSignal"
                                "pepMapGcFt",
                                "pepMapGcUnFt",
                                "Primer",
                                "PrimerPeaks",
                                "RbpAssocRna",
                                "SumSignal",
                                "TranscriptDeNovo",
                                "TranscriptEnsV65IAcuff",
                                "TranscriptGencV10",
                                "TranscriptGencV3c",
                                "TranscriptGencV7",
                                "Transfrags",
                                "TssGencV3c",
                                "TssGencV7",
                                "TssHmm",
                                "UniformlyProcessedPeakCalls",
                                "Uniqueness",
                                "Validation",
                                "Valleys",
                                "WaveSignal"]

    #if value['dataset']['award']['rfa'] != 'ENCODE3':
    if value['output_type'] in undesirable_output_type:
            detail = '{}'.format(value['output_type'])
            raise AuditFailure('undesirable output type', detail, level='ERROR')