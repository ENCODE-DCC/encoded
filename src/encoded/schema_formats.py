import re
from jsonschema import FormatChecker
from uuid import UUID

accession_re = re.compile('^ENC(FF|SR|AB|BS|DO|LB)[0-9][0-9][0-9][A-Z][A-Z][A-Z]$')


@FormatChecker.cls_checks("uuid")
def is_uuid(instance):
    try:
        UUID(instance)
    except:
        return False
    return True


@FormatChecker.cls_checks("accession")
def is_accession(instance):
    ''' just a pattern checker '''
    return bool(accession_re.match(instance))


@FormatChecker.cls_checks("gene_name")
def is_gene_name(instance):
    ''' should check a webservice at HGNC/MGI for validation '''
    return True


@FormatChecker.cls_checks("target_label")
def is_target_label(instance):
    if is_gene_name(instance):
        #note this always returns true
        return True
    mod_histone_patt = "^H([234]|2A|2B)[KRT][0-9]+(me|ac|ph)"
    fusion_patt = "^(eGFP|HA)-"
    oneoff_patts = "^(Control|Methylcytidine|POLR2Aphospho[ST][0-9+])$"
    if not re.match(mod_histone_patt, instance) or \
       not re.match(fusion_patt, instance) or \
       not re.match(oneoff_patts, instance):
        return False
    return True
