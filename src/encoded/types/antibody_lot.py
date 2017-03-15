from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    SharedItem,
    paths_filtered_by_status,
)

from .ab_lot_status_data import (
    ab_states,
    ab_state_details
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
    audit_inherit = [
        'source',
        'host_organism',
        'targets',
        'targets.organism',
        'characterizations',
        'characterizations.documents',
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
    "description": "Review outcome of an antibody lot in each characterized cell type submitted for review.",
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
                    
                    "characterized to standards",
                    "characterized to standards with exemption",
                    "partially characterized",
                    "awaiting characterization",
                    "not characterized to standards",
                    "not pursued"
                ]
            }
        }
    },
})
def lot_reviews(characterizations, targets, request):
    
    characterizations = paths_filtered_by_status(request, characterizations)
    
    # Review the targets of the lot
    target_organisms = dict()
    tmp = list()
    is_control = False
    is_histone_mod = False
    
    for t in targets:
        target = request.embed(t, '@@object')
        if 'control' in target['investigated_as']:
            is_control = True
        if 'histone modification' in target['investigated_as']:
            is_histone_mod = True

        organism = target['organism']
        tmp.append(organism)
        target_organisms[organism] = target['@id']
    target_organisms['all'] = tmp

    # I would move base_review here
    #    base_review = {
    #    'biosample_term_name': 'any cell type and tissues',
    #    'biosample_term_id': 'NTR:99999999',
    #    'organisms': sorted(target_organisms['all']),
    #    'targets': sorted(review_targets),
    #    'status': 'awaiting characterization',
    #    'detail': 'Awaiting compliant primary and secondary characterizations.'
    #}
    
    # If there are no characterizations, then default to awaiting characterization.
    if not characterizations:
        return [{ # I would use base review here
            'biosample_term_name': 'any cell type or tissues',
            'biosample_term_id': 'NTR:99999999',
            'organisms': sorted(target_organisms['all']),
            'targets': sorted(targets),  # Copy to prevent modification of original data
            'status': 'characterized to standards with exemption' if is_control else 'awaiting characterization',
            'detail': 'IgG does not require further characterization.' if is_control else 'No characterizations submitted for this antibody lot yet.'
        }]

    review_targets = set()
    char_organisms = dict()
    primary_chars = list()
    secondary_chars = list()
    secondary_status = None

    # Since characterizations can only take one target (not an array) and primary characterizations
    # for histone modifications may be done in multiple species, we really need to check lane.organism
    # against the antibody.targets.organism list to determine eligibility of use in that organism.
    # Cricket is not sure that the above statement is true about histones.

    for characterization_path in characterizations:
        characterization = request.embed(characterization_path, '@@object')
        target = request.embed(characterization['target'], '@@object')
        organism = request.embed(target['organism'], '@@object')
        review_targets.add(target['@id'])
        char_organisms[characterization['@id']] = organism['@id']
        
        # Split into primary and secondary to treat separately
        if 'primary_characterization_method' in characterization:
            primary_chars.append(characterization)
        else:
            secondary_chars.append(characterization)

    # The default if no characterizations have been submitted
    # This could be defined above
    base_review = {
        'biosample_term_name': 'any cell type and tissues',
        'biosample_term_id': 'NTR:99999999',
        'organisms': sorted(target_organisms['all']),
        'targets': sorted(review_targets),
        'status': 'awaiting characterization',
        'detail': 'Awaiting compliant primary and secondary characterizations.'
    }
    
    # These rankings need some explaination like why is not pursused above compliant
    status_ranking = {
        'characterized to standards': 15,
        'characterized to standards with exemption': 14,
        'partially characterized': 13,
        'awaiting characterization': 12,
        'not characterized to standards': 11,
        'not pursued': 10,
        'compliant': 9,
        'exempt from standards': 8,
        'not compliant': 7,
        'pending dcc review': 6,
        'in progress': 5,
        'not reviewed': 4,
        'not submitted for review by lab': 3,
        'deleted': 2
    }

    # This no longer needs to be a procedure of its own, it is only 2 lines
    # Determine the consensus secondary characterization statu
    if secondary_chars:
        secondary_status = get_secondary_status(secondary_chars, status_ranking)
        # secondary_statuses = [item['status'] for item in secondary_chars]
        # secondary_statuses.sort(key=lambda x: status_ranking[x], reverse=True)
        # secondary_status = secondary_statuses[0]
        
    # Build the lot reviews for each biosample given the simple secondary status
    lot_reviews = build_lot_reviews(primary_chars,
                                    secondary_status,
                                    status_ranking,
                                    base_review,
                                    review_targets,
                                    is_histone_mod,
                                    char_organisms)

    return lot_reviews


