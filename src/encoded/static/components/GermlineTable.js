import React from 'react';

class GermlineTable extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            showData: true,
        };
        this.tableConfig = {};
        this.data = [];
        this.germlineFilters = [];
        this.transferData = [];
    }


    render() {
        this.data = this.props.data;
        console.log(this.data);
        if (!Array.isArray(this.data) || !this.data.length) {
            return (
                <div>
                    <div className="flex-container">
                        <div className="chart-main">
                            <div className="chart-title">
                                <div><h3>{this.props.tableTitle}</h3> </div>
                                <div><h4>Germline mutation data is not available!</h4></div>
                            </div>
                        </div>
                    </div>
                </div>
            );
        } else {
            if (this.state.showData) {
                return (
                    
                    <div className="flex-container">
                        <div className="table-container">
                            <div className="table-body">
                                <div className="chart-title" ><h3>{this.props.tableTitle}</h3></div>
                                <div  id={this.props.tableId} className="table-area"> </div>
                            </div>
                        </div>
                    </div>
                );

            } else {
                return (
                <div>
                    <div className="flex-container">
                        <div className="chart-main">
                            <div className="chart-title">
                                <div><h3>{this.props.tableTitle}</h3> </div>
                                <div> <h4>No positive !</h4></div>
                            </div>
                        </div>
                    </div>
                </div>
                );
            }
        }
    }


    renderTable() {
        this.zingchart.render({
            id: this.props.tableId,
            data: this.tableConfig,
        });
    }
    filterData() {
        this.germlineFilters = this.data.filter(i => (i.significance === 'Positive' || i.significance === 'Variant' || i.significance === 'Positive and Variant'));
        // filter data with positive 
    }


    transferDataFun() {
        this.transferData = this.germlineFilters.map(i => ({ values: [i.target, i.significance] }));
        // need to transfer to series format: [{values:[i]},{values:[2]}...]
        this.setState({ showData: this.transferData.length > 0 });
    }

    updateTable() {
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
        this.renderTable();
    }

    componentDidMount() {
        this.zingchart = window.zingchart;
        this.moment = window.moment;
        this.filterData();
        this.transferDataFun();
        this.updateTable();
        this.renderTable();
    }
}


export default GermlineTable;
