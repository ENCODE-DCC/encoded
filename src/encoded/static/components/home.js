import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import moment from 'moment';
import { FetchedData, FetchedItems, Param } from './fetched';
import * as globals from './globals';
import { Panel, PanelBody } from '../libs/bootstrap/panel';


const newsUri = '/search/?type=Page&news=true&status=released';


// Convert the selected organisms and assays into an encoded query.
function generateQuery(selectedOrganisms, selectedAssayCategory) {
    // Make the base query.
    let query = selectedAssayCategory === 'COMPPRED' ? '?type=Annotation&encyclopedia_version=4' : '?type=Experiment&status=released';

    // Add the selected assay category, if any (doesn't apply to Computational Predictions).
    if (selectedAssayCategory && selectedAssayCategory !== 'COMPPRED') {
        query += `&assay_slims=${selectedAssayCategory}`;
    }

    // Add all the selected organisms, if any
    if (selectedOrganisms.length) {
        const organismSpec = selectedAssayCategory === 'COMPPRED' ? 'organism.scientific_name=' : 'replicates.library.biosample.donor.organism.scientific_name=';
        const queryStrings = {
            HUMAN: `${organismSpec}Homo+sapiens`, // human
            MOUSE: `${organismSpec}Mus+musculus`, // mouse
            WORM: `${organismSpec}Caenorhabditis+elegans`, // worm
            FLY: `${organismSpec}Drosophila+melanogaster&${organismSpec}Drosophila+pseudoobscura&${organismSpec}Drosophila+simulans&${organismSpec}Drosophila+mojavensis&${organismSpec}Drosophila+ananassae&${organismSpec}Drosophila+virilis&${organismSpec}Drosophila+yakuba`,
        };
        const organismQueries = selectedOrganisms.map(organism => queryStrings[organism]);
        query += `&${organismQueries.join('&')}`;
    }

    return query;
}


// Main page component to render the home page
export default class Home extends React.Component {
    constructor(props) {
        super(props);

        // Set initial React state.
        this.state = {
            organisms: [], // create empty array of selected tabs
            assayCategory: '',
            socialHeight: 0,
        };

        // Required binding of `this` to component methods or else they can't see `this`.
        this.handleAssayCategoryClick = this.handleAssayCategoryClick.bind(this);
        this.handleTabClick = this.handleTabClick.bind(this);
        this.newsLoaded = this.newsLoaded.bind(this);
    }

    handleAssayCategoryClick(assayCategory) {
        if (this.state.assayCategory === assayCategory) {
            this.setState({ assayCategory: '' });
        } else {
            this.setState({ assayCategory });
        }
    }

    handleTabClick(selectedTab) {
        // Create a copy of this.state.newtabs so we can manipulate it in peace.
        const tempArray = _.clone(this.state.organisms);
        if (tempArray.indexOf(selectedTab) === -1) {
            // if tab isn't already in array, then add it
            tempArray.push(selectedTab);
        } else {
            // otherwise if it is in array, remove it from array and from link
            const indexToRemoveArray = tempArray.indexOf(selectedTab);
            tempArray.splice(indexToRemoveArray, 1);
        }

        // Update the list of user-selected organisms.
        this.setState({ organisms: tempArray });
    }

    // Called when the news content loads so that we can get its height. That lets us match up the
    // height of <TwitterWidget>. If we don't have any news items, nodeRef has `undefined` and we
    // just hard-code the height at 600 so that the Twitter widget has some space.
    newsLoaded(nodeRef) {
        this.setState({ socialHeight: nodeRef ? nodeRef.clientHeight : 600 });
    }

    render() {
        // Based on the currently selected organisms and assay category, generate a query string
        // for the GET request to retrieve chart data.
        const currentQuery = generateQuery(this.state.organisms, this.state.assayCategory);

        return (
            <div className="whole-page">
                <div className="row">
                    <div className="col-xs-12">
                        <Panel>
                            <AssayClicking assayCategory={this.state.assayCategory} handleAssayCategoryClick={this.handleAssayCategoryClick} />
                            <div className="organism-tabs">
                                <TabClicking organisms={this.state.organisms} handleTabClick={this.handleTabClick} />
                            </div>
                            <div className="graphs">
                                <div className="row">
                                    <HomepageChartLoader organisms={this.state.organisms} assayCategory={this.state.assayCategory} query={currentQuery} />
                                </div>
                            </div>
                            <div className="social">
                                <div className="social-news">
                                    <div className="news-header">
                                        <h2>News <a href="/news/" title="More ENCODE news" className="twitter-ref">More ENCODE news</a></h2>
                                    </div>
                                    <NewsLoader newsLoaded={this.newsLoaded} />
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
}


// Given retrieved data, draw all home-page charts.
const ChartGallery = props => (
    <PanelBody>
        <div className="view-all">
            <a href={`/matrix/${props.query}`} className="view-all-button btn btn-info btn-sm" role="button">View Assay Matrix</a>
        </div>
        <div className="chart-gallery">
            <div className="chart-single">
                <HomepageChart {...props} />
            </div>
            <div className="chart-single">
                <HomepageChart2 {...props} />
            </div>
            <div className="chart-single">
                <HomepageChart3 {...props} />
            </div>
        </div>
    </PanelBody>
);

ChartGallery.propTypes = {
    query: PropTypes.string, // Query string to add to /matrix/ URI
};

ChartGallery.defaultProps = {
    query: null,
};


// Component to allow clicking boxes on classic image
class AssayClicking extends React.Component {
    constructor(props) {
        super(props);

        // Required binding of `this` to component methods or else they can't see `this`.
        this.sortByAssay = this.sortByAssay.bind(this);
    }

    // Properly adds or removes assay category from link
    sortByAssay(category, e) {
        function handleClick(cat, ctx) {
            // Call the Home component's function to record the new assay cateogry
            ctx.props.handleAssayCategoryClick(cat); // handles assay category click
        }

        if (e.type === 'touchend') {
            handleClick(category, this);
            this.assayClickHandled = true;
        } else if (e.type === 'click' && !this.assayClickHandled) {
            handleClick(category, this);
        } else {
            this.assayClickHandled = false;
        }
    }

    // Renders classic image and svg rectangles
    render() {
        const assayList = [
            '3D+chromatin+structure',
            'DNA+accessibility',
            'DNA+binding',
            'DNA+methylation',
            'COMPPRED',
            'Transcription',
            'RNA+binding',
        ];
        const assayCategory = this.props.assayCategory;

        return (
            <div>
                <div className="overall-classic">

                    <h1>ENCODE: Encyclopedia of DNA Elements</h1>

                    <div className="site-banner">
                        <div className="site-banner-img">
                            <img src="static/img/classic-image.jpg" alt="ENCODE representational diagram with embedded assay selection buttons" />

                            <svg id="site-banner-overlay" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2260 1450" className="classic-svg">
                                <BannerOverlayButton item={assayList[0]} x="101.03" y="645.8" width="257.47" height="230.95" selected={assayCategory === assayList[0]} clickHandler={this.sortByAssay} />
                                <BannerOverlayButton item={assayList[1]} x="386.6" y="645.8" width="276.06" height="230.95" selected={assayCategory === assayList[1]} clickHandler={this.sortByAssay} />
                                <BannerOverlayButton item={assayList[2]} x="688.7" y="645.8" width="237.33" height="230.95" selected={assayCategory === assayList[2]} clickHandler={this.sortByAssay} />
                                <BannerOverlayButton item={assayList[3]} x="950.83" y="645.8" width="294.65" height="230.95" selected={assayCategory === assayList[3]} clickHandler={this.sortByAssay} />
                                <BannerOverlayButton item={assayList[4]} x="1273.07" y="645.8" width="373.37" height="230.95" selected={assayCategory === assayList[4]} clickHandler={this.sortByAssay} />
                                <BannerOverlayButton item={assayList[5]} x="1674.06" y="645.8" width="236.05" height="230.95" selected={assayCategory === assayList[5]} clickHandler={this.sortByAssay} />
                                <BannerOverlayButton item={assayList[6]} x="1937.74" y="645.8" width="227.38" height="230.95" selected={assayCategory === assayList[6]} clickHandler={this.sortByAssay} />
                            </svg>
                        </div>

                        <div className="site-banner-intro">
                            <div className="site-banner-intro-content">
                                <p>The ENCODE (Encyclopedia of DNA Elements) Consortium is an international collaboration of research groups funded by the National Human Genome Research Institute (NHGRI). The goal of ENCODE is to build a comprehensive parts list of functional elements in the human genome, including elements that act at the protein and RNA levels, and regulatory elements that control cells and circumstances in which a gene is active.</p>
                                <div className="getting-started-button">
                                    <a href="/matrix/?type=Experiment&status=released" className="btn btn-info" role="button">Get Started</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

AssayClicking.propTypes = {
    assayCategory: PropTypes.string.isRequired, // Test to display in each audit's detail, possibly containing @ids that this component turns into links automatically
};


// Draw an overlay button on the ENCODE banner.
const BannerOverlayButton = (props) => {
    const { item, x, y, width, height, selected, clickHandler } = props;

    return (
        <rect
            id={item}
            x={x}
            y={y}
            width={width}
            height={height}
            className={`rectangle-box${selected ? ' selected' : ''}`}
            onClick={(e) => { clickHandler(item, e); }}
        />
    );
};

BannerOverlayButton.propTypes = {
    item: PropTypes.string, // ID of button being clicked
    x: PropTypes.string, // X coordinate of button
    y: PropTypes.string, // Y coordinate of button
    width: PropTypes.string, // Width of button in pixels
    height: PropTypes.string, // Height of button in pixels
    selected: PropTypes.bool, // `true` if button is selected
    clickHandler: PropTypes.func.isRequired, // Function to call when the button is clicked
};

BannerOverlayButton.defaultProps = {
    item: '',
    x: '0',
    y: '0',
    width: '0',
    height: '0',
    selected: false,
};


// Passes in tab to handleTabClick
/* eslint-disable react/prefer-stateless-function */
class TabClicking extends React.Component {
    render() {
        const { organisms, handleTabClick } = this.props;
        return (
            <div>
                <div className="organism-selector">
                    <OrganismSelector organism="Human" selected={organisms.indexOf('HUMAN') !== -1} clickHandler={handleTabClick} />
                    <OrganismSelector organism="Mouse" selected={organisms.indexOf('MOUSE') !== -1} clickHandler={handleTabClick} />
                    <OrganismSelector organism="Worm" selected={organisms.indexOf('WORM') !== -1} clickHandler={handleTabClick} />
                    <OrganismSelector organism="Fly" selected={organisms.indexOf('FLY') !== -1} clickHandler={handleTabClick} />
                </div>
            </div>
        );
    }
}
/* eslint-enable react/prefer-stateless-function */

TabClicking.propTypes = {
    organisms: PropTypes.array, // Array of currently selected tabs
    handleTabClick: PropTypes.func.isRequired, // Function to call when a tab is clicked
};

TabClicking.defaultProps = {
    organisms: [],
};


const OrganismSelector = (props) => {
    const { organism, selected, clickHandler } = props;

    return (
        <button className={`organism-selector__tab${selected ? ' organism-selector--selected' : ''}`} onClick={() => { clickHandler(organism.toUpperCase(organism)); }}>
            {organism}
        </button>
    );
};

OrganismSelector.propTypes = {
    organism: PropTypes.string, // Organism this selector represents
    selected: PropTypes.bool, // `true` if selector is selected
    clickHandler: PropTypes.func.isRequired, // Function to call to handle a selector click
};

OrganismSelector.defaultProps = {
    organism: '',
    selected: false,
};


// Initiates the GET request to search for experiments, and then pass the data to the HomepageChart
// component to draw the resulting chart.
const HomepageChartLoader = (props) => {
    const { query, organisms, assayCategory } = props;

    return (
        <FetchedData>
            <Param name="data" url={`/search/${query}`} />
            <ChartGallery organisms={organisms} assayCategory={assayCategory} query={query} />
        </FetchedData>
    );
};

HomepageChartLoader.propTypes = {
    query: PropTypes.string, // Current search URI based on selected assayCategory
    organisms: PropTypes.array, // Array of selected organism strings
    assayCategory: PropTypes.string, // Selected assay category
};

HomepageChartLoader.defaultProps = {
    query: '',
    organisms: [],
    assayCategory: '',
};


// Draw the total chart count in the middle of the donut.
function drawDonutCenter(chart) {
    const canvasId = chart.chart.canvas.id;
    const width = chart.chart.width;
    const height = chart.chart.height;
    const ctx = chart.chart.ctx;

    ctx.fillStyle = '#000000';
    ctx.restore();
    const fontSize = (height / 114).toFixed(2);
    ctx.font = `${fontSize}em sans-serif`;
    ctx.textBaseline = 'middle';

    if (canvasId === 'myChart' || canvasId === 'myChart2') {
        const data = chart.data.datasets[0].data;
        const total = data.reduce((prev, curr) => prev + curr);
        const textX = Math.round((width - ctx.measureText(total).width) / 2);
        const textY = height / 2;

        ctx.clearRect(0, 0, width, height);
        ctx.fillText(total, textX, textY);
        ctx.save();
    } else {
        ctx.clearRect(0, 0, width, height);
    }
}


// Component to display the D3-based chart for Project
class HomepageChart extends React.Component {
    constructor(props) {
        super(props);
        this.wrapperHeight = 200;
        this.createChart = this.createChart.bind(this);
        this.updateChart = this.updateChart.bind(this);
    }

    componentDidMount() {
        // Create the chart, and assign the chart to this.myPieChart when the process finishes.
        if (document.getElementById('myChart')) {
            this.createChart(this.facetData);
        }
    }

    componentDidUpdate() {
        if (this.myPieChart) {
            // Existing data updated
            this.updateChart(this.myPieChart, this.facetData);
        } else if (this.facetData.length) {
            // Chart existed but was destroyed for lack of data. Rebuild the chart.
            this.createChart(this.facetData);
        }
    }

    // Draw the Project chart, for initial load, or when the previous load had no data for this
    // chart.
    createChart(facetData) {
        require.ensure(['chart.js'], (require) => {
            const Chart = require('chart.js');

            // for each item, set doc count, add to total doc count, add proper label, and assign color.
            const colors = globals.projectColors.colorList(facetData.map(term => term.key), { shade: 10 });
            const data = [];
            const labels = [];

            // Convert facet data to chart data.
            facetData.forEach((term, i) => {
                data[i] = term.doc_count;
                labels[i] = term.key;
            });

            // adding total doc count to middle of donut
            // http://stackoverflow.com/questions/20966817/how-to-add-text-inside-the-doughnut-chart-using-chart-js/24671908
            Chart.pluginService.register({
                beforeDraw: drawDonutCenter,
            });

            // Pass the assay_title counts to the charting library to render it.
            const canvas = document.getElementById('myChart');
            if (canvas) {
                const ctx = canvas.getContext('2d');
                this.myPieChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels,
                        datasets: [{
                            data,
                            backgroundColor: colors,
                        }],
                    },

                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        legend: {
                            display: false, // Hide automatically generated legend; we draw it ourselves
                        },
                        animation: {
                            duration: 200,
                        },
                        legendCallback: (chart) => { // allows for legend clicking
                            const chartData = chart.data.datasets[0].data;
                            const text = [];
                            text.push('<ul>');
                            for (let i = 0; i < chartData.length; i += 1) {
                                if (chartData[i]) {
                                    text.push('<li>');
                                    text.push(`<a href="/matrix/${this.props.query}&award.project=${chart.data.labels[i]}">`); // go to matrix view when clicked
                                    text.push(`<span class="chart-legend-chip" style="background-color:${chart.data.datasets[0].backgroundColor[i]}"></span>`);
                                    if (chart.data.labels[i]) {
                                        text.push(`<span class="chart-legend-label">${chart.data.labels[i]}</span>`);
                                    }
                                    text.push('</a></li>');
                                }
                            }
                            text.push('</ul>');
                            return text.join('');
                        },
                        onClick: (e) => {
                            // React to clicks on pie sections
                            const activePoints = this.myPieChart.getElementAtEvent(e);

                            if (activePoints[0]) { // if click on wrong area, do nothing
                                const clickedElementIndex = activePoints[0]._index;
                                const term = this.myPieChart.data.labels[clickedElementIndex];
                                this.context.navigate(`/matrix/${this.props.query}&award.project=${term}`);
                            }
                        },
                    },
                });

                // Have chartjs draw the legend into the DOM.
                document.getElementById('chart-legend').innerHTML = this.myPieChart.generateLegend();

                // Save the chart <div> height so we can set it to that value when no data's available.
                const chartWrapperDiv = document.getElementById('chart-wrapper-1');
                this.wrapperHeight = chartWrapperDiv.clientHeight;
            }
        });
    }

    // Update existing chart with new data.
    /* eslint-disable class-methods-use-this */
    updateChart(Chart, facetData) {
        // for each item, set doc count, add to total doc count, add proper label, and assign color.
        const colors = globals.projectColors.colorList(facetData.map(term => term.key), { shade: 10 });
        const data = [];
        const labels = [];

        // Convert facet data to chart data.
        facetData.forEach((term, i) => {
            data[i] = term.doc_count;
            labels[i] = term.key;
        });

        // Update chart data and redraw with the new data
        Chart.data.datasets[0].data = data;
        Chart.data.datasets[0].backgroundColor = colors;
        Chart.data.labels = labels;
        Chart.update();

        // Redraw the updated legend
        document.getElementById('chart-legend').innerHTML = Chart.generateLegend();
    }
    /* eslint-enable class-methods-use-this */

    render() {
        const facets = this.props.data && this.props.data.facets;
        let total;

        // Get all project facets, or an empty array if none.
        if (facets) {
            const projectFacet = facets.find(facet => facet.field === 'award.project');
            this.facetData = projectFacet ? projectFacet.terms : [];
            const docCounts = this.facetData.length ? this.facetData.map(data => data.doc_count) : [];
            total = docCounts.length ? docCounts.reduce((prev, curr) => prev + curr) : 0;

            // No data with the current selection, but we used to? Destroy the existing chart so we can
            // display a no-data message instead.
            if ((this.facetData.length === 0 || total === 0) && this.myPieChart) {
                this.myPieChart.destroy();
                this.myPieChart = null;
            }
        } else {
            this.facets = null;
            if (this.myPieChart) {
                this.myPieChart.destroy();
                this.myPiechart = null;
            }
        }

        return (
            <div>
                <div className="title">
                    Project
                    <center><hr width="80%" color="blue" /></center>
                </div>
                {this.facetData.length && total ?
                    <div id="chart-wrapper-1" className="chart-wrapper">
                        <div className="chart-container">
                            <canvas id="myChart" />
                        </div>
                        <div id="chart-legend" className="chart-legend" />
                    </div>
                    :
                    <div className="chart-no-data" style={{ height: this.wrapperHeight }}><p>No data to display</p></div>
                }
            </div>
        );
    }
}

HomepageChart.propTypes = {
    query: PropTypes.string.isRequired,
    data: PropTypes.object,
};

HomepageChart.defaultProps = {
    data: null,
};

HomepageChart.contextTypes = {
    navigate: PropTypes.func,
    projectColors: PropTypes.object, // DataColor instance for experiment project
};


// Component to display the D3-based chart for Biosample
class HomepageChart2 extends React.Component {
    constructor(props) {
        super(props);
        this.wrapperHeight = 200;
        this.createChart = this.createChart.bind(this);
        this.updateChart = this.updateChart.bind(this);
    }

