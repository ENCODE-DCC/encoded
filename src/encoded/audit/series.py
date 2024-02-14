from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


@audit_checker('TreatmentTimeSeries', frame=['related_datasets',
                                            'related_datasets.replicates',
                                            'related_datasets.replicates.library',
                                            'related_datasets.replicates.library.biosample',
                                            'related_datasets.replicates.library.biosample.treatments'])
def audit_treatment_time_series_mixed_units(value, system):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if 'related_datasets' not in value:
        return

    treatment_duration_units = set()
    for assay in value['related_datasets']:
        if assay['status'] not in ['deleted', 'replaced', 'revoked']:
            if 'replicates' in assay:
                for rep in assay['replicates']:
                    if rep['status'] not in ['deleted'] and \
                       'library' in rep and 'biosample' in rep['library']:
                        biosample_object = rep['library']['biosample']
                        if 'treatments' in biosample_object:
                            if len(biosample_object['treatments']) != 0:
                                for t in biosample_object['treatments']:
                                    treatment_duration_units.add(t['duration_units'])
    if len(treatment_duration_units) > 1:
        detail = (f"Treatments associated with series {audit_link(path_to_text(value['@id']), value['@id'])} "
            f"use inconsistent duration units {treatment_duration_units}."
        )
        yield AuditFailure('inconsistent treatment units',
                           detail, level='INTERNAL_ACTION')
        return


@audit_checker('TreatmentConcentrationSeries', frame=['related_datasets',
                                            'related_datasets.replicates',
                                            'related_datasets.replicates.library',
                                            'related_datasets.replicates.library.biosample',
                                            'related_datasets.replicates.library.biosample.treatments'])
def audit_treatment_concentration_series_mixed_units(value, system):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if 'related_datasets' not in value:
        return

    treatment_amount_units = set()
    for assay in value['related_datasets']:
        if assay['status'] not in ['deleted', 'replaced', 'revoked']:
            if 'replicates' in assay:
                for rep in assay['replicates']:
                    if rep['status'] not in ['deleted'] and \
                       'library' in rep and 'biosample' in rep['library']:
                        biosample_object = rep['library']['biosample']
                        if 'treatments' in biosample_object:
                            if len(biosample_object['treatments']) != 0:
                                for t in biosample_object['treatments']:
                                    treatment_amount_units.add(t['amount_units'])
    if len(treatment_amount_units) > 1:
        detail = (f"Treatments associated with series {audit_link(path_to_text(value['@id']), value['@id'])} "
            f"use inconsistent amount units {treatment_amount_units}."
        )
        yield AuditFailure('inconsistent treatment units',
                           detail, level='INTERNAL_ACTION')
        return


@audit_checker('DifferentiationSeries', frame=[
    'related_datasets',
    'related_datasets.replicates',
    'related_datasets.replicates.library',
    'related_datasets.replicates.library.biosample'])
def audit_differentation_time_series_mixed_units(value, system):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if 'related_datasets' not in value:
        return

    post_differentation_time_units = set()
    for assay in value['related_datasets']:
        if assay['status'] not in ['deleted', 'replaced', 'revoked']:
            if 'replicates' in assay:
                for rep in assay['replicates']:
                    if rep['status'] not in ['deleted'] and \
                       'library' in rep and 'biosample' in rep['library']:
                        biosample_object = rep['library']['biosample']
                        if 'post_differentiation_time_units' in biosample_object:
                            post_differentation_time_units.add(biosample_object['post_differentiation_time_units'])
    if len(post_differentation_time_units) > 1:
        detail = (
            f"Biosamples associated with series {audit_link(path_to_text(value['@id']), value['@id'])} "
            f"use inconsistent post differentation time units {post_differentation_time_units}."
        )
        yield AuditFailure('inconsistent differentation time units',
                           detail, level='INTERNAL_ACTION')
        return
