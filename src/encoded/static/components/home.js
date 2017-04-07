'use strict';
var React = require('react');
var _ = require('underscore');
var moment = require('moment');
var globals = require('./globals');
var {FetchedData, FetchedItems, Param} = require('./fetched');
import NewsPreviews from './news';
var cloneWithProps = require('react/lib/cloneWithProps');
var panel = require('../libs/bootstrap/panel');
var {Panel, PanelBody, PanelHeading} = panel;


const newsUri = '/search/?type=Page&news=true&status=released';


// Main page component to render the home page
var Home = module.exports.Home = React.createClass({

    getInitialState: function () { // sets initial state for current and newtabs
        return {
            current: "?type=Experiment&status=released", // show all released experiments
            organisms: [], // create empty array of selected tabs
            assayCategory: "",
            socialHeight: 0
        };
    },

    handleAssayCategoryClick: function (assayCategory) {
        if (this.state.assayCategory === assayCategory) {
            this.setState({ assayCategory: '' });
        } else {
            this.setState({ assayCategory: assayCategory });
        }
    },

    // pass in string with organism query and either adds or removes tab from list of selected tabs
    handleTabClick: function (selectedTab) {

        var tempArray = _.clone(this.state.organisms); // creates a copy of this.state.newtabs

        if (tempArray.indexOf(selectedTab) == -1) {
            // if tab isn't already in array, then add it
            tempArray.push(selectedTab);
        } else {
            // otherwise if it is in array, remove it from array and from link
            let indexToRemoveArray = tempArray.indexOf(selectedTab);
            tempArray.splice(indexToRemoveArray, 1);
        }

        // update newtabs
        this.setState({ organisms: tempArray });
    },

    newsLoaded: function () {
        // Called once the news content gets loaded
        let newsEl = this.refs.newslisting.getDOMNode();
        this.setState({ socialHeight: newsEl.clientHeight });
    },

    // Convert the selected organisms and assays into an encoded query.
    generateQuery: function (selectedOrganisms, selectedAssayCategory) {
        // Make the base query
        let query = selectedAssayCategory === 'COMPPRED' ? '?type=Annotation&encyclopedia_version=3' : "?type=Experiment&status=released";

        // Add the selected assay category, if any (doesn't apply to Computational Predictions)
        if (selectedAssayCategory && selectedAssayCategory !== 'COMPPRED') {
            query += '&assay_slims=' + selectedAssayCategory;
        }

        // Add all the selected organisms, if any
        if (selectedOrganisms.length) {
            let organismSpec = selectedAssayCategory === 'COMPPRED' ? 'organism.scientific_name=' : 'replicates.library.biosample.donor.organism.scientific_name=';
            let queryStrings = {
                'HUMAN': organismSpec + 'Homo+sapiens', // human
                'MOUSE': organismSpec + 'Mus+musculus', // mouse
                'WORM': organismSpec + 'Caenorhabditis+elegans', // worm
                'FLY': organismSpec + 'Drosophila+melanogaster&' + // fly
                organismSpec + 'Drosophila+pseudoobscura&' +
                organismSpec + 'Drosophila+simulans&' +
                organismSpec + 'Drosophila+mojavensis&' +
                organismSpec + 'Drosophila+ananassae&' +
                organismSpec + 'Drosophila+virilis&' +
                organismSpec + 'Drosophila+yakuba'
            };
            let organismQueries = selectedOrganisms.map(organism => queryStrings[organism]);
            query += '&' + organismQueries.join('&');
        }

        return query;
    },

    render: function () {
        // Based on the currently selected organisms and assay category, generate a query string
        // for the GET request to retrieve chart data.
        let currentQuery = this.generateQuery(this.state.organisms, this.state.assayCategory);

        return (
            <div className="whole-page">
                <header className="row">
                    <div className="col-sm-12">
                        <h1 className="page-title"></h1>
                    </div>
                </header>
                <div className="row">
                    <div className="col-xs-12">
                        <Panel>
                            <AssayClicking assayCategory={this.state.assayCategory} handleAssayCategoryClick={this.handleAssayCategoryClick} />
                            <div className="organism-tabs">
                                <TabClicking organisms={this.state.organisms} handleTabClick={this.handleTabClick} />
                            </div>
                            <div className="graphs">
                                <div className="row">
                                    <HomepageChartLoader organisms={this.state.organisms} assayCategory={this.state.assayCategory} query={currentQuery} />
                                </div>
                            </div>
                            <div className="social">
                                <div className="social-news">
                                    <div className="news-header">
                                        <h2>News <a href="/news/" title="More ENCODE news" className="twitter-ref">More ENCODE news</a></h2>
                                    </div>
                                    <NewsLoader ref="newslisting" newsLoaded={this.newsLoaded} />
                                </div>
                                <div className="social-twitter">
                                    <TwitterWidget height={this.state.socialHeight} />
                                </div>
                            </div>
                        </Panel>
                    </div>
                </div>
            </div>
        );
    }

});


