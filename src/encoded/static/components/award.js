import React from 'react';
import { Panel, PanelHeading, PanelBody } from '../libs/bootstrap/panel';
import { AuditIndicators, AuditDetail, AuditMixin } from './audit';
import DataColors from './datacolors';
import { FetchedItems } from './fetched';
import globals from './globals';
import { ProjectBadge } from './image';
import { PickerActionsMixin } from './search';
import { StatusLabel } from './statuslabel';


const labChartId = 'lab-chart'; // Lab chart <div> id attribute
const assayChartId = 'assay-chart'; // Assay chart <div> id attribute
const statusChartId = 'status-chart'; // Status chart <div> id attribute
const labColors = new DataColors(); // Get a list of colors to use for the lab chart
const labColorList = labColors.colorList();
const typeSpecificColorList = labColors.colorList();
const statusColorList = labColors.colorList();


// Draw the total chart count in the middle of the donut.
function drawDonutCenter(chart) {
    const width = chart.chart.width;
    const height = chart.chart.height;
    const ctx = chart.chart.ctx;

    ctx.fillStyle = '#000000';
    ctx.restore();
    const fontSize = (height / 114).toFixed(2);
    ctx.font = `${fontSize}em sans-serif`;
    ctx.textBaseline = 'middle';

    const data = chart.data.datasets[0].data;
    const total = data.reduce((prev, curr) => prev + curr);
    const textX = Math.round((width - ctx.measureText(total).width) / 2);
    const textY = height / 2;

    ctx.clearRect(0, 0, width, height);
    ctx.fillText(total, textX, textY);
    ctx.save();
}


// Create a chart in the div.
//   chartId: Root HTML id of div to draw the chart into. Supply <divs> with `chartId`-chart for
//            the chart itself, and `chartId`-legend for its legend.
//   values: Array of values to chart.
//   labels: Array of string labels corresponding to the values.
//   colors: Array of hex colors corresponding to the values.
//   baseSearchUri: Base URI to navigate to when clicking a doughnut slice or legend item. Clicked
//                  item label gets appended to it.
//   navigate: Called when when a doughnut slice gets clicked. Gets passed the URI to go to. Needed
//             because this function can't access the navigation function.

function createDoughnutChart(chartId, values, labels, colors, baseSearchUri, navigate) {
    return new Promise((resolve) => {
        require.ensure(['chart.js'], (require) => {
            const Chart = require('chart.js');

            // adding total doc count to middle of donut
            // http://stackoverflow.com/questions/20966817/how-to-add-text-inside-the-doughnut-chart-using-chart-js/24671908
            Chart.pluginService.register({
                beforeDraw: drawDonutCenter,
            });

            // Create the chart.
            const canvas = document.getElementById(`${chartId}-chart`);
            const ctx = canvas.getContext('2d');
            const chart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: values,
                        backgroundColor: colors,
                    }],
                },
                options: {
                    maintainAspectRatio: true,
                    legend: {
                        display: false,
                    },
                    animation: {
                        duration: 200,
                    },
                    legendCallback: (chartInstance) => {
                        const chartData = chartInstance.data.datasets[0].data;
                        const chartColors = chartInstance.data.datasets[0].backgroundColor;
                        const chartLabels = chartInstance.data.labels;
                        const text = [];
                        text.push('<ul>');
                        for (let i = 0; i < chartData.length; i += 1) {
                            if (chartData[i]) {
                                text.push(`<li><a href="${baseSearchUri}${chartLabels[i]}">`);
                                text.push(`<span class="chart-legend-chip" style="background-color:${chartColors[i]}"></span>`);
                                text.push(`<span class="chart-legend-label">${chartLabels[i]}</span>`);
                                text.push('</a></li>');
                            }
                        }
                        text.push('</ul>');
                        return text.join('');
                    },
                    onClick: function (e) {
                        // React to clicks on pie sections
                        const activePoints = chart.getElementAtEvent(e);

                        if (activePoints[0]) { // if click on wrong area, do nothing
                            const clickedElementIndex = activePoints[0]._index;
                            const term = chart.data.labels[clickedElementIndex];
                            navigate(`${baseSearchUri}${term}`);
                        }
                    },
                },
            });
            document.getElementById(`${chartId}-legend`).innerHTML = chart.generateLegend();

            // Resolve the webpack loader promise with the chart instance.
            resolve(chart);
        });
    });
}


