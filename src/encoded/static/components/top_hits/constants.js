import {
    Query as TopHitsQuery,
    CollectionsQuery,
} from './query';
import Results, {
    CollectionResults
} from './results';


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

export const COLLECTIONS = [
    {
        title: 'Epigenomes from four individuals (ENTEx)',
        searchUrl: '/search/?type=Experiment&status=released&internal_tags=ENTEx&limit=0&format=json',
        '@id': '/entex-matrix/?type=Experiment&status=released&internal_tags=ENTEx',
        '@type': ['DataCollection'],
    },
    {
        title: 'Stem Cell Development Matrix (SESCC)',
        searchUrl: '/search/?type=Experiment&internal_tags=SESCC&limit=0&format=json',
        '@id': '/sescc-stem-cell-matrix/?type=Experiment&internal_tags=SESCC',
        '@type': ['DataCollection'],
    },
    {
        title: 'RNA-protein interactions (ENCORE)',
        searchUrl: '/search/?type=Experiment&status=released&internal_tags=ENCORE&limit=0&format=json',
        '@id': '/encore-matrix/?type=Experiment&status=released&internal_tags=ENCORE',
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
    }

]

export const COLLECTIONS_KEY = 'DataCollection'

export const queries = [
    ['dataCollections', CollectionsQuery, CollectionResults, 'Data collections'],
    ['topHits', TopHitsQuery, Results, 'Top results by type'],
];
