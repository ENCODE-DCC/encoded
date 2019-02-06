import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../libs/bootstrap/modal';
import * as globals from './globals';
import url from 'url';


// Display information on page as JSON formatted data
export class TestViz extends React.Component {
    constructor(props, context) {
        super(props, context);

        // Bind `this` to non-React methods.
        this.drawCharts = this.drawCharts.bind(this);
        this.bindClickHandlers = this.bindClickHandlers.bind(this);
        this.drawChartsResized = this.drawChartsResized.bind(this);
    };

    componentDidMount() {

        require.ensure('d3', (require) => {

            if (this.chartdisplay){

                this.d3 = require('d3');
                const targetElement = this.chartdisplay;
                this.drawCharts(targetElement);

                // Bind node/subnode click handlers to parent component handlers
                this.bindClickHandlers(this.d3, targetElement);

                window.addEventListener("resize", this.drawChartsResized);

            }

        });

    }

    componentWillUnmount() {
        window.removeEventListener("resize", this.drawChartsResized);
    }

    // need to redraw charts when window changes
    componentDidUpdate() {
        if (this.chartdisplay){
            this.d3 = require('d3');
            const targetElement = this.chartdisplay;
            targetElement.innerHTML = '';
            this.drawCharts(targetElement);
        }
    }

    drawChartsResized() {
        if (this.chartdisplay){
            this.d3 = require('d3');
            const targetElement = this.chartdisplay;
            targetElement.innerHTML = '';
            this.drawCharts(targetElement);
        }
    }

    drawCharts(targetElement) {

        function colorScale(index) {
            return index === 0 ? "#FFE391"
                 : index === 1 ? "#75BBA7"
                 : index === 2 ? "#6C809A"
                 : index === 3 ? "#7C9082"
                 : "#276A8E"
        }

        const d3 = this.d3;

        let displayCategories = ["assay_term_name", "organ_slims", "biosample_term_name", "target.label"];

        let facets = this.props.context.facets;

        let chosenIDX = [];
        let overallMax = 0;
        let obj = null, arr = null;
        facets.forEach(function(facet, facetIDX) {
            displayCategories.forEach(function(display,displayIDX){
                if (facet.field === display) {
                    obj = facet.terms;
                    arr = Object.keys( obj ).map(function ( key ) {
                        return obj[key]["doc_count"];
                    });
                    overallMax = Math.max(Math.max(...arr), overallMax);
                    if (Math.max(...arr) > 0) {
                        chosenIDX.push(facetIDX);
                    }
                }
            });
        });

        let maxWidth = 0;
        let screenWidth = document.getElementsByClassName("flex-panel")[0].offsetWidth - 43;
        if (screenWidth > 500) {
            maxWidth = Math.floor(screenWidth / chosenIDX.length);
        } else {
            maxWidth = Math.floor(screenWidth / 2)
        }

        chosenIDX.forEach(function(idx, idxidx){
            let TestData = facets[idx].terms;
            let filteredTestData = [], filteredIdx = 0;
            Object.keys(TestData).forEach(key => {
              if (TestData[key]["doc_count"] > 0) {
                  filteredTestData[filteredIdx] = TestData[key];
                  filteredIdx ++;
              }
            });
            let chartDataOrig = filteredTestData;

            // we want to be smarter about this but we can't display unlimited data
            let chartData = chartDataOrig.filter((chartData, cIDX) => cIDX < 10);

            const svgElement = d3.select(targetElement).append('svg');
            let fillColor = colorScale(idxidx);
            const xAxisLabel = facets[idx].title;
            const yAxisLabel = "Count";
            drawOneChart(svgElement, chartData, maxWidth, fillColor, xAxisLabel, yAxisLabel, overallMax);
        })

        // show tooltip
        let regbars_tooltip = this.d3.select("body")
            .append("div")
            .attr("class","barchart_tooltip")
            .style("position", "absolute")
            .style("z-index", "10")
            .style("display", "none")

        function drawOneChart(svgBars, chartData, maxWidth, fillColor, xAxisLabel, yAxisLabel, maxY){

            // create SVG container for chart components
            let margin = {top: 40, bottom: 170, right: 20, left: 30};
            let height = 310;
            let width = maxWidth;
            
            let chartArray = Object.keys( chartData ).map(function ( key ) {
                return chartData[key]["doc_count"];
            });
            let chartMax = Math.max(...chartArray);

            svgBars
                .attr("width", width)
                .attr("height", height)
                .append("g")

            const xScale = d3.scaleBand()
                .domain(chartData.map(d => d.key))
                .range([margin.left, width - margin.right])
                .padding(0.2)

            const yScale = d3.scaleLinear()
                .domain([0, chartMax])
                .range([height - margin.bottom, margin.top])

            // Define the axes
            const xAxis = svgBars.append("g")
                .attr("transform", `translate(0,${height - margin.bottom})`)
                .call(d3.axisBottom(xScale))
                    .selectAll("text")
                        .style("text-anchor", "end")
                        .attr("dx", "-.8em")
                        .attr("dy", "-.55em")
                        .attr("transform", "rotate(-90)" )
                .append("g").append("text")
                    .attr("class", "label")
                    .attr("x", width)
                    .attr("y", 40)
                    .attr("fill","black")
                    .style("text-anchor", "end")
                    .text(xAxisLabel);

            const yAxis = svgBars.append("g")
                .attr("transform", `translate(${margin.left},0)`)
                .call(d3.axisLeft(yScale)
                    .ticks(4)
                    .tickFormat(d3.format("d")));

            svgBars.append("text")
                .attr("class", "chart-title")
                .attr("x", width/2)
                .attr("y", 30)
                .text(xAxisLabel)
                .style("text-anchor", "middle")

            svgBars.selectAll("bar")
                .data(chartData)
              .enter().append("rect")
                .style("fill", fillColor)
                .attr("x", d=> xScale(d.key))
                .attr("width", xScale.bandwidth())
                .attr("y", d => yScale(+d.doc_count))
                .attr("height", function(d) {
                    return yScale(0) - yScale(+d.doc_count);
                })
                .on("mouseover", function(d) {
                  regbars_tooltip.html(`
                    <div><b>${d.key}</b></div>
                    <div><b>${d.doc_count}</b></div>
                  `);
                  regbars_tooltip.style("display", "block");
                })
                .on("mousemove", function(d) {
                  if (screen.width <= 480) {
                    return regbars_tooltip
                      .style("top", (d3.event.pageY+20)+"px")
                      .style("left",function(){
                        if (d3.event.pageX > 250){
                          return (d3.event.pageX-80)+"px";
                        } else {
                          return (d3.event.pageX-20)+"px";
                        }
                      });
                  } else {
                    return regbars_tooltip
                      .style("top", (d3.event.pageY+20)+"px")
                      .style("left",(d3.event.pageX-80)+"px");
                  }
                })
                .on("mouseout", function(){return regbars_tooltip.style("display", "none");});

        }

    }

    bindClickHandlers(d3, el) {
        // Add click event listeners to each node rendering. Node's ID is its ENCODE object ID
        const svg = d3.select(el);
        const nodes = svg.selectAll('g.node');
        const subnodes = svg.selectAll('g.subnode circle');

        nodes.on('click', (nodeId) => {
            this.nodeIdClick(nodeId);
        });
        subnodes.on('click', (subnode) => {
            d3.event.stopPropagation();
            this.nodeIdClick(subnode.id);
        });
    }

    render() {

        // const context = this.props.context;

        return (
            <div>
                <div ref={(div) => { this.chartdisplay = div; }} className="chart-display" />
            </div>
        );
    }
}
