import React from 'react';
import { Panel, PanelBody, PanelHeading } from '../libs/bootstrap/panel';
import Status from './status';
import CollapsiblePanel from './collapsiblePanel';


class PathologyReportTable extends React.Component {
    constructor(props) {
        super(props);
        this.filteredData = [];
        this.tableId = [];
    }

    filterData() {
        this.filteredData = this.props.data;
       

        for (let i = 0; i < this.filteredData.length; i++) {
            let tableTitle = this.props.tableTitle + "Tumor information" + " " + (i + 1);
            let tableIdi =
                (< div >

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
                                {this.filteredData[i].necrosis && <div data-test="necrosis">
                                    <dt>Necrosis</dt>
                                    <dd>{this.filteredData[i].necrosis}</dd>
                                </div>}
                                {this.filteredData[i].grade && <div data-test="grade">
                                    <dt>Grade</dt>
                                    <dd>{this.filteredData[i].grade}</dd>
                                </div>}
                                {this.filteredData[i].margins && <div data-test="margins">
                                    <dt>Margins</dt>
                                    <dd>{this.filteredData[i].margins}</dd>
                                </div>}
                                {this.filteredData[i].lvi && <div data-test="lvi">
                                    <dt>Lvi</dt>
                                    <dd>{this.filteredData[i].lvi}</dd>
                                </div>}
                                {this.filteredData[i].micro_limited && <div data-test="micro_limited">
                                    <dt>Micro-limited</dt>
                                    <dd>{this.filteredData[i].micro_limited}</dd>
                                </div>}
                                {this.filteredData[i].micro_vein && <div data-test="micro_vein">
                                    <dt>Micro-vein</dt>
                                    <dd>{this.filteredData[i].micro_vein}</dd>
                                </div>}
                                {this.filteredData[i].micro_perinephric && <div data-test="micro_perinephric">
                                    <dt>Micro-perinephric</dt>
                                    <dd>{this.filteredData[i].micro_perinephric}</dd>
                                </div>}
                                {this.filteredData[i].micro_adrenal && <div data-test="micro_adrenal">
                                    <dt>Micro-adrenal</dt>
                                    <dd>{this.filteredData[i].micro_adrenal}</dd>
                                </div>}
                                {this.filteredData[i].micro_sinus && <div data-test="micro_sinus">
                                    <dt>Micro-sinus</dt>
                                    <dd>{this.filteredData[i].micro_sinus}</dd>
                                </div>}
                                {this.filteredData[i].micro_gerota && <div data-test="micro_gerota">
                                    <dt>Micro-gerota</dt>
                                    <dd>{this.filteredData[i].micro_gerota}</dd>
                                </div>}

                                {this.filteredData[i].micro_pelvaliceal && <div data-test="micro_pelvaliceal">
                                    <dt>Micro-pelvaliceal</dt>
                                    <dd>{this.filteredData[i].micro_pelvaliceal}</dd>
                                </div>}

                                {this.filteredData[i].t_stage && <div data-test="t_stage">
                                    <dt>T stage</dt>
                                    <dd>{this.filteredData[i].t_stage}</dd>
                                </div>}

                                {this.filteredData[i].n_stage && <div data-test="n_stage">
                                    <dt>N stage</dt>
                                    <dd>{this.filteredData[i].n_stage}</dd>
                                </div>}

                                {this.filteredData[i].examined_lymph_nodes && <div data-test="examined_lymph_nodes">
                                    <dt>Examined lymph nodes</dt>
                                    <dd>{this.filteredData[i].examined_lymph_nodes}</dd>
                                </div>}

                                {this.filteredData[i].positive_lymph_nodes && <div data-test="positive_lymph_nodes">
                                    <dt>Positive lymph nodes</dt>
                                    <dd>{this.filteredData[i].positive_lymph_nodes}</dd>
                                </div>}

                                {this.filteredData[i].m_stage && <div data-test="m_stage">
                                    <dt>M stage</dt>
                                    <dd>{this.filteredData[i].m_stage}</dd>
                                </div>}

                                {this.filteredData[i].ajcc_version && <div data-test="ajcc_version">
                                    <dt>Ajcc version</dt>
                                    <dd>{this.filteredData[i].ajcc_version}</dd>
                                </div>}

                                {this.filteredData[i].ajcc_tnm_stage && <div data-test="ajcc_tnm_stage">
                                    <dt>Ajcc tnm stage</dt>
                                    <dd>{this.filteredData[i].ajcc_tnm_stage}</dd>
                                </div>}

                                {this.filteredData[i].ajcc_p_stage && <div data-test="ajcc_p_stage">
                                    <dt>Ajcc pT stage</dt>
                                    <dd>{this.filteredData[i].ajcc_p_stage}</dd>
                                </div>}

                                {this.filteredData[i].report_source && <div data-test="report_source">
                                    <dt>Report source</dt>
                                    <dd>{this.filteredData[i].report_source}</dd>
                                </div>}
                            </dl>
                        </PanelBody>
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
