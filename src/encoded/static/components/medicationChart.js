/* eslint-disable linebreak-style */
import React from 'react';


class MedicationChart extends React.Component {
  constructor(props) {
    super(props);
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
    }

  }
  render() {
    return (
      <div className="flex-container" >

        <div className="chart-main" >
          <div id={this.props.chartId} ></div>
        </div>
      </div>

    );
  }
  unixToDate(unix) {
    var date = new Date(unix);
    return (date.getMonth() + 1) + "-" + date.getDate() + "-" + date.getFullYear();
  }

  drawChart() {

    let dataPoints = [];
    dataPoints = this.props.data.map(i => { return ([Date.parse(i.start_date), Date.parse(i.end_date), i.start_date, i.end_date, i.name]) });
    let sortedDataPoints = dataPoints.sort((a, b) => (a[0] - b[0]));
    //Get xRange from dateRange.
    let sortedDateUnix = sortedDataPoints.map(i => { return [i[0], i[1]] }).flat();
    let minDateUnix = Math.min(...sortedDateUnix);
    let maxDateUnix = Math.max(...sortedDateUnix);

    let minDate = this.unixToDate(minDateUnix);
    let maxDate = this.unixToDate(maxDateUnix);
    // for medication ganttChart :
    let traceData = [];
    let trace1 = {};
    let yIndex = 1;
    let drugNames = [];
    let tickvalArray = [];
    for (let i = 0; i < sortedDataPoints.length; i++) {
      trace1 = {
        x: [sortedDataPoints[i][2], sortedDataPoints[i][3]],
        y: [yIndex, yIndex],
        mode: 'lines',
        line: { width: 20, color: '#29A2CC' },
        ticktext: sortedDataPoints[i][4],
        showlegend: false,
        hovertemplate: "MedName: " + sortedDataPoints[i][4] + "<br>Start date: " + sortedDataPoints[i][2] + "<br>End date: " + sortedDataPoints[i][3] + "<extra></extra>",
        hoverlabel: {
          bgcolor: '#29A2CC',
          font: { color: 'white' },
          bordercolor: "#29A2CC",
          borderwidth: 0,
          borderpad: 5,
        },
        xaxis: 'x1',
        yaxis: 'y1'
      }
      drugNames.push(sortedDataPoints[i][4]);
      tickvalArray.push(yIndex);
      traceData.push(trace1);
      yIndex += 1;
    };
    //for Diagnosis marker:

    if (this.props.diagnosis_date != "Not available") {
      minDateUnix = Date.parse(this.props.diagnosis_date + ' 00:00:00' );
      minDate = this.unixToDate(minDateUnix);

      let trace2 = {};
      trace2 = {
        type: 'scatter',
        x: [minDateUnix],
        y: [0],
        mode: 'markers+text',
        marker: {
          symbol: 'circle',
          color: '#D31E1E',
          size: 15
        },
        text: 'Date of diagnosis',
        textfont: {
          family:  'Raleway, sans-serif',
          size: 15
        },
        textposition: 'right',
        showlegend: false,
        hovertemplate: "Date of diagnosis: " + minDate + "<extra></extra>",
        xaxis: 'x2',
      };
      
      traceData.push(trace2);
    }
    //for deceaced marker:
    let trace3 = {};
    let deceasedDate;
    let lastFollowUpDate;

    if (this.props.death_date != null){
      deceasedDate = new Date(this.props.death_date + ' 00:00:00');
      maxDateUnix = Date.parse(this.props.death_date + ' 00:00:00');
      maxDate = this.unixToDate(maxDateUnix);
      trace3 = {
        type: 'scatter',
        x: [maxDateUnix],
        y: [yIndex],
  
        mode: 'markers+text',
        marker: {
          symbol: 'circle',
          color: '#D31E1E',
          size: 15
        },
        text: 'Deceaced date',
        textfont: {
          family:  'Raleway, sans-serif',
          size: 15
        },
        textposition: 'left',
        showlegend: false,
        hovertemplate: 'Deceased date: ' + maxDate + '<extra></extra>',
        xaxis: 'x2',
      };
      traceData.push(trace3);
    } else if(this.props.last_follow_up_date != "Not available") {
      lastFollowUpDate = new Date(this.props.last_follow_up_date + ' 00:00:00');
      maxDateUnix = Date.parse(this.props.last_follow_up_date + ' 00:00:00');
      maxDate = this.unixToDate(maxDateUnix);
      trace3 = {
        type: 'scatter',
        x: [maxDateUnix],
        y: [yIndex],
  
        mode: 'markers+text',
        marker: {
          symbol: 'circle',
          color: '#D31E1E',
          size: 15
        },
        text: 'Date of last follow up',
        textfont: {
          family:  'Raleway, sans-serif',
          size: 15
        },
        textposition: 'left',
        showlegend: false,
        hovertemplate: 'Date of last follow up: ' + maxDate + '<extra></extra>',
        xaxis: 'x2',
      };
      traceData.push(trace3);
    }

    
    
    var layout = {
      autosize: true,
      height: yIndex*80,

      xaxis: {
        type: 'date',
        range: [minDateUnix - 1000 * 60 * 60 * 24 * 30, maxDateUnix + 1000 * 60 * 60 * 24 * 30],
        anchor: 'x1',
        side: 'bottom',
        showgrid: true,
        showline: true,
      },
      yaxis: {
        autorange: "reversed",
        tickmode: 'array',
        tickvals: tickvalArray,
        ticktext: drugNames,
        zeroline: false,
        showline: true,
        showgrid: true,
        fixedrange: true
      },
      xaxis2: {
        type: 'date',
        range: [minDateUnix - 1000 * 60 * 60 * 24 * 30, maxDateUnix + 1000 * 60 * 60 * 24 * 30],
        overlaying: 'x1',
        anchor: 'x2',
        side: 'top',
        showline: true,
      },

      margin: {
        l: 120,
        r: 20,
        b: 30,
        t: 60,
        pad: 4
      },
      hovermode: 'closest',
    };

    this.plotly.plot(this.props.chartId, traceData, layout, this.plotlyConfig);


  }

  componentDidMount() {
    this.plotly = window.Plotly;
    this.moment = window.moment;
    this.drawChart();
    this.unixToDate();
  }
}
export default MedicationChart;

