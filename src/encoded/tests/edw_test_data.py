# EDW/encoded File object sync testing

# python representation of files below, with just EDW-relevant properties
# NOTE: input JSON for these are in data files in tests/edw_file/

# Recipe for pretty-printing JSON from python dict is:
# >>> x = json.dumps(dict, indent=4, separators=(',', ': '))
#>>> print x

format_app_file_out = {u'submitted_by': u'someone@gmail.com', u'file_format': u'fastq', u'md5sum': u'aeaea56e89ecb5acceece72f17d75717', u'accession': u'ENCFF001QZP', u'dataset': u'ENCSR000AAA', u'download_path': u'2013/5/9/ENCFF001QZP.txt.gz', u'replicate': 1, u'date_created': u'2013-05-09', u'output_type': u'reads2', u'submitted_file_name': u'../../../../pre-DCC/wgEncodeCshlLongRnaSeq/20130218_promocell_batches1-2_minus_batch1sFASTQ/SID38242_AC1GKKACXX_7_2.txt.gz'}

format_app_file_out2 = {u'submitted_by': u'/users/f5b7857d-208e-4acc-ac4d-4c2520814fe1/', u'file_format': u'fastq', u'md5sum': u'de9e05ad88fea5664f1c5d90815df358', u'accession': u'ENCFF001REQ', u'dataset': u'ENCSR000AES', u'download_path': u'2013/6/14/ENCFF001REQ.txt.gz', u'replicate': u'/replicates/ec1ed4db-de5f-481b-a686-261bda0319cb/', u'output_type': u'reads', u'date_created': u'2013-06-14', u'submitted_file_name': u'SID38822_AC1HYAACXX_5.txt.gz'}

