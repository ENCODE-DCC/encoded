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


def check_format(item, path):
    """ Local validation
    """
    try:
        import subprocess32 as subprocess  # Needed on Python 2.6
    except ImportError:
        import subprocess

    encValData = CONFIG['encValData']
    errors = {}
    gzip_types = [
        "CEL",
        "bam",
        "bed",
        "bed_bed3",
        "bed_bed6",
        "bed_bedLogR",
        "bed_bedMethyl",
        "bed_bedRnaElements",
        "bed_broadPeak",
        "bed_narrowPeak",
        "bed_peptideMapping",
        "csfasta",
        "csqual",
        "fasta",
        "fastq",
        "gff",
        "gtf",
        "tar",
    ]

    magic_number = open(path, 'rb').read(2)
    is_gzipped = magic_number == b'\x1f\x8b'
    if item['file_format'] in gzip_types:
        if not is_gzipped:
            errors['gzip'] = 'Expected gzipped file'
    else:
        if is_gzipped:
            errors['gzip'] = 'Expected un-gzipped file'

    if item['file_format'] == 'bam' and item.get('output_type','') == 'transcriptome alignments':
        chromInfo = ['-chromInfo=%s/%s/%s/chrom.sizes' % (encValData, item.get('assembly'), item['genome_annotation'])]
    else:
        chromInfo = '-chromInfo=%s/%s/chrom.sizes' % (encValData, item['assembly'])


    validate_map = {
        'bam': ['-type=bam', chromInfo],
        'bed': ['-type=bed6+', chromInfo],  # if this fails we will drop to bed3+
        'bedLogR': ['-type=bigBed9+1', chromInfo, '-as=%s/as/bedLogR.as' % encValData],
        'bed_bedLogR': ['-type=bed9+1', chromInfo, '-as=%s/as/bedLogR.as' % encValData],
        'bedMethyl': ['-type=bigBed9+2', chromInfo, '-as=%s/as/bedMethyl.as' % encValData],
        'bed_bedMethyl': ['-type=bed9+2', chromInfo, '-as=%s/as/bedMethyl.as' % encValData],
        'bigBed': ['-type=bigBed6+', chromInfo],  # if this fails we will drop to bigBed3+
        'bigWig': ['-type=bigWig', chromInfo],
        'broadPeak': ['-type=bigBed6+3', chromInfo, '-as=%s/as/broadPeak.as' % encValData],
        'bed_broadPeak': ['-type=bed6+3', chromInfo, '-as=%s/as/broadPeak.as' % encValData],
        'fasta': ['-type=fasta'],
        'fastq': ['-type=fastq'],
        'gtf': None,
        'idat': ['-type=idat'],
        'narrowPeak': ['-type=bigBed6+4', chromInfo, '-as=%s/as/narrowPeak.as' % encValData],
        'bed_narrowPeak': ['-type=bed6+4', chromInfo, '-as=%s/as/narrowPeak.as' % encValData],
        'rcc': ['-type=rcc'],
        'tar': None,
        'tsv': None,
        '2bit': None,
        'csfasta': ['-type=csfasta'],
        'csqual': ['-type=csqual'],
        'bedRnaElements': ['-type=bed6+3', chromInfo, '-as=%s/as/bedRnaElements.as' % encValData],
        'CEL': None,
    }

    validate_args = validate_map.get(item['file_format'])
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
    import hashlib
    import os.path
    try:
        from urllib.parse import urlparse
    except ImportError:
        from urlparse import urlparse

    result = None
    errors = {}
    r = requests.head(
        urljoin(CONFIG['url'], item['@id'] + '@@download'),
        auth=(CONFIG['username'], CONFIG['password']), headers=HEADERS)
    path = urlparse(r.headers['Location']).path[1:]

    key = BUCKET.get_key(path)
    if key is None:
        errors['key'] = 'not in s3'
        return item, result, errors

    if not os.path.exists(CONFIG['mirror'] + path):
        errors['sync'] = 'not synced'
        return item, result, errors

    if os.path.getsize(CONFIG['mirror'] + path) != key.size:
        errors['sync'] = 'sync size mismatch'
        return item, result, errors

    md5sum = hashlib.md5()
    with open(CONFIG['mirror'] + path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), ''):
            md5sum.update(chunk)

    if md5sum.hexdigest() != item['md5sum']:
        errors['md5sum'] = \
            'checked %s does not match item %s' % (md5sum.hexdigest(), item['md5sum'])

    if 'file_size' in item and key.size != item['file_size']:
        errors['file_size'] = \
            'uploaded %d does not match item %d' % (key.size, item['file_size'])

    result = {
        "accession": item['accession'],
        "path": path,
        "file_size": key.size,
        "md5sum": md5sum.hexdigest(),
    }

    if not errors:
        errors.update(check_format(item, CONFIG['mirror'] + path))

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
            sys.stderr.write(json.dumps([item['accession'], errors]) + '\n')


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
