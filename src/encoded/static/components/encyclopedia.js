import React from 'react';
import PropTypes from 'prop-types';
import url from 'url';
import { Panel, TabPanel } from '../libs/ui/panel';
import GenomeBrowser from './genome_browser';
import * as globals from './globals';
import getSeriesData from './series_search.js';
import { FacetList } from './search';
import { ASSEMBLY_DETAILS } from './vis_defines';
import {
    SearchBatchDownloadController,
    BatchDownloadActuator,
} from './batch_download';
import { svgIcon } from '../libs/svg-icons';
import QueryString from '../libs/query_string';

// Generate tabs for available organisms
const organismTabs = {};
const organismTerms = ['Homo sapiens', 'Mus musculus'];
organismTerms.forEach((organismName) => {
    organismTabs[organismName] = <div id={organismName} className={`organism-button ${organismName.replace(' ', '-')}`}><img src={`/static/img/bodyMap/organisms/${organismName.replace(' ', '-')}.svg`} alt={organismName} /><span>{organismName}</span></div>;
});

// Not all annotation facets are displayed, these are the ones we want to keep
// We also display two special facets (multi-select with one selection required) for annotation type and assembly
const keepFacets = [
    'assembly', // We will not display the default assembly facet, but we want to keep the facet data in order to generate the special assembly facet
    'biochemical_inputs',
    'biosample_ontology.term_name',
    'biosample_ontology.organ_slims',
    'targets.label',
    'assay_title',
    'encyclopedia_version',
];

// Annotation types to display
const annotationTypes = [
    'candidate Cis-Regulatory Elements',
    'chromatin state',
];

// Find element or parent of element with matching tag or class name
const findElement = (el, name, key) => {
    while (el.parentNode) {
        el = el.parentNode;
        if (el[key] === name) {
            return el;
        }
    }
    return null;
};

// Default assembly for each organism
const defaultAssemblyByOrganism = {
    'Homo sapiens': 'GRCh38',
    'Mus musculus': 'mm10',
};

// Hide facets that we don't want to display
const filterFacet = (response) => {
    const newResponse = response;
    const filteredFacets = response.facets.filter((facet) => (keepFacets.indexOf(facet.field) > -1));
    newResponse.facets = filteredFacets;
    return newResponse;
};

