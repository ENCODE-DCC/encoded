from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)

from .item import STATUS_LEVEL


def audit_validated(value, system):
    '''
    We check fastq metadata against the expected values based on the
    library protocol used to generate the sequence data.
    '''
    if value.get('no_file_available') != True:
        if value.get('s3_uri') or value.get('external_uri'):
            if value.get('validated') != True and value.get('file_format') in ['hdf5']:
                detail = ('File {} has not been validated.'.format(
                    audit_link(path_to_text(value['@id']), value['@id'])
                    )
                )
                yield AuditFailure('file not validated', detail, level='ERROR')
                return
        else:
            detail = ('File {} has no s3_uri, external_uri, and is not marked as no_file_available.'.format(
                audit_link(path_to_text(value['@id']), value['@id'])
                )
            )
            yield AuditFailure('file access not specified', detail, level='WARNING')
            return


def audit_file_ref_info(value, system):
    '''
    A file's reference metadata should match the reference
    metadata of any file it was derived from
    '''
    if 'derived_from' not in value and 'AnalysisFile' not in value.get('@type'):
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


def audit_analysis_library_types(value, system):
    '''
    An AnalysisFile should only have cellranger_assay_chemistry metadata
    if it is from an RNA-seq library.
    We expect CITE-seq libraries to be paired with RNA-seq libraries.
    '''
    if 'AnalysisFile' not in value.get('@type'):
        return

    lib_types = set()
    for l in value.get('libraries'):
        lib_types.add(l['protocol'].get('library_type'))
    if 'RNA-seq' not in lib_types and value.get('cellranger_assay_chemistry'):
        detail = ('File {} has {} and does not derive from any RNA-seq library'.format(
            audit_link(path_to_text(value['@id']), value['@id']),
            'cellranger_assay_chemistry',
            )
        )
        yield AuditFailure('cellranger spec inconsistent with library_type', detail, level="ERROR")

    if 'CITE-seq' in lib_types and 'RNA-seq' not in lib_types:
        detail = ('File {} derives from at least one CITE-seq library but does not derive from any RNA-seq library'.format(
            audit_link(path_to_text(value['@id']), value['@id']),
            'cellranger_assay_chemistry',
            )
        )
        yield AuditFailure('no RNA-seq Library with CITE-seq Library', detail, level="ERROR")
        return


function_dispatcher = {
    'audit_validated': audit_validated,
    'audit_file_ref_info': audit_file_ref_info,
    'audit_analysis_library_types': audit_analysis_library_types
}


@audit_checker('AnalysisFile',
               frame=['derived_from',
                      'libraries',
                      'libraries.protocol'])
def audit_file(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure

