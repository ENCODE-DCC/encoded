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
          ganttData[i].endDate = new Date(ganttData[i].end);
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

    let ganttData = [];

    for (let i = 0; i < this.radiationAppointments.length; i++) {
      let dataPoint = {
        id: this.radiationAppointments[i].site_general,
        startDate: this.radiationAppointments[i].start_date + ' 00:00:00',
        endDate: this.radiationAppointments[i].end_date + ' 00:00:00',
        numberOfSite: 1,
        maxDosagePerFraction: this.radiationAppointments[i].dose_per_fraction,
        minDosagePerFraction: this.radiationAppointments[i].dose_per_fraction
      };
      if (!this.containsObject(dataPoint, ganttData)) {
        ganttData.push(dataPoint);
      } else {
        this.filterData(dataPoint, ganttData);
      }
    }

      
      ganttData.sort((a, b) => new Date(a.startDate) - new Date(b.startDate));
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
let dumbbellData = [];
for (let i = 0; i < ganttData.length; i++) {
    data[i] = {
        name: '',
        x: [ganttData[i].startDate, ganttData[i].endDate],
        y: [yLabels.indexOf(ganttData[i].id), yLabels.indexOf(ganttData[i].id)],
        marker: {color: 'white',
      }
    };
    let midDate = new Date((new Date(ganttData[i].startDate).getTime() + new Date(ganttData[i].endDate).getTime()) / 2);
  
    let dosage = "";
    if (isNaN(ganttData[i].minDosagePerFraction) && isNaN(ganttData[i].maxDosagePerFraction) ){
        dosage = "<br>Dosage per fraction: Not available";
    } else if (ganttData[i].minDosagePerFraction === ganttData[i].maxDosagePerFraction) {
        dosage = "<br>Dosage per fraction: "+ ganttData[i].maxDosagePerFraction;
    } else {
        dosage = "<br>Dosage per fraction: "+ ganttData[i].minDosagePerFraction + " - " + ganttData[i].maxDosagePerFraction;
    }
    let endDate = "<br>End date: Not available";
    if (ganttData[i].endDate.split(" ")[0] !== "undefined") {
        endDate = "<br>End date: "+ganttData[i].endDate.split(" ")[0]
    }
    
    hoverData[i] = {
        x: [midDate],
        y: [yLabels.indexOf(ganttData[i].id)],
        xaxis: 'x2',
        mode: 'markers',
        marker: {color: '#29A2CC',
                 size: 1
                },
        type: 'scatter',
        hoverlabel: {
          bgcolor: '#29A2CC',
          font: {color: 'white'}
        },
        customdata: ["Site: " + ganttData[i].id + "<br>Number of lesions: "+ ganttData[i].numberOfSite + dosage + "<br>Start date: "+ganttData[i].startDate.split(" ")[0] +endDate],
        hovertemplate: "%{customdata}<extra></extra>"

    }

    dumbbellData[i] = {
      x: [ganttData[i].startDate, ganttData[i].endDate],
      y: [yLabels.indexOf(ganttData[i].id), yLabels.indexOf(ganttData[i].id)],
      mode: 'lines+markers',
      hoverinfo:'skip',
      marker: {
        color: '#29A2CC',
        size: 15
      },
      line: {
        color: '#29A2CC',
        width: 15
      },
      type: 'scatter',
      hoverlabel: {
        bgcolor: '#29A2CC',
        font: {color: 'white'}
      },
      hovertemplate: "Site: " + ganttData[i].id + "<br>Number of lesions: "+ ganttData[i].numberOfSite + dosage + "<br>Start date: "+ganttData[i].startDate.split(" ")[0] + endDate + "<extra></extra>"
    }
}

let diagnosisDate;
let minX =new Date(this.props.first_treatment_date + ' 00:00:00');
if (this.props.diagnosis_date != "Not available") {
  diagnosisDate = new Date(this.props.diagnosis_date + ' 00:00:00' );
  
} 
let deceasedDate;
let lastFollowUpDate;
let maxX;
if (this.props.death_date != null){
  deceasedDate = new Date(this.props.death_date + ' 00:00:00');
  maxX = new Date(this.props.death_date + ' 00:00:00');
} else if(this.props.last_follow_up_date != "Not available") {
  lastFollowUpDate = new Date(this.props.last_follow_up_date + ' 00:00:00');
  maxX = new Date(this.props.last_follow_up_date + ' 00:00:00');
}
else {
  maxX = new Date(ganttData[ganttData.length - 1].endDate);
}

minX =new Date(minX.setMonth(minX.getMonth()-1));

maxX =new Date(maxX.setMonth(maxX.getMonth()+1));

let trace1 ={};
if (diagnosisDate != null) {
  trace1 = {
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
    family:  'Raleway, sans-serif',
    size: 15
  },
  marker: { 
    color: '#D31E1E',
    size: 15
  }
};
}
let trace2 = {};
if (deceasedDate != null) {
  trace2 = {
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
    family:  'Raleway, sans-serif',
    size: 15
  },
  marker: { 
    color: '#D31E1E',
    size: 15
  }
};
} else if (lastFollowUpDate!= null) {
  trace2 = {
    x: [lastFollowUpDate],
    y: [scaleYIndex],
    xaxis: 'x2',
    mode: 'markers+text',
    type: 'scatter',
    name: '',
    text: ['Date of last follow up'],
    hovertemplate: "Date of last follow up: " + lastFollowUpDate.toISOString().split('T')[0],
    textposition: 'left',
    textfont: {
      family:  'Raleway, sans-serif',
      size: 15
    },
    marker: { 
      color: '#D31E1E',
      size: 15
    }
  };

}
data.push(trace1);
data.push(trace2);
data = data.concat(hoverData);
data = data.concat(dumbbellData);

let layout = {
    
  height: (scaleYIndex+ 2)*65, 
  margin: {
    l: 120,          
    r: 20,
    b: 20,
    t: 60,
    pad: 4
  },
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
    anchor: 'y', 
    overlaying: 'x',
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
    automargin: true,
    fixedrange: true
    
  }, 
 
  hovermode: 'closest', 
  showlegend: false,

};

this.plotly.newPlot(this.props.chartId, data, layout, this.plotlyConfig);
  }



  componentDidMount() {
    this.plotly = window.Plotly;
    this.moment = window.moment;
    this.drawChart();
  }
}

export default Radiation;






