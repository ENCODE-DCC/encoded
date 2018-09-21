import React from 'react';
import PropTypes from 'prop-types';
import { Panel, PanelHeading, PanelBody } from '../libs/bootstrap/panel';
import * as globals from './globals';
import DataColors from './datacolors';
import { DisplayAsJson } from './objectutils';


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
        // loaded yet. If it hasn't loaded yet, we have nothing to do yet. Also see if we have any
        // values to render at all, and skip this if not.
        if (Chart && this.values.length) {
            // In case we don't have enough colors defined for all the values, make an array of
            // colors with enough entries to fill out the labels and values.
            const colors = this.labels.map((label, i) => collectionColorList[i % collectionColorList.length]);

            if (this.chartInstance) {
                // We've already created a chart instance, so just update it with new data.
                this.chartInstance.data.datasets[0].data = this.values;
                this.chartInstance.data.datasets[0].backgroundColor = colors;
                this.chartInstance.data.labels = this.labels;
                this.chartInstance.update();
                document.getElementById(`${chartId}-legend`).innerHTML = this.chartInstance.generateLegend();
            } else {
                // We've not yet created a chart instance, so make a new one with the initial set
                // of data. First extract the data in a way suitable for the chart API.
                const canvas = document.getElementById(chartId);

                const ctx = canvas.getContext('2d');

                // Create and render the chart.
                this.chartInstance = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: this.labels,
                        datasets: [{
                            data: this.values,
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
                        legendCallback: (chart) => {
                            const chartData = chart.data.datasets[0].data;
                            const chartColors = chart.data.datasets[0].backgroundColor;
                            const chartLabels = chart.data.labels;
                            const text = [];
                            text.push('<ul>');
                            for (let i = 0; i < chartData.length; i += 1) {
                                const searchUri = `${baseSearchUri}&${facet.field}=${encodeURIComponent(chartLabels[i]).replace(/%20/g, '+')}`;
                                if (chartData[i]) {
                                    text.push(`<li><a href="${searchUri}">`);
                                    text.push(`<i class="icon icon-circle chart-legend-chip" aria-hidden="true" style="color:${chartColors[i]}"></i>`);
                                    text.push(`<span class="chart-legend-label">${chartLabels[i]}</span>`);
                                    text.push('</a></li>');
                                }
                            }
                            text.push('</ul>');
                            return text.join('');
                        },
                        onClick: (e) => {
                            // React to clicks on pie sections
                            const activePoints = this.chartInstance.getElementAtEvent(e);
                            if (activePoints[0]) {
                                const clickedElementIndex = activePoints[0]._index;
                                const chartLabels = this.chartInstance.data.labels;
                                const searchUri = `${baseSearchUri}&${facet.field}=${encodeURIComponent(chartLabels[clickedElementIndex]).replace(/%20/g, '+')}`;
                                this.context.navigate(searchUri);
                            }
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
        const { chartId, facet } = this.props;

        // Extract the arrays of labels from the facet keys, and the arrays of corresponding counts
        // from the facet doc_counts. Only use non-zero facet terms in the charts. IF we have no
        // usable data, both these arrays have no entries. componentDidMount assumes these arrays
        // have been populated.
        this.values = [];
        this.labels = [];
        facet.terms.forEach((term) => {
            if (term.doc_count) {
                this.values.push(term.doc_count);
                this.labels.push(term.key);
            }
        });

        // Check whether we have usable values in one array or the other we just collected (we'll
        // just use `this;values` here) to see if we need to render a chart or not.
        if (this.values.length) {
            return (
                <div className="collection-charts__chart">
                    <div className="collection-charts__title">{facet.title}</div>
                    <div className="collection-charts__canvas">
                        <canvas id={chartId} />
                    </div>
                    <div id={`${chartId}-legend`} className="collection-charts__legend" />
                </div>
            );
        }
        return null;
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

FacetChart.contextTypes = {
    navigate: PropTypes.func,
};


class Collection extends React.Component {
    constructor() {
        super();

        // Initialize component React state.
        this.state = {
            chartModule: null, // Refers to chart.js npm module
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
        const chartFacets = facets ? facets.filter(facet => facet.field !== 'type' && facet.field.substring(0, 6) !== 'audit.').slice(0, MAX_FACET_CHARTS) : [];

        return (
            <div className={globals.itemClass(context, 'view-item')}>
                <header className="row">
                    <div className="col-sm-12">
                        <h2>{context.title}</h2>
                        {context.schema_description ? <h4 className="collection-sub-header">{context.schema_description}</h4> : null}
                    </div>
                    <DisplayAsJson />
                </header>
                <Panel>
                    <PanelHeading addClasses="collection-heading">
                        <h4>{context.total} total {context.title}</h4>
                        <div className="collection-heading__controls">
                            {(context.actions || []).map(action =>
                                <a key={action.name} href={action.href} className="btn btn-info">
                                    {action.title}
                                </a>
                            )}
                        </div>
                    </PanelHeading>
                    <PanelBody>
                        {chartFacets.length ?
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
                        :
                            <p className="collection-no-chart">No facets defined in the &ldquo;{context.title}&rdquo; schema, or no data available.</p>
                        }
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
