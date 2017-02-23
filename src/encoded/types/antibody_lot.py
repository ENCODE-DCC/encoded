from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    SharedItem,
    paths_filtered_by_status,
)


@collection(
    name='antibodies',
    unique_key='accession',
    properties={
        'title': 'Antibodies Registry',
        'description': 'Listing of ENCODE antibodies',
    })
class AntibodyLot(SharedItem):
    item_type = 'antibody_lot'
    schema = load_schema('encoded:schemas/antibody_lot.json')
    name_key = 'accession'
    rev = {
        'characterizations': ('AntibodyCharacterization', 'characterizes'),
    }
    embedded = [
        'source',
        'host_organism',
        'targets',
        'targets.organism',
        'characterizations.award',
        'characterizations.documents',
        'characterizations.lab',
        'characterizations.submitted_by',
        'characterizations.target.organism',
        'lot_reviews.targets',
        'lot_reviews.targets.organism',
        'lot_reviews.organisms'
    ]

    def unique_keys(self, properties):
        keys = super(AntibodyLot, self).unique_keys(properties)
        source = properties['source']
        product_id = properties['product_id']
        lot_ids = [properties['lot_id']] + properties.get('lot_id_alias', [])
        values = (u'{}/{}/{}'.format(source, product_id, lot_id) for lot_id in lot_ids)
        keys.setdefault('antibody_lot:source_product_lot', []).extend(values)
        return keys

    @calculated_property(schema={
        "title": "Title",
        "type": "string",
    })
    def title(self, accession):
        return accession

    @calculated_property(schema={
        "title": "Characterizations",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "AntibodyCharacterization.characterizes",
        },
    })
    def characterizations(self, request, characterizations):
        return paths_filtered_by_status(request, characterizations)


