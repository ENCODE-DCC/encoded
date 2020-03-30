/* eslint-disable linebreak-style */
// eslint-disable-next-line linebreak-style
import React from 'react';
import { SortTablePanel, SortTable } from './sorttable';

class patientPathTable extends React.Component {
    constructor(props) {
        super(props);
        this.surgery = this.transformData(this.props.data);
    }

    transformData(data) {
        let surgeryData = [];
        let index = 0;
        let obj = {};
        for (let i = 0; i < data.length; i++) {
            obj = {
                surgery_accession: data[i].accession,
                surgery_id: data[i]['@id'],
                surgery_date: data[i].date,
            }
            if (data[i].pathology_report.length > 0) {
                for (let j = 0; j < data[i].pathology_report.length; j++) {

                    obj.path_accession = data[i].pathology_report[j].accession;
                    obj.path_id = data[i].pathology_report[j]['@id'];
                    obj.path_histology = data[i].pathology_report[j].histology;
                    obj.t_stage = data[i].pathology_report[j].t_stage;
                    obj.n_stage = data[i].pathology_report[j].n_stage;
                    obj.m_stage = data[i].pathology_report[j].m_stage;

                
                
                     surgeryData[index] = obj;
                     index++;

                }
                
            } else {
                surgeryData[index] = obj;
                index++;
            }

        }
        return surgeryData;
    }

    renderData() {
       
            const tableColumns = {
                surgery_date: {
                    title: 'Surgery date',
                },
                surgery_accession: {
                    title: 'Surgery',
                    display: surgeryData => <a href={surgeryData.surgery_id}>{surgeryData.surgery_accession}</a>,
                },

                path_accession: {
                    title: 'Pathology report',
                    display: surgeryData => <a href={surgeryData.path_id}>{surgeryData.path_accession}</a>,
                },
                path_histology: {
                    title: 'Histologic Subtype',
                },
                t_stage: {
                    title: 'pT stage',
                },
                n_stage: {
                    title: 'pN stage',
                },
                m_stage: {
                    title: 'pM stage',
                },

          
            };
            return (
                <SortTablePanel title={this.props.tableTitle}>
                    <SortTable list={this.surgery} columns={tableColumns} />
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

export default patientPathTable;

