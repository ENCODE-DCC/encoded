pipeline_titles = ['Small RNA-seq single-end pipeline',
                   'RNA-seq of long RNAs (paired-end, stranded)',
                   'RNA-seq of long RNAs (single-end, unstranded)',
                   'RAMPAGE (paired-end, stranded)',
                   'Histone ChIP-seq']

read_depths_special = {'shRNA knockdown followed by RNA-seq': 10000000,
                       'single cell isolation followed by RNA-seq': 5000000}

read_depths = {'Small RNA-seq single-end pipeline': 30000000,
               'RNA-seq of long RNAs (paired-end, stranded)': 30000000,
               'RNA-seq of long RNAs (single-end, unstranded)': 30000000,
               'RAMPAGE (paired-end, stranded)': 25000000}

marks = {'narrow': 20000000,
         'broad': 45000000}


broadPeaksTargets = [
    'H3K4me1-mouse',
    'H3K36me3-mouse',
    'H3K79me2-mouse',
    'H3K27me3-mouse',
    'H3K9me1-mouse',
    'H3K9me3-mouse',
    'H3K4me1-human',
    'H3K36me3-human',
    'H3K79me2-human',
    'H3K27me3-human',
    'H3K9me1-human',
    'H3K9me3-human',
    'H3F3A-human',
    'H4K20me1-human',
    'H3K79me3-human',
    'H3K79me3-mouse',
    ]


def collectErrors(file_inspected, pipelines, read_depth, target_name, special_assay_name):
    errors_list = []
    for pipeline in pipelines:
        if pipeline['title'] not in pipeline_titles:
            continue

        if pipeline['title'] == 'Histone ChIP-seq':  # do the chipseq narrow broad ENCODE3
            if target_name in ['Control-human', 'Control-mouse']:
                if read_depth < marks['broad']:
                    detail = 'ENCODE Processed alignment ' + \
                             'file {} has {} '.format(file_inspected['@id'],
                                                      read_depth) + \
                             'uniquely mapped reads. It can not be used as a control ' + \
                             'in experiments studying broad histone marks, which ' + \
                             'require {} uniquely mapped reads.'.format(marks['broad'])
                    error_to_add = {'level': 'WARNING', 'detail': detail,
                                    'message': 'insufficient read depth'}
                    errors_list.append(error_to_add)
                if read_depth < marks['narrow']:
                    detail = 'ENCODE Processed alignment ' + \
                             'file {} has {} '.format(file_inspected['@id'],
                                                      read_depth) + \
                             'uniquely mapped reads. It can not be used as a control, ' + \
                             'due to insufficient read depth, narrow histone marks assays ' + \
                             'require {} uniquely mapped reads.'.format(marks['narrow'])
                    error_to_add = {'level': 'NOT_COMPLIANT', 'detail': detail,
                                    'message': 'insufficient read depth'}
                    errors_list.append(error_to_add)

                break

            if target_name == 'empty':
                detail = 'ENCODE Processed alignment file {} '.format(file_inspected['@id']) + \
                         'belongs to ChIP-seq experiment with no target specified.'
                error_to_add = {'level': 'ERROR', 'detail': detail,
                                'message': 'ChIP-seq missing target'}
                errors_list.append(error_to_add)
                break

            if target_name in broadPeaksTargets:
                if read_depth < marks['broad']:
                    detail = 'ENCODE Processed alignment ' + \
                             'file {} has {} '.format(file_inspected['@id'],
                                                      read_depth) + \
                             'uniquely mapped reads. Replicates for ChIP-seq ' + \
                             'assay and target {} require '.format(target_name) + \
                             '{}'.format(marks['broad'])
                    error_to_add = {'level': 'NOT_COMPLIANT', 'detail': detail,
                                    'message': 'insufficient read depth'}
                    errors_list.append(error_to_add)
                    break
            else:
                if read_depth < (marks['narrow']+5000000) and read_depth > marks['narrow']:
                    detail = 'ENCODE Processed alignment ' + \
                             'file {} has {} '.format(file_inspected['@id'],
                                                      read_depth) + \
                             'uniquely mapped reads. ' + \
                             'The recommended numer of uniquely mapped reads for ChIP-seq assay ' + \
                             'and target {} would be '.format(target_name) + \
                             '{}'.format(marks['narrow']+5000000)
                    error_to_add = {'level': 'WARNING', 'detail': detail,
                                    'message': 'low read depth'}
                    errors_list.append(error_to_add)
                    break
                if read_depth < marks['narrow']:
                    detail = 'ENCODE Processed alignment ' + \
                             'file {} has {} '.format(file_inspected['@id'],
                                                      read_depth) + \
                             'uniquely mapped reads. Replicates for ChIP-seq assay ' + \
                             'and target {} require '.format(target_name) + \
                             '{}'.format(marks['narrow'])
                    error_to_add = {'level': 'NOT_COMPLIANT', 'detail': detail,
                                    'message': 'insufficient read depth'}
                    errors_list.append(error_to_add)
                    break
        else:
            if special_assay_name != 'empty':  # either shRNA or single cell
                if read_depth < read_depths_special[special_assay_name]:
                    detail = 'ENCODE Processed alignment ' + \
                             'file {} has {} '.format(file_inspected['@id'],
                                                      read_depth) + \
                             'uniquely mapped reads. Replicates for this assay ' + \
                             '{} require '.format(pipeline['title']) + \
                             '{}'.format(read_depths_special[special_assay_name])
                    error_to_add = {'level': 'NOT_COMPLIANT', 'detail': detail,
                                    'message': 'insufficient read depth'}
                    errors_list.append(error_to_add)
                    break
            else:
                if (read_depth < read_depths[pipeline['title']]):
                    detail = 'ENCODE Processed alignment ' + \
                             'file {} has {} '.format(file_inspected['@id'], read_depth) + \
                             'uniquely mapped reads. Replicates for this ' + \
                             'assay {} require {}'.format(pipeline['title'],
                                                          read_depths[pipeline['title']])
                    error_to_add = {'level': 'NOT_COMPLIANT', 'detail': detail,
                                    'message': 'insufficient read depth'}
                    errors_list.append(error_to_add)
                    break
    return errors_list
