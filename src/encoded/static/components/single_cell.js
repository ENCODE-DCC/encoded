import React from 'react';
import PropTypes from 'prop-types';
import url from 'url';
import { Panel, PanelBody, TabPanel } from '../libs/ui/panel';
import { ResultTable } from './search';
import QueryString from '../libs/query_string';
import * as globals from './globals';

const SingleCellReferences = () => (
    <>
        <ul className="single-cell-references">
            <li>
                <a
                    href="/documents/6267390f-76d3-4a93-a842-f8612164a229/"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    Metadata for all unique cell types and cell states annotated from all single
                    cell experiments
                </a>
            </li>
            <li>
                <a
                    href="/documents/0f99810a-697c-4631-bc0c-def084b56042/"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    Unified metadata and cell type annotation for all QC filtered cells from all
                    single cell experiments
                </a>
            </li>
        </ul>
        <p>
            Three levels of scRNA-seq and scATAC-seq pseudobulks were constructed in a hierarchical
            manner. Level 1 pseudobulks: pools cells of the same cell type and collected from a
            single scRNA-seq sample. First-level pseudobulks serve as building blocks for the
            second and third levels of pseudobulks.
        </p>
        <ul>
            <li>
                <a
                    href="/documents/fe984cd5-e9dd-45e2-b083-a83d810dd672/"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    Metadata and quality control metrics for all scRNA-seq Level 1 pseudobulks
                </a>
            </li>
            <li>
                <a
                    href="/documents/f4f9d6b4-1b6f-49ed-8af6-c0f575a5461b/"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    Metadata and quality control metrics for all scATAC-seq Level 1 pseudobulks
                </a>
            </li>
        </ul>
        <p>
            Level 2 pseudobulks: A second-level pseudobulk pools cells from all first level
            pseudobulks that belong to the same cell type and collected from samples with the same
            species, tissue, sex, and lifestage (adult/child or embryo/postnatal).
        </p>
        <ul>
            <li>
                <a
                    href="/documents/3a5a3644-2877-426a-9df3-2cd3259449b7/"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    Metadata and quality control metrics for all scRNA-seq Level 2 pseudobulks
                </a>
            </li>
            <li>
                <a
                    href="/documents/f4f9d6b4-1b6f-49ed-8af6-c0f575a5461b/"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    Metadata and quality control metrics for all scATAC-seq Level 2 pseudobulks
                </a>
            </li>
        </ul>
        <p>
            Level 3 pseudobulks: A third-level pseudobulk pools cells from all first level
            pseudobulks that belong to the same cell type and collected from samples with the same
            species, organ, and lifestage.
        </p>
        <ul>
            <li>
                <a
                    href="/documents/3745dc72-1fae-49bd-b42d-f15bddf2edec/"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    Metadata and quality control metrics for all scRNA-seq Level 3 pseudobulks
                </a>
            </li>
            <li>
                <a
                    href="/documents/2cc13b15-181e-4cd4-ad4d-cc8fc5ea445d/"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    Metadata and quality control metrics for all scATAC-seq Level 3 pseudobulks
                </a>
            </li>
        </ul>
    </>
);

// The single cell page includes the following three groups of experiments
const singleCellList = {
    highThroughput: {
        title: 'High throughput',
        search: '?type=Experiment&assay_slims=Single+cell&status=released&replicates.library.biosample.donor.organism.scientific_name=Homo%20sapiens',
        description: 'Single cell experiments performed on hundreds to thousands of cells in parallel.',
    },
    perturbedHighThroughput: {
        title: 'Perturbed high throughput',
        search: '?type=FunctionalCharacterizationExperiment&assay_slims=Single+cell&status=released',
        description: 'Single cell experiments performed on pooled genetic perturbation screens.',
    },
    lowThroughput: {
        title: 'Low throughput',
        search: '?type=SingleCellRnaSeries&status=released',
        description: 'Single cell experiments where individual cells were isolated and investigated.',
    },
    annotations: {
        title: 'Cell type and pseudobulk annotations',
        search: '?type=Annotation&annotation_type=cell+type+annotation&status=released&annotation_type=pseudobulk',
        description: (
            <div>
                Cell type and pseudobulk annotations for high-throughput single-cell RNA-seq and ATAC-seq datasets.
                <h5>Metadata Tables for Cell Type and Pseudobulk Annotations from the ENCODE 4 Single Cell Working Group</h5>
                <SingleCellReferences />
            </div>
        ),
    },
};

// Default facets to display (others will be hidden)
// Note: audit processed data facet is suppressed specially in audit_processed_data.js
const keepFacets = [
    'assay_title',
    'assay_term_name',
    'perturbation',
    'replicates.library.biosample.treatments.treatment_term_name',
    'biosample_ontology.term_name',
    'biosample_ontology.classification',
    'biosample_ontology.term_name',
    'biosample_ontology.system_slims',
    'biosample_ontology.organ_slims',
    'organism.scientific_name',
    'lab.title',
    'replicates.library.construction_platform.term_name',
    'replicates.library.construction_method',
    'replicates.library.biosample.subcellular_fraction_term_name',
    'replicates.library.biosample.organism.scientific_name',
    'replicates.library.biosample.donor.organism.scientific_name',
    'related_datasets.replicates.library.construction_platform.term_name',
    'related_datasets.replicates.library.construction_method',
    'related_datasets.replicates.library.biosample.subcellular_fraction_term_name',
    'status',
];

