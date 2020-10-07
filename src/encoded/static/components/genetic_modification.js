import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import url from 'url';
import * as encoding from '../libs/query_encoding';
import { Panel, PanelBody } from '../libs/ui/panel';
import { auditDecor } from './audit';
import { Document, DocumentPreview, DocumentFile, DocumentsPanel } from './doc';
import { FetchedData, Param } from './fetched';
import * as globals from './globals';
import { ProjectBadge } from './image';
import { RelatedItems } from './item';
import { Breadcrumbs } from './navigation';
import { singleTreatment, requestSearch, ItemAccessories, AlternateAccession } from './objectutils';
import { PickerActions, resultItemClass } from './search';
import { SortTablePanel, SortTable } from './sorttable';
import Status from './status';
import { BiosampleTable, DonorTable } from './typeutils';


// Generate a <dt>/<dd> combination to render GeneticModification.epitope_tags into a <dl>. If no
// epitope_tags exist in the given genetic modification object, nothing gets rendered.
const IntroducedTags = (props) => {
    const { geneticModification } = props;

    if (geneticModification.introduced_tags && geneticModification.introduced_tags.length > 0) {
        // Generate an array of React components, each containing one epitope_tags display from
        // the array of epitope_tags in the given genetic modification object. At least one
        // property of each epitope tag element must be present, or else an empty <li></li> will
        // get generated. Seems unlikely to have an empty epitope_tags element in the array, so
        // this currently seems like a good assumption.
        const elements = geneticModification.introduced_tags.map((tag, i) => {
            const targetName = tag.promoter_used ? globals.atIdToAccession(tag.promoter_used) : '';
            const name = tag.name ? <span>{tag.name}</span> : null;
            const location = tag.location ? <span>{name ? <span> &mdash; </span> : null}{tag.location}</span> : null;
            const promoterUsed = tag.promoter_used ? <span>{name || location ? <span> &mdash; </span> : null}<a href={tag.promoter_used} title={`View page for target ${targetName}`}>{targetName}</a></span> : null;
            return <li key={i}>{name}{location}{promoterUsed}</li>;
        });

        // Return a <div> to get rendered within a <dl> being displayed for the given genetic
        // modification.
        return (
            <div data-test="introducedtag">
                <dt>Tags</dt>
                <dd><ul className="multi-value">{elements}</ul></dd>
            </div>
        );
    }
    return null;
};

IntroducedTags.propTypes = {
    geneticModification: PropTypes.object.isRequired, // GeneticModification object being displayed
};


const modifiedSiteRenderers = {
    modified_site_by_target_id: (gm) => {
        let targetName;
        let targetLink;

        if (typeof gm.modified_site_by_target_id === 'string') {
            // Non-embedded target; get its name from its @id.
            targetName = globals.atIdToAccession(gm.modified_site_by_target_id);
            targetLink = gm.modified_site_by_target_id;
        } else {
            // Embedded target; get its name from the embedded object.
            targetName = gm.modified_site_by_target_id.name;
            targetLink = gm.modified_site_by_target_id['@id'];
        }
        return (
            <div data-test="mstarget">
                <dt>Target</dt>
                <dd><a href={targetLink} title={`View page for target ${targetName}`}>{targetName}</a></dd>
            </div>
        );
    },
    modified_site_by_gene_id: gm => (
        <div data-test="msgene">
            <dt>Gene</dt>
            <dd className="sequence"><a href={gm.modified_site_by_gene_id['@id']}>{gm.modified_site_by_gene_id.symbol}</a></dd>
        </div>
    ),
    modified_site_by_coordinates: (gm) => {
        const { assembly, chromosome, start, end } = gm.modified_site_by_coordinates;
        return (
            <div data-test="mscoords">
                <dt>Coordinates</dt>
                <dd>{`${assembly} chr${chromosome}:${start}-${end}`}</dd>
            </div>
        );
    },
    modified_site_by_sequence: gm => (
        <div data-test="msseq">
            <dt>Sequence</dt>
            <dd className="sequence">{gm.modified_site_by_sequence}</dd>
        </div>
    ),
    modified_site_nonspecific: gm => (
        <div data-test="msnonspec">
            <dt>Integration site</dt>
            <dd>{gm.modified_site_nonspecific}</dd>
        </div>
    ),
};


