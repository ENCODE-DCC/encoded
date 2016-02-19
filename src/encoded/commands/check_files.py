"""\
Run sanity checks on files.

Example.

    %(prog)s --username ACCESS_KEY_ID --password SECRET_ACCESS_KEY \\
        --output check_files.log https://www.encodeproject.org
"""
import boto
import requests
import sys
try:
    from shlex import quote
except ImportError:
    from pipes import quote
try:
    import subprocess32 as subprocess  # Needed on Python 2.6
except ImportError:
    import subprocess
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

EPILOG = __doc__

HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
}

BUCKET = None
CONFIG = None

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
    "wig"
]


def set_config(url, username, password, encValData, bucket, mirror):
    global CONFIG
    global BUCKET
    BUCKET = boto.connect_s3().get_bucket(bucket)
    CONFIG = {
        'url': url,
        'username': username,
        'password': password,
        'encValData': encValData,
        'mirror': mirror,
    }


def is_path_gzipped(path):
    with open(path, 'rb') as f:
        magic_number = f.read(2)
    return magic_number == b'\x1f\x8b'


def check_format(item, path):
    """ Local validation
    """
    encValData = CONFIG['encValData']
    errors = {}

    if item['file_format'] == 'bam' and item.get('output_type') == 'transcriptome alignments':
        if 'assembly' not in item:
            errors['assembly'] = 'missing assembly'
        if 'genome_annotation' not in item:
            errors['genome_annotation'] = 'missing genome_annotation'
        if errors:
            return errors
        chromInfo = '-chromInfo=%s/%s/%s/chrom.sizes' % (
            encValData, item['assembly'], item['genome_annotation'])
    else:
        chromInfo = '-chromInfo=%s/%s/chrom.sizes' % (encValData, item.get('assembly'))

    validate_map = {
        ('fasta', None): ['-type=fasta'],
        ('fastq', None): ['-type=fastq'],
        ('bam', None): ['-type=bam', chromInfo],
        ('bigWig', None): ['-type=bigWig', chromInfo],
        #standard bed formats
        ('bed', 'bed3'): ['-type=bed3', chromInfo],
        ('bigBed', 'bed3'): ['-type=bigBed3', chromInfo],
        ('bed', 'bed6'): ['-type=bed6', chromInfo],
        ('bigBed', 'bed6'): ['-type=bigBed6', chromInfo],
        ('bed', 'bed9'): ['-type=bed9', chromInfo],
        ('bigBed', 'bed9'): ['-type=bigBed9', chromInfo],
        ('bedGraph', None): ['-type=bedGraph', chromInfo],
        #extended "bed+" formats, -tab is required to allow for text fields to contain spaces
        ('bed', 'bed3+'): ['-tab', '-type=bed3+', chromInfo],
        ('bigBed', 'bed3+'): ['-tab', '-type=bigBed3+', chromInfo],
        ('bed', 'bed6+'): ['-tab', '-type=bed6+', chromInfo],
        ('bigBed', 'bed6+'): ['-tab', '-type=bigBed6+', chromInfo],
        ('bed', 'bed9+'): ['-tab', '-type=bed9+', chromInfo],
        ('bigBed', 'bed9+'): ['-tab', '-type=bigBed9+', chromInfo],
        #a catch-all shoe-horn (as long as it's tab-delimited)
        ('bed', 'unknown'): ['-tab', '-type=bed3+', chromInfo],
        ('bigBed', 'unknown'): ['-tab', '-type=bigBed3+', chromInfo],
        #special bed types
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
        #non-bed types
        ('rcc', None): ['-type=rcc'],
        ('idat', None): ['-type=idat'],
        ('gtf', None): None,
        ('tagAlign', None): ['-type=tagAlign'],
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
        ('vcf', None): None
    }

    validate_args = validate_map.get((item['file_format'], item.get('file_format_type')))
    if validate_args is None:
        return errors

    if chromInfo in validate_args and 'assembly' not in item:
        errors['assembly'] = 'missing assembly'
        return errors

    try:
        subprocess.check_output(['validateFiles'] + validate_args + [path])
    except subprocess.CalledProcessError as e:
        errors['validateFiles'] = e.output

    return errors


