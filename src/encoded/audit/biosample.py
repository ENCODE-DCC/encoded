from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


# flag biosamples that contain GM that is different from the GM in donor. It could be legitimate case, but we would like to see it.
# flag biosamples that have a GM that was specified in donor detecting redundant GM
def audit_biosample_modifications(value, system):
    
    if value['biosample_ontology']['classification'] == 'whole organisms':
        model_modifications_present = True
        model_modifications_ids = set()
        modifications_ids = set()
        if 'model_organism_donor_modifications' in value:
            for model_modification in value['model_organism_donor_modifications']:
                model_modifications_ids.add(model_modification)
        else:
            model_modifications_present = False
        if 'genetic_modifications' in value:
            for modification in value['genetic_modifications']:
                modifications_ids.add(modification)

        modification_difference = modifications_ids - model_modifications_ids

        if modification_difference and model_modifications_present:
            mod_diff_links = [audit_link(path_to_text(m), m) for m in modification_difference]
            model_mod_links = [audit_link(path_to_text(n), n) for n in model_modifications_ids]
            detail = ('Biosample {} contains '
                ' genetic modificatons {} that are not present'
                ' in the list of genetic modifications {} of the corresponding strain.'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    ', '.join(mod_diff_links),
                    ', '.join(model_mod_links)
                )
            )
            yield AuditFailure('mismatched genetic modifications', detail,
                               level='INTERNAL_ACTION')
        modification_duplicates = model_modifications_ids & modifications_ids
        mod_dup_links = [audit_link(path_to_text(d), d) for d in modification_duplicates]
        model_mod_links = [audit_link(path_to_text(n), n) for n in model_modifications_ids]
        if modification_duplicates:
            detail = ('Biosample {} contains '
                'genetic modifications {} that '
                'are duplicates of genetic modifications {} '
                'of the corresponding strain.'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    ', '.join(mod_dup_links),
                    ', '.join(model_mod_links)
                )
            )
            yield AuditFailure('duplicated genetic modifications', detail,
                               level='INTERNAL_ACTION')
    return

# def audit_biosample_gtex_children(value, system):
# https://encodedcc.atlassian.net/browse/ENCD-3538


def audit_biosample_CRISPR_modifications(value, system):
# flag biosamples with multiple CRISPR/characterization GM; may be legitimate but we want be notified
# https://encodedcc.atlassian.net/browse/ENCD-5203
    if 'applied_modifications' in value:
        if len(value['applied_modifications']) > 1:
            CRISPRchar = 0
            GM_ids = set()
            for GM in value['applied_modifications']:
                if GM['method'] == 'CRISPR' and GM['purpose'] == 'characterization':
                    CRISPRchar += 1
                    GM_ids.add(GM['@id'])
            GM_ids_links = [audit_link(path_to_text(m), m) for m in GM_ids]
            if CRISPRchar >1:
                detail = ('Biosample {} has multiple CRISPR characterization '
                          ' genetic modifications {}'.format(
                           audit_link(path_to_text(value['@id']), value['@id']),
                           ', '.join(GM_ids_links)
                          )
                )
                yield AuditFailure('multiple CRISPR characterization genetic modifications', detail,
                                   level='INTERNAL_ACTION')

def audit_biosample_culture_date(value, system):
    '''
    Culture date is allowed only in cultured biosamples.

    A culture_harvest_date should not precede
    a culture_start_date.
    This should move to the schema.
    '''

    restricted_type = ["single cell", "primary cell", "cell line",
                       "in vitro differentiated cells", "organoid"]
    if (('culture_harvest_date' in value or 'culture_start_date' in value)
        and value['biosample_ontology']['classification'] not in restricted_type):
        detail = ('Biosample {} is classified as {}, '
            'which is not from culture, '
            'thus shouldn\'t have culture dates specified.'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                value['biosample_ontology']['classification']
            )
        )
        yield AuditFailure('biosample not from culture', detail,
                           level='ERROR')

    if value['status'] in ['deleted']:
        return

    if ('culture_start_date' not in value) or ('culture_harvest_date' not in value):
        return

    if value['culture_harvest_date'] <= value['culture_start_date']:
        detail = ('Biosample {} has a culture_harvest_date {}'
            'which precedes the culture_start_date {}'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                value['culture_harvest_date'],
                value['culture_start_date']
            )
        )
        yield AuditFailure('invalid dates', detail, level='ERROR')


