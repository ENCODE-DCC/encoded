import json
from jsonschema import (
    FormatChecker
)
from .schema_utils import is_uuid
from .storage import (
    DBSession,
    CurrentStatement,
)

def lookup(predicate, instance):
    if is_uuid(instance):
        # use DBSession.CurrentStatement to look up predicate
        pass
    else:
        try:
        # get by DBSession.keyes
            pass
        except:
            return False

    return True

@FormatChecker.cls_checks("gene_name")
def is_gene_name(instance):
    ''' should check a webservice at HGNC/MGI for validation '''
    return True

@FormatChecker.cls_checks("accession")
def is_accession(instance):
    ''' just a pattern checker '''
    pattern = '^ENC(FF|SR|AB|BS|DO|LB)[0-9][0-9][0-9][A-Z][A-Z][A-Z]'
    if not re.match(pattern, instance):
        return False
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


@FormatChecker.cls_checks("antibody_lot_link")
def is_antibody_lot_link(instance):
    return lookup('antibody-lot', instance)

@FormatChecker.cls_checks("award_link")
def is_award_link(instance):
    ''' can be uuid or name or number '''
    if is_uuid(instance):
        pass
    else:
        # try get by name
        # except get by number
        # finally fail
        pass

    return True


@FormatChecker.cls_checks("biosample_link")
def is_biosample_link(instance):
    return lookup('biosample', instance)


@FormatChecker.cls_checks("colleague_link")
def is_colleague_link(instance):
    return lookup('colleague', instance)


@FormatChecker.cls_checks("construct_link")
def is_construct_link(instance):
    return lookup('construct', instance)


@FormatChecker.cls_checks("document_link")
def is_document_link(instance):
    return lookup('document', instance)


@FormatChecker.cls_checks("lab_link")
def is_lab_link(instance):
    return lookup('lab', instance)


@FormatChecker.cls_checks("source_link")
def is_source_link(instance):
    return lookup('source', instance)


@FormatChecker.cls_checks("target_link")
def is_target_link(instance):
    return lookup('target', instance)


@FormatChecker.cls_checks("treatment_link")
def is_treatment_link(instance):
    return lookup('treatment', instance)


@FormatChecker.cls_checks("validation_link")
def is_validation_link(instance):
    return lookup('validation', instance)



