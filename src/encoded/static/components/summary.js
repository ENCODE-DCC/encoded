import React from 'react';
import PropTypes from 'prop-types';
import queryString from 'query-string';
import _ from 'underscore';
import url from 'url';
import { Panel, PanelBody } from '../libs/bootstrap/panel';
import { LabChart, CategoryChart, ExperimentDate, createBarChart } from './award';
import * as globals from './globals';
import { FacetList } from './search';
import { getObjectStatuses } from './statuslabel';


// Get an array of all possible experiment statuses.
const experimentStatuses = getObjectStatuses('Experiment');


// Render the title pane.
const SummaryTitle = (props) => {
    const { context } = props;

    let clearButton;
    const searchQuery = url.parse(context['@id']).search;
    if (searchQuery) {
        // If we have a 'type' query string term along with others terms, we need a Clear Filters
        // button.
        const terms = queryString.parse(searchQuery);
        const nonPersistentTerms = _(Object.keys(terms)).any(term => term !== 'type');
        clearButton = nonPersistentTerms && terms.type;
    }

    return (
        <div className="summary-header__title">
            <h1>{context.title}</h1>
            {clearButton ?
                <div className="clear-filters-control--summary">
                    <a href={context.clear_filters}>Clear filters <i className="icon icon-times-circle" /></a>
                </div>
            : null}
        </div>
    );
};

