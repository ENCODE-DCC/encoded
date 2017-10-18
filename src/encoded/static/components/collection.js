import React from 'react';
import PropTypes from 'prop-types';
import * as globals from './globals';
import { Panel } from '../libs/bootstrap/panel';


// Maximum number of facet charts to display.
const MAX_FACET_CHARTS = 3;


class FacetChart extends React.Component {
    constructor() {
        super();

        this.chartInstance = null;
    }

    componentDidUpdate() {
        if (this.props.chartModule) {
            // Extract the arrays of labels from the facet keys, and the arrays of corresponding
            // counts from the facet doc_counts.
            const labels = this.props.facet.terms.map(term => term.key);
            const data = this.props.facet.terms.map(term => term.doc_count);

            if (this.chartInstance) {
                // We've already created a chart instance, so just update it with new data.
                const canvas = document.getElementById(this.props.chartId);
            } else {
                // We've not yet created a chart instance, so make a new one with the initial set
                // of data. First extract the data in a way suitable for the chart API.
                const Chart = this.props.chartModule;
                const canvas = document.getElementById(this.props.chartId);
                const ctx = canvas.getContext('2d');
                this.chartInstance = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels,
                        datasets: [{
                            data,
                        }],
                    },
                });
            }
        }
    }

    render() {
        const { chartId } = this.props;
        return <canvas id={chartId} />;
    }
}

FacetChart.propTypes = {
    facet: PropTypes.object.isRequired, // Facet data to display in the chart
    chartId: PropTypes.string.isRequired, // HTML element ID to assign to the chart <canvas>
    chartModule: PropTypes.func, // chart.js NPM module as loaded by webpack
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
                    {chartFacets.map(facet =>
                        <FacetChart key={facet.field} facet={facet} chartId={`${facet.field}-chart`} chartModule={this.state.chartModule} />
                    )}
                </Panel>
            </div>
        );
    }
}

Collection.propTypes = {
    context: PropTypes.object.isRequired,
};

globals.contentViews.register(Collection, 'Collection');
