/* eslint-disable linebreak-style */
import React from 'react';
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSearchPlus, faUserCircle } from "@fortawesome/free-solid-svg-icons";
import { faSearchMinus } from "@fortawesome/free-solid-svg-icons";

class MedicationChart extends React.Component {
  constructor(props) {
    super(props);
    this.myConfig = {
      "utc": true,
      "plotarea": {
        "adjust-layout": true
      },
      graphset: [],
    };
    this.filterData = [];
    this.dateRange = [];
    this.minDate = 0;
    this.maxDate = 0;
    this.diagnosisDate = 0;
    this.deceasedDate = 0;
    this.chart = {};
    this.treatRange = {};
    this.drugNames = [];
    this.series = [];
    this.scaleYIndex = 0;
    this.zoomIn = this.zoomIn.bind(this);
    this.zoomOut = this.zoomOut.bind(this);

  }
  render() {
    return (
      <div className="flex-container" >
        <div className="chart-menu" >
          <div className="chartboxes pt-2" >
            <div className="mb-2">
              <button type="button" className="btn btn btn-danger" onClick={this.zoomIn} title="Zoom in" aria-label="Zoom in"><FontAwesomeIcon icon={faSearchPlus} size="2x" /></button>
            </div>
            <div className="mb-2">
              <button type="button" className="btn btn-success" onClick={this.zoomOut} title="Zoom out" aria-label="Zoom out"><FontAwesomeIcon icon={faSearchMinus} size="2x" /></button>
            </div>
          </div>
        </div>
        <div className="chart-main" >
          <div id={this.props.chartId} ></div>
        </div>
      </div>

    );
  }
  zoomIn() {
    this.zingchart.exec(this.props.chartId, "zoomin", { zoomx: true, zoomy: false });
  }

