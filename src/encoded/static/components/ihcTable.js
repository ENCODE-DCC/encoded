/* eslint-disable linebreak-style */
// eslint-disable-next-line linebreak-style
import React from 'react';
import { SortTablePanel, SortTable } from './sorttable';

class IHCTable extends React.Component {
    constructor(props) {
        super(props);
        this.ihcFilters = [];
    }

    filterData() {
        this.ihcFilters = this.props.data.map(i =>({ "IHC antibody": i.antibody, "result": i.result }) ) ;
        console.log("IHCfilter",this.ihcFilters);
    }


    renderData() {
        
        if (this.ihcFilters.length>0) {
            const ihcTableColumns = {
                "IHC antibody": {
                    title: ' Staining Antibody',
                },
                "result": {
                    title: 'Assay Result',
                },
            };
            return (
                <SortTablePanel title={this.props.tableTitle}>
                    <SortTable list={this.ihcFilters} columns={ihcTableColumns} />
                </SortTablePanel>
            );
        }
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

export default IHCTable;
