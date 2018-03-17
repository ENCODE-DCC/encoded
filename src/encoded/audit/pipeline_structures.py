class basic_experiment(object):

    def __init__(self):
        self.file_types = {
            ('bam', 'alignments'): None
        }

        self.assembly = None
        self.replicates = None
        self.multiple_mappings_flag = False
        self.unexpected_file_flag = False
        self.unexpected_files_set = set()
        self.orphan_files = []
        self.orphan_files_flag = False

    def set_file(self, key, file_acession):
        if self.file_types[key] is not None:
            self.multiple_mappings_flag = True
        self.file_types[key] = file_acession

    def is_complete(self):
        for entry in self.file_types:
            if self.file_types[entry] is None:
                return False
        return True

    def is_analyzed_more_than_once(self):
        return self.multiple_mappings_flag

    def get_missing_fields_tuples(self):
        missing = []
        for entry in self.file_types:
            if self.file_types[entry] is None:
                missing.append(entry)
        return missing

    def has_unexpected_files(self):
        return self.unexpected_file_flag

    def get_unexpected_files(self):
        return self.unexpected_files_set

    def has_orphan_files(self):
        return self.orphan_files_flag

    def get_orphan_files(self):
        return self.orphan_files

    def update_fields(self, processed_file):
        if processed_file.get('lab') == '/labs/encode-processing-pipeline/':
            if len(processed_file.get('biological_replicates')) == 0:
                self.orphan_files.append(processed_file.get('accession'))
                self.orphan_files_flag = True
            else:
                f_format = processed_file.get('file_format')
                f_output = processed_file.get('output_type')
                if (f_format, f_output) not in self.file_types:
                    self.unexpected_file_flag = True
                    to_add = (f_format, f_output, processed_file['accession'])
                    self.unexpected_files_set.add(to_add)
                else:
                    # self.file_types[(f_format, f_output)] = processed_file.get('accession')
                    self.set_file((f_format, f_output), processed_file.get('accession'))
                    self.replicates = processed_file.get('biological_replicates')
                    self.assembly = processed_file.get('assembly')


class encode_chip_control(basic_experiment):
    def __init__(self):
        basic_experiment.__init__(self)
        self.file_types[('bam', 'unfiltered alignments')] = None

    def update_fields(self, processed_file):
        if processed_file.get('lab') == '/labs/encode-processing-pipeline/':
            if len(processed_file.get('biological_replicates')) == 0:
                self.orphan_files.append(processed_file.get('accession'))
                self.orphan_files_flag = True
            else:
                f_format = processed_file.get('file_format')
                f_output = processed_file.get('output_type')

                replicates_string = str(processed_file.get('biological_replicates'))[1:-1]

                if ((f_format, f_output) not in self.file_types) or \
                (len(replicates_string) > 0 and ',' in replicates_string):
                    self.unexpected_file_flag = True
                    to_add = (f_format, f_output, processed_file['accession'])
                    self.unexpected_files_set.add(to_add)
                else:
                    # self.file_types[(f_format, f_output)] = processed_file.get('accession')
                    self.set_file((f_format, f_output), processed_file.get('accession'))
                    self.replicates = processed_file.get('biological_replicates')
                    self.assembly = processed_file.get('assembly')


class encode_chip_experiment_replicate(basic_experiment):
    def __init__(self):
        basic_experiment.__init__(self)
        self.file_types[('bam', 'unfiltered alignments')] = None
        self.file_types[('bed', 'peaks')] = None
        self.file_types[('bigBed', 'peaks')] = None
        self.file_types[('bigWig', 'fold change over control')] = None
        self.file_types[('bigWig', 'signal p-value')] = None


class encode_chip_histone_experiment_unreplicated(basic_experiment):
    def __init__(self):
        basic_experiment.__init__(self)
        self.file_types[('bam', 'unfiltered alignments')] = None
        self.file_types[('bed', 'peaks')] = None
        self.file_types[('bigBed', 'peaks')] = None
        self.file_types[('bigWig', 'fold change over control')] = None
        self.file_types[('bigWig', 'signal p-value')] = None
        self.file_types[('bed', 'stable peaks')] = None
        self.file_types[('bigBed', 'stable peaks')] = None

class encode_chip_tf_experiment_unreplicated(basic_experiment):
    def __init__(self):
        basic_experiment.__init__(self)
        self.file_types[('bam', 'unfiltered alignments')] = None
        self.file_types[('bed', 'peaks')] = None
        self.file_types[('bigBed', 'peaks')] = None
        self.file_types[('bigWig', 'fold change over control')] = None
        self.file_types[('bigWig', 'signal p-value')] = None  
        self.file_types[('bed', 'pseudoreplicated idr thresholded peaks')] = None
        self.file_types[('bigBed', 'pseudoreplicated idr thresholded peaks')] = None


class encode_chip_histone_experiment_pooled(basic_experiment):
    def __init__(self):
        basic_experiment.__init__(self)
        del self.file_types[('bam', 'alignments')]
        self.file_types[('bed', 'replicated peaks')] = None
        self.file_types[('bigBed', 'replicated peaks')] = None
        self.file_types[('bed', 'peaks')] = None
        self.file_types[('bigBed', 'peaks')] = None
        self.file_types[('bigWig', 'fold change over control')] = None
        self.file_types[('bigWig', 'signal p-value')] = None


class encode_chip_tf_experiment_pooled(basic_experiment):
    def __init__(self):
        basic_experiment.__init__(self)
        del self.file_types[('bam', 'alignments')]
        self.file_types[('bed', 'peaks')] = None
        self.file_types[('bigBed', 'peaks')] = None
        self.file_types[('bigWig', 'fold change over control')] = None
        self.file_types[('bigWig', 'signal p-value')] = None
        self.file_types[('bed', 'conservative idr thresholded peaks')] = None
        self.file_types[('bigBed', 'conservative idr thresholded peaks')] = None
        self.file_types[('bed', 'optimal idr thresholded peaks')] = None
        self.file_types[('bigBed', 'optimal idr thresholded peaks')] = None

