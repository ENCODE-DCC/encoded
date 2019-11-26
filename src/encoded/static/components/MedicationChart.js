/* eslint-disable linebreak-style */
import React from 'react';
// -------------------------------------------------
// const medications=[
// {
//     "end_date": "1860-05-15",
//     "start_date": "1859-07-23",
//     "patient": "KCEPT318AXY",
//     "medication": "Sorafenib",
//     "status": "released",
//     "uuid": "562def00-3729-4c2d-842c-dd291c467177"
// },
// {
//     "end_date": "1857-03-25",
//     "start_date": "1856-03-03",
//     "patient": "KCEPT708IJT",
//     "medication": "Everolimus",
//     "status": "released",
//     "uuid": "8ea48080-b179-4d41-8c65-9c42d2acd452"
// },
// {
//     "end_date": "1856-07-19",
//     "start_date": "1855-09-05",
//     "patient": "KCEPT708IJT",
//     "medication": "Sunitinib",
//     "status": "released",
//     "uuid": "8eb8f472-7cf2-442a-bcfa-b321a1791c3a"
// }]

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
    this.minDate = 0;// unix time seconds
    this.maxDate = 0;// unix time seconds
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
      this.minDate = Date.parse(dateRangeSort[0]);// change to unix time(milliseconds)
      this.maxDate = Date.parse(dateRangeSort[dateRangeSort.length - 1]);// change to unix time(milliseconds)
      this.filterData = this.props.data.map(i => ({
        start: i.start_date,
        end: i.end_date,
        id: i.name,
      }));
    }
  }
  //  [ { startDate: '1859-07-23',
  //  endDate: '1860-05-15',
  //  id: 'Sorafenib' },
  // { startDate: '1856-03-03',
  //  endDate: '1857-03-25',
  //  id: 'Everolimus' },
  // { startDate: '1855-09-05',
  //  endDate: '1856-07-19',
  //  id: 'Sunitinib' } ]

  transformDataFun() {
    this.series = [];
    this.scaleYIndex = 1;// leave the first for diagnosis date. Else will set this.scaleYIndex = 0;
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
      console.log(this.scaleYIndex);
    }
    this.diagnosisDate = this.minDate - 6000*60*24*30;// hard code diagnosisDate with one day before.Should be replaced with a real one.
    this.deceasedDate = this.maxDate + 6000*60*24*30;// hare code diseasedDate with one day after, set with milliseconds.
    this.drugNames[0] = "diagnosisDate";// Set first one with diagnosis date
    this.drugNames[this.scaleYIndex] = "deceasedDate";// Set last one with diseased date.
    //this.drugNames[-1] = 'diagnosis date';
    console.log(this.drugNames);
    let diagnosisDot = {
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
        text: "Diagnosis date: %kl",
        //'background-color': '#498ead'
      },
    }
    let deceasedDot = {
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
        text: "Deceased date: %kl",
       // 'background-color': '#498ead'
      },
    }

    this.series.push(diagnosisDot);
    this.series.push(deceasedDot);
    //this.drugNames.pop();
    //console.log(this.drugNames);
    console.log(this.series);
    return this.series;
  }
  unixToDate(unix) {
    var date = new Date(unix);
    return (date.getMonth() + 1) + "/" + date.getDate() + "/" + date.getFullYear();
  }
  drawChart() {
    this.myConfig={
      type: "mixed",
      theme : 'light',
      plot :{
       alpha:0.7,
        lineWidth : 20,

     },
      globals : {
        shadow : false
     },
      plotarea : {
        maskTolerance : 80,
        marginTop : "dynamic",
        marginBottom : "50",
        marginLeft : "dynamic",
        marginRight : "50",
       backgroundColor: "#cde5fa",
       alpha:0.3
     },
     scaleX : {
        zooming : true,
        placement : "opposite",
       minValue : this.diagnosisDate,
       maxValue: this.deceasedDate,
       step : "month",
        item : {
        //visible : false
        },
        guide : {
          lineWidth : "1px"
        },
        tick : {
          visible : false
        },
        transform : {
          type : "date",
          text : "%M-%d-%Y"
        }
     },
      scaleY : {
        itemsOverlap : true,
       labels : this.drugNames,
        offset : 25,
        mirrored : true,
       maxValue: this.scaleYIndex,
       step: 1,
        guide : {
          visible : true,
          lineWidth : 1,
          lineStyle : "solid",
        //   rules : [
        //   {
        //     rule : "%v % 2 === 0",
        //     visible : false
        //   }
        //   ]
        // },
        // minorTicks : 1,
        // minorTick : {
        //   visible : false
        // },
        // tick : {
        //   visible : false
        }
     },
     series : this.series,
   }
    // this.myConfig = {
    //   type: "mixed",
    //   theme: 'light',
    //   plot: {
    //     lineWidth: 20,
    //     marker: {
    //       visible: false
    //     },
    //   },
    //   globals: {
    //     shadow: false
    //   },
    //   plotarea: {
    //     maskTolerance: 80,
    //     marginTop: "dynamic",
    //     marginBottom: "50",
    //     marginLeft: "dynamic",
    //     marginRight: "dynamic",
    //   },
    //   scaleX: {
    //     zooming: true,
    //     placement: "opposite",
    //     minValue: this.diagnosisDate,
    //     maxValue: this.deceasedDate,
    //     step: 'year',
    //     //   step: "day",
    //     item: {
    //       //visible : false
    //     },
    //     guide: {
    //       lineWidth: "1px"
    //     },
    //     tick: {
    //       visible: false
    //     },
    //     transform: {
    //       type: "date",
    //       text: "%m-%d-%Y"
    //     }
    //   },
    //   scaleY: {
    //     labels: this.drugNames,
    //     offset: 25,
    //     mirrored: true,
    //     step: 1,
    //     guide: {
    //       visible: true,
    //       lineWidth: 1,
    //       lineStyle: "solid",
    //     },
    //   },
    //   series: this.series,
    //   //series: createTimeline(ganttData2)
    // };
    // this.calculateLineWidth(this.myConfig);
    // this.addEventListener();
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
    // this.parseTime();
    this.unixToDate();
    //     this.calculateLineWidth();
    //     this.addEventListener();
  }
}
export default MedicationChart;
// ---------------------------------------------------------
// http://localhost:6543/patients/KCEPT359MHZ/ one drugs

