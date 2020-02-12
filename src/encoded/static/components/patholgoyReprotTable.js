import React from 'react';
import { Panel, PanelBody, PanelHeading } from '../libs/bootstrap/panel';
import Status from './status';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';

class PathologyReportTable extends React.Component {
    constructor(props) {
        super(props);
        this.filteredData = [];
        this.tableId=[];
        // this.transformData = [];
    }

    filterData() {
        this.filteredData = this.props.data;
        console.log(this.filteredData);
        // this.filteredData.filter(i => i.patholgogy_report);
        // this.tableId=[];

        for (let i = 0; i < this.filteredData.length; i++) {
           let tableIdi = 
                (< div >
                    <Panel>
                        <PanelHeading>
                            <h4>{this.props.tableTitle}{i + 1}</h4>
                        </PanelHeading>
                        <PanelBody>
                            <dl className="key-value">
                                <div data-test="status">
                                    <dt>Status</dt>
                                    <dd><Status item={this.filteredData[i].status} inline /></dd>
                                </div>

                                <div data-test="date">
                                    <dt>Pathology Report Date</dt>
                                    <dd>{this.filteredData[i].date}</dd>
                                </div>
                                <div data-test="laterality">
                                    <dt>Laterality</dt>
                                    <dd>{this.filteredData[i].laterality}</dd>
                                </div>
                                <div data-test="tumor_size">
                                    <dt>Tumor_size</dt>
                                    <dd>{this.filteredData[i].tumor_size}{this.filteredData[i].tumor_size_units}</dd>
                                </div>
                                {/* <div data-test="tumor_size_units">
                                <dt>Tumor_size_units</dt>
                                <dd></dd>
                            </div> */}
                                <div data-test="focality">
                                    <dt>Focality</dt>
                                    <dd>{this.filteredData[i].focality}</dd>
                                </div>
                                <div data-test="histology">
                                    <dt>Histology</dt>
                                    <dd>{this.filteredData[i].histology}</dd>
                                </div>
                                <div data-test="sarcomatoid">
                                    <dt>Sarcomatoid</dt>
                                    <dd>{this.filteredData[i].sarcomatoid}</dd>
                                </div>
                                <div data-test="sarcomatoid_percentage">
                                    <dt>Sarcomatoid_percentage</dt>
                                    <dd>{this.filteredData[i].sarcomatoid_percentage}</dd>
                                </div>
                                <div data-test="rhabdoid">
                                    <dt>Rhabdoid</dt>
                                    <dd>{this.filteredData[i].rhabdoid}</dd>
                                </div>


                                {/* {context.originated_from && <div data-test="originated_from">
                                <dt>Originated From</dt>
                                <dd><a href={context.originated_from}>{context.originated_from.split("/")[2]}</a></dd>
                            </div>} */}

                                {/* {context.necrosis && <div data-test="necrosis">
                                <dt>Necrosis</dt>
                                <dd>{context.necrosis}</dd>
                            </div>}
                            {context.grade && <div data-test="grade">
                                <dt>Grade</dt>
                                <dd>{context.grade}</dd>
                            </div>}
                            {context.margins && <div data-test="margins">
                                <dt>Margins</dt>
                                <dd>{context.margins}</dd>
                            </div>}
                            {context.lvi && <div data-test="lvi">
                                <dt>Lvi</dt>
                                <dd>{context.lvi}</dd>
                            </div>}
                            {context.micro_limited && <div data-test="micro_limited">
                                <dt>Micro-limited</dt>
                                <dd>{context.micro_limited}</dd>
                            </div>}
                            {context.micro_vein && <div data-test="micro_vein">
                                <dt>Micro-vein</dt>
                                <dd>{context.micro_vein}</dd>
                            </div>}
                            {context.micro_perinephric && <div data-test="micro_perinephric">
                                <dt>Micro-perinephric</dt>
                                <dd>{context.micro_perinephric}</dd>
                            </div>}
                            {context.micro_adrenal && <div data-test="micro_adrenal">
                                <dt>Micro-adrenal</dt>
                                <dd>{context.micro_adrenal}</dd>
                            </div>}
                            {context.micro_sinus && <div data-test="micro_sinus">
                                <dt>Micro-sinus</dt>
                                <dd>{context.micro_sinus}</dd>
                            </div>}
                            {context.micro_gerota && <div data-test="micro_gerota">
                                <dt>Micro-gerota</dt>
                                <dd>{context.micro_gerota}</dd>
                            </div>}
    
                            {context.micro_pelvaliceal && <div data-test="micro_pelvaliceal">
                                <dt>Micro-pelvaliceal</dt>
                                <dd>{context.micro_pelvaliceal}</dd>
                            </div>}
    
                            {context.t_stage && <div data-test="t_stage">
                                <dt>T stage</dt>
                                <dd>{context.t_stage}</dd>
                            </div>}
    
                            {context.n_stage && <div data-test="n_stage">
                                <dt>N stage</dt>
                                <dd>{context.n_stage}</dd>
                            </div>}
    
                            {context.examined_lymph_nodes && <div data-test="examined_lymph_nodes">
                                <dt>Examined lymph nodes</dt>
                                <dd>{context.examined_lymph_nodes}</dd>
                            </div>}
    
                            {context.positive_lymph_nodes && <div data-test="positive_lymph_nodes">
                                <dt>Positive lymph nodes</dt>
                                <dd>{context.positive_lymph_nodes}</dd>
                            </div>}
    
                            {context.m_stage && <div data-test="m_stage">
                                <dt>M stage</dt>
                                <dd>{context.m_stage}</dd>
                            </div>}
    
                            {context.ajcc_version && <div data-test="ajcc_version">
                                <dt>Ajcc version</dt>
                                <dd>{context.ajcc_version}</dd>
                            </div>}
    
                            {context.ajcc_tnm_stage && <div data-test="ajcc_tnm_stage">
                                <dt>Ajcc tnm stage</dt>
                                <dd>{context.ajcc_tnm_stage}</dd>
                            </div>}
    
                            {context.ajcc_p_stage && <div data-test="ajcc_p_stage">
                                <dt>Ajcc p stage</dt>
                                <dd>{context.ajcc_p_stage}</dd>
                            </div>}
    
                            {context.report_source && <div data-test="report_source">
                                <dt>Report source</dt>
                                <dd>{context.report_source}</dd>
                            </div>} */}
                                {/* {context.report_source && <div data-test="report_source">
                                <dt>report_source</dt>
                                <dd><a href={context.report_source}>{context.report_source}</a></dd>
                            </div>} */}
                            </dl>
                        </PanelBody>
                    </Panel>
                    {/* { hasGenomics && <GenomicsTable data={context.biolibrary} tableTitle="Genomics for this specimen"></GenomicsTable>}
    
                    {false &&
                        <div>
                            {PanelLookup({ context: context.patient, Pathology_report: context })}
                        </div>} */}
                </div >)
        this.tableId.push(tableIdi);
    }
}

// renderData() {
//     return (
//         <div>
//             <div> {this.props.tableTitle}</div>
//             {/* <div>{this.filteredData[i][0]}</div> */}
//         </div>);

// }

render() {
    return (
        <div className="flex-container" >

            <div className="chart-main" >
    <div>{this.tableId}</div>
            </div>
        </div>

    );
}


componentDidMount() {
    this.filterData();
    // this.renderData();
}


}
export default PathologyReportTable;
