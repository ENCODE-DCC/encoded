from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)

@audit_checker('Treatment', frame='object')
def audit_treatment_no_purpose(value, system):
    if "purpose" not in value:
        detail = (
            f"{value['treatment_type']} treatment {value['treatment_term_name']} "
            f"has no specified purpose."
        )
        yield AuditFailure('missing treatment purpose', detail, level='INTERNAL_ACTION')