  zoomOut() {
    this.zingchart.exec(this.props.chartId, "zoomout", { zoomx: true, zoomy: false });

  }
  filterDataFun() {
    if (this.props.data.length > 0) {
      this.dateRange = this.props.data.map(i => ([i.start_date, i.end_date]));
      let dateRangeSort = ([].concat(...this.dateRange)).sort();
      this.minDate = Date.parse(dateRangeSort[0]);// change time to milliseconds
      this.maxDate = Date.parse(dateRangeSort[dateRangeSort.length - 1]);// change time to milliseconds
      this.filterData = this.props.data.map(i => ({
        start: i.start_date,
        end: i.end_date,
        id: i.name,
      }));
    }
  }
  transformDataFun() {
    this.series = [];
    this.scaleYIndex = 1;// leave the first item for diagnosis date. Else will set this.scaleYIndex = 0;
    for (let i = 0; i < this.filterData.length; i++) {
      this.filterData[i].start = Date.parse(this.filterData[i].start);
      this.filterData[i].end = Date.parse(this.filterData[i].end);

      this.treatRange = {
        type: 'line',
        plot: {
          lineWidth: 20,
          marker: {
            visible: false
          },
        },
        scales: "scaleX, scaleY",//set top x-Axis
        values: [[this.filterData[i].start, this.scaleYIndex], [this.filterData[i].end, this.scaleYIndex]],
        lineColor: '#29A2CC',
        marker: {
          visible: false
        },
        tooltip: {
          text: 'MedName:' + this.filterData[i].id + '<br> Start date:' + this.unixToDate(this.filterData[i].start) + '<br> End date:' + this.unixToDate(this.filterData[i].end),

        },
        "data-line-index": this.scaleYIndex,
        'data-dragging': true,
      };
      this.series.push(this.treatRange);
      this.drugNames[this.scaleYIndex] = this.filterData[i].id;
      this.scaleYIndex += 1;
    }
    this.diagnosisDate = this.minDate - 6000 * 60 * 24 * 30;// hard code diagnosisDate with one month before.Should be replaced with a real one, set with milliseconds.
    this.deceasedDate = this.maxDate + 6000 * 60 * 24 * 30;// hare code diseasedDate with one month after, set with milliseconds.
    this.drugNames[0] = "";//"diagnosisDate";// Set first item to 'diagnosisdate'
    //this.drugNames[(this.scaleYIndex)] = "";// "deceasedDate";// Set last one to 'deceasedDate'.
    this.drugNames[this.drugNames.length] = "";
    console.log("drugName", this.drugNames);
    console.log("YIndex", this.scaleYIndex);
    console.log("series1", this.series);
    //console.log("series1", this.treatRange[values]);


    let diagnosisMarker = {
      type: 'scatter',
      values: [[this.diagnosisDate, 0]],
      scales: "scaleX2, scaleY",//set bottom x-Axis
      marker: {
        type: 'triangle',
        angle: 90,
        backgroundColor: 'none',
        borderColor: '#D31E1E',
        borderWidth: '2px',
        size: '5px',
      },
      tooltip: {
        text: "Diagnosis date: " + this.unixToDate(this.diagnosisDate),
        'background-color': 'green',//'#8BC34A' // '#498ead'
      },
    }
    let deceasedMarker = {
      type: 'scatter',
      scales: "scaleX2, scaleY",//set bottom x-Axis
      values: [[this.deceasedDate, this.scaleYIndex]],
      marker: {
        type: 'triangle',
        angle: -90,
        backgroundColor: 'none',
        borderColor: '#D31E1E',
        borderWidth: '2px',
        size: '5px',
      },
      "data-deceased-index": this.drugNames.length - 1,
      tooltip: {
        text: "Deceased date:" + this.unixToDate(this.deceasedDate),
        'background-color': 'green',//'#8BC34A'//'#498ead'
      },
    }

    this.series.push(diagnosisMarker);
    this.series.push(deceasedMarker);
    console.log("series2", this.series);
    console.log("series2", this.series.values);

    return this.series;
  }
  unixToDate(unix) {
    var date = new Date(unix);
    return (date.getMonth() + 1) + "/" + date.getDate() + "/" + date.getFullYear();
  }
  drawChart() {
    this.myConfig = {
      graphset: [
        {
          type: "mixed",
          theme: 'light',
          plot: {
            alpha: 0.7,
            lineWidth: 20,
            'value-box': {
              rules: [
                {
                  rule: "%v==0",
                  placement: "right",
                  text: "Diagnosis Date",
                  fontSize: "13px",
                  fontFamily: "Georgia",
                  fontWeight: "bold",
                  fontColor: "black",
                },
                {
                  rule: "%v==%data-deceased-index",
                  placement: "left",
                  text: "Deceased Date",
                  fontSize: "13px",
                  fontFamily: "Georgia",
                  fontWeight: "bold",
                  fontColor: "black",
                },
                {
                  rule: "%v==%data-line-index",
                  visible: "false",
                }
              ]
            }
          },
          globals: {
            shadow: false,
          },
          zoom: {
            shared: true
          },

          plotarea: {
            "adjust-layout": true,
            marginTop: "dynamic",
            marginBottom: "50",
            marginLeft: "dynamic",
            marginRight: "50",
            backgroundColor: "#cde5fa",
            alpha: 0.3
          },
          scaleX: {
            zooming: true,
            placement: "default",
            minValue: this.diagnosisDate - 6000 * 60 * 24 * 180,
            maxValue: this.deceasedDate + 6000 * 60 * 24 * 180,
            step: 'day',
            guide: {
              lineWidth: "1px"
            },
            tick: {
              visible: true, 
            },
            transform: {
              type: "date",
              text: "%M-%d-%Y"
            }
          },
          "scroll-x": {
            // "bar": {
            //   "background-color": "#DCEDC8",
            //   "alpha": 0.5
            // },
            // "handle": {
            //   "background-color": "#8BC34A"
            // }
          },
          scaleX2: {
            zooming: true,
            placement: "opposite",
            minValue: this.diagnosisDate - 6000 * 60 * 24 * 180,
            maxValue: this.deceasedDate + 6000 * 60 * 24 * 180,
            step: 'day',
            guide: {
              lineWidth: "1px"
            },
            tick: {
              visible: true,
            },
            transform: {
              type: "date",
              text: "%M-%d-%Y"
            },
          },

          scaleY: {
            itemsOverlap: true,
            labels: this.drugNames,
            offset: 25,
            mirrored: true,
            minValue: 0,
            maxValue: this.scaleYIndex,
            step: 1,
            guide: {
              visible: true,
              lineWidth: 1,
              lineStyle: "solid",
            },
            tick: {
              visible: false,
            },
          },

          series: this.series,
        }
      ]
    }
    this.chart = {
      id: this.props.chartId,
      data: this.myConfig,
      width: '100%',
    };
    this.chart.height = this.scaleYIndex * 75;
    this.zingchart.render(this.chart);
  }

  componentDidMount() {
    this.zingchart = window.zingchart;
    this.moment = window.moment;
    this.filterDataFun();
    this.transformDataFun();
    this.drawChart();
  }
}
export default MedicationChart;
// ---------------------------------------------------
// http://localhost:6543/patients/KCEPT294KIZ/  5 drugs
// http://localhost:6543/patients/KCEPT021XWS/ 1 drug
// http://localhost:6543/patients/KCEPT708IJT/ 3 drugs