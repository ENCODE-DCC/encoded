class modERN_TF_control(object):

    def __init__(self, alignments=None, unique_signal=None,
                 normalized_signal=None, assembly=None, replicates=None):
        self.alignments = alignments
        self.unique_signal = unique_signal
        self.normalized_signal = normalized_signal
        self.assembly = assembly
        self.replicates = replicates
        self.tuples_dict = {
            ('bam', 'alignments'): self.set_alignments,
            ('bigWig', 'signal of unique reads'): self.set_unique_signal,
            ('bigWig', 'read-depth normalized signal'): self.set_normalized_signal
        }

    def get_alignments(self):
        return self.alignments

    def get_unique_signal(self):
        return self.unique_signal

    def get_normalized_signal(self):
        return self.normalized_signal

    def get_assembly(self):
        return self.assembly

    def get_replicates(self):
        return self.replicates

    def set_alignments(self, alignments):
        self.alignments = alignments

    def set_unique_signal(self, unique_signal):
        self.unique_signal = unique_signal

    def set_normalized_signal(self, normalized_signal):
        self.normalized_signal = normalized_signal

    def set_assembly(self, assembly):
        self.assembly = assembly

    def set_replicates(self, replicates):
        self.replicates = replicates

    def is_complete(self):
        if (self.alignments is None) or \
           (self.unique_signal is None) or \
           (self.normalized_signal is None) or \
           (self.replicates is None) or \
           (self.assembly is None):
            return False
        return True

    def get_missing_fields_tuples(self):
        missing = []
        if self.alignments is None:
            missing.append(('bam', 'alignments'))
        if self.unique_signal is None:
            missing.append(('bigWig', 'signal of unique reads'))
        if self.normalized_signal is None:
            missing.append(('bigWig', 'read-depth normalized signal'))
        return missing

    def update_fields(self, processed_file):
        f_format = processed_file.get('file_format')
        f_output = processed_file.get('output_type')
        self.tuples_dict[(f_format, f_output)](processed_file.get('accession'))
        self.replicates = processed_file.get('biological_replicates')
        self.assembly = processed_file.get('assembly')
