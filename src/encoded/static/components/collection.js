import React from 'react';
import PropTypes from 'prop-types';
import { Panel, PanelBody } from '../libs/bootstrap/panel';
import * as globals from './globals';
import DataColors from './datacolors';


// Maximum number of facet charts to display.
const MAX_FACET_CHARTS = 3;

// Initialize a list of colors to use in the chart.
const collectionColors = new DataColors(); // Get a list of colors to use for the lab chart
const collectionColorList = collectionColors.colorList();


class FacetChart extends React.Component {
    constructor() {
        super();

        this.chartInstance = null;
    }

    componentDidUpdate() {
        // This method might be called because we're drawing the chart for the first time (in
        // that case this is an update because we already rendered an empty canvas before the
        // chart.js module was loaded) or because we have new data to render into an existing
        // chart.
        const { chartId, facet, baseSearchUri } = this.props;
        const Chart = this.props.chartModule;

        // Before rendering anything into the chart, check whether we have a the chart.js module
        // loaded yet. If it hasn't loaded yet, we have nothing to do yet.
        if (Chart) {
            // Extract the arrays of labels from the facet keys, and the arrays of corresponding
            // counts from the facet doc_counts. Only use non-zero facet terms in the charts.
            const values = [];
            const labels = [];
            facet.terms.forEach((term) => {
                if (term.doc_count) {
                    values.push(term.doc_count);
                    labels.push(term.key);
                }
            });

            if (this.chartInstance) {
                // We've already created a chart instance, so just update it with new data.
                this.chartInstance.data.datasets[0].data = values;
                this.chartInstance.data.labels = labels;
                this.chartInstance.update();
            } else {
                // We've not yet created a chart instance, so make a new one with the initial set
                // of data. First extract the data in a way suitable for the chart API.
                const canvas = document.getElementById(chartId);
                const ctx = canvas.getContext('2d');

                // In case we don't have enough colors defined for all the values, make an array of
                // colors with enough entries to fill out the labels and values.
                const colors = labels.map((label, i) => collectionColorList[i % collectionColorList.length]);

                // Create and render the chart.
                this.chartInstance = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels,
                        datasets: [{
                            data: values,
                            backgroundColor: colors,
                        }],
                    },
                    options: {
                        maintainAspectRatio: false,
                        responsive: true,
                        legend: {
                            display: false,
                        },
                        animation: {
                            duration: 200,
                        },
                        legendCallback: (chartInstance) => {
                            const chartData = chartInstance.data.datasets[0].data;
                            const chartLabels = chartInstance.data.labels;
                            const text = [];
                            text.push('<ul>');
                            for (let i = 0; i < chartData.length; i += 1) {
                                const searchUri = `${baseSearchUri}&${facet.field}=${encodeURIComponent(chartLabels[i]).replace(/%20/g, '+')}`;
                                if (chartData[i]) {
                                    text.push(`<li><a href="${searchUri}">`);
                                    text.push(`<i class="icon icon-circle chart-legend-chip" aria-hidden="true" style="color:${colors[i]}"></i>`);
                                    text.push(`<span class="chart-legend-label">${chartLabels[i]}</span>`);
                                    text.push('</a></li>');
                                }
                            }
                            text.push('</ul>');
                            return text.join('');
                        },
                    },
                });

                // Create and render the legend by drawibg it into the <div> we set up for that
                // purposee.
                document.getElementById(`${chartId}-legend`).innerHTML = this.chartInstance.generateLegend();
            }
        }
    }

    render() {
        const { chartId } = this.props;
        return (
            <div className="collection-charts__chart">
                <div className="collection-charts__canvas">
                    <canvas id={chartId} />
                </div>
                <div id={`${chartId}-legend`} className="collection-charts__legend" />
            </div>
        );
    }
}

FacetChart.propTypes = {
    facet: PropTypes.object.isRequired, // Facet data to display in the chart
    chartId: PropTypes.string.isRequired, // HTML element ID to assign to the chart <canvas>
    chartModule: PropTypes.func, // chart.js NPM module as loaded by webpack
    baseSearchUri: PropTypes.string.isRequired, // Base URL of clicked chart elements
};

FacetChart.defaultProps = {
    chartModule: null,
};


class Collection extends React.Component {
    constructor() {
        super();

        // Initialize component React state.
        this.state = {
            chartModule: null, // Refers to chart.js npm module
            facetCharts: [], // Tracks all chart instances
        };
    }

    componentDidMount() {
        // Have webpack load the chart.js npm module. Once the module's ready, set the chartModule
        // state so we can readraw the charts with the chart module in place.
        require.ensure(['chart.js'], (require) => {
            const Chart = require('chart.js');
            this.setState({ chartModule: Chart });
        });
    }

    render() {
        const { context } = this.props;
        const { facets } = context;

        // Collect the three facets that will be included in the charts. This comprises the first
        // MAX_FACET_CHARTS facets, not counting any facets with "type" for the field which we never
        // chart, nor audit facets.
        const chartFacets = facets.filter(facet => facet.field !== 'type' && facet.field.substring(0, 6) !== 'audit.').slice(0, MAX_FACET_CHARTS);

        return (
            <div className={globals.itemClass(context, 'view-item')}>
                <header className="row">
                    <div className="col-sm-12">
                        <h2>{context.title}</h2>
                    </div>
                </header>
                <Panel>
                    <PanelBody>
                        <div className="collection-charts">
                            {chartFacets.map(facet =>
                                <FacetChart
                                    key={facet.field}
                                    facet={facet}
                                    chartId={`${facet.field}-chart`}
                                    chartModule={this.state.chartModule}
                                    baseSearchUri={context.clear_filters}
                                />
                            )}
                        </div>
                    </PanelBody>
                </Panel>
            </div>
        );
    }
}

Collection.propTypes = {
    context: PropTypes.object.isRequired,
};

globals.contentViews.register(Collection, 'Collection');
