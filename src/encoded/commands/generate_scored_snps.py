from pyramid.paster import get_app
import logging
import json
import time  # DEBUG: timing
from ..region_indexer import (
    REGULOME_SUPPORTED_ASSEMBLIES
)
from ..region_atlas import (
    CHROM_SIZES,
    RegulomeAtlas
)

from snovault.elasticsearch.interfaces import (
    SNP_SEARCH_ES
)
import subprocess
import os
import sys
import math
from multiprocessing.pool import Pool


EPILOG = __doc__

log = logging.getLogger(__name__)

app = None  # global for multiprocessing

MAX_PROCESSES = 32


def regularized_file_name(assembly, chrom, start, end, signal, format_json):
    '''Return regularized file name based upon parameters'''
    prefix = 'regulome_SNPs'
    suffix = 'bed'
    if signal:
        prefix = 'regulome_signal'
        suffix = 'bedGraph'
    if format_json:
        suffix = 'json'
    if start == 0 and end == -1:  # whole chrom default
        return '%s_%s_%s.%s' % (prefix, assembly, chrom, suffix)
    elif end == -1:  # to end
        return '%s_%s_%s_%d_end.%s' % (prefix, assembly, chrom, start, suffix)
    else:
        return '%s_%s_%s_%d_%d.%s' % (prefix, assembly, chrom, start, end, suffix)


def header(atlas, signal, format_json):
    if format_json:
        return '{ "positions": [\n'
    else:
        if signal:
            columns = ['#chrom', 'start', 'end', 'num_score']  # bedGraph
        else:
            columns = ['#chrom', 'start', 'end', 'rsid', 'num_score', 'score']  # bed 5 +
            columns.extend(atlas.evidence_categories())
        return '\t'.join(columns) + '\n'


def footer(took, count, format_json):
    if format_json:
        return '],\n"took": %s,\n"count": %d\n}\n' % (took, count)
    else:
        return '# took: %s, count: %d\n' % (took, count)


def run(app, assembly, chrom, start=0, end=-1, file_name='',
        signal=False, format_json=False, skip_header=False):
    '''Run on single process to write file for one chrom and range.'''
    atlas = RegulomeAtlas(app.registry[SNP_SEARCH_ES])

    if assembly not in REGULOME_SUPPORTED_ASSEMBLIES:
        log.error("Chosen assembly '%s' is not supported." % (assembly))
        return
    if chrom not in CHROM_SIZES.keys():
        log.error("Chosen chromosome '%s' is not supported." % (chrom))
        return
    chrom_size = CHROM_SIZES[chrom][assembly]
    if start > chrom_size:
        log.error("Chosen start of %d is beyond %s.%s size of %d " %
                (start, assembly, chrom, chrom_size))
        return
    if end > chrom_size:
        end = chrom_size if start > 0 else -1  # full chrom
    if end >= 0 and end <= start:
        log.error("Chosen range of %d to %d is invalid." % (start, end))
        return
    what = 'SNPs'
    if signal:
        what = 'regions of contiguous score'
    if file_name == '':
        file_name = regularized_file_name(assembly, chrom, start, end, signal, format_json)

    if not skip_header:
        log.info("Starting to generate %s" % (file_name))
    begin = time.time()  # DEBUG: timing
    with open(file_name, 'w') as file_obj:
        if not skip_header:
            file_obj.write(header(atlas, signal, format_json))
            log.info("Wrote header to %s" % (file_name))

        end = atlas.cap_at_chrom_size(assembly, chrom, end)
        count = 0

        if signal:
            log.info("Starting on signal for %s %s:%d-%d" % (assembly, chrom, start, end))
            for (pos_start, pos_end, pos_score) in atlas.iter_scored_signal(assembly,
                                                                            chrom, start, end):
                if format_json:
                    pos_json = {'chrom': chrom, 'start': pos_start, 'end': pos_end,
                                'num_score': pos_score}
                    formatted_pos = json.dumps(pos_json, sort_keys=True)[1:-1] + ','
                else:
                    formatted_pos = "%s\t%d\t%d\t%d" %  (chrom, pos_start - 1, pos_end, pos_score)
                    #                                         - 1 because bed format is 'half open'
                file_obj.write(formatted_pos + '\n')
                count += 1
                if (count % 1000) == 0:  # Make some noise every 10 minutes
                    log.info("%s:%d-%d wrote: %d regions..." % (chrom, start, end, count))
        else:
            log.info("Starting on SNPs for %s %s:%d-%d" % (assembly, chrom, start, end))
            for pos in atlas.iter_scored_snps(assembly, chrom, start, end):
                coordinates = '{}:{}-{}'.format(chrom, pos['start'], pos['end'])
                if format_json:
                    formatted_pos = json.dumps({pos.get('rsid', coordinates): pos},
                                                sort_keys=True)[1:-1] + ','
                else:
                    score = pos.get('score', '')
                    num_score = atlas.numeric_score(score)
                    formatted_pos = ("%s\t%d\t%d\t%s\t%d\t%s" %
                                    (chrom, pos['start'] - 1, pos['end'],
                                    pos.get('rsid', coordinates), num_score, score))
                    #                                    - 1 because bed format is 'half open'
                    case = atlas.make_a_case(pos)
                    for category in atlas.evidence_categories():  # in order
                        formatted_pos += '\t%s' % case.get(category, '')
                file_obj.write(formatted_pos + '\n')
                count += 1
                if (count % 10000) == 0:  # Make some noise every so often
                    log.info("%s:%d-%d wrote: %d SNPs..." % (chrom, start, end, count))

        if format_json:
            file_obj.write('"%s_count": %d,\n' % (chrom, count))
        if chrom.lower() == 'all':
            log.info("wrote %d %s for %s to %s" % (count, what, chrom, file_name))

        took = '%.3f' % (time.time() - begin)    # DEBUG: timing
        if not skip_header:
            file_obj.write(footer(took, count, format_json))
    log.info("Finished writing %d %s for %s %s:%d-%d  Took: %s" %
          (count, what, assembly, chrom, start, end, took))
    return


