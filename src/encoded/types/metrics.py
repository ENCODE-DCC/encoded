from snovault import (
    collection,
    abstract_collection,
    load_schema,
)
from .base import (
    Item
)


@abstract_collection(
    name='metrics',
    properties={
        'title': 'Metrics',
        'description': 'Listing of all types of metrics.',
    })
class Metrics(Item):
    base_types = ['Metrics'] + Item.base_types
    embedded = []


@collection(
    name='rna-aggregate-metrics',
    properties={
        'title': "RNA Aggregate Metrics",
        'description': "",
    })
class RnaAggregateMetrics(Metrics):
    item_type = 'rna_aggregate_metrics'
    schema = load_schema('encoded:schemas/rna_aggregate_metrics.json')
    embedded = Metrics.embedded + []


@collection(
    name='antibody-capture-metrics',
    properties={
        'title': "Antibody Capture Metrics",
        'description': "",
    })
class AntibodyCaptureMetrics(Metrics):
    item_type = 'antibody_capture_metrics'
    schema = load_schema('encoded:schemas/antibody_capture_metrics.json')
    embedded = Metrics.embedded + []


@collection(
    name='cluster-metrics',
    properties={
        'title': "Cluster Metrics",
        'description': "",
    })
class ClusterMetrics(Metrics):
    item_type = 'cluster_metrics'
    schema = load_schema('encoded:schemas/cluster_metrics.json')
    embedded = Metrics.embedded + []


@collection(
    name='rna-metrics',
    properties={
        'title': "RNA Metrics",
        'description': "",
    })
class RnaMetrics(Metrics):
    item_type = 'rna_metrics'
    schema = load_schema('encoded:schemas/rna_metrics.json')
    embedded = Metrics.embedded + []

@collection(
    name='atac-metrics',
    properties={
        'title': "ATAC Metrics",
        'description': "",
    })
class AtacMetrics(Metrics):
    item_type = 'atac_metrics'
    schema = load_schema('encoded:schemas/atac_metrics.json')
    embedded = Metrics.embedded + []

@collection(
    name='atac-aggregate-metrics',
    properties={
        'title': "ATAC Aggregate Metrics",
        'description': "",
    })
class AtacAggregateMetrics(Metrics):
    item_type = 'atac_aggregate_metrics'
    schema = load_schema('encoded:schemas/atac_aggregate_metrics.json')
    embedded = Metrics.embedded + []
