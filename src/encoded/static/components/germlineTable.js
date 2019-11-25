/* eslint-disable linebreak-style */
// eslint-disable-next-line linebreak-style
import React from 'react';
import { SortTablePanel, SortTable } from './sorttable';

class GermlineTable extends React.Component {
    constructor(props) {
        super(props);
       // this.data = this.props.data;
        this.germlineFilters = [];
        this.transformData = [];
       // this.tableTitle = this.props.tableTitle;
    }

    filterData() {
        //let data=this.props.data;
        this.germlineFilters = this.props.data.filter(i => (i.significance === 'Positive' || i.significance === 'Variant' || i.significance === 'Positive and Variant'));
        this.transformData = this.germlineFilters.map(i => ({ target: i.target, significance: i.significance }));
        console.log(this.props.data);
        console.log(this.transformData);
        console.log(this.germlineFilters);
    }


    renderData() {
        if (!Array.isArray(this.props.data) || !this.props.data.length) {
            return (<SortTablePanel title={this.props.tableTitle}>
                        <div className="table-body"><h5>Germline mutation data is not available!</h5></div>
                    </SortTablePanel>
            );
        }
        else {
            if(this.transformData.length>0) {
                const germlineTableColumns = {
                    target: {
                        title: 'Target Gene',
                    },
                    significance: {
                        title: 'Clinical Significance',
                    },
                };
                return (
                    <SortTablePanel title={this.props.tableTitle}>
                        <SortTable list={this.transformData} columns={germlineTableColumns} />
                    </SortTablePanel>
                );
            }
            else {
                return (<SortTablePanel title={this.props.tableTitle}>
                        <div className="table-body"><h5>No Positive for mutations!</h5></div>
                    </SortTablePanel>
                );
            }
        }

        
        //Transformat data to <SortTable/> format

    }

    render() {
        return (
            <div> {this.renderData()}</div>
        );
    }

    componentDidMount() {
        this.filterData();
        this.renderData();
    }
}

export default GermlineTable;
// ============================================================
//http://localhost:6543/report/?type=Page&news=true&limit=all&sort=-%40id
{/* <SortTablePanel title={tableTitle}>
<SortTable list={condensedReplicates} columns={replicateTableColumns} />
</SortTablePanel> */}
// this.tableConfig = {
//     type: 'grid',
//     plotarea: {
//         margin: 20,
//     },
//     globals: {
//         fontFamily: 'Arial',
//         fontStyle: 'normal',
//         fontWeight: 'normal',
//     },
//     backgroundColor: '',
//     options: {
//         'col-labels': [
//             'Target',
//             'Significance',
//         ],
//         style: {
//             '.td': {
//                 paddingTop: '9px',
//                 align: 'center',
//                 borderTop: 'none',
//                 borderRight: '1px solid #2f3341',
//                 borderBottom: '1px solid #2f3341',
//                 borderLeft: '1px solid #2f3341',
//                 borderWidth: '1px',
//                 fontColor: '#000000',
//                 fontSize: '16px',
//                 height: '34px',
//             },
//             '.th': {
//                 align: 'center',
//                 backgroundColor: '#074361',
//                 borderTop: '1px solid #2f3341',
//                 borderRight: '1px solid #2f3341',
//                 borderBottom: '1px solid #2f3341',
//                 borderLeft: '1px solid #2f3341',
//                 fontColor: '#FFFFFF',
//                 fontSize: '20px',
//                 fontWeight: 'normal',
//                 height: '38px',
//             },
//             '.tr_even': {

//                 backgroundColor: 'none',
//             },
//             '.tr_odd': {
//                 backgroundColor: 'none',
//             },
//         },
//     },

//     series: this.transferData,
// };
// This module displays a table that can be sorted by any column. You can set one up for display with:
//     <SortTablePanel>
//         <SortTable list={array of objects} columns={object describing table columns} meta={table-specific data} />
//     </SortTablePanel>
//
// <SortTablePanel> supports multiple <SortTable> components as children, so you can have multiple tables,
// each with their own header, inside the table panel.
//
// The list array (required) must be an array of objects whose properties get displayed in each cell of the
// table. The meta object (optional) has any extra data relevant to the specific table and doesn't get
// processed -- only passed on -- by the SortTable code.
//
// The columns object (required) describes the columns of the table, and optionally how they get displayed,
// sorted, and hidden.