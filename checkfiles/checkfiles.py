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
import re
from urllib.parse import urljoin
import requests
import copy

EPILOG = __doc__

GZIP_TYPES = [
    "CEL",
    "bam",
    "bed",
    "bedpe",
    "csfasta",
    "csqual",
    "fasta",
    "fastq",
    "gff",
    "gtf",
    "tagAlign",
    "tar",
    "sam",
    "wig"
]


def is_path_gzipped(path):
    with open(path, 'rb') as f:
        magic_number = f.read(2)
    return magic_number == b'\x1f\x8b'


def update_content_error(errors, error_message):
    if 'content_error' not in errors:
        errors['content_error'] = error_message
    else:
        errors['content_error'] += ', ' + error_message


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
            update_content_error(errors, 'File metadata lacks assembly information')
        if 'genome_annotation' not in item:
            errors['genome_annotation'] = 'missing genome_annotation'
            update_content_error(errors, 'File metadata lacks genome annotation information')
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
        ('hic', None): None,
        ('gff', None): None,
        ('vcf', None): None,
        ('btr', None): None
    }

    validate_args = validate_map.get((item['file_format'], item.get('file_format_type')))
    if validate_args is None:
        return

    if chromInfo in validate_args and 'assembly' not in item:
        errors['assembly'] = 'missing assembly'
        update_content_error(errors, 'File metadata lacks assembly information')
        return

    result['validateFiles_args'] = ' '.join(validate_args)

    try:
        output = subprocess.check_output(
            ['validateFiles'] + validate_args + [path], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        errors['validateFiles'] = e.output.decode(errors='replace').rstrip('\n')
        update_content_error(errors, 'File failed file format specific ' +
                                     'validation (encValData) ' + errors['validateFiles'])
    else:
        result['validateFiles'] = output.decode(errors='replace').rstrip('\n')


def process_illumina_read_name_pattern(read_name,
                                       read_numbers_set,
                                       signatures_set,
                                       signatures_no_barcode_set,
                                       srr_flag):
    read_name_array = re.split(r'[:\s_]', read_name)
    flowcell = read_name_array[2]
    lane_number = read_name_array[3]
    if srr_flag:
        read_number = list(read_numbers_set)[0]
    else:
        read_number = read_name_array[-4]
        read_numbers_set.add(read_number)
    barcode_index = read_name_array[-1]
    signatures_set.add(
        flowcell + ':' + lane_number + ':' +
        read_number + ':' + barcode_index + ':')
    signatures_no_barcode_set.add(
        flowcell + ':' + lane_number + ':' +
        read_number + ':')


def process_special_read_name_pattern(read_name,
                                      words_array,
                                      signatures_set,
                                      signatures_no_barcode_set,
                                      read_numbers_set,
                                      srr_flag):
    if srr_flag:
        read_number = list(read_numbers_set)[0]
    else:
        read_number = 'not initialized'
        if len(words_array[0]) > 3 and \
           words_array[0][-2:] in ['/1', '/2']:
            read_number = words_array[0][-1]
            read_numbers_set.add(read_number)
    read_name_array = re.split(r'[:\s_]', read_name)
    flowcell = read_name_array[2]
    lane_number = read_name_array[3]
    barcode_index = read_name_array[-1]
    signatures_set.add(
        flowcell + ':' + lane_number + ':' +
        read_number + ':' + barcode_index + ':')
    signatures_no_barcode_set.add(
        flowcell + ':' + lane_number + ':' +
        read_number + ':')


def process_new_illumina_prefix(read_name,
                                signatures_set,
                                old_illumina_current_prefix,
                                read_numbers_set,
                                srr_flag):
    if srr_flag:
        read_number = list(read_numbers_set)[0]
    else:
        read_number = '1'
        read_numbers_set.add(read_number)
    read_name_array = re.split(r':', read_name)

    if len(read_name_array) > 3:
        flowcell = read_name_array[2]
        lane_number = read_name_array[3]

        prefix = flowcell + ':' + lane_number
        if prefix != old_illumina_current_prefix:
            old_illumina_current_prefix = prefix

            signatures_set.add(
                flowcell + ':' + lane_number + ':' +
                read_number + '::' + read_name)

    return old_illumina_current_prefix


def process_old_illumina_read_name_pattern(read_name,
                                           read_numbers_set,
                                           signatures_set,
                                           old_illumina_current_prefix,
                                           srr_flag):
    if srr_flag:
        read_number = list(read_numbers_set)[0]
    else:
        read_number = '1'
        if read_name[-2:] in ['/1', '/2']:
            read_numbers_set.add(read_name[-1])
            read_number = read_name[-1]
    arr = re.split(r':', read_name)
    if len(arr) > 1:
        prefix = arr[0] + ':' + arr[1]
        if prefix != old_illumina_current_prefix:
            old_illumina_current_prefix = prefix
            flowcell = arr[0][1:]
            if (flowcell.find('-') != -1 or
               flowcell.find('_') != -1):
                flowcell = 'TEMP'
            # at this point we assume the read name is following old illumina format template
            # however sometimes the read names are following some different template
            # in case the lane variable is different from number (i.e contains letters)
            # we will default it to 0, the information is not lost, since the whole read name is
            # at the end of the signature string
            lane_number = '0'
            if arr[1].isdigit():
                lane_number = arr[1]
            signatures_set.add(
                flowcell + ':' + lane_number + ':' +
                read_number + '::' + read_name)

    return old_illumina_current_prefix


def process_read_name_line(read_name_line,
                           read_name_prefix,
                           read_name_pattern,
                           special_read_name_pattern,
                           srr_read_name_pattern,
                           old_illumina_current_prefix,
                           read_numbers_set,
                           signatures_no_barcode_set,
                           signatures_set,
                           read_lengths_dictionary,
                           errors, srr_flag):
    read_name = read_name_line.strip()
    words_array = re.split(r'\s', read_name)
    if read_name_pattern.match(read_name) is None:
        if special_read_name_pattern.match(read_name) is not None:
            process_special_read_name_pattern(read_name,
                                              words_array,
                                              signatures_set,
                                              signatures_no_barcode_set,
                                              read_numbers_set,
                                              srr_flag)
        elif srr_read_name_pattern.match(read_name.split(' ')[0]) is not None:
            # in case the readname is following SRR format, read number will be
            # defined using SRR format specifications, and not by the illumina portion of the read name
            # srr_flag is used to distinguish between srr and "regular" readname formats
            srr_portion = read_name.split(' ')[0]
            if srr_portion.count('.') == 2:
                read_numbers_set.add(srr_portion[-1])
            else:
                read_numbers_set.add('1')
            illumina_portion = read_name.split(' ')[1]
            old_illumina_current_prefix = process_read_name_line('@'+illumina_portion,
                                                                 read_name_prefix,
                                                                 read_name_pattern,
                                                                 special_read_name_pattern,
                                                                 srr_read_name_pattern,
                                                                 old_illumina_current_prefix,
                                                                 read_numbers_set,
                                                                 signatures_no_barcode_set,
                                                                 signatures_set,
                                                                 read_lengths_dictionary,
                                                                 errors, True)
        else:
            # unrecognized read_name_format
            # current convention is to include WHOLE
            # readname at the end of the signature
            if len(words_array) == 1:
                if read_name_prefix.match(read_name) is not None:
                    # new illumina without second part
                    old_illumina_current_prefix = process_new_illumina_prefix(
                        read_name,
                        signatures_set,
                        old_illumina_current_prefix,
                        read_numbers_set,
                        srr_flag)

                elif len(read_name) > 3 and read_name.count(':') > 2:
                    # assuming old illumina format
                    old_illumina_current_prefix = process_old_illumina_read_name_pattern(
                        read_name,
                        read_numbers_set,
                        signatures_set,
                        old_illumina_current_prefix,
                        srr_flag)
                else:
                    errors['fastq_format_readname'] = read_name
                    # the only case to skip update content error - due to the changing
                    # nature of read names
            else:
                errors['fastq_format_readname'] = read_name
    # found a match to the regex of "almost" illumina read_name
    else:
        process_illumina_read_name_pattern(
            read_name,
            read_numbers_set,
            signatures_set,
            signatures_no_barcode_set,
            srr_flag)

    return old_illumina_current_prefix


def process_sequence_line(sequence_line, read_lengths_dictionary):
    length = len(sequence_line.strip())
    if length not in read_lengths_dictionary:
        read_lengths_dictionary[length] = 0
    read_lengths_dictionary[length] += 1


def process_fastq_file(job, fastq_data_stream, session, url):
    item = job['item']
    errors = job['errors']
    result = job['result']

    read_name_prefix = re.compile(
        '^(@[a-zA-Z\d]+[a-zA-Z\d_-]*:[a-zA-Z\d-]+:[a-zA-Z\d_-]' +
        '+:\d+:\d+:\d+:\d+)$')

    read_name_pattern = re.compile(
        '^(@[a-zA-Z\d]+[a-zA-Z\d_-]*:[a-zA-Z\d-]+:[a-zA-Z\d_-]' +
        '+:\d+:\d+:\d+:\d+[\s_][12]:[YXN]:[0-9]+:([ACNTG\+]*|[0-9]*))$'
    )

    special_read_name_pattern = re.compile(
        '^(@[a-zA-Z\d]+[a-zA-Z\d_-]*:[a-zA-Z\d-]+:[a-zA-Z\d_-]' +
        '+:\d+:\d+:\d+:\d+[/1|/2]*[\s_][12]:[YXN]:[0-9]+:([ACNTG\+]*|[0-9]*))$'
    )

    srr_read_name_pattern = re.compile(
        '^(@SRR[\d.]+)$'
    )

    read_numbers_set = set()
    signatures_set = set()
    signatures_no_barcode_set = set()
    read_lengths_dictionary = {}
    read_count = 0
    old_illumina_current_prefix = 'empty'
    try:
        line_index = 0
        for encoded_line in fastq_data_stream.stdout:
            try:
                line = encoded_line.decode('utf-8')
            except UnicodeDecodeError:
                errors['readname_encoding'] = 'Error occured, while decoding the readname string.'
            else:
                line_index += 1
                if line_index == 1:
                    old_illumina_current_prefix = \
                        process_read_name_line(
                            line,
                            read_name_prefix,
                            read_name_pattern,
                            special_read_name_pattern,
                            srr_read_name_pattern,
                            old_illumina_current_prefix,
                            read_numbers_set,
                            signatures_no_barcode_set,
                            signatures_set,
                            read_lengths_dictionary,
                            errors, False)
            if line_index == 2:
                read_count += 1
                process_sequence_line(line, read_lengths_dictionary)

            line_index = line_index % 4
    except IOError:
        errors['unzipped_fastq_streaming'] = 'Error occured, while streaming unzipped fastq.'
    else:

        # read_count update
        result['read_count'] = read_count

        # read1/read2
        if len(read_numbers_set) > 1:
            errors['inconsistent_read_numbers'] = \
                'fastq file contains mixed read numbers ' + \
                '{}.'.format(', '.join(sorted(list(read_numbers_set))))
            update_content_error(errors,
                                 'Fastq file contains a mixture of read1 and read2 sequences')

        # read_length
        read_lengths_list = []
        for k in sorted(read_lengths_dictionary.keys()):
            read_lengths_list.append((k, read_lengths_dictionary[k]))

        if 'read_length' in item and item['read_length'] > 2:
            process_read_lengths(read_lengths_dictionary,
                                 read_lengths_list,
                                 item['read_length'],
                                 read_count,
                                 0.95,
                                 errors,
                                 result)
        else:
            errors['read_length'] = 'no specified read length in the uploaded fastq file, ' + \
                                    'while read length(s) found in the file were {}. '.format(
                                    ', '.join(map(str, read_lengths_list)))
            update_content_error(errors,
                                 'Fastq file metadata lacks read length information, ' +
                                 'but the file contains read length(s) {}'.format(
                                     ', '.join(map(str, read_lengths_list))))
        # signatures
        signatures_for_comparison = set()
        is_UMI = False
        if 'flowcell_details' in item and len(item['flowcell_details']) > 0:
            for entry in item['flowcell_details']:
                if 'barcode' in entry and entry['barcode'] == 'UMI':
                    is_UMI = True
                    break
        if old_illumina_current_prefix == 'empty' and is_UMI:
            for entry in signatures_no_barcode_set:
                signatures_for_comparison.add(entry + 'UMI:')
        else:
            if old_illumina_current_prefix == 'empty' and len(signatures_set) > 100:
                signatures_for_comparison = process_barcodes(signatures_set)
                if len(signatures_for_comparison) == 0:
                    for entry in signatures_no_barcode_set:
                        signatures_for_comparison.add(entry + 'mixed:')

            else:
                signatures_for_comparison = signatures_set

        result['fastq_signature'] = sorted(list(signatures_for_comparison))
        check_for_fastq_signature_conflicts(
            session,
            url,
            errors,
            item,
            signatures_for_comparison)


def process_barcodes(signatures_set):
    set_to_return = set()
    flowcells_dict = {}
    for entry in signatures_set:
        (f, l, r, b, rest) = entry.split(':')
        if (f, l, r) not in flowcells_dict:
            flowcells_dict[(f, l, r)] = {}
        if b not in flowcells_dict[(f, l, r)]:
            flowcells_dict[(f, l, r)][b] = 0
        flowcells_dict[(f, l, r)][b] += 1
    for key in flowcells_dict.keys():
        barcodes_dict = flowcells_dict[key]
        total = 0
        for b in barcodes_dict.keys():
            total += barcodes_dict[b]
        for b in barcodes_dict.keys():
            if ((float(total)/float(barcodes_dict[b])) < 100):
                set_to_return.add(key[0] + ':' +
                                  key[1] + ':' +
                                  key[2] + ':' +
                                  b + ':')
    return set_to_return


def process_read_lengths(read_lengths_dict,
                         lengths_list,
                         submitted_read_length,
                         read_count,
                         threshold_percentage,
                         errors_to_report,
                         result):
    reads_quantity = sum([count for length, count in read_lengths_dict.items()
                          if (submitted_read_length - 2) <= length <= (submitted_read_length + 2)])
    if ((threshold_percentage * read_count) > reads_quantity):
        errors_to_report['read_length'] = \
            'in file metadata the read_length is {}, '.format(submitted_read_length) + \
            'however the uploaded fastq file contains reads of following length(s) ' + \
            '{}. '.format(', '.join(map(str, lengths_list)))
        update_content_error(errors_to_report,
                             'Fastq file metadata specified read length was {}, '.format(
                                 submitted_read_length) +
                             'but the file contains read length(s) {}'.format(
                                 ', '.join(map(str, lengths_list))))


def create_a_list_of_barcodes(details):
    barcodes = set()
    for entry in details:
        barcode = entry.get('barcode')
        lane = entry.get('lane')
        if lane and barcode:
            barcodes.add((lane, barcode))
    return barcodes


def compare_flowcell_details(flowcell_details_1, flowcell_details_2):
    barcodes_1 = create_a_list_of_barcodes(flowcell_details_1)
    barcodes_2 = create_a_list_of_barcodes(flowcell_details_1)
    if barcodes_1 & barcodes_2:
        # intersection found
        return True
    # no intersection
    return False


def check_for_fastq_signature_conflicts(session,
                                        url,
                                        errors,
                                        item,
                                        signatures_to_check):
    conflicts = []
    for signature in sorted(list(signatures_to_check)):
        if not signature.endswith('mixed:'):
            query = '/search/?type=File&status!=replaced&file_format=fastq&' + \
                    'datastore=database&fastq_signature=' + signature
            try:
                r = session.get(urljoin(url, query))
            except requests.exceptions.RequestException as e:
                errors['lookup_for_fastq_signature'] = 'Network error occured, while looking for ' + \
                                                       'fastq signature conflict on the portal. ' + \
                                                       str(e)
            else:
                r_graph = r.json().get('@graph')
                # found a conflict
                if len(r_graph) > 0:
                    #  the conflict in case of missing barcode in read names could be resolved with metadata flowcell details
                    for entry in r_graph:
                        if (not signature.endswith('::') or
                            (signature.endswith('::') and entry.get('flowcell_details') and
                             item.get('flowcell_details') and
                             compare_flowcell_details(entry.get('flowcell_details'),
                                                      item.get('flowcell_details')))):
                                if 'accession' in entry and 'accession' in item and \
                                   entry['accession'] != item['accession']:
                                        conflicts.append(
                                            '%s in file %s ' % (
                                                signature,
                                                entry['accession']))
                                elif 'accession' in entry and 'accession' not in item:
                                    conflicts.append(
                                        '%s in file %s ' % (
                                            signature,
                                            entry['accession']))
                                elif 'accession' not in entry and 'accession' not in item:
                                    conflicts.append(
                                        '%s ' % (
                                            signature) +
                                        'file on the portal.')

    # "Fastq file contains read name signatures that conflict with signatures from file X”]
    if len(conflicts) > 0:
        errors['not_unique_flowcell_details'] = 'Fastq file contains read name signature ' + \
                                                'that conflict with signature of existing ' + \
                                                'file(s): {}'.format(
                                                ', '.join(map(str, conflicts)))
        update_content_error(errors, 'Fastq file contains read name signature ' +
                                     'that conflict with signature of existing ' +
                                     'file(s): {}'.format(
                                         ', '.join(map(str, conflicts))))
        return False
    return True


def check_for_contentmd5sum_conflicts(item, result, output, errors, session, url):
    result['content_md5sum'] = output[:32].decode(errors='replace')
    try:
        int(result['content_md5sum'], 16)
    except ValueError:
        errors['content_md5sum'] = output.decode(errors='replace').rstrip('\n')
        update_content_error(errors, 'File content md5sum format error')
    else:
        query = '/search/?type=File&status!=replaced&datastore=database&content_md5sum=' + result[
            'content_md5sum']
        try:
            r = session.get(urljoin(url, query))
        except requests.exceptions.RequestException as e:
            errors['lookup_for_content_md5sum'] = 'Network error occured, while looking for ' + \
                                                  'content md5sum conflict on the portal. ' + str(e)
        else:
            try:
                r_graph = r.json().get('@graph')
            except ValueError:
                errors['content_md5sum_lookup_json_error'] = str(r)
            else:
                if len(r_graph) > 0:
                    conflicts = []
                    for entry in r_graph:
                        if 'accession' in entry and 'accession' in item:
                            if entry['accession'] != item['accession']:
                                conflicts.append(
                                    '%s in file %s ' % (
                                        result['content_md5sum'],
                                        entry['accession']))
                        elif 'accession' in entry:
                            conflicts.append(
                                '%s in file %s ' % (
                                    result['content_md5sum'],
                                    entry['accession']))
                        elif 'accession' not in entry and 'accession' not in item:
                            conflicts.append(
                                '%s ' % (
                                    result['content_md5sum']))
                    if len(conflicts) > 0:
                        errors['content_md5sum'] = str(conflicts)
                        update_content_error(errors,
                                             'File content md5sum conflicts with content ' +
                                             'md5sum of existing file(s) {}'.format(
                                                 ', '.join(map(str, conflicts))))


def check_file(config, session, url, job):
    item = job['item']
    errors = job['errors']
    result = job['result'] = {}

    if job.get('skip'):
        return job

    no_file_flag = item.get('no_file_available')
    if no_file_flag:
        return job

    upload_url = job['upload_url']
    local_path = os.path.join(config['mirror'], upload_url[len('s3://'):])
    # boolean standing for local .bed file creation
    is_local_bed_present = False
    if item['file_format'] == 'bed':
        # local_path[-18:-7] retreives the file accession from the path
        unzipped_modified_bed_path = local_path[-18:-7] + '_modified.bed'
    try:
        file_stat = os.stat(local_path)
    except FileNotFoundError:
        errors['file_not_found'] = 'File has not been uploaded yet.'
        if job['run'] < job['upload_expiration']:
            job['skip'] = True
        return job

    result["file_size"] = file_stat.st_size
    result["last_modified"] = datetime.datetime.utcfromtimestamp(
        file_stat.st_mtime).isoformat() + 'Z'

    # Faster than doing it in Python.
    try:
        output = subprocess.check_output(
            ['md5sum', local_path], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        errors['md5sum'] = e.output.decode(errors='replace').rstrip('\n')
    else:
        result['md5sum'] = output[:32].decode(errors='replace')
        try:
            int(result['md5sum'], 16)
        except ValueError:
            errors['md5sum'] = output.decode(errors='replace').rstrip('\n')
        if result['md5sum'] != item['md5sum']:
            errors['md5sum'] = \
                'checked %s does not match item %s' % (result['md5sum'], item['md5sum'])
            update_content_error(errors,
                                 'File metadata-specified md5sum {} '.format(item['md5sum']) +
                                 'does not match the calculated md5sum {}'.format(result['md5sum']))
    is_gzipped = is_path_gzipped(local_path)
    if item['file_format'] not in GZIP_TYPES:
        if is_gzipped:
            errors['gzip'] = 'Expected un-gzipped file'
            update_content_error(errors, 'Expected un-gzipped file')
    elif not is_gzipped:
        errors['gzip'] = 'Expected gzipped file'
        update_content_error(errors, 'Expected gzipped file')
    else:
        # May want to replace this with something like:
        # $ cat $local_path | tee >(md5sum >&2) | gunzip | md5sum
        # or http://stackoverflow.com/a/15343686/199100
        try:
            output = subprocess.check_output(
                'set -o pipefail; gunzip --stdout %s | md5sum' % quote(local_path),
                shell=True, executable='/bin/bash', stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            errors['content_md5sum'] = e.output.decode(errors='replace').rstrip('\n')
        else:
            check_for_contentmd5sum_conflicts(item, result, output, errors, session, url)

        if item['file_format'] == 'bed':
            # try to count comment lines
            try:
                output = subprocess.check_output(
                    'set -o pipefail; gunzip --stdout {} | grep -c \'^#\''.format(local_path),
                    shell=True, executable='/bin/bash', stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                # empty file, or other type of error
                if e.returncode > 1:
                    errors['grep_bed_problem'] = e.output.decode(errors='replace').rstrip('\n')
            # comments lines found, need to calculate content md5sum as usual
            # remove the comments and create modified.bed to give validateFiles scritp
            # not forget to remove the modified.bed after finishing
            else:
                try:
                    is_local_bed_present = True
                    subprocess.check_output(
                        'set -o pipefail; gunzip --stdout {} | grep -v \'^#\' > {}'.format(
                            local_path,
                            unzipped_modified_bed_path),
                        shell=True, executable='/bin/bash', stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as e:
                    # empty file
                    if e.returncode > 1:
                        errors['grep_bed_problem'] = e.output.decode(errors='replace').rstrip('\n')
                    else:
                        errors['bed_comments_remove_failure'] = e.output.decode(
                            errors='replace').rstrip('\n')

    if is_local_bed_present:
        check_format(config['encValData'], job, unzipped_modified_bed_path)
        remove_local_file(unzipped_modified_bed_path, errors)
    else:
        check_format(config['encValData'], job, local_path)

    if item['file_format'] == 'fastq':
        try:
            process_fastq_file(job,
                               subprocess.Popen(['gunzip --stdout {}'.format(
                                                local_path)],
                                                shell=True,
                                                executable='/bin/bash',
                                                stdout=subprocess.PIPE),
                               session, url)
        except subprocess.CalledProcessError as e:
            errors['fastq_information_extraction'] = 'Failed to extract information from ' + \
                                                     local_path
    if item['status'] != 'uploading':
        errors['status_check'] = \
            "status '{}' is not 'uploading'".format(item['status'])
    if errors:
        errors['gathered information'] = 'Gathered information about the file was: {}.'.format(
            str(result))

    return job


def remove_local_file(path_to_the_file, errors):
    try:
        path_to_the_file = path_to_the_file
        if os.path.exists(path_to_the_file):
            try:
                os.remove(path_to_the_file)
            except OSError:
                errors['file_remove_error'] = 'OS could not remove the file ' + \
                                              path_to_the_file
    except NameError:
        pass


def fetch_files(session, url, search_query, out, include_unexpired_upload=False, file_list=None):
    graph = []
    # checkfiles using a file with a list of file accessions to be checked
    if file_list:
        r = None
        ACCESSIONS = []
        if os.path.isfile(file_list):
            ACCESSIONS = [line.rstrip('\n') for line in open(file_list)]
        for acc in ACCESSIONS:
            r = session.get(
                urljoin(url, '/search/?field=@id&limit=all&type=File&accession=' + acc))
            r.raise_for_status()
            local = copy.deepcopy(r.json()['@graph'])
            graph.extend(local)
    # checkfiles using a query
    else:
        r = session.get(
            urljoin(url, '/search/?field=@id&limit=all&type=File&' + search_query))
        r.raise_for_status()
        graph = r.json()['@graph']

    for result in graph:
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
            # Probably a transient error
            job['skip'] = True

        yield job


def patch_file(session, url, job):
    result = job['result']
    errors = job['errors']
    data = None

    if not errors:
        data = {
            'status': 'in progress',

        }
    else:
        if 'fastq_format_readname' in errors:
            update_content_error(errors,
                                 'Fastq file contains read names that don’t follow ' +
                                 'the Illumina standard naming schema; for example {}'.format(
                                     errors['fastq_format_readname']))
        if 'content_error' in errors:
            data = {
                'status': 'content error',
                'content_error_detail': errors['content_error'].strip()
                }
        if 'file_not_found' in errors:
            data = {
                'status': 'upload failed'
                }
    if 'file_size' in result:
        data['file_size'] = result['file_size']
    if 'read_count' in result:
        data['read_count'] = result['read_count']
    if result.get('fastq_signature'):
        data['fastq_signature'] = result['fastq_signature']
    if 'content_md5sum' in result:
        data['content_md5sum'] = result['content_md5sum']

    if data:
        item_url = urljoin(url, job['@id'])

        etag_r = session.get(item_url + '?frame=edit&datastore=database')
        if etag_r.ok:
            if job['etag'] == etag_r.headers['etag']:
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
            else:
                errors['etag_does_not_match'] = 'Original etag was {}, but the current etag is {}.'.format(
                    job['etag'], etag_r.headers['etag']) + ' File {} '.format(job['item'].get('accession', 'UNKNOWN')) + \
                    'was {} and now is {}.'.format(job['item'].get('status', 'UNKNOWN'), etag_r.json()['status'])
    return

def run(out, err, url, username, password, encValData, mirror, search_query, file_list=None,
        processes=None, include_unexpired_upload=False, dry_run=False, json_out=False):
    import functools
    import multiprocessing

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

    version = '1.13'

    out.write("STARTING Checkfiles version %s (%s): with %d processes %s at %s\n" %
              (version, search_query, nprocesses, dr, datetime.datetime.now()))
    if processes == 0:
        # Easier debugging without multiprocessing.
        imap = map
    else:
        pool = multiprocessing.Pool(processes=processes)
        imap = pool.imap_unordered

    jobs = fetch_files(session, url, search_query, out, include_unexpired_upload, file_list)
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
    parser.add_argument(
        '--file-list', default='',
        help="list of file accessions to check")
    parser.add_argument('url', help="server to post to")
    args = parser.parse_args()
    run(**vars(args))


if __name__ == '__main__':
    main()
