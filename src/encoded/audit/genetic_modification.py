from snovault import (
    AuditFailure,
    audit_checker,
)


@audit_checker('GeneticModification', frame='object')
def audit_genetic_modification_reagents(value, system):
    '''
    Genetic modifications with missing reagents will be flagged by this audit.
    Modifications with acceptable substitutes for reagents will not be flagged,
    depending on their method. See the method dependecy in file.json for more
    detail.
    '''
    missing_reagents = False

    if not value.get('reagents'):
        method = value['method']
        if method == 'CRISPR':
            if not value.get('guide_rna_sequences'):
                missing_reagents = True
        elif method == 'RNAi':
            if not value.get('rnai_sequences'):
                missing_reagents = True
        elif method == 'TALEN':
            missing_reagents = True
        elif not value.get('documents'):
            missing_reagents = True

    if missing_reagents:
        detail = 'Genetic modification {} of method {} is missing reagents'.format(
            value['@id'],
            method)
        yield AuditFailure('missing genetic modification reagents', detail, level='ERROR')
