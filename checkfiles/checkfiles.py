"""\
Run sanity checks on files.

Example.

    %(prog)s --username ACCESS_KEY_ID --password SECRET_ACCESS_KEY \\
        --output check_files.log https://www.encodeproject.org
"""
import datetime
import os.path
import json
import sys
from shlex import quote
import subprocess
from urllib.parse import urljoin
import re

EPILOG = __doc__

GZIP_TYPES = [
    "CEL",
    "bam",
    "bed",
    "csfasta",
    "csqual",
    "fasta",
    "fastq",
    "gff",
    "gtf",
    "tagAlign",
    "tar",
    "sam",
    "wig",
]


def is_path_gzipped(path):
    with open(path, 'rb') as f:
        magic_number = f.read(2)
    return magic_number == b'\x1f\x8b'


def check_format(encValData, job, path):
    """ Local validation
    """
    ASSEMBLY_MAP = {
        'GRCh38-minimal': 'GRCh38',
        'mm10-minimal': 'mm10'
    }

    errors = job['errors']
    item = job['item']
    result = job['result']

    # if assembly is in the map, use the mapping, otherwise just use the string in assembly
    assembly = ASSEMBLY_MAP.get(item.get('assembly'), item.get('assembly'))

    if item['file_format'] == 'bam' and item.get('output_type') == 'transcriptome alignments':
        if 'assembly' not in item:
            errors['assembly'] = 'missing assembly'
        if 'genome_annotation' not in item:
            errors['genome_annotation'] = 'missing genome_annotation'
        if errors:
            return errors
        chromInfo = '-chromInfo=%s/%s/%s/chrom.sizes' % (
            encValData, assembly, item['genome_annotation'])
    else:
        chromInfo = '-chromInfo=%s/%s/chrom.sizes' % (encValData, assembly)

    validate_map = {
        ('fasta', None): ['-type=fasta'],
        ('fastq', None): ['-type=fastq'],
        ('bam', None): ['-type=bam', chromInfo],
        ('bigWig', None): ['-type=bigWig', chromInfo],
        # standard bed formats
        ('bed', 'bed3'): ['-type=bed3', chromInfo],
        ('bigBed', 'bed3'): ['-type=bigBed3', chromInfo],
        ('bed', 'bed5'): ['-type=bed5', chromInfo],
        ('bigBed', 'bed5'): ['-type=bigBed5', chromInfo],
        ('bed', 'bed6'): ['-type=bed6', chromInfo],
        ('bigBed', 'bed6'): ['-type=bigBed6', chromInfo],
        ('bed', 'bed9'): ['-type=bed9', chromInfo],
        ('bigBed', 'bed9'): ['-type=bigBed9', chromInfo],
        ('bedGraph', None): ['-type=bedGraph', chromInfo],
        # extended "bed+" formats, -tab is required to allow for text fields to contain spaces
        ('bed', 'bed3+'): ['-tab', '-type=bed3+', chromInfo],
        ('bigBed', 'bed3+'): ['-tab', '-type=bigBed3+', chromInfo],
        ('bed', 'bed6+'): ['-tab', '-type=bed6+', chromInfo],
        ('bigBed', 'bed6+'): ['-tab', '-type=bigBed6+', chromInfo],
        ('bed', 'bed9+'): ['-tab', '-type=bed9+', chromInfo],
        ('bigBed', 'bed9+'): ['-tab', '-type=bigBed9+', chromInfo],
        # a catch-all shoe-horn (as long as it's tab-delimited)
        ('bed', 'unknown'): ['-tab', '-type=bed3+', chromInfo],
        ('bigBed', 'unknown'): ['-tab', '-type=bigBed3+', chromInfo],
        # special bed types
        ('bed', 'bedLogR'): ['-type=bed9+1', chromInfo, '-as=%s/as/bedLogR.as' % encValData],
        ('bigBed', 'bedLogR'): ['-type=bigBed9+1', chromInfo, '-as=%s/as/bedLogR.as' % encValData],
        ('bed', 'bedMethyl'): ['-type=bed9+2', chromInfo, '-as=%s/as/bedMethyl.as' % encValData],
        ('bigBed', 'bedMethyl'): ['-type=bigBed9+2', chromInfo, '-as=%s/as/bedMethyl.as' % encValData],
        ('bed', 'broadPeak'): ['-type=bed6+3', chromInfo, '-as=%s/as/broadPeak.as' % encValData],
        ('bigBed', 'broadPeak'): ['-type=bigBed6+3', chromInfo, '-as=%s/as/broadPeak.as' % encValData],
        ('bed', 'gappedPeak'): ['-type=bed12+3', chromInfo, '-as=%s/as/gappedPeak.as' % encValData],
        ('bigBed', 'gappedPeak'): ['-type=bigBed12+3', chromInfo, '-as=%s/as/gappedPeak.as' % encValData],
        ('bed', 'narrowPeak'): ['-type=bed6+4', chromInfo, '-as=%s/as/narrowPeak.as' % encValData],
        ('bigBed', 'narrowPeak'): ['-type=bigBed6+4', chromInfo, '-as=%s/as/narrowPeak.as' % encValData],
        ('bed', 'bedRnaElements'): ['-type=bed6+3', chromInfo, '-as=%s/as/bedRnaElements.as' % encValData],
        ('bigBed', 'bedRnaElements'): ['-type=bed6+3', chromInfo, '-as=%s/as/bedRnaElements.as' % encValData],
        ('bed', 'bedExonScore'): ['-type=bed6+3', chromInfo, '-as=%s/as/bedExonScore.as' % encValData],
        ('bigBed', 'bedExonScore'): ['-type=bigBed6+3', chromInfo, '-as=%s/as/bedExonScore.as' % encValData],
        ('bed', 'bedRrbs'): ['-type=bed9+2', chromInfo, '-as=%s/as/bedRrbs.as' % encValData],
        ('bigBed', 'bedRrbs'): ['-type=bigBed9+2', chromInfo, '-as=%s/as/bedRrbs.as' % encValData],
        ('bed', 'enhancerAssay'): ['-type=bed9+1', chromInfo, '-as=%s/as/enhancerAssay.as' % encValData],
        ('bigBed', 'enhancerAssay'): ['-type=bigBed9+1', chromInfo, '-as=%s/as/enhancerAssay.as' % encValData],
        ('bed', 'modPepMap'): ['-type=bed9+7', chromInfo, '-as=%s/as/modPepMap.as' % encValData],
        ('bigBed', 'modPepMap'): ['-type=bigBed9+7', chromInfo, '-as=%s/as/modPepMap.as' % encValData],
        ('bed', 'pepMap'): ['-type=bed9+7', chromInfo, '-as=%s/as/pepMap.as' % encValData],
        ('bigBed', 'pepMap'): ['-type=bigBed9+7', chromInfo, '-as=%s/as/pepMap.as' % encValData],
        ('bed', 'openChromCombinedPeaks'): ['-type=bed9+12', chromInfo, '-as=%s/as/openChromCombinedPeaks.as' % encValData],
        ('bigBed', 'openChromCombinedPeaks'): ['-type=bigBed9+12', chromInfo, '-as=%s/as/openChromCombinedPeaks.as' % encValData],
        ('bed', 'peptideMapping'): ['-type=bed6+4', chromInfo, '-as=%s/as/peptideMapping.as' % encValData],
        ('bigBed', 'peptideMapping'): ['-type=bigBed6+4', chromInfo, '-as=%s/as/peptideMapping.as' % encValData],
        ('bed', 'shortFrags'): ['-type=bed6+21', chromInfo, '-as=%s/as/shortFrags.as' % encValData],
        ('bigBed', 'shortFrags'): ['-type=bigBed6+21', chromInfo, '-as=%s/as/shortFrags.as' % encValData],
        ('bed', 'encode_elements_H3K27ac'): ['-tab', '-type=bed9+1', chromInfo, '-as=%s/as/encode_elements_H3K27ac.as' % encValData],
        ('bigBed', 'encode_elements_H3K27ac'): ['-tab', '-type=bigBed9+1', chromInfo, '-as=%s/as/encode_elements_H3K27ac.as' % encValData],
        ('bed', 'encode_elements_H3K9ac'): ['-tab', '-type=bed9+1', chromInfo, '-as=%s/as/encode_elements_H3K9ac.as' % encValData],
        ('bigBed', 'encode_elements_H3K9ac'): ['-tab', '-type=bigBed9+1', chromInfo, '-as=%s/as/encode_elements_H3K9ac.as' % encValData],
        ('bed', 'encode_elements_H3K4me1'): ['-tab', '-type=bed9+1', chromInfo, '-as=%s/as/encode_elements_H3K4me1.as' % encValData],
        ('bigBed', 'encode_elements_H3K4me1'): ['-tab', '-type=bigBed9+1', chromInfo, '-as=%s/as/encode_elements_H3K4me1.as' % encValData],
        ('bed', 'encode_elements_H3K4me3'): ['-tab', '-type=bed9+1', chromInfo, '-as=%s/as/encode_elements_H3K4me3.as' % encValData],
        ('bigBed', 'encode_elements_H3K4me3'): ['-tab', '-type=bigBed9+1', chromInfo, '-as=%s/as/encode_elements_H3K4me3.as' % encValData],
        ('bed', 'dnase_master_peaks'): ['-tab', '-type=bed9+1', chromInfo, '-as=%s/as/dnase_master_peaks.as' % encValData],
        ('bigBed', 'dnase_master_peaks'): ['-tab', '-type=bigBed9+1', chromInfo, '-as=%s/as/dnase_master_peaks.as' % encValData],
        ('bed', 'encode_elements_dnase_tf'): ['-tab', '-type=bed5+1', chromInfo, '-as=%s/as/encode_elements_dnase_tf.as' % encValData],
        ('bigBed', 'encode_elements_dnase_tf'): ['-tab', '-type=bigBed5+1', chromInfo, '-as=%s/as/encode_elements_dnase_tf.as' % encValData],
        ('bed', 'candidate enhancer predictions'): ['-type=bed3+', chromInfo, '-as=%s/as/candidate_enhancer_prediction.as' % encValData],
        ('bigBed', 'candidate enhancer predictions'): ['-type=bigBed3+', chromInfo, '-as=%s/as/candidate_enhancer_prediction.as' % encValData],
        ('bed', 'enhancer predictions'): ['-type=bed3+', chromInfo, '-as=%s/as/enhancer_prediction.as' % encValData],
        ('bigBed', 'enhancer predictions'): ['-type=bigBed3+', chromInfo, '-as=%s/as/enhancer_prediction.as' % encValData],
        ('bed', 'idr_peak'): ['-type=bed6+', chromInfo, '-as=%s/as/idr_peak.as' % encValData],
        ('bigBed', 'idr_peak'): ['-type=bigBed6+', chromInfo, '-as=%s/as/idr_peak.as' % encValData],
        ('bed', 'tss_peak'): ['-type=bed6+', chromInfo, '-as=%s/as/tss_peak.as' % encValData],
        ('bigBed', 'tss_peak'): ['-type=bigBed6+', chromInfo, '-as=%s/as/tss_peak.as' % encValData],


        ('bedpe', None): ['-type=bed3+', chromInfo],
        ('bedpe', 'mango'): ['-type=bed3+', chromInfo],
        # non-bed types
        ('rcc', None): ['-type=rcc'],
        ('idat', None): ['-type=idat'],
        ('gtf', None): None,
        ('tagAlign', None): ['-type=tagAlign', chromInfo],
        ('tar', None): None,
        ('tsv', None): None,
        ('csv', None): None,
        ('2bit', None): None,
        ('csfasta', None): ['-type=csfasta'],
        ('csqual', None): ['-type=csqual'],
        ('CEL', None): None,
        ('sam', None): None,
        ('wig', None): None,
        ('hdf5', None): None,
        ('gff', None): None,
        ('vcf', None): None,
        ('btr', None): None
    }

    validate_args = validate_map.get((item['file_format'], item.get('file_format_type')))
    if validate_args is None:
        return

    if chromInfo in validate_args and 'assembly' not in item:
        errors['assembly'] = 'missing assembly'
        return

    result['validateFiles_args'] = ' '.join(validate_args)


def process_fastq_file(job, unzipped_fastq_path, session, url):
    '''
    1) for fastqs, we should calculate the read length (V)

    2) for fastqs, we should calculate the read count (V) -> possibly even run fastqc (X)

    3) For the fastqs we should try to figure out the flow cell details (V)

    4) For the fastqs we should try to figure out if it is read 1 or read
    2 and error if it is both or if it does not match the submitted (X)

    5) For the fastqs we should try to figure out if there is duplication. (V)
    '''

    item = job['item']
    errors = job['errors']
    result = job['result']

    sequence_pattern = re.compile('[ACTGN.]+')
    read_name_pattern = re.compile(
        '^(@[a-zA-Z\d]+[a-zA-Z\d_-]*:\d+:[a-zA-Z\d]+:\d+:\d+:\d+:\d+[\s_][12]:[YN]:[0-9]+:([ACNTG]+|[0-9]+))$'
        )
    read_count = 0
    read_lengths = set()
    unique_tuples_set = set()
    unique_string_ids_set = set()

    fastq_data_file = unzipped_fastq_path.split('_')[0] + '.info'

    try:
        print ('checking file ' + unzipped_fastq_path)
        with open(unzipped_fastq_path, 'r') as f:
            line_counter = 0
            for line in f:
                line_counter += 1
                first_colon = line.find(":")
                if line_counter == 1:
                    read_name = line.strip()
                    if read_name_pattern.match(read_name) is None:
                        errors['fastq_format_readname'] = 'submitted fastq file does not ' + \
                                                          'comply with illumina fastq read name format, ' + \
                                                          'read name was : {}'.format(read_name)
                    else:
                        sub_line = line[first_colon:].strip()
                        sub_line_array = re.split(r'[\s_]', sub_line)
                        if len(sub_line_array) == 2:  # assuming new illumina format
                            line_array = re.split(r'[:\s_]', line.strip())

                            flowcell = line_array[2]
                            lane_number = line_array[3]
                            read_number = line_array[-4]
                            barcode_index = line_array[-1]
                            unique_tuples_set.add((
                                flowcell,
                                lane_number,
                                read_number,
                                barcode_index
                                ))
                            unique_string_ids_set.add(
                                flowcell+':'+lane_number+':'+read_number+':'+barcode_index)
                        # else:  # either old or unknown read name convention
                            # count reads at least
                if line_counter == 2:  # sequence
                    sequence = line.strip()
                    if sequence_pattern.match(sequence) is not None:
                        read_count += 1
                        read_lengths.add(len(sequence))
                    else:
                        errors['fastq_format_sequence'] = 'submitted fastq file does not ' + \
                                                          'comply with illumina sequence fastq format, ' + \
                                                          'sequence was : {}'.format(sequence)
                        break
                # print (line)
                line_counter = line_counter % 4

        with open(fastq_data_file, 'w') as output:
            output.write('read_count\t'+str(read_count)+'\n')
            if len(read_lengths) > 0:
                output.write('read_length\t'+str(sorted(list(read_lengths))) + '\n')
            output.write('unique_signature\t'+str(sorted(list(unique_string_ids_set))) + '\n')
            unique_tuples_list_1 = sorted(list(unique_tuples_set))
            if len(unique_tuples_list_1) > 0:
                read_numbers = [x[2] for x in unique_tuples_list_1]
                read_numbers_list = sorted(list(set(read_numbers)))
                output.write('read_1_or_2\t' + str(read_numbers_list) + '\n')

            if not errors:
                #################
                # read_lengths
                #################

                print ('READ LENGTHS FOUND : ' + str(read_lengths))

                read_lengths_list = list(read_lengths)
                max_length = max(read_lengths_list)
                min_length = min(read_lengths_list)
                if 'read_length' in item:
                    print ('READ LENGTHS SUBMITTED : ' + str(item['read_length']))
                    reported_read_length = item['read_length']
                    if abs(reported_read_length - min_length) > 2 and \
                       abs(reported_read_length - max_length) > 2:
                        errors['read_length'] = 'read length {} in the uploaded file '.format(
                            reported_read_length) + \
                            'doesn\'t match read length(s) found in the file {}.'.format(
                            read_lengths_list)
                else:
                    errors['read_length'] = 'no specified read length in the uploaded fastq file, ' + \
                                            'while read length(s) found in the file were {}.'.format(
                                            ', '.join(read_lengths_list))
                #################
                # number_reads
                #################

                print ('COUNTED ' + str(read_count) + ' READS')
                # result['read_count'] = read_count

                ######################################
                # uniqueness / detected_flowcell_details validation
                ######################################
                unique_tuples_list = sorted(list(unique_tuples_set))
                # detected_flowcell_details = []
                if len(unique_tuples_list) > 0:
                    detected_flowcell_details = sorted(list(set([(x[0], x[1]) for x in unique_tuples_list])))
                    read_numbers = [x[2] for x in unique_tuples_list]
                    read_numbers_set = set(read_numbers)
                    if len(read_numbers_set) > 1:
                        errors['inconsistent_read_numbers'] = \
                            'fastq file contains mixed read numbers ' + \
                            '{}.'.format(', '.join(sorted(list(read_numbers_set))))

                    # for unique_tuple in unique_tuples_list:
                    #    detected_flowcell_details.append((unique_tuple[0],
                    #                                      unique_tuple[1]))
                    if 'flowcell_details' in item and len(item['flowcell_details']) > 0:
                        uniqueness_flag = True
                        submitted_flowcell_information = item['flowcell_details']
                        if len(unique_tuples_list) > 0:
                            # validation
                            submitted_flowcell_details = []
                            for entry in submitted_flowcell_information:
                                if 'flowcell' in entry and \
                                   'lane' in entry:
                                    submitted_flowcell = (entry['flowcell'],
                                                          entry['lane'])
                                    submitted_flowcell_details.append(submitted_flowcell)
                            difference = sorted(list(set(detected_flowcell_details) -
                                                set(submitted_flowcell_details)))
                            if len(difference) > 0:
                                errors['flowcell_details'] = \
                                    'specified in the metadata flowcell_details {} does mot match '.format(
                                        submitted_flowcell_details) + \
                                    'flowcell details {} '.format(detected_flowcell_details) + \
                                    'extracted from the read names.'

                            # check for uniqueness
                            conflicts = []
                            for unique_string_id in unique_string_ids_set:
                                query = '/'+unique_string_id
                                r = session.get(urljoin(url, query))
                                r_graph = r.json().get('@graph')
                                if r_graph is not None and len(r_graph) > 0:
                                    uniqueness_flag = False

                                    conflicts = [
                                        'specified unique identifier {} '.format(unique_string_id) +
                                        'is conflicting with identifier of reads from ' +
                                        'file {}.'.format(x['accession']) for x in r_graph]
                                    # for entry in r_graph:
                                    #    conflicts += \
                                    #        'specified unique identifier {} '.format(unique_string_id) + \
                                    #        'is conflicting with identifier of reads from ' + \
                                    #        'file {}.'.format(entry['accession'])
                        if uniqueness_flag is True:
                            # fill in the properties

                            print ('UNIQUE IDENTIFIERS ARE ' + str(unique_string_ids_set))
                            # result['fastq_signature'] = sorted(list(unique_string_ids_set))
                        else:
                            errors['not_unique_flowcell_details'] = conflicts

                    elif detected_flowcell_details != []:
                        errors['flowcell_details'] = 'no specified flowcell_details in a fastq file ' + \
                                                     ' containing reads with following flowcell ' + \
                                                     'identifiers {}.'.format(detected_flowcell_details)
            for key in errors:
                output.write(key + '\t' + str(errors[key]) + '\n')

    except IOError:
        errors['file_open_error'] = 'OS could not open the file ' + \
                                    unzipped_fastq_path


