'use strict';
var React = require('react/addons');
var _ = require('underscore');
var url = require('url');
var panel = require('../libs/bootstrap/panel');
var globals = require('./globals');
var image = require('./image');

var {Panel, PanelBody} = panel;
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
        documentSpecs: React.PropTypes.array.isRequired // List of document arrays and their titles
    },

    render: function() {
        var documentSpecs = this.props.documentSpecs.length && _.compact(this.props.documentSpecs.map(documentSpecs => {
            return documentSpecs.documents.length ? documentSpecs : null;
        }));

        if (documentSpecs.length) {
            return (
                <div>
                    <h3>Documents</h3>
                    <Panel addClasses="clearfix">
                        {documentSpecs.map(documentSpec => {
                            if (documentSpec.documents.length) {
                                return (
                                    <PanelBody>
                                        {documentSpec.title ? <h4>{documentSpec.title}</h4> : null}
                                        <div className="row multi-columns-row">
                                            {documentSpec.documents.map(doc => {
                                                var PanelView = globals.panel_views.lookup(doc);
                                                return <PanelView key={doc['@id']} context={doc} />;
                                            })}
                                        </div>
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
            // Each section is a panel; name all Bootstrap 3 sizes so .multi-columns-row class works
            <section className="col-xs-12 col-sm-6 col-md-6 col-lg-4 doc-panel">
                <div className={globals.itemClass(context, 'view-item view-detail status-none panel')}>
                    <DocumentHeaderView doc={context} />
                    <div className="panel-body">
                        <div className="document-header">
                            <DocumentPreviewView doc={context} />
                            <DocumentCaptionView doc={context} />
                        </div>
                        <DocumentFileView doc={this.props.context} detailOpen={this.state.panelOpen} detailSwitch={this.handleClick} />
                        <DocumentDetailView doc={this.props.context} detailOpen={this.state.panelOpen} key={this.props.key} />
                    </div>
                </div>
            </section>
        );
    }
});


// Document header component -- default
var DocumentHeader = React.createClass({
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

// Document header component -- Characterizations
var CharacterizationHeader = React.createClass({
    propTypes: {
        doc: React.PropTypes.object.isRequired // Document object to render
    },

    render: function() {
        var doc = this.props.doc;

        return (
            <div className="panel-header document-title sentence-case">
                {doc.characterization_method}
            </div>
        );
    }
});


// Document caption component -- default
var DocumentCaption = React.createClass({
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
            <div className="document-intro document-meta-data key-value-left">
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

// Document caption component -- Characterizations
var CharacterizationCaption = React.createClass({
    propTypes: {
        doc: React.PropTypes.object.isRequired // Document object to render
    },

    render: function() {
        var doc = this.props.doc;
        var excerpt, caption = doc.caption;
        if (caption && caption.length > EXCERPT_LENGTH) {
            excerpt = globals.truncateString(caption, EXCERPT_LENGTH);
        }

        return (
            <dl className="document-intro document-meta-data key-value-left">
                {excerpt || caption ?
                    <div data-test="caption">
                        <strong>{excerpt ? 'Caption excerpt: ' : 'Caption: '}</strong>
                        {excerpt ? <span>{excerpt}</span> : <span>{caption}</span>}
                    </div>
                : <em>No caption</em>}
            </dl>
        );
    }
});


// Document preview component -- default
var DocumentPreview = React.createClass({
    propTypes: {
        doc: React.PropTypes.object.isRequired // Document object to render
    },

    render: function() {
        return (
            <figure>
                <Attachment context={this.props.doc} className="characterization" />
            </figure>
        );
    }
});


// Document file component -- default
var DocumentFile = React.createClass({
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
                        <div className={'detail-switch' + (detailOpen ? ' open' : '')}>
                            <i className={'icon detail-trigger' + (detailOpen ? ' open' : '')} onClick={detailSwitch}></i>
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
var DocumentDetail = React.createClass({
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

// Document detail component -- default
var CharacterizationDetail = React.createClass({
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
globals.panel_views.register(Document, 'BiosampleCharacterization');
globals.panel_views.register(Document, 'DonorCharacterization');

// Register document header rendering components
globals.document_views.header.register(DocumentHeader, 'Document');
globals.document_views.header.register(CharacterizationHeader, 'BiosampleCharacterization');
globals.document_views.header.register(CharacterizationHeader, 'DonorCharacterization');

// Register document caption rendering components
globals.document_views.caption.register(DocumentCaption, 'Document');
globals.document_views.caption.register(CharacterizationCaption, 'BiosampleCharacterization');
globals.document_views.caption.register(CharacterizationCaption, 'DonorCharacterization');

// Register document preview rendering components
globals.document_views.preview.register(DocumentPreview, 'Document');
globals.document_views.preview.register(DocumentPreview, 'BiosampleCharacterization');
globals.document_views.preview.register(DocumentPreview, 'DonorCharacterization');

// Register document file rendering components
globals.document_views.file.register(DocumentFile, 'Document');
globals.document_views.file.register(DocumentFile, 'BiosampleCharacterization');
globals.document_views.file.register(DocumentFile, 'DonorCharacterization');

// Register document detail rendering components
globals.document_views.detail.register(DocumentDetail, 'Document');
globals.document_views.detail.register(CharacterizationDetail, 'BiosampleCharacterization');
globals.document_views.detail.register(CharacterizationDetail, 'DonorCharacterization');
