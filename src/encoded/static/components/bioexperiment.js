import React from 'react';
import PropTypes from 'prop-types';
import { Panel, PanelBody, PanelHeading } from '../libs/bootstrap/panel';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import Status from './status';
import { PanelLookup } from './objectutils';
import moment from 'moment';
import _ from 'underscore';
import { auditDecor } from './audit';
import { DocumentsPanelReq } from './doc';
import { DbxrefList } from './dbxref';
import { FetchedItems } from './fetched';
import { FileGallery } from './filegallery';
import { CartToggle } from './cart';
import { ProjectBadge } from './image';
import { singleTreatment, DisplayAsJson, InternalTags } from './objectutils';
import pubReferenceList from './reference';
import { SortTablePanel, SortTable } from './sorttable';
import { BiosampleSummaryString, BiosampleOrganismNames, CollectBiosampleDocs, AwardRef, ReplacementAccessions, ControllingExperiments } from './typeutils';
import BioreplicateTable from './bioreplicateTable';

class Bioexperiment extends React.Component {
    constructor(props) {
        super(props);
    }
    render() {
        const context = this.props.context;
        // console.log(context);
        let bioreplicate=context.bioreplicate;//Array 
        // console.log(bioreplicate);


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
                        <Breadcrumbs root="/search/?type=Experiment" crumbs={crumbs} crumbsReleased={crumbsReleased} />
                        <h2>Experiment summary for {context.accession}</h2>
                        <ReplacementAccessions context={context} />
                        {/* <div className="cart__toggle--header">
                            <CartToggle element={context} />
                        </div> */}
                        <DisplayAsJson />
                        {/* {this.props.auditIndicators(context.audit, 'experiment-audit', { session: this.context.session })} */}
                    </div>
                </header>
                {/* {this.props.auditDetail(context.audit, 'experiment-audit', { session: this.context.session, except: context['@id'] })} */}
                <Panel addClasses="data-display">
                    <PanelBody addClasses="panel-body-with-header">
                        <div className="flexrow">
                            {/* for summary */}
                            <div className="flexcol-sm-6">
                                <div className="flexcol-heading experiment-heading">
                                    <h4>Summary</h4>
                                </div>
                                <dl className="key-value">
                                    <div data-test="status">
                                        <dt>Status</dt>
                                        <dd>
                                            <Status item={context} css="dd-status" title="Experiment status" inline />
                                            {/* {adminUser && context.internal_status ?
                                                <Status item={context.internal_status} title="Internal status" inline />
                                            : null} */}
                                        </dd>
                                    </div>

                                    <div data-test="assay">
                                        <dt>Assay</dt>
                                        <dd>
                                            {context.assay_term_name}
                                            {/* {context.assay_term_name !== context.assay_title ?
                                                <span>{` (${context.assay_title})`}</span>
                                            : null} */}
                                        </dd>
                                    </div>

                                    {/* {context.biosample_summary ?
                                        <div data-test="biosample-summary">
                                            <dt>Biosample summary</dt>
                                            <dd>
                                                {organismNames.length ?
                                                    <span>
                                                        {organismNames.map((organismName, i) =>
                                                            <span key={organismName}>
                                                                {i > 0 ? <span> and </span> : null}
                                                                <i>{organismName}</i>
                                                            </span>
                                                        )}
                                                        &nbsp;
                                                    </span>
                                                : null}
                                                <span>{context.biosample_summary}</span>
                                            </dd>
                                        </div>
                                    : null} */}
                                    {/* 
                                    {context.biosample_ontology ?
                                        <div data-test="biosample-type">
                                            <dt>Biosample Type</dt>
                                            <dd>{context.biosample_ontology.classification}</dd>
                                        </div>
                                    : null} */}

                                    {/* {context.replication_type ?
                                        <div data-test="replicationtype">
                                            <dt>Replication type</dt>
                                            <dd>{context.replication_type}</dd>
                                        </div>
                                    : null} */}

                                    {context.experiment_description ?
                                        <div data-test="experiment_description">
                                            <dt>Description</dt>
                                            <dd>{context.experiment_description}</dd>
                                        </div>
                                        : null}

                                    {/* {AssayDetails(replicates, this.libraryValues, librarySpecials, libraryComponents)} */}

                                    {/* {Object.keys(platforms).length ?
                                        <div data-test="platform">
                                            <dt>Platform</dt>
                                            <dd>
                                                {Object.keys(platforms).map((platformId, i) =>
                                                    <span key={platformId}>
                                                        {i > 0 ? <span>, </span> : null}
                                                        <a className="stacked-link" href={platformId}>{platforms[platformId].title}</a>
                                                    </span>
                                                )}
                                            </dd>
                                        </div>
                                    : null} */}

                                    {/* {context.possible_controls && context.possible_controls.length ?
                                        <div data-test="possible-controls">
                                            <dt>Controls</dt>
                                            <dd>
                                                <ul>
                                                    {context.possible_controls.map(control => (
                                                        <li key={control['@id']} className="multi-comma">
                                                            <a href={control['@id']}>
                                                                {control.accession}
                                                            </a>
                                                        </li>
                                                    ))}
                                                </ul>
                                            </dd>
                                        </div>
                                    : null} */}
                                </dl>
                            </div>

                            {/* for attibution */}
                            <div className="flexcol-sm-6">
                                <div className="flexcol-heading experiment-heading">
                                    <h4>Attribution</h4>
                                    <ProjectBadge award={context.award} addClasses="badge-heading" />
                                </div>
                                <dl className="key-value">
                                    <div data-test="lab">
                                        <dt>Lab</dt>
                                        <dd>{context.lab.title}</dd>
                                    </div>

                                    <AwardRef context={context} />

                                    <div data-test="project">
                                        <dt>Project</dt>
                                        <dd>{context.award.project}</dd>
                                    </div>

                                    {/* {context.dbxrefs.length ?
                                        <div data-test="external-resources">
                                            <dt>External resources</dt>
                                            <dd><DbxrefList context={context} dbxrefs={context.dbxrefs} /></dd>
                                        </div>
                                    : null} */}

                                    {/* {references ?
                                        <div data-test="references">
                                            <dt>References</dt>
                                            <dd>{references}</dd>
                                        </div>
                                    : null} */}

                                    {/* {context.aliases.length ?
                                        <div data-test="aliases">
                                            <dt>Aliases</dt>
                                            <dd>{context.aliases.join(', ')}</dd>
                                        </div>
                                    : null} */}

                                    {context.date_submitted ?
                                        <div data-test="date-submitted">
                                            <dt>Date submitted</dt>
                                            <dd>{moment(context.date_submitted).format('MMMM D, YYYY')}</dd>
                                        </div>
                                        : null}

                                    {context.date_released ?
                                        <div data-test="date-released">
                                            <dt>Date released</dt>
                                            <dd>{moment(context.date_released).format('MMMM D, YYYY')}</dd>
                                        </div>
                                        : null}
                                    {/* 
                                    {seriesList.length ?
                                        <div data-test="relatedseries">
                                            <dt>Related datasets</dt>
                                            <dd><RelatedSeriesList seriesList={seriesList} /></dd>
                                        </div>
                                    : null} */}

                                    {/* {context.submitter_comment ?
                                        <div data-test="submittercomment">
                                            <dt>Submitter comment</dt>
                                            <dd>{context.submitter_comment}</dd>
                                        </div>
                                    : null} */}

                                    {/* {libSubmitterComments} */}
                                </dl>
                            </div>
                        </div>
                    </PanelBody>
                </Panel>
                {<BioreplicateTable data={context.bioreplicate} tableTitle="Bioreplicates summary"></BioreplicateTable>}

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

// export default Bioexperiment;
