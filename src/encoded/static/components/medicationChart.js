/* eslint-disable linebreak-style */
import React from 'react';

class MedicationChart extends React.Component {
  constructor(props) {
    super(props);
    this.myConfig = {
      "utc": true,
      "plotarea": {
        "adjust-layout": true
      }

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
  }
  render() {
    return (
      <div className="flex-container" >
        <div className="chart-main" >
          <div id={this.props.chartId} />
        </div>
      </div>
    );
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
        values: [[this.filterData[i].start, this.scaleYIndex], [this.filterData[i].end, this.scaleYIndex]],
        lineColor: '#29A2CC',
        marker: {
          visible: false
        },
        tooltip: {
          text: 'MedName:' + this.filterData[i].id + '<br> Start date:' + this.unixToDate(this.filterData[i].start) + '<br> End date:' + this.unixToDate(this.filterData[i].end),

        },
        'data-dragging': true,
      };
      this.series.push(this.treatRange);
      this.drugNames[this.scaleYIndex] = this.filterData[i].id;
      this.scaleYIndex += 1;
    }
    this.diagnosisDate = this.minDate - 6000 * 60 * 24 * 30;// hard code diagnosisDate with one month before.Should be replaced with a real one, set with milliseconds.
    this.deceasedDate = this.maxDate + 6000 * 60 * 24 * 30;// hare code diseasedDate with one month after, set with milliseconds.
    this.drugNames[0] = "diagnosisDate";// Set first item to 'diagnosisdate'
    this.drugNames[this.scaleYIndex] = "deceasedDate";// Set last one to 'deceasedDate'.

    let diagnosisMarker = {
      type: 'scatter',
      values: [[this.diagnosisDate, 0]],
      marker: {
        type: 'triangle',
        angle: 90,
        backgroundColor: 'none',
        borderColor: '#D31E1E',
        borderWidth: '2px',
        size: '5px'
      },
      tooltip: {
        text: "Diagnosis date: " + this.unixToDate(this.diagnosisDate),
        'background-color': '#498ead'
      },
    }
    let deceasedMarker = {
      type: 'scatter',
      values: [[this.deceasedDate, this.scaleYIndex]],
      marker: {
        type: 'triangle',
        angle: -90,
        backgroundColor: 'none',
        borderColor: '#D31E1E',
        borderWidth: '2px',
        size: '5px'
      },
      tooltip: {
        text: "Deceased date:"+this.unixToDate(this.deceasedDate),
        'background-color': '#498ead'
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
      type: "mixed",
      theme: 'light',
      plot: {
        alpha: 0.7,
        lineWidth: 20,

      },
      globals: {
        shadow: false
      },
      plotarea: {
        maskTolerance: 80,
        marginTop: "dynamic",
        marginBottom: "50",
        marginLeft: "dynamic",
        marginRight: "50",
        backgroundColor: "#cde5fa",
        alpha: 0.3
      },
      scaleX: {
        zooming: true,
        placement: "opposite",
        minValue: this.diagnosisDate,
        maxValue: this.deceasedDate,
        step: "month",
        guide: {
          lineWidth: "1px"
        },
        tick: {
          visible: false
        },
        transform: {
          type: "date",
          text: "%M-%d-%Y"
        }
      },
      scaleY: {
        itemsOverlap: true,
        labels: this.drugNames,
        offset: 25,
        mirrored: true,
        maxValue: this.scaleYIndex,
        step: 1,
        guide: {
          visible: true,
          lineWidth: 1,
          lineStyle: "solid",
        }
      },
      series: this.series,
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
