/* eslint-disable linebreak-style */
// eslint-disable-next-line linebreak-style
import React from 'react';
import { SortTablePanel, SortTable } from './sorttable';

class GenomicsTable extends React.Component {
    constructor(props) {
        super(props);
        this.library = this.transformData(this.props.data);
    }

    transformData(data) {
        let biolibrary = [];
        let index = 0;
        for (let i = 0; i < data.length; i++) {
            
            for (let j = 0; j < data[i].biofile.length; j++) {
                let obj = {
                    library_accession: data[i].accession,
                    library_id: data[i]['@id'],
                    library_nucleic_acid_term_name: data[i].nucleic_acid_term_name,
                    library_biological_replicate_number: data[i].biological_replicate_number,
                    library_technical_replicate_number: data[i].technical_replicate_number,
                    file_accession: data[i].biofile[j].accession,
                    file_run_type: data[i].biofile[j].run_type,
                    file_output_type: data[i].biofile[j].output_type,
                    file_size: data[i].biofile[j].file_size,
                    sequencing_replicate_number: data[i].biofile[j].sequencing_replicate_number,
                    file_format: data[i].biofile[j].file_format,
                    file_id: data[i].biofile[j]['@id'],
                };
                
                biolibrary[index] = obj;
                index++;

            }
        }
        return biolibrary;
    }

    renderData() {
       
            const tableColumns = {
                library_accession: {
                    title: 'Library',
                    
                },
                library_nucleic_acid_term_name: {
                    title: 'Library type',
                },
                file_accession: {
                    title: 'File',
                    display: biolibrary => <a href={biolibrary.file_id}>{biolibrary.file_accession}</a>,
                },
                library_biological_replicate_number: {
                    title: 'Biological replicate number',
                },
                library_technical_replicate_number: {
                    title: 'Technical replicate number',
                },
                sequencing_replicate_number: {
                    title: 'Sequencing replicate number',
                },
                file_format: {
                    title: 'File format',
                },
                file_size: {
                    title: 'File size',
                },
                file_run_type: {
                    title: 'File run type',
                },
                file_output_type: {
                    title: 'File output type',
                },
          
            };
            return (
                <SortTablePanel title={this.props.tableTitle}>
                    <SortTable list={this.library} columns={tableColumns} />
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

export default GenomicsTable;