// Display and handle clicks in the chart of labs.
const LabChart = React.createClass({
    propTypes: {
        award: React.PropTypes.object, // Award being displayed
        labs: React.PropTypes.array, // Array of labs facet data
        uriBase: React.PropTypes.string, // Base URI for matrix links
    },

    contextTypes: {
        navigate: React.PropTypes.func,
    },

    componentDidMount: function () {
        this.createChart(labChartId, this.props.labs);
    },

    componentDidUpdate: function () {
        if (this.chart) {
            this.updateChart(this.chart, this.props.labs);
        }
    },

    createChart: function (chartId, facetData) {
        // Extract the non-zero values, and corresponding labels and colors for the data.
        const values = [];
        const labels = [];
        facetData.forEach((item) => {
            if (item.doc_count) {
                values.push(item.doc_count);
                labels.push(item.key);
            }
        });
        const colors = labels.map((label, i) => labColorList[i % labColorList.length]);

        // Create the chart.
        createDoughnutChart(chartId, values, labels, colors, `${this.props.uriBase}${this.props.award.name}&lab.title=`, (uri) => { this.context.navigate(uri); })
            .then((chartInstance) => {
                // Save the created chart instance.
                this.chart = chartInstance;
            });
    },

    // Update existing chart with new data.
    updateChart: function (chart, facetData) {
        // Extract the non-zero values, and corresponding labels and colors for the data.
        const values = [];
        const labels = [];
        facetData.forEach((item) => {
            if (item.doc_count) {
                values.push(item.doc_count);
                labels.push(item.key);
            }
        });
        const colors = labels.map((label, i) => labColorList[i % labColorList.length]);

        // Update chart data and redraw with the new data
        chart.data.datasets[0].data = values;
        chart.data.datasets[0].backgroundColor = colors;
        chart.data.labels = labels;
        chart.update();

        // Redraw the updated legend.
        document.getElementById(`${labChartId}-legend`).innerHTML = chart.generateLegend();
    },

    render: function () {
        const { labs } = this.props;
        return (
            <div className="award-charts__chart">
                <div className="title">
                    Lab
                    <center><hr width="80%" position="static" color="blue" /></center>
                </div>
                {labs.length ?
                    <div>
                        <div id={labChartId} className="award-charts__canvas">
                            <canvas id={`${labChartId}-chart`} />
                        </div>
                        <div id={`${labChartId}-legend`} className="award-charts__legend" />
                    </div>
                :
                    <div className="chart-no-data" style={{ height: this.wrapperHeight }}>No data to display</div>
                }
            </div>
        );
    },
});


// Display and handle clicks in the chart of assays.
const TypeSpecificChart = React.createClass({
    propTypes: {
        award: React.PropTypes.object, // Award being displayed
        typeSpecificData: React.PropTypes.array, // Type-specific data to display in a chart
        uriBase: React.PropTypes.string, // Base URI for matrix links
        matrixFacet: React.PropTypes.func, // Element of matrix URI to select
    },

    contextTypes: {
        navigate: React.PropTypes.func,
    },

    componentDidMount: function () {
        if (this.props.typeSpecificData.length) {
            this.createChart(assayChartId, this.props.typeSpecificData);
        }
    },

    componentDidUpdate: function () {
        if (this.chart) {
            this.updateChart(this.chart, this.props.typeSpecificData);
        }
    },

    createChart: function (chartId, facetData) {
        const { award, matrixFacet } = this.props;

        // Extract the non-zero values, and corresponding labels and colors for the data.
        const values = [];
        const labels = [];
        facetData.forEach((item) => {
            if (item.doc_count) {
                values.push(item.doc_count);
                labels.push(item.key);
            }
        });
        const colors = labels.map((label, i) => typeSpecificColorList[i % typeSpecificColorList.length]);

        // Create the chart.
        createDoughnutChart(chartId, values, labels, colors, matrixFacet(award), (uri) => { this.context.navigate(uri); })
            .then((chartInstance) => {
                // Save the created chart instance.
                this.chart = chartInstance;
            });
    },

    // Update existing chart with new data.
    updateChart: function (chart, facetData) {
        // Extract the non-zero values, and corresponding labels and colors for the data.
        const values = [];
        const labels = [];
        facetData.forEach((item) => {
            if (item.doc_count) {
                values.push(item.doc_count);
                labels.push(item.key);
            }
        });
        const colors = labels.map((label, i) => typeSpecificColorList[i % typeSpecificColorList.length]);

        // Update chart data and redraw with the new data
        chart.data.datasets[0].data = values;
        chart.data.datasets[0].backgroundColor = colors;
        chart.data.labels = labels;
        chart.update();

        // Redraw the updated legend.
        document.getElementById(`${assayChartId}-legend`).innerHTML = chart.generateLegend();
    },

    render: function () {
        const { typeSpecificData, title } = this.props;
        return (
            <div className="award-charts__chart">
                <div className="title">
                    {title}
                    <center><hr width="80%" position="static" color="blue" /></center>
                </div>
                {typeSpecificData.length ?
                    <div>
                        <div id={assayChartId} className="award-charts__canvas">
                            <canvas id={`${assayChartId}-chart`} />
                        </div>
                        <div id={`${assayChartId}-legend`} className="award-charts__legend" />
                    </div>
                :
                    <div className="chart-no-data" style={{ height: this.wrapperHeight }}>No data to display</div>
                }
            </div>
        );
    },
});


