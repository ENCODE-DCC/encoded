import React from 'react';

class Metastasis extends React.Component {
  constructor(props) {
    super(props);

    this.records = this.props.data;
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
    let metsData = this.records;
    if (metsData.length > 1) {
        metsData.sort((a, b) => new Date(a.date) - new Date(b.date));
    }
    let yLabels = [];   
    let scaleYIndex = 0;
    let yTickvals = [];
    let metsTrace = [];
    let data = [];
        
    for (var i = 0; i < metsData.length; i++) {
        metsData[i].date = metsData[i].date + ' 00:00:00';
        let dataY;
        if (yLabels.indexOf(metsData[i].site) == -1) {
            yLabels[scaleYIndex] = metsData[i].site;
            dataY=scaleYIndex;
            yTickvals.push(yTickvals.length);

            scaleYIndex += 1;
        } else {
            dataY=yLabels.indexOf(metsData[i].site);
        }
        console.log(metsData[i].date);
        console.log(metsData[i].site);
        console.log(dataY);
        metsTrace[i] = {
            x: [metsData[i].date],
            y: [dataY],
            mode: 'markers',
            type: 'scatter',
            hoverinfo:'skip',
            marker: {
                color: '#29A2CC',
                size: 15
            },
            line: {
                color: '#29A2CC',
                width: 15
            },
            hoverlabel: {
                bgcolor: '#29A2CC',
                font: {color: 'white'}
            },
            hovertemplate: "Site: " + metsData[i].site  + "<br>Date: "+metsData[i].date.split(" ")[0] + "<br>Source: "+metsData[i].source + "<extra></extra>"
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
    maxX = new Date(metsData[metsData.length - 1].date);
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
    data = data.concat(metsTrace);


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

export default Metastasis;

