'use strict';
var React = require('react');
var _ = require('underscore');
var moment = require('moment');
var globals = require('./globals');
var {FetchedData, FetchedItems, Param} = require('./fetched');
var cloneWithProps = require('react/lib/cloneWithProps');
var panel = require('../libs/bootstrap/panel');
var {Panel, PanelBody, PanelHeading} = panel;


const newsUri = '/search/?type=Page&news=true&status=released';


// Main page component to render the home page
var Home = module.exports.Home = React.createClass({

    getInitialState: function() { // sets initial state for current and newtabs
        return {
            current: "?type=Experiment&status=released", // show all released experiments
            organisms: [], // create empty array of selected tabs
            assayCategory: "",
            socialHeight: 0
        };
    },

    handleAssayCategoryClick: function(assayCategory) {
        if (this.state.assayCategory === assayCategory) {
            this.setState({assayCategory: ''});
        } else{
            this.setState({assayCategory: assayCategory});
        }
    },

    // pass in string with organism query and either adds or removes tab from list of selected tabs
    handleTabClick: function(selectedTab) {

        var tempArray = _.clone(this.state.organisms); // creates a copy of this.state.newtabs

        if (tempArray.indexOf(selectedTab) == -1) {
            // if tab isn't already in array, then add it
            tempArray.push(selectedTab);
        } else{
            // otherwise if it is in array, remove it from array and from link
            var indexToRemoveArray = tempArray.indexOf(selectedTab);
            tempArray.splice(indexToRemoveArray, 1);
        }

        // update newtabs
        this.setState({organisms: tempArray});
    },

    newsLoaded: function() {
        // Called once the news content gets loaded
        var newsEl = this.refs.newslisting.getDOMNode();
        this.setState({socialHeight: newsEl.clientHeight});
    },

    generateQuery: function(selectedOrganisms, selectedAssayCategory) {
        // Make the base query
        let query = selectedAssayCategory === 'COMPPRED' ? '?type=Annotation&encyclopedia_version=3' : "?type=Experiment&status=released";

        // Add the selected assay category, if any (doesn't apply to Computational Predictions)
        if (selectedAssayCategory && selectedAssayCategory !== 'COMPPRED') {
            query += '&assay_slims=' + selectedAssayCategory;
        }

        // Add all the selected organisms, if any
        if (selectedOrganisms.length) {
            let organismSpec = selectedAssayCategory === 'COMPPRED' ? 'organism.scientific_name=' : 'replicates.library.biosample.donor.organism.scientific_name=';
            let queryStrings = {'HUMAN': organismSpec + 'Homo+sapiens', // human
                                'MOUSE': organismSpec + 'Mus+musculus', // mouse
                                'WORM':  organismSpec + 'Caenorhabditis+elegans', // worm
                                'FLY':   organismSpec + 'Drosophila+melanogaster&' + // fly
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

    render: function() {
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
                                    <HomepageChartLoader query={currentQuery} />
                                </div>
                            </div>
                            <div className="social">
                                <div className="social-news">
                                    <div className="news-header">
                                        <h2>News <a href={newsUri} title="All ENCODE news" className="twitter-ref">All news</a></h2>
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
    render: function() {
        return (
            <PanelBody>
                <div className="view-all">
                    <a href={"/matrix/" + this.props.searchBase} className="view-all-button btn btn-info btn-sm" role="button">View Assay Matrix</a>
                </div>
                <div className="col-md-4">
                    <HomepageChart {...this.props} searchBase={this.props.searchBase} />
                </div>
                <div className="col-md-4">
                    <HomepageChart2 {...this.props} searchBase={this.props.searchBase} />
                </div>
                <div className="col-md-4">
                    <HomepageChart3 {...this.props} searchBase={this.props.searchBase} />
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
    sortByAssay: function(category, e) {

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
    render: function() {
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
                                <rect id={assayList[0]} x="101.03" y="645.8" width="257.47" height="230.95"  className={"rectangle-box" + (assayCategory == assayList[0] ? " selected": "")} onClick={this.sortByAssay.bind(null, assayList[0])} onTouchEnd={this.sortByAssay.bind(null, assayList[0])} />
                                <rect id={assayList[1]} x="386.6" y="645.8" width="276.06" height="230.95"   className={"rectangle-box" + (assayCategory == assayList[1] ? " selected": "")} onClick={this.sortByAssay.bind(null, assayList[1])} onTouchEnd={this.sortByAssay.bind(null, assayList[1])} />
                                <rect id={assayList[2]} x="688.7" y="645.8" width="237.33" height="230.95"   className={"rectangle-box" + (assayCategory == assayList[2] ? " selected": "")} onClick={this.sortByAssay.bind(null, assayList[2])} onTouchEnd={this.sortByAssay.bind(null, assayList[2])} />
                                <rect id={assayList[3]} x="950.83" y="645.8" width="294.65" height="230.95"  className={"rectangle-box" + (assayCategory == assayList[3] ? " selected": "")} onClick={this.sortByAssay.bind(null, assayList[3])} onTouchEnd={this.sortByAssay.bind(null, assayList[3])} />
                                <rect id={assayList[4]} x="1273.07" y="645.8" width="373.37" height="230.95" className={"rectangle-box" + (assayCategory == assayList[4] ? " selected": "")} onClick={this.sortByAssay.bind(null, assayList[4])} onTouchEnd={this.sortByAssay.bind(null, assayList[4])} />
                                <rect id={assayList[5]} x="1674.06" y="645.8" width="236.05" height="230.95" className={"rectangle-box" + (assayCategory == assayList[5] ? " selected": "")} onClick={this.sortByAssay.bind(null, assayList[5])} onTouchEnd={this.sortByAssay.bind(null, assayList[5])} />
                                <rect id={assayList[6]} x="1937.74" y="645.8" width="227.38" height="230.95" className={"rectangle-box" + (assayCategory == assayList[6] ? " selected": "")} onClick={this.sortByAssay.bind(null, assayList[6])} onTouchEnd={this.sortByAssay.bind(null, assayList[6])} />
                            </svg>
                        </div>

                        <div className="site-banner-intro">
                            <div className="site-banner-intro-content">
                                <p>The ENCODE (Encyclopedia of DNA Elements) Consortium is an international collaboration of research groups funded by the National Human Genome Research Institute (NHGRI). The goal of ENCODE is to build a comprehensive parts list of functional elements in the human genome, including elements that act at the protein and RNA levels, and regulatory elements that control cells and circumstances in which a gene is active.</p>
                                <div className="getting-started-button">
                                    <a href="/matrix/?type=Experiment" className="btn btn-info" role="button">Get Started</a>
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

    render: function() {
        let organisms = this.props.organisms;
        return (
            <div ref="tabdisplay">
                <div className="organism-selector">
                    <a className={"single-tab" + (organisms.indexOf('HUMAN') != -1 ? " selected": "")} href="#" data-trigger onClick={this.props.handleTabClick.bind(null, 'HUMAN')}>Human</a>
                    <a className={"single-tab" + (organisms.indexOf('MOUSE') != -1 ? " selected": "")} href="#" data-trigger onClick={this.props.handleTabClick.bind(null, 'MOUSE')}>Mouse</a>
                    <a className={"single-tab" + (organisms.indexOf('WORM') != -1 ? " selected": "")} href="#" data-trigger onClick={this.props.handleTabClick.bind(null, 'WORM')}>Worm</a>
                    <a className={"single-tab" + (organisms.indexOf('FLY') != -1 ? " selected": "")} href="#" data-trigger onClick={this.props.handleTabClick.bind(null, 'FLY')}>Fly</a>
                </div>
            </div>
        );
    }

});



// Component to display the D3-based chart for Project
var HomepageChart = React.createClass({

    contextTypes: {
        location_href: React.PropTypes.string,
        navigate: React.PropTypes.func,
        projectColors: React.PropTypes.object // DataColor instance for experiment project
    },

    drawChart: function() {
        // Draw the chart of search results given in this.props.data.facets. Since D3 doesn't work
        // with the React virtual DOM, we have to load it separately using the webpack .ensure
        // mechanism. Once the callback is called, it's loaded and can be referenced through
        // require.
        require.ensure(['chart.js'], function(require) {
            var Chart = require('chart.js');
            var data = [];
            var labels = [];
            var facetData;

            // Handle cancelled GET request. We'll have made another GET request.
            if (this.props.data.status === 'error') {
                return;
            }

            var facets = this.props.data.facets;
            var assayFacet = facets.find(facet => facet.field === 'award.project');
            facetData = assayFacet ? assayFacet.terms : [];

            if(facetData.length){ // if there is data
                document.getElementById('MyEmptyChart').innerHTML = "";
                document.getElementById('MyEmptyChart').removeAttribute("class"); // clear out empty chart div

                var totalDocCount = 0;

                // for each item, set doc count, add to total doc count, add proper label, and assign color
                var colors = this.context.projectColors.colorList(facetData.map(term => term.key), {shade: 10});
                facetData.forEach(function(term, i) {
                    data[i] = term.doc_count;
                    totalDocCount += term.doc_count;
                    labels[i] = term.key;
                });

                // adding total doc count to middle of donut
                // http://stackoverflow.com/questions/20966817/how-to-add-text-inside-the-doughnut-chart-using-chart-js/24671908
                Chart.pluginService.register({
                    beforeDraw: function(chart) {
                        if(chart.chart.canvas.id == 'myChart'){
                            var width = chart.chart.width,
                                height = chart.chart.height,
                                ctx = chart.chart.ctx;

                            ctx.fillStyle = '#000000';
                            ctx.restore();
                            var fontSize = (height / 114).toFixed(2);
                            ctx.font = fontSize + "em sans-serif";
                            ctx.textBaseline = "middle";

                            var text = totalDocCount,
                                textX = Math.round((width - ctx.measureText(text).width) / 2),
                                textY = height / 2;

                            ctx.clearRect(0, 0, width, height);
                            ctx.fillText(text, textX, textY);
                            ctx.save();
                        }
                    }
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
                        legend: {
                            display: false // hiding automatically generated legend
                        },
                        legendCallback: (chart) => { // allows for legend clicking
                            facetData = _(facetData).filter(term => term.doc_count > 0);
                            var text = [];
                            text.push('<ul>');
                            for (var i = 0; i < facetData.length; i++) {
                                text.push('<li>');
                                text.push('<a href="' + '/matrix/' + this.props.searchBase + '&award.project=' + facetData[i].key  + '">'); // go to matrix view when clicked
                                text.push('<span class="chart-legend-chip" style="background-color:' + chart.data.datasets[0].backgroundColor[i] + '"></span>');
                                if (chart.data.labels[i]) {
                                    text.push('<span class="chart-legend-label">' + chart.data.labels[i] + '</span>');
                                }
                                text.push('</a></li>');
                            }
                            text.push('</ul>');
                            return text.join('');
                        },
                        onClick: (e) => {
                            // React to clicks on pie sections
                            var activePoints = this.myPieChart.getElementAtEvent(e);

                            if (activePoints[0] == null) { // if click on wrong area, do nothing
                                var placeholder = 0;
                            }
                            else{ // otherwise go to matrix view
                                var term = facetData[activePoints[0]._index].key;
                                this.context.navigate('/matrix/' + this.props.searchBase + '&award.project=' + term);
                            }
                        }
                    }
                });
                document.getElementById('chart-legend').innerHTML = this.myPieChart.generateLegend(); // generates legend

            }


            else{ //if no data

                var element = document.getElementById('MyEmptyChart');
                var chart = document.getElementById('myChart');
                var existingText = document.getElementById('p1');
                if(existingText){
                    element.removeChild(existingText);
                }

                var para = document.createElement("p");
                para.setAttribute('id', 'p1');
                var node = document.createTextNode("No data to display.");
                para.appendChild(node); // display no data error message

                element.appendChild(para);
                element.setAttribute('class', 'empty-chart'); // add class to empty-chart div

                chart.setAttribute('height', '0'); // clear chart canvas so it won't display
                document.getElementById('chart-legend').innerHTML = ''; // Clear legend
            }


        }.bind(this));

    },



    componentDidMount: function() {
        this.drawChart();
    },

    componentDidUpdate: function(){
        if (this.myPieChart) {
            this.myPieChart.destroy(); // clears old chart before creating new one
            this.drawChart();
        }
    },

    render: function() {
        return (
            <div>
                <div className="title">
                    Project
                    <center> <hr width="80%" position="static" color="blue"></hr> </center>
                </div>
                <canvas id="myChart"></canvas>
                <div id="MyEmptyChart"> </div>
                <div id="chart-legend" className="chart-legend"></div>
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

    render: function() {
        return (
            <FetchedData>
                <Param name="data" url={'/search/' + this.props.query} />
                <ChartGallery searchBase={this.props.query} />
            </FetchedData>
        );
    }

});

// Component to display the D3-based chart for Biosample
var HomepageChart2 = React.createClass({

    contextTypes: {
        navigate: React.PropTypes.func,
        biosampleTypeColors: React.PropTypes.object // DataColor instance for experiment project
    },

    drawChart: function() {

        // Draw the chart of search results given in this.props.data.facets. Since D3 doesn't work
        // with the React virtual DOM, we have to load it separately using the webpack .ensure
        // mechanism. Once the callback is called, it's loaded and can be referenced through
        // require.
        require.ensure(['chart.js'], function(require) {
            var Chart = require('chart.js');
            var data = [];
            var labels = [];
            var assayFacet;

            // Handle cancelled GET request. We'll have made another GET request.
            if (this.props.data.status === 'error') {
                return;
            }

            // Our data source will be different for computational predictions
            var computationalPredictions = this.props.searchBase === '?type=Annotation&encyclopedia_version=3';

            var facets = this.props.data.facets;
            if (computationalPredictions) {
                assayFacet = facets.find(facet => facet.field === 'biosample_type');
            } else {
                assayFacet = facets.find(facet => facet.field === 'replicates.library.biosample.biosample_type');
            }

            if(assayFacet) {
                // if there is data
                document.getElementById('MyEmptyChart2').innerHTML = "";
                document.getElementById('MyEmptyChart2').removeAttribute("class"); // clear out empty chart div

                var totalDocCount = 0;

                // for each item, set doc count, add to total doc count, add proper label, and assign color
                var colors = this.context.biosampleTypeColors.colorList(assayFacet.terms.map(term => term.key), {shade: 10});
                assayFacet.terms.forEach(function(term, i) {
                    data[i] = term.doc_count;
                    totalDocCount += term.doc_count;
                    labels[i] = term.key;
                });

                // adding total doc count to middle of donut
                // http://stackoverflow.com/questions/20966817/how-to-add-text-inside-the-doughnut-chart-using-chart-js/24671908
                Chart.pluginService.register({
                    beforeDraw: function(chart) {
                        if(chart.chart.canvas.id == 'myChart2'){
                            var width = chart.chart.width,
                                height = chart.chart.height,
                                ctx = chart.chart.ctx;

                            ctx.fillStyle = '#000000';
                            ctx.restore();
                            var fontSize = (height / 114).toFixed(2);
                            ctx.font = fontSize + "em sans-serif";
                            ctx.textBaseline = "middle";

                            var text = totalDocCount,
                                textX = Math.round((width - ctx.measureText(text).width) / 2),
                                textY = height / 2;

                            ctx.clearRect(0, 0, width, height);
                            ctx.fillText(text, textX, textY);
                            ctx.save();
                        }

                    }
                });


                // Pass the assay_title counts to the charting library to render it.
                var canvas = document.getElementById("myChart2");
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
                        legend: {
                            display: false // hiding automatically generated legend
                        },
                        legendCallback: (chart) => { // allows for legend clicking
                            var facetTerms = _(assayFacet.terms).filter(term => term.doc_count > 0);
                            var text = [];
                            var query = computationalPredictions ? 'biosample_type=' : 'replicates.library.biosample.biosample_type=';
                            text.push('<ul>');
                            for (var i = 0; i < facetTerms.length; i++) {
                                text.push('<li>');
                                text.push('<a href="/matrix/' + this.props.searchBase + '&' + query + facetTerms[i].key  + '">'); // go to matrix view when clicked
                                text.push('<span class="chart-legend-chip" style="background-color:' + chart.data.datasets[0].backgroundColor[i] + '"></span>');
                                if (chart.data.labels[i]) {
                                    text.push('<span class="chart-legend-label">' + chart.data.labels[i] + '</span>');
                                }
                                text.push('</a></li>');
                            }
                            text.push('</ul>');
                            return text.join('');
                        },
                        onClick: function(e) {
                            // React to clicks on pie sections
                            var query = computationalPredictions ? 'biosample_type=' : 'replicates.library.biosample.biosample_type=';
                            var activePoints = this.myPieChart.getElementAtEvent(e);
                            var term = assayFacet.terms[activePoints[0]._index].key;
                            this.context.navigate('/matrix/' + this.props.searchBase + '&' + query + term); // go to matrix view
                        }.bind(this)
                    }
                });

                document.getElementById('chart-legend-2').innerHTML = this.myPieChart.generateLegend(); // generates legend
            }

            else{ // if no data

                var element = document.getElementById('MyEmptyChart2');
                var chart = document.getElementById('myChart2');
                var existingText = document.getElementById('p2');
                if(existingText){
                    element.removeChild(existingText);
                }

                var para = document.createElement("p");
                para.setAttribute('id', 'p2');
                var node = document.createTextNode("No data to display.");
                para.appendChild(node); // display no data error message

                element.appendChild(para);
                element.setAttribute('class', 'empty-chart'); // add class to empty-chart div

                chart.setAttribute('height', '0'); // clear chart canvas so it won't display
                document.getElementById('chart-legend-2').innerHTML = ''; // Clear legend
            }

        }.bind(this));

    },

    componentDidMount: function() {
        this.drawChart();
    },

    componentDidUpdate: function() {
        if (this.myPieChart) {
            this.myPieChart.destroy(); // clears old chart before creating new one
            this.drawChart();
        }
    },

    render: function() {
        return (
            <div>
                <div className="title">
                    Biosample Type
                    <center> <hr width="80%" position="static" color="blue"></hr> </center>
                </div>
                <canvas id="myChart2"></canvas>
                <div id="MyEmptyChart2"> </div>
                <div id="chart-legend-2" className="chart-legend"></div>
            </div>
        );
    }
});


// Component to display the D3-based chart for Biosample
var HomepageChart3 = React.createClass({

    contextTypes: {
        navigate: React.PropTypes.func
    },

    drawChart: function() {

        // Draw the chart of search results given in this.props.data.facets. Since D3 doesn't work
        // with the React virtual DOM, we have to load it separately using the webpack .ensure
        // mechanism. Once the callback is called, it's loaded and can be referenced through
        // require.
        require.ensure(['chart.js'], function(require) {
            const Chart = require('chart.js');
            let data = [];
            let labels = [];
            let colors = [];
            let selectedAssay = (this.props.assayCategory && this.props.assayCategory !== 'COMPPRED') ? this.props.assayCategory.replace(/\+/g,' ') : '';

            // Handle cancelled GET request. We'll have made another GET request.
            if (this.props.data.status === 'error') {
                return;
            }

            let facets = this.props.data.facets;
            let assayFacet = facets.find(facet => facet.field === 'assay_slims');

            // Collect up the experiment assay_title counts to our local arrays to prepare for
            // the charts.
            if (assayFacet ) {
                // clear empty chart div
                document.getElementById('MyEmptyChart3').innerHTML = "";
                document.getElementById('MyEmptyChart3').removeAttribute("class");

                let totalDocCount = 0;

                // for each item, set doc count, add to total doc count, add proper label, and assign color
                assayFacet.terms.forEach((term, i) => {
                    data[i] = term.doc_count;
                    totalDocCount += term.doc_count;
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
                        legend: {
                            display: false // hiding automatically generated legend
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
                        onClick: (e) => {
                            // React to clicks on pie sections
                            var query = 'assay_slims=';
                            var activePoints = this.myPieChart.getElementAtEvent(e);
                            var term = assayFacet.terms[activePoints[0]._index].key;
                            this.context.navigate('/matrix/' + this.props.searchBase + '&' + query + term); // go to matrix view
                        }
                    }
                });
            }

            else{ // if no data

                var element = document.getElementById('MyEmptyChart3');
                var chart = document.getElementById('myChart3');
                var existingText = document.getElementById('p3');
                if(existingText){
                    element.removeChild(existingText);
                }

                var para = document.createElement("p");
                para.setAttribute('id', 'p3');
                var node = document.createTextNode("No data to display.");
                para.appendChild(node); // display no data error message

                element.appendChild(para);
                element.setAttribute('class', 'empty-chart'); // add class to empty-chart div

                chart.setAttribute('height', '0'); // clear chart canvas so it won't display

            }

        }.bind(this));

    },

    componentDidMount: function() {
        this.drawChart();
    },

    componentDidUpdate: function() {
        if (this.myPieChart) {
            this.myPieChart.destroy(); // clears old chart before creating new one
            this.drawChart();
        }
    },

    render: function() {
        return (
            <div>
                <div className="title">
                    Assay Categories
                </div>
                <center> <hr width="80%"></hr> </center>
                <canvas id="myChart3" height="240"></canvas>
                <div id="MyEmptyChart3"> </div>
                <div id="chart-legend-3" className="chart-legend"></div>
            </div>
        );
    }

});


// Send a GET request for the most recent five news posts.
var NewsLoader = React.createClass({
    propTypes: {
        newsLoaded: React.PropTypes.func.isRequired // Called parent once the news is loaded
    },

    render: function() {
        return <FetchedItems {...this.props} url={newsUri + '&limit=5'} Component={News} ignoreErrors newsLoaded={this.props.newsLoaded} />;
    }
});


// Render the most recent five news posts
var News = React.createClass({
    propTypes: {
        newsLoaded: React.PropTypes.func.isRequired // Called parent once the news is loaded
    },

    componentDidMount: function() {
        this.props.newsLoaded();
    },

    render: function() {
        var items = this.props.items;
        if (items && items.length) {
            return (
                <div className="news-listing">
                    {items.map(item => {
                        return (
                            <div key={item['@id']} className="news-listing-item">
                                <h3>{item.title}</h3>
                                <h4>{moment.utc(item.date_created).format('MMMM D, YYYY')}</h4>
                                <div className="news-excerpt">{item.news_excerpt}</div>
                                <div className="news-listing-readmore">
                                    <a className="btn btn-info btn-sm" href={item['@id']} title={'View news post for ' + item.title} key={item['@id']}>Read more</a>
                                </div>
                            </div>
                        );
                    })}
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

    injectTwitter: function() {
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

    componentDidMount: function() { // twitter script from API
        if (!this.initialized && this.props.height) {
            this.injectTwitter();
        }
    },

    componentDidUpdate: function() {
        if (!this.initialized && this.props.height) {
            this.injectTwitter();
        }
    },

    render: function() {
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
                    widget-id= "encodedcc"
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

