/* eslint-disable linebreak-style */
// eslint-disable-next-line linebreak-style
import React from 'react';
import { SortTablePanel, SortTable } from './sorttable';

class GermlineTable extends React.Component {
    constructor(props) {
        super(props);
        this.germlineFilters = [];
        this.transformData = [];
    }

    filterData() {
        this.germlineFilters = this.props.data.filter(i => (i.significance === 'Positive' || i.significance === 'Variant' || i.significance === 'Positive and Variant'));
        this.transformData = this.germlineFilters.map(i => ({ target: i.target, significance: i.significance }));
    }


    renderData() {
        if (!Array.isArray(this.props.data) || !this.props.data.length) {
            return (<SortTablePanel title={this.props.tableTitle}>
                        <div className="table-body"><h5>Germline mutation data is not available!</h5></div>
                    </SortTablePanel>
            );
        }
        if (this.transformData.length>0) {
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
        return (<SortTablePanel title={this.props.tableTitle}>
                    <div className="table-body"><h5>No Positive for mutations!</h5></div>
                </SortTablePanel>
         );
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
