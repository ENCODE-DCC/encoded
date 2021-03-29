import pytest


def test_audit_dnase_footprints(
    testapp,
    base_analysis,
    GRCh38_file,
    replicate_dnase,
    analysis_step_run_dnase_encode4,
    analysis_step_dnase_encode4,
    pipeline_dnase_encode4,
    encode4_award,
    dnase_footprinting_quality_metric,
):
    testapp.patch_json(
        base_analysis['@id'], {'files': [GRCh38_file['@id']]}
    )
    testapp.patch_json(
        GRCh38_file['@id'],
        {
            'replicate': replicate_dnase['@id'],
            'step_run': analysis_step_run_dnase_encode4['@id']
        }
    )
    testapp.patch_json(
        pipeline_dnase_encode4['@id'],
        {
            'analysis_steps': [analysis_step_dnase_encode4['@id']],
            'award': encode4_award['@id'],
        }
    )
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    assert any(
        error['category'] == 'missing footprints'
        for error in res.json['audit'].get('ERROR', [])
    )
    assert all(
        error['category'] != 'missing footprints'
        for errors in res.json['audit'].get('WARNING', [])
        for error in errors
    )

    testapp.patch_json(
        GRCh38_file['@id'], {'output_type': 'footprints'}
    )
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    assert all(
        error['category'] != 'missing footprints'
        for errors in res.json['audit'].get('ERROR', [])
        for error in errors
    )
    assert all(
        error['category'] != 'missing footprints'
        for errors in res.json['audit'].get('WARNING', [])
        for error in errors
    )

    testapp.patch_json(
        dnase_footprinting_quality_metric['@id'], {'footprint_count': 0}
    )
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    assert all(
        error['category'] != 'missing footprints'
        for errors in res.json['audit'].get('ERROR', [])
        for error in errors
    )
    assert any(
        error['category'] == 'missing footprints'
        for error in res.json['audit'].get('WARNING', [])
    )


def test_audit_dnase_encode3(
    testapp,
    base_analysis,
    base_experiment,
    file_tsv_1_1,
    file_bam_1_1,
    bigWig_file,
    correlation_quality_metric,
    hotspot_quality_metric,
    chip_seq_quality_metric,
    library_1,
    library_2,
    biosample_1,
    mouse_donor_1_6,
    replicate_1_1,
    replicate_2_1,
    analysis_step_run_dnase_encode4,
    analysis_step_version_dnase_encode4,
    analysis_step_dnase_encode4,
    pipeline_dnase_encode4,
    encode4_award,
    ENCODE3_award,
    encode_lab
):
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1_6['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(correlation_quality_metric['@id'], {
        'quality_metric_of': [bigWig_file['@id']],
        'Pearson correlation': 0.15})
    testapp.patch_json(chip_seq_quality_metric['@id'], {'mapped': 23})
    testapp.patch_json(
        bigWig_file['@id'],
        {
            'output_type': 'read-depth normalized signal',
            'dataset': base_experiment['@id'],
            'replicate': replicate_1_1['@id'],
            'step_run': analysis_step_run_dnase_encode4['@id']
        }
    )
    testapp.patch_json(
        file_tsv_1_1['@id'],
        {
            'dataset': base_experiment['@id'],
            'output_type': 'hotspots',
            'replicate': replicate_1_1['@id'],
            'step_run': analysis_step_run_dnase_encode4['@id']
        }
    )
    testapp.patch_json(
        file_bam_1_1['@id'],
        {
            'dataset': base_experiment['@id'],
            'output_type': 'alignments',
            'assembly': 'mm10',
            'replicate': replicate_1_1['@id'],
            'step_run': analysis_step_run_dnase_encode4['@id']
        }
    )
    testapp.patch_json(base_analysis['@id'], {
        'files': [
            file_tsv_1_1['@id'],
            file_bam_1_1['@id'],
            bigWig_file['@id']
        ]}
    )
    testapp.patch_json(
        pipeline_dnase_encode4['@id'],
        {
            'analysis_steps': [analysis_step_dnase_encode4['@id']],
            'award': ENCODE3_award['@id'],
            'title': 'DNase-HS pipeline single-end - Version 2',
            'lab': encode_lab['@id']
        }
    )
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    assert any(error['category'] ==
               'low spot score' for error in res.json['audit'].get('WARNING', []))
    assert any(error['category'] ==
               'extremely low read depth' for error in res.json['audit'].get('ERROR', []))
    assert any(error['category'] ==
               'insufficient replicate concordance' for error in res.json['audit'].get('NOT_COMPLIANT', []))


def test_audit_dnase_encode4(
    testapp,
    base_analysis,
    base_experiment,
    file_tsv_1_1,
    file_bam_1_1,
    bigWig_file,
    correlation_quality_metric,
    hotspot_quality_metric,
    chip_seq_quality_metric,
    library_1,
    library_2,
    biosample_1,
    mouse_donor_1_6,
    replicate_1_1,
    replicate_2_1,
    analysis_step_run_dnase_encode4,
    analysis_step_version_dnase_encode4,
    analysis_step_dnase_encode4,
    pipeline_dnase_encode4,
    encode4_award,
    encode_lab
):
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1_6['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(correlation_quality_metric['@id'], {
        'quality_metric_of': [bigWig_file['@id']],
        'Pearson correlation': 0.15})
    testapp.patch_json(chip_seq_quality_metric['@id'], {'mapped': 23})
    testapp.patch_json(
        bigWig_file['@id'],
        {
            'output_type': 'read-depth normalized signal',
            'dataset': base_experiment['@id'],
            'replicate': replicate_1_1['@id'],
            'step_run': analysis_step_run_dnase_encode4['@id']
        }
    )
    testapp.patch_json(
        file_tsv_1_1['@id'],
        {
            'dataset': base_experiment['@id'],
            'output_type': 'hotspots',
            'replicate': replicate_1_1['@id'],
            'step_run': analysis_step_run_dnase_encode4['@id']
        }
    )
    testapp.patch_json(
        file_bam_1_1['@id'],
        {
            'dataset': base_experiment['@id'],
            'output_type': 'alignments',
            'assembly': 'mm10',
            'replicate': replicate_1_1['@id'],
            'step_run': analysis_step_run_dnase_encode4['@id']
        }
    )
    testapp.patch_json(base_analysis['@id'], {
        'files': [
            file_tsv_1_1['@id'],
            file_bam_1_1['@id'],
            bigWig_file['@id']
        ]}
    )
    testapp.patch_json(
        pipeline_dnase_encode4['@id'],
        {
            'analysis_steps': [analysis_step_dnase_encode4['@id']],
            'award': encode4_award['@id'],
            'title': 'DNase-seq pipeline',
            'lab': encode_lab['@id']
        }
    )
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    assert any(error['category'] ==
               'low spot score' for error in res.json['audit'].get('WARNING', []))
    assert any(error['category'] ==
               'extremely low read depth' for error in res.json['audit'].get('ERROR', []))


def test_audit_dnase_missing_read_depth(
    testapp,
    base_analysis,
    base_experiment,
    file_tsv_1_1,
    file_bam_1_1,
    chip_seq_quality_metric,
    library_1,
    library_2,
    biosample_1,
    mouse_donor_1_6,
    replicate_1_1,
    replicate_2_1,
    analysis_step_run_dnase_encode4,
    analysis_step_version_dnase_encode4,
    analysis_step_dnase_encode4,
    pipeline_dnase_encode4,
    ENCODE3_award,
    encode_lab
):
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1_6['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(chip_seq_quality_metric['@id'], {
        'quality_metric_of': [file_tsv_1_1['@id']]})
    testapp.patch_json(
        file_tsv_1_1['@id'],
        {
            'dataset': base_experiment['@id'],
            'replicate': replicate_1_1['@id'],
            'step_run': analysis_step_run_dnase_encode4['@id']
        }
    )
    testapp.patch_json(
        file_bam_1_1['@id'],
        {
            'dataset': base_experiment['@id'],
            'output_type': 'alignments',
            'assembly': 'mm10',
            'replicate': replicate_1_1['@id'],
            'step_run': analysis_step_run_dnase_encode4['@id']
        }
    )
    testapp.patch_json(base_analysis['@id'], {
        'files': [
            file_bam_1_1['@id'],
        ]}
    )
    testapp.patch_json(
        pipeline_dnase_encode4['@id'],
        {
            'analysis_steps': [analysis_step_dnase_encode4['@id']],
            'award': ENCODE3_award['@id'],
            'title': 'DNase-HS pipeline single-end - Version 2',
            'lab': encode_lab['@id']
        }
    )
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    assert any(error['category'] ==
               'missing read depth' for error in res.json['audit'].get('INTERNAL_ACTION', []))


def test_audit_rampage(
    testapp,
    base_analysis,
    base_experiment,
    correlation_quality_metric,
    bam_quality_metric_2_1,
    mad_quality_metric_1_2,
    file_tsv_1_2,
    file_bam_2_1,
    library_1,
    library_2,
    biosample_1,
    mouse_donor_1_6,
    replicate_1_1,
    replicate_2_1,
    analysis_step_run_rna_encode4,
    analysis_step_version_rna_encode4,
    analysis_step_rna_encode4,
    pipeline_rna_encode4,
    ENCODE3_award,
    encode_lab
):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'long read RNA-seq'})
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1_6['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(correlation_quality_metric['@id'], {
        'quality_metric_of': [file_tsv_1_2['@id']],
        'Spearman correlation': 0.15})
    testapp.patch_json(bam_quality_metric_2_1['@id'], {
        'Uniquely mapped reads number': 100,
        'Number of reads mapped to multiple loci': 100
    })
    testapp.patch_json(mad_quality_metric_1_2['@id'], {'Spearman correlation': 0.1})
    testapp.patch_json(
        file_tsv_1_2['@id'],
        {
            'dataset': base_experiment['@id'],
            'output_type': 'gene quantifications',
            'replicate': replicate_1_1['@id'],
            'step_run': analysis_step_run_rna_encode4['@id']
        }
    )
    testapp.patch_json(
        file_bam_2_1['@id'],
        {
            'dataset': base_experiment['@id'],
            'output_type': 'alignments',
            'assembly': 'mm10',
            'replicate': replicate_1_1['@id'],
            'step_run': analysis_step_run_rna_encode4['@id']
        }
    )
    testapp.patch_json(base_analysis['@id'], {
        'files': [
            file_tsv_1_2['@id'],
            file_bam_2_1['@id']
        ]}
    )
    testapp.patch_json(
        pipeline_rna_encode4['@id'],
        {
            'analysis_steps': [analysis_step_rna_encode4['@id']],
            'award': ENCODE3_award['@id'],
            'title': 'RAMPAGE (paired-end, stranded)',
            'lab': encode_lab['@id']
        }
    )
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    assert any(error['category'] ==
               'extremely low read depth' for error in res.json['audit'].get('ERROR', []))
    assert any(error['category'] ==
               'low replicate concordance' for error in res.json['audit'].get('WARNING', []))


def test_audit_small_rna_seq(
    testapp,
    base_analysis,
    base_experiment,
    correlation_quality_metric,
    bam_quality_metric_2_1,
    mad_quality_metric_1_2,
    file_tsv_1_2,
    file_bam_2_1,
    library_1,
    library_2,
    biosample_1,
    mouse_donor_1_6,
    replicate_1_1,
    replicate_2_1,
    analysis_step_run_rna_encode4,
    analysis_step_version_rna_encode4,
    analysis_step_rna_encode4,
    pipeline_rna_encode4,
    ENCODE3_award,
    encode_lab
):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'long read RNA-seq'})
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1_6['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(correlation_quality_metric['@id'], {
        'quality_metric_of': [file_tsv_1_2['@id']],
        'Spearman correlation': 0.15})
    testapp.patch_json(bam_quality_metric_2_1['@id'], {
        'Uniquely mapped reads number': 100,
        'Number of reads mapped to multiple loci': 100
    })
    testapp.patch_json(mad_quality_metric_1_2['@id'], {'Spearman correlation': 0.1})
    testapp.patch_json(
        file_tsv_1_2['@id'],
        {
            'dataset': base_experiment['@id'],
            'output_type': 'gene quantifications',
            'replicate': replicate_1_1['@id'],
            'step_run': analysis_step_run_rna_encode4['@id']
        }
    )
    testapp.patch_json(
        file_bam_2_1['@id'],
        {
            'dataset': base_experiment['@id'],
            'output_type': 'alignments',
            'assembly': 'mm10',
            'replicate': replicate_1_1['@id'],
            'step_run': analysis_step_run_rna_encode4['@id']
        }
    )
    testapp.patch_json(base_analysis['@id'], {
        'files': [
            file_tsv_1_2['@id'],
            file_bam_2_1['@id']
        ]}
    )
    testapp.patch_json(
        pipeline_rna_encode4['@id'],
        {
            'analysis_steps': [analysis_step_rna_encode4['@id']],
            'award': ENCODE3_award['@id'],
            'title': 'Small RNA-seq single-end pipeline',
            'lab': encode_lab['@id']
        }
    )
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    assert any(error['category'] ==
               'extremely low read depth' for error in res.json['audit'].get('ERROR', []))
    assert any(error['category'] ==
               'low replicate concordance' for error in res.json['audit'].get('WARNING', []))


def test_audit_bulk_rna_seq(
    testapp,
    base_analysis,
    base_experiment,
    correlation_quality_metric,
    bam_quality_metric_2_1,
    mad_quality_metric_1_2,
    file_tsv_1_2,
    file_bam_2_1,
    library_1,
    library_2,
    biosample_1,
    mouse_donor_1_6,
    replicate_1_1,
    replicate_2_1,
    analysis_step_run_rna_encode4,
    analysis_step_version_rna_encode4,
    analysis_step_rna_encode4,
    pipeline_rna_encode4,
    ENCODE3_award,
    encode_lab
):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'long read RNA-seq'})
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1_6['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(correlation_quality_metric['@id'], {
        'quality_metric_of': [file_tsv_1_2['@id']],
        'Spearman correlation': 0.15})
    testapp.patch_json(bam_quality_metric_2_1['@id'], {
        'Uniquely mapped reads number': 100,
        'Number of reads mapped to multiple loci': 100
    })
    testapp.patch_json(mad_quality_metric_1_2['@id'], {'Spearman correlation': 0.1})
    testapp.patch_json(
        file_tsv_1_2['@id'],
        {
            'dataset': base_experiment['@id'],
            'output_type': 'gene quantifications',
            'replicate': replicate_1_1['@id'],
            'step_run': analysis_step_run_rna_encode4['@id']
        }
    )
    testapp.patch_json(
        file_bam_2_1['@id'],
        {
            'dataset': base_experiment['@id'],
            'output_type': 'alignments',
            'assembly': 'mm10',
            'replicate': replicate_1_1['@id'],
            'step_run': analysis_step_run_rna_encode4['@id']
        }
    )
    testapp.patch_json(base_analysis['@id'], {
        'files': [
            file_tsv_1_2['@id'],
            file_bam_2_1['@id']
        ]}
    )
    testapp.patch_json(
        pipeline_rna_encode4['@id'],
        {
            'analysis_steps': [analysis_step_rna_encode4['@id']],
            'award': ENCODE3_award['@id'],
            'title': 'Bulk RNA-seq',
            'lab': encode_lab['@id']
        }
    )
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    assert any(error['category'] ==
               'extremely low read depth' for error in res.json['audit'].get('ERROR', []))
    assert any(error['category'] ==
               'low replicate concordance' for error in res.json['audit'].get('WARNING', []))


def test_audit_micro_rna_seq(
    testapp,
    base_analysis,
    base_experiment,
    correlation_quality_metric,
    micro_rna_mapping_quality_metric_2_1,
    micro_rna_quantification_quality_metric_1_2,
    file_tsv_1_2,
    file_bam_2_1,
    library_1,
    library_2,
    biosample_1,
    mouse_donor_1_6,
    replicate_1_1,
    replicate_2_1,
    analysis_step_run_rna_encode4,
    analysis_step_version_rna_encode4,
    analysis_step_rna_encode4,
    pipeline_rna_encode4,
    ENCODE3_award,
    encode_lab
):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'long read RNA-seq'})
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1_6['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(correlation_quality_metric['@id'], {
        'quality_metric_of': [file_tsv_1_2['@id']],
        'Spearman correlation': 0.15})
    testapp.patch_json(
        micro_rna_mapping_quality_metric_2_1['@id'],
        {'aligned_reads': 1000000}
    )
    testapp.patch_json(
        micro_rna_quantification_quality_metric_1_2['@id'],
        {'expressed_mirnas': 100}
    )
    testapp.patch_json(
        file_tsv_1_2['@id'],
        {
            'dataset': base_experiment['@id'],
            'output_type': 'microRNA quantifications',
            'replicate': replicate_1_1['@id'],
            'step_run': analysis_step_run_rna_encode4['@id']
        }
    )
    testapp.patch_json(
        file_bam_2_1['@id'],
        {
            'dataset': base_experiment['@id'],
            'output_type': 'alignments',
            'assembly': 'mm10',
            'replicate': replicate_1_1['@id'],
            'step_run': analysis_step_run_rna_encode4['@id']
        }
    )
    testapp.patch_json(base_analysis['@id'], {
        'files': [
            file_tsv_1_2['@id'],
            file_bam_2_1['@id']
        ]}
    )
    testapp.patch_json(
        pipeline_rna_encode4['@id'],
        {
            'analysis_steps': [analysis_step_rna_encode4['@id']],
            'award': ENCODE3_award['@id'],
            'title': 'microRNA-seq pipeline',
            'lab': encode_lab['@id']
        }
    )
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    assert any(error['category'] ==
               'insufficient replicate concordance' for error in res.json['audit'].get('NOT_COMPLIANT', []))
    assert any(error['category'] ==
               'insufficient number of aligned reads' for error in res.json['audit'].get('NOT_COMPLIANT', []))
    assert any(error['category'] ==
               'insufficient microRNAs expressed' for error in res.json['audit'].get('NOT_COMPLIANT', []))


def test_audit_long_read_rna_seq(
    testapp,
    base_analysis,
    base_experiment,
    correlation_quality_metric,
    long_read_rna_mapping_quality_metric_2_1,
    long_read_rna_quantification_quality_metric_1_2,
    file_tsv_1_2,
    file_bam_2_1,
    library_1,
    library_2,
    biosample_1,
    mouse_donor_1_6,
    replicate_1_1,
    replicate_2_1,
    analysis_step_run_rna_encode4,
    analysis_step_version_rna_encode4,
    analysis_step_rna_encode4,
    pipeline_rna_encode4,
    ENCODE3_award,
    encode_lab
):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'long read RNA-seq'})
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1_6['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(correlation_quality_metric['@id'], {
        'quality_metric_of': [file_tsv_1_2['@id']],
        'Spearman correlation': 0.15})
    testapp.patch_json(long_read_rna_mapping_quality_metric_2_1['@id'], {
        'mapping_rate': 0.3,
        'full_length_non_chimeric_read_count': 100
    })
    testapp.patch_json(long_read_rna_quantification_quality_metric_1_2['@id'], {'genes_detected': 10})
    testapp.patch_json(
        file_tsv_1_2['@id'],
        {
            'dataset': base_experiment['@id'],
            'output_type': 'transcript quantifications',
            'replicate': replicate_1_1['@id'],
            'step_run': analysis_step_run_rna_encode4['@id']
        }
    )
    testapp.patch_json(
        file_bam_2_1['@id'],
        {
            'dataset': base_experiment['@id'],
            'output_type': 'unfiltered alignments',
            'assembly': 'mm10',
            'replicate': replicate_1_1['@id'],
            'step_run': analysis_step_run_rna_encode4['@id']
        }
    )
    testapp.patch_json(base_analysis['@id'], {
        'files': [
            file_tsv_1_2['@id'],
            file_bam_2_1['@id']
        ]}
    )
    testapp.patch_json(
        pipeline_rna_encode4['@id'],
        {
            'analysis_steps': [analysis_step_rna_encode4['@id']],
            'award': ENCODE3_award['@id'],
            'title': 'Long read RNA-seq pipeline',
            'lab': encode_lab['@id']
        }
    )
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    assert any(error['category'] ==
               'insufficient replicate concordance' for error in res.json['audit'].get('NOT_COMPLIANT', []))
    assert any(error['category'] ==
               'insufficient sequencing depth' for error in res.json['audit'].get('NOT_COMPLIANT', []))
    assert any(error['category'] ==
               'insufficient mapping rate' for error in res.json['audit'].get('NOT_COMPLIANT', []))
    assert any(error['category'] ==
               'insufficient genes detected' for error in res.json['audit'].get('NOT_COMPLIANT', []))


def test_audit_rna_seq_missing_read_depth(
    testapp,
    base_analysis,
    base_experiment,
    correlation_quality_metric,
    bam_quality_metric_2_1,
    mad_quality_metric_1_2,
    file_tsv_1_2,
    file_bam_2_1,
    library_1,
    library_2,
    biosample_1,
    mouse_donor_1_6,
    replicate_1_1,
    replicate_2_1,
    analysis_step_run_rna_encode4,
    analysis_step_version_rna_encode4,
    analysis_step_rna_encode4,
    pipeline_rna_encode4,
    ENCODE3_award,
    encode_lab
):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'long read RNA-seq'})
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1_6['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(correlation_quality_metric['@id'], {
        'quality_metric_of': [file_tsv_1_2['@id']],
        'Spearman correlation': 0.15})
    testapp.patch_json(bam_quality_metric_2_1['@id'], {
        'quality_metric_of': [file_tsv_1_2['@id']]
    })
    testapp.patch_json(mad_quality_metric_1_2['@id'], {'Spearman correlation': 0.1})
    testapp.patch_json(
        file_tsv_1_2['@id'],
        {
            'dataset': base_experiment['@id'],
            'output_type': 'gene quantifications',
            'replicate': replicate_1_1['@id'],
            'step_run': analysis_step_run_rna_encode4['@id']
        }
    )
    testapp.patch_json(
        file_bam_2_1['@id'],
        {
            'dataset': base_experiment['@id'],
            'output_type': 'alignments',
            'assembly': 'mm10',
            'replicate': replicate_1_1['@id'],
            'step_run': analysis_step_run_rna_encode4['@id']
        }
    )
    testapp.patch_json(base_analysis['@id'], {
        'files': [
            file_tsv_1_2['@id'],
            file_bam_2_1['@id']
        ]}
    )
    testapp.patch_json(
        pipeline_rna_encode4['@id'],
        {
            'analysis_steps': [analysis_step_rna_encode4['@id']],
            'award': ENCODE3_award['@id'],
            'title': 'Bulk RNA-seq',
            'lab': encode_lab['@id']
        }
    )
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    assert any(
        error['category'] == 'missing read depth'
        for error in res.json['audit'].get('INTERNAL_ACTION', []))
    testapp.patch_json(bam_quality_metric_2_1['@id'], {
        'quality_metric_of': [file_bam_2_1['@id']],
    })
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    assert any(
        error['category'] == 'missing read depth'
        for error in res.json['audit'].get('INTERNAL_ACTION', []))
    testapp.patch_json(bam_quality_metric_2_1['@id'], {
        'Uniquely mapped reads number': 100,
        'Number of reads mapped to multiple loci': 100
    })
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    assert all(
        error['category'] != 'missing read depth'
        for error in res.json['audit'].get('INTERNAL_ACTION', []))


def test_audit_chip_encode4(
    testapp,
    base_analysis,
    base_experiment,
    file_bam_1_chip,
    file_bam_2_chip,
    file_bed_narrowPeak_chip_peaks,
    chip_align_enrich_quality_metric,
    chipseq_filter_quality_metric,
    chip_alignment_quality_metric_extremely_low_read_depth,
    chip_replication_quality_metric_borderline_replicate_concordance,
    chip_library_quality_metric_severe_bottlenecking_poor_complexity,
    library_1,
    library_2,
    biosample_1,
    mouse_donor_1_6,
    replicate_1_1,
    replicate_2_1,
    analysis_step_run_chip_encode4,
    analysis_step_version_chip_encode4,
    analysis_step_chip_encode4,
    pipeline_chip_encode4,
    encode4_award,
    encode_lab
):
    testapp.patch_json(file_bam_1_chip['@id'], {'step_run': analysis_step_run_chip_encode4['@id']})
    testapp.patch_json(file_bam_2_chip['@id'], {'step_run': analysis_step_run_chip_encode4['@id']})
    testapp.patch_json(file_bed_narrowPeak_chip_peaks['@id'], {'step_run': analysis_step_run_chip_encode4['@id']})
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1_6['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_analysis['@id'], {
        'files': [
            file_bam_1_chip['@id'],
            file_bam_2_chip['@id'],
            file_bed_narrowPeak_chip_peaks['@id']
        ]}
    )
    testapp.patch_json(
        pipeline_chip_encode4['@id'],
        {'award': encode4_award['@id'], 'lab': encode_lab['@id']}
    )
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    assert any(error['category'] ==
               'negative NSC' for error in res.json['audit'].get('ERROR', []))
    assert any(error['category'] ==
               'extremely low read depth' for error in res.json['audit'].get('ERROR', []))
    assert any(error['category'] ==
               'poor library complexity' for error in res.json['audit'].get('NOT_COMPLIANT', []))
    assert any(error['category'] ==
               'severe bottlenecking' for error in res.json['audit'].get('NOT_COMPLIANT', []))
    assert any(error['category'] ==
               'borderline replicate concordance' for error in res.json['audit'].get('WARNING', []))


def test_audit_chip_modern(
    testapp,
    base_analysis,
    base_experiment,
    file_bam_1_chip,
    file_bam_2_chip,
    file_bed_narrowPeak_chip_peaks,
    chip_align_enrich_quality_metric,
    chipseq_filter_quality_metric,
    chip_alignment_quality_metric_extremely_low_read_depth,
    chip_replication_quality_metric_borderline_replicate_concordance,
    chip_library_quality_metric_severe_bottlenecking_poor_complexity,
    library_1,
    library_2,
    biosample_1,
    mouse_donor_1_6,
    replicate_1_1,
    replicate_2_1,
    analysis_step_run_chip_encode4,
    analysis_step_version_chip_encode4,
    analysis_step_chip_encode4,
    pipeline_chip_encode4,
    award_modERN,
    encode_lab
):
    testapp.patch_json(file_bam_1_chip['@id'], {'step_run': analysis_step_run_chip_encode4['@id']})
    testapp.patch_json(file_bam_2_chip['@id'], {'step_run': analysis_step_run_chip_encode4['@id']})
    testapp.patch_json(file_bed_narrowPeak_chip_peaks['@id'], {'step_run': analysis_step_run_chip_encode4['@id']})

    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1_6['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(base_analysis['@id'], {
        'files': [
            file_bam_1_chip['@id'],
            file_bam_2_chip['@id'],
            file_bed_narrowPeak_chip_peaks['@id']
        ]}
    )
    testapp.patch_json(
        pipeline_chip_encode4['@id'],
        {'award': award_modERN['@id'], 'lab': encode_lab['@id'], 'title': 'Transcription factor ChIP-seq pipeline (modERN)'}
    )
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    assert any(error['category'] ==
               'insufficient read depth' for error in res.json['audit'].get('NOT_COMPLIANT', []))
    assert any(error['category'] ==
               'poor library complexity' for error in res.json['audit'].get('NOT_COMPLIANT', []))
    assert any(error['category'] ==
               'severe bottlenecking' for error in res.json['audit'].get('NOT_COMPLIANT', []))
    assert any(error['category'] ==
               'borderline replicate concordance' for error in res.json['audit'].get('WARNING', []))


def test_audit_wgbs_encode3(
    testapp,
    base_analysis,
    base_experiment,
    correlation_quality_metric,
    samtools_stats_quality_metric,
    chip_seq_quality_metric,
    wgbs_quality_metric,
    file_bam_1_1,
    file_bam_2_1,
    file_bed_methyl,
    library_1,
    library_2,
    biosample_1,
    mouse_donor_1_6,
    replicate_1_1,
    replicate_2_1,
    analysis_step_run_bam,
    analysis_step_version_bam,
    analysis_step_bam,
    pipeline_bam,
    ENCODE3_award,
    encode_lab
):
    testapp.patch_json(base_experiment['@id'], {'assay_term_name': 'long read RNA-seq'})
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1_6['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(correlation_quality_metric['@id'], {
        'quality_metric_of': [file_bed_methyl['@id']],
        'Pearson correlation': 0.15})
    testapp.patch_json(chip_seq_quality_metric['@id'], {
        'quality_metric_of': [file_bed_methyl['@id']],
        'mapped': 1000})
    testapp.patch_json(wgbs_quality_metric['@id'], {'quality_metric_of': [file_bed_methyl['@id']],})
    testapp.patch_json(samtools_stats_quality_metric['@id'], {
        'quality_metric_of': [file_bam_1_1['@id']],
        'average length': 100})
    testapp.patch_json(file_bed_methyl['@id'], {
        'step_run': analysis_step_run_bam['@id'],
        'assembly': 'GRCh38',
        'award': ENCODE3_award['uuid']})
    testapp.patch_json(file_bam_1_1['@id'], {
        'step_run': analysis_step_run_bam['@id'],
        'assembly': 'GRCh38',
        'award': ENCODE3_award['uuid']})
    testapp.patch_json(file_bam_2_1['@id'], {
        'step_run': analysis_step_run_bam['@id'],
        'assembly': 'GRCh38',
        'award': ENCODE3_award['uuid']})
    testapp.patch_json(base_analysis['@id'], {
        'files': [
            file_bam_1_1['@id'],
            file_bam_2_1['@id'],
            file_bed_methyl['@id'],
        ]}
    )
    testapp.patch_json(
        pipeline_bam['@id'],
        {
            'title': 'WGBS paired-end pipeline',
            'lab': encode_lab['@id']
        }
    )
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    assert any(error['category'] ==
               'high lambda C methylation ratio' for error in res.json['audit'].get('WARNING', []))
    assert any(error['category'] ==
               'extremely low coverage' for error in res.json['audit'].get('ERROR', []))
    assert any(error['category'] ==
               'insufficient replicate concordance' for error in res.json['audit'].get('NOT_COMPLIANT', []))


def test_audit_wgbs_encode4(
    testapp,
    base_analysis,
    base_experiment,
    gembs_quality_metric,
    cpg_correlation_quality_metric,
    file_bam_1_1,
    file_bed_methyl,
    library_1,
    library_2,
    biosample_1,
    mouse_donor_1_6,
    replicate_1_1,
    replicate_2_1,
    analysis_step_run_bam,
    analysis_step_version_bam,
    analysis_step_bam,
    pipeline_bam,
    encode4_award,
    roadmap_award,
    encode_lab
):
    testapp.patch_json(base_experiment['@id'], {
        'status': 'released',
        'date_released': '2021-01-01',
        'replicates': [replicate_1_1['@id'], replicate_2_1['@id']],
        'assay_term_name': 'whole-genome shotgun bisulfite sequencing',
        'award': encode4_award['uuid'],
    })
    testapp.patch_json(biosample_1['@id'], {'donor': mouse_donor_1_6['@id']})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_1['@id']})
    testapp.patch_json(replicate_1_1['@id'], {'library': library_1['@id']})
    testapp.patch_json(replicate_2_1['@id'], {'library': library_2['@id']})
    testapp.patch_json(gembs_quality_metric['@id'], {
        'quality_metric_of': [file_bam_1_1['@id']],
        'average_coverage': 0.01})
    testapp.patch_json(cpg_correlation_quality_metric['@id'], {
        'quality_metric_of': [file_bed_methyl['@id']],
        'Pearson correlation': 0.15})

    testapp.patch_json(file_bam_1_1['@id'], {
        'step_run': analysis_step_run_bam['@id'],
        'assembly': 'GRCh38',
        'award': encode4_award['uuid']})
    testapp.patch_json(file_bed_methyl['@id'], {
        'step_run': analysis_step_run_bam['@id'],
        'assembly': 'GRCh38',
        'award': encode4_award['uuid']})

    testapp.patch_json(base_analysis['@id'], {
        'files': [
            file_bam_1_1['@id'],
            file_bed_methyl['@id']
        ]}
    )
    testapp.patch_json(
        pipeline_bam['@id'],
        {
            'title': 'gemBS',
            'lab': encode_lab['@id']
        }
    )
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    assert any(error['category'] ==
               'extremely low coverage' for error in res.json['audit'].get('ERROR', []))
    assert any(error['category'] ==
               'low lambda C conversion rate' for error in res.json['audit'].get('WARNING', []))
    assert any(error['category'] ==
               'insufficient replicate concordance' for error in res.json['audit'].get('NOT_COMPLIANT', []))

    gembs_qc = testapp.get(gembs_quality_metric['@id'] + '@@edit').json
    gembs_qc.pop('conversion_rate')
    testapp.put_json(gembs_quality_metric['@id'], gembs_qc)
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    assert any(error['category'] ==
               'missing lambda C conversion rate' for error in res.json['audit'].get('ERROR', []))

    testapp.patch_json(base_experiment['@id'], {
        'award': roadmap_award['uuid'],
    })
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    assert any(error['category'] ==
               'missing lambda C conversion rate' for error in res.json['audit'].get('WARNING', []))


def test_audit_analysis_ATAC_ENCODE4_QC_standards(
    testapp,
    base_analysis,
    ATAC_bam,
    ATAC_experiment,
    ATAC_pipeline,
    analysis_step_atac_encode4_alignment,
    atac_alignment_quality_metric_low,
    atac_library_complexity_quality_metric_poor,
    atac_align_enrich_quality_metric_med,
    atac_peak_enrichment_quality_metric_2,
    analysis_step_atac_encode4_pseudoreplicate_concordance,
    ATAC_experiment_replicated,
    replicate_ATAC_seq,
    atac_replication_quality_metric_borderline_replicate_concordance,
    atac_replication_quality_metric_high_peaks,
    atac_rep_metric_peaks_only,
    library_1,
    library_2,
    biosample_human_1,
    biosample_human_2,
    file_fastq_1_atac,
    file_bed_IDR_peaks_atac,
    file_bed_IDR_peaks_2_atac,
    file_bed_replicated_peaks_atac,
    file_bed_pseudo_replicated_peaks_atac,
):
    # https://encodedcc.atlassian.net/browse/ENCD-5255
    # https://encodedcc.atlassian.net/browse/ENCD-5350
    # https://encodedcc.atlassian.net/browse/ENCD-5468
    testapp.patch_json(base_analysis['@id'], {
        'files': [
            ATAC_bam['@id'],
            file_bed_pseudo_replicated_peaks_atac['@id'],
        ]}
    )
    testapp.patch_json(
        atac_alignment_quality_metric_low['@id'],
        {'quality_metric_of': [ATAC_bam['@id']]})
    testapp.patch_json(
        atac_library_complexity_quality_metric_poor['@id'],
        {'quality_metric_of': [ATAC_bam['@id']]})
    testapp.patch_json(
        atac_align_enrich_quality_metric_med['@id'],
        {'quality_metric_of': [ATAC_bam['@id']]})
    testapp.patch_json(
        atac_peak_enrichment_quality_metric_2['@id'],
        {'quality_metric_of': [file_bed_pseudo_replicated_peaks_atac['@id']]})
    testapp.patch_json(atac_replication_quality_metric_borderline_replicate_concordance['@id'],
                       {'quality_metric_of': [file_bed_pseudo_replicated_peaks_atac['@id']]})
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    audit_errors = res.json['audit']
    assert any(error['category'] == 'low alignment rate' for error in audit_errors.get('NOT_COMPLIANT', []))
    assert any(error['category'] == 'poor library complexity' for error in audit_errors.get('NOT_COMPLIANT', []))
    assert any(error['category'] == 'mild to moderate bottlenecking' for error in audit_errors.get('WARNING', []))
    assert any(error['category'] == 'severe bottlenecking' for error in audit_errors.get('NOT_COMPLIANT', []))
    assert any(error['category'] == 'moderate TSS enrichment' for error in audit_errors.get('WARNING', []))
    assert any(error['category'] == 'extremely low read depth' for error in audit_errors.get('ERROR', []))
    assert any(error['category'] == 'no peaks in nucleosome-free regions' for error in audit_errors.get('NOT_COMPLIANT', []))
    assert any(error['category'] == 'low FRiP score' for error in audit_errors.get('NOT_COMPLIANT', []))
    assert any(error['category'] == 'negative RSC' for error in audit_errors.get('ERROR', []))
    assert any(error['category'] == 'negative NSC' for error in audit_errors.get('ERROR', []))
    assert 'borderline replicate concordance' not in (error['category'] for error in audit_errors.get('WARNING', []))

    testapp.patch_json(base_analysis['@id'], {
        'files': [
            file_bed_IDR_peaks_2_atac['@id'],
            file_bed_replicated_peaks_atac['@id']
        ]}
    )
    testapp.patch_json(atac_replication_quality_metric_borderline_replicate_concordance['@id'],
                       {'quality_metric_of': [file_bed_replicated_peaks_atac['@id']]})
    testapp.patch_json(library_1['@id'], {'biosample': biosample_human_1['uuid']})
    testapp.patch_json(library_2['@id'], {'biosample': biosample_human_2['uuid']})
    testapp.patch_json(replicate_ATAC_seq['@id'], {'experiment': ATAC_experiment_replicated['@id']})
    testapp.patch_json(file_fastq_1_atac['@id'], {'dataset': ATAC_experiment_replicated['@id']})
    res2 = testapp.get(base_analysis['@id'] + '@@index-data')
    audit_errors = res2.json['audit']
    assert any(error['category'] == 'borderline replicate concordance' for error in audit_errors.get('WARNING', []))
    assert any(error['category'] == 'insufficient number of reproducible peaks' for error in audit_errors.get('NOT_COMPLIANT', []))

    # Reproducible peaks only checked in QC metrics when rescue_ratio/self_consistency_ratio appear
    testapp.patch_json(atac_rep_metric_peaks_only['@id'],
                       {'quality_metric_of': [file_bed_IDR_peaks_2_atac['@id']]})
    res2 = testapp.get(base_analysis['@id'] + '@@index-data')
    audit_errors = res2.json['audit']
    assert any(error['category'] == 'insufficient number of reproducible peaks' for error in audit_errors.get('NOT_COMPLIANT', []))

    # When reproducible peaks are checked in multiple files, the better value is reported
    # Unlike replicate concordance, which is reported per file
    testapp.patch_json(
        atac_replication_quality_metric_high_peaks['@id'],
        {'quality_metric_of': [file_bed_IDR_peaks_atac['@id']]})
    testapp.patch_json(base_analysis['@id'], {
        'files': [
            file_bed_IDR_peaks_2_atac['@id'],
            file_bed_replicated_peaks_atac['@id'],
            file_bed_IDR_peaks_atac['@id']
        ]}
    )
    res2 = testapp.get(base_analysis['@id'] + '@@index-data')
    audit_errors = res2.json['audit']
    assert 'insufficient number of reproducible peaks' not in (error['category'] for error in audit_errors.get('NOT_COMPLIANT', []))
    assert any(error['category'] == 'borderline replicate concordance' for error in audit_errors.get('WARNING', []))

    # Multiple AtacReplicationQualityMetric objects on the same file is flagged
    # And reproducible peaks/replicate concordance audits are not reported
    testapp.patch_json(
        atac_replication_quality_metric_high_peaks['@id'],
        {'quality_metric_of': [file_bed_IDR_peaks_2_atac['@id']]})
    res2 = testapp.get(base_analysis['@id'] + '@@index-data')
    audit_errors = res2.json['audit']
    assert any(error['category'] == 'duplicate QC metrics' for error in audit_errors.get('ERROR', []))


def test_audit_analysis_chia_encode4_qc_standards(
    testapp,
    base_analysis,
    encode2_award,
    chia_bam,
    chia_peaks,
    chia_chromatin_int,
    ChIA_PET_experiment,
    chia_pet_align_quality_metric,
    chia_pet_chr_int_quality_metric,
    chia_pet_peak_quality_metric,
    analysis_step_run_chia_alignment,
    analysis_step_version_chia_alignment,
    analysis_step_chia_alignment,
    ChIA_PIPE_pipeline
):
    testapp.patch_json(base_analysis['@id'], {
        'files': [
            chia_bam['@id'],
            chia_peaks['@id'],
            chia_chromatin_int['@id'],
        ]}
    )
    testapp.patch_json(
        chia_pet_align_quality_metric['@id'],
        {'quality_metric_of': [chia_bam['@id']]})
    testapp.patch_json(
        chia_pet_chr_int_quality_metric['@id'],
        {'quality_metric_of': [chia_chromatin_int['@id']]})
    testapp.patch_json(
        chia_pet_peak_quality_metric['@id'],
        {'quality_metric_of': [chia_peaks['@id']]})
    res = testapp.get(base_analysis['@id'] + '@@index-data')
    audit_errors = res.json['audit']
    assert any(error['category'] == 'low total read pairs' for error in audit_errors.get('WARNING', []))
    assert any(error['category'] == 'low fraction of read pairs with linker' for error in audit_errors.get('NOT_COMPLIANT', []))
    assert any(error['category'] == 'low non-redundant PET' for error in audit_errors.get('NOT_COMPLIANT', []))
    assert any(error['category'] == 'low protein factor binding peaks' for error in audit_errors.get('NOT_COMPLIANT', []))
    assert any(error['category'] == 'low intra/inter-chr PET ratio' for error in audit_errors.get('WARNING', []))
