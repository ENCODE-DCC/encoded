from pyramid.paster import get_app
from elasticsearch import RequestError
import logging
import json
import time  # DEBUG: timing
from ..region_indexer import (
    SUPPORTED_CHROMOSOMES,
    REGULOME_SUPPORTED_ASSEMBLIES
)
from ..region_atlas import (
    RegulomeAtlas
)

from snovault.elasticsearch.interfaces import (
    ELASTIC_SEARCH,
    SNP_SEARCH_ES
)


EPILOG = __doc__

log = logging.getLogger(__name__)


def run(app, format_json=False, chosen_assembly=None, chosen_chrom=None):
    if chosen_assembly is not None and chosen_assembly.lower() == 'all':
        chosen_assembly=None
    if chosen_chrom is not None and chosen_chrom.lower() == 'all':
        chosen_chrom=None

    atlas = RegulomeAtlas(app.registry[SNP_SEARCH_ES])

    for assmebly in REGULOME_SUPPORTED_ASSEMBLIES:
        if chosen_assembly is not None and assembly != chosen_assembly:
            continue
        count = 0
        chrom_count = 0
        bed_file_name = 'regulome_SNPs_%s.bed' % assembly
        print("Starting to generate %s", bed_file_name)
        begin = time.time()  # DEBUG: timing
        bed_file = open(bed_file_name, 'a')
        if format_json:
            header = '{\n'
        else:
            columns = ['#chrom', 'start', 'end', 'rsid', 'num_score', 'score']  # bed 5 +
            columns.extend(atlas.evidence_categories())
            header = '\t'.join(columns) + '\n'
        bed_file.write(header)
        for chrom in SUPPORTED_CHROMOSOMES:
            if chosen_chrom is not None and chrom != chosen_chrom:
                continue
            count_by_chrom = 0
            start = 0
            end = 200000000 # chrom_length ??
            # Alternative: call path regulome_evidence/regulomeDB_{assembly}_{chrom}_0_{end}.bed
            #              then append all chrom files into bed_file (grep -v $# to remove comments)
            for snp in atlas.iter_scored_snps(assembly, chrom, start, end):
                count += 1
                count_by_chrom += 1
                coordinates = '{}:{}-{}'.format(snp['chrom'], snp['start'], snp['end'])
                if format_json:
                    formatted_snp = json.dumps({snp.get('rsid', coordinates): snp},sort_keys=True)[1:-1] + ','
                else:
                    score = snp.get('score','')
                    num_score = atlas.numeric_score(score)
                    formatted_snp = "%s\t%d\t%d\t%s\t%d\t%s" % (snp['chrom'], snp['start'], snp['end'], \
                                                    snp.get('rsid',coordinates), num_score, score)
                    case = atlas.make_a_case(snp)
                    for category in atlas.evidence_categories():  # in order
                        formatted_snp += '\t%s' % case.get(category,'')
                bed_file.write(formatted_snp + '\n')
                if (count % 1000000) == 0:  # Make some noise every 10 minutes
                    print("%d", count)

            if format_json:
                bed_file.write('"%s_count": %d,\n' % (chrom, count_by_chrom))
            print("wrote %d SNPs for %s to %s", count_by_chrom, chrom, bed_file_name)
            if count_by_chrom > 0:
                chrom_count += 1
        took = '%.3f' % (time.time() - begin)    # DEBUG: timing
        if format_json:
            bed_file.write('"took": %s,\n"chrom_count": %d,\n"count": %d\n}\n' % (took, chrom_count, count))
        else:
            yield bytes('# took: %s, count: %d\n' % (took, count), 'utf-8')
        bed_file.close()
        print("wrote %d SNPs to %s", count, bed_file_name)
    print("Done (finally)")

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Generate scored SNPs from regulome_search", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    # sudo -u encoded bin/generate-scored-snps production.ini --app-name app --assembly hg19 --chrom chr22
    parser.add_argument('config_uri', help="path to configfile")
    parser.add_argument('--app-name', help="Pyramid app name in configfile", default='app', required=False)
    parser.add_argument('--assembly', help="Select 'hg19' or 'GRCh38'.", default=None, required=False)
    parser.add_argument('--chrom',    help="Limit file to a single chromosome.", default=None, required=False)
    parser.add_argument('--json',     help="Output JSON instead of default bed.", action='store_true', required=False)
    args = parser.parse_args()

    logging.basicConfig()
    app = get_app(args.config_uri, args.app_name)

    # Loading app will have configured from config file. Reconfigure here:
    logging.getLogger('encoded').setLevel(logging.DEBUG)

    return run(app, args.json, args.assembly, args.chrom)


if __name__ == '__main__':
    main()
