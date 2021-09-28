import React from 'react';
import PropTypes from 'prop-types';
import { Panel, TabPanel } from '../libs/ui/panel';
import GenomeBrowser from './genome_browser';
import * as globals from './globals';
import { FacetList } from './search';
import { ASSEMBLY_DETAILS } from './vis_defines';
import {
    SearchBatchDownloadController,
    BatchDownloadActuator,
} from './batch_download';
import { svgIcon } from '../libs/svg-icons';
import QueryString from '../libs/query_string';
import { BodyMapThumbnailAndModal } from './body_map';

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
const filterFacet = (facets) => {
    const filteredFacets = facets.filter((facet) => (keepFacets.indexOf(facet.field) > -1));
    return filteredFacets;
};

// The encyclopedia page displays a table of results corresponding to a selected annotation type
const Encyclopedia = (props, context) => {
    const annotation = props.context.filters.filter((f) => f.field === 'annotation_type').map((f) => f.term).length > 0 ? props.context.filters.filter((f) => f.field === 'annotation_type').map((f) => f.term) : 'candidate Cis-Regulatory Elements';
    const assembly = props.context.filters.filter((f) => f.field === 'assembly').map((f) => f.term)[0] || 'GRCh38';
    const organism = ASSEMBLY_DETAILS[assembly].species;
    const searchBase = `?type=File&annotation_type=${annotation}&assembly=${assembly}&file_format=bigBed&file_format=bigWig`;
    const resetUrl = `?type=File&annotation_type=candidate+Cis-Regulatory+Elements&assembly=${assembly}&file_format=bigBed&file_format=bigWig`;
    // If annotation or assembly is not set in url (required) page is reloaded with defaults
    const reloadPage = props.context.filters.filter((f) => f.field === 'annotation_type').map((f) => f.term).length === 0 || props.context.filters.filter((f) => f.field === 'assembly').map((f) => f.term).length === 0;

    const defaultFileDownload = 'all';
    const encyclopediaVersion = 'current';
    const fileOptions = ['CTCF-only', 'proximal enhancer-like', 'DNase-H3K4me3', 'distal enhancer-like', 'promoter-like', 'rDHS', 'all']; // Download options for cell-type agnostic cCREs
    const [selectedFiles, setSelectedFiles] = React.useState([defaultFileDownload]);

    // Links used to generate batch download objects
    const [downloadHref, setdownloadHref] = React.useState(`type=Annotation&annotation_subtype=${defaultFileDownload}&status=released&encyclopedia_version=${encyclopediaVersion}&assembly=${assembly}`);
    const [downloadController, setDownloadController] = React.useState(null);

    const browserQuery = new QueryString(props.context['@id'].replace('File', 'Annotation').split('?')[1]);
    browserQuery.deleteKeyValue('file_format');
    const browserController = new SearchBatchDownloadController('Annotation', browserQuery);

    const newFacets = filterFacet(props.context.facets.filter((facet) => facet.field !== 'assembly'));

    const annotationCounts = {};
    annotationTypes.forEach((type) => {
        if (props.context.facets.filter((f) => f.field === 'annotation_type')[0]?.terms.filter((t) => t.key === type)[0]) {
            annotationCounts[type] = props.context.facets.filter((f) => f.field === 'annotation_type')[0].terms.filter((t) => t.key === type)[0].doc_count;
        } else {
            annotationCounts[type] = 0;
        }
    });

    // Update cell-type agnostic batch download button when download link changes
    React.useEffect(() => {
        const query = new QueryString(downloadHref);
        const controller = new SearchBatchDownloadController('Annotation', query);
        setDownloadController(controller);
    }, [downloadHref]);

    // Reset page to defaults, clearing extraneous filters
    const handleReset = () => {
        context.navigate(resetUrl);
    };

    // Set page to defaults if no annotation or assembly is defined by url
    React.useEffect(() => {
        if (reloadPage) {
            handleReset();
        }
    }, []);

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

    const handleTabClick = (tab) => {
        const query = new QueryString(props.context['@id']);
        query.replaceKeyValue('assembly', defaultAssemblyByOrganism[tab]);
        context.navigate(query.format());
    };

    // Annotation type facet is not a normal facet, at least one annotation must be selected
    // Facet filters look like radiobuttons
    const chooseAnnotationType = (type) => {
        const query = new QueryString(props.context['@id']);
        const existingAnnotations = query.getKeyValues('annotation_type');
        if (existingAnnotations.indexOf(type) > -1 && existingAnnotations.length > 1) {
            query.deleteKeyValue('annotation_type', type);
        } else if (existingAnnotations.indexOf(type) === -1) {
            query.addKeyValue('annotation_type', type);
        } else {
            query.replaceKeyValue('annotation_type', 'candidate Cis-Regulatory Elements');
        }
        context.navigate(query.format());
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
            if (clickedLink?.href) {
                const clickedHref = clickedLink.href;
                context.navigate(clickedHref);
            }
        // Reset annotation type and assembly on "Clear filters" click
        } else if (isClearFilters) {
            handleReset();
        }
    };

    if (!reloadPage) {
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
                                    <a className="encyclopedia-href" href="https://regulomedb.org/regulome-search/">
                                        <img src="/static/img/regulome.ico" alt="Regulome" />
                                        <div className="href-name">RegulomeDB</div>
                                    </a>
                                    <a className="encyclopedia-href" href="http://funseq2.gersteinlab.org/">
                                        <img src="/static/img/FunSeq2.png" alt="FunSeq2" />
                                        <div className="href-name">FunSeq2</div>
                                    </a>
                                    <a className="encyclopedia-href" href="https://pubs.broadinstitute.org/mammals/haploreg/haploreg.php">
                                        <img src="/static/img/broadinstitute.ico" alt="Haplo" />
                                        <div className="href-name">HaploReg</div>
                                    </a>
                                </div>
                            </div>
                        </div>
                        <div className="outer-tab-container">
                            <TabPanel
                                tabs={organismTabs}
                                selectedTab={organism}
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
                                        <div>There are {props.context['@graph'].length} file{props.context['@graph'].length === 1 ? '' : 's'} displayed out of {props.context.total} file{props.context.total !== 1 ? 's' : ''} that match the selected filters.</div>
                                        <Panel>
                                            <div className="file-gallery-container encyclopedia-file-gallery">
                                                <div className="file-gallery-facet-redirect" onClick={(e) => handleFacetClick(e)}>{/* eslint-disable-line */}
                                                    <button className="reset-encyclopedia" type="button" onClick={handleReset}>
                                                        Reset filters
                                                    </button>
                                                    {newFacets.length > 0 ?
                                                        <FacetList
                                                            context={props.context}
                                                            facets={newFacets}
                                                            filters={props.context.filters}
                                                            searchBase={searchBase ? `${searchBase}&` : `${searchBase}?`}
                                                            hideDocType
                                                            additionalFacet={
                                                                <>
                                                                    <div className="facet ">
                                                                        <h5>Annotation Type</h5>
                                                                        {annotationTypes.map((type) => (
                                                                            <button type="button" key={type} className="facet-term annotation-type" onClick={() => chooseAnnotationType(type)}>
                                                                                {(annotation.indexOf(type) > -1) ?
                                                                                    <span className="full-dot dot" />
                                                                                :
                                                                                    <span className="empty-dot dot" />
                                                                                }
                                                                                <div className="facet-term__item">
                                                                                    {type} ({annotationCounts[type]})
                                                                                </div>
                                                                            </button>
                                                                        ))}
                                                                    </div>
                                                                    <BodyMapThumbnailAndModal
                                                                        context={props.context}
                                                                        location={context.location_href.replace('File', 'Experiment')}
                                                                        organism={organism}
                                                                    />
                                                                </>
                                                            }
                                                        />
                                                    :
                                                        <div className="facet ">
                                                            <h5>Annotation Type</h5>
                                                            {annotationTypes.map((type) => (
                                                                <button type="button" key={type} className="facet-term annotation-type" onClick={() => chooseAnnotationType(type)}>
                                                                    {(annotation.indexOf(type) > -1) ?
                                                                        <span className="full-dot dot" />
                                                                    :
                                                                        <span className="empty-dot dot" />
                                                                    }
                                                                    <div className="facet-term__item">
                                                                        {type} ({annotationCounts[type]})
                                                                    </div>
                                                                </button>
                                                            ))}
                                                        </div>
                                                    }
                                                </div>
                                                {(props.context['@graph'].length > 0) ?
                                                    <div className="file-gallery-tab-bar">
                                                        <GenomeBrowser
                                                            files={props.context['@graph']}
                                                            label="cart"
                                                            expanded
                                                            assembly={assembly}
                                                            annotation="V29"
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
    }
    return null;
};

Encyclopedia.propTypes = {
    context: PropTypes.object.isRequired, // Summary search result object
};

Encyclopedia.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    fetch: PropTypes.func,
};

globals.contentViews.register(Encyclopedia, 'Encyclopedia');