// Given retrieved data, draw all home-page charts.
var ChartGallery = React.createClass({
    render: function () {
        return (
            <PanelBody>
                <div className="view-all">
                    <a href={"/matrix/" + this.props.query} className="view-all-button btn btn-info btn-sm" role="button">View Assay Matrix</a>
                </div>
                <div className="chart-gallery">
                    <div className="chart-single">
                        <HomepageChart {...this.props} />
                    </div>
                    <div className="chart-single">
                        <HomepageChart2 {...this.props} />
                    </div>
                    <div className="chart-single">
                        <HomepageChart3 {...this.props} />
                    </div>
                </div>
            </PanelBody>
        );
    }
});


// Component to allow clicking boxes on classic image
var AssayClicking = React.createClass({
    propTypes: {
        assayCategory: React.PropTypes.string
    },

    // Properly adds or removes assay category from link
    sortByAssay: function (category, e) {

        function handleClick(category, ctx) {
            // Call the Home component's function to record the new assay cateogry
            ctx.props.handleAssayCategoryClick(category); // handles assay category click
        }

        if (e.type === 'touchend') {
            handleClick(category, this);
            this.assayClickHandled = true;
        } else if (e.type === 'click' && !this.assayClickHandled) {
            handleClick(category, this);
        } else {
            this.assayClickHandled = false;
        }
    },

    // Renders classic image and svg rectangles
    render: function () {
        const assayList = ["3D+chromatin+structure",
            "DNA+accessibility",
            "DNA+binding",
            "DNA+methylation",
            "COMPPRED",
            "Transcription",
            "RNA+binding"];
        let assayCategory = this.props.assayCategory;
        return (
            <div ref="graphdisplay">
                <div className="overall-classic">

                    <h1>ENCODE: Encyclopedia of DNA Elements</h1>

                    <div className="site-banner">
                        <div className="site-banner-img">
                            <img src="static/img/classic-image.jpg" />

                            <svg id="site-banner-overlay" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2260 1450" className="classic-svg">
                                <rect id={assayList[0]} x="101.03" y="645.8" width="257.47" height="230.95" className={"rectangle-box" + (assayCategory == assayList[0] ? " selected" : "")} onClick={this.sortByAssay.bind(null, assayList[0])} onTouchEnd={this.sortByAssay.bind(null, assayList[0])} />
                                <rect id={assayList[1]} x="386.6" y="645.8" width="276.06" height="230.95" className={"rectangle-box" + (assayCategory == assayList[1] ? " selected" : "")} onClick={this.sortByAssay.bind(null, assayList[1])} onTouchEnd={this.sortByAssay.bind(null, assayList[1])} />
                                <rect id={assayList[2]} x="688.7" y="645.8" width="237.33" height="230.95" className={"rectangle-box" + (assayCategory == assayList[2] ? " selected" : "")} onClick={this.sortByAssay.bind(null, assayList[2])} onTouchEnd={this.sortByAssay.bind(null, assayList[2])} />
                                <rect id={assayList[3]} x="950.83" y="645.8" width="294.65" height="230.95" className={"rectangle-box" + (assayCategory == assayList[3] ? " selected" : "")} onClick={this.sortByAssay.bind(null, assayList[3])} onTouchEnd={this.sortByAssay.bind(null, assayList[3])} />
                                <rect id={assayList[4]} x="1273.07" y="645.8" width="373.37" height="230.95" className={"rectangle-box" + (assayCategory == assayList[4] ? " selected" : "")} onClick={this.sortByAssay.bind(null, assayList[4])} onTouchEnd={this.sortByAssay.bind(null, assayList[4])} />
                                <rect id={assayList[5]} x="1674.06" y="645.8" width="236.05" height="230.95" className={"rectangle-box" + (assayCategory == assayList[5] ? " selected" : "")} onClick={this.sortByAssay.bind(null, assayList[5])} onTouchEnd={this.sortByAssay.bind(null, assayList[5])} />
                                <rect id={assayList[6]} x="1937.74" y="645.8" width="227.38" height="230.95" className={"rectangle-box" + (assayCategory == assayList[6] ? " selected" : "")} onClick={this.sortByAssay.bind(null, assayList[6])} onTouchEnd={this.sortByAssay.bind(null, assayList[6])} />
                            </svg>
                        </div>

                        <div className="site-banner-intro">
                            <div className="site-banner-intro-content">
                                <p>The ENCODE (Encyclopedia of DNA Elements) Consortium is an international collaboration of research groups funded by the National Human Genome Research Institute (NHGRI). The goal of ENCODE is to build a comprehensive parts list of functional elements in the human genome, including elements that act at the protein and RNA levels, and regulatory elements that control cells and circumstances in which a gene is active.</p>
                                <div className="getting-started-button">
                                    <a href="/matrix/?type=Experiment&status=released" className="btn btn-info" role="button">Get Started</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

});

// Passes in tab to handleTabClick
var TabClicking = React.createClass({
    propTypes: {
        organisms: React.PropTypes.array, // Array of currently selected tabs
        handleTabClick: React.PropTypes.func
    },

    render: function () {
        let organisms = this.props.organisms;
        return (
            <div ref="tabdisplay">
                <div className="organism-selector">
                    <a className={"single-tab" + (organisms.indexOf('HUMAN') != -1 ? " selected" : "")} href="#" data-trigger onClick={this.props.handleTabClick.bind(null, 'HUMAN')}>Human</a>
                    <a className={"single-tab" + (organisms.indexOf('MOUSE') != -1 ? " selected" : "")} href="#" data-trigger onClick={this.props.handleTabClick.bind(null, 'MOUSE')}>Mouse</a>
                    <a className={"single-tab" + (organisms.indexOf('WORM') != -1 ? " selected" : "")} href="#" data-trigger onClick={this.props.handleTabClick.bind(null, 'WORM')}>Worm</a>
                    <a className={"single-tab" + (organisms.indexOf('FLY') != -1 ? " selected" : "")} href="#" data-trigger onClick={this.props.handleTabClick.bind(null, 'FLY')}>Fly</a>
                </div>
            </div>
        );
    }

});


// Initiates the GET request to search for experiments, and then pass the data to the HomepageChart
// component to draw the resulting chart.
var HomepageChartLoader = React.createClass({
    propTypes: {
        query: React.PropTypes.string // Current search URI based on selected assayCategory
    },

    render: function () {
        return (
            <FetchedData ignoreErrors>
                <Param name="data" url={'/search/' + this.props.query} />
                <ChartGallery organisms={this.props.organisms} assayCategory={this.props.assayCategory} query={this.props.query} />
            </FetchedData>
        );
    }

});


// Draw the total chart count in the middle of the donut.
function drawDonutCenter(chart) {
    let canvasId = chart.chart.canvas.id;
    let width = chart.chart.width;
    let height = chart.chart.height;
    let ctx = chart.chart.ctx;

    ctx.fillStyle = '#000000';
    ctx.restore();
    let fontSize = (height / 114).toFixed(2);
    ctx.font = fontSize + "em sans-serif";
    ctx.textBaseline = "middle";

    if (canvasId === 'myChart' || canvasId === 'myChart2') {
        let data = chart.data.datasets[0].data;
        let total = data.reduce((prev, curr) => prev + curr);
        let textX = Math.round((width - ctx.measureText(total).width) / 2);
        let textY = height / 2;

        ctx.clearRect(0, 0, width, height);
        ctx.fillText(total, textX, textY);
        ctx.save();
    } else {
        ctx.clearRect(0, 0, width, height);
    }
}


// Component to display the D3-based chart for Project
let HomepageChart = React.createClass({

    contextTypes: {
        navigate: React.PropTypes.func,
        projectColors: React.PropTypes.object // DataColor instance for experiment project
    },

    wrapperHeight: 200,

    // Draw the Project chart, for initial load, or when the previous load had no data for this
    // chart.
    createChart: function (facetData) {
        require.ensure(['chart.js'], function (require) {
            let Chart = require('chart.js');

            // for each item, set doc count, add to total doc count, add proper label, and assign color.
            let colors = this.context.projectColors.colorList(facetData.map(term => term.key), { shade: 10 });
            let data = [];
            let labels = [];

            // Convert facet data to chart data.
            facetData.forEach((term, i) => {
                data[i] = term.doc_count;
                labels[i] = term.key;
            });

            // adding total doc count to middle of donut
            // http://stackoverflow.com/questions/20966817/how-to-add-text-inside-the-doughnut-chart-using-chart-js/24671908
            Chart.pluginService.register({
                beforeDraw: drawDonutCenter
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
                    responsive: true,
                    maintainAspectRatio: false,
                    legend: {
                        display: false // Hide automatically generated legend; we draw it ourselves
                    },
                    animation: {
                        duration: 200
                    },
                    legendCallback: function (chart) { // allows for legend clicking
                        let data = chart.data.datasets[0].data;
                        let text = [];
                        text.push('<ul>');
                        for (let i = 0; i < data.length; i++) {
                            if (data[i]) {
                                text.push('<li>');
                                text.push('<a href="' + '/matrix/' + this.props.query + '&award.project=' + chart.data.labels[i] + '">'); // go to matrix view when clicked
                                text.push('<span class="chart-legend-chip" style="background-color:' + chart.data.datasets[0].backgroundColor[i] + '"></span>');
                                if (chart.data.labels[i]) {
                                    text.push('<span class="chart-legend-label">' + chart.data.labels[i] + '</span>');
                                }
                                text.push('</a></li>');
                            }
                        }
                        text.push('</ul>');
                        return text.join('');
                    }.bind(this),
                    onClick: function (e) {
                        // React to clicks on pie sections
                        var activePoints = this.myPieChart.getElementAtEvent(e);

                        if (activePoints[0]) { // if click on wrong area, do nothing
                            var clickedElementIndex = activePoints[0]._index;
                            var term = this.myPieChart.data.labels[clickedElementIndex];
                            this.context.navigate('/matrix/' + this.props.query + '&award.project=' + term);
                        }
                    }.bind(this)
                }
            });

            // Have chartjs draw the legend into the DOM.
            document.getElementById('chart-legend').innerHTML = this.myPieChart.generateLegend();

            // Save the chart <div> height so we can set it to that value when no data's available.
            let chartWrapperDiv = document.getElementById('chart-wrapper-1');
            this.wrapperHeight = chartWrapperDiv.clientHeight;
        }.bind(this));
    },

    // Update existing chart with new data.
    updateChart: function (Chart, facetData) {
        // for each item, set doc count, add to total doc count, add proper label, and assign color.
        let colors = this.context.projectColors.colorList(facetData.map(term => term.key), { shade: 10 });
        let data = [];
        let labels = [];

        // Convert facet data to chart data.
        facetData.forEach((term, i) => {
            data[i] = term.doc_count;
            labels[i] = term.key;
        });

        // Update chart data and redraw with the new data
        Chart.data.datasets[0].data = data;
        Chart.data.datasets[0].backgroundColor = colors;
        Chart.data.labels = labels;
        Chart.update();

        // Redraw the updated legend
        document.getElementById('chart-legend').innerHTML = Chart.generateLegend();
    },

    componentDidMount: function () {
        // Create the chart, and assign the chart to this.myPieChart when the process finishes.
        if (document.getElementById("myChart")) {
            this.createChart(this.facetData);
        }
    },

    componentDidUpdate: function () {
        if (this.myPieChart) {
            // Existing data updated
            this.updateChart(this.myPieChart, this.facetData);
        } else if (this.facetData.length) {
            // Chart existed but was destroyed for lack of data. Rebuild the chart.
            this.createChart(this.facetData);
        }
    },

    render: function () {
        let facets = this.props.data && this.props.data.facets;
        let total;

        // Get all project facets, or an empty array if none.
        if (facets) {
            let projectFacet = facets.find(facet => facet.field === 'award.project');
            this.facetData = projectFacet ? projectFacet.terms : [];
            let docCounts = this.facetData.length ? this.facetData.map(data => data.doc_count) : [];
            total = docCounts.length ? docCounts.reduce((prev, curr) => prev + curr) : 0;

            // No data with the current selection, but we used to? Destroy the existing chart so we can
            // display a no-data message instead.
            if ((this.facetData.length === 0 || total === 0) && this.myPieChart) {
                this.myPieChart.destroy();
                this.myPieChart = null;
            }
        } else {
            this.facets = null;
            if (this.myPieChart) {
                this.myPieChart.destroy();
                this.myPiechart = null;
            }
        }

        return (
            <div>
                <div className="title">
                    Project
                    <center> <hr width="80%" position="static" color="blue"></hr> </center>
                </div>
                {this.facetData.length && total ?
                    <div id="chart-wrapper-1" className="chart-wrapper">
                        <div className="chart-container">
                            <canvas id="myChart"></canvas>
                        </div>
                        <div id="chart-legend" className="chart-legend"></div>
                    </div>
                    :
                    <div className="chart-no-data" style={{ height: this.wrapperHeight }}><p>No data to display</p></div>
                }
            </div>
        );
    }

});


// Component to display the D3-based chart for Biosample
var HomepageChart2 = React.createClass({

    contextTypes: {
        navigate: React.PropTypes.func,
        biosampleTypeColors: React.PropTypes.object // DataColor instance for experiment project
    },

    wrapperHeight: 200,

    createChart: function (facetData) {

        // Draw the chart of search results given in this.props.data.facets. Since D3 doesn't work
        // with the React virtual DOM, we have to load it separately using the webpack .ensure
        // mechanism. Once the callback is called, it's loaded and can be referenced through
        // require.
        require.ensure(['chart.js'], function (require) {
            var Chart = require('chart.js');
            var colors = this.context.biosampleTypeColors.colorList(facetData.map(term => term.key), { shade: 10 });
            var data = [];
            var labels = [];

            facetData.forEach((term, i) => {
                data[i] = term.doc_count;
                labels[i] = term.key;
            });

            // adding total doc count to middle of donut
            // http://stackoverflow.com/questions/20966817/how-to-add-text-inside-the-doughnut-chart-using-chart-js/24671908
            Chart.pluginService.register({
                beforeDraw: drawDonutCenter
            });

            // Pass the assay_title counts to the charting library to render it.
            var canvas = document.getElementById("myChart2");
            if (canvas) {
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
                        responsive: true,
                        maintainAspectRatio: false,
                        legend: {
                            display: false // hiding automatically generated legend
                        },
                        animation: {
                            duration: 200
                        },
                        legendCallback: function (chart) { // allows for legend clicking
                            let data = chart.data.datasets[0].data;
                            let text = [];
                            text.push('<ul>');
                            for (let i = 0; i < data.length; i++) {
                                if (data[i]) {
                                    text.push('<li>');
                                    text.push(`<a href="/matrix/${this.props.query}&biosample_type=${chart.data.labels[i]}">`); // go to matrix view when clicked
                                    text.push(`<span class="chart-legend-chip" style="background-color:${chart.data.datasets[0].backgroundColor[i]}"></span>`);
                                    if (chart.data.labels[i]) {
                                        text.push(`<span class="chart-legend-label">${chart.data.labels[i]}</span>`);
                                    }
                                    text.push('</a></li>');
                                }
                            }
                            text.push('</ul>');
                            return text.join('');
                        }.bind(this),
                        onClick: function (e) {
                            // React to clicks on pie sections
                            let activePoints = this.myPieChart.getElementAtEvent(e);
                            if (activePoints[0]) {
                                let clickedElementIndex = activePoints[0]._index;
                                let term = this.myPieChart.data.labels[clickedElementIndex];
                                this.context.navigate(`/matrix/${this.props.query}&biosample_type=${term}`); // go to matrix view
                            }
                        }.bind(this)
                    }
                });
            } else {
                this.myPieChart = null;
            }

            // Have chartjs draw the legend into the DOM.
            const legendElement = document.getElementById('chart-legend-2');
            if (legendElement) {
                legendElement.innerHTML = this.myPieChart.generateLegend();
            }

            // Save the chart <div> height so we can set it to that value when no data's available.
            let chartWrapperDiv = document.getElementById('chart-wrapper-2');
            if (chartWrapperDiv) {
                this.wrapperHeight = chartWrapperDiv.clientHeight;
            }
        }.bind(this));
    },

    updateChart: function (Chart, facetData) {
        // for each item, set doc count, add to total doc count, add proper label, and assign color.
        let colors = this.context.biosampleTypeColors.colorList(facetData.map(term => term.key), { shade: 10 });
        let data = [];
        let labels = [];

        // Convert facet data to chart data.
        facetData.forEach((term, i) => {
            data[i] = term.doc_count;
            labels[i] = term.key;
        });

        // Update chart data and redraw with the new data
        Chart.data.datasets[0].data = data;
        Chart.data.datasets[0].backgroundColor = colors;
        Chart.data.labels = labels;
        Chart.update();

        // Redraw the updated legend
        document.getElementById('chart-legend-2').innerHTML = Chart.generateLegend(); // generates legend
    },

    componentDidMount: function () {
        if (document.getElementById("myChart2")) {
            this.createChart(this.facetData);
        }
    },

    componentDidUpdate: function () {
        if (this.myPieChart) {
            // Existing data updated
            this.updateChart(this.myPieChart, this.facetData);
        } else if (this.facetData.length) {
            // Chart existed but was destroyed for lack of data. Rebuild the chart.
            this.createChart(this.facetData);
        }
    },

    render: function () {
        let assayFacet = {};
        let facets = this.props.data && this.props.data.facets;
        let total;

        // Our data source will be different for computational predictions
        if (facets) {
            this.computationalPredictions = this.props.assayCategory === 'COMPPRED';
            assayFacet = facets.find(facet => facet.field === 'biosample_type');
            this.facetData = assayFacet ? assayFacet.terms : [];
            let docCounts = this.facetData.length ? this.facetData.map(data => data.doc_count) : [];
            total = docCounts.length ? docCounts.reduce((prev, curr) => prev + curr) : 0;

            // No data with the current selection, but we used to destroy the existing chart so we can
            // display a no-data message instead.
            if ((this.facetData.length === 0 || total === 0) && this.myPieChart) {
                this.myPieChart.destroy();
                this.myPieChart = null;
            }
        } else {
            this.facets = null;
            if (this.myPieChart) {
                this.myPieChart.destroy();
                this.myPiechart = null;
            }
        }

        return (
            <div>
                <div className="title">
                    Biosample Type
                    <center> <hr width="80%" position="static" color="blue"></hr> </center>
                </div>
                {this.facetData.length && total ?
                    <div id="chart-wrapper-2" className="chart-wrapper">
                        <div className="chart-container">
                            <canvas id="myChart2"></canvas>
                        </div>
                        <div id="chart-legend-2" className="chart-legend"></div>
                    </div>
                    :
                    <div className="chart-no-data" style={{ height: this.wrapperHeight }}>No data to display</div>
                }
            </div>
        );
    }
});


