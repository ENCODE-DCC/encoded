import React from 'react';
import { Panel, PanelHeading, PanelBody } from '../libs/bootstrap/panel';
import DataColors from './datacolors';
import { FetchedItems } from './fetched';
import globals from './globals';
import { ProjectBadge } from './image';


const labChartId = 'lab-chart'; // Lab chart <div> id attribute
const assayChartId = 'assay-chart'; // Assay chart <div> id attribute
const labColors = new DataColors(); // Get a list of colors to use for the lab chart
const labColorList = labColors.colorList();


// Renders each status-chooser button.
const StatusChooserButton = React.createClass({
    propTypes: {
        title: React.PropTypes.string, // Title to display in button
        selected: React.PropTypes.bool, // True if the button is selected
        status: React.PropTypes.string, // Status being selected
        clickHandler: React.PropTypes.func, // Function to call when this button is clicked
    },

    handleClick: function () {
        this.props.clickHandler(this.props.status);
    },

    render: function () {
        const { title, selected } = this.props;

        return (
            <button onClick={this.handleClick} className={`status-chooser__button${selected ? ' status-chooser__button--selected' : ''}`}>{title}</button>
        );
    },
});


// Display and handle clicks in the menu-like area that lets the user choose experiment statuses to
// view in the charts.
const StatusChooser = React.createClass({
    propTypes: {
        statuses: React.PropTypes.object, // Selection state of each status
        clickHandler: React.PropTypes.func, // Function to call when a button is clicked
    },

    handleClick: function (status) {
        this.props.clickHandler(status);
    },

    render: function () {
        const { statuses } = this.props;

        return (
            <div className="status-chooser">
                <StatusChooserButton title="RELEASED" selected={statuses.released} status={'released'} clickHandler={this.handleClick} />
                <StatusChooserButton title="UNRELEASED" selected={statuses.unreleased} status={'unreleased'} clickHandler={this.handleClick} />
                <StatusChooserButton title="REVOKED" selected={statuses.revoked} status={'revoked'} clickHandler={this.handleClick} />
                <StatusChooserButton title="ARCHIVED" selected={statuses.archived} status={'archived'} clickHandler={this.handleClick} />
            </div>
        );
    },
});


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
                    maintainAspectRatio: false,
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
        labs: React.PropTypes.array, // Array of labs facet data
    },

    contextTypes: {
        navigate: React.PropTypes.func,
        assayTermNameColors: React.PropTypes.object,
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
        createDoughnutChart(chartId, values, labels, colors, '/search/?type=Experiment&lab.title=', (uri) => { this.context.navigate(uri); })
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
const AssayChart = React.createClass({
    propTypes: {
        assays: React.PropTypes.array, // Array of assay types facet data
    },

    contextTypes: {
        navigate: React.PropTypes.func,
        assayTermNameColors: React.PropTypes.object,
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
        const colors = this.context.assayTermNameColors.colorList(facetData.map(term => term.key), { shade: 10 });

        // Create the chart.
        createDoughnutChart(chartId, values, labels, colors, '/matrix/?type=Experiment&assay_title=', (uri) => { this.context.navigate(uri); })
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
        const colors = this.context.assayTermNameColors.colorList(facetData.map(term => term.key), { shade: 10 });

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
                <div className="title">
                    Assay Type
                    <center><hr width="80%" position="static" color="blue" /></center>
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


const ChartRenderer = React.createClass({
    propTypes: {
        data: React.PropTypes.object, // Array of experiments under this award
    },

    render: function () {
        const { data } = this.props;
        let labs; // Array of labs from facet data
        let assays; // Array of assay types from facet data

        // Find the chart data in the returned facets.
        if (data && data.facets && data.facets.length) {
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
        }

        if (labs || assays) {
            return (
                <div className="award-charts">
                    {labs ? <LabChart labs={labs} /> : null}
                    {assays ? <AssayChart assays={assays} /> : null}
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
        };
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

        // Convert statuses to a query string segment
        const statusQuery = Object.keys(this.state.statuses).reduce((query, statusKey) =>
            this.state.statuses[statusKey] ? query.concat(`&status=${statusKey}`) : query, '');

        return (
            <Panel>
                <PanelHeading>
                    <StatusChooser statuses={this.state.statuses} clickHandler={this.handleStatusSelection} />
                </PanelHeading>
                <PanelBody>
                    <FetchedItems
                        award={award}
                        url={`/search/?type=Experiment&award.name=${award.name}${statusQuery}`}
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

        return (
            <div className={globals.itemClass(context, 'view-item')}>
                <header className="row">
                    <div className="col-sm-12">
                        <h2>{context.title || context.name}</h2>
                    </div>
                </header>

                <Panel>
                    <PanelHeading>
                        <h4>Description</h4>
                        <ProjectBadge award={context} addClasses="badge-heading" />
                    </PanelHeading>
                    <PanelBody>
                        <div className="two-column-long-text two-column-long-text--gap">
                            {context.description ? <p>{context.description}</p> : <p className="browser-error">Award has no description</p>}
                        </div>
                        {context.pi && context.pi.lab ?
                            <dl className="key-value">
                                <div data-test="pi">
                                    <dt>Main PI contact</dt>
                                    <dd>{context.pi.lab.title}</dd>
                                </div>
                            </dl>
                        : null}
                    </PanelBody>
                </Panel>

                <AwardCharts award={context} />
            </div>
        );
    },
});

globals.content_views.register(Award, 'Award');
