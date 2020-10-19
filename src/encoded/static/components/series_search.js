import React from 'react';
import PropTypes from 'prop-types';
import url from 'url';
import { Panel, PanelBody } from '../libs/ui/panel';
import { ResultTable } from './search';
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

// Find parent node link if it exists
function nearestAncestorHref(node) {
    let nodeVar = node;
    while (nodeVar && !nodeVar.href) {
        nodeVar = nodeVar.parentNode;
    }
    return nodeVar && nodeVar.href;
}

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
    const [selectedSeries, setSeries] = React.useState('OrganismDevelopmentSeries');
    const [seriesData, setSeriesData] = React.useState(null);
    const [descriptionData, setDescriptionData] = React.useState(null);
    const searchBase = url.parse(context.location_href).search || '';

    const handleClick = React.useCallback((series) => {
        // Get series data from search
        const seriesHref = `/search/?type=${series}`;
        getSeriesData(seriesHref, context.fetch).then((response) => {
            setSeries(series);
            setSeriesData(response);
        });
        // Get series description from schema
        const seriesDescriptionHref = `/profiles/${seriesList[series].schema}.json`;
        getSeriesData(seriesDescriptionHref, context.fetch).then((response) => {
            setDescriptionData(response.description);
        });
    }, [context.fetch]);

    const currentRegion = (assembly, region) => {
        if (assembly && region) {
            this.lastRegion = {
                assembly,
                region,
            };
        }
        return SeriesSearch.lastRegion;
    };

    // When a user clicks on the page, if they click on what would generally be a link if this were a regular search page,
    // we want to refresh the data displayed for the given series
    const handleLinks = (e) => {
        const clickedUrl = nearestAncestorHref(e.target);
        if (clickedUrl && (clickedUrl.indexOf('search') > -1)) {
            const parsedUrl = url.parse(clickedUrl);
            e.preventDefault();
            const seriesHref = parsedUrl.path.replace('series-search', 'search');
            getSeriesData(seriesHref, context.fetch).then((response) => {
                setSeriesData(response);
            });
        }
    };

    // Select series from tab buttons
    React.useEffect(() => {
        handleClick(selectedSeries);
    }, [handleClick, selectedSeries]);

    /* eslint-disable jsx-a11y/click-events-have-key-events, jsx-a11y/no-static-element-interactions */
    return (
        <div className="layout">
            <div className="layout__block layout__block--100">
                <div className="ricktextblock block series-search" data-pos="0,0,0">
                    <h1>Functional genomics series</h1>
                    <div className="outer-tab-container">
                        <div className="tab-container series-tabs">
                            {Object.keys(seriesList).map(s => (
                                <button
                                    key={s}
                                    className={`tab-button${selectedSeries === s ? ' selected' : ''}`}
                                    onClick={() => handleClick(s)}
                                >
                                    <div className="tab-inner">
                                        <div className="tab-icon">
                                            <img src={`/static/img/series/${s.replace('Series', '')}.svg`} alt={s} />
                                        </div>
                                        {seriesList[s].title}
                                    </div>
                                </button>
                            ))}
                        </div>
                        <div className="tab-border" />
                    </div>
                    <div className="tab-body">
                        <div className="tab-description">{descriptionData}</div>
                        <div className="series-wrapper" onClick={e => handleLinks(e)} >
                            <Panel>
                                <PanelBody>
                                    {seriesData ?
                                        <ResultTable
                                            context={seriesData}
                                            searchBase={searchBase}
                                            onChange={context.navigate}
                                            currentRegion={currentRegion}
                                            seriesFlag
                                        />
                                    : null}
                                </PanelBody>
                            </Panel>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
    /* eslint-enable jsx-a11y/click-events-have-key-events */
};

SeriesSearch.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    fetch: PropTypes.func,
};

globals.contentViews.register(SeriesSearch, 'SeriesSearch');
