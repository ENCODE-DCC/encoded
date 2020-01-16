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
        var nephDataPoints = [];
        var ablaDataPoints = [];
        var metDataPoints = [];
        nephDataPoints = this.props.data.filter(i => { return i.surgery_type === "Nephrectomy" }).map(i => { return [Date.parse(i.date), i.date, i.surgery_type, i.hospital_location, i.nephrectomy_details] });
        nephDataPoints.sort((a, b) => a[0] - b[0]);

        ablaDataPoints = this.props.data.filter(i => { return i.surgery_type === "Ablation" }).map(i => { return [Date.parse(i.date), i.date, i.surgery_type, i.hospital_location] });
        ablaDataPoints.sort((a, b) => a[0] - b[0]);

        metDataPoints = this.props.data.filter(i => { return i.surgery_type === "Metastectomy" }).map(i => { return [Date.parse(i.date), i.date, i.surgery_type, i.hospital_location] });
        metDataPoints.sort((a, b) => a[0] - b[0]);
        
        let sortedDateUnix = [];
        sortedDateUnix = this.props.data.map(i => { return Date.parse(i.date) });
        sortedDateUnix.sort((a, b) => a - b);

        let minDateUnix = sortedDateUnix[0];
        let maxDateUnix = sortedDateUnix[sortedDateUnix.length - 1];


        let data = [];
        let traceNeph = {};
        if (nephDataPoints.length > 0) {
            for (let i = 0; i < nephDataPoints.length; i++) {
                traceNeph = {
                    type: 'scatter',
                    x: [nephDataPoints[i][1]],
                    y: [nephDataPoints[i][2]],
                    mode: 'markers',
                    marker: {
                        color: 'blue',
                        symbol: 'diamond',
                        size: '16'
                    },
                    text: nephDataPoints[i][2],
                    textposition: "right",
                    hovertemplate: "Hospital location: " + nephDataPoints[i][3] + "<br>Neph type: " + nephDataPoints[i][4].type + "<br>Neph approach: " + nephDataPoints[i][4].approach + "<br>Robotic Assist: " + nephDataPoints[i][4].robotic_assist + "<extra></extra>"
                };
                data.push(traceNeph);
            };
        };

        let traceMet = {};
        if (metDataPoints.length > 0) {
            for (let i = 0; i < metDataPoints.length; i++) {
                traceMet = {
                    type: 'scatter',
                    x: [metDataPoints[i][1]],
                    y: [metDataPoints[i][2]],
                    mode: 'markers',
                    marker: {
                        color: 'red',
                        symbol: 'circle',
                        size: '16'
                    },
                    text: metDataPoints[i][2],
                    textposition: "right",
                    hovertemplate: "Hospital location: " + metDataPoints[i][3] + "<extra></extra>"
                };
                data.push(traceMet);
            };
        }

        let traceAbla = {};
        if (ablaDataPoints.length > 0) {
            for (let i = 0; i < ablaDataPoints.length; i++) {
                traceAbla = {
                    type: 'scatter',
                    x: [ablaDataPoints[i][1]],
                    y: [ablaDataPoints[i][2]],
                    mode: 'markers',
                    marker: {
                        color: 'green',
                        symbol: 'square',
                        size: '16'
                    },
                    text: ablaDataPoints[i][2],
                    textposition: "right",
                    hovertemplate: "Hospital location: " + ablaDataPoints[i][3] + "<extra></extra>"
                };
                data.push(traceAbla);
            };
        };
        var layout = {

            autosize: true,
            height: 300,
            xaxis: {
                range: [minDateUnix - 600000 * 60 * 24 * 30, maxDateUnix + 600000 * 60 * 24 * 30],
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
                family: "Georgia",
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
