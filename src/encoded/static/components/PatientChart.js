import React from 'react';
import styles from './LabChartStyle';

//Thanks to scale-color-perceptual
const allViridisColors = ["#440154", "#440256", "#450457", "#450559", "#46075a", "#46085c", "#460a5d", "#460b5e", "#470d60", "#470e61", "#471063", "#471164", "#471365", "#481467", "#481668", "#481769", "#48186a", "#481a6c", "#481b6d", "#481c6e", "#481d6f", "#481f70", "#482071", "#482173", "#482374", "#482475", "#482576", "#482677", "#482878", "#482979", "#472a7a", "#472c7a", "#472d7b", "#472e7c", "#472f7d", "#46307e", "#46327e", "#46337f", "#463480", "#453581", "#453781", "#453882", "#443983", "#443a83", "#443b84", "#433d84", "#433e85", "#423f85", "#424086", "#424186", "#414287", "#414487", "#404588", "#404688", "#3f4788", "#3f4889", "#3e4989", "#3e4a89", "#3e4c8a", "#3d4d8a", "#3d4e8a", "#3c4f8a", "#3c508b", "#3b518b", "#3b528b", "#3a538b", "#3a548c", "#39558c", "#39568c", "#38588c", "#38598c", "#375a8c", "#375b8d", "#365c8d", "#365d8d", "#355e8d", "#355f8d", "#34608d", "#34618d", "#33628d", "#33638d", "#32648e", "#32658e", "#31668e", "#31678e", "#31688e", "#30698e", "#306a8e", "#2f6b8e", "#2f6c8e", "#2e6d8e", "#2e6e8e", "#2e6f8e", "#2d708e", "#2d718e", "#2c718e", "#2c728e", "#2c738e", "#2b748e", "#2b758e", "#2a768e", "#2a778e", "#2a788e", "#29798e", "#297a8e", "#297b8e", "#287c8e", "#287d8e", "#277e8e", "#277f8e", "#27808e", "#26818e", "#26828e", "#26828e", "#25838e", "#25848e", "#25858e", "#24868e", "#24878e", "#23888e", "#23898e", "#238a8d", "#228b8d", "#228c8d", "#228d8d", "#218e8d", "#218f8d", "#21908d", "#21918c", "#20928c", "#20928c", "#20938c", "#1f948c", "#1f958b", "#1f968b", "#1f978b", "#1f988b", "#1f998a", "#1f9a8a", "#1e9b8a", "#1e9c89", "#1e9d89", "#1f9e89", "#1f9f88", "#1fa088", "#1fa188", "#1fa187", "#1fa287", "#20a386", "#20a486", "#21a585", "#21a685", "#22a785", "#22a884", "#23a983", "#24aa83", "#25ab82", "#25ac82", "#26ad81", "#27ad81", "#28ae80", "#29af7f", "#2ab07f", "#2cb17e", "#2db27d", "#2eb37c", "#2fb47c", "#31b57b", "#32b67a", "#34b679", "#35b779", "#37b878", "#38b977", "#3aba76", "#3bbb75", "#3dbc74", "#3fbc73", "#40bd72", "#42be71", "#44bf70", "#46c06f", "#48c16e", "#4ac16d", "#4cc26c", "#4ec36b", "#50c46a", "#52c569", "#54c568", "#56c667", "#58c765", "#5ac864", "#5cc863", "#5ec962", "#60ca60", "#63cb5f", "#65cb5e", "#67cc5c", "#69cd5b", "#6ccd5a", "#6ece58", "#70cf57", "#73d056", "#75d054", "#77d153", "#7ad151", "#7cd250", "#7fd34e", "#81d34d", "#84d44b", "#86d549", "#89d548", "#8bd646", "#8ed645", "#90d743", "#93d741", "#95d840", "#98d83e", "#9bd93c", "#9dd93b", "#a0da39", "#a2da37", "#a5db36", "#a8db34", "#aadc32", "#addc30", "#b0dd2f", "#b2dd2d", "#b5de2b", "#b8de29", "#bade28", "#bddf26", "#c0df25", "#c2df23", "#c5e021", "#c8e020", "#cae11f", "#cde11d", "#d0e11c", "#d2e21b", "#d5e21a", "#d8e219", "#dae319", "#dde318", "#dfe318", "#e2e418", "#e5e419", "#e7e419", "#eae51a", "#ece51b", "#efe51c", "#f1e51d", "#f4e61e", "#f6e620", "#f8e621", "#fbe723", "#fde725"];

