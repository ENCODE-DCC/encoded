import requests
import json

METADATA_URL = 'http://submit.encodedcc.org'
FILES_URL = 'https://submit.encodedcc.org/edwWebSubmit'
headers = {'content-type': 'application/json'}  # may not be necessary

# you have to get these from the DCC after loggin in
# with your email address
key_pair = {
    "user": "script_user",
    "pw": "script_password"
}

# note: only admins can change user info for someone other than themselves!


'''
you could get this from the server with:

user_json = requests.get(key_pair['user']+':'+key_pair['pw']+
    '@'+METADATA_URL+'users/cherry@stanford.edu/').json()
user = json.loads(user_json)

Or you could pull data from your LIMS or google doc,
map it to the correct python object(s) (see schemas).

The colleague schema can be found at:
https://github.com/ENCODE-DCC/encoded/blob/newschemas/src/encoded/schemas/colleague.json
'''
colleague = {
    "_links": {
        "profile": {
            "href": "/profiles/user.json"
        },
        "labs": [
            {
                "href": "/labs/cfb789b8-46f3-4d59-a2b3-adc39e7df93a"
            }
        ],
        "self": {
            "href": "/users/860c4750-8d3c-40f5-8f2c-90c5e5d19e88"
        },
        "collection": {
            "href": "/users/"
        }
    },
    "fax": "650-725-1534",
    "last_name": "Cherry",
    "phone2": "Unknown",
    "google_chat": "Unknown",
    "phone1": "650-723-7541",
    "first_name": "Michael",
    "skype": "Unknown",
    "timezone": "UTC-8",
    "email": "cherry@stanford.edu",
    "job_title": "PI"
}

# The _links (or other fields beginning with _ are for internal fields
# If you submit them they will be ignored (at best)

for k in list(colleague.keys()):
    if k.startswith('_'):
        del colleague[k]


# change the name
colleague["first_name"] = 'J. Michael'
colleague_json = json.dumps(colleague)

object_url = METADATA_URL + "/users/" + colleague['email']
## You can also use UUID instead of email

response = requests.post(object_url,
                         auth=(key_pair['user'], key_pair['pw']),
                         data=colleague_json,
                         headers=headers)

assert(response.status_code == 200)  # 201 for creation

## Now submit some files
manifest_url = "http://mysite.org/mylab/encode/validated.txt"

data = {
    "name": key_pair['user'],
    "password": key_pair['pw'],
    "url": manifest_url
}

response = requests.get(FILES_URL, params=data)
assert(response.status_code == 200)


