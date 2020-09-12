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
    name='aggregate-metrics',
    properties={
        'title': "Aggregate Metrics",
        'description': "",
    })
class AggregateMetrics(Metrics):
    item_type = 'aggregate_metrics'
    schema = load_schema('encoded:schemas/aggregate_metrics.json')
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
    name='gene-expression-metrics',
    properties={
        'title': "Gene Expression Metrics",
        'description': "",
    })
class GeneExpressionMetrics(Metrics):
    item_type = 'gene_expression_metrics'
    schema = load_schema('encoded:schemas/gene_expression_metrics.json')
    embedded = Metrics.embedded + []
