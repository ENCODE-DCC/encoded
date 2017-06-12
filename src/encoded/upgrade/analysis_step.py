from snovault import upgrade_step
from .upgrade_data.analysis_step_5_to_6 import (
    label_mapping,
    status_mapping,
    title_mapping,
    major_version_mapping,
    aliases_mapping
)


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
    # http://redmine.encodedcc.org/issues/3019

    import re

    if 'output_file_types' in value:
        for i in range(0, len(value['output_file_types'])):
            string = value['output_file_types'][i]
            value['output_file_types'][i] = re.sub('multi-mapped', 'all', string)
    if 'input_file_types' in value:
        for i in range(0, len(value['input_file_types'])):
            string = value['input_file_types'][i]
            value['input_file_types'][i] = re.sub('multi-mapped', 'all', string)

    # http://redmine.encodedcc.org/issues/3074
    del value['software_versions']

    # http://redmine.encodedcc.org/issues/3074 note 16 and 3073
    if value.get('name') in ['lrna-se-star-alignment-step-v-2-0',
                            'lrna-pe-star-alignment-step-v-2-0',
                            'lrna-pe-star-stranded-signal-step-v-2-0',
                            'lrna-pe-star-stranded-signals-for-tophat-step-v-2-0',
                            'lrna-se-star-unstranded-signal-step-v-2-0',
                            'lrna-se-star-unstranded-signals-for-tophat-step-v-2-0',
                            'index-star-v-2-0',
                            'rampage-grit-peak-calling-step-v-1-1'
                            ]:
        value['status'] = 'deleted'

    if value.get('name') == 'lrna-pe-rsem-quantification-v-1':
        value['parents'] = ['ace7163c-563a-43d6-a86f-686405af167d', #/analysis-steps/lrna-pe-star-alignment-step-v-1/'
                            '9ca04da2-5ef7-4ba1-b78c-41dfc4be0c11'  #/analysis-steps/index-rsem-v-1-0/'
                            ]
    elif value.get('name') == 'lrna-se-rsem-quantification-step-v-1':
        value['parents'] = ['3cad3827-7f21-4f70-9cbc-e718b5529775', #/analysis-steps/lrna-se-star-alignment-step-v-1/',
                            '9ca04da2-5ef7-4ba1-b78c-41dfc4be0c11'  #/analysis-steps/index-rsem-v-1-0/'
                            ]


@upgrade_step('analysis_step', '3', '4')
def analysis_step_3_4(value, system):
    # http://redmine.encodedcc.org/issues/3063
    if 'analysis_step_types' in value:
        value['analysis_step_types'] = list(set(value['analysis_step_types']))

    if 'input_file_types' in value:
        value['input_file_types'] = list(set(value['input_file_types']))

    if 'output_file_types' in value:
        value['output_file_types'] = list(set(value['output_file_types']))

    if 'qa_stats_generated' in value:
        value['qa_stats_generated'] = list(set(value['qa_stats_generated']))

    if 'parents' in value:
        value['parents'] = list(set(value['parents']))

    if 'aliases' in value:
        value['aliases'] = list(set(value['aliases']))

    if 'documents' in value:
        value['documents'] = list(set(value['documents']))


@upgrade_step('analysis_step', '5', '6')
def analysis_step_5_6(value, system):
    # http://redmine.encodedcc.org/issues/4987

    uuid = value.get('uuid')

    value['step_label'] = label_mapping[uuid]
    value['major_version'] = major_version_mapping[uuid]
    if uuid in title_mapping:
        value['title'] = title_mapping.get(uuid)
    if uuid in status_mapping:
        value['status'] = status_mapping.get(uuid)
    if uuid in aliases_mapping:
        if 'aliases' not in value:
            value['aliases'] = []
        value['aliases'].append(aliases_mapping.get(uuid))
