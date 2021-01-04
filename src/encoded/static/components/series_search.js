import React from 'react';
import PropTypes from 'prop-types';
import url from 'url';
import { Panel, PanelBody, TabPanel } from '../libs/ui/panel';
import { ResultTable } from './search';
import QueryString from '../libs/query_string';
import * as globals from './globals';

// The series search page includes the following five series
const seriesList = {
    OrganismDevelopmentSeries: {
        title: 'Organism development',
        schema: 'organism_development_series',
    },
    TreatmentTimeSeries: {
        title: 'Treatment time',
        schema: 'treatment_time_series',
    },
    TreatmentConcentrationSeries: {
        title: 'Treatment concentration',
        schema: 'treatment_concentration_series',
    },
    ReplicationTimingSeries: {
        title: 'Replication timing',
        schema: 'replication_timing_series',
    },
    GeneSilencingSeries: {
        title: 'Gene silencing',
        schema: 'gene_silencing_series',
    },
};

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
const SeriesSearch = (props, context) => {
    const parsedUrl = url.parse(props.context['@id']);
    const query = new QueryString(parsedUrl.query);
    let selectedSeries = 'OrganismDevelopmentSeries';
    if (query.getKeyValues('type')[0]) {
        selectedSeries = query.getKeyValues('type')[0];
    }
    const [descriptionData, setDescriptionData] = React.useState(null);
    const searchBase = url.parse(context.location_href).search || '';

    const handleTabClick = React.useCallback((series) => {
        const href = `/series-search/?type=${series}`;
        context.navigate(href);
        // Get series description from schema
        const seriesDescriptionHref = `/profiles/${seriesList[series].schema}.json`;
        getSeriesData(seriesDescriptionHref, context.fetch).then((response) => {
            setDescriptionData(response.description);
        });
    }, [context]);

    const currentRegion = (assembly, region) => {
        if (assembly && region) {
            this.lastRegion = {
                assembly,
                region,
            };
        }
        return SeriesSearch.lastRegion;
    };

    const seriesTabs = [];
    Object.keys(seriesList).forEach((s) => {
        seriesTabs[s] =
            <div className="tab-inner">
                <div className="tab-icon">
                    <img src={`/static/img/series/${s.replace('Series', '')}.svg`} alt={s} />
                </div>
                {seriesList[s].title}
            </div>;
    });

    // Select series from tab buttons
    React.useEffect(() => {
        const seriesDescriptionHref = `/profiles/${seriesList[selectedSeries].schema}.json`;
        getSeriesData(seriesDescriptionHref, context.fetch).then((response) => {
            setDescriptionData(response.description);
        });
        if (!(query.getKeyValues('type')[0])) {
            query.addKeyValue('type', selectedSeries);
            const href = `?${query.format()}`;
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
                                <div className="tab-description">{descriptionData}</div>
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

SeriesSearch.propTypes = {
    context: PropTypes.object.isRequired,
};

SeriesSearch.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    fetch: PropTypes.func,
};

globals.contentViews.register(SeriesSearch, 'SeriesSearch');
