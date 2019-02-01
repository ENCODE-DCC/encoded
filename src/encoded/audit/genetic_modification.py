from snovault import (
    AuditFailure,
    audit_checker,
)

@audit_checker('GeneticModification', 
               frame=['object',
                      'biosamples_modified',
                      'biosamples_modified.organism',
                      'donors_modified',
                      'donors_modified.organism',
                     ]
                )
def audit_genetic_modification_reagents(value, system):
    '''
    Genetic modifications with missing reagents will be flagged by this audit.
    Modifications with acceptable substitutes for reagents will not be flagged,
    depending on their method. See the method dependency description in
    file.json for more detail.
    '''
    flies = ['ab546d43-8e2a-4567-8db7-a217e6d6eea0',
             '5be68469-94ba-4d60-b361-dde8958399ca',
             '74144f1f-f3a6-42b9-abfd-186a1ca93198',
             'c3cc08b7-7814-4cae-a363-a16b76883e3f',
             'd1072fd2-8374-4f9b-85ce-8bc2c61de122',
             'b9ce90a4-b791-40e9-9b4d-ffb1c6a5aa2b',
             '0bdd955a-57f0-4e4b-b93d-6dd1df9b766c']
    if value['method'] == 'RNAi' and 'biosamples_modified' in value:
        for biosample in value['biosamples_modified']:
            if biosample['organism']['uuid'] in flies:
                return
    if value['method'] == 'RNAi' and 'donors_modified' in value:
        for donor in value['donors_modified']:
            if donor['organism']['uuid'] in flies:
                return
    if not value.get('reagents'):
        missing_reagents = False
        method = value['method']
        if method == 'CRISPR':
            if not value.get('guide_rna_sequences'):
                missing_reagents = True
        elif method == 'RNAi':
            if not value.get('rnai_sequences'):
                missing_reagents = True
        elif method == 'TALEN':
            if not value.get('RVD_sequence_pairs'):
                missing_reagents = True
        elif not value.get('documents'):
            missing_reagents = True

        if missing_reagents:
            detail = 'Genetic modification {} of method {} is missing reagents'.format(
                value['@id'],
                method,
            )
            yield AuditFailure('missing genetic modification reagents', detail, level='ERROR')