// Display and handle clicks in the chart of labs.
const StatusChart = React.createClass({
    propTypes: {
        award: React.PropTypes.object, // Award being displayed
        statuses: React.PropTypes.array, // Array of status facet data
        uriBase: React.PropTypes.string, // Base URI to use for matrix links
    },

    contextTypes: {
        navigate: React.PropTypes.func,
    },

    componentDidMount: function () {
        if (this.props.statuses.length) {
            this.createChart(statusChartId, this.props.statuses);
        }
    },

    componentDidUpdate: function () {
        if (this.chart) {
            this.updateChart(this.chart, this.props.statuses);
        }
    },

    createChart: function (chartId, facetData) {
        // Extract the non-zero values, and corresponding labels and colors for the data.
        const values = [];
        const labels = [];
        facetData.forEach((item) => {
            if (item.doc_count) {
                values.push(item.doc_count);
                labels.push(item.key);
            }
        });
        const colors = labels.map((label, i) => statusColorList[i % statusColorList.length]);

        // Create the chart.
        createDoughnutChart(chartId, values, labels, colors, `${this.props.uriBase}${this.props.award.name}&status=`, (uri) => { this.context.navigate(uri); })
            .then((chartInstance) => {
                // Save the created chart instance.
                this.chart = chartInstance;
            });
    },

    // Update existing chart with new data.
    updateChart: function (chart, facetData) {
        // Extract the non-zero values, and corresponding labels and colors for the data.
        const values = [];
        const labels = [];
        facetData.forEach((item) => {
            if (item.doc_count) {
                values.push(item.doc_count);
                labels.push(item.key);
            }
        });
        const colors = labels.map((label, i) => statusColorList[i % statusColorList.length]);

        // Update chart data and redraw with the new data
        chart.data.datasets[0].data = values;
        chart.data.datasets[0].backgroundColor = colors;
        chart.data.labels = labels;
        chart.update();

        // Redraw the updated legend.
        document.getElementById(`${statusChartId}-legend`).innerHTML = chart.generateLegend();
    },

    render: function () {
        const { statuses } = this.props;
        return (
            <div className="award-charts__chart">
                <div className="title">
                    Status
                    <center><hr width="80%" position="static" color="blue" /></center>
                </div>
                {statuses.length ?
                    <div>
                        <div id={statusChartId} className="award-charts__canvas">
                            <canvas id={`${statusChartId}-chart`} />
                        </div>
                        <div id={`${statusChartId}-legend`} className="award-charts__legend" />
                    </div>
                :
                    <div className="chart-no-data" style={{ height: this.wrapperHeight }}>No data to display</div>
                }
            </div>
        );
    },
});


