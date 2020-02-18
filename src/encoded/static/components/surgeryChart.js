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
        console.log(this.props.data);
        this.props.data.forEach((i) => {
          i.surgery_procedure.forEach((surgery_procedure) => {
              if (surgery_procedure.procedure_type === "Nephrectomy") {
                nephDataPoints.push({ "date": Date.parse(i.date), "Date": i.date, "procedure_type": surgery_procedure.procedure_type, "hospital_location": i.hospital_location, "nephrectomy_details": surgery_procedure.nephrectomy_details})
              }
              else if (surgery_procedure.procedure_type === "Ablation") {
                ablaDataPoints.push({ "date": Date.parse(i.date), "Date": i.date, "procedure_type": surgery_procedure.procedure_type, "hospital_location": i.hospital_location})
              }
              else if (surgery_procedure.procedure_type === "Metastectomy") {
                metDataPoints.push({ "date": Date.parse(i.date), "Date": i.date, "procedure_type": surgery_procedure.procedure_type, "hospital_location": i.hospital_location})
              }
            })
          });

        //nephDataPoints = this.props.data.filter(i => {i.surgery_procedure.filter( surgery_procedure => { return surgery_procedure.procedure_type === "Nephrectomy" })}).map(i => { return [Date.parse(i.date), i.date, surgery_procedure.procedure_type, i.hospital_location, surgery_procedure.nephrectomy_details] });
        nephDataPoints.sort((a, b) => a[0] - b[0]);

        //ablaDataPoints = this.props.data.filter(i => { return i.surgery_procedure.procedure_type === "Ablation" }).map(i => { return [Date.parse(i.date), i.date, i.surgery_procedure.procedure_type, i.hospital_location] });
        ablaDataPoints.sort((a, b) => a[0] - b[0]);

        //metDataPoints = this.props.data.filter(i => { return i.surgery_procedure.procedure_type === "Metastectomy" }).map(i => { return [Date.parse(i.date), i.date, i.surgery_procedure.procedure_type, i.hospital_location] });
        metDataPoints.sort((a, b) => a[0] - b[0]);
          console.log(nephDataPoints);
          console.log(ablaDataPoints);
          console.log(metDataPoints);

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
                    x: [nephDataPoints[i]["Date"]],
                    y: [nephDataPoints[i]["procedure_type"]],
                    mode: 'markers',
                    marker: {
                        color: 'blue',
                        symbol: 'diamond',
                        size: '16'
                    },
                    text: nephDataPoints[i]["procedure_type"],
                    textposition: "right",
                    hovertemplate: "Hospital location: " + nephDataPoints[i]['hospital_location'] + "<br>Neph type: " + nephDataPoints[i]["nephrectomy_details"].type + "<br>Neph approach: " + nephDataPoints[i]["nephrectomy_details"].approach + "<br>Robotic Assist: " + nephDataPoints[i]["nephrectomy_details"].robotic_assist + "<extra></extra>"
                };
                data.push(traceNeph);
            };
        };

        let traceMet = {};
        if (metDataPoints.length > 0) {
            for (let i = 0; i < metDataPoints.length; i++) {
                traceMet = {
                    type: 'scatter',
                    x: [metDataPoints[i]["Date"]],
                    y: [metDataPoints[i]["procedure_type"]],
                    mode: 'markers',
                    marker: {
                        color: 'red',
                        symbol: 'circle',
                        size: '16'
                    },
                    text: metDataPoints[i]["procedure_type"],
                    textposition: "right",
                    hovertemplate: "Hospital location: " + metDataPoints[i]["hospital_location"] + "<extra></extra>"
                };
                data.push(traceMet);
            };
        }

        let traceAbla = {};
        if (ablaDataPoints.length > 0) {
            for (let i = 0; i < ablaDataPoints.length; i++) {
                traceAbla = {
                    type: 'scatter',
                    x: [ablaDataPoints[i]["Date"]],
                    y: [ablaDataPoints[i]["procedure_type"]],
                    mode: 'markers',
                    marker: {
                        color: 'green',
                        symbol: 'square',
                        size: '16'
                    },
                    text: ablaDataPoints[i]["procedure_type"],
                    textposition: "right",
                    hovertemplate: "Hospital location: " + ablaDataPoints[i]["hospital_location"] + "<extra></extra>"
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
