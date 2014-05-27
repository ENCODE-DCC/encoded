from ..auditor import (
    AuditFailure,
    audit_checker,
)


@audit_checker('experiment')
def audit_experiment_assay(value, system):
    '''
    Experiments should have assays with valid ontologies term ids and names that
    are a valid synonym.
    '''
    if 'assay_term_id' not in value:
        detail = 'assay_term_id missing'
        raise AuditFailure('missing assay information', detail, level='ERROR')

    if 'assay_term_name' not in value:
        detail = 'assay_term_name missing'
        raise AuditFailure('missing assay information', detail, level='ERROR')

    ontology = system['registry']['ontology']
    term_id = value.get('assay_term_id')
    term_name = value.get('assay_term_name')

    if term_id.startswith('NTR:'):
        detail = '{} - {}'.format(term_id, term_name)
        raise AuditFailure('NTR', detail, level='WARNING')

    # if term_id not in ontology:
    #    detail = 'assay_term_id - {}'.format(term_id)
    #    raise AuditFailure('assay term_id not in ontology', term_id, level='ERROR')

    # Must talk to nikhil and venkat about synonyms.  We want to  have a valid
    # synonym for that term


@audit_checker('experiment')
def audit_experiment_target(value, system):
    '''
    Certain assay types (ChIP-seq, ...) require valid targets and the replicate's
    antibodies should match.
    '''

    if ('assay_term_name' not in value) or (value['assay_term_name'] not in ['ChIP-seq', 'RNA Bind-n-Seq']):
        return

    if 'target' not in value:
        detail = '{} requires a target'.format(value['assay_term_name'])
        raise AuditFailure('missing target', detail, level='ERROR')

    target = value['target']['name']
    if target.startswith('Control'):
        return

    for i in range(0, len(value['replicates'])):
        rep = value['replicates'][i]
        if 'antibody' not in rep:
            detail = 'rep {} missing antibody'.format(rep["uuid"])
            raise AuditFailure('missing antibody', detail, level='ERROR')
            # What we really want here is a way to the approval, we want to know
            # if there is an approval for this antibody to this target
            # likely we should check if it the right species before thie point, or in library check


@audit_checker('experiment')
def audit_experiment_control(value, system):
    '''
    Certain assay types (ChIP-seq, ...) require possible controls with a matching biosample.
    Of course, controls do not require controls.
    '''
    if ('assay_term_name' not in value) or (value['assay_term_name'] not in ['ChIP-seq']):
        # RBNS, who else
        return

    if 'target' not in value or value['target']['name'].startswith('Control'):
        return

    if 'possible_controls' == []:
        detail = 'missing control'
        raise AuditFailure('missing possible controls', detail, level='ERROR')

    # A check should go here that would go through all possible controls to
    # verify that they are the same biosample term


@audit_checker('experiment')
def audit_experiment_biosample_term(value, system):
    '''
    The biosample term and id and type information should be present and
    concordent with library biosamples,
    probably there are assays that are the exception
    '''
    if 'biosample_term_id' not in value:
        return

    ontology = system['registry']['ontology']
    term_id = value.get('biosample_term_id')
    term_type = value.get('biosample_type')
    term_name = value.get('biosample_term_name')

    if term_id.startswith('NTR:'):
        detail = '{} - {}'.format(term_id, term_name)
        raise AuditFailure('NTR', detail, level='WARNING')

    if term_id not in ontology:
        raise AuditFailure('term id not in ontology', term_id, level='ERROR')

    ontology_term_name = ontology[term_id]['name']
    if ontology_term_name != term_name and term_name not in ontology[term_id]['synonyms']:
        detail = '{} - {} - {}'.format(term_id, term_name, ontology_term_name)
        raise AuditFailure('term name mismatch', detail, level='ERROR')

    for i in range(0, len(value['replicates'])):
        rep = value['replicates'][i]
        if 'library' not in rep:
            return

        lib = rep['library']
        if 'biosample' not in lib:
            detail = '{} missing biosample, expected {}'.format(lib['accession'], term_name)
            raise AuditFailure('missing biosample', detail, level='ERROR')

        biosample = lib['biosample']
        if 'biosample_term_id' not in biosample or 'biosample_term_name' not in biosample or 'biosample_type' not in biosample:
            return

        if biosample.get('biosample_type') != term_type:
            detail = '{} - {} in {}'.format(term_type, biosample.get('biosample_type'), lib['accession'])
            raise AuditFailure('biosample mismatch', detail, level='ERROR')

        if biosample.get('biosample_term_name') != term_name:
            detail = '{} - {} in {}'.format(term_name, biosample.get('biosample_term_name'), lib['accession'])
            raise AuditFailure('biosample mismatch', detail, level='ERROR')

        if biosample.get('biosample_term_id') != term_id:
            detail = '{} - {} in {}'.format(term_id, biosample.get('biosample_term_id'), lib['accession'])
            raise AuditFailure('biosample mismatch', detail, level='ERROR')


@audit_checker('experiment')
def audit_experiment_paired_end(value,system):
    '''
    Check that if the concordance of replicate and library information for paired end sequencing.
    '''
    ignore_assays = [
        "RNA Array",
        "Methyl Array",
        "Genotype",
        "RIP Array",
        "Proteogenomics",
        "microRNA Array",
        "Switchgear",
        "5C"
    ]

    paired_end_assays = [
        "RNA-PET",
        "ChIA-PET",
        "DNA-PET"
    ]

    term_name = value.get('assay_term_name')

    if term_name in ignore_assays:
        return

    for i in range(0, len(value['replicates'])):
        rep = value['replicates'][i]

        if 'paired_ended' not in rep:
            detail = '{} missing paired end information'.format(rep['uuid'])
            yield AuditFailure('missing replicate paired end', detail, level='ERROR')

        if 'library' not in rep:
            return

        lib = rep['library']

        if 'paired_ended' not in lib:
            detail = '{} missing paired end information'.format(lib['accession'])
            yield AuditFailure('missing library paired end', detail, level='ERROR')

        elif (rep['paired_ended'] == False or lib['paired_ended'] == False) and term_name in paired_end_assays:
            detail = 'paired ended required for {} either {} or {} is not pairend'.format(term_name, rep['uuid'], lib['accession'])
            yield AuditFailure('paired end required for assay', detail, level='ERROR')

        elif rep['paired_ended'] != lib['paired_ended'] and lib['paired_ended'] == False:
            detail = 'paired ended mismatch between {} - {}'.format(rep['uuid'], lib['accession'])
            yield AuditFailure('paired end mismatch', detail, level='ERROR')
