/** Amount of time between last search-box input and next server request; ms */
export const SEARCH_TIMEOUT_NATIVE = 1000;
export const SEARCH_TIMEOUT_SCREEN = 200;

/** Width of gap between cards in pixels. Keep in sync with the same const in _home.scss */
export const CARD_GAP_WIDTH = 10;

/** SCREEN URL to get suggestions based on a search term */
export const SCREEN_SUGGESTIONS_URL = 'https://api.wenglab.org/screen_v13/autows/suggestions';

/** Local URLs of native and screen icons */
export const NATIVE_ICON = '/static/img/encode-circle.png';
export const SCREEN_ICON = '/static/img/screen.png';

export const SEARCH_MODE_ICON_SIZE = 32;
export const SEARCH_INPUT_ID_NATIVE = 'search-input-native';
export const SEARCH_INPUT_ID_SCREEN = 'search-input-screen';

/** URI to perform a query of types matching a search term. Add searchTerm query to the end */
export const TYPE_QUERY_URI = '/homepage-search/?limit=0';

/** Maximum number of types to retrieve frmo type query */
export const MAX_TYPE_HITS_TYPES = 10;

/**
 * Background colors for the cards. Each card's `color` property refers to one of these properties.
 * Some define the color of an individual card, while others define the colors of a section of
 * cards. Each card definition refers to one of these colors, so feel free to mix and match colors
 * within and across sections. You can also add new colors with a corresponding property name here.
 */
export const CARD_COLORS = {
    functionalGenomics: '#4960ad',
    functionalCharacterization: '#d8ab6b',
    encyclopedia: '#799170',
    collections: '#606060',
    others: '#a06060',
    documentation: '#607090',
};

/**
 * Overall format of the cards in a section. Might not apply on mobile.
 */
export const CARD_FORMATS = {
    /** Title to the left, icon to the right */
    HORIZONTAL: 'card--format-horizontal',
    /** Icon above, title below */
    VERTICAL: 'card--format-vertical',
};


// Collections to request for the native home page search.
export const HOME_COLLECTIONS = [
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
            '/search/?type=Annotation&encyclopedia_version=current&annotation_type=candidate+Cis-Regulatory+Elements&annotation_type=chromatin+state&annotation_type=representative+DNase+hypersensitivity+sites&format=json'
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
        title: 'Computational and integrative products',
        searchUrl: '/search/?type=Annotation&annotation_type!=imputation&limit=0&format=json',
        '@id': '/matrix/?type=Annotation&encyclopedia_version=ENCODE+v5&annotation_type!=imputation',
        '@type': ['DataCollection'],
    },
    {
        title: 'Imputation',
        searchUrl: '/search/?type=Annotation&encyclopedia_version=current&annotation_type=imputation&limit=0&format=json',
        '@id': '/search/?type=Annotation&encyclopedia_version=ENCODE+v5&annotation_type=imputation',
        '@type': ['DataCollection'],
    },
];
