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

    review_targets = set()
    primary_chars = []
    secondary_chars = []
    at_least_one_active_primary = False

    # Since characterizations can only take one target (not an array) and primary characterizations
    # for histone modifications may be done in multiple species, we really need to check lane.organism
    # against the antibody.targets.organism list to determine eligibility of use in that organism.

    for characterization_path in characterizations:
        characterization = request.embed(characterization_path, '@@object')
        target = request.embed(characterization['target'], '@@object')
        organism = target['organism']

        # instead of adding to the target_organism list with whatever they put in the
        # characterization we need to instead compare the lane organism to see if it's in the
        # target_organism list. If not, we'll need to indicate that they characterized an
        # organism not in the antibody_lot.targets list so it'll have to be reviewed and
        # added if legitimate.
        review_targets.add(target['@id'])

        # Split into primary and secondary to treat separately
        if 'primary_characterization_method' in characterization:
            primary_chars.append(characterization)
            if 'characterization_reviews' in characterization:
                at_least_one_active_primary = True
        else:
            secondary_chars.append(characterization)

    # The default if no characterizations have been submitted
    base_review = {
        'biosample_term_name':
            'any cell type and tissues' if is_histone_mod
            else 'not specified',
        'biosample_term_id': 'NTR:99999999' if is_histone_mod else 'NTR:00000000',
        'organisms': sorted(target_organisms['all']),
        'targets': sorted(review_targets),
        'status': 'awaiting characterization',
        'detail': None
    }

    # Done with easy cases, the remaining require reviews.
    # Go through the secondary characterizations first

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
        'not characterized to standards': 0,
        'in progress': 0
    }

    secondary_status = get_secondary_status(secondary_chars, status_ranking) \
        if secondary_chars else None

    # Now check the primaries and update their status accordingly
    lot_reviews = build_lot_reviews(primary_chars,
                                    secondary_status,
                                    status_ranking,
                                    base_review,
                                    review_targets,
                                    is_histone_mod,
                                    at_least_one_active_primary,
                                    target_organisms)

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
                      active_primary,
                      target_organisms):

    if not primary_chars:
        if secondary_status in ['not reviewed', 'not submitted for review by lab']:
            base_review['status'] = 'not pursued'
        elif secondary_status in ['pending dcc review']:
            base_review['status'] = 'pending dcc review'
        elif secondary_status in ['in progress']:
            base_review['status'] = 'awaiting characterization'
        else:
            base_review['status'] = 'not characterized to standards'
        base_review['detail'] = 'Awaiting submission of primary characterization(s).'
        return [base_review]

    else:
        char_reviews = {}
        for primary in primary_chars:
            if not active_primary:
                if primary['status'] and secondary_status in ['not reviewed']:
                    base_review['status'] = 'not characterized to standards',
                if primary['status'] == 'not submitted for review by lab' and \
                        (secondary_status == 'not submitted for review by lab' or secondary_status is None):
                    base_review['status'] = 'not pursued'
                if secondary_status == 'pending dcc review':
                    base_review['status'] = 'pending dcc review'
                    base_review['detail'] = 'Awaiting submission of primary characterization(s).'
                if primary['status'] == 'in progress':
                    base_review['detail'] = 'Primary characterization(s) in progress.'
                if secondary_status == 'in progress':
                    base_review['detail'] = 'Secondary characterization(s) in progress.'
                return [base_review]
            elif 'characterization_reviews' in primary:
                for lane_review in primary.get('characterization_reviews', []):
                    # Get the organism information from the lane, not from the target since
                    # there are lanes
                    lane_organism = lane_review['organism']

                    new_review = {
                        'biosample_term_name':
                            'any cell type and tissues' if is_histone_mod
                            else lane_review['biosample_term_name'],
                        'biosample_term_id': 'NTR:99999999' if is_histone_mod
                            else lane_review['biosample_term_id'],
                        'organisms': [lane_organism],
                        'targets':
                            sorted(review_targets) if is_histone_mod
                            else [primary['target']],
                        'status': 'not submitted for review by lab' if primary['status'] ==
                            'not submitted for review by lab' else lane_review.get('lane_status'),
                        'detail': None
                    }

                    # Need to use status ranking to determine whether or not to
                    # add this review to the list or not if another already exists.
                    key = (
                        new_review['biosample_term_name'],
                        new_review['biosample_term_id'],
                        lane_review['organism'],
                        primary['target']
                    )
                    if key not in char_reviews:
                        char_reviews[key] = new_review
                        continue

                    rank = status_ranking[new_review.get('status')]
                    if rank > status_ranking[char_reviews[key].get('status')]:
                        char_reviews[key] = new_review
            else:
                # There is at mixture of active and inactive primaries, but there should be at least
                # one active primary with characterization reviews to populate the
                # antibody_lot.lot_reviews, so we can skip over those other inactive primaries.
                pass

        # Go through and calculate the appropriate statuses
        for key in char_reviews:
            if secondary_status is None:
                if char_reviews[key]['status'] in ['not reviewed', 'not submitted for review by lab']:
                    char_reviews[key]['status'] = 'not pursued'
                elif char_reviews[key]['status'] == 'pending dcc review':
                    char_reviews[key]['detail'] = 'One or more characterization(s) is pending review.'
                else:
                    char_reviews[key]['status'] = 'awaiting characterization'
                    char_reviews[key]['detail'] = 'Awaiting submission of secondary characterization(s).'
            elif secondary_status in ['not reviewed',
                                      'not compliant',
                                      'not submitted for review by lab',
                                      'in progress',
                                      'deleted']:
                char_reviews[key]['status'] = 'not characterized to standards'
                char_reviews[key]['detail'] = 'Awaiting a compliant secondary characterization.'
            elif char_reviews[key]['status'] == 'pending dcc review' or secondary_status == 'pending dcc review':
                char_reviews[key]['status'] = 'pending dcc review'
                char_reviews[key]['detail'] = 'One or more characterization(s) is pending review.'
            elif char_reviews[key]['status'] == 'not compliant':
                if secondary_status == 'pending dcc review':
                    char_reviews[key]['status'] = 'pending dcc review'
                    char_reviews[key]['detail'] = 'Pending review of a secondary characterization.'
                else:
                    char_reviews[key]['status'] = 'not characterized to standards'
                    char_reviews[key]['detail'] = 'Awaiting a compliant primary characterization.'
            elif char_reviews[key]['status'] == 'compliant' and secondary_status == 'compliant':

                # I think these checks can be removed for histones
                #
                if is_histone_mod:
                    if lane_organism not in target_organisms['all']:
                        char_reviews[key]['detail'] = 'Organism was not found in the list ' + \
                            'of organism targets in antibody lot metadata.'
                char_reviews[key]['status'] = 'characterized to standards'
                char_reviews[key]['detail'] = 'Fully characterized.'
            elif char_reviews[key]['status'] == 'compliant' and secondary_status == 'exempt from standards':
                if is_histone_mod:
                    if lane_organism not in target_organisms['all']:
                        char_reviews[key]['detail'] = 'Organism was not found in the list ' + \
                            'of organism targets in antibody lot metadata.'
                char_reviews[key]['status'] = 'characterized to standards with exemption'
                char_reviews[key]['detail'] = 'Fully characterized with exemption.'
            elif (char_reviews[key]['status'] == 'exempt from standards') and \
                    secondary_status in ['compliant', 'exempt from standards']:
                    if is_histone_mod:
                        if lane_organism not in target_organisms['all']:
                            char_reviews[key]['detail'] = 'Organism was not found in the list ' + \
                                'of organism targets in antibody lot metadata.'
                    char_reviews[key]['status'] = 'characterized to standards with exemption'
                    char_reviews[key]['detail'] = 'Fully characterized with exemption.'
            else:
                pass

        if char_reviews:
            return list(char_reviews.values())
