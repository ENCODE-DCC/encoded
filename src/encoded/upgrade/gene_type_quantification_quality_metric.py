
from snovault import (
    CONNECTION,
    upgrade_step,
)


@upgrade_step('gene_type_quantification_quality_metric', '1', '2')
def gene_type_quantification_quality_metric_1_2(value, system):
    props_to_remove = [
        '3prime_overlapping_ncrna',
        'IG_C_gene',
        'IG_C_pseudogene',
        'IG_D_gene',
        'IG_J_gene',
        'IG_J_pseudogene',
        'IG_V_gene',
        'IG_V_pseudogene',
        'Mt_tRNA',
        'TEC',
        'TR_C_gene',
        'TR_D_gene',
        'TR_J_gene',
        'TR_J_pseudogene',
        'TR_V_gene',
        'TR_V_pseudogene',
        'bidirectional_promoter_lncrna',
        'lincRNA',
        'macro_lncRNA',
        'misc_RNA',
        'polymorphic_pseudogene',
        'processed_pseudogene',
        'pseudogene',
        'tRNAscan',
        'transcribed_processed_pseudogene',
        'transcribed_unitary_pseudogene',
        'transcribed_unprocessed_pseudogene',
        'transcript_id_not_found',
        'translated_unprocessed_pseudogene',
        'unitary_pseudogene',
        'unprocessed_pseudogene',
        'vaultRNA'
    ]

    for prop in props_to_remove:
        if prop in value:
            value.pop(prop)
