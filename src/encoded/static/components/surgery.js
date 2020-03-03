import React from 'react';
import PropTypes from 'prop-types';
import { Panel, PanelBody, PanelHeading } from '../libs/bootstrap/panel';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import Status from './status';
import { PanelLookup } from './objectutils';
import CollapsiblePanel from './collapsiblePanel';
import PathologyReportTable from './patholgoyReprotTable';
import IHCTable from './ihcTable';



class Surgery extends React.Component {
    constructor(props) {
        super(props);
    }
    render() {
        const context = this.props.context;
        const itemClass = globals.itemClass(context, 'view-item');

        const crumbs = [
            { id: 'Surgeries' },
            { id: <i>{context.accession}</i> },
        ];
        const crumbsReleased = (context.status === 'released');

       
        let hasPathology=false;
        let hasIHC=false;

        if (Object.keys(this.props.context.pathology_report).length > 0) {
          hasPathology = true;
            
        }
        if (Object.keys(this.props.context.ihc).length > 0) {
            hasIHC = true;
          }
      
         return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs root="/search/?type=Surgery" crumbs={crumbs} crumbsReleased={crumbsReleased} />
                        <h2>{context.accession}</h2>

                    </div>

                </header>
                <Panel>
                    <PanelHeading>
                        <h4>Surgery view</h4>
                    </PanelHeading>
                    <PanelBody>
                    <dl className="key-value">
                        <div data-test="status">
                            <dt>Status</dt>
                            <dd><Status item={context} inline /></dd>
                        </div>
                        <div data-test="patient">
                            <dt>Patient</dt>
                            <dd><a href={context.patient}>{context.patient.split("/")[2]}</a></dd>
                        </div>
                        <div data-test="surgery date">
                            <dt>Surgery Date</dt>
                            <dd>{context.date}</dd>
                        </div>
                        <div data-test="hospital">
                            <dt>Hospital Location</dt>
                            <dd>{context.hospital_location}</dd>
                        </div>

                    </dl>
                    </PanelBody>
                </Panel>
                {hasPathology && <PathologyReportTable data={context.pathology_report} tableTitle="Pathology Report " ></PathologyReportTable>}
                {hasIHC&&<IHCTable data={context.ihc} tableTitle="IHC Assay Staining Results"></IHCTable>}
            
            </div>


            );

    }
}
/* eslint-enable react/prefer-stateless-function */

Surgery.propTypes = {
    context: PropTypes.object, // Target object to display
  };

Surgery.defaultProps = {
  context: null,
};

globals.contentViews.register(Surgery, 'Surgery');
