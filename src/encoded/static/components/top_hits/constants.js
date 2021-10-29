export const TOP_HITS_URL = '/top-hits-raw/';

export const TOP_HITS_PARAMS = (
    '&field=description' +
    '&field=accession' +
    '&field=external_accession' +
    '&field=title' +
    '&field=summary' +
    '&field=biosample_summary' +
    '&field=assay_term_name' +
    '&field=file_type' +
    '&field=status' +
    '&field=antigen_description' +
    '&field=target.label' +
    '&field=targets.label' +
    '&field=assay_title' +
    '&field=output_type' +
    '&field=replicates.library.biosample.organism.scientific_name' +
    '&field=organism.scientific_name' +
    '&field=term_name' +
    '&field=biosample_ontology.term_name' +
    '&field=classification' +
    '&field=document_type' +
    '&field=attachment.download' +
    '&field=lot_id' +
    '&field=product_id' +
    '&field=annotation_type' +
    '&field=news_excerpt' +
    '&field=abstract' +
    '&field=authors' +
    '&field=label' +
    '&field=symbol' +
    '&field=name' +
    '&field=category' +
    '&field=purpose' +
    '&field=method' +
    '&field=institute_name' +
    '&field=assay_term_names' +
    '&field=strain_name' +
    '&field=genotype' +
    '&format=json'
);

export const WHITESPACE = ' ';

export const MAX_WORDS_SHORT = 12;

export const MAX_WORDS_LONG = 12;

export const EXPERIMENT = 'Experiment';

export const FILE = 'File';

export const BIOSAMPLE = 'Biosample';

export const DONOR = 'Donor';

export const TERM_NAME = 'term_name';

export const SCIENTIFIC_NAME = 'scientific_name';

