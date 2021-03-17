from pyramid.traversal import find_root
from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    paths_filtered_by_status
)
from .dataset import Dataset
from .shared_calculated_properties import (
    CalculatedAssaySynonyms,
    CalculatedAssayTermID,
    CalculatedVisualize,
    CalculatedBiosampleSummary,
    CalculatedReplicates,
    CalculatedAssaySlims,
    CalculatedAssayTitle,
    CalculatedCategorySlims,
    CalculatedTypeSlims,
    CalculatedObjectiveSlims,
    CalculatedReplicationType
)

from .assay_data import assay_terms

@collection(
    name='low-throughput-single-cell-experiments',
    unique_key='accession',
    properties={
        'title': 'Low throughput single cell experiments',
        'description': 'Listing of Low Throughput Single Cell Experiments',
    })
class LowThroughputSingleCellExperiment(
    Dataset,
    CalculatedAssaySynonyms,
    CalculatedAssayTermID,
    CalculatedVisualize,
    CalculatedBiosampleSummary,
    CalculatedReplicates,
    CalculatedAssaySlims,
    CalculatedAssayTitle,
    CalculatedCategorySlims,
    CalculatedTypeSlims,
    CalculatedObjectiveSlims,
    CalculatedReplicationType):
    item_type = 'low_throughput_single_cell_experiment'
    schema = load_schema('encoded:schemas/low_throughput_single_cell_experiment.json')
    embedded = Dataset.embedded + [
        'biosample_ontology',        
        'possible_controls',
    ]
    audit_inherit = [
        'submitted_by',
        'lab',
        'award',
        'documents',
    ]
    set_status_up = [
        'original_files',
        'replicates',
        'documents',
        'target',
    ]
    set_status_down = [
        'original_files',
        'replicates',
    ]
    rev = Dataset.rev.copy()
    rev.update({
        'related_series': ('Series', 'related_datasets'),
        'replicates': ('Replicate', 'experiment'),
        'superseded_by': ('FunctionalCharacterizationExperiment', 'supersedes')
    })
