'use strict';
var React = require('react');
var _ = require('underscore');
var url = require('url');
var panel = require('../libs/bootstrap/panel');
var {SvgIcon, CollapseIcon} = require('../libs/svg-icons');
var globals = require('./globals');
var image = require('./image');

var {Panel, PanelHeading, PanelBody} = panel;
var Attachment = image.Attachment;

const EXCERPT_LENGTH = 80; // Maximum number of characters in an excerpt


// To add more @types for document panels, see the bottom of this file.

// <DocumentsPanel> displays groups of documents within a panel. Each group gets its own title and shows
// one subpanel for each document within that group. The @type of each document must contain 'Document'
// somewhere.
//
// <DocumentsPanel> property: documentsList
//
// This object is mostly an array of arrays. The inner arrays holds the list of documents of one type,
// while the outer array holds all the types of arrays along with their section titles. Literally though,
// documentList is an array of objects, including the array of documents and the title to display above
// those documents within the panel.
//
// [
//     {
//         title: 'Section title',
//         documents: array of document objects
//     },
//     {
//         ...next one...
//     }
// ]

var DocumentsPanel = module.exports.DocumentsPanel = React.createClass({
    propTypes: {
        documentSpecs: React.PropTypes.array.isRequired, // List of document arrays and their titles
        title: React.PropTypes.string // Title of the document panel
    },

    render: function() {
        var documentSpecs = this.props.documentSpecs.length && _.compact(this.props.documentSpecs.map(documentSpecs => {
            return documentSpecs.documents.length ? documentSpecs : null;
        }));

        if (documentSpecs.length) {
            return (
                <div>
                    <Panel addClasses="clearfix">
                        <PanelHeading>
                            <h4>{this.props.title ? <span>{this.props.title}</span> : <span>Documents</span>}</h4>
                        </PanelHeading>
                        {documentSpecs.map((documentSpec, i) => {
                            if (documentSpec.documents.length) {
                                return (
                                    <PanelBody key={i} addClasses="panel-body-doc">
                                        <DocumentsSubpanels documentSpec={documentSpec} />
                                    </PanelBody>
                                );
                            }
                            return null;
                        })}
                    </Panel>
                </div>
            );
        }
        return null;
    }
});


var DocumentsSubpanels = module.exports.DocumentsSubpanels = React.createClass({
    propTypes: {
        documentSpec: React.PropTypes.object.isRequired // List of document arrays and their titles
    },

    render: function() {
        var documentSpec = this.props.documentSpec;

        return (
            <div>
                {documentSpec.title ? <h4>{documentSpec.title}</h4> : null}
                <div className="panel-docs-list">
                    {documentSpec.documents.map(doc => {
                        var PanelView = globals.panel_views.lookup(doc);
                        return <PanelView key={doc['@id']} context={doc} />;
                    })}
                </div>
            </div>
        );
    }
});


// Display a single document within a <DocumentPanel>. This routine requires that you register display components for each
// of the five major parts of a single document panel. See globals.js for a guide to the parts.
var Document = module.exports.Document = React.createClass({
    getInitialState: function() {
        return {panelOpen: false};
    },

    // Clicking the Lab bar inverts visible state of the popover
    handleClick: function(e) {
        e.preventDefault();
        e.stopPropagation();

        // Tell parent (App component) about new popover state
        // Pass it this component's React unique node ID
        this.setState({panelOpen: !this.state.panelOpen});
    },

    render: function() {
        var context = this.props.context;

        // Set up rendering components
        var DocumentHeaderView = globals.document_views.header.lookup(context);
        var DocumentCaptionView = globals.document_views.caption.lookup(context);
        var DocumentPreviewView = globals.document_views.preview.lookup(context);
        var DocumentFileView = globals.document_views.file.lookup(context);
        var DocumentDetailView = globals.document_views.detail.lookup(context);

        return (
            <section className="panel-doc">
                <Panel addClasses={globals.itemClass(context, 'view-detail')}>
                    <DocumentHeaderView doc={context} />
                    <PanelBody>
                        <div className="document-header">
                            <DocumentPreviewView doc={context} />
                            <DocumentCaptionView doc={context} />
                        </div>
                        <DocumentFileView doc={context} detailOpen={this.state.panelOpen} detailSwitch={this.handleClick} />
                        <DocumentDetailView doc={context} detailOpen={this.state.panelOpen} key={this.props.key} />
                    </PanelBody>
                </Panel>
            </section>
        );
    }
});


// Document header component -- default
var DocumentHeader = module.exports.DocumentHeader = React.createClass({
    propTypes: {
        doc: React.PropTypes.object.isRequired // Document object to render
    },

    render: function() {
        var doc = this.props.doc;

        return (
            <div className="panel-header document-title sentence-case">
                {doc.document_type}
            </div>
        );
    }
});

