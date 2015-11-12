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
from .shared_calculated_properties import (
    CalculatedBiosampleSlims,
    CalculatedBiosampleSynonyms,
    CalculatedAssaySynonyms
)


@collection(
    name='experiments',
    unique_key='accession',
    properties={
        'title': 'Experiments',
        'description': 'Listing of Experiments',
    })
class Experiment(Dataset, CalculatedBiosampleSlims, CalculatedBiosampleSynonyms, CalculatedAssaySynonyms):
    item_type = 'experiment'
    schema = load_schema('encoded:schemas/experiment.json')
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
        "description": "Calculated field that indicates the replication model",
        "type": "string"
    })
    def replication_type(self, request, replicates=None):
        # Compare the biosamples to see if for humans they are the same donor and for 
        # model organisms if they are sex-matched and age-matched
        biosample_dict = {}
        biosample_age_list = []
        biosample_sex_list = []
        biosample_donor_list = []

        for rep in replicates:
            replicateObject = request.embed(rep, '@@object')

            if 'library' in replicateObject:
                libraryObject = request.embed(replicateObject['library'], '@@object')
                if 'biosample' in libraryObject:
                    biosampleObject = request.embed(libraryObject['biosample'], '@@object')
                    biosample_dict[biosampleObject['accession']] = biosampleObject
                    biosample_age_list.append(biosampleObject.get('age'))
                    biosample_sex_list.append(biosampleObject.get('sex'))
                    biosample_donor_list.append(biosampleObject.get('donor'))
                    biosample_species = biosampleObject.get('organism')
                    biosample_type = biosampleObject.get('biosample_type')
                else:
                    # If I have a library without a biosample,
                    # I cannot make a call about replicate structure
                    return None
            else:
                # REPLICATES WITH NO LIBRARIES WILL BE CAUGHT BY AUDIT (TICKET 3268)
                # If I have a replicate without a library,
                # I cannot make a call about the replicate structure
                return None

        if len(biosample_dict.keys()) < 2:
            return 'unreplicated'

        if biosample_type == 'immortalized cell line':
            return 'isogenic'

        # I am assuming tech reps have the same biosample, if they do not,
        # this should generate an audit, not be caught here

        '''
        Humans and model organisms are modeled differently
        '''

        if biosample_species == '/organisms/human/':
            if None in biosample_donor_list:
                return None
            if len(set(biosample_donor_list)) == 0:
                return None
            if len(set(biosample_donor_list)) == 1:
                return 'isogenic'
            # I am not sure we handle unknown well for model organisms
            if 'unknown' in biosample_age_list:
                matchedAgeFlag = False
            if 'unknown' in biosample_sex_list:
                matchedSexFlag = False

        if len(set(biosample_age_list)) > 1:
            matchedAgeFlag = False
        elif len(set(biosample_age_list)) == 1:
            matchedAgeFlag = True
        else:
            matchedAgeFlag = False

        if len(set(biosample_sex_list)) > 1:
            matchedSexFlag = False
        elif len(set(biosample_sex_list)) == 1:
            matchedSexFlag = True
        else:
            matchedSexFlag = False

        if matchedAgeFlag and matchedSexFlag:
            if biosample_species == '/organisms/human/':
                return 'anisogenic, sex-matched and age-matched'
            elif len(set(biosample_donor_list)) == 1:
                return 'isogenic'
            else:
                return 'anisogenic, sex-matched and age-matched'
        if matchedAgeFlag and not matchedSexFlag:
            return 'anisogenic, age-matched'
        if not matchedAgeFlag and matchedSexFlag:
            return 'anisogenic, sex-matched'
        if not matchedAgeFlag and not matchedSexFlag:
            return 'anisogenic'


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
