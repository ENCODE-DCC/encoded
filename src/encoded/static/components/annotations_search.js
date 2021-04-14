import React from 'react';
import PropTypes from 'prop-types';
import url from 'url';
import { Panel, PanelBody, TabPanel } from '../libs/ui/panel';
import { ResultTable } from './search';
import GenomeBrowser from './genome_browser';
import QueryString from '../libs/query_string';
import * as globals from './globals';
import getSeriesData from './series_search.js';

// The series search page includes the following five series
const annotationsList = {
    'promoter-like': {
        title: 'Promoter-Like',
    },
    'proximal enhancer-like': {
        title: 'Enhancer-Like (proximal)',
    },
    'distal enhancer-like': {
        title: 'Enhancer-Like (distal)',
    },
    'DNase-H3K4me3': {
        title: 'DNase-H3K4me3',
    },
    'CTCF-only': {
        title: 'candidate Cis-Regulatory Elements',
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

// The series search page displays a table of results corresponding to a selected series
// Buttons for each series are displayed like tabs or links
const AnnotationsSearch = (props, context) => {
    const parsedUrl = url.parse(props.context['@id']);
    const query = new QueryString(parsedUrl.query);
    let selectedSeries = 'promoter-like';
    if (query.getKeyValues('annotation_subtype')[0]) {
        selectedSeries = query.getKeyValues('annotation_subtype')[0];
    }
    const [vizData, setVizData] = React.useState(null);
    const searchBase = url.parse(context.location_href).search || '';

    const handleTabClick = React.useCallback((series) => {
        const href = `/annotations-search/?annotation_subtype=${series}`;
        context.navigate(href);
        // Get series description from schema
        // const seriesDescriptionHref = `/annotations-search/${annotationsList[series].schema}.json`;
        // getSeriesData(seriesDescriptionHref, context.fetch).then((response) => {
        //     setDescriptionData(response.description);
        // });
    }, [context]);

    const currentRegion = (assembly, region) => {
        let lastRegion = {};
        if (assembly && region) {
            lastRegion = {
                assembly,
                region,
            };
        }
        return lastRegion;
    };

    const annotationsTabs = {};
    Object.keys(annotationsList).forEach((s) => {
        annotationsTabs[s] =
            <div className="tab-inner">
                {annotationsList[s].title}
            </div>;
    });

    // Select series from tab buttons
    React.useEffect(() => {
        const vizHref = '/annotations-search/?annotation_subtype=all';
        getSeriesData(vizHref, context.fetch).then((response) => {
            console.log(response.description);
            setVizData(response.description);
        });
        if (!(query.getKeyValues('annotation_subtype')[0])) {
            query.addKeyValue('annotation_subtype', selectedSeries);
            const href = `?${query.format()}`;
            context.navigate(href);
        }
    }, [context, context.fetch, query, selectedSeries]);

    return (
        <div className="layout">
            <div className="layout__block layout__block--100">
                <div className="block series-search" data-pos="0,0,0">
                    {vizData ?
                        <GenomeBrowser
                            files={vizData}
                            label="file gallery"
                            expanded
                            assembly="hg19"
                            annotation="v10"
                            displaySort
                        />
                    : null}
                    <h1>Functional genomics series</h1>
                    <div className="outer-tab-container">
                        <TabPanel
                            tabs={annotationsTabs}
                            selectedTab={selectedSeries}
                            handleTabClick={handleTabClick}
                            tabCss="tab-button"
                            tabPanelCss="tab-container series-tabs"
                        >
                            <div className="tab-body">
                                <div className="series-wrapper">
                                    <Panel>
                                        <PanelBody>
                                            <ResultTable
                                                {...props}
                                                searchBase={searchBase}
                                                onChange={context.navigate}
                                                currentRegion={currentRegion}
                                                hideDocType
                                            />
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

AnnotationsSearch.propTypes = {
    context: PropTypes.object.isRequired,
};

AnnotationsSearch.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    fetch: PropTypes.func,
};

globals.contentViews.register(AnnotationsSearch, 'AnnotationsSearch');
