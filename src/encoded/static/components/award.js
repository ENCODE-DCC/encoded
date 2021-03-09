import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import dayjs from 'dayjs';
import * as encoding from '../libs/query_encoding';
import { Panel, PanelHeading, PanelBody } from '../libs/ui/panel';
import DataColors from './datacolors';
import { FetchedData, Param } from './fetched';
import * as globals from './globals';
import { ProjectBadge } from './image';
import { ItemAccessories } from './objectutils';
import { PickerActions, resultItemClass } from './search';
import { SortTablePanel, SortTable } from './sorttable';
import queryString from 'query-string';
import Status from './status';

const labChartId = 'lab-chart'; // Lab chart <div> id attribute
const categoryChartId = 'category-chart'; // Assay chart <div> id attribute
const statusChartId = 'status-chart'; // Status chart <div> id attribute
const labColors = new DataColors(); // Get a list of colors to use for the lab chart
const labColorList = labColors.colorList();
const typeSpecificColorList = labColors.colorList();
const statusColorList = labColors.colorList();

// Create a string based on the genus buttons selected.
function generateQuery(chosenOrganisms, searchTerm) {
    // Make the base query.
    let query = '';

    // Add all the selected organisms, if any
    if (chosenOrganisms.length > 0) {
        const queryStrings = {
            HUMAN: `${searchTerm}Homo+sapiens`, // human
            MOUSE: `${searchTerm}Mus+musculus`, // mouse
        };
        const organismQueries = chosenOrganisms.map(organism => queryStrings[organism]);
        query += `&${organismQueries.join('&')}`;
    }

    return query;
}

// Draw the total chart count in the middle of the donut.
function drawDonutCenter(chart) {
    const canvasId = chart.chart.canvas.id;
    const width = chart.chart.width;
    const height = chart.chart.height;
    const ctx = chart.chart.ctx;
    // Undraws donut centers for Cumulative Line Chart and Status Stacked Bar Chart.
    if (canvasId === 'myGraph' || canvasId === 'status-chart-experiments-chart') {
        ctx.clearRect(0, 0, width, height);
    } else {
        const data = chart.data.datasets[0].data;
        if (data.length > 0) {
            ctx.fillStyle = '#000000';
            ctx.restore();
            const fontSize = (height / 114).toFixed(2);
            ctx.font = `${fontSize}em sans-serif`;
            ctx.textBaseline = 'middle';

            const total = data.reduce((prev, curr) => prev + curr);
            const textX = Math.round((width - ctx.measureText(total).width) / 2);
            const textY = height / 2;

            ctx.clearRect(0, 0, width, height);
            ctx.fillText(total, textX, textY);
            ctx.save();
        }
    }
}


// Create a chart in the div.
//   chartId: Root HTML id of div to draw the chart into. Supply <divs> with `chartId`-chart for
//            the chart itself, and `chartId`-legend for its legend.
//   values: Array of values to chart.
//   labels: Array of string labels corresponding to the values.
//   colors: Array of hex colors corresponding to the values.
//   baseSearchUri: Base URI to navigate to when clicking a doughnut slice or legend item. Clicked
//                  item label gets appended to it.
//   navigate: Called when when a doughnut slice gets clicked. Gets passed the URI to go to. Needed
//             because this function can't access the navigation function.

function createDoughnutChart(chartId, values, labels, colors, baseSearchUri, navigate) {
    return new Promise((resolve) => {
        require.ensure(['chart.js'], (require) => {
            const Chart = require('chart.js');

            // adding total doc count to middle of donut
            // http://stackoverflow.com/questions/20966817/how-to-add-text-inside-the-doughnut-chart-using-chart-js/24671908
            Chart.pluginService.register({
                beforeDraw: drawDonutCenter,
            });

            // Create the chart.
            const canvas = document.getElementById(`${chartId}-chart`);
            const parent = document.getElementById(chartId);
            canvas.width = parent.offsetWidth;
            canvas.height = parent.offsetHeight;
            canvas.style.width = `${parent.offsetWidth}px`;
            canvas.style.height = `${parent.offsetHeight}px`;
            const ctx = canvas.getContext('2d');
            const chart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels,
                    datasets: [{
                        data: values,
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
                    legendCallback: (chartInstance) => {
                        const chartData = chartInstance.data.datasets[0].data;
                        const chartColors = chartInstance.data.datasets[0].backgroundColor;
                        const chartLabels = chartInstance.data.labels;
                        const text = [];
                        text.push('<ul>');
                        for (let i = 0; i < chartData.length; i += 1) {
                            if (chartData[i]) {
                                text.push(`<li><a href="${baseSearchUri}${encoding.encodedURIComponentOLD(chartLabels[i])}">`);
                                text.push(`<i class="icon icon-circle chart-legend-chip" aria-hidden="true" style="color:${chartColors[i]}"></i>`);
                                text.push(`<span class="chart-legend-label">${chartLabels[i]}</span>`);
                                text.push('</a></li>');
                            }
                        }
                        text.push('</ul>');
                        return text.join('');
                    },
                    onClick: function onClick(e) {
                        // React to clicks on pie sections
                        const activePoints = chart.getElementAtEvent(e);
                        // chart.options.onClick.baseSearchUri is created or altered based on user input of selected Genus Buttons
                        // Each type of Object (e.g. Experiments, Annotations, Biosample, AntibodyLot) has a unique
                        //      query string for the corresponding report search -- cannot simply append something
                        //      to end of baseSearchUri, as baseSearchUri ends with {searchtype}=
                        //      so, query string specifying genus must end up somewhere in the middle of the string
                        //      that is baseSearchUri.
                        // chart.options.onClick.baseSearchUri must be defined in the type of chart (StatusChart, CategoryChart)
                        //      that is passed to the createDonutChart or createBarChart functions because cannot directly
                        //      make changes to the param baseSearchUri in updateChart().
                        if (activePoints[0]) { // if click on wrong area, do nothing
                            const clickedElementIndex = activePoints[0]._index;
                            const term = chart.data.labels[clickedElementIndex];
                            if (chart.options.onClick.baseSearchUri) {
                                navigate(`${chart.options.onClick.baseSearchUri}${encoding.encodedURIComponentOLD(term)}`);
                            } else {
                                navigate(`${baseSearchUri}${encoding.encodedURIComponentOLD(term)}`);
                            }
                        }
                    },
                },
            });
            document.getElementById(`${chartId}-legend`).innerHTML = chart.generateLegend();

            // Resolve the webpack loader promise with the chart instance.
            resolve(chart);
        }, 'chartjs');
    });
}

/**
 * Create a stacked bar chart in the div.
 *
 * @param {object} chartId - Root HTML id of div to draw the chart into. Supply <divs> with `chartId`-chart for
//            the chart itself, and `chartId`-legend for its legend.
 * @param {object} data - Contains arrays of values to chart, array of string labels corresponding to the values (status)
 * @param {array} colors - Hex colors corresponding to the values.
 * @param {array} replicateLabels - Array of string labels corresponding to the values (replicate type)
 * @param {object} baseSearchUri - Base URI to navigate to when clicking a bar chart section or legend item. Clicked
//                  item label gets appended to it.
 * @param {object} navigate - Called when when a bar chart section gets clicked. Gets passed the URI to go to. Needed
//             because this function can't access the navigation function.
 * @return {promise}
 */
export function createBarChart(chartId, data, colors, replicateLabels, legendTitle, baseSearchUri, navigate) {
    return new Promise((resolve) => {
        require.ensure(['chart.js'], (require) => {
            const Chart = require('chart.js');
            const datasets = [];
            if (data.unreplicatedDataset.some(x => x > 0)) {
                datasets.push({ label: 'unreplicated', data: data.unreplicatedDataset, backgroundColor: colors[0] });
            }
            if (data.isogenicDataset.some(x => x > 0)) {
                datasets.push({ label: 'isogenic', data: data.isogenicDataset, backgroundColor: colors[1] });
            }
            if (data.anisogenicDataset.some(x => x > 0)) {
                datasets.push({ label: 'anisogenic', data: data.anisogenicDataset, backgroundColor: colors[2] });
            }
            for (let i = 0; i < datasets.length; i += 1) {
                datasets[i].backgroundColor = colors[i];
            }

            // Create the chart.
            const canvas = document.getElementById(`${chartId}-chart`);
            const parent = document.getElementById(chartId);
            canvas.width = parent.offsetWidth;
            canvas.height = parent.offsetHeight;
            canvas.style.width = `${parent.offsetWidth}px`;
            canvas.style.height = `${parent.offsetHeight}px`;
            const ctx = canvas.getContext('2d');
            const chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets,
                },
                options: {
                    maintainAspectRatio: false,
                    responsive: true,
                    legend: {
                        display: false,
                    },
                    scales: {
                        xAxes: [{
                            scaleLabel: {
                                display: false,
                            },
                            gridLines: {
                            },
                            stacked: true,
                            ticks: {
                                autoSkip: false,
                            },
                        }],
                        yAxes: [{
                            gridLines: {
                                display: false,
                                color: '#fff',
                                zeroLineColor: '#fff',
                                zeroLineWidth: 0,
                            },
                            stacked: true,
                        }],
                    },
                    animation: {
                        duration: 0,
                    },
                    legendCallback: (chartInstance) => {
                        const LegendLabels = [];
                        const dataColors = [];
                        // If data array has value, add to legend
                        for (let i = 0; i < chartInstance.data.datasets.length; i += 1) {
                            LegendLabels.push(chartInstance.data.datasets[i].label);
                            dataColors.push(chartInstance.data.datasets[i].backgroundColor);
                        }
                        const text = [];
                        if (legendTitle) {
                            text.push(`<div class="legend-title">${legendTitle}</div>`);
                        }
                        text.push('<ul>');
                        for (let i = 0; i < LegendLabels.length; i += 1) {
                            if (LegendLabels[i]) {
                                text.push(`<li><a href="${baseSearchUri}&replication_type=${LegendLabels[i]}">`);
                                text.push(`<i class="icon icon-circle chart-legend-chip" aria-hidden="true" style="color:${dataColors[i]}"></i>`);
                                text.push(`<span class="chart-legend-label">${LegendLabels[i]}</span>`);
                                text.push('</a></li>');
                            }
                        }
                        text.push('</ul>');
                        return text.join('');
                    },
                    onClick: function onClick(e) {
                        const activePoints = chart.getElementAtEvent(e);

                        if (activePoints[0]) { // if click on wrong area, do nothing
                            const clickedElementIndex = activePoints[0]._index;
                            const clickedElementdataset = activePoints[0]._datasetIndex;
                            const term = chart.data.labels[clickedElementIndex];
                            const item = chart.data.datasets[clickedElementdataset].label;
                            // chart.options.onClick.baseSearchUri is created or altered based on user input of selected Genus Buttons
                            // Each type of Object (e.g. Experiments, Annotations, Biosample, AntibodyLot) has a unique
                            //      query string for the corresponding report search -- cannot simply append something
                            //      to end of baseSearchUri, as baseSearchUri ends with {searchtype}=
                            //      so, query string specifying genus must end up somewhere in the middle of the string
                            //      that is baseSearchUri.
                            // chart.options.onClick.baseSearchUri must be defined in the type of chart (StatusChart, CategoryChart)
                            //      that is passed to the createDonutChart or createBarChart functions because cannot directly
                            //      make changes to the param baseSearchUri in updateChart().
                            if (chart.options.onClick.baseSearchUri) {
                                navigate(`${chart.options.onClick.baseSearchUri}&status=${encoding.encodedURIComponentOLD(term)}&replication_type=${item}`);
                            } else {
                                navigate(`${baseSearchUri}&status=${encoding.encodedURIComponentOLD(term)}&replication_type=${item}`);
                            }
                        }
                    },
                },
            });
            document.getElementById(`${chartId}-legend`).innerHTML = chart.generateLegend();
            resolve(chart);
        }, 'chartjs');
    });
}

export function createNewBarChart(chartId, data, colors, replicateLabels, baseSearchUri, navigate) {
    return new Promise((resolve) => {
        require.ensure(['chart.js'], (require) => {
            const Chart = require('chart.js');
            const datasets = [];
            if (data.unknownDataset.some(x => x > 0)) {
                datasets.push({ label: 'unknown', data: data.unknownDataset, backgroundColor: colors[0] });
            }
            if (data.maleDataset.some(x => x > 0)) {
                datasets.push({ label: 'male', data: data.maleDataset, backgroundColor: colors[1] });
            }
            if (data.femaleDataset.some(x => x > 0)) {
                datasets.push({ label: 'female', data: data.femaleDataset, backgroundColor: colors[2] });
            }
            for (let i = 0; i < datasets.length; i += 1) {
                datasets[i].backgroundColor = colors[i];
            }

            // Create the chart.
            const canvas = document.getElementById(`${chartId}-chart`);
            const parent = document.getElementById(chartId);
            canvas.width = parent.offsetWidth;
            canvas.height = parent.offsetHeight;
            canvas.style.width = `${parent.offsetWidth}px`;
            canvas.style.height = `${parent.offsetHeight}px`;
            const ctx = canvas.getContext('2d');
            const chart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets,
                },
                options: {
                    maintainAspectRatio: false,
                    responsive: true,
                    legend: {
                        display: false,
                    },
                    scales: {
                        xAxes: [{
                            scaleLabel: {
                                display: false,
                            },
                            gridLines: {
                            },
                            stacked: true,
                            ticks: {
                                autoSkip: false,
                            },
                        }],
                        yAxes: [{
                            gridLines: {
                                display: false,
                                color: '#fff',
                                zeroLineColor: '#fff',
                                zeroLineWidth: 0,
                            },
                            stacked: true,
                        }],
                    },
                    animation: {
                        duration: 0,
                    },
                    onClick: function onClick(e) {
                        const activePoints = chart.getElementAtEvent(e);

                        if (activePoints[0]) { // if click on wrong area, do nothing
                            const clickedElementIndex = activePoints[0]._index;
                            const clickedElementdataset = activePoints[0]._datasetIndex;
                            const term = chart.data.labels[clickedElementIndex];
                            const item = chart.data.datasets[clickedElementdataset].label;
                            // chart.options.onClick.baseSearchUri is created or altered based on user input of selected Genus Buttons
                            // Each type of Object (e.g. Experiments, Annotations, Biosample, AntibodyLot) has a unique
                            //      query string for the corresponding report search -- cannot simply append something
                            //      to end of baseSearchUri, as baseSearchUri ends with {searchtype}=
                            //      so, query string specifying genus must end up somewhere in the middle of the string
                            //      that is baseSearchUri.
                            // chart.options.onClick.baseSearchUri must be defined in the type of chart (StatusChart, CategoryChart)
                            //      that is passed to the createDonutChart or createBarChart functions because cannot directly
                            //      make changes to the param baseSearchUri in updateChart().
                            if (chart.options.onClick.baseSearchUri) {
                                navigate(`${chart.options.onClick.baseSearchUri}&donors.ethnicity.term_name=${encoding.encodedURIComponentOLD(term)}&donors.sex=${item}`);
                            } else {
                                navigate(`${baseSearchUri}&donors.ethnicity.term_name=${encoding.encodedURIComponentOLD(term)}&donors.sex=${item}`);
                            }
                        }
                    },
                },
            });
            resolve(chart);
        }, 'chartjs');
    });
}

// Display and handle clicks in the chart of labs.
export class LabChart extends React.Component {
    constructor() {
        super();

        // Bind this to non-React components.
        this.createChart = this.createChart.bind(this);
        this.updateChart = this.updateChart.bind(this);
    }

    componentDidMount() {
        if (this.relevantData.length > 0) {
            this.createChart(`${labChartId}-${this.props.ident}`, this.relevantData);
        }
    }

    shouldComponentUpdate(nextProps) {
        return !_.isEqual(this.props.labs, nextProps.labs);
    }

    componentDidUpdate() {
        if (this.relevantData.length > 0) {
            if (this.chart) {
                this.updateChart(this.chart, this.relevantData);
            } else {
                this.createChart(`${labChartId}-${this.props.ident}`, this.props.labs);
            }
        } else if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    // Update existing chart with new data.
    updateChart(chart, facetData) {
        const { award, linkUri, objectQuery } = this.props;
        // Extract the non-zero values, and corresponding labels and colors for the data.
        const values = [];
        const labels = [];
        facetData.forEach((item) => {
            if (item.doc_count) {
                values.push(item.doc_count);
                labels.push(item.key);
            }
        });
        const colors = labels.map((label, i) => labColorList[i % labColorList.length]);
        // Update chart data and redraw with the new data
        chart.data.datasets[0].data = values;
        chart.data.datasets[0].backgroundColor = colors;
        chart.data.labels = labels;
        chart.options.onClick.baseSearchUri = `${linkUri}${award ? award.name : ''}${objectQuery}&lab.title=`;
        chart.update();

        // Redraw the updated legend
        document.getElementById(`${labChartId}-${this.props.ident}-legend`).innerHTML = chart.generateLegend();
    }

    createChart(chartId, facetData) {
        // Extract the non-zero values, and corresponding labels and colors for the data.
        const values = [];
        const labels = [];
        facetData.forEach((item) => {
            if (item.doc_count) {
                values.push(item.doc_count);
                labels.push(item.key);
            }
        });
        const colors = labels.map((label, i) => labColorList[i % labColorList.length]);

        // Create the chart.
        createDoughnutChart(chartId, values, labels, colors, `${this.props.linkUri}${this.props.award ? this.props.award.name : ''}&lab.title=`, (uri) => { this.context.navigate(uri); })
            .then((chartInstance) => {
                // Save the created chart instance.
                this.chart = chartInstance;
            });
    }

    render() {
        const { labs, ident, filteredOutLabs } = this.props;
        const filteredLabNames = filteredOutLabs ? filteredOutLabs.map(l => l.term) : [];

        // Filter out lab information with zero doc_count and filtered out via facets.
        this.relevantData = labs.filter(term => term.doc_count && !filteredLabNames.includes(term.key));

        // Calculate a (hopefully) unique ID to put on the DOM elements.
        const id = `${labChartId}-${ident}`;

        return (
            <div className="award-charts__chart">
                <div className="award-charts__title">
                    Lab
                </div>
                {this.relevantData.length > 0 ?
                    <div className="award-charts__visual">
                        <div id={id} className="award-charts__canvas">
                            <canvas id={`${id}-chart`} />
                        </div>
                        <div id={`${id}-legend`} className="award-charts__legend" />
                    </div>
                :
                    <div className="chart-no-data" style={{ height: this.wrapperHeight }}>No data to display</div>
                }
            </div>
        );
    }
}

LabChart.propTypes = {
    award: PropTypes.object, // Award being displayed
    labs: PropTypes.array.isRequired, // Array of labs facet data
    linkUri: PropTypes.string.isRequired, // Base URI for matrix links
    ident: PropTypes.string.isRequired, // Unique identifier to `id` the charts
    filteredOutLabs: PropTypes.array,
    objectQuery: PropTypes.string,
};

LabChart.defaultProps = {
    award: null,
    objectQuery: '',
    filteredOutLabs: [],
};

LabChart.contextTypes = {
    navigate: PropTypes.func,
};

// Display and handle clicks in the chart of assays.
export class CategoryChart extends React.Component {
    constructor() {
        super();
        this.createChart = this.createChart.bind(this);
        this.updateChart = this.updateChart.bind(this);
    }

    componentDidMount() {
        if (this.relevantData.length > 0) {
            this.createChart(`${categoryChartId}-${this.props.ident}`, this.relevantData);
        }
    }

    shouldComponentUpdate(nextProps) {
        return !_.isEqual(this.props.categoryData, nextProps.categoryData);
    }

    componentDidUpdate() {
        if (this.relevantData.length > 0) {
            if (this.chart) {
                this.updateChart(this.chart, this.relevantData);
            } else {
                this.createChart(`${categoryChartId}-${this.props.ident}`, this.relevantData);
            }
        } else if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    // Update existing chart with new data.
    updateChart(chart, facetData) {
        const { award, linkUri, objectQuery, categoryFacet } = this.props;
        // Extract the non-zero values, and corresponding labels and colors for the data.
        const values = [];
        const labels = [];
        facetData.forEach((item) => {
            if (item.doc_count) {
                values.push(item.doc_count);
                labels.push(item.key);
            }
        });
        const colors = labels.map((label, i) => typeSpecificColorList[i % typeSpecificColorList.length]);

        // Update chart data and redraw with the new data.
        chart.data.datasets[0].data = values;
        chart.data.datasets[0].backgroundColor = colors;
        chart.data.labels = labels;
        chart.options.onClick.baseSearchUri = `${linkUri}${award ? award.name : ''}${objectQuery}&${categoryFacet}=`;
        chart.update();

        // Redraw the updated legend
        document.getElementById(`${categoryChartId}-${this.props.ident}-legend`).innerHTML = chart.generateLegend();
    }

    createChart(chartId, facetData) {
        const { award, linkUri, categoryFacet } = this.props;

        // Extract the non-zero values, and corresponding labels and colors for the data.
        const values = [];
        const labels = [];
        facetData.forEach((item) => {
            if (item.doc_count) {
                values.push(item.doc_count);
                labels.push(item.key);
            }
        });
        const colors = labels.map((label, i) => typeSpecificColorList[i % typeSpecificColorList.length]);

        // Create the chart.
        createDoughnutChart(chartId, values, labels, colors, `${linkUri}${award ? award.name : ''}&${categoryFacet}=`, (uri) => { this.context.navigate(uri); })
            .then((chartInstance) => {
                // Save the created chart instance.
                this.chart = chartInstance;
            });
    }

    render() {
        const { categoryData, title, ident, filteredOutAssays } = this.props;
        const filteredOutAssayTitles = filteredOutAssays ? filteredOutAssays.map(a => a.term) : [];

        // Filter out category data with zero doc_count and filtered via facet.
        this.relevantData = categoryData.filter(term => term.doc_count && !filteredOutAssayTitles.includes(term.key));

        // Calculate a (hopefully) unique ID to put on the DOM elements.
        const id = `${categoryChartId}-${ident}`;

        return (
            <div className="award-charts__chart">
                <div className="title">
                    {title}
                </div>
                {this.relevantData.length > 0 ?
                    <div className="award-charts__visual">
                        <div id={id} className="award-charts__canvas">
                            <canvas id={`${id}-chart`} />
                        </div>
                    </div>
                :
                    <div className="chart-no-data" style={{ height: this.wrapperHeight }}>No data to display</div>
                }
            </div>
        );
    }
}

CategoryChart.propTypes = {
    award: PropTypes.object, // Award being displayed
    categoryData: PropTypes.array.isRequired, // Type-specific data to display in a chart
    title: PropTypes.string.isRequired, // Title to display above the chart
    linkUri: PropTypes.string.isRequired, // Element of matrix URI to select
    categoryFacet: PropTypes.string.isRequired, // Add to linkUri to link to matrix facet item
    ident: PropTypes.string.isRequired, // Unique identifier to `id` the charts
    filteredOutAssays: PropTypes.array,
    objectQuery: PropTypes.string,
};

CategoryChart.defaultProps = {
    award: null,
    objectQuery: '',
    filteredOutAssays: [],
};

CategoryChart.contextTypes = {
    navigate: PropTypes.func,
};


// Display and handle clicks in the chart of biosamples.
class BiosampleChart extends React.Component {
    constructor() {
        super();
        this.createChart = this.createChart.bind(this);
        this.updateChart = this.updateChart.bind(this);
    }