    componentDidMount() {
        if (document.getElementById('myChart2')) {
            this.createChart(this.facetData);
        }
    }

    componentDidUpdate() {
        if (this.myPieChart) {
            // Existing data updated
            this.updateChart(this.myPieChart, this.facetData);
        } else if (this.facetData.length) {
            // Chart existed but was destroyed for lack of data. Rebuild the chart.
            this.createChart(this.facetData);
        }
    }

    createChart(facetData) {
        // Draw the chart of search results given in this.props.data.facets. Since D3 doesn't work
        // with the React virtual DOM, we have to load it separately using the webpack .ensure
        // mechanism. Once the callback is called, it's loaded and can be referenced through
        // require.
        require.ensure(['chart.js'], (require) => {
            const Chart = require('chart.js');
            const colors = globals.biosampleTypeColors.colorList(facetData.map(term => term.key), { shade: 10 });
            const data = [];
            const labels = [];

            facetData.forEach((term, i) => {
                data[i] = term.doc_count;
                labels[i] = term.key;
            });

            // adding total doc count to middle of donut
            // http://stackoverflow.com/questions/20966817/how-to-add-text-inside-the-doughnut-chart-using-chart-js/24671908
            Chart.pluginService.register({
                beforeDraw: drawDonutCenter,
            });

            // Pass the assay_title counts to the charting library to render it.
            const canvas = document.getElementById('myChart2');
            if (canvas) {
                const ctx = canvas.getContext('2d');
                this.myPieChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels,
                        datasets: [{
                            data,
                            backgroundColor: colors,
                        }],
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        legend: {
                            display: false, // hiding automatically generated legend
                        },
                        animation: {
                            duration: 200,
                        },
                        legendCallback: (chart) => { // allows for legend clicking
                            const chartData = chart.data.datasets[0].data;
                            const text = [];
                            text.push('<ul>');
                            for (let i = 0; i < chartData.length; i += 1) {
                                if (chartData[i]) {
                                    text.push('<li>');
                                    text.push(`<a href="/matrix/${this.props.query}&biosample_type=${chart.data.labels[i]}">`); // go to matrix view when clicked
                                    text.push(`<span class="chart-legend-chip" style="background-color:${chart.data.datasets[0].backgroundColor[i]}"></span>`);
                                    if (chart.data.labels[i]) {
                                        text.push(`<span class="chart-legend-label">${chart.data.labels[i]}</span>`);
                                    }
                                    text.push('</a></li>');
                                }
                            }
                            text.push('</ul>');
                            return text.join('');
                        },
                        onClick: (e) => {
                            // React to clicks on pie sections
                            const activePoints = this.myPieChart.getElementAtEvent(e);
                            if (activePoints[0]) {
                                const clickedElementIndex = activePoints[0]._index;
                                const term = this.myPieChart.data.labels[clickedElementIndex];
                                this.context.navigate(`/matrix/${this.props.query}&biosample_type=${term}`); // go to matrix view
                            }
                        },
                    },
                });
            } else {
                this.myPieChart = null;
            }