@calculated_property(context=AntibodyLot, schema={
    "title": "Antibody lot reviews",
    "description":
        "Review outcome of an antibody lot in each characterized cell type submitted for review.",
    "type": "array",
    "items": {
        "title": "Antibody lot review",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "biosample_term_id": {
                "title": "Ontology ID",
                "description": "Ontology identifier describing biosample.",
                "comment": "NTR is a new term request identifier provided by the DCC.",
                "type": "string",
                "pattern": "^(UBERON|EFO|CL|NTR|FBbt|WBbt):[0-9]{2,8}$"
            },
            "biosample_term_name": {
                "title": "Ontology term",
                "description": "Ontology term describing biosample.",
                "type":  "string"
            },
            "organisms": {
                "title": "Organism",
                "type": "array",
                "items": {
                    "comment": "See organism.json for available identifiers.",
                    "type": "string",
                    "linkTo": "Organism"
                }
            },
            "targets": {
                "title": "Targets",
                "type": "array",
                "items": {
                    "description":
                        "The name of the gene whose expression or product is the intended goal of "
                        "the antibody.",
                    "comment": "See target.json for available identifiers.",
                    "type": "string",
                    "linkTo": "Target"
                }
            },
            "status": {
                "title": "Status",
                "description": "The current state of the antibody characterizations.",
                "comment":
                    "Do not submit, the value is assigned by server. "
                    "The status is updated by the DCC.",
                "type": "string",
                "default": "awaiting characterization",
                "enum": [
                    "awaiting characterization",
                    "pending dcc review",
                    "characterized to standards",
                    "characterized to standards with exemption",
                    "not characterized to standards",
                    "not pursued"
                ]
            }
        }
    },
})
def lot_reviews(characterizations, targets, request):
    characterizations = paths_filtered_by_status(request, characterizations)
    target_organisms = dict()
    tmp = list()

    is_control = False
    for t in targets:
        target = request.embed(t, '@@object')
        if 'control' in target['investigated_as']:
            is_control = True

        organism = target['organism']
        tmp.append(organism)
        target_organisms[organism] = target['@id']
    target_organisms['all'] = tmp

    if not characterizations:
        # If there are no characterizations, then default to awaiting characterization.
        return [{
            'biosample_term_name': 'any cell type or tissues',
            'biosample_term_id': 'NTR:99999999',
            'organisms': sorted(target_organisms['all']),
            'targets': sorted(targets),  # Copy to prevent modification of original data
            'status': 'characterized to standards with exemption' if is_control else 'awaiting characterization',
            'detail': 'IgG does not require further characterization.' if is_control else 'No characterizations submitted for this antibody lot yet.'
        }]

    histone_mod_target = False
    review_targets = set()
    lab_not_reviewed_chars = 0
    total_characterizations = 0
    not_reviewed_chars = 0
    in_progress_chars = 0
    primary_chars = []
    secondary_chars = []

    # Since characterizations can only take one target (not an array), primary characterizations for 
    # histone modifications may be done in multiple species, so we really need to check lane.organism
    # against the antibody.targets.organism list to determine eligibility of use in that organism.

    for characterization_path in characterizations:
        characterization = request.embed(characterization_path, '@@object')
        target = request.embed(characterization['target'], '@@object')
        organism = target['organism']

        review_targets.add(target['@id'])

        # All characterization targets should be a histone_mod_target or all not.
        # (Checked by an audit.)
        if 'histone modification' in target['investigated_as']:
            histone_mod_target = True

        # instead of adding to the target_organism list with whatever they put in the characterization
        # we need to instead compare the lane organism to see if it's in the target_organism list. 
        # If not, will need to indicate that they characterized an organism not in the antibody_lot.targets
        # list so it'll have to be reviewed and added if legitimate.
        # organisms.add(organism)

        if characterization['status'] == 'not submitted for review by lab':
            lab_not_reviewed_chars += 1
            total_characterizations += 1
        elif characterization['status'] == 'not reviewed':
            not_reviewed_chars += 1
            total_characterizations += 1
        elif characterization['status'] == 'in progress':
            in_progress_chars += 1
            total_characterizations += 1
        else:
            total_characterizations += 1

        # Split into primary and secondary to treat separately
        if 'primary_characterization_method' in characterization:
            primary_chars.append(characterization)
        else:
            secondary_chars.append(characterization)

    base_review = {
        'biosample_term_name': 'not specified',
        'biosample_term_id': 'NTR:00000000',
        'organisms': sorted(target_organisms['all']),
        'targets': sorted(review_targets),
        'status': 'awaiting characterization',
        'detail': None
    }

    # Deal with the easy cases where both characterizations have the same
    # statuses not from DCC reviews
    if lab_not_reviewed_chars == total_characterizations and total_characterizations > 0:
        base_review['status'] = 'not pursued'
        return [base_review]

    if not_reviewed_chars == total_characterizations and total_characterizations > 0:
        base_review['status'] = 'not characterized to standards'
        base_review['detail'] = 'Characterizations not reviewed.'
        return [base_review]

    if in_progress_chars == total_characterizations and total_characterizations > 0:
        base_review['detail'] = 'Characterizations in progress.'
        return [base_review]

    if (lab_not_reviewed_chars + not_reviewed_chars) == total_characterizations and \
            total_characterizations > 0:
        base_review['status'] = 'not pursued'
        return [base_review]

    if histone_mod_target:
        if len(primary_chars) > 0 and len(secondary_chars) == 0:
            # There are only primary characterization(s)
            base_review['detail'] = 'Awaiting submission of secondary characterization(s).'
            return [base_review]

    if len(primary_chars) == 0 and len(secondary_chars) > 0:
        # There are only secondary characterization(s)
        base_review['detail'] = 'Awaiting submission of primary characterization(s).'
        return [base_review]

    # Done with easy cases, the remaining require reviews.
    # Go through the secondary characterizations first
    compliant_secondary = False
    not_compliant_secondary = False
    pending_secondary = False
    exempted_secondary = False
    in_progress_secondary = 0
    not_reviewed_secondary = 0

    for secondary in secondary_chars:
        if secondary['status'] == 'compliant':
            compliant_secondary = True
            break
        elif secondary['status'] == 'exempt from standards':
            exempted_secondary = True
            break
        else:
            if not (compliant_secondary or exempted_secondary):
                if secondary['status'] == 'pending dcc review':
                    pending_secondary = True
                if secondary['status'] == 'not compliant':
                    not_compliant_secondary = True
                if secondary['status'] == 'in progress':
                    in_progress_secondary += 1
                if secondary['status'] == 'not reviwed':
                    not_reviewed_secondary += 1

    # Now check the primaries and update their status accordingly
    char_reviews = {}

    for primary in primary_chars:
        if primary['status'] in ['not reviewed', 'not submitted for review by lab']:
            continue

        if primary['status'] == 'in progress':
            base_review['detail'] = 'Primary characterization(s) in progress.'

        for lane_review in primary.get('characterization_reviews', []):
            # Get the organism information from the lane, not from the target since there are lanes
            lane_organism = lane_review['organism']

            new_review = {
                'biosample_term_name': lane_review['biosample_term_name'],
                'biosample_term_id': lane_review['biosample_term_id'],
                'organisms': [lane_organism],
                'targets':
                    sorted(review_targets) if histone_mod_target
                    else [primary['target']],
                'status': 'awaiting characterization',
                'detail': None
            }

            if lane_review['lane_status'] == 'pending dcc review':
                new_review['status'] = 'pending dcc review'
                if compliant_secondary:
                    new_review['detail'] = 'Pending review of primary characterization.'
                if pending_secondary:
                    new_review['detail'] = 'Pending review of primary and secondary characterizations.'
                if not secondary_chars:
                    new_review['detail'] = 'Pending review of primary and awaiting submission of secondary characterization(s).'
            elif lane_review['lane_status'] == 'not compliant':
                if not_compliant_secondary or len(secondary_chars) == 0 or \
                        (not_reviewed_secondary == len(secondary_chars)):
                    new_review['status'] = 'not characterized to standards'
                    new_review['detail'] = 'Awaiting compliant primary and secondary characterizations.'
                else:
                    if histone_mod_target:
                        new_review['biosample_term_name'] = 'any cell type and tissues'
                        new_review['biosample_term_id'] = 'NTR:99999999'
                    new_review['detail'] = 'Awaiting a compliant primary characterization.'
            elif lane_review['lane_status'] == 'exempt from standards':
                if not histone_mod_target:
                    if compliant_secondary or exempted_secondary:
                        new_review['status'] = 'characterized to standards with exemption'
                        new_review['detail'] = 'Fully characterized.'
                    if not secondary_chars or (not_reviewed_secondary == len(secondary_chars)):
                        new_review['detail'] = 'Awaiting submission of secondary characterization(s).'
                    if in_progress_secondary == len(secondary_chars):
                        new_review['detail'] = 'Secondary characterization(s) in progress.'
                else:
                    # exempted_organisms.add(lane_organism)
                    new_review['biosample_term_name'] = 'any cell type and tissues'
                    new_review['biosample_term_id'] = 'NTR:99999999'
                    if lane_organism in target_organisms:
                        new_review['targets'] = [target_organisms[lane_organism]]
                        if compliant_secondary or exempted_secondary:
                            new_review['status'] = 'characterized to standards with exemption'
                            new_review['detail'] = 'Fully characterized.'
                    else:
                        new_review['detail'] = 'Characterized organism not in antibody target list.'

            elif lane_review['lane_status'] == 'compliant':
                if not histone_mod_target:
                    if compliant_secondary:
                        new_review['status'] = 'characterized to standards'
                        new_review['detail'] = 'Fully characterized.'
                    elif exempted_secondary:
                        new_review['status'] = 'characterized to standards with exemption'
                        new_review['detail'] = 'Fully characterized.'
                    else:
                        new_review['detail'] = 'Awaiting a compliant secondary characterization.'
                        pass
                    # Keep track of compliant organisms for histones and we
                    # will fill them in after going through all the lanes
                else:
                    new_review['biosample_term_name'] = 'any cell type and tissues'
                    new_review['biosample_term_id'] = 'NTR:99999999'
                    if lane_organism in target_organisms:
                        # characterized_organisms.add(lane_organism)
                        new_review['targets'] = [target_organisms[lane_organism]]
                        if compliant_secondary:
                            new_review['status'] = 'characterized to standards'
                            new_review['detail'] = 'Fully characterized.'
                        elif exempted_secondary:
                            new_review['status'] = 'characterized to standards with exemption'
                            new_review['detail'] = 'Fully characterized.'
                        else:
                            new_review['detail'] = 'Awaiting a compliant secondary characterization.'
                            pass
                    else:
                        new_review['detail'] = 'Characterized organism not in antibody target list.'

                if pending_secondary:
                    new_review['status'] = 'pending dcc review'
                    new_review['detail'] = 'Pending review of a secondary characterization.'
            else:
                # For all other cases, can keep the awaiting status
                pass

            key = (
                lane_review['biosample_term_name'],
                lane_review['biosample_term_id'],
                lane_review['organism'],
                primary['target'],
            )
            if key not in char_reviews:
                char_reviews[key] = new_review
                continue

            status_ranking = {
                'characterized to standards': 6,
                'characterized to standards with exemption': 5,
                'compliant': 4,
                'exempt from standards': 3,
                'pending dcc review': 2,
                'awaiting characterization': 1,
                'not compliant': 0,
                'not reviewed': 0,
                'not submitted for review by lab': 0,
                'deleted': 0,
                'not characterized to standards': 0
            }

            rank = status_ranking[new_review['status']]
            if rank > status_ranking[char_reviews[key]['status']]:
                # Check to see if existing status should be overridden
                char_reviews[key] = new_review

    if not char_reviews:
        return [base_review]

    return list(char_reviews.values())
