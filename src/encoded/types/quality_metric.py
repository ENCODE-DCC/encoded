from ..schema_utils import (
    load_schema,
)
from ..contentbase import (
    collection,
    calculated_property,
)
from .base import (
    Item,
    paths_filtered_by_status,
)


class QualityMetric(Item):
    item_type = 'quality_metric'
    base_types = ['quality_metric'] + Item.base_types


@collection(
    name='mad-cc-lrna-metrics',
    properties={
        'title': "lRNA Replicate Concordance Metrics",
        'description': 'A set of QC metrics comparing two quantificiations from (long) RNA-seq replicates',
    })
class MadCCLrnaMetric(QualityMetric):
    item_type = 'mad_cc_lrna_qc_metric'
    schema = load_schema('mad_cc_lrna_qc_metric.json')

    @calculated_property(schema={
        "title": "Applies to",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "file",
        },
    })
    def applies_to(self, request, step_run):
        workflow_run = request.embed(step_run, '@@object')['workflow_run']
        input_files = request.embed(workflow_run, '@@object')['input_files']
        return input_files