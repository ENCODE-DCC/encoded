import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import url from 'url';
import { Panel, TabPanel } from '../libs/ui/panel';
import GenomeBrowser from './genome_browser';
import * as globals from './globals';
import getSeriesData from './series_search.js';
import { FacetList } from './search';
import { BatchDownloadEncyclopedia } from './view_controls';
import { ASSEMBLY_DETAILS } from './vis_defines';

const organismTabs = {};
const organismTerms = ['Homo sapiens', 'Mus musculus'];
organismTerms.forEach((organismName) => {
    organismTabs[organismName] = <div id={organismName} className={`organism-button ${organismName.replace(' ', '-')}`}><img src={`/static/img/bodyMap/organisms/${organismName.replace(' ', '-')}.svg`} alt={organismName} /><span>{organismName}</span></div>;
});

const keepFacets = [
    'assembly',
    'annotation_subtype',
    'biosample_ontology.term_name',
];

const annotationTypes = [
    'candidate Cis-Regulatory Elements',
    'chromatin state',
    'representative DNase hypersensitivity sites',
    'imputation',
];

function findUpTag(el, tag) {
    while (el.parentNode) {
        el = el.parentNode;
        if (el.tagName === tag) {
            return el;
        }
    }
    return null;
}

const defaultAssembly = {
    'Homo sapiens': 'hg19',
    'Mus musculus': 'mm10',
};

const filterAssemblyFacet = (response, selectedOrganism) => {
    const newResponse = response;
    const newFacets = response.facets.filter((facet) => (keepFacets.indexOf(facet.field) > -1));
    const newnewFacets = [];
    newFacets.forEach((facet) => {
        const newFacet = facet;
        if (facet.field === 'assembly') {
            const newTerms = [];
            newFacet.terms.forEach((term) => {
                const termName = term.key.toString();
                if (ASSEMBLY_DETAILS[termName].species === selectedOrganism) {
                    newTerms.push(term);
                }
            });
            newFacet.terms = newTerms;
        }
        newnewFacets.push(newFacet);
    });
    newResponse.facets = newnewFacets;
    return newResponse;
};

// The series search page displays a table of results corresponding to a selected series
// Buttons for each series are displayed like tabs or links
const Encyclopedia = (props, context) => {
    const [selectedOrganism, setSelectedOrganism] = React.useState('Homo sapiens');
    const [pinnedFiles, setPinnedFiles] = React.useState([]);
    const [facetData, setFacetData] = React.useState([]);
    const [vizFiles, setVizFiles] = React.useState([]);
    const searchBase = url.parse(context.location_href).search || '';
    const fileOptions = ['CTCF-only', 'proximal enhancer-like', 'DNase-H3K4me3', 'distal enhancer-like', 'promoter-like', 'rDHS', 'all'];
    const [selectedFiles, setSelectedFiles] = React.useState(['all']);
    const [downloadLink, setDownloadLink] = React.useState('');
    const [annotationType, setAnnotationType] = React.useState(['candidate Cis-Regulatory Elements']);
    const [browserHref, setBrowserHref] = React.useState('');
    const [pinnedHref, setPinnedHref] = React.useState('');
    const [selectedAssembly, setAssembly] = React.useState('GRCh38');
    const encyclopediaVersion = 'ENCODE v5';

    // Select series from tab buttons
    React.useEffect(() => {
        const allHref = `?type=File&annotation_subtype=*&annotation_subtype=all&status=released&encyclopedia_version=${encyclopediaVersion}&file_format=bigBed&file_format=bigWig&assembly=${selectedAssembly}`;
        setPinnedHref(allHref);
        getSeriesData(allHref, context.fetch).then((response) => {
            if (response && response['@graph']) {
                setPinnedFiles(response['@graph']);
            }
        });
        let facetHref;
        if (annotationType.length === 1) {
            facetHref = `?type=File&annotation_type=${annotationType}&status=released&encyclopedia_version=${encyclopediaVersion}&file_format=bigBed&file_format=bigWig&assembly=${selectedAssembly}`;
        } else {
            facetHref = `?type=File&annotation_type=${annotationType.join('&annotation_type=')}&status=released&encyclopedia_version=${encyclopediaVersion}&file_format=bigBed&file_format=bigWig&assembly=${selectedAssembly}`;
        }
        setBrowserHref(facetHref);
        getSeriesData(facetHref, context.fetch).then((response) => {
            if (response) {
                const newResponse = filterAssemblyFacet(response, selectedOrganism);
                setFacetData(newResponse);
            }
        });
    }, [selectedOrganism, annotationType, context.fetch]);

    React.useEffect(() => {
        if (facetData && facetData['@graph']) {
            let newFiles = [...pinnedFiles, ...facetData['@graph']];
            newFiles = _.uniq(newFiles, (file) => file['@id']);
            setVizFiles(newFiles);
        } else {
            setVizFiles(pinnedFiles);
        }
    }, [facetData, pinnedFiles]);

    React.useEffect(() => {
        // re-generate download link
        let newLink = '';
        if (selectedFiles.length < 2) {
            newLink = `type=Annotation&annotation_subtype=${selectedFiles[0]}&status=released&encyclopedia_version=${encyclopediaVersion}&assembly=${selectedAssembly}`;
        } else {
            newLink = `type=Annotation&annotation_subtype=${selectedFiles.join('&annotation_subtype=')}&status=released&encyclopedia_version=${encyclopediaVersion}&assembly=${selectedAssembly}`;
        }
        setDownloadLink(newLink);
    });

    const changeDownloadLink = (input) => {
        let newFiles = [];
        if (selectedFiles.indexOf(input) === -1) {
            newFiles = [...selectedFiles, input];
        } else {
            newFiles = selectedFiles.filter((file) => file !== input);
        }
        setSelectedFiles(newFiles);
        let newLink = '';
        if (newFiles.length < 2) {
            newLink = `type=Annotation&annotation_subtype=${newFiles[0]}&status=released&encyclopedia_version=${encyclopediaVersion}&assembly=${selectedAssembly}`;
        } else {
            newLink = `type=Annotation&annotation_subtype=${newFiles.join('&annotation_subtype=')}&status=released&encyclopedia_version=${encyclopediaVersion}&assembly=${selectedAssembly}`;
        }
        setDownloadLink(newLink);
    };

    const handleTabClick = (tab) => {
        setSelectedOrganism(tab);
        setAssembly(defaultAssembly[tab]);

        // re-generate download link
        let newLink = '';
        if (selectedFiles.length < 2) {
            newLink = `type=Annotation&annotation_subtype=${selectedFiles[0]}&status=released&encyclopedia_version=${encyclopediaVersion}&assembly=${selectedAssembly}`;
        } else {
            newLink = `type=Annotation&annotation_subtype=${selectedFiles.join('&annotation_subtype=')}&status=released&encyclopedia_version=${encyclopediaVersion}&assembly=${selectedAssembly}`;
        }
        setDownloadLink(newLink);
    };

    let canDownload = false;
    if (selectedFiles.length > 0) {
        canDownload = true;
    }

    const onFilter = () => {
        console.log('filter');
    };

    const chooseAnnotationType = (type) => {
        let newAnnotationType = annotationType;
        if (annotationType.indexOf(type) > -1 && annotationType.length > 1) {
            newAnnotationType = annotationType.filter((annotation) => annotation !== type);
        } else if (annotationType.indexOf(type) === -1) {
            newAnnotationType = [...annotationType, type];
        }
        setAnnotationType(newAnnotationType);
    };

    const handleFacetClick = (e) => {
        e.preventDefault();
        const clickedLink = findUpTag(e.target, 'A');
        if (clickedLink && clickedLink.href) {
            setBrowserHref(clickedLink.href);
            getSeriesData(clickedLink.href, context.fetch).then((response) => {
                if (response) {
                    const newResponse = filterAssemblyFacet(response, selectedOrganism);
                    setFacetData(newResponse);
                }
            });
        } else if (e.target.innerText === 'Clear Filters ') {
            const allHref = `?type=File&annotation_subtype=*&annotation_subtype=all&status=released&encyclopedia_version=${encyclopediaVersion}&file_format=bigBed&file_format=bigWig&assembly=${selectedAssembly}`;
            setPinnedHref(allHref);
            getSeriesData(allHref, context.fetch).then((response) => {
                if (response && response['@graph']) {
                    setPinnedFiles(response['@graph']);
                }
            });
            let facetHref;
            if (annotationType.length === 1) {
                facetHref = `?type=File&annotation_type=${annotationType}&status=released&encyclopedia_version=${encyclopediaVersion}&file_format=bigBed&file_format=bigWig&assembly=${selectedAssembly}`;
            } else {
                facetHref = `?type=File&annotation_type=${annotationType.join('&annotation_type=')}&status=released&encyclopedia_version=${encyclopediaVersion}&file_format=bigBed&file_format=bigWig&assembly=${selectedAssembly}`;
            }
            setBrowserHref(facetHref);
            getSeriesData(facetHref, context.fetch).then((response) => {
                if (response) {
                    const newResponse = filterAssemblyFacet(response, selectedOrganism);
                    setFacetData(newResponse);
                }
            });
        }
    };

    return (
        <div className="layout">
            <div className="layout__block layout__block--100">
                <div className="block series-search">
                    <h1>{props.context.title}</h1>
                    <div><span className="encyclopedia-badge">{encyclopediaVersion}</span></div>
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
                                    <div className="download-line">
                                        <BatchDownloadEncyclopedia
                                            queryString={downloadLink}
                                            modalText={!canDownload ? <div>Please select annotation files to download</div> : null}
                                            canDownload={canDownload}
                                            additionalContent={
                                                <div className="download-selections">
                                                    {fileOptions.map((download) => <label className="download-checkbox"><input type="checkbox" name="checkbox" value={download} onChange={() => changeDownloadLink(download)} checked={(selectedFiles.indexOf(download) > -1)} />{download}</label>)}
                                                </div>
                                            }
                                        />
                                        <span>{`Download ${selectedOrganism === 'Homo sapiens' ? 'human' : 'mouse'} cCREs`}</span>
                                    </div>
                                    <div className="download-line">
                                        <BatchDownloadEncyclopedia
                                            queryString={browserHref.replace('File', 'Annotation').replace('?', '')}
                                            modalText={null}
                                            canDownload
                                        />
                                        <span>Download selected annotations</span>
                                    </div>
                                    <hr />
                                </div>
                                <div className="series-wrapper">
                                    <Panel>
                                        <div className="file-gallery-container">
                                            {(facetData && facetData.facets && facetData.facets.length > 0) ?
                                                <div className="file-gallery-facets" onClick={(e) => handleFacetClick(e)} role="button">
                                                    <FacetList
                                                        context={facetData}
                                                        facets={facetData.facets}
                                                        filters={facetData.filters}
                                                        searchBase={searchBase ? `${searchBase}&` : `${searchBase}?`}
                                                        onFilter={onFilter}
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
                                                            </>
                                                        }
                                                    />
                                                </div>
                                            : null}
                                            {(vizFiles && vizFiles.length > 1) ?
                                                <div className="file-gallery-tab-bar">
                                                    <GenomeBrowser
                                                        files={vizFiles}
                                                        label="cart"
                                                        expanded
                                                        assembly={selectedAssembly}
                                                        annotation="V33"
                                                        displaySort
                                                    />
                                                </div>
                                            : null}
                                        </div>
                                    </Panel>
                                </div>
                            </div>
                        </TabPanel>
                        <div>download link: {downloadLink}</div>
                        <div>pinned file link: {pinnedHref}</div>
                        <div>other browser files link: {browserHref}</div>
                    </div>
                </div>
            </div>
        </div>
    );
};

