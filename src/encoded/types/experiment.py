from pyramid.traversal import find_root
from contentbase import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    ALLOW_SUBMITTER_ADD,
    Item,
    paths_filtered_by_status,
)
from .dataset import Dataset
import datetime


@collection(
    name='experiments',
    unique_key='accession',
    properties={
        'title': 'Experiments',
        'description': 'Listing of Experiments',
    })
class Experiment(Dataset):
    item_type = 'experiment'
    schema = load_schema('encoded:schemas/experiment.json')
    base_types = [Dataset.__name__] + Dataset.base_types
    embedded = Dataset.embedded + [
        'files.lab',
        'files.platform',
        'files.lab',
        'files.derived_from',
        'files.derived_from.replicate',
        'files.analysis_step_version.analysis_step',
        'files.analysis_step_version.analysis_step.pipelines',
        'files.analysis_step_version.analysis_step.versions',
        'files.analysis_step_version.analysis_step.versions.software_versions',
        'files.analysis_step_version.analysis_step.versions.software_versions.software',
        'files.analysis_step_version.software_versions',
        'files.analysis_step_version.software_versions.software',
        'files.replicate.library.biosample',
        'files.quality_metrics',
        'files.quality_metrics.step_run',
        'files.quality_metrics.step_run.analysis_step_version.analysis_step',
        'contributing_files.platform',
        'contributing_files.lab',
        'contributing_files.derived_from',
        'contributing_files.analysis_step_version.analysis_step',
        'contributing_files.analysis_step_version.analysis_step.pipelines',
        'contributing_files.analysis_step_version.software_versions',
        'contributing_files.analysis_step_version.software_versions.software',
        'award.pi.lab',
        'replicates.antibody',
        'replicates.antibody.targets',
        'replicates.library',
        'replicates.library.documents.lab',
        'replicates.library.documents.submitted_by',
        'replicates.library.documents.award',
        'replicates.library.biosample.submitted_by',
        'replicates.library.biosample.source',
        'replicates.library.biosample.organism',
        'replicates.library.biosample.rnais',
        'replicates.library.biosample.donor.organism',
        'replicates.library.biosample.donor.mutated_gene',
        'replicates.library.biosample.treatments',
        'replicates.library.spikeins_used',
        'replicates.library.treatments',
        'possible_controls',
        'possible_controls.target',
        'possible_controls.lab',
        'target.organism',
        'references',
    ]
    audit_inherit = [
        'original_files',
        'original_files.replicate',
        'original_files.platform',
        'target',
        'revoked_files',
        'revoked_files.replicate',
        'submitted_by',
        'lab',
        'award',
        'documents',
        'replicates.antibody',
        'replicates.antibody.characterizations',
        'replicates.antibody.targets',
        'replicates.library',
        'replicates.library.documents',
        'replicates.library.biosample',
        'replicates.library.biosample.organism',
        'replicates.library.biosample.treatments',
        'replicates.library.biosample.donor.organism',
        'replicates.library.biosample.donor',
        'replicates.library.biosample.treatments',
        'replicates.library.biosample.derived_from',
        'replicates.library.biosample.part_of',
        'replicates.library.biosample.pooled_from',
        'replicates.library.spikeins_used',
        'replicates.library.treatments',
        'target.organism',
    ]
    rev = Dataset.rev.copy()
    rev.update({
        'replicates': ('Replicate', 'experiment')
    })

    @calculated_property(condition='biosample_term_id', schema={
        "title": "Organ slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def organ_slims(self, registry, biosample_term_id):
        if biosample_term_id in registry['ontology']:
            return registry['ontology'][biosample_term_id]['organs']
        return []

    @calculated_property(condition='biosample_term_id', schema={
        "title": "System slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def system_slims(self, registry, biosample_term_id):
        if biosample_term_id in registry['ontology']:
            return registry['ontology'][biosample_term_id]['systems']
        return []

    @calculated_property(condition='biosample_term_id', schema={
        "title": "Developmental slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def developmental_slims(self, registry, biosample_term_id):
        if biosample_term_id in registry['ontology']:
            return registry['ontology'][biosample_term_id]['developmental']
        return []

    @calculated_property(condition='biosample_term_id', schema={
        "title": "Biosample synonyms",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def biosample_synonyms(self, registry, biosample_term_id):
        if biosample_term_id in registry['ontology']:
            return registry['ontology'][biosample_term_id]['synonyms']
        return []

    @calculated_property(condition='assay_term_id', schema={
        "title": "Assay synonyms",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def assay_synonyms(self, registry, assay_term_id):
        if assay_term_id in registry['ontology']:
            return registry['ontology'][assay_term_id]['synonyms'] + [
                registry['ontology'][assay_term_id]['name'],
            ]
        return []

    @calculated_property(condition='date_released', schema={
        "title": "Month released",
        "type": "string",
    })
    def month_released(self, date_released):
        return datetime.datetime.strptime(date_released, '%Y-%m-%d').strftime('%B, %Y')

    @calculated_property(schema={
        "title": "Replicates",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Replicate.experiment",
        },
    })
    def replicates(self, request, replicates):
        return paths_filtered_by_status(request, replicates)

    @calculated_property(schema={
        "title": "Replication type",
        "description":"Calculated field for experiment object that indicates the biological replicates type",
        "type": "array",
        "enum": [
            "anisogenic, sex-matched",
            "anisogenic, age-matched",
            "anisogenic, sex-matched age-matched",
            "anisogenic",
            "isogenic",
            "anisogenic technical replicates"
        ]
    })
    def replication_type(self, request, replicates=None):
        bio_tech_biosample_dict = {}
        
        for x in replicates:
            replicateObject = request.embed(x, '@@object')
            
            biol_rep_num = replicateObject['biological_replicate_number']
            tech_rep_num = replicateObject['technical_replicate_number']        
            if 'library' in replicateObject:
                libraryObject = request.embed(replicateObject['library'], '@@object')
                if 'biosample' in libraryObject:
                    biosampleObject = request.embed(libraryObject['biosample'], '@@object')
                    #######################################################################################
                    # VERY IMPORTANT CONDITION, ASIDE THE FACT OF REPLICATES WITH NO LIBRARIES ASSOCIATED #
                    # NOT INCLUDING IN THE CALCULATED VALUE REPLICATES WITHOUT AGE AND SEX                #
                    # SHOULD ADD AUDIT FOR THAT                                                           #
                    #######################################################################################
                    if 'age' in biosampleObject and 'sex' in biosampleObject:
                        if not biol_rep_num in bio_tech_biosample_dict:
                            bio_tech_biosample_dict[biol_rep_num]={}
                        bio_tech_biosample_dict[biol_rep_num][tech_rep_num]=biosampleObject

        '''
        First we have ot make sure the technical replicates are isogenic - in order to be able ot pick the representative biological replicate
        '''
        for biol_rep_key in bio_tech_biosample_dict.keys():
            donorsList = []
            for tech_rep_key in bio_tech_biosample_dict[biol_rep_key].keys():
                sample = bio_tech_biosample_dict[biol_rep_key][tech_rep_key]
                if 'donor' in sample:
                    donorObject = request.embed(sample['donor'], '@@object')
                    donorsList.append(donorObject['accession'])
            if (len(donorsList)>1):
                initialDonorAccession = donorsList[0]
                for accessionNumber in donorsList:
                    if accessionNumber != initialDonorAccession:
                        #######################################################################################
                        # talk with Sricket about the return value in case of anisogenic technical replicates #
                        #######################################################################################
                        return "anisogenic technical replicates" 

        '''
        Second create a list of biological replicates representatives
        '''
        bio_reps = []
        for biol_rep_key in bio_tech_biosample_dict.keys():   
            for tech_rep_key in bio_tech_biosample_dict[biol_rep_key].keys(): 
                bio_reps.append(bio_tech_biosample_dict[biol_rep_key][tech_rep_key])
                break
        
        if len(bio_reps)==0:
            return []

        initialBiosample = bio_reps[0]
        initialDonor = request.embed(initialBiosample['donor'], '@@object')
        initialOrganism = request.embed(initialDonor['organism'], '@@object')
        initialAccession = initialDonor['accession']

        humanFlag = False
        if initialOrganism['scientific_name']=='Homo sapiens':
            humanFlag = True 


        listOfReturns =[]
        for biosample_entry in bio_reps:
            currentDonor = request.embed(biosample_entry['donor'], '@@object')
            currentAccession = currentDonor['accession']
            if currentAccession != initialAccession: # biological replicates with different donors
                
                matchedAgeFlag = False
                age_1 = initialBiosample['age']
                age_2 = biosample_entry['age'] 
                if age_1 != 'unknown' and 'age_2' != 'unknown':                    
                    age_1_units = initialBiosample['age_units']
                    age_2_units = biosample_entry['age_units']
                    if age_1_units == age_2_units and age_1 == age_2:
                        matchedAgeFlag = True

                matchedSexFlag = False
                sex_1 = initialBiosample['sex']
                sex_2 = biosample_entry['sex'] 
                if sex_1 != 'unknown' and sex_2 != 'unknown':
                    if (sex_1 == sex_2 and sex_1 != 'mixed') or (sex_1 == sex_2 and sex_1 == 'mixed' and humanFlag == False):
                        matchedSexFlag = True

                returnValue = 0
                if matchedAgeFlag==True and matchedSexFlag==True:
                    returnValue =  1 # 
                if matchedAgeFlag==True and matchedSexFlag==False:
                    returnValue =  2 # unmatched sex
                if matchedAgeFlag==False and matchedSexFlag==True:
                    returnValue =  3 # unmatched age
                if matchedAgeFlag==False and matchedSexFlag==False:
                    return "anisogenic"
                
                if returnValue != 0: 
                    if len(listOfReturns)==0:
                        listOfReturns.append(returnValue)
                    else:
                        if len(listOfReturns)>0 and returnValue not in listOfReturns:
                            listOfReturns.append(returnValue)
        
        if len(listOfReturns)>0:
            if 2 in listOfReturns and 3 in listOfReturns:
                return "anisogenic"
            else:
                if 2 in listOfReturns:
                    return "anisigenic, mathced-age"
                else:
                    if 3 in listOfReturns:
                        return "anisogenic, sex-matched"
                    else:
                        return "anisogenic, sex-matched and age-matched"
        return "isogenic"

@collection(
    name='replicates',
    acl=ALLOW_SUBMITTER_ADD,
    properties={
        'title': 'Replicates',
        'description': 'Listing of Replicates',
    })
class Replicate(Item):
    item_type = 'replicate'
    schema = load_schema('encoded:schemas/replicate.json')
    embedded = [
        'antibody',
        'experiment',
        'library',
        'library.biosample',
        'library.biosample.donor',
        'library.biosample.donor.organism',
    ]

    def unique_keys(self, properties):
        keys = super(Replicate, self).unique_keys(properties)
        value = u'{experiment}/{biological_replicate_number}/{technical_replicate_number}'.format(
            **properties)
        keys.setdefault('replicate:experiment_biological_technical', []).append(value)
        return keys

    def __ac_local_roles__(self):
        properties = self.upgrade_properties()
        root = find_root(self)
        experiment = root.get_by_uuid(properties['experiment'])
        return experiment.__ac_local_roles__()