/**
 * Determine if a genetic modification object includes any modification site properties.
 * @param {object} geneticModification GM object
 * @return {boolean} True if `geneticModification` includes any modification site properties.
 */
const hasModificationSiteProps = geneticModification => (
    Object.keys(modifiedSiteRenderers).some(siteType => geneticModification[siteType])
);


// Render the modification site items into a definition list.
const ModificationSiteItems = (props) => {
    const { geneticModification, itemClass } = props;

    const elements = Object.keys(modifiedSiteRenderers).map((siteType) => {
        if (geneticModification[siteType]) {
            return <div key={siteType}>{modifiedSiteRenderers[siteType](geneticModification)}</div>;
        }
        return null;
    });

    return (
        <dl className={itemClass}>
            {elements}
        </dl>
    );
};

ModificationSiteItems.propTypes = {
    geneticModification: PropTypes.object.isRequired, // Genetic modification object whose modification_site we're rendering here
    itemClass: PropTypes.string, // CSS class string to add to <dl>
};

ModificationSiteItems.defaultProps = {
    itemClass: '',
};


/**
 * Display a section for the modification site data from the given genetic modification object. to
 * render into the GM summary panel as its own section;
 */
const ModificationSite = (props) => {
    const { geneticModification } = props;

    if (hasModificationSiteProps(geneticModification)) {
        const itemClass = globals.itemClass(geneticModification, 'view-detail key-value');
        return (
            <div className="gm-summary-subsection">
                <h4>Modification site</h4>
                <ModificationSiteItems geneticModification={geneticModification} itemClass={itemClass} />
            </div>
        );
    }
    return null;
};

ModificationSite.propTypes = {
    /** GM object with modification site data to display */
    geneticModification: PropTypes.object.isRequired,
};


// Render data for the Modification Technique section of the GM summary panel, for the given
// GeneticModification object.
const ModificationMethod = (props) => {
    const { geneticModification } = props;
    const itemClass = globals.itemClass(geneticModification, 'view-detail key-value');

    // Make an array of treatment text summaries within <li> elements that can get inserted
    // directly into a <ul> element.
    let treatments = [];
    if (geneticModification.treatments && geneticModification.treatments.length > 0) {
        treatments = geneticModification.treatments.map(treatment => <li key={treatment.uuid}>{singleTreatment(treatment)}</li>);
    }

    return (
        <div className="gm-summary-subsection">
            <h4>Modification method</h4>
            <dl className={itemClass}>
                {geneticModification.method ?
                    <div data-test="method">
                        <dt>Method</dt>
                        <dd>{geneticModification.method}</dd>
                    </div>
                : null}

                {geneticModification.nucleic_acid_delivery_method && geneticModification.nucleic_acid_delivery_method.length > 0 ?
                    <div data-test="nucleic-acid-delivery-method">
                        <dt>Nucleic acid delivery method</dt>
                        <dd>{geneticModification.nucleic_acid_delivery_method.join(', ')}</dd>
                    </div>
                : null}

                {treatments.length > 0 ?
                    <div data-test="treatments">
                        <dt>Treatments</dt>
                        <dd>
                            <ul className="multi-value">
                                {treatments}
                            </ul>
                        </dd>
                    </div>
                : null}

                {geneticModification.rnai_sequences && geneticModification.rnai_sequences.length > 0 ?
                    <div data-test="rnai">
                        <dt>RNAi sequences</dt>
                        <dd>{geneticModification.rnai_sequences.join(', ')}</dd>
                    </div>
                : null}

                {geneticModification.guide_rna_sequences && geneticModification.guide_rna_sequences.length > 0 ?
                    <div data-test="guiderna">
                        <dt>Guide RNAs</dt>
                        <dd>
                            {geneticModification.guide_rna_sequences.join(', ')}
                        </dd>
                    </div>
                : null}

                {geneticModification.RVD_sequence_pairs && geneticModification.RVD_sequence_pairs.length > 0 ?
                    <div data-test="rvdseq">
                        <dt>RVD sequence pairs</dt>
                        <dd>
                            <ul className="multi-value">
                                {geneticModification.RVD_sequence_pairs.map((pair, i) => (
                                    <li key={i}>{pair.left_RVD_sequence} : {pair.right_RVD_sequence}</li>
                                ))}
                            </ul>
                        </dd>
                    </div>
                : null}

                {geneticModification.reagents && geneticModification.reagents.length > 0 ?
                    <div data-test="reagent">
                        <dt>Reagents</dt>
                        <dd>
                            <ul className="multi-value-line">
                                {geneticModification.reagents.map((reagent, i) => {
                                    // Although reagents specify source, we want to use the source prefix from the identifier for best consistency
                                    const parsedIdentifier = reagent.identifier.split(':');
                                    const reagentId = <span>{parsedIdentifier[0]} &mdash; {parsedIdentifier[1]}</span>;
                                    if (reagent.url) {
                                        return <li key={i}><a href={reagent.url}>{reagentId}</a></li>;
                                    }
                                    return <li key={i}>{reagentId}</li>;
                                })}
                            </ul>
                        </dd>
                    </div>
                : null}
            </dl>
        </div>
    );
};