// http://localhost:6543/patients/KCEPT708IJT/ three drugs
// this.myConfig = {
//     type: 'line',
//     theme: 'light',
//     plot: {
//         lineWidth: 15,
//         marker: {
//             visible: false,
//         },
//     },
//     globals: {
//         shadow: false,
//     },
//     plotarea: {
//         maskTolerance: 80,
//         marginTop: 'dynamic',
//         marginBottom: '50',
//         marginLeft: 'dynamic',
//         marginRight: 'dynamic',
//     },
//     scaleX: {
//         zooming: true,
//         placement: 'opposite',
//         minValue: this.minDate,
//         maxValue: this.maxDate,
//         step: 'year',
//         item: {
//             visible : false,
//         },
//         guide: {
//             lineWidth: '1px',
//         },
//         tick: {
//             visible: false,
//         },
//         transform: {
//             type: 'date',
//             text: '%m-%d-%Y',
//         },
//     },
//     scaleY: {
//         itemsOverlap: true,
//         labels: this.drugNames,
//         offset: 25,
//         mirrored: true,
//         minValue: 0,
//         maxValue: this.drugNames.length-1,
//         step: 1,
//         guide: {
//             visible: true,
//             lineWidth: 1,
//             lineStyle: 'solid',
//             rules: [
//                 {
//                     rule: '%v',
//                     //rule: '%v % 2 === 0',
//                     visible: false,
//                 },
//             ],
//         },
//         // minorTicks: 3,
//         // minorTick: {
//         //     visible: true,
//         // },
//         tick: {
//             visible: false,
//         },
//         //maxTicks: this.scaleYIndex,
//     },
//     // series: this.transferDataFun(this.filterData),
//     series: this.series,
// };
