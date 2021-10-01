import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import url from 'url';
import { Panel, PanelBody, PanelHeading } from '../libs/ui/panel';
import { auditDecor } from './audit';
import { DbxrefList } from './dbxref';
import { DocumentsPanel, DocumentsSubpanels } from './doc';
import GeneticModificationSummary from './genetic_modification';
import * as globals from './globals';
import { RelatedItems } from './item';
import { requestObjects, AlternateAccession, ItemAccessories, InternalTags, TopAccessories } from './objectutils';
import pubReferenceList from './reference';
import { PickerActions, resultItemClass } from './search';
import { SortTablePanel, SortTable } from './sorttable';
import Status from './status';
import { BiosampleTable, ExperimentTable } from './typeutils';
import formatMeasurement from '../libs/formatMeasurement';


const HumanDonor = (props) => {
    const { context, biosample } = props;
    const references = pubReferenceList(context.references);

    return (
        <div>
            <Panel>
                <PanelHeading>
                    <h4>Donor information</h4>
                </PanelHeading>
                <PanelBody>
                    <dl className="key-value">
                        <div data-test="status">
                            <dt>Status</dt>
                            <dd><Status item={context} inline /></dd>
                        </div>

                        <div data-test="accession">
                            <dt>Accession</dt>
                            <dd>{biosample ? <a href={context['@id']}>{context.accession}</a> : context.accession}</dd>
                        </div>

                        {context.aliases.length > 0 ?
                            <div data-test="aliases">
                                <dt>Aliases</dt>
                                <dd>{context.aliases.join(', ')}</dd>
                            </div>
                        : null}

                        {context.external_ids && context.external_ids.length > 0 ?
                            <div data-test="externalid">
                                <dt>Donor external identifiers</dt>
                                <dd><DbxrefList context={context} dbxrefs={context.external_ids} /></dd>
                            </div>
                        : null}

                        {context.organism.scientific_name ?
                            <div data-test="species">
                                <dt>Species</dt>
                                <dd className="sentence-case"><em>{context.organism.scientific_name}</em></dd>
                            </div>
                        : null}

                        {context.life_stage ?
                            <div data-test="life-stage">
                                <dt>Life stage</dt>
                                <dd className="sentence-case">{context.life_stage}</dd>
                            </div>
                        : null}

                        {context.age ?
                            <div data-test="age">
                                <dt>Age</dt>
                                <dd className="sentence-case">{formatMeasurement(context.age, context.age_units)}</dd>
                            </div>
                        : null}

                        {context.sex ?
                            <div data-test="sex">
                                <dt>Sex</dt>
                                <dd className="sentence-case">{context.sex}</dd>
                            </div>
                        : null}

                        {context.health_status ?
                            <div data-test="health-status">
                                <dt>Health status</dt>
                                <dd className="sentence-case">{context.health_status}</dd>
                            </div>
                        : null}

                        {context.ethnicity && context.ethnicity.length > 0 ?
                            <div data-test="ethnicity">
                                <dt>Ethnicity</dt>
                                <dd className="sentence-case">{context.ethnicity.join(', ')}</dd>
                            </div>
                        : null}

                        {context.dbxrefs && context.dbxrefs.length > 0 ?
                            <div data-test="external-resources">
                                <dt>External resources</dt>
                                <dd><DbxrefList context={context} dbxrefs={context.dbxrefs} /></dd>
                            </div>
                        : null}

                        {references ?
                            <div data-test="references">
                                <dt>References</dt>
                                <dd>{references}</dd>
                            </div>
                        : null}

                        {context.submitter_comment ?
                            <div data-test="submittercomment">
                                <dt>Submitter comment</dt>
                                <dd>{context.submitter_comment}</dd>
                            </div>
                        : null}

                        {context.internal_tags && context.internal_tags.length > 0 ?
                            <div className="tag-badges" data-test="tags">
                                <dt>Tags</dt>
                                <dd><InternalTags internalTags={context.internal_tags} objectType={context['@type'][0]} /></dd>
                            </div>
                        : null}
                    </dl>
                </PanelBody>
            </Panel>
        </div>
    );
};

HumanDonor.propTypes = {
    context: PropTypes.object.isRequired, // Donor being displayed
    biosample: PropTypes.object, // Biosample this donor is associated with
};

