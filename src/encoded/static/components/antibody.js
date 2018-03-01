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
import StatusLabel from './statuslabel';


const LotComponent = (props, reactContext) => {
    const context = props.context;

    // Sort characterization arrays
    const characterizations = _(context.characterizations).sortBy(characterization => (
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
                            <span>Antibody against {Object.keys(targets).map((target, i) => {
                                const targetObj = targets[target];
                                return <span key={i}>{i !== 0 ? ', ' : ''}<em>{targetObj.organism.scientific_name}</em>{` ${targetObj.label}`}</span>;
                            })}</span>
                        :
                            <span>Antibody</span>
                        }
                    </h3>
                    <div className="status-line">
                        <div className="characterization-status-labels">
                            <StatusLabel title="Status" status={context.status} />
                        </div>
                        {props.auditIndicators(context.audit, 'antibody-audit', { session: reactContext.session })}
                    </div>
                </div>
            </header>
            {props.auditDetail(context.audit, 'antibody-audit', { except: context['@id'], session: reactContext.session })}

            {context.lot_reviews && context.lot_reviews.length ?
                <div className="antibody-statuses">
                    {antibodyStatuses}
                </div>
            :
                <div className="characterization-status-labels">
                    <StatusLabel status="Awaiting lab characterization" />
                </div>
            }

            <Panel addClasses="data-display">
                <PanelBody>
                    <dl className="key-value">
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
                title={'Experiments using this antibody'}
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
};

const Lot = auditDecor(LotComponent);

globals.contentViews.register(Lot, 'AntibodyLot');

// Must export for Jest testing.
export default Lot;


const AntibodyStatus = (props) => {
    const context = props.context;

    // Sort the lot reviews by their status according to our predefined order
    // given in the statusOrder array we imported from globals.js.
    const lotReviews = _.sortBy(context.lot_reviews, lotReview =>
        globals.statusOrder.indexOf(lotReview.status) // Use underscore indexOf so that this works in IE8
    );

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
        <section className="type-antibody-status view-detail panel">
            <div className="row">
                <div className="col-xs-12">
                    {Object.keys(statusTree).map((status) => {
                        const organisms = statusTree[status];
                        return (
                            <div key={status} className="row status-status-row">
                                {Object.keys(organisms).map((organism, i) => {
                                    const terms = Object.keys(organisms[organism]);
                                    return (
                                        <div key={i} className="row status-organism-row">
                                            <div className="col-sm-3 col-sm-push-9 status-status sentence-case">
                                                {i === 0 ? <span><i className={globals.statusClass(status, 'indicator icon icon-circle')} />{status}</span> : ''}
                                            </div>
                                            <div className="col-sm-2 col-sm-pull-3 status-organism">
                                                {organism}
                                            </div>
                                            <div className="col-sm-7 col-sm-pull-3 status-terms">
                                                {terms.length === 1 && terms[0] === 'not specified' ? '' : terms.join(', ')}
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        );
                    })}
                </div>
            </div>
        </section>
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
            <div className="document__characterization-badge"><StatusLabel status={doc.status} /></div>
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
