# EDW/encoded File object sync testing

# test_format_app_file
#
# python representation of files below, with just EDW-relevant properties
# NOTE: input JSON for these are in data files in tests/edw_file/

# Recipe for pretty-printing JSON from python dict is:
# >>> x = json.dumps(dict, indent=4, separators=(',', ': '))
#>>> print x

format_app_file_out = {
u'status': u'CURRENT', u'submitted_by': u'risus.fermentum@vel.at', u'file_format': u'fastq', u'md5sum': u'f73b8010630a28fe9ac1f93155a46e8b', u'accession': u'ENCFF001RET', u'dataset': u'ENCSR000AER', u'download_path': u'2013/6/14/ENCFF001RET.txt.gz', u'replicate': 1, u'output_type': u'reads1', u'date_created': u'2013-06-14', u'submitted_file_name': u'SID38815_AC1UHYACXX_7_1.txt.gz'
}


# test_list_new
# input is list of some accessions in test data set, and some not (the ZZZ's)
# output should be just those not (the new ones)

new_in = ['ENCFF000LSP', 'ENCFF999ZZZ', 'ENCFF998ZZZ', 'ENCFF001MXE',
          'ENCFF001MXG', 'ENCFF001MYM', 'ENCFF997ZZZ', 'ENCFF996ZZZ']

# ENCFF9??ZZZ not in app test database (may be reserved at EDW for testing)
new_out = ['ENCFF999ZZZ', 'ENCFF998ZZZ', 'ENCFF997ZZZ', 'ENCFF996ZZZ']

# All ENCODE 2 experiments in test set
encode2 = {
    'wgEncodeEM002001',
    'wgEncodeEM002004',
    'wgEncodeEH003317',
    'wgEncodeEH002229',
}

# An ENCODE 3 experiment in test set
encode3 = 'ENCSR000AES'