def get_secondary_status(secondary_chars, status_ranking):
    # Determine the consensus secondary characterization status based on
    # all those submitted if more than one
    secondary_statuses = [item['status'] for item in secondary_chars]

    # Get the highest ranking status in the set
    secondary_statuses.sort(key=lambda x: status_ranking[x], reverse=True)

    return secondary_statuses[0]


def build_lot_reviews(primary_chars,
                      secondary_status,
                      status_ranking,
                      base_review,
                      review_targets,
                      is_histone_mod,
                      char_organisms):

    if not primary_chars:
        base_review['status'] = ab_states[(None, secondary_status)]
        base_review['detail'] = ab_state_details[(None, secondary_status)]
        return [base_review]
    else:
        char_reviews = {}
        lane_organism = None
        key = None
        for primary in primary_chars:
            if 'characterization_reviews' not in primary:
                lane_organism = char_organisms[primary['@id']]
                base_review['status'] = ab_states[(primary['status'], secondary_status)]
                base_review['detail'] = ab_state_details[(primary['status'], secondary_status)]

                key = (
                    base_review['biosample_term_name'],
                    base_review['biosample_term_id'],   # Why is both the id and the name in the key  
                    lane_organism,
                    primary['target']
                )
                if key not in char_reviews:
                    char_reviews[key] = base_review
                    continue

                rank = status_ranking[base_review.get('status')]
                if rank > status_ranking[char_reviews[key].get('status')]:
                    char_reviews[key] = base_review
            else:
                # This primary characterization has characterization_reviews
                for lane_review in primary.get('characterization_reviews', []):
                    # Get the organism information from the lane, not from the target since
                    # there are lanes. Build a new base_review using the lane information
                    base_review = dict()
                    lane_organism = lane_review['organism']

                    base_review['biosample_term_name'] = 'any cell type and tissues' \
                        if is_histone_mod else lane_review['biosample_term_name']
                    base_review['biosample_term_id'] = 'NTR:99999999' \
                        if is_histone_mod else lane_review['biosample_term_id']
                    base_review['organisms'] = [lane_organism]
                    base_review['targets'] = sorted(review_targets) \
                        if is_histone_mod else [primary['target']]
                    base_review['status'] = ab_states[(lane_review['lane_status'], secondary_status)] \
                        if primary['status'] in ['compliant',
                                                 'not compliant',
                                                 'pending dcc review',
                                                 'exempt from standards'] else \
                        ab_states[primary['status'], secondary_status]
                    base_review['detail'] = ab_state_details[(lane_review['lane_status'], secondary_status)] \
                        if primary['status'] in ['compliant',
                                                 'not compliant',
                                                 'pending dcc review',
                                                 'exempt from standards'] else \
                        ab_state_details[primary['status'], secondary_status]

                    # Need to use status ranking to determine whether or not to
                    # add this review to the list or not if another already exists.
                    key = (
                        base_review['biosample_term_name'],
                        base_review['biosample_term_id'],
                        lane_organism,
                        primary['target']
                    )
                    if key not in char_reviews:
                        char_reviews[key] = base_review
                        continue

                    rank = status_ranking[base_review.get('status')]
                    if rank > status_ranking[char_reviews[key].get('status')]:
                        char_reviews[key] = base_review

        return list(char_reviews.values())
