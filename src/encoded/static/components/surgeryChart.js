import React from 'react';
import { faCalendarDay } from '@fortawesome/free-solid-svg-icons';
import { months } from 'moment';

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
        let dataPoints = [];
        dataPoints = this.props.data.map(i => { return ([Date.parse(i.date),i.date, i.surgery_type, i.nephrectomy_details]) });
        dataPoints.sort((a, b) => (a[0] - b[0]));
        let sortedDate = dataPoints.map(i => i[0]);

        let minDate = Math.min(...sortedDate);
        let maxDate = Math.max(...sortedDate);

        let data = [];
        let traceData = {};
        for (let i = 0; i < dataPoints.length; i++) {
            traceData = {
                type: 'scatter',
                x: [dataPoints[i][1]],
                y: [dataPoints[i][2]],
                mode: 'markers+text',
                text: dataPoints[i][2],
                textposition: "right",
                hovertemplate: "Approach: " + dataPoints[i][3].approach +"<br>Location: " + dataPoints[i][3].location + "<br>Type: " + dataPoints[i][3].type + "<br>Robotic Assist: " + dataPoints[i][3].robotic_assist + "<extra></extra>",
                transforms: [{
                    type: 'groupby',
                    groups: [dataPoints[i][2]],
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
                        {
                            target: 'Ablation', value: {
                                marker: {
                                    color: 'green',
                                    symbol: 'square',
                                    size: '16'
                                }
                            }
                        },
                    ],
                }],
            }
            data.push(traceData);

        }

        var layout = {

            autosize: true,
            height:300,
            xaxis: {
                range: [minDate - 600000 * 60 * 24 * 30, maxDate + 600000 * 60 * 24 * 30],
                showgrid: true,
                showline: true,
            },
            yaxis: {
                zeroline: false,
                showline: true,
                showgrid: true,
                fixedrange: true
            },
            margin: {
                l: 150,
                r: 40,
                b: 50,
                t: 20,
                pad: 4
            },
            font: {
                family: "Roboto,sans-serif",
                size: 16,
            },
            hovermode: 'closest',
            showlegend: false,
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
