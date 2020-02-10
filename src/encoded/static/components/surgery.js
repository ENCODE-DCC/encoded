import React from 'react';
import PropTypes from 'prop-types';
import { Panel, PanelBody, PanelHeading } from '../libs/bootstrap/panel';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import Status from './status';
import { PanelLookup } from './objectutils';

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

        // Get procedure_type
        //surgeryTypes = surgeryTypes.concat(context.surgery_procedure.procedure_type);

        //list single page of Surgery View.
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
                        <div data-test="hospital">
                            <dt>Hospital Location</dt>
                            <dd>{context.hospital_location}</dd>
                        </div>

                    </dl>
                    </PanelBody>
                </Panel>
            </div>
            )

    }
}
Surgery.propTypes = {
    context: PropTypes.object, // Target object to display
  };

Surgery.defaultProps = {
  context: null,
};

globals.contentViews.register(Surgery, 'Surgery');