HumanDonor.defaultProps = {
    biosample: null,
};

globals.panelViews.register(HumanDonor, 'HumanDonor');


/**
 * Display a table of donors. Mostly useful for arrays of donors related to the one being
 * displayed.
 */
const donorTableColumns = {
    accession: {
        title: 'Accession',
        display: (donor) => <a href={donor['@id']}>{donor.accession}</a>,
    },
    age_display: {
        title: 'Age',
        display: (donor) => {
            if (donor.age) {
                return (
                    <span>
                        {formatMeasurement(donor.age, donor.age_units)}
                    </span>
                );
            }
            return null;
        },
    },
    health_status: { title: 'Health status' },
    life_stage: { title: 'Life stage' },
    sex: { title: 'Sex' },
    status: {
        title: 'Status',
        display: (donor) => <Status item={donor} badgeSize="small" inline />,
    },
};

const DonorTable = (props) => {
    const { title, donors } = props;

    return (
        <SortTablePanel title={title}>
            <SortTable list={donors} columns={donorTableColumns} />
        </SortTablePanel>
    );
};

DonorTable.propTypes = {
    title: PropTypes.string, // Title to display in the title bar of the donor table
    donors: PropTypes.array, // Array of donors to display in the table
};

DonorTable.defaultProps = {
    title: '',
    donors: '',
};


const MouseDonor = (props) => {
    const { context, biosample } = props;
    let donorUrlDomain;

    // Get the domain name of the donor URL.
    if (biosample && biosample.donor && biosample.donor.url) {
        const donorUrl = url.parse(biosample.donor.url);
        donorUrlDomain = donorUrl.hostname || '';
    }

    return (
        <div>
            <Panel>
                <PanelHeading>
                    <h4>Strain information</h4>
                </PanelHeading>
                <PanelBody>
                    <dl className="key-value">
                        <div data-test="status">
                            <dt>Status</dt>
                            <dd><Status item={context} inline /></dd>
                        </div>

                        <div data-test="accession">
                            <dt>Accession</dt>
                            <dd>{biosample ? <a href={context['@id']}>{context.accession}</a> : context.accession}</dd>
                        </div>

                        {context.aliases.length > 0 ?
                            <div data-test="aliases">
                                <dt>Aliases</dt>
                                <dd>{context.aliases.join(', ')}</dd>
                            </div>
                        : null}

                        {context.external_ids && context.external_ids.length > 0 ?
                            <div data-test="externalid">
                                <dt>Donor external identifiers</dt>
                                <dd><DbxrefList context={context} dbxrefs={context.external_ids} /></dd>
                            </div>
                        : null}

                        {context.organism.scientific_name ?
                            <div data-test="organism">
                                <dt>Species</dt>
                                <dd className="sentence-case"><em>{context.organism.scientific_name}</em></dd>
                            </div>
                        : null}

                        {context.genotype ?
                            <div data-test="genotype">
                                <dt>Genotype</dt>
                                <dd>{context.genotype}</dd>
                            </div>
                        : null}

                        {biosample && biosample.sex ?
                            <div data-test="sex">
                                <dt>Sex</dt>
                                <dd className="sentence-case">{biosample.sex}</dd>
                            </div>
                        : null}

                        {biosample && biosample.health_status ?
                            <div data-test="health-status">
                                <dt>Health status</dt>
                                <dd className="sentence-case">{biosample.health_status}</dd>
                            </div>
                        : null}

                        {donorUrlDomain ?
                            <div data-test="mutatedgene">
                                <dt>Strain reference</dt>
                                <dd><a href={biosample.donor.url}>{donorUrlDomain}</a></dd>
                            </div>
                        : null}

                        {context.strain_background ?
                            <div data-test="strain-background">
                                <dt>Strain background</dt>
                                <dd className="sentence-case">{context.strain_background}</dd>
                            </div>
                        : null}

                        {context.strain_name ?
                            <div data-test="strain-name">
                                <dt>Strain name</dt>
                                <dd>{context.strain_name}</dd>
                            </div>
                        : null}

                        {context.dbxrefs && context.dbxrefs.length > 0 ?
                            <div data-test="external-resources">
                                <dt>External resources</dt>
                                <dd><DbxrefList context={context} dbxrefs={context.dbxrefs} /></dd>
                            </div>
                        : null}

                        {context.references && context.references.length > 0 ?
                            <div data-test="references">
                                <dt>References</dt>
                                <dd>{pubReferenceList(context.references)}</dd>
                            </div>
                        : null}

                        {context.submitter_comment ?
                            <div data-test="submittercomment">
                                <dt>Submitter comment</dt>
                                <dd>{context.submitter_comment}</dd>
                            </div>
                        : null}
                    </dl>

                    {biosample && biosample.donor.characterizations && biosample.donor.characterizations.length > 0 ?
                        <div>
                            <hr />
                            <h4>Characterizations</h4>
                            <PanelBody addClasses="panel-body-doc-interior">
                                <DocumentsSubpanels documentSpec={{ documents: biosample.donor.characterizations }} />
                            </PanelBody>
                        </div>
                    : null}
                </PanelBody>
            </Panel>
        </div>
    );
};