ModificationMethod.propTypes = {
    geneticModification: PropTypes.object.isRequired, // GM object being rendered
};


// Rendering component for the attribution pane of the summary panel. This gets called as a result
// of a successful GET request for the GM's award and lab objects which are no longer embedded in
// the GM object.
const AttributionRenderer = (props) => {
    const { geneticModification, award } = props;

    return (
        <div>
            <div className="panel__split-heading panel__split-heading--genetic-modification">
                <h4>Attribution</h4>
                <ProjectBadge award={award} addClasses="badge-heading" />
            </div>
            <dl className="key-value">
                <div data-test="lab">
                    <dt>Lab</dt>
                    <dd>{geneticModification.lab.title}</dd>
                </div>

                {award.pi && award.pi.lab ?
                    <div data-test="awardpi">
                        <dt>Award PI</dt>
                        <dd>{award.pi.lab.title}</dd>
                    </div>
                : null}

                <div data-test="project">
                    <dt>Project</dt>
                    <dd>{award.project}</dd>
                </div>

                {geneticModification.aliases && geneticModification.aliases.length > 0 ?
                    <div data-test="aliases">
                        <dt>Aliases</dt>
                        <dd>{geneticModification.aliases.join(', ')}</dd>
                    </div>
                : null}

                {geneticModification.submitter_comment ?
                    <div data-test="submittercomment">
                        <dt>Submitter comment</dt>
                        <dd>{geneticModification.submitter_comment}</dd>
                    </div>
                : null}
            </dl>
        </div>
    );
};

AttributionRenderer.propTypes = {
    geneticModification: PropTypes.object.isRequired, // GeneticModification object being displayed
    award: PropTypes.object, // Award object retreived from an individual GET request; don't make isRequired because React's static analysizer will ding it
};

AttributionRenderer.defaultProps = {
    award: null, // Actually required, but React can't tell this property's coming from a GET request, so treat as optional
};


// Display the contents of the attribution panel (currently the right-hand side of the summary
// panel) for the given genetic modification object. Because the award and lab informatino isn't
// embedded in the GM object, we have to retrieve it with a couple GET requests here, and have
// <AttributionRenderer> actually render the panel contents after the GET request completes.
const Attribution = (props) => {
    const { geneticModification } = props;

    return (
        <FetchedData>
            <Param name="award" url={geneticModification.award} />
            <AttributionRenderer geneticModification={geneticModification} />
        </FetchedData>
    );
};

Attribution.propTypes = {
    geneticModification: PropTypes.object.isRequired, // Genetic modificastion object for which we're getting the attribution information
};