            // Have chartjs draw the legend into the DOM.
            const legendElement = document.getElementById('chart-legend-2');
            if (legendElement) {
                legendElement.innerHTML = this.myPieChart.generateLegend();
            }

            // Save the chart <div> height so we can set it to that value when no data's available.
            const chartWrapperDiv = document.getElementById('chart-wrapper-2');
            if (chartWrapperDiv) {
                this.wrapperHeight = chartWrapperDiv.clientHeight;
            }
        });
    }

    /* eslint-disable class-methods-use-this */
    updateChart(Chart, facetData) {
        // for each item, set doc count, add to total doc count, add proper label, and assign color.
        const colors = globals.biosampleTypeColors.colorList(facetData.map(term => term.key), { shade: 10 });
        const data = [];
        const labels = [];

        // Convert facet data to chart data.
        facetData.forEach((term, i) => {
            data[i] = term.doc_count;
            labels[i] = term.key;
        });

        // Update chart data and redraw with the new data
        Chart.data.datasets[0].data = data;
        Chart.data.datasets[0].backgroundColor = colors;
        Chart.data.labels = labels;
        Chart.update();

        // Redraw the updated legend
        document.getElementById('chart-legend-2').innerHTML = Chart.generateLegend(); // generates legend
    }
    /* eslint-enable class-methods-use-this */

    render() {
        const facets = this.props.data && this.props.data.facets;
        let total;

        // Our data source will be different for computational predictions
        if (facets) {
            this.computationalPredictions = this.props.assayCategory === 'COMPPRED';
            const assayFacet = facets.find(facet => facet.field === 'biosample_type');
            this.facetData = assayFacet ? assayFacet.terms : [];
            const docCounts = this.facetData.length ? this.facetData.map(data => data.doc_count) : [];
            total = docCounts.length ? docCounts.reduce((prev, curr) => prev + curr) : 0;

            // No data with the current selection, but we used to destroy the existing chart so we can
            // display a no-data message instead.
            if ((this.facetData.length === 0 || total === 0) && this.myPieChart) {
                this.myPieChart.destroy();
                this.myPieChart = null;
            }
        } else {
            this.facets = null;
            if (this.myPieChart) {
                this.myPieChart.destroy();
                this.myPiechart = null;
            }
        }

        return (
            <div>
                <div className="title">
                    Biosample Type
                    <center><hr width="80%" color="blue" /></center>
                </div>
                {this.facetData.length && total ?
                    <div id="chart-wrapper-2" className="chart-wrapper">
                        <div className="chart-container">
                            <canvas id="myChart2" />
                        </div>
                        <div id="chart-legend-2" className="chart-legend" />
                    </div>
                    :
                    <div className="chart-no-data" style={{ height: this.wrapperHeight }}>No data to display</div>
                }
            </div>
        );
    }
}