MouseDonor.propTypes = {
    context: PropTypes.object.isRequired, // Mouse donor object being rendered
    biosample: PropTypes.object, // Biosample object this donor belongs to
};

MouseDonor.defaultProps = {
    biosample: null,
};

globals.panelViews.register(MouseDonor, 'MouseDonor');


const FlyWormDonor = (props) => {
    const { context, biosample } = props;
    let donorUrlDomain;

    return (
        <div>
            <Panel>
                <PanelHeading>
                    <h4>Strain information</h4>
                </PanelHeading>
                <PanelBody>
                    <dl className="key-value">
                        <div data-test="status">
                            <dt>Status</dt>
                            <dd><Status item={context} inline /></dd>
                        </div>

                        <div data-test="accession">
                            <dt>Accession</dt>
                            <dd>{biosample ? <a href={context['@id']}>{context.accession}</a> : context.accession}</dd>
                        </div>

                        {context.aliases.length > 0 ?
                            <div data-test="aliases">
                                <dt>Aliases</dt>
                                <dd>{context.aliases.join(', ')}</dd>
                            </div>
                        : null}

                        {context.external_ids && context.external_ids.length > 0 ?
                            <div data-test="externalid">
                                <dt>Donor external identifiers</dt>
                                <dd><DbxrefList context={context} dbxrefs={context.external_ids} /></dd>
                            </div>
                        : null}

                        {context.organism.scientific_name ?
                            <div data-test="species">
                                <dt>Species</dt>
                                <dd className="sentence-case"><em>{context.organism.scientific_name}</em></dd>
                            </div>
                        : null}

                        {context.genotype ?
                            <div data-test="genotype">
                                <dt>Genotype</dt>
                                <dd>{context.genotype}</dd>
                            </div>
                        : null}

                        {biosample && biosample.sex ?
                            <div data-test="sex">
                                <dt>Sex</dt>
                                <dd className="sentence-case">{biosample.sex}</dd>
                            </div>
                        : null}

                        {biosample && biosample.health_status ?
                            <div data-test="health-status">
                                <dt>Health status</dt>
                                <dd className="sentence-case">{biosample.health_status}</dd>
                            </div>
                        : null}

                        {donorUrlDomain ?
                            <div data-test="mutatedgene">
                                <dt>Strain reference</dt>
                                <dd><a href={biosample.donor.url}>{donorUrlDomain}</a></dd>
                            </div>
                        : null}

                        {context.strain_background ?
                            <div data-test="strain-background">
                                <dt>Strain background</dt>
                                <dd className="sentence-case">{context.strain_background}</dd>
                            </div>
                        : null}

                        {context.strain_name ?
                            <div data-test="strain-name">
                                <dt>Strain name</dt>
                                <dd>{context.strain_name}</dd>
                            </div>
                        : null}

                        {context.dbxrefs && context.dbxrefs.length > 0 ?
                            <div data-test="external-resources">
                                <dt>External resources</dt>
                                <dd><DbxrefList context={context} dbxrefs={context.dbxrefs} /></dd>
                            </div>
                        : null}


                        {context.submitter_comment ?
                            <div data-test="submittercomment">
                                <dt>Submitter comment</dt>
                                <dd>{context.submitter_comment}</dd>
                            </div>
                        : null}
                    </dl>
                </PanelBody>
            </Panel>
        </div>
    );
};

