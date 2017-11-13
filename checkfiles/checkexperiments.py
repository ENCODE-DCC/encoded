"""\
Run status check on experiments.

Example.

    %(prog)s --username ACCESS_KEY_ID --password SECRET_ACCESS_KEY \\
        --out experiments_statuses.log https://www.encodeproject.org
"""
import datetime
import json
import sys
import copy
import os.path
import subprocess
from urllib.parse import urljoin
import requests
from slackclient import SlackClient

EPILOG = __doc__

def run(out, err, url, username, password, search_query, accessions_list=None, bot_token=None, dry_run=False):
    session = requests.Session()
    session.auth = (username, password)
    session.headers['Accept'] = 'application/json'

    dr = ""
    if dry_run:
        dr = "-- Dry Run"

    version = '0.1'

    try:
        ip_output = subprocess.check_output(
            ['hostname'], stderr=subprocess.STDOUT).strip()
        ip = ip_output.decode(errors='replace').rstrip('\n')
    except subprocess.CalledProcessError as e:
        ip = ''

    initiating_run = 'STARTING Checkexperiments version ' + \
        '{} ({}) ({}): {} on {} at {}'.format(
            version, url, search_query, dr, ip, datetime.datetime.now())
    if bot_token:
        sc = SlackClient(bot_token)
        sc.api_call(
            "chat.postMessage",
            channel="#bot-reporting",
            text=initiating_run,
            as_user=True
        )

    # read_depth definitions:
    min_depth = {}
    min_depth['ChIP-seq'] = 20000000
    min_depth['RAMPAGE'] = 10000000
    min_depth['shRNA knockdown followed by RNA-seq'] = 10000000
    min_depth['siRNA knockdown followed by RNA-seq'] = 10000000
    min_depth['single cell isolation followed by RNA-seq'] = 10000000
    min_depth['CRISPR genome editing followed by RNA-seq'] = 10000000
    min_depth['modENCODE-chip'] = 500000

    graph = []
    # checkexperiments using a file with a list of experiment accessions to be checked
    if accessions_list:
        r = None
        ACCESSIONS = []
        if os.path.isfile(accessions_list):
            ACCESSIONS = [line.rstrip('\n') for line in open(accessions_list)]
        for acc in ACCESSIONS:
            r = session.get(
                urljoin(url, '/search/?field=@id&limit=all&type=Experiment&accession=' + acc))
            try:
                r.raise_for_status()
            except requests.HTTPError:
                return
            else:
                local = copy.deepcopy(r.json()['@graph'])
                graph.extend(local)
    # checkexperiments using a query
    else:
        r = session.get(
            urljoin(
                url,
                '/search/?type=Experiment&status=proposed' \
                '&status=started&format=json&limit=all' + search_query))
        try:
            r.raise_for_status()
        except requests.HTTPError:
            return
        else:
            graph = r.json()['@graph']
    for ex in graph:
        replicates = set()
        replicates_reads = {}
        files = []
        try:
            if ex.get('replicates') and ex.get('files'):
                award_request = session.get(urljoin(
                    url,
                    '/' + ex.get('award') + '?frame=object&format=json'))
                award_obj = award_request.json()
                for replicate in ex.get('replicates'):
                    replicate_request = session.get(urljoin(
                        url,
                        '/' + replicate + '?frame=object&format=json'))
                    replicate_obj = replicate_request.json()
                    if replicate_obj.get('status') not in ['deleted']:
                        replicates.add(replicate_obj['@id'])
                        replicates_reads[replicate_obj['@id']] = 0
                for file_acc in ex.get('files'):
                    file_request = session.get(urljoin(
                        url,
                        '/' + file_acc + '?frame=object&format=json'))
                    file_obj = file_request.json()
                    if file_obj.get('status') not in [
                            'uploading',
                            'content error',
                            'upload failed',
                        ]:
                        files.append(file_obj)
                        if file_obj.get('read_count') and file_obj.get('replicate'):
                            if not replicates_reads.get(file_obj.get('replicate')) is None:
                                replicates_reads[file_obj.get('replicate')] += \
                                    file_obj.get('read_count')
        except requests.exceptions.RequestException:
            continue
        else:
            submitted_replicates = set()
            for file_obj in files:
                if file_obj.get('replicate'):
                    submitted_replicates.add(file_obj.get('replicate'))
            if not replicates - submitted_replicates:
                # check read depth:
                depth_flag = False
                if award_obj.get('rfa') == 'modENCODE':
                    for rep in replicates_reads:
                        if replicates_reads[rep] < min_depth['modENCODE-chip']:
                            depth_flag = True
                            err.write(
                                award_obj.get('rfa') + '\t' + \
                                ex['accession']+'\t' + rep + \
                                '\treads_count=' + str(replicates_reads[rep]) + '\n')
                            err.flush()
                            break
                    if not depth_flag:
                        out.write(
                            award_obj.get('rfa') + \
                            '\t' +ex['accession']+'\t' + \
                            ex['status'] + '\t-> submitted\n')
                        out.flush()
                else:
                    if ex['assay_term_name'] in min_depth:
                        for rep in replicates_reads:
                            if replicates_reads[rep] < min_depth[ex['assay_term_name']]:
                                depth_flag = True
                                err.write(
                                    award_obj.get('rfa') + '\t' + \
                                    ex['accession']+'\t' + rep + \
                                    '\treads_count=' + \
                                    str(replicates_reads[rep]) + '\n')
                                err.flush()
                                break
                        if not depth_flag:
                            out.write(
                                award_obj.get('rfa') + '\t' + \
                                ex['accession']+'\t' + ex['status'] + \
                                '\t-> submitted\n')
                            out.flush()
                    else:
                        out.write(
                            award_obj.get('rfa') + '\t' + \
                            ex['accession']+'\t' + ex['status'] + \
                            '\t-> submitted\n')
                        out.flush()

    finishing_run = 'FINISHED Checkexperiments at {}'.format(datetime.datetime.now())
    out.write(finishing_run + '\n')
    out.flush()
    output_filename = out.name
    out.close()
    error_filename = err.name
    err.close()

    if bot_token:
        with open(output_filename, 'r') as output_file:
            sc.api_call("files.upload",
                        title=output_filename,
                        channels='#bot-reporting',
                        content=output_file.read(),
                        as_user=True)

        with open(error_filename, 'r') as output_file:
            sc.api_call("files.upload",
                        title=error_filename,
                        channels='#bot-reporting',
                        content=output_file.read(),
                        as_user=True)

        sc.api_call(
            "chat.postMessage",
            channel="#bot-reporting",
            text=finishing_run,
            as_user=True
        )

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Update experiments status", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '--username', '-u', default='', help="HTTP username (access_key_id)")
    parser.add_argument(
        '--bot-token', default='', help="Slack bot token")
    parser.add_argument(
        '--password', '-p', default='',
        help="HTTP password (secret_access_key)")
    parser.add_argument(
        '--out', '-o', type=argparse.FileType('w'), default=sys.stdout,
        help="file to write json lines of results with or without errors")
    parser.add_argument(
        '--err', '-e', type=argparse.FileType('w'), default=sys.stderr,
        help="file to write json lines of results with errors")
    parser.add_argument(
        '--dry-run', action='store_true', help="Don't update status, just check")
    parser.add_argument(
        '--json-out', action='store_true', help="Output results as JSON (legacy)")
    parser.add_argument(
        '--search-query', default='status=proposed&status=started',
        help="override the experiment search query, e.g. 'accession=ENCFF000ABC'")
    parser.add_argument(
        '--accessions-list', default='',
        help="list of experiment accessions to check")
    parser.add_argument('url', help="server to post to")
    args = parser.parse_args()
    run(**vars(args))


if __name__ == '__main__':
    main()
