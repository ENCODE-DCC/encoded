import React from 'react';
import { Panel, PanelHeading, PanelBody } from '../libs/bootstrap/panel';
import { FetchedItems } from './fetched';
import globals from './globals';
import { ProjectBadge } from './image';


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

    createChart: function (labs) {
        // Draw the chart of search results given in this.props.data.facets. Since D3 doesn't work
        // with the React virtual DOM, we have to load it separately using the webpack .ensure
        // mechanism. Once the callback is called, it's loaded and can be referenced through
        // require.
        require.ensure(['chart.js'], (require) => {
            let Chart = require('chart.js');
            let colors = [];
            let data = [];
            let labels = [];
            let selectedAssay = (this.props.assayCategory && this.props.assayCategory !== 'COMPPRED') ? this.props.assayCategory.replace(/\+/g, ' ') : '';

            // for each item, set doc count, add to total doc count, add proper label, and assign color
            facetData.forEach((term, i) => {
                data[i] = term.doc_count;
                labels[i] = term.key;
                colors[i] = selectedAssay ? (term.key === selectedAssay ? 'rgb(255,217,98)' : 'rgba(255,217,98,.4)') : '#FFD962';
            });

            // Pass the counts to the charting library to render it.
            let canvas = document.getElementById("myChart3");
            let ctx = canvas.getContext("2d");
            this.myPieChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels, // full labels
                    datasets: [{
                        data: data,
                        backgroundColor: colors
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    legend: {
                        display: false // hiding automatically generated legend
                    },
                    animation: {
                        duration: 200
                    },
                    scales: {
                        xAxes: [{
                            gridLines: {
                                display: false
                            },
                            ticks: {
                                autoSkip: false
                            }
                        }]
                    },
                    onClick: function (e) {
                        // React to clicks on pie sections
                        var query = 'assay_slims=';
                        var activePoints = this.myPieChart.getElementAtEvent(e);
                        if (activePoints[0]) {
                            let clickedElementIndex = activePoints[0]._index;
                            var term = this.myPieChart.data.labels[clickedElementIndex];
                            this.context.navigate('/matrix/' + this.props.query + '&' + query + term); // go to matrix view
                        }
                    }.bind(this)
                }
            });

            // Save height of wrapper div.
            let chartWrapperDiv = document.getElementById('chart-wrapper-3');
            this.wrapperHeight = chartWrapperDiv.clientHeight;
        }.bind(this));

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
                    <div id="lab-chart" className="chart-wrapper">
                        <div className="chart-container-assaycat">
                            <canvas id="lab-chart-canvas"></canvas>
                        </div>
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
        data: React.PropTypes.array, // Array of experiments under this award
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
                labs = labFacet.terms && labFacet.terms.length ? labFacet.terms : null;
            }

            // Gett the array of assay types.
            const assayFacet = data.facets.find(facet => facet.field === 'assay_slims');
            if (assayFacet) {
                assays = assayFacet.terms && assayFacet.terms.length ? assayFacet.terms : null;
            }
        }

        // Find the array of assay types in the facet data

        return (
            <div>
                <LabChart labs={labs} />
                <AssayChart assays={assays} />
            </div>
        );
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

                <Panel>
                    <AwardCharts award={context} />
                </Panel>
            </div>
        );
    },
});

globals.content_views.register(Award, 'Award');
