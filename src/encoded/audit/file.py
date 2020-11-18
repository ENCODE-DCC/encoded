from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)

from .item import STATUS_LEVEL


def audit_file_assembly(value, system):
    if 'derived_from' not in value:
        return
    for f in value['derived_from']:
        if f.get('assembly') and value.get('assembly') and \
           f.get('assembly') != value.get('assembly'):
            detail = ('Processed file {} assembly {} '
                'does not match assembly {} of the file {} '
                'it was derived from.'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    value['assembly'],
                    f['assembly'],
                    audit_link(path_to_text(f['@id']), f['@id'])
                )
            )
            yield AuditFailure('inconsistent assembly',
                               detail, level='WARNING')
            return


def audit_file_genome_annotation(value, system):
    if 'derived_from' not in value:
        return
    for f in value['derived_from']:
        if f.get('genome_annotation') and value.get('genome_annotation') and \
           f.get('genome_annotation') != value.get('genome_annotation'):
            detail = ('Processed file {} genome_annotation {} '
                'does not match genome_annotation {} of the file {} '
                'it was derived from.'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    value['genome_annotation'],
                    f['genome_annotation'],
                    audit_link(path_to_text(f['@id']), f['@id'])
                )
            )
            yield AuditFailure('inconsistent genome_annotation',
                               detail, level='WARNING')
            return


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
        yield AuditFailure('Variable library protocols', detail, level='INTERNAL_ACTION')
        return
    else:
        no_stds_flag = False
        if not value['libraries'][0]['protocol'].get('standards'):
            no_stds_flag = True
        else:
            my_standards = ''
            for standard in value['libraries'][0]['protocol'].get('standards'):
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
                yield AuditFailure('No standards', detail, level='INTERNAL_ACTION')
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
                    yield AuditFailure('Not aligned with library protocol', detail, level='INTERNAL_ACTION')
            if my_standards['read_length'] != value.get('read_length'):
                std_flag = False
                rl_spec = my_standards['read_length_specification']
                if rl_spec == 'exact':
                    rl_spec = 'exactly'
                    audit_level = 'WARNING'
                    std_flag = True
                elif rl_spec == 'minimum' and value.get('read_length') < my_standards['read_length']:
                    audit_level = 'WARNING'
                    std_flag = True
                elif rl_spec == 'ideal':
                    rl_spec = 'ideally'
                    audit_level = 'INTERNAL_ACTION'
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
                    yield AuditFailure('Not aligned with library protocol', detail, level=audit_level)



function_dispatcher = {
    'audit_file_assembly': audit_file_assembly,
    'audit_file_genome_annotation': audit_file_genome_annotation,
    'audit_library_protocol_standards': audit_library_protocol_standards
}


@audit_checker('File',
               frame=['derived_from',
                      'libraries',
                      'libraries.protocol'])
def audit_file(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure

