/** @jsx React.DOM */
define(['exports', 'jquery', 'react', 'globals', 'd3'],
function (search, $, React, globals, d3) {
    'use strict';

    var FacetBuilder = search.FacetBuilder = React.createClass({
        render: function() {
            var context = this.props.context;
            var result_count = context['@graph']['results'].length;
            var facets = context['@graph']['facets'];
            var terms = [];
            var url = (this.props.location)['search'];
            for (var i in facets) {
                terms.push(i);
            }
            var counter, counter1 = 0;
            var buildTerms = function(map) {
                var id;
                var count;
                var field;
                counter = counter + 1;
                for (var j in map) {
                    if(j == "field") {
                        field = map[j];
                    }else {
                        id = j;
                        count = map[j];
                    }
                }
                if(counter < 4) {
                    if(count == result_count) {
                        return <li>
                                <label><small>{id} ({count})</small></label>
                            </li>
                    }else {
                        return <li>
                                <a href={url+'&'+field+'='+id}>
                                    <label><small>{id} ({count})</small></label>
                                </a>
                            </li>
                    }
                } 
            };
            var buildCollapsingTerms = function(map) {
                var id;
                var count;
                var field;
                counter1 = counter1 + 1;
                for (var j in map) {
                    if(j == "field") {
                        field = map[j];
                    }else {
                        id = j;
                        count = map[j];
                    }
                }
                if (counter1 >= 4) {
                   if(count == result_count) {
                        return <li>
                                <label><small>{id} ({count})</small></label>
                            </li>
                    }else {
                        return <li>
                                <a href={url+'&'+field+'='+id}>
                                    <label><small>{id} ({count})</small></label>
                                </a>
                            </li>
                    }
                }
            };
            var buildSection = function(term) {
                counter = 0;
                counter1 = 0;
                var termID = term.replace(/\s+/g, '');
                return <div>
                        <legend><small>{term}</small></legend>
                        <ul className="facet-list">
                            {facets[term].length ?
                                facets[term].map(buildTerms)
                            : null}
                        </ul>
                        {facets[term].length > 3 ?
                            <ul className="facet-list">
                                <div id={termID} className="collapse">
                                    {facets[term].length ?
                                        facets[term].map(buildCollapsingTerms)
                                    : null}
                                </div>
                            </ul>
                        : null}
                        {facets[term].length > 3 ?
                            <label className="pull-right">
                                    <small>
                                        <button type="button" className="btn btn-link collapsed" data-toggle="collapse" data-target={'#'+termID} />
                                    </small>
                            </label>
                        : null}
                        
                    </div>
            };
            return (
                <div>
                    {Object.keys(facets).length ?
                        terms.map(buildSection)
                    : null}
                </div>
            );
        }
    });

    var ResultTable = search.ResultTable = React.createClass({
        render: function() {
            var context = this.props.context;
            var results = context['@graph'];
            var url = (this.props.location)['search'];
            var facets = context['@graph']['facets'];
            var myNode = document.getElementById("viz");
            if(myNode) {
                while (myNode.firstChild) {
                    myNode.removeChild(myNode.firstChild);
                }
            }
            for (var key in facets) {
                var data = [];
                for (var key1 in facets[key]) {
                    var data1 = {};
                    for (var key2 in facets[key][key1]) {
                        if(key2 != 'field') {
                            data1['label'] = key2;
                            data1['count'] = facets[key][key1][key2];
                        }
                        if(key2 == 'field') {
                            data1['link'] = url + '?searchTerm=*&type=biosamples&' + facets[key][key1][key2] + "="; 
                        }
                    }
                    data.push(data1);
                }
                var margin = {top: 30, right: 10, bottom: 30, left: 10};  
                var valueLabelWidth = 60; // space reserved for value labels (right)
                var barHeight = 20; // height of one bar
                var barLabelWidth = 250; // space reserved for bar labels
                var barLabelPadding = 10; // padding between bar and bar labels (left)
                var gridLabelHeight = 18; // space reserved for gridline labels
                var gridChartOffset = 3; // space between start of grid and first bar
                var maxBarWidth = 600; // width of the bar with the max value
                 
                // accessor functions 
                var barLabel = function(d) { return d['label']; };
                var barValue = function(d) { return parseFloat(d['count']); };
                var barLink  = function(d) { return d['link'] + d['label']; };
                 
                // scales
                var yScale = d3.scale.ordinal().domain(d3.range(0, data.length)).rangeBands([0, data.length * barHeight]);
                var y = function(d, i) { return yScale(i); };
                var yText = function(d, i) { return y(d, i) + yScale.rangeBand() / 2; };
                var x = d3.scale.linear().domain([0, d3.max(data, barValue)]).range([0, maxBarWidth]);
                
                // svg container element
                var chart = d3.select('#viz').append("svg")
                    .attr('width', maxBarWidth + barLabelWidth + valueLabelWidth + margin.left + margin.right) 
                    .attr('height', gridLabelHeight + gridChartOffset + data.length * barHeight + margin.top + margin.bottom);
                
                // grid line labels
                var gridContainer = chart.append('g')
                  .attr('transform', 'translate(' + barLabelWidth + ',' + gridLabelHeight + ')'); 
                
                gridContainer.selectAll("text").data(x.ticks(10)).enter().append("text")
                  .attr("x", x)
                  .attr("dy", -3)
                  .attr("text-anchor", "middle")
                  .text(String);
                
                // vertical grid lines
                gridContainer.selectAll("line").data(x.ticks(10)).enter().append("line")
                  .attr("x1", x)
                  .attr("x2", x)
                  .attr("y1", 0)
                  .attr("y2", yScale.rangeExtent()[1] + gridChartOffset)
                  .style("stroke", "#ccc");
                
                // bar labels
                var labelsContainer = chart.append('g')
                  .attr('transform', 'translate(' + (barLabelWidth - barLabelPadding) + ',' + (gridLabelHeight + gridChartOffset) + ')'); 
                labelsContainer.selectAll('text').data(data).enter().append('text')
                  .attr('y', yText)
                  .attr('stroke', 'none')
                  .attr('fill', 'black')
                  .attr("dy", ".35em") // vertical-align: middle
                  .attr('text-anchor', 'end')
                  .text(barLabel);
                
                // bars
                var barsContainer = chart.append('g')
                  .attr('transform', 'translate(' + barLabelWidth + ',' + (gridLabelHeight + gridChartOffset) + ')'); 
                
                barsContainer.selectAll("rect").data(data).enter()
                    .append("a")
                    .attr("xlink:href", function(d) {return barLink(d); })
                    .append("rect")
                    .attr('y', y)
                    .attr('height', yScale.rangeBand())
                    .attr('width', function(d) { return x(barValue(d)); })
                    .attr('stroke', 'white')
                    .attr('fill', 'steelblue')
                    .on("mouseover", function(d) { 
                        d3.select(this)
                            .attr('fill', 'orange');
                    })
                    .on("mouseout", function(d) { 
                         d3.select(this)
                            .attr('fill', 'steelblue');
                    });
                
                // bar value labels
                barsContainer.selectAll("text").data(data).enter().append("text")
                  .attr("x", function(d) { return x(barValue(d)); })
                  .attr("y", yText)
                  .attr("dx", 3) // padding-left
                  .attr("dy", ".35em") // vertical-align: middle
                  .attr("text-anchor", "start") // text-align: right
                  .attr("fill", "black")
                  .attr("stroke", "none")
                  .text(function(d) { return d3.round(barValue(d), 2); });
                
                // start line
                barsContainer.append("line")
                  .attr("y1", -gridChartOffset)
                  .attr("y2", yScale.rangeExtent()[1] + gridChartOffset)
                  .style("stroke", "#000");  

                chart.append("text")
                    .attr("x", 100)     
                    .attr("y", 20)
                    .attr("text-anchor", "middle")  
                    .style("font-size", "18px") 
                    .text(key)
                    .attr("fill", "steelblue");
            }

            var resultsView = function(result) {
                var highlight = result['highlight'];
                switch (result['@type'][0]) {
                    case "biosample":
                        return <li className="post">
                                    <strong><small>Biosample</small></strong>
                                    <div className="accession"><a href={result['@id']}>{result['accession']}</a></div>
                                    <small>{result['biosample_term_name']} - {result['biosample_term_id']} - {result['lab.title']}
                                        <br />
                                        <div className="highlight"dangerouslySetInnerHTML={{__html: highlight.toString()}} />
                                    </small>
                            </li>
                        break;
                    case "experiment":
                        return <li className="post">
                                    <strong><small>Experiment</small></strong>
                                    <div className="accession"><a href={result['@id']}>{result['accession']}</a></div>
                                    <small>{result['description']} - {result['assay_term_name']} - {result['lab.title']}
                                        <br />
                                        <div className="highlight" dangerouslySetInnerHTML={{__html: highlight.toString()}} />
                                    </small>
                            </li>
                        break;
                    case "antibody_approval":
                        return <li className="post">
                                <strong><small>Antibody</small></strong>
                                <div className="accession"><a href={result['@id']}>{result['antibody.accession']}</a></div>
                                <small>{result['target.label']} - {result['antibody.source.title']}
                                    <br />
                                    <div className="highlight" dangerouslySetInnerHTML={{__html: highlight.toString()}} />
                                </small>
                            </li>
                        break;
                    case "target":
                        return <li className="post">
                                <strong><small>Target</small></strong>
                                <div className="accession"><a href={result['@id']}>{result['label']}</a></div>
                                <small>{result['organism.name']}
                                    <br />
                                    <div  className="highlight" dangerouslySetInnerHTML={{__html: highlight.toString()}} />
                                </small>
                            </li>
                        break;
                }
            };  
            return (
                    <div>
                        {results['results'].length == 0 ?
                            <div className="panel data-display">
                                <legend>Biosample Facet Distribution</legend>
                                <div id="viz"></div>
                            </div>
                        : null}
                        {results['results'].length ?
                            <div className="panel data-display">
                                <div className="row">
                                    <div className="span3" id="facets">
                                        <h4>Filter Results</h4>
                                        <section className="facet box">
                                            <div>
                                                <legend><small>Data Type</small></legend>
                                                <ul className="facet-list">
                                                    {results['count']['antibodies'] ?
                                                        <li>
                                                            <span className="badge pull-right">{results['count']['antibodies']}</span>
                                                            <a href={url+'&type=antibodies'}><small>Antibodies</small></a>
                                                        </li>
                                                    : null}
                                                    {results['count']['biosamples'] ?
                                                        <li>
                                                            <span className="badge pull-right">{results['count']['biosamples']}</span>
                                                            <a href={url+'&type=biosamples'}><small>Biosamples</small></a>
                                                        </li>
                                                    : null}
                                                    {results['count']['experiments'] ?
                                                        <li>
                                                            <span className="badge pull-right">{results['count']['experiments']}</span>
                                                            <a href={url+'&type=experiments'}><small>Experiments</small></a>
                                                        </li>
                                                    : null}
                                                    {results['count']['targets'] ?
                                                        <li>
                                                            <span className="badge pull-right">{results['count']['targets']}</span>
                                                            <a href={url+'&type=targets'}><small>Targets</small></a>
                                                        </li>
                                                    : null}
                                                </ul>
                                            </div>
                                            {Object.keys(results['facets']).length ?
                                                <FacetBuilder location={this.props.location} context={this.props.context} />
                                            :null }
                                        </section>
                                    </div>
                                    <div className="span8">
                                        <legend>{results['results'].length} Results Found</legend>
                                        <div className="results">
                                            <ul class = "nav">
                                                {results['results'].length ?
                                                    results['results'].map(resultsView)
                                                : null}
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            </div>  
                    : null}
                </div>  
            );
        }
    });


    var Search = search.Search = React.createClass({
        getInitialState: function() {
            return {items: [], text: ''};
        },
        render: function() {
            var context = this.props.context;
            var results = context['@graph'];
            return (
                <div >
                    <form className="input-prepend">
                        <span className="add-on"><i className="icon-search"></i></span>
                        <input className="input-xxlarge" type="text" placeholder="Search ENCODE" name="searchTerm" defaultValue={this.state.text} />
                    </form>
                    {Object.keys(results).length ?
                        <ResultTable location={this.props.location} context={this.props.context} />
                    :null }
                </div>
            );
        }
    });

    globals.content_views.register(Search, 'search');
    return search;
});
