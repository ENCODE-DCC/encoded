from collections import OrderedDict


# All series subtypes allowed to download files
METADATA_SERIES_TYPES = [
    'AggregateSeries',
    'DifferentiationSeries',
    'DiseaseSeries',
    'FunctionalCharacterizationSeries',
    'GeneSilencingSeries',
    'MatchedSet',
    'MultiomicsSeries',
    'OrganismDevelopmentSeries',
    'ReferenceEpigenome',
    'SingleCellRnaSeries',
    'TreatmentConcentrationSeries',
    'TreatmentTimeSeries',
]


METADATA_ALLOWED_TYPES = [
    'Experiment',
    'Annotation',
    'FunctionalCharacterizationExperiment',
    'Reference',
    'Project',
    'UcscBrowserComposite',
    'PublicationData',
    'Analysis',
] + METADATA_SERIES_TYPES


METADATA_COLUMN_TO_FIELDS_MAPPING = OrderedDict(
    [
        ('File accession', ['files.title']),
        ('File format', ['files.file_type']),
        ('File type', ['files.file_format']),
        ('File format type', ['files.file_format_type']),
        ('Output type', ['files.output_type']),
        ('File assembly', ['files.assembly']),
        ('Experiment accession', ['accession']),
        ('Assay', ['assay_title']),
        ('Donor(s)', ['files.donors']),
        ('Biosample term id', ['biosample_ontology.term_id']),
        ('Biosample term name', ['biosample_ontology.term_name']),
        ('Biosample type', ['biosample_ontology.classification']),
        ('Biosample organism', ['replicates.library.biosample.organism.scientific_name']),
        ('Biosample treatments', ['replicates.library.biosample.treatments.treatment_term_name']),
        (
            'Biosample treatments amount',
            [
                'replicates.library.biosample.treatments.amount',
                'replicates.library.biosample.treatments.amount_units'
            ]
        ),
        (
            'Biosample treatments duration',
            [
                'replicates.library.biosample.treatments.duration',
                'replicates.library.biosample.treatments.duration_units'
            ]
        ),
        ('Biosample genetic modifications methods', ['replicates.library.biosample.applied_modifications.method']),
        ('Biosample genetic modifications categories', ['replicates.library.biosample.applied_modifications.category']),                                   
        ('Biosample genetic modifications targets', ['replicates.library.biosample.applied_modifications.modified_site_by_target_id']),                                   
        ('Biosample genetic modifications gene targets', ['replicates.library.biosample.applied_modifications.modified_site_by_gene_id']),
        (
            'Biosample genetic modifications site coordinates', [
                'replicates.library.biosample.applied_modifications.modified_site_by_coordinates.assembly',
                'replicates.library.biosample.applied_modifications.modified_site_by_coordinates.chromosome',
                'replicates.library.biosample.applied_modifications.modified_site_by_coordinates.start',
                'replicates.library.biosample.applied_modifications.modified_site_by_coordinates.end'
            ]
        ),
        ('Biosample genetic modifications zygosity', ['replicates.library.biosample.applied_modifications.zygosity']), 
        ('Experiment target', ['target.name']),
        ('Library made from', ['replicates.library.nucleic_acid_term_name']),
        ('Library depleted in', ['replicates.library.depleted_in_term_name']),
        ('Library extraction method', ['replicates.library.extraction_method']),
        ('Library lysis method', ['replicates.library.lysis_method']),
        ('Library crosslinking method', ['replicates.library.crosslinking_method']),
        ('Library strand specific', ['replicates.library.strand_specificity']),
        ('Experiment date released', ['date_released']),
        ('Project', ['award.project']),
        (
            'RBNS protein concentration', [
                'files.replicate.rbns_protein_concentration',
                'files.replicate.rbns_protein_concentration_units'
            ]
        ),
        ('Library fragmentation method', ['replicates.library.fragmentation_methods']),
        ('Library size range', ['replicates.library.size_range']),
        ('Biological replicate(s)', ['files.biological_replicates']),
        ('Technical replicate(s)', ['files.technical_replicates']),
        ('Read length', ['files.read_length']),
        ('Mapped read length', ['files.mapped_read_length']),
        ('Run type', ['files.run_type']),
        ('Paired end', ['files.paired_end']),
        ('Paired with', ['files.paired_with']),
        ('Index of', ['files.index_of']),
        ('Derived from', ['files.derived_from']),
        ('Size', ['files.file_size']),
        ('Lab', ['files.lab.title']),
        ('md5sum', ['files.md5sum']),
        ('dbxrefs', ['files.dbxrefs']),
        ('File download URL', ['files.href']),
        ('Genome annotation', ['files.genome_annotation']),
        ('Platform', ['files.platform.title']),
        ('Controlled by', ['files.controlled_by']),
        ('File Status', ['files.status']),
        ('No File Available', ['files.no_file_available']),
        ('Restricted', ['files.restricted']),
        ('s3_uri', ['files.s3_uri']),
        ('File analysis title', ['files.analyses.title']),
        ('File analysis status', ['files.analyses.status']),
    ]
)


METADATA_AUDIT_TO_AUDIT_COLUMN_MAPPING = [
    ('WARNING', 'Audit WARNING'),
    ('NOT_COMPLIANT', 'Audit NOT_COMPLIANT'),
    ('ERROR', 'Audit ERROR'),
]