    componentDidMount() {
        if (this.relevantData.length > 0) {
            this.createChart(`${categoryChartId}-${this.props.ident}`, this.relevantData);
        }
    }

    componentDidUpdate() {
        if (this.relevantData.length > 0) {
            if (this.chart) {
                this.updateChart(this.chart, this.relevantData);
            } else {
                this.createChart(`${categoryChartId}-${this.props.ident}`, this.relevantData);
            }
        } else if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    // Update existing chart with new data.
    updateChart(chart, facetData) {
        const { award } = this.props;
        // Extract the non-zero values, and corresponding labels and colors for the data.
        const values = [];
        const labels = [];
        facetData.forEach((item) => {
            if (item.doc_count) {
                values.push(item.doc_count);
                labels.push(item.key);
            }
        });
        const colors = labels.map((label, i) => typeSpecificColorList[i % typeSpecificColorList.length]);
        const LibraryQuery = generateQuery(this.props.selectedOrganisms, 'derived_from.organisms=');
        // Update chart data and redraw with the new data.
        chart.data.datasets[0].data = values;
        chart.data.datasets[0].backgroundColor = colors;
        chart.data.labels = labels;
        chart.options.onClick.baseSearchUri = `/report/?type=Library&award.name=${award.name}&${LibraryQuery}&assay=`;
        chart.update();

        // Redraw the updated legend
        document.getElementById(`${categoryChartId}-${this.props.ident}-legend`).innerHTML = chart.generateLegend();
    }

    createChart(chartId, facetData) {
        const { award, linkUri, categoryFacet, selectedOrganisms } = this.props;

        // Extract the non-zero values, and corresponding labels and colors for the data.
        const values = [];
        const labels = [];
        facetData.forEach((item) => {
            if (item.doc_count) {
                values.push(item.doc_count);
                labels.push(item.key);
            }
        });
        const colors = labels.map((label, i) => typeSpecificColorList[i % typeSpecificColorList.length]);
        createDoughnutChart(chartId, values, labels, colors, `${linkUri}${award.name}&${categoryFacet}=`, (uri) => { this.context.navigate(uri); }, selectedOrganisms)
            .then((chartInstance) => {
                // Save the created chart instance.
                this.chart = chartInstance;
            });
    }

    render() {
        const { categoryData, ident, award } = this.props;
        const LibraryQuery = generateQuery(this.props.selectedOrganisms, 'derived_from.organisms=');

        // Filter out category data with zero doc_count.
        this.relevantData = categoryData.filter(term => term.doc_count);

        // Calculate a (hopefully) unique ID to put on the DOM elements.
        const id = `${categoryChartId}-${ident}`;

        return (
            <div className="award-charts__chart">
                <div className="award-charts__title">
                    <div className="reagentsreporttitle">Libraries</div>
                    {this.relevantData.length > 0 ?
                        <a className="btn btn-info btn-sm reagentsreportlink" href={`/report/?type=Library&${LibraryQuery}&award.name=${award.name}`} title="View tabular report"><svg id="Table" data-name="Table" xmlns="http://www.w3.org/2000/svg" width="29" height="17" viewBox="0 0 29 17" className="svg-icon svg-icon-table"><path d="M22,0H0V17H29V0H22ZM21,4.33V8H15V4.33h6ZM15,9h6v3H15V9Zm-1,3H8V9h6v3Zm0-7.69V8H8V4.33h6Zm-13,0H7V8H1V4.33ZM1,9H7v3H1V9Zm0,7V13H7v3H1Zm7,0V13h6v3H8Zm7,0V13h6v3H15Zm13,0H22V13h6v3Zm0-4H22V9h6v3Zm0-4H22V4.33h6V8Z" /></svg></a>
                    : null}
                </div>
                {this.relevantData.length > 0 ?
                    <div>
                        <div className="award-charts__visual">
                            <div id={id} className="award-charts__canvas">
                                <canvas id={`${id}-chart`} />
                            </div>
                            <div id={`${id}-legend`} className="award-charts__legend" />
                        </div>
                    </div>
                :
                    <div className="chart-no-data" style={{ height: this.wrapperHeight }}>No data to display</div>
                }
            </div>
        );
    }
}

BiosampleChart.propTypes = {
    award: PropTypes.object.isRequired, // Award being displayed
    categoryData: PropTypes.array.isRequired, // Type-specific data to display in a chart
    categoryFacet: PropTypes.string.isRequired, // Add to linkUri to link to matrix facet item
    ident: PropTypes.string.isRequired, // Unique identifier to `id` the charts
    linkUri: PropTypes.string.isRequired,
    selectedOrganisms: PropTypes.array,
};

BiosampleChart.defaultProps = {
    selectedOrganisms: [],
};

BiosampleChart.contextTypes = {
    navigate: PropTypes.func,
};

class ControlsChart extends React.Component {
    constructor() {
        super();
        this.createChart = this.createChart.bind(this);
        this.updateChart = this.updateChart.bind(this);
    }

    componentDidMount() {
        if (this.relevantData.length > 0) {
            this.createChart(`${statusChartId}-${this.props.ident}-controls`, this.relevantData);
        }
    }

    componentDidUpdate() {
        if (this.relevantData.length > 0) {
            if (this.chart) {
                this.updateChart(this.chart, this.relevantData);
            } else {
                this.createChart(`${statusChartId}-${this.props.ident}-controls`, this.relevantData);
            }
        } else if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    updateChart(chart, facetData) {
        const { award, objectQuery } = this.props;
        // Extract the non-zero values, and corresponding labels and colors for the data.
        const values = [];
        const labels = [];
        facetData.forEach((item) => {
            if (item.doc_count) {
                values.push(item.doc_count);
                labels.push(item.key);
            }
        });

        const colors = labels.map((label, i) => statusColorList[i % statusColorList.length]);

        // Update chart data and redraw with the new data
        chart.data.datasets[0].data = values;
        chart.data.datasets[0].backgroundColor = colors;
        chart.data.labels = labels;
        chart.options.onClick.baseSearchUri = `/matrix/?type=Dataset&award.name=${award.name}&${objectQuery}&status=`;
        chart.update();

        // Redraw the updated legend
        document.getElementById(`${statusChartId}-${this.props.ident}-controls-legend`).innerHTML = chart.generateLegend();
    }

    createChart(chartId, facetData) {
        // Extract the non-zero values, and corresponding labels and colors for the data.
        const values = [];
        const labels = [];
        facetData.forEach((item) => {
            if (item.doc_count) {
                values.push(item.doc_count);
                labels.push(item.key);
            }
        });
        const colors = labels.map((label, i) => statusColorList[i % statusColorList.length]);

        // Create the chart.
        createDoughnutChart(chartId, values, labels, colors, `${this.props.linkUri}${this.props.award.name}&status=`, (uri) => { this.context.navigate(uri); })
            .then((chartInstance) => {
                // Save the created chart instance.
                this.chart = chartInstance;
            });
    }

    render() {
        const { statuses, ident } = this.props;

        // Filter out category data with zero doc_count.
        this.relevantData = statuses.filter(term => term.doc_count);

        // Calculate a (hopefully) unique ID to put on the DOM elements.
        const id = `${statusChartId}-${ident}-controls`;

        return (
            <div className="award-charts__chart">
                <div className="award-charts__title">
                    Controls
                </div>
                {this.relevantData.length > 0 ?
                    <div className="award-charts__visual">
                        <div id={id} className="award-charts__canvas">
                            <canvas id={`${id}-chart`} />
                        </div>
                        <div id={`${id}-legend`} className="award-charts__legend" />
                    </div>
                :
                    <div className="chart-no-data" style={{ height: this.wrapperHeight }}>No data to display</div>
                }
            </div>
        );
    }
}

ControlsChart.propTypes = {
    award: PropTypes.object.isRequired, // Award being displayed
    statuses: PropTypes.array, // Array of status facet data
    linkUri: PropTypes.string.isRequired, // URI to use for matrix links
    ident: PropTypes.string.isRequired, // Unique identifier to `id` the charts
    objectQuery: PropTypes.string,
};

ControlsChart.defaultProps = {
    statuses: [],
    objectQuery: '',
};

ControlsChart.contextTypes = {
    navigate: PropTypes.func,
};

class StatusExperimentChart extends React.Component {
    constructor() {
        super();
        this.createChart = this.createChart.bind(this);
        this.updateChart = this.updateChart.bind(this);
    }

