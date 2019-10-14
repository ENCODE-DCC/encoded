import React from 'react';
import styles from './LabChartStyle';

//Thanks to scale-color-perceptual
const allViridisColors = ["#440154", "#440256", "#450457", "#450559", "#46075a", "#46085c", "#460a5d", "#460b5e", "#470d60", "#470e61", "#471063", "#471164", "#471365", "#481467", "#481668", "#481769", "#48186a", "#481a6c", "#481b6d", "#481c6e", "#481d6f", "#481f70", "#482071", "#482173", "#482374", "#482475", "#482576", "#482677", "#482878", "#482979", "#472a7a", "#472c7a", "#472d7b", "#472e7c", "#472f7d", "#46307e", "#46327e", "#46337f", "#463480", "#453581", "#453781", "#453882", "#443983", "#443a83", "#443b84", "#433d84", "#433e85", "#423f85", "#424086", "#424186", "#414287", "#414487", "#404588", "#404688", "#3f4788", "#3f4889", "#3e4989", "#3e4a89", "#3e4c8a", "#3d4d8a", "#3d4e8a", "#3c4f8a", "#3c508b", "#3b518b", "#3b528b", "#3a538b", "#3a548c", "#39558c", "#39568c", "#38588c", "#38598c", "#375a8c", "#375b8d", "#365c8d", "#365d8d", "#355e8d", "#355f8d", "#34608d", "#34618d", "#33628d", "#33638d", "#32648e", "#32658e", "#31668e", "#31678e", "#31688e", "#30698e", "#306a8e", "#2f6b8e", "#2f6c8e", "#2e6d8e", "#2e6e8e", "#2e6f8e", "#2d708e", "#2d718e", "#2c718e", "#2c728e", "#2c738e", "#2b748e", "#2b758e", "#2a768e", "#2a778e", "#2a788e", "#29798e", "#297a8e", "#297b8e", "#287c8e", "#287d8e", "#277e8e", "#277f8e", "#27808e", "#26818e", "#26828e", "#26828e", "#25838e", "#25848e", "#25858e", "#24868e", "#24878e", "#23888e", "#23898e", "#238a8d", "#228b8d", "#228c8d", "#228d8d", "#218e8d", "#218f8d", "#21908d", "#21918c", "#20928c", "#20928c", "#20938c", "#1f948c", "#1f958b", "#1f968b", "#1f978b", "#1f988b", "#1f998a", "#1f9a8a", "#1e9b8a", "#1e9c89", "#1e9d89", "#1f9e89", "#1f9f88", "#1fa088", "#1fa188", "#1fa187", "#1fa287", "#20a386", "#20a486", "#21a585", "#21a685", "#22a785", "#22a884", "#23a983", "#24aa83", "#25ab82", "#25ac82", "#26ad81", "#27ad81", "#28ae80", "#29af7f", "#2ab07f", "#2cb17e", "#2db27d", "#2eb37c", "#2fb47c", "#31b57b", "#32b67a", "#34b679", "#35b779", "#37b878", "#38b977", "#3aba76", "#3bbb75", "#3dbc74", "#3fbc73", "#40bd72", "#42be71", "#44bf70", "#46c06f", "#48c16e", "#4ac16d", "#4cc26c", "#4ec36b", "#50c46a", "#52c569", "#54c568", "#56c667", "#58c765", "#5ac864", "#5cc863", "#5ec962", "#60ca60", "#63cb5f", "#65cb5e", "#67cc5c", "#69cd5b", "#6ccd5a", "#6ece58", "#70cf57", "#73d056", "#75d054", "#77d153", "#7ad151", "#7cd250", "#7fd34e", "#81d34d", "#84d44b", "#86d549", "#89d548", "#8bd646", "#8ed645", "#90d743", "#93d741", "#95d840", "#98d83e", "#9bd93c", "#9dd93b", "#a0da39", "#a2da37", "#a5db36", "#a8db34", "#aadc32", "#addc30", "#b0dd2f", "#b2dd2d", "#b5de2b", "#b8de29", "#bade28", "#bddf26", "#c0df25", "#c2df23", "#c5e021", "#c8e020", "#cae11f", "#cde11d", "#d0e11c", "#d2e21b", "#d5e21a", "#d8e219", "#dae319", "#dde318", "#dfe318", "#e2e418", "#e5e419", "#e7e419", "#eae51a", "#ece51b", "#efe51c", "#f1e51d", "#f4e61e", "#f6e620", "#f8e621", "#fbe723", "#fde725"];

