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
import StatusLabel from './statuslabel';

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
                                text.push(`<li><a href="${baseSearchUri}${chartLabels[i]}">`);
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

                        if (activePoints[0]) { // if click on wrong area, do nothing
                            const clickedElementIndex = activePoints[0]._index;
                            const term = chart.data.labels[clickedElementIndex];
                            navigate(`${baseSearchUri}${globals.encodedURIComponent(term)}`);
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

function createBarChart(chartId, unreplicatedLabel, unreplicatedDataset, isogenicDataset, anisogenicDataset, colors, labels, replicatelabels, baseSearchUri, navigate) {
    return new Promise((resolve) => {
        require.ensure(['chart.js'], (require) => {
            const Chart = require('chart.js');

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
                    labels,
                    datasets: [{
                        label: 'unreplicated',
                        data: unreplicatedDataset,
                        backgroundColor: colors[0],
                    }, {
                        label: 'isogenic',
                        data: isogenicDataset,
                        backgroundColor: colors[1],
                    }, {
                        label: 'anisogenic',
                        data: anisogenicDataset,
                        backgroundColor: colors[2],
                    }],
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
                        duration: 200,
                    },
                    legendCallback: (chartInstance) => {
                        const chartLabels = replicatelabels;
                        const LegendLabels = [];
                        // If data array has value, add to legend
                        for (let i = 0; i < chartLabels.length; i += 1) {
                            if (chartInstance.data.datasets[i].data.length !== 0) {
                                LegendLabels.push(chartInstance.data.datasets[i].label);
                            }
                        }
                        const text = [];
                        text.push('<ul>');
                        for (let i = 0; i < LegendLabels.length; i += 1) {
                            if (LegendLabels[i]) {
                                text.push(`<li><a href="${baseSearchUri}${LegendLabels[i]}">`);
                                text.push(`<i class="icon icon-circle chart-legend-chip" aria-hidden="true" style="color:${chartInstance.data.datasets[i].backgroundColor}"></i>`);
                                text.push(`<span class="chart-legend-label">${LegendLabels[i]}</span>`);
                                text.push('</a></li>');
                            }
                        }
                        text.push('</ul>');
                        return text.join('');
                    },
                    onClick: function onClick(e) {
                        // React to clicks on pie sections
                        const activePoints = chart.getElementAtEvent(e);

                        if (activePoints[0]) { // if click on wrong area, do nothing
                            const clickedElementIndex = activePoints[0]._index;
                            const term = chart.data.labels[clickedElementIndex];
                            navigate(`${baseSearchUri}${globals.encodedURIComponent(term)}`);
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
class LabChart extends React.Component {
    constructor() {
        super();

        // Bind this to non-React components.
        this.createChart = this.createChart.bind(this);
        this.updateChart = this.updateChart.bind(this);
    }

    componentDidMount() {
        this.createChart(`${labChartId}-${this.props.ident}`, this.props.labs);
    }

    componentDidUpdate() {
        if (this.props.labs.length) {
            if (this.chart) {
                this.updateChart(this.chart, this.props.labs);
            } else {
                this.createChart(`${statusChartId}-${this.props.ident}`, this.props.labs);
            }
        } else if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    // Update existing chart with new data.
    updateChart(chart, facetData) {
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
        createDoughnutChart(chartId, values, labels, colors, `${this.props.linkUri}${this.props.award.name}&lab.title=`, (uri) => { this.context.navigate(uri); })
            .then((chartInstance) => {
                // Save the created chart instance.
                this.chart = chartInstance;
            });
    }

    render() {
        const { labs, ident } = this.props;

        // Calculate a (hopefully) unique ID to put on the DOM elements.
        const id = `${labChartId}-${ident}`;

        return (
            <div className="award-charts__chart">
                <div className="award-charts__title">
                    Lab
                </div>
                {labs.length ?
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
    award: PropTypes.object.isRequired, // Award being displayed
    labs: PropTypes.array.isRequired, // Array of labs facet data
    linkUri: PropTypes.string.isRequired, // Base URI for matrix links
    ident: PropTypes.string.isRequired, // Unique identifier to `id` the charts
};

LabChart.contextTypes = {
    navigate: PropTypes.func,
};

// Display and handle clicks in the chart of assays.
class CategoryChart extends React.Component {
    constructor() {
        super();
        this.createChart = this.createChart.bind(this);
        this.updateChart = this.updateChart.bind(this);
    }

    componentDidMount() {
        if (this.props.categoryData.length) {
            this.createChart(`${categoryChartId}-${this.props.ident}`, this.props.categoryData);
        }
    }

    componentDidUpdate() {
        if (this.props.categoryData.length) {
            if (this.chart) {
                this.updateChart(this.chart, this.props.categoryData);
            } else {
                this.createChart(`${categoryChartId}-${this.props.ident}`, this.props.categoryData);
            }
        } else if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    // Update existing chart with new data.
    updateChart(chart, facetData) {
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
        createDoughnutChart(chartId, values, labels, colors, `${linkUri}${award.name}&${categoryFacet}=`, (uri) => { this.context.navigate(uri); })
            .then((chartInstance) => {
                // Save the created chart instance.
                this.chart = chartInstance;
            });
    }

    render() {
        const { categoryData, title, ident } = this.props;

        // Calculate a (hopefully) unique ID to put on the DOM elements.
        const id = `${categoryChartId}-${ident}`;

        return (
            <div className="award-charts__chart">
                <div className="title">
                    {title}
                </div>
                {categoryData.length ?
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
    award: PropTypes.object.isRequired, // Award being displayed
    categoryData: PropTypes.array.isRequired, // Type-specific data to display in a chart
    title: PropTypes.string.isRequired, // Title to display above the chart
    linkUri: PropTypes.string.isRequired, // Element of matrix URI to select
    categoryFacet: PropTypes.string.isRequired, // Add to linkUri to link to matrix facet item
    ident: PropTypes.string.isRequired, // Unique identifier to `id` the charts
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
        if (this.props.categoryData.length) {
            this.createChart(`${categoryChartId}-${this.props.ident}`, this.props.categoryData);
        }
    }

    componentDidUpdate() {
        if (this.props.categoryData.length) {
            if (this.chart) {
                this.updateChart(this.chart, this.props.categoryData);
            } else {
                this.createChart(`${categoryChartId}-${this.props.ident}`, this.props.categoryData);
            }
        } else if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    // Update existing chart with new data.
    updateChart(chart, facetData) {
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
        chart.update();

        // Redraw the updated legend
        document.getElementById(`${categoryChartId}-${this.props.ident}-legend`).innerHTML = chart.generateLegend();
    }

    createChart(chartId, facetData) {
        const { award, categoryFacet } = this.props;

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
        createDoughnutChart(chartId, values, labels, colors, `${award.name}&${categoryFacet}=`, (uri) => { this.context.navigate(uri); })
            .then((chartInstance) => {
                // Save the created chart instance.
                this.chart = chartInstance;
            });
    }

    render() {
        const { categoryData, ident, award } = this.props;

        // Calculate a (hopefully) unique ID to put on the DOM elements.
        const id = `${categoryChartId}-${ident}`;

        return (
            <div className="award-charts__chart">
                <div className="award-charts__title">
                    Antibodies {categoryData.length ?
                    <a className="btn btn-info btn-xs reagentsreporttitle" href={`/report/?type=AntibodyLot&award=${award['@id']}&field=accession&field=lot_reviews.status&field=lot_reviews.targets.label&field=lot_reviews.targets.organism.scientific_name&field=source.title&field=product_id&field=lot_id&field=date_created`} title="View tabular report"><svg id="Table" data-name="Table" xmlns="http://www.w3.org/2000/svg" width="29" height="17" viewBox="0 0 29 17" className="svg-icon svg-icon-table"><title>table-tab-icon </title><path d="M22,0H0V17H29V0H22ZM21,4.33V8H15V4.33h6ZM15,9h6v3H15V9Zm-1,3H8V9h6v3Zm0-7.69V8H8V4.33h6Zm-13,0H7V8H1V4.33ZM1,9H7v3H1V9Zm0,7V13H7v3H1Zm7,0V13h6v3H8Zm7,0V13h6v3H15Zm13,0H22V13h6v3Zm0-4H22V9h6v3Zm0-4H22V4.33h6V8Z" /></svg></a>
                    :
                    null}
                    </div>
                {categoryData.length ?
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
        if (this.props.categoryData.length) {
            this.createChart(`${categoryChartId}-${this.props.ident}`, this.props.categoryData);
        }
    }

    componentDidUpdate() {
        if (this.props.categoryData.length) {
            if (this.chart) {
                this.updateChart(this.chart, this.props.categoryData);
            } else {
                this.createChart(`${categoryChartId}-${this.props.ident}`, this.props.categoryData);
            }
        } else if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    // Update existing chart with new data.
    updateChart(chart, facetData) {
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
        chart.update();

        // Redraw the updated legend
        document.getElementById(`${categoryChartId}-${this.props.ident}-legend`).innerHTML = chart.generateLegend();
    }

    createChart(chartId, facetData) {
        const { award, categoryFacet } = this.props;

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
        createDoughnutChart(chartId, values, labels, colors, `${award.name}&${categoryFacet}=`, (uri) => { this.context.navigate(uri); })
            .then((chartInstance) => {
                // Save the created chart instance.
                this.chart = chartInstance;
            });
    }

    render() {
        const { categoryData, ident, award } = this.props;

        // Calculate a (hopefully) unique ID to put on the DOM elements.
        const id = `${categoryChartId}-${ident}`;

        return (
            <div className="award-charts__chart">
                <div className="award-charts__title">
                    Biosamples {categoryData.length ?
                    <a className="btn btn-info btn-sm reagentsreporttitle" href={`/report/?type=Biosample&award.name=${award.name}`} title="View tabular report"><svg id="Table" data-name="Table" xmlns="http://www.w3.org/2000/svg" width="29" height="17" viewBox="0 0 29 17" className="svg-icon svg-icon-table"><title>table-tab-icon </title><path d="M22,0H0V17H29V0H22ZM21,4.33V8H15V4.33h6ZM15,9h6v3H15V9Zm-1,3H8V9h6v3Zm0-7.69V8H8V4.33h6Zm-13,0H7V8H1V4.33ZM1,9H7v3H1V9Zm0,7V13H7v3H1Zm7,0V13h6v3H8Zm7,0V13h6v3H15Zm13,0H22V13h6v3Zm0-4H22V9h6v3Zm0-4H22V4.33h6V8Z" /></svg></a>
                    :
                    null}
                </div>
                    {categoryData.length ?
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
};

BiosampleChart.contextTypes = {
    navigate: PropTypes.func,
};

// Function to be called in createChart and updateChart of class StatusExperimentChart, creates arrays for chart data
function StatusData(experiments, unreplicated, isogenic, anisogenic) {
    let unreplicatedArray;
    let isogenicArray;
    let anisogenicArray;
    const unreplicatedLabel = [];
    const unreplicatedDataset = [];
    const isogenicLabel = [];
    const isogenicDataset = [];
    const anisogenicLabel = [];
    const anisogenicDataset = [];

    if (experiments && experiments.facets && experiments.facets.length) {
        const unreplicatedFacet = unreplicated.facets.find(facet => facet.field === 'status');
        const isogenicFacet = isogenic.facets.find(facet => facet.field === 'status');
        const anisogenicFacet = anisogenic.facets.find(facet => facet.field === 'status');
        unreplicatedArray = (unreplicatedFacet && unreplicatedFacet.terms && unreplicatedFacet.terms.length) ? unreplicatedFacet.terms : [];
        isogenicArray = (isogenicFacet && isogenicFacet.terms && isogenicFacet.terms.length) ? isogenicFacet.terms : [];
        anisogenicArray = (anisogenicFacet && anisogenicFacet.terms && anisogenicFacet.terms.length) ? anisogenicFacet.terms : [];
    }
    const labels = ['proposed', 'started', 'submitted', 'released', 'deleted', 'replaced', 'archived', 'revoked'];
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
    }
    return ([labels, unreplicatedLabel, unreplicatedDataset, isogenicDataset, anisogenicDataset]);
}

class ControlsChart extends React.Component {
    constructor() {
        super();
        this.createChart = this.createChart.bind(this);
        this.updateChart = this.updateChart.bind(this);
    }

    componentDidMount() {
        if (this.props.statuses.length) {
            this.createChart(`${statusChartId}-${this.props.ident}-controls`, this.props.statuses);
        }
    }

    componentDidUpdate() {
        if (this.props.statuses.length) {
            if (this.chart) {
                this.updateChart(this.chart, this.props.statuses);
            } else {
                this.createChart(`${statusChartId}-${this.props.ident}-controls`, this.props.statuses);
            }
        } else if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    updateChart(chart, facetData) {
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

        // Calculate a (hopefully) unique ID to put on the DOM elements.
        const id = `${statusChartId}-${ident}-controls`;

        return (
            <div className="award-charts__chart">
                <div className="award-charts__title">
                    Status
                </div>
                {statuses.length ?
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
};

ControlsChart.defaultProps = {
    statuses: [],
};

class StatusExperimentChart extends React.Component {
    constructor() {
        super();
        this.createChart = this.createChart.bind(this);
        this.updateChart = this.updateChart.bind(this);
    }

    componentDidMount() {
        if (this.props.statuses.length) {
            this.createChart(`${statusChartId}-${this.props.ident}`, this.props.statuses);
        }
    }

    componentDidUpdate() {
        if (this.props.statuses.length) {
            if (this.chart) {
                this.updateChart(this.chart, this.props.statuses);
            } else {
                this.createChart(`${statusChartId}-${this.props.ident}`, this.props.statuses);
            }
        } else if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    updateChart(chart) {
        const { experiments, unreplicated, isogenic, anisogenic } = this.props;
        const data = StatusData(experiments, unreplicated, isogenic, anisogenic); // Array of datasets and labels
        const statusLabel = data[1];
        const unreplicatedDataset = data[2];
        const isogenicDataset = data[3];
        const anisogenicDataset = data[4];
        chart.data.datasets[0].data = unreplicatedDataset;
        chart.data.datasets[1].data = isogenicDataset;
        chart.data.datasets[2].data = anisogenicDataset;
        chart.data.labels = statusLabel;
        chart.update();

        document.getElementById(`${statusChartId}-${this.props.ident}-legend`).innerHTML = chart.generateLegend();
    }

    createChart(chartId) {
        const { experiments, unreplicated, isogenic, anisogenic } = this.props;
        const data = StatusData(experiments, unreplicated, isogenic, anisogenic); // Array of datasets and labels
        const labels = data[0];
        const statusLabel = data[1];
        const unreplicatedDataset = data[2];
        const isogenicDataset = data[3];
        const anisogenicDataset = data[4];
        const replicatelabels = ['unreplicated', 'isogenic', 'anisogenic'];
        const colors = replicatelabels.map((label, i) => statusColorList[i % statusColorList.length]);

        createBarChart(chartId, statusLabel, unreplicatedDataset, isogenicDataset, anisogenicDataset, colors, labels, replicatelabels, `${this.props.linkUri}${this.props.award.name}&status=`, (uri) => { this.context.navigate(uri); })
            .then((chartInstance) => {
                // Save the created chart instance.
                this.chart = chartInstance;
            });
    }

    render() {
        const { statuses, ident } = this.props;

        // Calculate a (hopefully) unique ID to put on the DOM elements.
        const id = `${statusChartId}-${ident}`;

        return (
            <div className="award-charts__chart">
                <div className="award-charts__title">
                    Status
                </div>
                 {statuses.length ?
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
    award: PropTypes.object.isRequired, // Award being displayed
    statuses: PropTypes.array, // Array of status facet data
    linkUri: PropTypes.string.isRequired, // URI to use for matrix links
    ident: PropTypes.string.isRequired, // Unique identifier to `id` the charts
    experiments: PropTypes.object.isRequired,
    unreplicated: PropTypes.object,
    anisogenic: PropTypes.object,
    isogenic: PropTypes.object,
};

StatusExperimentChart.defaultProps = {
    statuses: [],
    unreplicated: {},
    anisogenic: {},
    isogenic: {},
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
        if (this.props.statuses.length) {
            this.createChart(`${statusChartId}-${this.props.ident}`, this.props.statuses);
        }
    }

    componentDidUpdate() {
        if (this.props.statuses.length) {
            if (this.chart) {
                this.updateChart(this.chart, this.props.statuses);
            } else {
                this.createChart(`${statusChartId}-${this.props.ident}`, this.props.statuses);
            }
        } else if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    updateChart(chart, facetData) {
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

        // Calculate a (hopefully) unique ID to put on the DOM elements.
        const id = `${statusChartId}-${ident}`;

        return (
            <div className="award-charts__chart">
                <div className="award-charts__title">
                    Status
                </div>
                {statuses.length ?
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
};

StatusChart.defaultProps = {
    statuses: [],
};

StatusChart.contextTypes = {
    // navigate: PropTypes.func,
};

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
            uriBase: '/search/?type=Experiment&award.name=',
            linkUri: '/matrix/?type=Experiment&award.name=',
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
        },
        controls: {
            ident: 'experiments',
            data: [],
            labs: [],
            categoryData: [],
            statuses: [],
            categoryFacet: 'assay_title',
            title: 'Assays',
            uriBase: '/search/?type=Experiment&award.name=',
            linkUri: '/matrix/?type=Experiment&award.name=',
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

    return (
        <div className="award-charts">
            <div> <GenusButtons handleClick={handleClick} selectedOrganisms={selectedOrganisms} updatedGenusArray={updatedGenusArray} /> </div>
            <PanelBody>
                <div className="award-chart__group-wrapper">
                    <h2>Assays {experimentsConfig.labs.length ?
                    <a className="btn btn-info btn-sm reporttitle" href={`/report/?type=Experiment&award.name=${award.name}`} title="View tabular report"><svg id="Table" data-name="Table" xmlns="http://www.w3.org/2000/svg" width="29" height="17" viewBox="0 0 29 17" className="svg-icon svg-icon-table"><title>table-tab-icon </title><path d="M22,0H0V17H29V0H22ZM21,4.33V8H15V4.33h6ZM15,9h6v3H15V9Zm-1,3H8V9h6v3Zm0-7.69V8H8V4.33h6Zm-13,0H7V8H1V4.33ZM1,9H7v3H1V9Zm0,7V13H7v3H1Zm7,0V13h6v3H8Zm7,0V13h6v3H15Zm13,0H22V13h6v3Zm0-4H22V9h6v3Zm0-4H22V4.33h6V8Z" /></svg></a>
                    : null}</h2>
                    {experimentsConfig.labs.length ?
                        <div>
                            <div className="award-chart__group">
                                <LabChart
                                    award={award}
                                    labs={experimentsConfig.labs}
                                    linkUri={experimentsConfig.linkUri}
                                    ident={experimentsConfig.ident}
                                />
                                <CategoryChart
                                    award={award}
                                    categoryData={experimentsConfig.categoryData || []}
                                    title={experimentsConfig.title}
                                    linkUri={experimentsConfig.linkUri}
                                    categoryFacet={experimentsConfig.categoryFacet}
                                    ident={experimentsConfig.ident}
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
                                />
                            </div>
                        </div>
                    :
                        <div className="browser-error">No assays were submitted under this award</div>
                    }
                </div>
                <div className="award-chart__group-wrapper">
                    <h2>Annotations {annotationsConfig.labs.length ?
                    <a className="btn btn-info btn-sm reporttitle" href={`/report/?type=Annotation&award.name=${award.name}`} title="View tabular report"><svg id="Table" data-name="Table" xmlns="http://www.w3.org/2000/svg" width="29" height="17" viewBox="0 0 29 17" className="svg-icon svg-icon-table"><title>table-tab-icon </title><path d="M22,0H0V17H29V0H22ZM21,4.33V8H15V4.33h6ZM15,9h6v3H15V9Zm-1,3H8V9h6v3Zm0-7.69V8H8V4.33h6Zm-13,0H7V8H1V4.33ZM1,9H7v3H1V9Zm0,7V13H7v3H1Zm7,0V13h6v3H8Zm7,0V13h6v3H15Zm13,0H22V13h6v3Zm0-4H22V9h6v3Zm0-4H22V4.33h6V8Z" /></svg></a>
                    : null}</h2>
                    {annotationsConfig.labs.length ?
                        <div>
                            <div className="award-chart__group">
                                <LabChart
                                    award={award}
                                    labs={annotationsConfig.labs}
                                    linkUri={annotationsConfig.linkUri}
                                    ident={annotationsConfig.ident}
                                />
                                <CategoryChart
                                    award={award}
                                    categoryData={annotationsConfig.categoryData || []}
                                    linkUri={annotationsConfig.linkUri}
                                    categoryFacet={annotationsConfig.categoryFacet}
                                    title={annotationsConfig.title}
                                    ident={annotationsConfig.ident}
                                />
                                <StatusChart
                                    award={award}
                                    statuses={annotationsConfig.statuses || []}
                                    linkUri={annotationsConfig.linkUri}
                                    ident={annotationsConfig.ident}
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
                                ident={antibodiesConfig.ident}
                            />
                            <BiosampleChart
                                award={award}
                                categoryData={biosamplesConfig.categoryData}
                                categoryFacet={biosamplesConfig.categoryFacet}
                                ident={biosamplesConfig.ident}
                            />
                            <ControlsChart
                                award={award}
                                experiments={experiments}
                                statuses={controlsConfig.statuses || []}
                                linkUri={controlsConfig.linkUri}
                                ident={controlsConfig.ident}
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

// Overall component to render the cumulative line chart
const ExperimentDate = (props) => {
    const { experiments, award } = props;
    let dateReleasedArray = [];
    let dateSubmittedArray = [];
    const deduplicatedreleased = {};
    const deduplicatedsubmitted = {};
    let label = [];
    let data = [];
    let cumulativedatasetReleased = [];
    let cumulativedatasetSubmitted = [];
    let accumulatorreleased = 0;
    let accumulatorsubmitted = 0;
    let monthreleaseddiff = 0;
    let monthsubmitteddiff = 0;
    const fillreleasedDates = [];
    const fillsubmittedDates = [];

    // Search experiments for month_released and date_submitted in facets
    if (experiments && experiments.facets && experiments.facets.length) {
        const monthReleasedFacet = experiments.facets.find(facet => facet.field === 'month_released');
        const dateSubmittedFacet = experiments.facets.find(facet => facet.field === 'date_submitted');
        dateReleasedArray = (monthReleasedFacet && monthReleasedFacet.terms && monthReleasedFacet.terms.length) ? monthReleasedFacet.terms : [];
        dateSubmittedArray = (dateSubmittedFacet && dateSubmittedFacet.terms && dateSubmittedFacet.terms.length) ? dateSubmittedFacet.terms : [];
    }

    // Use Moment to format arrays of submitted and released date
    const standardreleasedTerms = dateReleasedArray.map((term) => {
        const standardDate = moment(term.key, ['MMMM, YYYY', 'YYYY-MM']).format('YYYY-MM');
        return { key: standardDate, doc_count: term.doc_count };
    });

    const standardsubmittedTerms = dateSubmittedArray.map((term) => {
        const standardDate = moment(term.key, ['MMMM, YYYY', 'YYYY-MM']).format('YYYY-MM');
        return { key: standardDate, doc_count: term.doc_count };
    });

    // Sort arrays chronologically
    const sortedreleasedTerms = standardreleasedTerms.sort((termA, termB) => {
        if (termA.key < termB.key) {
            return -1;
        } else if (termB.key < termA.key) {
            return 1;
        }
        return 0;
    });
    const sortedsubmittedTerms = standardsubmittedTerms.sort((termA, termB) => {
        if (termA.key < termB.key) {
            return -1;
        } else if (termB.key < termA.key) {
            return 1;
        }
        return 0;
    });

    // Add an object with the most current date to one of the arrays
    if ((dateReleasedArray && dateReleasedArray.length) && (dateSubmittedArray && dateSubmittedArray.length)) {
        if (moment(sortedsubmittedTerms[sortedsubmittedTerms.length - 1].key).isAfter(sortedreleasedTerms[sortedreleasedTerms.length - 1].key, 'date')) {
            sortedreleasedTerms.push({ key: sortedsubmittedTerms[sortedsubmittedTerms.length - 1].key, doc_count: 0 });
        } else if (moment(sortedsubmittedTerms[sortedsubmittedTerms.length - 1].key).isBefore(sortedreleasedTerms[sortedreleasedTerms.length - 1].key, 'date')) {
            sortedsubmittedTerms.push({ key: sortedreleasedTerms[sortedreleasedTerms.length - 1].key, doc_count: 0 });
        }
    }

    // Add an object with the award start date to both arrays
    sortedsubmittedTerms.unshift({ key: award.start_date, doc_count: 0 });
    sortedreleasedTerms.unshift({ key: award.start_date, doc_count: 0 });

    // Add objects to the array with doc_count 0 for the missing months
    const sortedreleasedTermsLength = sortedreleasedTerms.length;
    for (let j = 0; j < sortedreleasedTermsLength - 1; j += 1) {
        fillreleasedDates.push(sortedreleasedTerms[j]);
        const startDate = moment(sortedreleasedTerms[j].key);
        const endDate = moment(sortedreleasedTerms[j + 1].key);
        monthreleaseddiff = endDate.diff(startDate, 'months', false);
        if (monthreleaseddiff > 1) {
            for (let i = 0; i < monthreleaseddiff; i += 1) {
                fillreleasedDates.push({ key: startDate.add(1, 'months').format('YYYY-MM'), doc_count: 0 });
            }
        }
    }
    fillreleasedDates.push(sortedreleasedTerms[sortedreleasedTerms - 1]);

    const sortedsubmittedTermsLength = sortedsubmittedTerms.length;
    for (let j = 0; j < sortedsubmittedTermsLength - 1; j += 1) {
        fillsubmittedDates.push(sortedsubmittedTerms[j]);
        const startDate = moment(sortedsubmittedTerms[j].key);
        const endDate = moment(sortedsubmittedTerms[j + 1].key);
        monthsubmitteddiff = endDate.diff(startDate, 'months', false);
        if (monthsubmitteddiff > 1) {
            for (let i = 0; i < monthsubmitteddiff; i += 1) {
                fillsubmittedDates.push({ key: startDate.add(1, 'months').format('YYYY-MM'), doc_count: 0 });
            }
        }
    }
    fillsubmittedDates.push(sortedsubmittedTerms[sortedsubmittedTermsLength - 1]);

    // Remove any objects with keys before the start date of the award
    const arrayreleasedLength = fillreleasedDates.length;
    const arraysubmittedLength = fillsubmittedDates.length;
    const assayreleasedStart = award.start_date;
    const shortenedreleasedArray = [];
    const shortenedsubmittedArray = [];
    for (let j = 0; j < arrayreleasedLength - 2; j += 1) {
        if (moment(fillreleasedDates[j].key).isSameOrAfter(assayreleasedStart, 'date')) {
            shortenedreleasedArray.push(fillreleasedDates[j]);
        }
    }
    for (let j = 0; j < arraysubmittedLength - 2; j += 1) {
        if (moment(fillsubmittedDates[j].key).isSameOrAfter(assayreleasedStart, 'date')) {
            shortenedsubmittedArray.push(fillsubmittedDates[j]);
        }
    }

    const formatreleasedTerms = shortenedreleasedArray.map((term) => {
        const formattedDate = moment(term.key, ['YYYY-MM']).format('MMM YY');
        return { key: formattedDate, doc_count: term.doc_count };
    });

    const formatsubmittedTerms = shortenedsubmittedArray.map((term) => {
        const formattedDate = moment(term.key, ['YYYY-MM']).format('MMM YY');
        return { key: formattedDate, doc_count: term.doc_count };
    });

    // Deduplicate dates
    formatreleasedTerms.forEach((elem) => {
        if (deduplicatedreleased[elem.key]) {
            deduplicatedreleased[elem.key] += elem.doc_count;
        } else {
            deduplicatedreleased[elem.key] = elem.doc_count;
        }
    });

    formatsubmittedTerms.forEach((elem) => {
        if (deduplicatedsubmitted[elem.key]) {
            deduplicatedsubmitted[elem.key] += elem.doc_count;
        } else {
            deduplicatedsubmitted[elem.key] = elem.doc_count;
        }
    });


    // Create an array of dates
    const date = Object.keys(deduplicatedreleased).map((term) => {
        label = term;
        return label;
    });

    // Create an array of data from objects' doc_counts
    const datasetreleased = Object.keys(deduplicatedreleased).map((item) => {
        label = item;
        data = deduplicatedreleased[label];
        return data;
    });
    const datasetsubmitted = Object.keys(deduplicatedsubmitted).map((item) => {
        label = item;
        data = deduplicatedsubmitted[label];
        return data;
    });

    // Make the data cumulative
    const accumulatedDataReleased = datasetreleased.map((term) => {
        accumulatorreleased += term;
        cumulativedatasetReleased = accumulatorreleased;
        return cumulativedatasetReleased;
    });
    const accumulatedDataSubmitted = datasetsubmitted.map((term) => {
        accumulatorsubmitted += term;
        cumulativedatasetSubmitted = accumulatorsubmitted;
        return cumulativedatasetSubmitted;
    });

    return (
        <div>
            {experiments && experiments.facets && experiments.facets.length ?
                <Panel>
                <PanelHeading>
                    <h4>Cumulative Number of Experiments</h4>
                </PanelHeading>
                <PanelBody>
                    <CumulativeGraph releaseddatavalue={accumulatedDataReleased} submitteddatavalue={accumulatedDataSubmitted} monthReleased={date} />
                </PanelBody>
                </Panel>
            :
                null
            }
        </div>
    );
};

ExperimentDate.propTypes = {
    experiments: PropTypes.object,
    award: PropTypes.object.isRequired,
};

ExperimentDate.defaultProps = {
    experiments: {},
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
                        <Param name="experiments" url={`/search/?type=Experiment&award.name=${award.name}${ExperimentQuery}`} />
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

class FetchGraphData extends React.Component {
    render() {
        const { award } = this.props;
        return (
            <div>
                <FetchedData ignoreErrors>
                    <Param name="experiments" url={`/search/?type=Experiment&award.name=${award.name}`} />
                    <ExperimentDate award={award} />
                </FetchedData>
            </div>
        );
    }
}

FetchGraphData.propTypes = {
    award: PropTypes.object.isRequired, // Award represented by this chart
};


// Create a cumulative line chart in the div.
class CumulativeGraph extends React.Component {
    componentDidMount() {
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
                        },
                        ],
                    },
                },
                data: {
                    labels: monthReleased,
                    datasets: [{
                        label: 'Date Submitted',
                        data: submitteddatavalue,
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    },
                    {
                        label: 'Date Released',
                        data: releaseddatavalue,
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    }],
                },
            });
        });
    }

    render() {
        return (
            <canvas id="myGraph" style={{ height: 300 }} /> // responsive and maintainAspectRatio allow for height to be set here
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
    const { labs } = props;
    const sortedArray = labs['@graph'].map(term => term.title);
    return (
        <div>
            {sortedArray.map((item, index) => <div key={index}>{item}</div>)}
        </div>
    );
};

AffiliatedLabsArray.propTypes = {
    labs: PropTypes.object,
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
        return (
            <div className={globals.itemClass(context, 'view-item')}>
                <header className="row">
                    <div className="col-sm-12">
                        <h2>AWARD SUMMARY for {context.pi.lab.title} ({context.name})</h2>
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
                                        <dt>NHGRI project information</dt>
                                        <dd><a href={context.url} title={`${context.name} project page at NHGRI`}>{context.name}</a></dd>
                                    </div>
                                </dl>
                                <dl className="key-value">
                                    <div data-test="pi">
                                        <dt>Primary Investigator</dt>
                                        <dd>{context.pi.lab.title}</dd>
                                    </div>
                                </dl>
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
                                <dl className="key-value">
                                    <div data-test="milestone">
                                        <dt>Milestones</dt>
                                    </div>
                                </dl>
                            </div>
                        </div>
                    </PanelBody>
                </Panel>
                <FetchGraphData award={context} />
            </div>
        );
    }
}

Award.propTypes = {
    context: PropTypes.object.isRequired, // Award object being rendered
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
