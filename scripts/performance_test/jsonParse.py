import urllib, json
import os

url = os.environ['URL_PREF']
response = urllib.urlopen(url)
data = json.loads(response.read())

print data["status"]