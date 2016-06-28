from pyramid.traversal import find_root
from snovault import (
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
        'files.derived_from.analysis_step_version.software_versions',
        'files.derived_from.analysis_step_version.software_versions.software',
        'files.derived_from.replicate',
        'files.analysis_step_version.analysis_step',
        'files.analysis_step_version.analysis_step.documents',
        'files.analysis_step_version.analysis_step.documents.award',
        'files.analysis_step_version.analysis_step.documents.lab',
        'files.analysis_step_version.analysis_step.documents.submitted_by',
        'files.analysis_step_version.analysis_step.pipelines',
        'files.analysis_step_version.analysis_step.pipelines.documents',
        'files.analysis_step_version.analysis_step.pipelines.documents.award',
        'files.analysis_step_version.analysis_step.pipelines.documents.lab',
        'files.analysis_step_version.analysis_step.pipelines.documents.submitted_by',
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
        'related_series',
        'replicates.antibody',
        'replicates.antibody.targets',
        'replicates.library',
        'replicates.library.documents.lab',
        'replicates.library.documents.submitted_by',
        'replicates.library.documents.award',
        'replicates.library.biosample.submitted_by',
        'replicates.library.biosample.source',
        'replicates.library.biosample.characterizations',
        'replicates.library.biosample.characterizations.award',
        'replicates.library.biosample.characterizations.lab',
        'replicates.library.biosample.characterizations.submitted_by',
        'replicates.library.biosample.constructs.documents',
        'replicates.library.biosample.constructs.documents.award',
        'replicates.library.biosample.constructs.documents.lab',
        'replicates.library.biosample.constructs.documents.submitted_by',
        'replicates.library.biosample.protocol_documents',
        'replicates.library.biosample.protocol_documents.award',
        'replicates.library.biosample.protocol_documents.lab',
        'replicates.library.biosample.protocol_documents.submitted_by',
        'replicates.library.biosample.talens.documents',
        'replicates.library.biosample.talens.documents.award',
        'replicates.library.biosample.talens.documents.lab',
        'replicates.library.biosample.talens.documents.submitted_by',
        'replicates.library.biosample.organism',
        'replicates.library.biosample.rnais.documents',
        'replicates.library.biosample.rnais.documents.award',
        'replicates.library.biosample.rnais.documents.lab',
        'replicates.library.biosample.rnais.documents.submitted_by',
        'replicates.library.biosample.donor',
        'replicates.library.biosample.donor.documents',
        'replicates.library.biosample.donor.documents.award',
        'replicates.library.biosample.donor.documents.lab',
        'replicates.library.biosample.donor.documents.submitted_by',
        'replicates.library.biosample.donor.characterizations',
        'replicates.library.biosample.donor.characterizations.award',
        'replicates.library.biosample.donor.characterizations.lab',
        'replicates.library.biosample.donor.characterizations.submitted_by',
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
        'replicates': ('Replicate', 'experiment'),
        'related_series': ('Series', 'related_datasets'),
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

    @calculated_property(condition='assay_term_id', schema={
        "title": "Assay type",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def assay_slims(self, registry, assay_term_id):
        if assay_term_id in registry['ontology']:
            return registry['ontology'][assay_term_id]['assay']
        return []

    @calculated_property(condition='assay_term_id', schema={
        "title": "Assay title",
        "type": "string",
    })
    def assay_title(self, request, registry, assay_term_id, assay_term_name,
                    replicates=None, target=None):
        # This is the preferred name in generate_ontology.py if exists
        if assay_term_id in registry['ontology']:
            preferred_name = registry['ontology'][assay_term_id].get('preferred_name',
                                                                     assay_term_name)
            if preferred_name == 'RNA-seq' and replicates is not None:
                for rep in replicates:
                    replicateObject = request.embed(rep, '@@object')
                    if replicateObject['status'] == 'deleted':
                        continue
                    if 'library' in replicateObject:
                        libraryObject = request.embed(replicateObject['library'], '@@object')
                        if 'size_range' in libraryObject and \
                           libraryObject['size_range'] == '<200':
                            preferred_name = 'small RNA-seq'
                            break
                        elif 'depleted_in_term_name' in libraryObject and \
                             'polyadenylated mRNA' in libraryObject['depleted_in_term_name']:
                            preferred_name = 'polyA depleted RNA-seq'
                            break
                        elif 'nucleic_acid_term_name' in libraryObject and \
                             libraryObject['nucleic_acid_term_name'] == 'polyadenylated mRNA':
                            preferred_name = 'polyA mRNA RNA-seq'
                            break
            return preferred_name or assay_term_name
        return assay_term_name

    @calculated_property(condition='assay_term_id', schema={
        "title": "Assay category",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def category_slims(self, registry, assay_term_id):
        if assay_term_id in registry['ontology']:
            return registry['ontology'][assay_term_id]['category']
        return []

    @calculated_property(condition='assay_term_id', schema={
        "title": "Assay type",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def type_slims(self, registry, assay_term_id):
        if assay_term_id in registry['ontology']:
            return registry['ontology'][assay_term_id]['types']
        return []

    @calculated_property(condition='assay_term_id', schema={
        "title": "Assay objective",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def objective_slims(self, registry, assay_term_id):
        if assay_term_id in registry['ontology']:
            return registry['ontology'][assay_term_id]['objectives']
        return []

    @calculated_property(schema={
        "title": "Related series",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Series.related_datasets",
        },
    })
    def related_series(self, request, related_series):
        return paths_filtered_by_status(request, related_series)

    @calculated_property(schema={
        "title": "Replication type",
        "description": "Calculated field that indicates the replication model",
        "type": "string"
    })
    def replication_type(self, request, replicates=None, assay_term_name=None):
        # Compare the biosamples to see if for humans they are the same donor and for
        # model organisms if they are sex-matched and age-matched
        biosample_dict = {}
        biosample_donor_list = []
        biosample_number_list = []

        for rep in replicates:
            replicateObject = request.embed(rep, '@@object')
            if replicateObject['status'] == 'deleted':
                continue
            if 'library' in replicateObject:
                libraryObject = request.embed(replicateObject['library'], '@@object')
                if 'biosample' in libraryObject:
                    biosampleObject = request.embed(libraryObject['biosample'], '@@object')
                    biosample_dict[biosampleObject['accession']] = biosampleObject
                    biosample_donor_list.append(biosampleObject.get('donor'))
                    biosample_number_list.append(replicateObject.get('biological_replicate_number'))
                    biosample_species = biosampleObject.get('organism')
                    biosample_type = biosampleObject.get('biosample_type')
                else:
                    # special treatment for "RNA Bind-n-Seq" they will be called unreplicated
                    # untill we change our mind
                    if assay_term_name == 'RNA Bind-n-Seq':
                        return 'unreplicated'
                    # If I have a library without a biosample,
                    # I cannot make a call about replicate structure
                    return None
            else:
                # REPLICATES WITH NO LIBRARIES WILL BE CAUGHT BY AUDIT (TICKET 3268)
                # If I have a replicate without a library,
                # I cannot make a call about the replicate structure
                return None

        #  exclude ENCODE2
        if (len(set(biosample_number_list)) < 2):
            return 'unreplicated'

        if biosample_type == 'immortalized cell line':
            return 'isogenic'

        # Since we are not looking for model organisms here, we likely need audits
        if biosample_species != '/organisms/human/':
            if len(set(biosample_donor_list)) == 1:
                return 'isogenic'
            else:
                return 'anisogenic'

        if len(set(biosample_donor_list)) == 0:
            return None
        if len(set(biosample_donor_list)) == 1:
            if None in biosample_donor_list:
                return None
            else:
                return 'isogenic'

        return 'anisogenic'

    matrix = {
        'y': {
            'facets': [
                'replicates.library.biosample.donor.organism.scientific_name',
                'replicates.library.biosample.biosample_type',
                'organ_slims',
                'award.project',
                'assembly',
            ],
            'group_by': ['replicates.library.biosample.biosample_type', 'biosample_term_name'],
            'label': 'Biosample',
        },
        'x': {
            'facets': [
                'assay_title',
                'assay_slims',
                'target.investigated_as',
                'month_released',
                'files.file_type',
            ],
            'group_by': 'assay_title',
            'label': 'Assay',
        },
    }


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
