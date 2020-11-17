import pytest


def test_treatment_time_series_mixed_units(
    testapp,
    treatment_time_series,
    experiment_chip_H3K4me3,
    experiment_chip_H3K27me3,
    replicate_1_chip,
    replicate_2_chip,
    library_1_chip,
    library_2_chip,
    biosample_human_1,
    biosample_human_2,
    treatment_5,
    treatment_with_duration_amount_units
):
    testapp.patch_json(treatment_time_series['@id'], {'related_datasets': [experiment_chip_H3K4me3['@id'], experiment_chip_H3K27me3['@id']]})
    testapp.patch_json(treatment_5['@id'], {'duration': 9, 'duration_units': 'minute'})
    testapp.patch_json(biosample_human_1['@id'], {'treatments': [treatment_5['@id']]})
    testapp.patch_json(biosample_human_2['@id'], {'treatments': [treatment_with_duration_amount_units['@id']]})
    testapp.patch_json(replicate_2_chip['@id'], {'experiment': experiment_chip_H3K4me3['@id']})
    res = testapp.get(treatment_time_series['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mixed duration units in treatment time series' for error in errors_list)


def test_treatment_concentration_series_mixed_units(
    testapp,
    treatment_concentration_series,
    experiment_chip_H3K4me3,
    experiment_chip_H3K27me3,
    replicate_1_chip,
    replicate_2_chip,
    library_1_chip,
    library_2_chip,
    biosample_human_1,
    biosample_human_2,
    treatment_5,
    treatment_with_duration_amount_units
):
    testapp.patch_json(treatment_concentration_series['@id'], {'related_datasets': [experiment_chip_H3K4me3['@id'], experiment_chip_H3K27me3['@id']]})
    testapp.patch_json(treatment_5['@id'], {'amount': 9, 'amount_units': 'nM'})
    testapp.patch_json(biosample_human_1['@id'], {'treatments': [treatment_5['@id']]})
    testapp.patch_json(biosample_human_2['@id'], {'treatments': [treatment_with_duration_amount_units['@id']]})
    testapp.patch_json(replicate_2_chip['@id'], {'experiment': experiment_chip_H3K4me3['@id']})
    res = testapp.get(treatment_concentration_series['@id'] + '@@index-data')
    errors = res.json['audit']
    errors_list = []
    for error_type in errors:
        errors_list.extend(errors[error_type])
    assert any(error['category'] == 'mixed amount units in treatment concentration series' for error in errors_list)
