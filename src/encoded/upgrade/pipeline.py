from contentbase import upgrade_step


@upgrade_step('pipeline', '', '2')
def pipeline_0_2(value, system):
    # http://redmine.encodedcc.org/issues/3001

    value['lab'] = "a558111b-4c50-4b2e-9de8-73fd8fd3a67d"  # /labs/encode-processing-pipeline/
    value['award'] = "b5736134-3326-448b-a91a-894aafb77876"  # /awards/ENCODE/


@upgrade_step('pipeline', '2', '3')
def pipeline_2_3(value, system):
    # http://redmine.encodedcc.org/issues/3093
    value.pop('name', None)
    value.pop('version', None)
    value.pop('end_points', None)

    # http://redmine.encodedcc.org/issues/3074 note 16
    if value.get('accession') in ['ENCPL739VZK', 'ENCPL086BPC', 'ENCPL611KAU']:
        value['status'] = 'replaced'
    elif value.get('accession') == 'ENCPL521QAX':
        value['status'] = 'deleted'
    elif value.get('accession') == 'ENCPL002LSE':
        value['analysis_steps'] = [
            '9ca04da2-5ef7-4ba1-b78c-41dfc4be0c11',  # /analysis-steps/index-rsem-v-1-0/
            '76635694-c515-4a41-9976-ec59bb8b8522',  # /analysis-steps/index-star-v-1-0/
            '9e559b6e-c6f8-4ea7-9073-ec2d75af360f',  # /analysis-steps/index-tophat-v-1-0/
            '3cad3827-7f21-4f70-9cbc-e718b5529775',  # /analysis-steps/lrna-se-star-alignment-step-v-1/
            '7505ced9-3584-4146-84a1-7c5695cb8cf4',  # /analysis-steps/lrna-se-rsem-quantification-step-v-1/
            'd89fc557-a9a3-4a08-8bea-a92739380464',  # /analysis-steps/lrna-se-tophat-alignment-step-v-1/
            '67dec549-0feb-493c-8b3c-830b34207076',  # /analysis-steps/lrna-se-star-unstranded-signals-for-tophat-step-v-1/
            '267a9410-348b-4f32-a1bf-9392aacb8f61'   # /analysis-steps/lrna-se-star-unstranded-signal-step-v-1/
            ]
    elif value.get('accession') == 'ENCPL002LPE':
        value['analysis_steps'] = [
            '9ca04da2-5ef7-4ba1-b78c-41dfc4be0c11',  # /analysis-steps/index-rsem-v-1-0/
            '76635694-c515-4a41-9976-ec59bb8b8522',  # /analysis-steps/index-star-v-1-0/
            '9e559b6e-c6f8-4ea7-9073-ec2d75af360f',  # /analysis-steps/index-tophat-v-1-0/
            'ace7163c-563a-43d6-a86f-686405af167d',  # /analysis-steps/lrna-pe-star-alignment-step-v-1/
            'e33749d8-8680-4f0a-b1c3-5f58dcd9dc28',  # /analysis-steps/lrna-pe-rsem-quantification-v-1/
            '8d7d13b4-a841-47d0-a7aa-ddf473f18e88',  # /analysis-steps/lrna-pe-tophat-alignment-step-v-1/
            'b7c26c44-6c6a-4b13-a723-d09542516761',  # /analysis-steps/lrna-pe-star-stranded-signal-step-v-1/
            'bec07d6f-7283-4960-b04b-94819b5f69df',  # /analysis-steps/lrna-pe-star-stranded-signals-for-tophat-step-v-1/
            ]
