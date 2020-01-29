import React from 'react';
import PropTypes from 'prop-types';
import { Panel, PanelBody, PanelHeading } from '../libs/bootstrap/panel';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import Status from './status';
import CollapsiblePanel from './collapsiblePanel';
import { PanelLookup } from './objectutils';
import GenomicsTable from './genomicsTable';

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
        let hasGenomics =false;
        if (Object.keys(this.props.context.biolibrary).length > 0) {
            hasGenomics = true;
        }

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
                        <div data-test="internal_ID">
                            <dt>Internal ID</dt>
                            <dd>{context.internal_ID}</dd>
                        </div>

                        <div data-test="patient">
                            <dt>Patient</dt>
                            <dd><a href={context.patient}>{context.patient.split("/")[2]}</a></dd>
                            
                        </div>
                        <div data-test="collection_date">
                            <dt>Collection Date</dt>
                            <dd>{context.collection_date}</dd>
                        </div>
                        <div data-test="collection_type">
                            <dt>Collection Type</dt>
                            <dd>{context.collection_type}</dd>
                        </div>

                        <div data-test="processing_type">
                            <dt>Processing Type</dt>
                            <dd>{context.processing_type}</dd>
                        </div>
                        <div data-test="host">
                            <dt>Host</dt>
                            <dd>{context.host}</dd>
                        </div>
                        {context.originated_from && <div data-test="originated_from">
                            <dt>Originated From</dt>
                            <dd><a href={context.originated_from}>{context.originated_from.split("/")[2]}</a></dd>
                        </div>}
                        {context.path_ID && <div data-test="path_ID">
                            <dt>Path Report</dt>
                            <dd>{context.path_ID}</dd>
                        </div>}
                        {context.tissue_type && <div data-test="tissue_type">
                            <dt>Tissue Type</dt>
                            <dd>{context.tissue_type}</dd>
                        </div>}
                        {context.anatomic_site && <div data-test="anatomic_site">
                            <dt>Anatomic Site</dt>
                            <dd>{context.anatomic_site}</dd>
                        </div>}
                        {context.primary_site && <div data-test="primary_site">
                            <dt>Primary Site</dt>
                            <dd>{context.primary_site}</dd>
                        </div>}

                        <div data-test="distributed">
                            <dt>Distributed</dt>
                            <dd>{context.distributed}</dd>
                        </div>
                    </dl>
                    </PanelBody>
                </Panel>
                { hasGenomics && <GenomicsTable data={context.biolibrary} tableTitle="Genomics for this specimen"></GenomicsTable>}

                {false && 
                    <div>
                        {PanelLookup({ context: context.patient, biospecimen: context })}
                    </div>}


            </div>
        )
    }
}

globals.contentViews.register(Biospecimen, 'Biospecimen');