// Render a panel containing GM document panels and GM characterization panels associated with a
// GM object.
const DocumentsRenderer = ({ characterizations, modificationDocuments, characterizationDocuments }) => {
    // Don't need to check for characterizationDocuments.length because these only get displayed
    // within characterization panels.
    if (characterizations.length > 0 || modificationDocuments.length > 0) {
        // Make a mapping of characterization document @ids to characterization documents
        // to make searching in the next step easier.
        const characterizationDocumentMap = {};
        characterizationDocuments.forEach((document) => {
            characterizationDocumentMap[document['@id']] = document;
        });

        // Need to replace the `documents` array of @ids in each characterization with an array of
        // corresponding document objects. We can't touch the GM object's characterizations so we
        // make a copy of each and modify that instead.
        const characterizationsCopy = characterizations.map((characterization) => {
            const copy = Object.assign({}, characterization);
            copy.documents = characterization.documents ? _.compact(characterization.documents.map(documentAtId => characterizationDocumentMap[documentAtId])) : [];
            return copy;
        });

        return (
            <DocumentsPanel
                documentSpecs={[
                    { label: 'Characterization', documents: characterizationsCopy },
                    { label: 'Modification document', documents: modificationDocuments },
                ]}
            />
        );
    }
    return null;
};

DocumentsRenderer.propTypes = {
    characterizations: PropTypes.array.isRequired, // GM characterizations
    characterizationDocuments: PropTypes.array.isRequired, // GM characterization documents for all given characterizations
    modificationDocuments: PropTypes.array.isRequired, // GM documents
};


/**
 * Collect an array of all characterization document @ids.
 *
 * @param {array} characterizations - Array of characterizations from GM context object.
 * @return {array} - Array of all characterization document @ids from all characterizations in the GM context object.
 */
const collectCharacterizationAtIds = (characterizations) => {
    const characterizationDocumentAtIds = [];
    if (characterizations && characterizations.length > 0) {
        characterizations.forEach((characterization) => {
            if (characterization.documents && characterization.documents.length > 0) {
                characterizationDocumentAtIds.push(...characterization.documents);
            }
        });
    }
    return characterizationDocumentAtIds;
};


// Render the entire GeneticModification page. This is called by the back end as a result of an
// attempt to render an object with an @type of GeneticModification.
class GeneticModificationComponent extends React.Component {
    constructor() {
        super();
        this.state = {
            modificationDocuments: [], // GM document search results
            characterizationDocuments: [], // GM characterization document search results
        };
        this.requestDocuments = this.requestDocuments.bind(this);
        this.documentsChanged = this.documentsChanged.bind(this);
        this.conditionsChanged = this.conditionsChanged.bind(this);
    }

    componentDidMount() {
        this.requestDocuments();
    }

    componentDidUpdate(previousProperties) {
        if (this.conditionsChanged(previousProperties)) {
            this.requestDocuments();
        }
    }

    conditionsChanged(previousProperties) {
        // Logged-in state has changed.
        const previousLoggedIn = !!(previousProperties.session && previousProperties.session['auth.userid']);
        const currentLoggedIn = !!(this.props.session && this.props.session['auth.userid']);
        if (previousLoggedIn !== currentLoggedIn) {
            return true;
        }

        const previousCharacterizations = previousProperties.context.characterizations || [];
        const currentCharacterizations = this.props.context.characterizations || [];
        const previousModificationDocuments = previousProperties.context.documents || [];
        const currentModificationDocuments = this.props.context.documents || [];

        // The characterizations array length or the GM documents array length has changed.
        if (previousCharacterizations.length !== currentCharacterizations.length || previousModificationDocuments.length !== currentModificationDocuments.length) {
            return true;
        }

        // The lengths of both arrays are the same; check their contents.
        if (previousCharacterizations.some((characterization, i) => characterization['@id'] !== currentCharacterizations[i]['@id']) ||
                previousModificationDocuments.some((document, i) => document !== currentModificationDocuments[i])) {
            return true;
        }

        // The characterizations and documents arrays have the same contents. Now check the
        // previous and current characterization document array lengths and contents.
        const previousCharacterizationDocuments = collectCharacterizationAtIds(previousCharacterizations);
        const currentCharacterizationDocuments = collectCharacterizationAtIds(currentCharacterizations);
        if (previousCharacterizationDocuments.length !== currentCharacterizationDocuments.length) {
            return true;
        }
        if (previousCharacterizationDocuments.some((documentAtId, i) => documentAtId !== currentCharacterizationDocuments[i])) {
            return true;
        }
        return false;
    }

