from snovault import (
    AuditFailure,
    audit_checker,
)
from .formatter import (
    audit_link,
    path_to_text,
)

@audit_checker('AnalysisStep', frame=['object', 'pipelines', 'pipelines.award'])
def audit_analysis_steps_used_by_multiple_pipelines(value, system):
    ''' We want to avoid situations where a single analysis step is used by
        multiple pipelines of different award and lab. 
    '''
    if not value.get('pipelines'):
        return
    if len(value.get('pipelines')) < 2:
    	return

    analysisStep = value['@id']
    pipelines = value.get('pipelines')
    pipelineAward = {}
    pipelineLab = {}
    for p in pipelines:
        pipelineAward[p['@id']] = (p.get('award')['rfa'])
        pipelineLab[p['@id']] = (p['lab'])

    flippedAwardDict = {}
    flippedLabDict = {}
    for key, value in pipelineAward.items():
	    if value not in flippedAwardDict:
	        flippedAwardDict[value] = [key]
	    else:
	        flippedAwardDict[value].append(key)

    for key, value in pipelineLab.items():
	    if value not in flippedLabDict:
	        flippedLabDict[value] = [key] 
	    else:
	        flippedLabDict[value].append(key)

    if len(flippedAwardDict.keys()) > 1:
    	awardA = list(flippedAwardDict.keys())[0]
    	awardB = list(flippedAwardDict.keys())[1]
    	pipelineA = flippedAwardDict[awardA][0]
    	pipelineB = flippedAwardDict[awardB][0]
    	detail = ('Analysis step {} is associated with multiple pipelines with different '
    		'RFAs, where {} is associated with {} and {} is associated with {}.'.format(
    			audit_link(path_to_text(analysisStep), analysisStep),
				audit_link(path_to_text(pipelineA), pipelineA),
				awardA,
				audit_link(path_to_text(pipelineB), pipelineB),
				awardB
				)
    		)
    	yield AuditFailure('analysis step used by multiple pipelines', detail, level='INTERNAL_ACTION')


    if len(flippedLabDict.keys()) > 1:
        LabA = list(flippedLabDict.keys())[0]
        LabB = list(flippedLabDict.keys())[1]
        pipelineA = flippedLabDict[LabA][0]
        pipelineB = flippedLabDict[LabB][0]
        detail = ('Analysis step {} is associated with multiple pipelines from different '
    		'labs, where {} is associated with {} and {} is associated with {}.'.format(
    			audit_link(path_to_text(analysisStep), analysisStep),
				audit_link(path_to_text(pipelineA), pipelineA),
				audit_link(path_to_text(LabA), LabA),
				audit_link(path_to_text(pipelineB), pipelineB),
				audit_link(path_to_text(LabB), LabB)
				)
    		)
        yield AuditFailure('analysis step used by multiple pipelines', detail, level='INTERNAL_ACTION')
