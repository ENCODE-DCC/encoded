import React from 'react';
import { Panel, PanelBody, PanelHeading } from '../libs/ui/panel';
import Status from './status';
import CollapsiblePanel from './collapsiblePanel';
import IHCTable from './ihcTable';


class PathologyReportTable extends React.Component {
    constructor(props) {
        super(props);
        this.filteredData = [];
        this.tableId = [];
    }

    filterData() {
        this.filteredData = this.props.data;
        for (let i = 0; i < this.filteredData.length; i++) {
            let pathologyReporti = this.filteredData[i];
            let IHCi = pathologyReporti.ihc;
            let hasIHC = false;
            if (IHCi.length > 0) {
                hasIHC = true;
            }
            let tableTitle = this.props.tableTitle + "Tumor information" + " " + (i + 1);
            let tableIdi =
                (< div >

                    <PanelBody>
                        <dl className="key-value">
                            <div >
                                <div data-test="status">
                                    <dt>Status</dt>
                                    <dd><Status item={this.filteredData[i].status} inline /></dd>
                                </div>
                                <div data-test="date">
                                    <dt>Pathology Report Date</dt>
                                    <dd>{this.filteredData[i].date}</dd>
                                </div>
                                <div data-test="report_source">
                                    <dt>Pathology Report Source</dt>
                                    <dd>{this.filteredData[i].report_source}</dd>
                                </div>
                                <div data-test="tumor_sequence_number">
                                    <dt>Pathology Report Tumor Sequence Number</dt>
                                    <dd>{this.filteredData[i].tumor_sequence_number}</dd>
                                </div>
                                <div data-test="path_source_procedure">
                                    <dt>Pathology Diagnosis Source Type</dt>
                                    <dd>{this.filteredData[i].path_source_procedure}</dd>
                                </div>
                            </div>

                            <div className="constainer" >
                                <div className="row" style={{ borderTop: "1px solid #151313" }}>
                                    <div className="col-lg-6 col-md-6  col-sm-12">
                                        {this.filteredData[i].laterality && <div data-test="laterality">
                                            <dt>Tumor Laterality</dt>
                                            <dd>{this.filteredData[i].laterality}</dd>
                                        </div>}
                                        {this.filteredData[i].focality && <div data-test="focality">
                                            <dt>Tumor Focality</dt>
                                            <dd>{this.filteredData[i].focality}</dd>
                                        </div>}
                                        {this.filteredData[i].tumor_size && <div data-test="tumor_size">
                                            <dt>Tumor Size</dt>
                                            <dd>{this.filteredData[i].tumor_size}{this.filteredData[i].tumor_size_units}</dd>
                                        </div>}
                                        {this.filteredData[i].histology && <div data-test="histology">
                                            <dt>Tumor Histology Subtypes</dt>
                                            <dd>{this.filteredData[i].histology}</dd>
                                        </div>}
                                        {this.filteredData[i].sarcomatoid && <div data-test="sarcomatoid">
                                            <dt>Sarcomatoid Change</dt>
                                            <dd>{this.filteredData[i].sarcomatoid}</dd>
                                        </div>}
                                        {this.filteredData[i].sarcomatoid_percentage && <div data-test="sarcomatoid_percentage">
                                            <dt>Sarcomatoid Percentage</dt>
                                            <dd>{this.filteredData[i].sarcomatoid_percentage}</dd>
                                        </div>}
                                        {this.filteredData[i].rhabdoid && <div data-test="rhabdoid">
                                            <dt>Tumor Rhabdoid</dt>
                                            <dd>{this.filteredData[i].rhabdoid}</dd>
                                        </div>}
                                        {this.filteredData[i].necrosis && <div data-test="necrosis">
                                            <dt>Tumor Necrosis</dt>
                                            <dd>{this.filteredData[i].necrosis}</dd>
                                        </div>}
                                        {this.filteredData[i].grade && <div data-test="grade">
                                            <dt>Tumor Grade</dt>
                                            <dd>{this.filteredData[i].grade}</dd>
                                        </div>}
                                        {this.filteredData[i].margins && <div data-test="margins">
                                            <dt>Margin Status</dt>
                                            <dd>{this.filteredData[i].margins}</dd>
                                        </div>}
                                        {this.filteredData[i].lvi && <div data-test="lvi">
                                            <dt>Lymphvascular invasion(LVI)</dt>
                                            <dd>{this.filteredData[i].lvi}</dd>
                                        </div>}
                                        {this.filteredData[i].micro_limited && <div data-test="micro_limited">
                                            <dt>Renal Limited</dt>
                                            <dd>{this.filteredData[i].micro_limited}</dd>
                                        </div>}
                                        {this.filteredData[i].micro_vein && <div data-test="micro_vein">
                                            <dt>Renal Vein Involvement(MicroVein)</dt>
                                            <dd>{this.filteredData[i].micro_vein}</dd>
                                        </div>}
                                        {this.filteredData[i].micro_perinephric && <div data-test="micro_perinephric">
                                            <dt>Perinephric Infiltration</dt>
                                            <dd>{this.filteredData[i].micro_perinephric}</dd>
                                        </div>}


                                    </div>


                                    <div className="col-lg-6 col-md-6  col-sm-12" >

                                        {this.filteredData[i].micro_adrenal && <div data-test="micro_adrenal">
                                            <dt>Ipsilateral Adrenal Gland Involvement(MicroAdrenal)</dt>
                                            <dd>{this.filteredData[i].micro_adrenal}</dd>
                                        </div>}{this.filteredData[i].micro_sinus && <div data-test="micro_sinus">
                                            <dt>Renal Sinus Involvement(MicroSinus)</dt>
                                            <dd>{this.filteredData[i].micro_sinus}</dd>
                                        </div>}
                                        {this.filteredData[i].micro_gerota && <div data-test="micro_gerota">
                                            <dt>Gerotas Fascia Involvement(microGerota)</dt>
                                            <dd>{this.filteredData[i].micro_gerota}</dd>
                                        </div>}
                                        {this.filteredData[i].micro_pelvaliceal && <div data-test="micro_pelvaliceal">
                                            <dt>Pelvicaliceal Involvement(MicroPelvaliceal)</dt>
                                            <dd>{this.filteredData[i].micro_pelvaliceal}</dd>
                                        </div>}
                                        {this.filteredData[i].t_stage && <div data-test="t_stage">
                                            <dt>pT Stage</dt>
                                            <dd>{this.filteredData[i].t_stage}</dd>
                                        </div>}

                                        {this.filteredData[i].n_stage && <div data-test="n_stage">
                                            <dt>pN Stage</dt>
                                            <dd>{this.filteredData[i].n_stage}</dd>
                                        </div>}
                                        {this.filteredData[i].m_stage && <div data-test="m_stage">
                                            <dt>pM Stage</dt>
                                            <dd>{this.filteredData[i].m_stage}</dd>
                                        </div>}

                                        {this.filteredData[i].examined_lymph_nodes && <div data-test="examined_lymph_nodes">
                                            <dt>Examined Lymph Nodes</dt>
                                            <dd>{this.filteredData[i].examined_lymph_nodes}</dd>
                                        </div>}

                                        {this.filteredData[i].positive_lymph_nodes && <div data-test="positive_lymph_nodes">
                                            <dt>Positive Lymph Nodes</dt>
                                            <dd>{this.filteredData[i].positive_lymph_nodes}</dd>
                                        </div>}



                                        {this.filteredData[i].ajcc_version && <div data-test="ajcc_version">
                                            <dt>AJCC Version</dt>
                                            <dd>{this.filteredData[i].ajcc_version}</dd>
                                        </div>}

                                        {this.filteredData[i].ajcc_tnm_stage && <div data-test="ajcc_tnm_stage">
                                            <dt>AJCC TNM Stage</dt>
                                            <dd>{this.filteredData[i].ajcc_tnm_stage}</dd>
                                        </div>}

                                        {this.filteredData[i].ajcc_p_stage && <div data-test="ajcc_p_stage">
                                            <dt>AJCC pT stage</dt>
                                            <dd>{this.filteredData[i].ajcc_p_stage}</dd>
                                        </div>}

                                    </div>
                                </div>

                            </div>


                            <div>
                                {this.filteredData[i].metasis_details && <div data-test="metasis_details.site" style={{ borderTop: "1px solid #151313" }}>

                                    <dt>Metasis Details Site</dt>
                                    <dd>{this.filteredData[i].metasis_details.site}</dd>
                                </div>}
                                {this.filteredData[i].metasis_details && <div data-test="metasis_details.type">
                                    <dt>Metasis Details Type</dt>
                                    <dd>{this.filteredData[i].metasis_details.type}</dd>
                                </div>}
                            </div>


                        </dl>
                    </PanelBody>
                    {hasIHC && <IHCTable data={IHCi} tableTitle="IHC Assay Staining Results"></IHCTable>}

                </div >
                )

            let collapTablei = (<CollapsiblePanel panelId={i} title={tableTitle} content={tableIdi} ></CollapsiblePanel>);
            this.tableId.push(collapTablei);
        }
    }


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
    }


}
export default PathologyReportTable;
