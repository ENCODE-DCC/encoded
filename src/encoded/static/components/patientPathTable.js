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

        for (let i = 0; i < data.length; i++) {
            let obj1 = {
                surgery_accession: data[i].accession,
                surgery_id: data[i]['@id'],
                surgery_date: data[i].date,
            }
            if (data[i].surgery_procedure.length > 0){
                let procedure_type = data[i].surgery_procedure[0].procedure_type;
                for (let j = 1; j < data[i].surgery_procedure.length; j++) {
                    procedure_type += ", " + data[i].surgery_procedure[j].procedure_type;
                }
                obj1.procedure_type = procedure_type
            }
            if (data[i].pathology_report.length > 0) {
                for (let j = 0; j < data[i].pathology_report.length; j++) {
                    let obj2 = {
                        surgery_accession: obj1.surgery_accession,
                        surgery_id: obj1.surgery_id,
                        surgery_date: obj1.surgery_date,
                        procedure_type: obj1.procedure_type,
                        path_accession: data[i].pathology_report[j].accession,
                        path_id: data[i].pathology_report[j]['@id'],
                        path_histology: data[i].pathology_report[j].histology,
                        t_stage: data[i].pathology_report[j].t_stage,
                        n_stage: data[i].pathology_report[j].n_stage,
                        m_stage: data[i].pathology_report[j].m_stage,
                    }
                    

                
                
                     surgeryData[index] = obj2;
                     index++;

                }
                
            } else {
                surgeryData[index] = obj1;
                index++;
            }

        }
        return surgeryData;
    }

    renderData() {
       
            const tableColumns = {
                surgery_date: {
                    title: 'Surgery Date',
                },
                surgery_accession: {
                    title: 'Surgery',
                    display: surgeryData => <a href={surgeryData.surgery_id}>{surgeryData.surgery_accession}</a>,
                },
                procedure_type: {
                    title: 'Procedure Type',
                },

                path_accession: {
                    title: 'Pathology Report',
                    display: surgeryData => <a href={surgeryData.path_id}>{surgeryData.path_accession}</a>,
                },
                path_histology: {
                    title: 'Histologic Subtype',
                },
                t_stage: {
                    title: 'pT Stage',
                },
                n_stage: {
                    title: 'pN Stage',
                },
                m_stage: {
                    title: 'pM Stage',
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