    requestDocuments() {
        const { context } = this.props;

        // Collect all GM characterization document @ids.
        const characterizationDocumentAtIds = collectCharacterizationAtIds(context.characterizations);

        // Collect GM document @ids and combine with characterization document @ids so we can do
        // one GET request for both.
        const modificationCharacterizationDocumentsAtIds = _.uniq((context.documents && context.documents.length > 0 ? context.documents : []).concat(characterizationDocumentAtIds));

        // Convert the array of document @ids into a query string and do the GET request for their
        // objects.
        const modificationDocuments = [];
        const characterizationDocuments = [];
        let searchPromise = null;
        const modificationCharacterizationDocumentsQuery = modificationCharacterizationDocumentsAtIds.length > 0 ? modificationCharacterizationDocumentsAtIds.reduce((acc, document) => `${acc}&${encoding.encodedURIComponentOLD(`@id=${document}`)}`, '') : null;
        if (modificationCharacterizationDocumentsQuery) {
            searchPromise = requestSearch(`type=Document${modificationCharacterizationDocumentsQuery}`);
        } else {
            // No documents to search for, so return empty object, as requestSearch does if it
            // finds no documents.
            searchPromise = Promise.resolve({});
        }
        searchPromise.then(
            (results) => {
                // `results` is the search results object, or {} if it 404ed.
                if (results['@graph'] && results['@graph'].length > 0) {
                    // Split the results into arrays of modification and characterization
                    // document objects.
                    results['@graph'].forEach((document) => {
                        if (characterizationDocumentAtIds.indexOf(document['@id']) > -1) {
                            characterizationDocuments.push(document);
                        } else {
                            modificationDocuments.push(document);
                        }
                    });
                }

                // If the resulting documents are different from what we have in state, then
                // update the state.
                if (this.documentsChanged(modificationDocuments, characterizationDocuments)) {
                    this.setState({ modificationDocuments, characterizationDocuments });
                }
            }
        );
    }

    // Compare the given modificationDocuments and characterizationDocuments arrays with what's
    // currently in state, returning true if they're different.
    documentsChanged(modificationDocuments, characterizationDocuments) {
        if (modificationDocuments.length !== this.state.modificationDocuments.length ||
            characterizationDocuments.length !== this.state.characterizationDocuments.length) {
            return true;
        }
        if (modificationDocuments.some((document, i) => document['@id'] !== this.state.modificationDocuments[i]['@id'])) {
            return true;
        }
        if (characterizationDocuments.some((document, i) => document['@id'] !== this.state.characterizationDocuments[i]['@id'])) {
            return true;
        }
        return false;
    }

