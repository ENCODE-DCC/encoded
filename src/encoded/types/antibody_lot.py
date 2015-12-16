from contentbase import (
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
                "default": "awaiting lab characterization",
                "enum": [
                    "awaiting lab characterization",
                    "pending dcc review",
                    "eligible for new data",
                    "not eligible for new data",
                    "not pursued"
                ]
            }
        }
    },
})
def lot_reviews(characterizations, targets, request):
    characterizations = paths_filtered_by_status(request, characterizations)
    organisms = set()
    antibody_targets = list()

    is_control = False
    for t in targets:
        target = request.embed(t, '@@object')
        if 'control' in target['investigated_as']:
            is_control = True

        organism = target['organism']
        organisms.add(organism)
        antibody_targets.append(target)

    if not characterizations:
        # If there are no characterizations, then default to awaiting lab characterization.
        return [{
            'biosample_term_name': 'not specified',
            'biosample_term_id': 'NTR:00000000',
            'organisms': sorted(organisms),
            'targets': sorted(targets),  # Copy to prevent modification of original data
            'status': 'eligible for new data' if is_control else 'awaiting lab characterization'
        }]

    histone_mod_target = False
    review_targets = set()
    lab_not_reviewed_chars = 0
    total_characterizations = 0
    not_reviewed_chars = 0
    in_progress_chars = 0
    primary_chars = []
    secondary_chars = []

    for characterization_path in characterizations:
        characterization = request.embed(characterization_path, '@@object')
        target = request.embed(characterization['target'], '@@object')
        organism = target['organism']

        review_targets.add(target['@id'])

        # All characterization targets should be a histone_mod_target or all not.
        # (Checked by an audit.)
        if 'histone modification' in target['investigated_as']:
            histone_mod_target = True

        organisms.add(organism)

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
        'organisms': sorted(organisms),
        'targets': sorted(review_targets),
        'status': 'awaiting lab characterization'
    }

    # Deal with the easy cases where both characterizations have the same
    # statuses not from DCC reviews
    if lab_not_reviewed_chars == total_characterizations and total_characterizations > 0:
        base_review['status'] = 'not pursued'
        return [base_review]

    if not_reviewed_chars == total_characterizations and total_characterizations > 0:
        base_review['status'] = 'not eligible for new data'
        return [base_review]

    if in_progress_chars == total_characterizations and total_characterizations > 0:
        return [base_review]

    if (lab_not_reviewed_chars + not_reviewed_chars) == total_characterizations and \
            total_characterizations > 0:
        base_review['status'] = 'not pursued'
        return [base_review]

    if len(primary_chars) > 0 and len(secondary_chars) == 0:
        # There are only primary characterization(s)
        return [base_review]

    if len(primary_chars) == 0 and len(secondary_chars) > 0:
        # There are only secondary characterization(s)
        return [base_review]

    # Done with easy cases, the remaining require reviews.
    # Go through the secondary characterizations first
    compliant_secondary = False
    not_compliant_secondary = False
    pending_secondary = False
    exempted_secondary = False

    for secondary in secondary_chars:
        if secondary['status'] == 'compliant':
            compliant_secondary = True
            break
        elif secondary['status'] == 'exempt from standards':
            exempted_secondary = True
            break
        elif secondary['status'] == 'pending dcc review':
            pending_secondary = True
        elif secondary['status'] == 'not compliant':
            not_compliant_secondary = True
        else:
            pass

    # Now check the primaries and update their status accordingly
    char_reviews = {}
    characterized_organisms = set()
    exempted_organisms = set()

    for primary in primary_chars:
        if primary['status'] in ['not reviewed', 'not submitted for review by lab']:
            continue

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
                'status': 'awaiting lab characterization'
            }

            if lane_review['lane_status'] == 'pending dcc review':
                if pending_secondary or compliant_secondary:
                    new_review['status'] = 'pending dcc review'
            elif lane_review['lane_status'] == 'not compliant':
                if not_compliant_secondary:
                    new_review['status'] = 'not eligible for new data'
            elif lane_review['lane_status'] == 'exempt from standards':
                if not histone_mod_target:
                    if compliant_secondary or exempted_secondary:
                        new_review['status'] = 'eligible for new data (via exemption)'
                else:
                    if lane_organism in organisms:
                        exempted_organisms.add(lane_organism)
            elif lane_review['lane_status'] == 'compliant':
                if not histone_mod_target:
                    if compliant_secondary:
                        new_review['status'] = 'eligible for new data'
                    elif exempted_secondary:
                        new_review['status'] = 'eligible for new data (via exemption)'
                    else:
                        pass
                    # Keep track of compliant organisms for histones and we
                    # will fill them in after going through all the lanes
                else:
                    if lane_organism in organisms:
                        characterized_organisms.add(lane_organism)

                if pending_secondary:
                    new_review['status'] = 'pending dcc review'
            else:
                # For all other cases, can keep the awaiting status
                pass

            key = (
                lane_review['biosample_term_name'],
                lane_review['biosample_term_id'],
                lane_review['organism'],
                target['@id'],
            )
            if key not in char_reviews:
                char_reviews[key] = new_review
                continue

            status_ranking = {
                'eligible for new data': 6,
                'eligible for new data (via exemption)': 5,
                'compliant': 4,
                'exempt from standards': 3,
                'pending dcc review': 2,
                'awaiting lab characterization': 1,
                'not compliant': 0,
                'not reviewed': 0,
                'not submitted for review by lab': 0,
                'deleted': 0,
                'not eligible for new data': 0
            }

            rank = status_ranking[lane_review['lane_status']]
            if rank > status_ranking[char_reviews[key]['status']]:
                # Check to see if existing status should be overridden
                char_reviews[key] = new_review

    if not char_reviews:
        return [base_review]

    if histone_mod_target:
        # Review of antibodies against histone modifications are treated differently.
        # There should be at least 3 compliant cell types for eligibility for use
        # (Feb 2014 standards)
        #
        # August 2015 standards removed the requirement for 3 compliant cell types,
        # the antibody only needs to be characterized in the species it is to be used in.

        just_exempted_organisms = exempted_organisms.difference(characterized_organisms)
        not_characterized_organisms = organisms.symmetric_difference(characterized_organisms.union(exempted_organisms))
        not_characterized_targets = set()
        characterized_targets = set()
        output = list()

        if not_characterized_organisms:
            for not_characterized_organism in not_characterized_organisms:
                for target in antibody_targets:
                    if not_characterized_organism in target['organism']:
                        not_characterized_targets.add(target['@id'])
                    else:
                        characterized_targets.add(target['@id'])
        else:
            for target in antibody_targets:
                characterized_targets.add(target['@id'])

        if just_exempted_organisms:
            if compliant_secondary or exempted_secondary:
                output.append({
                    'biosample_term_name': 'all cell types and tissues',
                    'biosample_term_id': 'NTR:00000000',
                    'organisms': sorted(just_exempted_organisms),
                    'targets': sorted(characterized_targets),
                    'status': 'eligible for new data (via exemption)'
                })

        if characterized_organisms:
            if compliant_secondary:
                output.append({
                    'biosample_term_name': 'all cell types and tissues',
                    'biosample_term_id': 'NTR:00000000',
                    'organisms': sorted(characterized_organisms),
                    'targets': sorted(characterized_targets),
                    'status': 'eligible for new data'
                })
            if exempted_secondary:
                output.append({
                    'biosample_term_name': 'all cell types and tissues',
                    'biosample_term_id': 'NTR:00000000',
                    'organisms': sorted(characterized_organisms),
                    'targets': sorted(characterized_targets),
                    'status': 'eligible for new data (via exemption)'
                })
        if not_characterized_organisms:
            output.append({
                'biosample_term_name': 'all cell types and tissues',
                'biosample_term_id': 'NTR:00000000',
                'organisms': sorted(not_characterized_organisms),
                'targets': sorted(not_characterized_targets),
                'status': 'awaiting lab characterization'
            })
        if not output:
            output.append({
                'biosample_term_name': 'all cell types and tissues',
                'biosample_term_id': 'NTR:99999999',
                'organisms': sorted(organisms),
                'targets': sorted(review_targets),
                'status': 'awaiting lab characterization'
            })

        return output

    return list(char_reviews.values())
