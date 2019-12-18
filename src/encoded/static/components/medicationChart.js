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
              <button type="button" onClick={this.zoomIn} title="Zoom in" aria-label="Zoom in"><FontAwesomeIcon icon={faSearchPlus} background-color="#cde5fa" size="2x" /></button>
            </div>
            <div className="mb-2">
              <button type="button" onClick={this.zoomOut} title="Zoom out" aria-label="Zoom out"><FontAwesomeIcon icon={faSearchMinus} size="2x" /></button>
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
      let dateRangeSort =[...new Set(([].concat(...this.dateRange)).sort())] ;
      console.log("dateRangeSort",dateRangeSort)
      let data1=[];
      let sortedData=[];
      // let startDateArray = this.props.data.map(i => (i.start_date)).sort();
      // console.log(startDateArray);
      for (let j = 0; j < dateRangeSort.length; j++) {
        
        let dataPoints = this.props.data.filter(i => { return i.start_date === dateRangeSort[j] });
        data1.push(dataPoints);
        sortedData=[...new Set([].concat(...data1))];
        
      }
      console.log("data1",data1);
      console.log("sortedData",sortedData);
      this.minDate = Date.parse(dateRangeSort[0]);// change time to milliseconds
      this.maxDate = Date.parse(dateRangeSort[dateRangeSort.length - 1]);// change time to milliseconds
      //sorting data according to startDate:
     
      

      
      //   for (let j = 0; j < allDates.length; j++) {
      //     let currentDate = allDates[j];
      //     let dataPoints = filteredData.filter(i => { return i.date === currentDate });
      //     if (dataPoints.length > 0) {
      //         values.push([allDatesUnix[j], dataPoints[0].value]);
      //     }
      //     else {
      //         values.push([allDatesUnix[j], null]);
      //     }
      // }

      this.filterData = sortedData.map(i => ({
        start: i.start_date,
        end: i.end_date,
        id: i.name,
      }));
      
      console.log("filterData",this.filterData);
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
          lineWidth: 15,
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
    this.drugNames[0] = "";// Set first item for 'diagnosis date', not show in YAxis
    this.drugNames[this.drugNames.length] = "";//set last one for 'deceaced date', not show in YAxis.


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
        'background-color': 'green',
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
        'background-color': 'green',
      },
    }

    this.series.push(diagnosisMarker);
    this.series.push(deceasedMarker);

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
            backgroundColor: "#cde5fa",//"#cde5fa"  blue
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
