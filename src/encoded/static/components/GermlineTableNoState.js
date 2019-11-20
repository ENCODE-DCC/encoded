/* eslint-disable linebreak-style */
// eslint-disable-next-line linebreak-style
import React from 'react';
import { SortTablePanel, SortTable } from './sorttable';

class GermlineTableNoState extends React.Component {
    constructor(props) {
        super(props);
        // this.state = {
        //     showData: true,
        // };
        //this.tableConfig = {};
        this.data = this.props.data;
        //this.zingchart = window.zingchart;
        this.germlineFilters = [];
        this.transferData = [];
    }

    render() {
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
        } else {
             this.germlineFilters = this.data.filter(i => (i.significance === 'Positive' || i.significance === 'Variant' || i.significance === 'Positive and Variant'));;
            //this.transferData = this.germlineFilters.map(i => ({ values: [i.target, i.significance] }));
            //this.transferData = this.germlineFilters.map(i => ({ "target": i.target, "significance": i.significance}));
            this.transferData = this.germlineFilters.map(i => (
                    // { target:{ 
                    //     title: 'Target',
                    //     display: i.target
                    //     }, 
                    // significance:{ 
                    //     title: 'Significance', 
                    //     display: i.significance
                    //     }
                    // }));

            //this.data = this.props.data;
            console.log(this.data);
            console.log(this.transferData);
            //console.log(this.germlineFilters);
            // this.transferData=[{target: "VHL", significance: "Positive"}]
            
                if(this.transferData){
                    // for(let i=0; i<this.transferData.length;i++){
                    //     const transferDataColumns = {
                    //         target : {
                    //             title: 'Target',
                    //             //getValue: this.transferData[i] => this.transferData[i].target,
                    //             getValue: this.transferData[i] => return this.transferData[i].target,
                    //         },
                    //         significance: {
                    //             title: 'Significance',
                    //             getValue: this.transferData[i] => this.transferData[i].significance,
                    //         }
                    //     };
                    // } 
                
               //this.transferData=[{"target":"vhl", "significance": "positive"},{"target":"bca1", "significance": "Positive and Variant"}]
                //let list=[{"target":vhl, "significance": positive}]
                //let columns={}
                
                // for(let i=0;i<this.transferData.length, i++;)
                // {
                   
                   return ( <SortTablePanel  title={this.props.tableTitle} >
                            <SortTable   list={this.transferData}  columns={this.transferData[0]}></SortTable>
                        </SortTablePanel>)
                    //columnsSet.push();
                    
            } else {
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
        }
    }
}

export default GermlineTableNoState;
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