    componentDidMount() {
        if (this.relevantData.length > 0) {
            this.createChart(`${statusChartId}-${this.props.ident}`, this.props.statuses);
        }
    }

    componentDidUpdate() {
        if (this.relevantData.length > 0) {
            if (this.chart) {
                this.updateChart(this.chart, this.relevantData);
            } else {
                this.createChart(`${statusChartId}-${this.props.ident}`, this.relevantData);
            }
        } else if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    render() {
        const { statuses, ident } = this.props;

        // Filter out category data with zero doc_count.
        this.relevantData = statuses.filter(term => term.doc_count);

        // Calculate a (hopefully) unique ID to put on the DOM elements.
        const id = `${statusChartId}-${ident}`;

        return (
            <div className="award-charts__chart">
                <div className="award-charts__title">
                    Status
                </div>
                {this.relevantData.length > 0 ?
                    <div className="award-charts__visual">
                        <div id={id} className="award-charts__canvas">
                            <canvas id={`${id}-chart`} />
                        </div>
                        <div id={`${id}-legend`} className="award-charts__legend" />
                    </div>
                :
                    <div className="chart-no-data" style={{ height: this.wrapperHeight }}>No data to display</div>
                }
            </div>
        );
    }
}

StatusExperimentChart.propTypes = {
    award: PropTypes.object, // Award being displayed
    statuses: PropTypes.array, // Array of status facet data
    linkUri: PropTypes.string.isRequired, // URI to use for matrix links
    ident: PropTypes.string.isRequired, // Unique identifier to `id` the charts
    experiments: PropTypes.object.isRequired,
    objectQuery: PropTypes.string,
};

StatusExperimentChart.defaultProps = {
    award: null,
    statuses: [],
    objectQuery: '',
};

StatusExperimentChart.contextTypes = {
    navigate: PropTypes.func,
};

// Display and handle clicks in the chart of labs.
class StatusChart extends React.Component {
    // Update existing chart with new data.
    constructor() {
        super();
        this.createChart = this.createChart.bind(this);
        this.updateChart = this.updateChart.bind(this);
    }

    componentDidMount() {
        if (this.relevantData.length > 0) {
            this.createChart(`${statusChartId}-${this.props.ident}`, this.relevantData);
        }
    }