FlyWormDonor.propTypes = {
    context: PropTypes.object.isRequired, // Mouse donor object being rendered
    biosample: PropTypes.object, // Biosample object this donor belongs to
};

FlyWormDonor.defaultProps = {
    biosample: null,
};

globals.panelViews.register(FlyWormDonor, 'FlyDonor');
globals.panelViews.register(FlyWormDonor, 'WormDonor');


const ManateeDonor = (props) => {
    const { context, biosample } = props;

    return (
        <div>
            <Panel>
                <PanelHeading>
                    <h4>Donor information</h4>
                </PanelHeading>
                <PanelBody>
                    <dl className="key-value">
                        <div data-test="status">
                            <dt>Status</dt>
                            <dd><Status item={context} inline /></dd>
                        </div>

                        <div data-test="accession">
                            <dt>Accession</dt>
                            <dd>{biosample ? <a href={context['@id']}>{context.accession}</a> : context.accession}</dd>
                        </div>

                        {context.aliases.length > 0 ?
                            <div data-test="aliases">
                                <dt>Aliases</dt>
                                <dd>{context.aliases.join(', ')}</dd>
                            </div>
                        : null}

                        {context.external_ids && context.external_ids.length > 0 ?
                            <div data-test="externalid">
                                <dt>Donor external identifiers</dt>
                                <dd><DbxrefList context={context} dbxrefs={context.external_ids} /></dd>
                            </div>
                        : null}

                        {context.organism.scientific_name ?
                            <div data-test="species">
                                <dt>Species</dt>
                                <dd className="sentence-case"><em>{context.organism.scientific_name}</em></dd>
                            </div>
                        : null}

                        {context.age ?
                            <div data-test="age">
                                <dt>Age</dt>
                                <dd className="sentence-case">{formatMeasurement(context.age, context.age_units)}</dd>
                            </div>
                        : null}

                        {context.sex ?
                            <div data-test="sex">
                                <dt>Sex</dt>
                                <dd className="sentence-case">{context.sex}</dd>
                            </div>
                        : null}

                        {context.dbxrefs && context.dbxrefs.length > 0 ?
                            <div data-test="external-resources">
                                <dt>External resources</dt>
                                <dd><DbxrefList context={context} dbxrefs={context.dbxrefs} /></dd>
                            </div>
                        : null}


                        {context.submitter_comment ?
                            <div data-test="submittercomment">
                                <dt>Submitter comment</dt>
                                <dd>{context.submitter_comment}</dd>
                            </div>
                        : null}
                    </dl>
                </PanelBody>
            </Panel>
        </div>
    );
};

ManateeDonor.propTypes = {
    context: PropTypes.object.isRequired, // Manatee donor object being rendered
    biosample: PropTypes.object, // Biosample object this donor belongs to
};

ManateeDonor.defaultProps = {
    biosample: null,
};

globals.panelViews.register(ManateeDonor, 'ManateeDonor');


// This component activates for any donors that aren't any of the above registered types.
class DonorComponent extends React.Component {
    constructor() {
        super();
        this.state = {
            parentDonors: [],
            childDonors: [],
        };

        // Bind `this` to non-React methods.
        this.requestRelations = this.requestRelations.bind(this);
    }

    componentDidMount() {
        // Humans need to do a couple requests to get the parents and children of the donor.
        if (this.props.context['@type'][0] === 'HumanDonor') {
            // Now that the component has mounted, we can do a GET request of the donor's children and
            // parents so we can display them once the results come back.
            this.requestRelations();

            // In case the logged-in state changes, we have to keep track of the old logged-in state.
            this.loggedIn = !!(this.context.session && this.context.session['auth.userid']);
        }
    }

    /* eslint-disable camelcase */
    UNSAFE_componentWillReceiveProps() {
        // Humans need to do a couple requests to get the parents and children of the donor.
        if (this.props.context['@type'][0] === 'HumanDonor') {
            // If the logged-in state has changed since the last time we rendered, request files again
            // in case logging in changes the list of dependent files.
            const currLoggedIn = !!(this.context.session && this.context.session['auth.userid']);
            if (this.loggedIn !== currLoggedIn) {
                this.requestRelations();
                this.loggedIn = currLoggedIn;
            }
        }
    }
    /* eslint-enable camelcase */

