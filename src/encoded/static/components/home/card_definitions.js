/**
 * CARD DEFINITIONS
 *
 * Each of the following objects define the cards that appear in each section of the home page.
 * The `Home` component at the bottom of index.js contains `<CardSection>` components, each of which
 * refers to one of these objects to render the cards in that section.
 *
 * Each card-section object must include these properties:
 *     - id
 *       A unique string that identifies the section.
 *
 *     - format
 *       Defines the overall format of the cards in the section. It can have one of the following
 *       values:
 *
 *       - CARD_FORMATS.HORIZONTAL: Title to the left; icon to the right
 *       - CARD_FORMATS.VERTICAL: Title above; icon below
 *
 *       Note that the format can automatically change from these on mobile devices.
 *
 *     - columns
 *       Defines the number of columns that appear across the section. Five columns constitutes a
 *       reasonable maximum to avoid the appearance degrading on smaller devices. All sections
 *       appear as one column on mobile automatically.
 *
 *     - cards
 *       An array of objects defining each card in the section.
 *
 * Each card object must include these properties:
 *     - id
 *       A unique identifier for the card. Make sure they have unique values within a section.
 *       Different card sections can contain cards with the same id.
 *
 *     - title
 *       The title that appears on the card. Don't make these too long or you can affect the height
 *       of all the cards in its row.
 *
 *     - help
 *       A short description of the card that appears when the user clicks the question-mark icon
 *       in the card.
 *
 *     - icon
 *       An SVG icon to display on the card. Have this refer to a property in the global `icons`
 *       object. Feel free to add new SVG icons to this object for new cards.
 *
 *     - link
 *       A URI to link to when the card is clicked.
 *
 *     - color
 *       A color to use for the card's background. This must be a property in the `CARD_COLORS`
 *       object. Feel free to add new properties to this object to use new colors.
 *
 *     - useSearchTerm
 *       If true, the link in the `link` property above includes the user's current search term.
 *
 *     - displayCount
 *       If true, the number of results for the card is displayed in the card.
 *
 *     - collections
 *       An array of collection names to match collections search results to. Any collections
 *       results that match one of these collections will cause this card to highlight.
 */

// libs
import { uc } from '../../libs/constants';
// local
import { CARD_COLORS, CARD_FORMATS } from './constants';
import icons from './icons';


// Top section cards.
export const CARDS_FOR_MAIN = {
    id: 'main',
    format: CARD_FORMATS.HORIZONTAL,
    columns: 3,
    cards: [
        {
            id: 'functional-genomics',
            title: 'Functional genomics',
            help: 'Data generated by assays (such as RNA-seq, ChIP-seq, DNase-seq, ATAC-seq, WGBS, ChIA-PET, and Hi-C) investigating processes such as transcription, translation, and epigenetic regulation on a genome-wide scale.',
            icon: icons.functionalGenomics,
            link: '/matrix/?type=Experiment&control_type!=*&status=released&perturbed=false',
            color: CARD_COLORS.functionalGenomics,
            useSearchTerm: true,
            displayCount: true,
            collections: ['Functional genomics'],
        },
        {
            id: 'functional-characterization',
            title: 'Functional characterization',
            help: 'Data generated by assays (such as MPRA and CRISPR screen) investigating the relationship between DNA sequences and their regulatory activities.',
            icon: icons.functionalCharacterization,
            link: '/functional-characterization-matrix/?type=FunctionalCharacterizationExperiment&type=FunctionalCharacterizationSeries&type=TransgenicEnhancerExperiment&config=FunctionalCharacterization&datapoint=false&control_type!=*&status=released',
            color: CARD_COLORS.functionalCharacterization,
            useSearchTerm: true,
            displayCount: true,
            collections: ['Functional characterization'],
        },
        {
            id: 'encyclopedia-of-elements',
            title: 'Encyclopedia of elements',
            help: 'Data from the registry of candidate cis-Regulatory Elements (cCREs), representative DHSs, and chromatin state annotations.',
            icon: icons.encyclopedia,
            link: '/search/?type=Annotation&encyclopedia_version=current&annotation_type=candidate+Cis-Regulatory+Elements&annotation_type=chromatin+state&annotation_type=representative+DNase+hypersensitivity+sites&status=released',
            color: CARD_COLORS.encyclopedia,
            useSearchTerm: true,
            displayCount: true,
            collections: ['Encyclopedia of DNA Elements'],
        },
    ],
};