class PatientChart extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            features: [],
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
        this.zoomIn = this.zoomIn.bind(this);
        this.zoomOut = this.zoomOut.bind(this);
    }
    render() {
        return (<div>
            <div className="flex-container" style={styles.flexContainer}>
                <div className="chart-menu" style={styles.chartMenu}>
                    <h4>Show/Hide Results</h4>
                    <div className="chart-checkboxes pb-2" style={styles.chartCheckboxes, styles.pb2}>{this.state.checkboxes}</div>
                    {/* zoom in and out buttons */}
                    <div className="pt-2" style={styles.pt2}>
                        <button className="mr-2" style={styles.mr2} onClick={this.zoomIn}>Zoom In</button>
                        <button onClick={this.zoomOut}>Zoom Out</button>
                    </div>
                </div>
                <div className="chart-main" style={styles.chartMain}>
                    <div className="chart-title" style={styles.chartTitle}><h3>{this.props.chartTitle}</h3></div>
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
        let tempFeatures = Object.keys(this.props.data).sort();
        this.data = this.props.data;
        //console.log('before the setState method.');
        this.setState({ features: tempFeatures }, () => {
          this.compileViridisColors();
          this.createCheckboxes();
          this.updateChart();
          //console.log('inside the setState method.');
        });
        //console.log('outside the setState method.');
    }

    parseTime(dateString) {
        return this.moment(dateString).unix() * 1000;
    }
    handleCheckboxChange(event) {
        let checked = event.currentTarget.checked;
        let value = event.currentTarget.value;
        this.featuresChecked[value]["checked"] = checked;
        this.updateChart();

    }



    updateChart() {
        this.myConfig.graphset = [];

        this.myConfig.layout = (this.state.features.length + 1) + "x1";
        //extract all dates

        //let allDates = [...new Set(this.data.filter(i => { return i.patient === this.state.currentPatient }).map(i => { return i.date }))];
        let allDates = [];
        for (let i = 0; i < this.state.features.length; i++) {
            allDates = allDates.concat(this.data[this.state.features[i]].map(i => {return i.date;}));
        };
        allDates = [...new Set(allDates)]
        allDates.sort(function(a,b) {
            a = a.split('-').join('');
            b = b.split('-').join('');
            return a > b ? 1 : a < b ? -1 : 0;
            // return a.localeCompare(b);         // <-- alternative
        });
        let allDatesUnix = allDates.map(i => { return this.parseTime(i) });
        let startDate = Math.min(...allDatesUnix);
        let endDate = Math.max(...allDatesUnix);

        for (let i = 0; i < this.state.features.length; i++) {
            // for (let i = 0; i < 3; i++) {
            let feature = this.state.features[i];
            if (this.featuresChecked[feature]["checked"] === false) {
                continue;
            }
            //let filteredData = this.data.filter(i => { return i.patient === this.state.currentPatient && i.lab === feature });
            let filteredData = this.data[this.state.features[i]];
            let filteredDates = this.data[this.state.features[i]].map(i => {return i.date;});
            let filteredDatesUnix = filteredDates.map(i => { return this.parseTime(i) });
            let values = [];
            let rangeValues = [];
            let rangeLows = [];
            for (let j = 0; j < filteredDates.length; j++) {
                let currentDate = filteredDates[j];
                let dataPoints = filteredData.filter(i => { return i.date === currentDate });

                values.push([filteredDatesUnix[j], dataPoints[0].value]);

                rangeValues.push([filteredDatesUnix[j], [dataPoints[0].reference_low, dataPoints[0].reference_high]]);

                if (dataPoints[0].reference_low != undefined) {
                  rangeLows.push([dataPoints[0].reference_low]);
                };
            };
            let rangeDataForDisplay = [];
            for (let i = 0; i < rangeValues.length; i++) {
              if (rangeValues[i][1][0] === undefined || rangeValues[i][1][1] === undefined) {
                rangeDataForDisplay.push(-1);
              } else {
                rangeDataForDisplay.push("Reference low: "+ rangeValues[i][1][0] + ", Reference high: " + rangeValues[i][1][1]);

              };
            };

            let unit = filteredData[0].value_units;
            let minY = Math.min(...filteredData.map(i => { return i.value }));
            if (rangeLows.length > 0) {
              let minRange = Math.min(...rangeLows);
              minY = Math.min(minY, minRange);
            };

            let chart = {
                type: "mixed",
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

                title: {
                    text: feature + " (" + unit + ")",
                    fontSize: 10
                },
                series: [
                  {
                    type: 'line',
                    values: values,
                    "data-range": rangeDataForDisplay,
                    // "data-day": allDates, //uncomment this to use dates in label
                    lineWidth: 1, /* in pixels */
                    lineColor: this.pickNextColor(i),
                    tooltip: {
                        visible: true,
                        rules: [
                          {
                            rule: "%data-range === -1",
                            text: feature + ": %v " + unit + "<br> Date: %kl"
                          }



                        ],
                        text: feature + ": %v " + unit + "<br> Date: %kl <br>%data-range"



                    }
                  },
                  {
                    type: 'range',
                    values: rangeValues,
                    backgroundColor: '#448aff',
                    lineColor: '#448aff',
                    tooltip: {
                        visible: false,
                        //text: "Date: %kl"
                    }

                  }
                ],
                // labels: allDatesUnix,
                scaleX: {
                  transform: {
                    type: "date",
                    all: "%m-%d-%Y"
                  },
                    minValue: startDate,
                    //maxValue: endDate,
                    visible: true,
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
            this.myConfig.graphset.push(chart);
        }
        if (this.myConfig.graphset.length > 0) {
          /*
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
              //maxValue: endDate,
          }
          */
          this.zingchart.exec(this.props.chartId, 'destroy'); //kill the chart
          this.renderChart();
        } else {
          this.zingchart.exec(this.props.chartId, 'destroy'); //kill the chart
        }
    }

    pickNextColor(index) {
        return this.viridisColors[index];
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

    componentDidMount() {
        this.zingchart = window.zingchart;
        this.moment = window.moment;
        this.axios = window.axios;
        this.drawChart();
    }
}

export default PatientChart;
