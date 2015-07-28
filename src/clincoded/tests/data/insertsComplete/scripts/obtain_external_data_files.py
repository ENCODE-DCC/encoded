"""

    Usage: obtain_external_data_files.py [-h] [-s {hgnc,orphanet,clinvar}]

    Script gets source data we need from HGNC, Orphanet, or ClinVar.

    optional arguments:
      -h, --help            show this help message and exit
      -s {hgnc,orphanet,clinvar}, --source {hgnc,orphanet,clinvar}
                            (hgnc=HGNC, orphanet=Orphanet, clinvar=ClinVar)


    Note:
        Dependencies: requests
        Before running, `pip3 install requests`

    Note2: HGNC URL to fetch data is derived by going to the main page:
            http://www.genenames.org/cgi-bin/download
            and accepting the default options shown, then click "submit"

    Note3: TODO: Add error handling for connections
            + test correct output is saved

"""

import sys
import argparse
from ftplib import FTP
import os
import gzip

import requests

# usage information and arument processing
purpose = 'Script gets source data we need from HGNC, Orphanet, or ClinVar.'
parser = argparse.ArgumentParser(description=purpose)
parser.add_argument("-s", "--source", choices=["hgnc", "orphanet", "clinvar"],
                    help="(hgnc=HGNC, orphanet=Orphanet, clinvar=ClinVar)")

# if no args are passed to script, print basic usage and exit
if len(sys.argv) < 2:
    parser.print_usage()
    sys.exit(1)
else:
    args = parser.parse_args()


def print_output_spacer():
    print("")
    print("--------------------------------------------------")


# fetch data from URL using python requests package
# and write out results to specified destination
# (requests does not support ftp)
def request_and_save_data(url, file_destination):
    page = requests.get(url)
    with open(file_destination, 'wb') as file:
        file.write(page.content)

# hgnc
if args.source == "hgnc":
    print_output_spacer()
    print("Obtaining latest HUGO Gene Nomenclature data from the HGNC site...")
    print("--saving output to rawData/gene.txt")

    file_destination = "rawData/gene.txt"
    url = "http://www.genenames.org/cgi-bin/download?col=gd_hgnc_id&col=gd_app_sym&col=gd_app_name&col=gd_status&col=gd_locus_type&col=gd_locus_group&col=gd_prev_sym&col=gd_prev_name&col=gd_aliases&col=gd_name_aliases&col=gd_pub_chrom_map&col=gd_pub_acc_ids&col=gd_pub_eg_id&col=gd_pubmed_ids&col=md_eg_id&col=md_mim_id&status=Approved&status=Entry+Withdrawn&status_opt=2&where=&order_by=gd_app_sym_sort&format=text&limit=&hgnc_dbtag=on&submit=submit"
    request_and_save_data(url, file_destination)

# orphanet
elif args.source == "orphanet":
    print_output_spacer()
    print("Obtaining latest Orphanet release data from the Orphanet site...")
    print("--saving en_product1.xml to rawData/disease.xml")

    file_destination = "rawData/disease.xml"
    url = "http://www.orphadata.org/data/xml/en_product1.xml"
    request_and_save_data(url, file_destination)

# clinvar
elif args.source == "clinvar":
    print_output_spacer()
    print("Obtaining latest ClinVar release data from the NCBI ftp site...")

    # Note: ClinVar's ClinVarFullRelease_00-latest.xml.gz is a symlink to the
    # whatever the current version of the file is. We will grab the file it is
    # symlinked to so we can preserve the name information associated with that
    # version, and then symlink it locally as ClinVar does to
    # ClinVarFullRelease_00-latest.xml.gz

    master_symlink_filename = "ClinVarFullRelease_00-latest.xml.gz"
    master_filename = "ClinVarFullRelease_00-latest.xml"

    # make ftp connection and identify and download the most current
    # version of the data
    with FTP("ftp.ncbi.nlm.nih.gov") as ftp:
        ftp.login()
        unique_file_id = None

        # get a listing of files in the clinvar xml dir
        # the unique IDs will tell us which file is symlinked to the "latest
        # file" so we can obtain that version
        for file in ftp.mlsd(path="pub/clinvar/xml", facts=["unique"]):
            # if file name matches the name we expect for the file symlinked
            # to the most updated version
            if file[0] == master_symlink_filename:
                unique_file_id = file[1]["unique"]
                print("--Unique ID for {0} is {1}".format(master_symlink_filename, unique_file_id))
            # if a subsequent file has the same unique ID it is the source
            # file for the symlink
            if file[1]["unique"] == unique_file_id and file[0] != master_symlink_filename and unique_file_id != None:
                file_to_retrieve = file[0]
                print("--The file symlinked to {0} is {1}".format(master_symlink_filename, file_to_retrieve))

        ftp.cwd('pub/clinvar/xml')
        localfile = open('rawData/' + file_to_retrieve, 'wb')
        print("--Downloading {0}".format(file_to_retrieve))
        ftp.retrbinary('RETR ' + file_to_retrieve, localfile.write, 1024)

        # close ftp connection
        ftp.quit()
        localfile.close()

    # symlink the "master" filename to the file with the most current data
    print_output_spacer()
    print("Symlinking {0} to {1} in the ./data directory".format(master_symlink_filename, file_to_retrieve))
    if os.path.exists('rawData/' + master_symlink_filename):
        print("--A symlink already exists for {0}, renaming that to {0}_OLD first".format(master_symlink_filename))
        os.rename('rawData/' + master_symlink_filename, 'rawData/' + master_symlink_filename + '_OLD')
    os.symlink(file_to_retrieve, 'rawData/' + master_symlink_filename)

    # uncompress the downloaded file (actually the symlinked file)
    print_output_spacer()
    print("Uncompressing {0} in the ./data directory".format(master_symlink_filename))
    gzipped_file_in = gzip.open('rawData/' + file_to_retrieve, 'rb')
    gzipped_file_out = open('rawData/' + master_filename, 'wb')
    gzipped_file_out.write(gzipped_file_in.read())
    gzipped_file_in.close()
    gzipped_file_out.close()

    print_output_spacer()
    print("The final ClinVar uncompressed data file {0} can be found here: rawData/{0}".format(master_filename))


print_output_spacer()
print("DONE!")
