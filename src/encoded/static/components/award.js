import React from 'react';
import PropTypes from 'prop-types';
import { Panel, PanelHeading, PanelBody } from '../libs/bootstrap/panel';
import DataColors from './datacolors';
import { FetchedData, Param } from './fetched';
import globals from './globals';
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


// Draw the total chart count in the middle of the donut.
function drawDonutCenter(chart) {
    const width = chart.chart.width;
    const height = chart.chart.height;
    const ctx = chart.chart.ctx;

    ctx.fillStyle = '#000000';
    ctx.restore();
    const fontSize = (height / 114).toFixed(2);
    ctx.font = `${fontSize}em sans-serif`;
    ctx.textBaseline = 'middle';

    const data = chart.data.datasets[0].data;
    const total = data.reduce((prev, curr) => prev + curr);
    const textX = Math.round((width - ctx.measureText(total).width) / 2);
    const textY = height / 2;

    ctx.clearRect(0, 0, width, height);
    ctx.fillText(total, textX, textY);
    ctx.save();
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
                    labels: labels,
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
                                text.push(`<span class="chart-legend-chip" style="background-color:${chartColors[i]}"></span>`);
                                text.push(`<span class="chart-legend-label">${chartLabels[i]}</span>`);
                                text.push('</a></li>');
                            }
                        }
                        text.push('</ul>');
                        return text.join('');
                    },
                    onClick: function (e) {
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


// Display and handle clicks in the chart of labs.
class LabChart extends React.Component {
    // Update existing chart with new data.
    static updateChart(chart, facetData) {
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
    }

    constructor() {
        super();
        this.createChart = this.createChart.bind(this);
    }

    componentDidMount() {
        this.createChart(`${labChartId}-${this.props.ident}`, this.props.labs);
    }

    componentDidUpdate() {
        if (this.chart) {
            this.constructor.updateChart(this.chart, this.props.labs);
        }
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
    // Update existing chart with new data.
    static updateChart(chart, facetData) {
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
    }

    constructor() {
        super();

        this.createChart = this.createChart.bind(this);
    }

    componentDidMount() {
        if (this.props.categoryData.length) {
            this.createChart(`${categoryChartId}-${this.props.ident}`, this.props.categoryData);
        }
    }

    componentDidUpdate() {
        if (this.chart) {
            this.constructor.updateChart(this.chart, this.props.categoryData);
        }
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


// Display and handle clicks in the chart of labs.
class StatusChart extends React.Component {
    // Update existing chart with new data.
    static updateChart(chart, facetData) {
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
    }

    constructor() {
        super();
        this.createChart = this.createChart.bind(this);
    }

    componentDidMount() {
        if (this.props.statuses.length) {
            this.createChart(`${statusChartId}-${this.props.ident}`, this.props.statuses);
        }
    }

    componentDidUpdate() {
        if (this.chart) {
            this.constructor.updateChart(this.chart, this.props.statuses);
        }
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
    navigate: PropTypes.func,
};


const ChartRenderer = (props) => {
    const { award, experiments, annotations } = props;

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
    };

    // Find the chart data in the returned facets.
    const experimentsConfig = searchData.experiments;
    const annotationsConfig = searchData.annotations;
    searchData.experiments.data = (experiments && experiments.facets) || [];
    searchData.annotations.data = (annotations && annotations.facets) || [];
    ['experiments', 'annotations'].forEach((chartCategory) => {
        if (searchData[chartCategory].data.length) {
            // Get the array of lab data.
            const labFacet = searchData[chartCategory].data.find(facet => facet.field === 'lab.title');
            searchData[chartCategory].labs = (labFacet && labFacet.terms && labFacet.terms.length) ? labFacet.terms.sort((a, b) => (a.key < b.key ? -1 : (a.key > b.key ? 1 : 0))) : [];

            // Get the array of data specific to experiments or annotations.
            const categoryFacet = searchData[chartCategory].data.find(facet => facet.field === searchData[chartCategory].categoryFacet);
            searchData[chartCategory].categoryData = (categoryFacet && categoryFacet.terms && categoryFacet.terms.length) ? categoryFacet.terms : [];

            // Get the array of status data.
            const statusFacet = searchData[chartCategory].data.find(facet => facet.field === 'status');
            searchData[chartCategory].statuses = (statusFacet && statusFacet.terms && statusFacet.terms.length) ? statusFacet.terms : [];
        }
    });

    return (
        <div className="award-charts">
            <div className="award-chart__group-wrapper">
                <h2>Assays</h2>
                {experimentsConfig.labs.length ?
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
                        <StatusChart
                            award={award}
                            statuses={experimentsConfig.statuses || []}
                            linkUri={experimentsConfig.linkUri}
                            ident={experimentsConfig.ident}
                        />
                    </div>
                :
                    <div className="browser-error">No assays were submitted under this award</div>
                }
            </div>
            <div className="award-chart__group-wrapper">
                <h2>Annotations</h2>
                {annotationsConfig.labs.length ?
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
                :
                    <div className="browser-error">No annotations were submitted under this award</div>
                }
            </div>
        </div>
    );
};

ChartRenderer.propTypes = {
    award: PropTypes.object.isRequired, // Award being displayed
    experiments: PropTypes.object, // Search result of matching experiments
    annotations: PropTypes.object, // Search result of matching annotations
};

ChartRenderer.defaultProps = {
    experiments: {},
    annotations: {},
};


// Overall component to render the award charts
const AwardCharts = (props) => {
    const { award } = props;

    return (
        <Panel>
            <PanelHeading>
                <h4>{award.pi && award.pi.lab ? <span>{award.pi.lab.title}</span> : <span>No PI indicated</span>}</h4>
                <ProjectBadge award={award} addClasses="badge-heading" />
            </PanelHeading>
            <PanelBody>
                <FetchedData>
                    <Param name="experiments" url={`/search/?type=Experiment&award.name=${award.name}`} />
                    <Param name="annotations" url={`/search/?type=Annotation&award.name=${award.name}`} />
                    <ChartRenderer award={award} />
                </FetchedData>
            </PanelBody>
        </Panel>
    );
};

AwardCharts.propTypes = {
    award: PropTypes.object.isRequired, // Award represented by this chart
};


const Award = (props) => {
    const { context } = props;
    const statuses = [{ status: context.status, title: 'Status' }];

    return (
        <div className={globals.itemClass(context, 'view-item')}>
            <header className="row">
                <div className="col-sm-12">
                    <h2>{context.title || context.name}</h2>
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
                    <h4>Description</h4>
                </PanelHeading>
                <PanelBody>
                    {context.url ?
                        <div>
                            <strong>NHGRI project information: </strong><a href={context.url} title={`${context.name} project page at NHGRI`}>{context.name}</a>
                            <hr />
                        </div>
                    : null}
                    {context.description ?
                        <div className="two-column-long-text two-column-long-text--gap">
                            <p>{context.description}</p>
                        </div>
                    :
                        <p className="browser-error">Award has no description</p>
                    }
                </PanelBody>
            </Panel>
        </div>
    );
};

Award.propTypes = {
    context: PropTypes.object.isRequired, // Award object being rendered
};

globals.content_views.register(Award, 'Award');


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

globals.listing_views.register(Listing, 'Award');
