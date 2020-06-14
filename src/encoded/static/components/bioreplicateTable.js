/* eslint-disable linebreak-style */
// eslint-disable-next-line linebreak-style
import React from 'react';
import { SortTablePanel, SortTable } from './sorttable';

class BioreplicateTable extends React.Component {
    constructor(props) {
        super(props);
        this.bioreplicateFilters = [];
    }

    filterData() {
        console.log(this.props.data);//data is replicates is array.So we can use map.
        this.bioreplicateFilters = this.props.data.map(i => ({

            "Biological_replicate_number": i.biological_replicate_number,
            "Technical_replicate_number": i.technical_replicate_number,
            "Library summary": i.biolibrary.nucleic_acid_term_name,
            "Biospecimen accession": i.biolibrary.biospecimen.accession,
            "library accession": i.biolibrary.accession,

        }));
        console.log("bioreplicateFilters",this.bioreplicateFilters);

    }


    renderData() {

        if (this.bioreplicateFilters.length > 0) {
            const bioreplicateTableColumns = {
                "Biological_replicate_number": {
                    title: ' Biological replicate',
                },
                "Technical_replicate_number": {
                    title: 'Technical replicate',
                },
                "Library summary": {
                    title: 'Summary',
                },
                "Biospecimen accession": {
                    title: 'Biospecimen',
                },
                "Library accession": {
                    title: 'Library',
                },
            };
            return (
                <SortTablePanel title={this.props.tableTitle}>
                    <SortTable list={this.bioreplicateFilters} columns={bioreplicateTableColumns} />
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

export default BioreplicateTable;