def audit_biosample_donor(value, system):
    '''
    A biosample should have a donor.
    The organism of donor and biosample should match.
    '''
    if value['status'] in ['deleted']:
        return

    if 'donor' not in value:
        detail = ('Biosample {} is not associated with any donor.'.format(
            audit_link(value['accession'], value['@id'])
            )
        )
        if 'award' in value and 'rfa' in value['award'] and \
           value['award']['rfa'] == 'GGR':
            yield AuditFailure('missing donor', detail, level='INTERNAL_ACTION')
            return
        else:
            yield AuditFailure('missing donor', detail, level='ERROR')
            return

    donor = value['donor']
    if value.get('organism') != donor.get('organism'):
        detail = ('Biosample {} is organism {}, yet its donor {} is organism {}.'
            ' Biosamples require a donor of the same species'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                path_to_text(value.get('organism')),
                audit_link(path_to_text(donor['@id']), donor['@id']),
                path_to_text(donor.get('organism'))
            )
        )
        yield AuditFailure('inconsistent organism', detail, level='ERROR')


def audit_biosample_part_of_consistency(value, system):
    if 'part_of' not in value:
        return
    else:
        part_of_biosample = value['part_of']
        term_id = value['biosample_ontology']['term_id']
        term_name = value['biosample_ontology']['term_name']
        part_of_term_id = part_of_biosample['biosample_ontology']['term_id']
        part_of_term_name = part_of_biosample['biosample_ontology']['term_name']

        if term_id == part_of_term_id or part_of_term_id == 'UBERON:0000468':
            return

        ontology = system['registry']['ontology']
        if (term_id in ontology) and (part_of_term_id in ontology):
            if is_part_of(term_id, part_of_term_id, ontology) is True:
                return

        detail = ('Biosample {} with biosample term {} '
            'was separated from biosample {} '
            'with biosample term {}. The {} '
            'ontology does not note that part_of relationship.'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                term_name,
                audit_link(path_to_text(part_of_biosample['@id']), part_of_biosample['@id']),
                part_of_term_name,
                term_id
            )
        )
        yield AuditFailure('inconsistent BiosampleType term', detail,
                           level='INTERNAL_ACTION')
        return


def audit_biosample_phase(value, system):
    restricted_type = ["single cell", "primary cell", "cell line",
                       "in vitro differentiated cells"]
    if ('phase' in value
        and value['biosample_ontology']['classification'] not in restricted_type):
        detail = ('Biosample {} is classified as {}, '
            'which shouldn\'t have a defined cell cycle phase {}.'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                value['biosample_ontology']['classification'],
                value['phase']
            )
        )
        yield AuditFailure('biosample cannot have defined cell cycle phase',
                           detail, level='ERROR')


def audit_biosample_pmi(value, system):
    if (('PMI' in value or 'PMI_units' in value)
        and value['biosample_ontology']['classification'] not in ['tissue']):
        detail = ('PMI is for tissue sample only. '
            'Biosample {} is classified as {}.'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                value['biosample_ontology']['classification'],
            )
        )
        yield AuditFailure('non-tissue sample has PMI',
                           detail, level='ERROR')


def audit_biosample_cell_isolation_method(value, system):
    excluded_type = ["whole organisms", "tissue", "organoid"]
    if ('cell_isolation_method' in value
        and value['biosample_ontology']['classification'] in excluded_type):
        detail = ('Biosample {} is classified as {}, '
            'which is not cell and shouldn\'t have cell_isolation_method {}.'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                value['biosample_ontology']['classification'],
                value['cell_isolation_method']
            )
        )
        yield AuditFailure('non-cell sample has cell_isolation_method',
                           detail, level='ERROR')


