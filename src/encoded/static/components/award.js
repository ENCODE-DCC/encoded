import React from 'react';
import { Panel, PanelHeading, PanelBody } from '../libs/bootstrap/panel';
import { AuditIndicators, AuditDetail, AuditMixin } from './audit';
import DataColors from './datacolors';
import { FetchedData, Param } from './fetched';
import globals from './globals';
import { ProjectBadge } from './image';
import { PickerActionsMixin } from './search';
import { StatusLabel } from './statuslabel';


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
                    maintainAspectRatio: true,
                    legend: {
                        display: false,
                    },
                    animation: {
                        duration: 200,
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

            // Resolve the webpack loader promise with the chart instance.
            resolve(chart);
        });
    });
}


// Display and handle clicks in the chart of labs.
const LabChart = React.createClass({
    propTypes: {
        award: React.PropTypes.object.isRequired, // Award being displayed
        labs: React.PropTypes.array.isRequired, // Array of labs facet data
        linkUri: React.PropTypes.string.isRequired, // Base URI for matrix links
        ident: React.PropTypes.string.isRequired, // Unique identifier to `id` the charts
    },

    contextTypes: {
        navigate: React.PropTypes.func,
    },

    componentDidMount: function () {
        this.createChart(`${labChartId}-${this.props.ident}`, this.props.labs);
    },

    componentDidUpdate: function () {
        if (this.chart) {
            this.updateChart(this.chart, this.props.labs);
        }
    },

    createChart: function (chartId, facetData) {
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
    },

    // Update existing chart with new data.
    updateChart: function (chart, facetData) {
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
    },

    render: function () {
        const { labs, ident } = this.props;

        // Calculate a (hopefully) unique ID to put on the DOM elements.
        const id = `${labChartId}-${ident}`;

        return (
            <div className="award-charts__chart">
                <div className="title">
                    Lab
                </div>
                {labs.length ?
                    <div>
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
    },
});


// Display and handle clicks in the chart of assays.
const CategoryChart = React.createClass({
    propTypes: {
        award: React.PropTypes.object.isRequired, // Award being displayed
        categoryData: React.PropTypes.array.isRequired, // Type-specific data to display in a chart
        title: React.PropTypes.string.isRequired, // Title to display above the chart
        linkUri: React.PropTypes.string.isRequired, // Element of matrix URI to select
        categoryFacet: React.PropTypes.string.isRequired, // Add to linkUri to link to matrix facet item
        ident: React.PropTypes.string.isRequired, // Unique identifier to `id` the charts
    },

    contextTypes: {
        navigate: React.PropTypes.func,
    },

    componentDidMount: function () {
        if (this.props.categoryData.length) {
            this.createChart(`${categoryChartId}-${this.props.ident}`, this.props.categoryData);
        }
    },

    componentDidUpdate: function () {
        if (this.chart) {
            this.updateChart(this.chart, this.props.categoryData);
        }
    },

    createChart: function (chartId, facetData) {
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
    },

    // Update existing chart with new data.
    updateChart: function (chart, facetData) {
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

        // Update chart data and redraw with the new data
        chart.data.datasets[0].data = values;
        chart.data.datasets[0].backgroundColor = colors;
        chart.data.labels = labels;
        chart.update();
    },

    render: function () {
        const { categoryData, title, ident } = this.props;

        // Calculate a (hopefully) unique ID to put on the DOM elements.
        const id = `${categoryChartId}-${ident}`;

        return (
            <div className="award-charts__chart">
                <div className="title">
                    {title}
                    <center><hr width="80%" position="static" color="blue" /></center>
                </div>
                {categoryData.length ?
                    <div>
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
    },
});


// Display and handle clicks in the chart of labs.
const StatusChart = React.createClass({
    propTypes: {
        award: React.PropTypes.object.isRequired, // Award being displayed
        statuses: React.PropTypes.array.isRequired, // Array of status facet data
        linkUri: React.PropTypes.string.isRequired, // URI to use for matrix links
        ident: React.PropTypes.string.isRequired, // Unique identifier to `id` the charts
    },

    contextTypes: {
        navigate: React.PropTypes.func,
    },

    componentDidMount: function () {
        if (this.props.statuses.length) {
            this.createChart(`${statusChartId}-${this.props.ident}`, this.props.statuses);
        }
    },

    componentDidUpdate: function () {
        if (this.chart) {
            this.updateChart(this.chart, this.props.statuses);
        }
    },

    createChart: function (chartId, facetData) {
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
    },

    // Update existing chart with new data.
    updateChart: function (chart, facetData) {
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
    },

    render: function () {
        const { statuses, ident } = this.props;

        // Calculate a (hopefully) unique ID to put on the DOM elements.
        const id = `${statusChartId}-${ident}`;

        return (
            <div className="award-charts__chart">
                <div className="title">
                    Status
                    <center><hr width="80%" position="static" color="blue" /></center>
                </div>
                {statuses.length ?
                    <div>
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
    },
});


// Once we get chart data to display, render the charts. We render three charts:
//   1. Lab - The labs the award applies to.
//   2. TypeSpecificData - A chart of data specific for an object type this award represents. We
//                         can have more than one data type associated with an award, but we only
//                         draw the data for one type for this chart. Whatever's the first type to
//                         return data is what we use.
//   3. Status - The release statuses of the objects associated with this award.
const ChartRenderer = React.createClass({
    propTypes: {
        award: React.PropTypes.object.isRequired, // Award being displayed
        experiments: React.PropTypes.object, // Search result of matching experiments
        annotations: React.PropTypes.object, // Search result of matching annotations
    },

    // "Array" of ways to extract from returned search results. It's actually an object keyed by
    //   chart category. The properties of each are:
    //   data: Receives array of data from search result facets for each category of search.
    //   labs: Receives array of lab.title data from search results.
    //   categoryData: Receives array of data specific to each category from search results.
    //   statuses: Receives array of statuses from search results.
    //   categoryFacet: Specifies the facet to look for data to put into categoryData.
    //   title: Title of the category-specific chart
    //   uriBase: URI to search for data for the charts
    //   linkUri: URI base to link to matrix
    searchData: {
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
    },

    render: function () {
        const { award, experiments, annotations } = this.props;
        const experimentsConfig = this.searchData.experiments;
        const annotationsConfig = this.searchData.annotations;

        // Find the chart data in the returned facets.
        this.searchData.experiments.data = (experiments && experiments.facets) || [];
        this.searchData.annotations.data = (annotations && annotations.facets) || [];
        ['experiments', 'annotations'].forEach((chartCategory) => {
            if (this.searchData[chartCategory].data.length) {
                // Get the array of lab data.
                const labFacet = this.searchData[chartCategory].data.find(facet => facet.field === 'lab.title');
                if (labFacet) {
                    this.searchData[chartCategory].labs = labFacet.terms && labFacet.terms.length ? labFacet.terms.sort((a, b) => (a.key < b.key ? -1 : (a.key > b.key ? 1 : 0))) : null;
                }

                // Get the array of data specific to experiments or annotations.
                const categoryFacet = this.searchData[chartCategory].data.find(facet => facet.field === this.searchData[chartCategory].categoryFacet);
                if (categoryFacet) {
                    this.searchData[chartCategory].categoryData = categoryFacet.terms && categoryFacet.terms.length ? categoryFacet.terms : null;
                }

                // Get the array of status data.
                const statusFacet = this.searchData[chartCategory].data.find(facet => facet.field === 'status');
                if (statusFacet) {
                    this.searchData[chartCategory].statuses = statusFacet.terms && statusFacet.terms.length ? statusFacet.terms : null;
                }
            }
        });

        return (
            <div className="award-charts">
                <div className="award-chart--experiments">
                    {experimentsConfig.labs.length ?
                        <div>
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
                        <div className="browser-error">No labs reference this award for assays</div>
                    }
                </div>
                <div className="award-chart--annotations">
                    {this.searchData.annotations.labs.length ?
                        <div>
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
                        <div className="browser-error">No labs reference this award for annotations</div>
                    }
                </div>
            </div>
        );
    },
});


// Overall component to render the award charts
const AwardCharts = React.createClass({
    propTypes: {
        award: React.PropTypes.object, // Award represented by this chart
    },

    getInitialState: function () {
        return {
            searchData: {}, // Search data from search of objects using this award.
            chartSource: {}, // Element of `this.chartSource` that generated the data in `awardData`.
        };
    },

    render: function () {
        const { award } = this.props;

        return (
            <Panel>
                <PanelHeading>
                    <h4>{award.pi && award.pi.lab ? <span>{award.pi.lab.title}</span> : <span>No PI indicated</span>}</h4>
                    <ProjectBadge award={award} addClasses="badge-heading" />
                </PanelHeading>
                <PanelBody>
                    <FetchedData ignoreErrors>
                        <Param name="experiments" url={`/search/?type=Experiment&award.name=${award.name}`} />
                        <Param name="annotations" url={`/search/?type=Annotation&award.name=${award.name}`} />
                        <ChartRenderer award={award} />
                    </FetchedData>
                </PanelBody>
            </Panel>
        );
    },
});


const Award = React.createClass({
    propTypes: {
        context: React.PropTypes.object, // Award object being rendered
    },

    render: function () {
        const { context } = this.props;
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
    },
});

globals.content_views.register(Award, 'Award');


const Listing = React.createClass({
    propTypes: {
        context: React.PropTypes.object, // Object whose search result we're displaying
    },

    mixins: [PickerActionsMixin, AuditMixin],

    render: function () {
        const result = this.props.context;
        return (
            <li>
                <div className="clearfix">
                    {this.renderActions()}
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Award</p>
                        <p className="type">{` ${result.name}`}</p>
                        <p className="type meta-status">{` ${result.status}`}</p>
                        <AuditIndicators audits={result.audit} id={result['@id']} search />
                    </div>
                    <div className="accession">
                        <a href={result['@id']}>{result.title}</a>
                    </div>
                    <div className="data-row">
                        <div><strong>Project / RFA: </strong>{result.project} / {result.rfa}</div>
                    </div>
                </div>
                <AuditDetail audits={result.audit} except={result['@id']} id={this.props.context['@id']} forcedEditLink />
            </li>
        );
    },
});
globals.listing_views.register(Listing, 'Award');
