from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)
from .standards_data import pipelines_with_read_depth, minimal_read_depth_requirements


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
    'siRNA knockdown followed by RNA-seq',
    'CRISPR genome editing followed by RNA-seq',
    'CRISPRi followed by RNA-seq',
    'PLAC-seq',
]

controlRequiredAssayList = [
    'ChIP-seq',
    'RNA Bind-n-Seq',
    'RIP-seq',
    'RAMPAGE',
    'CAGE',
    'eCLIP',
    'single cell isolation followed by RNA-seq',
    'shRNA knockdown followed by RNA-seq',
    'siRNA knockdown followed by RNA-seq',
    'CRISPR genome editing followed by RNA-seq',
    'CRISPRi followed by RNA-seq'
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
    'PLAC-seq',
    'microRNA-seq',
    'long read RNA-seq',
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
                    'ChIP-seq']:
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
            if assay_term_name == 'ChIP-seq' and 'run_type' in file_object:
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
    if assay_term_name == 'ChIP-seq':  
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
    if value['assay_term_name'] in ['single cell isolation followed by RNA-seq',
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
        biosample_classification = value.get(
            'biosample_ontology', {'classification': 'unknown'}
        )['classification']
        if biosample_classification == 'single cell':
            return
        # different levels of severity for different biosample classifications
        else:
            detail = ('This experiment is expected to be replicated, but '
                'contains only one listed biological replicate.')
            level='NOT_COMPLIANT'
            if biosample_classification in ['tissue', 'primary cell']:
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


def is_tagging_genetic_modification(modification):
    if modification['purpose'] == 'tagging':
        return True
    return False


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
                   assay_name != 'single cell isolation followed by RNA-seq':
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
        yield AuditFailure('inconsistent experiment target', detail, level='INTERNAL_ACTION')

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
    if value.get('assay_term_name') == 'single cell isolation followed by RNA-seq' and \
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
    if dataset['@type'][0] in ['Dataset']:
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
    if value.get('assay_term_name') != 'ChIP-seq':
        return

    # We do not want controls
    if value.get('control_type'):
        return

    if not value['possible_controls']:
        return

    num_IgG_controls = 0

    for control_dataset in value['possible_controls']:
        if not is_control_dataset(control_dataset):
            detail = (
                'Experiment {} is ChIP-seq but its control {} does not '
                'have a valid "control_type".'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    audit_link(path_to_text(control_dataset['@id']), control_dataset['@id'])
                )
            )
            yield AuditFailure('invalid possible_control', detail, level='ERROR')
            return

        if not control_dataset.get('replicates'):
            continue

        if 'antibody' in control_dataset.get('replicates')[0]:
            num_IgG_controls += 1

    # If all of the possible_control experiments are mock IP control experiments
    if num_IgG_controls == len(value['possible_controls']):
        if value.get('assay_term_name') == 'ChIP-seq':
            # The binding group agreed that ChIP-seqs all should have an input control.
            detail = ('Experiment {} is ChIP-seq and requires at least one input control,'
                ' as agreed upon by the binding group. Experiment {} is not an input control'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    audit_link(path_to_text(control_dataset['@id']), control_dataset['@id'])
                )
            )
            yield AuditFailure('missing input control', detail, level='NOT_COMPLIANT')
    return


def is_control_dataset(dataset):
    return bool(dataset.get('control_type'))


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
            detail = ('Library {} is in '
                'an RNA-seq experiment and has size_range >200. '
                'It requires a value for spikeins_used'.format(
                    audit_link(path_to_text(lib['@id']), lib['@id'])
                )
            )
            yield AuditFailure('missing spikeins', detail, level='NOT_COMPLIANT')
            # Informattional if ENCODE2 and release error if ENCODE3
    return


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
            yield AuditFailure('term_id not in ontology', term_id, level='INTERNAL_ACTION')
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
        if (lib['nucleic_acid_term_name'] in RNAs) and ('size_range' not in lib):
            detail = ('Metadata of RNA library {} lacks information on '
                'the size range of fragments used to construct the library.'.format(
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
                 'OBI:0001271', # RNA-seq (poly(A)-, poly(A)+, small, and total)
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


def audit_experiment_inconsistent_analyses_files(value, system, files_structure):
    processed_data = files_structure.get('processed_data')
    files_not_in_analysis = []
    files_not_in_processed_data = []
    if processed_data and 'analyses' in value:
        analysis_outputs = set()
        for analysis in value['analyses']:
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
        yield AuditFailure('inconsistent analyses files', detail, level='INTERNAL_ACTION')
    if len(files_not_in_processed_data) > 0:
        files_not_in_processed_data_links = [audit_link(path_to_text(file), file) for file in files_not_in_processed_data]
        detail = ('Experiment {} '
                'contains file(s) in an analysis {} '
                'not in processed data'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    ', '.join(files_not_in_processed_data_links)
                )
            )
        yield AuditFailure('inconsistent analyses files', detail, level='INTERNAL_ACTION')


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


def get_read_lengths_wgbs(fastq_files):
    list_of_lengths = []
    for f in fastq_files:
        if 'read_length' in f:
            list_of_lengths.append(f['read_length'])
    return list_of_lengths


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
                 'signal_files': {},
                 'preferred_default_idr_peaks': {},
                 'cpg_quantifications': {},
                 'contributing_files': {},
                 'raw_data': {},
                 'processed_data': {},
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

                if file_output and file_output == 'methylation state at CpG':
                    to_return['cpg_quantifications'][file_object['@id']
                                                     ] = file_object

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
    if assay_name != 'ChIP-seq':
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
        if assay_name == 'ChIP-seq' and file_acc not in derived_from_fastq_accessions:
            paired_file_id = file_object.get('paired_with')
            if paired_file_id and paired_file_id.split('/')[2] not in derived_from_fastq_accessions:
                return True
            elif not paired_file_id:
                return True
        # for DNase all the files from tech. rep should be in the list of the derived_from
        elif assay_name != 'ChIP-seq' and file_acc not in derived_from_fastq_accessions:
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

function_dispatcher_without_files = {}

function_dispatcher_with_files = {}


@audit_checker(
    'Dataset',
    frame=[
        'biosample_ontology',
        'award',
        'target',
        'contributing_files',
        'original_files',
        'original_files.award',
        'original_files.platform'
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

@audit_checker('Dataset', frame=['original_files'])
def audit_experiment_released_with_unreleased_files(value, system):
    if value['status'] != 'released':
        return
    if 'original_files' not in value:
        return
    for f in value['original_files']:
        if f['status'] not in ['released', 'deleted',
                               'revoked', 'replaced',
                               'archived']:
            detail = ('Released dataset {} contains file {} that has not been released.'.format(
                    audit_link(path_to_text(value['@id']), value['@id']),
                    audit_link(path_to_text(f['@id']), f['@id'])
                )
            )
            yield AuditFailure('mismatched file status', detail, level='INTERNAL_ACTION')
    return


@audit_checker('Dataset', frame=['original_files'])
def audit_dataset_with_uploading_files(value, system):
    for file in value['original_files']:
        category = None
        if file['status'] in ['upload failed', 'content error']:
            category = 'file validation error'
        elif file['status'] == 'uploading':
            category = 'file in uploading state'

        if category is not None:
            detail = ('Dataset {} contains a file {} with the status {}.'.format(
                audit_link(path_to_text(value['@id']), value['@id']),
                audit_link(path_to_text(file['@id']), file['@id']),
                file['status']
                )
            )
            yield AuditFailure(category, detail, level='ERROR')
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