def audit_biosample_depleted_in_term_name(value, system):
    restricted_type = ["whole organisms", "tissue"]
    if ('depleted_in_term_name' in value
        and value['biosample_ontology']['classification'] not in restricted_type):
        detail = ('Biosample {} is classified as {}, '
            'which cannot have {} depleted.'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                value['biosample_ontology']['classification'],
                value['depleted_in_term_name']
            )
        )
        yield AuditFailure('non-tissue sample has parts depleted',
                           detail, level='ERROR')


# utility functions

def is_part_of(term_id, part_of_term_id, ontology, parent_term_id=None):
    """
    Given the term_ids for a child and parent biosample pair as obtained from the
    portal, check that the part_of relationship is reflected in the ontology as
    well. While the portal model insinuates a direct parent-child relation, in
    the ontology the relationship may traverse several levels of inheritance.
    As such, this function traverses up the ontology tree until it has found the
    ancestor node with the matching term_id.

    Parameters
    ----------
    term_id : str
        The biosample_term_id of the child biosample
    part_of_term_id : str
        The biosample_term_id of the biosample specified by the child biosample's
        "part_of" property, i.e. the biosample_term_id of the parent biosample
    ontology : dict
        The ontology generated by ontology.py, from system['registry']['ontology']
    parent_term_id : str, optional
        The term id of the previous node in the traversal. This argument is passed
        for recursive is_part_of calls to ensure that the search does not bounce
        between two ontology terms pointing to each other.

    Returns
    -------
    bool
        Returns True if the ontology term of any ancestor of the term_id in the
        ontology, or the term_id itself, matches part_of_term_id. Otherwise,
        returns False after the search over all ancestor nodes has been exhausted.

    Examples
    --------
    >>> is_part_of('CL:0000598', 'UBERON:0002037', ontology)
    False

    >>> is_part_of('CL:0000121', 'UBERON:0002037', ontology)
    True
    """
    if 'part_of' not in ontology[term_id] or ontology[term_id]['part_of'] == []:
        return False
    if part_of_term_id in ontology[term_id]['part_of']:
        return True
    else:
        parents = []
        for x in ontology[term_id]['part_of']:
            if not parent_term_id == x:
                parents.append(
                    is_part_of(x, part_of_term_id, ontology, parent_term_id=term_id)
                )
        return any(parents)


def audit_biosample_post_differentiation_time(value, system):
    biosample_type = value['biosample_ontology']['classification']
    if biosample_type not in ['organoid', 'in vitro differentiated cells']:
        if value.get('post_differentiation_time') or value.get('post_differentiation_time_units'):
            detail = ('Biosample {} of type {} has post_differentiation_time and/or '
                'post_differentiation_time_units specified, properties which are '
                'restricted to biosamples of type organoid or in vitro differentiated cells.'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    biosample_type
                )
            )
            yield AuditFailure(
                'invalid post_differentiation_time details',
                detail,
                level='WARNING'
            )


function_dispatcher = {
    'audit_modification': audit_biosample_modifications,
    'audit_CRISPR_modification': audit_biosample_CRISPR_modifications,
    'audit_culture_date': audit_biosample_culture_date,
    'audit_donor': audit_biosample_donor,
    'audit_part_of': audit_biosample_part_of_consistency,
    'audit_phase': audit_biosample_phase,
    'audit_pmi': audit_biosample_pmi,
    'audit_cell_isolation_method': audit_biosample_cell_isolation_method,
    'audit_depleted_in_term_name': audit_biosample_depleted_in_term_name,
    'audit_post_differentiation_time': audit_biosample_post_differentiation_time
}

@audit_checker('Biosample',
               frame=['award',
                      'biosample_ontology',
                      'donor',
                      'part_of',
                      'part_of.biosample_ontology',
                      'applied_modifications'])
def audit_biosample(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure
