from contentbase import upgrade_step


@upgrade_step('analysis_step', '1', '2')
def analysis_step_1_2(value, system):
    # http://redmine.encodedcc.org/issues/2770

    input_mapping = {
        'align-star-pe-v-1-0-2': ['reads'],
        'align-star-pe-v-2-0-0': ['reads'],
        'align-star-se-v-1-0-2': ['reads'],
        'align-star-se-v-2-0-0': ['reads'],
        'index-star-v-1-0-1': ['genome reference', 'spike-in sequence', 'reference genes'],
        'index-star-v-2-0-0': ['genome reference', 'spike-in sequence', 'reference genes'],
        'index-rsem-v-1-0-1': ['genome reference', 'spike-in sequence', 'reference genes'],
        'index-tophat-v-1-0-0': ['genome reference', 'spike-in sequence', 'reference genes'],
        'quant-rsem-v-1-0-2': ['transcriptome alignments'],
        'stranded-signal-star-v-1-0-1': ['alignments'],
        'stranded-signal-star-v-2-0-0': ['alignments'],
        'unstranded-signal-star-v-1-0-1': ['alignments'],
        'unstranded-signal-star-v-2-0-0': ['alignments'],
        'align-tophat-pe-v-1-0-1': ['reads'],
        'align-tophat-se-v-1-0-1': ['reads']
    }
    output_mapping = {
        'align-star-pe-v-1-0-2': ['alignments'],
        'align-star-pe-v-2-0-0': ['alignments'],
        'align-star-se-v-1-0-2': ['alignments'],
        'align-star-se-v-2-0-0': ['alignments'],
        'index-star-v-1-0-1': ['genome index'],
        'index-star-v-2-0-0': ['genome index'],
        'index-rsem-v-1-0-1': ['genome index'],
        'index-tophat-v-1-0-0': ['genome index'],
        'quant-rsem-v-1-0-2': ['gene quantifications'],
        'stranded-signal-star-v-1-0-1': [
            'minus strand signal of multi-mapped reads',
            'plus strand signal of multi-mapped reads',
            'minus strand signal of unique reads',
            'plus strand signal of unique reads'
        ],
        'stranded-signal-star-v-2-0-0': [
            'minus strand signal of multi-mapped reads',
            'plus strand signal of multi-mapped reads',
            'minus strand signal of unique reads',
            'plus strand signal of unique reads'
        ],
        'unstranded-signal-star-v-1-0-1': [
            'signal of multi-mapped reads',
            'signal of unique reads'
        ],
        'unstranded-signal-star-v-2-0-0': [
            'signal of multi-mapped reads',
            'signal of unique reads'
        ],
        'align-tophat-pe-v-1-0-1': ['alignments'],
        'align-tophat-se-v-1-0-1': ['alignments']
    }

    value['input_file_types'] = input_mapping[value['name']]
    value['output_file_types'] = output_mapping[value['name']]


@upgrade_step('analysis_step', '2', '3')
def analysis_step_2_3(value, system):
    # http://redmine.encodedcc.org/issues/3074
    del value['software_versions']
