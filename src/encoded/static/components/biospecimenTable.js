/* eslint-disable linebreak-style */
// eslint-disable-next-line linebreak-style
import React from 'react';
import { SortTablePanel, SortTable } from './sorttable';

class BiospecimenTable extends React.Component {
    constructor(props) {
        super(props);
        
    }

    renderData() {
       
            const germlineTableColumns = {
                accession: {
                    title: 'Accession',
                    display: biospecimen => <a href={biospecimen['@id']}>{biospecimen.accession}</a>,
                },
                openspecimen_ID: {
                    title: 'OpenSpecimen ID',
                },
                collection_type: {
                    title: 'Collection type',
                },
                processing_type: {
                    title: 'Processing type',
                },
                tissue_type: {
                    title: 'Tissue type',
                },
                anatomic_site: {
                    title: 'Anatomic site',
                },
                primary_site: {
                    title: "Primary site",
                },
                host: {
                    title: "Host",
                },
                distributed: {
                    title: 'Distributed?',
                },
            };
            return (
                <SortTablePanel title={this.props.tableTitle}>
                    <SortTable list={this.props.data} columns={germlineTableColumns} />
                </SortTablePanel>
            );
        
        
    }

    render() {
        return (
            <div> {this.renderData()}</div>
        );
    }

    componentDidMount() {
        
        this.renderData();
    }

}

export default BiospecimenTable;