    requestRelations() {
        // donor.parents and donor.children aren't embedded in the human donor object -- they're
        // just arrays of human_donor @ids. This function does a database search to retrieve all
        // donor.parent and donor.children objects.
        const donor = this.props.context;
        const parentAtids = donor.parents && donor.parents.length > 0 ? donor.parents : [];
        const childrenAtids = donor.children && donor.children.length > 0 ? donor.children : [];

        // Do both the donor.parent and donor.children as a combined search, and sort the results
        // out after they get retrieved.
        const atIds = parentAtids.concat(childrenAtids);

        // atIds now has an array of human_donor parents and children @ids. Send a GET request to
        // perform a search.
        if (atIds.length > 0) {
            requestObjects(atIds, '/search/?type=HumanDonor&limit=all&status!=deleted&status!=revoked&status!=replaced').then((parentChildDonors) => {
                // Got search results with all human_donor parents and children as one search
                // result array. Sort them into parents and children based on their locations in
                // the donor.
                const relations = _(parentChildDonors).groupBy((parentChildDonor) => {
                    // Any results that have a matching @id in the array of parents in the donor
                    // get put into the 'parents' key in the `relations` object as an array. Any
                    // with a matching @id in the array of children get put into the 'children' key
                    // as an array.
                    if (parentAtids.indexOf(parentChildDonor['@id']) !== -1) {
                        return 'parents';
                    }
                    if (childrenAtids.indexOf(parentChildDonor['@id']) !== -1) {
                        return 'children';
                    }

                    // This should *never* happen.
                    return 'unknown';
                });

                // Rerender the page with the parents and children tables.
                this.setState({
                    parentDonors: relations.parents || [],
                    childDonors: relations.children || [],
                });
            });
        }
    }

    render() {
        const { context } = this.props;
        const itemClass = globals.itemClass(context, 'view-item');
        const PanelView = globals.panelViews.lookup(context);
        let characterizationDocuments = [];
        let donorDocuments = [];

        // Collect the characterization documents.
        if (context.characterizations && context.characterizations.length > 0) {
            characterizationDocuments = context.characterizations;
        }

        // Collect the donor documents.
        if (context.documents && context.documents.length > 0) {
            donorDocuments = context.documents;
        }

        // Combine characterization and donor documents.
        const combinedDocuments = [].concat(characterizationDocuments, donorDocuments);

        // Set up breadcrumbs.
        const crumbs = [
            { id: 'Donors' },
            { id: <i>{context.organism.scientific_name}</i> },
        ];

        return (
            <div className={itemClass}>
                <header>
                    <TopAccessories context={context} crumbs={crumbs} />
                    <h1>{context.accession}</h1>
                    <div className="replacement-accessions">
                        <AlternateAccession altAcc={context.alternate_accessions} />
                    </div>
                    <ItemAccessories item={context} audit={{ auditIndicators: this.props.auditIndicators, auditId: 'experiment-audit', except: context['@id'] }} />
                    {this.props.auditDetail(context.audit, 'donor-audit', { session: this.context.session, sessionProperties: this.context.session_properties, except: context['@id'] })}
                </header>

                <PanelView key={context.uuid} {...this.props} />

                {context.genetic_modifications && context.genetic_modifications.length > 0 ?
                    <GeneticModificationSummary geneticModifications={context.genetic_modifications} />
                : null}

                <RelatedItems
                    title={`Biosamples from this ${context.organism.name === 'human' ? 'donor' : 'strain'}`}
                    url={`/search/?type=Biosample&donor.uuid=${context.uuid}`}
                    Component={BiosampleTable}
                />

                {context['@type'][0] === 'HumanDonor' && this.state.childDonors && this.state.childDonors.length > 0 ?
                    <DonorTable title="Children of this donor" donors={this.state.childDonors} />
                : null}

                {context['@type'][0] === 'HumanDonor' && this.state.parentDonors && this.state.parentDonors.length > 0 ?
                    <DonorTable title="Parents of this donor" donors={this.state.parentDonors} />
                : null}

                <RelatedItems
                    title={`Functional genomics experiments from this ${context.organism.name === 'human' ? 'donor' : 'strain'}`}
                    url={`/search/?type=Experiment&replicates.library.biosample.donor.uuid=${context.uuid}`}
                    Component={ExperimentTable}
                />

                <RelatedItems
                    title={`Functional characterization experiments from this ${context.organism.name === 'human' ? 'donor' : 'strain'}`}
                    url={`/search/?type=FunctionalCharacterizationExperiment&replicates.library.biosample.donor.uuid=${context.uuid}`}
                    Component={ExperimentTable}
                />

                {combinedDocuments.length > 0 ?
                    <DocumentsPanel documentSpecs={[{ documents: combinedDocuments }]} />
                : null}
            </div>
        );
    }
}

DonorComponent.propTypes = {
    context: PropTypes.object.isRequired, // Donor being rendered
    auditIndicators: PropTypes.func.isRequired, // Audit indicator rendering function from auditDecor
    auditDetail: PropTypes.func.isRequired, // Audit detail rendering function from auditDecor
};

DonorComponent.contextTypes = {
    session: PropTypes.object, // Login information
    session_properties: PropTypes.object,
};

const Donor = auditDecor(DonorComponent);

globals.contentViews.register(Donor, 'Donor');


const DonorListingComponent = (props, reactContext) => {
    const { organismTitle } = props;
    const result = props.context;

    // Make array of extra info for display in the search results link with a join. The `Boolean`
    // constructor in the filter cleverly filters out falsy values from the array. See:
    // https://stackoverflow.com/questions/32906887/remove-all-falsy-values-from-an-array#answer-32906951
    const details = [
        result.strain_name,
        result.strain_background ? (result.strain_background !== 'unknown' ? result.strain_background : 'unknown strain background') : null,
        result.sex ? (result.sex !== 'unknown' ? result.sex : 'unknown sex') : null,
        result.life_stage ? (result.life_stage !== 'unknown' ? result.life_stage : 'unknown life stage') : null,
        formatMeasurement(result.age, result.age_units),
    ].filter(Boolean);

    return (
        <div className={resultItemClass(result)}>
            <div className="result-item">
                <div className="result-item__data">
                    <a href={result['@id']} className="result-item__link">
                        <i>{result.organism.scientific_name}</i>
                        {details.length > 0 ? ` (${details.join(', ')})` : null}
                    </a>
                    <div className="result-item__data-row">
                        {result.lab ? <div><strong>Lab: </strong>{result.lab.title}</div> : null}
                        {result.external_ids && result.external_ids.length ?
                            <>
                                <strong>External resources: </strong>
                                <DbxrefList context={result} dbxrefs={result.external_ids} />
                            </>
                        : null}
                    </div>
                </div>
                <div className="result-item__meta">
                    <div className="result-item__meta-title">{organismTitle}</div>
                    <div className="result-item__meta-id">{` ${result.accession}`}</div>
                    <Status item={result.status} badgeSize="small" css="result-table__status" />
                    {props.auditIndicators(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties, search: true })}
                </div>
                <PickerActions context={result} />
            </div>
            {props.auditDetail(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties })}
        </div>
    );
};

DonorListingComponent.propTypes = {
    context: PropTypes.object.isRequired, // Search results object
    organismTitle: PropTypes.string.isRequired, // Title to display on the right for each kind of organism
    auditDetail: PropTypes.func.isRequired, // Audit HOC function to show audit details
    auditIndicators: PropTypes.func.isRequired, // Audit HOC function to display audit indicators
};

DonorListingComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
    session_properties: PropTypes.object,
};

const DonorListing = auditDecor(DonorListingComponent);


const HumanListing = (props) => (
    <DonorListing {...props} organismTitle="Human donor" />
);

const MouseListing = (props) => (
    <DonorListing {...props} organismTitle="Mouse donor" />
);

const WormListing = (props) => (
    <DonorListing {...props} organismTitle="Worm donor" />
);

const FlyListing = (props) => (
    <DonorListing {...props} organismTitle="Fly donor" />
);

const ManateeListing = (props) => (
    <DonorListing {...props} organismTitle="Manatee donor" />
);

globals.listingViews.register(HumanListing, 'HumanDonor');
globals.listingViews.register(MouseListing, 'MouseDonor');
globals.listingViews.register(WormListing, 'WormDonor');
globals.listingViews.register(FlyListing, 'FlyDonor');
globals.listingViews.register(ManateeListing, 'ManateeDonor');
