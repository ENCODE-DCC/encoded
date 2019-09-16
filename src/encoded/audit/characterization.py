from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
    space_in_words,
)

@audit_checker('Characterization', frame='object')
def audit_characterization_review_lane(value, system):
    """
    Biosample and genetic modification characterizations need their reviews to have lane
    specified if the review also has its status specified and the characterization's
    characterization_method is one that necessitates lane information.
    """
    characterization_type_audited_methods = {
        'GeneticModificationCharacterization': [
            'immunoblot',
            'PCR analysis',
            'restriction digest',
        ],
        'BiosampleCharacterization': [
            'immunoblot',
            'immunoprecipitation',
            'PCR',
        ]
    }
    for characterization_type, audited_methods in characterization_type_audited_methods.items():
        if characterization_type in value['@type']:
            review = value.get('review', {})
            characterization_method = value.get('characterization_method')
            if all(
                (
                    characterization_method in audited_methods,
                    review,
                    'lane' not in review,
                )
            ):
                detail = ('{} {} of characterization method {} should have a lane '
                    'specified in its review.'.format(
                        space_in_words(characterization_type).capitalize(),
                        audit_link(path_to_text(value['@id']), value['@id']),
                        characterization_method,
                    )
                )
                yield AuditFailure('missing review lane', detail, level='NOT_COMPLIANT')