// Collection cards.
export const CARDS_FOR_COLLECTIONS = {
    id: 'collections',
    format: CARD_FORMATS.VERTICAL,
    columns: 3,
    cards: [
        {
            id: 'rush-ad',
            title: `Rush Alzheimer${uc.rsquo}s`,
            help: 'Data from multiple brain regions collected from individuals with various levels of cognitive impairment.',
            icon: icons.rushAD,
            link: '/brain-matrix/?type=Experiment&status=released&internal_tags=RushAD',
            color: CARD_COLORS.collections,
            useSearchTerm: true,
            displayCount: false,
            collections: ['Rush Alzheimer’s Disease Study'],
        },
        {
            id: 'en-tex',
            title: 'EN-TEx',
            help: 'Data generated by the collaboration of the ENCODE Consortium with the GTEx Consortium profiling approximately 30 overlapping tissues from four donors.',
            icon: icons.entex,
            link: '/entex-matrix/?type=Experiment&status=released&internal_tags=ENTEx',
            color: CARD_COLORS.collections,
            useSearchTerm: true,
            displayCount: false,
            collections: ['Epigenomes from four individuals (ENTEx)'],
        },
        {
            id: 'deeply-profiled-cell-lines',
            title: 'Deeply profiled cell lines',
            help: 'Data from cell-line samples that were deeply profiled using a set of diverse biochemical approaches.',
            icon: icons.deeplyProfiled,
            link: '/deeply-profiled-uniform-batch-matrix/?type=Experiment&control_type!=*&status=released&replicates.library.biosample.biosample_ontology.term_id=EFO:0002106&replicates.library.biosample.biosample_ontology.term_id=EFO:0001203&replicates.library.biosample.biosample_ontology.term_id=EFO:0006711&replicates.library.biosample.biosample_ontology.term_id=EFO:0002713&replicates.library.biosample.biosample_ontology.term_id=EFO:0002847&replicates.library.biosample.biosample_ontology.term_id=EFO:0002074&replicates.library.biosample.biosample_ontology.term_id=EFO:0001200&replicates.library.biosample.biosample_ontology.term_id=EFO:0009747&replicates.library.biosample.biosample_ontology.term_id=EFO:0002824&replicates.library.biosample.biosample_ontology.term_id=CL:0002327&replicates.library.biosample.biosample_ontology.term_id=CL:0002618&replicates.library.biosample.biosample_ontology.term_id=EFO:0002784&replicates.library.biosample.biosample_ontology.term_id=EFO:0001196&replicates.library.biosample.biosample_ontology.term_id=EFO:0001187&replicates.library.biosample.biosample_ontology.term_id=EFO:0002067&replicates.library.biosample.biosample_ontology.term_id=EFO:0001099&replicates.library.biosample.biosample_ontology.term_id=EFO:0002819&replicates.library.biosample.biosample_ontology.term_id=EFO:0009318&replicates.library.biosample.biosample_ontology.term_id=EFO:0001086&replicates.library.biosample.biosample_ontology.term_id=EFO:0007950&replicates.library.biosample.biosample_ontology.term_id=EFO:0003045&replicates.library.biosample.biosample_ontology.term_id=EFO:0003042&replicates.library.biosample.internal_tags=Deeply%20Profiled',
            color: CARD_COLORS.collections,
            useSearchTerm: true,
            displayCount: false,
            collections: ['Deeply-profiled cell lines'],
        },
        {
            id: 'degron',
            title: 'Protein knockdown (Degron)',
            help: 'Protein knockdown (Degron)',
            icon: icons.degron,
            link: '/degron-matrix/?type=Experiment&control_type!=*&status=released&internal_tags=Degron',
            color: CARD_COLORS.collections,
            useSearchTerm: true,
            displayCount: false,
            collections: ['Protein knockdown using the auxin-inducible degron'],
        },
        {
            id: 'computational-and-integrative-products',
            title: 'Computational and integrative products',
            help: 'Integrative computational analyses results that include, but are not limited to the annotation of genomic functional elements, registry of candidate cis-Regulatory Elements (cCREs), computational models, chromatin states, footprints, and PWMs.',
            icon: icons.computationalIntegrative,
            link: ' /matrix/?type=Annotation&annotation_type!=imputation&status=released',
            color: CARD_COLORS.collections,
            useSearchTerm: true,
            displayCount: false,
            collections: ['Computational and integrative products'],
        },
        {
            id: 'human-donor',
            title: 'Human donors',
            help: 'Data generated by high-throughput assays (such as RNA-seq, ChIP-seq, ATAC-seq and DNase-seq) for a variety of tissues and primary cells grouped by the human donors the samples originated from.',
            icon: icons.humanDonor,
            link: '/human-donor-matrix/?type=Experiment&control_type!=*&replicates.library.biosample.donor.organism.scientific_name=Homo+sapiens&biosample_ontology.classification=tissue&status=released&config=HumanDonorMatrix',
            color: CARD_COLORS.collections,
            useSearchTerm: true,
            displayCount: false,
            collections: ['Human donors'],
        },
        {
            id: 'encore',
            title: 'ENCORE',
            help: 'Data generated by the ENCORE project that aims to study protein-RNA interactions by creating a map of RNA binding proteins (RBPs) encoded in the human genome and identifying the RNA elements that the RBPs bind to.',
            icon: icons.encore,
            link: '/encore-matrix/?type=Experiment&status=released&internal_tags=ENCORE',
            color: CARD_COLORS.collections,
            useSearchTerm: true,
            displayCount: false,
            collections: ['RNA-protein interactions (ENCORE)'],
        },
        {
            id: 'southeast-stem-cell-consortium',
            title: 'Southeast Stem Cell Consortium',
            help: 'Data generated for multiple cell types differentiated from the H9 cell line provided by the Southeast Stem Cell Consortium.',
            icon: icons.southeastStemCellConsortium,
            link: '/sescc-stem-cell-matrix/?type=Experiment&internal_tags=SESCC&status=released',
            color: CARD_COLORS.collections,
            useSearchTerm: true,
            displayCount: false,
            collections: ['Stem-cell development matrix (SESCC)'],
        },
        {
            id: 'imputed-experiments',
            title: 'Imputed experiments',
            help: 'Computational model-based imputations of epigenomic experiments (such as RNA-seq and ChIP-seq) outputs.',
            icon: icons.imputedExperiments,
            link: '/search/?type=Annotation&encyclopedia_version=current&annotation_type=imputation&status=released',
            color: CARD_COLORS.collections,
            useSearchTerm: true,
            displayCount: false,
            collections: ['Imputation'],
        },
    ],
};

