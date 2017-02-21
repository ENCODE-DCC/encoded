import React from 'react';
import { Panel, PanelHeading, PanelBody } from '../libs/bootstrap/panel';
import DataColors from './datacolors';
import { FetchedItems } from './fetched';
import globals from './globals';
import { ProjectBadge } from './image';
import { PickerActions } from './search';
import { StatusLabel } from './statuslabel';


const labChartId = 'lab-chart'; // Lab chart <div> id attribute
const assayChartId = 'assay-chart'; // Assay chart <div> id attribute
const statusChartId = 'status-chart'; // Status chart <div> id attribute
const labColors = new DataColors(); // Get a list of colors to use for the lab chart
const labColorList = labColors.colorList();
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
        createDoughnutChart(chartId, values, labels, colors, `/matrix/?type=Experiment&award.name=${this.props.award.name}&lab.title=`, (uri) => { this.context.navigate(uri); })
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
                <div className="award-charts__title">
                    Lab
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
const AssayChart = React.createClass({
    propTypes: {
        award: React.PropTypes.object, // Award being displayed
        assays: React.PropTypes.array, // Array of assay types facet data
        colors: React.PropTypes.object, // Colors for the assay chart
    },

    contextTypes: {
        navigate: React.PropTypes.func,
    },

    componentDidMount: function () {
        this.createChart(assayChartId, this.props.assays);
    },

    componentDidUpdate: function () {
        if (this.chart) {
            this.updateChart(this.chart, this.props.assays);
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
        const colors = this.props.colors.colorList(facetData.map(term => term.key), { shade: 10 });

        // Create the chart.
        createDoughnutChart(chartId, values, labels, colors, `/matrix/?type=Experiment&award.name=${this.props.award.name}&assay_title=`, (uri) => { this.context.navigate(uri); })
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
        const colors = this.props.colors.colorList(facetData.map(term => term.key), { shade: 10 });

        // Update chart data and redraw with the new data
        chart.data.datasets[0].data = values;
        chart.data.datasets[0].backgroundColor = colors;
        chart.data.labels = labels;
        chart.update();

        // Redraw the updated legend.
        document.getElementById(`${assayChartId}-legend`).innerHTML = chart.generateLegend();
    },

    render: function () {
        const { assays } = this.props;
        return (
            <div className="award-charts__chart">
                <div className="award-charts__title">
                    Assay Type
                </div>
                {assays.length ?
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
    },

    contextTypes: {
        navigate: React.PropTypes.func,
    },

    componentDidMount: function () {
        this.createChart(statusChartId, this.props.statuses);
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
        createDoughnutChart(chartId, values, labels, colors, `/matrix/?type=Experiment&award.name=${this.props.award.name}&status=`, (uri) => { this.context.navigate(uri); })
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
                <div className="award-charts__title">
                    Status
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


const ChartRenderer = React.createClass({
    propTypes: {
        data: React.PropTypes.object, // Array of experiments under this award
        award: React.PropTypes.object, // Award being displayed
        colors: React.PropTypes.object, // Color object for assay term names
    },

    render: function () {
        const { data, award, colors } = this.props;
        let labs; // Array of labs from facet data
        let assays; // Array of assay types from facet data
        let statuses; // Array of statuses from facet data

        // Find the chart data in the returned facets.
        if (data && data.facets && data.facets.length && colors) {
            // Get the array of lab data.
            const labFacet = data.facets.find(facet => facet.field === 'lab.title');
            if (labFacet) {
                labs = labFacet.terms && labFacet.terms.length ? labFacet.terms.sort((a, b) => (a.key < b.key ? -1 : (a.key > b.key ? 1 : 0))) : null;
            }

            // Get the array of assay types.
            const assayFacet = data.facets.find(facet => facet.field === 'assay_title');
            if (assayFacet) {
                assays = assayFacet.terms && assayFacet.terms.length ? assayFacet.terms : null;
            }

            // Get the array of status data.
            const statusFacet = data.facets.find(facet => facet.field === 'status');
            if (statusFacet) {
                statuses = statusFacet.terms && statusFacet.terms.length ? statusFacet.terms : null;
            }
        }

        if (labs || assays || statuses) {
            return (
                <div className="award-charts">
                    {labs ? <LabChart award={award} labs={labs} /> : null}
                    {assays ? <AssayChart award={award} assays={assays} colors={colors} /> : null}
                    {statuses ? <StatusChart award={award} statuses={statuses} /> : null}
                </div>
            );
        }
        return <p className="browser-error">No labs nor assays reference this award</p>;
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
            assayTermNameColors: null,
        };
    },

    // Get the list of available assay_titles by doing a search of experiments and getting the
    // array of returned assay_titles.
    componentDidMount: function () {
        return fetch('/search/?type=Experiment&field=@id', {
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
        }).then((result) => {
            // Look for the assay_title facet
            const assayTitleFacet = result.facets.find(facet => facet.field === 'assay_title');
            if (assayTitleFacet) {
                const assayTitleList = assayTitleFacet.terms.map(term => term.key);
                const assayTitleColors = new DataColors(assayTitleList);
                this.setState({ assayTermNameColors: assayTitleColors });
            }
            return null;
        });
    },

    // Called when a status selection button gets clicked. The clicked status (either to enable or
    // disable it) gets passed in `status`.
    handleStatusSelection: function (status) {
        const newStatuses = this.state.statuses;
        newStatuses[status] = !newStatuses[status];
        this.setState({ statuses: newStatuses });
    },

    render: function () {
        const { award } = this.props;

        return (
            <Panel>
                <PanelHeading>
                    <h4>{award.pi && award.pi.lab ? <span>{award.pi.lab.title}</span> : <span>No PI indicated</span>}</h4>
                    <ProjectBadge award={award} addClasses="badge-heading" />
                </PanelHeading>
                <PanelBody>
                    <FetchedItems
                        award={award}
                        colors={this.state.assayTermNameColors}
                        url={`/search/?type=Experiment&award.name=${award.name}`}
                        Component={ChartRenderer}
                        ignoreErrors
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

    render: function () {
        const result = this.props.context;
        return (
            <li>
                <div className="clearfix">
                    <PickerActions {...this.props} />
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Award</p>
                        <p className="type">{` ${result.name}`}</p>
                        <p className="type meta-status">{` ${result.status}`}</p>
                    </div>
                    <div className="accession">
                        <a href={result['@id']}>{result.title}</a>
                    </div>
                    <div className="data-row">
                        <div><strong>Project / RFA: </strong>{result.project} / {result.rfa}</div>
                    </div>
                </div>
            </li>
        );
    },
});

globals.listing_views.register(Listing, 'Award');
