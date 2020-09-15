import React from 'react';

class PatientChart extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            checkboxes: [],
            displayPlots: {}
        };
        this.features = Object.keys(this.props.data).sort();
        if (this.features.indexOf("BP_SYS") != -1 && this.features.indexOf("BP_DIAS") != -1){
          let indexSystolic = this.features.indexOf("BP_SYS");
          let indexDiastolic = this.features.indexOf("BP_DIAS");
          this.features[indexSystolic] = "BP_DIAS";
          this.features[indexDiastolic] = "BP_SYS";
        }
        this.data = {};
        this.plotlyCharts = [];
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
        },
        this.firstTime = true;
    }
    render() {
      var plots = [];
      for (var [index,value] of this.features.entries()) {
        plots.push(<div id={this.props.chartId + value} className="lab-plot" style={!this.state.displayPlots[value] && !this.firstTime ? {display:"none"} : {}}></div>);
      }
        return (<div>
            <div className="flex-container" >
                <div className="chart-menu" >
                    <h4>Show/Hide Results</h4>
                    <div className="chart-checkboxes pb-2"> {this.state.checkboxes}</div>
                </div>
                <div className="chart-main" >
                    {plots}
                  
                </div>
            </div>
        </div>)

    }

    renderChart() {
        for (var i = 0; i < this.plotlyCharts.length; i++) {
          this.plotly.newPlot(this.plotlyCharts[i].id, this.plotlyCharts[i].data, this.plotlyCharts[i].layout, this.plotlyConfig);
        }
        this.firstTime = false;
    }

    createCheckboxes() {
        let tempCheckboxes = [];
        let tempDisplayPlots = {};

        for (let i = 0; i < this.features.length; i++) {
            let feature = this.features[i];
            var styles = {
                color: "#003767"
            }
            tempCheckboxes.push(<div key={i} className="pointer"><input type="checkbox" id={feature} value={feature} name={feature} defaultChecked="checked" onChange={(e) => {this.handleCheckboxChange(e, this)}} />
                <label style={styles} htmlFor={feature}>{feature}</label></div>);
            tempDisplayPlots[feature] = true;
        }
        this.setState({ checkboxes: tempCheckboxes, displayPlots :tempDisplayPlots });
        
    }

    drawChart() {
        this.data = this.props.data;
        this.createCheckboxes();
        this.initChart();
    }

    parseTime(dateString) {
        return this.moment(dateString).unix() * 1000;
    }
    handleCheckboxChange(event) {
        let checked = event.currentTarget.checked;
        let value = event.currentTarget.value;
        let tempDisplayPlots = JSON.parse(JSON.stringify(this.state.displayPlots));
        tempDisplayPlots[value] = checked;
        this.setState({ displayPlots :tempDisplayPlots });

    }
    initChart() {
        let allDates = [];
        for (let i = 0; i < this.features.length; i++) {
            allDates = allDates.concat(this.data[this.features[i]].map(i => {return i.date;}));
        };
        allDates = [...new Set(allDates)]
        allDates.sort(function(a,b) {
            a = a.split('-').join('');
            b = b.split('-').join('');
            return a > b ? 1 : a < b ? -1 : 0;

        });
        let allDatesUnix = allDates.map(i => { return this.parseTime(i) });
        let startDate = Math.min(...allDatesUnix);
        let endDate = Math.max(...allDatesUnix) + 1000*60*60*24;

        for (let i = 0; i < this.features.length; i++) {
            let feature = this.features[i];
            let filteredData = this.data[this.features[i]];
            let filteredDates = this.data[this.features[i]].map(i => {return i.date;});
            let filteredDatesUnix = filteredDates.map(i => { return this.parseTime(i) });
            let values = [];
            let rangeValues = [];
            let rangeLows = [];
            let y = [];
            let yRangeTop = [];
            let yRangeBottom = [];
            for (let j = 0; j < filteredDates.length; j++) {
                let currentDate = filteredDates[j];
                let dataPoints = filteredData.filter(i => { return i.date === currentDate });

                values.push([filteredDatesUnix[j], dataPoints[0].value]);
                y.push(dataPoints[0].value);

                rangeValues.push([filteredDatesUnix[j], [dataPoints[0].reference_low, dataPoints[0].reference_high]]);
                yRangeTop.push(dataPoints[0].reference_high);
                yRangeBottom.push(dataPoints[0].reference_low);

                if (dataPoints[0].reference_low != undefined) {
                  rangeLows.push([dataPoints[0].reference_low]);
                  yRangeBottom.push(dataPoints[0].reference_low);
                };
            };
            let highs = [];
            let lows = []
            let customRangeText = [];
            
            for (let i = 0; i < rangeValues.length; i++) {
              if (rangeValues[i][1][0] === undefined && rangeValues[i][1][1] === undefined) {
                lows.push(-1);
                highs.push(-1);
                customRangeText.push("");
              } else {
                lows.push(rangeValues[i][1][0]);
                highs.push(rangeValues[i][1][1]);
                customRangeText.push("Reference range: " + rangeValues[i][1][0] + " - " + rangeValues[i][1][1]);
              };
            };

            let unit = filteredData[0].value_units;
            let minY = Math.min(...filteredData.map(i => { return i.value }));
            if (rangeLows.length > 0) {
              let minRange = Math.min(...rangeLows);
              minY = Math.min(minY, minRange);
            };

            let maxY = -1;
            maxY = Math.max(maxY, highs.slice(0).sort(this.sortingStringsAsNumber).reverse()[0]);
            maxY = Math.max(maxY, y.slice(0).sort(this.sortingStringsAsNumber).reverse()[0]);

            let traceData = [
              {
                x: filteredDates.slice(0).sort().concat(filteredDates.slice(0).sort().reverse()),
                y: yRangeTop.concat(yRangeBottom.reverse()),
                hoverinfo: 'skip',
                mode: "lines",
                fill: 'tonexty',
                line: {
                  color: '#cde5fa',
                  width: 0
                },
                showlegend: false,
              },
              {
                x: filteredDates,
                y: y,
                mode: 'lines+markers',
                customdata: customRangeText,
                hovertemplate: feature + ": %{y} " + unit + "<br>Date: %{x} <br>%{customdata}<extra></extra>",
                showlegend: false,
                line: {
                  color: "#003767",
                  width: 1
                }
              },
            ];
            let traceLayout = {
              title: feature + " (" + unit + ")",
              yaxis: {
                range: [minY * 0.95, maxY * 1.05],
                zeroline: false,
                showline: true,
                fixedrange: true
              },
              xaxis: {
                range: [startDate - 1000*60*60*24*30, endDate + 1000*60*60*24*30],
                showgrid: false,
                showline: true,
              },
              hovermode: "closest",
              font: {
                family: "Raleway, sans-serif",
                size:10,
              },
              margin: {
                l: 40,
                r: 20,
                b: 20,
                t: 30,
                pad: 4
              },

            };
            this.plotlyCharts.push({id:this.props.chartId + feature, data: traceData, layout:traceLayout});
        }

        this.renderChart();
    }

    sortingStringsAsNumber(a, b) {
      return (+a) - (+b);
    }

    componentDidMount() {
      this.plotly = window.Plotly;
      this.moment = window.moment;
      this.drawChart();
    }
}

export default PatientChart;