// Cards for other services.
export const CARDS_FOR_OTHER_DATA = {
    id: 'other-data',
    format: CARD_FORMATS.VERTICAL,
    columns: 3,
    cards: [
        {
            id: 'immune-cells',
            title: 'Immune cells',
            help: 'Collection of assays aimed at obtaining epigenomic profiles of human immune cells at different cellular fates and states (such as naive, activated, and stimulated cells).',
            icon: icons.immuneCells,
            link: '/immune-cells/?type=Experiment&replicates.library.biosample.donor.organism.scientific_name=Homo+sapiens&biosample_ontology.cell_slims=hematopoietic+cell&biosample_ontology.classification=primary+cell&control_type!=*&status!=replaced&status!=revoked&status!=archived&biosample_ontology.system_slims=immune+system&biosample_ontology.system_slims=circulatory+system&config=immune',
            color: CARD_COLORS.others,
            useSearchTerm: false,
            displayCount: false,
            collections: [],
        },
        {
            id: 'mouse-development',
            title: 'Mouse development',
            help: 'Data generated for embryonic to postnatal mouse developmental time course data across several tissues organized as reference epigenomes.',
            icon: icons.mouseDevelopment,
            link: '/mouse-development-matrix/?type=Experiment&status=released&related_series.@type=OrganismDevelopmentSeries&replicates.library.biosample.organism.scientific_name=Mus+musculus',
            color: CARD_COLORS.others,
            useSearchTerm: false,
            displayCount: false,
            collections: [],
        },
        {
            id: 'reference-epigenome',
            title: 'Reference epigenome',
            help: 'Data generated for tissues, cell lines, primary cells, and in vitro differentiated cells organized as reference epigenomes following guidelines set out by the International Human Epigenome Consortium.',
            icon: icons.referenceEpigenome,
            link: '/reference-epigenome-matrix/?type=Experiment&related_series.@type=ReferenceEpigenome&replicates.library.biosample.donor.organism.scientific_name=Homo+sapiens&status=released',
            color: CARD_COLORS.others,
            useSearchTerm: false,
            displayCount: false,
            collections: [],
        },
        {
            id: 'functional-genomic-series',
            title: 'Functional genomic series',
            help: 'Groupings of genome-wide experimental datasets that investigate a process along a trajectory, such as transcription through developmental stages or epigenetic regulation across different concentrations of an applied treatment.',
            icon: icons.functionalSeries,
            link: '/series-search/?type=OrganismDevelopmentSeries&status=released',
            color: CARD_COLORS.others,
            useSearchTerm: false,
            displayCount: false,
            collections: [],
        },
        {
            id: 'single-cell-experiments',
            title: 'Single-cell experiments',
            help: 'Data generated by assays (such as scRNA-seq, snATAC-seq) that provide sequencing results for the individual cells within a sample.',
            icon: icons.singleCell,
            link: '/single-cell/?type=Experiment&assay_slims=Single+cell&status=released&replicates.library.biosample.donor.organism.scientific_name=Homo%20sapiens',
            color: CARD_COLORS.others,
            useSearchTerm: false,
            displayCount: false,
            collections: [],
        },
        {
            id: 'rna-get',
            title: 'RNA-get',
            help: 'Tabular view to explore transcript expression levels for various genes across different tissue types.',
            icon: icons.rnaGet,
            link: '/rnaget-report/?type=RNAExpression',
            color: CARD_COLORS.others,
            useSearchTerm: false,
            displayCount: false,
            collections: [],
        },
        {
            id: 'region-search',
            title: 'Region search',
            help: 'Genome browser view to explore user-defined regions of interest and how they overlap with DNA binding regions as identified in various assays across different tissues.',
            icon: icons.regionSearch,
            link: '/region-search/',
            color: CARD_COLORS.others,
            useSearchTerm: false,
            displayCount: false,
            collections: [],
        },
        {
            id: 'encyclopedia-browser',
            title: 'Encyclopedia browser',
            help: 'Genome browser page displaying tracks from the registry of candidate cis-Regulatory Elements (cCREs), which integrates all high-quality DNase-seq and H3K4me3, H3K27ac, and CTCF ChIP-seq data produced by the ENCODE and Roadmap Epigenomics Consortia.',
            icon: icons.encyclopediaBrowser,
            link: '/encyclopedia/?type=File&status=released&annotation_type=candidate+Cis-Regulatory+Elements&assembly=GRCh38&file_format=bigBed&file_format=bigWig&encyclopedia_version=current',
            color: CARD_COLORS.others,
            useSearchTerm: false,
            displayCount: false,
            collections: [],
        },
        {
            id: 'chip-seq-experiments',
            title: 'ChIP-seq experiments',
            help: 'Genome-wide profiles of chromatin interactions with DNA-binding proteins of interest, such as transcription factors or histones.',
            icon: icons.chipSeqExperiments,
            link: '/chip-seq-matrix/?type=Experiment&replicates.library.biosample.donor.organism.scientific_name=Homo%20sapiens&assay_title=Histone%20ChIP-seq&assay_title=Mint-ChIP-seq&status=released',
            color: CARD_COLORS.others,
            useSearchTerm: false,
            displayCount: false,
            collections: [],
        },
    ],
};


// Various cards with documentation.
export const CARDS_FOR_DOCUMENTATION = {
    id: 'documentation',
    format: CARD_FORMATS.VERTICAL,
    columns: 3,
    cards: [
        {
            id: 'materials-methods',
            title: 'Materials and methods',
            help: '',
            icon: icons.methodsStandards,
            link: '/data-standards',
            color: CARD_COLORS.documentation,
            useSearchTerm: false,
            displayCount: false,
            collections: [],
        },
        {
            id: 'publications',
            title: 'Publications',
            help: '',
            icon: icons.publications,
            link: '/publications/',
            color: CARD_COLORS.documentation,
            useSearchTerm: false,
            displayCount: false,
            collections: [],
        },
        {
            id: 'getting-started',
            title: 'Getting started',
            help: '',
            icon: icons.gettingStarted,
            link: '/help/getting-started/',
            color: CARD_COLORS.documentation,
            useSearchTerm: false,
            displayCount: false,
            collections: [],
        },
    ],
};