SummaryTitle.propTypes = {
    context: PropTypes.object.isRequired, // Summary search result object
};


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
    const statusData = Array.from({ length: experimentStatuses.length }, (() => 0));

    // Convert statusData to a form createBarChart understands.
    if (buckets && buckets.length) {
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
        this.createChart = this.createChart.bind(this);
    }

    componentDidMount() {
        if (this.props.totalStatusData) {
            this.createChart();
        }
    }

    componentDidUpdate() {
        const { chart, props } = this;
        const { statusData } = props;

        if (chart) {
            const replicateTypeColors = globals.replicateTypeColors.colorList(globals.replicateTypeList);

            // For each replicate type, extract the data for each status to assign to the existing
            // chart's dataset.
            const datasets = [];
            globals.replicateTypeList.forEach((replicateType, replicateTypeIndex) => {
                const facetData = statusData.find(facet => facet.key === replicateType);
                if (facetData) {
                    // Get an array of replicate data per status from the facet data.
                    const data = generateStatusData(facetData.status.buckets, experimentStatuses);

                    datasets.push({
                        backgroundColor: replicateTypeColors[replicateTypeIndex],
                        data,
                        label: replicateType,
                    });
                }
            });

            // Update the chart data, then force a redraw of the chart and legend.
            chart.data.datasets = datasets;
            chart.update();
            document.getElementById(`${this.chartId}-legend`).innerHTML = chart.generateLegend();
        }
    }

    createChart() {
        const { statusData } = this.props;

        // Initialize data object to pass to createBarChart.
        const data = {
            anisogenicDataset: null,
            isogenicDataset: null,
            unreplicatedDataset: null,
            labels: experimentStatuses,
        };

        // Convert statusData to a form createBarChart understands.
        let facetData = statusData.find(facet => facet.key === 'anisogenic');
        data.anisogenicDataset = facetData ? generateStatusData(facetData.status.buckets, data.labels) : [];
        facetData = statusData.find(facet => facet.key === 'isogenic');
        data.isogenicDataset = facetData ? generateStatusData(facetData.status.buckets, data.labels) : [];
        facetData = statusData.find(facet => facet.key === 'unreplicated');
        data.unreplicatedDataset = facetData ? generateStatusData(facetData.status.buckets, data.labels) : [];

        // Generate colors to use for each replicate type.
        const colors = globals.replicateTypeColors.colorList(globals.replicateTypeList);

        createBarChart(this.chartId, data, colors, globals.replicateTypeList, 'Replication', this.props.linkUri, (uri) => { this.context.navigate(uri); })
            .then((chartInstance) => {
                // Save the created chart instance.
                this.chart = chartInstance;
            });
    }

    render() {
        const { totalStatusData } = this.props;

        // Calculate a (hopefully) unique ID to put on the DOM elements.
        this.chartId = 'status-chart-experiments';

        return (
            <div className="award-charts__chart">
                <div className="award-charts__title">
                    Status
                </div>
                {totalStatusData ?
                    <div className="award-charts__visual">
                        <div id={this.chartId} className="award-charts__canvas">
                            <canvas id={`${this.chartId}-chart`} />
                        </div>
                        <div id={`${this.chartId}-legend`} className="award-charts__legend" />
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
    navigate: PropTypes.func,
};


// Render the horizontal facets.
class SummaryHorzFacets extends React.Component {
    constructor() {
        super();

        // Bind `this` to non-React methods
        this.onFilter = this.onFilter.bind(this);
    }

    onFilter(e) {
        const search = e.currentTarget.getAttribute('href');
        this.context.navigate(search);
        e.stopPropagation();
        e.preventDefault();
    }

    render() {
        const { context } = this.props;
        const { location_href } = this.context;
        const allFacets = context.facets;

        // Get the array of facet field values to display in the horizontal facet area.
        const horzFacetFields = context.summary.x.facets;

        // Extract the horizontal facets from the list of all facets. We use the array of horizontal
        // facet field values of facets that should appear in the horizontal facets.
        const horzFacets = allFacets.filter(facet => horzFacetFields.indexOf(facet.field) >= 0);

        // Calculate the searchBase, which is the current search query string fragment that can have
        // terms added to it.`
        const searchBase = `${url.parse(location_href).search}&` || '?';

        return (
            <div className="summary-header__facets-horizontal">
                <FacetList
                    facets={horzFacets}
                    filters={context.filters}
                    orientation="horizontal"
                    searchBase={searchBase}
                    onFilter={this.onFilter}
                    addClasses="summary-facets"
                />
            </div>
        );
    }
}

SummaryHorzFacets.propTypes = {
    context: PropTypes.object.isRequired, // Summary search result object
};

SummaryHorzFacets.contextTypes = {
    location_href: PropTypes.string, // Current URL
    navigate: PropTypes.func, // encoded navigation
};


// Render the vertical facets.
class SummaryVertFacets extends React.Component {
    constructor() {
        super();

        // Bind `this` to non-React methods.
        this.onFilter = this.onFilter.bind(this);
    }

    onFilter(e) {
        const search = e.currentTarget.getAttribute('href');
        this.context.navigate(search);
        e.stopPropagation();
        e.preventDefault();
    }

    render() {
        const { context } = this.props;

        // Get the array of facet field values to display in the horizontal facet area.
        const vertFacetFields = context.summary.y.facets;

        // Extract the horizontal facets from the list of all facets. We use the array of horizontal
        // facet field values of facets that should appear in the horizontal facets.
        const vertFacets = context.facets.filter(facet => vertFacetFields.indexOf(facet.field) >= 0);

        // Calculate the searchBase, which is the current search query string fragment that can have
        // terms added to it.`
        const searchBase = `${url.parse(this.context.location_href).search}&` || '?';

        return (
            <div className="summary-content__facets-vertical">
                <FacetList
                    facets={vertFacets}
                    filters={context.filters}
                    searchBase={searchBase}
                    onFilter={this.onFilter}
                    addClasses="summary-facets"
                />
            </div>
        );
    }
}

SummaryVertFacets.propTypes = {
    context: PropTypes.object.isRequired, // Summary search result object
};

SummaryVertFacets.contextTypes = {
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
        const labFacet = context.facets.find(facet => facet.field === 'lab.title');
        let labs = labFacet ? labFacet.terms : null;
        const assayFacet = context.facets.find(facet => facet.field === 'assay_title');
        let assays = assayFacet ? assayFacet.terms : null;

        // Filter the assay list if any assay facets have been selected so that the assay graph will be
        // filtered accordingly. Find assay_title filters. Same applies to the lab filters.
        if (context.filters && context.filters.length) {
            const assayTitleFilters = context.filters.filter(filter => filter.field === 'assay_title');
            if (assayTitleFilters.length) {
                const assayTitleFilterTerms = assayTitleFilters.map(filter => filter.term);
                assays = assays.filter(assayItem => assayTitleFilterTerms.indexOf(assayItem.key) !== -1);
            }
            const labFilters = context.filters.filter(filter => filter.field === 'lab.title');
            if (labFilters.length) {
                const labFilterTerms = labFilters.map(filter => filter.term);
                labs = labs.filter(labItem => labFilterTerms.indexOf(labItem.key) !== -1);
            }
        }

        // Get the status data with a process completely different from the others because it comes
        // in its own property in the /summary/ context. Start by getting the name of the property
        // that contains the status data, as well as the number of items within it.
        const statusProp = context.summary.summary_grouping[0];
        const statusSection = context.summary[statusProp];
        const statusDataCount = statusSection.doc_count;
        const statusData = statusSection[statusProp].buckets;

        // Collect selected facet terms to add to the base linkUri.
        let searchQuery = '';
        if (context.filters && context.filters.length) {
            searchQuery = context.filters.reduce((queryAcc, filter) => `${queryAcc}&${filter.field}=${globals.encodedURIComponent(filter.term)}`, '');
        }
        const linkUri = `/matrix/?type=Experiment${searchQuery}`;

        return (
            <div className="summary-content__data">
                <div className="summary-content__snapshot">
                    {labs ? <LabChart labs={labs} linkUri={linkUri} ident="experiments" /> : null}
                    {assays ? <CategoryChart categoryData={assays} categoryFacet="assay_title" title="Assay" linkUri={linkUri} ident="assay" /> : null}
                    {statusDataCount ? <SummaryStatusChart statusData={statusData} totalStatusData={statusDataCount} linkUri={linkUri} ident="status" /> : null}
                </div>
                <div className="summary-content__statistics">
                    <ExperimentDate experiments={context.facets} panelCss="summary-content__panel" panelHeadingCss="summary-content__panel-heading" />
                </div>
            </div>
        );
    }
}

SummaryData.propTypes = {
    context: PropTypes.object.isRequired, // Summary search result object
};


// Render the title panel and the horizontal facets.
const SummaryHeader = (props) => {
    const { context } = props;

    return (
        <div className="summary-header">
            <SummaryTitle context={context} />
            <SummaryHorzFacets context={context} />
        </div>
    );
};

SummaryHeader.propTypes = {
    context: PropTypes.object.isRequired, // Summary search result object
};


// Render the vertical facets and the summary contents.
const SummaryContent = (props) => {
    const { context } = props;

    return (
        <div className="summary-content">
            <SummaryVertFacets context={context} />
            <SummaryData context={context} />
        </div>
    );
};

SummaryContent.propTypes = {
    context: PropTypes.object.isRequired, // Summary search result object
};


// Render the entire summary page based on summary search results.
const Summary = (props) => {
    const { context } = props;
    const itemClass = globals.itemClass(context, 'view-item');

    if (context.summary.doc_count) {
        return (
            <Panel addClasses={itemClass}>
                <PanelBody>
                    <SummaryHeader context={context} />
                    <SummaryContent context={context} />
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
