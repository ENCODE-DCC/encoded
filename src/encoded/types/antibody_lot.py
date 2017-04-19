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
                    "awaiting characterization",
                    "characterized to standards",
                    "partially characterized",
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
    target_organisms = {}

    is_control = False
    is_histone_mod = False
    for t in targets:
        target = request.embed(t, '@@object')
        if 'control' in target['investigated_as']:
            is_control = True
        if 'histone modification' in target['investigated_as']:
            is_histone_mod = True

        organism = target['organism']
        target_organisms = { 'all' : [] }
        target_organisms['all'].append(organism)
        target_organisms[organism] = target['@id']

    # The default base characterization if no characterizations have been submitted
    base_review = {
        'biosample_term_name': 'any cell type or tissue',
        'biosample_term_id': 'NTR:99999999',
        'organisms': sorted(target_organisms['all']),
        'targets': sorted(targets),
        'status': 'characterized to standards with exemption'
        if is_control else ab_states[(None, None)],
        'detail': 'IgG does not require further characterization.'
        if is_control else ab_state_details[(None, None)]
    }

    if not characterizations:
        # If there are no characterizations, then default to awaiting characterization.
        return [base_review]

    review_targets = set()
    char_organisms = {}
    primary_chars = []
    secondary_chars = []
    secondary_status = None

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

    # Since characterizations can only take one target (not an array) and primary characterizations
    # for histone modifications may be done in multiple species, we really need to check lane.organism
    # against the antibody.targets.organism list to determine eligibility of use in that organism.

    for characterization_path in characterizations:
        characterization = request.embed(characterization_path, '@@object')
        target = request.embed(characterization['target'], '@@object')

        # instead of adding to the target_organism list with whatever they put in the
        # characterization we need to instead compare the lane organism to see if it's in the
        # target_organism list. If not, we'll need to indicate that they characterized an
        # organism not in the antibody_lot.targets list so it'll have to be reviewed and
        # added if legitimate.
        review_targets.add(target['@id'])
        char_organisms[characterization['@id']] = target['organism']
        # Split into primary and secondary to treat separately
        if 'primary_characterization_method' in characterization:
            primary_chars.append(characterization)

        else:
            secondary_chars.append(characterization)

    # Go through the secondary characterizations first
    if secondary_chars:
        # Determine the consensus secondary characterization status based on
        # all those submitted if more than one
        secondary_statuses = [item['status'] for item in secondary_chars]

        # Get the highest ranking status in the set
        secondary_statuses.sort(key=lambda x: status_ranking[x], reverse=True)
        secondary_status = secondary_statuses[0]

    # If there are no primaries, return the lot review with the secondary status
    if not primary_chars:
        # The default if no primary characterizations have been submitted
        base_review['status'] = ab_states[(None, secondary_status)]
        base_review['detail'] = ab_state_details[(None, secondary_status)]
        if base_review['status'] == 'not pursued':
            base_review['biosample_term_name'] = 'at least one cell type or tissue'
            base_review['biosample_term_id'] = 'NTR:00000000'
        return [base_review]

    # Done with easy cases, the remaining require reviews.
    # Check the primaries and update their status accordingly
    lot_reviews = build_lot_reviews(primary_chars,
                                    secondary_status,
                                    status_ranking,
                                    review_targets,
                                    is_histone_mod,
                                    char_organisms)

    return lot_reviews


def build_lot_reviews(primary_chars,
                      secondary_status,
                      status_ranking,
                      review_targets,
                      is_histone_mod,
                      char_organisms):

    # We have primary characterizatons
    char_reviews = {}
    lane_organism = None
    key = None
    for primary in primary_chars:
        # The default base review to update as needed
        base_review = {
            'biosample_term_name': 'at least one cell type or tissue',
            'biosample_term_id': 'NTR:00000000',
            'organisms': [char_organisms[primary['@id']]],
            'targets': [primary['target']]
        }
        if not primary.get('characterization_reviews', []):
            base_review['status'] = ab_states[(primary['status'], secondary_status)]
            base_review['detail'] = ab_state_details[(primary['status'], secondary_status)]
            if base_review['status'] == 'partially characterized':
                base_review['biosample_term_name'] = 'any cell type or tissue'
                base_review['biosample_term_id'] = 'NTR:99999999'

            # Don't need to rank and unique the primaries with unknown cell types, we can't
            # know if they're distinct or not anyway without characterization reviews.
            char_reviews[(base_review['biosample_term_name'],
                          base_review['biosample_term_id'],
                          char_organisms[primary['@id']],
                          primary['target'])] = base_review

        else:
            # This primary characterization has characterization_reviews
            for lane_review in primary.get('characterization_reviews', []):
                # Get the organism information from the lane, not from the target since
                # there are lanes. Build a new base_review using the lane information
                base_review = {}
                lane_organism = lane_review['organism']

                base_review['biosample_term_name'] = 'any cell type or tissue' \
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
