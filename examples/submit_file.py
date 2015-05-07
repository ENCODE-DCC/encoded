""" Example file submission script

Requires the `aws` command line utility: http://aws.amazon.com/cli/
"""
import hashlib
import json
import os
import requests
import subprocess
import sys
import time

host = 'http://localhost:6543'
encoded_access_key = '...'
encoded_secret_access_key = '...'

path = 'example.fastq.gz'
my_lab = '/labs/your-lab-here'
my_award = '/awards/your-award-here'

# From http://hgwdev.cse.ucsc.edu/~galt/encode3/validatePackage/validateEncode3-latest.tgz
encValData = 'encValData'
assembly = 'hg19'

# ~2s/GB
print("Calculating md5sum.")
md5sum = hashlib.md5()
with open(path, 'rb') as f:
    for chunk in iter(lambda: f.read(1024*1024), b''):
        md5sum.update(chunk)

data = {
    "dataset": "ENCSR000ACY",
    "file_format": "fastq",
    "file_format_type": None,
    "file_size": os.path.getsize(path),
    "md5sum": md5sum.hexdigest(),
    "output_type": "reads",
    "read_length": "101",
    "run_type": "single-ended",
    "platform": "ENCODE:HiSeq2000",
    "submitted_file_name": path,
    "lab": my_lab,
    "award": my_award
}


####################
# Local validation

gzip_types = [
    "CEL",
    "bam",
    "bed",
    "csfasta",
    "csqual",
    "fasta",
    "fastq",
    "gff",
    "gtf",
    "tar",
    "sam",
    "wig"
]

magic_number = open(path, 'rb').read(2)
is_gzipped = magic_number == b'\x1f\x8b'
if data['file_format'] in gzip_types:
    assert is_gzipped, 'Expected gzipped file'
else:
    assert not is_gzipped, 'Expected un-gzipped file'

chromInfo = '-chromInfo=%s/%s/chrom.sizes' % (encValData, assembly)
validate_map = {
    ('bam', None): ['-type=bam', chromInfo],
    ('bed', 'unknown'): ['-type=bed6+', chromInfo],  # if this fails we will drop to bed3+
    ('bigBed', 'bedLogR'): ['-type=bigBed9+1', chromInfo, '-as=%s/as/bedLogR.as' % encValData],
    ('bed', 'bedLogR'): ['-type=bed9+1', chromInfo, '-as=%s/as/bedLogR.as' % encValData],
    ('bigBed', 'bedMethyl'): ['-type=bigBed9+2', chromInfo, '-as=%s/as/bedMethyl.as' % encValData],
    ('bed', 'bedMethyl'): ['-type=bed9+2', chromInfo, '-as=%s/as/bedMethyl.as' % encValData],
    ('bigBed', 'unknown'): ['-type=bigBed6+', chromInfo],  # if this fails we will drop to bigBed3+
    ('bigWig', None): ['-type=bigWig', chromInfo],
    ('bigBed', 'broadPeak'): ['-type=bigBed6+3', chromInfo, '-as=%s/as/broadPeak.as' % encValData],
    ('bed', 'broadPeak'): ['-type=bed6+3', chromInfo, '-as=%s/as/broadPeak.as' % encValData],
    ('fasta', None): ['-type=fasta'],
    ('fastq', None): ['-type=fastq'],
    ('bigBed', 'gappedPeak'): ['-type=bigBed12+3', chromInfo, '-as=%s/as/gappedPeak.as' % encValData],
    ('bed', 'gappedPeak'): ['-type=bed12+3', chromInfo, '-as=%s/as/gappedPeak.as' % encValData],
    ('gtf', None): None,
    ('idat', None): ['-type=idat'],
    ('bigBed', 'narrowPeak'): ['-type=bigBed6+4', chromInfo, '-as=%s/as/narrowPeak.as' % encValData],
    ('bed', 'narrowPeak'): ['-type=bed6+4', chromInfo, '-as=%s/as/narrowPeak.as' % encValData],
    ('rcc', None): ['-type=rcc'],
    ('tar', None): None,
    ('tsv', None): None,
    ('csv', None): None,
    ('2bit', None): None,
    ('csfasta', None): ['-type=csfasta'],
    ('csqual', None): ['-type=csqual'],
    ('bigBed', 'bedRnaElements'): ['-type=bed6+3', chromInfo, '-as=%s/as/bedRnaElements.as' % encValData],
    ('CEL', None): None,
    ('sam', None): None,
    ('wig', None): None,
    ('hdf5', None): None,
    ('gff', None): None
}

validate_args = validate_map.get((data['file_format'], data['file_format_type']))
if validate_args is not None:
    print("Validating file.")
    try:
        subprocess.check_output(['validateFiles'] + validate_args + [path])
    except subprocess.CalledProcessError as e:
        print(e.output)
        raise


####################
# POST metadata

headers = {
    'Content-type': 'application/json',
    'Accept': 'application/json',
}

print("Submitting metadata.")
r = requests.post(
    host + '/file',
    auth=(encoded_access_key, encoded_secret_access_key),
    data=json.dumps(data),
    headers=headers,
)
try:
    r.raise_for_status()
except:
    print('Submission failed: %s %s' % (r.status_code, r.reason))
    print(r.text)
    raise
item = r.json()['@graph'][0]
print(json.dumps(item, indent=4, sort_keys=True))


####################
# POST file to S3

creds = item['upload_credentials']
env = os.environ.copy()
env.update({
    'AWS_ACCESS_KEY_ID': creds['access_key'],
    'AWS_SECRET_ACCESS_KEY': creds['secret_key'],
    'AWS_SECURITY_TOKEN': creds['session_token'],
})

# ~10s/GB from Stanford - AWS Oregon
# ~12-15s/GB from AWS Ireland - AWS Oregon
print("Uploading file.")
start = time.time()
try:
    subprocess.check_call(['aws', 's3', 'cp', path, creds['upload_url']], env=env)
except subprocess.CalledProcessError as e:
    # The aws command returns a non-zero exit code on error.
    print("Upload failed with exit code %d" % e.returncode)
    sys.exit(e.returncode)
else:
    end = time.time()
    duration = end - start
    print("Uploaded in %.2f seconds" % duration)