    componentDidUpdate() {
        if (this.relevantData.length > 0) {
            if (this.chart) {
                this.updateChart(this.chart, this.relevantData);
            } else {
                this.createChart(`${statusChartId}-${this.props.ident}`, this.relevantData);
            }
        } else if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    updateChart(chart, facetData) {
        const { award, linkUri, objectQuery } = this.props;
        // Extract the non-zero values, and corresponding labels and colors for the data.
        const values = [];
        const labels = [];
        facetData.forEach((item) => {
            if (item.doc_count) {
                values.push(item.doc_count);
                labels.push(item.key);
            }
        });

        const colors = labels.map((label, i) => statusColorList[i % statusColorList.length]);
        // Update chart data and redraw with the new data
        chart.data.datasets[0].data = values;
        chart.data.datasets[0].backgroundColor = colors;
        chart.data.labels = labels;
        chart.options.onClick.baseSearchUri = `${linkUri}${award.name}${objectQuery}&status=`;
        chart.update();

        // Redraw the updated legend
        document.getElementById(`${statusChartId}-${this.props.ident}-legend`).innerHTML = chart.generateLegend();
    }

    createChart(chartId, facetData) {
        // Extract the non-zero values, and corresponding labels and colors for the data.
        const values = [];
        const labels = [];
        facetData.forEach((item) => {
            if (item.doc_count) {
                values.push(item.doc_count);
                labels.push(item.key);
            }
        });
        const colors = labels.map((label, i) => statusColorList[i % statusColorList.length]);

        // Create the chart.
        createDoughnutChart(chartId, values, labels, colors, `${this.props.linkUri}${this.props.award.name}&status=`, (uri) => { this.context.navigate(uri); })
            .then((chartInstance) => {
                // Save the created chart instance.
                this.chart = chartInstance;
            });
    }

    render() {
        const { statuses, ident } = this.props;

        // Filter out category data with zero doc_count.
        this.relevantData = statuses.filter(term => term.doc_count);

        // Calculate a (hopefully) unique ID to put on the DOM elements.
        const id = `${statusChartId}-${ident}`;

        return (
            <div className="award-charts__chart">
                <div className="award-charts__title">
                    Status
                </div>
                {this.relevantData.length > 0 ?
                    <div className="award-charts__visual">
                        <div id={id} className="award-charts__canvas">
                            <canvas id={`${id}-chart`} />
                        </div>
                        <div id={`${id}-legend`} className="award-charts__legend" />
                    </div>
                :
                    <div className="chart-no-data" style={{ height: this.wrapperHeight }}>No data to display</div>
                }
            </div>
        );
    }
}

StatusChart.propTypes = {
    award: PropTypes.object.isRequired, // Award being displayed
    statuses: PropTypes.array, // Array of status facet data
    linkUri: PropTypes.string.isRequired, // URI to use for matrix links
    ident: PropTypes.string.isRequired, // Unique identifier to `id` the charts
    objectQuery: PropTypes.string,
};

StatusChart.defaultProps = {
    statuses: [],
    objectQuery: '',
};

StatusChart.contextTypes = {
    navigate: PropTypes.func,
};

// The existing species are added to the array of species
function generateUpdatedSpeciesArray(categories, query, updatedSpeciesArray) {
    let categorySpeciesArray;
    if (categories && categories.facets && categories.facets.length > 0) {
        const genusFacet = categories.facets.find(facet => facet.field === query);
        categorySpeciesArray = (genusFacet && genusFacet.terms && genusFacet.terms.length > 0) ? genusFacet.terms : [];
        const categorySpeciesArrayLength = categorySpeciesArray.length;
        for (let j = 0; j < categorySpeciesArrayLength; j += 1) {
            if (categorySpeciesArray[j].doc_count !== 0) {
                updatedSpeciesArray.push(categorySpeciesArray[j].key);
            }
        }
    }
    return updatedSpeciesArray;
}

const ChartRenderer = (props) => {
    const { award, experiments, biosamples, handleClick, selectedOrganisms } = props;

    // Put all search-related configuration data in one consistent place.
    const searchData = {
        experiments: {
            ident: 'experiments',
            data: [],
            labs: [],
            categoryData: [],
            statuses: [],
            categoryFacet: 'libraries.assay',
            title: 'Assays',
            uriBase: '/search/?type=Dataset&award.name=',
            linkUri: '/report/?type=Dataset&award.name=',
        },
        biosamples: {
            ident: 'biosamples',
            data: [],
            labs: [],
            categoryData: [],
            statuses: [],
            categoryFacet: 'assay',
            title: 'Libraries',
            uriBase: '/search/?type=Library&award.name=',
            linkUri: '/report/?type=Library&award.name=',
        },
    };
    // Match the species to their genera
    const speciesGenusMap = {
        'Homo sapiens': 'HUMAN',
        'Mus musculus': 'MOUSE',
    };

    // Find the chart data in the returned facets.
    const experimentsConfig = searchData.experiments;
    const biosamplesConfig = searchData.biosamples;
    let experimentSpeciesArray;
    let biosampleSpeciesArray;
    // let controlSpeciesArray;
    const updatedSpeciesArray = [];
    searchData.experiments.data = (experiments && experiments.facets) || [];
    searchData.biosamples.data = (biosamples && biosamples.facets) || [];

    ['experiments', 'biosamples'].forEach((chartCategory) => {
        if (searchData[chartCategory].data.length > 0) {
            // Get the array of lab data.
            const labFacet = searchData[chartCategory].data.find(facet => facet.field === 'lab.title');
            searchData[chartCategory].labs = (labFacet && labFacet.terms && labFacet.terms.length > 0) ? labFacet.terms.sort((a, b) => (a.key < b.key ? -1 : (a.key > b.key ? 1 : 0))) : [];

            // Get the array of data specific to experiments, annotations, or antibodies
            const categoryFacet = searchData[chartCategory].data.find(facet => facet.field === searchData[chartCategory].categoryFacet);
            searchData[chartCategory].categoryData = (categoryFacet && categoryFacet.terms && categoryFacet.terms.length > 0) ? categoryFacet.terms : [];

            // Get the array of status data.
            const statusFacet = searchData[chartCategory].data.find(facet => facet.field === 'status');
            searchData[chartCategory].statuses = (statusFacet && statusFacet.terms && statusFacet.terms.length > 0) ? statusFacet.terms : [];
        }
    });
    // If there are experiments, then the corresponding species are added to the array of species
    if (experiments && experiments.facets && experiments.facets.length > 0) {
        const genusFacet = experiments.facets.find(facet => facet.field === 'libraries.derived_from.organisms');
        experimentSpeciesArray = (genusFacet && genusFacet.terms && genusFacet.terms.length > 0) ? genusFacet.terms : [];
        const experimentSpeciesArrayLength = experimentSpeciesArray.length;
        for (let j = 0; j < experimentSpeciesArrayLength; j += 1) {
            if (experimentSpeciesArray[j].doc_count !== 0) {
                updatedSpeciesArray.push(experimentSpeciesArray[j].key);
            }
        }
    }
    // If there are biosamples, then the corresponding species are iadded to the array of species
    if (biosamples && biosamples.facets && biosamples.facets.length > 0) {
        const genusFacet = biosamples.facets.find(facet => facet.field === 'derived_from.organisms=');
        biosampleSpeciesArray = (genusFacet && genusFacet.terms && genusFacet.terms.length > 0) ? genusFacet.terms : [];
        const biosampleSpeciesArrayLength = biosampleSpeciesArray.length;
        for (let j = 0; j < biosampleSpeciesArrayLength; j += 1) {
            if (biosampleSpeciesArray[j].doc_count !== 0) {
                updatedSpeciesArray.push(biosampleSpeciesArray[j].key);
            }
        }
    }
    // Array of species is converted to an array of genera
    let updatedGenusArray = updatedSpeciesArray.map(species => speciesGenusMap[species]);

    // Array of genera is deduplicated
    updatedGenusArray = _.uniq(updatedGenusArray);
    const ExperimentQuery = generateQuery(selectedOrganisms, 'libraries.derived_from.organisms=');
 
    // For each category (experiments, biosamples), the corresponding species are added to the array of species
    generateUpdatedSpeciesArray(experiments, 'libraries.derived_from.organisms=', updatedSpeciesArray);
    generateUpdatedSpeciesArray(biosamples, 'derived_from.organisms=', updatedSpeciesArray);
 
    // Array of species is converted to an array of genera
    updatedGenusArray = updatedSpeciesArray.map(species => speciesGenusMap[species]);

    return (
        <div className="award-charts">
            <div> <GenusButtons handleClick={handleClick} selectedOrganisms={selectedOrganisms} updatedGenusArray={updatedGenusArray} /> </div>
            <PanelBody>
                <div className="award-chart__group-wrapper">
                    <h2>Libraries</h2>
                    {biosamplesConfig.categoryData.length > 0 ?
                        <div className="award-chart__group">
                            <BiosampleChart
                                award={award}
                                categoryData={biosamplesConfig.categoryData}
                                categoryFacet={biosamplesConfig.categoryFacet}
                                linkUri={biosamplesConfig.linkUri}
                                ident={biosamplesConfig.ident}
                                selectedOrganisms={selectedOrganisms}
                            />
                        </div>
                    :
                        <div className="browser-error">No libraries were submitted under this award</div>
                    }
                </div>
            </PanelBody>
        </div>
    );
};

ChartRenderer.propTypes = {
    award: PropTypes.object.isRequired, // Award being displayed
    experiments: PropTypes.object, // Search result of matching experiments
    biosamples: PropTypes.object, // Search result of matching biosamples
    handleClick: PropTypes.func.isRequired, // Function to call when a button is clicked
    selectedOrganisms: PropTypes.array, // Array of currently selected buttons
};

ChartRenderer.defaultProps = {
    experiments: {},
    biosamples: {},
    selectedOrganisms: [],
};

// Create new tabdisplay of genus buttons
/* eslint-disable react/prefer-stateless-function */
class GenusButtons extends React.Component {
    render() {
        const { updatedGenusArray, selectedOrganisms, handleClick } = this.props;
        // If genera exist, then the button for each specific genus is created
        if (updatedGenusArray.length > 0) {
            return (
                <div className="organism-selector">
                    {updatedGenusArray.indexOf('HUMAN') !== -1 ?
                        <OrganismSelector organism="HUMAN" selected={selectedOrganisms.indexOf('HUMAN') !== -1} organismButtonClick={handleClick} />
                    :
                    null}
                    {updatedGenusArray.indexOf('MOUSE') !== -1 ?
                        <OrganismSelector organism="MOUSE" selected={selectedOrganisms.indexOf('MOUSE') !== -1} organismButtonClick={handleClick} />
                    :
                    null}
                </div>
            );
        }
        return null;
    }
}
/* eslint-enable react/prefer-stateless-function */

GenusButtons.propTypes = {
    selectedOrganisms: PropTypes.array, // Array of currently selected buttons
    handleClick: PropTypes.func.isRequired, // Function to call when a button is clicked
    updatedGenusArray: PropTypes.array, // Array of existing genera
};

GenusButtons.defaultProps = {
    selectedOrganisms: [],
    updatedGenusArray: [],
};

const milestonesTableColumns = {
    assay: {
        title: 'Assay name',
    },

    proposed_count: {
        title: 'Proposed count',
    },

    deliverable_unit: {
        title: 'Library',
    },

    contract_date: {
        title: 'Contract date',
    },
};

const MilestonesTable = (props) => {
    const { award } = props;
    return (
        <SortTablePanel title="Milestones">
            <SortTable list={award.milestones} columns={milestonesTableColumns} />
        </SortTablePanel>
    );
};

MilestonesTable.propTypes = {
    award: PropTypes.object.isRequired,
};


/**
 * Take a sorted array of date terms and generate a new array of date terms with the same dates
 * plus `0` doc_count entries for any months missing between `sortedDateTerms` entries. The new
 * array has contiguous months.
 *
 * @param {array} sortedDateTerms - Array of date terms sorted by date
 * @param {string} startDateText - First date to appear in new array in YYYY-MM format
 * @return {array} - New array with `sortedDateTerms` data plus 0 entries in between given months.
 */
const fillDates = (sortedDateTerms, startDateText, awardEndDate) => {
    // The new array limits go between `startDate` and the current date.
    const startingDate = dayjs(startDateText, 'YYYY-MM');
    const endingDate = dayjs();
    const monthCount = endingDate.diff(startingDate, 'months') + 1;
    const awardFinalDate = dayjs(awardEndDate);

    // For every possible month, generate a new array entry, filling in the doc_count with
    // matching data from `sortedDateTerms`, or 0 if `sortedDateTerms` has no matching month.
    const filledDateArray = [];
    let sortedDateIndex = sortedDateTerms.findIndex(term => term.key >= startDateText);
    sortedDateIndex = sortedDateIndex > -1 ? sortedDateIndex : 0;
    let currentMonthText = startDateText;
    let currentDate = startingDate.clone();
    for (let i = 0; i < monthCount; i += 1) {
        let docCount = 0;
        if (sortedDateTerms[sortedDateIndex] && currentMonthText === sortedDateTerms[sortedDateIndex].key) {
            // An entry in `sortedDateTerms` matches the current month we're generating in the new
            // array, so copy its doc_count to the new array and go to the next entry in
            // `sortedDateTerms`.
            docCount = sortedDateTerms[sortedDateIndex].doc_count;
            sortedDateIndex += 1;
        }
        filledDateArray.push({ key: currentMonthText, doc_count: docCount });

        // Move to the next month..
        currentDate = currentDate.add(1, 'month');

        if (currentDate.isAfter(awardFinalDate)) {
            break;
        }

        currentMonthText = currentDate.format('YYYY-MM');
    }
    return filledDateArray;
};


/**
 * Any terms in `dateTerms` (must be sorted by month) with matching months get their values
 * combined and placed into just one date term entry in the new output array of date terms.
 * The new output array of date terms is still sorted.
 *
 * @param {array} dateTerms - Array of search result date terms to consolidate.
 * @returns {array} - Equivalent to `dateTerms` but with duplicate date entries consolidated.
 */
const consolidateSortedDates = (dateTerms) => {
    const consolidatedTerms = [];
    let lastTerm = null;
    for (let i = 0; i < dateTerms.length; i += 1) {
        if (lastTerm && dateTerms[i].key === lastTerm.key) {
            // Current `dateTerms` entry key matches last one we pushed onto consolidatedTerms,
            // so just add their doc_counts together in the last term.
            lastTerm.doc_count += dateTerms[i].doc_count;
        } else {
            consolidatedTerms.push({ key: dateTerms[i].key, doc_count: dateTerms[i].doc_count });
            lastTerm = consolidatedTerms[consolidatedTerms.length - 1];
        }
    }
    return consolidatedTerms;
};


// Overall component to render the cumulative line chart
export const ExperimentDate = (props) => {
    const { experiments, award, panelCss, panelHeadingCss } = props;
    let releasedDates = [];
    let deduplicatedreleased = {};

    // Search experiments for date_released and date_submitted in facets
    if (experiments.facets && experiments.facets.length > 0) {
        const dateReleasedFacet = experiments.facets.find(facet => facet.field === 'date_released');
        releasedDates = (dateReleasedFacet && dateReleasedFacet.terms && dateReleasedFacet.terms.length > 0) ? dateReleasedFacet.terms : [];
    }

    // Take an array of date facet terms and return an array of terms sorted by date.
    function sortTerms(dateArray) {
        // Use dayjs to format arrays of submitted and released date
        const standardTerms = dateArray.map((term) => {
            const standardDate = dayjs(term.key).format('YYYY-MM');
            return { key: standardDate, doc_count: term.doc_count };
        });

        // Sort arrays chronologically
        const sortedTerms = standardTerms.sort((termA, termB) => {
            if (termA.key < termB.key) {
                return -1;
            } else if (termB.key < termA.key) {
                return 1;
            }
            return 0;
        });
        return (
            sortedTerms
        );
    }

    function createDataset(deduplicated) {
        let accumulator = 0;
        // Make the data cumulative
        const accumulatedData = deduplicated.map((term) => {
            accumulator += term.doc_count;
            return accumulator;
        });
        return (accumulatedData);
    }

    let accumulatedDataReleased = [];
    let date = [];
    const dateRange = queryString.parse(experiments['@id']).advancedQuery;
    const dates = dateRange ? dateRange.match(/\d{4}-\d{1,2}-\d{1,2}/gi) : null;

    if (releasedDates.length > 0) {
        const sortedreleasedTerms = consolidateSortedDates(sortTerms(releasedDates));

        // Figure out the award start date. If none, use the earlier of the earliest released or submitted dates.
        let awardStartDate;
        let awardEndDate = null;

        if (dates) {
            awardStartDate = dayjs(dates[0]).format('YYYY-MM').toString();
            awardEndDate = dayjs(dates[1]).format('YYYY-MM').toString();
        } else if (award && award.start_date) {
            awardStartDate = dayjs(award.start_date).format('YYYY-MM');
        } else {
            const releasedIndex = sortedreleasedTerms.findIndex(item => item.doc_count);
            awardStartDate = releasedIndex > -1 ? sortedreleasedTerms[releasedIndex].key : sortedreleasedTerms[sortedreleasedTerms.length - 1];
        }
        deduplicatedreleased = fillDates(sortedreleasedTerms, awardStartDate, awardEndDate);

        // Create an array of dates.
        date = deduplicatedreleased.map(dateTerm => dayjs(dateTerm.key).format('MMM YYYY'));
        accumulatedDataReleased = createDataset(deduplicatedreleased);
    }

    return (
        <div>
            {accumulatedDataReleased.length > 0 ?
                <Panel addClasses={panelCss}>
                    <PanelHeading addClasses={panelHeadingCss}>
                        <h4>Cumulative Number of Experiments</h4>
                    </PanelHeading>
                    <PanelBody>
                        <CumulativeGraph releaseddatavalue={accumulatedDataReleased} monthReleased={date} />
                    </PanelBody>
                </Panel>
            : null}
        </div>
    );
};

ExperimentDate.propTypes = {
    experiments: PropTypes.object,
    award: PropTypes.object,
    panelCss: PropTypes.string,
    panelHeadingCss: PropTypes.string,
};

ExperimentDate.defaultProps = {
    experiments: {},
    award: null,
    panelCss: '',
    panelHeadingCss: '',
};


// Add the new style class to the selected button when it is clicked
class OrganismSelector extends React.Component {
    constructor() {
        super();
        this.buttonClick = this.buttonClick.bind(this);
    }

