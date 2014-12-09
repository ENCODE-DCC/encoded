from ..schema_utils import (
    load_schema,
)
from ..contentbase import (
    location,
)
from .base import (
    ACCESSION_KEYS,
    ALIAS_KEYS,
    Collection,
    paths_filtered_by_status,
)
from pyramid.traversal import (
    find_resource,
    resource_path,
)


def lot_reviews(root, characterizations, targets):
    characterizations = paths_filtered_by_status(root, characterizations)
    organisms = set()

    if not characterizations:
        # If there are no characterizations, then default to awaiting lab characterization.
        is_control = False
        for t in targets:
            target = find_resource(root, t)
            target_properties = target.upgrade_properties(finalize=False)
            if 'control' in target_properties['investigated_as']:
                is_control = True

            organism = find_resource(root, target_properties['organism'])
            organisms.add(resource_path(organism, ''))

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
        characterization = find_resource(root, characterization_path)
        characterization_properties = characterization.upgrade_properties(finalize=False)
        target = find_resource(root, characterization_properties['target'])
        target_properties = target.upgrade_properties(finalize=False)
        organism = find_resource(root, target_properties['organism'])

        review_targets.add(resource_path(target, ''))

        # All characterization targets should be a histone_mod_target or all not.
        # (Checked by an audit.)
        if 'histone modification' in target_properties['investigated_as']:
            histone_mod_target = True

        if resource_path(organism, '') not in organisms:
            organisms.add(resource_path(organism, ''))

        if characterization_properties['status'] == 'not submitted for review by lab':
            lab_not_reviewed_chars += 1
            total_characterizations += 1
        elif characterization_properties['status'] == 'not reviewed':
            not_reviewed_chars += 1
            total_characterizations += 1
        elif characterization_properties['status'] == 'in progress':
            in_progress_chars += 1
            total_characterizations += 1
        else:
            total_characterizations += 1

        # Split into primary and secondary to treat separately
        if 'primary_characterization_method' in characterization_properties:
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
        secondary_properties = secondary.upgrade_properties(finalize=False)
        if secondary_properties['status'] == 'compliant':
            compliant_secondary = True
            break
        elif secondary_properties['status'] == 'pending dcc review':
            pending_secondary = True
        elif secondary_properties['status'] == 'not compliant':
            not_compliant_secondary = True

    # Now check the primaries and update their status accordingly
    char_reviews = {}
    histone_organisms = set()

    for primary in primary_chars:
        primary_properties = primary.upgrade_properties(finalize=False)
        if primary_properties['status'] in ['not reviewed', 'not submitted for review by lab']:
            continue

        for lane_review in primary_properties.get('characterization_reviews', []):
            # Get the organism information from the lane, not from the target since there are lanes
            lane_organism = find_resource(root, lane_review['organism'])

            new_review = {
                'biosample_term_name': lane_review['biosample_term_name'],
                'biosample_term_id': lane_review['biosample_term_id'],
                'organisms': [resource_path(lane_organism, '')],
                'targets':
                    sorted(review_targets) if histone_mod_target
                    else [resource_path(find_resource(root, primary_properties['target']), '')],
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
                        histone_organisms.add(resource_path(lane_organism, ''))

                if pending_secondary:
                    new_review['status'] = 'pending dcc review'

            else:
                # For all other cases, can keep the awaiting status
                pass

            key = (
                lane_review['biosample_term_name'],
                lane_review['biosample_term_id'],
                lane_review['organism'],
                resource_path(target, ''),
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

    return char_reviews.values()


@location('antibodies')
class AntibodyLot(Collection):
    item_type = 'antibody_lot'
    schema = load_schema('antibody_lot.json')
    properties = {
        'title': 'Antibodies Registry',
        'description': 'Listing of ENCODE antibodies',
    }

    class Item(Collection.Item):
        template = {
            'lot_reviews': lot_reviews,
            'title': {'$value': '{accession}'},
            'characterizations': (
                lambda root, characterizations: paths_filtered_by_status(root, characterizations)
            ),
        }
        name_key = 'accession'

        keys = ACCESSION_KEYS + ALIAS_KEYS + [
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
