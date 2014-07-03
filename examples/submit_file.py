import hashlib
import json
import requests
import subprocess
import time

host = 'http://localhost:6543'
encoded_access_key = '...'
encoded_secret_access_key = '...'
path = 'example.fastq.gz'

# ~2s/GB
print("Calculating md5sum.")
md5sum = hashlib.md5()
with open(path, 'rb') as f:
    for chunk in iter(lambda: f.read(1024*1024), ''):
        md5sum.update(chunk)

data = {
    "dataset": "ENCSR000ACY",
    "file_format": "fastq",
    "md5sum": md5sum.hexdigest(),
    "output_type": "rawData",
    "submitted_file_name": path,
}

gzip_types = [
    "CEL",
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
if data['file_format'] in gzip_types:
    assert is_gzipped, 'Expected gzipped file'
else:
    assert not is_gzipped, 'Expected un-gzipped file'

validate_map = {
    'fastq': 'fastq',
    'fasta': 'fasta',
}

if data['file_format'] in validate_map:
    print("Validating file.")
    subprocess.check_call([
        'validateFiles',
        '-type=%s' % validate_map[data['file_format']],
        path,
    ])

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
r.raise_for_status()
item = r.json()['@graph'][0]
print(json.dumps(item, indent=4, sort_keys=True))
creds = item['upload_credentials']
env = {
    'AWS_ACCESS_KEY_ID': creds['access_key'],
    'AWS_SECRET_ACCESS_KEY': creds['secret_key'],
    'AWS_SECURITY_TOKEN': creds['session_token'],
}

# ~10s/GB from Stanford - AWS Oregon
print("Uploading file.")
start = time.time()
subprocess.check_call(['bin/aws', 's3', 'cp', path, creds['upload_url']], env=env)
end = time.time()
duration = end - start
print("Uploaded in %.2f seconds" % duration)