def pool_initializer(config_uri, app_name):
    global app
    app = get_app(config_uri, app_name)


def run_in_processes(args):
    global app
    assembly, chrom, start, end, file_name, signal, json, skip_header = args
    run(app, assembly, chrom, start, end, file_name, signal, json, skip_header)
    return '%s:%d-%d' % (chrom, start, end)  # return allows enumeration to wait for all results


def run_multiprocess(args):
    '''Run this code on multiple processes'''
    # NOTE: an earlier version tried using threads but that
    #       isn't true concurrency because of python GIL.
    # TODO: one command for all chroms ?!
    #if args.chrom.lower() == 'all':
    #    log.error("Multiplrocessing is only supported for single chrom.")
    #    return
    if args.chrom not in CHROM_SIZES.keys():
        log.error("Chosen chromosome '%s' is not supported." % (args.chrom))
        return

    app = get_app(args.config_uri, args.app_name)

    atlas = RegulomeAtlas(app.registry[SNP_SEARCH_ES])

    begin = time.time()  # DEBUG: timing
    chrom = args.chrom  # TODO: one command for all chroms!
    start = args.start
    final_end = atlas.cap_at_chrom_size(args.assembly, chrom, args.end)
    size_per_worker = int(math.ceil((final_end - start) / args.task_count))
    end = atlas.cap_at_chrom_size(args.assembly, chrom, start + size_per_worker)
    files = []

    log.info("Setting up %d tasks to run in multiple processes, each covering %d bases of sequence." %
          (args.task_count, size_per_worker))

    tasks = []
    while start < final_end:
        if end > final_end:
            end = final_end
        file_name = '/tmp/' + regularized_file_name(args.assembly, chrom, start, end,
                                                    args.signal, args.json)
        files.append(file_name)
        task_args = (args.assembly, chrom, start, end, file_name, args.signal, args.json, True)
        tasks.append(task_args)
        start = end + 1
        end = atlas.cap_at_chrom_size(args.assembly, args.chrom, end + size_per_worker)

    assert(args.task_count == len(tasks))

    process_count = min(args.task_count, args.process_count)
    try:
        pool = Pool(processes=process_count,initializer=pool_initializer,
                    initargs=(args.config_uri, args.app_name))
    except:
        log.info('Failed to make process pool')

    chunkiness = 1
    if args.task_count > process_count:
        chunkiness = int((args.task_count - 1) / process_count) + 1
    log.info('Launching %d workers for %d tasks (chunkiness: %d)' %
          (process_count, args.task_count, chunkiness))

    try:
        for i, pos in enumerate(pool.imap_unordered(run_in_processes, tasks, chunkiness)):
            #log.info('Finished task %d: %s' % (i + 1, pos))
            continue  # TMI... just keep it to yourself
    except:
        log.info('Failed to launch tasks')

    try:
        pool.terminate()
        pool.join()
    except:
        pass

    final_file_name = args.file_name
    if final_file_name == '':
        final_file_name = regularized_file_name(args.assembly, chrom, args.start, args.end,
                                                args.signal, args.json)
    log.info("All tasks are done.  Begining to write '%s'" % (final_file_name))

    with open(final_file_name, 'w') as final_out:  # overwrites anything in 'ts path
        final_out.write(header(atlas, args.signal, args.json))
        # closing file again, because mysteriously the header showed up after the files' contents

    with open(final_file_name, 'a') as final_out:
        for file_name in files:
            subprocess.call(['cat', file_name], stdout=final_out)
            os.remove(file_name)
    count = int(subprocess.check_output(['wc', '-l', final_file_name]).split()[0]) - 1  # not header
    took = '%.3f' % (time.time() - begin)    # DEBUG: timing
    with open(final_file_name, 'a') as final_out:
        final_out.write(footer(took, count, args.json))

    log.info('All work is DONE on %s %s:%d-%d  Took: %s  count: %d' %
          (args.assembly, chrom, args.start, final_end, took, count))
    return


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Generate scored SNPs from regulome_search", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    # sudo -u encoded bin/generate-scored-snps production.ini --assembly hg19 --chrom chr22
    parser.add_argument('config_uri', help="path to configfile")
    parser.add_argument('--app-name', help="Pyramid app name in configfile", default='app',
                        required=False)
    parser.add_argument('--assembly', help="Select 'hg19' or 'GRCh38'. Default: 'GRCh38'.",
                        default='GRCh38', required=False)
    # TODO: handle all chroms in one multiprocessing call?
    # parser.add_argument('--chrom', help="Limit file to a single chromosome. Default: 'all'",
    #                     default='all', required=False)
    parser.add_argument('--chrom', help="Limit file to a single chromosome.", required=True)
    parser.add_argument('--start', help="Start location. Default: 0",
                        default=0, type=int, required=False)
    parser.add_argument('--end', help="End location. Default: chrom size",
                        default=-1, type=int, required=False)
    parser.add_argument('--signal', help="Output bedGraph format for bigWig signal.",
                        action='store_true', required=False)
    parser.add_argument('--json', help="Output JSON instead of default bed.",
                        action='store_true', required=False)
    parser.add_argument('--file-name',
                        help="Name file to write to. "
                        "Default: 'regulome_<signal>_<assembly>_<chrom>_<start>_<end>.bed'",
                        default='', required=False)
    parser.add_argument('--task-count',
                        help="Launch multiple tasks in up to %d processes. Default: 1." %
                        (MAX_PROCESSES), default=1, type=int, required=False)
    parser.add_argument('--process-count',
                        help="Number of processes that tasks will run on. Default: %d." %
                        (MAX_PROCESSES), default=MAX_PROCESSES, type=int, required=False)
    args = parser.parse_args()

    # logging.basicConfig(stream=sys.stdout)
    logging.basicConfig()

    # Loading app will have configured from config file. Reconfigure here:
    logging.getLogger('encoded').setLevel(logging.DEBUG)

    if args.task_count > 1:
        return run_multiprocess(args)
    else:
        app = get_app(args.config_uri, args.app_name)
        return run(app, args.assembly, args.chrom, args.start, args.end, args.file_name,
                args.signal, args.json)


if __name__ == '__main__':
    main()
