from snovault import (
    upgrade_step,
)


@upgrade_step('annotation', '8', '9')
def annotation_8_9(value, system):
    # http://redmine.encodedcc.org/issues/3764
    # upgrading annotation_types
    if 'annotation_type' in value:
        if value['annotation_type'] == 'segmentation':
            value['annotation_type'] = 'chromatin state'
        if value['annotation_type'] == 'SAGA':
            value['annotation_type'] = 'chromatin state'
        elif value['annotation_type'] == 'enhancer prediction':
            value['annotation_type'] = 'enhancer predictions'
        elif value['annotation_type'] == 'encyclopedia':
            value['annotation_type'] = 'other'
        elif value['annotation_type'] == 'candidate enhancers':
            value['annotation_type'] = 'enhancer-like regions'
        elif value['annotation_type'] == 'candidate promoters':
            value['annotation_type'] = 'promoter-like regions'
