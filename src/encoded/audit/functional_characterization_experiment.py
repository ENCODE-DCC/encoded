from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)
from .experiment import (
    audit_experiment_no_processed_data,
    create_files_mapping
)


function_dispatcher_without_files = {}
function_dispatcher_with_files = {
		'audit_no_processed_data': audit_experiment_no_processed_data
	}

@audit_checker(
	'FunctionalCharacterizationExperiment', 
	frame=[
		'original_files',
		'original_files.replicate'
	])
def audit_fcc_experiment(value, system):
    excluded_files = ['revoked', 'archived']
    if value.get('status') == 'revoked':
        excluded_files = []
    if value.get('status') == 'archived':
        excluded_files = ['revoked']
    files_structure = create_files_mapping(
        value.get('original_files'), excluded_files)

    for function_name in function_dispatcher_with_files.keys():
        yield from function_dispatcher_with_files[function_name](value, system, files_structure)

    excluded_types = excluded_files + ['deleted', 'replaced']
    for function_name in function_dispatcher_without_files.keys():
        yield from function_dispatcher_without_files[function_name](value, system, excluded_types)

    return
