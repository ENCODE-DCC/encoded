'use strict';
var React = require('react');
var _ = require('underscore');
var globals = require('./globals');
var {FetchedData, Param} = require('./fetched');
var cloneWithProps = require('react/lib/cloneWithProps');
var panel = require('../libs/bootstrap/panel');
var {Panel, PanelBody, PanelHeading} = panel;


// Main page component to render the home page
var Home = module.exports.Home = React.createClass({

    getInitialState: function(){ // sets initial state for current and newtabs
        return {
            current: "?type=Experiment&status=released", // show all released experiments
            newtabs: [], // create empty array of selected tabs
            assayCategory: ""
        };
    },

    handleAssayCategoryClick: function(assay){
        var oldLink = this.state.current; // getting original search
        var tempAssay = assay;

        if(tempAssay == '?type=Annotation&encyclopedia_version=3'){
            if(oldLink.indexOf('?type=Annotation&encyclopedia_version=3') != -1){
                oldLink = "?type=Experiment&status=released";
            }
            else{
                oldLink = '?type=Annotation&encyclopedia_version=3';
            }

        }
        else {
            console.log("SHOULD BE CHROMATIN: " + assay);
        
            if(this.state.assayCategory == assay){
                tempAssay = "";
                console.log("NOT IN FIRST TIME, ONLY WHEN CLICKED");
            }

            this.setState({
                assayCategory: tempAssay
            });

            var indexOfExperiment = oldLink.indexOf("?type=Experiment&status=released");
            if (indexOfExperiment == -1){
                oldLink = oldLink.substring(39);
                oldLink = "?type=Experiment&status=released" + oldLink;
            }

            
            var startingIndex = oldLink.search("&assay_slims="); // getting index of "&assay_slims=" in original search link if it's there
            
            if (startingIndex != -1) { // if &assay_slims already is in original search link, then remove it so we can add the correct "&assay_slims="
                var endingIndex = startingIndex + 13; // adding the length of "&assay_slims" to make endingIndex the index of the category
                
                while (endingIndex < oldLink.length-1 && oldLink.substring(endingIndex, endingIndex + 1) != "&") { // either get to end of string or find next parameter starting with "&"
                    endingIndex++; // increase endingIndex until the end of the "&assay_slims=" parameter
                }
                
                if(endingIndex != oldLink.length-1){ // if did not reach end of string, "&assay_slims=" is in middle of search
                    oldLink = oldLink.substr(0, startingIndex) + oldLink.substr(endingIndex +1); // assay_slims part is from (startingIndex, endingIndex), so cut that out of oldLink
                }
                else{ // "&assay_slims=" is at end of search
                    oldLink = oldLink.substr(0, startingIndex); // assay_slims is from (startingIndex, oldLink.length, so cut that out
                }
                console.log("oldLink should be completely empty of all assay cateogry: " + oldLink);
            }
            if (tempAssay != "") {
                console.log("WHEN NOT CLEARED");
                oldLink = oldLink + '&assay_slims=' + tempAssay;
            }
            console.log("TEMPASSAY SHOULD BE CHROMATIN AGAIN: " + tempAssay);
            
            console.log("CLEARED " + oldLink);

        }
        
        this.callback(oldLink); // updating current through callback

    },


    handleTabClick: function(tab){ // pass in string with organism query and either adds or removes tab from list of selected tabs
        
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

    render: function() { // renders home page
        return (
            
            <div className="whole-page">

                <header class="row">
                    <div class="col-sm-12">
                        <h1 className="page-title">
                            
                        </h1>
                    </div>
                </header>
                <div className="row">
                    
                        <div className="col-xs-12">
                            
                            <AssayClicking current={this.state.current} callback={this.callback} assayCategory={this.state.assayCategory} handleAssayCategoryClick={this.handleAssayCategoryClick}/>
                            
                            <Panel>
                            <TabClicking handleTabClick={this.handleTabClick} newtabs={this.state.newtabs}/>
                            <div className="graphs clearfix" >
                                <div className="row">
                                    <div className="col-sm-4">
                                        <div className="title">
                                            Project
                                            <center> <hr width="80%" position="static" color="blue"></hr> </center>
                                        </div>
                                        
                                        <HomepageChartLoader searchBase={this.state.current} 
                                                    callback={this.callback}/>
                                        <div id="chart-legend" className="chart-legend"></div>
                                
                                    </div>
                                    <div className="col-sm-4">
                                        <div className="title">
                                            Biosample Type
                                        </div>
                                        <center> <hr width="80%"></hr> </center>
                                        <HomepageChartLoader2 searchBase={this.state.current}
                                                 callback={this.callback}/>
                                    </div>
                                    <div className="col-sm-4">
                                        <div className="title">
                                            Data Released
                                        </div>
                                        <center> <hr width="80%"></hr> </center>
                                        <HomepageChartLoader3 searchBase={this.state.current}
                                                 callback={this.callback}/>
                                    </div>
                                </div>
                                <div className="view-all">
                                        <a href={"/matrix/" + this.state.current} className="view-all-button btn btn-info btn-lg" role="button"> View All </a>
                                </div>
                            </div>

                            </Panel>
                        </div>
                    </div>
                    <div className="row">
                        <div className="col-md-9">
                            <Panel>
                                <div className="getting-started">
                                    <PanelBody addClasses="description"> 
                                                
                                        The ENCODE (Encyclopedia of DNA Elements) Consortium is an international collaboration of research groups funded by the National Human Genome Research Institute (NHGRI). The goal of ENCODE is to build a comprehensive parts list of functional elements in the human genome, including elements that act at the protein and RNA levels, and regulatory elements that control cells and circumstances in which a gene is active.
                                                
                                    </PanelBody>
                                    <a href="/help/getting-started" className="getting-started-button btn btn-info btn-lg" role="button"> Getting Started </a>
                                    <img src="static/img/getting-started.jpg" className="getting-started-image"/>
                                </div>
                            </Panel>
                        </div>
                    
                        
                        <div className="col-md-3">
                                
                            <Panel>
                            <TwitterWidget/>
                            </Panel>
                        </div>
                    
                </div>
                
            </div>
            
        );
    }

});

// Creates twitter widget
var TwitterWidget = React.createClass({ 
    componentDidMount: function() { // twitter script from API
        var js, link;
        link = this.refs.link.getDOMNode();
        if (!this.initialized) {
            this.initialized = true;
            js = document.createElement("script");
            js.id = "twitter-wjs";
            js.src = "//platform.twitter.com/widgets.js";
            return link.parentNode.appendChild(js);
        }
    },
    render: function() {
        var content, ref2, title, widget;
        return (
            <a
            ref= "link"
            className= "twitter-timeline"
            href= "https://twitter.com/encodedcc" // from encodedcc twitter
            widget-id= "encodedcc" 
            
            data-screen-name="EncodeDCC"
            //data-tweet-limit = "4"
            //data-width = "300"
            data-height = "720" // height so it matches with rest of site
            ></a>
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

    // Sets value of updatedLink to current to allow easy modification
    getInitialState: function(){
        return {
            updatedLink: this.props.current,
            currentAssay: this.props.assayCategory,
            assayList: ["3D+chromatin+structure", 
                        "DNA+accessibility",
                        "DNA+binding",
                        "DNA+methylation",
                        "",
                        "Transcription",
                        "RNA+binding"]
        };
    },

    // Properly adds or removes assay category from link
    sortByAssay: function(category) {
        // var oldLink = this.props.current; // getting original search
        // var startingIndex = oldLink.search("&assay_slims="); // getting index of "&assay_slims=" in original search link if it's there
        
        // if (startingIndex != -1) { // if &assay_slims already is in original search link, then remove it so we can add the correct "&assay_slims="
        //     var endingIndex = startingIndex + 13; // adding the length of "&assay_slims" to make endingIndex the index of the category
            
        //     while (endingIndex < oldLink.length-1 && oldLink.substring(endingIndex, endingIndex + 1) != "&") { // either get to end of string or find next parameter starting with "&"
        //         endingIndex++; // increase endingIndex until the end of the "&assay_slims=" parameter
        //     }
            
        //     if(endingIndex != oldLink.length-1){ // if did not reach end of string, "&assay_slims=" is in middle of search
        //         oldLink = oldLink.substr(0, startingIndex) + oldLink.substr(endingIndex +1); // assay_slims part is from (startingIndex, endingIndex), so cut that out of oldLink
        //     }
        //     else{ // "&assay_slims=" is at end of search
        //         oldLink = oldLink.substr(0, startingIndex); // assay_slims is from (startingIndex, oldLink.length, so cut that out
        //     }
        // }
        
        this.props.handleAssayCategoryClick(category); // updates assay category
        console.log("should be empty: " + this.state.currentAssay);
        this.setState({currentAssay: category});
        console.log("should be dna somethign: " + this.state.currentAssay);
        //this.props.callback(oldLink + '&assay_slims=' + category); // updating current through callback
        //this.setState({updatedLink: oldLink + '&assay_slims=' + category}); // updating updatedLink

    },

    // Binds clicking to SVG rectangles
    bindClickHandlers: function(d3, el) {
        // Add click event listeners to each rectangle
        var svg = el[0];
        el.on('click', rect => {
            this.sortByAssay(rect); // calls function to properly add in rectangle to link
        });
    },


    componentDidMount: function() {
        // Since D3 doesn't work
        // with the React virtual DOM, we have to load it separately using the webpack .ensure
        // mechanism. Once the callback is called, it's loaded and can be referenced through
        // require.

        // Requires d3, selects rectangles, and calls bindClickHandlers
        require.ensure(['d3'], function(require) {
            if (this.refs.graphdisplay) {
                this.d3 = require('d3');
            
                var allRects = this.d3.selectAll("rect.rectangle-box");
                var dataset = [];
                for(var x = 0; x < allRects[0].length; x++){
                    dataset.push(allRects[0][x].id);
                }

                var el = this.d3.selectAll("rect.rectangle-box")
                    .data(dataset);

                this.bindClickHandlers(this.d3, el);
            }

                
        }.bind(this));


        var temp = document.getElementById("graphdisplay");

    },

    // Renders classic image and svg rectangles
    render: function() {
        return (
            <Panel ref="graphdisplay"> 
             <div className="overall-classic">

                    <img src="static/img/classic-image.jpg" className="classicImage"/> 
                    
                    <svg id="classic-image-svg-overlay" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 3253 1440" className="classic-svg">
                    
                    <rect id = {this.state.assayList[0]} x="928.1" y="859.1" class="st0" width="190.2" height="171.6" className={"rectangle-box" + (this.props.assayCategory == this.state.assayList[0] ? " selected": "")}/>
                    <rect id = {this.state.assayList[1]} x="1132.8" y="859.1" class="st0" width="202.6" height="171.6" className={"rectangle-box" + (this.props.assayCategory == this.state.assayList[1] ? " selected": "")}/>
                    <rect id = {this.state.assayList[2]} x="1354.1" y="859.1" class="st0" width="171.6" height="171.6" className={"rectangle-box" + (this.props.assayCategory == this.state.assayList[2] ? " selected": "")}/>
                    <rect id = {this.state.assayList[3]} x="1538.1" y="859.1" class="st0" width="213" height="171.6" className={"rectangle-box" + (this.props.assayCategory == this.state.assayList[3] ? " selected": "")}/>
                    <rect id = {this.state.assayList[4]} x="1771.7" y="859.1" class="st0" width="266.7" height="171.6" onClick={this.props.handleAssayCategoryClick.bind(null, '?type=Annotation&encyclopedia_version=3')} className={"rectangle-box" + (this.props.current.indexOf('?type=Annotation&encyclopedia_version=3') != -1 ? " selected": "")}/>
                    <rect id = {this.state.assayList[5]} x="2057.1" y="859.1" class="st0" width="171.6" height="171.6" className={"rectangle-box" + (this.props.assayCategory == this.state.assayList[5] ? " selected": "")}/>
                    <rect id = {this.state.assayList[6]} x="2247.3" y="859.1" class="st0" width="163.3" height="175.8" className={"rectangle-box" + (this.props.assayCategory == this.state.assayList[6] ? " selected": "")}/>
                    
                    </svg>
                    
                    

                </div>
            </Panel>
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

   


    componentDidMount: function() {

        var tabBoxes = document.getElementById("tabdisplay");

    },

    render: function() {
        return (
            <div ref="tabdisplay"> 
                <div className="tabTable">

                <table>
                    <tr>
                        <td> <a className={"single-tab" + (this.props.newtabs.indexOf(this.state.queryStrings[0]) != -1 ? " selected": "")} href="#" data-trigger onClick={this.props.handleTabClick.bind(null, this.state.queryStrings[0])}>Human</a></td>
                        <td> <a className={"single-tab" + (this.props.newtabs.indexOf(this.state.queryStrings[1]) != -1 ? " selected": "")} href="#" data-trigger onClick={this.props.handleTabClick.bind(null, this.state.queryStrings[1])}>Mouse</a></td>
                        <td> <a className={"single-tab" + (this.props.newtabs.indexOf(this.state.queryStrings[2]) != -1 ? " selected": "")} href="#" data-trigger onClick={this.props.handleTabClick.bind(null, this.state.queryStrings[2])}>Worm</a></td>
                        <td> <a className={"single-tab" + (this.props.newtabs.indexOf(this.state.queryStrings[3]) != -1 ? " selected": "")} href="#" data-trigger onClick={this.props.handleTabClick.bind(null, this.state.queryStrings[3])}>Fly</a></td>
                    </tr>
                </table>
                    

                </div>
            </div>
        );
    }

});






// Component to display the D3-based chart for Project
var HomepageChart = React.createClass({

    contextTypes: {
        location_href: React.PropTypes.string,
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
                '#FF4F4D',
                '#10A0F6',
                '#FFBC01',
                '#6A71E5',
                '#4EB266',
                'A3A4A8',
                '61D1FD',
                'FFFFFF'
            ];
            var colorList2 = [
                '#9C008A',
                '#FDC325',
                '#33298C',
                '#179A53',
                '#E5E4E2'
            ];
            var data = [];
            var labels = [];
            var colors = [];
            var tempColors = ['0000FF'];

            // Get the assay_title counts from the facets
            var facets = this.props.data.facets;
            var assayFacet = facets.find(facet => facet.field === 'award.project');

            // Collect up the experiment assay_title counts to our local arrays to prepare for
            // the charts.
            var totalDocCount = 0;
            assayFacet.terms.forEach(function(term, i) {
                data[i] = term.doc_count;
                totalDocCount += term.doc_count;
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
                    legend: {
                        display: false
                    },
                    onClick: (e) => {
                        // React to clicks on pie sections
                        var activePoints = this.myPieChart.getElementAtEvent(e);

                        if (activePoints[0] == null) {
                            var placeholder = 0;
                        }
                        else{
                            var term = assayFacet.terms[activePoints[0]._index].key;
                            this.context.navigate(this.props.data['@id'] + '&award.project=' + term);
                        }

                        
                        this.myPieChart.update();
                        this.myPieChart.render();
                        this.forceUpdate();
                        var test = document.getElementById('chart-legend').innerHTML = this.myPieChart.generateLegend();
                    }
                }
            });

        }.bind(this));

    
        
    },

    

    componentDidMount: function() {
        this.drawChart();
        //document.getElementById('chart-legend').innerHTML = this.myPieChart.generateLegend();
    },

    componentDidUpdate: function(){
        this.myPieChart.destroy(); // clears old chart before creating new one
        this.drawChart();
    },

    render: function() {

        return (
            <div>
                <canvas id="myChart" width="0" height="0"></canvas>
                
            </div>
        );
    }

});




// Initiates the GET request to search for experiments, and then pass the data to the HomepageChart
// component to draw the resulting chart.
var HomepageChartLoader = React.createClass({
    propTypes: {
        
        callback: React.PropTypes.func
    },


    render: function() {
        console.log("searchBase: " + this.props.searchBase);
        return (
            <FetchedData>
                <Param name="data" url={'/matrix/' + this.props.searchBase} />
                <HomepageChart searchBase={this.props.searchBase + '&'} />
                
            </FetchedData>
        );
    }

});

// Component to display the D3-based chart for Biosample
var HomepageChart2 = React.createClass({

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
                '#FF4F4D',
                '#10A0F6',
                '#FFBC01',
                '#6A71E5',
                '#4EB266',
                'A3A4A8',
                '61D1FD',
                'FFFFFF'
            ];
            var data = [];
            var labels = [];
            var colors = [];

            // Get the assay_title counts from the facets
            var facets = this.props.data.facets;
            var assayFacet = facets.find(facet => facet.field === 'replicates.library.biosample.biosample_type');

            // Collect up the experiment assay_title counts to our local arrays to prepare for
            // the charts.
            assayFacet.terms.forEach(function(term, i) {
                data[i] = term.doc_count;
                labels[i] = term.key;
                colors[i] = colorList[i % colorList.length];
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
                    onClick: (e) => {
                        // React to clicks on pie sections
                        var activePoints = this.myPieChart.getElementAtEvent(e);
                        var term = assayFacet.terms[activePoints[0]._index].key;
                        this.context.navigate(this.props.data['@id'] + '&y.limit=&replicates.library.biosample.biosample_type=' + term);
                    }
                }
            });

        }.bind(this));

    },

    componentDidMount: function() {
        this.drawChart();
    },

    componentDidUpdate: function() {
        this.myPieChart.destroy(); // clears old chart before creating new one
        this.drawChart();
    },

    render: function() {
        return (
            <canvas id="myChart2" width="0" height="0"></canvas>
        );
    }

});

