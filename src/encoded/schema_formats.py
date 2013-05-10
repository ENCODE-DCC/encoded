import json
import jsonschema
from .schema_utils import is_uuid
from .storage import (
    DBSession,
    CurrentStatement,
)


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


@FormatChecker.cls_checks( "antibody_lot_link" )
def is_antibody_lot_link(instance):
    ''' can be a uuid or accession '''
    if is_uuid(instance):
        # get /antibody-lot/{instance} or use DBSession?
        pass
    elif is_accession(instance):
        # get by accessions, requires uniquekeys branch
        pass
    else:
        return False

    return True

@FormatChecker.cls_checks( "award_link" )
@FormatChecker.cls_checks( "biosample_link" )
@FormatChecker.cls_checks( "colleague_link" )
@FormatChecker.cls_checks( "construct_link" )
@FormatChecker.cls_checks( "document_link" )
@FormatChecker.cls_checks( "donor_link" )
@FormatChecker.cls_checks( "lab_link" )
@FormatChecker.cls_checks( "organism_link" )
@FormatChecker.cls_checks( "source_link" )
@FormatChecker.cls_checks( "target_link" )
@FormatChecker.cls_checks( "treatment_link" )
@FormatChecker.cls_checks( "validation_link" )

