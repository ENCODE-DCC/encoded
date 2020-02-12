import React from 'react';
import PropTypes from 'prop-types';
import { Panel, PanelBody, PanelHeading } from '../libs/bootstrap/panel';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import Status from './status';
import { PanelLookup } from './objectutils';
import CollapsiblePanel from './collapsiblePanel';
// import PathologyReport from './pathology_report';
import PathologyReportTable from './patholgoyReprotTable';





class Surgery extends React.Component {
    constructor(props) {
        super(props);
    }
    render() {
        const context = this.props.context;
        const itemClass = globals.itemClass(context, 'view-item');
        // Set up breadcrumbs
        const crumbs = [
            { id: 'Surgery' },
            { id: <i>{context.accession}</i> },
        ];
        const crumbsReleased = (context.status === 'released');
        console.log(context);
        console.log(context.pathology_report);
        // Get procedure_type
        //surgeryTypes = surgeryTypes.concat(context.surgery_procedure.procedure_type);

        //list single page of Surgery View.
       
        let hasPathology=false;
        if (Object.keys(this.props.context.pathology_report).length > 0) {
          hasPathology = true;
            
        }
          const pathologyPanelBody = (
            <PathologyReportTable data={context.pathology_report} tableTitle="Pathology Report Details" ></PathologyReportTable>
          );

        
        // const pathologyPanelBody = (
        //     <PathologyReport data={this.props.context} chartTitle="Pathology Report Details" ></PathologyReport>
        //   );
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
                            <dt>Surgery date</dt>
                            <dd>{context.date}</dd>
                        </div>
                        <div data-test="hospital">
                            <dt>Hospital Location</dt>
                            <dd>{context.hospital_location}</dd>
                        </div>

                    </dl>
                    </PanelBody>
                </Panel>
                {/* {hasPathology && <CollapsiblePanel panelId="pathology" title="Pathology report Details" content={pathologyPanelBody} />} */}
            
                <PathologyReportTable data={context.pathology_report} tableTitle="Pathology Report Details" ></PathologyReportTable>
            
            </div>


            );

    }
}
Surgery.propTypes = {
    context: PropTypes.object, // Target object to display
  };

Surgery.defaultProps = {
  context: null,
};

globals.contentViews.register(Surgery, 'Surgery');