    render() {
        const { context, session, sessionProperties } = this.props;

        // Configure breadcrumbs for the page.
        const crumbs = [
            { id: 'Genetic Modifications' },
            { id: context.target && context.target.label, query: `target.label=${context.target && context.target.label}`, tip: context.target && context.target.label },
            { id: context.modification_type, query: `modification_type=${context.modification_type}`, tip: context.modification_type },
        ];

        const crumbsReleased = (context.status === 'released');

        return (
            <div className={globals.itemClass(context, 'view-item')}>
                <header>
                    <Breadcrumbs root="/search/?type=GeneticModification" crumbs={crumbs} crumbsReleased={crumbsReleased} />
                    <h1>{context.accession}</h1>
                    <div className="replacement-accessions">
                        <AlternateAccession altAcc={context.alternate_accessions} />
                    </div>
                    <ItemAccessories item={context} audit={{ auditIndicators: this.props.auditIndicators, auditId: 'genetic-modification-audit' }} />
                </header>
                {this.props.auditDetail(context.audit, 'genetic-modification-audit', { session, sessionProperties, except: context['@id'] })}
                <Panel>
                    <PanelBody addClasses="panel__split">
                        <div className="panel__split-element">
                            <div className="panel__split-heading panel__split-heading--genetic-modification">
                                <h4>Summary</h4>
                            </div>
                            <dl className="key-value">
                                <div data-test="status">
                                    <dt>Status</dt>
                                    <dd><Status item={context} inline /></dd>
                                </div>

                                {context.description ?
                                    <div data-test="description">
                                        <dt>Description</dt>
                                        <dd>{context.description}</dd>
                                    </div>
                                : null}

                                <div data-test="type">
                                    <dt>Type</dt>
                                    <dd>{context.category}</dd>
                                </div>

                                {context.introduced_sequence ?
                                    <div data-test="type">
                                        <dt>Introduced sequence</dt>
                                        <dd>{context.introduced_sequence ? <span>{context.introduced_sequence}</span> : null}</dd>
                                    </div>
                                : null}

                                {context.introduced_gene ?
                                    <div data-test="introduced-gene">
                                        <dt>Introduced gene</dt>
                                        <dd><a href={context.introduced_gene}>{context.introduced_gene}</a></dd>
                                    </div>
                                : null}

                                {context.introduced_elements ?
                                    <div data-test="introduced-elements">
                                        <dt>Introduced elements</dt>
                                        <dd>{context.introduced_elements}</dd>
                                    </div>
                                : null}

                                {context.zygosity ?
                                    <div data-test="zygosity">
                                        <dt>Zygosity</dt>
                                        <dd>{context.zygosity}</dd>
                                    </div>
                                : null}

                                <IntroducedTags geneticModification={context} />

                                <div data-test="purpose">
                                    <dt>Purpose</dt>
                                    <dd>{context.purpose}</dd>
                                </div>
                            </dl>
                            <ModificationSite geneticModification={context} />
                            <ModificationMethod geneticModification={context} />
                        </div>

                        <div className="panel__split-element">
                            <Attribution geneticModification={context} />
                        </div>
                    </PanelBody>
                </Panel>

                <DocumentsRenderer
                    characterizations={context.characterizations || []}
                    modificationDocuments={this.state.modificationDocuments}
                    characterizationDocuments={this.state.characterizationDocuments}
                />

                <RelatedItems
                    title="Donors using this genetic modification"
                    url={`/search/?type=Donor&genetic_modifications.uuid=${context.uuid}`}
                    Component={DonorTable}
                />

                <RelatedItems
                    title="Biosamples using this genetic modification"
                    url={`/search/?type=Biosample&applied_modifications.uuid=${context.uuid}`}
                    Component={BiosampleTable}
                />
            </div>
        );
    }
}

GeneticModificationComponent.propTypes = {
    context: PropTypes.object.isRequired, // GM object being displayed
    auditIndicators: PropTypes.func.isRequired, // Audit HOC function to display audit indicators
    auditDetail: PropTypes.func.isRequired, // Audit HOC function to display audit details
    session: PropTypes.object, // Login information from <App>
    sessionProperties: PropTypes.object,
};

GeneticModificationComponent.defaultProps = {
    session: null,
    sessionProperties: null,
};

const GeneticModificationInternal = (props, reactContext) => (
    <GeneticModificationComponent {...props} session={reactContext.session} sessionProperties={reactContext.session_properties} />
);

GeneticModificationInternal.propTypes = {
    context: PropTypes.object.isRequired, // GM object being displayed
    auditIndicators: PropTypes.func.isRequired, // Audit HOC function to display audit indicators
    auditDetail: PropTypes.func.isRequired, // Audit HOC function to display audit details
};

GeneticModificationInternal.contextTypes = {
    session: PropTypes.object, // Login information from <App>
    session_properties: PropTypes.object,
};

const GeneticModification = auditDecor(GeneticModificationInternal);

globals.contentViews.register(GeneticModification, 'GeneticModification');