// Once we get chart data to display, render the charts. We render three charts:
//   1. Lab - The labs the award applies to.
//   2. TypeSpecificData - A chart of data specific for an object type this award represents. We
//                         can have more than one data type associated with an award, but we only
//                         draw the data for one type for this chart. Whatever's the first type to
//                         return data is what we use.
//   3. Status - The release statuses of the objects associated with this award.
const ChartRenderer = React.createClass({
    propTypes: {
        award: React.PropTypes.object.isRequired, // Award being displayed
        searchData: React.PropTypes.object, // Array of experiments under this award
        title: React.PropTypes.string, // Title to display in chart
        uriBase: React.PropTypes.string, // Base URI to retrieve chart data
        matrixFacet: React.PropTypes.func, // Element of matrix URL to select
        legendExtractor: React.PropTypes.func, // Function to extract type-specific data from facets
    },

    render: function () {
        const { award, searchData, title, uriBase, matrixFacet, legendExtractor } = this.props;
        let labs; // Array of labs from facet data
        let typeSpecificData; // Array of type-specific data
        let statuses; // Array of statuses from facet data

        // Find the chart data in the returned facets.
        if (searchData && searchData.facets && searchData.facets.length) {
            // Get the array of lab data.
            const labFacet = searchData.facets.find(facet => facet.field === 'lab.title');
            if (labFacet) {
                labs = labFacet.terms && labFacet.terms.length ? labFacet.terms.sort((a, b) => (a.key < b.key ? -1 : (a.key > b.key ? 1 : 0))) : null;
            }

            // Get the array of assay types.
            const typeSpecificFacet = searchData.facets.find(legendExtractor);
            if (typeSpecificFacet) {
                typeSpecificData = typeSpecificFacet.terms && typeSpecificFacet.terms.length ? typeSpecificFacet.terms : null;
            }

            // Get the array of status data.
            const statusFacet = searchData.facets.find(facet => facet.field === 'status');
            if (statusFacet) {
                statuses = statusFacet.terms && statusFacet.terms.length ? statusFacet.terms : null;
            }
        }

        if (labs) {
            return (
                <div className="award-charts">
                    <LabChart award={award} labs={labs} uriBase={uriBase} />
                    <TypeSpecificChart award={award} typeSpecificData={typeSpecificData || []} uriBase={uriBase} matrixFacet={matrixFacet} title={title} />
                    <StatusChart award={award} statuses={statuses || []} uriBase={uriBase} />
                </div>
            );
        }
        return <p className="browser-error">No labs reference this award</p>;
    },
});


