import urllib, json
import os

oldurl = os.environ['URL_PREF']
url = oldurl + '/_indexer'
response = urllib.urlopen(url)
data = json.loads(response.read())

print data["status"]