def check_file(item):
    import os.path
    try:
        from urllib.parse import urlparse
    except ImportError:
        from urlparse import urlparse

    result = None
    errors = {}
    r = requests.get(
        urljoin(CONFIG['url'], item['@id'] + '@@upload'),
        auth=(CONFIG['username'], CONFIG['password']), headers=HEADERS)
    upload_url = r.json()['@graph'][0]['upload_credentials']['upload_url']
    path = urlparse(upload_url).path[1:]
    local_path = CONFIG['mirror'] + path

    key = BUCKET.get_key(path)
    if key is None:
        errors['key'] = 'not in s3'
        return item, result, errors

    if not os.path.exists(local_path):
        errors['sync'] = 'not synced'
        return item, result, errors

    if os.path.getsize(local_path) != key.size:
        errors['sync'] = 'sync size mismatch'
        return item, result, errors

    if 'file_size' in item and key.size != item['file_size']:
        errors['file_size'] = \
            'uploaded %d does not match item %d' % (key.size, item['file_size'])

    result = {
        "@id": item['@id'],
        "path": path,
        "file_size": key.size,
    }

    # Faster than doing it in Python.
    try:
        output = subprocess.check_output(['md5sum', local_path])
    except subprocess.CalledProcessError as e:
        errors['md5sum'] = e.output
    else:
        result['md5sum'] = output[:32].decode('ascii')
        if result['md5sum'] != item['md5sum']:
            errors['md5sum'] = \
                'checked %s does not match item %s' % (result['md5sum'], item['md5sum'])

    is_gzipped = is_path_gzipped(local_path)
    if item['file_format'] not in GZIP_TYPES:
        if is_gzipped:
            errors['gzip'] = 'Expected un-gzipped file'
    elif not is_gzipped:
        errors['gzip'] = 'Expected gzipped file'
    else:
        # May want to replace this with something like:
        # $ cat $local_path | tee >(md5sum >&2) | gunzip | md5sum
        # or http://stackoverflow.com/a/15343686/199100
        try:
            output = subprocess.check_output(
                'set -o pipefail; gunzip --stdout  %s | md5sum' % quote(local_path), shell=True)
        except subprocess.CalledProcessError as e:
            errors['content_md5sum'] = e.output
        else:
            result['content_md5sum'] = output[:32].decode('ascii')
            try:
                int(result['content_md5sum'], 16)
            except ValueError:
                errors['content_md5sum'] = output

    if not errors:
        errors.update(check_format(item, local_path))

    return item, result, errors


def fetch_files(url, username, password):
    r = requests.get(
        urljoin(url, '/search/?type=file&status=uploading&frame=object&limit=all'),
        auth=(username, password), headers=HEADERS)
    r.raise_for_status()
    return r.json()['@graph']


def run(output, url, username, password, encValData, bucket, mirror):
    import json
    import multiprocessing
    pool = multiprocessing.Pool(
        processes=16,
        initializer=set_config,
        initargs=(url, username, password, encValData, bucket, mirror),
    )
    imap = pool.imap_unordered
    # from itertools import imap
    # set_config(url, username, password, encValData, bucket, mirror)

    files = fetch_files(url, username, password)
    for item, result, errors in imap(check_file, files):
        output.write(json.dumps([item, result, errors]) + '\n')
        if errors:
            sys.stderr.write(json.dumps([item['@id'], errors]) + '\n')


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Update file status", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--bucket', default='encode-files', help="S3 files bucket")
    parser.add_argument('--mirror', default='/external/encode/s3/encode-files/')
    # From http://hgwdev.cse.ucsc.edu/~galt/encode3/validatePackage/validateEncode3-latest.tgz
    parser.add_argument(
        '--encValData', default='/external/encode/encValData', help="encValData location")
    parser.add_argument('--username', '-u', default='', help="HTTP username (access_key_id)")
    parser.add_argument('--password', '-p', default='', help="HTTP password (secret_access_key)")
    parser.add_argument(
        '--output', '-o', type=argparse.FileType('w'), default=sys.stdout, help="Output file.")
    parser.add_argument('url', help="server to post to")
    args = parser.parse_args()
    run(args.output, args.url, args.username, args.password, args.encValData,
        args.bucket, args.mirror)


if __name__ == '__main__':
    main()
