#!/usr/bin/env python
# -*- coding: latin-1 -*-
import requests, subprocess, shlex, urlparse, os, sys

AUTHID='user'; AUTHPW='secret'; HEADERS = {'content-type': 'application/json'}; SERVER = 'https://www.encodeproject.org/'
S3_SERVER='s3://encode-files/'

#get all the file objects
files = requests.get(
    'https://www.encodeproject.org/search/?type=file&frame=embedded&limit=all',
    auth=(AUTHID,AUTHPW), headers=HEADERS).json()['@graph']

#select your file
f_obj = files[123]

#make the URL that will get redirected - get it from the file object's href property
encode_url = urlparse.urljoin(SERVER,f_obj.get('href'))

#stream=True avoids actually downloading the file, but it evaluates the redirection
r = requests.get(encode_url, auth=(AUTHID,AUTHPW), headers=HEADERS, allow_redirects=True, stream=True)
try:
    r.raise_for_status
except:
    print '%s href does not resolve' %(f_obj.get('accession'))
    sys.exit()

#this is the actual S3 https URL after redirection
s3_url = r.url

#release the connection
r.close()

#split up the url into components
o = urlparse.urlparse(s3_url)

#pull out the filename
filename = os.path.basename(o.path)

#hack together the s3 cp url (with the s3 method instead of https)
bucket_url = S3_SERVER.rstrip('/') + o.path
#print bucket_url

#ls the file from the bucket
s3ls_string = subprocess.check_output(shlex.split('aws s3 ls %s' %(bucket_url)))
if s3ls_string.rstrip() == "":
    print >> sys.stderr, "%s not in bucket" %(bucket_url)
else:
    print "%s %s" %(f_obj.get('accession'), s3ls_string.rstrip())

#do the actual s3 cp
#return_value = subprocess.check_call(shlex.split('aws s3 cp %s %s' %(bucket_url, filename)))