// Overall component to render the award charts
const AwardCharts = React.createClass({
    propTypes: {
        award: React.PropTypes.object, // Award represented by this chart
    },

    getInitialState: function () {
        return {
            statuses: { // Each set to True if their button is selected in the UI
                released: false,
                unreleased: false,
                revoked: false,
                archived: false,
            },
            searchData: {}, // Search data from search of objects using this award.
            chartSource: {}, // Element of `this.chartSource` that generated the data in `awardData`.
        };
    },

    // Get the data we need to draw the charts. Loop through this.chartSources until we get a search
    // that returns results.
    componentDidMount: function () {
        // Start with a resolved promise with undefined data (no parameter to Promise.resolve is
        // undefined data).
        let promise = Promise.resolve({ data: null, chartSource: {} });

        // Loop until we get data from the search.
        this.chartSources.forEach((chartSource) => {
            promise = promise.then((results) => {
                if (results.data) {
                    return Promise.resolve(results);
                }

                // Have not received data for the last search. Request data for the next source.
                return this.retrieveChartData(chartSource);
            });
        });
        promise.then((results) => {
            // We recieved good data. Set the component state to the new data we we can
            // render it.
            this.setState({
                searchData: results.data,
                chartSource: results.chartSource,
            });
        });
    },

    // Called when a status selection button gets clicked. The clicked status (either to enable or
    // disable it) gets passed in `status`.
    handleStatusSelection: function (status) {
        const newStatuses = this.state.statuses;
        newStatuses[status] = !newStatuses[status];
        this.setState({ statuses: newStatuses });
    },

    // Retrieve data for the type of search specified in searchConfig, which holds one object in
    // chartSources array. Returns a promise with the resulting data if any, or null if not.
    retrieveChartData: function (chartSource) {
        return fetch(globals.encodedURI(`${chartSource.uriBase}${this.props.award.name}`), {
            method: 'GET',
            headers: {
                Accept: 'application/json',
            },
        }).then((response) => {
            // Convert each response response to JSON
            if (response.ok) {
                return response.json();
            }
            return Promise.resolve(null);
        }).then(jsonData => Promise.resolve({ data: jsonData, chartSource: chartSource }));
    },

    // This array defines the order and some distinguishing aspects of the searches of data to
    // generate the award graphs. If one search returns no results, move on to the next until we
    // either get results or we run out of searches and can display no graph. Move to constructor
    // in React 15.
    //
    // title {string} - Displayed to indicate what award data we're seeing.
    // uriBase {string} - URI fragment to search for datasets that use this award. The award name
    //                    gets appended to this.
    // matrixFacet {string} - Element of URI to add to matrix to select a fact item.
    // legendExtractor { function} = Function to extract facets to use as a legend display for the
    //                               type-specific chart.
    chartSources: [
        {
            title: 'Assays',
            uriBase: '/search/?type=Experiment&award.name=',
            matrixFacet: award => `/matrix/?type=Experiment&award.name=${award.name}&assay_title=`,
            legendExtractor: facet => facet.field === 'assay_title',
        },
        {
            title: 'Annotation Types',
            uriBase: '/search/?type=Annotation&award.name=',
            matrixFacet: award => `/matrix/?type=Annotation&award.name=${award.name}&annotation_type=`,
            legendExtractor: facet => facet.field === 'annotation_type',
        },
    ],

    render: function () {
        const { award } = this.props;
        const { searchData, chartSource } = this.state;

        return (
            <Panel>
                <PanelHeading>
                    <h4>{award.pi && award.pi.lab ? <span>{award.pi.lab.title}</span> : <span>No PI indicated</span>}</h4>
                    <ProjectBadge award={award} addClasses="badge-heading" />
                </PanelHeading>
                <PanelBody>
                    <ChartRenderer
                        award={award}
                        searchData={searchData}
                        title={chartSource.title}
                        matrixFacet={chartSource.matrixFacet}
                        uriBase={chartSource.uriBase}
                        legendExtractor={chartSource.legendExtractor}
                    />
                </PanelBody>
            </Panel>
        );
    },
});


const Award = React.createClass({
    propTypes: {
        context: React.PropTypes.object, // Award object being rendered
    },

    render: function () {
        const { context } = this.props;
        const statuses = [{ status: context.status, title: 'Status' }];

        return (
            <div className={globals.itemClass(context, 'view-item')}>
                <header className="row">
                    <div className="col-sm-12">
                        <h2>{context.title || context.name}</h2>
                        <div className="status-line">
                            <div className="characterization-status-labels">
                                <StatusLabel status={statuses} />
                            </div>
                        </div>
                    </div>
                </header>

                <AwardCharts award={context} />

                <Panel>
                    <PanelHeading>
                        <h4>Description</h4>
                    </PanelHeading>
                    <PanelBody>
                        {context.description ?
                            <div className="two-column-long-text two-column-long-text--gap">
                                <p>{context.description}</p>
                            </div>
                        :
                            <p className="browser-error">Award has no description</p>
                        }
                    </PanelBody>
                </Panel>
            </div>
        );
    },
});

globals.content_views.register(Award, 'Award');


const Listing = React.createClass({
    propTypes: {
        context: React.PropTypes.object, // Object whose search result we're displaying
    },

    mixins: [PickerActionsMixin, AuditMixin],

    render: function () {
        const result = this.props.context;
        return (
            <li>
                <div className="clearfix">
                    {this.renderActions()}
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Award</p>
                        <p className="type">{` ${result.name}`}</p>
                        <p className="type meta-status">{` ${result.status}`}</p>
                        <AuditIndicators audits={result.audit} id={result['@id']} search />
                    </div>
                    <div className="accession">
                        <a href={result['@id']}>{result.title}</a>
                    </div>
                    <div className="data-row">
                        <div><strong>Project / RFA: </strong>{result.project} / {result.rfa}</div>
                    </div>
                </div>
                <AuditDetail audits={result.audit} except={result['@id']} id={this.props.context['@id']} forcedEditLink />
            </li>
        );
    },
});
globals.listing_views.register(Listing, 'Award');
