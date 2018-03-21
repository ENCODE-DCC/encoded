import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import moment from 'moment';
import { Panel, PanelHeading, PanelBody } from '../libs/bootstrap/panel';
import DataColors from './datacolors';
import { FetchedData, Param } from './fetched';
import * as globals from './globals';
import { ProjectBadge } from './image';
import { PickerActions } from './search';
import { SortTablePanel, SortTable } from './sorttable';
import { StatusLabel } from './statuslabel';

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
    if (chosenOrganisms.length) {
        const queryStrings = {
            HUMAN: `${searchTerm}Homo+sapiens`, // human
            MOUSE: `${searchTerm}Mus+musculus`, // mouse
            WORM: `${searchTerm}Caenorhabditis+elegans`, // worm
            FLY: `${searchTerm}Drosophila+melanogaster&${searchTerm}Drosophila+pseudoobscura&${searchTerm}Drosophila+simulans&${searchTerm}Drosophila+mojavensis&${searchTerm}Drosophila+ananassae&${searchTerm}Drosophila+virilis&${searchTerm}Drosophila+yakuba`,
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
        if (data.length) {
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
                                text.push(`<li><a href="${baseSearchUri}${globals.encodedURIComponent(chartLabels[i])}">`);
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
                                navigate(`${chart.options.onClick.baseSearchUri}${globals.encodedURIComponent(term)}`);
                            } else {
                                navigate(`${baseSearchUri}${globals.encodedURIComponent(term)}`);
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
                                navigate(`${chart.options.onClick.baseSearchUri}&status=${globals.encodedURIComponent(term)}&replication_type=${item}`);
                            } else {
                                navigate(`${baseSearchUri}&status=${globals.encodedURIComponent(term)}&replication_type=${item}`);
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


// Display and handle clicks in the chart of labs.
export class LabChart extends React.Component {
    constructor() {
        super();

        // Bind this to non-React components.
        this.createChart = this.createChart.bind(this);
        this.updateChart = this.updateChart.bind(this);
    }

    componentDidMount() {
        if (this.relevantData.length) {
            this.createChart(`${labChartId}-${this.props.ident}`, this.relevantData);
        }
    }

    shouldComponentUpdate(nextProps) {
        return !_.isEqual(this.props.labs, nextProps.labs);
    }

    componentDidUpdate() {
        if (this.relevantData.length) {
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
        const { labs, ident } = this.props;

        // Filter out category data with zero doc_count.
        this.relevantData = labs.filter(term => term.doc_count);

        // Calculate a (hopefully) unique ID to put on the DOM elements.
        const id = `${labChartId}-${ident}`;

        return (
            <div className="award-charts__chart">
                <div className="award-charts__title">
                    Lab
                </div>
                {this.relevantData.length ?
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
    objectQuery: PropTypes.string,
};

LabChart.defaultProps = {
    award: null,
    objectQuery: '',
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
        if (this.relevantData.length) {
            this.createChart(`${categoryChartId}-${this.props.ident}`, this.relevantData);
        }
    }

    shouldComponentUpdate(nextProps) {
        return !_.isEqual(this.props.categoryData, nextProps.categoryData);
    }

    componentDidUpdate() {
        if (this.relevantData.length) {
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
        const { categoryData, title, ident } = this.props;

        // Filter out category data with zero doc_count.
        this.relevantData = categoryData.filter(term => term.doc_count);

        // Calculate a (hopefully) unique ID to put on the DOM elements.
        const id = `${categoryChartId}-${ident}`;

        return (
            <div className="award-charts__chart">
                <div className="title">
                    {title}
                </div>
                {this.relevantData.length ?
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

CategoryChart.propTypes = {
    award: PropTypes.object, // Award being displayed
    categoryData: PropTypes.array.isRequired, // Type-specific data to display in a chart
    title: PropTypes.string.isRequired, // Title to display above the chart
    linkUri: PropTypes.string.isRequired, // Element of matrix URI to select
    categoryFacet: PropTypes.string.isRequired, // Add to linkUri to link to matrix facet item
    ident: PropTypes.string.isRequired, // Unique identifier to `id` the charts
    objectQuery: PropTypes.string,
};

CategoryChart.defaultProps = {
    award: null,
    objectQuery: '',
};

CategoryChart.contextTypes = {
    navigate: PropTypes.func,
};


// Display and handle clicks in the chart of antibodies.
class AntibodyChart extends React.Component {
    constructor() {
        super();
        this.createChart = this.createChart.bind(this);
        this.updateChart = this.updateChart.bind(this);
    }

    componentDidMount() {
        if (this.relevantData.length) {
            this.createChart(`${categoryChartId}-${this.props.ident}`, this.relevantData);
        }
    }

    componentDidUpdate() {
        if (this.relevantData.length) {
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
        // Extract the non-zero values, and corresponding labels and colors for the data.
        const { award } = this.props;
        const values = [];
        const labels = [];
        facetData.forEach((item) => {
            if (item.doc_count) {
                values.push(item.doc_count);
                labels.push(item.key);
            }
        });
        const colors = labels.map((label, i) => typeSpecificColorList[i % typeSpecificColorList.length]);
        const AntibodyQuery = generateQuery(this.props.selectedOrganisms, 'targets.organism.scientific_name=');
        // Update chart data and redraw with the new data.
        chart.data.datasets[0].data = values;
        chart.data.datasets[0].backgroundColor = colors;
        chart.data.labels = labels;
        chart.options.onClick.baseSearchUri = `/report/?type=AntibodyLot&award=/awards/${award.name}/${AntibodyQuery}&lot_reviews.status=`;
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

        createDoughnutChart(chartId, values, labels, colors, `${linkUri}${award.name}/&${categoryFacet}=`, (uri) => { this.context.navigate(uri); })
            .then((chartInstance) => {
                // Save the created chart instance.
                this.chart = chartInstance;
            });
    }

    render() {
        const { categoryData, ident, award } = this.props;
        const AntibodyQuery = generateQuery(this.props.selectedOrganisms, 'targets.organism.scientific_name=');

        // Filter out category data with zero doc_count.
        this.relevantData = categoryData.filter(term => term.doc_count);

        // Calculate a (hopefully) unique ID to put on the DOM elements.
        const id = `${categoryChartId}-${ident}`;

        return (
            <div className="award-charts__chart">
                <div className="award-charts__title">
                    Antibodies {this.relevantData.length ?
                    <a className="btn btn-info btn-xs reagentsreporttitle" href={`/report/?type=AntibodyLot&${AntibodyQuery}&award=${award['@id']}&field=accession&field=lot_reviews.status&field=lot_reviews.targets.label&field=lot_reviews.targets.organism.scientific_name&field=source.title&field=product_id&field=lot_id&field=date_created`} title="View tabular report"><svg id="Table" data-name="Table" xmlns="http://www.w3.org/2000/svg" width="29" height="17" viewBox="0 0 29 17" className="svg-icon svg-icon-table"><title>table-tab-icon </title><path d="M22,0H0V17H29V0H22ZM21,4.33V8H15V4.33h6ZM15,9h6v3H15V9Zm-1,3H8V9h6v3Zm0-7.69V8H8V4.33h6Zm-13,0H7V8H1V4.33ZM1,9H7v3H1V9Zm0,7V13H7v3H1Zm7,0V13h6v3H8Zm7,0V13h6v3H15Zm13,0H22V13h6v3Zm0-4H22V9h6v3Zm0-4H22V4.33h6V8Z" /></svg></a>
                    :
                    null}
                </div>
                {this.relevantData.length ?
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

AntibodyChart.propTypes = {
    award: PropTypes.object.isRequired, // Award being displayed
    categoryData: PropTypes.array.isRequired, // Type-specific data to display in a chart
    categoryFacet: PropTypes.string.isRequired, // Add to linkUri to link to matrix facet item
    ident: PropTypes.string.isRequired, // Unique identifier to `id` the charts
    linkUri: PropTypes.string.isRequired,
    selectedOrganisms: PropTypes.array.isRequired,
};

AntibodyChart.contextTypes = {
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
        if (this.relevantData.length) {
            this.createChart(`${categoryChartId}-${this.props.ident}`, this.relevantData);
        }
    }

    componentDidUpdate() {
        if (this.relevantData.length) {
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
        // if (this.props.selectedOrganisms.length)
        const BiosampleQuery = generateQuery(this.props.selectedOrganisms, 'organism.scientific_name=');
        // Update chart data and redraw with the new data.
        chart.data.datasets[0].data = values;
        chart.data.datasets[0].backgroundColor = colors;
        chart.data.labels = labels;
        chart.options.onClick.baseSearchUri = `/report/?type=Biosample&award.name=${award.name}&${BiosampleQuery}&biosample_type=`;
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
        const BiosampleQuery = generateQuery(this.props.selectedOrganisms, 'organism.scientific_name=');

        // Filter out category data with zero doc_count.
        this.relevantData = categoryData.filter(term => term.doc_count);

        // Calculate a (hopefully) unique ID to put on the DOM elements.
        const id = `${categoryChartId}-${ident}`;

        return (
            <div className="award-charts__chart">
                <div className="award-charts__title">
                    Biosamples {this.relevantData.length ?
                        <a className="btn btn-info btn-sm reagentsreporttitle" href={`/report/?type=Biosample&${BiosampleQuery}&award.name=${award.name}`} title="View tabular report"><svg id="Table" data-name="Table" xmlns="http://www.w3.org/2000/svg" width="29" height="17" viewBox="0 0 29 17" className="svg-icon svg-icon-table"><title>table-tab-icon </title><path d="M22,0H0V17H29V0H22ZM21,4.33V8H15V4.33h6ZM15,9h6v3H15V9Zm-1,3H8V9h6v3Zm0-7.69V8H8V4.33h6Zm-13,0H7V8H1V4.33ZM1,9H7v3H1V9Zm0,7V13H7v3H1Zm7,0V13h6v3H8Zm7,0V13h6v3H15Zm13,0H22V13h6v3Zm0-4H22V9h6v3Zm0-4H22V4.33h6V8Z" /></svg></a>
                    : null}
                </div>
                {this.relevantData.length ?
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

/**
 * Function to be called in createChart and updateChart of class StatusExperimentChart, creates arrays for chart data.
 *
 * @param {object} experiments - Fetched data for experiments in Award
 * @param {object} unreplicated - Experiment search with specific replication_type unreplicated
 * @param {array} isogenic - Experiment search with specific replication_type isogenic
 * @param {array} anisogenic - Experiment search with specific replication_type anisogenic
 * @return {object} - with labels (for status -- x-axis of bar chart), unreplicatedDataset, isogenicDataset, anisogenicDataset
//              to be passed to the createChart function
 */

function StatusData(experiments, unreplicated, isogenic, anisogenic) {
    let unreplicatedArray;
    let isogenicArray;
    let anisogenicArray;
    const unreplicatedLabel = [];
    let unreplicatedDataset = [];
    const isogenicLabel = [];
    let isogenicDataset = [];
    const anisogenicLabel = [];
    let anisogenicDataset = [];

    // Find status in facets for each replicate type (unreplicated, isogenic, anisogenic) search
    if (experiments && experiments.facets && experiments.facets.length) {
        const unreplicatedFacet = unreplicated.facets.find(facet => facet.field === 'status');
        const isogenicFacet = isogenic.facets.find(facet => facet.field === 'status');
        const anisogenicFacet = anisogenic.facets.find(facet => facet.field === 'status');
        unreplicatedArray = (unreplicatedFacet && unreplicatedFacet.terms && unreplicatedFacet.terms.length) ? unreplicatedFacet.terms : [];
        isogenicArray = (isogenicFacet && isogenicFacet.terms && isogenicFacet.terms.length) ? isogenicFacet.terms : [];
        anisogenicArray = (anisogenicFacet && anisogenicFacet.terms && anisogenicFacet.terms.length) ? anisogenicFacet.terms : [];
    }
    const labels = ['started', 'submitted', 'released', 'deleted', 'replaced', 'archived', 'revoked'];

    // Check existence of data for each of the keys in array labels
    // Ensures that for each replicate type there exists the same set of labels and the corresponding data values (in order)
    //      so that it can be easily and accurately passed to chart.js in createBarChart
    //      First pushes anything that has a key in labels, then sorts the dataset
    //      If the array has no length, just push an array with 0 values
    if (unreplicatedArray.length) {
        for (let j = 0; j < labels.length; j += 1) {
            for (let i = 0; i < unreplicatedArray.length; i += 1) {
                if (unreplicatedArray[i].key === labels[j]) {
                    unreplicatedLabel.push(unreplicatedArray[i].key);
                    unreplicatedDataset.push(unreplicatedArray[i].doc_count);
                }
            }
        }
        for (let j = 0; j < labels.length; j += 1) {
            if (labels[j] !== unreplicatedLabel[j]) {
                unreplicatedLabel.splice(j, 0, labels[j]);
                unreplicatedDataset.splice(j, 0, 0);
            }
        }
    } else {
        unreplicatedDataset = [0, 0, 0, 0, 0, 0, 0, 0];
    }
    if (isogenicArray.length) {
        for (let j = 0; j < labels.length; j += 1) {
            for (let i = 0; i < isogenicArray.length; i += 1) {
                if (isogenicArray[i].key === labels[j]) {
                    isogenicLabel.push(isogenicArray[i].key);
                    isogenicDataset.push(isogenicArray[i].doc_count);
                }
            }
        }
        for (let j = 0; j < labels.length; j += 1) {
            if (labels[j] !== isogenicLabel[j]) {
                isogenicLabel.splice(j, 0, labels[j]);
                isogenicDataset.splice(j, 0, 0);
            }
        }
    } else {
        isogenicDataset = [0, 0, 0, 0, 0, 0, 0, 0];
    }
    if (anisogenicArray.length) {
        for (let j = 0; j < labels.length; j += 1) {
            for (let i = 0; i < anisogenicArray.length; i += 1) {
                if (anisogenicArray[i].key === labels[j]) {
                    anisogenicLabel.push(anisogenicArray[i].key);
                    anisogenicDataset.push(anisogenicArray[i].doc_count);
                }
            }
        }
        for (let j = 0; j < labels.length; j += 1) {
            if (labels[j] !== anisogenicLabel[j]) {
                anisogenicLabel.splice(j, 0, labels[j]);
                anisogenicDataset.splice(j, 0, 0);
            }
        }
    } else {
        anisogenicDataset = [0, 0, 0, 0, 0, 0, 0, 0];
    }
    return ({ labels, unreplicatedDataset, isogenicDataset, anisogenicDataset });
}

class ControlsChart extends React.Component {
    constructor() {
        super();
        this.createChart = this.createChart.bind(this);
        this.updateChart = this.updateChart.bind(this);
    }

    componentDidMount() {
        if (this.relevantData.length) {
            this.createChart(`${statusChartId}-${this.props.ident}-controls`, this.relevantData);
        }
    }

    componentDidUpdate() {
        if (this.relevantData.length) {
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
        chart.options.onClick.baseSearchUri = `/matrix/?type=Experiment&target.investigated_as=control&award.name=${award.name}&${objectQuery}&status=`;
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
                {this.relevantData.length ?
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
        if (this.relevantData.length) {
            this.createChart(`${statusChartId}-${this.props.ident}`, this.props.statuses);
        }
    }

    componentDidUpdate() {
        if (this.relevantData.length) {
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

    updateChart(chart) {
        const { experiments, unreplicated, isogenic, anisogenic, linkUri, award, objectQuery } = this.props;
        // Object with arrays of status labels, unreplicatedDataset, isogenicDataset, anisogenicDataset
        const data = StatusData(experiments, unreplicated, isogenic, anisogenic);
        const replicatelabels = ['unreplicated', 'isogenic', 'anisogenic'];
        const colors = replicatelabels.map((label, i) => statusColorList[i % statusColorList.length]);
        // Must specify each case of data availability - must remove available, data-less chart.data.datasets
        // Ensures that the colors will be the default and legend labels does not include unnecessary strings
        if (data.unreplicatedDataset.some(x => x > 0)) {
            chart.data.datasets[0] = { label: 'unreplicated', data: data.unreplicatedDataset, backgroundColor: colors[0] };
            if (data.isogenicDataset.some(x => x > 0)) {
                chart.data.datasets[1] = { label: 'isogenic', data: data.isogenicDataset, backgroundColor: colors[1] };
                if (data.anisogenicDataset.some(x => x > 0)) {
                    chart.data.datasets[2] = { label: 'anisogenic', data: data.anisogenicDataset, backgroundColor: colors[2] };
                } else if (data.anisogenicDataset.every(x => x === 0)) {
                    chart.data.datasets[2] = {};
                }
            } else if (data.isogenicDataset.every(x => x === 0) && data.anisogenicDataset.some(x => x > 0)) {
                chart.data.datasets[1] = { label: 'anisogenic', data: data.anisogenicDataset, backgroundColor: colors[1] };
                chart.data.datasets[2] = {};
            }
        } else if (data.unreplicatedDataset.every(x => x === 0) && data.isogenicDataset.some(x => x > 0)) {
            chart.data.datasets[0] = { label: 'isogenic', data: data.isogenicDataset, backgroundColor: colors[0] };
            if (data.anisogenicDataset.some(x => x > 0)) {
                chart.data.datasets[1] = { label: 'anisogenic', data: data.anisogenicDataset, backgroundColor: colors[1] };
                chart.data.datasets[2] = {};
            } else if (data.anisogenicDataset.every(x => x === 0)) {
                chart.data.datasets[1] = {};
                chart.data.datasets[2] = {};
            }
        } else if (data.unreplicatedDataset.every(x => x === 0) && data.isogenicDataset.every(x => x === 0) && data.anisogenicDataset.some(x => x > 0)) {
            chart.data.datasets[0] = { label: 'anisogenic', data: data.anisogenicDataset, backgroundColor: colors[0] };
            chart.data.datasets[1] = {};
            chart.data.datasets[2] = {};
        }
        chart.options.onClick.baseSearchUri = `${linkUri}${award ? award.name : ''}${objectQuery}`;
        chart.update();

        document.getElementById(`${statusChartId}-${this.props.ident}-legend`).innerHTML = chart.generateLegend();
    }

    createChart(chartId) {
        const { experiments, unreplicated, isogenic, anisogenic } = this.props;
        // Object with arrays of status labels, unreplicatedDataset, isogenicDataset, anisogenicDataset
        const data = StatusData(experiments, unreplicated, isogenic, anisogenic);
        const replicatelabels = ['unreplicated', 'isogenic', 'anisogenic'];
        const colors = replicatelabels.map((label, i) => statusColorList[i % statusColorList.length]);

        createBarChart(chartId, data, colors, replicatelabels, 'Replication', `${this.props.linkUri}${this.props.award ? this.props.award.name : ''}`, (uri) => { this.context.navigate(uri); })
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
                {this.relevantData.length ?
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
    unreplicated: PropTypes.object,
    anisogenic: PropTypes.object,
    isogenic: PropTypes.object,
    objectQuery: PropTypes.string,
};

StatusExperimentChart.defaultProps = {
    award: null,
    statuses: [],
    unreplicated: {},
    anisogenic: {},
    isogenic: {},
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
        if (this.relevantData.length) {
            this.createChart(`${statusChartId}-${this.props.ident}`, this.relevantData);
        }
    }

    componentDidUpdate() {
        if (this.relevantData.length) {
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
                {this.relevantData.length ?
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
    if (categories && categories.facets && categories.facets.length) {
        const genusFacet = categories.facets.find(facet => facet.field === query);
        categorySpeciesArray = (genusFacet && genusFacet.terms && genusFacet.terms.length) ? genusFacet.terms : [];
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
    const { award, experiments, annotations, antibodies, biosamples, handleClick, selectedOrganisms, unreplicated, isogenic, anisogenic, controls } = props;

    // Put all search-related configuration data in one consistent place.
    const searchData = {
        experiments: {
            ident: 'experiments',
            data: [],
            labs: [],
            categoryData: [],
            statuses: [],
            categoryFacet: 'assay_title',
            title: 'Assays',
            uriBase: '/search/?type=Experiment&target.investigated_as!=control&award.name=',
            linkUri: '/matrix/?type=Experiment&target.investigated_as!=control&award.name=',
        },
        annotations: {
            ident: 'annotations',
            data: [],
            labs: [],
            categoryData: [],
            statuses: [],
            categoryFacet: 'annotation_type',
            title: 'Annotation Types',
            uriBase: '/search/?type=Annotation&award.name=',
            linkUri: '/matrix/?type=Annotation&award.name=',
        },
        biosamples: {
            ident: 'biosamples',
            data: [],
            labs: [],
            categoryData: [],
            statuses: [],
            categoryFacet: 'biosample_type',
            title: 'Biosamples',
            uriBase: '/search/?type=Biosample&award.name=',
            linkUri: '/report/?type=Biosample&award.name=',
        },
        antibodies: {
            ident: 'antibodies',
            data: [],
            labs: [],
            categoryData: [],
            statuses: [],
            categoryFacet: 'lot_reviews.status',
            title: 'Antibodies',
            uriBase: 'type=AntibodyLot&award=/awards',
            linkUri: '/report/?type=AntibodyLot&award=/awards/',
        },
        controls: {
            ident: 'experiments',
            data: [],
            labs: [],
            categoryData: [],
            statuses: [],
            categoryFacet: 'assay_title',
            title: 'Assays',
            uriBase: '/search/?type=Experiment&target.investigated_as=control&award.name=',
            linkUri: '/matrix/?type=Experiment&target.investigated_as=control&award.name=',
        },
    };
    // Match the species to their genera
    const speciesGenusMap = {
        'Homo sapiens': 'HUMAN',
        'Mus musculus': 'MOUSE',
        'Caenorhabditis elegans': 'WORM',
        'Drosophila melanogaster': 'FLY',
        'Drosophila pseudoobscura': 'FLY',
        'Drosophila simulans': 'FLY',
        'Drosophila mojavensis': 'FLY',
        'Drosophila ananassae': 'FLY',
        'Drosophila virilis': 'FLY',
        'Drosophila yakuba': 'FLY',
    };

    // Find the chart data in the returned facets.
    const experimentsConfig = searchData.experiments;
    const annotationsConfig = searchData.annotations;
    const biosamplesConfig = searchData.biosamples;
    const antibodiesConfig = searchData.antibodies;
    const controlsConfig = searchData.controls;
    let experimentSpeciesArray;
    let annotationSpeciesArray;
    let biosampleSpeciesArray;
    let antibodySpeciesArray;
    // let controlSpeciesArray;
    const updatedSpeciesArray = [];
    searchData.experiments.data = (experiments && experiments.facets) || [];
    searchData.annotations.data = (annotations && annotations.facets) || [];
    searchData.biosamples.data = (biosamples && biosamples.facets) || [];
    searchData.antibodies.data = (antibodies && antibodies.facets) || [];
    searchData.controls.data = (controls && controls.facets) || [];

    ['experiments', 'annotations', 'antibodies', 'biosamples', 'controls'].forEach((chartCategory) => {
        if (searchData[chartCategory].data.length) {
            // Get the array of lab data.
            const labFacet = searchData[chartCategory].data.find(facet => facet.field === 'lab.title');
            searchData[chartCategory].labs = (labFacet && labFacet.terms && labFacet.terms.length) ? labFacet.terms.sort((a, b) => (a.key < b.key ? -1 : (a.key > b.key ? 1 : 0))) : [];

            // Get the array of data specific to experiments, annotations, or antibodies
            const categoryFacet = searchData[chartCategory].data.find(facet => facet.field === searchData[chartCategory].categoryFacet);
            searchData[chartCategory].categoryData = (categoryFacet && categoryFacet.terms && categoryFacet.terms.length) ? categoryFacet.terms : [];

            // Get the array of status data.
            const statusFacet = searchData[chartCategory].data.find(facet => facet.field === 'status');
            searchData[chartCategory].statuses = (statusFacet && statusFacet.terms && statusFacet.terms.length) ? statusFacet.terms : [];
        }
    });
    // If there are experiements, then the corresponding species are added to the array of species
    if (experiments && experiments.facets && experiments.facets.length) {
        const genusFacet = experiments.facets.find(facet => facet.field === 'replicates.library.biosample.donor.organism.scientific_name');
        experimentSpeciesArray = (genusFacet && genusFacet.terms && genusFacet.terms.length) ? genusFacet.terms : [];
        const experimentSpeciesArrayLength = experimentSpeciesArray.length;
        for (let j = 0; j < experimentSpeciesArrayLength; j += 1) {
            if (experimentSpeciesArray[j].doc_count !== 0) {
                updatedSpeciesArray.push(experimentSpeciesArray[j].key);
            }
        }
    }
    // If there are annotations, then the corresponding species are added to the array of species
    if (annotations && annotations.facets && annotations.facets.length) {
        const genusFacet = annotations.facets.find(facet => facet.field === 'organism.scientific_name');
        annotationSpeciesArray = (genusFacet && genusFacet.terms && genusFacet.terms.length) ? genusFacet.terms : [];
        const annotationSpeciesArrayLength = annotationSpeciesArray.length;
        for (let j = 0; j < annotationSpeciesArrayLength; j += 1) {
            if (annotationSpeciesArray[j].doc_count !== 0) {
                updatedSpeciesArray.push(annotationSpeciesArray[j].key);
            }
        }
    }
    // If there are biosamples, then the corresponding species are iadded to the array of species
    if (biosamples && biosamples.facets && biosamples.facets.length) {
        const genusFacet = biosamples.facets.find(facet => facet.field === 'organism.scientific_name=');
        biosampleSpeciesArray = (genusFacet && genusFacet.terms && genusFacet.terms.length) ? genusFacet.terms : [];
        const biosampleSpeciesArrayLength = biosampleSpeciesArray.length;
        for (let j = 0; j < biosampleSpeciesArrayLength; j += 1) {
            if (biosampleSpeciesArray[j].doc_count !== 0) {
                updatedSpeciesArray.push(biosampleSpeciesArray[j].key);
            }
        }
    }
    // If there are antibodies, then the corresponding species are added to the array of species
    if (antibodies && antibodies.facets && antibodies.facets.length) {
        const genusFacet = antibodies.facets.find(facet => facet.field === 'targets.organism.scientific_name=');
        antibodySpeciesArray = (genusFacet && genusFacet.terms && genusFacet.terms.length) ? genusFacet.terms : [];
        const antibodySpeciesArrayLength = antibodySpeciesArray.length;
        for (let j = 0; j < antibodySpeciesArrayLength; j += 1) {
            if (antibodySpeciesArray[j].doc_count !== 0) {
                updatedSpeciesArray.push(antibodySpeciesArray[j].key);
            }
        }
    }
    // Array of species is converted to an array of genera
    let updatedGenusArray = updatedSpeciesArray.map(species => speciesGenusMap[species]);

    // Array of genera is deduplicated
    updatedGenusArray = _.uniq(updatedGenusArray);
    const ExperimentQuery = generateQuery(selectedOrganisms, 'replicates.library.biosample.donor.organism.scientific_name=');
    const AnnotationQuery = generateQuery(selectedOrganisms, 'organism.scientific_name=');

    // For each category (experiments, annotations, biosamples, and antibodies), the corresponding species are added to the array of species
    generateUpdatedSpeciesArray(experiments, 'replicates.library.biosample.donor.organism.scientific_name', updatedSpeciesArray);
    generateUpdatedSpeciesArray(annotations, 'organism.scientific_name', updatedSpeciesArray);
    generateUpdatedSpeciesArray(biosamples, 'organism.scientific_name=', updatedSpeciesArray);
    generateUpdatedSpeciesArray(antibodies, 'targets.organism.scientific_name=', updatedSpeciesArray);

    // Array of species is converted to an array of genera
    updatedGenusArray = updatedSpeciesArray.map(species => speciesGenusMap[species]);

    return (
        <div className="award-charts">
            <div> <GenusButtons handleClick={handleClick} selectedOrganisms={selectedOrganisms} updatedGenusArray={updatedGenusArray} /> </div>
            <PanelBody>
                <div className="award-chart__group-wrapper">
                    <h2>Assays {experimentsConfig.labs.length ?
                    <a className="btn btn-info btn-sm reporttitle" href={`/report/?type=Experiment&${ExperimentQuery}&award.name=${award.name}`} title="View tabular report"><svg id="Table" data-name="Table" xmlns="http://www.w3.org/2000/svg" width="29" height="17" viewBox="0 0 29 17" className="svg-icon svg-icon-table"><title>table-tab-icon </title><path d="M22,0H0V17H29V0H22ZM21,4.33V8H15V4.33h6ZM15,9h6v3H15V9Zm-1,3H8V9h6v3Zm0-7.69V8H8V4.33h6Zm-13,0H7V8H1V4.33ZM1,9H7v3H1V9Zm0,7V13H7v3H1Zm7,0V13h6v3H8Zm7,0V13h6v3H15Zm13,0H22V13h6v3Zm0-4H22V9h6v3Zm0-4H22V4.33h6V8Z" /></svg></a>
                    : null}</h2>
                    {experimentsConfig.labs.length ?
                        <div>
                            <div className="award-chart__group">
                                <LabChart
                                    award={award}
                                    labs={experimentsConfig.labs}
                                    linkUri={experimentsConfig.linkUri}
                                    ident={experimentsConfig.ident}
                                    objectQuery={ExperimentQuery}
                                />
                                <CategoryChart
                                    award={award}
                                    categoryData={experimentsConfig.categoryData || []}
                                    title={experimentsConfig.title}
                                    linkUri={experimentsConfig.linkUri}
                                    categoryFacet={experimentsConfig.categoryFacet}
                                    ident={experimentsConfig.ident}
                                    selectedOrganisms={updatedGenusArray}
                                    objectQuery={ExperimentQuery}
                                />
                                <StatusExperimentChart
                                    award={award}
                                    experiments={experiments}
                                    statuses={experimentsConfig.statuses || []}
                                    linkUri={experimentsConfig.linkUri}
                                    ident={experimentsConfig.ident}
                                    unreplicated={unreplicated}
                                    isogenic={isogenic}
                                    anisogenic={anisogenic}
                                    selectedOrganisms={updatedGenusArray}
                                    objectQuery={ExperimentQuery}
                                />
                            </div>
                        </div>
                    :
                        <div className="browser-error">No assays were submitted under this award</div>
                    }
                </div>
                <div className="award-chart__group-wrapper">
                    <h2>Annotations {annotationsConfig.labs.length ?
                    <a className="btn btn-info btn-sm reporttitle" href={`/report/?type=Annotation&${AnnotationQuery}&award.name=${award.name}`} title="View tabular report"><svg id="Table" data-name="Table" xmlns="http://www.w3.org/2000/svg" width="29" height="17" viewBox="0 0 29 17" className="svg-icon svg-icon-table"><title>table-tab-icon </title><path d="M22,0H0V17H29V0H22ZM21,4.33V8H15V4.33h6ZM15,9h6v3H15V9Zm-1,3H8V9h6v3Zm0-7.69V8H8V4.33h6Zm-13,0H7V8H1V4.33ZM1,9H7v3H1V9Zm0,7V13H7v3H1Zm7,0V13h6v3H8Zm7,0V13h6v3H15Zm13,0H22V13h6v3Zm0-4H22V9h6v3Zm0-4H22V4.33h6V8Z" /></svg></a>
                    : null}</h2>
                    {annotationsConfig.labs.length ?
                        <div>
                            <div className="award-chart__group">
                                <LabChart
                                    award={award}
                                    labs={annotationsConfig.labs}
                                    linkUri={annotationsConfig.linkUri}
                                    ident={annotationsConfig.ident}
                                    selectedOrganisms={selectedOrganisms}
                                    objectQuery={AnnotationQuery}
                                />
                                <CategoryChart
                                    award={award}
                                    categoryData={annotationsConfig.categoryData || []}
                                    linkUri={annotationsConfig.linkUri}
                                    categoryFacet={annotationsConfig.categoryFacet}
                                    title={annotationsConfig.title}
                                    ident={annotationsConfig.ident}
                                    selectedOrganisms={selectedOrganisms}
                                    objectQuery={AnnotationQuery}
                                />
                                <StatusChart
                                    award={award}
                                    statuses={annotationsConfig.statuses || []}
                                    linkUri={annotationsConfig.linkUri}
                                    ident={annotationsConfig.ident}
                                    selectedOrganisms={selectedOrganisms}
                                    objectQuery={AnnotationQuery}
                                />
                            </div>
                        </div>
                    :
                        <div className="browser-error">No annotations were submitted under this award</div>
                    }
                </div>
                <div className="award-chart__group-wrapper">
                    <h2>Reagents</h2>
                    {antibodiesConfig.categoryData.length || biosamplesConfig.categoryData.length || experimentsConfig.statuses.length ?
                        <div className="award-chart__group">
                            <AntibodyChart
                                award={award}
                                categoryData={antibodiesConfig.categoryData}
                                categoryFacet={antibodiesConfig.categoryFacet}
                                linkUri={antibodiesConfig.linkUri}
                                ident={antibodiesConfig.ident}
                                selectedOrganisms={selectedOrganisms}
                            />
                            <BiosampleChart
                                award={award}
                                categoryData={biosamplesConfig.categoryData}
                                categoryFacet={biosamplesConfig.categoryFacet}
                                linkUri={biosamplesConfig.linkUri}
                                ident={biosamplesConfig.ident}
                                selectedOrganisms={selectedOrganisms}
                            />
                            <ControlsChart
                                award={award}
                                experiments={experiments}
                                statuses={controlsConfig.statuses || []}
                                linkUri={controlsConfig.linkUri}
                                ident={controlsConfig.ident}
                                objectQuery={ExperimentQuery}
                            />
                        </div>
                    :
                        <div className="browser-error">No reagents were submitted under this award</div>
                    }
                </div>
            </PanelBody>
        </div>
    );
};

ChartRenderer.propTypes = {
    award: PropTypes.object.isRequired, // Award being displayed
    experiments: PropTypes.object, // Search result of matching experiments
    annotations: PropTypes.object, // Search result of matching annotations
    antibodies: PropTypes.object, // Search result of matching antibodies
    biosamples: PropTypes.object, // Search result of matching biosamples
    unreplicated: PropTypes.object,
    isogenic: PropTypes.object,
    anisogenic: PropTypes.object,
    controls: PropTypes.object,
    handleClick: PropTypes.func.isRequired, // Function to call when a button is clicked
    selectedOrganisms: PropTypes.array, // Array of currently selected buttons
};

ChartRenderer.defaultProps = {
    experiments: {},
    annotations: {},
    antibodies: {},
    biosamples: {},
    unreplicated: {},
    isogenic: {},
    anisogenic: {},
    controls: {},
    selectedOrganisms: [],
};

// Create new tabdisplay of genus buttons
class GenusButtons extends React.Component {
    render() {
        const { updatedGenusArray, selectedOrganisms, handleClick } = this.props;
        // If genera exist, then the button for each specific genus is created
        if (updatedGenusArray.length) {
            return (
                <div className="organism-selector" ref="tabdisplay">
                    {updatedGenusArray.indexOf('HUMAN') !== -1 ?
                        <OrganismSelector organism="HUMAN" selected={selectedOrganisms.indexOf('HUMAN') !== -1} organismButtonClick={handleClick} />
                    :
                    null}
                    {updatedGenusArray.indexOf('MOUSE') !== -1 ?
                        <OrganismSelector organism="MOUSE" selected={selectedOrganisms.indexOf('MOUSE') !== -1} organismButtonClick={handleClick} />
                    :
                    null}
                    {updatedGenusArray.indexOf('WORM') !== -1 ?
                        <OrganismSelector organism="WORM" selected={selectedOrganisms.indexOf('WORM') !== -1} organismButtonClick={handleClick} />
                    :
                    null}
                    {updatedGenusArray.indexOf('FLY') !== -1 ?
                        <OrganismSelector organism="FLY" selected={selectedOrganisms.indexOf('FLY') !== -1} organismButtonClick={handleClick} />
                    :
                    null}
                </div>
            );
        }
        return null;
    }
}

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
    assay_term_name: {
        title: 'Assay name',
    },

    proposed_count: {
        title: 'Proposed count',
    },

    deliverable_unit: {
        title: 'Biosample',
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


const ExperimentDateRenderer = (props) => {
    const { experiments, awards } = props;

    if (experiments) {
        return <ExperimentDate experiments={experiments.facets} awards={awards} />;
    }
    return null;
};

ExperimentDateRenderer.propTypes = {
    experiments: PropTypes.object,
    awards: PropTypes.object,
};

ExperimentDateRenderer.defaultProps = {
    experiments: null,
    awards: null,
};


// Overall component to render the cumulative line chart
export const ExperimentDate = (props) => {
    const { experiments, award, panelCss, panelHeadingCss } = props;
    let releasedDates = [];
    let submittedDates = [];
    let deduplicatedreleased = {};
    let deduplicatedsubmitted = {};
    const cumulativedatasetReleased = [];
    const cumulativedatasetSubmitted = [];
    const accumulatorreleased = 0;
    const accumulatorsubmitted = 0;

    // Search experiments for month_released and date_submitted in facets
    if (experiments && experiments.length) {
        const monthReleasedFacet = experiments.find(facet => facet.field === 'month_released');
        const dateSubmittedFacet = experiments.find(facet => facet.field === 'date_submitted');
        releasedDates = (monthReleasedFacet && monthReleasedFacet.terms && monthReleasedFacet.terms.length) ? monthReleasedFacet.terms : [];
        submittedDates = (dateSubmittedFacet && dateSubmittedFacet.terms && dateSubmittedFacet.terms.length) ? dateSubmittedFacet.terms : [];
    }

    // Take an array of date facet terms and return an array of terms sorted by date.
    function sortTerms(dateArray) {
        // Use Moment to format arrays of submitted and released date
        const standardTerms = dateArray.map((term) => {
            const standardDate = moment(term.key, ['MMMM, YYYY', 'YYYY-MM']).format('YYYY-MM');
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

    function fillDates(sortedArray, deduplicated, awardStartDate) {
        const fillArray = [];

        // Add an object with the award start date to both arrays
        sortedArray.unshift({ key: awardStartDate, doc_count: 0 });

        // Add objects to the array with doc_count 0 for the missing months
        const sortedTermsLength = sortedArray.length;
        for (let j = 0; j < sortedTermsLength - 1; j += 1) {
            fillArray.push(sortedArray[j]);
            const startDate = moment(sortedArray[j].key);
            const endDate = moment(sortedArray[j + 1].key);
            const monthdiff = endDate.diff(startDate, 'months', false);
            if (monthdiff > 1) {
                for (let i = 0; i < monthdiff; i += 1) {
                    fillArray.push({ key: startDate.add(1, 'months').format('YYYY-MM'), doc_count: 0 });
                }
            }
        }
        fillArray.push(sortedArray[sortedArray - 1]);

        // Remove any objects with keys before the start date of the award
        const shortenedArray = [];
        for (let j = 0; j < fillArray.length - 2; j += 1) {
            if (moment(fillArray[j].key).isSameOrAfter(awardStartDate, 'date')) {
                shortenedArray.push(fillArray[j]);
            }
        }
        const formatTerms = shortenedArray.map((term) => {
            const formattedDate = moment(term.key, ['YYYY-MM']).format('MMM YY');
            return { key: formattedDate, doc_count: term.doc_count };
        });
        // Deduplicate dates
        formatTerms.forEach((elem) => {
            if (deduplicated[elem.key]) {
                deduplicated[elem.key] += elem.doc_count;
            } else {
                deduplicated[elem.key] = elem.doc_count;
            }
        });
        return (deduplicated);
    }

    function createDataset(deduplicated, accumulatorType, cumulativeData) {
        let cumulativedataset = cumulativeData;
        let accumulator = accumulatorType;
        // Create an array of data from objects' doc_counts
        const dataset = Object.keys(deduplicated).map(item => deduplicated[item]);
        // Make the data cumulative
        const accumulatedData = dataset.map((term) => {
            accumulator += term;
            cumulativedataset = accumulator;
            return cumulativedataset;
        });
        return (accumulatedData);
    }

    let accumulatedDataReleased = [];
    let accumulatedDataSubmitted = [];
    let date = [];
    if (releasedDates.length || submittedDates.length) {
        const sortedreleasedTerms = sortTerms(releasedDates);
        const sortedsubmittedTerms = sortTerms(submittedDates);

        // Add an object with the most current date to one of the arrays.
        if ((releasedDates && releasedDates.length) && (submittedDates && submittedDates.length)) {
            if (sortedreleasedTerms.length && moment(sortedsubmittedTerms[sortedsubmittedTerms.length - 1].key).isAfter(sortedreleasedTerms[sortedreleasedTerms.length - 1].key, 'date')) {
                sortedreleasedTerms.push({ key: sortedsubmittedTerms[sortedsubmittedTerms.length - 1].key, doc_count: 0 });
            } else if (sortedsubmittedTerms.length && moment(sortedsubmittedTerms[sortedsubmittedTerms.length - 1].key).isBefore(sortedreleasedTerms[sortedreleasedTerms.length - 1].key, 'date')) {
                sortedsubmittedTerms.push({ key: sortedreleasedTerms[sortedreleasedTerms.length - 1].key, doc_count: 0 });
            }
        }

        // Figure out the award start date. If none, use the earlier of the earliest released or submitted dates.
        let awardStartDate;
        if (award && award.start_date) {
            awardStartDate = moment(award.start_date, 'YYYY-MM-DD').format('YYYY-MM');
        } else {
            const earliestReleased = sortedreleasedTerms[0].key;
            const earliestSubmitted = sortedsubmittedTerms[0].key;
            awardStartDate = earliestReleased < earliestSubmitted ? earliestReleased : earliestSubmitted;
        }
        deduplicatedreleased = fillDates(sortedreleasedTerms, deduplicatedreleased, awardStartDate);
        deduplicatedsubmitted = fillDates(sortedsubmittedTerms, deduplicatedsubmitted, awardStartDate);

        // Create an array of dates.
        date = Object.keys(deduplicatedreleased).map(term => term);
        accumulatedDataReleased = createDataset(deduplicatedreleased, accumulatorreleased, cumulativedatasetReleased);
        accumulatedDataSubmitted = createDataset(deduplicatedsubmitted, accumulatorsubmitted, cumulativedatasetSubmitted);
    }

    return (
        <div>
            {accumulatedDataReleased.length || accumulatedDataSubmitted.length ?
                <Panel addClasses={panelCss}>
                    <PanelHeading addClasses={panelHeadingCss}>
                        <h4>Cumulative Number of Experiments</h4>
                    </PanelHeading>
                    <PanelBody>
                        <CumulativeGraph releaseddatavalue={accumulatedDataReleased} submitteddatavalue={accumulatedDataSubmitted} monthReleased={date} />
                    </PanelBody>
                </Panel>
            : null}
        </div>
    );
};

ExperimentDate.propTypes = {
    experiments: PropTypes.array,
    award: PropTypes.object,
    panelCss: PropTypes.string,
    panelHeadingCss: PropTypes.string,
};

ExperimentDate.defaultProps = {
    experiments: [],
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
            <button onClick={this.buttonClick} className={`organism-selector__tab${selected ? ' organism-selector--selected' : ''}`} >
            {organism} </button>
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
            selectedOrganisms: [], //create empty array of selected organism tabs
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
        const AnnotationQuery = generateQuery(this.state.selectedOrganisms, 'organism.scientific_name=');
        const ExperimentQuery = generateQuery(this.state.selectedOrganisms, 'replicates.library.biosample.donor.organism.scientific_name=');
        const BiosampleQuery = generateQuery(this.state.selectedOrganisms, 'organism.scientific_name=');
        const AntibodyQuery = generateQuery(this.state.selectedOrganisms, 'targets.organism.scientific_name=');
        return (
            <Panel>
                <PanelHeading>
                    <h4>Current Production</h4>
                    <ProjectBadge award={award} addClasses="badge-heading" />
                </PanelHeading>
                <div>
                    <FetchedData ignoreErrors>
                        <Param name="experiments" url={`/search/?type=Experiment&target.investigated_as!=control&award.name=${award.name}${ExperimentQuery}`} />
                        <Param name="annotations" url={`/search/?type=Annotation&award.name=${award.name}${AnnotationQuery}`} />
                        <Param name="biosamples" url={`/search/?type=Biosample&award.name=${award.name}${BiosampleQuery}`} />
                        <Param name="antibodies" url={`/search/?type=AntibodyLot&award=${award['@id']}${AntibodyQuery}`} />
                        <Param name="controls" url={`/search/?type=Experiment&target.investigated_as=control&award.name=${award.name}${ExperimentQuery}`} />
                        <Param name="unreplicated" url={`/search/?type=Experiment&target.investigated_as!=control&replication_type=unreplicated&award.name=${award.name}${ExperimentQuery}`} />
                        <Param name="isogenic" url={`/search/?type=Experiment&target.investigated_as!=control&replication_type=isogenic&award.name=${award.name}${ExperimentQuery}`} />
                        <Param name="anisogenic" url={`/search/?type=Experiment&target.investigated_as!=control&replication_type=anisogenic&award.name=${award.name}${ExperimentQuery}`} />
                        <ChartRenderer award={award} updatedGenusArray={updatedGenusArray} handleClick={this.handleClick} selectedOrganisms={this.state.selectedOrganisms} />
                    </FetchedData>
                </div>
            </Panel>
        );
    }
}

AwardCharts.propTypes = {
    award: PropTypes.object.isRequired, // Award represented by this chart
    updatedGenusArray: PropTypes.array, //Array of existing genera
};
AwardCharts.defaultProps = {
    updatedGenusArray: [],
};

class LineChart extends React.Component {
    render() {
        const { award } = this.props;
        return (
            <div>
                <FetchedData ignoreErrors>
                    <Param name="experiments" url={`/search/?type=Experiment&award.name=${award.name}`} />
                    <ExperimentDateRenderer award={award} />
                </FetchedData>
            </div>
        );
    }
}

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
                !_.isEqual(this.props.submitteddatavalue, nextProps.submitteddatavalue) ||
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
        const { releaseddatavalue, submitteddatavalue, monthReleased } = this.props;
        require.ensure(['chart.js'], (require) => {
            const Chart = require('chart.js');
            const ctx = document.getElementById('myGraph').getContext('2d');

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
                                autoSkip: true,
                                maxTicksLimit: 15, // sets maximum number of x-axis labels
                            },
                        }],
                        yAxes: [{
                            stacked: true,
                        }],
                    },
                },
                data: {
                    labels: monthReleased,
                    datasets: [{
                        label: 'Date Released',
                        data: releaseddatavalue,
                        backgroundColor: '#604a7b',
                    },
                    {
                        label: 'Date Submitted',
                        data: submitteddatavalue,
                        backgroundColor: '#ccc1da',
                    }],
                },
            });
        });
    }

    updateChart() {
        const { releaseddatavalue, submitteddatavalue, monthReleased } = this.props;

        this.chart.data.labels = monthReleased;
        this.chart.data.datasets[0].data = releaseddatavalue;
        this.chart.data.datasets[1].data = submitteddatavalue;
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
    submitteddatavalue: PropTypes.array.isRequired,
    monthReleased: PropTypes.array.isRequired,
};

CumulativeGraph.defaultProps = {
    data: [],
    monthReleased: [],
};

// Create Affiliated Labs list with carriage return to be displayed under description panel
const AffiliatedLabsArray = (props) => {
    const { labs, award } = props;
    const labsArray = labs['@graph'].map(term => term.title);
    const sortedArray = award.pi && award.pi.lab ? _.without(labsArray, award.pi.lab.title) : labsArray;
    return (
        <div>
            {sortedArray.map((item, index) => <div key={index}>{item}</div>)}
        </div>
    );
};

AffiliatedLabsArray.propTypes = {
    labs: PropTypes.object,
    award: PropTypes.object.isRequired,
};

AffiliatedLabsArray.defaultProps = {
    labs: {},
};

class AffiliatedLabs extends React.Component {
    render() {
        const { award } = this.props;
        return (
            <FetchedData>
                <Param name="labs" url={`/search/?type=Lab&awards.name=${award.name}`} />
                <AffiliatedLabsArray award={award} />
            </FetchedData>
        );
    }
}

AffiliatedLabs.propTypes = {
    award: PropTypes.object.isRequired, // Award represented by this chart
};

class Award extends React.Component {
    render() {
        // const { award } = this.props;
        const { context } = this.props;
        const statuses = [{ status: context.status, title: 'Status' }];
        const loggedIn = !!(this.context.session && this.context.session['auth.userid']);

        return (
            <div className={globals.itemClass(context, 'view-item')}>
                <header className="row">
                    <div className="col-sm-12">
                        {context.pi && context.pi.lab ?
                            <h2>AWARD SUMMARY for {context.pi.lab.title} ({context.name})</h2>
                            :
                            <h2>AWARD SUMMARY for ({context.name})</h2>
                        }
                        <div className="status-line">
                            <div className="characterization-status-labels">
                                <StatusLabel status={statuses} />
                            </div>
                        </div>
                    </div>
                </header>
                <AwardCharts award={context} />
                <Panel>
                    <PanelHeading>
                        <h4>{context.title || context.name}</h4>
                    </PanelHeading>
                    <PanelBody>
                        {context.description ?
                            <div className="two-column-long-text two-column-long-text--gap">
                                <p>{context.description}</p>
                            </div>
                        :
                            <p className="browser-error">Award has no description</p>
                        }
                        <div className="description">
                            <hr />
                            <div className="description__columnone">
                                <dl className="key-value">
                                    <div data-test="projectinfo">
                                        <dt>NIH Grant</dt>
                                        <dd><a href={context.url} title={`${context.name} NIH Grant`}>{context.name}</a></dd>
                                    </div>
                                </dl>
                                {context.pi && context.pi.lab ?
                                    <dl className="key-value">
                                        <div data-test="pi">
                                            <dt>Primary Investigator</dt><dd>{context.pi.lab.title}</dd>
                                        </div>
                                    </dl>
                                :
                                    null
                                }
                                <dl className="key-value">
                                    <div data-test="labs">
                                        <dt>Affiliated Labs</dt>
                                        <dd><AffiliatedLabs award={context} /> </dd>
                                    </div>
                                </dl>
                            </div>
                            <div className="description__columnone">
                                <dl className="key-value">
                                    <div data-test="dates">
                                        <dt>Dates</dt>
                                        <dd>{moment(context.start_date).format('MMMM DD, YYYY')} - {moment(context.end_date).format('MMMM DD, YYYY')}</dd>
                                    </div>
                                </dl>
                                <dl className="key-value">
                                    <div data-test="rfa">
                                        <dt>Award RFA</dt>
                                        <dd>{context.rfa}</dd>
                                    </div>
                                </dl>
                            </div>
                        </div>
                    </PanelBody>
                </Panel>

                {context.milestones && loggedIn ?
                    <MilestonesTable award={context} />
                : null}

                <LineChart award={context} />
            </div>
        );
    }
}

Award.propTypes = {
    context: PropTypes.object.isRequired, // Award object being rendered
};

Award.contextTypes = {
    session: PropTypes.object, // Login information
};

globals.contentViews.register(Award, 'Award');

const Listing = (props) => {
    const result = props.context;
    return (
        <li>
            <div className="clearfix">
                <PickerActions {...props} />
                <div className="pull-right search-meta">
                    <p className="type meta-title">Award</p>
                    <p className="type">{` ${result.name}`}</p>
                    <p className="type meta-status">{` ${result.status}`}</p>
                </div>
                <div className="accession">
                    <a href={result['@id']}>{result.title}</a>
                </div>
                <div className="data-row">
                    <div><strong>Project / RFA: </strong>{result.project} / {result.rfa}</div>
                </div>
            </div>
        </li>
    );
};

Listing.propTypes = {
    context: PropTypes.object.isRequired, // Object whose search result we're displaying
};

globals.listingViews.register(Listing, 'Award');