    buttonClick() {
        this.props.organismButtonClick(this.props.organism);
    }
    render() {
        const { organism, selected } = this.props;
        return (
            <button onClick={this.buttonClick} className={`organism-selector__tab${selected ? ' organism-selector--selected' : ''}`}>
                {organism}
            </button>
        );
    }
}

OrganismSelector.propTypes = {
    organism: PropTypes.string, // Organism this selector represents
    selected: PropTypes.bool, // `true` if selector is selected
    organismButtonClick: PropTypes.func.isRequired, // Function that takes in the prop organism when button is clicked
};

OrganismSelector.defaultProps = {
    organism: {},
    selected: {},
};


// Overall component to render the award charts
class AwardCharts extends React.Component {
    constructor() {
        super();
        this.state = {
            selectedOrganisms: [], // create empty array of selected organism tabs
        };
        this.handleClick = this.handleClick.bind(this);
    }

    handleClick(organism) {
        // Create a copy of this.state.selectedOrganisms so we can manipulate it in peace.
        const tempArray = _.clone(this.state.selectedOrganisms);
        if (tempArray.indexOf(organism) === -1) {
            // if organism isn't already in array, then add it
            tempArray.push(organism);
        } else {
            // otherwise if it is in array, remove it from array
            const indexToRemoveArray = tempArray.indexOf(organism);
            tempArray.splice(indexToRemoveArray, 1);
        }

        // Update the list of user-selected organisms.
        this.setState({ selectedOrganisms: tempArray });
    }

