from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)

from .item import STATUS_LEVEL


def no_read_type(value, system):
    if value.get('no_file_available') != True:
        if not value.get('read_type'):
            detail = ('File {} does not have a read_type.'.format(
                audit_link(path_to_text(value['@id']), value['@id'])
                )
            )
            yield AuditFailure('no read_type', detail, level='ERROR')
            return


def no_file_name(value, system):
    if value.get('no_file_available') != True:
        if not value.get('submitted_file_name'):
            detail = ('File {} does not have a submitted_file_name.'.format(
                audit_link(path_to_text(value['@id']), value['@id'])
                )
            )
            yield AuditFailure('no submitted_file_name', detail, level='ERROR')
            return
        elif (value.get('submitted_file_name').startswith('/') or value.get('submitted_file_name').endswith('/')):
            detail = ('File {} submitted_file_name {} has a leading or trailing slash.'.format(
                audit_link(path_to_text(value['@id']), value['@id'],),
                value.get('submitted_file_name')
                )
            )
            yield AuditFailure('invalid submitted_file_name', detail, level='ERROR')
            return


def no_file_stats(value, system):
    if value.get('no_file_available') != True and value.get('validated') == True:
        missing = []
        for stat in ['file_size','sha256','crc32c']:
            if not value.get(stat):
                missing.append(stat)
        if missing:
            detail = ('File {} does not have {}.'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                ','.join(missing)
                )
            )
            yield AuditFailure('missing file stats', detail, level='ERROR')
            return


def not_validated(value, system):
    if value.get('no_file_available') != True:
        if value.get('validated') != True:
            detail = ('File {} has not been validated.'.format(
                audit_link(path_to_text(value['@id']), value['@id'])
                )
            )
            yield AuditFailure('file not validated', detail, level='ERROR')
            return


def no_uri(value, system):
    if value.get('no_file_available') != True:
        if not (value.get('s3_uri') or value.get('external_uri')):
            detail = ('File {} has no s3_uri, external_uri, and is not marked as no_file_available.'.format(
                audit_link(path_to_text(value['@id']), value['@id'])
                )
            )
            yield AuditFailure('file access not specified', detail, level='ERROR')
            return


def audit_library_protocol_standards(value, system):
    '''
    We check fastq metadata against the expected values based on the
    library protocol used to generate the sequence data.
    '''
    if value.get('no_file_available') != True and value.get('validated') == True:
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
                    if not value.get('read_length'):
                        audit_level = 'ERROR'
                        std_flag = True
                    elif rl_spec == 'exact':
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


function_dispatcher = {
    'no_read_type': no_read_type,
    'no_file_name': no_file_name,
    'no_file_stats': no_file_stats,
    'not_validated': not_validated,
    'no_uri': no_uri,
    'audit_library_protocol_standards': audit_library_protocol_standards
}


@audit_checker('RawSequenceFile',
               frame=['libraries',
                      'libraries.protocol'])
def audit_file(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure

