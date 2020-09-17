from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)
from .gtex_data import gtexDonorsList
from .standards_data import pipelines_with_read_depth, minimal_read_depth_requirements


targetBasedAssayList = [
    'Mint-ChIP-seq',
    'ChIP-seq',
    'RNA Bind-n-Seq',
    'ChIA-PET',
    'RIP Array',
    'RIP-seq',
    'MeDIP-seq',
    'iCLIP',
    'eCLIP',
    'shRNA knockdown followed by RNA-seq',
    'siRNA knockdown followed by RNA-seq',
    'CRISPR genome editing followed by RNA-seq',
    'CRISPRi followed by RNA-seq',
    'PLAC-seq',
    'CUT&RUN',
    'CUT&Tag',
]

controlRequiredAssayList = [
    'Mint-ChIP-seq',
    'ChIP-seq',
    'RNA Bind-n-Seq',
    'RIP-seq',
    'RAMPAGE',
    'CAGE',
    'eCLIP',
    'single-cell RNA sequencing assay',
    'shRNA knockdown followed by RNA-seq',
    'siRNA knockdown followed by RNA-seq',
    'CRISPR genome editing followed by RNA-seq',
    'CRISPRi followed by RNA-seq'
]

seq_assays = [
    'RNA-seq',
    'polyA plus RNA-seq',
    'polyA minus RNA-seq',
    'Mint-ChIP-seq',
    'ChIP-seq',
    'RNA Bind-n-Seq',
    'MeDIP-seq',
    'RNA-PET',
    'DNA-PET',
    'ChIA-PET',
    'CAGE',
    'RAMPAGE',
    'RIP-seq',
    'PLAC-seq',
    'microRNA-seq',
    'long read RNA-seq',
    'small RNA-seq',
    'ATAC-seq',
    'CUT&RUN',
    'CUT&Tag',
]


def audit_hic_restriction_enzyme_in_libaries(value, system, excluded_types):
    '''
    Libraries for HiC experiments should use the same restriction enzymes
    '''
    if value['assay_term_name'] != 'HiC':
        return
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return
    if 'replicates' not in value:
        return
    
    
    fragmentation_methods_for_experiment = set()
    fragmentation_methods_by_library = {}

    for replicate in value['replicates']:
        library = replicate.get('library', {})
        replicate_status = replicate.get('status')
        library_status = library.get('status')
        missing_fragmentation_audit_conditions = [
            library,
            replicate_status,
            library_status,
            replicate_status not in excluded_types,
            library_status not in excluded_types,
        ]
        if all(missing_fragmentation_audit_conditions):
            library_fragmentation_methods = library.get('fragmentation_methods')
            library_id = library.get('@id')
            if library_fragmentation_methods and library_id:
                fragmentation_methods_by_library[library_id] = set(library_fragmentation_methods)
                fragmentation_methods_for_experiment.update(library_fragmentation_methods)
            else:
                detail = ('Experiment {} contains a library {} '
                    'lacking the specification of the fragmentation '
                    'method used to generate it.'.format(
                        audit_link(path_to_text(value['@id']), value['@id']),
                        audit_link(path_to_text(library_id), library_id)
                    )
                )
                yield AuditFailure('missing fragmentation method', detail, level='WARNING')

    for library_id, library_fragmentation_methods in fragmentation_methods_by_library.items():
        if len(fragmentation_methods_for_experiment) - len(library_fragmentation_methods) != 0:
            detail = ('Experiment {} contains library {} generated using {} '
                'fragmentation methods, which are inconsistent with '
                'fragmentation methods {} used for other libraries.'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    audit_link(path_to_text(library_id), library_id),
                    sorted(list(library_fragmentation_methods)),
                    sorted(list(fragmentation_methods_for_experiment))
                )
            )
            yield AuditFailure('inconsistent fragmentation method', detail, level='ERROR')       


def audit_experiment_chipseq_control_read_depth(value, system, files_structure):
    # relevant only for ChIP-seq and MINT
    if value.get('assay_term_id') not in ['OBI:0000716', 'OBI:0002160']:
        return

    if value.get('target') and 'name' in value.get('target'):
        target_name = value['target']['name']
        target_investigated_as = value['target']['investigated_as']
    elif value.get('control_type'):
        if get_organism_name(
            reps=value['replicates'], excluded_types=[]
        ) in ['human', 'mouse']:
            return
        target_name = value.get('control_type')
        target_investigated_as = [value.get('control_type')]
    else:
        return
    controls = value.get('possible_controls')
    if controls:
        controls_files_structures = {}
        control_objects = {}
        for control_experiment in controls:
            control_objects[control_experiment.get('@id')] = control_experiment
            controls_files_structures[control_experiment.get('@id')] = create_files_mapping(
                control_experiment.get('original_files'),
                files_structure.get('excluded_types'))
        awards_to_be_checked = [
                        'ENCODE3',
                        'ENCODE4',
                        'ENCODE2-Mouse',
                        'ENCODE2',
                        'ENCODE',
                        'Roadmap']
        peaks_file_gen = (
            peaks_file for peaks_file in files_structure.get('peaks_files').values()
            if  (peaks_file.get('award') and
                peaks_file.get('award')['rfa'] in awards_to_be_checked and
                peaks_file.get('lab') in ['/labs/encode-processing-pipeline/'] and
                peaks_file.get('biological_replicates') and
                len(peaks_file.get('biological_replicates')) == 1)
        )

        pipelines_to_check = ['ChIP-seq read mapping', 
                                'Pool and subsample alignments', 
                                'Histone ChIP-seq 2',
                                'Histone ChIP-seq 2 (unreplicated)',
                                'Transcription factor ChIP-seq 2',
                                'Transcription factor ChIP-seq 2 (unreplicated)']
        analysis_steps_to_check = ['Alignment pooling and subsampling step',
                                   'Control alignment subsampling step',
                                   'ChIP seq alignment step']
        for peaks_file in peaks_file_gen:
            derived_from_files = get_derived_from_files_set([peaks_file],
                                                            files_structure,
                                                            'bam',
                                                            True)
            derived_from_external_bams_gen = (
                derived_from for derived_from in
                derived_from_files
                if (derived_from.get('dataset') != value.get('@id')
                    and
                    derived_from.get('dataset') in controls_files_structures
                    and
                    (check_for_any_pipelines(
                        pipelines_to_check,
                        derived_from.get('@id'),
                        controls_files_structures[derived_from.get('dataset')])
                        or
                        check_for_analysis_steps(
                            analysis_steps_to_check,
                            derived_from.get('@id'),
                            controls_files_structures[derived_from.get('dataset')]))))
            control_bam_details = []
            cumulative_read_depth = 0
            missing_control_quality_metric = False
            target_failures = False
            for bam_file in derived_from_external_bams_gen:
                failures = check_control_target_failures(bam_file.get('dataset'),
                    control_objects, bam_file['@id'],
                    bam_file['output_type'])
                if failures:
                    target_failures = True
                    for f in failures:
                        yield f
                else:
                    control_depth = get_chip_seq_bam_read_depth(bam_file)
                    if not control_depth:
                        detail = ('Control {} file {} has no associated quality metric, '
                            'preventing calculation of the read depth.'.format(
                                bam_file['output_type'],
                                audit_link(path_to_text(bam_file['@id']), bam_file['@id'])
                            )
                        )
                        yield AuditFailure('missing control quality metric', detail, level='WARNING')
                        missing_control_quality_metric = True
                    else:
                        cumulative_read_depth += control_depth
                        control_bam_details.append(
                            (bam_file.get('@id'), control_depth, bam_file.get('dataset')))
            if not missing_control_quality_metric and not target_failures:
                yield from check_control_read_depth_standards(
                    peaks_file.get('@id'),
                    peaks_file.get('assembly'),
                    cumulative_read_depth,
                    control_bam_details,
                    target_name,
                    target_investigated_as)


def check_control_target_failures(control_id, control_objects, bam_id, bam_type):
    control = control_objects.get(control_id)
    if not control:
        return
    target_failures = []
    if not control.get('control_type'):
        detail = 'Control {} file {} has no control_type specified.'.format(
            bam_type,
            audit_link(path_to_text(bam_id), bam_id)
        )
        target_failures.append(
            AuditFailure(
                'missing control_type of control experiment',
                detail,
                level='WARNING'
            )
        )
    elif (
        ('input library' not in control['control_type'])
        and ('wild type' not in control['control_type'])
    ):
        detail = (
            'Control {} file {} has a wrong control type {} '
            'which is not "input library" or "wild type".'
        ).format(
            bam_type,
            audit_link(path_to_text(bam_id), bam_id),
            control['control_type']
        )
        target_failures.append(
            AuditFailure(
                'improper control_type of control experiment',
                detail,
                level='WARNING'
            )
        )
    if 'target' in control and control['target']:
        if isinstance(control['target'], list):
            target_name = ', '.join(t['name'] for t in control['target'])
        else:
            target_name = control['target']['name']
        detail = (
            'Control {} file {} has unexpected target {} specified.'
        ).format(
            bam_type,
            audit_link(path_to_text(bam_id), bam_id),
            target_name
        )
        target_failures.append(
            AuditFailure(
                'unexpected target of control experiment',
                detail,
                level='WARNING'
            )
        )
    return target_failures


def check_for_any_pipelines(pipeline_titles, control_file_id, file_structure):
    for pipeline_title in pipeline_titles:
        if check_pipeline(pipeline_title, control_file_id, file_structure):
            return True
    return False


def check_for_analysis_steps(analysis_step_titles, control_file_id, file_structure):
    for analysis_step_title in analysis_step_titles:
        if check_analysis_step(analysis_step_title, control_file_id, file_structure):
            return True
    return False


def check_analysis_step(analysis_step_title, control_file_id, file_structure):
    control_file = file_structure.get('alignments')[control_file_id]
    if ('analysis_step_version' in control_file and
            'analysis_step' in control_file.get('analysis_step_version')):
        title = control_file.get('analysis_step_version').get('analysis_step').get('title')
        return analysis_step_title == title
    return False


def check_pipeline(pipeline_title, control_file_id, file_structure):
    control_file = file_structure.get('alignments')[control_file_id]
    if ('analysis_step_version' in control_file and
            'analysis_step' in control_file.get('analysis_step_version')):
        pipelines = control_file.get('analysis_step_version').get('analysis_step').get('pipelines')
        return pipeline_title in get_pipeline_titles(pipelines)
    return False


def generate_control_bam_details_string(control_bam_details):
    to_return = ''
    for (file_id, depth, exp_id) in control_bam_details:
        to_return += ('file {} from control experiment {} has {} usable fragments;'.format(
            audit_link(path_to_text(file_id), file_id),
            audit_link(path_to_text(exp_id), exp_id),
            depth
            )
        )
    return to_return[:-1]


def check_control_read_depth_standards(peaks_file_id,
                                       assembly,
                                       read_depth,
                                       control_bam_details,
                                       control_to_target,
                                       target_investigated_as):
    marks = pipelines_with_read_depth['ChIP-seq read mapping']
    if control_to_target == 'empty':
        return

    if not control_bam_details:
        detail = ('The peaks file {} produced by ENCODE uniformly processing '
            'ChIP-seq pipeline has no valid control alignments specified.'.format(
                audit_link(path_to_text(peaks_file_id), peaks_file_id)
            )
        )
        yield AuditFailure('missing control alignments', detail, level='ERROR')
        return
    control_details = generate_control_bam_details_string(control_bam_details)
    if assembly:
        prefix = ('Control alignment files ({}) '
                  'mapped to {} assembly have in aggregate {} '
                  'usable fragments. ').format(
                      control_details,
                      assembly,
                      read_depth)
    else:
        prefix = ('Control alignment files ({}) '
            'have in aggregate {} usable fragments. ').format(
                control_details,
                read_depth)
    detail = ('{} The minimum ENCODE standard for a control of ChIP-seq assays '
        'targeting {} {} is {} million usable fragments, '
        'the recommended number of usable fragments is > {} million. '
        '(See {} )')
    if 'broad histone mark' in target_investigated_as:
        detail = (detail.format(
            prefix,
            'broad histone mark',
            control_to_target,
            35,
            45,
            audit_link('ENCODE ChIP-seq data standards', '/data-standards/chip-seq/')
            )
        )
        if read_depth >= marks['broad']['minimal'] and read_depth < marks['broad']['recommended']:
                yield AuditFailure('control low read depth', detail, level='WARNING')
        elif read_depth >= marks['broad']['low'] and read_depth < marks['broad']['minimal']:
            yield AuditFailure('control insufficient read depth', detail, level='NOT_COMPLIANT')
        elif read_depth < marks['broad']['low']:
            yield AuditFailure('control extremely low read depth', detail, level='ERROR')
    elif 'narrow histone mark' in target_investigated_as:
        detail = (detail.format(
            prefix,
            'narrow histone mark',
            control_to_target,
            10,
            20,
            audit_link('ENCODE ChIP-seq data standards', '/data-standards/chip-seq/')
            )
        )
        if read_depth >= marks['narrow']['minimal'] and read_depth < marks['narrow']['recommended']:
            yield AuditFailure('control low read depth', detail, level='WARNING')
        elif read_depth >= marks['narrow']['low'] and read_depth < marks['narrow']['minimal']:
            yield AuditFailure('control insufficient read depth', detail, level='NOT_COMPLIANT')
        elif read_depth < marks['narrow']['low']:
            yield AuditFailure('control extremely low read depth', detail, level='ERROR')
    else:
        detail = (detail.format(
            prefix,
            control_to_target,
            'and investigated as a transcription factor',
            10,
            20,
            audit_link('ENCODE ChIP-seq data standards', '/data-standards/chip-seq/')
            )
        )
        if read_depth >= marks['TF']['minimal'] and read_depth < marks['TF']['recommended']:
            yield AuditFailure('control low read depth', detail, level='WARNING')
        elif read_depth >= marks['TF']['low'] and read_depth < marks['TF']['minimal']:
            yield AuditFailure('control insufficient read depth', detail, level='NOT_COMPLIANT')
        elif read_depth < marks['TF']['low']:
            yield AuditFailure('control extremely low read depth', detail, level='ERROR')


def audit_experiment_mixed_libraries(value, system, excluded_types):
    '''
    Experiments should not have mixed libraries nucleic acids
    '''
    if value['status'] in ['deleted', 'replaced']:
        return

    if 'replicates' not in value:
        return

    nucleic_acids = set()

    for rep in value['replicates']:
        if rep.get('status') not in excluded_types and \
           'library' in rep and rep['library'].get('status') not in excluded_types:
            if 'nucleic_acid_term_name' in rep['library']:
                nucleic_acids.add(rep['library']['nucleic_acid_term_name'])

    if len(nucleic_acids) > 1:
        detail = ('Experiment {} '
            'contains libraries with mixed nucleic acids {} '.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                nucleic_acids
            )
        )
        yield AuditFailure('mixed libraries', detail, level='INTERNAL_ACTION')
    return


def audit_experiment_pipeline_assay_details(value, system, files_structure):
    for pipeline in get_pipeline_objects(files_structure.get('original_files').values()):
        pipeline_assays = pipeline.get('assay_term_names')
        if not pipeline_assays or value.get('assay_term_name') not in pipeline_assays:
            detail = ('This experiment '
                'contains file(s) associated with '
                'pipeline {} which assay_term_names list '
                'does not include experiments\'s assay_term_name.'.format(
                    audit_link(path_to_text(pipeline['@id']), pipeline['@id'])
                )
            )
            yield AuditFailure('inconsistent assay_term_name', detail, level='INTERNAL_ACTION')
    return


# def audit_experiment_missing_processed_files(value, system): removed from v54


def audit_experiment_missing_unfiltered_bams(value, system, files_structure):
    if value.get('assay_term_id') not in ['OBI:0000716', 'OBI:0002160']:  # not a ChIP-seq
        return

    # if there are no bam files - we don't know what pipeline, exit
    if len(files_structure.get('alignments').values()) == 0:
        return
    pipeline_title = ['ChIP-seq read mapping',
                        'Histone ChIP-seq 2',
                        'Histone ChIP-seq 2 (unreplicated)',
                        'Transcription factor ChIP-seq 2',
                        'Transcription factor ChIP-seq 2 (unreplicated)']                    
    for pipeline in pipeline_title:
        if pipeline in get_pipeline_titles(
                get_pipeline_objects(files_structure.get('alignments').values())):
            for filtered_file in files_structure.get('alignments').values():
                if has_only_raw_files_in_derived_from(filtered_file, files_structure) and \
                   filtered_file.get('lab') == '/labs/encode-processing-pipeline/' and \
                   has_no_unfiltered(filtered_file,
                                     files_structure.get('unfiltered_alignments').values()):
                    detail = ('Experiment {} contains biological replicate '
                        '{} with a filtered {} file {}, mapped to '
                        'a {} assembly, but has no unfiltered '
                        '{} file.'.format(
                            audit_link(path_to_text(value['@id']), value['@id']),
                            filtered_file['biological_replicates'],
                            filtered_file['output_type'],
                            audit_link(path_to_text(filtered_file['@id']), filtered_file['@id']),
                            filtered_file['assembly'],
                            filtered_file['output_type']
                        )
                    ) 
                    yield AuditFailure('missing unfiltered alignments', detail, level='INTERNAL_ACTION')
    return


def audit_experiment_out_of_date_analysis(value, system, files_structure):
    valid_assay_term_names = [
        'ChIP-seq',
        'Mint-ChIP-seq',
        'DNase-seq',
        'genetic modification followed by DNase-seq',
    ]
    assay_name = value['assay_term_name']
    if assay_name not in valid_assay_term_names:
        return

    if len(files_structure.get('alignments').values()) == 0 and \
       len(files_structure.get('unfiltered_alignments').values()) == 0 and \
       len(files_structure.get('transcriptome_alignments').values()) == 0:
        return  # probably needs pipeline, since there are no processed files

    file_types = ['alignments', 'unfiltered_alignments',
                  'transcriptome_alignments']
    for file_type in file_types:
        for bam_file in files_structure.get(file_type).values():
            if bam_file.get('lab') == '/labs/encode-processing-pipeline/' and bam_file.get('derived_from'):  
                if is_outdated_bams_replicate(bam_file, files_structure, assay_name):
                    assembly_detail = ' '
                    if bam_file.get('assembly'):
                        assembly_detail = ' for {} assembly '.format(
                            bam_file['assembly'])
                    detail = ('Experiment {} '
                        '{} file {} mapped to {}'
                        'is out of date.'.format(
                            audit_link(path_to_text(value['@id']), value['@id']),
                            bam_file['output_type'],
                            audit_link(path_to_text(bam_file['@id']), bam_file['@id']),
                            assembly_detail
                        )
                    )
                    yield AuditFailure('out of date analysis', detail, level='INTERNAL_ACTION')
    return


def audit_experiment_standards_dispatcher(value, system, files_structure):
    if not check_award_condition(value, ['ENCODE4',
                                         'ENCODE3',
                                         'ENCODE2-Mouse',
                                         'ENCODE2',
                                         'ENCODE',
                                         'Roadmap']):
        return
    '''
    Dispatcher function that will redirect to other functions that would
    deal with specific assay types standards
    '''
    if value.get('status') in ['revoked', 'deleted', 'replaced']:
        return
    if value.get('assay_term_name') not in [
        'DNase-seq',
        'RAMPAGE',
        'RNA-seq',
        'polyA plus RNA-seq',
        'polyA minus RNA-seq',
        'ChIP-seq',
        'Mint-ChIP-seq',
        'CAGE',
        'shRNA knockdown followed by RNA-seq',
        'siRNA knockdown followed by RNA-seq',
        'CRISPRi followed by RNA-seq',
        'CRISPR genome editing followed by RNA-seq',
        'single-cell RNA sequencing assay',
        'whole-genome shotgun bisulfite sequencing',
        'genetic modification followed by DNase-seq',
        'microRNA-seq',
        'long read RNA-seq',
        'small RNA-seq',
        'icSHAPE',
        'ATAC-seq'
    ]:
        return
    if not value.get('original_files'):
        return
    if 'replicates' not in value:
        return

    num_bio_reps = set()
    for rep in value['replicates']:
        num_bio_reps.add(rep['biological_replicate_number'])

    if len(num_bio_reps) < 1:
        return

    organism_name = get_organism_name(
        value['replicates'], files_structure.get('excluded_types'))  # human/mouse
    if organism_name == 'human':
        desired_assembly = 'GRCh38'
        desired_annotation = ['V24', 'V29']
    else:
        if organism_name == 'mouse':
            desired_assembly = 'mm10'
            desired_annotation = ['M4', 'M21']
        else:
            return

    standards_version = 'ENC3'

    if value['assay_term_name'] in ['DNase-seq', 'genetic modification followed by DNase-seq']:

        yield from check_experiment_dnase_seq_standards(
            value,
            files_structure,
            desired_assembly,
            desired_annotation,
            '/data-standards/dnase-seq/')
        return

    if value['assay_term_name'] in ['RAMPAGE', 'RNA-seq', 'polyA minus RNA-seq', 'polyA plus RNA-seq', 'CAGE',
                                    'shRNA knockdown followed by RNA-seq',
                                    'siRNA knockdown followed by RNA-seq',
                                    'CRISPRi followed by RNA-seq',
                                    'CRISPR genome editing followed by RNA-seq',
                                    'single-cell RNA sequencing assay',
                                    'microRNA-seq', 'small RNA-seq',
                                    'icSHAPE', 'long read RNA-seq']:
        yield from check_experiment_rna_seq_standards(
            value,
            files_structure,
            desired_assembly,
            desired_annotation,
            standards_version)
        return

    if value['assay_term_name'] in ['ChIP-seq', 'Mint-ChIP-seq']:
        yield from check_experiment_chip_seq_standards(
            value,
            files_structure,
            standards_version)

    if standards_version == 'ENC3' and \
            value['assay_term_name'] == 'whole-genome shotgun bisulfite sequencing':

        yield from check_experiment_wgbs_encode3_standards(
            value,
            files_structure,
            organism_name,
            desired_assembly)
        return

    if value['assay_term_name'] == 'ATAC-seq':
        yield from check_experiment_atac_encode4_qc_standards(
            value,
            files_structure)
        return


def audit_modERN_experiment_standards_dispatcher(value, system, files_structure):

    if not check_award_condition(value, ['modERN']):
        return
    '''
    Dispatcher function that will redirect to other functions that would
    deal with specific assay types standards. This version is for the modERN project
    '''

    if value['status'] in ['revoked', 'deleted', 'replaced']:
        return
    if value.get('assay_term_name') != 'ChIP-seq':
        return
    if not files_structure.get('original_files').values():
        return
    if 'replicates' not in value:
        return

    yield from check_experiment_chip_seq_standards(value,
                                                   files_structure,
                                                   'modERN')
    return


def check_experiment_dnase_seq_standards(experiment,
                                         files_structure,
                                         desired_assembly,
                                         desired_annotation,
                                         link_to_standards):
    fastq_files = files_structure.get('fastq_files').values()
    alignment_files = files_structure.get('alignments').values()
    signal_files = files_structure.get('signal_files').values()
    assay_term_name = experiment['assay_term_name']

    pipeline_title = scanFilesForPipelineTitle_not_chipseq(
        alignment_files,
        ['GRCh38', 'mm10'],
        ['DNase-HS pipeline single-end - Version 2',
         'DNase-HS pipeline paired-end - Version 2'])
    if pipeline_title is False:
        return
    for f in fastq_files:
        yield from check_file_read_length_rna(
            f, 36,
            pipeline_title,
            link_to_standards)

    pipelines = get_pipeline_objects(alignment_files)

    if pipelines is not None and len(pipelines) > 0:
        samtools_flagstat_metrics = get_metrics(alignment_files,
                                                'SamtoolsFlagstatsQualityMetric',
                                                desired_assembly)

        if samtools_flagstat_metrics is not None and \
                len(samtools_flagstat_metrics) > 0:
            for metric in samtools_flagstat_metrics:
                if 'mapped' in metric and 'quality_metric_of' in metric:
                    alignment_file = files_structure.get(
                        'alignments')[metric['quality_metric_of'][0]]
                    suffix = ('According to ENCODE standards, conventional '
                        'DNase-seq profile requires a minimum of 20 million uniquely mapped '
                        'reads to generate a reliable '
                        'SPOT (Signal Portion of Tags) score. '
                        'The recommended value is > 50 million. For deep, foot-printing depth '
                        'DNase-seq 150-200 million uniquely mapped reads are '
                        'recommended. (See {} )'.format(
                            audit_link('ENCODE DNase-seq data standards', link_to_standards)
                        )
                    )
                    if 'assembly' in alignment_file:
                        detail = ('Alignment file {} produced by {} ( {} ) '
                            'for {} assembly has {} mapped reads. {}'.format(
                                audit_link(path_to_text(alignment_file['@id']), alignment_file['@id']),
                                pipelines[0]['title'],
                                audit_link(path_to_text(pipelines[0]['@id']), pipelines[0]['@id']),
                                alignment_file['assembly'],
                                metric['mapped'],
                                suffix
                            )
                        )
                    else:
                        detail = ('Alignment file {} produced by {} ( {} ) '
                            'has {} mapped reads. {}'.format(
                                audit_link(path_to_text(alignment_file['@id']), alignment_file['@id']),
                                pipelines[0]['title'],
                                audit_link(path_to_text(pipelines[0]['@id']), pipelines[0]['@id']),
                                metric['mapped'],
                                suffix
                            )
                        )
                    if 20000000 <= metric['mapped'] < 50000000:
                        yield AuditFailure('low read depth', detail, level='WARNING')
                    elif metric['mapped'] < 20000000:
                        yield AuditFailure('extremely low read depth', detail, level='ERROR')
        elif alignment_files is not None and len(alignment_files) > 0 and \
                (samtools_flagstat_metrics is None or
                 len(samtools_flagstat_metrics) == 0):
            file_list = []
            for f in alignment_files:
                file_list.append(f['@id'])
            file_names_links = [audit_link(path_to_text(file), file) for file in file_list]
            detail = ('Alignment files ( {} ) produced by {} '
                '( {} ) lack read depth information.'.format(
                    ', '.join(file_names_links),
                    pipelines[0]['title'],
                    audit_link(path_to_text(pipelines[0]['@id']), pipelines[0]['@id'])
                )
            )
            yield AuditFailure('missing read depth', detail, level='INTERNAL_ACTION')

        alignments_assemblies = {}
        for alignment_file in alignment_files:
            if 'assembly' in alignment_file:
                alignments_assemblies[alignment_file['accession']
                                      ] = alignment_file['assembly']

        # duplication rate audit was removed from v54

        signal_assemblies = {}
        for signal_file in signal_files:
            if 'assembly' in signal_file:
                signal_assemblies[signal_file['accession']
                                  ] = signal_file['assembly']

        hotspot_quality_metrics = get_metrics(alignment_files,
                                              'HotspotQualityMetric',
                                              desired_assembly)
        if hotspot_quality_metrics is not None and \
           len(hotspot_quality_metrics) > 0:
            for metric in hotspot_quality_metrics:
                if "spot1_score" in metric:
                    file_names = []
                    file_list = []
                    for f in metric['quality_metric_of']:
                        file_names.append(f.split('/')[2])
                        file_list.append(f)
                    file_names_string = str(file_names).replace('\'', ' ')
                    file_names_links = [audit_link(path_to_text(file), file) for file in file_list]
                    detail = ("Signal Portion of Tags (SPOT) is a measure of enrichment, "
                        "analogous to the commonly used fraction of reads in peaks metric. "
                        "ENCODE processed alignment files {} produced by {} "
                        "( {} ) {}"
                        " have a SPOT1 score of {:.2f}. "
                        "According to ENCODE standards, "
                        "SPOT1 score of 0.4 or higher is considered a product of high quality "
                        "data. "
                        "Any sample with a SPOT1 score <0.3 should be targeted for replacement "
                        "with a higher quality sample, and a "
                        "SPOT1 score of 0.25 is considered minimally acceptable "
                        "SPOT1 score of 0.25 is considered minimally acceptable "
                        "for rare and hard to find primary tissues. (See {} )".format(
                            ', '.join(file_names_links),
                            pipelines[0]['title'],
                            audit_link(path_to_text(pipelines[0]['@id']), pipelines[0]['@id']),
                            assemblies_detail(extract_assemblies(alignments_assemblies, file_names)),
                            metric["spot1_score"],
                            audit_link('ENCODE DNase-seq data standards', link_to_standards)
                        )
                    )

                    if 0.25 <= metric["spot1_score"] < 0.4:
                        yield AuditFailure('low spot score', detail, level='WARNING')
                    elif metric["spot1_score"] < 0.25:
                        yield AuditFailure('extremely low spot score', detail, level='ERROR')

        if 'replication_type' not in experiment or experiment['replication_type'] == 'unreplicated':
            return

        signal_quality_metrics = get_metrics(signal_files,
                                             'CorrelationQualityMetric',
                                             desired_assembly)
        if signal_quality_metrics is not None and \
           len(signal_quality_metrics) > 0:
            threshold = 0.9
            if experiment['replication_type'] == 'anisogenic':
                threshold = 0.85
            for metric in signal_quality_metrics:
                if 'Pearson correlation' in metric:
                    file_names = []
                    file_list = []
                    for f in metric['quality_metric_of']:
                        file_names.append(f.split('/')[2])
                        file_list.append(f)
                    file_names_string = str(file_names).replace('\'', ' ')
                    file_names_links = [audit_link(path_to_text(file), file) for file in file_list]
                    detail = ('Replicate concordance in DNase-seq experiments is measured by '
                        'calculating the Pearson correlation between signal quantification '
                        'of the replicates. '
                        'ENCODE processed signal files {} produced by {} ( {} ) {} '
                        'have a Pearson correlation of {:.2f}. '
                        'According to ENCODE standards, in an {} '
                        'assay a Pearson correlation value > {} '
                        'is recommended. (See {} )'.format(
                            ', '.join(file_names_links),
                            pipelines[0]['title'],
                            audit_link(path_to_text(pipelines[0]['@id']), pipelines[0]['@id']),
                            assemblies_detail(extract_assemblies(signal_assemblies, file_names)),
                            metric['Pearson correlation'],
                            experiment['replication_type'],
                            threshold,
                            audit_link('ENCODE DNase-seq data standards', link_to_standards)
                        )
                    )

                    if metric['Pearson correlation'] < threshold:
                        yield AuditFailure('insufficient replicate concordance',
                                           detail, level='NOT_COMPLIANT')
    return


def check_experiment_rna_seq_standards(value,
                                       files_structure,
                                       desired_assembly,
                                       desired_annotation,
                                       standards_version):

    fastq_files = files_structure.get('fastq_files').values()
    alignment_files = files_structure.get('alignments').values()
    unfiltered_alignment_files = files_structure.get('unfiltered_alignments').values()
    merged_files_list = list(alignment_files) + list(unfiltered_alignment_files)
    gene_quantifications = files_structure.get(
        'gene_quantifications_files').values()
    transcript_quantifications = files_structure.get(
        'transcript_quantifications_files').values()
    microRNA_quantifications = files_structure.get(
        'microRNA_quantifications_files').values()
    assay_term_name = value['assay_term_name']

    pipeline_title = scanFilesForPipelineTitle_not_chipseq(
        merged_files_list,
        ['GRCh38', 'mm10'],
        ['RNA-seq of long RNAs (paired-end, stranded)',
         'RNA-seq of long RNAs (single-end, unstranded)',
         'Small RNA-seq single-end pipeline',
         'RAMPAGE (paired-end, stranded)',
         'microRNA-seq pipeline',
         'Long read RNA-seq pipeline',
         'Bulk RNA-seq'])
    if pipeline_title is False:
        return

    standards_links = {
        'RNA-seq of long RNAs (paired-end, stranded)': '/data-standards/rna-seq/long-rnas/',
        'RNA-seq of long RNAs (single-end, unstranded)': '/data-standards/rna-seq/long-rnas/',
        'Small RNA-seq single-end pipeline': '/data-standards/rna-seq/small-rnas/',
        'RAMPAGE (paired-end, stranded)': '/data-standards/rampage/',
        'microRNA-seq pipeline': '/microrna/microrna-seq/',
        'Long read RNA-seq pipeline': '/data-standards/long-read-rna-pipeline/',
        'Bulk RNA-seq': '/data-standards/rna-seq/long-rnas/',
    }

    for f in fastq_files:
        if pipeline_title not in ['Long read RNA-seq pipeline', 'microRNA-seq pipeline']:
            yield from check_file_read_length_rna(f, 50,
                                                  pipeline_title,
                                                  standards_links[pipeline_title])
        yield from check_file_platform(f, ['OBI:0002024', 'OBI:0000696'])

    if pipeline_title in ['RNA-seq of long RNAs (paired-end, stranded)',
                          'RNA-seq of long RNAs (single-end, unstranded)',
                          'Small RNA-seq single-end pipeline',
                          'RAMPAGE (paired-end, stranded)',
                          'Bulk RNA-seq']:
        star_metrics = get_metrics(alignment_files,
                                   'StarQualityMetric',
                                   desired_assembly)

        if len(star_metrics) < 1:
            detail = ('ENCODE experiment {} of {} assay'
                ', processed by {} pipeline has no read depth'
                ' containing quality metric associated with it.'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    assay_term_name,
                    pipeline_title
                )
            )
            yield AuditFailure('missing read depth', detail, level='INTERNAL_ACTION')

    alignment_files = get_non_tophat_alignment_files(alignment_files)

    if pipeline_title in ['RAMPAGE (paired-end, stranded)']:
        upper_limit = 20000000
        medium_limit = 10000000
        lower_limit = 1000000
        yield from check_experiment_cage_rampage_standards(
            value,
            fastq_files,
            alignment_files,
            pipeline_title,
            gene_quantifications,
            desired_assembly,
            desired_annotation,
            upper_limit,
            medium_limit,
            lower_limit,
            standards_version,
            standards_links[pipeline_title])
    elif pipeline_title in ['Small RNA-seq single-end pipeline']:
        upper_limit = 30000000
        medium_limit = 20000000
        lower_limit = 1000000
        yield from check_experiment_small_rna_standards(
            value,
            fastq_files,
            alignment_files,
            pipeline_title,
            gene_quantifications,
            desired_assembly,
            desired_annotation,
            upper_limit,
            medium_limit,
            lower_limit,
            standards_links[pipeline_title])

    elif pipeline_title in ['RNA-seq of long RNAs (paired-end, stranded)',
                            'RNA-seq of long RNAs (single-end, unstranded)',
                            'Bulk RNA-seq']:
        upper_limit = 30000000
        medium_limit = 20000000
        lower_limit = 1000000
        yield from check_experiment_long_rna_standards(
            value,
            fastq_files,
            alignment_files,
            pipeline_title,
            gene_quantifications,
            desired_assembly,
            desired_annotation,
            upper_limit,
            medium_limit,
            lower_limit,
            standards_links[pipeline_title])
    elif pipeline_title == 'microRNA-seq pipeline':
        yield from check_experiment_micro_rna_standards(
            value,
            fastq_files,
            alignment_files,
            pipeline_title,
            microRNA_quantifications,
            desired_assembly,
            desired_annotation,
            standards_links[pipeline_title],
            upper_limit_reads_mapped=5000000,
            lower_limit_reads_mapped=3000000,
            upper_limit_spearman=0.85,
            lower_limit_spearman=0.8,
            upper_limit_expressed_mirnas=300,
            lower_limit_expressed_mirnas=200,
        )
    elif pipeline_title == 'Long read RNA-seq pipeline':
        yield from check_experiment_long_read_rna_standards(
            value,
            unfiltered_alignment_files,
            transcript_quantifications,
            desired_assembly,
            desired_annotation,
            upper_limit_flnc=600000,
            lower_limit_flnc=400000,
            upper_limit_mapping_rate=0.9,
            lower_limit_mapping_rate=0.6,
            upper_limit_spearman=0.8,
            lower_limit_spearman=0.6,
            upper_limit_genes_detected=8000,
            lower_limit_genes_detected=4000,
        )
    return

def check_experiment_wgbs_encode3_standards(experiment,
                                            files_structure,
                                            organism_name,
                                            desired_assembly):

    alignment_files = files_structure.get('alignments').values()
    fastq_files = files_structure.get('fastq_files').values()
    cpg_quantifications = files_structure.get('cpg_quantifications').values()

    if fastq_files == []:
        return

    yield from check_wgbs_read_lengths(fastq_files, organism_name, 130, 100)

    read_lengths = get_read_lengths_wgbs(fastq_files)

    pipeline_title = scanFilesForPipelineTitle_not_chipseq(alignment_files,
                                                           ['GRCh38', 'mm10'],
                                                           ['WGBS single-end pipeline - version 2',
                                                            'WGBS single-end pipeline',
                                                            'WGBS paired-end pipeline'])

    if pipeline_title is False:
        return

    if 'replication_type' not in experiment or experiment['replication_type'] == 'unreplicated':
        return

    bismark_metrics = get_metrics(
        cpg_quantifications, 'BismarkQualityMetric', desired_assembly)
    cpg_metrics = get_metrics(
        cpg_quantifications, 'CpgCorrelationQualityMetric', desired_assembly)

    samtools_metrics = get_metrics(cpg_quantifications,
                                   'SamtoolsFlagstatsQualityMetric',
                                   desired_assembly)

    yield from check_wgbs_coverage(
        samtools_metrics,
        pipeline_title,
        min(read_lengths),
        organism_name,
        get_pipeline_objects(alignment_files))

    yield from check_wgbs_pearson(cpg_metrics, 0.8, pipeline_title)

    yield from check_wgbs_lambda(bismark_metrics, 1, pipeline_title)

    return


def check_wgbs_read_lengths(fastq_files,
                            organism_name,
                            human_threshold,
                            mouse_threshold):
    for f in fastq_files:
        if 'read_length' in f:
            l = f['read_length']
            if organism_name == 'mouse' and l < 100:
                detail = ('Fastq file {} '
                    'has read length of {}bp, while '
                    'the recommended read length for {} '
                    'data is > 100bp.'.format(
                        audit_link(path_to_text(f['@id']), f['@id']),
                        l,
                        organism_name
                    )
                )
                yield AuditFailure('insufficient read length',
                                   detail, level='NOT_COMPLIANT')
            elif organism_name == 'human' and l < 100:
                detail = ('Fastq file {} '
                    'has read length of {}bp, while '
                    'the recommended read length for {} '
                    'data is > 100bp.'.format(
                        audit_link(path_to_text(f['@id']), f['@id']),
                        l,
                        organism_name
                    )
                )
                yield AuditFailure('insufficient read length',
                                   detail, level='NOT_COMPLIANT')
    return


def check_experiment_chip_seq_standards(
        experiment,
        files_structure,
        standards_version):

    fastq_files = files_structure.get('fastq_files').values()
    alignment_files = files_structure.get('alignments').values()
    unfiltered_alignment_files = files_structure.get('unfiltered_alignments').values()
    idr_peaks_files = files_structure.get('preferred_default_idr_peaks').values()
    assay_name = experiment.get('assay_term_name')

    upper_limit_read_length = 50
    medium_limit_read_length = 36
    lower_limit_read_length = 26
    for f in fastq_files:
        yield from check_file_read_length_chip(
            f,
            upper_limit_read_length,
            medium_limit_read_length,
            lower_limit_read_length)

    pipeline_title = scanFilesForPipelineTitle_yes_chipseq(
        alignment_files,
        ['ChIP-seq read mapping',
        'Transcription factor ChIP-seq pipeline (modERN)',
        'Histone ChIP-seq 2 (unreplicated)',
        'Histone ChIP-seq 2',
        'Transcription factor ChIP-seq 2',
        'Transcription factor ChIP-seq 2 (unreplicated)'])
    if pipeline_title is False:
        return

    organism_name = get_organism_name(
        reps=experiment['replicates'],
        excluded_types=[]
    )  # human/mouse

    target = get_target(experiment)
    if target is False and not experiment.get('control_type'):
        return

    align_enrich_metrics = get_metrics(alignment_files, 'ChipAlignmentEnrichmentQualityMetric')
    # Checks in ChIPAlignmentEnrichmentQualityMetric
    if align_enrich_metrics is not None and len(align_enrich_metrics) > 0:
        for metric in align_enrich_metrics:
            yield from negative_coefficients(metric, ['NSC', 'RSC'], files_structure)

    # Handles library_complexity for all cases and read_depth for all but H3K9me3
    for f in alignment_files:

        yield from check_file_chip_seq_library_complexity(f)

        if target and target['name'] in ['H3K9me3-human', 'H3K9me3-mouse']:
            continue

        read_depth = get_file_read_depth_from_alignment(f, target, assay_name)
        yield from check_file_chip_seq_read_depth(
            f,
            experiment.get('control_type'),
            organism_name,
            target,
            read_depth,
            standards_version
        )

    # Specifically handles read_depth for experiments with H3K9me3 mark
    if target and target['name'] in ['H3K9me3-human', 'H3K9me3-mouse']:
        for f in unfiltered_alignment_files:
            read_depth = get_file_read_depth_from_alignment(f, target, assay_name)
            yield from check_file_chip_seq_read_depth(
                f,
                experiment.get('control_type'),
                organism_name,
                target,
                read_depth,
                standards_version
            )

    if 'replication_type' not in experiment or experiment['replication_type'] == 'unreplicated':
        return

    ListofMetrics = []
    ListofMetrics.extend([get_metrics(idr_peaks_files, 'IDRQualityMetric'), get_metrics(idr_peaks_files, 'ChipReplicationQualityMetric')]) 
    if ListofMetrics:
        for idr_metrics in ListofMetrics:
            yield from check_idr(idr_metrics, 2, 2)
    return


def check_experiment_long_rna_standards(experiment,
                                        fastq_files,
                                        alignment_files,
                                        pipeline_title,
                                        gene_quantifications,
                                        desired_assembly,
                                        desired_annotation,
                                        upper_limit_read_depth,
                                        medium_limit_read_depth,
                                        lower_limit_read_depth,
                                        standards_link):

    yield from check_experiment_ERCC_spikeins(experiment, pipeline_title)

    pipelines = get_pipeline_objects(alignment_files)
    if pipelines is not None and len(pipelines) > 0:
        for f in alignment_files:

            if 'assembly' in f and f['assembly'] == desired_assembly:

                read_depth = get_file_read_depth_from_alignment(f,
                                                                get_target(
                                                                    experiment),
                                                                'long RNA')

                if experiment['assay_term_name'] in ['shRNA knockdown followed by RNA-seq',
                                                     'siRNA knockdown followed by RNA-seq',
                                                     'CRISPRi followed by RNA-seq',
                                                     'CRISPR genome editing followed by RNA-seq']:
                    yield from check_file_read_depth(
                        f, read_depth, 10000000, 10000000, 1000000,
                        experiment['assay_term_name'],
                        pipeline_title,
                        pipelines[0],
                        standards_link)
                elif experiment['assay_term_name'] in ['single-cell RNA sequencing assay']:
                    yield from check_file_read_depth(
                        f, read_depth, 5000000, 5000000, 500000,
                        experiment['assay_term_name'],
                        pipeline_title,
                        pipelines[0],
                        standards_link)
                else:
                    yield from check_file_read_depth(
                        f, read_depth,
                        upper_limit_read_depth,
                        medium_limit_read_depth,
                        lower_limit_read_depth,
                        experiment['assay_term_name'],
                        pipeline_title,
                        pipelines[0],
                        standards_link)

    if 'replication_type' not in experiment:
        return

    mad_metrics = get_metrics(gene_quantifications,
                              'MadQualityMetric',
                              desired_assembly,
                              desired_annotation)

    if experiment['assay_term_name'] != 'single-cell RNA sequencing assay':
        yield from check_spearman(
            mad_metrics, experiment['replication_type'],
            0.9, 0.8, pipeline_title)
    # for failure in check_mad(mad_metrics, experiment['replication_type'],
    #                         0.2, pipeline_title):
    #    yield failure

    return


def check_experiment_small_rna_standards(experiment,
                                         fastq_files,
                                         alignment_files,
                                         pipeline_title,
                                         gene_quantifications,
                                         desired_assembly,
                                         desired_annotation,
                                         upper_limit_read_depth,
                                         medium_limit_read_depth,
                                         lower_limit_read_depth,
                                         standards_link):
    for f in fastq_files:
        if 'run_type' in f and f['run_type'] != 'single-ended':
            detail = ('Small RNA-seq experiment {} '
                'contains a file {} '
                'that is not single-ended.'.format(
                    audit_link(path_to_text(experiment['@id']), experiment['@id']),
                    audit_link(path_to_text(f['@id']), f['@id'])
                )
            )
            yield AuditFailure('non-standard run type', detail, level='WARNING')
    pipelines = get_pipeline_objects(alignment_files)
    if pipelines is not None and len(pipelines) > 0:
        for f in alignment_files:
            if 'assembly' in f and f['assembly'] == desired_assembly:
                read_depth = get_file_read_depth_from_alignment(f,
                                                                get_target(
                                                                    experiment),
                                                                'small RNA')

                yield from check_file_read_depth(
                    f, read_depth,
                    upper_limit_read_depth,
                    medium_limit_read_depth,
                    lower_limit_read_depth,
                    experiment['assay_term_name'],
                    pipeline_title,
                    pipelines[0],
                    standards_link)

    if 'replication_type' not in experiment:
        return

    mad_metrics = get_metrics(gene_quantifications,
                              'MadQualityMetric',
                              desired_assembly,
                              desired_annotation)

    yield from check_spearman(
        mad_metrics, experiment['replication_type'],
        0.9, 0.8, 'Small RNA-seq single-end pipeline')
    return


def check_experiment_cage_rampage_standards(experiment,
                                            fastq_files,
                                            alignment_files,
                                            pipeline_title,
                                            gene_quantifications,
                                            desired_assembly,
                                            desired_annotation,
                                            upper_limit_read_depth,
                                            middle_limit_read_depth,
                                            lower_limit_read_depth,
                                            standards_version,
                                            standards_link):

    if standards_version == 'ENC3':
        for f in fastq_files:
            if 'run_type' in f and f['run_type'] != 'paired-ended':
                detail = ('{} experiment {} '
                    'contains a file {} '
                    'that is not paired-ended.'.format(
                        experiment['assay_term_name'].capitalize(),
                        audit_link(path_to_text(experiment['@id']), experiment['@id']),
                        audit_link(path_to_text(f['@id']), f['@id'])
                    )
                )
                yield AuditFailure('non-standard run type', detail, level='WARNING')
    pipelines = get_pipeline_objects(alignment_files)
    if pipelines is not None and len(pipelines) > 0:
        for f in alignment_files:
            if 'assembly' in f and f['assembly'] == desired_assembly:

                read_depth = get_file_read_depth_from_alignment(f,
                                                                get_target(
                                                                    experiment),
                                                                experiment['assay_term_name'])
                yield from check_file_read_depth(
                    f, read_depth,
                    upper_limit_read_depth,
                    middle_limit_read_depth,
                    lower_limit_read_depth,
                    experiment['assay_term_name'],
                    pipeline_title,
                    pipelines[0],
                    standards_link)

    if 'replication_type' not in experiment:
        return

    mad_metrics = get_metrics(gene_quantifications,
                              'MadQualityMetric',
                              desired_assembly,
                              desired_annotation)

    yield from check_spearman(
        mad_metrics, experiment['replication_type'],
        0.9, 0.8, 'RAMPAGE (paired-end, stranded)')
    return


def check_experiment_micro_rna_standards(
    experiment,
    fastq_files,
    alignment_files,
    pipeline_title,
    microRNA_quantifications,
    desired_assembly,
    desired_annotation,
    standards_links,
    upper_limit_reads_mapped,
    lower_limit_reads_mapped,
    upper_limit_spearman,
    lower_limit_spearman,
    upper_limit_expressed_mirnas,
    lower_limit_expressed_mirnas
):
    # Audit read length
    minimum_threshold = 30 
    for f in fastq_files:
        yield from check_file_read_length_rna(f, minimum_threshold,
                                                  pipeline_title,
                                                  standards_links)
    # Gather metrics
    quantification_metrics = get_metrics(
        microRNA_quantifications,
        'MicroRnaQuantificationQualityMetric',
        desired_assembly,
        desired_annotation,
    )
    # Desired annotation does not pertain to alignment files
    alignment_metrics = get_metrics(
        alignment_files,
        'MicroRnaMappingQualityMetric',
        desired_assembly,
    )
    correlation_metrics = get_metrics(
        microRNA_quantifications,
        'CorrelationQualityMetric',
        desired_assembly,
        desired_annotation,
    )
    # Audit Spearman correlations
    yield from check_replicate_metric_dual_threshold(
        correlation_metrics,
        metric_name='Spearman correlation',
        audit_name='replicate concordance',
        upper_limit=upper_limit_spearman,
        lower_limit=lower_limit_spearman,
    )
    # Audit flnc read counts
    yield from check_replicate_metric_dual_threshold(
        alignment_metrics,
        metric_name='aligned_reads',
        audit_name='number of aligned reads',
        upper_limit=upper_limit_reads_mapped,
        lower_limit=lower_limit_reads_mapped,
    )
    # Audit mapping rate
    yield from check_replicate_metric_dual_threshold(
        quantification_metrics,
        metric_name='expressed_mirnas',
        audit_name='microRNAs expressed',
        upper_limit=upper_limit_expressed_mirnas,
        lower_limit=lower_limit_expressed_mirnas,
    )
    return


def check_experiment_long_read_rna_standards(
    experiment,
    unfiltered_alignment_files,
    transcript_quantifications,
    desired_assembly,
    desired_annotation,
    upper_limit_flnc,
    lower_limit_flnc,
    upper_limit_mapping_rate,
    lower_limit_mapping_rate,
    upper_limit_spearman,
    lower_limit_spearman,
    upper_limit_genes_detected,
    lower_limit_genes_detected,
):
    # Gather metrics
    quantification_metrics = get_metrics(
        transcript_quantifications,
        'LongReadRnaQuantificationQualityMetric',
        desired_assembly,
        desired_annotation,
    )
    # Desired annotation does not pertain to alignment files
    unfiltered_alignment_metrics = get_metrics(
        unfiltered_alignment_files,
        'LongReadRnaMappingQualityMetric',
        desired_assembly,
    )
    correlation_metrics = get_metrics(
        transcript_quantifications,
        'CorrelationQualityMetric',
        desired_assembly,
        desired_annotation,
    )
    # Audit Spearman correlations
    yield from check_replicate_metric_dual_threshold(
        correlation_metrics,
        metric_name='Spearman correlation',
        audit_name='replicate concordance',
        upper_limit=upper_limit_spearman,
        lower_limit=lower_limit_spearman,
    )
    # Audit flnc read counts
    yield from check_replicate_metric_dual_threshold(
        unfiltered_alignment_metrics,
        metric_name='full_length_non_chimeric_read_count',
        audit_name='sequencing depth',
        upper_limit=upper_limit_flnc,
        lower_limit=lower_limit_flnc,
        metric_description='full-length non-chimeric (FLNC) read count',
    )
    # Audit mapping rate
    yield from check_replicate_metric_dual_threshold(
        unfiltered_alignment_metrics,
        metric_name='mapping_rate',
        audit_name='mapping rate',
        upper_limit=upper_limit_mapping_rate,
        lower_limit=lower_limit_mapping_rate,
        metric_description='mapping rate',
    )
    # Audit gene quantifications
    yield from check_replicate_metric_dual_threshold(
        quantification_metrics,
        metric_name='genes_detected',
        audit_name='genes detected',
        upper_limit=upper_limit_genes_detected,
        lower_limit=lower_limit_genes_detected,
        metric_description='GENCODE genes detected',
    )
    return


def check_replicate_metric_dual_threshold(
    metrics,
    metric_name,
    audit_name,
    upper_limit,
    lower_limit,
    metric_description=None,
):
    """
    Generic function to handle audits on files from a single replicate with multiple thresholds
    """
    if not metric_description:
        metric_description = metric_name
    for metric in metrics:
        metric_value = metric.get(metric_name)
        files = metric['quality_metric_of']
        if metric_value and metric_value < upper_limit:
            level = 'WARNING'
            standards_severity = 'recommendations'
            audit_name_severity = 'borderline'
            if metric_value < lower_limit:
                level = 'NOT_COMPLIANT'
                standards_severity = 'requirements'
                audit_name_severity = 'insufficient'
            file_names_links = [audit_link(path_to_text(file), file) for file in files]
            detail = ('Files {} have {} of {}, which is below ENCODE {}. According to '
                'ENCODE data standards, a number for this property in a replicate of > {:,} '
                'is required, and > {:,} is recommended.'.format(
                    ', '.join(file_names_links),
                    metric_description,
                    metric_value,
                    standards_severity,
                    lower_limit,
                    upper_limit,
                )
            )
            yield AuditFailure('{} {}'.format(audit_name_severity, audit_name), detail, level=level)
    return


def check_idr(metrics, rescue, self_consistency):
    for m in metrics:
        if 'rescue_ratio' in m and 'self_consistency_ratio' in m:
            rescue_r = m['rescue_ratio']
            self_r = m['self_consistency_ratio']
            if rescue_r > rescue and self_r > self_consistency:
                file_list = []
                for f in m['quality_metric_of']:
                    file_list.append(f)
                file_names_links = [audit_link(path_to_text(file), file) for file in file_list]
                detail = ('Replicate concordance in ChIP-seq experiments is measured by '
                    'calculating IDR values (Irreproducible Discovery Rate). '
                    'ENCODE processed IDR thresholded peaks files {} '
                    'have a rescue ratio of {:.2f} and a '
                    'self consistency ratio of {:.2f}. '
                    'According to ENCODE standards, having both rescue ratio '
                    'and self consistency ratio values < 2 is recommended, but '
                    'having only one of the ratio values < 2 is acceptable.'.format(
                        ', '.join(file_names_links),
                        rescue_r,
                        self_r
                    )
                )
                yield AuditFailure('insufficient replicate concordance', detail,
                                   level='NOT_COMPLIANT')
            elif (rescue_r <= rescue and self_r > self_consistency) or \
                 (rescue_r > rescue and self_r <= self_consistency):
                file_list = []
                for f in m['quality_metric_of']:
                    file_list.append(f)
                file_names_links = [audit_link(path_to_text(file), file) for file in file_list]
                detail = ('Replicate concordance in ChIP-seq experiments is measured by '
                    'calculating IDR values (Irreproducible Discovery Rate). '
                    'ENCODE processed IDR thresholded peaks files {} '
                    'have a rescue ratio of {:.2f} and a '
                    'self consistency ratio of {:.2f}. '
                    'According to ENCODE standards, having both rescue ratio '
                    'and self consistency ratio values < 2 is recommended, but '
                    'having only one of the ratio values < 2 is acceptable.'.format(
                        ', '.join(file_names_links),
                        rescue_r,
                        self_r
                    )
                )
                yield AuditFailure('borderline replicate concordance', detail,
                                   level='WARNING')
    return


def check_mad(metrics, replication_type, mad_threshold, pipeline):
    if replication_type == 'anisogenic':
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
                file_list = []
                for f in m['quality_metric_of']:
                    file_list.append(f['@id'])
                file_names_links = [audit_link(path_to_text(file), file) for file in file_list]
                detail = ('ENCODE processed gene quantification files {} '
                    'has Median-Average-Deviation (MAD) '
                    'of replicate log ratios from quantification '
                    'value of {}.'
                    ' For gene quantification files from an {}'
                    ' assay in the {} '
                    'pipeline, a value <0.2 is recommended, but a value between '
                    '0.2 and 0.5 is acceptable.'.format(
                        ', '.join(file_names_links),
                        mad_value,
                        experiment_replication_type,
                        pipeline
                    )
                )
                if experiment_replication_type == 'isogenic':
                    if mad_value < 0.5:
                        yield AuditFailure('low replicate concordance', detail,
                                           level='WARNING')
                    else:
                        yield AuditFailure('insufficient replicate concordance', detail,
                                           level='NOT_COMPLIANT')
                elif experiment_replication_type == 'anisogenic' and mad_value > 0.5:
                    file_names_links = [audit_link(path_to_text(file), file) for file in file_list]
                    detail = ('ENCODE processed gene quantification files {} '
                        'has Median-Average-Deviation (MAD) '
                        'of replicate log ratios from quantification '
                        'value of {}.'
                        ' For gene quantification files from an {}'
                        ' assay in the {} '
                        'pipeline, a value <0.5 is recommended.'.format(
                            ', '.join(file_names_links),
                            mad_value,
                            experiment_replication_type,
                            pipeline
                        )
                    )
                    yield AuditFailure('low replicate concordance', detail,
                                       level='WARNING')
    return


def check_experiment_ERCC_spikeins(experiment, pipeline):
    '''
    The assumption in this functon is that the regular audit will catch anything without spikeins.
    This audit is checking specifically for presence of ERCC spike-in in long-RNA pipeline
    experiments
    '''
    for rep in experiment['replicates']:
        lib = rep.get('library')
        if lib is None:
            continue
        if check_library_for_long_fragments(lib) is False:
            continue

        ercc_flag = False
        some_spikein_present = False
        spikes = lib.get('spikeins_used')

        if (spikes is not None) and (len(spikes) > 0):
            for s in spikes:
                some_spikein_present = True
                if s.get('files'):
                    for f in s.get('files'):
                        if (
                                ('/files/ENCFF001RTP/' == f) or
                                ('/files/ENCFF001RTO/' == f and
                                 experiment['assay_term_name'] ==
                                 'single-cell RNA sequencing assay')):
                            ercc_flag = True

        if ercc_flag is False:
            if some_spikein_present is True:
                detail = ('Library {} in experiment {} '
                    'that was processed by {} pipeline '
                    'requires standard ERCC spike-in to be used in its preparation.'.format(
                        audit_link(path_to_text(lib['@id']), lib['@id']),
                        audit_link(path_to_text(experiment['@id']), experiment['@id']),
                        pipeline
                    )
                )
                yield AuditFailure('missing spikeins',
                                   detail, level='WARNING')
            else:
                detail = ('Library {} in experiment {} '
                    'that was processed by {} pipeline '
                    'requires ERCC spike-in to be used in its preparation.'.format(
                        audit_link(path_to_text(lib['@id']), lib['@id']),
                        audit_link(path_to_text(experiment['@id']), experiment['@id']),
                        pipeline
                    )
                )
                yield AuditFailure('missing spikeins',
                                   detail, level='NOT_COMPLIANT')
    return


def check_spearman(metrics, replication_type, isogenic_threshold,
                   anisogenic_threshold, pipeline):

    if replication_type == 'anisogenic':
        threshold = anisogenic_threshold
    elif replication_type == 'isogenic':
        threshold = isogenic_threshold
    else:
        return

    for m in metrics:
        if 'Spearman correlation' in m:
            spearman_correlation = m['Spearman correlation']
            if spearman_correlation < threshold:
                file_names = []
                for f in m['quality_metric_of']:
                    file_names.append(f)
                file_names_links = [audit_link(path_to_text(f), f) for f in file_names]
                detail = ('Replicate concordance in RNA-seq experiments is measured by '
                    'calculating the Spearman correlation between gene quantifications '
                    'of the replicates. '
                    'ENCODE processed gene quantification files {} '
                    'have a Spearman correlation of {:.2f}. '
                    'According to ENCODE standards, in an {} '
                    'assay analyzed using the {} pipeline, '
                    'a Spearman correlation value > {} '
                    'is recommended.'.format(
                        ', '.join(file_names_links),
                        spearman_correlation,
                        replication_type,
                        pipeline,
                        threshold
                    )
                )
                yield AuditFailure('low replicate concordance', detail,
                                   level='WARNING')
    return


def check_file_chip_seq_library_complexity(alignment_file):
    '''
    An alignment file from the ENCODE ChIP-seq processing pipeline
    should have minimal library complexity in accordance with the criteria
    '''
    if alignment_file['output_type'] == 'transcriptome alignments':
        return

    if alignment_file['lab'] not in ['/labs/encode-processing-pipeline/', '/labs/kevin-white/']:
        return

    if ('quality_metrics' not in alignment_file) or (alignment_file.get('quality_metrics') == []):
        return

    nrf_detail = ('NRF (Non Redundant Fraction) is equal to the result of the '
        'division of the number of reads after duplicates removal by '
        'the total number of reads. '
        'An NRF value in the range 0 - 0.5 is poor complexity, '
        '0.5 - 0.8 is moderate complexity, '
        'and > 0.8 high complexity. NRF value > 0.8 is recommended, '
        'but > 0.5 is acceptable. ')

    pbc1_detail = ('PBC1 (PCR Bottlenecking Coefficient 1, M1/M_distinct) '
        'is the ratio of the number of genomic '
        'locations where exactly one read maps uniquely (M1) to the number of '
        'genomic locations where some reads map (M_distinct). '
        'A PBC1 value in the range 0 - 0.5 is severe bottlenecking, 0.5 - 0.8 '
        'is moderate bottlenecking, 0.8 - 0.9 is mild bottlenecking, and > 0.9 '
        'is no bottlenecking. PBC1 value > 0.9 is recommended, but > 0.8 is '
        'acceptable. ')

    pbc2_detail = ('PBC2 (PCR Bottlenecking Coefficient 2, M1/M2) is the ratio of the number of '
        'genomic locations where exactly one read maps uniquely (M1) to the number of genomic '
        'locations where two reads map uniquely (M2). '
        'A PBC2 value in the range 0 - 1 is severe bottlenecking, 1 - 3 '
        'is moderate bottlenecking, 3 - 10 is mild bottlenecking, > 10 is '
        'no bottlenecking. PBC2 value > 10 is recommended, but > 3 is acceptable. ')

    quality_metrics = alignment_file.get('quality_metrics')
    for metric in quality_metrics:

        if 'NRF' in metric:
            NRF_value = float(metric['NRF'])
            detail = ('{} ENCODE processed {} file {} '
                'was generated from a library with '
                'NRF value of {:.2f}.'.format(
                    nrf_detail,
                    alignment_file['output_type'],
                    audit_link(path_to_text(alignment_file['@id']), alignment_file['@id']),
                    NRF_value
                )
            )
            if NRF_value < 0.5:
                yield AuditFailure('poor library complexity', detail,
                                   level='NOT_COMPLIANT')
            elif NRF_value >= 0.5 and NRF_value < 0.8:
                yield AuditFailure('moderate library complexity', detail,
                                   level='WARNING')
        if 'PBC1' in metric:
            PBC1_value = float(metric['PBC1'])
            detail = ('{} ENCODE processed {} file {} '
                'was generated from a library with PBC1 value of {:.2f}.'.format(
                    pbc1_detail,
                    alignment_file['output_type'],
                    audit_link(path_to_text(alignment_file['@id']), alignment_file['@id']),
                    PBC1_value
                )
            )
            if PBC1_value < 0.5:
                yield AuditFailure('severe bottlenecking', detail,
                                   level='NOT_COMPLIANT')
            elif PBC1_value >= 0.5 and PBC1_value < 0.9:
                yield AuditFailure('mild to moderate bottlenecking', detail,
                                   level='WARNING')
        if 'PBC2' in metric:
            PBC2_raw_value = metric['PBC2']
            if PBC2_raw_value == 'Infinity':
                PBC2_value = float('inf')
            else:
                PBC2_value = float(metric['PBC2'])
            detail = ('{} ENCODE processed {} file {} '
                'was generated from a library with PBC2 value of {:.2f}.'.format(
                    pbc2_detail,
                    alignment_file['output_type'],
                    audit_link(path_to_text(alignment_file['@id']), alignment_file['@id']),
                    PBC2_value
                )
            )
            if PBC2_value < 1: 
                yield AuditFailure('severe bottlenecking', detail,
                                   level='NOT_COMPLIANT')
            elif PBC2_value >= 1 and PBC2_value < 10:
                yield AuditFailure('mild to moderate bottlenecking', detail,
                                   level='WARNING')
    return


def check_wgbs_coverage(samtools_metrics,
                        pipeline_title,
                        read_length,
                        organism,
                        pipeline_objects):
    for m in samtools_metrics:
        if 'mapped' in m:
            mapped_reads = m['mapped']
            if organism == 'mouse':
                coverage = float(mapped_reads * read_length) / 2800000000.0
            elif organism == 'human':
                coverage = float(mapped_reads * read_length) / 3300000000.0
            detail = ('Replicate of experiment processed by {} ( {} ) '
                'has a coverage of {}X. '
                'The minimum ENCODE standard coverage for each replicate in '
                'a WGBS assay is 25X and the recommended value '
                'is > 30X (See {} )'.format(
                    pipeline_title,
                    audit_link(path_to_text(pipeline_objects[0]['@id']), pipeline_objects[0]['@id']),
                    int(coverage),
                    audit_link('ENCODE WGBS data standards', '/data-standards/wgbs/')
                )
            )
            if coverage < 5:
                yield AuditFailure('extremely low coverage',
                                   detail,
                                   level='ERROR')
            elif coverage < 25:
                yield AuditFailure('insufficient coverage',
                                   detail,
                                   level='NOT_COMPLIANT')
            elif coverage < 30:
                yield AuditFailure('low coverage',
                                   detail,
                                   level='WARNING')
    return


def check_wgbs_pearson(cpg_metrics, threshold,  pipeline_title):
    for m in cpg_metrics:
        if 'Pearson Correlation Coefficient' in m:
            if m['Pearson Correlation Coefficient'] < threshold:
                detail = ('ENCODE experiment processed by {} '
                    'pipeline has CpG quantification Pearson Correlation Coefficient of '
                    '{}, while a value >={} is required.'.format(
                        pipeline_title,
                        m['Pearson Correlation Coefficient'],
                        threshold
                    )
                )
                yield AuditFailure('insufficient replicate concordance',
                                   detail,
                                   level='NOT_COMPLIANT')
    return


def check_wgbs_lambda(bismark_metrics, threshold, pipeline_title):
    for metric in bismark_metrics:
        cpg_string = metric.get('lambda C methylated in CpG context')
        chg_string = metric.get('lambda C methylated in CHG context')
        chh_string = metric.get('lambda C methylated in CHH context')
        if (cpg_string and chg_string and chh_string):
            lambdaCpG = float(cpg_string[:-1])
            lambdaCHG = float(chg_string[:-1])
            lambdaCHH = float(chh_string[:-1])
            if (lambdaCpG > 1 and lambdaCHG > 1 and lambdaCHH > 1) or \
            (((lambdaCpG * 0.25) + (lambdaCHG * 0.25) + (lambdaCHH * 0.5)) > 1):
                detail = ('ENCODE experiment processed by {} '
                    'pipeline has the following %C methylated in different contexts. '
                    'lambda C methylated in CpG context was {}%, '
                    'lambda C methylated in CHG context was {}%, '
                    'lambda C methylated in CHH context was {}%. '
                    'The %C methylated in all contexts should be < 1%.'.format(
                        pipeline_title,
                        lambdaCpG,
                        lambdaCHG,
                        lambdaCHH
                    )
                )
                yield AuditFailure('high lambda C methylation ratio', detail,
                                   level='WARNING')


def check_file_chip_seq_read_depth(file_to_check,
                                   control_type,
                                   organism_name,
                                   target,
                                   read_depth,
                                   standards_version):
    # added individual file pipeline validation due to the fact that one experiment may
    # have been mapped using 'Raw mapping' and also 'Histone ChIP-seq' - and there is no need to
    # check read depth on Raw files, while it is required for Histone
    pipeline_title = scanFilesForPipelineTitle_yes_chipseq(
        [file_to_check],
        ['ChIP-seq read mapping',
        'Transcription factor ChIP-seq pipeline (modERN)',
        'Histone ChIP-seq 2 (unreplicated)',
        'Histone ChIP-seq 2',
        'Transcription factor ChIP-seq 2',
        'Transcription factor ChIP-seq 2 (unreplicated)'])

    if pipeline_title is False:
        return
    pipeline_objects = get_pipeline_objects([file_to_check])

    marks = pipelines_with_read_depth['ChIP-seq read mapping']
    modERN_cutoff = pipelines_with_read_depth[
        'Transcription factor ChIP-seq pipeline (modERN)']
    if read_depth is False:
        detail = ('ENCODE processed {} file {} has no read depth information.'.format(
            file_to_check['output_type'],
            audit_link(path_to_text(file_to_check['@id']), file_to_check['@id'])
            )
        )
        yield AuditFailure('missing read depth', detail, level='INTERNAL_ACTION')
        return

    if target is not False and 'name' in target:
        target_name = target['name']
    elif control_type:
        target_name = control_type
    else:
        return

    if target is not False and 'investigated_as' in target:
        target_investigated_as = target['investigated_as']
    elif control_type:
        target_investigated_as = [control_type]
    else:
        return

    if control_type == 'input library' and organism_name in ['human', 'mouse']:
        if pipeline_title == 'Transcription factor ChIP-seq pipeline (modERN)':
            if read_depth < modERN_cutoff:
                detail = ('modERN processed alignment file {} has {} '
                    'usable fragments. It cannot be used as a control '
                    'in experiments studying transcription factors, which '
                    'require {} usable fragments, according to '
                    'the standards defined by the modERN project.'.format(
                        audit_link(path_to_text(file_to_check['@id']), file_to_check['@id']),
                        read_depth,
                        modERN_cutoff
                    )
                )
                yield AuditFailure('insufficient read depth',
                                   detail, level='NOT_COMPLIANT')
        else:
            if read_depth >= marks['narrow']['recommended'] and read_depth < marks['broad']['recommended']:
                if 'assembly' in file_to_check:
                    detail = ('Control {} file {} mapped using {} assembly has {} '
                        'usable fragments. '
                        'The minimum ENCODE standard for a control of ChIP-seq assays targeting broad '
                        'histone marks '
                        'is 20 million usable fragments, the recommended number of usable '
                        'fragments is > 45 million. (See {} )'.format(
                            file_to_check['output_type'],
                            audit_link(path_to_text(file_to_check['@id']), file_to_check['@id']),
                            file_to_check['assembly'],
                            read_depth,
                            audit_link('ENCODE ChIP-seq data standards', '/data-standards/chip-seq/')
                        )
                    )
                else:
                    detail = ('Control {} file {} has {} '
                        'usable fragments. '
                        'The minimum ENCODE standard for a control of ChIP-seq assays targeting broad '
                        'histone marks '
                        'is 20 million usable fragments, the recommended number of usable '
                        'fragments is > 45 million. (See {} )'.format(
                            file_to_check['output_type'],
                            audit_link(path_to_text(file_to_check['@id']), file_to_check['@id']),
                            read_depth,
                            audit_link('ENCODE ChIP-seq data standards', '/data-standards/chip-seq/')
                        )
                    )
                yield AuditFailure('insufficient read depth for broad peaks control', detail, level='INTERNAL_ACTION')
            if read_depth < marks['narrow']['recommended']:
                if 'assembly' in file_to_check:
                    detail = ('Control {} file {} mapped using {} assembly has {} '
                        'usable fragments. '
                        'The minimum ENCODE standard for a control of ChIP-seq assays targeting broad '
                        'histone marks '
                        'is 20 million usable fragments, the recommended number of usable '
                        'fragments is > 45 million. '
                        'The minimum for a control of ChIP-seq assays targeting narrow '
                        'histone marks or transcription factors '
                        'is 10 million usable fragments, the recommended number of usable '
                        'fragments is > 20 million. (See {} )'.format(
                            file_to_check['output_type'],
                            audit_link(path_to_text(file_to_check['@id']), file_to_check['@id']),
                            file_to_check['assembly'],
                            read_depth,
                            audit_link('ENCODE ChIP-seq data standards', '/data-standards/chip-seq/')
                        )
                    )
                else:
                    detail = ('Control {} file {} has {} '
                        'usable fragments. '
                        'The minimum ENCODE standard for a control of ChIP-seq assays targeting broad '
                        'histone marks '
                        'is 20 million usable fragments, the recommended number of usable '
                        'fragments is > 45 million. '
                        'The minimum for a control of ChIP-seq assays targeting narrow '
                        'histone marks or transcription factors '
                        'is 10 million usable fragments, the recommended number of usable '
                        'fragments is > 20 million. (See {} )'.format(
                            file_to_check['output_type'],
                            audit_link(path_to_text(file_to_check['@id']), file_to_check['@id']),
                            read_depth.
                            audit_link('ENCODE ChIP-seq data standards', '/data-standards/chip-seq/')
                        )
                    )
                if read_depth >= marks['narrow']['minimal']:
                    yield AuditFailure('low read depth', detail, level='WARNING')
                elif read_depth >= marks['narrow']['low'] and read_depth < marks['narrow']['minimal']:
                    yield AuditFailure('insufficient read depth',
                                       detail, level='NOT_COMPLIANT')
                else:
                    yield AuditFailure('extremely low read depth',
                                       detail, level='ERROR')
    elif 'broad histone mark' in target_investigated_as and \
            standards_version != 'modERN':  # target_name in broad_peaks_targets:
        pipeline_object = get_pipeline_by_name(
            pipeline_objects, pipeline_title)
        if pipeline_object:
            if target_name in ['H3K9me3-human', 'H3K9me3-mouse']:
                if read_depth < marks['broad']['recommended']:
                    if 'assembly' in file_to_check:
                        detail = ('Processed {} file {} produced by {} '
                            'pipeline ( {} ) using the {} assembly '
                            'has {} mapped reads. '
                            'The minimum ENCODE standard for each replicate in a ChIP-seq '
                            'experiment targeting {} and investigated as '
                            'a broad histone mark is 35 million mapped reads. '
                            'The recommended value is > 45 million, but > 35 million is '
                            'acceptable. (See {} )'.format(
                                file_to_check['output_type'],
                                audit_link(path_to_text(file_to_check['@id']), file_to_check['@id']),
                                pipeline_object['title'],
                                audit_link(path_to_text(pipeline_object['@id']), pipeline_object['@id']),
                                file_to_check['assembly'],
                                read_depth,
                                target_name,
                                audit_link('ENCODE ChIP-seq data standards', '/data-standards/chip-seq/')
                            )
                        )
                    else:
                        detail = ('Processed {} file {} produced by {} '
                            'pipeline ( {} ) has {} mapped reads. '
                            'The minimum ENCODE standard for each replicate in a ChIP-seq '
                            'experiment targeting {} and investigated as '
                            'a broad histone mark is 35 million mapped reads. '
                            'The recommended value is > 45 million, but > 35 million is '
                            'acceptable. (See {} )'.format(
                                file_to_check['output_type'],
                                audit_link(path_to_text(file_to_check['@id']), file_to_check['@id']),
                                pipeline_object['title'],
                                audit_link(path_to_text(pipeline_object['@id']), pipeline_object['@id']),
                                read_depth,
                                target_name,
                                audit_link('ENCODE ChIP-seq data standards', '/data-standards/chip-seq/')
                            )
                        )
                    if read_depth >= marks['broad']['minimal']:
                        yield AuditFailure('low read depth',
                                           detail, level='WARNING')
                    elif read_depth >= 100 and read_depth < marks['broad']['minimal']:
                        yield AuditFailure('insufficient read depth',
                                           detail, level='NOT_COMPLIANT')
                    elif read_depth < 100:
                        yield AuditFailure('extremely low read depth',
                                           detail, level='ERROR')
            else:
                if 'assembly' in file_to_check:
                    detail = ('Processed {} file {} produced by {} '
                        'pipeline ( {} ) using the {} assembly '
                        'has {} usable fragments. '
                        'The minimum ENCODE standard for each replicate in a ChIP-seq '
                        'experiment targeting {} and investigated as '
                        'a broad histone mark is 20 million usable fragments. '
                        'The recommended value is > 45 million, but > 35 million is '
                        'acceptable. (See {} )'.format(
                            file_to_check['output_type'],
                            audit_link(path_to_text(file_to_check['@id']), file_to_check['@id']),
                            pipeline_object['title'],
                            audit_link(path_to_text(pipeline_object['@id']), pipeline_object['@id']),
                            file_to_check['assembly'],
                            read_depth,
                            target_name,
                            audit_link('ENCODE ChIP-seq data standards', '/data-standards/chip-seq/')
                        )
                    )
                else:
                    detail = ('Processed {} file {} produced by {} '
                        'pipeline ( {} ) has {} usable fragments. '
                        'The minimum ENCODE standard for each replicate in a ChIP-seq '
                        'experiment targeting {} and investigated as '
                        'a broad histone mark is 20 million usable fragments. '
                        'The recommended value is > 45 million, but > 35 million is '
                        'acceptable. (See {} )'.format(
                            file_to_check['output_type'],
                            audit_link(path_to_text(file_to_check['@id']), file_to_check['@id']),
                            pipeline_object['title'],
                            audit_link(path_to_text(pipeline_object['@id']), pipeline_object['@id']),
                            read_depth,
                            target_name,
                            audit_link('ENCODE ChIP-seq data standards', '/data-standards/chip-seq/')
                        )
                    )

                if read_depth >= marks['broad']['minimal'] and read_depth < marks['broad']['recommended']:
                    yield AuditFailure('low read depth',
                                       detail, level='WARNING')
                elif read_depth < marks['broad']['minimal'] and read_depth >= marks['broad']['low']:
                    yield AuditFailure('insufficient read depth',
                                       detail, level='NOT_COMPLIANT')
                elif read_depth < marks['broad']['low']:
                    yield AuditFailure('extremely low read depth',
                                       detail, level='ERROR')
    elif 'narrow histone mark' in target_investigated_as and \
            standards_version != 'modERN':
        pipeline_object = get_pipeline_by_name(
            pipeline_objects, pipeline_title)
        if pipeline_object:
            if 'assembly' in file_to_check:
                detail = ('Processed {} file {} produced by {} '
                    'pipeline ( {} ) using the {} assembly '
                    'has {} usable fragments. '
                    'The minimum ENCODE standard for each replicate in a ChIP-seq '
                    'experiment targeting {} and investigated as '
                    'a narrow histone mark is 10 million usable fragments. '
                    'The recommended value is > 20 million, but > 10 million is '
                    'acceptable. (See {} )'.format(
                        file_to_check['output_type'],
                        audit_link(path_to_text(file_to_check['@id']), file_to_check['@id']),
                        pipeline_object['title'],
                        audit_link(path_to_text(pipeline_object['@id']), pipeline_object['@id']),
                        file_to_check['assembly'],
                        read_depth,
                        target_name,
                        audit_link('ENCODE ChIP-seq data standards', '/data-standards/chip-seq/')
                    )
                )
            else:
                detail = ('Processed {} file {} produced by {} '
                    'pipeline ( {} ) has {} usable fragments. '
                    'The minimum ENCODE standard for each replicate in a ChIP-seq '
                    'experiment targeting {} and investigated as '
                    'a narrow histone mark is 10 million usable fragments. '
                    'The recommended value is > 20 million, but > 10 million is '
                    'acceptable. (See {} )'.format(
                        file_to_check['output_type'],
                        audit_link(path_to_text(file_to_check['@id']), file_to_check['@id']),
                        pipeline_object['title'],
                        audit_link(path_to_text(pipeline_object['@id']), pipeline_object['@id']),
                        read_depth,
                        target_name,
                        audit_link('ENCODE ChIP-seq data standards', '/data-standards/chip-seq/')
                    )
                )
            if read_depth >= marks['narrow']['minimal'] and read_depth < marks['narrow']['recommended']:
                yield AuditFailure('low read depth', detail, level='WARNING')
            elif read_depth < marks['narrow']['minimal'] and read_depth >= marks['narrow']['low']:
                yield AuditFailure('insufficient read depth',
                                   detail, level='NOT_COMPLIANT')
            elif read_depth < marks['narrow']['low']:
                yield AuditFailure('extremely low read depth',
                                   detail, level='ERROR')
    else:
        if pipeline_title == 'Transcription factor ChIP-seq pipeline (modERN)':
            if read_depth < modERN_cutoff:
                detail = ('modERN processed alignment file {} has {} '
                    'usable fragments. Replicates for ChIP-seq '
                    'assays and target {} '
                    'investigated as transcription factor require ' 
                    '{} usable fragments, according to '
                    'the standards defined by the modERN project.'.format(
                        audit_link(path_to_text(file_to_check['@id']), file_to_check['@id']),
                        read_depth,
                        target_name,
                        modERN_cutoff
                    )
                )
                yield AuditFailure('insufficient read depth',
                                   detail, level='NOT_COMPLIANT')
        else:
            pipeline_object = get_pipeline_by_name(pipeline_objects,
                                                   pipeline_title)
            if pipeline_object:
                if 'assembly' in file_to_check:
                    detail = ('Processed {} file {} produced by {} '
                        'pipeline ( {} ) using the {} assembly has {} '
                        'usable fragments. '
                        'The minimum ENCODE standard for each replicate in a ChIP-seq '
                        'experiment targeting {} and investigated as '
                        'a transcription factor is 10 million usable fragments. '
                        'The recommended value is > 20 million, but > 10 million is '
                        'acceptable. (See {} )'.format(
                            file_to_check['output_type'],
                            audit_link(path_to_text(file_to_check['@id']), file_to_check['@id']),
                            pipeline_object['title'],
                            audit_link(path_to_text(pipeline_object['@id']), pipeline_object['@id']),
                            file_to_check['assembly'],
                            read_depth,
                            target_name,
                            audit_link('ENCODE ChIP-seq data standards', '/data-standards/chip-seq/')
                        )
                    )
                else:
                    detail = ('Processed {} file {} roduced by {} '
                        'pipeline ( {} ) has {} usable fragments. '
                        'The minimum ENCODE standard for each replicate in a ChIP-seq '
                        'experiment targeting {} and investigated as '
                        'a transcription factor is 10 million usable fragments. '
                        'The recommended value is > 20 million, but > 10 million is '
                        'acceptable. (See {} )'.format(
                            file_to_check['output_type'],
                            audit_link(path_to_text(file_to_check['@id']), file_to_check['@id']),
                            pipeline_object['title'],
                            audit_link(path_to_text(pipeline_object['@id']), pipeline_object['@id']),
                            read_depth,
                            target_name,
                            audit_link('ENCODE ChIP-seq data standards', '/data-standards/chip-seq/')
                        )
                    )
                if read_depth >= marks['TF']['minimal'] and read_depth < marks['TF']['recommended']:
                    yield AuditFailure('low read depth', detail, level='WARNING')
                elif read_depth < marks['TF']['minimal'] and read_depth >= marks['TF']['low']:
                    yield AuditFailure('insufficient read depth',
                                       detail, level='NOT_COMPLIANT')
                elif read_depth < marks['TF']['low']:
                    yield AuditFailure('extremely low read depth',
                                       detail, level='ERROR')
    return


def check_file_read_depth(file_to_check,
                          read_depth,
                          upper_threshold,
                          middle_threshold,
                          lower_threshold,
                          assay_term_name,
                          pipeline_title,
                          pipeline,
                          standards_link):
    if read_depth is False:
        detail = ('Processed {} file {} has no read depth information.'.format(
            file_to_check['output_type'],
            audit_link(path_to_text(file_to_check['@id']), file_to_check['@id'])
            )
        )
        yield AuditFailure('missing read depth', detail, level='INTERNAL_ACTION')
        return

    if read_depth is not False:
        second_half_of_detail = ('The minimum ENCODE standard for each replicate in a '
            '{} assay is {} aligned reads. '
            'The recommended value is > {}. '
            '(See {} )'.format(
                assay_term_name,
                middle_threshold,
                upper_threshold,
                audit_link(('ENCODE ' + assay_term_name + ' data standards'), standards_link)
            )
        )
        if middle_threshold == upper_threshold:
            second_half_of_detail = ('The minimum ENCODE standard for each replicate in a '
                '{} assay is {} aligned reads. (See {} )'.format(
                    assay_term_name,
                    middle_threshold,
                    audit_link(('ENCODE ' + assay_term_name + ' data standards'), standards_link)
                )
            )
        if 'assembly' in file_to_check:
            detail = ('Processed {} file {} produced by {} '
                'pipeline ( {} ) using the {} assembly has {} aligned reads. {}'.format(
                    file_to_check['output_type'],
                    audit_link(path_to_text(file_to_check['@id']), file_to_check['@id']),
                    pipeline_title,
                    audit_link(path_to_text(pipeline['@id']), pipeline['@id']),
                    file_to_check['assembly'],
                    read_depth,
                    second_half_of_detail
                )
            )
        else:
            detail = ('Processed {} file {} produced by {} '
                'pipeline ( {} ) has {} aligned reads. {}'.format(
                    file_to_check['output_type'],
                    audit_link(path_to_text(file_to_check['@id']), file_to_check['@id']),
                    pipeline_title,
                    audit_link(path_to_text(pipeline['@id']), pipeline['@id']),
                    read_depth,
                    second_half_of_detail
                )
            )
        if read_depth >= middle_threshold and read_depth < upper_threshold:
            yield AuditFailure('low read depth', detail, level='WARNING')
        elif read_depth >= lower_threshold and read_depth < middle_threshold:
            yield AuditFailure('insufficient read depth', detail,
                               level='NOT_COMPLIANT')
        elif read_depth < lower_threshold:
            yield AuditFailure('extremely low read depth', detail,
                               level='ERROR')
    return


def check_file_platform(file_to_check, excluded_platforms):
    if 'platform' not in file_to_check:
        return
    elif file_to_check['platform'] in excluded_platforms:
        detail = ('Reads file {} has not compliant '
            'platform (SOLiD) {}.'.format(
                audit_link(path_to_text(file_to_check['@id']), file_to_check['@id']),
                file_to_check['platform']
            )
        )
        yield AuditFailure('not compliant platform', detail, level='WARNING')
    return


def check_file_read_length_chip(file_to_check,
                                upper_threshold_length,
                                medium_threshold_length,
                                lower_threshold_length):
    if 'read_length' not in file_to_check:
        detail = ('Reads file {} missing read_length'.format(
            audit_link(path_to_text(file_to_check['@id']), file_to_check['@id'])
            )
        )
        yield AuditFailure('missing read_length', detail, level='NOT_COMPLIANT')
        return

    read_length = file_to_check['read_length']
    detail = ('Fastq file {} '
        'has read length of {}bp. '
        'For mapping accuracy ENCODE standards recommend that sequencing reads should '
        'be at least {}bp long. (See {} )'.format(
            audit_link(path_to_text(file_to_check['@id']), file_to_check['@id']),
            read_length,
            upper_threshold_length,
            audit_link('ENCODE ChIP-seq data standards', '/data-standards/chip-seq/')
        )
    )
    if read_length < lower_threshold_length:
        yield AuditFailure('extremely low read length', detail, level='ERROR')
    elif read_length >= lower_threshold_length and read_length < medium_threshold_length:
        yield AuditFailure('insufficient read length', detail, level='NOT_COMPLIANT')
    elif read_length >= medium_threshold_length and read_length < upper_threshold_length:
        yield AuditFailure('low read length', detail, level='WARNING')
    return


def check_file_read_length_rna(file_to_check, threshold_length, pipeline_title, standard_link):
    if 'read_length' not in file_to_check:
        detail = ('Reads file {} missing read_length'.format(
            audit_link(path_to_text(file_to_check['@id']), file_to_check['@id'])
            )
        )
        yield AuditFailure('missing read_length', detail, level='NOT_COMPLIANT')
        return
    if file_to_check.get('read_length') < threshold_length:
        detail = ('Fastq file {} '
            'has read length of {}bp. '
            'ENCODE uniform processing pipeline standards '
            'require sequencing reads to be at least {}bp long. (See {} )'.format(
                audit_link(path_to_text(file_to_check['@id']), file_to_check['@id']),
                file_to_check.get('read_length'),
                threshold_length,
                audit_link('ENCODE ' + pipeline_title + ' data standards', standard_link)
            )
        )
        yield AuditFailure('insufficient read length', detail,
                           level='NOT_COMPLIANT')
    return


def audit_experiment_internal_tag(value, system, excluded_types):

    if value['status'] in ['deleted', 'replaced']:
        return

    experimental_tags = []
    if 'internal_tags' in value:
        experimental_tags = value['internal_tags']

    updated_experimental_tags = []
    for tag in experimental_tags:
        if tag in ['ENTEx', 'SESCC']:
            updated_experimental_tags.append(tag)

    experimental_tags = updated_experimental_tags
    biosamples = get_biosamples(value)
    bio_tags = set()

    for biosample in biosamples:
        if 'internal_tags' in biosample:
            for tag in biosample['internal_tags']:
                if tag in ['ENTEx', 'SESCC']:
                    bio_tags.add(tag)
                    if experimental_tags == []:
                        detail = ('This experiment contains a '
                            'biosample {} '
                            'with internal tag {}, '
                            'while the experiment has  '
                            'no internal_tags specified.'.format(
                                audit_link(path_to_text(biosample['@id']), biosample['@id']),
                                tag
                            )
                        )
                        yield AuditFailure('inconsistent internal tags',
                                           detail, level='INTERNAL_ACTION')
                    elif experimental_tags != [] and tag not in experimental_tags:
                        detail = ('This experiment contains a '
                            'biosample {} '
                            'with internal tag {} '
                            'that is not specified in experimental '
                            'list of internal_tags {}.'.format(
                                audit_link(path_to_text(biosample['@id']), biosample['@id']),
                                tag,
                                experimental_tags
                            )
                        )
                        yield AuditFailure('inconsistent internal tags',
                                           detail, level='INTERNAL_ACTION')

    if len(bio_tags) == 0 and len(experimental_tags) > 0:
        for biosample in biosamples:
            detail = ('This experiment contains a '
                'biosample {} without internal tags '
                'belonging to internal tags {} '
                'of the experiment.'.format(
                    audit_link(path_to_text(biosample['@id']), biosample['@id']),
                    experimental_tags
                )
            )
            yield AuditFailure('inconsistent internal tags',
                               detail, level='INTERNAL_ACTION')

    for biosample in biosamples:
        if len(bio_tags) > 0 and ('internal_tags' not in biosample or
                                  biosample['internal_tags'] == []):
            detail = ('This experiment contains a '
                'biosample {} with no internal tags '
                'belonging to internal tags {} '
                'other biosamples are assigned.'.format(
                    audit_link(path_to_text(biosample['@id']), biosample['@id']),
                    list(bio_tags)
                )
            )
            yield AuditFailure('inconsistent internal tags',
                               detail, level='INTERNAL_ACTION')
        elif len(bio_tags) > 0 and biosample['internal_tags'] != []:
            for x in bio_tags:
                if x not in biosample['internal_tags']:
                    detail = ('This experiment contains a '
                        'biosample {} without internal tag '
                        '{} belonging to internal tags {} '
                        'other biosamples are assigned.'.format(
                            audit_link(path_to_text(biosample['@id']), biosample['@id']),
                            x,
                            list(bio_tags)
                        )
                    )
                    yield AuditFailure('inconsistent internal tags',
                                       detail, level='INTERNAL_ACTION')
    return


def audit_experiment_geo_submission(value, system, excluded_types):
    if value['status'] not in ['released']:
        return
    if 'assay_term_id' in value and \
       value['assay_term_id'] in ['NTR:0000612',
                                  'OBI:0001923',
                                  'OBI:0002044']:
        return
    submitted_flag = False
    detail = ('Experiment {} is released,'
        ' but was not submitted to GEO.'.format(
            audit_link(path_to_text(value['@id']), value['@id'])
        )
    )
    if 'dbxrefs' in value and value['dbxrefs'] != []:
        for entry in value['dbxrefs']:
            if entry.startswith('GEO:'):
                submitted_flag = True
    if submitted_flag is False:
        detail = ('Experiment {} is released,'
            ' but is not submitted to GEO.'.format(
                audit_link(path_to_text(value['@id']), value['@id'])
            )
        )
        yield AuditFailure('experiment not submitted to GEO', detail, level='INTERNAL_ACTION')
    return


def audit_experiment_status(value, system, files_structure):
    if value['status'] not in ['in progress']:
        return
    assay_term_name = value.get('assay_term_name')
    if assay_term_name not in minimal_read_depth_requirements:
        return
    award_rfa = value.get('award', {}).get('rfa')
    if award_rfa == 'modERN':
        return
    if award_rfa == 'modENCODE' and assay_term_name != 'ChIP-seq':
        return
    replicates = value.get('replicates')
    if not replicates:
        return
    replicates_set = set()
    submitted_replicates = set()
    replicates_reads = {}
    bio_rep_reads = {}
    replicates_bio_index = {}
    for replicate in replicates:
        if replicate.get('status') not in ['deleted']:
            replicate_id = replicate.get('@id')
            replicates_set.add(replicate_id)
            replicates_reads[replicate_id] = 0
            replicates_bio_index[replicate_id] = replicate.get('biological_replicate_number')
            bio_rep_reads[replicates_bio_index[replicate_id]] = 0

    erroneous_status = ['uploading', 'content error', 'upload failed']
    for fastq_file in files_structure.get('fastq_files').values():
        if fastq_file.get('status') not in erroneous_status:
            file_replicate = fastq_file.get('replicate')
            read_count = fastq_file.get('read_count')
            if read_count and file_replicate:
                replicate_id = file_replicate.get('@id')
                submitted_replicates.add(replicate_id)
                if replicate_id in replicates_reads:
                    run_type = fastq_file.get('run_type')
                    if run_type and run_type == 'paired-ended':
                        read_count == read_count/2
                    replicates_reads[replicate_id] += read_count
                    bio_rep_reads[replicates_bio_index[replicate_id]] += read_count


    if replicates_set and not replicates_set - submitted_replicates:
        part_of_detail = 'replicate'
        if award_rfa == 'modENCODE':
            key = 'modENCODE-chip'
        else:
            key = assay_term_name
            if assay_term_name in [
                    'DNase-seq',
                    'genetic modification followed by DNase-seq',
                    'ChIP-seq',
                    'Mint-ChIP-seq']:
                replicates_reads = bio_rep_reads
                part_of_detail = 'biological replicate'

        for rep in replicates_reads:
            if replicates_reads[rep] < minimal_read_depth_requirements[key]:
                detail = ('The cumulative number of reads in '
                    '{} {} of experiment {} is {}. That is lower then '
                    'the minimal expected read depth of {} '
                    'for this type of assay.'.format(
                        part_of_detail,
                        rep,
                        audit_link(path_to_text(value['@id']), value['@id']),
                        replicates_reads[rep],
                        minimal_read_depth_requirements[key]
                    )
                )
                yield AuditFailure('low read count',
                                    detail, level='WARNING')


def audit_experiment_consistent_sequencing_runs(value, system, files_structure):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if not value.get('replicates'):
        return

    assay_term_name = value.get('assay_term_name')

    replicate_pairing_statuses = {}
    replicate_read_lengths = {}

    for file_object in files_structure.get('fastq_files').values():
        if 'replicate' in file_object:
            bio_rep_number = file_object['replicate']['biological_replicate_number']

            if 'read_length' in file_object:
                if bio_rep_number not in replicate_read_lengths:
                    replicate_read_lengths[bio_rep_number] = set()
                replicate_read_lengths[bio_rep_number].add(
                    file_object['read_length'])

            # run type consistency is relevant only for ChIP-seq
            if assay_term_name in ['Mint-ChIP-seq', 'ChIP-seq'] and 'run_type' in file_object:
                if bio_rep_number not in replicate_pairing_statuses:
                    replicate_pairing_statuses[bio_rep_number] = set()
                replicate_pairing_statuses[bio_rep_number].add(
                    file_object['run_type'])

    length_threshold = 2
    # different length threshold for DNase-seq and genetic modification followed by DNase-seq
    if value.get("assay_term_id") in ["OBI:0001853", "NTR:0004774"]:
        length_threshold = 9
    for key in replicate_read_lengths:
        if len(replicate_read_lengths[key]) > 1:
            upper_value = max(list(replicate_read_lengths[key]))
            lower_value = min(list(replicate_read_lengths[key]))
            if (upper_value - lower_value) > length_threshold:
                detail = ('Biological replicate {} '
                    'in experiment {} '
                    'has mixed sequencing read lengths {}.'.format(
                        key,
                        audit_link(path_to_text(value['@id']), value['@id']),
                        replicate_read_lengths[key]
                    )
                )
                yield AuditFailure('mixed read lengths',
                                   detail, level='WARNING')

    keys = list(replicate_read_lengths.keys())

    if len(keys) > 1:
        for index_i in range(len(keys)):
            for index_j in range(index_i + 1, len(keys)):
                i_lengths = list(replicate_read_lengths[keys[index_i]])
                j_lengths = list(replicate_read_lengths[keys[index_j]])

                i_max = max(i_lengths)
                i_min = min(i_lengths)
                j_max = max(j_lengths)
                j_min = min(j_lengths)

                diff_flag = False
                if (i_max - j_min) > length_threshold:
                    diff_flag = True
                if (j_max - i_min) > length_threshold:
                    diff_flag = True

                if diff_flag is True:
                    detail = ('Biological replicate {} '
                        'in experiment {} '
                        'has sequencing read lengths {} '
                        ' that differ from replicate {},'
                        ' which has {} sequencing read lengths.'.format(
                            keys[index_i],
                            audit_link(path_to_text(value['@id']), value['@id']),
                            i_lengths,
                            keys[index_j],
                            j_lengths
                        )
                    )
                    yield AuditFailure('mixed read lengths',
                                       detail, level='WARNING')

    # run type consistency is relevant only for ChIP-seq
    if assay_term_name in ['Mint-ChIP-seq', 'ChIP-seq']:
        for key in replicate_pairing_statuses:
            if len(replicate_pairing_statuses[key]) > 1:
                detail = ('Biological replicate {} '
                    'in experiment {} '
                    'has mixed endedness {}.'.format(
                        key,
                        audit_link(path_to_text(value['@id']), value['@id']),
                        replicate_pairing_statuses[key]
                    )
                )
                yield AuditFailure('mixed run types',
                                detail, level='WARNING')

        

        keys = list(replicate_pairing_statuses.keys())
        if len(keys) > 1:
            for index_i in range(len(keys)):
                for index_j in range(index_i + 1, len(keys)):
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
                        detail = ('Biological replicate {} '
                            'in experiment {} '
                            'has endedness {} '
                            ' that differ from replicate {},'
                            ' which has {}.'.format(
                                keys[index_i],
                                audit_link(path_to_text(value['@id']), value['@id']),
                                i_pairs,
                                keys[index_j],
                                j_pairs
                            )
                        )
                        yield AuditFailure('mixed run types',
                                        detail, level='WARNING')


def audit_experiment_replicate_with_no_files(value, system, excluded_statuses):
    if 'internal_tags' in value and 'DREAM' in value['internal_tags']:
        return

    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return
    if not value.get('replicates'):
        return

    seq_assay_flag = False
    if value['assay_term_name'] in seq_assays:
        seq_assay_flag = True

    rep_dictionary = {}
    rep_numbers = {}
    files_structure = create_files_mapping(
        value.get('original_files'),
        [x for x in excluded_statuses if x != 'archived'])

    for rep in value.get('replicates'):
        if rep['status'] in excluded_statuses:
            continue
        rep_dictionary[rep['@id']] = []
        rep_numbers[rep['@id']] = (rep['biological_replicate_number'],
                                   rep['technical_replicate_number'])

    for file_object in files_structure.get('original_files').values():
        file_replicate = file_object.get('replicate')
        if file_replicate:
            if file_replicate['@id'] in rep_dictionary:
                rep_dictionary[file_replicate['@id']].append(
                    file_object['output_category'])

    audit_level = 'ERROR'

    if check_award_condition(value, ["ENCODE2", "Roadmap",
                                     "modENCODE", "MODENCODE", "ENCODE2-Mouse"]):
        audit_level = 'INTERNAL_ACTION'

    for key in rep_dictionary.keys():

        if len(rep_dictionary[key]) == 0:
            detail = ('This experiment contains a replicate '
                '[{},{}] {} without any associated files.'.format(
                    rep_numbers[key][0],
                    rep_numbers[key][1],
                    audit_link(path_to_text(key), key)
                )
            )

            yield AuditFailure('missing raw data in replicate', detail, level=audit_level)
        else:
            if seq_assay_flag is True:
                if 'raw data' not in rep_dictionary[key]:
                    detail = ('This experiment contains a replicate '
                        '[{},{}] {} without raw data associated files.'.format(
                            rep_numbers[key][0],
                            rep_numbers[key][1],
                            audit_link(path_to_text(key), key)
                        )
                    )
                    yield AuditFailure('missing raw data in replicate',
                                       detail, level=audit_level)
    return


def audit_experiment_replicated(value, system, excluded_types):
    if not check_award_condition(value, [
            'ENCODE4', 'ENCODE3', 'GGR']):
        return
    '''
    Experiments in submitted state should be replicated. If not,
    wranglers should check with lab as to why before release.
    '''
    if value['status'] not in ['released', 'submitted']:
        return
    '''
    Excluding single cell isolation experiments from the replication requirement
    Excluding RNA-bind-and-Seq from the replication requirment
    Excluding genetic modification followed by DNase-seq from the replication requirement
    '''
    if value['assay_term_name'] in ['single-cell RNA sequencing assay',
                                    'RNA Bind-n-Seq',
                                    'genetic modification followed by DNase-seq']:
        return
    '''
    Excluding GTEX experiments from the replication requirement
    '''
    if is_gtex_experiment(value) is True:
        return

    if value.get('control_type'):
        return

    num_bio_reps = set()
    for rep in value['replicates']:
        num_bio_reps.add(rep['biological_replicate_number'])

    if len(num_bio_reps) == 0:
        detail = ('This experiment is expected to be replicated, but '
            'currently does not have any replicates associated with it.')
        yield AuditFailure('unreplicated experiment', detail, level='NOT_COMPLIANT')

    if len(num_bio_reps) == 1:
        '''
        Excluding single cell experiments
        '''
        if value['biosample_ontology']['classification'] == 'single cell':
            return
        # different levels of severity for different biosample classifications
        else:
            detail = ('This experiment is expected to be replicated, but '
                'contains only one listed biological replicate.')
            level='NOT_COMPLIANT'
            if value['biosample_ontology']['classification'] in ['tissue', 'primary cell']:
                level='INTERNAL_ACTION'
            yield AuditFailure('unreplicated experiment', detail, level)
    return


def audit_experiment_replicates_with_no_libraries(value, system, excluded_types):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return
    if len(value['replicates']) == 0:
        return
    for rep in value['replicates']:
        if rep.get('status') not in excluded_types and 'library' not in rep:
            detail = ('Experiment {} has a replicate {},'
                ' that has no library associated with'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    audit_link(path_to_text(rep['@id']), rep['@id'])
                )
            )
            yield AuditFailure('replicate with no library', detail, level='ERROR')
    return


def audit_experiment_isogeneity(value, system, excluded_types):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return
    if value.get('replication_type') is None:
        detail = ('In experiment {} the replication_type'
            ' cannot be determined'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
            )
        )
        yield AuditFailure('undetermined replication_type', detail, level='INTERNAL_ACTION')
    if len(value['replicates']) < 2:
        return

    biosample_dict = {}
    biosample_age_set = set()
    biosample_sex_set = set()
    biosample_donor_set = set()

    for rep in value['replicates']:
        if 'library' in rep:
            if 'biosample' in rep['library']:
                biosampleObject = rep['library']['biosample']
                biosample_dict[biosampleObject['accession']] = biosampleObject
                biosample_age_set.add(biosampleObject.get('age_display'))
                biosample_sex_set.add(biosampleObject.get('sex'))
                biosample_species = biosampleObject.get('organism')
                if biosampleObject.get('donor'):
                    biosample_donor_set.add(
                        biosampleObject.get('donor')['@id'])
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

    if len(biosample_donor_set) > 1:
        donors_list_link = [audit_link(path_to_text(d), d) for d in biosample_donor_set]
        detail = ('Replicates of this experiment were prepared using biosamples '
                 'from different strains {}.'.format(', '.join(donors_list_link)))
        yield AuditFailure('inconsistent donor', detail, level='ERROR')

    if len(biosample_age_set) > 1:
        ages_list = str(list(biosample_age_set)).replace('\'', ' ')
        detail = ('Replicates of this experiment were prepared using biosamples '
                 'of different ages {}.'.format(ages_list))
        yield AuditFailure('inconsistent age', detail, level='NOT_COMPLIANT')

    if len(biosample_sex_set) > 1:
        sexes_list = str(list(biosample_sex_set)).replace('\'', ' ')
        detail = ('Replicates of this experiment were prepared using biosamples '
                 'of different sexes {}.'.format(sexes_list))
        yield AuditFailure('inconsistent sex', detail, level='NOT_COMPLIANT')
    return


def audit_experiment_technical_replicates_same_library(value, system, excluded_types):
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
                detail = ('Experiment {} has different technical replicates'
                    ' associated with the same library'.format(
                        audit_link(path_to_text(value['@id']), value['@id'])
                    )
                )
                yield AuditFailure('sequencing runs labeled as technical replicates', detail,
                                   level='INTERNAL_ACTION')
                return
            else:
                biological_replicates_dict[bio_rep_num].append(
                    library['accession'])
    return


def audit_experiment_tagging_genetic_modification(value, system, excluded_types):
    if check_award_condition(value, ["ENCODE4"]) and value.get('assay_term_name') == 'ChIP-seq':
        level = 'ERROR'
    else:
        level = 'WARNING'
    if 'replicates' in value:
        mods = []
        mods_ids = []
        for rep in value['replicates']:
            if (rep['status'] not in excluded_types and
               'library' in rep and
               rep['library']['status'] not in excluded_types and
               'biosample' in rep['library'] and
               rep['library']['biosample']['status'] not in excluded_types):
                biosample = rep['library']['biosample']
                if 'applied_modifications' in biosample:
                    for m in biosample['applied_modifications']:
                        if m['@id'] not in mods_ids:
                            mods_ids.append(m['@id'])
                            mods.append(m)
        for modification in mods:
            if (modification['status'] not in excluded_types and
                modification['purpose'] == 'tagging' and
                not modification.get('characterizations')):
                    detail = ('Genetic modification {} performed for the '
                        'purpose of {} is missing validating characterization.'.format(
                            audit_link(path_to_text(modification['@id']), modification['@id']),
                            modification['purpose']
                        )
                    )
                    yield AuditFailure(
                        'missing genetic modification characterization',
                        detail,
                        level
                    )


def is_tagging_genetic_modification(modification):
    if modification['purpose'] == 'tagging':
        return True
    return False


def audit_experiment_biosample_characterization(value, system, excluded_types):
    missing_characterizations = []
    characterization_status = {}
    needs_characterization_flags = []
    # First check and collect necessary biosample characterizations
    for rep in value.get('replicates', []):
        if rep['status'] in excluded_types:
            continue
        if 'library' not in rep or rep['library']['status'] in excluded_types:
            continue
        if (
            'biosample' not in rep['library']
            or rep['library']['biosample']['status'] in excluded_types
        ):
            continue
        biosample = rep['library']['biosample']
        needs_characterization_flag = False
        modifications = biosample.get('applied_modifications')
        if not modifications:
            needs_characterization_flags.append(needs_characterization_flag)
            continue
        mods = []
        for mod in modifications:
            mods.append(mod['@id'])
            if is_tagging_genetic_modification(mod):
                needs_characterization_flag = True
        needs_characterization_flags.append(needs_characterization_flag)
        sample_characterization_status = {}
        for characterization in biosample.get('characterizations', []):
            status = characterization.get('review', {}).get('status')
            sample_characterization_status.setdefault(status, [])
            sample_characterization_status[status].append(biosample['@id'])
        # Need to have all parents characterized if relying on pool parents
        if (
            not sample_characterization_status
            and biosample.get('pooled_from')
            and all(
                parent.get('characterizations')
                for parent in biosample['pooled_from']
            )
        ):
            # Summarize pool parent characterization and give one status
            parent_characterization_status = {
                c.get('review', {}).get('status')
                for parent in biosample.get('pooled_from', [])
                for c in parent['characterizations']
            }
            if 'not compliant' in parent_characterization_status:
                sample_characterization_status['not compliant'] = [
                    biosample['@id']
                ]
            elif None in parent_characterization_status:
                sample_characterization_status[None] = [
                    biosample['@id']
                ]
            elif 'requires secondary opinion' in parent_characterization_status:
                sample_characterization_status['requires secondary opinion'] = [
                    biosample['@id']
                ]
            elif 'exempt from standards' in parent_characterization_status:
                sample_characterization_status['exempt from standards'] = [
                    biosample['@id']
                ]
            elif 'compliant' in parent_characterization_status:
                sample_characterization_status['compliant'] = [
                    biosample['@id']
                ]
        if sample_characterization_status:
            for status in sample_characterization_status:
                characterization_status.setdefault(status, [])
                characterization_status[status].extend(
                    sample_characterization_status[status]
                )
            continue
        missing_characterizations.append((biosample['@id'], mods))

    # Build audits
    level = 'WARNING'
    if (
        value.get('assay_term_name') == 'ChIP-seq'
        and any(needs_characterization_flags)
        and check_award_condition(value, ["ENCODE4"])
    ):
        level = 'ERROR'
    # There are no characterizations at all for the whole experiment
    # Build missing characterizations audit if needed and return anyway
    if not characterization_status:
        for biosample_id, mods in missing_characterizations:
            detail = (
                'Biosample {} which has been modified by genetic modification '
                '{} is missing characterization validating the '
                'modification.'.format(
                    audit_link(path_to_text(biosample_id), biosample_id),
                    ', '.join(
                        audit_link(path_to_text(mod), mod) for mod in mods
                    ),
                )
            )
            yield AuditFailure(
                'missing biosample characterization', detail, level
            )
        return

    # Has characterizations and check their review status
    if 'not compliant' in characterization_status:
        multi_characterizations = len(
            characterization_status['not compliant']
        ) > 1
        detail = 'Biosample {} {} not compliant characterization'.format(
            ', '.join(
                audit_link(path_to_text(biosample_id), biosample_id)
                for biosample_id in characterization_status['not compliant']
            ),
            'have' if multi_characterizations else 'has',
        )
        yield AuditFailure(
            'not compliant biosample characterization', detail, level
        )
    if (
        'compliant' not in characterization_status
        and 'exempt from standards' not in characterization_status
    ):
        biosample_ids = set(
            characterization_status.get(None, [])
            + characterization_status.get('requires secondary opinion', [])
        )
        if biosample_ids:
            detail = (
                'Characterization for biosample {} has not finished '
                'review'.format(
                    ', '.join(
                        audit_link(path_to_text(biosample_id), biosample_id)
                        for biosample_id in biosample_ids
                    )
                )
            )
            yield AuditFailure(
                'missing compliant biosample characterization', detail, level
            )


def audit_experiment_replicates_biosample(value, system, excluded_types):
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
                    detail = ('Experiment {} has multiple biological replicates '
                        'associated with the same biosample {}'.format(
                            audit_link(path_to_text(value['@id']), value['@id']),
                            audit_link(path_to_text(biosample['@id']), biosample['@id'])
                        )
                    )
                    yield AuditFailure('biological replicates with identical biosample',
                                       detail, level='INTERNAL_ACTION')
                    return
                else:
                    biosamples_list.append(biosample['accession'])

            else:
                if biosample['accession'] != biological_replicates_dict[bio_rep_num] and \
                   assay_name != 'single-cell RNA sequencing assay':
                    detail = ('Experiment {} has technical replicates '
                        'associated with the different biosamples'.format(
                            audit_link(path_to_text(value['@id']), value['@id'])
                        )
                    )
                    yield AuditFailure('technical replicates with not identical biosample',
                                       detail, level='ERROR')
                    return
    return


def audit_experiment_documents(value, system, excluded_types):
    if not check_award_condition(value, [
            "ENCODE3", "modERN", "GGR", "ENCODE4",
            "ENCODE", "ENCODE2-Mouse", "Roadmap"]):
        return
    '''
    Experiments should have documents.  Protocol documents or some sort of document.
    '''
    if value['status'] in ['deleted', 'replaced']:
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
        detail = ('Experiment {} has no attached documents'.format(
            audit_link(value['accession'], value['@id'])
            )
        )
        yield AuditFailure('missing documents', detail, level='NOT_COMPLIANT')
    return


def audit_experiment_target(value, system, excluded_types):
    '''
    Certain assay types (ChIP-seq, ...) require valid targets and the replicate's
    antibodies should match.
    '''

    if value['status'] in ['deleted']:
        return

    if value.get('assay_term_name') not in targetBasedAssayList:
        return

    # ENCD-4674 control target assays (ChIP-seq, etc) can be no target
    if value.get('control_type'):
        return

    if 'target' not in value:
        detail = ('{} experiments require a target'.format(
            value['assay_term_name'])
        )
        yield AuditFailure('missing target', detail, level='ERROR')
        return

    target = value['target']

    # Experiment target should be untagged
    non_tag_mods = ['Methylation',
                    'Monomethylation',
                    'Dimethylation',
                    'Trimethylation',
                    'Acetylation',
                    'Ubiquitination',
                    'Phosphorylation']
    if any(mod['modification'] not in non_tag_mods
           for mod in target.get('modifications', [])
           if 'modification' in mod):
        detail = ('Experiment {} has a tagged target {}. Should consider using '
            'untagged target version for experiment.'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                audit_link(path_to_text(target['@id']), target['@id'])
            )
        )
        yield AuditFailure('inconsistent experiment target', detail, level='WARNING')

    # Some assays don't need antibodies
    if value['assay_term_name'] in ['RNA Bind-n-Seq',
                                    'shRNA knockdown followed by RNA-seq',
                                    'siRNA knockdown followed by RNA-seq',
                                    'CRISPRi followed by RNA-seq',
                                    'CRISPR genome editing followed by RNA-seq']:
        return

    for rep in value['replicates']:
        # Check target of experiment matches target of genetic modifications
        biosample = rep.get('library', {}).get('biosample', {})
        modifications = biosample.get('applied_modifications', [])
        if modifications:
            if all(mod['modified_site_by_target_id']['@id'] != target['@id']
                   for mod in modifications
                   if 'modified_site_by_target_id' in mod):
                detail = ('This experiment {} targeting {} has a '
                          'biosample {} with no genetic modification targeting {}.')
                yield AuditFailure(
                    'inconsistent genetic modification targets',
                    (detail.format(
                        audit_link(path_to_text(value['@id']), value['@id']),
                        audit_link(path_to_text(target['@id']), target['@id']),
                        audit_link(path_to_text(biosample['@id']), biosample['@id']),
                        audit_link(path_to_text(target['@id']), target['@id']))),
                    level='INTERNAL_ACTION'
                )
        # Check that target of experiment matches target of antibody
        if 'antibody' not in rep:
            detail = ('{} assays require an antibody specification. '
                'In replicate [{}, {}] {}, the antibody needs to be specified.'.format(
                    value['assay_term_name'],
                    rep['biological_replicate_number'],
                    rep['technical_replicate_number'],
                    audit_link(path_to_text(rep['@id']), rep['@id']),
                )
            )
            yield AuditFailure('missing antibody', detail, level='ERROR')
        else:
            antibody = rep['antibody']
            unique_antibody_target = set()
            unique_investigated_as = set()
            for antibody_target in antibody.get('targets', []):
                label = antibody_target['label']
                unique_antibody_target.add(label)
                for investigated_as in antibody_target['investigated_as']:
                    unique_investigated_as.add(investigated_as)
            if ('tag' not in unique_investigated_as
                  and 'synthetic tag' not in unique_investigated_as):
                # Target matching for tag antibody is only between antibody and
                # genetic modification within replicate after ENCD-4425.
                target_matches = False
                antibody_targets = []
                for antibody_target in antibody.get('targets', []):
                    antibody_targets.append(antibody_target.get('name'))
                    if target['name'] == antibody_target.get('name'):
                        target_matches = True
                if not target_matches:
                    antibody_targets_string = str(
                        antibody_targets).replace('\'', '')
                    detail = ('The target of the experiment is {}, '
                        'but it is not present in the experiment\'s antibody {} '
                        'target list {}.'.format(
                            target['name'],
                            audit_link(path_to_text(antibody['@id']), antibody['@id']),
                            antibody_targets_string
                        )
                    )
                    yield AuditFailure('inconsistent target', detail, level='ERROR')
    return


def audit_experiment_control(value, system, excluded_types):
    if not check_award_condition(value, [
            "ENCODE3", "ENCODE4", "modERN", "ENCODE2", "modENCODE",
            "ENCODE", "ENCODE2-Mouse", "Roadmap"]):
        return

    '''
    Certain assay types (ChIP-seq, ...) require possible controls with a matching biosample.
    Of course, controls do not require controls.
    '''

    if value['status'] in ['deleted', 'replaced']:
        return

    if value.get('assay_term_name') not in controlRequiredAssayList:
        return

    # single cell RNA-seq in E4 do not require controls (ticket WOLD-6)
    # single cell RNA-seq in E3 also do not require controls (ENCD-4984, WOLD-52)
    if value.get('assay_term_name') == 'single-cell RNA sequencing assay' and \
            check_award_condition(value, [
                "ENCODE4",
                "ENCODE3",
                ]
            ):
        return

    # We do not want controls
    if value.get('control_type'):
        return

    audit_level = 'ERROR'
    if value.get('assay_term_name') in ['CAGE',
                                        'RAMPAGE'] or \
        check_award_condition(value, ["ENCODE2",
                                      "Roadmap",
                                      "modENCODE",
                                      "ENCODE2-Mouse"]):
        audit_level = 'NOT_COMPLIANT'
    if value['possible_controls'] == []:
        detail = ('possible_controls is a list of experiment(s) that can '
            'serve as analytical controls for a given experiment. '
            '{} experiments require a value in possible_controls. '
            'This experiment should be associated with at least one control '
            'experiment, but has no specified values in the possible_controls list.'.format(
            value['assay_term_name']
            )
        )
        yield AuditFailure('missing possible_controls', detail, level=audit_level)

    for control in value['possible_controls']:
        # https://encodedcc.atlassian.net/browse/ENCD-5071
        if 'Series' in control['@type'] or control['@type'][0] == 'Project':
            for each in control['biosample_ontology']:
                if each.get('term_id') != value.get('biosample_ontology', {}).get('term_id'):
                    detail = ('The specified control {} '
                    'for this experiment is on {}, '
                    'but this experiment is done on {}.'.format(
                        audit_link(path_to_text(control['@id']), control['@id']),
                        each.get('term_name'),
                        value['biosample_ontology']['term_name']
                        )
                    )
                    yield AuditFailure('inconsistent control', detail, level='ERROR')

        else:
            if not is_matching_biosample_control(
                control, value.get('biosample_ontology', {}).get('term_id')):
                detail = ('The specified control {} '
                    'for this experiment is on {}, '
                    'but this experiment is done on {}.'.format(
                        audit_link(path_to_text(control['@id']), control['@id']),
                        control.get('biosample_ontology', {}).get('term_name'),
                        value['biosample_ontology']['term_name']
                    )
                )
                yield AuditFailure('inconsistent control', detail, level='ERROR')
            return


def is_matching_biosample_control(dataset, biosample_term_id):
    if dataset['@type'][0] in ['Experiment', 'Annotation']:
        return dataset.get('biosample_ontology', {}).get('term_id') == biosample_term_id
    elif (not dataset.get('biosample_ontology') or
         any([term['term_id'] != biosample_term_id
              for term in dataset.get('biosample_ontology')])):
            return False
    return True


def audit_experiment_platforms_mismatches(value, system, files_structure):
    if value['status'] in ['deleted', 'replaced']:
        return

    # do not apply the audit to DNase-seq and genetic modification followed by DNase-seq
    if value.get("assay_term_id") in ["OBI:0001853", "NTR:0004774"]:
        return

    if not files_structure.get('original_files'):
        return

    platforms = get_platforms_used_in_experiment(files_structure)
    if len(platforms) > 1:
        platforms_string = str(list(platforms)).replace('\'', '')
        detail = ('This experiment '
            'contains data produced on incompatible '
            'platforms {}.'.format(platforms_string))
        yield AuditFailure('inconsistent platforms', detail, level='WARNING')
    elif len(platforms) == 1:
        platform_term_name = list(platforms)[0]
        if 'possible_controls' in value and \
           value['possible_controls'] != []:
            for control in value['possible_controls']:
                if control.get('original_files'):
                    control_platforms = get_platforms_used_in_experiment(
                        create_files_mapping(control.get('original_files'), files_structure.get('excluded_types')))
                    if len(control_platforms) > 1:
                        control_platforms_string = str(
                            list(control_platforms)).replace('\'', '')
                        detail = ('possible_controls is a list of experiment(s) that can serve '
                            'as analytical controls for a given experiment. '
                            'Experiment {} found in possible_controls list of this experiment '
                            'contains data produced on platform(s) {} '
                            'which are not compatible with platform {} '
                            'used in this experiment.'.format(
                                audit_link(path_to_text(control['@id']), control['@id']),
                                control_platforms_string,
                                platform_term_name
                            )
                        )
                        yield AuditFailure('inconsistent platforms', detail, level='WARNING')
                    elif len(control_platforms) == 1 and \
                            list(control_platforms)[0] != platform_term_name:
                        detail = ('possible_controls is a list of experiment(s) that can serve '
                            'as analytical controls for a given experiment. '
                            'Experiment {} found in possible_controls list of this experiment '
                            'contains data produced on platform {} '
                            'which is not compatible with platform {} '
                            'used in this experiment.'.format(
                                audit_link(path_to_text(control['@id']), control['@id']),
                                list(control_platforms)[0],
                                platform_term_name
                            )
                        )
                        yield AuditFailure('inconsistent platforms', detail, level='WARNING')
    return


def audit_experiment_ChIP_control(value, system, files_structure):
    if not check_award_condition(value, [
            'ENCODE3', 'ENCODE4', 'Roadmap']):
        return

    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    # Currently controls are only be required for ChIP-seq
    if value.get('assay_term_name') not in ['Mint-ChIP-seq', 'ChIP-seq']:
        return

    # We do not want controls
    if value.get('control_type'):
        return

    if not value['possible_controls']:
        return

    tagged = value.get('protein_tags')
    has_input_control = False
    has_wt_control = False

    for control_dataset in value['possible_controls']:
        control_type = control_dataset.get('control_type')
        if not control_type:
            detail = (
                'Experiment {} is ChIP-seq but its control {} does not '
                'have a valid "control_type".'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    audit_link(path_to_text(control_dataset['@id']), control_dataset['@id'])
                )
            )
            yield AuditFailure('invalid possible_control', detail, level='ERROR')
            return

        if control_type == 'input library':
            has_input_control = True

        if control_type == 'wild type':
            has_wt_control = True

        if has_input_control and has_wt_control:
            break

    if (not has_input_control) and (not tagged):
        detail = (
            'ChIP-seq experiment {} is required to specify at least one '
            '"input library" control experiment. None of the experiments '
            'listed as possible controls ({}) satisfied this '
            'requirement.'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                ', '.join(
                    audit_link(path_to_text(ctrl['@id']), ctrl['@id'])
                    for ctrl in value['possible_controls']
                )
            )
        )
        yield AuditFailure(
            'missing input control', detail, level='NOT_COMPLIANT'
        )

    if tagged and (not has_wt_control) and (not has_input_control):
        detail = (
            'Epitope-tagged ChIP-seq experiment {} is required to specify '
            'either "input library" or "wild-type" as a control experiment. '
            'None of the experiments listed as possible controls ({}) '
            'satisfied this requirement.'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                ', '.join(
                    audit_link(path_to_text(ctrl['@id']), ctrl['@id'])
                    for ctrl in value['possible_controls']
                )
            )
        )
        yield AuditFailure(
            'missing input control', detail, level='NOT_COMPLIANT'
        )


def audit_experiment_spikeins(value, system, excluded_types):
    if not check_award_condition(value, [
            "ENCODE3",
            "ENCODE4",
            "modERN",
            "ENCODE",
            "ENCODE2-Mouse",
            "Roadmap"]):
        return
    '''
    All ENCODE 3 long (>200) RNA-seq experiments should specify their spikeins.
    The spikeins specified should have datasets of type spikeins.
    The spikeins datasets should have a fasta file, a document, and maybe a tsv
    '''

    if value['status'] in ['deleted', 'replaced']:
        return

    if value.get('assay_term_name') not in ['RNA-seq', 'polyA plus RNA-seq', 'polyA minus RNA-seq']:
        return

    for rep in value['replicates']:

        lib = rep.get('library')
        if lib is None:
            continue

        if check_library_for_long_fragments(lib) is False:
            continue
        spikes = lib.get('spikeins_used')
        if (spikes is None) or (spikes == []):
            detail = ('Library {} is in '
                'an RNA-seq experiment and has an average fragment size or size_range >200. '
                'It requires a value for spikeins_used'.format(
                    audit_link(path_to_text(lib['@id']), lib['@id'])
                )
            )
            yield AuditFailure('missing spikeins', detail, level='NOT_COMPLIANT')
            # Informational if ENCODE2 and release error if ENCODE3
    return


def check_library_for_long_fragments(library):
    if 'size_range' in library:
        size_range = library.get('size_range')
        if size_range != '>200':
            return False
        else:
            return True
    elif 'average_fragment_size' in library:
        size_range = library.get('average_fragment_size')
        if size_range <= 200:
            return False
        else:
            return True
    else:
        return False


def audit_experiment_biosample_term(value, system, excluded_types):
    if value['status'] in ['deleted', 'replaced']:
        return

    if value.get('biosample_ontology', {}).get('classification') in ('cell-free sample', 'cloning host'):
        return

    ontology = system['registry']['ontology']
    term_id = value.get('biosample_ontology', {}).get('term_id')
    term_type = value.get('biosample_ontology', {}).get('classification')
    term_name = value.get('biosample_ontology', {}).get('term_name')

    if 'biosample_ontology' not in value:
        detail = ('Biosample {} is missing biosample_ontology'.format(
            audit_link(path_to_text(value['@id']), value['@id']))
        )
        yield AuditFailure('missing biosample_ontology', detail, level='ERROR')
    # The type and term name should be put into dependencies

    if term_id.startswith('NTR:'):
        detail = ('Experiment {} has an NTR biosample {} - {}'.format(
            audit_link(path_to_text(value['@id']), value['@id']),
            term_id,
            term_name)
        )
        yield AuditFailure('NTR biosample', detail, level='INTERNAL_ACTION')
    else:
        if term_id not in ontology:
            detail = ('Experiment {} has term_id {} which is not in ontology'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                term_id)
            )
            yield AuditFailure('term_id not in ontology', detail, level='INTERNAL_ACTION')
        else:
            ontology_name = ontology[term_id]['name']
            if ontology_name != term_name and term_name not in ontology[term_id]['synonyms']:
                detail = ('Experiment {} has a mismatch between biosample term_id ({}) '
                    'and term_name ({}), ontology term_name for term_id {} '
                    'is {}.'.format(
                        audit_link(path_to_text(value['@id']), value['@id']),
                        term_id,
                        term_name,
                        term_id,
                        ontology_name
                    )
                )
                yield AuditFailure('inconsistent ontology term', detail, level='ERROR')

    if 'replicates' in value:
        for rep in value['replicates']:
            if 'library' not in rep:
                continue

            lib = rep['library']
            if 'biosample' not in lib:
                detail = ('Library {} is missing biosample, expecting one of type {}'.format(
                    audit_link(path_to_text(lib['@id']), lib['@id']),
                    term_name)
                )
                yield AuditFailure('missing biosample', detail, level='ERROR')
                continue

            biosample = lib['biosample']
            bs_type = biosample.get('biosample_ontology', {}).get('@id')
            bs_name = biosample.get('biosample_ontology', {}).get('name')
            experiment_bs_type = value.get('biosample_ontology', {}).get('@id')
            experiment_bs_name = value.get('biosample_ontology', {}).get('name')
            if bs_type != experiment_bs_type:
                detail = ("Experiment {} contains a library {} linked to biosample "
                    "type '{}', while experiment's biosample type is '{}'.".format(
                        audit_link(path_to_text(value['@id']), value['@id']),
                        audit_link(path_to_text(lib['@id']), lib['@id']),
                        audit_link(path_to_text(bs_type), bs_type),
                        audit_link(path_to_text(experiment_bs_type), experiment_bs_type)
                    )
                )
                yield AuditFailure('inconsistent library biosample', detail, level='ERROR')
    return


def audit_experiment_antibody_characterized(value, system, excluded_types):
    '''Check that biosample in the experiment has been characterized for the given antibody.'''
    if not check_award_condition(value, [
            'ENCODE4', 'ENCODE3', 'modERN']):
        return

    if value['status'] in ['deleted']:
        return

    if value.get('assay_term_name') not in targetBasedAssayList:
        return

    target = value.get('target')
    if not target:
        return

    if value.get('control_type'):
        return

    if value['assay_term_name'] in ['RNA Bind-n-Seq',
                                    'shRNA knockdown followed by RNA-seq',
                                    'siRNA knockdown followed by RNA-seq',
                                    'CRISPRi followed by RNA-seq']:
        return

    for rep in value['replicates']:
        antibody = rep.get('antibody')
        lib = rep.get('library')

        if not antibody or not lib:
            continue

        biosample = lib.get('biosample')
        if not biosample:
            continue

        organism = biosample.get('organism')
        antibody_targets = antibody.get('targets', [])
        ab_targets_investigated_as = set()
        sample_match = False

        for t in antibody_targets:
            for i in t['investigated_as']:
                ab_targets_investigated_as.add(i)

        characterized = bool(antibody['characterizations'])
        # ENCODE4 tagged antibodies are characterized differently (ENCD-4608)
        if (
            'tag' in ab_targets_investigated_as
            or 'synthetic tag' in ab_targets_investigated_as
        ):
            ab_award = system.get('request').embed(
                antibody['award'], '@@object?skip_calculated=true'
            )['rfa']
            if ab_award == 'ENCODE4':
                characterized = bool(
                    antibody['used_by_biosample_characterizations']
                )
            elif ab_award == 'ENCODE3':
                characterized = characterized or bool(
                    antibody['used_by_biosample_characterizations']
                )

        if not characterized:
            detail = ('Antibody {} has not yet been characterized in any cell type or tissue in {}.'.format(
                audit_link(path_to_text(antibody['@id']), antibody['@id']),
                path_to_text(organism)
                )
            )
            yield AuditFailure('uncharacterized antibody', detail, level='NOT_COMPLIANT')
            return

        # We only want the audit raised if the organism in lot reviews matches that of the biosample
        # and if has not been characterized to standards. Otherwise, it doesn't apply and we
        # shouldn't raise a stink

        if 'histone' in ab_targets_investigated_as:
            for lot_review in antibody['lot_reviews']:
                if lot_review['organisms'] and organism == lot_review['organisms'][0]:
                    sample_match = True
                    if lot_review['status'] == 'characterized to standards with exemption':
                        detail = ('Antibody {} has been characterized '
                            'to the standard with exemption for {}'.format(
                                audit_link(path_to_text(antibody['@id']), antibody['@id']),
                                path_to_text(organism)
                            )
                        )
                        yield AuditFailure('antibody characterized with exemption',
                                           detail, level='WARNING')
                    elif lot_review['status'] == 'awaiting characterization':
                        detail = ('Antibody {} has not yet been characterized in '
                            'any cell type or tissue in {}'.format(
                                audit_link(path_to_text(antibody['@id']), antibody['@id']),
                                path_to_text(organism)
                            )
                        )
                        yield AuditFailure('uncharacterized antibody',
                                           detail, level='NOT_COMPLIANT')
                    elif lot_review['status'] in ['not characterized to standards', 'not pursued']:
                        detail = ('Antibody {} has not been '
                            'characterized to the standard for {}: {}'.format(
                                audit_link(path_to_text(antibody['@id']), antibody['@id']),
                                path_to_text(organism),
                                lot_review['detail']
                            )
                        )
                        yield AuditFailure('antibody not characterized to standard', detail,
                                           level='NOT_COMPLIANT')
                    elif lot_review['status'] in ['pending dcc review',
                                                  'partially characterized']:
                        detail = ('Antibody {} has characterization attempts '
                            'but does not have the full complement of characterizations '
                            'meeting the standard in {}: {}'.format(
                                audit_link(path_to_text(antibody['@id']), antibody['@id']),
                                path_to_text(organism),
                                lot_review['detail']
                            )
                        )
                        yield AuditFailure('partially characterized antibody',
                                           detail, level='NOT_COMPLIANT')
                    else:
                        # This should only leave the characterized to standards case
                        pass
        else:
            biosample_term_id = value['biosample_ontology']['term_id']
            biosample_term_name = value['biosample_ontology']['term_name']
            experiment_biosample = (biosample_term_id, organism)

            for lot_review in antibody['lot_reviews']:
                biosample_key = (
                    lot_review['biosample_term_id'],
                    lot_review['organisms'][0] if lot_review['organisms'] else None
                )
                if experiment_biosample == biosample_key:
                    sample_match = True
                    if lot_review['status'] == 'characterized to standards with exemption':
                        detail = ('Antibody {} has been characterized to the '
                            'standard with exemption for {} in {}'.format(
                                audit_link(path_to_text(antibody['@id']), antibody['@id']),
                                biosample_term_name,
                                path_to_text(organism)
                            )
                        )
                        yield AuditFailure('antibody characterized with exemption', detail,
                                           level='WARNING')
                    elif lot_review['status'] == 'awaiting characterization':
                        detail = ('Antibody {} has not been characterized at al for {} in {}'.format(
                            audit_link(path_to_text(antibody['@id']), antibody['@id']),
                            biosample_term_name,
                            path_to_text(organism)
                            )
                        )
                        yield AuditFailure('uncharacterized antibody',
                                           detail, level='NOT_COMPLIANT')
                    elif lot_review['status'] in ['partially characterized', 'pending dcc review']:
                        detail = ('Antibody {} has characterization attempts '
                            'but does not have the full complement of characterizations '
                            'meeting the standard in {}: {}'.format(
                                audit_link(path_to_text(antibody['@id']), antibody['@id']),
                                path_to_text(organism),
                                lot_review['detail']
                            )
                        )
                        yield AuditFailure('partially characterized antibody',
                                           detail, level='NOT_COMPLIANT')
                    elif lot_review['status'] in ['not characterized to standards', 'not pursued']:
                        detail = ('Antibody {} has not been '
                            'characterized to the standard for {}: {}'.format(
                                audit_link(path_to_text(antibody['@id']), antibody['@id']),
                                path_to_text(organism),
                                lot_review['detail']
                            )
                        )
                        yield AuditFailure('antibody not characterized to standard', detail,
                                           level='NOT_COMPLIANT')
                    else:
                        # This should only leave the characterized to standards case
                        pass

            # The only characterization present is a secondary or an incomplete primary that
            # has no characterization_reviews since we don't know what the biosample is
            if not sample_match:
                detail = ('Antibody {} has characterization attempts '
                    'but does not have the full complement of characterizations '
                    'meeting the standard in this cell type and organism: Awaiting '
                    'submission of primary characterization(s).'.format(
                        audit_link(path_to_text(antibody['@id']), antibody['@id'])
                    )
                )
                yield AuditFailure('partially characterized antibody', detail,
                                   level='NOT_COMPLIANT')
    return


def audit_experiment_library_biosample(value, system, excluded_types):
    if value['status'] in ['deleted', 'replaced']:
        return

    if value.get('assay_term_name') == 'RNA Bind-n-Seq':
        return
    for rep in value['replicates']:
        if 'library' not in rep:
            continue

        lib = rep['library']
        if 'biosample' not in lib:
            detail = ('Library {} is missing biosample'.format(
                audit_link(path_to_text(lib['@id']), lib['@id'])
                )
            )
            yield AuditFailure('missing biosample', detail, level='ERROR')
    return


def audit_library_RNA_size_range(value, system, excluded_types):
    '''
    An RNA library should have a size_range specified.
    This needs to accomodate the rfa
    '''
    if value['status'] in ['deleted', 'replaced']:
        return

    if value.get('assay_term_name') in ['transcription profiling by array assay',
                                        'long read RNA-seq',
                                        ]:
        return

    RNAs = ['RNA',
            'polyadenylated mRNA',
            'miRNA']

    for rep in value['replicates']:
        if 'library' not in rep:
            continue
        lib = rep['library']
        if ((lib['nucleic_acid_term_name'] in RNAs) and ('size_range' not in lib)) and \
                ((lib['nucleic_acid_term_name'] in RNAs) and ('average_fragment_size' not in lib)):
            detail = ('Metadata of RNA library {} lacks information on '
                'the size range or average size of fragments used to construct the library.'.format(
                    audit_link(path_to_text(rep['library']['@id']), rep['library']['@id'])
                )
            )
            yield AuditFailure('missing RNA fragment size', detail, level='NOT_COMPLIANT')
    return


def audit_RNA_library_RIN(value, system, excluded_types):
    '''
    An RNA library should have a RIN specified.
    '''
    RNAs = ['RNA', 'polyadenylated mRNA', 'miRNA']
    assay_IDs = ['OBI:0002093', # 5' RLM RACE
                 'OBI:0001674', # CAGE
                 'NTR:0003814', # CRISPR RNA-seq
                 'NTR:0004619', # CRISPRi RNA-seq
                 'NTR:0000445', # long read RNA-seq
                 'OBI:0002045', # PAS-seq
                 'OBI:0001864', # RAMPAGE
                 'OBI:0001463', # RNA microarray
                 'OBI:0001850', # RNA-PET
                 'OBI:0001271', # RNA-seq (total)
                 'OBI:0002112', # small RNA-seq
                 'OBI:0002571', # polyA plus RNA-seq
                 'OBI:0002572', # polyA minus RNA-seq
                 'NTR:0000762', # shRNA RNA-seq
                 'NTR:0000763'  # siRNA RNA-seq
                ]
    if value['assay_term_id'] in assay_IDs:
        for rep in value['replicates']:
            if (rep['status'] not in excluded_types and
               'library' in rep and rep['library']['status'] not in excluded_types and
               rep['library']['nucleic_acid_term_name'] in RNAs and
               'rna_integrity_number' not in rep['library']):
                detail = ('Metadata of RNA library {} lacks specification of '
                    'the rna integrity number.'.format(
                        audit_link(path_to_text(rep['library']['@id']), rep['library']['@id'])
                    )
                )
                yield AuditFailure('missing RIN', detail, level='INTERNAL_ACTION')


# ENCD-4655: if the experiment uses a tag antibody and its target is not tag,
# its biosamples should have at least one GM with matched introduced_tags in
# the applied_modifications.
def audit_missing_modification(value, system, excluded_types):
    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if (
        'target' not in value
        or 'tag' in value['target']['investigated_as']
        or 'synthetic tag' in value['target']['investigated_as']
    ):
        return

    for rep in value['replicates']:
        antibody = rep.get('antibody', {})
        ab_tags = {
            target['label']
            for target in antibody.get('targets', [])
            if {'tag', 'synthetic tag'} & set(target['investigated_as'])
        }
        if not ab_tags:
            continue
        biosample = rep.get('library', {}).get('biosample')
        if not biosample:
            continue
        tags = {
            tag['name']
            for mod in biosample.get('applied_modifications', [])
            for tag in mod.get('introduced_tags', [])
            if tag.get('name')
        }
        if not (ab_tags & tags):
            detail = (
                '{} specifies antibody {} targeting {} yet its biosample {} has no '
                'genetic modifications tagging the target.'.format(
                    audit_link(
                        'Replicate {}_{}'.format(
                            rep['biological_replicate_number'],
                            rep['technical_replicate_number']
                        ),
                        rep['@id']
                    ),
                    audit_link(path_to_text(antibody['@id']), antibody['@id']),
                    ', '.join(ab_tags),
                    audit_link(
                        path_to_text(biosample['@id']), biosample['@id']
                    ),
                )
            )
            yield AuditFailure(
                'inconsistent genetic modification tags',
                detail,
                level='ERROR'
            )


def audit_experiment_mapped_read_length(value, system, files_structure):
    if value.get('assay_term_id') not in ['OBI:0000716', 'OBI:0002160']:  # not a ChIP-seq
        return
    for peaks_file in files_structure.get('peaks_files').values():
        if peaks_file.get('lab') == '/labs/encode-processing-pipeline/':
            derived_from_bams = get_derived_from_files_set(
                [peaks_file], files_structure, 'bam', True)
            #derived_from_bams = get_derived_from_files_set([peaks_file], 'bam', True)
            read_lengths_set = set()
            for bam_file in derived_from_bams:
                if bam_file.get('lab') == '/labs/encode-processing-pipeline/':
                    mapped_read_length = get_mapped_length(
                        bam_file, files_structure)
                    if mapped_read_length:
                        read_lengths_set.add(mapped_read_length)
                    else:
                        detail = ('Experiment {} '
                            'contains a processed {} .bam file {} '
                            'that lacks mapped reads '
                            'length information.'.format(
                                audit_link(path_to_text(value['@id']), value['@id']),
                                bam_file['output_type'],
                                audit_link(path_to_text(bam_file['@id']), bam_file['@id'])
                            )
                        )
                        yield AuditFailure('missing mapped reads lengths', detail,
                                           level='INTERNAL_ACTION')
            if len(read_lengths_set) > 1:
                if max(read_lengths_set) - min(read_lengths_set) >= 7:
                    detail = ('Experiment {} '
                        'contains a processed .bed file {} '
                        'that was derived from alignments files with inconsistent mapped '
                        'reads lengths {}.'.format(
                            audit_link(path_to_text(value['@id']), value['@id']),
                            audit_link(path_to_text(peaks_file['@id']), peaks_file['@id']),
                            sorted(list(read_lengths_set))
                        )
                    )
                    yield AuditFailure('inconsistent mapped reads lengths',
                                       detail, level='INTERNAL_ACTION')
    return


def audit_experiment_nih_institutional_certification(value, system, excluded_types):
    '''
    Check if ENCODE4 experiment uses biosample without NIH institutional certification.
    '''
    # Only check ENCODE4 experiments. 
    award = value.get('award', {})
    if award.get('rfa') != 'ENCODE4' or award.get('component') == 'functional characterization':
        return
    # Build up list of human biosamples missing NIC used in experiment. 
    human_biosamples_missing_hic = {
        b['@id']
        for b in get_biosamples(value)
        if (b.get('organism') == '/organisms/human/'
            and not b.get('nih_institutional_certification'))
    }
    # Yield AuditFailure for unique biosamples.
    for b in human_biosamples_missing_hic:
        detail = ('Experiment {} uses biosample {} missing NIH institutional'
            ' certification required for human data'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                audit_link(path_to_text(b), b)
            )
        )
        yield AuditFailure('missing nih_institutional_certification', detail, level='ERROR')


def audit_experiment_eclip_queried_RNP_size_range(value, system, excluded_types):
    '''
    Check if libraries of eCLIP experiment and its control have matching queried_RNP_size_range.
    '''
    if value.get('assay_term_name') != 'eCLIP':
        return

    experiment_size_range = set()
    control_size_range = set()
    details = []
    control_accessions = []

    for rep in value['replicates']:
        if rep.get('status') not in excluded_types and 'library' in rep:
            lib = rep.get('library', {})
            if 'queried_RNP_size_range' in lib:
                experiment_size_range.add(lib['queried_RNP_size_range'])
            else:
                details.append(
                    'Library {} is missing specification of queried_RNP_size_range.'.format(
                        audit_link(path_to_text(lib['@id']), lib['@id'])
                    )
                )

    for control in value.get('possible_controls'):
        control_accessions.append(audit_link(path_to_text(control['@id']), control['@id']))
        for rep in control['replicates']:
            if rep.get('status') not in excluded_types and 'library' in rep:
                lib = rep.get('library', {})
                if 'queried_RNP_size_range' in lib:
                    control_size_range.add(lib['queried_RNP_size_range'])
                else:
                    details.append(
                        'Library {} is missing specification of queried_RNP_size_range.'.format(
                            audit_link(path_to_text(lib['@id']), lib['@id'])
                        )
                    )

    if details:
        for detail in details:
            yield AuditFailure('missing queried_RNP_size_range', detail, level='ERROR')
        return

    if len(experiment_size_range) > 1 or len(control_size_range) > 1:
        if len(experiment_size_range) > 1:
            detail = 'Libraries of experiment {} have mixed queried_RNP_size_range values of {}.'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                ', '.join(experiment_size_range)
            )
            yield AuditFailure('mixed queried_RNP_size_range', detail, level='ERROR')

        if len(control_size_range) > 1:
            detail = 'Libraries of control experiment(s) {} have mixed queried_RNP_size_range values of {}.'.format(
                ', '.join(control_accessions),
                ', '.join(control_size_range)
            )
            yield AuditFailure('mixed queried_RNP_size_range', detail, level='ERROR')
        return

    if experiment_size_range != control_size_range and value['possible_controls']:
        detail = ('Libraries of experiment {} have queried_RNP_size_range of {},'
            ' but the libraries of its control experiment(s) {} have queried_RNP_size_range of {}.'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                ', '.join(experiment_size_range),
                ', '.join(control_accessions),
                ', '.join(control_size_range)
            )
        )
        yield AuditFailure('inconsistent queried_RNP_size_range', detail, level='ERROR')


def audit_experiment_no_processed_data(value, system, files_structure):
    '''
    ENCD-5057: flag experiments that do not have any processed data
    '''
    raw_data = files_structure.get('raw_data')
    processed_data = files_structure.get('processed_data')

    if not raw_data:
        return

    if not processed_data:
        detail = 'Experiment {} only has raw data and does not contain any processed data'.format(audit_link(path_to_text(value['@id']), value['@id']))
        yield AuditFailure('lacking processed data', detail, level='WARNING')


def audit_experiment_inconsistent_analysis_files(value, system, files_structure):
    processed_data = files_structure.get('processed_data')
    files_not_in_analysis = []
    files_not_in_processed_data = []
    if processed_data and 'analysis_objects' in value:
        analysis_outputs = set()
        for analysis in value['analysis_objects']:
            for f in analysis['files']:
                analysis_outputs.add(f)
        for processed_file_id in processed_data:
            if processed_file_id in analysis_outputs:
                continue
            if processed_file_id not in analysis_outputs:
                files_not_in_analysis.append(processed_file_id)
        for analysis_file_id in analysis_outputs:
            if analysis_file_id in processed_data:
                continue
            if analysis_file_id not in processed_data:
                files_not_in_processed_data.append(analysis_file_id)
    if len(files_not_in_analysis) > 0:
        files_not_in_analysis_links = [audit_link(path_to_text(file), file) for file in files_not_in_analysis]
        detail = ('Experiment {} '
                'contains processed file(s) {} '
                'not in an analysis'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    ', '.join(files_not_in_analysis_links)
                )
            )
        yield AuditFailure('inconsistent analysis files', detail, level='INTERNAL_ACTION')
    if len(files_not_in_processed_data) > 0:
        files_not_in_processed_data_links = [audit_link(path_to_text(file), file) for file in files_not_in_processed_data]
        detail = ('Experiment {} '
                'contains file(s) in an analysis {} '
                'not in processed data'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    ', '.join(files_not_in_processed_data_links)
                )
            )
        yield AuditFailure('inconsistent analysis files', detail, level='INTERNAL_ACTION')


def audit_experiment_inconsistent_genetic_modifications(value, system, excluded_types):
    genetic_modifications = {'no genetic modifications': set()}

    if value['status'] in ['deleted', 'replaced', 'revoked']:
        return

    if value['assay_term_name'] == 'pooled clone sequencing':
        return

    if value.get('replicates') is not None and len(value['replicates']) > 1:
        for rep in value['replicates']:
            if (rep['status'] not in excluded_types and 'library' in rep and rep['library']['status'] not in excluded_types and 'biosample' in rep['library'] and rep['library']['biosample']['status'] not in excluded_types):
                biosampleObject = rep['library']['biosample']
                modifications = biosampleObject.get('applied_modifications')
                if not modifications:
                    genetic_modifications['no genetic modifications'].add(biosampleObject['@id'])
                else:
                    gm_combined = tuple(sorted(gm['@id'] for gm in modifications))
                    if gm_combined not in genetic_modifications:
                        genetic_modifications[gm_combined] = set(biosampleObject['@id'])
                    else:
                        genetic_modifications[gm_combined].add(biosampleObject['@id'])

    # Removed unused key from dict if necessary
    if len(genetic_modifications['no genetic modifications']) == 0:
        genetic_modifications.pop('no genetic modifications')

    if len(genetic_modifications) > 1:
        detail = 'Experiment {} contains biosamples with inconsistent genetic modifications'.format(audit_link(path_to_text(value['@id']), value['@id']))
        yield AuditFailure('inconsistent genetic modifications', detail, level='INTERNAL_ACTION')


def audit_biosample_perturbed_mixed(value, system, excluded_types):
    '''Error for biosamples with mixed perturbed values'''
    biosamples = get_biosamples(value)
    bio_perturbed = set()
    for biosample in biosamples:
        bio_perturbed.add(biosample['perturbed'])
    if len(bio_perturbed) > 1:
        detail = 'Experiment {} contains both perturbed and non-perturbed biosamples'.format(audit_link(path_to_text(value['@id']), value['@id']))
        yield AuditFailure('mixed biosample perturbations', detail, level='ERROR')


def negative_coefficients(metric, coefficients, files_structure):
    for coefficient in coefficients:
        if coefficient in metric and metric[coefficient] < 0 and 'quality_metric_of' in metric:
            alignment_file = files_structure.get(
                'alignments')[metric['quality_metric_of'][0]]
            detail = (
                f'Alignment file {audit_link(path_to_text(alignment_file["@id"]),alignment_file["@id"])} '
                f'has a negative {coefficient} value of {metric[coefficient]}. The {coefficient} value is expected to be a positive number.'
            )
            yield AuditFailure('negative ' + coefficient, detail, level='ERROR')

    
def check_experiment_atac_encode4_qc_standards(experiment, files_structure):
    # https://encodedcc.atlassian.net/browse/ENCD-5255
    # https://encodedcc.atlassian.net/browse/ENCD-5350
    # https://encodedcc.atlassian.net/browse/ENCD-5468
    alignment_files = files_structure.get('alignments').values()
    pseudo_replicated_peaks_files = files_structure.get(
        'pseudo_replicated_peaks_files'
    ).values()
    idr_thresholded_peaks_files = files_structure.get('idr_thresholded_peaks').values()
    all_peaks_files = files_structure.get('overlap_and_idr_peaks').values()
    overlap_peaks_files = []

    assay_term_name = experiment['assay_term_name']
    if assay_term_name != 'ATAC-seq':
        return
    pipeline_title = scanFilesForPipelineTitle_not_chipseq(
        alignment_files, ['GRCh38', 'mm10'],
        ['ATAC-seq (unreplicated)',
         'ATAC-seq (replicated)'])
    if pipeline_title is False:
        return

    # For FRiP: use the pseudo-replicated peaks with multiple biological replicates as input
    if 'replication_type' in experiment and experiment['replication_type'] != 'unreplicated':
        for file in pseudo_replicated_peaks_files:
            if 'biological_replicates' in file:
                reps = file['biological_replicates']
                if len(reps) > 1:
                    overlap_peaks_files.append(file)
    else:
        for each in pseudo_replicated_peaks_files:
            overlap_peaks_files.append(each)

    alignment_metrics = get_metrics(alignment_files, 'AtacAlignmentQualityMetric')
    align_enrich_metrics = get_metrics(alignment_files, 'AtacAlignmentEnrichmentQualityMetric')
    library_metrics = get_metrics(alignment_files, 'AtacLibraryQualityMetric')
    peak_enrich_metrics = get_metrics(overlap_peaks_files, 'AtacPeakEnrichmentQualityMetric')

    # Checks in AtacAlignmentQualityMetric
    if alignment_metrics is not None and len(alignment_metrics) > 0:
        for metric in alignment_metrics:
            alignment_file = files_structure.get(
                    'alignments')[metric['quality_metric_of'][0]]
            if 'pct_mapped_reads' in metric and 'quality_metric_of' in metric:
                pct_mapped = str(metric['pct_mapped_reads'])
                detail = (
                    f'Alignment file '
                    f'{audit_link(path_to_text(alignment_file["@id"]),alignment_file["@id"])} has '
                    f'{pct_mapped}% mapped reads. '
                    f'According to ENCODE4 standards, ATAC-seq assays processed '
                    f'by the uniform processing pipeline require a minimum of 80% '
                    f'reads mapped. The recommended value is over 95%, but 80-95% is acceptable.'
                    )
                if metric['pct_mapped_reads'] <= 95 and metric['pct_mapped_reads'] >= 80:
                    yield AuditFailure('acceptable alignment rate', detail, level='WARNING')
                elif metric['pct_mapped_reads'] < 80:
                    yield AuditFailure('low alignment rate', detail, level='NOT_COMPLIANT')

            if 'mapped_reads' in metric:
                mappedReads = metric['mapped_reads']
                mapped_run_type = alignment_file.get('mapped_run_type', None)
                if mapped_run_type:
                    if mapped_run_type == 'paired-ended':
                        mappedReads = int(mappedReads / 2)
                    else:
                        mappedReads = int(mappedReads)
                else:
                    if ('read1' in metric and 'read2' in metric):
                        mappedReads = int(mappedReads / 2)
                    else:
                        mappedReads = int(mappedReads)

                detail = (
                    f'Alignment file {audit_link(path_to_text(alignment_file["@id"]),alignment_file["@id"])} '
                    f'has {mappedReads} usable fragments. According to ENCODE4 standards, ATAC-seq assays '
                    f'processed by the uniform processing pipeline should have > 25 million '
                    f'usable fragments. 20-25 million is acceptable and < 15 million is not compliant.'
                    )

                marks = pipelines_with_read_depth['ATAC-seq (unreplicated)']
                if mappedReads >= marks['minimal'] and mappedReads < marks['recommended']:
                    yield AuditFailure('low read depth', detail, level='WARNING')
                elif mappedReads >= marks['low'] and mappedReads < marks['minimal']:
                    yield AuditFailure('insufficient read depth', detail, level='NOT_COMPLIANT')
                elif mappedReads < marks['low']:
                    yield AuditFailure('extremely low read depth', detail, level='ERROR')

            if 'nfr_peak_exists' in metric:
                if metric['nfr_peak_exists'] is False:
                    detail = (
                        f'Alignment file {audit_link(path_to_text(alignment_file["@id"]),alignment_file["@id"])} '
                        f'indicates that there are no peaks in nucleosome-free regions (NFR); ENCODE4 standards '
                        f'require that ATAC-seq experiments have some overlap between NFR and peaks.'
                    )
                    yield AuditFailure('no peaks in nucleosome-free regions', detail, level='NOT_COMPLIANT')

    # Checks in AtacAlignmentEnrichmentQualityMetric
    if align_enrich_metrics is not None and len(align_enrich_metrics) > 0:
        for metric in align_enrich_metrics:
            yield from negative_coefficients(metric, ['NSC', 'RSC'], files_structure)
            if 'tss_enrichment' in metric and 'quality_metric_of' in metric:
                alignment_file = files_structure.get(
                    'alignments')[metric['quality_metric_of'][0]]
                tss = metric['tss_enrichment']
                assembly = alignment_file.get('assembly')

                if assembly and assembly == 'mm10':
                    mouse_detail = (
                        f'Transcription Start Site (TSS) enrichment values for alignments '
                        f'to the mouse genome mm10 are concerning when < 10, acceptable '
                        f'between 10 and 15, and ideal when > 15. ENCODE processed '
                        f'file {audit_link(path_to_text(alignment_file["@id"]),alignment_file["@id"])} '
                        f'has a TSS enrichment value of {tss}.'
                        )
                    if tss < 10:
                        yield AuditFailure('low TSS enrichment', mouse_detail, level='NOT_COMPLIANT')
                    elif tss >= 10 and tss <= 15:
                        yield AuditFailure('moderate TSS enrichment', mouse_detail, level='WARNING')

                if assembly and assembly == 'GRCh38':
                    human_detail = (
                        f'Transcription Start Site (TSS) enrichment values for alignments '
                        f'to the human genome GRCh38 are concerning when < 5, acceptable '
                        f'between 5 and 7, and ideal when > 7. ENCODE processed '
                        f'file {audit_link(path_to_text(alignment_file["@id"]),alignment_file["@id"])} '
                        f'has a TSS enrichment value of {tss}.'
                        )
                    if tss < 5:
                        yield AuditFailure('low TSS enrichment', human_detail, level='NOT_COMPLIANT')
                    elif tss >= 5 and tss <= 7:
                        yield AuditFailure('moderate TSS enrichment', human_detail, level='WARNING')

    # Checks in AtacLibraryQualityMetric
    if library_metrics is not None and len(library_metrics) > 0:
        for metric in library_metrics:
            alignment_file = files_structure.get(
                    'alignments')[metric['quality_metric_of'][0]]

            if 'NRF' in metric and 'quality_metric_of' in metric:
                NRF_value = float(metric['NRF'])
                detail = (
                    f'NRF (Non Redundant Fraction) is equal to the result of the '
                    f'division of the number of reads after duplicates removal by '
                    f'the total number of reads. '
                    f'An NRF value < 0.7 is poor complexity, '
                    f'between 0.7 and 0.9 is moderate complexity, '
                    f'and >= 0.9 high complexity. NRF value > 0.9 is recommended, '
                    f'but > 0.7 is acceptable. ENCODE processed file '
                    f'{audit_link(path_to_text(alignment_file["@id"]),alignment_file["@id"])} '
                    f'was generated from a library with NRF value of {NRF_value}.'
                    )
                if NRF_value < 0.7:
                    yield AuditFailure('poor library complexity', detail, level='NOT_COMPLIANT')
                elif NRF_value >= 0.7 and NRF_value < 0.9:
                    yield AuditFailure('moderate library complexity', detail, level='WARNING')

            if 'PBC1' in metric and 'quality_metric_of' in metric:
                PBC1 = float(metric['PBC1'])
                pbc1_detail = (
                    f'PBC1 (PCR Bottlenecking Coefficient 1, M1/M_distinct) '
                    f'is the ratio of the number of genomic locations where  '
                    f'exactly one read maps uniquely (M1) to the number of '
                    f'genomic locations where some reads map (M_distinct). '
                    f'A PBC1 value in the range 0 - 0.5 is severe bottlenecking, '
                    f'0.5 - 0.8 is moderate bottlenecking, 0.8 - 0.9 is mild '
                    f'bottlenecking, and > 0.9 is no bottlenecking. PBC1 value > '
                    f'0.9 is recommended, but > 0.7 is acceptable. ENCODE processed file '
                    f'{audit_link(path_to_text(alignment_file["@id"]),alignment_file["@id"])} '
                    f'was generated from a library with a PBC1 value of {PBC1:.2f}.'
                    )
                if PBC1 < 0.7:
                    yield AuditFailure('severe bottlenecking', pbc1_detail, level='NOT_COMPLIANT')
                elif PBC1 >= 0.7 and PBC1 <= 0.9:
                    yield AuditFailure('mild to moderate bottlenecking', pbc1_detail, level='WARNING')

            if 'PBC2' in metric and 'quality_metric_of' in metric:
                PBC2_raw = metric['PBC2']
                if PBC2_raw == 'Infinity':
                    PBC2 = float('inf')
                else:
                    PBC2 = float(metric['PBC2'])
                pbc2_detail = (
                    f'PBC2 (PCR Bottlenecking Coefficient 2, M1/M2) is the ratio of '
                    f'the number of genomic locations where exactly one read maps '
                    f'uniquely (M1) to the number of genomic locations where two reads '
                    f'map uniquely (M2). A PBC2 value in the range 0 - 1 is severe '
                    f'bottlenecking, 1 - 3 is moderate bottlenecking, 3 - 10 is mild '
                    f'bottlenecking, > 10 is no bottlenecking. PBC2 value > 10 is '
                    f'recommended, but > 3 is acceptable. ENCODE processed file '
                    f'{audit_link(path_to_text(alignment_file["@id"]),alignment_file["@id"])} '
                    f'was generated from a library with a PBC2 value of {PBC2:.2f}.'
                    )
                if PBC2 < 1:
                    yield AuditFailure('severe bottlenecking', pbc2_detail, level='NOT_COMPLIANT')
                elif PBC2 >= 1 and PBC2 <= 3:
                    yield AuditFailure('mild to moderate bottlenecking', pbc2_detail, level='WARNING')

    # Checks in AtacPeakEnrichmentQualityMetric
    if peak_enrich_metrics is not None and len(peak_enrich_metrics) > 0:
        for metric in peak_enrich_metrics:
            overlap_peaks_file = files_structure.get('pseudo_replicated_peaks_files')[metric['quality_metric_of'][0]]
            if 'frip' in metric and 'quality_metric_of' in metric:
                frip = float(metric['frip'])
                detail = (
                    f'According to ENCODE4 standards, overlap peaks files in ATAC-seq assays processed '
                    f'by the uniform processing pipeline should have FRiP (fraction of reads in '
                    f'called peak regions) scores > 0.3. FRiP scores 0.2-0.3 are acceptable, '
                    f'and < 0.2 are not compliant. '
                    f'{audit_link(path_to_text(overlap_peaks_file["@id"]),overlap_peaks_file["@id"])} '
                    f' has a FRiP score of {frip:.2f}.')
                if frip < 0.2:
                    yield AuditFailure('low FRiP score', detail, level='NOT_COMPLIANT')
                elif frip >= 0.2 and PBC1 <= 0.3:
                    yield AuditFailure('moderate FRiP score', detail, level='WARNING')

    # Checks in AtacReplicationQualityMetric
    peaks_report = {}
    problematic_files = 0
    for f in all_peaks_files:
        output_type = f['output_type']
        file_list = []
        file_list.append(f)
        f_replication_metrics = get_metrics(file_list, 'AtacReplicationQualityMetric')
        if f_replication_metrics is not None and len(f_replication_metrics) > 0:
            if len(f_replication_metrics) != 1:
                problematic_files += 1
                detail = (
                    f'Multiple AtacReplicationQualityMetric objects are posted on '
                    f'{audit_link(path_to_text(f["@id"]),f["@id"])}. Values in these metrics may '
                    f'not be assessed for QC until this is resolved.')
                yield AuditFailure('duplicate QC metrics', detail, level='ERROR')
            elif len(f_replication_metrics) == 1:
                for metric in f_replication_metrics:
                    if 'rescue_ratio' in metric and 'self_consistency_ratio' in metric:
                        rescue = metric['rescue_ratio']
                        self_consistency = metric['self_consistency_ratio']
                        if 'reproducible_peaks' in metric:
                            if output_type in ['pseudo-replicated peaks', 'replicated peaks']:
                                peaks_report['overlap_rep_peaks'] = metric['reproducible_peaks']
                                peaks_report['overlap_rep_peaks_file'] = f['@id']
                                if metric['reproducible_peaks'] > 150000:
                                    peaks_report['overlap_rep_peaks_qual'] = 'pass'
                                if metric['reproducible_peaks'] <= 150000 and metric['reproducible_peaks'] >= 100000:
                                    peaks_report['overlap_rep_peaks_qual'] = 'warning'
                                if metric['reproducible_peaks'] < 100000:
                                    peaks_report['overlap_rep_peaks_qual'] = 'not_compliant'

                            if output_type in ['IDR thresholded peaks', 'conservative IDR thresholded peaks']:
                                peaks_report['idr_rep_peaks'] = metric['reproducible_peaks']
                                peaks_report['idr_rep_peaks_file'] = f['@id']
                                if metric['reproducible_peaks'] > 70000:
                                    peaks_report['idr_rep_peaks_qual'] = 'pass'
                                if metric['reproducible_peaks'] <= 70000 and metric['reproducible_peaks'] >= 50000:
                                    peaks_report['idr_rep_peaks_qual'] = 'warning'
                                if metric['reproducible_peaks'] < 50000:
                                    peaks_report['idr_rep_peaks_qual'] = 'not_compliant'

                        # Replicate concordance is only reported for replicated experiments
                        if 'replication_type' in experiment and \
                                experiment['replication_type'] != 'unreplicated':
                            detail = (
                                f'According to ENCODE4 standards, peaks files in replicated '
                                f'ATAC-seq assays processed by the uniform processing pipeline '
                                f'should have a rescue ratio and self-consistency ratio < 2. '
                                f'Having only one of these ratios < 2 is acceptable. '
                                f'{audit_link(path_to_text(f["@id"]),f["@id"])} '
                                f' has a rescue ratio of {rescue:.2f} and self-consistency ratio '
                                f'of {self_consistency:.2f}.'
                                )
                            if rescue >= 2 and self_consistency >= 2:
                                yield AuditFailure('insufficient replicate concordance', detail, level='NOT_COMPLIANT')
                            elif rescue >= 2 or self_consistency >= 2:
                                yield AuditFailure('borderline replicate concordance', detail, level='WARNING')

    # The better reproducible peaks value in overlap or IDR thresholded peaks is reported
    # This should not be reported if any peaks file has multiple Replication metrics
    if problematic_files == 0:
        detail_items = []
        if 'overlap_rep_peaks' in peaks_report.keys():
            detail_items.append(tuple((str(peaks_report['overlap_rep_peaks']),
                                peaks_report.get('overlap_rep_peaks_file'), ' (overlap peaks)')))
        if 'idr_rep_peaks' in peaks_report.keys():
            detail_items.append(tuple((str(peaks_report['idr_rep_peaks']),
                                peaks_report.get('idr_rep_peaks_file'), ' (IDR thresholded peaks)')))
        audit_peaks = ' and '.join(m[0] for m in detail_items)
        file_links = ' and '.join((audit_link(path_to_text(m[1]), m[1])) + m[2] for m in detail_items)
        detail = (
            f'According to ENCODE4 standards, ATAC-seq assays processed by the uniform processing '
            f'pipeline should have either >150k reproducible peaks in an overlap peaks file, or '
            f'>70k in an IDR thresholded peaks file. 100-150k or 50-70k peaks respectively is '
            f'acceptable, and <100k or <50k respectively is not compliant. '
            f'File(s) {file_links} have {audit_peaks} peaks.')
        if 'pass' in peaks_report.values():
            return
        elif 'warning' in peaks_report.values():
            yield AuditFailure('moderate number of reproducible peaks', detail, level='WARNING')
        elif 'not_compliant' in peaks_report.values():
            yield AuditFailure('insufficient number of reproducible peaks', detail, level='NOT_COMPLIANT')


def audit_analysis_files(value, system, files_structure):
    if 'analysis_objects' not in value:
        return
    detail_list = []
    for analysis in value['analysis_objects']:
        for f in analysis.get('files', []):
            if f not in files_structure['original_files']:
                detail_list.append(
                    'Analysis {} has a file {} which does not belong to this '
                    'experiment {}.'.format(
                        audit_link(
                            path_to_text(analysis['@id']), analysis['@id']
                        ),
                        audit_link(path_to_text(f), f),
                        audit_link(path_to_text(value['@id']), value['@id']),
                    )
                )
                break
    for detail in detail_list:
        yield AuditFailure('inconsistent analysis files', detail, 'WARNING')



#######################
# utilities
#######################

def extract_assemblies(assemblies, file_names):
    to_return = set()
    for f_name in file_names:
        if f_name in assemblies:
            to_return.add(assemblies[f_name])
    return sorted(list(to_return))


def assemblies_detail(assemblies):
    assemblies_detail = ''
    if assemblies:
        if len(assemblies) > 1:
            assemblies_detail = "for {} assemblies ".format(
                str(assemblies).replace('\'', ' '))
        else:
            assemblies_detail = "for {} assembly ".format(
                assemblies[0])
    return assemblies_detail


def get_mapped_length(bam_file, files_structure):
    mapped_length = bam_file.get('mapped_read_length')
    if mapped_length:
        return mapped_length
    derived_from_fastqs = get_derived_from_files_set(
        [bam_file], files_structure, 'fastq', True)
    for f in derived_from_fastqs:
        length = f.get('read_length')
        if length:
            return length
    return None


def get_control_bam(experiment_bam, pipeline_name, derived_from_fastqs, files_structure):
    #  get representative FASTQ file
    if not derived_from_fastqs:
        return False
    control_fastq = False
    for entry in derived_from_fastqs:
        if entry.get('dataset') == experiment_bam.get('dataset') and \
           'controlled_by' in entry and len(entry['controlled_by']) > 0:
            # getting representative FASTQ
            control_fastq = entry['controlled_by'][0]
            break
    # get representative FASTQ from control
    if control_fastq is False:
        return False
    else:
        if 'original_files' not in control_fastq['dataset']:
            return False

        control_bam = False
        control_files_structure = create_files_mapping(control_fastq['dataset'].get('original_files'),
                                                       files_structure.get('excluded_types'))

        for control_file in control_files_structure.get('alignments').values():
            if 'assembly' in control_file and 'assembly' in experiment_bam and \
               control_file['assembly'] == experiment_bam['assembly']:
                #  we have BAM file, now we have to make sure it was created by pipeline
                #  with similar pipeline_name

                is_same_pipeline = False
                if has_pipelines(control_file) is True:
                    for pipeline in \
                            control_file['analysis_step_version']['analysis_step']['pipelines']:
                        if pipeline['title'] == pipeline_name:
                            is_same_pipeline = True
                            break

                if is_same_pipeline is True and \
                   'derived_from' in control_file and \
                   len(control_file['derived_from']) > 0:
                    derived_list = get_derived_from_files_set(
                        [control_file],
                        control_files_structure,
                        'fastq',
                        True)

                    for entry in derived_list:
                        if entry['accession'] == control_fastq['accession']:
                            control_bam = control_file
                            break
        return control_bam


def has_pipelines(bam_file):
    if 'analysis_step_version' not in bam_file:
        return False
    if 'analysis_step' not in bam_file['analysis_step_version']:
        return False
    if 'pipelines' not in bam_file['analysis_step_version']['analysis_step']:
        return False
    return True


def get_target(experiment):
    if 'target' in experiment:
        return experiment['target']
    return False


def get_organism_name(reps, excluded_types):
    excluded_types += ['deleted', 'replaced']
    for rep in reps:
        if rep['status'] not in excluded_types and \
           'library' in rep and \
           rep['library']['status'] not in excluded_types and \
           'biosample' in rep['library'] and \
           rep['library']['biosample']['status'] not in excluded_types:
            if 'organism' in rep['library']['biosample']:
                return rep['library']['biosample']['organism'].split('/')[2]
    return False


def scanFilesForPipelineTitle_not_chipseq(files_to_scan, assemblies, pipeline_titles):
    for f in files_to_scan:
        if 'file_format' in f and f['file_format'] == 'bam' and \
           f['status'] not in ['replaced', 'deleted'] and \
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


def get_pipeline_by_name(pipeline_objects, pipeline_title):
    for pipe in pipeline_objects:
        if pipe['title'] == pipeline_title:
            return pipe
    return None


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


def get_file_read_depth_from_alignment(alignment_file, target, assay_name):

    if alignment_file.get('output_type') in ['transcriptome alignments']:
        return False

    if alignment_file.get('lab') not in ['/labs/encode-processing-pipeline/', '/labs/kevin-white/']:
        return False

    quality_metrics = alignment_file.get('quality_metrics')

    if not quality_metrics:
        return False

    if assay_name in ['RAMPAGE', 'CAGE',
                      'small RNA',
                      'long RNA']:
        if alignment_file.get('output_type') in ['unfiltered alignments']:
            return False
        for metric in quality_metrics:
            if 'Uniquely mapped reads number' in metric and \
               'Number of reads mapped to multiple loci' in metric:
                unique = metric['Uniquely mapped reads number']
                multi = metric['Number of reads mapped to multiple loci']
                return unique + multi

    elif assay_name in ['Mint-ChIP-seq', 'ChIP-seq']:
        mapped_run_type = alignment_file.get('mapped_run_type', None)
        if target is not False and \
           'name' in target and target['name'] in ['H3K9me3-human', 'H3K9me3-mouse']:
           # exception (mapped reads). Unfiltered bam QC metrics are used for H3K9me3 only
            for metric in quality_metrics:
                if 'mapped_reads' in metric:
                    mappedReads = metric['mapped_reads']
                elif 'mapped' in metric:
                    mappedReads = metric['mapped']
                if 'processing_stage' in metric and \
                    metric['processing_stage'] == 'unfiltered' and \
                        ('mapped' in metric or 'mapped_reads' in metric):
                    if mapped_run_type:
                        if mapped_run_type == 'paired-ended':
                            return int(mappedReads / 2)
                        else:
                            return int(mappedReads)
                    else:
                        if ('read1' in metric and 'read2' in metric):
                            return int(mappedReads / 2)
                        else:
                            return int(mappedReads)

        else:
            # not exception (useful fragments). All marks other than H3K9me3
            if alignment_file.get('output_type') in ['unfiltered alignments', \
                'redacted unfiltered alignments']:
                return False
            for metric in quality_metrics:
                if 'total_reads' in metric:
                    totalReads = metric['total_reads']
                elif 'total' in metric:
                    totalReads = metric['total']
                if ('total' in metric or 'total_reads' in metric) and \
                   (('processing_stage' in metric and metric['processing_stage'] == 'filtered') or
                        ('processing_stage' not in metric)):
                    if mapped_run_type:
                        if mapped_run_type == 'paired-ended':
                            return int(totalReads / 2)
                        else:
                            return int(totalReads)
                    else:
                        if ("read1" in metric and "read2" in metric):
                            return int(totalReads / 2)
                        else:
                            return int(totalReads)
    return False


def get_non_tophat_alignment_files(files_list):
    list_to_return = []
    for f in files_list:
        tophat_flag = False
        if 'analysis_step_version' in f and \
           'software_versions' in f['analysis_step_version']:
            for soft_version in f['analysis_step_version']['software_versions']:
                #  removing TopHat files
                if 'software' in soft_version and \
                   soft_version['software']['uuid'] == '7868f960-50ac-11e4-916c-0800200c9a66':
                    tophat_flag = True
        if tophat_flag is False and \
           f['lab'] == '/labs/encode-processing-pipeline/':
            list_to_return.append(f)
    return list_to_return


def get_read_lengths_wgbs(fastq_files):
    list_of_lengths = []
    for f in fastq_files:
        if 'read_length' in f:
            list_of_lengths.append(f['read_length'])
    return list_of_lengths


def get_metrics(files_list, metric_type, desired_assembly=None, desired_annotation=[]):
    metrics_dict = {}
    for f in files_list:
        if (desired_assembly is None or ('assembly' in f and
                                         f['assembly'] == desired_assembly)) and \
            (desired_annotation == [] or ('genome_annotation' in f and
                                            f['genome_annotation'] in desired_annotation)):
            if 'quality_metrics' in f and len(f['quality_metrics']) > 0:
                for qm in f['quality_metrics']:
                    if metric_type in qm['@type']:
                        if qm['uuid'] not in metrics_dict:
                            metrics_dict[qm['uuid']] = qm
    metrics = []
    for k in metrics_dict:
        metrics.append(metrics_dict[k])
    return metrics


def get_chip_seq_bam_read_depth(bam_file):
    if bam_file['status'] in ['deleted', 'replaced']:
        return False
    if bam_file['file_format'] != 'bam' or \
        bam_file['output_type'] not in ['alignments', 'redacted alignments']:
        return False
    # Check to see if bam is from ENCODE or modERN pipelines
    if bam_file['lab'] not in ['/labs/encode-processing-pipeline/', '/labs/kevin-white/']:
        return False
    
    quality_metrics = bam_file.get('quality_metrics')

    if (quality_metrics is None) or (quality_metrics == []):
        return False

    read_depth = 0

    for metric in quality_metrics:
        if 'total_reads' in metric:
            totalReads = metric['total_reads']
        elif 'total' in metric:
            totalReads = metric['total']
        if (('total' in metric or 'total_reads' in metric) and
                (('processing_stage' in metric and metric['processing_stage'] == 'filtered') or
                 ('processing_stage' not in metric))):
            if "read1" in metric and "read2" in metric:
                read_depth = int(totalReads / 2)
            else:
                read_depth = totalReads
            break

    if read_depth == 0:
        return False

    return read_depth


def create_files_mapping(files_list, excluded):
    to_return = {'original_files': {},
                 'fastq_files': {},
                 'alignments': {},
                 'unfiltered_alignments': {},
                 'alignments_unfiltered_alignments': {},
                 'transcriptome_alignments': {},
                 'peaks_files': {},
                 'gene_quantifications_files': {},
                 'transcript_quantifications_files': {},
                 'microRNA_quantifications_files': {},
                 'signal_files': {},
                 'preferred_default_idr_peaks': {},
                 'idr_thresholded_peaks': {},
                 'cpg_quantifications': {},
                 'contributing_files': {},
                 'raw_data': {},
                 'processed_data': {},
                 'pseudo_replicated_peaks_files': {},
                 'overlap_and_idr_peaks': {},
                 'excluded_types': excluded}
    if files_list:
        for file_object in files_list:
            if file_object['status'] not in excluded:
                to_return['original_files'][file_object['@id']] = file_object

                file_format = file_object.get('file_format')
                file_output = file_object.get('output_type')
                file_output_category = file_object.get('output_category')

                if file_format and file_format == 'fastq' and \
                        file_output and file_output == 'reads':
                    to_return['fastq_files'][file_object['@id']] = file_object

                if file_format and file_format == 'bam' and \
                        file_output and (
                            file_output == 'alignments' or
                            file_output and file_output == 'redacted alignments'):
                    to_return['alignments'][file_object['@id']] = file_object

                if file_format and file_format == 'bam' and \
                        file_output and (
                            file_output == 'unfiltered alignments' or
                            file_output == 'redacted unfiltered alignments'):
                    to_return['unfiltered_alignments'][file_object['@id']
                                                       ] = file_object

                if file_format and file_format == 'bam' and \
                        file_output and file_output == 'transcriptome alignments':
                    to_return['transcriptome_alignments'][file_object['@id']
                                                          ] = file_object

                if file_format and file_format == 'bed' and \
                        file_output and file_output in ['peaks',
                                                        'peaks and background as input for IDR']:
                    to_return['peaks_files'][file_object['@id']] = file_object

                if file_output and file_output == 'gene quantifications':
                    to_return['gene_quantifications_files'][file_object['@id']
                                                            ] = file_object

                if file_output and file_output == 'transcript quantifications':
                    to_return['transcript_quantifications_files'][file_object['@id']
                                                            ] = file_object

                if file_output and file_output == 'microRNA quantifications':
                    to_return['microRNA_quantifications_files'][file_object['@id']
                                                            ] = file_object

                if file_output and file_output == 'signal of unique reads':
                    to_return['signal_files'][file_object['@id']] = file_object

                if file_output and file_output == 'optimal IDR thresholded peaks':
                    to_return['preferred_default_idr_peaks'][
                        file_object['@id']
                    ] = file_object
                if (
                    file_object.get('preferred_default')
                    and file_output == 'IDR thresholded peaks'
                ):
                    to_return['preferred_default_idr_peaks'][
                        file_object['@id']
                    ] = file_object
                if file_output and file_output == 'IDR thresholded peaks':
                    to_return['idr_thresholded_peaks'][
                        file_object['@id']
                    ] = file_object
                if file_output and file_output == 'methylation state at CpG':
                    to_return['cpg_quantifications'][file_object['@id']
                                                     ] = file_object
                if (
                    file_format
                    and file_format == 'bed'
                    and file_output
                    and file_output == 'pseudo-replicated peaks'
                ):
                    to_return['pseudo_replicated_peaks_files'][
                        file_object['@id']
                    ] = file_object

                if file_format and file_format == 'bed' and file_output and \
                        file_output in ['replicated peaks', 'pseudo-replicated peaks',
                                        'conservative IDR thresholded peaks',
                                        'IDR thresholded peaks']:
                    to_return['overlap_and_idr_peaks'][file_object['@id']] = file_object
                    
                if file_output_category == 'raw data':
                    to_return['raw_data'][file_object['@id']] = file_object
                else:
                    to_return['processed_data'][file_object['@id']] = file_object

    return to_return


def get_contributing_files(files_list, excluded_types):
    to_return = {}
    if files_list:
        for file_object in files_list:
            if file_object['status'] not in excluded_types:
                to_return[file_object['@id']] = file_object
    return to_return


def scanFilesForPipelineTitle_yes_chipseq(alignment_files, pipeline_titles):

    if alignment_files:
        for f in alignment_files:
            if f.get('lab') in ['/labs/encode-processing-pipeline/', '/labs/kevin-white/'] and \
                'analysis_step_version' in f and \
                'analysis_step' in f['analysis_step_version'] and \
                    'pipelines' in f['analysis_step_version']['analysis_step']:
                pipelines = f['analysis_step_version']['analysis_step']['pipelines']
                for p in pipelines:
                    if p['title'] in pipeline_titles:
                        return p['title']
    return False


def get_derived_from_files_set(list_of_files, files_structure, file_format, object_flag):
    derived_from_set = set()
    derived_from_objects_list = []
    for file_object in list_of_files:
        if 'derived_from' in file_object:
            for derived_id in file_object['derived_from']:
                derived_object = files_structure.get(
                    'original_files').get(derived_id)
                if not derived_object:
                    derived_object = files_structure.get(
                        'contributing_files').get(derived_id)
                if derived_object and \
                   derived_object.get('file_format') == file_format and \
                   derived_object.get('accession') not in derived_from_set:
                    derived_from_set.add(derived_object.get('accession'))
                    if object_flag:
                        derived_from_objects_list.append(derived_object)
    if object_flag:
        return derived_from_objects_list
    return list(derived_from_set)


def get_file_accessions(list_of_files):
    accessions_set = set()
    for file_object in list_of_files:
        accessions_set.add(file_object.get('accession'))
    return accessions_set


def is_outdated_bams_replicate(bam_file, files_structure, assay_name):
    # if derived_from contains accessions that were not in
    # original_files and not in contributing files - it is outdated!    
    for file_id in bam_file.get('derived_from'):
        if file_id not in files_structure.get('original_files') and \
           file_id not in files_structure.get('contributing_files'):
            return True

    derived_from_fastqs = get_derived_from_files_set(
        [bam_file], files_structure, 'fastq', True)

    # if there are no FASTQs we can not find our the replicate
    if len(derived_from_fastqs) == 0:
        return False

    derived_from_fastq_accessions = get_file_accessions(derived_from_fastqs)

    # for ChIP-seq we should consider biological replicates
    # for DNase we should consider technial replicates
    if assay_name not in ['Mint-ChIP-seq', 'ChIP-seq']:
        replicate_type = 'technical_replicates'
    else:
        replicate_type = 'biological_replicates'
    rep = bam_file.get(replicate_type)
    
    # number of replicates BAM file should belong to have to be one
    # in cases where it is more than one, there probably was replicates 
    # reorganization, that invalidates the analysis    
    if isinstance(rep, list) and len(rep) > 1:
        return True


    rep_type_fastqs = [
        f for f in files_structure.get('fastq_files').values()
        if replicate_type in f
    ]
    rep_set = set(rep)
    rep_fastqs = [
        f for f in rep_type_fastqs
        if any(e in rep_set for e in set(f[replicate_type]))
    ]

    replicate_fastq_accessions = get_file_accessions(rep_fastqs)
    for file_object in rep_fastqs:
        file_acc = file_object.get('accession')
        # for ChIP even one file out of pair is considerd uptodate
        if assay_name in ['Mint-ChIP-seq', 'ChIP-seq'] and file_acc not in derived_from_fastq_accessions:
            paired_file_id = file_object.get('paired_with')
            if paired_file_id and paired_file_id.split('/')[2] not in derived_from_fastq_accessions:
                return True
            elif not paired_file_id:
                return True
        # for DNase all the files from tech. rep should be in the list of the derived_from
        elif assay_name not in ['Mint-ChIP-seq', 'ChIP-seq'] and file_acc not in derived_from_fastq_accessions:
            return True

    for f_accession in derived_from_fastq_accessions:
        if f_accession not in replicate_fastq_accessions:
            return True
    return False


def has_only_raw_files_in_derived_from(bam_file, files_structure):
    if 'derived_from' in bam_file:
        if bam_file['derived_from'] == []:
            return False
        for file_id in bam_file['derived_from']:
            file_object = files_structure.get('original_files').get('file_id')
            if file_object and \
               file_object['file_format'] not in ['fastq', 'tar', 'fasta']:
                return False
        return True
    else:
        return False


def has_no_unfiltered(filtered_bam, unfiltered_bams):
    if 'assembly' in filtered_bam:
        for file_object in unfiltered_bams:
            if 'assembly' in file_object:
                if file_object['assembly'] == filtered_bam['assembly'] and \
                   file_object['biological_replicates'] == filtered_bam['biological_replicates']:
                    derived_candidate = set()
                    derived_filtered = set()
                    if 'derived_from' in file_object:
                        for file_id in file_object['derived_from']:
                            derived_candidate.add(file_id)
                    if 'derived_from' in filtered_bam:
                        for file_id in filtered_bam['derived_from']:
                            derived_filtered.add(file_id)
                    if derived_candidate == derived_filtered:
                        return False
        return True
    return False


def get_platforms_used_in_experiment(files_structure_to_check):
    platforms = set()
    for file_object in files_structure_to_check.get('original_files').values():
        if file_object['output_category'] == 'raw data' and \
                'platform' in file_object:
            # collapsing interchangable platforms HiSeq2000/2500 and all Ilumina Genome Analyzers II/IIe/IIx
            if file_object['platform']['term_id'] in ['OBI:0002002', 'OBI:0002001']:
                platforms.add('Illumina HiSeq 2000/2500')
            elif file_object['platform']['term_id'] in ['OBI:0002000',
                                                        'OBI:0000703',
                                                        'OBI:0002027']:
                platforms.add('Illumina Genome Analyzer II/e/x')
            else:
                platforms.add(file_object['platform']['term_name'])
    return platforms


def get_pipeline_titles(pipeline_objects):
    to_return = set()
    for pipeline in pipeline_objects:
        to_return.add(pipeline.get('title'))
    return list(to_return)


def get_pipeline_objects(files):
    added_pipelines = []
    pipelines_to_return = []
    for inspected_file in files:
        if 'analysis_step_version' in inspected_file and \
           'analysis_step' in inspected_file['analysis_step_version'] and \
           'pipelines' in inspected_file['analysis_step_version']['analysis_step']:
            for p in inspected_file['analysis_step_version']['analysis_step']['pipelines']:
                if p['title'] not in added_pipelines:
                    added_pipelines.append(p['title'])
                    pipelines_to_return.append(p)
    return pipelines_to_return


def get_biosamples(experiment):
    accessions_set = set()
    biosamples_list = []
    if 'replicates' in experiment:
        for rep in experiment['replicates']:
            if ('library' in rep) and ('biosample' in rep['library']):
                biosample = rep['library']['biosample']
                if biosample['accession'] not in accessions_set:
                    accessions_set.add(biosample['accession'])
                    biosamples_list.append(biosample)
    return biosamples_list


def is_gtex_experiment(experiment_to_check):
    for rep in experiment_to_check['replicates']:
        if ('library' in rep) and ('biosample' in rep['library']) and \
           ('donor' in rep['library']['biosample']):
            if rep['library']['biosample']['donor']['accession'] in gtexDonorsList:
                return True
    return False


def check_award_condition(experiment, awards):
    return experiment.get('award') and experiment.get('award')['rfa'] in awards

function_dispatcher_without_files = {
    'audit_isogeneity': audit_experiment_isogeneity,
    'audit_replicate_biosample': audit_experiment_replicates_biosample,
    'audit_tagging_genetic_modification_characterization': audit_experiment_tagging_genetic_modification,
    'audit_tagging_biosample_characterization': audit_experiment_biosample_characterization,
    'audit_replicate_library': audit_experiment_technical_replicates_same_library,
    'audit_documents': audit_experiment_documents,
    'audit_replicate_without_libraries': audit_experiment_replicates_with_no_libraries,
    'audit_experiment_biosample': audit_experiment_biosample_term,
    'audit_library_biosample': audit_experiment_library_biosample,
    'audit_target': audit_experiment_target,
    'audit_mixed_libraries': audit_experiment_mixed_libraries,
    'audit_hic_restriction_enzyme_in_libaries': audit_hic_restriction_enzyme_in_libaries,
    'audit_internal_tags': audit_experiment_internal_tag,
    'audit_geo_submission': audit_experiment_geo_submission,
    'audit_replication': audit_experiment_replicated,
    'audit_RNA_size': audit_library_RNA_size_range,
    'audit_RNA_library_RIN': audit_RNA_library_RIN,
    'audit_missing_modifiction': audit_missing_modification,
    'audit_AB_characterization': audit_experiment_antibody_characterized,
    'audit_control': audit_experiment_control,
    'audit_spikeins': audit_experiment_spikeins,
    'audit_nih_consent': audit_experiment_nih_institutional_certification,
    'audit_replicate_no_files': audit_experiment_replicate_with_no_files,
    'audit_experiment_eclip_queried_RNP_size_range': audit_experiment_eclip_queried_RNP_size_range,
    'audit_inconsistent_genetic_modifications': audit_experiment_inconsistent_genetic_modifications,
    'audit_biosample_perturbed_mixed': audit_biosample_perturbed_mixed
}

function_dispatcher_with_files = {
    'audit_consistent_sequencing_runs': audit_experiment_consistent_sequencing_runs,
    'audit_experiment_out_of_date': audit_experiment_out_of_date_analysis,
    'audit_platforms': audit_experiment_platforms_mismatches,
    'audit_pipeline_assay': audit_experiment_pipeline_assay_details,
    'audit_missing_unfiltered_bams': audit_experiment_missing_unfiltered_bams,
    'audit_modERN': audit_modERN_experiment_standards_dispatcher,
    'audit_read_length': audit_experiment_mapped_read_length,
    'audit_chip_control': audit_experiment_ChIP_control,
    'audit_read_depth_chip_control': audit_experiment_chipseq_control_read_depth,
    'audit_experiment_standards': audit_experiment_standards_dispatcher,
    'audit_submitted_status': audit_experiment_status,
    'audit_no_processed_data': audit_experiment_no_processed_data,
    'audit_experiment_inconsistent_analysis_files': audit_experiment_inconsistent_analysis_files,
    'audit_analysis_files': audit_analysis_files,
}


@audit_checker(
    'Experiment',
    frame=[
        'analysis_objects',
        'biosample_ontology',
        'award',
        'target',
        'replicates',
        'replicates.library',
        'replicates.library.spikeins_used',
        'replicates.library.biosample',
        'replicates.library.biosample.biosample_ontology',
        'replicates.library.biosample.applied_modifications',
        'replicates.library.biosample.applied_modifications.modified_site_by_target_id',
        'replicates.library.biosample.characterizations',
        'replicates.library.biosample.pooled_from.characterizations',
        'replicates.library.biosample.donor',
        'replicates.libraries',
        'replicates.libraries.spikeins_used',
        'replicates.libraries.biosample',
        'replicates.libraries.biosample.applied_modifications',
        'replicates.libraries.biosample.applied_modifications.modified_site_by_target_id',
        'replicates.libraries.biosample.donor',
        'replicates.antibody',
        'replicates.antibody.targets',
        'replicates.antibody.lot_reviews',
        'possible_controls',
        'possible_controls.biosample_ontology',
        'possible_controls.original_files',
        'possible_controls.original_files.quality_metrics',
        'possible_controls.original_files.platform',
        'possible_controls.original_files.analysis_step_version',
        'possible_controls.original_files.analysis_step_version.analysis_step',
        'possible_controls.original_files.analysis_step_version.analysis_step.pipelines',
        'possible_controls.target',
        'possible_controls.replicates',
        'possible_controls.replicates.antibody',
        'possible_controls.replicates.library',
        'contributing_files',
        'contributing_files.quality_metrics',
        'original_files',
        'original_files.award',
        'original_files.quality_metrics',
        'original_files.platform',
        'original_files.replicate',
        'original_files.analysis_step_version',
        'original_files.analysis_step_version.analysis_step',
        'original_files.analysis_step_version.analysis_step.pipelines',
        'original_files.analysis_step_version.software_versions',
        'original_files.analysis_step_version.software_versions.software'
    ])
def audit_experiment(value, system):
    excluded_files = ['revoked', 'archived']
    if value.get('status') == 'revoked':
        excluded_files = []
    if value.get('status') == 'archived':
        excluded_files = ['revoked']
    files_structure = create_files_mapping(
        value.get('original_files'), excluded_files)
    files_structure['contributing_files'] = get_contributing_files(
        value.get('contributing_files'), excluded_files)

    for function_name in function_dispatcher_with_files.keys():
        yield from function_dispatcher_with_files[function_name](value, system, files_structure)

    excluded_types = excluded_files + ['deleted', 'replaced']
    for function_name in function_dispatcher_without_files.keys():
        yield from function_dispatcher_without_files[function_name](value, system, excluded_types)

    return


#  def audit_experiment_control_out_of_date_analysis(value, system):
#  removed due to https://encodedcc.atlassian.net/browse/ENCD-3460

# def create_pipeline_structures(files_to_scan, structure_type):
# condensed under https://encodedcc.atlassian.net/browse/ENCD-3493

# def check_structures(replicate_structures, control_flag, experiment):
# https://encodedcc.atlassian.net/browse/ENCD-3538

# def audit_experiment_gtex_biosample(value, system):
# https://encodedcc.atlassian.net/browse/ENCD-3538

# def audit_experiment_biosample_term_id(value, system): removed release 56
# http://redmine.encodedcc.org/issues/4900

# def audit_experiment_needs_pipeline(value, system): removed in release 56
# http://redmine.encodedcc.org/issues/4990

# def audit_experiment_with_uploading_files(value, system, files_structure): removed in release 98
# https://encodedcc.atlassian.net/browse/ENCD-5109