HomepageChart2.propTypes = {
    query: PropTypes.string.isRequired,
    data: PropTypes.object,
    assayCategory: PropTypes.string,
};

HomepageChart2.defaultProps = {
    data: null,
    assayCategory: '',
};

HomepageChart2.contextTypes = {
    navigate: PropTypes.func,
    biosampleTypeColors: PropTypes.object, // DataColor instance for experiment project
};


// Draw the small triangle above the selected assay in the "Assay Categories" chart if the user has
// selected an assay from the classic image.
function drawColumnSelects(currentAssay, ctx, data) {
    // Adapted from https://github.com/chartjs/Chart.js/issues/2477#issuecomment-255042267
    if (currentAssay) {
        ctx.fillStyle = '#2138B2';

        // Find the data with a label matching the currently selected assay.
        const currentColumn = data.labels.indexOf(currentAssay);
        if (currentColumn !== -1) {
            // Get information on the matching column's coordinates so we know where to draw the
            // triangle.
            const dataset = data.datasets[0];
            const model = dataset._meta[Object.keys(dataset._meta)[0]].data[currentColumn]._model;

            // Draw the triangle into the HTML5 <canvas> element.
            ctx.beginPath();
            ctx.moveTo(model.x - 5, model.y - 8);
            ctx.lineTo(model.x, model.y - 3);
            ctx.lineTo(model.x + 5, model.y - 8);
            ctx.fill();
        }
    }
}


// Component to display the D3-based chart for Biosample
class HomepageChart3 extends React.Component {
    constructor(props) {
        super(props);
        this.wrapperHeight = 200;
        this.createChart = this.createChart.bind(this);
        this.updateChart = this.updateChart.bind(this);
    }

    componentDidMount() {
        if (document.getElementById('myChart3')) {
            this.createChart(this.facetData);
        }
    }

    componentDidUpdate() {
        if (this.myPieChart) {
            // Existing data updated
            this.updateChart(this.myPieChart, this.facetData);
        } else if (this.facetData.length) {
            // Chart existed but was destroyed for lack of data. Rebuild the chart.
            this.createChart(this.facetData);
        }
    }

    createChart(facetData) {
        // Draw the chart of search results given in this.props.data.facets. Since D3 doesn't work
        // with the React virtual DOM, we have to load it separately using the webpack .ensure
        // mechanism. Once the callback is called, it's loaded and can be referenced through
        // require.
        require.ensure(['chart.js'], (require) => {
            const Chart = require('chart.js');
            const colors = [];
            const data = [];
            const labels = [];
            const selectedAssay = (this.props.assayCategory && this.props.assayCategory !== 'COMPPRED') ? this.props.assayCategory.replace(/\+/g, ' ') : '';

            // For each item, set doc count, add to total doc count, add proper label, and assign
            // color.
            facetData.forEach((term, i) => {
                data[i] = term.doc_count;
                labels[i] = term.key;
                colors[i] = selectedAssay ? (term.key === selectedAssay ? 'rgb(255,217,98)' : 'rgba(255,217,98,.4)') : '#FFD962';
            });

            // Pass the counts to the charting library to render it.
            const canvas = document.getElementById('myChart3');
            if (canvas) {
                const ctx = canvas.getContext('2d');
                this.myPieChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels, // full labels
                        datasets: [{
                            data,
                            backgroundColor: colors,
                        }],
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        legend: {
                            display: false, // hiding automatically generated legend
                        },
                        hover: {
                            mode: false,
                        },
                        animation: {
                            duration: 0,
                            onProgress: function onProgress() { drawColumnSelects(selectedAssay, this.chart.ctx, this.data); },
                            onComplete: function onComplete() { drawColumnSelects(selectedAssay, this.chart.ctx, this.data); },
                        },
                        scales: {
                            xAxes: [{
                                gridLines: {
                                    display: false,
                                },
                                ticks: {
                                    autoSkip: false,
                                },
                            }],
                        },
                        layout: {
                            padding: {
                                top: 10,
                            },
                        },
                        onClick: (e) => {
                            // React to clicks on pie sections
                            const query = 'assay_slims=';
                            const activePoints = this.myPieChart.getElementAtEvent(e);
                            if (activePoints[0]) {
                                const clickedElementIndex = activePoints[0]._index;
                                const term = this.myPieChart.data.labels[clickedElementIndex];
                                this.context.navigate(`/matrix/${this.props.query}&${query}${term}`); // go to matrix view
                            }
                        },
                    },
                });

                // Save height of wrapper div.
                const chartWrapperDiv = document.getElementById('chart-wrapper-3');
                this.wrapperHeight = chartWrapperDiv.clientHeight;
            }
        });
    }

    updateChart(Chart, facetData) {
        // for each item, set doc count, add to total doc count, add proper label, and assign color.
        const data = [];
        const labels = [];
        const colors = [];

        // Convert facet data to chart data.
        const selectedAssay = (this.props.assayCategory && this.props.assayCategory !== 'COMPPRED') ? this.props.assayCategory.replace(/\+/g, ' ') : '';
        facetData.forEach((term, i) => {
            data[i] = term.doc_count;
            labels[i] = term.key;
            colors[i] = selectedAssay ? (term.key === selectedAssay ? 'rgb(255,217,98)' : 'rgba(255,217,98,.4)') : '#FFD962';
        });

        // Update chart data and redraw with the new data
        Chart.data.datasets[0].data = data;
        Chart.data.labels = labels;
        Chart.data.datasets[0].backgroundColor = colors;
        Chart.options.hover.mode = false;
        Chart.options.animation.onProgress = function onProgress() { drawColumnSelects(selectedAssay, this.chart.ctx, this.data); };
        Chart.options.animation.onComplete = function onComplete() { drawColumnSelects(selectedAssay, this.chart.ctx, this.data); };
        Chart.update();
    }

    render() {
        const facets = this.props.data && this.props.data.facets;
        let total;

        // Get all assay category facets, or an empty array if none
        if (facets) {
            const projectFacet = facets.find(facet => facet.field === 'assay_slims');
            this.facetData = projectFacet ? projectFacet.terms : [];
            const docCounts = this.facetData.length ? this.facetData.map(data => data.doc_count) : [];
            total = docCounts.length ? docCounts.reduce((prev, curr) => prev + curr) : 0;

            // No data with the current selection, but we used to? Destroy the existing chart so we can
            // display a no-data message instead.
            if ((this.facetData.length === 0 || total === 0) && this.myPieChart) {
                this.myPieChart.destroy();
                this.myPieChart = null;
            }
        } else {
            this.facets = null;
            if (this.myPieChart) {
                this.myPieChart.destroy();
                this.myPiechart = null;
            }
        }

        return (
            <div>
                <div className="title">
                    Assay Categories
                    <center><hr width="80%" color="blue" /></center>
                </div>
                {this.facetData.length && total ?
                    <div id="chart-wrapper-3" className="chart-wrapper">
                        <div className="chart-container-assaycat">
                            <canvas id="myChart3" />
                        </div>
                    </div>
                    :
                    <div className="chart-no-data" style={{ height: this.wrapperHeight }}>No data to display</div>
                }
            </div>
        );
    }
}

