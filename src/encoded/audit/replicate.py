from snovault import (
    AuditFailure,
    audit_checker,
)


@audit_checker('replicate', frame=['experiment'])
def audit_status_replicate(value, system):
    '''
    As the experiment-replicate relationship is reverse calculated, the status checker for item
    is not sufficient to catch all cases of status mismatch between replicates and experiments.
    * in-progress replicate can't have experiment in [released, deleted, revoked]
    * released or revoked replicate must be in [released or revoked]
    * if experiment is deleted, replicate must be deleted
    '''

    rep_status = value['status']
    exp_status = value['experiment']['status']

    if ((rep_status in ['in progress'] and exp_status in ['released',
                                                          'revoked']) or
        (rep_status in ['released', 'revoked'] and
            exp_status not in ['released', 'revoked']) or
            (exp_status in ['deleted'] and rep_status not in ['deleted'])):
        #  If any of the three cases exist, there is an error
        detail = '{} replicate {} is in {} experiment'.format(
            rep_status,
            value['@id'],
            exp_status
        )
        yield AuditFailure('mismatched status', detail, level='INTERNAL_ACTION')
    return


# check that chip-seq experiments have antibody target matching the GM insert
# target of the biosample in the replicate (it could match on target name level
# or tags level
@audit_checker(
    'Replicate',
    frame=[
        'experiment',
        'experiment.target',
        'library',
        'library.biosample',
        'library.biosample.applied_modifications',
        'antibody',
        'antibody.targets'])
def audit_inconsistent_modifications_tag(value, system):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return
    if 'target' not in value['experiment']:
        return
    if 'assay_term_id' not in value['experiment'] or \
       value['experiment']['assay_term_id'] != 'OBI:0000716':
        return  # not ChIP-seq
    exp_target = value['experiment']['target']
    if 'library' in value and 'biosample' in value['library']:
        matching_flag = False
        tags_names = get_biosample_modifications_tags(value)
        if len(tags_names) > 0:
            antibody_targets = get_ab_targets(value)
            for ab_target in antibody_targets:
                if 'recombinant protein' in ab_target['investigated_as'] or \
                   'tag' in ab_target['investigated_as']:
                    if ab_target['label'] in tags_names:
                        matching_flag = True
                        break
                if ab_target['name'] == exp_target['name']:
                    matching_flag = True
                    break
            if len(antibody_targets) > 0 and not matching_flag:
                detail = 'Replicate {}-{} in experiment {} '.format(
                    value['biological_replicate_number'],
                    value['technical_replicate_number'],
                    value['experiment']['@id']) + \
                    'specifies antibody {} that is inconsistent '.format(
                        value['antibody']['@id']) + \
                    'with biosample {} modification tags {}.'.format(
                    value['library']['biosample']['@id'],
                    tags_names)
                yield AuditFailure('inconsistent modification tag', detail, level='INTERNAL_ACTION')
    return


def get_ab_targets(replicate):
    uuids_set = set()
    targtes_to_return = []
    if 'antibody' in replicate and \
       replicate['antibody']['status'] not in ['deleted', 'replaced', 'revoked']:
        ab_targets = replicate['antibody']['targets']
        for t in ab_targets:
            if t['uuid'] not in uuids_set and t['status'] not in ['deleted', 'replaced', 'revoked']:
                uuids_set.add(t['uuid'])
                targtes_to_return.append(t)
    return targtes_to_return


def get_biosample_modifications_tags(replicate):
    tags_names = set()
    if 'library' in replicate and 'biosample' in replicate['library'] and \
       replicate['library']['status'] not in ['deleted', 'replaced', 'revoked']:
        biosample = replicate['library']['biosample']
        if biosample['status'] not in ['deleted', 'replaced', 'revoked']:
            if biosample.get('applied_modifications'):
                for modification in biosample.get('applied_modifications'):
                    if modification.get('status') not in ['deleted', 'replaced', 'revoked'] and \
                       modification.get('purpose') == 'tagging' and \
                       modification.get('introduced_tags'):
                        for tag in modification.get('introduced_tags'):
                            tags_names.add(tag.get('name'))
    return tags_names