    render() {
        const { award, updatedGenusArray } = this.props;
        // Create searchTerm-specific query strings
        const ExperimentQuery = generateQuery(this.state.selectedOrganisms, 'libraries.derived_from.organisms=');
        const LibraryQuery = generateQuery(this.state.selectedOrganisms, 'derived_from.organisms=');
        return (
            <Panel>
                <PanelHeading>
                    <h4>Current Production</h4>
                    <ProjectBadge award={award} addClasses="badge-heading" />
                </PanelHeading>
                <div>
                    <FetchedData ignoreErrors>
                        <Param name="experiments" url={`/search/?type=Dataset&award.name=${award.name}${ExperimentQuery}`} />
                        <Param name="biosamples" url={`/search/?type=Library&award.name=${award.name}${LibraryQuery}`} />
                        <ChartRenderer award={award} updatedGenusArray={updatedGenusArray} handleClick={this.handleClick} selectedOrganisms={this.state.selectedOrganisms} />
                    </FetchedData>
                </div>
            </Panel>
        );
    }
}

AwardCharts.propTypes = {
    award: PropTypes.object.isRequired, // Award represented by this chart
    updatedGenusArray: PropTypes.array, // Array of existing genera
};
AwardCharts.defaultProps = {
    updatedGenusArray: [],
};

/* eslint-disable react/prefer-stateless-function */
class LineChart extends React.Component {
    render() {
        const { award } = this.props;
        return (
            <div>
                <FetchedData ignoreErrors>
                    <Param name="experiments" url={`/search/?type=Dataset&award.name=${award.name}`} />
                    <ExperimentDate award={award} />
                </FetchedData>
            </div>
        );
    }
}
/* eslint-enable react/prefer-stateless-function */

LineChart.propTypes = {
    award: PropTypes.object.isRequired, // Award represented by this chart
};


// Create a cumulative line chart in the div.
class CumulativeGraph extends React.Component {
    constructor() {
        super();
        this.chart = null;

        // Bind `this` to non-React methods.
        this.createChart = this.createChart.bind(this);
        this.updateChart = this.updateChart.bind(this);
    }

    componentDidMount() {
        this.createChart();
    }

    shouldComponentUpdate(nextProps) {
        return !_.isEqual(this.props.releaseddatavalue, nextProps.releaseddatavalue) ||
                !_.isEqual(this.props.monthReleased, nextProps.monthReleased);
    }

    componentDidUpdate() {
        if (this.chart) {
            this.updateChart();
        } else {
            this.createChart();
        }
    }

    createChart() {
        const { releaseddatavalue, monthReleased } = this.props;
        require.ensure(['chart.js'], (require) => {
            const Chart = require('chart.js');
            const ctx = document.getElementById('myGraph').getContext('2d');
            const xticksBallParkCount = 25; // ballpark number desired x-axis ticks
            const monthReleasedLength = monthReleased.length;
            const lastxAxisIndex = monthReleasedLength - 1;
            const xticks = monthReleasedLength < xticksBallParkCount ? 1 : Math.ceil(monthReleasedLength / xticksBallParkCount);
            const dateValues = [];
            const totals = [];

            for (let i = 0; i < monthReleasedLength; i += 1) {
                if (i % xticks === 0 || i === lastxAxisIndex) {
                    const y = releaseddatavalue[i];
                    const x = monthReleased[i];

                    dateValues.push(x);
                    totals.push(y);
                }
            }

            this.chart = new Chart(ctx, {
                type: 'line',
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    legend: {
                        display: true,
                        labels: {
                            display: false,
                        },
                        position: 'bottom', // Position the legend beneath the line chart
                    },
                    elements: {
                        line: {
                            tension: 0,
                        },
                        point: {
                            radius: 0,
                        },
                    },
                    scales: {
                        xAxes: [{
                            ticks: {
                                autoSkip: false,
                                maxTicksLimit: 25,
                                maxRotation: 45,
                                minRotation: 45,
                            },
                        }],
                        yAxes: [{
                            stacked: true,
                        }],
                    },
                },
                data: {
                    labels: dateValues,
                    datasets: [{
                        label: 'Released',
                        data: totals,
                        backgroundColor: '#538235',
                    }],
                },
            });
        });
    }

    updateChart() {
        const { releaseddatavalue, monthReleased } = this.props;

        this.chart.data.labels = monthReleased;
        this.chart.data.datasets[0].data = releaseddatavalue;
        this.chart.update();
    }

    render() {
        return (
            <div style={{ position: 'relative', height: 500 }}>
                <canvas id="myGraph" />
            </div>
        );
    }
}

CumulativeGraph.propTypes = {
    releaseddatavalue: PropTypes.array.isRequired,
    monthReleased: PropTypes.array.isRequired,
};

function piList(values, field) {
    if (values && values.length > 0) {
        return Array.from(new Set(values.map(function(value) { return value[field] }))).join(", ");
    }
    return null;
}

const Award = ({ context }, reactContext) => {
    const loggedIn = !!(reactContext.session && reactContext.session['auth.userid']);

    const pi_titles = piList(context.principal_investigators, 'title');
    const collab_titles = piList(context.collaborators, 'title');

    return (
        <div className={globals.itemClass(context, 'view-item')}>
            <header>
                <h1>AWARD SUMMARY for {context.name}</h1>
                <ItemAccessories item={context} />
            </header>
            <AwardCharts award={context} />
            <Panel>
                <PanelHeading>
                    <h4>{context.title || context.name}</h4>
                </PanelHeading>
                <PanelBody>
                    {context.description ?
                        <div>
                            <p>{context.description}</p>
                        </div>
                    :
                        <p className="browser-error">Award has no description</p>
                    }
                </PanelBody>
                <PanelBody addClasses="panel__split">
                    <div className="panel__split-element">
                        <dl className="key-value">
                            {context.principal_investigators ?
                                <div data-test="pi">
                                    <dt>Principal Investigators</dt>
                                    <dd>{pi_titles}</dd>
                                </div>
                            : null}
                            {context.collaborators ?
                                <div data-test="colllabs">
                                    <dt>Collaborators</dt>
                                    <dd>{collab_titles}</dd>
                                </div>
                            : null}
                        </dl>
                    </div>
                    <div className="panel__split-element">
                        <dl className="key-value">
                            <div data-test="project">
                                <dt>Project</dt>
                                <dd>{context.project}</dd>
                            </div>

                            <div data-test="projectinfo">
                                <dt>CZI Project</dt>
                                <dd><a href={context.url} title={`${context.name} CZI Project`}>{context.name}</a></dd>
                            </div>

                            <div data-test="projectinfo">
                                <dt>Status</dt>
                                <dd><Status item={context} inline /></dd>
                            </div>
                        </dl>
                    </div>
                </PanelBody>
            </Panel>
        </div>
    );
};

Award.propTypes = {
    context: PropTypes.object.isRequired, // Award object being rendered
};

Award.contextTypes = {
    session: PropTypes.object, // Login information
};

globals.contentViews.register(Award, 'Award');

const Listing = ({ context: result }) => (
    <li className={resultItemClass(result)}>
        <div className="result-item">
            <div className="result-item__data">
                <a href={result['@id']} className="result-item__link">{result.title}</a>
                <div className="result-item__data-row">
                    <strong>Project / RFA: </strong>{result.project} / {result.rfa}
                </div>
            </div>
            <div className="result-item__meta">
                <div className="result-item__meta-title">Award</div>
                <div className="type">{` ${result.name}`}</div>
                <Status item={result.status} badgeSize="small" css="result-table__status" />
            </div>
            <PickerActions context={result} />
        </div>
    </li>
);

Listing.propTypes = {
    context: PropTypes.object.isRequired, // Object whose search result we're displaying
};

globals.listingViews.register(Listing, 'Award');