HomepageChart3.propTypes = {
    assayCategory: PropTypes.string,
    query: PropTypes.string.isRequired,
    data: PropTypes.object,
};

HomepageChart3.defaultProps = {
    assayCategory: '',
    data: null,
};

HomepageChart3.contextTypes = {
    navigate: PropTypes.func,
};


// Render the most recent five news posts
class News extends React.Component {
    componentDidMount() {
        this.props.newsLoaded(this.nodeRef);
    }

    render() {
        const { items } = this.props;
        if (items && items.length) {
            return (
                <div ref={(node) => { this.nodeRef = node; }} className="news-listing">
                    {items.map(item =>
                        <div key={item['@id']} className="news-listing-item">
                            <h3>{item.title}</h3>
                            <h4>{moment.utc(item.date_created).format('MMMM D, YYYY')}</h4>
                            <div className="news-excerpt">{item.news_excerpt}</div>
                            <div className="news-listing-readmore">
                                <a className="btn btn-info btn-sm" href={item['@id']} title={`View news post for ${item.title}`} key={item['@id']}>Read more</a>
                            </div>
                        </div>
                    )}
                </div>
            );
        }
        return <div className="news-empty">No news available at this time</div>;
    }
}

News.propTypes = {
    items: PropTypes.array,
    newsLoaded: PropTypes.func.isRequired, // Called parent once the news is loaded
};

