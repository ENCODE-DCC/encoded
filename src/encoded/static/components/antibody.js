import React from 'react';
import PropTypes from 'prop-types';
import url from 'url';
import _ from 'underscore';
import { auditDecor } from './audit';
import { Panel, PanelBody } from '../libs/bootstrap/panel';
import { collapseIcon } from '../libs/svg-icons';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import { ExperimentTable } from './dataset';
import { DbxrefList } from './dbxref';
import { DocumentsPanel, Document, DocumentPreview, CharacterizationDocuments } from './doc';
import { RelatedItems } from './item';
import { AlternateAccession } from './objectutils';
import { PickerActions } from './search';
import Status, { getObjectStatuses, sessionToAccessLevel } from './status';


// Order that antibody statuses should be displayed.
const antibodyStatusOrder = [
    'characterized to standards',
    'characterized to standards with exemption',
    'awaiting characterization',
    'partially characterized',
    'not pursued',
    'not characterized to standards',
];


const LotComponent = (props, reactContext) => {
    const context = props.context;

    // Sort characterization arrays, filtering for the current logged-in and administrative status.
    const accessLevel = sessionToAccessLevel(reactContext.session, reactContext.session_properties);
    const viewableStatuses = getObjectStatuses('AntibodyCharacterization', accessLevel);
    let characterizations = context.characterizations.filter(characterization => viewableStatuses.indexOf(characterization.status) !== -1);
    characterizations = _(characterizations).sortBy(characterization => (
        [characterization.target.label, characterization.target.organism.name]
    ));

    // Compile the document list
    const documentSpecs = [
        { documents: characterizations },
    ];

    // Build antibody status panel
    const PanelView = globals.panelViews.lookup(context);
    const antibodyStatuses = <PanelView context={context} key={context['@id']} />;

    // Make an array of targets with no falsy entries and no repeats
    const targets = {};
    if (context.lot_reviews && context.lot_reviews.length) {
        context.lot_reviews.forEach((lotReview) => {
            lotReview.targets.forEach((target) => {
                targets[target['@id']] = target;
            });
        });
    }
    const targetKeys = Object.keys(targets);

    // Set up the breadcrumbs
    const organismComponents = [];
    const organismTerms = [];
    const organismTips = [];
    const geneComponents = [];
    const geneTerms = [];
    const geneTips = [];
    targetKeys.forEach((key, i) => {
        const scientificName = targets[key].organism.scientific_name;
        const geneName = targets[key].gene_name;

        // Add to the information on organisms from the targets
        organismComponents.push(<span key={key}>{i > 0 ? <span> + <i>{scientificName}</i></span> : <i>{scientificName}</i>}</span>);
        organismTerms.push(`targets.organism.scientific_name=${scientificName}`);
        organismTips.push(scientificName);

        // Add to the information on gene names from the targets
        if (geneName && geneName !== 'unknown') {
            geneComponents.push(<span key={key}>{i > 0 ? <span> + {geneName}</span> : <span>{geneName}</span>}</span>);
            geneTerms.push(`targets.gene_name=${geneName}`);
            geneTips.push(geneName);
        }
    });

    const organismQuery = organismTerms.join('&');
    const geneQuery = geneTerms.join('&');
    const crumbs = [
        { id: 'Antibodies' },
        { id: organismComponents, query: organismQuery, tip: organismTips.join(' + ') },
        { id: geneComponents.length ? geneComponents : null, query: geneQuery, tip: geneTips.join(' + ') },
    ];

    return (
        <div className={globals.itemClass(context, 'view-item')}>
            <header className="row">
                <div className="col-sm-12">
                    <Breadcrumbs root="/search/?type=antibody_lot" crumbs={crumbs} />
                    <h2>{context.accession}</h2>
                    <AlternateAccession altAcc={context.alternate_accessions} />
                    <h3>
                        {targetKeys.length ?
                            <span>
                                Antibody against {Object.keys(targets).map((target, i) => {
                                    const targetObj = targets[target];
                                    return <span key={i}>{i !== 0 ? ', ' : ''}<em>{targetObj.organism.scientific_name}</em>{` ${targetObj.label}`}</span>;
                                })}
                            </span>
                        :
                            <span>Antibody</span>
                        }
                    </h3>
                    {props.auditIndicators(context.audit, 'antibody-audit', { session: reactContext.session })}
                </div>
            </header>
            {props.auditDetail(context.audit, 'antibody-audit', { except: context['@id'], session: reactContext.session })}

            <div className="antibody-statuses">
                {antibodyStatuses}
            </div>

            <Panel addClasses="data-display">
                <PanelBody>
                    <dl className="key-value">
                        <div data-test="status">
                            <dt>Status</dt>
                            <dd><Status item={context} css="dd-status" title="Antibody status" inline /></dd>
                        </div>

                        <div data-test="source">
                            <dt>Source (vendor)</dt>
                            <dd><a href={context.source.url}>{context.source.title}</a></dd>
                        </div>

                        <div data-test="productid">
                            <dt>Product ID</dt>
                            <dd><a href={context.url}>{context.product_id}</a></dd>
                        </div>

                        <div data-test="lotid">
                            <dt>Lot ID</dt>
                            <dd>{context.lot_id}</dd>
                        </div>

                        {Object.keys(targets).length ?
                            <div data-test="targets">
                                <dt>Targets</dt>
                                <dd>
                                    {targetKeys.map((target, i) => {
                                        const targetObj = targets[target];
                                        return <span key={i}>{i !== 0 ? ', ' : ''}<a href={target}>{targetObj.label}{' ('}<em>{targetObj.organism.scientific_name}</em>{')'}</a></span>;
                                    })}
                                </dd>
                            </div>
                        : null}

                        {context.lot_id_alias && context.lot_id_alias.length ?
                            <div data-test="lotidalias">
                                <dt>Lot ID aliases</dt>
                                <dd>{context.lot_id_alias.join(', ')}</dd>
                            </div>
                        : null}

                        <div data-test="host">
                            <dt>Host</dt>
                            <dd className="sentence-case">{context.host_organism.name}</dd>
                        </div>

                        {context.clonality ?
                            <div data-test="clonality">
                                <dt>Clonality</dt>
                                <dd className="sentence-case">{context.clonality}</dd>
                            </div>
                        : null}

                        {context.purifications && context.purifications.length ?
                            <div data-test="purifications">
                                <dt>Purification</dt>
                                <dd className="sentence-case">{context.purifications.join(', ')}</dd>
                            </div>
                        : null}

                        {context.isotype ?
                            <div data-test="isotype">
                                <dt>Isotype</dt>
                                <dd className="sentence-case">{context.isotype}</dd>
                            </div>
                        : null}

                        {context.antigen_description ?
                            <div data-test="antigendescription">
                                <dt>Antigen description</dt>
                                <dd>{context.antigen_description}</dd>
                            </div>
                        : null}

                        {context.antigen_sequence ?
                            <div data-test="antigensequence">
                                <dt>Antigen sequence</dt>
                                <dd className="sequence">{context.antigen_sequence}</dd>
                            </div>
                        : null}

                        {context.aliases && context.aliases.length ?
                            <div data-test="aliases">
                                <dt>Aliases</dt>
                                <dd>{context.aliases.join(', ')}</dd>
                            </div>
                        : null}

                        {context.dbxrefs && context.dbxrefs.length ?
                            <div data-test="dbxrefs">
                                <dt>External resources</dt>
                                <dd><DbxrefList context={context} dbxrefs={context.dbxrefs} /></dd>
                            </div>
                        : null}
                    </dl>
                </PanelBody>
            </Panel>

            <RelatedItems
                title="Experiments using this antibody"
                url={`/search/?type=Experiment&replicates.antibody.accession=${context.accession}`}
                Component={ExperimentTable}
            />

            <DocumentsPanel title="Characterizations" documentSpecs={documentSpecs} />
        </div>
    );
};

