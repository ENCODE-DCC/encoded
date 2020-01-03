import React from 'react';
import PropTypes from 'prop-types';
import { Panel, PanelBody, PanelHeading } from '../libs/bootstrap/panel';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import Status from './status';
import CollapsiblePanel from './collapsiblePanel';

class Biospecimen extends React.Component {
    constructor(props) {
        super(props);


    }
    render() {
        const context = this.props.context;
        const itemClass = globals.itemClass(context, 'view-item');
        // Set up breadcrumbs
        const crumbs = [
            { id: 'Biospecimens' },
            { id: <i>{context.accession}</i> },
        ];
        const crumbsReleased = (context.status === 'released');

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs root="/search/?type=Biospecimen" crumbs={crumbs} crumbsReleased={crumbsReleased} />
                        <h2>{context.accession}</h2>

                    </div>

                </header>
                <Panel>
                    <PanelHeading>
                        <h4>Biospecimen Information</h4>
                    </PanelHeading>
                    <PanelBody>
                    <dl className="key-value">
                        <div data-test="status">
                            <dt>Status</dt>
                            <dd><Status item={context} inline /></dd>
                        </div>
                        <div data-test="openspecimen_ID">
                            <dt>OpenSpecimen ID</dt>
                            <dd>{context.openspecimen_ID}</dd>
                        </div>

                        <div data-test="collection_type">
                            <dt>Collection Type</dt>
                            <dd>{context.collection_type}</dd>
                        </div>

                        <div data-test="processing_type">
                            <dt>Processing Type</dt>
                            <dd>{context.processing_type}</dd>
                        </div>

                        <div data-test="distributed">
                            <dt>Distributed</dt>
                            <dd>{context.distributed}</dd>
                        </div>
                    </dl>
                    </PanelBody>
                </Panel>

            </div>
        )
    }
}
globals.contentViews.register(Biospecimen, 'Biospecimen');