// Specifies all of the details needed for searching over data collections with a
// given user searchTerm and returning results that can be rendered by dropdown.
export const COLLECTIONS = [
    {
        title: 'Functional genomics',
        searchUrl: '/search/?type=Experiment&control_type!=*&status=released&perturbed=false&limit=0&format=json',
        '@id': '/matrix/?type=Experiment&control_type!=*&status=released&perturbed=false',
        '@type': ['DataCollection'],
    },
    {
        title: 'Functional characterization',
        searchUrl: (
            '/search/?type=FunctionalCharacterizationExperiment&type=FunctionalCharacterizationSeries' +
            '&type=TransgenicEnhancerExperiment&config=FunctionalCharacterization&datapoint=false' +
            '&control_type!=*&limit=0&format=json'
        ),
        '@id': (
            '/search/?type=FunctionalCharacterizationExperiment&type=FunctionalCharacterizationSeries' +
            '&type=TransgenicEnhancerExperiment&config=FunctionalCharacterization&datapoint=false' +
            '&control_type!=*'
        ),
        '@type': ['DataCollection'],
    },
    {
        title: 'Encyclopedia of DNA Elements',
        searchUrl: (
            '/?type=File&annotation_type=candidate+Cis-Regulatory+Elements&file_format=bigBed' +
            '&file_format=bigWig&encyclopedia_version=current&limit=0&format=json'
        ),
        '@id': '/encyclopedia/',
        '@type': ['DataCollection'],
    },
    {
        title: 'Rush Alzheimer’s Disease Study',
        searchUrl: '/search/?type=Experiment&status=released&internal_tags=RushAD&limit=0&format=json',
        '@id': '/brain-matrix/?type=Experiment&status=released&internal_tags=RushAD',
        '@type': ['DataCollection'],
    },
    {
        title: 'RNA-protein interactions (ENCORE)',
        searchUrl: '/search/?type=Experiment&status=released&internal_tags=ENCORE&limit=0&format=json',
        '@id': '/encore-matrix/?type=Experiment&status=released&internal_tags=ENCORE',
        '@type': ['DataCollection'],
    },
    {
        title: 'Stem-cell development matrix (SESCC)',
        searchUrl: '/search/?type=Experiment&internal_tags=SESCC&limit=0&format=json',
        '@id': '/sescc-stem-cell-matrix/?type=Experiment&internal_tags=SESCC',
        '@type': ['DataCollection'],
    },
    {
        title: 'Epigenomes from four individuals (ENTEx)',
        searchUrl: '/search/?type=Experiment&status=released&internal_tags=ENTEx&limit=0&format=json',
        '@id': '/entex-matrix/?type=Experiment&status=released&internal_tags=ENTEx',
        '@type': ['DataCollection'],
    },
    {
        title: 'Human reference epigenomes',
        searchUrl: (
            '/search/?type=Experiment&related_series.@type=ReferenceEpigenome' +
            '&replicates.library.biosample.donor.organism.scientific_name=Homo+sapiens&limit=0&format=json'
        ),
        '@id': (
            '/reference-epigenome-matrix/?type=Experiment&related_series.@type=ReferenceEpigenome' +
            '&replicates.library.biosample.donor.organism.scientific_name=Homo+sapiens'
        ),
        '@type': ['DataCollection'],
    },
    {
        title: 'Mouse development matrix',
        searchUrl: (
            '/search/?type=Experiment&status=released&related_series.@type=OrganismDevelopmentSeries' +
            '&replicates.library.biosample.organism.scientific_name=Mus+musculus&limit=0&format=json'
        ),
        '@id': (
            '/mouse-development-matrix/?type=Experiment&status=released&related_series.@type=OrganismDevelopmentSeries' +
            '&replicates.library.biosample.organism.scientific_name=Mus+musculus'
        ),
        '@type': ['DataCollection'],
    },
    {
        title: 'Deeply-profiled cell lines',
        searchUrl: (
            '/deeply-profiled-uniform-batch-matrix/?type=Experiment&control_type!=*&status=released' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0002106' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0001203' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0006711' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0002713' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0002847' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0002074' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0001200' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0009747' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0002824' +
            '&replicates.library.biosample.biosample_ontology.term_id=CL:0002327' +
            '&replicates.library.biosample.biosample_ontology.term_id=CL:0002618' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0002784' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0001196' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0001187' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0002067' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0001099' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0002819' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0009318' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0001086' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0007950' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0003045' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0003042' +
            '&replicates.library.biosample.internal_tags=Deeply Profiled&limit=0&format=json'
        ),
        '@id': (
            '/deeply-profiled-uniform-batch-matrix/?type=Experiment&control_type!=*&status=released' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0002106' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0001203' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0006711' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0002713' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0002847' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0002074' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0001200' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0009747' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0002824' +
            '&replicates.library.biosample.biosample_ontology.term_id=CL:0002327' +
            '&replicates.library.biosample.biosample_ontology.term_id=CL:0002618' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0002784' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0001196' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0001187' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0002067' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0001099' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0002819' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0009318' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0001086' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0007950' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0003045' +
            '&replicates.library.biosample.biosample_ontology.term_id=EFO:0003042' +
            '&replicates.library.biosample.internal_tags=Deeply Profiled'
        ),
        '@type': ['DataCollection'],
    },
    {
        title: 'Single-cell experiments',
        searchUrl: '/single-cell/?type=Experiment&assay_slims=Single+cell&status!=replaced&limit=0&format=json',
        '@id': '/single-cell/?type=Experiment&assay_slims=Single+cell&status!=replaced',
        '@type': ['DataCollection'],
    },
    {
        title: 'ChIP-seq matrix',
        searchUrl: (
            '/chip-seq-matrix/?type=Experiment&replicates.library.biosample.donor.organism.scientific_name=Homo%20sapiens' +
            '&assay_title=Histone%20ChIP-seq&assay_title=Mint-ChIP-seq&status=released&limit=0&format=json'
        ),
        '@id': (
            '/chip-seq-matrix/?type=Experiment&replicates.library.biosample.donor.organism.scientific_name=Homo%20sapiens' +
            '&assay_title=Histone%20ChIP-seq&assay_title=Mint-ChIP-seq&status=released'
        ),
        '@type': ['DataCollection'],
    },
    {
        title: 'Functional genomic series',
        searchUrl: (
            '/search/?type=OrganismDevelopmentSeries&type=TreatmentTimeSeries&type=TreatmentConcentrationSeries' +
            '&type=ReplicationTimingSeries&type=GeneSilencingSeries&type=DifferentiationSeries'
        ),
        '@id': '/series-search/',
        '@type': ['DataCollection'],
    },
    {
        title: 'Computational and integrative products',
        searchUrl: '/search/?type=Annotation&encyclopedia_version=ENCODE+v5&annotation_type!=imputation&limit=0&format=json',
        '@id': '/matrix/?type=Annotation&encyclopedia_version=ENCODE+v5&annotation_type!=imputation',
        '@type': ['DataCollection'],
    },
    {
        title: 'Imputation',
        searchUrl: '/search/?type=Annotation&encyclopedia_version=ENCODE+v5&annotation_type=imputation&limit=0&format=json',
        '@id': '/search/?type=Annotation&encyclopedia_version=ENCODE+v5&annotation_type=imputation',
        '@type': ['DataCollection'],
    },
];

export const COLLECTIONS_KEY = 'DataCollection';
