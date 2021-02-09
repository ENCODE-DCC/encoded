import React from 'react';
import PropTypes from 'prop-types';
import url from 'url';
import { Panel, PanelBody, TabPanel } from '../libs/ui/panel';
import { FacetList, ResultTableList } from './search';
import QueryString from '../libs/query_string';
import * as globals from './globals';
import GenomeBrowser from './genome_browser';
import { BodyMapThumbnailAndModal } from './body_map';

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


// Fetch data from href
function getSeriesData(seriesLink, fetch) {
    return fetch(seriesLink, {
        method: 'GET',
        headers: {
            Accept: 'application/json',
        },
    }).then((response) => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('not ok');
    }).catch((e) => {
        console.log('OBJECT LOAD ERROR: %s', e);
    });
}

// The series search page displays a table of results corresponding to a selected series
// Buttons for each series are displayed like tabs or links
const AnnotationsSearch = (props, context) => {
    const parsedUrl = url.parse(props.context['@id']);
    const query = new QueryString(parsedUrl.query);

    const [encyclopediaVersion, setEncyclopediaVersion] = React.useState(query.getKeyValues('encyclopedia_version')[0] || 'ENCODE v2');
    const [annotationType, setAnnotationType] = React.useState('chromatin state');
    const [annotationData, setAnnotationData] = React.useState([]);
    const [biosampleType, setBiosampleType] = React.useState('chromatin state');
    const [biosampleData, setBiosampleData] = React.useState([]);

    // const [descriptionData, setDescriptionData] = React.useState(null);
    const searchBase = url.parse(context.location_href).search || '';

    const { facets, total, columns, filters } = props.context;
    const results = props.context['@graph'];
    const label = 'results';
    // const visualizeDisabledTitle = context.total > VISUALIZE_LIMIT ? `Filter to ${VISUALIZE_LIMIT} to visualize` : '';

    const handleTabClick = React.useCallback((series) => {
        setAnnotationType(series);
        const href = `/annotations-search/?type=Annotation&encyclopedia_version=${encyclopediaVersion}&annotation_type=${series}`;
        context.navigate(href);
        // Get series description from schema
        // const seriesDescriptionHref = `/profiles/${annotationsList[series].schema}.json`;
        // getSeriesData(seriesDescriptionHref, context.fetch).then((response) => {
        //     setDescriptionData(response.description);
        // });
    }, [context]);

    const handleSecondaryTabClick = React.useCallback((series) => {
        console.log(series);
        setBiosampleType(series);
        const href = `/search/?type=Annotation&encyclopedia_version=${encyclopediaVersion}&annotation_type=${series}`;
        // context.navigate(href);
        setBiosampleData(getSeriesData(href, context.fetch));

        console.log(context.fetch);

        console.log(getSeriesData(href, context.fetch));
        // Get series description from schema
        // const seriesDescriptionHref = `/profiles/${annotationsList[series].schema}.json`;
        // getSeriesData(seriesDescriptionHref, context.fetch).then((response) => {
        //     setDescriptionData(response.description);
        // });
    }, [context]);

    const onFilter = (e) => {
        // const searchStr = e.currentTarget.getAttribute('href');
        // props.onChange(searchStr);
        e.stopPropagation();
        e.preventDefault();
    };

    // const currentRegion = (assembly, region) => {
    //     let lastRegion = {};
    //     if (assembly && region) {
    //         lastRegion = {
    //             assembly,
    //             region,
    //         };
    //     }
    //     return lastRegion;
    // };

    const seriesTabs = {};
    Object.keys(annotationsList).forEach((s) => {
        seriesTabs[s] =
            <div className="tab-inner">
                {s}
            </div>;
    });
    console.log(seriesTabs);

    const secondarySeriesTabs = {};
    Object.keys(secondaryAnnotationsList).forEach((s) => {
        secondarySeriesTabs[secondaryAnnotationsList[s].search] =
            <div className="tab-inner">
                {s}
            </div>;
    });
    console.log(secondarySeriesTabs);

    const selectEncyclopedia = (e) => {
        setEncyclopediaVersion(e.target.value);
        const href = `?type=Annotation&encyclopedia_version=${e.target.value}&annotation_type=${annotationType}`;
        context.navigate(href);
    };

    // Select series from tab buttons
    // React.useEffect(() => {
    //     // const seriesDescriptionHref = `/profiles/${annotationsList[selectedSeries].schema}.json`;
    //     // getSeriesData(seriesDescriptionHref, context.fetch).then((response) => {
    //     //     setDescriptionData(response.description);
    //     // });
    //     if (!(query.getKeyValues('annotation_type')[0])) {
    //         query.addKeyValue('annotation_type', annotationType);
    //         const href = `?type=Annotation&encyclopedia_version=${encyclopediaVersion}&${query.format()}`;
    //         console.log(href);
    //         context.navigate(href);
    //     }
    // }, [context, context.fetch, query]);

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
                                            <div className="annotations-results-wrapper">
                                                <div className="browser-list-container">
                                                    <h4>Showing {results.length} of {total} {label}</h4>
                                                    {props.context.notification === 'Success' ?
                                                        <div className="search-results__result-list">
                                                            <ResultTableList results={results} columns={columns} cartControls />
                                                        </div>
                                                    :
                                                        <h4>{context.notification}</h4>
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
                            selectedTab={annotationType}
                            handleTabClick={handleSecondaryTabClick}
                            tabCss="tab-button"
                            tabPanelCss="tab-container series-tabs"
                        >
                            <div className="tab-body">
                                <div className="series-wrapper">
                                    <Panel>
                                        <PanelBody>
                                            <div className="annotations-results-wrapper">
                                                <div className="body-map-facets-container">
                                                    <BodyMapThumbnailAndModal context={context} location={context.location_href} />
                                                    <FacetList
                                                        {...props}
                                                        facets={facets}
                                                        filters={filters}
                                                        searchBase={searchBase ? `${searchBase}&` : `${searchBase}?`}
                                                        onFilter={onFilter}
                                                        hideDocType
                                                    />
                                                </div>
                                                <div className="browser-list-container">
                                                    <h4>Showing {biosampleData.length} of {total} {label}</h4>
                                                    {props.context.notification === 'Success' ?
                                                        <div className="search-results__result-list">
                                                            <ResultTableList results={biosampleData} columns={columns} cartControls />
                                                        </div>
                                                    :
                                                        <h4>{context.notification}</h4>
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

// <GenomeBrowser
//     files={[]}
//     label="file gallery"
//     expanded
//     assembly="hg19"
//     displaySort
// />

AnnotationsSearch.propTypes = {
    context: PropTypes.object.isRequired,
};

AnnotationsSearch.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    fetch: PropTypes.func,
};

// export class ResultTable extends React.Component {
//     constructor(props) {
//         super(props);
//
//         // Bind `this` to non-React methods.
//         this.onFilter = this.onFilter.bind(this);
//     }
//
//     getChildContext() {
//         return {
//             actions: this.props.actions,
//         };
//     }
//
//     onFilter(e) {
//         const searchStr = e.currentTarget.getAttribute('href');
//         this.props.onChange(searchStr);
//         e.stopPropagation();
//         e.preventDefault();
//     }
//
//     render() {
//         const { context, searchBase, actions, hideDocType } = this.props;
//         const { facets, total, columns, filters } = context;
//         const results = context['@graph'];
//         const label = 'results';
//         const visualizeDisabledTitle = context.total > VISUALIZE_LIMIT ? `Filter to ${VISUALIZE_LIMIT} to visualize` : '';
//
//         return (
//             <div className="search-results">
//                 <FacetList
//                     {...this.props}
//                     facets={facets}
//                     filters={filters}
//                     searchBase={searchBase ? `${searchBase}&` : `${searchBase}?`}
//                     onFilter={this.onFilter}
//                     hideDocType={hideDocType}
//                 />
//                 {context.notification === 'Success' ?
//                     <div className="search-results__result-list">
//                         <h4>Showing {results.length} of {total} {label}</h4>
//                         <SearchControls context={context} visualizeDisabledTitle={visualizeDisabledTitle} onFilter={this.onFilter} showResultsToggle />
//                         {!(actions && actions.length > 0) ?
//                             <CartSearchControls searchResults={context} />
//                         : null}
//                         <ResultTableList results={results} columns={columns} cartControls />
//                     </div>
//                 :
//                     <h4>{context.notification}</h4>
//                 }
//             </div>
//         );
//     }
// }


globals.contentViews.register(AnnotationsSearch, 'AnnotationsSearch');