// Hide facets that we don't want to display
const filterFacet = (response) => {
    const newResponse = response;
    const filteredFacets = response.facets.filter((facet) => (keepFacets.indexOf(facet.field) > -1));
    newResponse.facets = filteredFacets;
    return newResponse;
};

const getOrganismTabs = (organisms, selectedOrganism) => {
    const organismTabs = {};
    const organismTerms = ['Homo sapiens', 'Mus musculus'];
    organismTerms.forEach((organismName) => {
        organismTabs[organismName] = <div className={`organism-button ${organismName.replace(' ', '-')} ${selectedOrganism === organismName ? 'active' : ''} ${!(organisms.includes(organismName)) ? 'disabled' : ''}`}><img src={`/static/img/bodyMap/organisms/${organismName.replace(' ', '-')}.svg`} alt={organismName} /><span>{organismName}</span></div>;
    });
    return organismTabs;
};

// The single cell page displays a table of results corresponding to groupings
const SingleCell = (props, context) => {
    const parsedUrl = url.parse(props.context['@id']);
    const query = new QueryString(parsedUrl.query);
    let selectedSeries = 'highThroughput';
    if (query.getKeyValues('type')[0]) {
        const selectedType = query.getKeyValues('type')[0];
        if (selectedType === 'Experiment') {
            selectedSeries = 'highThroughput';
        } else if (selectedType === 'FunctionalCharacterizationExperiment') {
            selectedSeries = 'perturbedHighThroughput';
        } else if (selectedType === 'SingleCellRnaSeries') {
            selectedSeries = 'lowThroughput';
        } else if (selectedType === 'Annotation') {
            selectedSeries = 'annotations';
        }
    }
    const searchBase = url.parse(context.location_href).search || '';
    const descriptionData = singleCellList[selectedSeries].description;

    let bodyMapBool = false;
    let organismTabs;
    let selectedOrganism;
    let organismField;
    if (selectedSeries === 'highThroughput') {
        bodyMapBool = true;
        const organismFacet = props.context.facets.filter((f) => f.title === 'Organism')[0];
        organismField = organismFacet ? organismFacet.field : null;
        selectedOrganism = query.getKeyValues(organismField)[0];
        const organisms = organismFacet && organismFacet.terms ? organismFacet.terms.map((term) => term.key).sort() : null;
        organismTabs = organisms ? getOrganismTabs(organisms, selectedOrganism) : null;
    }

    const newProps = {};
    newProps.context = filterFacet(props.context);

    const handleTabClick = React.useCallback((series) => {
        const href = `/single-cell/${singleCellList[series].search}`;
        context.navigate(href);
    }, [context]);

    const seriesTabs = {};
    Object.keys(singleCellList).forEach((s) => {
        seriesTabs[s] =
            <div className="tab-inner">
                {singleCellList[s].title}
            </div>;
    });

    // We want to retain some filters at all times
    const clearFilters = () => {
        const href = `/single-cell/${singleCellList[selectedSeries].search}`;
        context.navigate(href);
    };

    const handleOrganismTabClick = React.useCallback((tab) => {
        const q = new QueryString(props.context['@id']);
        q.replaceKeyValue(organismField, tab);
        context.navigate(`${q.format()}`);
    }, [context]);

    return (
        <div className="layout">
            <div className="layout__block layout__block--100">
                <div className="block single-cell-page">
                    <h1>Single cell experiments</h1>
                    <div className="outer-tab-container">
                        <TabPanel
                            tabs={seriesTabs}
                            selectedTab={selectedSeries}
                            handleTabClick={handleTabClick}
                            tabCss="tab-button"
                            tabPanelCss="tab-container series-tabs"
                        >
                            <div className="tab-body">
                                <div className="tab-description">{descriptionData}</div>
                                {(selectedSeries === 'highThroughput' && organismTabs) ?
                                    <TabPanel
                                        tabs={organismTabs}
                                        selectedTab={selectedOrganism}
                                        handleTabClick={handleOrganismTabClick}
                                        tabPanelCss="matrix__data-wrapper epigenome-tabs"
                                    >
                                        <div className="matrix-facet-container">
                                            <div className="series-wrapper">
                                                <Panel>
                                                    <PanelBody>
                                                        <button className="reset-encyclopedia" type="button" onClick={() => clearFilters()}>
                                                            Reset filters
                                                        </button>
                                                        <ResultTable
                                                            {...newProps}
                                                            searchBase={searchBase}
                                                            onChange={context.navigate}
                                                            hideDocType
                                                            bodyMap={bodyMapBool}
                                                            organism={selectedOrganism}
                                                            bodyMapLocation={context.location_href}
                                                            displaySystems={false}
                                                        />
                                                    </PanelBody>
                                                </Panel>
                                            </div>
                                        </div>
                                    </TabPanel>
                                :
                                    <div className="matrix-facet-container">
                                        <div className="series-wrapper">
                                            <Panel>
                                                <PanelBody>
                                                    <button className="reset-encyclopedia" type="button" onClick={() => clearFilters()}>
                                                        Reset filters
                                                    </button>
                                                    <ResultTable
                                                        {...newProps}
                                                        searchBase={searchBase}
                                                        onChange={context.navigate}
                                                        hideDocType
                                                    />
                                                </PanelBody>
                                            </Panel>
                                        </div>
                                    </div>
                                }
                            </div>
                        </TabPanel>
                    </div>
                </div>
            </div>
        </div>
    );
};

SingleCell.propTypes = {
    context: PropTypes.object.isRequired,
};

SingleCell.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    fetch: PropTypes.func,
};

globals.contentViews.register(SingleCell, 'SingleCell');
