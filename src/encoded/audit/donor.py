from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)


def ordinalize(number):
    n = int(number)
    suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    return number + suffix


def audit_donor_age(value, system):
    if value.get('age'):
        age = value['age']
    else:
        age = value['conceptional_age']

    if value['status'] in ['deleted'] or age in ['unknown', '>89']:
        return

    if '-' in age:
        range_min = float(age.split('-')[0])
        range_max = float(age.split('-')[1])
        if range_min >= range_max:
            detail = ('Donor {} has inconsistent age range {}.'.format(
                audit_link(value['accession'], value['@id']),
                age
                )
            )
            yield AuditFailure('inconsistent age range', detail, level='ERROR')
            return
    else:
        range_min = float(age)

    years = 0
    if value.get('age_units') == 'month':
        years = range_min/7
    elif value.get('age_units') == 'year':
        years = range_min

    if years >= 90:
        detail = ('Donor {} has age {}, HIPAA requires no age 90 yr or older be reported, should be ">89".'.format(
            audit_link(value['accession'], value['@id']),
            value['age_display']
            )
        )
        yield AuditFailure('age in violation of HIPAA', detail, level='ERROR')
        return

def audit_donor_dev_stage(value, system):
    if value['status'] in ['deleted']:
        return

    dev = value['development_ontology']['term_name']
    post_term_end = '-year-old human stage'
    pre_term_end = ' week post-fertilization human stage'

    if value['age_display'] == 'unknown' or '-' in value.get('age','') or '-' in value.get('conceptional_age',''):
        if dev.endswith(post_term_end) or dev.endswith(pre_term_end):
            detail = ('Donor {} of age {} not expected age-specific development_ontology ({}).'.format(
                audit_link(value['accession'], value['@id']),
                value.get('age_display'),
                dev
                )
            )
            yield AuditFailure('inconsistent age, development', detail, level='ERROR')
            return
    elif value.get('age_units') == 'year':
        if value['age'] == '>89':
            if dev != '80 year-old and over human stage':
                detail = ('Donor {} of age {} expected "80 year-old and over human stage" development_ontology, not {}.'.format(
                    audit_link(value['accession'], value['@id']),
                    value.get('age_display'),
                    dev
                    )
                )
                yield AuditFailure('inconsistent age, development', detail, level='ERROR')
                return
        elif dev != value['age'] + post_term_end:
            detail = ('Donor {} of age {} expected matching age-specific development_ontology, not {}.'.format(
                audit_link(value['accession'], value['@id']),
                value.get('age_display'),
                dev
                )
            )
            yield AuditFailure('inconsistent age, development', detail, level='ERROR')
            return
    elif value.get('conceptional_age_units') == 'week' and int(value.get('conceptional_age')) > 8:
        if dev != ordinalize(value['conceptional_age']) + pre_term_end:
            detail = ('Donor {} of age {} expected matching age-specific development_ontology, not {}.'.format(
                audit_link(value['accession'], value['@id']),
                value.get('age_display'),
                dev
                )
            )
            yield AuditFailure('inconsistent age, development', detail, level='ERROR')
            return
    elif value.get('conceptional_age_units') == 'day' and int(value.get('conceptional_age')) > 56:
        days = int(value['conceptional_age'])
        week = days//7
        if days%7 != 0:
            week += 1
        if dev != ordinalize(str(week)) + pre_term_end:
            detail = ('Donor {} of age {} expected matching age-specific development_ontology, not {}.'.format(
                audit_link(value['accession'], value['@id']),
                value.get('age_display'),
                dev
                )
            )
            yield AuditFailure('inconsistent age, development', detail, level='ERROR')
            return
    elif value.get('conceptional_age_units') == 'week' and int(value.get('conceptional_age')) < 9 or \
        value.get('conceptional_age_units') == 'day' and int(value.get('conceptional_age')) < 57:
        if 'embryonic' not in value['development_ontology']['development_slims']:
            detail = ('Donor {} of age 56 days (8 wk) or less should be embryonic, not {}.'.format(
                audit_link(value['accession'], value['@id']),
                value['development_ontology']['development_slims']
                )
            )
            yield AuditFailure('inconsistent age, development', detail, level='ERROR')
            return



function_dispatcher = {
    'audit_donor_age': audit_donor_age,
    'audit_donor_dev_stage': audit_donor_dev_stage
}

@audit_checker('Donor',
               frame=['development_ontology'])
def audit_donor(value, system):
    for function_name in function_dispatcher.keys():
        for failure in function_dispatcher[function_name](value, system):
            yield failure
