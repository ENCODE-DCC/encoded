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
        'title': 'Antibody lot',
        'description': 'Listing of ENCODE antibodies',
    })
class AntibodyLot(SharedItem):
    item_type = 'antibody_lot'
    schema = load_schema('encoded:schemas/antibody_lot.json')
    name_key = 'accession'
    rev = {
        'characterizations': ('AntibodyCharacterization', 'characterizes'),
        'used_by_biosample_characterizations': (
            'BiosampleCharacterization', 'antibody'
        )
    }
    embedded = [
        'award',
        'source',
        'host_organism',
        'targets',
        'targets.genes',
        'targets.organism',
        'characterizations.award',
        'characterizations.characterization_reviews.biosample_ontology',
        'characterizations.documents',
        'characterizations.lab',
        'characterizations.submitted_by',
        'characterizations.target.genes',
        'characterizations.target.organism',
        'lot_reviews.targets',
        'lot_reviews.targets.genes',
        'lot_reviews.targets.organism',
        'lot_reviews.organisms'
    ]
    audit_inherit = [
        'source',
        'host_organism',
        'targets',
        'targets.organism',
        'characterizations',
        'characterizations.characterization_reviews.biosample_ontology',
        'characterizations.documents',
        'lot_reviews.targets',
        'lot_reviews.targets.organism',
        'lot_reviews.organisms'
    ]
    set_status_up = [
        'source',
        'targets',
        'host_organism',
    ]
    set_status_down = []

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

    @calculated_property(schema={
        "title": "Used by biosample characterizatons",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "BiosampleCharacterization.antibody",
        },
        'notSubmittable': True,
    })
    def used_by_biosample_characterizations(self, request, used_by_biosample_characterizations):
        return paths_filtered_by_status(request, used_by_biosample_characterizations)


