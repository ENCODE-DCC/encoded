"""\
Move files from "uploading" to "in progress".

Example:

    %(prog)s --username ACCESS_KEY_ID --password SECRET_ACCESS_KEY \\
        --input check_files.log https://www.encodeproject.org
"""

import json
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


def run(fp, url, username, password):
    for line in fp.readlines():
        item, result, errors = json.loads(line)
        if errors:
            print('skipped %s: %s' % (item['accession'], errors))
            continue
        item_url = urljoin(url, item['@id'])
        r = requests.get(
            item_url + '?frame=object&datastore=database',
            auth=(username, password),
            headers=HEADERS,
        )
        if r.status_code != 200:
            print('ERROR retrieving %s: %s %s' % (item['@id'], r.status_code, r.reason))
            print(r.text)
            continue
        if r.json()['status'] != 'uploading':
            print('skipped %s: status %r is not "uploading"' % (item['@id'], r.json()['status']))
            continue
        r = requests.patch(
            item_url,
            data=json.dumps({
                'status': 'in progress',
                'file_size': result['file_size'],
            }),
            auth=(username, password),
            headers=HEADERS,
        )
        if r.status_code != 200:
            print('ERROR patching %s: %s %s' % (item['@id'], r.status_code, r.reason))
            print(r.text)
            continue
        print('patched %s' % item['@id'])


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Update file status", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--username', '-u', default='', help="HTTP username (access_key_id)")
    parser.add_argument('--password', '-p', default='', help="HTTP password (secret_access_key)")
    parser.add_argument(
        '--input', '-i', type=argparse.FileType('r'), default=sys.stdin, help="Input file.")
    parser.add_argument('url', help="server to post to")
    args = parser.parse_args()
    run(args.input, args.url, args.username, args.password)


if __name__ == '__main__':
    main()
