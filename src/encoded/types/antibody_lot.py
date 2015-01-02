from ..schema_utils import (
    load_schema,
)
from ..contentbase import (
    location,
)
from .base import (
    Item,
    paths_filtered_by_status,
)


def lot_reviews(characterizations, targets, request):
    characterizations = paths_filtered_by_status(request, characterizations)
    organisms = set()

    if not characterizations:
        # If there are no characterizations, then default to awaiting lab characterization.
        is_control = False
        for t in targets:
            target = request.embed(t, '@@object')
            if 'control' in target['investigated_as']:
                is_control = True

            organism = target['organism']
            organisms.add(organism)

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

    if len(primary_chars) == 0 and len(secondary_chars) > 0:
        # There're only secondary characterization(s)
        return [base_review]

    # Done with easy cases, the remaining require reviews.
    # Go through the secondary characterizations first
    compliant_secondary = False
    not_compliant_secondary = False
    pending_secondary = False

    for secondary in secondary_chars:
        if secondary['status'] == 'compliant':
            compliant_secondary = True
            break
        elif secondary['status'] == 'pending dcc review':
            pending_secondary = True
        elif secondary['status'] == 'not compliant':
            not_compliant_secondary = True

    # Now check the primaries and update their status accordingly
    char_reviews = {}
    histone_organisms = set()

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
            elif lane_review['lane_status'] == 'compliant':
                if compliant_secondary:
                    if not histone_mod_target:
                        new_review['status'] = 'eligible for new data'
                    else:
                        new_review['status'] = 'compliant'

                        # Keep track of compliant organisms for histones and we
                        # will fill them in after going through all the lanes
                        histone_organisms.add(lane_organism)

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
                'eligible for new data': 4,
                'compliant': 3,
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
        num_compliant_celltypes = 0
        for char_review in char_reviews.values():
            if char_review['status'] == 'compliant':
                char_review['status'] = 'awaiting lab characterization'
                num_compliant_celltypes += 1

        if num_compliant_celltypes >= 3 and compliant_secondary:
            return [{
                'biosample_term_name': 'all cell types and tissues',
                'biosample_term_id': 'NTR:00000000',
                'organisms': sorted(histone_organisms),
                'targets': sorted(review_targets),
                'status': 'eligible for new data'
            }]

    return list(char_reviews.values())


@location(
    name='antibodies',
    properties={
        'title': 'Antibodies Registry',
        'description': 'Listing of ENCODE antibodies',
    })
class AntibodyLot(Item):
    item_type = 'antibody_lot'
    schema = load_schema('antibody_lot.json')
    name_key = 'accession'
    template = {
        'lot_reviews': lot_reviews,
        'title': {'$value': '{accession}'},
        'characterizations': (
            lambda request, characterizations: paths_filtered_by_status(request, characterizations)
        ),
    }
    template_keys = [
        {
            'name': '{item_type}:source_product_lot',
            'value': '{source}/{product_id}/{lot_id}',
            '$templated': True,
        },
        {
            'name': '{item_type}:source_product_lot',
            'value': '{source}/{product_id}/{alias}',
            '$repeat': 'alias lot_id_alias',
            '$templated': True,
        },
    ]
    rev = {
        'characterizations': ('antibody_characterization', 'characterizes'),
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
