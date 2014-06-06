import hashlib
import json
import os.path
import requests
import subprocess
import time
from pprint import pprint

host = 'http://localhost:6543'
encoded_access_key = '...'
encoded_secret_access_key = '...'
path = 'example.fastq.gz'
path = path
size = os.path.getsize(path)

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
headers = {
    'Content-type': 'application/json',
    'Accept': 'application/json',
}

print("Submitting data.")
r = requests.post(
    host + '/file',
    auth=(encoded_access_key, encoded_secret_access_key),
    data=json.dumps(data),
    headers=headers,
)

item = r.json()['@graph'][0]
pprint(item)
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
print("Uploaded in %f seconds" % duration)
