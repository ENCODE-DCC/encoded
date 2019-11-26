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
        this.data = this.props.data;
        this.filterData = [];
        this.dateRange = [];
        this.minDate = 0;// unix time seconds
        this.maxDate = 0;// unix time seconds
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
  //   parseTime(dateString) {
  //     return this.moment(dateString).unix() * 1000;// change to milliseconds;
  // }
    filterDataFun() {
        // this.data=this.props.data;
        console.log(this.data);
        if (this.data) {
            this.dateRange = this.data.map(i => ([i.start_date, i.end_date]));
            let dateRangeSort = ([].concat(...this.dateRange)).sort();
            console.log(this.dateRange);
            console.log(dateRangeSort);
            //this.minDate = Math.min(this.parseTime(dateRangeSort[0]));// change to unix time(milliseconds)
            //this.maxDate = Math.max(this.parseTime(dateRangeSort[dateRangeSort.length-1]));// change to unix time(milliseconds)
            // this.maxDate = this.parseTime(dateRangeSort[length - 1]);// change to unix time(seconds)
            this.minDate = Date.parse(dateRangeSort[0]) ;// change to unix time(milliseconds)
            this.maxDate = Date.parse(dateRangeSort[dateRangeSort.length-1]);// change to unix time(milliseconds)
            console.log(this.minDate);
            console.log(this.maxDate);
            this.filterData = this.data.map(i => ({
                start: i.start_date,
                end: i.end_date,
                id: i.name,
            }));
            console.log(this.filterData);
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

    transferDataFun() {
        // return unix time(seconds as unit) of input date
        this.series = [];
        this.scaleYIndex = 0;
        for (let i = 0; i < this.filterData.length; i++) {
           //this.filterData[i].start = this.parseTime(this.filterData[i].start);
            //this.filterData[i].end = this.parseTime(this.filterData[i].end);
            this.filterData[i].start = Date.parse(this.filterData[i].start);
            this.filterData[i].end = Date.parse(this.filterData[i].end);

                this.treatRange = {
                  values: [[this.filterData[i].start, this.scaleYIndex], [this.filterData[i].end, this.scaleYIndex]],
                  //values: [[this.filterData[i].start, this.drugNames.indexOf(this.filterData[i].id)], [this.filterData[i].end, this.drugNames.indexOf(this.filterData[i].id)]],
                    lineColor: '#29A2CC',
                    marker : {
                      visible : false
                     },
                    tooltip: {
                        // text: this.filterData[i].id,
                        text: 'MedName:'+this.filterData[i].id+'<br> Start date:'+this.unixToDate(this.filterData[i].start) +'<br> End date:' +this.unixToDate(this.filterData[i].end),
                    },
                    'data-dragging': true,
                };
                this.series.push(this.treatRange);
            
            //this.drugNames[this.scaleYIndex - 1] = '';
            this.drugNames[this.scaleYIndex] = this.filterData[i].id;
            this.scaleYIndex += 1;
            console.log(this.scaleYIndex);
        }
        //this.drugNames[-1] = 'diagnosis date';
        console.log(this.drugNames);
        //this.drugNames.pop();
        //console.log(this.drugNames);
        console.log(this.series);
        return this.series;
    }
    unixToDate(unix){
        var date = new Date(unix);
        return (date.getMonth()+1) + "/" + date.getDate() + "/" + date.getFullYear();
    }
    drawChart() {
      
       this.myConfig = {
            type: "line",
            theme: 'light',
            plot: {
              lineWidth: 20,
              marker: {
                visible: false
              },
            },
            globals: {
              shadow: false
            },
            plotarea: {
              maskTolerance: 80,
              marginTop: "dynamic",
              marginBottom: "50",
              marginLeft: "dynamic",
              marginRight: "dynamic",
            },
            scaleX: {
              zooming: true,
              placement: "opposite",
              minValue: this.minDate,
              maxValue: this.maxDate,
              step: 'year',
            //   step: "day",
              item: {
                //visible : false
              },
              guide: {
                lineWidth: "1px"
              },
              tick: {
                visible: false
              },
              transform: {
                type: "date",
                text: "%m-%d-%Y"
              }
            },
            scaleY: {
              labels: this.drugNames,
              offset: 25,
              mirrored: true,
              step: 1,
              guide: {
                visible: true,
                lineWidth: 1,
                lineStyle: "solid",
              },
            },
            series: this.series,
            //series: createTimeline(ganttData2)
          };
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
        this.transferDataFun();
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
