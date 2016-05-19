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

    def set_alignments(self, alignments):
        self.alignments = alignments

    def set_unique_signal(self, unique_signal):
        self.unique_signal = unique_signal

    def set_normalized_signal(self, normalized_signal):
        self.normalized_signal = normalized_signal

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


class modERN_TF(object):
    def __init__(self, replicates):
        if len(replicates[1:-1]) == 1:
            self.rep = modERN_TF_relicate()
        else:
            self.rep = modERN_TF_pooled()

    def is_complete(self):
        return self.rep.is_complete()

    def get_missing_fields_tuples(self):
        return self.rep.get_missing_fields_tuples()

    def update_fields(self, processed_file):
        self.rep.update_fields(processed_file)


class modERN_TF_relicate(object):

    def __init__(self, alignments=None, unique_signal=None,
                 read_depth_normalized_signal=None,
                 control_normalized_signal=None,
                 narrowPeak_bed=None, narrowPeak_bigBed=None,
                 assembly=None, replicates=None):
        self.alignments = alignments
        self.unique_signal = unique_signal
        self.read_depth_normalized_signal = read_depth_normalized_signal
        self.control_normalized_signal = control_normalized_signal
        self.narrowPeak_bed = narrowPeak_bed
        self.narrowPeak_bigBed = narrowPeak_bigBed
        self.assembly = assembly
        self.replicates = replicates
        self.tuples_dict = {
            ('bam', 'alignments'): self.set_alignments,
            ('bigWig', 'signal of unique reads'): self.set_unique_signal,
            ('bigWig', 'read-depth normalized signal'): self.set_read_depth_normalized_signal,
            ('bigWig', 'control normalized signal'): self.set_control_normalized_signal,
            ('bed', 'narrowPeak'): self.set_narrowPeak_bed,
            ('bigBed', 'narrowPeak'): self.set_narrowPeak_bigBed
        }

    def set_alignments(self, alignments):
        self.alignments = alignments

    def set_unique_signal(self, unique_signal):
        self.unique_signal = unique_signal

    def set_read_depth_normalized_signal(self, normalized_signal):
        self.read_depth_normalized_signal = normalized_signal

    def set_control_normalized_signal(self, control_signal):
        self.control_normalized_signal = control_signal

    def set_narrowPeak_bed(self, bed):
        self.narrowPeak_bed = bed

    def set_narrowPeak_bigBed(self, bigBed):
        self.narrowPeak_bigBed = bigBed

    def is_complete(self):
        if (self.alignments is None) or \
           (self.unique_signal is None) or \
           (self.read_depth_normalized_signal is None) or \
           (self.replicates is None) or \
           (self.assembly is None) or \
           (self.control_normalized_signal is None) or \
           (self.narrowPeak_bed is None) or \
           (self.narrowPeak_bigBed is None):
            return False
        return True

    def get_missing_fields_tuples(self):
        missing = []
        if self.alignments is None:
            missing.append(('bam', 'alignments'))
        if self.unique_signal is None:
            missing.append(('bigWig', 'signal of unique reads'))
        if self.read_depth_normalized_signal is None:
            missing.append(('bigWig', 'read-depth normalized signal'))
        if self.control_normalized_signal is None:
            missing.append(('bigWig', 'control normalized signal'))
        if self.narrowPeak_bed is None:
            missing.append(('bed', 'narrowPeak'))
        if self.narrowPeak_bigBed is None:
            missing.append(('bigBed', 'narrowPeak'))
        return missing

    def update_fields(self, processed_file):
        f_format = processed_file.get('file_format')
        if processed_file.get('output_type') in ['peaks']:
            f_output = processed_file.get('file_format_type')
        else:
            f_output = processed_file.get('output_type')
        self.tuples_dict[(f_format, f_output)](processed_file.get('accession'))
        self.replicates = processed_file.get('biological_replicates')
        self.assembly = processed_file.get('assembly')