News.defaultProps = {
    items: null,
};


// Send a GET request for the most recent five news posts. Don't make this a stateless component
// because we attach `ref` to this, and stateless components don't support that.
/* eslint-disable react/prefer-stateless-function */
class NewsLoader extends React.Component {
    render() {
        return <FetchedItems {...this.props} url={`${newsUri}&limit=5`} Component={News} newsLoaded={this.props.newsLoaded} />;
    }
}
/* eslint-enable react/prefer-stateless-function */

NewsLoader.propTypes = {
    newsLoaded: PropTypes.func.isRequired, // Called parent once the news is loaded
};


class TwitterWidget extends React.Component {
    constructor(props) {
        super(props);
        this.initialized = false;
        this.injectTwitter = this.injectTwitter.bind(this);
    }

    componentDidMount() {
        if (!this.initialized && this.props.height) {
            this.injectTwitter();
        }
    }

    componentDidUpdate() {
        if (!this.initialized && this.props.height) {
            this.injectTwitter();
        }
    }

    injectTwitter() {
        if (!this.initialized) {
            const link = this.anchor;
            this.initialized = true;
            const js = document.createElement('script');
            js.id = 'twitter-wjs';
            js.src = '//platform.twitter.com/widgets.js';
            return link.parentNode.appendChild(js);
        }
        return null;
    }

    render() {
        return (
            <div>
                <div className="twitter-header">
                    <h2>Twitter <a href="https://twitter.com/EncodeDCC" title="ENCODE DCC Twitter page in a new window or tab" target="_blank" rel="noopener noreferrer"className="twitter-ref">@EncodeDCC</a></h2>
                </div>
                {this.props.height ?
                    <a
                        ref={(anchor) => { this.anchor = anchor; }}
                        className="twitter-timeline"
                        href="https://twitter.com/encodedcc" // from encodedcc twitter
                        data-chrome="noheader"
                        data-screen-name="EncodeDCC"
                        data-height={this.props.height.toString()} // height so it matches with rest of site
                    >
                        @EncodeDCC
                    </a>
                : null}
            </div>
        );
    }
}

TwitterWidget.propTypes = {
    height: PropTypes.number.isRequired, // Number of pixels tall to make widget
};
