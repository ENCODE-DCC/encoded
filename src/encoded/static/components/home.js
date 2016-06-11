'use strict';
var React = require('react');
var globals = require('./globals');
var {FetchedData, Param} = require('./fetched');

var Home = module.exports.Home = React.createClass({
    componentDidMount: function() {
    },

    render: function() {
        return (
            <div>
                <div className="homepage-main-box panel-gray">
                    <div className="row">
                        <div className="col-sm-12">
                            <div className="project-info site-title">
                                <h1>ENCODE: The Encyclopedia of DNA Elements</h1>
                            </div>
                            <div id="info-box" className="project-info text-panel">
                                <h4>Preview the new ENCODE Portal</h4>
                                <p>Enter a search term like "skin", "ChIP-seq", or "CTCF" or select a data type in the toolbar above.</p>
                            </div>
                            <HomepageSummaryLoader />
                        </div>
                    </div>
                </div>
            </div>
        );
    }
});


var HomepageSummary = React.createClass({
    contextTypes: {
        navigate: React.PropTypes.func
    },

    componentDidMount: function() {
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

            console.log(this.props);
            var facets = this.props.data.facets;
            var assayFacet = facets.find(facet => facet.field === 'assay_title');
            assayFacet.terms.forEach(function(term, i) {
                data[i] = term.doc_count;
                labels[i] = term.key;
                colors[i] = colorList[i % colorList.length];
            });
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
                        var activePoints = this.myPieChart.getElementAtEvent(e);
                        var term = assayFacet.terms[activePoints[0]._index].key;
                        this.context.navigate(this.props.data['@id'] + '&assay_title=' + term + '&ratio=' + window.devicePixelRatio);
                        console.log(activePoints);
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


var HomepageSummaryLoader = React.createClass({

    getDefaultProps: function () {
        return {searchBase: '?type=Experiment'};
    },

    getInitialState: function() {
        return {search: this.props.searchBase};
    },

    render: function() {
        return (
            <FetchedData>
                <Param name="data" url={'/search/' + this.state.search} />
                <HomepageSummary searchBase={this.state.search + '&'} />
            </FetchedData>
        );
    }

});
