'use strict';
var React = require('react');
var globals = require('./globals');
var {FetchedData, Param} = require('./fetched');


// Main page component to render the home page
var Home = module.exports.Home = React.createClass({

    render: function() {
        return (
            <div>
                <div className="homepage-banner">
                    <div className="home-page-banner-title">
                        ENCYCLOPEDIA of DNA ELEMENTS
                    </div>
                </div>
                <div className="row">
                    <div className="col-sm-12">
                        <HomepageChartLoader />
                    </div>
                </div>
            </div>
        );
    }

});


// Component to display the D3-based chart
var HomepageChart = React.createClass({

    contextTypes: {
        navigate: React.PropTypes.func
    },

    componentDidMount: function() {
        // Draw the chart of search results given in this.props.data.facets. Since D3 doesn't work
        // with the React virtual DOM, we have to load it separately using the webpack .ensure
        // mechanism. Once the callback is called, it's loaded and can be referenced through
        // require.
        require.ensure(['chart.js'], function(require) {
            var Chart = require('chart.js');
            var colorList = [
                '#1F518B',
                '#1488C8',
                '#F7E041',
                '#E2413E',
                '#B5292A'
            ];
            var data = [];
            var labels = [];
            var colors = [];

            // Get the assay_title counts from the facets
            var facets = this.props.data.facets;
            var assayFacet = facets.find(facet => facet.field === 'assay_title');

            // Collect up the experiment assay_title counts to our local arrays to prepare for
            // the charts.
            assayFacet.terms.forEach(function(term, i) {
                data[i] = term.doc_count;
                labels[i] = term.key;
                colors[i] = colorList[i % colorList.length];
            });

            // Pass the assay_title counts to the charting library to render it.
            var canvas = document.getElementById("myChart");
            var ctx = canvas.getContext("2d");
            this.myPieChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: colors
                    }]
                },
                options: {
                    onClick: (e) => {
                        // React to clicks on pie sections
                        var activePoints = this.myPieChart.getElementAtEvent(e);
                        var term = assayFacet.terms[activePoints[0]._index].key;
                        this.context.navigate(this.props.data['@id'] + '&assay_title=' + term);
                    }
                }
            });
        }.bind(this));
    },

    render: function() {
        return (
            <canvas id="myChart" width="400" height="400"></canvas>
        );
    }

});


// Initiates the GET request to search for experiments, and then pass the data to the HomepageChart
// component to draw the resulting chart.
var HomepageChartLoader = React.createClass({

    getDefaultProps: function () {
        // Default searchBase if none passed in
        return {searchBase: '?type=Experiment'};
    },

    getInitialState: function() {
        return {search: this.props.searchBase};
    },

    render: function() {
        return (
            <FetchedData>
                <Param name="data" url={'/search/' + this.state.search} />
                <HomepageChart searchBase={this.state.search + '&'} />
            </FetchedData>
        );
    }

});