var HomepageChartLoader2 = React.createClass({
    propTypes: {
        
        callback: React.PropTypes.func
    },

    render: function() {
        return (
            <FetchedData>
                <Param name="data" url={'/matrix/' + this.props.searchBase} />
                <HomepageChart2 searchBase={this.props.searchBase + '&'} />
            </FetchedData>
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
            var data = [];
            var labels = [];
            var colors = [];

            // Get the assay_title counts from the facets
            var facets = this.props.data.facets;
            var assayFacet = facets.find(facet => facet.field === 'month_released');
            var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

            // Collect up the experiment assay_title counts to our local arrays to prepare for
            // the charts.




            while(data.length < 6){
                var firstValues = assayFacet.terms[0].key.split(", ");
                var maxIndex = 0;
                var maxMonth = months.indexOf(firstValues[0]);
                if (maxMonth < 10){
                    var maxMonthString = "0" + maxMonth.toString();
                    maxMonth = maxMonthString;
                }
                var maxYear = firstValues[1];
                var maxYearMonthCombo = maxYear + maxMonth;


                for(var x = 0; x < assayFacet.terms.length; x++){
                    var tempDate = assayFacet.terms[x].key.split(", ");
                    var tempMonth = months.indexOf(tempDate[0]);
                    if (tempMonth < 10){
                        var tempMonthString = "0" + tempMonth.toString();
                        tempMonth = tempMonthString;
                    }
                    var tempYear = tempDate[1];
                    var tempYearMonthCombo = tempYear + tempMonth;
                    //console.log("Year: " + tempYear + " Month: " + tempMonth);

                    if(tempYearMonthCombo > maxYearMonthCombo){

                        maxYearMonthCombo = tempYearMonthCombo;
                        maxIndex = x;
                    }
                }
                data.push(assayFacet.terms[maxIndex].doc_count);
                labels.push(assayFacet.terms[maxIndex].key);
                assayFacet.terms.splice(maxIndex, 1);
            }

            data.reverse();
            labels.reverse();
            colors = ['#939393', '#939393', '#939393', '#939393', '#939393', '#939393'];

            
            // assayFacet.terms.forEach(function(term, i) {
            //     data[i] = term.doc_count;
            //     labels[i] = term.key;
            //     colors[i] = colorList[i % colorList.length];
            // });

            // Pass the assay_title counts to the charting library to render it.
            var canvas = document.getElementById("myChart3");
            var ctx = canvas.getContext("2d");
            this.myBarChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: colors,
                        label: "Number of Released Experiments"
                    }]
                },
                options: {
                    legend: {
                        display: false
                    },
                    onClick: (e) => {
                        // React to clicks on pie sections
                        var activePoints = this.myBarChart.getElementAtEvent(e);
                        var term = assayFacet.terms[activePoints[0]._index].key;
                        this.context.navigate(this.props.data['@id'] + '&month_released=' + term);
                    }
                }
            });

        }.bind(this));

    },

    componentDidMount: function() {
        this.drawChart();
    },

    componentDidUpdate: function() {
        this.myBarChart.destroy(); // clears old chart before creating new one
        this.drawChart();
    },

    render: function() {
        return (
            <canvas id="myChart3" width="0" height="0"></canvas>
        );
    }

});

var HomepageChartLoader3 = React.createClass({
    propTypes: {
        
        callback: React.PropTypes.func
    },

    render: function() {
        return (
            <FetchedData>
                <Param name="data" url={'/matrix/' + this.props.searchBase} />
                <HomepageChart3 searchBase={this.props.searchBase + '&'} />
            </FetchedData>
        );
    }

});