def check_for_contentmd5sum_conflicts(item, result, output, errors, session, url):
    result['content_md5sum'] = output[:32].decode(errors='replace')
    try:
        int(result['content_md5sum'], 16)
    except ValueError:
        errors['content_md5sum'] = output.decode(errors='replace').rstrip('\n')
    else:
        query = '/search/?type=File&status!=replaced&content_md5sum=' + result[
            'content_md5sum']
        r = session.get(urljoin(url, query))
        r_graph = r.json().get('@graph')
        if len(r_graph) > 0:
            conflicts = []
            for entry in r_graph:
                if 'accession' in entry and 'accession' in item:
                    if entry['accession'] != item['accession']:
                        conflicts.append(
                            'checked %s is conflicting with content_md5sum of %s' % (
                                result['content_md5sum'],
                                entry['accession']))
                else:
                    conflicts.append(
                        'checked %s is conflicting with content_md5sum of %s' % (
                            result['content_md5sum'],
                            entry['accession']))
            if len(conflicts) > 0:
                errors['content_md5sum'] = str(conflicts)


def check_file(config, session, url, job):
    item = job['item']
    errors = job['errors']
    result = job['result'] = {}

    if job.get('skip'):
        return job

    upload_url = job['upload_url']
    local_path = os.path.join(config['mirror'], upload_url[len('s3://'):])

    try:
        file_stat = os.stat(local_path)
    except FileNotFoundError:
        errors['file_not_found'] = 'File has not been uploaded yet.'
        if job['run'] < job['upload_expiration']:
            job['skip'] = True
        return job

    if 'file_size' in item and file_stat.st_size != item['file_size']:
        errors['file_size'] = 'uploaded {} does not match item {}'.format(
            file_stat.st_size, item['file_size'])

    result["file_size"] = file_stat.st_size
    result["last_modified"] = datetime.datetime.utcfromtimestamp(
        file_stat.st_mtime).isoformat() + 'Z'

    is_gzipped = is_path_gzipped(local_path)
    if item['file_format'] not in GZIP_TYPES:
        if is_gzipped:
            errors['gzip'] = 'Expected un-gzipped file'
    elif not is_gzipped:
        errors['gzip'] = 'Expected gzipped file'
    else:
        if item['file_format'] == 'bed':
            try:
                # unzipped_original_bed_path = local_path[-18:-7] + '_original.bed'
                unzipped_modified_bed_path = local_path[-18:-7] + '_modified.bed'

                output = subprocess.check_output(
                    'set -o pipefail; gunzip --stdout | ' +
                    'tee >(grep -v \'^#\' > {}) | md5sum'.format(
                        unzipped_modified_bed_path),
                    shell=True, executable='/bin/bash', stderr=subprocess.STDOUT)
                ''' CAN BE REMOVED THANKS TO PIPING
                output = subprocess.check_output(
                    'set -o pipefail; md5sum {}'.format(unzipped_original_bed_path),
                    shell=True, executable='/bin/bash', stderr=subprocess.STDOUT)
                '''
            except subprocess.CalledProcessError as e:
                errors['content_md5sum'] = e.output.decode(errors='replace').rstrip('\n')
            else:
                check_for_contentmd5sum_conflicts(item, result, output, errors, session, url)
                ''' CAN BE REMOVED THANKS TO PIPING
                if os.path.exists(unzipped_original_bed_path):
                    try:
                        os.remove(unzipped_original_bed_path)
                    except OSError as e:
                        errors['file_remove_error'] = 'OS could not remove the file ' + \
                                                      unzipped_original_bed_path
                '''
        else:
            # May want to replace this with something like:
            # $ cat $local_path | tee >(md5sum >&2) | gunzip | md5sum
            # or http://stackoverflow.com/a/15343686/199100
            try:
                if item['file_format'] == 'fastq':
                    if file_stat.st_size < 20000000000:
                        unzipped_fastq_path = local_path[-20:-9] + '_original.fastq'                    
                        output = subprocess.check_output(
                            'set -o pipefail; gunzip --stdout {} > {}'.format(
                                local_path, unzipped_fastq_path),
                            shell=True, executable='/bin/bash', stderr=subprocess.STDOUT)
                else:
                    output = subprocess.check_output(
                        'set -o pipefail; gunzip --stdout %s | md5sum' % quote(local_path),
                        shell=True, executable='/bin/bash', stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                errors['content_md5sum'] = e.output.decode(errors='replace').rstrip('\n')
    if not errors:
        if item['file_format'] == 'bed':
            check_format(config['encValData'], job, unzipped_modified_bed_path)
        else:
            check_format(config['encValData'], job, local_path)

        if item['file_format'] == 'fastq':
            if file_stat.st_size < 20000000000:
                process_fastq_file(job, unzipped_fastq_path, session, url)

    if item['file_format'] == 'bed':
        try:
            unzipped_modified_bed_path = unzipped_modified_bed_path
            if os.path.exists(unzipped_modified_bed_path):
                try:
                    os.remove(unzipped_modified_bed_path)
                except OSError as e:
                    errors['file_remove_error'] = 'OS could not remove the file ' + \
                                                  unzipped_modified_bed_path
        except NameError:
            pass
    elif item['file_format'] == 'fastq':
        try:
            unzipped_fastq_path = unzipped_fastq_path
            if os.path.exists(unzipped_fastq_path):
                try:
                    os.remove(unzipped_fastq_path)
                except OSError as e:
                    errors['file_remove_error'] = 'OS could not remove the file ' + \
                                                  unzipped_fastq_path
        except NameError:
            pass

    if item['status'] != 'uploading':
        errors['status_check'] = \
            "status '{}' is not 'uploading'".format(item['status'])

    return job


def fetch_files(session, url, search_query, out, include_unexpired_upload=False):
    r = session.get(
        urljoin(url, '/search/?field=@id&limit=all&type=File&' + search_query))
    r.raise_for_status()
    out.write("PROCESSING: %d files in query: %s\n" % (len(r.json()['@graph']), search_query))
    for result in r.json()['@graph']:
        job = {
            '@id': result['@id'],
            'errors': {},
            'run': datetime.datetime.utcnow().isoformat() + 'Z',
        }
        errors = job['errors']
        item_url = urljoin(url, job['@id'])

        r = session.get(item_url + '@@upload?datastore=database')
        if r.ok:
            upload_credentials = r.json()['@graph'][0]['upload_credentials']
            job['upload_url'] = upload_credentials['upload_url']
            # Files grandfathered from EDW have no upload expiration.
            job['upload_expiration'] = upload_credentials.get('expiration', '')
            # Only check files that will not be changed during the check.
            if job['run'] < job['upload_expiration']:
                if not include_unexpired_upload:
                    continue
        else:
            job['errors']['get_upload_url_request'] = \
                '{} {}\n{}'.format(r.status_code, r.reason, r.text)

        r = session.get(item_url + '?frame=edit&datastore=database')
        if r.ok:
            item = job['item'] = r.json()
            job['etag'] = r.headers['etag']
        else:
            errors['get_edit_request'] = \
                '{} {}\n{}'.format(r.status_code, r.reason, r.text)

        if errors:
            job['skip'] = True  # Probably a transient error

        yield job


def patch_file(session, url, job):
    item = job['item']
    result = job['result']
    errors = job['errors']
    if errors:
        return
    item_url = urljoin(url, job['@id'])

    if not errors:
        data = {
            'status': 'in progress',
            'file_size': result['file_size'],
        }
        if 'content_md5sum' in result:
            data['content_md5sum'] = result['content_md5sum']
        r = session.patch(
            item_url,
            data=json.dumps(data),
            headers={
                'If-Match': job['etag'],
                'Content-Type': 'application/json',
            },
        )
        if not r.ok:
            errors['patch_file_request'] = \
                '{} {}\n{}'.format(r.status_code, r.reason, r.text)
        else:
            job['patched'] = True


def run(out, err, url, username, password, encValData, mirror, search_query,
        processes=None, include_unexpired_upload=False, dry_run=False, json_out=False):
    import functools
    import multiprocessing
    import requests
    session = requests.Session()
    session.auth = (username, password)
    session.headers['Accept'] = 'application/json'

    config = {
        'encValData': encValData,
        'mirror': mirror,
    }

    dr = ""
    if dry_run:
        dr = "-- Dry Run"
    try:
        nprocesses = multiprocessing.cpu_count()
    except multiprocessing.NotImplmentedError:
        nprocesses = 1

    out.write("STARTING Checkfiles (%s): with %d processes %s at %s\n" %
             (search_query, nprocesses, dr, datetime.datetime.now()))
    if processes == 0:
        # Easier debugging without multiprocessing.
        imap = map
    else:
        pool = multiprocessing.Pool(processes=processes)
        imap = pool.imap_unordered

    jobs = fetch_files(session, url, search_query, out, include_unexpired_upload)
    if not json_out:
        headers = '\t'.join(['Accession', 'Lab', 'Errors', 'Aliases', 'Upload URL',
                             'Upload Expiration'])
        out.write(headers + '\n')
        err.write(headers + '\n')
    for job in imap(functools.partial(check_file, config, session, url), jobs):
        if not dry_run:
            patch_file(session, url, job)

        tab_report = '\t'.join([
            job['item'].get('accession', 'UNKNOWN'),
            job['item'].get('lab', 'UNKNOWN'),
            str(job.get('errors', {'errors': None})),
            str(job['item'].get('aliases', ['n/a'])),
            job.get('upload_url', ''),
            job.get('upload_expiration', ''),
            ])

        if json_out:
            out.write(json.dumps(job) + '\n')
            if job['errors']:
                err.write(json.dumps(job) + '\n')
        else:
            out.write(tab_report + '\n')
            if job['errors']:
                err.write(tab_report + '\n')

    out.write("FINISHED Checkfiles at %s\n" % datetime.datetime.now())


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Update file status", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--mirror', default='/s3')
    parser.add_argument(
        '--encValData', default='/opt/encValData', help="encValData location")
    parser.add_argument(
        '--username', '-u', default='', help="HTTP username (access_key_id)")
    parser.add_argument(
        '--password', '-p', default='',
        help="HTTP password (secret_access_key)")
    parser.add_argument(
        '--out', '-o', type=argparse.FileType('w'), default=sys.stdout,
        help="file to write json lines of results with or without errors")
    parser.add_argument(
        '--err', '-e', type=argparse.FileType('w'), default=sys.stderr,
        help="file to write json lines of results with errors")
    parser.add_argument(
        '--processes', type=int,
        help="defaults to cpu count, use 0 for debugging in a single process")
    parser.add_argument(
        '--include-unexpired-upload', action='store_true',
        help="include files whose upload credentials have not yet expired (may be replaced!)")
    parser.add_argument(
        '--dry-run', action='store_true', help="Don't update status, just check")
    parser.add_argument(
        '--json-out', action='store_true', help="Output results as JSON (legacy)")
    parser.add_argument(
        '--search-query', default='status=uploading',
        help="override the file search query, e.g. 'accession=ENCFF000ABC'")
    parser.add_argument('url', help="server to post to")
    args = parser.parse_args()
    run(**vars(args))


if __name__ == '__main__':
    main()