class LabChart extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            patients: [],
            features: [],
            featuresChecked: {},
            currentPatient: "KCEPT925TMI",
            currentFeature: "ALBUMIN",
            checkboxes: []
        };
        // this.zingchart = window.zingchart;
        // this.moment = window.moment;
        // this.axios = window.axios;
        this.myConfig = {
            "utc": true,
            "plotarea": {
                "adjust-layout": true
            },
            graphset: []
        };
        this.featuresChecked = {};
        this.data = {};
        this.viridisColors = [];
        this.oldMethods = false;

        // This binding is necessary to make `this` work in the callback
        this.toggleMethods = this.toggleMethods.bind(this);
        this.zoomIn = this.zoomIn.bind(this);
        this.zoomOut = this.zoomOut.bind(this);
    }
    render() {
        return (<div>
            <div className="flex-container" style={styles.flexContainer}>
                <div className="chart-menu" style={styles.chartMenu}>
                    <h4>Show/Hide Lab Results</h4>
                <div>
                    <button onClick={this.toggleMethods}>Switch data</button>
                    <div>Currently using {this.oldMethods ? "old " : "new "} methods.</div>
                </div>
                    <div className="chart-checkboxes pb-2" style={styles.chartCheckboxes, styles.pb2}>{this.state.checkboxes}</div>
                    {/* zoom in and out buttons */}
                    <div className="pt-2" style={styles.pt2}>
                        <button className="mr-2" style={styles.mr2} onClick={this.zoomIn}>Zoom In</button>
                        <button onClick={this.zoomOut}>Zoom Out</button>
                    </div>
                </div>
                <div className="chart-main" style={styles.chartMain}>
                    <div className="chart-title" style={styles.chartTitle}><h3>Lab Results Over Time</h3></div>
                    <div id={this.props.chartId} className="chart-area" style={styles.chartArea}>

                    </div>
                </div>
            </div>
        </div>)

    }
    renderChart() {
        this.zingchart.render({
            id: this.props.chartId,
            data: this.myConfig,
            height: '100%',
            width: '100%'
        });
    }
    zoomIn() {
        this.zingchart.exec(this.props.chartId, "zoomin", { zoomx: true, zoomy: false });
    }
    zoomOut() {
        this.zingchart.exec(this.props.chartId, "zoomout", { zoomx: true, zoomy: false });
    }
    createCheckboxes() {
        let tempCheckboxes = [];
        for (let i = 0; i < this.state.features.length; i++) {
            let feature = this.state.features[i];
            this.featuresChecked[feature] = { checked: true, color: this.viridisColors[i] };
            var styles = {
                color: this.viridisColors[i]
            }
            tempCheckboxes.push(<div key={i}><input type="checkbox" id={feature} value={feature} name={feature} defaultChecked="checked" onChange={(e) => {this.handleCheckboxChange(e, this)}} />
                <label style={styles} htmlFor={feature}>{feature}</label></div>)
        }
        this.setState({ checkboxes: tempCheckboxes });
    }
    drawChart() {
        this.axios.get(
            "https://raw.githubusercontent.com/utsw-bicf/pandiseased/kce/src/encoded/tests/data/inserts/lab_results.json",
            {
                params: {
                }
            })
            .then(response => {
                if (response.status === 200) {
                    this.prepareData(response.data);
                }
            }).catch(error => {
                console.log(error);
            });
    }
    drawChart2() {
        this.prepareData2(this.props.labs);
    }
    parseTime(dateString) {
        return this.moment(dateString).unix() * 1000;
    }
    handleCheckboxChange(event) {
        let checked = event.currentTarget.checked;
        let value = event.currentTarget.value;
        this.featuresChecked[value]["checked"] = checked;
        if (this.oldMethods) {
            this.updateChart(value, checked);
        }
        else {
            this.updateChart2(value, checked);
        }
    }
    updateChart(value, checked) {
        this.myConfig.graphset = [];

        this.myConfig.layout = (this.state.features.length + 1) + "x1";
        //extract all dates
        let allDates = [...new Set(this.data.filter(i => { return i.patient === this.state.currentPatient }).map(i => { return i.date }))];
        let allDatesUnix = allDates.map(i => { return this.parseTime(i) });
        let startDate = Math.min(...allDatesUnix);
        let endDate = Math.max(...allDatesUnix);
        for (let i = 0; i < this.state.features.length; i++) {
            // for (let i = 0; i < 3; i++) {
            let feature = this.state.features[i];
            if (this.featuresChecked[feature]["checked"] === false) {
                continue;
            }
            let filteredData = this.data.filter(i => { return i.patient === this.state.currentPatient && i.lab === feature });
            let values = [];
            for (let j = 0; j < allDates.length; j++) {
                let currentDate = allDates[j];
                let dataPoints = filteredData.filter(i => { return i.date === currentDate });
                if (dataPoints.length > 0) {
                    values.push([allDatesUnix[j], dataPoints[0].value]);
                }
                else {
                    values.push([allDatesUnix[j], null]);
                }
            }

            // let values = filteredData.map(i => {return [parseTime(i.date), i.value]});
            // let formattedDates = filteredData.map(i => {return i.date});
            let unit = filteredData[0].value_units;
            let minY = Math.min(...filteredData.map(i => { return i.value }));
            let chart = {
                type: "line",
                // crosshairX: {
                //     shared: true,
                //     plotLabel: {
                //         // text: "%data-day " + feature + ": %v " + unit //uncomment this to use dates in label
                //         text: feature + ": %v " + unit
                //     }
                // },
                plot: {
                    marker: {
                        size: 2,
                        borderColor: "white",
                        borderWidth: 0,
                        backgroundColor: this.pickNextColor(i)
                    }
                },
                zoom: {
                    shared: true
                },
                tooltip: {
                    visible: true,
                    text: feature + ": %v " + unit
                },
                title: {
                    text: feature + " (" + unit + ")",
                    fontSize: 10
                },
                series: [{
                    values: values,
                    // "data-day": allDates, //uncomment this to use dates in label
                    lineWidth: 1, /* in pixels */
                    lineColor: this.pickNextColor(i)
                }],
                // labels: allDatesUnix,
                scaleX: {
                    minValue: startDate,
                    maxValue: endDate,
                    visible: false,
                    zooming: true
                },
                scrollX: {
                },
                scaleY: {
                    visible: true,
                    minValue: minY
                },
                plotarea: {
                    // margin:"dynamic",
                    "margin-left": "50px",
                    "margin-top": "20px",
                    "margin-right": "0px",
                    "margin-bottom": "20px"
                },
            };
            // if (i === (this.state.features.length - 1)) {
            //     chart.scaleX = {
            //         transform: {
            //             type: "date",
            //             all: "%Y-%m-%d"
            //         },
            //         visible: true,
            //         zooming: true,
            //         minValue: startDate,
            //         maxValue: endDate,
            //     }
            //     // chart.preview = {};
            //     // chart.plotarea.paddingBottom = "-300px";
            // }
            this.myConfig.graphset.push(chart);
        }
        let lastChart = this.myConfig.graphset[this.myConfig.graphset.length - 1];
        lastChart.scaleX = {
            transform: {
                type: "date",
                // all: "%Y-%m-%d",
                all: "%m-%d-%Y"
            },
            visible: true,
            zooming: true,
            minValue: startDate,
            maxValue: endDate,
        }
        // lastChart.preview = {
        //     adjustLayout: true
        // };
        this.zingchart.exec(this.props.chartId, 'destroy'); //kill the chart 
        this.renderChart();

    }
    updateChart2(value, checked) {
        //TODO once prepareData2 is done, modify this method
        //the format of "this.data" might not be compatible with the code below to extract dates and other features.
        //you might need to adapt it.
        //You can use a for loop instead of => to iterate through each element of an array if you're not comfortable with that syntax yet.
        //the "filter" method only keep elements in the array where the condition is true and creates a new array with those elements. For instance:
        //i.patient === this.state.currentPatient means that we only keep elements where the "patient" field equals "currentPatient"
        //the "map" method creates a new element for each element in the array. For instance:
        //.map(i => { return i.date }) means that I transform the element "i" into just the date value ("i.date")
        //look online for the proper definitions of filter, map and ... (it's called spread)
        this.myConfig.graphset = [];

        this.myConfig.layout = (this.state.features.length + 1) + "x1";
        //extract all dates
        let allDates = [...new Set(this.data.filter(i => { return i.patient === this.state.currentPatient }).map(i => { return i.date }))];
        let allDatesUnix = allDates.map(i => { return this.parseTime(i) });
        let startDate = Math.min(...allDatesUnix);
        let endDate = Math.max(...allDatesUnix);
        for (let i = 0; i < this.state.features.length; i++) {
            // for (let i = 0; i < 3; i++) {
            let feature = this.state.features[i];
            if (this.featuresChecked[feature]["checked"] === false) {
                continue;
            }
            let filteredData = this.data.filter(i => { return i.patient === this.state.currentPatient && i.lab === feature });
            let values = [];
            for (let j = 0; j < allDates.length; j++) {
                let currentDate = allDates[j];
                let dataPoints = filteredData.filter(i => { return i.date === currentDate });
                if (dataPoints.length > 0) {
                    values.push([allDatesUnix[j], dataPoints[0].value]);
                }
                else {
                    values.push([allDatesUnix[j], null]);
                }
            }

            // let values = filteredData.map(i => {return [parseTime(i.date), i.value]});
            // let formattedDates = filteredData.map(i => {return i.date});
            let unit = filteredData[0].value_units;
            let minY = Math.min(...filteredData.map(i => { return i.value }));
            let chart = {
                type: "line",
                // crosshairX: {
                //     shared: true,
                //     plotLabel: {
                //         // text: "%data-day " + feature + ": %v " + unit //uncomment this to use dates in label
                //         text: feature + ": %v " + unit
                //     }
                // },
                plot: {
                    marker: {
                        size: 2,
                        borderColor: "white",
                        borderWidth: 0,
                        backgroundColor: this.pickNextColor(i)
                    }
                },
                zoom: {
                    shared: true
                },
                tooltip: {
                    visible: true,
                    text: feature + ": %v " + unit
                },
                title: {
                    text: feature + " (" + unit + ")",
                    fontSize: 10
                },
                series: [{
                    values: values,
                    // "data-day": allDates, //uncomment this to use dates in label
                    lineWidth: 1, /* in pixels */
                    lineColor: this.pickNextColor(i)
                }],
                // labels: allDatesUnix,
                scaleX: {
                    minValue: startDate,
                    maxValue: endDate,
                    visible: false,
                    zooming: true
                },
                scrollX: {
                },
                scaleY: {
                    visible: true,
                    minValue: minY
                },
                plotarea: {
                    // margin:"dynamic",
                    "margin-left": "50px",
                    "margin-top": "20px",
                    "margin-right": "0px",
                    "margin-bottom": "20px"
                },
            };
            // if (i === (this.state.features.length - 1)) {
            //     chart.scaleX = {
            //         transform: {
            //             type: "date",
            //             all: "%Y-%m-%d"
            //         },
            //         visible: true,
            //         zooming: true,
            //         minValue: startDate,
            //         maxValue: endDate,
            //     }
            //     // chart.preview = {};
            //     // chart.plotarea.paddingBottom = "-300px";
            // }
            this.myConfig.graphset.push(chart);
        }
        let lastChart = this.myConfig.graphset[this.myConfig.graphset.length - 1];
        lastChart.scaleX = {
            transform: {
                type: "date",
                // all: "%Y-%m-%d",
                all: "%m-%d-%Y"
            },
            visible: true,
            zooming: true,
            minValue: startDate,
            maxValue: endDate,
        }
        // lastChart.preview = {
        //     adjustLayout: true
        // };
        this.zingchart.exec(this.props.chartId, 'destroy'); //kill the chart 
        this.renderChart();

    }
    pickNextColor(index) {
        return this.viridisColors[index];
    }
    /**
 * Format the data for ZingChart line plot by extracting 
 * the current patient data.
 * 
 * @param {JSON array of format 
 * [{
    "date": "1866-04-17",
    "lab": "PLATELETS",
    "value": 346,
    "reference_flag": "Normal",
    "value_units": "x10(3)/ul",
    "reference_low": 170,
    "reference_high": 404,
    "patient": "KCEPT078DUA",
    "uuid": "e88e7d60-a566-4058-8d8f-198e64070e3a"
 * }, ...]
 * } data 
 */
    prepareData(data) {
        console.log(data);
        console.log(this.props.labs);
        let tempPatients = [];
        let tempFeatures = [];
        let patientSet = new Set();
        let patientNames = data.map(i => { return i.patient }, this);
        patientNames.forEach(name => { patientSet.add(name) });
        for (let name of patientSet.entries()) {
            tempPatients.push(name[0]);
            tempPatients.sort();
        }
        let featureSet = new Set();
        let featureNames = data.map(i => { return i.lab }, this);
        featureNames.forEach(name => { featureSet.add(name) });
        for (let name of featureSet.entries()) {
            tempFeatures.push(name[0]);
            tempFeatures.sort();
        }
        // console.log(tempPatients, tempFeatures);
        this.data = data;
        this.setState({ patients: tempPatients });
        this.setState({ features: tempFeatures });
        this.compileViridisColors();
        this.createCheckboxes();
        this.updateChart();
    }
    prepareData2(data) {
        //TODO change the code here to use the new format of "data" (from "this.props.labs")
        //there is only one patient so remove any references to "patientNames"
        //careful with updateChart2: there is a check to see if the patient name matches "currentPatient"
        //"data" is not an array this time, it's a dictionary. You can iterate through each key/value pair with Object.entries(data) which creates an array
        //look at other methods online to extract the keys (without the values) to build the array "tempFeatures"
        //use plenty of console.log(<MY_VALUE>) to inspect the values of your objects in the Chrome console. You can delete them later.
        //use breakpoints to stop your code inside each method and inspect object available in that method.
        let tempPatients = [];
        let tempFeatures = Object.keys(data).sort();
        // let patientSet = new Set();
        // let patientNames = data.map(i => { return i.patient }, this);
        // patientNames.forEach(name => { patientSet.add(name) });
        // for (let name of patientSet.entries()) {
        //     tempPatients.push(name[0]);
        //     tempPatients.sort();
        // }
        // let featureSet = new Set();
        // let featureNames = data.map(i => { return i.lab }, this);
        // featureNames.forEach(name => { featureSet.add(name) });
        // for (let name of featureSet.entries()) {
        //     tempFeatures.push(name[0]);
        //     tempFeatures.sort();
        // }
        // console.log(tempPatients, tempFeatures);
        this.data = data;
        this.setState({ patients: tempPatients });
        this.setState({ features: tempFeatures });
        this.compileViridisColors();
        this.createCheckboxes();
        this.updateChart2();
    }
    /**
     * Create a subset of the viridis color scale
     */
    compileViridisColors() {
        this.viridisColors = [];
        var count = Math.round(allViridisColors.length / this.state.features.length);
        for (let i = 0; i < allViridisColors.length; i++) {
            if (i % count === 0) {
                this.viridisColors.push(allViridisColors[i]);
            }
        };
        console.log(this.viridisColors);

    }
    toggleMethods() {
        this.oldMethods = !this.oldMethods;
        if (this.oldMethods) {
            this.drawChart();
        }
        else {
            this.drawChart2();
        }
    }
    componentDidMount() {
        this.zingchart = window.zingchart;
        this.moment = window.moment;
        this.axios = window.axios;
        if (this.oldMethods) {
            this.drawChart();
        }
        else {
            this.drawChart2();
        }
    }
}

export default LabChart;