// {sortedKeys.map((item) => (
//     <button type="button" className={`facet-term-${item.replace(/\s/g, '')}-${currentTab} facet-term${selectedObj[item] ? ' selected' : ''}`} onClick={() => filterFiles(item, facetKey)} key={item}>
//         {facetTitle === 'Assembly' ?
//             <i className={`${selectedObj[item] ? 'icon icon-circle' : 'icon icon-circle-o'}`} />
//         : null}
//         <div className="facet-term__item">
//             <div className="facet-term__text">
//                 <span>{item}</span>
//             </div>
//             { (facetTitle !== 'Assembly') ?
//                 <div>
//                     <div className="facet-term__count">{facetObject[item]}</div>
//                     <div className="facet-term__bar" style={{ width: `${Math.ceil((facetObject[item] / objSum) * 100)}%` }} />
//                 </div>
//             : null}
//         </div>
//     </button>
// ))}

// facets={facetData.facets.filter((facet) => (keepFacets.indexOf(facet.field) > -1))}
// bodyMap={facetData.facets.map((facet) => facet.field).indexOf('biosample_ontology.term_name') > -1}

Encyclopedia.propTypes = {
    context: PropTypes.object.isRequired,
};

Encyclopedia.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    fetch: PropTypes.func,
};

globals.contentViews.register(Encyclopedia, 'Encyclopedia');