// The encyclopedia page displays a table of results corresponding to a selected annotation type
const Encyclopedia = (props, context) => {
    const defaultOrganism = 'Homo sapiens';
    const defaultAnnotation = 'candidate Cis-Regulatory Elements';
    const defaultAssembly = 'GRCh38';
    const defaultFileDownload = 'all';
    const encyclopediaVersion = 'current';
    const searchBase = url.parse(context.location_href).search || '';
    const fileOptions = ['CTCF-only', 'proximal enhancer-like', 'DNase-H3K4me3', 'distal enhancer-like', 'promoter-like', 'rDHS', 'all']; // Download options for cell-type agnostic cCREs

    const [selectedOrganism, setSelectedOrganism] = React.useState(defaultOrganism);
    const [annotationType, setAnnotationType] = React.useState([defaultAnnotation]);
    const [selectedAssembly, setAssembly] = React.useState(defaultAssembly);
    const [assemblyList, setAssemblyList] = React.useState([defaultAssembly]);
    const [selectedFiles, setSelectedFiles] = React.useState([defaultFileDownload]);

    // Data which populates the browser
    const [facetData, setFacetData] = React.useState([]);
    const [vizFiles, setVizFiles] = React.useState([]);

    // Links used to generate batch download objects
    const [downloadHref, setdownloadHref] = React.useState(`type=Annotation&annotation_subtype=${defaultFileDownload}&status=released&encyclopedia_version=${encyclopediaVersion}&assembly=${defaultAssembly}`);
    const [downloadController, setDownloadController] = React.useState(null);
    const [browserHref, setBrowserHref] = React.useState('');
    const [browserController, setBrowserController] = React.useState(null);

    // vizFilesError is true when there are no results for selected filters
    const [vizFilesError, setVizFilesError] = React.useState(false);
    // Number of files available is displayed
    const [totalFiles, setTotalFiles] = React.useState(0);

    // Reset button resets to cCREs and the assembly matching the organism tab
    const resetPage = () => {
        const assembly = defaultAssemblyByOrganism[selectedOrganism];
        setAssembly(assembly);
        const newBrowserHref = `?type=File&annotation_type=${defaultAnnotation}&status=released&encyclopedia_version=${encyclopediaVersion}&file_format=bigBed&file_format=bigWig&assembly=${assembly}`;
        setAnnotationType(['candidate Cis-Regulatory Elements']);
        setBrowserHref(newBrowserHref);
        getSeriesData(newBrowserHref, context.fetch).then((response) => {
            if (response) {
                const newResponse = filterFacet(response, selectedOrganism);
                setFacetData(newResponse);
                setTotalFiles(newResponse.total);
                setVizFilesError(false);
            } else {
                setFacetData([]);
                setTotalFiles(0);
                setVizFilesError(true);
            }
        });
    };

    // Compile list of available assemblies from facet
    const findAvailableAssemblies = (facets) => {
        const newAssemblyList = [];
        facets.forEach((facet) => {
            if (facet.field === 'assembly') {
                facet.terms.forEach((term) => {
                    const termName = term.key.toString();
                    if (ASSEMBLY_DETAILS[termName] && ASSEMBLY_DETAILS[termName].species === selectedOrganism) {
                        newAssemblyList.push(termName);
                    }
                });
                setAssemblyList(newAssemblyList);
            }
        });
    };

    // Update browser link and facet data when organism, assembly, or annotation type changes
    React.useEffect(() => {
        let newBrowserHref;
        // If "browserHref" is already set, update assembly and annotation
        if (browserHref) {
            const query = new QueryString(browserHref);
            query.deleteKeyValue('annotation_type');
            annotationType.forEach((type) => {
                query.addKeyValue('annotation_type', type);
            });
            query.deleteKeyValue('assembly');
            query.addKeyValue('assembly', selectedAssembly);
            newBrowserHref = query.format();
        // Set browserHref if it is not set
        } else {
            newBrowserHref = `?type=File&annotation_type=${annotationType}&status=released&encyclopedia_version=${encyclopediaVersion}&file_format=bigBed&file_format=bigWig&assembly=${selectedAssembly}`;
        }
        setBrowserHref(newBrowserHref);
        getSeriesData(newBrowserHref, context.fetch).then((response) => {
            if (response) {
                const newResponse = filterFacet(response, selectedOrganism);
                findAvailableAssemblies(newResponse.facets);
                setFacetData(newResponse);
                setTotalFiles(newResponse.total);
                setVizFilesError(false);
            } else {
                setFacetData([]);
                setTotalFiles(0);
                setVizFilesError(true);
            }
        });
    }, [selectedOrganism, selectedAssembly, annotationType, context.fetch]);

    // Update visualized files when facet data is updated
    // Filter out cCRE files that are not the "cCRE, all" file
    React.useEffect(() => {
        let newFiles = [];
        if (facetData && facetData['@graph']) {
            newFiles = facetData['@graph'];
            const filteredFiles = newFiles.filter(((file) => {
                let hideFile = false;
                hideFile = file.annotation_type === 'candidate Cis-Regulatory Elements' && file.annotation_subtype && file.annotation_subtype !== 'all';
                return !hideFile;
            }));
            setVizFiles(filteredFiles);
        } else {
            setVizFiles([]);
        }
    }, [facetData]);

    // Update cell-type agnostic batch download button when download link changes
    React.useEffect(() => {
        const query = new QueryString(downloadHref);
        const controller = new SearchBatchDownloadController('Annotation', query);
        setDownloadController(controller);
    }, [downloadHref]);

    // Update browser files batch download button when browser files link changes
    React.useEffect(() => {
        const query = new QueryString(browserHref.replace('File', 'Annotation').split('?')[1]);
        query.deleteKeyValue('file_format');
        const controller = new SearchBatchDownloadController('Annotation', query);
        setBrowserController(controller);
    }, [browserHref]);

    // Update download link from selection on batch download modal
    const changedownloadHref = (input) => {
        const query = new QueryString(downloadHref);
        let newFiles;
        if (selectedFiles.indexOf(input) === -1) {
            newFiles = [...selectedFiles, input];
        } else {
            newFiles = selectedFiles.filter((file) => file !== input);
        }

        // Do not allow the user to de-select all checkboxes
        if (newFiles.length === 0) {
            return;
        }

        // Clear current selections
        query.deleteKeyValue('annotation_subtype');

        // Add selected annotation subtypes
        newFiles.forEach((type) => {
            query.addKeyValue('annotation_subtype', type.replace('rDHS', 'DHS'));
        });

        const newHref = query.format();
        setSelectedFiles(newFiles);
        setdownloadHref(newHref);
    };

    // Update assembly, organism, browser files, and download link when user clicks on tab
    const handleTabClick = (tab) => {
        setVizFiles([]);
        setSelectedOrganism(tab);
        setAssembly(defaultAssemblyByOrganism[tab]);

        // Update download link
        const query = new QueryString(downloadHref);
        query.replaceKeyValue('assembly', defaultAssemblyByOrganism[tab]);
        const newHref = query.format();
        setdownloadHref(newHref);
    };

    // Annotation type facet is not a normal facet, at least one annotation must be selected
    // Facet filters look like radiobuttons
    const chooseAnnotationType = (type) => {
        let newAnnotationType = annotationType;
        if (annotationType.indexOf(type) > -1 && annotationType.length > 1) {
            newAnnotationType = annotationType.filter((annotation) => annotation !== type);
        } else if (annotationType.indexOf(type) === -1) {
            newAnnotationType = [...annotationType, type];
        }
        setAnnotationType(newAnnotationType);
    };

    // Update browser url from facet filters
    const handleFacetClick = (e) => {
        // If clicked filter belongs to the annotation facet, clear filters, or boolean switch, we do not want to prevent default
        const isButton = findElement(e.target, 'BUTTON', 'tagName');
        const isClearFilters = e.target.innerText === 'Reset filters';
        const isBooleanSwitch = findElement(e.target, 'boolean-switch', 'className');
        if (!isButton && !isClearFilters && !isBooleanSwitch) {
            e.preventDefault();
            let clickedLink = findElement(e.target, 'A', 'tagName');
            if (!clickedLink && e.target.href) {
                clickedLink = e.target;
            }
            if (clickedLink && clickedLink.href) {
                const clickedHref = clickedLink.href;
                getSeriesData(clickedHref, context.fetch).then((response) => {
                    if (response) {
                        const newResponse = filterFacet(response, selectedOrganism);
                        setFacetData(newResponse);
                        setTotalFiles(newResponse.total);
                        setBrowserHref(clickedHref);
                    } else {
                        setFacetData([]);
                        setTotalFiles(0);
                        setVizFilesError(true);
                    }
                });
            }
        // Reset annotation type and assembly on "Clear filters" click
        } else if (isClearFilters) {
            resetPage();
        }
    };

    return (
        <div className="layout">
            <div className="layout__block layout__block--100">
                <div className="block series-search">
                    <div className="encyclopedia-info-wrapper">
                        <div className="badge-container">
                            <h1>Encyclopedia - Integrative Annotations</h1>
                            <span className="encyclopedia-badge">{encyclopediaVersion}</span>
                        </div>
                        <div className="related-links-container">
                            <div className="boder-container">
                                <div className="encyclopedia-subhead">Variant Annotation</div>
                                <div><a href="https://regulomedb.org/regulome-search/">RegulomeDB</a></div>
                                <div><a href="http://funseq2.gersteinlab.org/">FunSeq2</a></div>
                                <div><a href="https://pubs.broadinstitute.org/mammals/haploreg/haploreg.php">HaploReg</a></div>
                            </div>
                        </div>
                    </div>
                    <div className="outer-tab-container">
                        <TabPanel
                            tabs={organismTabs}
                            selectedTab={selectedOrganism}
                            handleTabClick={(tab) => handleTabClick(tab)}
                            tabCss="tab-button"
                            tabPanelCss="tab-container encyclopedia-tabs"
                        >
                            <div className="tab-body">
                                <div className="download-wrapper">
                                    <hr />
                                    {downloadController ?
                                        <div className="download-line">
                                            <BatchDownloadActuator
                                                controller={downloadController}
                                                actuator={
                                                    <button className="download-icon-button" type="button">
                                                        {svgIcon('download')}
                                                    </button>
                                                }
                                                modalContent={
                                                    <div className="download-selections">
                                                        <div className="encyclopedia-subhead">Download cell-type agnostic cCREs:</div>
                                                        {fileOptions.map((download) => <label className="download-checkbox"><input type="checkbox" name="checkbox" value={download} onChange={() => changedownloadHref(download)} checked={(selectedFiles.indexOf(download) > -1)} />{download}</label>)}
                                                    </div>
                                                }
                                            />
                                            <span>Download cell-type agnostic cCREs</span>
                                        </div>
                                    : null}
                                    {browserController ?
                                        <div className="download-line">
                                            <BatchDownloadActuator
                                                controller={browserController}
                                                actuator={
                                                    <button className="download-icon-button" type="button">
                                                        {svgIcon('download')}
                                                    </button>
                                                }
                                            />
                                            <span>Download selected annotations</span>
                                        </div>
                                    : null}
                                    <hr />
                                </div>
                                <div className="series-wrapper">
                                    <div>There are {vizFiles.length} file{vizFiles.length === 1 ? '' : 's'} displayed out of {totalFiles} file{totalFiles.length > 1 ? '' : 's'} that match the selected filters.</div>
                                    <Panel>
                                        <div className="file-gallery-container encyclopedia-file-gallery">
                                            {(facetData && facetData.facets && facetData.facets.length > 0) ?
                                                <div className="file-gallery-facet-redirect" onClick={(e) => handleFacetClick(e)}>{/* eslint-disable-line */}
                                                    <button className="reset-encyclopedia" type="button">
                                                        Reset filters
                                                    </button>
                                                    <FacetList
                                                        context={facetData}
                                                        facets={facetData.facets.filter((facet) => facet.field !== 'assembly')}
                                                        filters={facetData.filters}
                                                        searchBase={searchBase ? `${searchBase}&` : `${searchBase}?`}
                                                        hideDocType
                                                        additionalFacet={
                                                            <>
                                                                <div className="facet ">
                                                                    <h5>Annotation Type</h5>
                                                                    {annotationTypes.map((type) => (
                                                                        <button type="button" key={type} className="facet-term annotation-type" onClick={() => chooseAnnotationType(type)}>
                                                                            {(annotationType.indexOf(type) > -1) ?
                                                                                <span className="full-dot dot" />
                                                                            :
                                                                                <span className="empty-dot dot" />
                                                                            }
                                                                            <div className="facet-term__text">
                                                                                {type}
                                                                            </div>
                                                                        </button>
                                                                    ))}
                                                                </div>
                                                                <div className="facet ">
                                                                    <h5>Genome assembly</h5>
                                                                    {(assemblyList.length > 0) ?
                                                                        <>
                                                                            {assemblyList.map((assembly) => (
                                                                                <button type="button" key={assembly} className="facet-term annotation-type" onClick={() => setAssembly(assembly)}>
                                                                                    {(selectedAssembly.indexOf(assembly) > -1) ?
                                                                                        <span className="full-dot dot" />
                                                                                    :
                                                                                        <span className="empty-dot dot" />
                                                                                    }
                                                                                    <div className="facet-term__text">
                                                                                        {assembly}
                                                                                    </div>
                                                                                </button>
                                                                            ))}
                                                                        </>
                                                                    : null}
                                                                </div>
                                                            </>
                                                        }
                                                    />
                                                </div>
                                            :
                                                <div className="file-gallery-facet-redirect">
                                                    <button className="reset-encyclopedia" type="button" onClick={resetPage}>
                                                        Reset filters
                                                    </button>
                                                    <div className="box facets">
                                                        <div className="facet-list-wrapper">
                                                            <div className="facet ">
                                                                <h5>Annotation Type</h5>
                                                                {annotationTypes.map((type) => (
                                                                    <button type="button" key={type} className="facet-term annotation-type" onClick={() => chooseAnnotationType(type)}>
                                                                        {(annotationType.indexOf(type) > -1) ?
                                                                            <span className="full-dot dot" />
                                                                        :
                                                                            <span className="empty-dot dot" />
                                                                        }
                                                                        <div className="facet-term__text">
                                                                            {type}
                                                                        </div>
                                                                    </button>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            }
                                            {((vizFiles && vizFiles.length > 0) && !vizFilesError) ?
                                                <div className="file-gallery-tab-bar">
                                                    <GenomeBrowser
                                                        files={vizFiles}
                                                        label="cart"
                                                        expanded
                                                        assembly={selectedAssembly}
                                                        annotation="V33"
                                                        displaySort
                                                        sortParam={['Biosample term name', 'Annotation type']}
                                                        maxCharPerLine={30}
                                                    />
                                                </div>
                                            :
                                                <div>There are no visualizable results.</div>
                                            }
                                        </div>
                                    </Panel>
                                </div>
                            </div>
                        </TabPanel>
                    </div>
                </div>
            </div>
        </div>
    );
};

Encyclopedia.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    fetch: PropTypes.func,
};

globals.contentViews.register(Encyclopedia, 'Encyclopedia');
