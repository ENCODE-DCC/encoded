import React from 'react';
import PropTypes from 'prop-types';
import url from 'url';
import { Panel, PanelBody, TabPanel } from '../libs/ui/panel';
import { FacetList, ResultTableList } from './search';
import QueryString from '../libs/query_string';
import * as globals from './globals';
import GenomeBrowser from './genome_browser';
import { BodyMapThumbnailAndModal } from './body_map';
import getSeriesData from './series_search.js';

// The series search page includes the following five series
const annotationsList = {
    'Promoter-Like': {
        search: 'transcript expression',
    },
    'Enhancer-Like (proximal)': {
        search: 'enhancer predictions',
    },
    'Enhancer-Like (distal)': {
        search: 'validated enhancers',
    },
    'Chromatin Accessible': {
        search: 'chromatin state',
    },
    'CTCF-only': {
        search: 'candidate Cis-Regulatory Elements',
    },
    'H3K4me3-Accessible': {
        search: 'overlap',
    },
};

// The series search page includes the following five series
const secondaryAnnotationsList = {
    ccREs: {
        search: 'candidate Cis-Regulatory Elements',
    },
    Imputations: {
        search: 'imputation',
    },
    'Chromatin states': {
        search: 'chromatin state',
    },
};

const encyclopediaVersions = [
    'ENCODE v5',
    'ENCODE v4',
    'ENCODE v3',
    'ENCODE v2',
    'ENCODE v1',
    'Roadmap',
];

//&encyclopedia_version=${encyclopediaVersion}

