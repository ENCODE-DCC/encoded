import React from 'react';

class Radiation extends React.Component {
  constructor(props) {
    super(props);

    this.radiationAppointments = this.props.data;
    this.plotlyConfig = {
      displayModeBar: true,     
      displaylogo: false,
      modeBarButtonsToRemove: [
              "sendDataToCloud",
              "editInChartStudio",
              "select2d",
              "lasso2d",
              "hoverClosestCartesian",
              "hoverCompareCartesian",
              "toggleSpikelines",
              "autoScale2d"
      ],
      responsive: true
    };
  }

  containsObject(obj, list) {
    for (let i = 0; i < list.length; i++) {
      if (list[i].id === obj.id && list[i].start === obj.start) {
        return true;
      }
    }
    return false;
  }
  filterData(dataPoint, ganttData) {
    for (let i = 0; i < ganttData.length; i++) {
      if (ganttData[i].id === dataPoint.id && ganttData[i].start === dataPoint.start) {
        ganttData[i].numberOfSite++;
        //compare DosagePerFraction
        ganttData[i].maxDosagePerFraction = Math.max(ganttData[i].maxDosagePerFraction, dataPoint.maxDosagePerFraction);
        ganttData[i].minDosagePerFraction = Math.min(ganttData[i].minDosagePerFraction, dataPoint.minDosagePerFraction);

        //compare end date
        if (ganttData[i].end != ganttData[i].end) {
          ganttData[i].end = Math.max(ganttData[i].end, dataPoint.end);
          ganttData[i].endDate = new Date(ganttData[i].end - 60000 * 60 * 24);
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
      let startDateUnix = this.parseTime(this.radiationAppointments[i].start_date);
      let endDateUnix = this.parseTime(this.radiationAppointments[i].end_date) + 60000 * 60 * 24;
      let dataPoint = {
        id: this.radiationAppointments[i].site_general,
        start: startDateUnix,
        startDate: this.radiationAppointments[i].start_date,
        end: endDateUnix,
        endDate: this.radiationAppointments[i].end_date,
        numberOfSite: 1,
        maxDosagePerFraction: this.radiationAppointments[i].dose_per_fraction,
        minDosagePerFraction: this.radiationAppointments[i].dose_per_fraction
      };
      if (!this.containsObject(dataPoint, ganttData)) {
        ganttData.push(dataPoint);
      } else {
        this.filterData(dataPoint, ganttData);
      }
      datesUnix.push(startDateUnix);
    }

      
      ganttData.sort((a, b) => a.start - b.start);
      let yLabels = [];
    
let scaleYIndex = 0;

let yTickvals = [];
     
for (var i = 0; i < ganttData.length; i++) {
    if (yLabels.indexOf(ganttData[i].id) == -1) {
        yLabels[scaleYIndex] = ganttData[i].id;
        yTickvals.push(yTickvals.length);

        scaleYIndex += 1;
    }
}
    
let data = [];
let hoverData = [];
let testShape = [];
for (let i = 0; i < ganttData.length; i++) {
    data[i] = {
        name: '',
        x: [ganttData[i].startDate, ganttData[i].endDate],
        y: [yLabels.indexOf(ganttData[i].id), yLabels.indexOf(ganttData[i].id)],
        marker: {color: 'white'}
    };
    let endDate = new Date(ganttData[i].endDate);
    endDate = new Date(endDate.setDate(endDate.getDate() + 1));
    let midDate = new Date((new Date(ganttData[i].startDate).getTime() + endDate.getTime()) / 2);
  
    let dosage = "";
    if (ganttData[i].minDosagePerFraction === ganttData[i].maxDosagePerFraction) {
        dosage = "<br>Dosage per fraction: "+ ganttData[i].maxDosagePerFraction;
    } else {
        dosage = "<br>Dosage per fraction: "+ ganttData[i].minDosagePerFraction + " - " + ganttData[i].maxDosagePerFraction;
    }
    hoverData[i] = {
        x: [midDate],
        y: [yLabels.indexOf(ganttData[i].id)],
        xaxis: 'x2',
        mode: 'markers',
        marker: {color: 'white'},
        type: 'scatter',
        hoverlabel: {
          bgcolor: '#29A2CC',
          font: {color: 'white'}
        },
        customdata: ["Site: " + ganttData[i].id + "<br>Number of lesions: "+ ganttData[i].numberOfSite + dosage + "<br>Start date: "+ganttData[i].startDate +"<br>End date: "+ganttData[i].endDate],
        hovertemplate: "%{customdata}<extra></extra>"

    }
  
    testShape[i] = {
        x0: ganttData[i].startDate,
        x1: endDate,
        y0: yLabels.indexOf(ganttData[i].id) - 0.4,
        y1: yLabels.indexOf(ganttData[i].id) + 0.4,
        line: {width: 0}, 
      type: 'rect', 
      xref: 'x', 
      yref: 'y', 
      opacity: 1, 
      fillcolor: '#29A2CC'
    }
}
let date1 = new Date(ganttData[0].startDate);
let diagnosisDate = new Date(date1.setMonth(date1.getMonth()-1));
let date2 = new Date(ganttData[ganttData.length - 1].endDate);
let deceasedDate = new Date(date2.setMonth(date2.getMonth()+1));
let minX =new Date(date1.setMonth(date1.getMonth()-1));
let maxX =new Date(date2.setMonth(date2.getMonth()+1));

let trace1 = {
  x: [diagnosisDate],
  y: [-1],
  xaxis: 'x2',
  mode: 'markers+text',
  type: 'scatter',
  name: '',
  text: ['Date of diagnosis'],
  hovertemplate: "Date of diagnosis: " + diagnosisDate.toISOString().split('T')[0],
  textposition: 'right',
  textfont: {
    family:  'Raleway, sans-serif'
  },
  marker: { 
    color: '#D31E1E',
    size: 12 
  }
};

let trace2 = {
  x: [deceasedDate],
  y: [scaleYIndex],
  xaxis: 'x2',
  mode: 'markers+text',
  type: 'scatter',
  name: '',
  text: ['Deceased date'],
  hovertemplate: "Deceased date: " + deceasedDate.toISOString().split('T')[0],
  textposition: 'left',
  textfont: {
    family:  'Raleway, sans-serif'
  },
  marker: { 
    color: '#D31E1E',
    size: 12 
  }
};
data.push(trace1);
data.push(trace2);
data = data.concat(hoverData);

let layout = {
    
  height: (scaleYIndex+ 2)*100, 
  
  xaxis: {
    type: 'date', 
    showgrid: true, 
    zeroline: false, 
    showline: true,
    range: [minX, maxX],
    automargin: true
 
  }, 
  xaxis2: {
    type: 'date', 
    side: 'top',
   
    showgrid: true, 
    zeroline: false, 
    showline: true,
    range: [minX, maxX],
    automargin: true
 
  }, 
  yaxis: {
    range: [-1, yLabels.length], 
    autorange: "reversed",
    showgrid: true, 
    tickvals: yTickvals,
    ticktext: yLabels, 
    zeroline: false, 
    showline: true,
    automargin: true
    
  }, 
 
  shapes: testShape, 
  hovermode: 'closest', 
  showlegend: false,

};

this.plotly.newPlot(this.props.chartId, data, layout, this.plotlyConfig);
  }

  parseTime(dateString) {
    return this.moment(dateString).unix() * 1000;
  }


  componentDidMount() {
    this.plotly = window.Plotly;
    this.moment = window.moment;
    this.drawChart();
  }
}

export default Radiation;
