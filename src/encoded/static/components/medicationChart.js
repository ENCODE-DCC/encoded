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
    return (date.getMonth() + 1) + "/" + date.getDate() + "/" + date.getFullYear();
  }

  drawChart() {

    let dataPoints = [];
    dataPoints = this.props.data.map(i => { return ([Date.parse(i.start_date), Date.parse(i.end_date), i.start_date, i.end_date, i.name]) });
    console.log("dataPoints", dataPoints);
    let sortedDataPoints = dataPoints.sort((a, b) => (a[0] - b[0]));
    console.log("dataPoints1", sortedDataPoints);
    //Get xRange from dateRange.
    let sortedDateUnix = sortedDataPoints.map(i => { return [i[0], i[1]] }).flat();
    console.log("sortedDateUnix", sortedDateUnix);
    let minDateUnix = Math.min(...sortedDateUnix);
    let maxDateUnix = Math.max(...sortedDateUnix);

    console.log(minDateUnix);
    console.log(maxDateUnix);
    let minDate = this.unixToDate(minDateUnix);
    let maxDate = this.unixToDate(maxDateUnix);
    console.log(minDate);
    console.log(maxDate);

    let traceData = [];
    let trace1 = {};
    let yIndex = 1;
    let drugNames = [];
    let tickvalArray = [];
    for (let i = 0; i < sortedDataPoints.length; i++) {
      trace1 = {
        // type:"line",
        // name:'',
        x: [sortedDataPoints[i][2], sortedDataPoints[i][3]],
        y: [yIndex, yIndex],
        mode: 'lines',
        line: { width: 20, color: '#29A2CC' },
        ticktext: sortedDataPoints[i][4],
        // text: dataPoints[i][2],
        // textposition: "right",
        showlegend: false,
        hovertemplate: "MedName: " + sortedDataPoints[i][4] + "<br>Start date: " + sortedDataPoints[i][2] + "<br>End date: " + sortedDataPoints[i][3] + "<extra></extra>",
        xaxis: 'x1',
        yaxis: 'y1'
      }
      drugNames.push(sortedDataPoints[i][4]);
      tickvalArray.push(yIndex);
      traceData.push(trace1);
      yIndex += 1;
    };
    console.log("drugNames", drugNames);
    console.log("tickvalsArray", tickvalArray);
    //for Diagnosis marker:
    let trace2 = {};
    trace2 = {
      type: 'scatter',
      x: [minDateUnix],
      y: [0],
      mode: 'markers+text',
      marker: {
        symbol: 'triangle-right',
        color: 'red',
        size: 16
      },
      text: 'Diagnosis date',
      textfont: {
        family: "Georgia",//'sans serif'
        size: 16,
        color: "black"
      },
      textposition: 'right',
      showlegend: false,
      hovertemplate: "Diagnosis date: " + minDate + "<extra></extra>",
      xaxis: 'x2',
      // yaxis:'y2'
      // xanchor: 'bottom',
      // mirror:'true',

    };
    //for deceaced marker:
    let trace3 = {};
    trace3 = {
      type: 'scatter',
      x: [maxDateUnix],
      y: [yIndex],

      mode: 'markers+text',
      marker: {
        symbol: 'triangle-left',
        color: 'red',
        size: 16
      },
      text: 'Deceaced date',
      textfont: {
        family: "Georgia",
        size: 16,
        color: "black"
      },
      textposition: 'left',
      showlegend: false,
      hovertemplate: 'Diagnosis date: ' + maxDate + '<extra></extra>',
      xaxis: 'x2',
      // yaxis:'y2'
    };
    traceData.push(trace2);
    traceData.push(trace3);
    // drugNames.push("Diagnosis Date");
    // console.log(data);
    var layout = {
      autosize: true,
      // width: 800,
      height: 300,
      xaxis: {
        type: 'date',
        range: [minDateUnix - 1000 * 60 * 60 * 24 * 180, maxDateUnix + 1000 * 60 * 60 * 24 * 180],
        // domain: [0, 0.45],
        anchor: 'x1',
        side: 'bottom',
        // step:'month',
        // dx: 5,
        // dtick:'1000*60*60*24*30*12*3',
        showgrid: true,
        showline: true,
        // zeroline: false,
      },
      yaxis: {
        // range:[0,yAxis*1.05],
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
        range: [minDateUnix - 1000 * 60 * 60 * 24 * 180, maxDateUnix + 1000 * 60 * 60 * 24 * 180],
        // anchor: 'y1', 
        overlaying: 'x1',
        // dx:'date',
        // domain: [0, 0.45],
        anchor: 'x2',
        side: 'top',
        showline: true,
      },
      font: {
        family: "Georgia",
        fontweight:"bold",
        size: 16,
    },
      // yaxis2:{
      //   anchor:'y2'
      // }
      margin: {
        l: 150,
        r: 40,
        b: 50,
        t: 50,
        pad: 4
      },
      hovermode: 'closest',
    };

    // var data1 = [trace0, trace1, trace2];
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
