import React from 'react';
// -------------------------------------------------
  const medications=[
  {
      "end_date": "1860-05-15",
      "start_date": "1859-07-23",
      "patient": "KCEPT318AXY",
      "medication": "Sorafenib",
      "status": "released",
      "uuid": "562def00-3729-4c2d-842c-dd291c467177"
  },
  {
      "end_date": "1857-03-25",
      "start_date": "1856-03-03",
      "patient": "KCEPT708IJT",
      "medication": "Everolimus",
      "status": "released",
      "uuid": "8ea48080-b179-4d41-8c65-9c42d2acd452"
  },
  {
      "end_date": "1856-07-19",
      "start_date": "1855-09-05",
      "patient": "KCEPT708IJT",
      "medication": "Sunitinib",
      "status": "released",
      "uuid": "8eb8f472-7cf2-442a-bcfa-b321a1791c3a"
  }]

class MedicationChart extends React.Component {
    constructor(props) {
        super(props);
        this.myConfig = {};
        this.Data = this.props.data;
        this.filterData=[];
        this.dateRange=[];
        this.minDate=0;//unix time seconds
        this.maxDate=0;//unix time seconds
    }
    render(){
        return (
            <div className="flex-container" >
                <div className="chart-main" >
                    <div id={this.props.chartId}  >
                    </div>
                </div>
            </div>
        )
    }
    filterData(){
        //this.data=this.props.data;
        console.log(this.data);
        if(this.data){
            this.dateRange=this.data.map(i=>{return [i.start_date,i.end_date]}).flat().sort();
            this.minDate=this.parseTime(dateRange[0]);//change to unix time(seconds)
            this.maxDate=this.parseTime(dateRange[length-1]);//change to unix time(seconds)
            console.log(this.minDate,this.maxDate);
            this.filterData=this.data.map(i=>{
                return {
                    start: i.start_date,
                    end: i.end_date,
                    drug: i.medication
                }
            });
            console.log(filterData);
        }
    }
//  [ { startDate: '1859-07-23',
//  endDate: '1860-05-15',
//  drug: 'Sorafenib' },
// { startDate: '1856-03-03',
//  endDate: '1857-03-25',
//  drug: 'Everolimus' },
// { startDate: '1855-09-05',
//  endDate: '1856-07-19',
//  drug: 'Sunitinib' } ]
    transferData(arr){
        var drugNames = [];
        var series=[];
        var scaleYIndex=0;
        //return unix time(seconds as unit) of input date
        for(var i = 0; i < arr.length; i++){
            arr[i].start = this.parseTime(arr[i].start);
            arr[i].end = this.parseTime(arr[i].end);

            var treatDuration= {
                values : [[arr[i].start, scaleYIndex], [arr[i].end, scaleYIndex]],
                lineColor : "#29A2CC",
                tooltip : {
                  text : arr[i].drug 
                },
                "data-dragging" : true,
            };
                series.push(treatDuration);
                  
                drugNames[scaleYIndex -1] = "";
                drugNames[scaleYIndex] = arr[i].drug;
                scaleYIndex += 2;
        }
        return series;
    }
    drawChart(){
        this.myConfig = {
            type: "line", 
            theme : 'light',
            plot :{
                lineWidth : 1,
                marker : {
                  visible : false
                },
            },
            globals : {
                shadow : false
            },
            plotarea : {
                maskTolerance : 80,
                marginTop : "dynamic",
                marginBottom : "50",
                marginLeft : "dynamic",
                marginRight : "dynamic",
            },
            scaleX : {
                zooming : true,
                placement : "opposite",
                minValue : this.minDate,
                maxValue: this.maxDate,
                step : "day",
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
                  text : "%m/%d/%y"
                }
            },
            scaleY : {
                itemsOverlap : true,
                labels : drugNames,
                offset : 25,
                mirrored : true,
                guide : {
                  visible : true,
                  lineWidth : 1,
                  lineStyle : "solid",
                  rules : [
                    {
                      rule : "%v % 2 === 0",
                      visible : false
                    }
                  ]
                },
                minorTicks : 1,
                minorTick : {
                  visible : false
                },
                tick : {
                  visible : false
                }
            },
            series : this.transferData(this.filterData)
        };
        calculateLineWidth(myConfig);
        function calculateLineWidth(dataset){
            var chart = document.getElementById('myChart');
            var data = zingchart.exec('myChart', 'getdata');
            var width = (chart.clientHeight-20) / dataset.series.length;
            dataset.plot.lineWidth = Math.floor(width);
            
            dataset.plot.lineWidth = Math.min(dataset.plot.lineWidth , 50);
        }
        
        window.addEventListener('resize', function(){
          calculateLineWidth(myConfig);
          zingchart.resize = function(p){
            zingchart.exec(this.props.chartId, 'setdata', {
              data : myConfig
            });
          };
        });
        let chart = {
          id: this.props.chartId,
          data: this.myConfig,
          width: '100%'
        }
       chart.height = scaleYIndex * 75;
       this.zingchart.render(chart);
    }
    parseTime(dateString) {
      return this.moment(dateString).unix() * 1000;
    }
    componentDidMount() {
      this.zingchart = window.zingchart;
      this.moment = window.moment;
      this.filterData();
      this.transferData();
      this.drawChart();
      this.parseTime();
    }
}
export default MedicationChart;
