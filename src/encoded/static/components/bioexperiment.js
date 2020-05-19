import React from 'react';
import PropTypes from 'prop-types';
import { Panel, PanelBody, PanelHeading } from '../libs/bootstrap/panel';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import Status from './status';
import { PanelLookup } from './objectutils';

class Bioexperiment extends React.Component {
    constructor(props) {
        super(props);
    }
    render() {
        const context = this.props.context;

        const itemClass = globals.itemClass(context, 'view-item');
        // Set up breadcrumbs
        const crumbs = [
            { id: 'Bioexperiments' },
            { id: <i>{context.accession}</i> },
        ];
        const crumbsReleased = (context.status === 'released');

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs root="/search/?type=bioexperiment" crumbs={crumbs} crumbsReleased={crumbsReleased} />
                        <h2>{context.accession}</h2>
                    </div>

                </header>
                <Panel>
                    <PanelHeading>
                        <h4>Bioexperiment Information</h4>
                    </PanelHeading>
                    <PanelBody>

                        <dl className="key-value">
                            <div >
                                <div data-test="status">
                                    <dt>Status</dt>
                                    <dd><Status item={context.status} inline /></dd>
                                </div>
                                <div data-test="assay_term_name">
                                    <dt>Assay Term Name</dt>
                                    <dd>{context.assay_term_name}</dd>
                                </div>
                                <div data-test="experiment_description">
                                    <dt>Assay Term Name</dt>
                                    <dd>{context.experiment_description}</dd>
                                </div>
                                {/* <div data-test="biospecimen">
                                    <dt>Biospecimen Accession</dt>
                                    <dd>{context.biospecimen}</dd>
                                </div> */}
                               
                            </div>
                        </dl>
                    </PanelBody>
                  
                </Panel>

            </div>
        )
    }

}


Bioexperiment.propTypes = {
    context: PropTypes.object, // Target object to display
};

Bioexperiment.defaultProps = {
    context: null,
};

globals.contentViews.register(Bioexperiment, 'Bioexperiment');

export default Bioexperiment;
