import React from 'react';
import PropTypes from 'prop-types';
import { Panel, PanelBody, PanelHeading } from '../libs/ui/panel';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import Status from './status';
import { PanelLookup } from './objectutils';
import IHCTable from './ihcTable';

class PathologyReport extends React.Component {
    constructor(props) {
        super(props);
    }
    render() {
        const context = this.props.context;

        const itemClass = globals.itemClass(context, 'view-item');
        // Set up breadcrumbs
        const crumbs = [
            { id: 'pathology-reports' },
            { id: <i>{context.accession}</i> },
        ];
        const crumbsReleased = (context.status === 'released');

        let hasIHC=false;
        if (Object.keys(this.props.context.ihc).length > 0) {
              hasIHC = true;
          }


        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs root="/search/?type=PathologyReport" crumbs={crumbs} crumbsReleased={crumbsReleased} />
                        <h2>{context.accession}</h2>

                    </div>

                </header>
                <Panel>
                    <PanelHeading>
                        <h4>Pathology Report tumor information</h4>
                    </PanelHeading>
                    <PanelBody>

                        <dl className="key-value">
                            <div >
                                <div data-test="status">
                                    <dt>Status</dt>
                                    <dd><Status item={context.status} inline /></dd>
                                </div>
                                <div data-test="date">
                                    <dt>Pathology Report Date</dt>
                                    <dd>{context.date}</dd>
                                </div>
                                <div data-test="report_source">
                                    <dt>Pathology Report Source</dt>
                                    <dd>{context.report_source}</dd>
                                </div>
                                <div data-test="tumor_sequence_number">
                                    <dt>Pathology Report Tumor Sequence Number</dt>
                                    <dd>{context.tumor_sequence_number}</dd>
                                </div>
                                <div data-test="path_source_procedure">
                                    <dt>Pathology Diagnosis Source Type</dt>
                                    <dd>{context.path_source_procedure}</dd>
                                </div>
                            </div>

                            <div className="constainer" >
                                <div className="row" style={{ borderTop: "1px solid #151313" }}>
                                    <div className="col-lg-6 col-md-6  col-sm-12" >
                                        {context.laterality && <div data-test="laterality">
                                            <dt>Tumor Laterality</dt>
                                            <dd>{context.laterality}</dd>
                                        </div>}
                                        {context.focality && <div data-test="focality">
                                            <dt>Tumor Focality</dt>
                                            <dd>{context.focality}</dd>
                                        </div>}
                                        {context.tumor_size && <div data-test="tumor_size">
                                            <dt>Tumor Size</dt>
                                            <dd>{context.tumor_size}{context.tumor_size_units}</dd>
                                        </div>}
                                        {context.histology && <div data-test="histology">
                                            <dt>Tumor Histology Subtypes</dt>
                                            <dd>{context.histology}</dd>
                                        </div>}
                                        {context.sarcomatoid && <div data-test="sarcomatoid">
                                            <dt>Sarcomatoid Change</dt>
                                            <dd>{context.sarcomatoid}</dd>
                                        </div>}
                                        {context.sarcomatoid_percentage && <div data-test="sarcomatoid_percentage">
                                            <dt>Sarcomatoid Percentage</dt>
                                            <dd>{context.sarcomatoid_percentage}</dd>
                                        </div>}
                                        {context.rhabdoid && <div data-test="rhabdoid">
                                            <dt>Tumor Rhabdoid</dt>
                                            <dd>{context.rhabdoid}</dd>
                                        </div>}
                                        {context.necrosis && <div data-test="necrosis">
                                            <dt>Tumor Necrosis</dt>
                                            <dd>{context.necrosis}</dd>
                                        </div>}
                                        {context.grade && <div data-test="grade">
                                            <dt>Tumor Grade</dt>
                                            <dd>{context.grade}</dd>
                                        </div>}
                                        {context.margins && <div data-test="margins">
                                            <dt>Margin Status</dt>
                                            <dd>{context.margins}</dd>
                                        </div>}
                                        {context.lvi && <div data-test="lvi">
                                            <dt>Lymphvascular invasion(LVI)</dt>
                                            <dd>{context.lvi}</dd>
                                        </div>}
                                        {context.micro_limited && <div data-test="micro_limited">
                                            <dt>Renal Limited</dt>
                                            <dd>{context.micro_limited}</dd>
                                        </div>}
                                        {context.micro_vein && <div data-test="micro_vein">
                                            <dt>Renal Vein Involvement(MicroVein)</dt>
                                            <dd>{context.micro_vein}</dd>
                                        </div>}
                                        {context.micro_perinephric && <div data-test="micro_perinephric">
                                            <dt>Perinephric Infiltration</dt>
                                            <dd>{context.micro_perinephric}</dd>
                                        </div>}


                                    </div>


                                    <div className="col-lg-6 col-md-6  col-sm-12" >

                                        {context.micro_adrenal && <div data-test="micro_adrenal">
                                            <dt>Ipsilateral Adrenal Gland Involvement(MicroAdrenal)</dt>
                                            <dd>{context.micro_adrenal}</dd>
                                        </div>}{context.micro_sinus && <div data-test="micro_sinus">
                                            <dt>Renal Sinus Involvement(MicroSinus)</dt>
                                            <dd>{context.micro_sinus}</dd>
                                        </div>}
                                        {context.micro_gerota && <div data-test="micro_gerota">
                                            <dt>Gerotas Fascia Involvement(microGerota)</dt>
                                            <dd>{context.micro_gerota}</dd>
                                        </div>}
                                        {context.micro_pelvaliceal && <div data-test="micro_pelvaliceal">
                                            <dt>Pelvicaliceal Involvement(MicroPelvaliceal)</dt>
                                            <dd>{context.micro_pelvaliceal}</dd>
                                        </div>}
                                        {context.t_stage && <div data-test="t_stage">
                                            <dt>pT Stage</dt>
                                            <dd>{context.t_stage}</dd>
                                        </div>}

                                        {context.n_stage && <div data-test="n_stage">
                                            <dt>pN Stage</dt>
                                            <dd>{context.n_stage}</dd>
                                        </div>}
                                        {context.m_stage && <div data-test="m_stage">
                                            <dt>pM Stage</dt>
                                            <dd>{context.m_stage}</dd>
                                        </div>}

                                        {context.examined_lymph_nodes && <div data-test="examined_lymph_nodes">
                                            <dt>Examined Lymph Nodes</dt>
                                            <dd>{context.examined_lymph_nodes}</dd>
                                        </div>}

                                        {context.positive_lymph_nodes && <div data-test="positive_lymph_nodes">
                                            <dt>Positive Lymph Nodes</dt>
                                            <dd>{context.positive_lymph_nodes}</dd>
                                        </div>}



                                        {context.ajcc_version && <div data-test="ajcc_version">
                                            <dt>AJCC Version</dt>
                                            <dd>{context.ajcc_version}</dd>
                                        </div>}

                                        {context.ajcc_tnm_stage && <div data-test="ajcc_tnm_stage">
                                            <dt>AJCC TNM Stage</dt>
                                            <dd>{context.ajcc_tnm_stage}</dd>
                                        </div>}

                                        {context.ajcc_p_stage && <div data-test="ajcc_p_stage">
                                            <dt>AJCC pT stage</dt>
                                            <dd>{context.ajcc_p_stage}</dd>
                                        </div>}

                                    </div>
                                </div>

                            </div>


                            <div>
                                {context.metasis_details && <div data-test="metasis_details.site" style={{ borderTop: "1px solid #151313" }}>

                                    <dt>Metasis Details Site</dt>
                                    <dd>{context.metasis_details.site}</dd>
                                </div>}
                                {context.metasis_details && <div data-test="metasis_details.type">
                                    <dt>Metasis Details Type</dt>
                                    <dd>{context.metasis_details.type}</dd>
                                </div>}
                            </div>


                        </dl>
                    </PanelBody>
                    {/* {context.report_source && <div data-test="report_source">
                                <dt>Report source</dt>
                                <dd>{context.report_source}</dd>
                            </div>} */}
                </Panel>
                {hasIHC&&<IHCTable data={context.ihc} tableTitle="IHC Assay Staining Results"></IHCTable>}

            </div>
        )
    }

}


PathologyReport.propTypes = {
    context: PropTypes.object, // Target object to display
};

PathologyReport.defaultProps = {
    context: null,
};

globals.contentViews.register(PathologyReport, 'PathologyReport');

export default PathologyReport;
