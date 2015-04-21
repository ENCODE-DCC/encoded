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
    embedded = [
        'applies_to'
    ]
    ref = {
        "applies_to": ('input_files', 'workflow_run', 'step_run')
    }

    @calculated_property(schema={
        "title": "Applies to",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "step_run.workflow_run.input_files",
        },
    })
    def applies_to(self, request, applies_to):
        return paths_filtered_by_status(request, applies_to)
