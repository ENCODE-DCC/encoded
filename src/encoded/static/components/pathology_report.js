import React from 'react';
import PropTypes from 'prop-types';
import { Panel, PanelBody, PanelHeading } from '../libs/bootstrap/panel';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import Status from './status';
import { PanelLookup } from './objectutils';

class PathologyReport extends React.Component {
    constructor(props) {
        super(props);
    }
    render() {
        const context = this.props.context;
        console.log(context);

        const itemClass = globals.itemClass(context, 'view-item');
        // Set up breadcrumbs
        const crumbs = [
            { id: 'pathology-reports' },
            { id: <i>{context.name}</i> },
        ];
        const crumbsReleased = (context.status === 'released');

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs root="/search/?type=PathologyReport" crumbs={crumbs} crumbsReleased={crumbsReleased} />
                        <h2>{context.name}</h2>

                    </div>

                </header>
                <Panel>
                    <PanelHeading>
                        <h4>{this.props.chartTitle}</h4>
                    </PanelHeading>
                    <PanelBody>
                        <dl className="key-value">
                            <div data-test="status">
                                <dt>Status</dt>
                                <dd><Status item={context} inline /></dd>
                            </div>
                            <div data-test="surgery">
                                <dt>Surgery</dt>
                                <dd><a href={context.surgery}>{context.surgery.split("/")[2]}</a></dd>
                            </div>
                            <div data-test="date">
                                <dt>Date</dt>
                                <dd>{context.date}</dd>
                            </div>
                            <div data-test="laterality">
                                <dt>Laterality</dt>
                                <dd>{context.laterality}</dd>
                            </div>
                            <div data-test="tumor_size">
                                <dt>Tumor_size</dt>
                                <dd>{context.tumor_size}{context.tumor_size_units}</dd>
                            </div>

                            <div data-test="focality">
                                <dt>Focality</dt>
                                <dd>{context.focality}</dd>
                            </div>
                            <div data-test="histology">
                                <dt>Histology</dt>
                                <dd>{context.histology}</dd>
                            </div>
                            <div data-test="sarcomatoid">
                                <dt>Sarcomatoid</dt>
                                <dd>{context.sarcomatoid}</dd>
                            </div>
                            <div data-test="sarcomatoid_percentage">
                                <dt>Sarcomatoid_percentage</dt>
                                <dd>{context.sarcomatoid_percentage}</dd>
                            </div>
                            <div data-test="rhabdoid">
                                <dt>Rhabdoid</dt>
                                <dd>{context.rhabdoid}</dd>
                            </div>

                            {context.necrosis && <div data-test="necrosis">
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
                                <dt>AJCC version</dt>
                                <dd>{context.ajcc_version}</dd>
                            </div>}

                            {context.ajcc_tnm_stage && <div data-test="ajcc_tnm_stage">
                                <dt>AJCC tnm stage</dt>
                                <dd>{context.ajcc_tnm_stage}</dd>
                            </div>}

                            {context.ajcc_p_stage && <div data-test="ajcc_p_stage">
                                <dt>AJCC p stage</dt>
                                <dd>{context.ajcc_p_stage}</dd>
                            </div>}

                            {context.report_source && <div data-test="report_source">
                                <dt>Report source</dt>
                                <dd>{context.report_source}</dd>
                            </div>}
                          
                        </dl>
                    </PanelBody>
                </Panel>
               
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