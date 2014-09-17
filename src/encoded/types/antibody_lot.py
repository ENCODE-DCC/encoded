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

    if characterizations:
        compliant_secondary = False
        not_compliant_secondary = False
        pending_secondary = False
        not_reviewed_secondary = False
        has_lane_review = False
        not_reviewed = False
        histone_mod_target = False
        lab_not_reviewed_chars = 0
        not_reviewed_chars = 0
        in_progress_chars = 0
        total_characterizations = 0
        num_compliant_celltypes = 0
        organisms = []
        review_targets = []
        histone_organisms = []
        char_reviews = dict()
        primary_chars = []
        secondary_chars = []
        antibody_lot_reviews = []

        for characterization_path in characterizations:
            characterization = find_resource(root, characterization_path)
            target = find_resource(root, characterization.properties['target'])
            organism = find_resource(root, target.properties['organism'])

            if resource_path(target, '') not in review_targets:
                review_targets.append(resource_path(target, ''))

            if 'histone modification' in target.upgrade_properties(finalize=False)['investigated_as']:
                histone_mod_target = True

            if resource_path(organism, '') not in organisms:
                organisms.append(resource_path(organism, ''))

            if characterization.properties['status'] == 'deleted':
                continue
            elif characterization.properties['status'] == 'not submitted for review by lab':
                lab_not_reviewed_chars += 1
                total_characterizations += 1
            elif characterization.properties['status'] == 'not reviewed':
                not_reviewed_chars += 1
                total_characterizations += 1
            elif characterization.properties['status'] == 'in progress':
                in_progress_chars += 1
                total_characterizations += 1
            else:
                total_characterizations += 1

            # Split into primary and secondary to treat separately
            if 'primary_characterization_method' in characterization.properties:
                primary_chars.append(characterization)
            else:
                secondary_chars.append(characterization)

        base_review = {
            'biosample_term_name': 'not specified',
            'biosample_term_id': 'NTR:00000000',
            'organisms': organisms,
            'targets': review_targets,
            'status': 'awaiting lab characterization'
        }

        # Deal with the easy cases where both characterizations have the same statuses not from DCC reviews
        if lab_not_reviewed_chars == total_characterizations and total_characterizations > 0:
            base_review['status'] = 'not pursued'
            antibody_lot_reviews.append(base_review)
        elif not_reviewed_chars == total_characterizations and total_characterizations > 0:
            base_review['status'] = 'not eligible for new data'
            antibody_lot_reviews.append(base_review)
        elif in_progress_chars == total_characterizations and total_characterizations > 0:
            antibody_lot_reviews.append(base_review)
        elif (lab_not_reviewed_chars + not_reviewed_chars) == total_characterizations and total_characterizations > 0:
            antibody_lot_reviews.append(base_review)
        else:
            # Done with easy cases, the remaining require reviews.
            # Go through the secondary characterizations first
            for secondary in secondary_chars:
                if secondary.properties['status'] == 'compliant':
                    compliant_secondary = True
                    break
                elif secondary.properties['status'] == 'pending dcc review':
                    pending_secondary = True
                elif secondary.properties['status'] == 'not compliant':
                    not_compliant_secondary = True
                else:
                    not_reviewed_secondary = True
                    continue

            # Now check the primaries and update their status accordingly
            for primary in primary_chars:
                has_lane_review = False
                if primary.properties['status'] in ['deleted', 'not reviewed', 'not submitted for review by lab']:
                    not_reviewed = True
                    continue

                if 'characterization_reviews' in primary.properties:
                    for lane_review in primary.properties['characterization_reviews']:
                        new_review = {
                            'biosample_term_name': lane_review['biosample_term_name'],
                            'biosample_term_id': lane_review['biosample_term_id'],
                            'status': 'awaiting lab characterization'
                        }

                        # Get the organism information from the lane, not from the target since there are lanes
                        lane_organism = find_resource(root, lane_review['organism'])
                        new_review['organisms'] = [resource_path(lane_organism, '')]

                        if not histone_mod_target:
                            new_review['targets'] = [resource_path(find_resource(root, primary.properties['target']), '')]
                        else:
                            new_review['targets'] = review_targets

                        if lane_review['lane_status'] == 'pending dcc review':
                            if pending_secondary or compliant_secondary:
                                new_review['status'] = 'pending dcc review'
                        elif lane_review['lane_status'] == 'not compliant':
                            if compliant_secondary or not_compliant_secondary:
                                new_review['status'] = 'not eligible for new data'
                        elif lane_review['lane_status'] == 'compliant':
                            if compliant_secondary:
                                if not histone_mod_target:
                                    new_review['status'] = 'eligible for new data'
                                else:
                                    new_review['status'] = 'compliant'

                                    # Keep track of compliant organisms for histones and we
                                    # will fill them in after going through all the lanes
                                    if resource_path(lane_organism, '') not in histone_organisms:
                                        histone_organisms.append(resource_path(lane_organism, ''))

                            if pending_secondary:
                                new_review['status'] = 'pending dcc review'

                        else:
                            # For all other cases, can keep the awaiting status
                            pass

                        key = "%s;%s;%s;%s" % (lane_review['biosample_term_name'], lane_review['biosample_term_id'], lane_review['organism'], target)
                        if key not in char_reviews:
                            char_reviews[key] = new_review
                            has_lane_review = True
                        else:
                            has_lane_review = True
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

                            if status_ranking[lane_review['lane_status']] > status_ranking[char_reviews[key]['status']]:
                                # Check to see if existing status should be overridden
                                char_reviews[key] = new_review

            if has_lane_review:
                for key in char_reviews:
                    if not histone_mod_target:
                        antibody_lot_reviews.append(char_reviews[key])
                    else:
                        # Review of antibodies against histone modifications are treated differently.
                        # There should be at least 3 compliant cell types for eligibility for use
                        if char_reviews[key]['status'] == 'compliant':
                            char_reviews[key]['status'] = 'awaiting lab characterization'
                            num_compliant_celltypes += 1

                if histone_mod_target:
                    if num_compliant_celltypes >= 3 and compliant_secondary:
                        antibody_lot_reviews = [{
                            'biosample_term_name': 'all cell types and tissues',
                            'biosample_term_id': 'NTR:00000000',
                            'organisms': histone_organisms,
                            'targets': review_targets,
                            'status': 'eligible for new data'
                        }]
                    else:
                        for key in char_reviews:
                            antibody_lot_reviews.append(char_reviews[key])

            else:
                # The only uncovered case left in this block is if there is only 1 or more active
                # secondary and 0 or more inactive primaries.
                if (len(primary_chars) >= 1 and not_reviewed_secondary) or (len(secondary_chars) >= 1 and not_reviewed):
                    antibody_lot_reviews.append(base_review)
                else:
                    pass

        if len(primary_chars) == 0 and len(secondary_chars) > 0:
            # There's only seocndary characterization(s)
            antibody_lot_reviews.append(base_review)

    else:
        # If there are no characterizations, then default to awaiting lab characterization.
        is_control = False
        organisms = []
        for t in targets:
            target = find_resource(root, t)
            if 'control' in target.upgrade_properties(finalize=False)['investigated_as']:
                is_control = True

            organism = find_resource(root, target.properties['organism'])
            if resource_path(organism, '') not in organisms:
                organisms.append(resource_path(organism, ''))

        antibody_lot_reviews = [{
            'biosample_term_name': 'not specified',
            'biosample_term_id': 'NTR:00000000',
            'organisms': organisms,
            'targets': list(targets),
            'status': 'eligible for new data' if is_control else 'awaiting lab characterization'
        }]

    return antibody_lot_reviews


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
            'characterizations.award',
            'characterizations.documents',
            'characterizations.lab',
            'characterizations.submitted_by',
            'characterizations.target.organism',
            'lot_reviews.targets',
            'lot_reviews.targets.organism',
            'lot_reviews.organisms'
        ]