// The series search page displays a table of results corresponding to a selected series
// Buttons for each series are displayed like tabs or links
const AnnotationsSearch = (props, context) => {
    // const parsedUrl = url.parse(props.context['@id']);
    // const query = new QueryString(parsedUrl.query);

    const [encyclopediaVersion, setEncyclopediaVersion] = React.useState('ENCODE v2');
    const [annotationType, setAnnotationType] = React.useState('chromatin state');
    const [annotationPanel, setAnnotationPanel] = React.useState({
        props: {},
        data: [],
        facets: [],
        total: 0,
        columns: [],
        filters: [],
        notification: '',
    });
    const [annotationHref, setAnnotationHref] = React.useState('');

    // const [annotationData, setAnnotationData] = React.useState(null);
    const [biosampleType, setBiosampleType] = React.useState('candidate Cis-Regulatory Elements');
    const [biosamplePanel, setBiosamplePanel] = React.useState({
        props: {},
        data: [],
        facets: [],
        total: 0,
        columns: [],
        filters: [],
        notification: '',
    });
    const [biosampleHref, setBiosampleHref] = React.useState('');
    // const [biosampleData, setBiosampleData] = React.useState(null);

    // const [descriptionData, setDescriptionData] = React.useState(null);
    const searchBase = url.parse(context.location_href).search || '';
    // const results = props.context['@graph'];
    const label = 'results';
    // const visualizeDisabledTitle = context.total > VISUALIZE_LIMIT ? `Filter to ${VISUALIZE_LIMIT} to visualize` : '';

    const handleTabClick = React.useCallback((series) => {
        setAnnotationType(series);
        const href = `/search/?type=Annotation&annotation_type=${series}`;
        setAnnotationHref(href);
    }, [context]);

    const handleSecondaryTabClick = React.useCallback((series) => {
        setBiosampleType(series);
        const href = `/search/?type=Annotation&annotation_type=${series}`;
        setBiosampleHref(href);
    }, [context]);

    const onFilter = (e) => {
        // const searchStr = e.currentTarget.getAttribute('href');
        // props.onChange(searchStr);
        e.stopPropagation();
        e.preventDefault();
    };

    const seriesTabs = {};
    Object.keys(annotationsList).forEach((s) => {
        seriesTabs[annotationsList[s].search] =
            <div className="tab-inner">
                {s}
            </div>;
    });

    const secondarySeriesTabs = {};
    Object.keys(secondaryAnnotationsList).forEach((s) => {
        secondarySeriesTabs[secondaryAnnotationsList[s].search] =
            <div className="tab-inner">
                {s}
            </div>;
    });

    const selectEncyclopedia = (e) => {
        setEncyclopediaVersion(e.target.value);
        const href = `?type=Annotation&encyclopedia_version=${e.target.value}&annotation_type=${annotationType}`;
        // context.navigate(href);
    };

    function redirectClick(e, panel) {
        e.stopPropagation();
        e.preventDefault();
        if (e.target.closest('a')) {
            const closestLink = e.target.closest('a');
            let linkHref = closestLink.getAttribute('href');
            console.log(linkHref);
            if (linkHref === '/annotations-search?type=Annotation') {
                if (panel === 'biosample') {
                    linkHref = `/search/?type=Annotation&annotation_type=${biosampleType}`;
                } else {
                    linkHref = `/search/?type=Annotation&annotation_type=${annotationType}`;
                }
            }
            if (panel === 'biosample') {
                setBiosampleHref(linkHref);
            } else {
                setAnnotationHref(linkHref);
            }
        }
    }

    // Select series from tab buttons
    React.useEffect(() => {
        getSeriesData(biosampleHref, context.fetch).then((response) => {
            setBiosamplePanel({
                props: response,
                data: response['@graph'],
                facets: response.facets,
                total: response.total,
                columns: response.columns,
                filters: response.filters,
                notification: response.notification,
            });
        });
    }, [biosampleHref]);

    // Select series from tab buttons
    React.useEffect(() => {
        getSeriesData(annotationHref, context.fetch).then((response) => {
            setAnnotationPanel({
                props: response,
                data: response['@graph'],
                facets: response.facets,
                total: response.total,
                columns: response.columns,
                filters: response.filters,
                notification: response.notification,
            });
        });
    }, [annotationHref]);

    React.useEffect(() => {
        if (annotationHref === '') {
            const href = `/search/?type=Annotation&annotation_type=${annotationType}`;
            setAnnotationHref(href);
        }
        if (biosampleHref === '') {
            const href = `/search/?type=Annotation&annotation_type=${biosampleType}`;
            setBiosampleHref(href);
        }
    }, []);

    return (
        <div className="layout">
            <div className="layout__block layout__block--100">
                <div className="block series-search" data-pos="0,0,0">
                    <h1>Encyclopedia search</h1>
                    <div className="encyclopedia-select-container">
                        <label htmlFor="encyclopedia-select">Encyclopedia version</label>
                        <select
                            name="encyclopedia"
                            id="encyclopedia-select"
                            value={encyclopediaVersion}
                            onChange={(e) => { selectEncyclopedia(e); }}
                        >
                            {encyclopediaVersions.map((version) => <option key={version} value={version}>{version}</option>)}
                        </select>
                    </div>
                    <h3>Here is a sub headline</h3>
                    <div className="outer-tab-container">
                        <TabPanel
                            tabs={seriesTabs}
                            selectedTab={annotationType}
                            handleTabClick={handleTabClick}
                            tabCss="tab-button"
                            tabPanelCss="tab-container series-tabs"
                        >
                            <div className="tab-body">
                                <div className="series-wrapper">
                                    <Panel>
                                        <PanelBody>
                                            <div className="annotations-results-wrapper" onClick={e => redirectClick(e, 'annotation')}>
                                                <div className="body-map-facets-container">
                                                    {annotationPanel.props ?
                                                        <FacetList
                                                            context={annotationPanel.props}
                                                            facets={annotationPanel.facets}
                                                            filters={annotationPanel.filters}
                                                            searchBase={searchBase ? `${searchBase}&` : `${searchBase}?`}
                                                            onFilter={onFilter}
                                                            hideDocType
                                                        />
                                                    : null}
                                                </div>
                                                <div className="browser-list-container">
                                                    <h4>Showing {annotationPanel.data.length} of {annotationPanel.total} {annotationPanel.label}</h4>
                                                    <GenomeBrowser
                                                        files={[]}
                                                        label="file gallery"
                                                        expanded
                                                        assembly="hg19"
                                                        displaySort
                                                    />
                                                    {annotationPanel.notification === 'Success' ?
                                                        <div className="search-results__result-list">
                                                            <ResultTableList results={annotationPanel.data} columns={annotationPanel.columns} cartControls />
                                                        </div>
                                                    :
                                                        <h4>{annotationPanel.notification}</h4>
                                                    }
                                                </div>
                                            </div>
                                        </PanelBody>
                                    </Panel>
                                </div>
                            </div>
                        </TabPanel>
                    </div>
                    <h3>Biosample-specific annotations</h3>
                    <div className="outer-tab-container">
                        <TabPanel
                            tabs={secondarySeriesTabs}
                            selectedTab={biosampleType}
                            handleTabClick={handleSecondaryTabClick}
                            tabCss="tab-button"
                            tabPanelCss="tab-container series-tabs"
                        >
                            <div className="tab-body">
                                <div className="series-wrapper">
                                    <Panel>
                                        <PanelBody>
                                            <div className="annotations-results-wrapper" onClick={e => redirectClick(e, 'biosample')}>
                                                <div className="body-map-facets-container">
                                                    {biosamplePanel.props ?
                                                        <FacetList
                                                            context={biosamplePanel.props}
                                                            facets={biosamplePanel.facets}
                                                            filters={biosamplePanel.filters}
                                                            searchBase={searchBase ? `${searchBase}&` : `${searchBase}?`}
                                                            onFilter={onFilter}
                                                            hideDocType
                                                        />
                                                    : null}
                                                </div>
                                                <div className="browser-list-container">
                                                    <h4>Showing {biosamplePanel.data.length} of {biosamplePanel.total} {biosamplePanel.label}</h4>
                                                    {biosamplePanel.notification === 'Success' ?
                                                        <div className="search-results__result-list">
                                                            <ResultTableList results={biosamplePanel.data} columns={biosamplePanel.columns} cartControls />
                                                        </div>
                                                    :
                                                        <h4>{biosamplePanel.notification}</h4>
                                                    }
                                                </div>
                                            </div>
                                        </PanelBody>
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

AnnotationsSearch.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    fetch: PropTypes.func,
};

// <BodyMapThumbnailAndModal
//     context={annotationPanel.props}
//     location={annotationHref}
//     organism="Homo sapiens"
// />

globals.contentViews.register(AnnotationsSearch, 'AnnotationsSearch');
