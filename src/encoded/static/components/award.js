import React from 'react';
import { Panel, PanelHeading, PanelBody } from '../libs/bootstrap/panel';
import DataColors from './datacolors';
import { FetchedItems } from './fetched';
import globals from './globals';
import { ProjectBadge } from './image';


const labChartId = 'lab-chart'; // Lab chart <div> id attribute
const assayChartId = 'assay-chart'; // Assay chart <div> id attribute
const labColors = new DataColors(); // Get a list of colors to use for the lab chart
const assayColors = new DataColors(); // Get a list of colors to use of the assay chart
const labColorList = labColors.colorList();
const assayColorList = assayColors.colorList();

// Display and handle clicks in the menu-like area that lets the user choose experiment statuses to
// view in the charts.
const StatusChooser = React.createClass({
    render: function () {
        return null;
    },
});


// Display and handle clicks in the chart of labs.
const LabChart = React.createClass({
    propTypes: {
        labs: React.PropTypes.array, // Array of labs facet data
    },

    contextTypes: {
        navigate: React.PropTypes.func,
    },

    componentDidMount: function () {
        this.createChart(labChartId, this.props.labs);
    },

    createChart: function (chartId, data) {
        require.ensure(['chart.js'], (require) => {
            const Chart = require('chart.js');

            // Generate the chart labels from the lab facet keys.
            const values = [];
            const labels = [];
            data.forEach((item) => {
                if (item.doc_count) {
                    values.push(item.doc_count);
                    labels.push(item.key);
                }
            });

            // Make an array of colors from the labels. Make it a list of
            const colors = labels.map((label, i) => labColorList[i % labColorList.length]);

            // Create the chart.
            const canvas = document.getElementById(`${chartId}-chart`);
            const ctx = canvas.getContext('2d');
            this.chart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: values,
                        backgroundColor: colors,
                    }],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    legend: {
                        display: false,
                    },
                    animation: {
                        duration: 200,
                    },
                    legendCallback: (chart) => {
                        const chartData = chart.data.datasets[0].data;
                        const chartColors = chart.data.datasets[0].backgroundColor;
                        const chartLabels = chart.data.labels;
                        const text = [];
                        text.push('<ul>');
                        for (let i = 0; i < chartData.length; i += 1) {
                            if (data[i]) {
                                text.push('<li>');
                                text.push(`<a href="/search/?type=Experiment&lab.title=${chartLabels[i]}">`);
                                text.push(`<span class="chart-legend-chip" style="background-color:${chartColors[i]}"></span>`);
                                if (chart.data.labels[i]) {
                                    text.push(`<span class="chart-legend-label">${chartLabels[i]}</span>`);
                                }
                                text.push('</a></li>');
                            }
                        }
                        text.push('</ul>');
                        return text.join('');
                    },
                    onClick: function (e) {
                        // React to clicks on pie sections
                        const activePoints = this.chart.getElementAtEvent(e);

                        if (activePoints[0]) { // if click on wrong area, do nothing
                            const clickedElementIndex = activePoints[0]._index;
                            const term = this.chart.data.labels[clickedElementIndex];
                            this.context.navigate(`/search/?type=Experiment&lab.title=${term}`);
                        }
                    }.bind(this),
                },
            });
            document.getElementById(`${chartId}-legend`).innerHTML = this.chart.generateLegend();
        });
    },

    render: function () {
        console.log('LAB: %o', this.props.labs);
        const { labs } = this.props;
        return (
            <div>
                <div className="title">
                    Lab
                    <center><hr width="80%" position="static" color="blue" /></center>
                </div>
                {labs.length ?
                    <div>
                        <div id={labChartId} className="chart-wrapper">
                            <canvas id={`${labChartId}-chart`} />
                        </div>
                        <div id={`${labChartId}-legend`} className="chart-legend" />
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

    render: function () {
        console.log('ASSAY: %o', this.props.assays);
        return null;
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
                <div>
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

    render: function () {
        const { award } = this.props;

        return (
            <Panel>
                <PanelHeading>
                    <StatusChooser />
                </PanelHeading>
                <PanelBody>
                    <FetchedItems
                        award={award}
                        url={`/search/?type=Experiment&limit=all&award.name=${award.name}`}
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