LotComponent.propTypes = {
    context: PropTypes.object.isRequired,
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

LotComponent.contextTypes = {
    session: PropTypes.object, // Login session information
    session_properties: PropTypes.object, // Logged-in user information
};

const Lot = auditDecor(LotComponent);

globals.contentViews.register(Lot, 'AntibodyLot');

// Must export for Jest testing.
export default Lot;


const AntibodyStatus = (props) => {
    const context = props.context;

    // Sort the lot reviews by their status according to our predefined order
    // given in the statusOrder array we imported from globals.js.
    const lotReviews = _.sortBy(context.lot_reviews, (lotReview =>
        antibodyStatusOrder.indexOf(lotReview.status)
    ));

    // Build antibody display object as a hierarchy: status=>organism=>biosample_term_name
    const statusTree = {};
    lotReviews.forEach((lotReview) => {
        // Status at top of hierarchy. If haven’t seen this status before, remember it
        if (!statusTree[lotReview.status]) {
            statusTree[lotReview.status] = {};
        }

        // Look at all organisms in current lot_review. They go under this lot_review's status
        const statusNode = statusTree[lotReview.status];
        lotReview.organisms.forEach((organism) => {
            // If haven’t seen this organism with this status before, remember it
            if (!statusNode[organism.scientific_name]) {
                statusNode[organism.scientific_name] = {};
            }

            // If haven't seen this biosample term name for this organism, remember it
            const organismNode = statusNode[organism.scientific_name];
            if (!organismNode[lotReview.biosample_term_name]) {
                organismNode[lotReview.biosample_term_name] = true;
            }
        });
    });

    return (
        <Panel>
            <PanelBody>
                {Object.keys(statusTree).map((status) => {
                    const organisms = statusTree[status];
                    return (
                        <div key={status} className="antibody-status">
                            {Object.keys(organisms).map((organism, i) => {
                                const terms = Object.keys(organisms[organism]);
                                return (
                                    <div key={i} className="antibody-status__group">
                                        <div className="antibody-status__organism">
                                            {organism}
                                        </div>
                                        <div className="antibody-status__terms">
                                            {terms.length === 1 && terms[0] === 'not specified' ? '' : terms.join(', ')}
                                        </div>
                                        <div className="antibody-status__status">
                                            {i === 0 ? <Status item={status} inline /> : null}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    );
                })}
            </PanelBody>
        </Panel>
    );
};

AntibodyStatus.propTypes = {
    context: PropTypes.object.isRequired,
};

globals.panelViews.register(AntibodyStatus, 'AntibodyLot');


// Antibody characterization documents

const EXCERPT_LENGTH = 80; // Maximum number of characters in an excerpt

// Document header component -- antibody characterization
const CharacterizationHeader = (props) => {
    const doc = props.doc;

    return (
        <div>
            <div className="document__header">
                {doc.target.label} {doc.target.organism.scientific_name ? <span>{' ('}<i>{doc.target.organism.scientific_name}</i>{')'}</span> : ''}
            </div>
            {doc.characterization_reviews && doc.characterization_reviews.length ?
                <div className="document__characterization-reviews">
                    {doc.characterization_reviews.map(review => (
                        <span key={review.biosample_term_name} className="document__characterization-biosample-term">{review.biosample_term_name}</span>
                    ))}
                </div>
            : null}
        </div>
    );
};

CharacterizationHeader.propTypes = {
    doc: PropTypes.object.isRequired, // Document object to render
};


// Document caption component -- antibody characterization
const CharacterizationCaption = (props) => {
    const doc = props.doc;

    return (
        <div className="document__caption">
            {doc.characterization_method ?
                <div data-test="caption">
                    <strong>Method: </strong>
                    {doc.characterization_method}
                </div>
            : null}
        </div>
    );
};

CharacterizationCaption.propTypes = {
    doc: PropTypes.object.isRequired, // Document object to render
};


const CharacterizationFile = (props) => {
    const { doc, detailOpen, detailSwitch } = props;

    return (
        <div className="document__file">
            <div className="document__characterization-badge"><Status item={doc} size="small" inline /></div>
            {detailSwitch ?
                <button onClick={detailSwitch} className="document__file-detail-switch">
                    {collapseIcon(!detailOpen)}
                </button>
            : null}
        </div>
    );
};

CharacterizationFile.propTypes = {
    doc: PropTypes.object.isRequired, // Document object to render
    detailOpen: PropTypes.bool, // True if detail panel is visible
    detailSwitch: PropTypes.func, // Parent component function to call when detail switch clicked
};

CharacterizationFile.defaultProps = {
    detailOpen: false,
    detailSwitch: null,
};


const CharacterizationDetail = (props) => {
    const { doc, detailOpen, id } = props;
    const keyClass = `document__detail${detailOpen ? ' active' : ''}`;
    const excerpt = doc.caption && doc.caption.length > EXCERPT_LENGTH;

    let download;
    let attachmentHref;
    if (doc.attachment && doc.attachment.href && doc.attachment.download) {
        attachmentHref = url.resolve(doc['@id'], doc.attachment.href);
        download = (
            <dd className="dl-link">
                <i className="icon icon-download" />&nbsp;
                <a data-bypass="true" href={attachmentHref} download={doc.attachment.download}>
                    {doc.attachment.download}
                </a>
            </dd>
        );
    } else {
        download = (
            <em>Document not available</em>
        );
    }

    return (
        <div className={keyClass}>
            <dl className="key-value-doc" id={`panel${id}`} aria-labelledby={`tab${id}`} role="tabpanel">
                {excerpt ?
                    <div data-test="caption">
                        <dt>Caption</dt>
                        <dd className="sentence-case para-text">{doc.caption}</dd>
                    </div>
                : null}

                {doc.submitter_comment ?
                    <div data-test="submittercomment">
                        <dt>Submitter comment</dt>
                        <dd className="para-text">{doc.submitter_comment}</dd>
                    </div>
                : null}

                {doc.notes ?
                    <div data-test="reviewercomment">
                        <dt>Reviewer comment</dt>
                        <dd className="para-text">{doc.notes}</dd>
                    </div>
                : null}

                {doc.submitted_by && doc.submitted_by.title ?
                    <div data-test="submitted">
                        <dt>Submitted by</dt>
                        <dd>{doc.submitted_by.title}</dd>
                    </div>
                : null}

                <div data-test="lab">
                    <dt>Lab</dt>
                    <dd>{doc.lab.title}</dd>
                </div>

                <div data-test="grant">
                    <dt>Grant</dt>
                    <dd><a href={doc.award['@id']}>{doc.award.name}</a></dd>
                </div>

                <div data-test="download">
                    <dt>Download</dt>
                    {download}
                </div>

                {doc.documents && doc.documents.length ?
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
    detailOpen: PropTypes.bool, // True if detail panel is visible
    id: PropTypes.string, // Unique key for identification
};

CharacterizationDetail.defaultProps = {
    detailOpen: false,
    id: '',
};


// Parts of individual document panels
globals.panelViews.register(Document, 'AntibodyCharacterization');
globals.documentViews.header.register(CharacterizationHeader, 'AntibodyCharacterization');
globals.documentViews.caption.register(CharacterizationCaption, 'AntibodyCharacterization');
globals.documentViews.preview.register(DocumentPreview, 'AntibodyCharacterization');
globals.documentViews.file.register(CharacterizationFile, 'AntibodyCharacterization');
globals.documentViews.detail.register(CharacterizationDetail, 'AntibodyCharacterization');


// Display one antibody status indicator
class StatusIndicator extends React.Component {
    constructor() {
        super();

        // Set initial React component state.
        this.state = {
            tipOpen: false,
            tipStyles: {},
        };

        // Bind `this` to non-React methods.
        this.onMouseEnter = this.onMouseEnter.bind(this);
        this.onMouseLeave = this.onMouseLeave.bind(this);
    }

    // Display tooltip on hover
    onMouseEnter() {
        function getNextElementSibling(el) {
            // IE8 doesn't support nextElementSibling
            return el.nextElementSibling ? el.nextElementSibling : el.nextSibling;
        }

        // Get viewport bounds of result table and of this tooltip
        let whiteSpace = 'nowrap';
        const resultBounds = document.getElementById('result-table').getBoundingClientRect();
        const resultWidth = resultBounds.right - resultBounds.left;
        const tipBounds = _.clone(getNextElementSibling(this.indicator).getBoundingClientRect());
        const tipWidth = tipBounds.right - tipBounds.left;
        let width = tipWidth;
        if (tipWidth > resultWidth) {
            // Tooltip wider than result table; set tooltip to result table width and allow text to wrap
            tipBounds.right = (tipBounds.left + resultWidth) - 2;
            whiteSpace = 'normal';
            width = tipBounds.right - tipBounds.left - 2;
        }

        // Set an inline style to move the tooltip if it runs off right edge of result table
        const leftOffset = resultBounds.right - tipBounds.right;
        if (leftOffset < 0) {
            // Tooltip goes outside right edge of result table; move it to the left
            this.setState({ tipStyles: { left: `${leftOffset + 10}px`, maxWidth: `${resultWidth}px`, whiteSpace, width: `${width}px` } });
        } else {
            // Tooltip fits inside result table; move it to native position
            this.setState({ tipStyles: { left: '10px', maxWidth: `${resultWidth}px`, whiteSpace, width: `${width}px` } });
        }

        this.setState({ tipOpen: true });
    }

    // Close tooltip when not hovering
    onMouseLeave() {
        this.setState({ tipStyles: { maxWidth: 'none', whiteSpace: 'nowrap', width: 'auto', left: '15px' } }); // Reset position and width
        this.setState({ tipOpen: false });
    }

    render() {
        const classes = `tooltip-status sentence-case${this.state.tipOpen ? ' tooltipopen' : ''}`;

        return (
            <span className="tooltip-status-trigger">
                <span ref={(indicator) => { this.indicator = indicator; }} onMouseEnter={this.onMouseEnter} onMouseLeave={this.onMouseLeave}>
                    <Status item={this.props.status} size="small" noLabel inline />
                </span>
                <div className={classes} style={this.state.tipStyles}>
                    {this.props.status}<br /><span>{this.props.terms.join(', ')}</span>
                </div>
            </span>
        );
    }
}

StatusIndicator.propTypes = {
    status: PropTypes.string,
    terms: PropTypes.array.isRequired,
};

StatusIndicator.defaultProps = {
    status: '',
};


// Display the status indicators for one target
const StatusIndicators = (props) => {
    const { targetTree, target } = props;

    return (
        <span className="status-indicators">
            {Object.keys(targetTree[target]).map((status, i) => {
                if (status !== 'target') {
                    return <StatusIndicator key={i} status={status} terms={targetTree[target][status]} />;
                }
                return null;
            })}
        </span>
    );
};

StatusIndicators.propTypes = {
    targetTree: PropTypes.object.isRequired,
    target: PropTypes.string.isRequired,
};


const ListingComponent = (props, reactContext) => {
    const result = props.context;

    // Sort the lot reviews by their status according to our predefined order
    // given in the statusOrder array.
    const lotReviews = _.sortBy(result.lot_reviews, lotReview => antibodyStatusOrder.indexOf(lotReview.status));

    // Build antibody display object as a hierarchy: target=>status=>biosample_term_names
    const targetTree = {};
    lotReviews.forEach((lotReview) => {
        lotReview.targets.forEach((target) => {
            // If we haven't seen this target, save it in targetTree along with the
            // corresponding target and organism structures.
            if (!targetTree[target.name]) {
                targetTree[target.name] = { target };
            }
            const targetNode = targetTree[target.name];

            // If we haven't seen the status, save it in the targetTree target
            if (!targetNode[lotReview.status]) {
                targetNode[lotReview.status] = [];
            }
            const statusNode = targetNode[lotReview.status];

            // If we haven't seen the biosample term name, save it in the targetTree target status
            if (statusNode.indexOf(lotReview.biosample_term_name) === -1) {
                statusNode.push(lotReview.biosample_term_name);
            }
        });
    });

    return (
        <li>
            <div className="clearfix">
                <PickerActions {...props} />
                <div className="pull-right search-meta">
                    <p className="type meta-title">Antibody</p>
                    <p className="type">{` ${result.accession}`}</p>
                    <Status item={result.status} size="small" css="result-table__status" />
                    {props.auditIndicators(result.audit, result['@id'], { session: reactContext.session, search: true })}
                </div>
                <div className="accession">
                    {Object.keys(targetTree).map(target =>
                        <div key={target}>
                            <a href={result['@id']}>
                                {targetTree[target].target.label}
                                {targetTree[target].target.organism ? <span>{' ('}<i>{targetTree[target].target.organism.scientific_name}</i>{')'}</span> : ''}
                            </a>
                            <StatusIndicators targetTree={targetTree} target={target} />
                        </div>
                    )}
                </div>
                <div className="data-row">
                    <div><strong>Source: </strong>{result.source.title}</div>
                    <div><strong>Product ID / Lot ID: </strong>{result.product_id} / {result.lot_id}</div>
                </div>
            </div>
            {props.auditDetail(result.audit, result['@id'], { session: reactContext.session, except: result['@id'], forcedEditLink: true })}
        </li>
    );
};

ListingComponent.propTypes = {
    context: PropTypes.object.isRequired, // Antibody search results
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

ListingComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
};

const Listing = auditDecor(ListingComponent);

globals.listingViews.register(Listing, 'AntibodyLot');
