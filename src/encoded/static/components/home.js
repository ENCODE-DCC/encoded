'use strict';
var React = require('react');
var _ = require('underscore');
var moment = require('moment');
var globals = require('./globals');
var {FetchedData, FetchedItems, Param} = require('./fetched');
var cloneWithProps = require('react/lib/cloneWithProps');
var panel = require('../libs/bootstrap/panel');
var {Panel, PanelBody, PanelHeading} = panel;


// Main page component to render the home page
var Home = module.exports.Home = React.createClass({

    getInitialState: function(){ // sets initial state for current and newtabs
        return {
            current: "?type=Experiment&status=released", // show all released experiments
            newtabs: [], // create empty array of selected tabs
            assayCategory: "",
            socialHeight: 0
        };
    },

    handleAssayCategoryClick: function(assay){
        var oldLink = this.state.current; // getting original search
        var tempAssay = assay;

        // if assay category already clicked then clear tempAssay essentially unclicking it
        if(this.state.assayCategory == assay){
            tempAssay = "";
        }

        this.setState({
            assayCategory: tempAssay // set assayCategory to tempAssay
        });

        // checking to see if it is currently computational predictions
        var indexOfExperiment = oldLink.indexOf("?type=Experiment&status=released");
        if (indexOfExperiment === -1){ // if computational predictions
            // keeps any organism parameters and puts back normal searchbase
            oldLink = "?type=Experiment&status=released";
        }

        // getting index of "&assay_slims=" in original search link if it's there
        var startingIndex = oldLink.search("&assay_slims=");

        // if &assay_slims already is in original search link, then remove it so we can add
        // the correct "&assay_slims="
        if (startingIndex != -1) {

            // adding the length of "&assay_slims" to make endingIndex the index of the
            // category
            var endingIndex = startingIndex + 13;

            // either get to end of string or find next parameter starting with "&"
            while (endingIndex < oldLink.length-1 && oldLink.substring(endingIndex, endingIndex + 1) != "&") {

                // increase endingIndex until the end of the "&assay_slims=" parameter
                endingIndex++;
            }

            // if did not reach end of string, "&assay_slims=" is in middle of search
            if(endingIndex != oldLink.length-1){

                // assay_slims part is from (startingIndex, endingIndex), so cut that out
                // of oldLink
                oldLink = oldLink.substr(0, startingIndex) + oldLink.substr(endingIndex);
            }
            else{ // "&assay_slims=" is at end of search

                // assay_slims is from (startingIndex, oldLink.length, so cut that out
                oldLink = oldLink.substr(0, startingIndex);
            }
        }
        if (tempAssay != "") { // if not unclicking
            // add in assay category parameter to search
            if (assay === 'COMPPRED') {
                oldLink = '?type=Annotation&encyclopedia_version=3';
            } else {
                oldLink = oldLink + '&assay_slims=' + tempAssay;
            }
        }

        this.callback(oldLink); // updating current through callback

    },


    // pass in string with organism query and either adds or removes tab from list of selected tabs
    handleTabClick: function(tab){

        var tempArray = _.clone(this.state.newtabs); // creates a copy of this.state.newtabs
        var finalLink = _.clone(this.state.current); // clones current

        if (tempArray.indexOf(tab) == -1) { // if tab isn't already in array, then add it
            tempArray.push(tab);
        }
        else{ // otherwise if it is in array, remove it from array and from link
            var indexToRemoveArray = tempArray.indexOf(tab);
            tempArray.splice(indexToRemoveArray, 1);
            var indexToRemoveLink = finalLink.indexOf(tab);
            finalLink = finalLink.substr(0, indexToRemoveLink) + finalLink.substr(indexToRemoveLink + tab.length);
        }

        var organismString = ""; // create empty string to add all organisms selected
        for(var x = 0; x < tempArray.length; x++){
            if(finalLink.indexOf(tempArray[x]) == -1){ // if organisms were previously not selected
                organismString = organismString + tempArray[x]; // then add them in
            }
        }

        finalLink = finalLink + organismString; // add in updated organism queries to link

        this.setState({
            newtabs: tempArray // update newtabs
        });

        this.callback(finalLink); // updated current, updating homepage charts

    },

    callback: function(newUrl){ // updates current when it changes
        this.setState({
            current: newUrl
        });
    },

    newsLoaded: function() {
        // Called once the news content gets loaded
        var newsEl = this.refs.newslisting.getDOMNode();
        this.setState({socialHeight: newsEl.clientHeight});
    },

    render: function() { // renders home page
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
                            <AssayClicking current={this.state.current} callback={this.callback} assayCategory={this.state.assayCategory} handleAssayCategoryClick={this.handleAssayCategoryClick}/>
                            <div className="organism-tabs">
                                <TabClicking handleTabClick={this.handleTabClick} newtabs={this.state.newtabs}/>
                            </div>
                            <div className="graphs">
                                <div className="row">
                                    <HomepageChartLoader searchBase={this.state.current} callback={this.callback} />
                                </div>
                            </div>
                            <div className="social">
                                <div className="social-news">
                                    <div className="news-header">
                                        <h2>News <a href="/search/?type=Page&news=true" title="All ENCODE news" className="twitter-ref">All news</a></h2>
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
            <div>
                <div className="col-md-4">
                    <HomepageChart {...this.props} searchBase={this.props.searchBase} />
                </div>
                <div className="col-md-4">
                    <HomepageChart2 {...this.props} searchBase={this.props.searchBase} />
                </div>
                <div className="col-md-4">
                    <HomepageChart3 {...this.props} searchBase={this.props.searchBase} />
                    <div className="view-all">
                        <a href={"/matrix/" + this.props.searchBase} className="view-all-button btn btn-info btn-lg" role="button"> View Selected </a>
                    </div>
                </div>
            </div>
        );
    }
});


