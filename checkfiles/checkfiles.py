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

            checked_list = ['ENCFF000BED', 'ENCFF000BEL', 'ENCFF000BEQ', 'ENCFF000BFR', 'ENCFF000BFU', 'ENCFF000BLU', 'ENCFF000BMI', 'ENCFF000BMX', 'ENCFF000BOE', 'ENCFF000BPB', 'ENCFF000BQG', 'ENCFF000CGW', 'ENCFF000CHU', 'ENCFF000CHZ', 'ENCFF000CMM', 'ENCFF000CMY', 'ENCFF000CNP', 'ENCFF000COB', 'ENCFF000COD', 'ENCFF000COI', 'ENCFF000COL', 'ENCFF000CPP', 'ENCFF000CPY', 'ENCFF000CQI', 'ENCFF000CRA', 'ENCFF000CRH', 'ENCFF000CRN', 'ENCFF000CRP', 'ENCFF000CRX', 'ENCFF000CSR', 'ENCFF000CTO', 'ENCFF000CTT', 'ENCFF000CUF', 'ENCFF000CVG', 'ENCFF000CVL', 'ENCFF000CVM', 'ENCFF000CWJ', 'ENCFF000CWV', 'ENCFF000CWX', 'ENCFF000JTT', 'ENCFF000JWC', 'ENCFF000KYY', 'ENCFF000KZS', 'ENCFF000KZT', 'ENCFF000LBN', 'ENCFF000LBV', 'ENCFF000LFT', 'ENCFF000LFX', 'ENCFF000LGE', 'ENCFF000LGF', 'ENCFF000LHU', 'ENCFF000LIN', 'ENCFF000LIR', 'ENCFF000LJN', 'ENCFF000LJW', 'ENCFF000LKX', 'ENCFF000LLB', 'ENCFF000LUH', 'ENCFF000LUK', 'ENCFF000LUQ', 'ENCFF000LVO', 'ENCFF000LVV', 'ENCFF000LWL', 'ENCFF000LWP', 'ENCFF000LXO', 'ENCFF000LXT', 'ENCFF000LYU', 'ENCFF000LZH', 'ENCFF000LZX', 'ENCFF000MAK', 'ENCFF000MAW', 'ENCFF000MDB', 'ENCFF000MDF', 'ENCFF000MDH', 'ENCFF000MEF', 'ENCFF000MET', 'ENCFF000MEV', 'ENCFF000MFM', 'ENCFF000MHJ', 'ENCFF000MIT', 'ENCFF000MJV', 'ENCFF000MLE', 'ENCFF000MLS', 'ENCFF000MLU', 'ENCFF000MMA', 'ENCFF000MMD', 'ENCFF000PIX', 'ENCFF000PKJ', 'ENCFF000PKR', 'ENCFF000PMC', 'ENCFF000PMF', 'ENCFF000PMU', 'ENCFF000PMZ', 'ENCFF000PPF', 'ENCFF000PQC', 'ENCFF000PQJ', 'ENCFF000PQU', 'ENCFF000PSA', 'ENCFF000PSW', 'ENCFF000PSY', 'ENCFF000PTO', 'ENCFF000PVC', 'ENCFF000PVZ', 'ENCFF000PWI', 'ENCFF000PWL', 'ENCFF000PWM', 'ENCFF000PZV', 'ENCFF000QAG', 'ENCFF000QBN', 'ENCFF000QCI', 'ENCFF000QCR', 'ENCFF000QCS', 'ENCFF000QED', 'ENCFF000QEG', 'ENCFF000QEJ', 'ENCFF000QGJ', 'ENCFF000QGV', 'ENCFF000QIM', 'ENCFF000QIS', 'ENCFF000QIU', 'ENCFF000QIW', 'ENCFF000QNC', 'ENCFF000QPW', 'ENCFF000QQA', 'ENCFF000ROS', 'ENCFF000RPB', 'ENCFF000RRN', 'ENCFF000RRS', 'ENCFF000RSE', 'ENCFF000RTX', 'ENCFF000RTY', 'ENCFF000RUA', 'ENCFF000RXB', 'ENCFF000RXE', 'ENCFF000RXO', 'ENCFF000RXR', 'ENCFF000RXS', 'ENCFF000RXV', 'ENCFF000RYB', 'ENCFF000RYT', 'ENCFF000RZC', 'ENCFF000RZT', 'ENCFF000RZV', 'ENCFF000RZY', 'ENCFF000SBI', 'ENCFF000SBO', 'ENCFF000SCV', 'ENCFF000SDQ', 'ENCFF000SDU', 'ENCFF000SGE', 'ENCFF000SKE', 'ENCFF000SKJ', 'ENCFF000SMZ', 'ENCFF000SNJ', 'ENCFF000SOT', 'ENCFF000SPK', 'ENCFF000SQT', 'ENCFF000SSV', 'ENCFF000STG', 'ENCFF000SVA', 'ENCFF000SYK', 'ENCFF000SZP', 'ENCFF000TCM', 'ENCFF000TEC', 'ENCFF000TED', 'ENCFF000TEQ', 'ENCFF000TEZ', 'ENCFF000TFC', 'ENCFF000THY', 'ENCFF000TIN', 'ENCFF000TIR', 'ENCFF000TJU', 'ENCFF000TLW', 'ENCFF000TMV', 'ENCFF000TND', 'ENCFF000TOT', 'ENCFF000TOU', 'ENCFF000TPA', 'ENCFF000TPU', 'ENCFF000TQI', 'ENCFF000VAU', 'ENCFF000VKE', 'ENCFF000VKZ', 'ENCFF000VLF', 'ENCFF000VRO', 'ENCFF000VRQ', 'ENCFF000VSG', 'ENCFF000VTF', 'ENCFF000VTN', 'ENCFF000VTX', 'ENCFF000VVB', 'ENCFF000VVX', 'ENCFF000VWL', 'ENCFF000VYE', 'ENCFF000VYM', 'ENCFF000VYN', 'ENCFF000VZU', 'ENCFF000VZW', 'ENCFF000WBT', 'ENCFF000WBX', 'ENCFF000WDE', 'ENCFF000WGX', 'ENCFF000WIZ', 'ENCFF000WJC', 'ENCFF000WKH', 'ENCFF000WKK', 'ENCFF000WKY', 'ENCFF000WLF', 'ENCFF000WLN', 'ENCFF000WOC', 'ENCFF000WOT', 'ENCFF000WPB', 'ENCFF000WTG', 'ENCFF000WTH', 'ENCFF000WUJ', 'ENCFF000XOT', 'ENCFF000XOU', 'ENCFF000XPA', 'ENCFF000XQR', 'ENCFF000XRH', 'ENCFF000XRT', 'ENCFF000XSE', 'ENCFF000XSK', 'ENCFF000XSM', 'ENCFF000XVC', 'ENCFF000XWR', 'ENCFF000XXK', 'ENCFF000XYS', 'ENCFF000XZJ', 'ENCFF000XZX', 'ENCFF000YCE', 'ENCFF000YCN', 'ENCFF000YDP', 'ENCFF000YDR', 'ENCFF000YDY', 'ENCFF000YEW', 'ENCFF000YFW', 'ENCFF000YHB', 'ENCFF000YHY', 'ENCFF000YIA', 'ENCFF000YJL', 'ENCFF000YLD', 'ENCFF000YLP', 'ENCFF000YMS', 'ENCFF000YMW', 'ENCFF000YND', 'ENCFF000YNF', 'ENCFF000YNM', 'ENCFF000YNX', 'ENCFF000YNZ', 'ENCFF000YPB', 'ENCFF000YPG', 'ENCFF000YPH', 'ENCFF000YPI', 'ENCFF000YPN', 'ENCFF000YPP', 'ENCFF000YPW', 'ENCFF000YQC', 'ENCFF000YQK', 'ENCFF000YRC', 'ENCFF000YRQ', 'ENCFF000YSC', 'ENCFF000YSR', 'ENCFF000YSS', 'ENCFF000YTU', 'ENCFF000YUJ', 'ENCFF000YVV', 'ENCFF000YWU', 'ENCFF000YXT', 'ENCFF000YYD', 'ENCFF000YYF', 'ENCFF000ZAZ', 'ENCFF000ZBF', 'ENCFF000ZBJ', 'ENCFF000ZBR', 'ENCFF000ZBY', 'ENCFF000ZBZ', 'ENCFF000ZCL', 'ENCFF000ZDS', 'ENCFF000ZDU', 'ENCFF000ZES', 'ENCFF000ZET', 'ENCFF000ZFB', 'ENCFF000ZFX', 'ENCFF000ZGC', 'ENCFF000ZGI', 'ENCFF000ZHC', 'ENCFF000ZJZ', 'ENCFF001ACS', 'ENCFF001AST', 'ENCFF001ASU', 'ENCFF001ASW', 'ENCFF001ATB', 'ENCFF001ATE', 'ENCFF001ATF', 'ENCFF001AUI', 'ENCFF001AWR', 'ENCFF001AWX', 'ENCFF001AYI', 'ENCFF001AYN', 'ENCFF001AYU', 'ENCFF001AZE', 'ENCFF001BAB', 'ENCFF001BEU', 'ENCFF001BGX', 'ENCFF001BGY', 'ENCFF001BHF', 'ENCFF001BJJ', 'ENCFF001BJL', 'ENCFF001BJP', 'ENCFF001BKX', 'ENCFF001BME', 'ENCFF001BNC', 'ENCFF001BNK', 'ENCFF001BNL', 'ENCFF001BNP', 'ENCFF001BRI', 'ENCFF001BXI', 'ENCFF001CBZ', 'ENCFF001CCC', 'ENCFF001CCO', 'ENCFF001CCV', 'ENCFF001CDD', 'ENCFF001CDF', 'ENCFF001CDY', 'ENCFF001CFM', 'ENCFF001CHN', 'ENCFF001CIE', 'ENCFF001CIM', 'ENCFF001CJN', 'ENCFF001CJU', 'ENCFF001CJX', 'ENCFF001CKL', 'ENCFF001CLB', 'ENCFF001CNL', 'ENCFF001CNU', 'ENCFF001CPL', 'ENCFF001CQK', 'ENCFF001CRR', 'ENCFF001CSA', 'ENCFF001CSL', 'ENCFF001CSU', 'ENCFF001CTC', 'ENCFF001CXV', 'ENCFF001CYE', 'ENCFF001CYW', 'ENCFF001CZJ', 'ENCFF001DAW', 'ENCFF001DBS', 'ENCFF001DFN', 'ENCFF001DHW', 'ENCFF001DJL', 'ENCFF001DKJ', 'ENCFF001DLF', 'ENCFF001DLY', 'ENCFF001DMT', 'ENCFF001DMU', 'ENCFF001DNN', 'ENCFF001DNY', 'ENCFF001DQU', 'ENCFF001DRP', 'ENCFF001DSV', 'ENCFF001DTG', 'ENCFF001DVT', 'ENCFF001DVY', 'ENCFF001DWY', 'ENCFF001DXP', 'ENCFF001EAE', 'ENCFF001EAV', 'ENCFF001EEA', 'ENCFF001EEL', 'ENCFF001EEP', 'ENCFF001EES', 'ENCFF001EFQ', 'ENCFF001EHJ', 'ENCFF001EJV', 'ENCFF001GXV', 'ENCFF001GZJ', 'ENCFF001HCS', 'ENCFF001HDG', 'ENCFF001HEC', 'ENCFF001HEP', 'ENCFF001HEQ', 'ENCFF001HGJ', 'ENCFF001HHL', 'ENCFF001HJW', 'ENCFF001HMI', 'ENCFF001HPM', 'ENCFF001HWL', 'ENCFF001IEI', 'ENCFF001IPQ', 'ENCFF001IPT', 'ENCFF001JAF', 'ENCFF001JIE', 'ENCFF001JQB', 'ENCFF001JXN', 'ENCFF001KPE', 'ENCFF001KUF', 'ENCFF001KVI', 'ENCFF001KWF', 'ENCFF001LIB', 'ENCFF001LRT', 'ENCFF001LUA', 'ENCFF001MGT', 'ENCFF001MGV', 'ENCFF001MHA', 'ENCFF001MHN', 'ENCFF001MIK', 'ENCFF001MIN', 'ENCFF001MKA', 'ENCFF001MKH', 'ENCFF001MKP', 'ENCFF001MNL', 'ENCFF001MNV', 'ENCFF001MPX', 'ENCFF001MQJ', 'ENCFF001MSI', 'ENCFF001MTM', 'ENCFF001MUJ', 'ENCFF001MVC', 'ENCFF001MVJ', 'ENCFF001NEX', 'ENCFF001NGC', 'ENCFF001NHC', 'ENCFF001NHJ', 'ENCFF001NIQ', 'ENCFF001NKS', 'ENCFF001NLB', 'ENCFF001NLX', 'ENCFF001NLZ', 'ENCFF001NMK', 'ENCFF001NNM', 'ENCFF001ODB', 'ENCFF001ODK', 'ENCFF001ODM', 'ENCFF001OFE', 'ENCFF001OFI', 'ENCFF001OFS', 'ENCFF001OGN', 'ENCFF001OIB', 'ENCFF001OJB', 'ENCFF001OJD', 'ENCFF001OJH', 'ENCFF001OJJ', 'ENCFF001OJL', 'ENCFF001OKE', 'ENCFF001OMC', 'ENCFF001OMD', 'ENCFF001OML', 'ENCFF001OMM', 'ENCFF001OOS', 'ENCFF001ORA', 'ENCFF001ORB', 'ENCFF001ORQ', 'ENCFF001OTA', 'ENCFF001OTV', 'ENCFF001PDQ', 'ENCFF001PER', 'ENCFF001PEV', 'ENCFF001PGC', 'ENCFF001PHA', 'ENCFF001PKF', 'ENCFF001PLH', 'ENCFF001POZ', 'ENCFF001PRQ', 'ENCFF001PTC', 'ENCFF001PUU', 'ENCFF001QBW', 'ENCFF001RFB', 'ENCFF001RGK', 'ENCFF001RLU', 'ENCFF001RMA', 'ENCFF001RMC', 'ENCFF001RNE', 'ENCFF001RNF', 'ENCFF001ROD', 'ENCFF001ROE', 'ENCFF001ROG', 'ENCFF001ROO', 'ENCFF001ROT', 'ENCFF001RRR', 'ENCFF001RTE', 'ENCFF001RTM', 'ENCFF001RTY', 'ENCFF001RUR', 'ENCFF001RUY', 'ENCFF001RVG', 'ENCFF001YVZ', 'ENCFF001YYA', 'ENCFF001ZGF', 'ENCFF001ZGG', 'ENCFF001ZVP', 'ENCFF001ZVY', 'ENCFF001ZWB', 'ENCFF001ZWD', 'ENCFF001ZWH', 'ENCFF001ZXB', 'ENCFF001ZXJ', 'ENCFF001ZXL', 'ENCFF001ZXN', 'ENCFF001ZXR', 'ENCFF001ZYC', 'ENCFF001ZYG', 'ENCFF001ZYH', 'ENCFF001ZYI', 'ENCFF001ZYP', 'ENCFF001ZYV', 'ENCFF001ZZU', 'ENCFF002ACN', 'ENCFF002ACS', 'ENCFF002ADF', 'ENCFF002BZZ', 'ENCFF002CAA', 'ENCFF002CBD', 'ENCFF002CCK', 'ENCFF002CCN', 'ENCFF002CCY', 'ENCFF002DHG', 'ENCFF002DWA', 'ENCFF002DWC', 'ENCFF002DWN', 'ENCFF002DXB', 'ENCFF002DXV', 'ENCFF002DYI', 'ENCFF002ERN', 'ENCFF002FAG', 'ENCFF002FAH', 'ENCFF002FAJ', 'ENCFF007ZAU', 'ENCFF011UGF', 'ENCFF016LGS', 'ENCFF018IKH', 'ENCFF018MRL', 'ENCFF040KCF', 'ENCFF050XWR', 'ENCFF054NWZ', 'ENCFF056ZMD', 'ENCFF059GYT', 'ENCFF064CHP', 'ENCFF071OOV', 'ENCFF075TFB', 'ENCFF079DKF', 'ENCFF079FLG', 'ENCFF080WPI', 'ENCFF091CQF', 'ENCFF094IRP', 'ENCFF096WNB', 'ENCFF102HMP', 'ENCFF102YVT', 'ENCFF105BSP', 'ENCFF105TIY', 'ENCFF107XBZ', 'ENCFF112POR', 'ENCFF113ELN', 'ENCFF115MEG', 'ENCFF143JYN', 'ENCFF149MQE', 'ENCFF151FXF', 'ENCFF162PYI', 'ENCFF173DNO', 'ENCFF198TME', 'ENCFF208QHU', 'ENCFF209PWZ', 'ENCFF236CIA', 'ENCFF242RPJ', 'ENCFF247QAD', 'ENCFF259CJR', 'ENCFF265XQX', 'ENCFF288IKC', 'ENCFF292ZMS', 'ENCFF295LLM', 'ENCFF300WJR', 'ENCFF302JND', 'ENCFF308LTN', 'ENCFF331ENP', 'ENCFF337JEU', 'ENCFF344ZXG', 'ENCFF348JXC', 'ENCFF356PAF', 'ENCFF361GMK', 'ENCFF361HII', 'ENCFF367WHH', 'ENCFF373UMT', 'ENCFF382HGK', 'ENCFF386MBZ', 'ENCFF388GKR', 'ENCFF389VYH', 'ENCFF398YOJ', 'ENCFF406XWQ', 'ENCFF408JLR', 'ENCFF415TIV', 'ENCFF420KNO', 'ENCFF422FQW', 'ENCFF437AJW', 'ENCFF443LQI', 'ENCFF443NRH', 'ENCFF445JWU', 'ENCFF446XAC', 'ENCFF459YEL', 'ENCFF463GPU', 'ENCFF465XJV', 'ENCFF471BJR', 'ENCFF485LVZ', 'ENCFF487SCX', 'ENCFF493QGP', 'ENCFF503IOU', 'ENCFF509AMH', 'ENCFF518PVS', 'ENCFF520CLC', 'ENCFF523OKJ', 'ENCFF526GHY', 'ENCFF543WUZ', 'ENCFF546PCU', 'ENCFF569DYW', 'ENCFF583CMW', 'ENCFF589GWR', 'ENCFF589JML', 'ENCFF600UXK', 'ENCFF607ZPA', 'ENCFF613LNZ', 'ENCFF615BON', 'ENCFF628CFW', 'ENCFF631TIM', 'ENCFF652UKP', 'ENCFF658ZRQ', 'ENCFF668NJW', 'ENCFF681LXU', 'ENCFF687SJZ', 'ENCFF687VSJ', 'ENCFF694OXY', 'ENCFF695CHM', 'ENCFF700PZE', 'ENCFF714FLI', 'ENCFF717GVN', 'ENCFF719DBG', 'ENCFF740KMV', 'ENCFF746BQQ', 'ENCFF747TQH', 'ENCFF755LDG', 'ENCFF758CTS', 'ENCFF762JMA', 'ENCFF772DZT', 'ENCFF772WNW', 'ENCFF776KZD', 'ENCFF794ZJK', 'ENCFF803DQJ', 'ENCFF808OHA', 'ENCFF824GRS', 'ENCFF849DKX', 'ENCFF855AQH', 'ENCFF859DHA', 'ENCFF861CQU', 'ENCFF863TSF', 'ENCFF863XOZ', 'ENCFF875XQI', 'ENCFF876CTE', 'ENCFF881MKS', 'ENCFF888YNZ', 'ENCFF897LHW', 'ENCFF906GES', 'ENCFF912CJB', 'ENCFF915ONY', 'ENCFF924FUL', 'ENCFF929ADI', 'ENCFF933LBI', 'ENCFF947LNX', 'ENCFF954GWE', 'ENCFF960HBD', 'ENCFF963HXO', 'ENCFF964DUY', 'ENCFF967KEP', 'ENCFF967MQJ', 'ENCFF968OJG', 'ENCFF978XAG', 'ENCFF985IBV', 'ENCFF992WOH', 'ENCFF994AQR', 'ENCFF995DWU']

            try:
                if item['file_format'] == 'fastq' and item['accession'] not in checked_list:
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