// Document caption component -- default
var DocumentCaption = module.exports.DocumentCaption = React.createClass({
    propTypes: {
        doc: React.PropTypes.object.isRequired // Document object to render
    },

    render: function() {
        var doc = this.props.doc;
        var excerpt, caption = doc.description;
        if (caption && caption.length > EXCERPT_LENGTH) {
            excerpt = globals.truncateString(caption, EXCERPT_LENGTH);
        }

        return (
            <div className="document-intro document-meta-data">
                {excerpt || caption ?
                    <div data-test="caption">
                        <strong>{excerpt ? 'Description excerpt: ' : 'Description: '}</strong>
                        {excerpt ? <span>{excerpt}</span> : <span>{caption}</span>}
                    </div>
                : <em>No description</em>}
            </div>
        );
    }
});

// Document preview component -- default
var DocumentPreview = module.exports.DocumentPreview = React.createClass({
    propTypes: {
        doc: React.PropTypes.object.isRequired // Document object to render
    },

    render: function() {
        return (
            <figure>
                <Attachment context={this.props.doc} attachment={this.props.doc.attachment} className="characterization" />
            </figure>
        );
    }
});


// Document file component -- default
var DocumentFile = module.exports.DocumentFile = React.createClass({
    propTypes: {
        doc: React.PropTypes.object.isRequired, // Document object to render
        detailOpen: React.PropTypes.bool, // True if detail panel is visible
        detailSwitch: React.PropTypes.func // Parent component function to call when detail switch clicked
    },

    render: function() {
        var {doc, detailOpen, detailSwitch} = this.props;

        if (doc.attachment && doc.attachment.href && doc.attachment.download) {
            var attachmentHref = url.resolve(doc['@id'], doc.attachment.href);
            var dlFileTitle = "Download file " + doc.attachment.download;

            return (
                <div className="dl-bar">
                    <i className="icon icon-download"></i>&nbsp;
                    <a data-bypass="true" title={dlFileTitle} href={attachmentHref} download={doc.attachment.download}>
                        {doc.attachment.download}
                    </a>
                    {detailSwitch ?
                        <div className="detail-switch">
                            <a href="#" data-trigger onClick={detailSwitch} className="collapsing-doc">
                                {CollapseIcon(!this.props.detailOpen)}
                            </a>
                        </div>
                    : null}
                </div>
            );
        }

        return (
            <div className="dl-bar">
                <em>Document not available</em>
            </div>
        );
    }
});


// Document detail component -- default
var DocumentDetail = module.exports.DocumentDetail = React.createClass({
    propTypes: {
        doc: React.PropTypes.object.isRequired, // Document object to render
        detailOpen: React.PropTypes.bool, // True if detail panel is visible
        key: React.PropTypes.string // Unique key for identification
    },

    render: function() {
        var doc = this.props.doc;
        var keyClass = 'document-slider' + (this.props.detailOpen ? ' active' : '');
        var excerpt = doc.description && doc.description.length > EXCERPT_LENGTH;

        return (
            <div className={keyClass}>
                <dl className='key-value-doc' id={'panel' + this.props.key} aria-labeledby={'tab' + this.props.key} role="tabpanel">
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
                            <dd>{doc.award.name}</dd>
                        </div>
                    : null}
                </dl>
            </div>
        );
    }
});

// Register document @types so they display in the standard document panel
globals.panel_views.register(Document, 'Document');

// Register document header rendering components
globals.document_views.header.register(DocumentHeader, 'Document');

// Register document caption rendering components
globals.document_views.caption.register(DocumentCaption, 'Document');

// Register document preview rendering components
globals.document_views.preview.register(DocumentPreview, 'Document');

// Register document file rendering components
globals.document_views.file.register(DocumentFile, 'Document');

// Register document detail rendering components
globals.document_views.detail.register(DocumentDetail, 'Document');


// Display a panel for attachments that aren't a part of an associated document
var AttachmentPanel = module.exports.AttachmentPanel = React.createClass({
    propTypes: {
        context: React.PropTypes.object.isRequired, // Object that owns the attachment; needed for attachment path
        attachment: React.PropTypes.object.isRequired, // Attachment being rendered
        title: React.PropTypes.string // Title to display in the caption area
    },

    render: function() {
        var {context, attachment, title} = this.props;

        // Make the download link
        var download, attachmentHref;
        if (attachment.href && attachment.download) {
            attachmentHref = url.resolve(context['@id'], attachment.href);
            download = (
                <div className="dl-link">
                    <i className="icon icon-download"></i>&nbsp;
                    <a data-bypass="true" href={attachmentHref} download={attachment.download}>
                        Download
                    </a>
                </div>
            );
        } else {
            download = <em>Attachment not available to download</em>;
        }

        return (
            <section className="col-sm-12 col-md-6">
                <Panel addClasses={globals.itemClass(context, 'view-detail quality-metric-header')}>
                    <figure>
                        <Attachment context={context} attachment={attachment} className="characterization" />
                    </figure>
                    <div className="document-intro document-meta-data">
                        {title ?
                            <div data-test="attachments">
                                <strong>Attachment: </strong>
                                {title}
                            </div>
                        : null}
                        {download}
                    </div>
                </Panel>
            </section>
        );
    }
});
