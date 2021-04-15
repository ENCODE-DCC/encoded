import React from 'react';
import PropTypes from 'prop-types';
import queryString from 'query-string';
import url from 'url';
import * as encoding from '../libs/query_encoding';
import QueryString from '../libs/query_string';
import { Panel, PanelBody } from '../libs/ui/panel';
import { CategoryChart, createNewBarChart } from './award';
import * as globals from './globals';
import { requestSearch } from './objectutils';
import { FacetList, ClearFilters } from './search';
import { getObjectStatuses, sessionToAccessLevel } from './status';
import { ViewControls } from './view_controls';

/**
 * Generate an array of data from one facet bucket for displaying in a chart, with one array entry
 * per experiment status. The order of the entries in the resulting array correspond to the order
 * of the statuses in `labels`.
 *
 * @param {array} buckets - Buckets for one facet returned in summary search results.
 * @param {array} labels - Experiment status labels.
 * @return {array} - Data extracted from buckets with an order of values corresponding to `labels`.
 */

function generateStatusData(buckets, labels) {
    // Fill the array to the proper length with zeroes to start with. Actual non-zero data will
    // overwrite the appropriate entries.
    const statusData = Array.from({ length: labels.length }, (() => 0));

    // Convert statusData to a form createBarChart understands.
    if (buckets && buckets.length > 0) {
        buckets.forEach((bucketItem) => {
            const statusIndex = labels.indexOf(bucketItem.key);
            if (statusIndex !== -1) {
                statusData[statusIndex] = bucketItem.doc_count;
            }
        });
    }
    return statusData;
}


// Column graph of experiment statuses.
class SummaryStatusChart extends React.Component {
    constructor() {
        super();
        this.chart = null;
        this.createChart = this.createChart.bind(this);
        this.updateChart = this.updateChart.bind(this);
    }

    componentDidMount() {
        if (this.props.totalStatusData) {
            this.createChart();
        }
    }

    componentDidUpdate() {
        if (this.props.totalStatusData) {
            if (this.chart) {
                this.updateChart(this.chart, this.props.statusData);
            } else {
                this.createChart();
            }
        } else if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    createChart() {
        const { statusData } = this.props;

        var ethnicityFacet = []
        this.props.facets.forEach(function(element) {
            if (element['field'] == 'donors.ethnicity.term_name') {
                ethnicityFacet = element['terms'];
            }
        });
        const ethnicityNames = Array.from(ethnicityFacet, x => x['key']);

        // Initialize data object to pass to createBarChart.
        const data = {
            femaleDataset: null,
            maleDataset: null,
            unknownDataset: null,
            labels: ethnicityNames,
        };

        // Convert statusData to a form createBarChart understands.
        let facetData = statusData.find(facet => facet.key === 'female');
        data.femaleDataset = facetData ? generateStatusData(facetData["donors.ethnicity.term_name"].buckets, data.labels) : [];
        facetData = statusData.find(facet => facet.key === 'male');
        data.maleDataset = facetData ? generateStatusData(facetData["donors.ethnicity.term_name"].buckets, data.labels) : [];
        facetData = statusData.find(facet => facet.key === 'unknown');
        data.unknownDataset = facetData ? generateStatusData(facetData["donors.ethnicity.term_name"].buckets, data.labels) : [];

        // Generate colors to use for each sex value.
        const colors = globals.donorSexColors.colorList(globals.donorSexList);

        createNewBarChart(this.chartId, data, colors, globals.donorSexList, this.props.linkUri, (uri) => { this.context.navigate(uri); })
            .then((chartInstance) => {
                // Save the created chart instance.
                this.chart = chartInstance;
            });
    }

    updateChart(chart, statusData) {
        const donorSexColors = globals.donorSexColors.colorList(globals.donorSexList);

        var ethnicityFacet = []
        this.props.facets.forEach(function(element) {
            if (element['field'] == 'donors.ethnicity.term_name') {
                ethnicityFacet = element['terms'];
            }
        });
        const ethnicityNames = Array.from(ethnicityFacet, x => x['key']);

        // For each sex value, extract the data for each status to assign to the existing
        // chart's dataset.
        const datasets = [];
        globals.donorSexList.forEach((donorSex, donorSexIndex) => {
            const facetData = statusData.find(facet => facet.key === donorSex);
            if (facetData) {
                // Get an array of replicate data per status from the facet data.
                const data = generateStatusData(facetData["donors.ethnicity.term_name"].buckets, ethnicityNames);

                datasets.push({
                    backgroundColor: donorSexColors[donorSexIndex],
                    data,
                    label: donorSex,
                });
            }
        });

        // Update the chart data, then force a redraw of the chart and legend.
        chart.data.datasets = datasets;
        chart.data.labels = ethnicityNames;
        chart.update();
    }

    render() {
        const { totalStatusData } = this.props;

        // Calculate a (hopefully) unique ID to put on the DOM elements.
        this.chartId = 'status-chart-experiments';

        return (
            <div className="award-charts__chart">
                <div className="award-charts__title">
                    Donors
                </div>
                {totalStatusData ?
                    <div className="award-charts__visual">
                        <div id={this.chartId} className="award-charts__canvas">
                            <canvas id={`${this.chartId}-chart`} />
                        </div>
                    </div>
                :
                    <div className="chart-no-data" style={{ height: this.wrapperHeight }}>No data to display</div>
                }
            </div>
        );
    }
}

SummaryStatusChart.propTypes = {
    statusData: PropTypes.array.isRequired, // Experiment status data from /summary/ search results
    totalStatusData: PropTypes.number.isRequired, // Number of items in statusData
    linkUri: PropTypes.string.isRequired, // URI of base link for each bar to link to
};

SummaryStatusChart.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
    navigate: PropTypes.func,
};

// Render the horizontal facets.
// Note: these facets are not necessarily horizontal, it depends on the screen width
const SummaryHorizontalFacets = ({ context, facetList }, reactContext) => {
    let horizFacets;
    if (facetList === 'all') {
        horizFacets = context.facets.filter(f => ['donors.organism.scientific_name', 'donors.sex', 'donors.life_stage', 'donors.ethnicity.term_name'].includes(f.field));
    } else {
        horizFacets = context.facets.filter(f => [].includes(f.field));
    }

    // Calculate the searchBase, which is the current search query string fragment that can have
    // terms added to it.
    const searchBase = `${url.parse(reactContext.location_href).search}&` || '?';

    // Note: we subtract one from the horizontal facet length because "date-released" and "date-submitted" are collapsed into one facet
    return (
        <FacetList
            context={context}
            facets={horizFacets}
            filters={context.filters}
            searchBase={searchBase}
            addClasses={`summary-horizontal-facets facet-num-${horizFacets.length - 1} ${facetList}`}
            supressTitle
            orientation="horizontal"
        />
    );
};

SummaryHorizontalFacets.propTypes = {
    context: PropTypes.object.isRequired, // Summary search result object
    facetList: PropTypes.string,
};

SummaryHorizontalFacets.defaultProps = {
    facetList: '',
};

SummaryHorizontalFacets.contextTypes = {
    location_href: PropTypes.string, // Current URL
    navigate: PropTypes.func, // encoded navigation
};

// Update all charts to resize themselves on print.
const printHandler = () => {
    Object.keys(window.Chart.instances).forEach((id) => {
        window.Chart.instances[id].resize();
    });
};


// Render the data for the summary in the main panel. Note that we use the charting components from
// awards.js for labs and categories, but not for the status chart. That's because the data gets
// retrieved so differently -- through multiple search requests in awards.js, but in its own
// property with this summary page. Might be good for a refactor later to share common code.

// "displayCharts" is an optional parameter which allows for display of subset of all possible charts
// Possible parameter values are "all", "donuts" or "area", and the default is "all"
class SummaryData extends React.Component {
    constructor() {
        super();
        this.mediaQueryInfo = null;
    }

    componentDidMount() {
        if (window.matchMedia) {
            this.mediaQueryInfo = window.matchMedia('print');
            this.mediaQueryInfo.addListener(printHandler);
        }

        // In case matchMedia doesn't work (e.g. FF and IE).
        window.onbeforeprint = printHandler;
        window.onafterprint = printHandler;
    }

    componentWillUnmount() {
        if (this.mediaQueryInfo) {
            this.mediaQueryInfo.removeListener(printHandler);
            this.mediaQueryInfo = null;
        }
    }

    render() {
        const { context } = this.props;

        // Find the labs and assay facets in the search results.
        const assayFacet = context.facets.find(facet => facet.field === 'assay');
        let assays = assayFacet ? assayFacet.terms : null;
        const awardFacet = context.facets.find(facet => facet.field === 'award.coordinating_pi.title');
        let awards = awardFacet ? awardFacet.terms : null;

        const filteredOutAssays = context.filters.filter(c => c.field === 'assay!');
        const filteredOutAwards = context.filters.filter(c => c.field === 'award.coordinating_pi.title!');

        // Filter the assay list if any assay facets have been selected so that the assay graph will be
        // filtered accordingly. Find assay_title filters. Same applies to the lab filters.
        if (context.filters && context.filters.length > 0) {
            const assayTitleFilters = context.filters.filter(filter => filter.field === 'assay');
            if (assayTitleFilters.length > 0) {
                const assayTitleFilterTerms = assayTitleFilters.map(filter => filter.term);
                assays = assays.filter(assayItem => assayTitleFilterTerms.indexOf(assayItem.key) !== -1);
            }
            const awardNameFilters = context.filters.filter(filter => filter.field === 'award.coordinating_pi.title');
            if (awardNameFilters.length > 0) {
                const awardNameFilterTerms = awardNameFilters.map(filter => filter.term);
                awards = awards.filter(awardItem => awardNameFilterTerms.indexOf(awardItem.key) !== -1);
            }
        }

        // Get the status data with a process completely different from the others because it comes
        // in its own property in the /summary/ context. Start by getting the name of the property
        // that contains the status data, as well as the number of items within it.
        const statusProp = context.matrix.y.group_by[0];
        const statusSection = context.matrix.y[statusProp];
        const statusDataCount = context.total;
        const statusData = statusSection.buckets;

        // Collect selected facet terms to add to the base linkUri.
        let searchQuery = '';
        if (context.filters && context.filters.length > 0) {
            searchQuery = context.filters.map(filter => `${filter.field}=${encoding.encodedURIComponentOLD(filter.term)}`).join('&');
        }
        const linkUri = `/report/?${searchQuery}`;
        const displayCharts = this.props.displayCharts;

        return (
            <div className="summary-content__data">
                {(displayCharts === 'all' || displayCharts === 'donuts') ?
                    <div className="summary-content__snapshot">
                        {assays ? <CategoryChart categoryData={assays} categoryFacet="assay" title="Assay" linkUri={linkUri} ident="assay" filteredOutAssays={filteredOutAssays} /> : null}
                        {statusDataCount ? <SummaryStatusChart statusData={statusData} totalStatusData={statusDataCount} linkUri={linkUri} facets={context.facets} ident="term_name" /> : null}
                        {awards ? <CategoryChart categoryData={awards} categoryFacet="award.coordinating_pi.title" title="Award" linkUri={linkUri} ident="award" filteredOutAwards={filteredOutAwards} /> : null}
                    </div>
                : null}
            </div>
        );
    }
}

