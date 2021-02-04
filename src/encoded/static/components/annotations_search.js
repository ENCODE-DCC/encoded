import React from 'react';
import PropTypes from 'prop-types';
import url from 'url';
import { Panel, PanelBody, TabPanel } from '../libs/ui/panel';
import { ResultTable } from './search';
import QueryString from '../libs/query_string';
import * as globals from './globals';

// The series search page includes the following five series
const annotationsList = {
    PromoterSeries: {
        title: 'Promoter-Like',
        schema: 'organism_development_series',
        type: 'chromatin state',
    },
    EnhancerProximalSeries: {
        title: 'Enhancer-Like (proximal)',
        schema: 'treatment_time_series',
        type: 'candidate Cis-Regulatory Elements',
    },
    EnhancerDistalSeries: {
        title: 'Enhancer-Like (distal)',
        schema: 'treatment_concentration_series',
        type: 'enhancer predictions',
    },
    ChromatinSeries: {
        title: 'Chromatin Accessible',
        schema: 'replication_timing_series',
        type: 'validated enhancers',
    },
    CTCFSeries: {
        title: 'CTCF-only',
        schema: 'gene_silencing_series',
        type: 'overlap',
    },
    H3K4me3Series: {
        title: 'H3K4me3-Accessible',
        schema: 'gene_silencing_series',
        type: 'gene expression',
    },
};

// Fetch data from href
// function getSeriesData(seriesLink, fetch) {
//     return fetch(seriesLink, {
//         method: 'GET',
//         headers: {
//             Accept: 'application/json',
//         },
//     }).then((response) => {
//         if (response.ok) {
//             return response.json();
//         }
//         throw new Error('not ok');
//     }).catch((e) => {
//         console.log('OBJECT LOAD ERROR: %s', e);
//     });
// }

// The series search page displays a table of results corresponding to a selected series
// Buttons for each series are displayed like tabs or links
const AnnotationsSearch = (props, context) => {
    const parsedUrl = url.parse(props.context['@id']);
    const query = new QueryString(parsedUrl.query);
    let selectedSeries = 'chromatin state';
    if (query.getKeyValues('annotation_type')[0]) {
        selectedSeries = query.getKeyValues('annotation_type')[0];
    }
    // const [descriptionData, setDescriptionData] = React.useState(null);
    const searchBase = url.parse(context.location_href).search || '';

    const handleTabClick = React.useCallback((series) => {
        const href = `/annotations-search/?type=Annotation&annotation_type=${series.type}`;
        context.navigate(href);
        // Get series description from schema
        // const seriesDescriptionHref = `/profiles/${annotationsList[series].schema}.json`;
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

    const seriesTabs = {};
    Object.keys(annotationsList).forEach((s) => {
        seriesTabs[s] =
            <div className="tab-inner">
                {annotationsList[s].title}
            </div>;
    });

    // Select series from tab buttons
    React.useEffect(() => {
        // const seriesDescriptionHref = `/profiles/${annotationsList[selectedSeries].schema}.json`;
        // getSeriesData(seriesDescriptionHref, context.fetch).then((response) => {
        //     setDescriptionData(response.description);
        // });
        if (!(query.getKeyValues('annotation_type')[0])) {
            console.log(selectedSeries);
            query.addKeyValue('annotation_type', selectedSeries);
            const href = `?type=Annotation&${query.format()}`;
            console.log(href);
            context.navigate(href);
        }
    }, [context, context.fetch, query, selectedSeries]);

    return (
        <div className="layout">
            <div className="layout__block layout__block--100">
                <div className="block series-search" data-pos="0,0,0">
                    <h1>Functional genomics series</h1>
                    <div className="outer-tab-container">
                        <TabPanel
                            tabs={seriesTabs}
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