const ListingComponent = (props, reactContext) => {
    const result = props.context;

    return (
        <li className={resultItemClass(result)}>
            <div className="result-item">
                <div className="result-item__data">
                    <a href={result['@id']} className="result-item__link">{result.category} &mdash; {result.purpose}</a>
                    <div className="result-item__data-row">
                        {result.modified_site_by_target_id ? <div><strong>Target: </strong>{result.modified_site_by_target_id.name}</div> : null}
                        {result.method ? <div><strong>Method: </strong>{result.method}</div> : null}
                        {result.nucleic_acid_delivery_method && result.nucleic_acid_delivery_method.length > 0 ?
                            <div><strong>Nucleic acid delivery method: </strong>{result.nucleic_acid_delivery_method.join(', ')}</div>
                        : null}
                        {result.lab ? <div><strong>Lab: </strong>{result.lab.title}</div> : null}
                    </div>
                </div>
                <div className="result-item__meta">
                    <div className="result-item__meta-title">Genetic modification</div>
                    <div className="result-item__meta-id">{` ${result.accession}`}</div>
                    <Status item={result.status} badgeSize="small" css="result-table__status" />
                    {props.auditIndicators(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties, search: true })}
                </div>
                <PickerActions context={result} />
            </div>
            {props.auditDetail(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties })}
        </li>
    );
};

ListingComponent.propTypes = {
    context: PropTypes.object.isRequired, // Search results object
    auditDetail: PropTypes.func.isRequired, // Audit HOC function to show audit details
    auditIndicators: PropTypes.func.isRequired, // Audit HOC function to display audit indicators
};

ListingComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
    session_properties: PropTypes.object,
};

const Listing = auditDecor(ListingComponent);

globals.listingViews.register(Listing, 'GeneticModification');


// Display a table of genetic modifications.
const GeneticModificationSummary = (props) => {
    const { geneticModifications } = props;

    return (
        <SortTablePanel title="Genetic modifications">
            <SortTable list={geneticModifications} columns={GeneticModificationSummary.columns} />
        </SortTablePanel>
    );
};

GeneticModificationSummary.propTypes = {
    geneticModifications: PropTypes.array, // Array of genetic modifications to display
};

GeneticModificationSummary.defaultProps = {
    geneticModifications: null,
};

GeneticModificationSummary.columns = {
    accession: {
        title: 'Accession',
        display: item => <a href={item['@id']}>{item.accession}</a>,
    },
    category: { title: 'Category' },
    purpose: { title: 'Purpose' },
    method: { title: 'Method' },
    nucleic_acid_delivery_method: {
        title: 'Nucleic acid delivery method',
        display: item => (item.nucleic_acid_delivery_method && item.nucleic_acid_delivery_method.length > 0 ? item.nucleic_acid_delivery_method.join(', ') : null),
    },
    site: {
        title: 'Site',
        display: item => (hasModificationSiteProps(item) ? <ModificationSiteItems geneticModification={item} itemClass={'gm-table-modification-site'} /> : null),
    },
};

export default GeneticModificationSummary;


// The next few components override parts of the standard documents panel for genetic modification
// characterizations. GM characterizations are attachments and not actual document objects, so the
// default document display components have to be overridden with these. See globals.js for a
// summary of the different document panel components.

const EXCERPT_LENGTH = 80; // Maximum number of characters in an excerpt

const CharacterizationHeader = props => (
    <div className="document__header">
        {props.doc.characterization_method} {props.label ? <span>{props.label}</span> : null}
    </div>
);

CharacterizationHeader.propTypes = {
    doc: PropTypes.object.isRequired, // Characterization object to render
    label: PropTypes.string, // Extra label to add to document type in header
};

CharacterizationHeader.defaultProps = {
    label: '',
};


const CharacterizationCaption = (props) => {
    const doc = props.doc;
    const caption = doc.caption;
    let excerpt;

    if (caption && caption.length > EXCERPT_LENGTH) {
        excerpt = globals.truncateString(caption, EXCERPT_LENGTH);
    }

    return (
        <div className="document__caption">
            {excerpt || caption ?
                <div data-test="caption">
                    <strong>{excerpt ? 'Caption excerpt: ' : 'Caption: '}</strong>
                    {excerpt ? <span>{excerpt}</span> : <span>{caption}</span>}
                </div>
            : <em>No caption</em>}
        </div>
    );
};

CharacterizationCaption.propTypes = {
    doc: PropTypes.object.isRequired, // Document object to render
};


