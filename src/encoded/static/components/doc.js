import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import url from 'url';
import { Panel, PanelHeading, PanelBody } from '../libs/bootstrap/panel';
import { collapseIcon } from '../libs/svg-icons';
import { FetchedData, Param } from './fetched';
import * as globals from './globals';
import { Attachment } from './image';

const EXCERPT_LENGTH = 80; // Maximum number of characters in an excerpt


// To add more @types for document panels, see the bottom of this file.

// <DocumentsPanel> displays groups of documents within a panel. Each group gets its own title and shows
// one subpanel for each document within that group. The @type of each document must contain 'Document'
// somewhere.
//
// <DocumentsPanel> property: documentsList
//
// This object is mostly an array of arrays. The inner arrays holds the list of documents of one type,
// while the outer array holds all the types of arrays along with their section label. Literally though,
// documentList is an array of objects, including the array of documents and the label to display above
// those documents within the panel.
//
// [
//     {
//         label: 'document label',
//         documents: array of document objects
//     },
//     {
//         ...next one...
//     }
// ]

export const DocumentsPanel = (props) => {
    // Filter documentSpecs to just those that have actual documents in them.
    const documentSpecsMapped = props.documentSpecs.length && _.compact(props.documentSpecs.map(documentSpecs => (
        documentSpecs.documents.length ? documentSpecs : null
    )));

    // Concatenate all documents, and map their UUIDs to corresponding labels
    let allDocs = [];
    const docLabelMap = {};
    documentSpecsMapped.forEach((spec) => {
        spec.documents.forEach((doc) => {
            docLabelMap[doc.uuid] = spec.label;
        });
        allDocs = allDocs.concat(spec.documents);
    });

    if (documentSpecsMapped.length) {
        return (
            <div>
                <Panel addClasses="clearfix">
                    <PanelHeading>
                        <h4>{props.title ? <span>{props.title}</span> : <span>Documents</span>}</h4>
                    </PanelHeading>
                    <PanelBody addClasses="panel-body-doc doc-panel__outer">
                        <section className="doc-panel__inner">
                            {allDocs.map((doc) => {
                                const PanelView = globals.panelViews.lookup(doc);
                                return <PanelView key={doc['@id']} label={docLabelMap[doc.uuid]} context={doc} />;
                            })}
                        </section>
                    </PanelBody>
                </Panel>
            </div>
        );
    }
    return null;
};

DocumentsPanel.propTypes = {
    documentSpecs: PropTypes.array.isRequired, // List of document arrays and their titles
    title: PropTypes.string, // Title of the document panel
};

DocumentsPanel.defaultProps = {
    title: '',
};


// Called when a GET request for all the documents associated with an experiment returns with the
// array of matching documents.
const DocumentsPanelRenderer = (props) => {
    const documents = props.documentSearch['@graph'];
    if (documents && documents.length) {
        return <DocumentsPanel documentSpecs={[{ documents }]} />;
    }
    return null;
};

DocumentsPanelRenderer.propTypes = {
    documentSearch: PropTypes.object, // Search result object; we use its @graph to get the documents,
};

DocumentsPanelRenderer.defaultProps = {
    documentSearch: null,
};


export const DocumentsPanelReq = (props) => {
    const { documents } = props;

    if (documents && documents.length) {
        return (
            <FetchedData>
                <Param name="documentSearch" url={`/search/?type=Item&${documents.map(docAtId => `@id=${docAtId}`).join('&')}`} />
                <DocumentsPanelRenderer />
            </FetchedData>
        );
    }
    return null;
};

DocumentsPanelReq.propTypes = {
    documents: PropTypes.array.isRequired, // Array of document @ids to request and render
};


export const DocumentsSubpanels = (props) => {
    const documentSpec = props.documentSpec;

    return (
        <div>
            <div className="panel-docs-list">
                {documentSpec.documents.map((doc) => {
                    const PanelView = globals.panelViews.lookup(doc);
                    return <PanelView key={doc['@id']} label={documentSpec.label} context={doc} />;
                })}
            </div>
        </div>
    );
};

DocumentsSubpanels.propTypes = {
    documentSpec: PropTypes.object.isRequired, // List of document arrays and their titles
};


