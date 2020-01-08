import React from 'react';

class SurgeryChart extends React.Component {
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

    drawChart() {
        console.log(this.props.data);
        let date = this.props.data.map(i => i.date).sort();
        console.log(date);
        var x = [];
        var y = [];
        // var text = [];
        // let roboticAssist=[];
        // var type = [];
        let data1 = [];
        // let location=[];
        for (let j = 0; j < date.length; j++) {
            var dataPoints = this.props.data.filter(i => i.date === date[j]).map(i => { return [i.date, i.surgery_type, i.nephrectomy_details] }).flat();
        console.log("dataPoints", dataPoints);
        data1.push(dataPoints);
        data1.flat();
        console.log("data1", data1);
        
        var data = [];
        for (let i = 0; i < data1.length; i++) {

            var traceData = {};
            traceData = {
                type: 'scatter',
                x: [data1[i][0]],
                y: [data1[i][1][0]],
                text:data1[i][1][0],
                textposition:'right',
                hovertemplate: "Approach:" + data1[i][2].approach + "<br>Location:" + data1[i][2].location + "<br> Type:" + data1[i][2].type + "<br>RoboticAssist:" + data1[i][2].robotic_assist,
                mode: 'markers+text',
                opacity: 0.5,
                transforms: [{
                    type: 'groupby',
                    groups: [data1[i][1][0]],
                    styles: [
                        {
                            target: 'Nephrectomy', value: {
                                marker: {
                                    color: 'blue',
                                    symbol: 'diamond',
                                    size: '16'
                                }
                            }
                        },
                        {
                            target: 'Ablation', value: {
                                marker: {
                                    color: 'green',
                                    symbol: 'triangle',
                                    size: '16'
                                }
                            }
                        },
                        {
                            target: 'Metastectomy', value: {
                                marker: {
                                    color: 'red',
                                    symbol: 'circle',
                                    size: '16'
                                }
                            }
                        },
                    ],
                }],

            }
            data.push(traceData);
            // console.log("traceData",traceData);
            console.log("data", data);
        }
    }
var layout = {
         
    autosize: true,
    xaxis: {
        showgrid: true,
        showline: true,
        linecolor: 'black',
        autotick: true,
        // dtick: 10,
        // ticks: 'inside',
        // tickcolor: 'black'
    },
    yaxis: {
        showgrid: true,
        showline: true,
        linecolor: 'black',
        autotick: true,
        // dtick: 10,
        // ticks: 'inside',
        // tickcolor: 'black'
    },
    margin: {
        l: 100,
        r: 40,
        b: 50,
        t: 80
    },
    width: 800,
    height: 300,
    hovermode: 'closest'
};

this.plotly.plot(this.props.chartId, data, layout,this.plotlyConfig);
    }

render() {
    return (
        <div className="flex-container" >

            <div className="chart-main" >
                <div id={this.props.chartId}></div>
            </div>
        </div>

    );
}
componentDidMount() {
    this.plotly = window.Plotly;
    this.moment = window.moment;
    this.drawChart();
}
}

export default SurgeryChart;
// =======================================================
// surgery=[
//     {
//         "patient": "KCEPT359MHZ",
//         "date": "1860-06-03",
//         "surgery_type": ["Nephrectomy"],
//         "nephrectomy_details": {
//           "type":"Partial",
//           "approach": "Open",
//           "robotic_assist": true,
//           "location": "UTSW"
//         },
//         "uuid": "41692393-f1f3-4797-9043-989c96a9621c"
//     },
//     {
//         "patient": "KCEPT708IJT",
//         "date": "1855-01-03",
//         "surgery_type": ["Nephrectomy"],
//         "nephrectomy_details": {
//           "type":"Total",
//           "approach": "Open",
//           "robotic_assist": true,
//           "location": "UTSW"
//         },
//         "uuid": "717612f1-0fb7-411b-a8b3-b045e252d098"
//     },
// ]