SummaryData.propTypes = {
    context: PropTypes.object.isRequired, // Summary search result object
    displayCharts: PropTypes.string, // Optional property that allows display of subset of charts
};

SummaryData.defaultProps = {
    displayCharts: 'all',
};

class SummaryBody extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            cellCount: 0
        }
        const searchQuery = url.parse(this.props.context['@id']).search;
        const terms = queryString.parse(searchQuery);
    }

    componentDidMount() {
        const query_url = this.props.context.search_base.replace('/search/?', '')
        this.getCellCount(query_url);
    }

    getCellCount(searchBase) {
        requestSearch(searchBase + '&limit=all').then((results) => {
            if (Object.keys(results).length > 0 && results['@graph'].length > 0) {
                var mx_query = 'type=MatrixFile&layers.value_scale=linear&layers.normalized=false&derivation_process=cell calling&field=observation_count&limit=all'
                results['@graph'].forEach(x => mx_query += '&libraries=' + x['@id']);
                requestSearch(mx_query).then((results2) => {
                    var cell_count = 0
                    results2['@graph'].forEach(y => {
                        if (y['observation_count']) {
                            cell_count += y['observation_count']
                        }
                    });
                    this.setState({
                        cellCount: cell_count
                    })
                })
            }
        })
    }

    render() {
        const searchQuery = url.parse(this.props.context['@id']).search;
        const context = this.props.context;
        const vertFacetNames = ['assay', 'protocol.title', 'biosample_classification', 'biosample_ontologies.system_slims', 'biosample_ontologies.organ_slims', 'biosample_ontologies.term_name', 'award.project', 'award.coordinating_pi.title'];
        const vertFacets = []
        context.facets.forEach(x => {
            if (vertFacetNames.includes(x.field)) vertFacets.push(x);
            })
        const cell_count = this.state.cellCount.toLocaleString();
        return (
            <div className="search-results">
                <div className="search-results__facets">
                    <FacetList context={context} facets={vertFacets} filters={context.filters} searchBase={searchQuery} docTypeTitleSuffix="summary" />
                </div>
                <div className="search-results__report-list">
                    <h4>{this.props.context.total} {this.props.context.total > 1 ? 'libraries' : 'library'}</h4>
                    <h4>{cell_count} cells/nuclei</h4>
                    <div className="view-controls-container">
                        <ViewControls results={this.props.context} alternativeNames={['Tabular report']} />
                    </div>
                    <div className="top-facets">
                        <SummaryHorizontalFacets context={this.props.context} facetList="all" />
                    </div>
                    <React.Fragment>
                        <div className="summary-content">
                            <SummaryData context={this.props.context} displayCharts={'all'} />
                        </div>
                    </React.Fragment>
                </div>
            </div>
        );
    }
}

SummaryBody.propTypes = {
    context: PropTypes.object.isRequired, // Summary search result object
};

SummaryBody.contextTypes = {
    navigate: PropTypes.func,
    location_href: PropTypes.string,
};

// Render the entire summary page based on summary search results.
const Summary = (props) => {
    const { context } = props;
    const itemClass = globals.itemClass(context, 'view-item');

    if (context.total) {
        return (
            <Panel addClasses={itemClass}>
                <PanelBody>
                    <SummaryBody context={context} />
                </PanelBody>
            </Panel>
        );
    }
    return <h4>No results found</h4>;
};

Summary.propTypes = {
    context: PropTypes.object.isRequired, // Summary search result object
};

globals.contentViews.register(Summary, 'Summary');