ANNOTATION_METADATA_COLUMN_TO_FIELDS_MAPPING = OrderedDict(
    [
        ('File accession', ['files.title']),
        ('File format', ['files.file_type']),
        ('Output type', ['files.output_type']),
        ('Assay term name', ['files.assay_term_name']),
        ('Dataset accession', ['accession']),
        ('Annotation type', ['annotation_type']),
        ('Software used', ['software_used.software.title']),
        ('Encyclopedia Version', ['encyclopedia_version']),
        ('Biosample term id', ['biosample_ontology.term_id']),
        ('Biosample term name', ['biosample_ontology.term_name']),
        ('Biosample type', ['biosample_ontology.classification']),
        ('Life stage', ['relevant_life_stage']),
        ('Age', ['relevant_timepoint']),
        ('Age units', ['relevant_timepoint_units']),
        ('Organism', ['organism.scientific_name']),
        ('Targets', ['targets.name']),
        ('Dataset date released', ['date_released']),
        ('Project', ['award.project']),
        ('Lab', ['files.lab.title']),
        ('md5sum', ['files.md5sum']),
        ('dbxrefs', ['files.dbxrefs']),
        ('File download URL', ['files.href']),
        ('Assembly', ['files.assembly']),
        ('Controlled by', ['files.controlled_by']),
        ('File Status', ['files.status']),
        ('Derived from', ['files.derived_from']),
        ('S3 URL', ['files.cloud_metadata.url']),
        ('Size', ['files.file_size']),
        ('No File Available', ['files.no_file_available']),
        ('Restricted', ['files.restricted'])
    ]
)


PUBLICATION_DATA_METADATA_COLUMN_TO_FIELDS_MAPPING = OrderedDict(
    [
        ('File accession', ['files.title']),
        ('File dataset', ['files.dataset']),
        ('File type', ['files.file_format']),
        ('File format', ['files.file_type']),
        ('File output type', ['files.output_type']),
        ('Assay term name', ['files.assay_term_name']),
        ('Biosample term id', ['files.biosample_ontology.term_id']),
        ('Biosample term name', ['files.biosample_ontology.term_name']),
        ('Biosample type', ['files.biosample_ontology.classification']),
        ('File target', ['files.target.label']),
        ('Dataset accession', ['accession']),
        ('Dataset date released', ['date_released']),
        ('Project', ['award.project']),
        ('Lab', ['files.lab.title']),
        ('md5sum', ['files.md5sum']),
        ('dbxrefs', ['files.dbxrefs']),
        ('File download URL', ['files.href']),
        ('Assembly', ['files.assembly']),
        ('File status', ['files.status']),
        ('Derived from', ['files.derived_from']),
        ('S3 URL', ['files.cloud_metadata.url']),
        ('Size', ['files.file_size']),
        ('No File Available', ['files.no_file_available']),
        ('Restricted', ['files.restricted'])
    ]
)


SERIES_METADATA_COLUMN_TO_FIELDS_MAPPING = OrderedDict(
    [
        ('File accession', ['related_datasets.files.title']),
        ('File format', ['related_datasets.files.file_type']),
        ('File type', ['related_datasets.files.file_format']),
        ('File format type', ['related_datasets.files.file_format_type']),
        ('Output type', ['related_datasets.files.output_type']),
        ('File assembly', ['related_datasets.files.assembly']),
        ('Series accession', ['accession']),
        ('Biosample term id', ['biosample_ontology.term_id']),
        ('Biosample term name', ['biosample_ontology.term_name']),
        ('Biosample type', ['biosample_ontology.classification']),
        ('Experiment target', ['target.name']),
        ('Series date released', ['date_released']),
        ('Project', ['award.project']),
        ('Biological replicate(s)', ['related_datasets.files.biological_replicates']),
        ('Technical replicate(s)', ['related_datasets.files.technical_replicates']),
        ('Read length', ['related_datasets.files.read_length']),
        ('Mapped read length', ['related_datasets.files.mapped_read_length']),
        ('Run type', ['related_datasets.files.run_type']),
        ('Paired end', ['related_datasets.files.paired_end']),
        ('Paired with', ['related_datasets.files.paired_with']),
        ('Index of', ['related_datasets.files.index_of']),
        ('Derived from', ['related_datasets.files.derived_from']),
        ('Size', ['related_datasets.files.file_size']),
        ('Lab', ['related_datasets.files.lab.title']),
        ('md5sum', ['related_datasets.files.md5sum']),
        ('dbxrefs', ['related_datasets.files.dbxrefs']),
        ('File download URL', ['related_datasets.files.href']),
        ('Genome annotation', ['related_datasets.files.genome_annotation']),
        ('Platform', ['related_datasets.files.platform.title']),
        ('Controlled by', ['related_datasets.files.controlled_by']),
        ('File Status', ['related_datasets.files.status']),
        ('No File Available', ['related_datasets.files.no_file_available']),
        ('Restricted', ['related_datasets.files.restricted']),
        ('s3_uri', ['related_datasets.files.s3_uri']),
        ('File analysis title', ['related_datasets.files.analyses.title']),
        ('File analysis status', ['related_datasets.files.analyses.status']),
    ]
)


BATCH_DOWNLOAD_COLUMN_TO_FIELDS_MAPPING = OrderedDict(
    [
        ('File download URL', ['files.href']),
    ]
)


SERIES_BATCH_DOWNLOAD_COLUMN_TO_FIELDS_MAPPING = OrderedDict(
    [
        ('File download URL', ['related_datasets.files.href']),
    ]
)


METADATA_LINK = '"{}/metadata/?{}"'


AT_IDS_AS_JSON_DATA_LINK = (
    ' -X GET '
    '-H "Accept: text/tsv" '
    '-H "Content-Type: application/json" '
    '--data \'{{"elements": [{}]}}\''
)


BOOLEAN_MAP = {
    'true': True,
    'false': False
}
