from snovault import (
    AuditFailure,
    audit_checker,
)
from .experiment import (
    audit_experiment_documents,
    audit_experiment_no_processed_data,
    audit_experiment_replicated,
    audit_experiment_replicates_biosample,
    audit_experiment_replicates_with_no_libraries,
    audit_experiment_technical_replicates_same_library,
    audit_experiment_inconsistent_genetic_modifications,
    create_files_mapping
)
from .formatter import (
    audit_link,
    path_to_text,
)


def audit_experiment_biosample(value, system, excluded_types):
    if value['status'] in excluded_types:
        return
    if value.get('biosample_ontology', {}).get('classification') in ('cell-free sample', 'cloning host'):
        return
    exp_bio_ontology = value['biosample_ontology']
    if exp_bio_ontology['term_id'].startswith('NTR:'):
        detail = (
            'Experiment {} has an NTR biosample {} - {}'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                exp_bio_ontology['term_id'],
                exp_bio_ontology['term_name']
            )
        )
        yield AuditFailure('NTR biosample', detail, level='INTERNAL_ACTION')

    for rep in value.get('replicates', []):
        lib = rep.get('library')
        if not lib:
            continue
        if 'biosample' not in lib:
            detail = (
                'Library {} is missing biosample, '
                'expecting one of type {}'.format(
                    audit_link(path_to_text(lib['@id']), lib['@id']),
                    exp_bio_ontology['term_name']
                )
            )
            yield AuditFailure('missing biosample', detail, level='ERROR')
            continue
        biosample = lib['biosample']
        if biosample['biosample_ontology']['@id'] != exp_bio_ontology['@id']:
            detail = (
                "Experiment {} contains a library {} linked to biosample "
                "type '{}', while experiment's biosample type "
                "is '{}'.".format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    audit_link(path_to_text(lib['@id']), lib['@id']),
                    audit_link(
                        path_to_text(biosample['biosample_ontology']['@id']),
                        biosample['biosample_ontology']['@id']
                    ),
                    audit_link(
                        path_to_text(exp_bio_ontology['@id']),
                        exp_bio_ontology['@id']
                    )
                )
            )
            yield AuditFailure(
                'inconsistent library biosample', detail, level='ERROR'
            )


def audit_experiment_missing_modification(value, system, excluded_types):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return
    if value['assay_term_name'] == 'pooled clone sequencing':
        return
    for rep in value.get('replicates', []):
        lib = rep.get('library')
        if not lib:
            continue
        if 'biosample' in lib:
            if lib['biosample'].get('applied_modifications', []):
                continue
            detail = (
                'Biosample {} has no genetic modifications.'.format(
                    audit_link(
                        path_to_text(lib['biosample']['@id']),
                        lib['biosample']['@id']
                    ),
                )
            )
            yield AuditFailure(
                'missing genetic modification', detail, level='ERROR'
            )


def audit_experiment_replicate_with_no_files(value, system, excluded_statuses):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return
    if not value.get('replicates'):
        return
    replicates_with_raw_data = {
        f['replicate']['@id']
        for f in value.get('original_files')
        if (
            f['status'] not in (set(excluded_statuses) - {'archived'})
            and f['output_category'] == 'raw data'
            and 'replicate' in f
        )
    }
    for rep in value.get('replicates'):
        if rep['@id'] in replicates_with_raw_data:
            continue
        detail = (
            'This experiment contains a replicate '
            '[{},{}] {} without raw data associated files.'.format(
                rep['biological_replicate_number'],
                rep['technical_replicate_number'],
                audit_link(path_to_text(rep['@id']), rep['@id'])
            )
        )
        yield AuditFailure(
            'missing raw data in replicate', detail, level='ERROR'
        )


def audit_experiment_mixed_expression_measurement_methods(value, system, excluded_types):
    if value['status'] in excluded_types:
        return
    if value['assay_term_name'] != 'CRISPR screen':
        return
    if 'examined_loci' not in value:
        return
    methods = []
    for locus in value.get('examined_loci'):
        if 'expression_measurement_method' not in locus:
            methods.append('none')
        else:
            methods.append(locus.get('expression_measurement_method'))
    if len(set(methods)) == 1:
        return
    else:
        methods_detail = ', '.join(methods)
        detail = f'This experiment uses multiple expression measurement methods, {methods_detail}.'
        yield AuditFailure(
            'mixed expression_measurement_method', detail, level='WARNING'
        )


def audit_CRISPR_screen_not_in_series(value, system, excluded_types):
    '''CRISPR screen experiments are expected to belong to a series'''
    if value['status'] in excluded_types:
        return
    if value['assay_term_name'] != 'CRISPR screen':
        return
    related_series = value.get('related_series', [])
    if related_series == []:
        detail = f'CRISPR screen {audit_link(path_to_text(value["@id"]),value["@id"])} is not part of a series.'
        yield AuditFailure('missing related_series', detail, level='INTERNAL_ACTION')


function_dispatcher_without_files = {
    'audit_biosample': audit_experiment_biosample,
    'audit_documents': audit_experiment_documents,
    'audit_missing_modifiction': audit_experiment_missing_modification,
    'audit_replicate_no_files': audit_experiment_replicate_with_no_files,
    'audit_replicated': audit_experiment_replicated,
    'audit_replicates_biosample': audit_experiment_replicates_biosample,
    'audit_replicates_no_libraries': audit_experiment_replicates_with_no_libraries,
    'audit_technical_replicates_same_library': audit_experiment_technical_replicates_same_library,
    'audit_inconsistent_genetic_modifications': audit_experiment_inconsistent_genetic_modifications,
    'audit_experiment_mixed_expression_measurement_methods': audit_experiment_mixed_expression_measurement_methods,
    'audit_CRISPR_screen_not_in_series': audit_CRISPR_screen_not_in_series,
}
function_dispatcher_with_files = {
    'audit_no_processed_data': audit_experiment_no_processed_data,
}


@audit_checker(
    'FunctionalCharacterizationExperiment',
    frame=[
        'award',
        'biosample_ontology',
        'original_files',
        'original_files.replicate',
        'replicates',
        'replicates.library',
        'replicates.library.biosample',
        'replicates.library.biosample.biosample_ontology',
        'replicates.library.biosample.applied_modifications',
        'replicates.library.biosample.donor',
    ]
)
def audit_fcc_experiment(value, system):
    excluded_files = ['revoked', 'archived']
    if value.get('status') == 'revoked':
        excluded_files = []
    if value.get('status') == 'archived':
        excluded_files = ['revoked']
    files_structure = create_files_mapping(
        value.get('original_files'), excluded_files)

    for function_name in function_dispatcher_with_files.keys():
        yield from function_dispatcher_with_files[function_name](
            value, system, files_structure
        )

    excluded_types = excluded_files + ['deleted', 'replaced']
    for function_name in function_dispatcher_without_files.keys():
        yield from function_dispatcher_without_files[function_name](
            value, system, excluded_types
        )