@calculated_property(context=AntibodyLot, schema={
    "title": "Antibody review",
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
def lot_reviews(
    request,
    characterizations,
    award,
    control_type=None,
    targets=[],
    used_by_biosample_characterizations=[]
):
    target_organisms = set()
    is_control = bool(control_type)
    is_histone = False
    is_tag = False
    for t in targets:
        target = request.embed(t, '@@object')
        if 'histone' in target['investigated_as']:
            is_histone = True
        if (
            'tag' in target['investigated_as']
            or 'synthetic tag' in target['investigated_as']
        ):
            is_tag = True

        organism = target.get('organism')
        if organism:  # None (synthetic tag) triggers indexinng error
            target_organisms.add(organism)

    # The default base characterization if no characterizations have been submitted
    base_review = {
        'biosample_term_name': 'any cell type or tissue',
        'biosample_term_id': 'NTR:99999999',
        'organisms': sorted(target_organisms),
        'targets': sorted(targets),
    }

    # All control antibodies are exempt and won't be reviewed
    if is_control:
        base_review['status'] = 'characterized to standards with exemption'
        base_review['detail'] = 'IgG does not require further characterization.'
        return [base_review]

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

    # ENCD-4608 ENCODE4 new characterization process for ENCODE4 tagged antibody
    # ENCD-4872 open ENCODE4 new characterization process for ENCODE3 tagged antibody
    rfa = request.embed(award, '@@object?skip_calculated=true')['rfa']
    bio_char_reviews = {}
    if is_tag and rfa in ['ENCODE4', 'ENCODE3']:
        # ENCD-4608 standards for ENCODE4 tag antibody needs different
        # configurations to start with
        encode4_tag_ab_states = {
            'compliant': 'characterized to standards',
            'not compliant': 'not characterized to standards',
            'exempt from standards': 'characterized to standards with exemption',
            'requires secondary opinion': 'awaiting characterization',
            None: 'awaiting characterization',
        }
        encode4_tag_ab_state_details = {
            'compliant': 'Fully characterized.',
            'not compliant': 'Awaiting compliant biosample characterizations.',
            'exempt from standards': 'Fully characterized with exemption.',
            'requires secondary opinion': 'Awaiting to be linked to biosample characterizations.',
            None: 'Awaiting to be linked to biosample characterizations.',
        }

        for bio_char in used_by_biosample_characterizations:
            bio_char_obj = request.embed(
                bio_char, '@@object?skip_calculated=true'
            )
            bio_char_status = bio_char_obj.get('review', {}).get('status')
            bio_obj = request.embed(
                bio_char_obj['characterizes'], '@@object?skip_calculated=true'
            )
            bio_type_obj = request.embed(
                bio_obj['biosample_ontology'], '@@object?skip_calculated=true'
            )
            for target in targets:
                key = (
                    bio_type_obj['term_name'],
                    bio_type_obj['term_id'],
                    bio_obj['organism'],
                    target,
                )
                review = {
                    'biosample_term_name': bio_type_obj['term_name'],
                    'biosample_term_id': bio_type_obj['term_id'],
                    'organisms': [bio_obj['organism']],
                    'targets': [target],
                    'status': encode4_tag_ab_states[bio_char_status],
                    'detail': encode4_tag_ab_state_details[bio_char_status]
                }
                if key not in bio_char_reviews:
                    bio_char_reviews[key] = review
                    continue
                rank = status_ranking[review.get('status')]
                if rank > status_ranking[bio_char_reviews[key].get('status')]:
                    bio_char_reviews[key] = review
        # ENCODE4 tagged antibody will not follow ENCODE3 characterization
        # process and will return here.
        if rfa == 'ENCODE4':
            if bio_char_reviews:
                return list(bio_char_reviews.values())
            else:
                base_review['status'] = 'awaiting characterization'
                base_review['detail'] = 'Awaiting to be linked to biosample characterizations.'
                return [base_review]

    # ENCODE3 characterization process
    ab_char_reviews = build_ab_char_reviews(
        request,
        base_review,
        status_ranking,
        is_histone,
        paths_filtered_by_status(request, characterizations)
    )

    if is_tag and rfa == 'ENCODE3' and bio_char_reviews:
        # ENCD-4872 use biosample characterizations to compensate reviews for
        # ENCODE3 tagged antibody. To avoid permutating organisms and targets
        # while matching `bio_char_reviews` to `ab_char_reviews`, two
        # assumptions here are:
        # 1) if `bio_char_reviews` is not empty, every review in it will have
        # only one organism and one target.
        # 2) if `ab_char_reviews` is not base review, every review in it will
        # have only one organism and one target.
        for review in ab_char_reviews:
            test_key = (
                review['biosample_term_name'],
                review['biosample_term_id'],
                ','.join(review['organisms']),
                ','.join(review['targets']),
            )
            if test_key in bio_char_reviews:
                bio_char_status = bio_char_reviews[test_key]['status']
                if status_ranking[bio_char_status] > status_ranking[review['status']]:
                    review['status'] = bio_char_reviews[test_key]['status']
                    review['detail'] = bio_char_reviews[test_key]['detail']
                bio_char_reviews.pop(test_key)
        return ab_char_reviews + list(bio_char_reviews.values())
    else:
        return ab_char_reviews


def build_ab_char_reviews(
    request,
    base_review,
    status_ranking,
    is_histone,
    characterizations
):
    review_targets = set()
    char_organisms = {}
    primary_chars = []
    secondary_chars = []
    secondary_status = None

    # Since characterizations can only take one target (not an array)
    # and primary characterizations for histone modifications may be done in
    # multiple species, we really need to check lane.organism against the
    # antibody.targets.organism list to determine eligibility of use in that
    # organism.

    for characterization_path in characterizations:
        characterization = request.embed(characterization_path, '@@object')
        target = request.embed(characterization['target'], '@@object')

        # instead of adding to the target_organism list with whatever they put
        # in the characterization we need to instead compare the lane organism
        # to see if it's in the target_organism list. If not, we'll need to
        # indicate that they characterized an organism not in the
        # antibody_lot.targets list so it'll have to be reviewed and added if
        # legitimate.
        review_targets.add(target['@id'])
        char_organisms[characterization['@id']] = target.get('organism')
        # Split into primary and secondary to treat separately
        if 'primary_characterization_method' in characterization:
            primary_chars.append(characterization)
        else:
            secondary_chars.append(characterization)

    # Go through the secondary characterizations first
    if secondary_chars:
        # Determine the consensus secondary characterization status based on
        # all those submitted if more than one and get the highest ranking
        # status in the set
        secondary_status = max(
            (item['status'] for item in secondary_chars),
            key=lambda x: status_ranking[x]
        )

    # If there are no primaries, return the lot review with the secondary status
    if not primary_chars:
        # The default if no primary characterizations have been submitted
        base_review['status'] = ab_states[(None, secondary_status)]
        base_review['detail'] = ab_state_details[(None, secondary_status)]
        if base_review['status'] == 'not pursued':
            base_review['biosample_term_name'] = 'at least one cell type or tissue'
            base_review['biosample_term_id'] = 'NTR:00000000'
        return [base_review]

    # Done with easy cases, the remaining requires checking the primaries and
    # update their status accordingly
    char_reviews = {}
    lane_organism = None
    key = None
    for primary in primary_chars:
        # The default base review to update as needed
        base_review = {
            'biosample_term_name': 'at least one cell type or tissue',
            'biosample_term_id': 'NTR:00000000',
            'organisms': [char_organisms[primary['@id']]] if char_organisms[primary['@id']] else [],
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

                review_biosample_object = request.embed(
                    lane_review['biosample_ontology'],
                    '@@object'
                )
                base_review['organisms'] = [lane_organism]
                if is_histone:
                    base_review['biosample_term_name'] = 'any cell type or tissue'
                    base_review['biosample_term_id'] = 'NTR:99999999'
                    base_review['targets'] = sorted(review_targets)
                else:
                    base_review['biosample_term_name'] = review_biosample_object['term_name']
                    base_review['biosample_term_id'] = review_biosample_object['term_id']
                    base_review['targets'] = [primary['target']]

                if primary['status'] in [
                    'compliant',
                    'not compliant',
                    'pending dcc review',
                    'exempt from standards',
                ]:
                    base_review['status'] = ab_states[
                        (lane_review['lane_status'], secondary_status)
                    ]
                    base_review['detail'] = ab_state_details[
                        (lane_review['lane_status'], secondary_status)
                    ]
                else:
                    base_review['status'] = ab_states[
                        (primary['status'], secondary_status)
                    ]
                    base_review['detail'] = ab_state_details[
                        (primary['status'], secondary_status)
                    ]

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
