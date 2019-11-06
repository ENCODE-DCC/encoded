import React from 'react';

class Radiation extends React.Component {
    constructor(props) {
        super(props);

        this.myConfig = {
            "utc": true,
            "plotarea": {
                "adjust-layout": true
            }

        };

        this.radiationAppointments = this.props.data;

    }

    containsObject(obj, list) {
      for (let i = 0; i < list.length; i++) {
        if (list[i].id === obj.id && list[i].start === obj.start) {
            return true;
        }
      }
      return false;
    }

    render() {
        return (
          <div>
            <div className="flex-container" >

                <div className="chart-main" >
                    <div id={this.props.chartId}  >

                    </div>
                </div>
            </div>
        </div>)

    }

    drawChart() {


      let datesUnix = [];

      let ganttData = [];

      for (let i = 0; i < this.radiationAppointments.length; i++) {
        let startDateUnix =  this.parseTime(this.radiationAppointments[i].start_date);
        let endDateUnix = startDateUnix + this.radiationAppointments[i].fractions_actual *60000*60*24;
        let dataPoint = {
          id: this.radiationAppointments[i].site_general,
          start: startDateUnix,
          end: endDateUnix
        };
        if (!this.containsObject(dataPoint, ganttData)) {
          ganttData.push(dataPoint);
        }
        datesUnix.push(startDateUnix);
      }

      let minDateUnix = Math.min(...datesUnix) - 60000*60*24*30;
      let maxDateUnix = Math.max(...datesUnix) + 60000*60*24*30;


      var projectNames = [];
      var seriesData = [];
    	var scaleYIndex = 2;

      for(var i = 0; i < ganttData.length; i++){

        if (projectNames.indexOf(ganttData[i].id) == -1) {
          projectNames[scaleYIndex -1] = "";

          projectNames[scaleYIndex] = ganttData[i].id;

          scaleYIndex += 2;
        }

      }
      projectNames[0] = "Diagnosis Date";
      projectNames[scaleYIndex - 1] = "";
      projectNames[scaleYIndex] = "Deceased Date";


      for(var i = 0; i < ganttData.length; i++){

        seriesData.push({
          type: 'line',
          values : [[ganttData[i].start, projectNames.indexOf(ganttData[i].id) ], [ganttData[i].end, projectNames.indexOf(ganttData[i].id) ]],
          lineColor : '#29A2CC',
          marker : {
 	         visible : false
 	        },
          tooltip : {
            text : "Radiation site: " + ganttData[i].id + "<br> Start date: %kl"
          },
        })

      }


      let diagnosisDate = minDateUnix + 60000*60*24;
      let deceasedDate = maxDateUnix - 60000*60*24;
      seriesData.push(
        {
          type: 'scatter',
          values: [[diagnosisDate, 0]],
          marker: {
            type: 'triangle',
            angle: 90,
            backgroundColor: 'none',
            borderColor: '#D31E1E',
            borderWidth: '3px',
            size: '10px'
          },
          tooltip : {
            text : "Diagnosis date: %kl"
          },
        }
      );
      seriesData.push(
        {
          type: 'scatter',
          values: [[deceasedDate, scaleYIndex]],
          marker: {
            type: 'triangle',
            angle: -90,
            backgroundColor: 'none',
            borderColor: '#D31E1E',
            borderWidth: '3px',
            size: '10px'
          },
          tooltip : {
            text : "Deceased date: %kl"
          },
        }
      );


      this.myConfig = {
 	      type: "mixed",
 	      theme : 'light',
       	plot :{
          alpha:0.7,
 	        lineWidth : 40,

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
          minValue : minDateUnix,
          maxValue: maxDateUnix,
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
 	          text : "%M-%d-%y"
 	        }
      	},
 	      scaleY : {
 	        itemsOverlap : true,
          labels : projectNames,
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
        series : seriesData
      };


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
        this.drawChart();
    }
}

export default Radiation;