// Display a single document within a <DocumentPanel>. This routine requires that you register display components for each
// of the five major parts of a single document panel. See globals.js for a guide to the parts.
export class Document extends React.Component {
    constructor() {
        super();
        this.state = {
            panelOpen: false,
        };

        // Bind non-React methods to this.
        this.handleClick = this.handleClick.bind(this);
    }

    // Clicking the Lab bar inverts visible state of the popover
    handleClick(e) {
        e.preventDefault();
        e.stopPropagation();

        // Tell parent (App component) about new popover state
        // Pass it this component's React unique node ID
        this.setState(prevState => ({
            panelOpen: !prevState.panelOpen,
        }));
    }

    render() {
        const context = this.props.context;

        // Set up rendering components
        const DocumentHeaderView = globals.documentViews.header.lookup(context);
        const DocumentCaptionView = globals.documentViews.caption.lookup(context);
        const DocumentPreviewView = globals.documentViews.preview.lookup(context);
        const DocumentFileView = globals.documentViews.file.lookup(context);
        const DocumentDetailView = globals.documentViews.detail.lookup(context);

        return (
            <section className="flexcol flexcol--doc">
                <Panel addClasses={globals.itemClass(context, 'document')}>
                    <DocumentHeaderView doc={context} label={this.props.label} />
                    <div className="document__intro">
                        <DocumentCaptionView doc={context} />
                        <DocumentPreviewView doc={context} />
                    </div>
                    <DocumentFileView doc={context} detailOpen={this.state.panelOpen} detailSwitch={this.handleClick} />
                    <DocumentDetailView doc={context} detailOpen={this.state.panelOpen} id={context['@id']} />
                </Panel>
            </section>
        );
    }
}

Document.propTypes = {
    context: PropTypes.object.isRequired, // Document context object to render
    label: PropTypes.string, // Extra label to add to document type in header
};

Document.defaultProps = {
    label: '',
};


// Document header component -- default
export const DocumentHeader = (props) => {
    const { doc, label } = props;

    return (
        <div className="document__header">
            {doc.document_type} {label ? <span>{label}</span> : null}
        </div>
    );
};

DocumentHeader.propTypes = {
    doc: PropTypes.object.isRequired, // Document object to render
    label: PropTypes.string, // Extra label to add to document type in header
};

DocumentHeader.defaultProps = {
    label: '',
};


// Document caption component -- default
export const DocumentCaption = (props) => {
    const doc = props.doc;
    const caption = doc.description;
    let excerpt;

    if (caption && caption.length > EXCERPT_LENGTH) {
        excerpt = globals.truncateString(caption, EXCERPT_LENGTH);
    }

    return (
        <div className="document__caption">
            {excerpt || caption ?
                <div data-test="caption">
                    <strong>{excerpt ? 'Description excerpt: ' : 'Description: '}</strong>
                    {excerpt ? <span>{excerpt}</span> : <span>{caption}</span>}
                </div>
            : <em>No description</em>}
        </div>
    );
};

DocumentCaption.propTypes = {
    doc: PropTypes.object.isRequired, // Document object to render
};


// Document preview component -- default
export const DocumentPreview = props => (
    <figure className="document__preview">
        <Attachment context={props.doc} attachment={props.doc.attachment} className="characterization" />
    </figure>
);

DocumentPreview.propTypes = {
    doc: PropTypes.object.isRequired, // Document object to render
};


// Document file component -- default
export const DocumentFile = (props) => {
    const { doc, detailOpen, detailSwitch } = props;

    if (doc.attachment && doc.attachment.href && doc.attachment.download) {
        const attachmentHref = url.resolve(doc['@id'], doc.attachment.href);
        const dlFileTitle = `Download file ${doc.attachment.download}`;

        return (
            <div className="document__file">
                <div className="document__file-name">
                    <i className="icon icon-download document__file-name-icon" />
                    <a data-bypass="true" className="document__file-name-link" title={dlFileTitle} href={attachmentHref} download={doc.attachment.download}>
                        {doc.attachment.download}
                    </a>
                </div>
                {detailSwitch ?
                    <button data-trigger onClick={detailSwitch} className="document__file-detail-switch">
                        {collapseIcon(!detailOpen)}
                    </button>
                : null}
            </div>
        );
    }

    return (
        <div className="dl-bar">
            <em>Document not available</em>
        </div>
    );
};

