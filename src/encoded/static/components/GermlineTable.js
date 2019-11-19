import React from 'react';

class GermlineTable extends React.Component {
    constructor(props) {
        super(props);
        // this.state = {
        //     showData: true,
        // };
        this.tableConfig = {};
        // this.data = [];
        this.germlineFilters = [];
        this.transferData = [];
        this.data = this.props.data;
        //this.zingchart = this.window.zingchart;
    }
    // eslint-disable-next-line react/sort-comp
    filterData() {
        this.germlineFilters = this.data.filter(i => (i.significance === 'Positive' || i.significance === 'Variant' || i.significance === 'Positive and Variant'));
        // filter data with positive
        console.log(this.germlineFilters);
    }


    transferDataFun() {
        this.transferData = this.germlineFilters.map(i => ({ values: [i.target, i.significance] }));
        // need to transfer to series format: [{values:[i]},{values:[2]}...]
        // this.setState({ showData: this.transferData.length > 0 });
        console.log(this.transferData);
    }
    configTable() {
        this.tableConfig = {
            type: 'grid',
            plotarea: {
                margin: 20,
            },
            globals: {
                fontFamily: 'Arial',
                fontStyle: 'normal',
                fontWeight: 'normal',
            },
            backgroundColor: '',
            options: {
                'col-labels': [
                    'Target',
                    'Significance',
                ],
                style: {
                    '.td': {
                        paddingTop: '9px',
                        align: 'center',
                        borderTop: 'none',
                        borderRight: '1px solid #2f3341',
                        borderBottom: '1px solid #2f3341',
                        borderLeft: '1px solid #2f3341',
                        borderWidth: '1px',
                        fontColor: '#000000',
                        fontSize: '16px',
                        height: '34px',
                    },
                    '.th': {
                        align: 'center',
                        backgroundColor: '#074361',
                        borderTop: '1px solid #2f3341',
                        borderRight: '1px solid #2f3341',
                        borderBottom: '1px solid #2f3341',
                        borderLeft: '1px solid #2f3341',
                        fontColor: '#FFFFFF',
                        fontSize: '20px',
                        fontWeight: 'normal',
                        height: '38px',
                    },
                    '.tr_even': {

                        backgroundColor: 'none',
                    },
                    '.tr_odd': {
                        backgroundColor: 'none',
                    },
                },
            },

            series: this.transferData,
        };
        let chart={
            id: this.props.tableId,
            data: this.tableConfig,
            height: '100%',
            width: '100%',
        };
        this.zingchart.render(chart);
    }

    componentDidMount() {
        this.zingchart = window.zingchart;
        // this.moment = window.moment;
        this.filterData();
        this.transferDataFun();
        // this.updateTable();
        this.configTable();
        // this.zingchart.render();
        // console.log(this.germlineFilters);
        // console.log(this.transferData);
    }
    renderData() {
        if (!Array.isArray(this.data) || !this.data.length) {
            return (
                <div className="flex-container">
                    <div className="chart-main">
                        <div className="chart-title">
                            <div><h3>{this.props.tableTitle}</h3> </div>
                            <div><h4>Germline mutation data is not available!</h4></div>
                        </div>
                    </div>
                </div>
            );
        }
        if (this.transferData) {
            return (
                <div className="flex-container">
                    <div className="table-container">
                        <div className="table-body">
                            <div className="chart-title" ><h3>{this.props.tableTitle}</h3></div>
                            <div id={this.props.tableId} className="table-area"> </div>
                        </div>
                    </div>
                </div>
            );
        }
        return (
            <div className="flex-container">
                <div className="chart-main">
                    <div className="chart-title">
                        <div><h3>{this.props.tableTitle}</h3> </div>
                        <div> <h4>No positive !</h4></div>
                    </div>
                </div>
            </div>
        );
    }
    render() {
        return (<div>{this.renderData()}</div>);
    }
}


export default GermlineTable;
//----------------------------------------------------------------------------------------------
// Test: http://localhost:6543/patients/KCEPT480NBU / Positive
// Test: http://localhost:6543/patients/KCEPT873QVK/ Positive and Variant;
// Test: http://localhost:6543/patients/KCEPT398JLK/ not available
// [
//     {
//         "patient": "KCEPT139SOR",
//         "register_date": "1876-03-21",
//         "service_date": "1876-04-09",
//         "significance": "Not Available",
//         "status": "released",
//         "target": "BRCA1",
//         "uuid": "ad334be1-86a0-4b21-9130-e22c4eb48356"
//     },
//     {
//         "patient": "KCEPT139SOR",
//         "register_date": "1876-03-21",
//         "service_date": "1876-04-09",
//         "significance": "Not Available",
//         "status": "released",
//         "target": "BRCA2",
//     {
//     {
//         "patient": "KCEPT139SOR",
//         "register_date": "1876-03-21",
//         "service_date": "1876-04-09",
//         "significance": "Not Available",
//         "status": "released",
//         "target": "MULTISITE3",
//         "uuid": "c54558ef-5b6a-4752-ad50-5b27431eb9be"
//     }]
