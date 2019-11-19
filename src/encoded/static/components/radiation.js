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
    filterData(dataPoint, ganttData){
      for (let i = 0; i < ganttData.length; i++) {
        if (ganttData[i].id === dataPoint.id && ganttData[i].start === dataPoint.start) {
            ganttData[i].numberOfSite++;
            //compare DosagePerFraction
            ganttData[i].maxDosagePerFraction = Math.max(ganttData[i].maxDosagePerFraction, dataPoint.maxDosagePerFraction);
            ganttData[i].minDosagePerFraction = Math.min(ganttData[i].minDosagePerFraction, dataPoint.minDosagePerFraction);

            //compare end date
            if (ganttData[i].end != ganttData[i].end) {
              ganttData[i].end = Math.max(ganttData[i].end,dataPoint.end);
              ganttData[i].endDate = new Date(ganttData[i].end - 60000*60*24);
            }


        }
      }
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
        let endDateUnix = this.parseTime(this.radiationAppointments[i].end_date) + 60000*60*24;
        let dataPoint = {
          id: this.radiationAppointments[i].site_general,
          start: startDateUnix,
          startDate: this.radiationAppointments[i].start_date,
          end: endDateUnix,
          endDate: this.radiationAppointments[i].end_date,
          numberOfSite: 1,
          maxDosagePerFraction: this.radiationAppointments[i].dose_cgy_actual/this.radiationAppointments[i].fractions_actual,
          minDosagePerFraction: this.radiationAppointments[i].dose_cgy_actual/this.radiationAppointments[i].fractions_actual
        };
        if (!this.containsObject(dataPoint, ganttData)) {
          ganttData.push(dataPoint);
        } else{
          this.filterData(dataPoint, ganttData);
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
          "data-max": ganttData[i].maxDosagePerFraction,
          "data-min": ganttData[i].minDosagePerFraction,
          values : [[ganttData[i].start, projectNames.indexOf(ganttData[i].id) ], [ganttData[i].end, projectNames.indexOf(ganttData[i].id) ]],
          lineColor : '#29A2CC',
          marker : {
 	         visible : false
 	        },
          tooltip : {
            rules: [
              {
                rule: "%data-max === %data-min",
                text : "Site: " + ganttData[i].id  + "<br>Number of lesions: "+ ganttData[i].numberOfSite +"<br>Dosage per fraction: " + ganttData[i].minDosagePerFraction + "<br>Start date: " + ganttData[i].startDate +  "<br>End date: " + ganttData[i].endDate

              },
              {
                rule: "%data-max > %data-min",
                text : "Site: " + ganttData[i].id  + "<br>Number of lesions: "+ ganttData[i].numberOfSite +"<br>Dosage per fraction: " + ganttData[i].minDosagePerFraction + " - " + ganttData[i].maxDosagePerFraction + "<br>Start date: " + ganttData[i].startDate +  "<br>End date: " + ganttData[i].endDate

              }
            ]
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
 	          text : "%M-%d-%Y"
 	        }
      	},
 	      scaleY : {
 	        itemsOverlap : true,
          labels : projectNames,
 	        offset : 25,
 	        mirrored : true,
          maxValue: scaleYIndex,
          step: 1,
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
