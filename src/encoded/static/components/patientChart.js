import React from 'react';
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSearchPlus } from "@fortawesome/free-solid-svg-icons";
import { faSearchMinus } from "@fortawesome/free-solid-svg-icons";

class PatientChart extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            checkboxes: []
        };
        this.myConfig = {
            "utc": true,
            "plotarea": {
                "adjust-layout": true
            },
            graphset: []
        };
        this.featuresChecked = {};
        this.features = Object.keys(this.props.data).sort();
        if (this.features.indexOf("BP_SYS") != -1 && this.features.indexOf("BP_DIAS") != -1){
          let indexSystolic = this.features.indexOf("BP_SYS");
          let indexDiastolic = this.features.indexOf("BP_DIAS");
          this.features[indexSystolic] = "BP_DIAS";
          this.features[indexDiastolic] = "BP_SYS";
        }
        this.numOfFeaturesChecked = this.features.length;
        this.data = {};
        this.charts = {};
        this.currentCharts = {};
        this.zoomIn = this.zoomIn.bind(this);
        this.zoomOut = this.zoomOut.bind(this);
    }
    render() {
        return (<div>
            <div className="flex-container" >
                <div className="chart-menu" >
                    <h4>Show/Hide Results</h4>
                    <div className="chart-checkboxes pb-2"> {this.state.checkboxes}</div>
                    {/* zoom in and out buttons */}
                    <div className="pt-2" >
                        <button className="mr-2"  onClick={this.zoomIn} title="Zoom in" aria-label="Zoom in"><FontAwesomeIcon icon={faSearchPlus} size="2x"/></button>
                        <button onClick={this.zoomOut} title="Zoom out" aria-label="Zoom out"><FontAwesomeIcon icon={faSearchMinus} size="2x"/></button>
                    </div>
                </div>
                <div className="chart-main" >
                    <div id={this.props.chartId} >

                    </div>
                </div>
            </div>
        </div>)

    }

    renderChart() {
        this.zingchart.render({
            id: this.props.chartId,
            data: this.myConfig,
            height: this.numOfFeaturesChecked * 180,
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

        for (let i = 0; i < this.features.length; i++) {
            let feature = this.features[i];
            this.featuresChecked[feature] = { checked: true, color: "#003767" };
            var styles = {
                color: "#003767"
            }
            tempCheckboxes.push(<div key={i}><input type="checkbox" id={feature} value={feature} name={feature} defaultChecked="checked" onChange={(e) => {this.handleCheckboxChange(e, this)}} />
                <label style={styles} htmlFor={feature}>{feature}</label></div>)
        }
        this.setState({ checkboxes: tempCheckboxes });
    }

    drawChart() {

        this.data = this.props.data;
        this.createCheckboxes();
        this.initChart();
    }

    parseTime(dateString) {
        return this.moment(dateString).unix() * 1000;
    }
    handleCheckboxChange(event) {
        let checked = event.currentTarget.checked;
        let value = event.currentTarget.value;
        this.featuresChecked[value]["checked"] = checked;
        if (event.currentTarget.checked) {
          this.numOfFeaturesChecked++;
        }else {
          this.numOfFeaturesChecked--;
        }
        this.updateChart(value, checked);

    }
    updateChart(value, checked) {
      if(checked) {
        let chart = this.charts[value];
        this.currentCharts[value] = chart;
      } else{
        delete this.currentCharts[value];
      }
      this.myConfig.graphset = [];
      this.myConfig.layout = this.numOfFeaturesChecked  + "x1";
      let features = Object.keys(this.currentCharts).sort();
      if (features.indexOf("BP_SYS") != -1 && features.indexOf("BP_DIAS") != -1){
        let indexSystolic = features.indexOf("BP_SYS");
        let indexDiastolic = features.indexOf("BP_DIAS");
        features[indexSystolic] = "BP_DIAS";
        features[indexDiastolic] = "BP_SYS";
      }
      for (let i = 0; i < this.numOfFeaturesChecked; i++) {
        this.myConfig.graphset.push(this.currentCharts[features[i]]);
      }
      if (this.myConfig.graphset.length > 0) {

        this.zingchart.exec(this.props.chartId, 'destroy'); //kill the chart
        this.renderChart();
      } else {
        this.zingchart.exec(this.props.chartId, 'destroy'); //kill the chart
      }
    }

    initChart() {
        this.myConfig.graphset = [];

        this.myConfig.layout = this.numOfFeaturesChecked  + "x1";

        let allDates = [];
        for (let i = 0; i < this.features.length; i++) {
            allDates = allDates.concat(this.data[this.features[i]].map(i => {return i.date;}));
        };
        allDates = [...new Set(allDates)]
        allDates.sort(function(a,b) {
            a = a.split('-').join('');
            b = b.split('-').join('');
            return a > b ? 1 : a < b ? -1 : 0;

        });
        let allDatesUnix = allDates.map(i => { return this.parseTime(i) });
        let startDate = Math.min(...allDatesUnix);
        let endDate = Math.max(...allDatesUnix) + 1000*60*60*24;

        for (let i = 0; i < this.features.length; i++) {
            let feature = this.features[i];
            let filteredData = this.data[this.features[i]];
            let filteredDates = this.data[this.features[i]].map(i => {return i.date;});
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
            let highs = [];
            let lows = []
            for (let i = 0; i < rangeValues.length; i++) {
              if (rangeValues[i][1][0] === undefined && rangeValues[i][1][1] === undefined) {
                lows.push(-1);
                highs.push(-1);
              } else {
                lows.push(rangeValues[i][1][0]);
                highs.push(rangeValues[i][1][1])

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
                plot: {
                    marker: {

                        size: 2,
                        borderColor: "white",
                        borderWidth: 0,
                        backgroundColor: "#003767"
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
                    //"data-range": rangeDataForDisplay,
                    "data-highs": highs,
                    "data-lows": lows,
                    // "data-day": allDates, //uncomment this to use dates in label
                    lineWidth: 1, /* in pixels */
                    lineColor: "#003767",
                    tooltip: {
                        visible: true,
                        rules: [
                          {
                            rule: "%data-highs === -1 ",
                            text: feature + ": %v " + unit + "<br> Date: %kl"
                          },
                          {
                            rule: "%data-lows === -1",
                            text: feature + ": %v " + unit + "<br> Date: %kl"
                          }
                        ],
                        text: feature + ": %v " + unit + "<br> Date: %kl <br>Reference range: %data-lows - %data-highs"
                    }
                  },
                  {
                    type: 'range',
                    values: rangeValues,
                    backgroundColor: '#cde5fa',
                    lineColor: 'none',
                    tooltip: {
                        visible: false,
                    }
                  }
                ],
                scaleX: {
                  transform: {
                    type: "date",
                    all: "%M-%d-%Y"
                  },
                    minValue: startDate,
                    maxValue: endDate,
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
                    "margin-right": "50px",
                    "margin-bottom": "50px"
                },
            };
            this.myConfig.graphset.push(chart);
            this.charts[feature] = chart;
            this.currentCharts[feature] = chart;
        }

        this.renderChart();

    }

    componentDidMount() {
        this.zingchart = window.zingchart;
        this.moment = window.moment;
        //this.axios = window.axios;
        this.drawChart();
    }
}

export default PatientChart;