const CharacterizationDocuments = (props) => {
    const docs = props.docs.filter(doc => !!doc);
    return (
        <dd>
            {docs.map((doc, i) => {
                if (doc && doc.attachment) {
                    const attachmentHref = url.resolve(doc['@id'], doc.attachment.href);
                    const docName = (doc.aliases && doc.aliases.length > 0) ? doc.aliases[0] :
                        ((doc.attachment && doc.attachment.download) ? doc.attachment.download : '');
                    return (
                        <div className="multi-dd dl-link" key={doc['@id']}>
                            <i className="icon icon-download" />&nbsp;
                            <a data-bypass="true" href={attachmentHref} download={doc.attachment.download}>
                                {docName}
                            </a>
                        </div>
                    );
                }
                return <div className="multi-dd dl-link" key={doc['@id']} />;
            })}
        </dd>
    );
};

CharacterizationDocuments.propTypes = {
    docs: PropTypes.array.isRequired,
};


const CharacterizationDetail = (props) => {
    const doc = props.doc;
    const keyClass = `document__detail${props.detailOpen ? ' active' : ''}`;
    const excerpt = doc.description && doc.description.length > EXCERPT_LENGTH;

    return (
        <div className={keyClass}>
            <dl className="key-value-doc" id={`panel${props.id}`} aria-labelledby={`tab${props.id}`} role="tabpanel">
                {excerpt ?
                    <div data-test="caption">
                        <dt>Caption</dt>
                        <dd>{doc.caption}</dd>
                    </div>
                : null}

                {doc.submitted_by && doc.submitted_by.title ?
                    <div data-test="submitted-by">
                        <dt>Submitted by</dt>
                        <dd>{doc.submitted_by.title}</dd>
                    </div>
                : null}

                <div data-test="lab">
                    <dt>Lab</dt>
                    <dd>{doc.lab.title}</dd>
                </div>

                {doc.award && doc.award.name ?
                    <div data-test="award">
                        <dt>Grant</dt>
                        <dd>
                            {doc.award['@id'] ? <a href={doc.award['@id']}>{doc.award.name}</a> : doc.award['@id']}
                        </dd>
                    </div>
                : null}

                {doc.submitter_comment ?
                    <div data-test="submittercomment">
                        <dt>Submitter comment</dt>
                        <dd>{doc.submitter_comment}</dd>
                    </div>
                : null}

                {doc.documents && doc.documents.length > 0 ?
                    <div data-test="documents">
                        <dt>Documents</dt>
                        <CharacterizationDocuments docs={doc.documents} />
                    </div>
                : null}
            </dl>
        </div>
    );
};

CharacterizationDetail.propTypes = {
    doc: PropTypes.object.isRequired, // Document object to render
    id: PropTypes.string.isRequired, // Unique ID string for the detail panel
    detailOpen: PropTypes.bool, // True if detail panel is visible
};

CharacterizationDetail.defaultProps = {
    detailOpen: false,
};


/**
 * Display a genetic modification characterization object.
 */
const GeneticModificationCharacterization = ({ context }) => {
    const documentSpecs = [
        { documents: [context] },
    ];
    return <DocumentsPanel title="Characterizations" documentSpecs={documentSpecs} />;
};

GeneticModificationCharacterization.propTypes = {
    /** GeneticModificationCharacterization object */
    context: PropTypes.object.isRequired,
};


// Parts of individual genetic modification characterization panels override default parts.
globals.contentViews.register(GeneticModificationCharacterization, 'GeneticModificationCharacterization');
globals.panelViews.register(Document, 'GeneticModificationCharacterization');
globals.documentViews.header.register(CharacterizationHeader, 'GeneticModificationCharacterization');
globals.documentViews.caption.register(CharacterizationCaption, 'GeneticModificationCharacterization');
globals.documentViews.preview.register(DocumentPreview, 'GeneticModificationCharacterization');
globals.documentViews.file.register(DocumentFile, 'GeneticModificationCharacterization');
globals.documentViews.detail.register(CharacterizationDetail, 'GeneticModificationCharacterization');
