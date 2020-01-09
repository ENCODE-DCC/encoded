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
        let date = this.props.data.map(i => i.date).sort();
        let minDate = Date.parse(date[0]);// change time to milliseconds
      let maxDate = Date.parse(date[date.length - 1]);// change time to milliseconds
        let filteredData = [];
        for (let j = 0; j < date.length; j++) {
            let dataPoints = this.props.data.filter(i => i.date === date[j]).map(i => { return [i.date, i.surgery_type, i.nephrectomy_details] }).flat();
            filteredData.push(dataPoints);
            filteredData.flat();

            var data = [];
            for (let i = 0; i < filteredData.length; i++) {

                var traceData = {};
                traceData = {
                    type: 'scatter',
                    x: [filteredData[i][0]],
                    y: [filteredData[i][1]],
                    mode: 'markers+text',
                    text: filteredData[i][1],
                    textposition: "right",
                    hoverinfo: "text",
                    hovertemplate: "Approach:" + filteredData[i][2].approach + "<br>Location:" + filteredData[i][2].location + "<br>Type:" + filteredData[i][2].type + "<br>RoboticAssist:" + filteredData[i][2].robotic_assist+"<extra></extra>",
                    transforms: [{
                        type: 'groupby',
                        groups: [filteredData[i][1]],
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
            }
        }

        var layout = {

            autosize: true,
            xaxis: {
                range: [minDate-600000 * 60 * 24 * 30, maxDate+600000 * 60 * 24 * 30],
                dx: 5,
                showgrid: false,
                showline: true,
            },
            yaxis: {
                zeroline: false,
                showline: true,
                fixedrange: true
            },
            margin: {
                l: 150,
                r: 40,
                b: 50,
                t: 20,
                pad:4
            },
            font: {
                family: "Roboto,sans-serif",
                size:16,
              },
            hovermode: 'closest',
            showlegend:false
        };

        this.plotly.plot(this.props.chartId, data, layout, this.plotlyConfig);
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