class modERN_TF_pooled(object):

    def __init__(self, unique_signal=None,
                 read_depth_normalized_signal=None,
                 control_normalized_signal=None,
                 narrowPeak_bed=None, narrowPeak_bigBed=None,
                 idr_narrowPeak_bed=None, idr_narrowPeak_bigBed=None,
                 assembly=None, replicates=None):

        self.unique_signal = unique_signal
        self.read_depth_normalized_signal = read_depth_normalized_signal
        self.control_normalized_signal = control_normalized_signal
        self.narrowPeak_bed = narrowPeak_bed
        self.narrowPeak_bigBed = narrowPeak_bigBed
        self.idr_narrowPeak_bed = idr_narrowPeak_bed
        self.idr_narrowPeak_bigBed = idr_narrowPeak_bigBed
        self.assembly = assembly
        self.replicates = replicates
        self.tuples_dict = {
            ('bigWig', 'signal of unique reads'): self.set_unique_signal,
            ('bigWig', 'read-depth normalized signal'): self.set_read_depth_normalized_signal,
            ('bigWig', 'control normalized signal'): self.set_control_normalized_signal,
            ('bed', 'narrowPeak'): self.set_narrowPeak_bed,
            ('bigBed', 'narrowPeak'): self.set_narrowPeak_bigBed,
            ('bed', 'optimal idr thresholded narrowPeak'): self.set_idr_narrowPeak_bed,
            ('bigBed', 'optimal idr thresholded narrowPeak'): self.set_idr_narrowPeak_bigBed
        }

    def set_unique_signal(self, unique_signal):
        self.unique_signal = unique_signal

    def set_read_depth_normalized_signal(self, normalized_signal):
        self.read_depth_normalized_signal = normalized_signal

    def set_control_normalized_signal(self, control_signal):
        self.control_normalized_signal = control_signal

    def set_narrowPeak_bed(self, bed):
        self.narrowPeak_bed = bed

    def set_narrowPeak_bigBed(self, bigBed):
        self.narrowPeak_bigBed = bigBed

    def set_idr_narrowPeak_bed(self, idr_bed):
        self.idr_narrowPeak_bed = idr_bed

    def set_idr_narrowPeak_bigBed(self, idr_bigBed):
        self.idr_narrowPeak_bigBed = idr_bigBed

    def is_complete(self):
        if (self.unique_signal is None) or \
           (self.read_depth_normalized_signal is None) or \
           (self.replicates is None) or \
           (self.assembly is None) or \
           (self.control_normalized_signal is None) or \
           (self.narrowPeak_bed is None) or \
           (self.narrowPeak_bigBed is None) or \
           (self.idr_narrowPeak_bed is None) or \
           (self.idr_narrowPeak_bigBed is None):
            return False
        return True

    def get_missing_fields_tuples(self):
        missing = []
        if self.unique_signal is None:
            missing.append(('bigWig', 'signal of unique reads'))
        if self.read_depth_normalized_signal is None:
            missing.append(('bigWig', 'read-depth normalized signal'))
        if self.control_normalized_signal is None:
            missing.append(('bigWig', 'control normalized signal'))
        if self.narrowPeak_bed is None:
            missing.append(('bed', 'narrowPeak'))
        if self.narrowPeak_bigBed is None:
            missing.append(('bigBed', 'narrowPeak'))
        if self.idr_narrowPeak_bed is None:
            missing.append(('bed', 'optimal idr thresholded narrowPeak'))
        if self.idr_narrowPeak_bigBed is None:
            missing.append(('bigBed', 'optimal idr thresholded narrowPeak'))
        return missing

    def update_fields(self, processed_file):
        f_format = processed_file.get('file_format')
        if processed_file.get('output_type') in ['peaks']:
            f_output = processed_file.get('file_format_type')
        else:
            f_output = processed_file.get('output_type')
        self.tuples_dict[(f_format, f_output)](processed_file.get('accession'))
        self.replicates = processed_file.get('biological_replicates')
        self.assembly = processed_file.get('assembly')
