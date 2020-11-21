from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)

from .item import STATUS_LEVEL


def audit_file_ref_info(value, system):
    if 'derived_from' not in value:
        return
    for f in value['derived_from']:
        for ref_prop in ['assembly', 'genome_annotation']:
            if f.get(ref_prop) and value.get(ref_prop) and \
               f.get(ref_prop) != value.get(ref_prop):
                detail = ('Processed file {} {} {} '
                    'does not match {} {} of the file {} '
                    'it was derived from.'.format(
                        audit_link(path_to_text(value['@id']), value['@id']),
                        ref_prop,
                        value[ref_prop],
                        ref_prop,
                        f[ref_prop],
                        audit_link(path_to_text(f['@id']), f['@id'])
                    )
                )
                yield AuditFailure('inconsistent reference', detail, level='ERROR')


def audit_library_protocol_standards(value, system):
    if 'RawSequenceFile' not in value.get('@type'):
        return

    lib_prots = set()
    for l in value.get('libraries'):
        lp_name = l['protocol']['name']
        lib_prots.add(lp_name)
    if len(lib_prots) != 1:
        detail = ('File {} derives from Libraries of variable library protocols - {}.'.format(
            audit_link(path_to_text(value['@id']), value['@id']),
            lib_prots
            )
        )
        yield AuditFailure('variable library protocols', detail, level='ERROR')
        return
    else:
        no_stds_flag = False
        if not value['libraries'][0]['protocol'].get('sequence_file_standards'):
            no_stds_flag = True
        else:
            my_standards = ''
            for standard in value['libraries'][0]['protocol'].get('sequence_file_standards'):
                if standard['read_type'] == value.get('read_type'):
                    my_standards = standard
                    break
            if no_stds_flag == True or my_standards == '':
                detail = ('File {} derives from Library Protocol {} with no noted standards for read_type {}.'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    audit_link(path_to_text(value['libraries'][0]['protocol']['@id']), value['libraries'][0]['protocol']['@id']),
                    value.get('read_type')
                    )
                )
                yield AuditFailure('no protocol standards', detail, level='ERROR')
                return
            for k in ['sequence_elements', 'demultiplexed_type']:
                if my_standards[k] != value.get(k):
                    detail = ('{} of file {} should be {} but is {}'.format(
                        k,
                        audit_link(path_to_text(value['@id']), value['@id']),
                        my_standards[k],
                        value.get(k)
                        )
                    )
                    yield AuditFailure('does not meet protocol standards', detail, level='INTERNAL_ACTION')
            if my_standards['read_length'] != value.get('read_length'):
                std_flag = False
                rl_spec = my_standards['read_length_specification']
                if rl_spec == 'exact':
                    rl_spec = 'exactly'
                    audit_level = 'ERROR'
                    std_flag = True
                elif rl_spec == 'minimum' and value.get('read_length') < my_standards['read_length']:
                    audit_level = 'ERROR'
                    std_flag = True
                elif rl_spec == 'ideal':
                    rl_spec = 'ideally'
                    audit_level = 'WARNING'
                    std_flag = True
                if std_flag == True:
                    detail = ('{} of file {} is {}, should be {} {} based on standards for {}'.format(
                        'read_length',
                        audit_link(path_to_text(value['@id']), value['@id']),
                        value.get('read_length'),
                        rl_spec,
                        my_standards['read_length'],
                        audit_link(path_to_text(value['libraries'][0]['protocol']['@id']), value['libraries'][0]['protocol']['@id'])
                        )
                    )
                    yield AuditFailure('does not meet protocol standards', detail, level=audit_level)


def audit_cellranger_spec(value, system):
    if 'AnalysisFile' not in value.get('@type'):
        return

    non_rna_flag = False
    for l in value.get('libraries'):
        if l['protocol'].get('library_type') != 'RNA-seq':
            non_rna_flag = True
    if non_rna_flag == True and value.get('cellranger_assay_chemistry'):
        detail = ('File {} of file has {} and derives from at least one non-RNA-seq library'.format(
            audit_link(path_to_text(value['@id']), value['@id']),
            'cellranger_assay_chemistry',
            )
        )
        yield AuditFailure('cellranger spec inconsistent with library_type', detail, level="ERROR")
        return


function_dispatcher = {
    'audit_file_ref_info': audit_file_ref_info,
    'audit_library_protocol_standards': audit_library_protocol_standards,
    'audit_cellranger_spec': audit_cellranger_spec
}


@audit_checker('File',
               frame=['derived_from',
                      'libraries',
                      'libraries.protocol'])
def audit_file(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure

