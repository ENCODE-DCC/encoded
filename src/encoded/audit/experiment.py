from snovault import (
    AuditFailure,
    audit_checker,
)
from .conditions import rfa
from .ontology_data import biosampleType_ontologyPrefix
from .gtex_data import gtexDonorsList
from .standards_data import pipelines_with_read_depth

import datetime

targetBasedAssayList = [
    'ChIP-seq',
    'RNA Bind-n-Seq',
    'ChIA-PET',
    'RIP Array',
    'RIP-seq',
    'MeDIP-seq',
    'iCLIP',
    'eCLIP',
    'shRNA knockdown followed by RNA-seq',
    'CRISPR genome editing followed by RNA-seq',
    ]

controlRequiredAssayList = [
    'ChIP-seq',
    'RNA Bind-n-Seq',
    'RIP-seq',
    'RAMPAGE',
    'CAGE',
    'single cell isolation followed by RNA-seq',
    'shRNA knockdown followed by RNA-seq',
    'CRISPR genome editing followed by RNA-seq',
    ]

seq_assays = [
    'RNA-seq',
    'ChIP-seq',
    'RNA Bind-n-Seq',
    'MeDIP-seq',
    'RNA-PET',
    'DNA-PET',
    'ChIA-PET',
    'CAGE',
    'RAMPAGE',
    'RIP-seq',
    ]

non_seq_assays = [
    'RNA profiling by array assay',
    'DNA methylation profiling by array assay',
    'Genotype',
    'comparative genomic hybridization by array',
    'RIP-chip',
    'protein sequencing by tandem mass spectrometry assay',
    'microRNA profiling by array assay',
    'Switchgear',
    '5C',
    ]



@audit_checker('Experiment', frame=['original_files',
                                    'target',
                                    'replicates',
                                    'replicates.library',
                                    'replicates.library.spikeins_used',
                                    'replicates.library.biosample',
                                    'replicates.library.biosample.donor',
                                    'replicates.library.biosample.donor.organism',
                                    'original_files.quality_metrics',
                                    'original_files.derived_from',
                                    'original_files.analysis_step_version',
                                    'original_files.analysis_step_version.analysis_step',
                                    'original_files.analysis_step_version.analysis_step.pipelines'],
               condition=rfa('ENCODE3'))
def audit_experiment_standards_dispatcher(value, system):
    '''
    Dispatcher function that will redirect to other functions that woudl deal with specific assay types standards
    '''
    if value['status'] not in ['released', 'release ready']:
        return
    if 'assay_term_name' not in value or \
       value['assay_term_name'] not in ['RAMPAGE', 'RNA-seq', 'ChIP-seq',
                                        'shRNA knockdown followed by RNA-seq',
                                        'CRISPR genome editing followed by RNA-seq',
                                        'single cell isolation followed by RNA-seq']:
        return
    # WE HAVE TO ADD (1) WGBS
    if 'original_files' not in value or len(value['original_files']) == 0:
        return
    if 'replicates' not in value:
        return


    num_bio_reps = set()
    for rep in value['replicates']:
        num_bio_reps.add(rep['biological_replicate_number'])

    if len(num_bio_reps) <= 1:
        return

    organism_name = get_organism_name(value['replicates'])  # human/mouse
    if organism_name == 'human':
        desired_assembly = 'GRCh38'
        desired_annotation = 'V24'
    else:
        if organism_name == 'mouse':
            desired_assembly = 'mm10'
            desired_annotation = 'M4'
        else:
            return

    alignment_files = scanFilesForFileFormat(value['original_files'], 'bam')

    pipeline_title = scanFilesForPipelineTitle(alignment_files,
                                               ['GRCh38', 'mm10'],
                                               ['RNA-seq of long RNAs (paired-end, stranded)',
                                                'RNA-seq of long RNAs (single-end, unstranded)',
                                                'Small RNA-seq single-end pipeline',
                                                'RAMPAGE (paired-end, stranded)',
                                                'Histone ChIP-seq'])
    # I can dd a cross check between pipeline name and assay - but I am not sure it is necessary
    # WE HAVE TO ADD (1) WGBS
    if pipeline_title is False:
        return

    fastq_files = scanFilesForFileFormat(value['original_files'], 'fastq')
    gene_quantifications = scanFilesForOutputType(value['original_files'],
                                                  'gene quantifications')

    if pipeline_title in ['RAMPAGE (paired-end, stranded)']:
        for failure in check_experiement_rampage_encode3_standards(value,
                                                                   fastq_files,
                                                                   alignment_files,
                                                                   pipeline_title,
                                                                   gene_quantifications,
                                                                   desired_assembly,
                                                                   desired_annotation):
            yield failure

    elif pipeline_title in ['Small RNA-seq single-end pipeline']:
        for failure in check_experiement_small_rna_encode3_standards(value,
                                                                     fastq_files,
                                                                     alignment_files,
                                                                     pipeline_title,
                                                                     gene_quantifications,
                                                                     desired_assembly,
                                                                     desired_annotation):
            yield failure

    elif pipeline_title in ['RNA-seq of long RNAs (paired-end, stranded)',
                            'RNA-seq of long RNAs (single-end, unstranded)']:
        for failure in check_experiement_long_rna_encode3_standards(value,
                                                                    fastq_files,
                                                                    alignment_files,
                                                                    pipeline_title,
                                                                    gene_quantifications,
                                                                    desired_assembly,
                                                                    desired_annotation):
            yield failure
    elif pipeline_title in ['Histone ChIP-seq']:
        for failure in check_experiment_chip_seq_encode3_standards(value,
                                                                   fastq_files,
                                                                   alignment_files,
                                                                   pipeline_title):
            yield failure

def check_experiment_chip_seq_encode3_standards(experiment,
                                                fastq_files,
                                                alignment_files,
                                                pipeline_title):
    '''
    Library complexity is measured using the Non-Redundant Fraction (NRF) and PCR Bottlenecking Coefficients 1 and 2, or PBC1 and PBC2. Preferred values are as follows: NRF>0.9, PBC1>0.9, and PBC2>10.
   
   
    Replicate concordance is measured by calculating IDR values 
    (Irreproducible Discovery Rate). The experiment passes if both rescue and self consistency ratios are less than 2.

   '''                                              
    for f in fastq_files:
        if 'run_type' not in f:
            detail = 'Experiment {} '.format(experiment['@id']) + \
                     'contains a file {} '.format(f['@id']) + \
                     'without sequencing run type specified.'
            yield AuditFailure('ChIP-seq - run type not specified', detail, level='WARNING')
        for failure in check_file_read_length(f, 50, 'ChIP-seq'):
            yield failure

    for f in alignment_files:
        target = get_target(experiment)
        read_depth = get_file_read_depth_from_alignment(f, target, 'ChIP-seq')

        #print ("REAd DEPTH " + f['accession'])
        #print (target)
        #print ('depth = ' + str(read_depth))
        #print ("REAd DEPTH")

        for failure in check_chip_seq_file_read_depth(f, target, read_depth, 'ChIP-seq'):
            yield failure


def check_experiement_long_rna_encode3_standards(experiment,
                                                 fastq_files,
                                                 alignment_files,
                                                 pipeline_title,
                                                 gene_quantifications,
                                                 desired_assembly,
                                                 desired_annotation):

    if experiment['assay_term_name'] not in ['shRNA knockdown followed by RNA-seq',
                                             'CRISPR genome editing followed by RNA-seq']:
        for failure in check_experiment_ERCC_spikeins(experiment, pipeline_title, 'long RNA'):
            yield failure
        for failure in check_target(experiment, pipeline_title, 'long RNA'):
            yield failure

    for f in fastq_files:
        if 'run_type' not in f:
            detail = 'Long RNA-seq experiment {} '.format(experiment['@id']) + \
                     'contains a file {} '.format(f['@id']) + \
                     'without sequencing run type specified.'
            yield AuditFailure('long RNA - run type not specified', detail, level='WARNING')
        for failure in check_file_read_length(f, 50, 'long RNA'):
            yield failure
        for failure in check_file_platform(f, ['OBI:0002024', 'OBI:0000696'], 'long RNA'):
            yield failure

    for f in alignment_files:
        if 'assembly' in f and f['assembly'] == desired_assembly:

            read_depth = get_file_read_depth_from_alignment(f,
                                                            get_target(experiment),
                                                            'long RNA')

            if experiment['assay_term_name'] in ['shRNA knockdown followed by RNA-seq',
                                                 'CRISPR genome editing followed by RNA-seq']:
                for failure in check_file_read_depth(f, read_depth, 10000000,
                                                     experiment['assay_term_name'],
                                                     pipeline_title, 'long RNA'):
                    yield failure
            elif experiment['assay_term_name'] in ['single cell isolation followed by RNA-seq']:
                for failure in check_file_read_depth(f, read_depth, 5000000,
                                                     experiment['assay_term_name'],
                                                     pipeline_title, 'long RNA'):
                    yield failure
            else:
                for failure in check_file_read_depth(f, read_depth, 30000000,
                                                     experiment['assay_term_name'],
                                                     pipeline_title, 'long RNA'):
                    yield failure

    if 'replication_type' not in experiment:
        return

    mad_metrics_dict = {}
    for f in gene_quantifications:
        if 'assembly' in f and f['assembly'] == desired_assembly and \
           'genome_annotation' in f and f['genome_annotation'] == desired_annotation:
            if 'quality_metrics' in f and len(f['quality_metrics']) > 0:
                for qm in f['quality_metrics']:
                    mad_metrics_dict[qm['@id']] = qm
    mad_metrics = []
    for k in mad_metrics_dict:
        mad_metrics.append(mad_metrics_dict[k])
    for failure in check_spearman(mad_metrics, experiment['replication_type'],
                                  0.9, 0.8, pipeline_title, 'long RNA'):
        yield failure
    for failure in check_mad(mad_metrics, experiment['replication_type'],
                             0.2, pipeline_title, 'long RNA'):
        yield failure

    return


def check_experiement_small_rna_encode3_standards(experiment,
                                                  fastq_files,
                                                  alignment_files,
                                                  pipeline_title,
                                                  gene_quantifications,
                                                  desired_assembly,
                                                  desired_annotation):
    for f in fastq_files:
        if 'run_type' in f and f['run_type'] != 'single-ended':
            detail = 'Small RNA-seq experiment {} '.format(experiment['@id']) + \
                     'contains a file {} '.format(f['@id']) + \
                     'that is not single-ended.'
            yield AuditFailure('small RNA - not single-ended', detail, level='WARNING')
        for failure in check_file_read_length(f, 50, 'small RNA'):
            yield failure
        for failure in check_file_platform(f, ['OBI:0002024', 'OBI:0000696'], 'small RNA'):
            yield failure

    for f in alignment_files:
        if 'assembly' in f and f['assembly'] == desired_assembly:
            read_depth = get_file_read_depth_from_alignment(f,
                                                            get_target(experiment),
                                                            'small RNA')

            for failure in check_file_read_depth(f, read_depth, 30000000,
                                                 experiment['assay_term_name'],
                                                 pipeline_title, 'small RNA'):
                yield failure

    if 'replication_type' not in experiment:
        return

    mad_metrics_dict = {}
    for f in gene_quantifications:
        if 'assembly' in f and f['assembly'] == desired_assembly and \
           'genome_annotation' in f and f['genome_annotation'] == desired_annotation:
            if 'quality_metrics' in f and len(f['quality_metrics']) > 0:
                for qm in f['quality_metrics']:
                    mad_metrics_dict[qm['@id']] = qm
    mad_metrics = []
    for k in mad_metrics_dict:
        mad_metrics.append(mad_metrics_dict[k])
    for failure in check_spearman(mad_metrics, experiment['replication_type'],
                                  0.9, 0.8, 'Small RNA-seq single-end pipeline', 'small RNA'):
        yield failure
    return


def check_experiement_rampage_encode3_standards(experiment,
                                                fastq_files,
                                                alignment_files,
                                                pipeline_title,
                                                gene_quantifications,
                                                desired_assembly,
                                                desired_annotation):

    for f in fastq_files:
        if 'run_type' in f and f['run_type'] != 'paired-ended':
            detail = 'RAMPAGE experiment {} '.format(experiment['@id']) + \
                     'contains a file {} '.format(f['@id']) + \
                     'that is not paired-ended.'
            yield AuditFailure('RAMPAGE - not paired-ended', detail, level='WARNING')
        for failure in check_file_read_length(f, 50, 'RAMPAGE'):
            yield failure
        for failure in check_file_platform(f, ['OBI:0002024', 'OBI:0000696'], 'RAMPAGE'):
            yield failure

    for f in alignment_files:
        if 'assembly' in f and f['assembly'] == desired_assembly:

            read_depth = get_file_read_depth_from_alignment(f,
                                                            get_target(experiment),
                                                            'RAMPAGE')
            for failure in check_file_read_depth(f, read_depth, 25000000,
                                                 experiment['assay_term_name'],
                                                 pipeline_title, 'RAMPAGE'):
                yield failure

    if 'replication_type' not in experiment:
        return

    mad_metrics_dict = {}
    for f in gene_quantifications:
        if 'assembly' in f and f['assembly'] == desired_assembly and \
           'genome_annotation' in f and f['genome_annotation'] == desired_annotation:
            if 'quality_metrics' in f and len(f['quality_metrics']) > 0:
                for qm in f['quality_metrics']:
                    mad_metrics_dict[qm['@id']] = qm
    mad_metrics = []
    for k in mad_metrics_dict:
        mad_metrics.append(mad_metrics_dict[k])
    for failure in check_spearman(mad_metrics, experiment['replication_type'],
                                  0.9, 0.8, 'RAMPAGE (paired-end, stranded)', 'RAMPAGE'):
        yield failure
    return


def check_mad(metrics, replication_type, mad_threshold, pipeline, assay_name):
    if replication_type in ['anisogenic',
                            'anisogenic, sex-matched and age-matched',
                            'anisogenic, age-matched',
                            'anisogenic, sex-matched']:
        experiment_replication_type = 'anisogenic'
    elif replication_type == 'isogenic':
        experiment_replication_type = 'isogenic'
    else:
        return

    mad_value = None
    for m in metrics:
        if 'MAD of log ratios' in m:
            mad_value = m['MAD of log ratios']
            if mad_value > 0.2:
                detail = 'ENCODE processed gene quantification files {} '.format(m['quality_metric_of']) + \
                         'has Median-Average-Deviation (MAD) ' + \
                         'of replicate log ratios from quantification ' + \
                         'value of {}.'.format(mad_value) + \
                         ' For gene quantification files from an {}'.format(experiment_replication_type) + \
                         ' assay in the {} '.format(pipeline) + \
                         'pipeline, a value <0.2 is recommended, but a value between ' + \
                         '0.2 and 0.5 is acceptable.'
                if experiment_replication_type == 'isogenic':
                    if mad_value < 0.5:
                        yield AuditFailure(assay_name + ' - borderline MAD value', detail,
                                           level='DCC_ACTION')
                    else:
                        yield AuditFailure(assay_name + ' - insufficient MAD value', detail,
                                           level='DCC_ACTION')
                elif experiment_replication_type == 'anisogenic' and mad_value > 0.5:
                    detail = 'ENCODE processed gene quantification files {} '.format(m['quality_metric_of']) + \
                             'has Median-Average-Deviation (MAD) ' + \
                             'of replicate log ratios from quantification ' + \
                             'value of {}.'.format(mad_value) + \
                             ' For gene quantification files from an {}'.format(experiment_replication_type) + \
                             ' assay in the {} '.format(pipeline) + \
                             'pipeline, a value <0.5 is recommended.'
                    yield AuditFailure(assay_name + ' - borderline MAD value', detail,
                                       level='DCC_ACTION')


def check_experiment_ERCC_spikeins(experiment, pipeline, assay_name):
    '''
    The assumption in this functon is that the regular audit will catch anything without spikeins.
    This audit is checking specifically for presence of ERCC spike-in in long-RNA pipeline experiments
    '''
    for rep in experiment['replicates']:

        lib = rep.get('library')
        if lib is None:
            continue

        size_range = lib.get('size_range')
        if size_range != '>200':
            continue

        spikes = lib.get('spikeins_used')
        if (spikes is not None) and (len(spikes) > 0):
            accs = set()
            for s in spikes:
                accs.ad(s['accession'])
            if 'ENCSR156CIL' not in accs:
                detail = 'Library {} '.format(lib['@id']) + \
                         'in experiment {} '.format(experiment['@id']) + \
                         'that was processed by {} pipeline '.format(pipeline) + \
                         'requires ERCC spike-in to be used in it`s preparation.'
                yield AuditFailure(assay_name + ' - missing ERCC spike-in',
                                   detail, level='NOT_COMPLIANT')


def check_target(experiment, pipeline, assay_name):
    if 'target' not in experiment:
        detail = 'Experiment {} '.format(experiment['@id']) + \
                 'that was processed by {} pipeline '.format(pipeline) + \
                 'requires target specification.'
        yield AuditFailure(assay_name + ' - missing target',
                           detail, level='NOT_COMPLIANT')


def get_target(experiment):
    if 'target' in experiment:
        return experiment['target']
    return False


def check_spearman(metrics, replication_type, isogenic_threshold,
                   anisogenic_threshold, pipeline, assay_name):

    if replication_type in ['anisogenic',
                            'anisogenic, sex-matched and age-matched',
                            'anisogenic, age-matched',
                            'anisogenic, sex-matched']:
        threshold = anisogenic_threshold
    elif replication_type == 'isogenic':
        threshold = isogenic_threshold
    else:
        return
    border_value = threshold - 0.07
    print_border = '%.2f' % border_value

    for m in metrics:
        if 'Spearman correlation' in m:
            spearman_correlation = m['Spearman correlation']
            if spearman_correlation < threshold:
                detail = 'ENCODE processed gene quantification files {} '.format(m['quality_metric_of']) + \
                         'have Spearman correlation of {}.'.format(spearman_correlation) + \
                         ' For gene quantification files from an {}'.format(replication_type) + \
                         ' assay in the {} '.format(pipeline) + \
                         'pipeline, >{} is recommended, but a value between '.format(threshold) + \
                         '{} and one STD away ({}) is acceptable.'.format(threshold,
                                                                          print_border)
                if spearman_correlation > border_value:
                    yield AuditFailure(assay_name + ' - low spearman correlation', detail,
                                       level='WARNING')
                else:
                    yield AuditFailure(assay_name + ' - insufficient spearman correlation', detail,
                                       level='NOT_COMPLIANT')


def get_file_read_depth_from_alignment(alignment_file, target, assay_name):

    if alignment_file['output_type'] == 'transcriptome alignments':
        return False

    if alignment_file['lab'] != '/labs/encode-processing-pipeline/':
        return False

    quality_metrics = alignment_file.get('quality_metrics')

    if (quality_metrics is None) or (quality_metrics == []):
        return False

    if assay_name in ['RAMPAGE',
                      'small RNA',
                      'long RNA']:
        for metric in quality_metrics:
            if 'Uniquely mapped reads number' in metric:
                return metric['Uniquely mapped reads number']

    elif assay_name in ['ChIP-seq']:

        derived_from_files = alignment_file.get('derived_from')
        #print ('INSIDE INSIDE INSIDE INSIDE INSIDE INSIDE INSIDE INSIDE INSIDE INSIDE INSIDE INSIDE INSIDE INSIDE INSIDE EXCEPTION' + str(target))

        if (derived_from_files is None) or (derived_from_files == []):
            return False
        #print ('INSIDE INSIDE INSIDE INSIDE INSIDE INSIDE INSIDE INSIDE INSIDE INSIDE INSIDE INSIDE INSIDE INSIDE INSIDE EXCEPTION' + str(target))

        if target is not False and \
           'name' in target and target['name'] in ['H3K9me3-human', 'H3K9me3-mouse']:
            # exception (mapped)
            for metric in quality_metrics:
                if 'processing_stage' in metric and \
                    metric['processing_stage'] == 'unfiltered' and \
                        'mapped' in metric:
                    if "read1" in metric and "read2" in metric:
                        return int(metric['mapped']/2)
                    else:
                        return int(metric['mapped'])
        else:
            # not exception (useful fragments)
            for metric in quality_metrics:
                if ('total' in metric) and \
                   (('processing_stage' in metric and metric['processing_stage'] == 'filtered') or
                   ('processing_stage' not in metric)):
                    if "read1" in metric and "read2" in metric:
                        return int(metric['total']/2)
                    else:
                        return int(metric['total'])
    return False


def check_chip_seq_file_read_depth(file_to_check,
                                   target,
                                   read_depth,
                                   assay_name):

    marks = pipelines_with_read_depth['Histone ChIP-seq']

    if read_depth is False:
        detail = 'ENCODE Processed alignment file {} has no read depth information'.format(
            file_to_check['@id'])
        yield AuditFailure(assay_name + ' - missing read depth', detail, level='DCC_ACTION')
        return

    if target is not False and 'name' in target:
        target_name = target['name']
    else:
        return

    if target is not False and 'investigated_as' in target:
        target_investigated_as = target['investigated_as']
    else:
        return

    if target_name in ['Control-human', 'Control-mouse'] and 'control' in target_investigated_as:
        if read_depth >= marks['narrow'] and read_depth < marks['broad']:
            detail = 'ENCODE Processed alignment file {} has {} '.format(file_to_check['@id'],
                                                                         read_depth) + \
                     'usable fragments. It cannot be used as a control ' + \
                     'in experiments studying broad histone marks, which ' + \
                     'require {} usable fragments, according to '.format(marks['broad']) + \
                     'June 2015 standards.'
            yield AuditFailure(assay_name + ' - insufficient read depth', detail, level='WARNING')
        if read_depth >= 10000000 and read_depth < marks['narrow']:
            detail = 'ENCODE Processed alignment file {} has {} '.format(file_to_check['@id'],
                                                                         read_depth) + \
                     'usable fragments. It cannot be used as a control ' + \
                     'in experiments studying narrow histone marks or ' + \
                     'transcription factors, which ' + \
                     'require {} usable fragments, according to '.format(marks['narrow']) + \
                     'June 2015 standards.'
            yield AuditFailure(assay_name + ' - low read depth', detail, level='WARNING')
        if read_depth < 10000000:
            detail = 'ENCODE Processed alignment file {} has {} '.format(file_to_check['@id'],
                                                                         read_depth) + \
                     'usable fragments. It cannot be used as a control ' + \
                     'in experiments studying narrow histone marks or ' + \
                     'transcription factors, which ' + \
                     'require {} usable fragments, according to '.format(marks['narrow']) + \
                     'June 2015 standards, and 10000000 usable fragments according to' + \
                     ' ENCODE2 standards.'
            yield AuditFailure(assay_name + ' - insufficient read depth',
                               detail, level='NOT_COMPLIANT')
        return
    elif 'broad histone mark' in target_investigated_as:  # target_name in broad_peaks_targets:
        if target_name in ['H3K9me3-human', 'H3K9me3-mouse']:
            if read_depth < marks['broad']:
                detail = 'ENCODE Processed alignment file {} has {} '.format(file_to_check['@id'],
                                                                             read_depth) + \
                         'mapped reads. Replicates for ChIP-seq ' + \
                         'assays and target {} '.format(target_name) + \
                         'investigated as broad histone mark require ' + \
                         '{} mapped reads, according to '.format(marks['broad']) + \
                         'June 2015 standards.'
                yield AuditFailure(assay_name + ' - insufficient read depth',
                                   detail, level='NOT_COMPLIANT')
        else:
            if read_depth >= marks['narrow'] and read_depth < marks['broad']:
                detail = 'ENCODE Processed alignment file {} has {} '.format(file_to_check['@id'],
                                                                             read_depth) + \
                         'usable fragments. Replicates for ChIP-seq ' + \
                         'assays and target {} '.format(target_name) + \
                         'investigated as broad histone mark require ' + \
                         '{} usable fragments, according to '.format(marks['broad']) + \
                         'June 2015 standards.'
                yield AuditFailure(assay_name + ' - low read depth', detail, level='NOT_COMPLIANT')
            elif read_depth < marks['narrow']:
                detail = 'ENCODE Processed alignment file {} has {} '.format(file_to_check['@id'],
                                                                             read_depth) + \
                         'usable fragments. Replicates for ChIP-seq ' + \
                         'assays and target {} '.format(target_name) + \
                         'investigated as broad histone mark require ' + \
                         '{} usable fragments, according to '.format(marks['broad']) + \
                         'June 2015 standards, and 20000000 usable fragments according to' + \
                         ' ENCODE2 standards.'
                yield AuditFailure(assay_name + ' - insufficient read depth',
                                   detail, level='NOT_COMPLIANT')
    elif 'narrow histone mark' in target_investigated_as:
        if read_depth >= 10000000 and read_depth < marks['narrow']:
            detail = 'ENCODE Processed alignment file {} has {} '.format(file_to_check['@id'],
                                                                         read_depth) + \
                     'usable fragments. Replicates for ChIP-seq ' + \
                     'assays and target {} '.format(target_name) + \
                     'investigated as narrow histone mark require ' + \
                     '{} usable fragments, according to '.format(marks['narrow']) + \
                     'June 2015 standards.'
            yield AuditFailure(assay_name + ' - low read depth', detail, level='WARNING')
        elif read_depth < 10000000:
            detail = 'ENCODE Processed alignment file {} has {} '.format(file_to_check['@id'],
                                                                         read_depth) + \
                     'usable fragments. Replicates for ChIP-seq ' + \
                     'assays and target {} '.format(target_name) + \
                     'investigated as narrow histone mark require ' + \
                     '{} usable fragments, according to '.format(marks['narrow']) + \
                     'June 2015 standards, and 10000000 usable fragments according to' + \
                     ' ENCODE2 standards.'
            yield AuditFailure(assay_name + ' - insufficient read depth',
                               detail, level='NOT_COMPLIANT')
    elif 'transcription factor' in target_investigated_as:
        if read_depth >= 10000000 and read_depth < marks['narrow']:
            detail = 'ENCODE Processed alignment file {} has {} '.format(file_to_check['@id'],
                                                                         read_depth) + \
                     'usable fragments. Replicates for ChIP-seq ' + \
                     'assays and target {} '.format(target_name) + \
                     'investigated as transcription factor require ' + \
                     '{} usable fragments, according to '.format(marks['narrow']) + \
                     'June 2015 standards.'
            yield AuditFailure(assay_name + ' - low read depth', detail, level='WARNING')
        elif read_depth < 10000000:
            detail = 'ENCODE Processed alignment file {} has {} '.format(file_to_check['@id'],
                                                                         read_depth) + \
                     'usable fragments. Replicates for ChIP-seq ' + \
                     'assays and target {} '.format(target_name) + \
                     'investigated as transcription factor require ' + \
                     '{} usable fragments, according to '.format(marks['narrow']) + \
                     'June 2015 standards, and 10000000 usable fragments according to' + \
                     ' ENCODE2 standards.'
            yield AuditFailure(assay_name + ' - insufficient read depth',
                               detail, level='NOT_COMPLIANT')


def check_file_read_depth(file_to_check, read_depth, threshold, assay_term_name,
                          pipeline_title, assay_name):
    if read_depth is False:
        detail = 'ENCODE Processed alignment file {} has no read depth information'.format(
            file_to_check['@id'])
        yield AuditFailure(assay_name + ' - missing read depth', detail, level='DCC_ACTION')
        return
    if read_depth is not False and read_depth < threshold:
        detail = 'ENCODE Processed alignment file {} has {} '.format(file_to_check['@id'],
                                                                     read_depth) + \
                 'uniquely mapped reads. Replicates for ' + \
                 '{} assay '.format(assay_term_name) + \
                 'processed by {} pipeline '.format(pipeline_title) + \
                 'require {} uniquely mapped reads.'.format(threshold)
        yield AuditFailure(assay_name + ' - insufficient read depth', detail, level='NOT_COMPLIANT')
        return


def check_file_platform(file_to_check, excluded_platforms, assay_name):
    if 'platform' not in file_to_check:
        detail = 'Reads file {} missing platform'.format(file_to_check['@id'])
        yield AuditFailure(assay_name + ' - missing platform', detail, level='WARNING')
    elif file_to_check['platform'] in excluded_platforms:
        detail = 'Reads file {} has not compliant '.format(file_to_check['@id']) + \
                 'platform (SOLiD) {}.'.format(file_to_check['platform'])
        yield AuditFailure(assay_name + ' - not compliant platform', detail, level='WARNING')


def check_file_read_length(file_to_check, threshold_length, assay_name):
    if 'read_length' not in file_to_check:
        detail = 'Reads file {} missing read_length'.format(file_to_check['@id'])
        yield AuditFailure(assay_name + ' - missing read_length', detail, level='NOT_COMPLIANT')
        return

    creation_date = file_to_check['date_created'][:10].split('-')
    year = int(creation_date[0])
    month = int(creation_date[1])
    day = int(creation_date[2])
    created_date = str(year)+'-'+str(month)+'-'+str(day)
    file_date_creation = datetime.date(year, month, day)
    threshold_date = datetime.date(2015, 6, 30)

    read_length = file_to_check['read_length']
    if read_length < threshold_length:
        detail = 'Fastq file {} '.format(file_to_check['@id']) + \
                 'that was created on {} '.format(created_date) + \
                 'has read length of {}bp.'.format(read_length) + \
                 ' It is not compliant with ENCODE3 standards.' + \
                 ' According to ENCODE3 standards files submitted after 2015-6-30 ' + \
                 'should be at least {}bp long.'.format(threshold_length)
        if file_date_creation < threshold_date:
            yield AuditFailure(assay_name + ' - insufficient read length', detail, level='WARNING')
        else:
            yield AuditFailure(assay_name + ' - insufficient read length', detail, level='NOT_COMPLIANT')
    return


def get_organism_name(reps):
    for rep in reps:
        if rep['status'] not in ['replaced', 'revoked', 'deleted'] and \
           'library' in rep and \
           rep['library']['status'] not in ['replaced', 'revoked', 'deleted'] and \
           'biosample' in rep['library'] and \
           rep['library']['biosample']['status'] not in ['replaced', 'revoked', 'deleted']:
            if 'donor' in rep['library']['biosample']:
                donor = rep['library']['biosample']['donor']
                if 'organism' in donor:
                    return donor['organism']['name']
    return False


def scanFilesForFileFormat(files_to_scan, f_format):
    files_to_return = []
    for f in files_to_scan:
        if 'file_format' in f and f['file_format'] == f_format and \
           f['status'] not in ['replaced', 'revoked', 'deleted']:
            files_to_return.append(f)
    return files_to_return


def scanFilesForOutputType(files_to_scan, o_type):
    files_to_return = []
    for f in files_to_scan:
        if 'output_type' in f and f['output_type'] == o_type and \
           f['status'] not in ['replaced', 'revoked', 'deleted']:
            files_to_return.append(f)
    return files_to_return


def scanFilesForPipelineTitle(files_to_scan, assemblies, pipeline_titles):
    for f in files_to_scan:
        if 'file_format' in f and f['file_format'] == 'bam' and \
           f['status'] not in ['replaced', 'revoked', 'deleted'] and \
           'assembly' in f and f['assembly'] in assemblies and \
           f['lab'] == '/labs/encode-processing-pipeline/' and \
           'analysis_step_version' in f and \
           'analysis_step' in f['analysis_step_version'] and \
           'pipelines' in f['analysis_step_version']['analysis_step']:
            pipelines = f['analysis_step_version']['analysis_step']['pipelines']
            for p in pipelines:
                if p['title'] in pipeline_titles:
                    return p['title']
    return False


@audit_checker('Experiment', frame=['original_files', 'target',
                                    'original_files.analysis_step_version',
                                    'original_files.analysis_step_version.analysis_step',
                                    'original_files.analysis_step_version.analysis_step.pipelines',
                                    'replicates', 'replicates.library'],
               condition=rfa('ENCODE3'))
def audit_experiment_needs_pipeline(value, system):

    if value['status'] not in ['released', 'release ready']:
        return

    if 'assay_term_name' not in value:
        return

    if value['assay_term_name'] not in ['whole-genome shotgun bisulfite sequencing',
                                        'ChIP-seq',
                                        'RNA-seq',
                                        'shRNA knockdown followed by RNA-seq',
                                        'RAMPAGE']:
        return

    if 'original_files' not in value or len(value['original_files']) == 0:
        #  possible ERROR to throw
        return

    pipelines_dict = {'WGBS': ['WGBS single-end pipeline', 'WGBS single-end pipeline - version 2',
                               'WGBS paired-end pipeline'],
                      'RNA-seq-long-paired': ['RNA-seq of long RNAs (paired-end, stranded)'],
                      'RNA-seq-long-single': ['RNA-seq of long RNAs (single-end, unstranded)'],
                      'RNA-seq-short': ['Small RNA-seq single-end pipeline'],
                      'RAMPAGE': ['RAMPAGE (paired-end, stranded)'],
                      'ChIP': ['Histone ChIP-seq']}

    if value['assay_term_name'] == 'whole-genome shotgun bisulfite sequencing':
        if scanFilesForPipeline(value['original_files'], pipelines_dict['WGBS']) is False:
            detail = 'Experiment {} '.format(value['@id']) + \
                     ' needs to be processed by WGBS pipeline.'
            raise AuditFailure('needs pipeline run', detail, level='DCC_ACTION')
        else:
            return

    if 'replicates' not in value:
        return

    file_size_range = 0

    size_flag = False

    for rep in value['replicates']:
        if 'library' in rep:
            if 'size_range' in rep['library']:
                file_size_range = rep['library']['size_range']
                size_flag = True
                break

    if size_flag is False:
        return

    run_type = 'unknown'

    for f in value['original_files']:
        if f['status'] not in ['deleted', 'replaced', 'revoked'] and 'run_type' in f:
            run_type = f['run_type']
            break

    if run_type == 'unknown':
        return

    if value['assay_term_name'] == 'RAMPAGE' and \
       run_type == 'paired-ended' and \
       file_size_range == '>200':
        if scanFilesForPipeline(value['original_files'], pipelines_dict['RAMPAGE']) is False:
            detail = 'Experiment {} '.format(value['@id']) + \
                     'needs to be processed by pipeline {}.'.format(pipelines_dict['RAMPAGE'][0])
            raise AuditFailure('needs pipeline run', detail, level='DCC_ACTION')
        else:
            return

    if value['assay_term_name'] in ['RNA-seq', 'shRNA knockdown followed by RNA-seq'] and \
       run_type == 'single-ended' and \
       file_size_range == '>200':
        if scanFilesForPipeline(value['original_files'],
                                pipelines_dict['RNA-seq-long-single']) is False:
            detail = 'Experiment {} '.format(value['@id']) + \
                     'needs to be processed by ' + \
                     'pipeline {}.'.format(pipelines_dict['RNA-seq-long-single'][0])
            raise AuditFailure('needs pipeline run', detail, level='DCC_ACTION')
        else:
            return

    if value['assay_term_name'] in ['RNA-seq', 'shRNA knockdown followed by RNA-seq'] and \
       run_type == 'paired-ended' and \
       file_size_range == '>200':
        if scanFilesForPipeline(value['original_files'],
                                pipelines_dict['RNA-seq-long-paired']) is False:
            detail = 'Experiment {} '.format(value['@id']) + \
                     'needs to be processed by ' + \
                     'pipeline {}.'.format(pipelines_dict['RNA-seq-long-paired'][0])
            raise AuditFailure('needs pipeline run', detail, level='DCC_ACTION')
        else:
            return

    if value['assay_term_name'] == 'RNA-seq' and \
       run_type == 'single-ended' and \
       file_size_range == '<200':
        if scanFilesForPipeline(value['original_files'],
                                pipelines_dict['RNA-seq-short']) is False:
            detail = 'Experiment {} '.format(value['@id']) + \
                     'needs to be processed by ' + \
                     'pipeline {}.'.format(pipelines_dict['RNA-seq-short'][0])
            raise AuditFailure('needs pipeline run', detail, level='DCC_ACTION')
        else:
            return

    investigated_as_histones = False

    if 'target' in value and 'histone modification' in value['target']['investigated_as']:
        investigated_as_histones = True

    if value['assay_term_name'] == 'ChIP-seq' and investigated_as_histones is True:
        if scanFilesForPipeline(value['original_files'],
                                pipelines_dict['ChIP']) is False:
            detail = 'Experiment {} '.format(value['@id']) + \
                     'needs to be processed by ' + \
                     'pipeline {}.'.format(pipelines_dict['ChIP'])
            raise AuditFailure('needs pipeline run', detail, level='DCC_ACTION')
        else:
            return
    return


def scanFilesForPipeline(files_to_scan, pipeline_title_list):
    for f in files_to_scan:
        if 'analysis_step_version' not in f:
            continue
        else:
            if 'analysis_step' not in f['analysis_step_version']:
                continue
            else:
                if 'pipelines' not in f['analysis_step_version']['analysis_step']:
                    continue
                else:
                    pipelines = f['analysis_step_version']['analysis_step']['pipelines']
                    for p in pipelines:
                        if p['title'] in pipeline_title_list:
                            return True
    return False


def is_gtex_experiment(experiment_to_check):
    for rep in experiment_to_check['replicates']:
        if ('library' in rep) and ('biosample' in rep['library']) and \
           ('donor' in rep['library']['biosample']):
            if rep['library']['biosample']['donor']['accession'] in gtexDonorsList:
                return True
    return False


@audit_checker('experiment', frame=['replicates',
                                    'replicates.library',
                                    'replicates.library.biosample',
                                    'replicates.library.biosample.donor'])
def audit_experiment_gtex_biosample(value, system):
    '''
    Experiments for GTEx should not have more than one biosample (originating in GTEx donor)
    associated with
    '''
    if value['status'] in ['deleted', 'replaced']:
        return

    if len(value['replicates']) < 2:
        return

    if is_gtex_experiment(value) is False:
        return

    biosample_set = set()

    for rep in value['replicates']:
        if ('library' in rep) and ('biosample' in rep['library']):
            biosampleObject = rep['library']['biosample']
            biosample_set.add(biosampleObject['accession'])

    if len(biosample_set) > 1:
        detail = 'GTEx experiment {} '.format(value['@id']) + \
                 'contains {} '.format(len(biosample_set)) + \
                 'biosamples, while according to HRWG decision it should have only 1'
        yield AuditFailure('invalid modelling of GTEx experiment ', detail, level='NOT_COMPLIANT')

    return


@audit_checker('experiment', frame=['object'])
def audit_experiment_biosample_term_id(value, system):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return
    # excluding Bind-n-Seq because they dont have biosamples
    if 'assay_term_name' in value and value['assay_term_name'] == 'RNA Bind-n-Seq':
        return

    if value['status'] not in ['preliminary', 'proposed']:
        if 'biosample_term_id' not in value:
            detail = 'Experiment {} '.format(value['@id']) + \
                     'has no biosample_term_id'
            yield AuditFailure('experiment missing biosample_term_id', detail, level='DCC_ACTION')
        if 'biosample_type' not in value:
            detail = 'Experiment {} '.format(value['@id']) + \
                     'has no biosample_type'
            yield AuditFailure('experiment missing biosample_type', detail, level='DCC_ACTION')
    return


@audit_checker('experiment',
               frame=['replicates', 'original_files', 'original_files.replicate'],
               condition=rfa("ENCODE3", "modERN", "ENCODE2", "GGR",
                             "ENCODE", "modENCODE", "MODENCODE", "ENCODE2-Mouse"))
def audit_experiment_consistent_sequencing_runs(value, system):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return
    if 'replicates' not in value:
        return
    if len(value['replicates']) == 0:
        return
    if 'assay_term_name' not in value:  # checked in audit_experiment_assay
        return

    if value.get('assay_term_name') not in ['ChIP-seq', 'DNase-seq']:
        return

    replicate_pairing_statuses = {}
    replicate_read_lengths = {}

    for file_object in value['original_files']:
        if file_object['status'] in ['deleted', 'replaced', 'revoked']:
            continue
        if file_object['file_format'] == 'fastq':
            if 'replicate' in file_object:
                bio_rep_number = file_object['replicate']['biological_replicate_number']

                if 'read_length' in file_object:
                    if bio_rep_number not in replicate_read_lengths:
                        replicate_read_lengths[bio_rep_number] = set()
                    replicate_read_lengths[bio_rep_number].add(file_object['read_length'])

                if 'run_type' in file_object:
                    if bio_rep_number not in replicate_pairing_statuses:
                        replicate_pairing_statuses[bio_rep_number] = set()
                    replicate_pairing_statuses[bio_rep_number].add(file_object['run_type'])

    for key in replicate_read_lengths:
        if len(replicate_read_lengths[key]) > 1:
            detail = 'Biological replicate {} '.format(key) + \
                     'in experiment {} '.format(value['@id']) + \
                     'has mixed sequencing read lengths {}.'.format(replicate_read_lengths[key])
            yield AuditFailure('mixed intra-replicate read lengths',
                               detail, level='WARNING')

    for key in replicate_pairing_statuses:
        if len(replicate_pairing_statuses[key]) > 1:
            detail = 'Biological replicate {} '.format(key) + \
                     'in experiment {} '.format(value['@id']) + \
                     'has mixed endedness {}.'.format(replicate_pairing_statuses[key])
            yield AuditFailure('mixed intra-replicate endedness',
                               detail, level='WARNING')

    keys = list(replicate_read_lengths.keys())

    if len(keys) > 1:
        for index_i in range(len(keys)):
            for index_j in range(index_i+1, len(keys)):
                i_lengths = replicate_read_lengths[keys[index_i]]
                j_lengths = replicate_read_lengths[keys[index_j]]
                diff_flag = False
                for entry in i_lengths:
                    if entry not in j_lengths:
                        diff_flag = True
                for entry in j_lengths:
                    if entry not in i_lengths:
                        diff_flag = True
                if diff_flag is True:
                    detail = 'Biological replicate {} '.format(keys[index_i]) + \
                             'in experiment {} '.format(value['@id']) + \
                             'has sequencing read lengths {} '.format(i_lengths) + \
                             ' that differ from replicate {},'.format(keys[index_j]) + \
                             ' which has {} sequencing read lengths.'.format(j_lengths)
                    yield AuditFailure('mixed inter-replicate read lengths',
                                       detail, level='WARNING')

    keys = list(replicate_pairing_statuses.keys())
    if len(keys) > 1:
        for index_i in range(len(keys)):
            for index_j in range(index_i+1, len(keys)):
                i_pairs = replicate_pairing_statuses[keys[index_i]]
                j_pairs = replicate_pairing_statuses[keys[index_j]]
                diff_flag = False
                for entry in i_pairs:
                    if entry not in j_pairs:
                        diff_flag = True
                for entry in j_pairs:
                    if entry not in i_pairs:
                        diff_flag = True
                if diff_flag is True:
                    detail = 'Biological replicate {} '.format(keys[index_i]) + \
                             'in experiment {} '.format(value['@id']) + \
                             'has endedness {} '.format(i_pairs) + \
                             ' that differ from replicate {},'.format(keys[index_j]) + \
                             ' which has {}.'.format(j_pairs)
                    yield AuditFailure('mixed inter-replicate endedness',
                                       detail, level='WARNING')

    return


@audit_checker('experiment',
               frame=['replicates', 'original_files', 'original_files.replicate'],
               condition=rfa("ENCODE3", "modERN", "ENCODE2", "GGR",
                             "ENCODE", "modENCODE", "MODENCODE", "ENCODE2-Mouse"))
def audit_experiment_replicate_with_no_files(value, system):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return
    if 'replicates' not in value:
        return
    if len(value['replicates']) == 0:
        return
    if 'assay_term_name' not in value:  # checked in audit_experiment_assay
        return

    seq_assay_flag = False
    if value['assay_term_name'] in seq_assays:
        seq_assay_flag = True

    rep_dictionary = {}
    for rep in value['replicates']:
        rep_dictionary[rep['@id']] = []

    for file_object in value['original_files']:
        if file_object['status'] in ['deleted', 'replaced', 'revoked']:
            continue
        if 'replicate' in file_object:
            file_replicate = file_object['replicate']
            if file_replicate['@id'] in rep_dictionary:
                rep_dictionary[file_replicate['@id']].append(file_object['file_format'])

    audit_level = 'ERROR'
    if value['status'] in ['proposed', 'preliminary', 'in progress', 'started', 'submitted']:
        audit_level = 'WARNING'

    for key in rep_dictionary.keys():
        if len(rep_dictionary[key]) == 0:
            detail = 'Experiment {} replicate '.format(value['@id']) + \
                     '{} does not have files associated with'.format(key)
            yield AuditFailure('missing file in replicate', detail, level='ERROR')
        else:
            if seq_assay_flag is True:
                if 'fasta' not in rep_dictionary[key] and \
                   'csfasta' not in rep_dictionary[key] and \
                   'fastq' not in rep_dictionary[key]:
                    detail = 'Sequencing experiment {} replicate '.format(value['@id']) + \
                             '{} does not have sequence files associated with it.'.format(key)
                    yield AuditFailure('missing sequence file in replicate',
                                       detail, level=audit_level)
    return


@audit_checker('experiment', frame='object')
def audit_experiment_release_date(value, system):
    '''
    Released experiments need release date.
    This should eventually go to schema
    '''
    if value['status'] in ['released', 'revoked'] and 'date_released' not in value:
        detail = 'Experiment {} is released or revoked and requires a value in date_released'.format(value['@id'])
        raise AuditFailure('missing date_released', detail, level='DCC_ACTION')


@audit_checker('experiment',
               frame=['replicates', 'award', 'target',
                      'replicates.library',
                      'replicates.library.biosample',
                      'replicates.library.biosample.donor'],
               condition=rfa("ENCODE3", "modERN", "GGR",
                             "ENCODE", "modENCODE", "MODENCODE", "ENCODE2-Mouse"))
def audit_experiment_replicated(value, system):
    '''
    Experiments in ready for review or release ready state should be replicated. If not,
    wranglers should check with lab as to why before release.
    '''
    if value['status'] not in ['released', 'release ready', 'ready for review']:
        return
    '''
    Excluding single cell isolation experiments from the replication requirement
    Excluding RNA-bind-and-Seq from the replication requirment
    '''
    if value['assay_term_name'] in ['single cell isolation followed by RNA-seq',
                                    'RNA Bind-n-Seq']:
        return
    '''
    Excluding GTEX experiments from the replication requirement
    '''
    if is_gtex_experiment(value) is True:
        return

    if 'target' in value:
        target = value['target']
        if 'control' in target['investigated_as']:
            return

    num_bio_reps = set()
    for rep in value['replicates']:
        num_bio_reps.add(rep['biological_replicate_number'])

    if len(num_bio_reps) <= 1:
        # different levels of severity for different rfas
        if value['award']['rfa'] in ['ENCODE3', 'GGR']:
            detail = 'Experiment {} has only one biological '.format(value['@id']) + \
                     'replicate and is released. Check for proper annotation ' + \
                     'of this state in the metadata'
            raise AuditFailure('unreplicated experiment', detail, level='NOT_COMPLIANT')
        else:
            detail = 'Experiment {} has only one biological '.format(value['@id']) + \
                     'replicate, more than one is typically expected before release'
            raise AuditFailure('unreplicated experiment', detail, level='WARNING')


@audit_checker('experiment', frame=['replicates', 'replicates.library'])
def audit_experiment_replicates_with_no_libraries(value, system):
    if value['status'] in ['deleted', 'replaced', 'revoked', 'proposed']:
        return
    if len(value['replicates']) == 0:
        return
    for rep in value['replicates']:
        if 'library' not in rep:
            detail = 'Experiment {} has a replicate {}, that has no library associated with'.format(
                value['@id'],
                rep['@id'])
            yield AuditFailure('replicate with no library', detail, level='ERROR')
    return


@audit_checker('experiment', frame=['replicates', 'replicates.library.biosample'])
def audit_experiment_isogeneity(value, system):

    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if len(value['replicates']) < 2:
        return

    if value.get('replication_type') is None:
        detail = 'In experiment {} the replication_type cannot be determined'.format(value['@id'])
        yield AuditFailure('undetermined replication_type', detail, level='DCC_ACTION')

    biosample_dict = {}
    biosample_age_list = []
    biosample_sex_list = []
    biosample_donor_list = []

    for rep in value['replicates']:
        if 'library' in rep:
            if 'biosample' in rep['library']:
                biosampleObject = rep['library']['biosample']
                biosample_dict[biosampleObject['accession']] = biosampleObject
                biosample_age_list.append(biosampleObject.get('age'))
                biosample_sex_list.append(biosampleObject.get('sex'))
                biosample_donor_list.append(biosampleObject.get('donor'))
                biosample_species = biosampleObject.get('organism')
            else:
                # If I have a library without a biosample,
                # I cannot make a call about replicate structure
                return
        else:
            # REPLICATES WITH NO LIBRARIES WILL BE CAUGHT BY AUDIT (TICKET 3268)
            # If I have a replicate without a library,
            # I cannot make a call about the replicate structure
            return

    if len(biosample_dict.keys()) < 2:
            return  # unreplicated

    if biosample_species == '/organisms/human/':
        return  # humans are handled in the the replication_type

    if len(set(biosample_donor_list)) > 1:
        detail = 'In experiment {} the biosamples have varying strains {}'.format(
            value['@id'],
            biosample_donor_list)
        yield AuditFailure('mismatched donor', detail, level='ERROR')

    if len(set(biosample_age_list)) > 1:
        detail = 'In experiment {} the biosamples have varying ages {}'.format(
            value['@id'],
            biosample_age_list)
        yield AuditFailure('mismatched age', detail, level='ERROR')

    if len(set(biosample_sex_list)) > 1:
        detail = 'In experiment {} the biosamples have varying sexes {}'.format(
            value['@id'],
            repr(biosample_sex_list))
        yield AuditFailure('mismatched sex', detail, level='ERROR')
    return


@audit_checker('experiment', frame=['replicates', 'replicates.library'])
def audit_experiment_technical_replicates_same_library(value, system):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return
    biological_replicates_dict = {}
    for rep in value['replicates']:
        bio_rep_num = rep['biological_replicate_number']
        if 'library' in rep:
            library = rep['library']
            if bio_rep_num not in biological_replicates_dict:
                biological_replicates_dict[bio_rep_num] = []
            if library['accession'] in biological_replicates_dict[bio_rep_num]:
                detail = 'Experiment {} has '.format(value['@id']) + \
                         'different technical replicates associated with the same library'
                raise AuditFailure('sequencing runs labeled as technical replicates', detail,
                                   level='DCC_ACTION')
            else:
                biological_replicates_dict[bio_rep_num].append(library['accession'])


@audit_checker('experiment', frame=['replicates', 'award',
                                    'replicates.library', 'replicates.library.biosample'])
def audit_experiment_replicates_biosample(value, system):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return
    biological_replicates_dict = {}
    biosamples_list = []
    assay_name = 'unknown'
    if 'assay_term_name' in value:
        assay_name = value['assay_term_name']

    for rep in value['replicates']:
        bio_rep_num = rep['biological_replicate_number']
        if 'library' in rep and 'biosample' in rep['library']:
            biosample = rep['library']['biosample']

            if bio_rep_num not in biological_replicates_dict:
                biological_replicates_dict[bio_rep_num] = biosample['accession']
                if biosample['accession'] in biosamples_list:
                    detail = 'Experiment {} has multiple biological replicates \
                              associated with the same biosample {}'.format(
                        value['@id'],
                        biosample['@id'])
                    raise AuditFailure('biological replicates with identical biosample',
                                       detail, level='DCC_ACTION')
                else:
                    biosamples_list.append(biosample['accession'])

            else:
                if biosample['accession'] != biological_replicates_dict[bio_rep_num] and \
                   assay_name != 'single cell isolation followed by RNA-seq':
                    detail = 'Experiment {} has technical replicates \
                              associated with the different biosamples'.format(
                        value['@id'])
                    raise AuditFailure('technical replicates with not identical biosample',
                                       detail, level='ERROR')


@audit_checker('experiment', frame=['replicates', 'replicates.library'])
def audit_experiment_documents(value, system):
    '''
    Experiments should have documents.  Protocol documents or some sort of document.
    '''
    if value['status'] in ['deleted', 'replaced', 'proposed', 'preliminary']:
        return

    # If the experiment has documents, we are good
    if len(value.get('documents')) > 0:
        return

    # If there are no replicates to check yet, why bother
    if 'replicates' not in value:
        return

    lib_docs = 0
    for rep in value['replicates']:
        if 'library' in rep:
            lib_docs += len(rep['library']['documents'])

    # If there are no library documents anywhere, then we say something
    if lib_docs == 0:
        detail = 'Experiment {} has no attached documents'.format(value['@id'])
        raise AuditFailure('missing documents', detail, level='NOT_COMPLIANT')


@audit_checker('experiment', frame='object')
def audit_experiment_assay(value, system):
    '''
    Experiments should have assays with valid ontologies term ids and names that
    are a valid synonym.
    '''
    if value['status'] == 'deleted':
        return

    if 'assay_term_id' not in value:
        detail = 'Experiment {} is missing assay_term_id'.format(value['@id'])
        yield AuditFailure('missing assay information', detail, level='ERROR')
        return
        # This should be a dependancy

    if 'assay_term_name' not in value:
        detail = 'Experiment {} is missing assay_term_name'.format(value['@id'])
        yield AuditFailure('missing assay information', detail, level='ERROR')
        return
        # This should be a dependancy

    ontology = system['registry']['ontology']
    term_id = value.get('assay_term_id')
    term_name = value.get('assay_term_name')

    if term_id.startswith('NTR:'):
        detail = 'Assay_term_id is a New Term Request ({} - {})'.format(term_id, term_name)
        yield AuditFailure('NTR assay', detail, level='DCC_ACTION')
        return

    if term_id not in ontology:
        detail = 'Assay_term_id {} is not found in cached version of ontology'.format(term_id)
        yield AuditFailure('assay_term_id not in ontology', term_id, level='DCC_ACTION')
        return

    ontology_term_name = ontology[term_id]['name']
    modifed_term_name = term_name + ' assay'
    if (ontology_term_name != term_name and term_name not in ontology[term_id]['synonyms']) and \
        (ontology_term_name != modifed_term_name and
            modifed_term_name not in ontology[term_id]['synonyms']):
        detail = 'Experiment has a mismatch between assay_term_name "{}" and assay_term_id "{}"'.format(
            term_name,
            term_id,
            )
        yield AuditFailure('mismatched assay_term_name', detail, level='DCC_ACTION')
        return


@audit_checker('experiment', frame=['replicates.antibody', 'target', 'replicates.antibody.targets'])
def audit_experiment_target(value, system):
    '''
    Certain assay types (ChIP-seq, ...) require valid targets and the replicate's
    antibodies should match.
    '''

    if value['status'] in ['deleted', 'proposed']:
        return

    if value.get('assay_term_name') not in targetBasedAssayList:
        return

    if 'target' not in value:
        detail = '{} experiments require a target'.format(value['assay_term_name'])
        yield AuditFailure('missing target', detail, level='ERROR')
        return

    target = value['target']
    if 'control' in target['investigated_as']:
        return

    # Some assays don't need antibodies
    if value['assay_term_name'] in ['RNA Bind-n-Seq', 'shRNA knockdown followed by RNA-seq']:
        return

    # Check that target of experiment matches target of antibody
    for rep in value['replicates']:
        if 'antibody' not in rep:
            detail = 'Replicate {} in a {} assay requires an antibody'.format(
                rep['@id'],
                value['assay_term_name']
                )
            yield AuditFailure('missing antibody', detail, level='ERROR')
        else:
            antibody = rep['antibody']
            if 'recombinant protein' in target['investigated_as']:
                prefix = target['label'].split('-')[0]
                unique_antibody_target = set()
                unique_investigated_as = set()
                for antibody_target in antibody['targets']:
                    label = antibody_target['label']
                    unique_antibody_target.add(label)
                    for investigated_as in antibody_target['investigated_as']:
                        unique_investigated_as.add(investigated_as)
                if 'tag' not in unique_investigated_as:
                    detail = '{} is not to tagged protein'.format(antibody['@id'])
                    yield AuditFailure('not tagged antibody', detail, level='ERROR')
                else:
                    if prefix not in unique_antibody_target:
                        detail = '{} is not found in target for {}'.format(
                            prefix,
                            antibody['@id']
                            )
                        yield AuditFailure('mismatched tag target', detail, level='ERROR')
            else:
                target_matches = False
                for antibody_target in antibody['targets']:
                    if target['name'] == antibody_target.get('name'):
                        target_matches = True
                if not target_matches:
                    detail = '{} is not found in target list for antibody {}'.format(
                        target['name'],
                        antibody['@id']
                        )
                    yield AuditFailure('mismatched target', detail, level='ERROR')


@audit_checker('experiment', frame=['target', 'possible_controls'])
def audit_experiment_control(value, system):
    '''
    Certain assay types (ChIP-seq, ...) require possible controls with a matching biosample.
    Of course, controls do not require controls.
    '''

    if value['status'] in ['deleted', 'proposed']:
        return

    # Currently controls are only be required for ChIP-seq
    if value.get('assay_term_name') not in controlRequiredAssayList:
        return

    # We do not want controls
    if 'target' in value and 'control' in value['target']['investigated_as']:
        return

    if value['possible_controls'] == []:
        detail = '{} experiments require a value in possible_control'.format(
            value['assay_term_name']
            )
        raise AuditFailure('missing possible_controls', detail, level='ERROR')

    for control in value['possible_controls']:
        if control.get('biosample_term_id') != value.get('biosample_term_id'):
            detail = 'Control {} is for {} but experiment is done on {}'.format(
                control['@id'],
                control.get('biosample_term_name'),
                value['biosample_term_name'])
            raise AuditFailure('mismatched control', detail, level='ERROR')


@audit_checker('experiment', frame=['target',
                                    'possible_controls',
                                    'replicates', 'replicates.antibody',
                                    'possible_controls.replicates',
                                    'possible_controls.replicates.antibody',
                                    'possible_controls.target'],
               condition=rfa('ENCODE3', 'Roadmap'))
def audit_experiment_ChIP_control(value, system):

    if value['status'] in ['deleted', 'proposed', 'preliminary', 'replaced', 'revoked']:
        return

    # Currently controls are only be required for ChIP-seq
    if value.get('assay_term_name') != 'ChIP-seq':
        return

    # We do not want controls
    if 'target' in value and 'control' in value['target']['investigated_as']:
        return

    if not value['possible_controls']:
        return

    num_IgG_controls = 0
    for control in value['possible_controls']:
        if ('target' not in control) or ('control' not in control['target']['investigated_as']):
            detail = 'Experiment {} is ChIP-seq but its control {} is not linked to a target with investigated.as = control'.format(
                value['@id'],
                control['@id'])
            raise AuditFailure('invalid possible_control', detail, level='ERROR')

        if not control['replicates']:
            continue

        if 'antibody' in control['replicates'][0]:
            num_IgG_controls += 1

    # If all of the possible_control experiments are mock IP control experiments
    if num_IgG_controls == len(value['possible_controls']):
        if value.get('assay_term_name') == 'ChIP-seq':
            # The binding group agreed that ChIP-seqs all should have an input control.
            detail = 'Experiment {} is ChIP-seq and requires at least one input control, as agreed upon by the binding group. {} is not an input control'.format(
                value['@id'],
                control['@id'])
            raise AuditFailure('missing input control', detail, level='NOT_COMPLIANT')


@audit_checker('experiment', frame=['replicates', 'replicates.library'])
def audit_experiment_spikeins(value, system):
    '''
    All ENCODE 3 long (>200) RNA-seq experiments should specify their spikeins.
    The spikeins specified should have datasets of type spikeins.
    The spikeins datasets should have a fasta file, a document, and maybe a tsv
    '''

    if value['status'] in ['deleted', 'replaced']:
        return

    if value.get('assay_term_name') != 'RNA-seq':
        return

    for rep in value['replicates']:

        lib = rep.get('library')
        if lib is None:
            continue

        size_range = lib.get('size_range')
        if size_range != '>200':
            continue

        spikes = lib.get('spikeins_used')
        if (spikes is None) or (spikes == []):
            detail = 'Library {} is in an RNA-seq experiment and has size_range >200. It requires a value for spikeins_used'.format(lib['@id'])
            yield AuditFailure('missing spikeins_used', detail, level='NOT_COMPLIANT')
            # Informattional if ENCODE2 and release error if ENCODE3


@audit_checker('experiment', frame=['replicates',
                                    'replicates.library',
                                    'replicates.library.biosample'])
def audit_experiment_biosample_term(value, system):
    '''
    The biosample term and id and type information should be present and
    concordent with library biosamples,
    Exception: RNA Bind-n-Seq
    '''
    if value['status'] in ['deleted', 'replaced']:
        return

    if value.get('assay_term_name') == 'RNA Bind-n-Seq':
        return

    ontology = system['registry']['ontology']
    term_id = value.get('biosample_term_id')
    term_type = value.get('biosample_type')
    term_name = value.get('biosample_term_name')

    if 'biosample_type' not in value:
        detail = '{} is missing biosample_type'.format(value['@id'])
        yield AuditFailure('missing biosample_type', detail, level='ERROR')

    if 'biosample_term_name' not in value:
        detail = '{} is missing biosample_term_name'.format(value['@id'])
        yield AuditFailure('missing biosample_term_name', detail, level='ERROR')
    # The type and term name should be put into dependancies

    if term_id is None:
        detail = '{} is missing biosample_term_id'.format(value['@id'])
        yield AuditFailure('missing biosample_term_id', detail, level='ERROR')
        return

    if term_id.startswith('NTR:'):
        detail = '{} has an NTR biosample {} - {}'.format(value['@id'], term_id, term_name)
        yield AuditFailure('NTR biosample', detail, level='DCC_ACTION')
    else:
        biosample_prefix = term_id.split(':')[0]
        if 'biosample_type' in value and \
           biosample_prefix not in biosampleType_ontologyPrefix[term_type]:
            detail = 'Experiment {} has '.format(value['@id']) + \
                     'a biosample of type {} '.format(term_type) + \
                     'with biosample_term_id {} '.format(value['biosample_term_id']) + \
                     'that is not one of ' + \
                     '{}'.format(biosampleType_ontologyPrefix[term_type])
            yield AuditFailure('experiment with biosample term-type mismatch', detail,
                               level='DCC_ACTION')

        elif term_id not in ontology:
            detail = '{} has term_id {} which is not in ontology'.format(value['@id'], term_id)
            yield AuditFailure('term_id not in ontology', term_id, level='DCC_ACTION')
        else:
            ontology_name = ontology[term_id]['name']
            if ontology_name != term_name and term_name not in ontology[term_id]['synonyms']:
                detail = '{} has a biosample mismatch {} - {} but ontology says {}'.format(
                    value['@id'],
                    term_id,
                    term_name,
                    ontology_name
                    )
                yield AuditFailure('mismatched biosample_term_name', detail, level='ERROR')

    if 'replicates' in value:
        for rep in value['replicates']:
            if 'library' not in rep:
                continue

            lib = rep['library']
            if 'biosample' not in lib:
                detail = '{} is missing biosample, expecting one of type {}'.format(
                    lib['@id'],
                    term_name
                    )
                yield AuditFailure('missing biosample', detail, level='ERROR')
                continue

            biosample = lib['biosample']
            bs_type = biosample.get('biosample_type')
            bs_name = biosample.get('biosample_term_name')
            bs_id = biosample.get('biosample_term_id')

            if bs_type != term_type:
                detail = 'Experiment {} '.format(value['@id']) + \
                         'contains a library {} '.format(lib['@id']) + \
                         'prepared from biosample type \"{}\", '.format(bs_type) + \
                         'while experiment\'s biosample type is \"{}\".'.format(term_type)
                yield AuditFailure('mismatched biosample_type', detail, level='ERROR')

            if bs_name != term_name:
                detail = 'Experiment {} '.format(value['@id']) + \
                         'contains a library {} '.format(lib['@id']) + \
                         'prepared from biosample {}, '.format(bs_name) + \
                         'while experiment\'s biosample is {}.'.format(term_name)
                yield AuditFailure('mismatched biosample_term_name', detail, level='ERROR')

            if bs_id != term_id:
                detail = 'Experiment {} '.format(value['@id']) + \
                         'contains a library {} '.format(lib['@id']) + \
                         'prepared from biosample with an id \"{}\", '.format(bs_id) + \
                         'while experiment\'s biosample id is \"{}\".'.format(term_id)
                yield AuditFailure('mismatched biosample_term_id', detail, level='ERROR')


@audit_checker(
    'experiment',
    frame=[
        'target',
        'replicates',
        'replicates.antibody',
        'replicates.antibody.targets',
        'replicates.antibody.lot_reviews'
        'replicates.antibody.lot_reviews.organisms',
        'replicates.library',
        'replicates.library.biosample',
        'replicates.library.biosample.organism',
    ],
    condition=rfa('ENCODE3', 'modERN'))
def audit_experiment_antibody_eligible(value, system):
    '''Check that biosample in the experiment is eligible for new data for the given antibody.'''

    if value['status'] in ['deleted', 'proposed', 'preliminary']:
        return

    if value.get('assay_term_name') not in targetBasedAssayList:
        return

    if 'target' not in value:
        return

    target = value['target']
    if 'control' in target['investigated_as']:
        return

    if value['assay_term_name'] in ['RNA Bind-n-Seq', 'shRNA knockdown followed by RNA-seq']:
        return

    for rep in value['replicates']:
        if 'antibody' not in rep:
            continue
        if 'library' not in rep:
            continue

        antibody = rep['antibody']
        lib = rep['library']

        if 'biosample' not in lib:
            continue

        biosample = lib['biosample']
        organism = biosample['organism']['@id']
        antibody_targets = antibody['targets']
        ab_targets_investigated_as = set()
        for t in antibody_targets:
            for i in t['investigated_as']:
                ab_targets_investigated_as.add(i)

        # We only want the audit raised if the organism in lot reviews matches that of the biosample
        # and if is not eligible for new data. Otherwise, it doesn't apply and we shouldn't raise a stink

        if 'histone modification' in ab_targets_investigated_as:
            for lot_review in antibody['lot_reviews']:
                if (lot_review['status'] == 'awaiting lab characterization'):
                    for lot_organism in lot_review['organisms']:
                        if organism == lot_organism:
                            detail = '{} is not eligible for {}'.format(antibody["@id"], organism)
                            yield AuditFailure('not eligible antibody',
                                               detail, level='NOT_COMPLIANT')
                if lot_review['status'] == 'eligible for new data (via exemption)':
                    for lot_organism in lot_review['organisms']:
                        if organism == lot_organism:
                            detail = '{} is eligible via exemption for {}'.format(antibody["@id"],
                                                                                  organism)
                            yield AuditFailure('antibody eligible via exemption',
                                               detail, level='WARNING')

        else:
            biosample_term_id = value['biosample_term_id']
            biosample_term_name = value['biosample_term_name']
            experiment_biosample = (biosample_term_id, organism)
            eligible_biosamples = set()
            exempt_biosamples = set()
            for lot_review in antibody['lot_reviews']:
                if lot_review['status'] in ['eligible for new data',
                                            'eligible for new data (via exemption)']:
                    for lot_organism in lot_review['organisms']:
                        eligible_biosample = (lot_review['biosample_term_id'], lot_organism)
                        if lot_review['status'] == 'eligible for new data (via exemption)':
                            exempt_biosamples.add(eligible_biosample)
                        eligible_biosamples.add(eligible_biosample)

            if experiment_biosample in exempt_biosamples:
                detail = '{} is eligible via exemption for {} in {}'.format(antibody["@id"],
                                                                            biosample_term_name,
                                                                            organism)
                yield AuditFailure('antibody eligible via exemption', detail, level='WARNING')

            if experiment_biosample not in eligible_biosamples:
                detail = '{} is not eligible for {} in {}'.format(antibody["@id"],
                                                                  biosample_term_name, organism)
                yield AuditFailure('not eligible antibody', detail, level='NOT_COMPLIANT')


@audit_checker(
    'experiment',
    frame=[
        'replicates',
        'replicates.library'])
def audit_experiment_library_biosample(value, system):
    if value['status'] in ['deleted', 'replaced']:
        return

    if value.get('assay_term_name') == 'RNA Bind-n-Seq':
        return
    for rep in value['replicates']:
        if 'library' not in rep:
            continue

        lib = rep['library']
        if 'biosample' not in lib:
            detail = '{} is missing biosample'.format(
                lib['@id'])
            yield AuditFailure('missing biosample', detail, level='ERROR')


@audit_checker(
    'experiment',
    frame=[
        'replicates',
        'replicates.library'])
def audit_library_RNA_size_range(value, system):
    '''
    An RNA library should have a size_range specified.
    This needs to accomodate the rfa
    '''
    if value['status'] in ['deleted', 'replaced']:
        return

    if value.get('assay_term_name') == 'transcription profiling by array assay':
        return

    if value['status'] in ['deleted']:
        return

    RNAs = ['SO:0000356', 'SO:0000871']

    for rep in value['replicates']:
        if 'library' not in rep:
            continue
        lib = rep['library']
        if (lib['nucleic_acid_term_id'] in RNAs) and ('size_range' not in lib):
            detail = 'RNA library {} requires a value for size_range'.format(rep['library']['@id'])
            raise AuditFailure('missing size_range', detail, level='NOT_COMPLIANT')