// Component to allow clicking boxes on classic image
var AssayClicking = React.createClass({
    propTypes: {
        current: React.PropTypes.string,
        callback: React.PropTypes.func,
        assayCategory: React.PropTypes.string
    },

    // Sets value of updatedLink to current to allow easy modification, sets value of currentAssay
    // to assayCategory, creates assayList with ids of assay categories for rectangles in SVG
    getInitialState: function(){
        return {
            updatedLink: this.props.current,
            currentAssay: this.props.assayCategory,
            assayList: ["3D+chromatin+structure",
                        "DNA+accessibility",
                        "DNA+binding",
                        "DNA+methylation",
                        "COMPPRED",
                        "Transcription",
                        "RNA+binding"]
        };
    },

    // Properly adds or removes assay category from link
    sortByAssay: function(category) {
        this.props.handleAssayCategoryClick(category); // handles assay category click
        this.setState({currentAssay: category}); // updates current assay
    },

    // Renders classic image and svg rectangles
    render: function() {
        return (
            <div ref="graphdisplay">
                <div className="overall-classic">

                    <h1>ENCODE: Encyclopedia of DNA Elements</h1>

                    <div className="site-banner">
                        <div className="site-banner-img">
                            <img src="static/img/classic-image.jpg" />

                            <svg id="site-banner-overlay" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2260 1450" className="classic-svg">
                                <rect id={this.state.assayList[0]} x="101.03" y="645.8" width="257.47" height="230.95"  className={"rectangle-box" + (this.props.assayCategory == this.state.assayList[0] ? " selected": "")} onClick={this.sortByAssay.bind(null, this.state.assayList[0])} />
                                <rect id={this.state.assayList[1]} x="386.6" y="645.8" width="276.06" height="230.95"   className={"rectangle-box" + (this.props.assayCategory == this.state.assayList[1] ? " selected": "")} onClick={this.sortByAssay.bind(null, this.state.assayList[1])} />
                                <rect id={this.state.assayList[2]} x="688.7" y="645.8" width="237.33" height="230.95"   className={"rectangle-box" + (this.props.assayCategory == this.state.assayList[2] ? " selected": "")} onClick={this.sortByAssay.bind(null, this.state.assayList[2])} />
                                <rect id={this.state.assayList[3]} x="950.83" y="645.8" width="294.65" height="230.95"  className={"rectangle-box" + (this.props.assayCategory == this.state.assayList[3] ? " selected": "")} onClick={this.sortByAssay.bind(null, this.state.assayList[3])} />
                                <rect id={this.state.assayList[4]} x="1273.07" y="645.8" width="373.37" height="230.95" className={"rectangle-box" + (this.props.assayCategory == this.state.assayList[4] ? " selected": "")} onClick={this.sortByAssay.bind(null, this.state.assayList[4])} />
                                <rect id={this.state.assayList[5]} x="1674.06" y="645.8" width="236.05" height="230.95" className={"rectangle-box" + (this.props.assayCategory == this.state.assayList[5] ? " selected": "")} onClick={this.sortByAssay.bind(null, this.state.assayList[5])} />
                                <rect id={this.state.assayList[6]} x="1937.74" y="645.8" width="227.38" height="230.95" className={"rectangle-box" + (this.props.assayCategory == this.state.assayList[6] ? " selected": "")} onClick={this.sortByAssay.bind(null, this.state.assayList[6])} />
                            </svg>
                        </div>

                        <div className="site-banner-intro">
                            <div className="site-banner-intro-content">
                                <p>The ENCODE (Encyclopedia of DNA Elements) Consortium is an international collaboration of research groups funded by the National Human Genome Research Institute (NHGRI). The goal of ENCODE is to build a comprehensive parts list of functional elements in the human genome, including elements that act at the protein and RNA levels, and regulatory elements that control cells and circumstances in which a gene is active.</p>
                                <div className="getting-started-button">
                                    <a href="/help/getting-started" className="btn btn-info btn-lg" role="button">Getting Started</a>
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
        handleTabClick: React.PropTypes.func
    },

    // Gives proper queries to tabs
    getInitialState: function(){
        return {
            queryStrings: ['&replicates.library.biosample.donor.organism.scientific_name=Homo+sapiens', // human
                            '&replicates.library.biosample.donor.organism.scientific_name=Mus+musculus', // mouse
                            '&replicates.library.biosample.donor.organism.scientific_name=Caenorhabditis+elegans', // worm

                            '&replicates.library.biosample.donor.organism.scientific_name=Drosophila+melanogaster' + // fly
                            '&replicates.library.biosample.donor.organism.scientific_name=Drosophila+pseudoobscura' +
                            '&replicates.library.biosample.donor.organism.scientific_name=Drosophila+simulans' +
                            '&replicates.library.biosample.donor.organism.scientific_name=Drosophila+mojavensis' +
                            '&replicates.library.biosample.donor.organism.scientific_name=Drosophila+ananassae' +
                            '&replicates.library.biosample.donor.organism.scientific_name=Drosophila+virilis' +
                            '&replicates.library.biosample.donor.organism.scientific_name=Drosophila+yakuba']
        };
    },

    render: function() {
        return (
            <div ref="tabdisplay">
                <div className="organism-selector">
                    <a className={"single-tab" + (this.props.newtabs.indexOf(this.state.queryStrings[0]) != -1 ? " selected": "")} href="#" data-trigger onClick={this.props.handleTabClick.bind(null, this.state.queryStrings[0])}>Human</a>
                    <a className={"single-tab" + (this.props.newtabs.indexOf(this.state.queryStrings[1]) != -1 ? " selected": "")} href="#" data-trigger onClick={this.props.handleTabClick.bind(null, this.state.queryStrings[1])}>Mouse</a>
                    <a className={"single-tab" + (this.props.newtabs.indexOf(this.state.queryStrings[2]) != -1 ? " selected": "")} href="#" data-trigger onClick={this.props.handleTabClick.bind(null, this.state.queryStrings[2])}>Worm</a>
                    <a className={"single-tab" + (this.props.newtabs.indexOf(this.state.queryStrings[3]) != -1 ? " selected": "")} href="#" data-trigger onClick={this.props.handleTabClick.bind(null, this.state.queryStrings[3])}>Fly</a>
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
                                text.push('<a href="' + this.props.data['@id'] + '&award.project=' + facetData[i].key  + '">'); // go to matrix view when clicked
                                text.push('<span style="background-color:' + chart.data.datasets[0].backgroundColor[i] + '"></span>');
                                if (chart.data.labels[i]) {
                                    text.push(chart.data.labels[i]);
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

                            this.myPieChart.update();
                            this.myPieChart.render();
                            this.forceUpdate();

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
        searchBase: React.PropTypes.string,
        callback: React.PropTypes.func
    },

    render: function() {
        return (
            <FetchedData ignoreErrors>
                <Param name="data" url={'/search/' + this.props.searchBase} />
                <ChartGallery searchBase={this.props.searchBase} />
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
                                text.push('<a href="' + this.props.data['@id'] + '&' + query + facetTerms[i].key  + '">'); // go to matrix view when clicked
                                text.push('<span style="background-color:' + chart.data.datasets[0].backgroundColor[i] + '"></span>');
                                if (chart.data.labels[i]) {
                                    text.push(chart.data.labels[i]);
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
            var Chart = require('chart.js');
            var colorList = [
                '#871F78',
                '#FFB90F',
                '#003F87',
                '#3D9140',
                '#E5E4E2'
            ];
            var colors = [];

            // Handle cancelled GET request. We'll have made another GET request.
            if (this.props.data.status === 'error') {
                return;
            }

            // Get the assay_title counts from the facets
            var facets = this.props.data.facets;
            var assayFacet = facets.find(facet => facet.field === 'month_released');
            var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

            // Collect up the experiment assay_title counts to our local arrays to prepare for
            // the charts.
            if (assayFacet && assayFacet.terms.length ) {
                // clear empty chart div
                document.getElementById('MyEmptyChart3').innerHTML = "";
                document.getElementById('MyEmptyChart3').removeAttribute("class");

                // Sort assayFacet terms array by year/month, and get most recent six entries
                var terms = assayFacet.terms.sort((a, b) => {
                    // Split "Month, YEAR" into array ["Month", "YEAR"];
                    var sortDataA = a.key.split(', ');
                    var sortDataB = b.key.split(', ');

                    // Convert arrays to "YYYYMM" format
                    var normalizedDateA = sortDataA[1] + globals.zeroFill(months.indexOf(sortDataA[0]), 2);
                    var normalizedDateB = sortDataB[1] + globals.zeroFill(months.indexOf(sortDataB[0]), 2);
                    return (normalizedDateA < normalizedDateB) ? -1 : ((normalizedDateA > normalizedDateB) ? 1 : 0);
                }).slice(-6);

                // Extract counts and abbreviated months from sortedReleases, so we can pass these
                // to the charting code.
                var xlabels = [];
                var labels = [];
                var data = terms.map(term => {
                    // Collect abbreviated and full month names corresponding to term month names;
                    // needed to create the chart.
                    var month = term.key.split(', ')[0];
                    labels.push(term.key);
                    xlabels.push(month.substring(0, 3));
                    return term.doc_count;
                });

                // gives bar graph a constant green color
                colors = ['#96e528', '#96e528', '#96e528', '#96e528', '#96e528', '#96e528'];


                // Pass the counts to the charting library to render it.
                var canvas = document.getElementById("myChart3");
                var ctx = canvas.getContext("2d");
                this.myBarChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: labels, // full labels
                        xLabels: xlabels, // abbreviated labels
                        datasets: [{
                            data: data,
                            backgroundColor: colors,
                            label: "Number of Released Experiments"
                        }]
                    },
                    options: {
                        tooltips: {
                            callbacks: {
                                title: function(tooltipItems, data){ // show full label in hovering
                                    return data.labels[tooltipItems[0].index];
                                }
                            }
                        },
                        legend: {
                            display: false // hiding legend
                        },
                        scales: {
                            xAxes: [{
                                ticks: { // http://www.chartjs.org/docs/ tick configuration
                                    maxRotation: 30, // max rotation of 30 degrees
                                }
                            }],
                            yAxes: [{
                                scaleLabel: {
                                    display: true,
                                    labelString: 'Experiments'
                                }
                            }]
                        },

                        onClick: (e) => {
                            // React to clicks on pie sections
                            var activePoints = this.myBarChart.getElementAtEvent(e);
                            var term = labels[activePoints[0]._index];
                            this.context.navigate('/matrix' + this.props.searchBase + '&month_released=' + term); // goes to matrix view
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
        if (this.myBarChart) {
            this.myBarChart.destroy(); // clears old chart before creating new one
            this.drawChart();
        }
    },

    render: function() {
        return (
            <div>
                <div className="title">
                    Recent Releases
                </div>
                <center> <hr width="80%"></hr> </center>
                <canvas id="myChart3"></canvas>
                <div id="MyEmptyChart3"> </div>
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
        return <FetchedItems {...this.props} url="/search/?type=Page&news=true&limit=5" Component={News} ignoreErrors newsLoaded={this.props.newsLoaded} />;
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
                            <a href={item['@id']} title={'View news post for ' + item.title} key={item['@id']}>
                                <h3>{item.title}</h3>
                                <h4>{moment.utc(item.date_created).format('MMMM D, YYYY')}</h4>
                                <div className="news-excerpt">{item.news_excerpt}</div>
                            </a>
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