DocumentFile.propTypes = {
    doc: PropTypes.object.isRequired, // Document object to render
    detailOpen: PropTypes.bool.isRequired, // True if detail panel is visible
    detailSwitch: PropTypes.func.isRequired, // Parent component function to call when detail switch clicked
};


// Document detail component -- default
const DocumentDetail = (props) => {
    const doc = props.doc;
    const keyClass = `document__detail${props.detailOpen ? ' active' : ''}`;
    const excerpt = doc.description && doc.description.length > EXCERPT_LENGTH;

    return (
        <div className={keyClass}>
            <dl className="key-value-doc" id={`panel-${props.id}`} aria-labelledby={`tab-${props.id}`} role="tabpanel">
                {excerpt ?
                    <div data-test="caption">
                        <dt>Description</dt>
                        <dd>{doc.description}</dd>
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
                        <dd><a href={doc.award['@id']}>{doc.award.name}</a></dd>
                    </div>
                : null}
            </dl>
        </div>
    );
};

DocumentDetail.propTypes = {
    doc: PropTypes.object.isRequired, // Document object to render
    detailOpen: PropTypes.bool, // True if detail panel is visible
    id: PropTypes.string, // Unique key for identification
};

DocumentDetail.defaultProps = {
    detailOpen: false,
    id: '',
};


// Register document @types so they display in the standard document panel
globals.panelViews.register(Document, 'Document');

// Register document header rendering components
globals.documentViews.header.register(DocumentHeader, 'Document');

// Register document caption rendering components
globals.documentViews.caption.register(DocumentCaption, 'Document');

// Register document preview rendering components
globals.documentViews.preview.register(DocumentPreview, 'Document');

// Register document file rendering components
globals.documentViews.file.register(DocumentFile, 'Document');

// Register document detail rendering components
globals.documentViews.detail.register(DocumentDetail, 'Document');


const QCAttachmentCaption = props => (
    <div className="document__caption">
        <div data-test="caption">
            <strong>Attachment: </strong>
            {props.title}
        </div>
    </div>
);

QCAttachmentCaption.propTypes = {
    title: PropTypes.string.isRequired, // Title to display for attachment
};


const QCAttachmentPreview = (props) => {
    const { context, attachment } = props;

    return (
        <figure className="document__preview">
            <Attachment context={context} attachment={attachment} className="characterization" />
        </figure>
    );
};

QCAttachmentPreview.propTypes = {
    context: PropTypes.object.isRequired, // QC metric object that owns the attachment to render
    attachment: PropTypes.object.isRequired, // Attachment to render
};


// Display a panel for attachments that aren't a part of an associated document
export const AttachmentPanel = (props) => {
    const { context, attachment, title, modal } = props;

    // Set up rendering components.
    const DocumentCaptionView = globals.documentViews.caption.lookup(context);
    const DocumentPreviewView = globals.documentViews.preview.lookup(context);

    // Determine the attachment area CSS classes based on whether they're displayed in a modal
    // or not.
    const attachmentClasses = `flexcol flexcol--attachment${modal ? '-modal' : ''}`;

    return (
        <section className={attachmentClasses}>
            <Panel addClasses={globals.itemClass(context, 'attachment')}>
                <div className="document__intro document__intro--attachment-only">
                    <DocumentCaptionView title={title} />
                    <DocumentPreviewView context={context} attachment={attachment} />
                </div>
            </Panel>
        </section>
    );
};

AttachmentPanel.propTypes = {
    context: PropTypes.object.isRequired, // Object that owns the attachment; needed for attachment path
    attachment: PropTypes.object.isRequired, // Attachment being rendered
    title: PropTypes.string, // Title to display in the caption area
    modal: PropTypes.bool, // `true` if attachments are displayed in a modal
};

AttachmentPanel.defaultProps = {
    title: '',
    modal: false,
};


// Register document caption rendering components
globals.documentViews.caption.register(QCAttachmentCaption, 'QualityMetric');

// Register document preview rendering components
globals.documentViews.preview.register(QCAttachmentPreview, 'QualityMetric');