// Draw the small triangle above the selected assay in the "Assay Categories" chart if the user has
// selected an assay from the classic image.
function drawColumnSelects(currentAssay, ctx, data) {
    // Adapted from https://github.com/chartjs/Chart.js/issues/2477#issuecomment-255042267
    if (currentAssay) {
        ctx.fillStyle = '#2138B2';

        // Find the data with a label matching the currently selected assay.
        const currentColumn = data.labels.indexOf(currentAssay);
        if (currentColumn !== -1) {
            // Get information on the matching column's coordinates so we know where to draw the
            // triangle.
            const dataset = data.datasets[0];
            const model = dataset._meta[Object.keys(dataset._meta)[0]].data[currentColumn]._model;

            // Draw the triangle into the HTML5 <canvas> element.
            ctx.beginPath();
            ctx.moveTo(model.x - 5, model.y - 8);
            ctx.lineTo(model.x, model.y - 3);
            ctx.lineTo(model.x + 5, model.y - 8);
            ctx.fill();
        }
    }
}


// Component to display the D3-based chart for Biosample
let HomepageChart3 = React.createClass({

    contextTypes: {
        navigate: React.PropTypes.func
    },

    wrapperHeight: 200,

    createChart: function (facetData) {

        // Draw the chart of search results given in this.props.data.facets. Since D3 doesn't work
        // with the React virtual DOM, we have to load it separately using the webpack .ensure
        // mechanism. Once the callback is called, it's loaded and can be referenced through
        // require.
        require.ensure(['chart.js'], function (require) {
            let Chart = require('chart.js');
            let colors = [];
            let data = [];
            let labels = [];
            const selectedAssay = (this.props.assayCategory && this.props.assayCategory !== 'COMPPRED') ? this.props.assayCategory.replace(/\+/g, ' ') : '';

            // For each item, set doc count, add to total doc count, add proper label, and assign
            // color.
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
                    hover: {
                        mode: false,
                    },
                    animation: {
                        duration: 0,
                        onProgress: function() { drawColumnSelects(selectedAssay, this.chart.ctx, this.data); },
                        onComplete: function() { drawColumnSelects(selectedAssay, this.chart.ctx, this.data); },
                    },
                    scales: {
                        xAxes: [{
                            gridLines: {
                                display: false
                            },
                            ticks: {
                                autoSkip: false
                            }
                        }],
                    },
                    layout: {
                        padding: {
                            top: 10,
                        }
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

    updateChart: function (Chart, facetData) {
        // for each item, set doc count, add to total doc count, add proper label, and assign color.
        let data = [];
        let labels = [];
        let colors = [];

        // Convert facet data to chart data.
        let selectedAssay = (this.props.assayCategory && this.props.assayCategory !== 'COMPPRED') ? this.props.assayCategory.replace(/\+/g, ' ') : '';
        facetData.forEach((term, i) => {
            data[i] = term.doc_count;
            labels[i] = term.key;
            colors[i] = selectedAssay ? (term.key === selectedAssay ? 'rgb(255,217,98)' : 'rgba(255,217,98,.4)') : '#FFD962';
        });

        // Update chart data and redraw with the new data
        Chart.data.datasets[0].data = data;
        Chart.data.labels = labels;
        Chart.data.datasets[0].backgroundColor = colors;
        Chart.options.hover.mode = false;
        Chart.options.animation.onProgress = function() { drawColumnSelects(selectedAssay, this.chart.ctx, this.data); }
        Chart.options.animation.onComplete = function() { drawColumnSelects(selectedAssay, this.chart.ctx, this.data); }
        Chart.update();
    },

    componentDidMount: function () {
        if (document.getElementById("myChart3")) {
            this.createChart(this.facetData);
        }
    },

    componentDidUpdate: function () {
        if (this.myPieChart) {
            // Existing data updated
            this.updateChart(this.myPieChart, this.facetData);
        } else if (this.facetData.length) {
            // Chart existed but was destroyed for lack of data. Rebuild the chart.
            this.createChart(this.facetData);
        }
    },

    render: function () {
        let facets = this.props.data && this.props.data.facets;
        let total;

        // Get all assay category facets, or an empty array if none
        if (facets) {
            let projectFacet = facets.find(facet => facet.field === 'assay_slims');
            this.facetData = projectFacet ? projectFacet.terms : [];
            let docCounts = this.facetData.length ? this.facetData.map(data => data.doc_count) : [];
            total = docCounts.length ? docCounts.reduce((prev, curr) => prev + curr) : 0;

            // No data with the current selection, but we used to? Destroy the existing chart so we can
            // display a no-data message instead.
            if ((this.facetData.length === 0 || total === 0) && this.myPieChart) {
                this.myPieChart.destroy();
                this.myPieChart = null;
            }
        } else {
            this.facets = null;
            if (this.myPieChart) {
                this.myPieChart.destroy();
                this.myPiechart = null;
            }
        }

        return (
            <div>
                <div className="title">
                    Assay Categories
                    <center> <hr width="80%" position="static" color="blue"></hr> </center>
                </div>
                {this.facetData.length && total ?
                    <div id="chart-wrapper-3" className="chart-wrapper">
                        <div className="chart-container-assaycat">
                            <canvas id="myChart3"></canvas>
                        </div>
                    </div>
                    :
                    <div className="chart-no-data" style={{ height: this.wrapperHeight }}>No data to display</div>
                }
            </div>
        );
    }

});


// Send a GET request for the most recent five news posts.
var NewsLoader = React.createClass({
    propTypes: {
        newsLoaded: React.PropTypes.func.isRequired // Called parent once the news is loaded
    },

    render: function () {
        return <FetchedItems {...this.props} url={newsUri + '&limit=5'} Component={News} ignoreErrors newsLoaded={this.props.newsLoaded} />;
    }
});


// Render the most recent five news posts
var News = React.createClass({
    propTypes: {
        newsLoaded: React.PropTypes.func.isRequired // Called parent once the news is loaded
    },

    componentDidMount: function () {
        this.props.newsLoaded();
    },

    render: function () {
        var items = this.props.items;
        if (items && items.length) {
            return (
                <div className="news-listing">
                    <NewsPreviews items={items} />
                </div>
            );
        } else {
            return <div className="news-empty">No news available at this time</div>
        }
    }
});


var TwitterWidget = React.createClass({
    propTypes: {
        height: React.PropTypes.number.isRequired // Number of pixels tall to make widget
    },

    injectTwitter: function () {
        var js, link;
        if (!this.initialized) {
            link = this.refs.link.getDOMNode();
            this.initialized = true;
            js = document.createElement("script");
            js.id = "twitter-wjs";
            js.src = "//platform.twitter.com/widgets.js";
            return link.parentNode.appendChild(js);
        }
    },

    componentDidMount: function () { // twitter script from API
        if (!this.initialized && this.props.height) {
            this.injectTwitter();
        }
    },

    componentDidUpdate: function () {
        if (!this.initialized && this.props.height) {
            this.injectTwitter();
        }
    },

    render: function () {
        var content, ref2, title, widget;
        return (
            <div ref="twitterwidget">
                <div className="twitter-header">
                    <h2>Twitter <a href="https://twitter.com/EncodeDCC" title="ENCODE DCC Twitter page in a new window or tab" target="_blank" className="twitter-ref">@EncodeDCC</a></h2>
                </div>
                {this.props.height ?
                    <a
                        ref="link"
                        className="twitter-timeline"
                        href="https://twitter.com/encodedcc" // from encodedcc twitter
                        widget-id="encodedcc"
                        data-chrome="noheader"
                        data-screen-name="EncodeDCC"
                        //data-tweet-limit = "4"
                        //data-width = "300"
                        data-height={this.props.height + ''} // height so it matches with rest of site
                        ></a>
                    : null}
            </div>
        );
    }
});

