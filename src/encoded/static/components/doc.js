'use strict';
var React = require('react/addons');
var _ = require('underscore');
var url = require('url');
var panel = require('../libs/bootstrap/panel');
var globals = require('./globals');
var image = require('./image');

var {Panel, PanelBody} = panel;
var Attachment = image.Attachment;

// To add more @types for document panels, see the bottom of this file.

// 'documents' Object
//
// This object is mostly an array of arrays. The inner arrays holds the list of documents
// of one type, while the outer array holds all the types of arrays along with their section titles.
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

var DocumentPanel = module.exports.DocumentPanel = React.createClass({
    propTypes: {
        documentList: React.PropTypes.array.isRequired // List of document arrays and their titles
    },

    render: function() {
        var documentList = this.props.documentList.length && _.compact(this.props.documentList.map(docObj => {
            return docObj.documents.length ? docObj : null;
        }));

        if (documentList && documentList.length) {
            return (
                <div>
                    <h3>Documents</h3>
                    <Panel addClasses="clearfix">
                        {this.props.documentList.map(docObj => {
                            if (docObj.documents.length) {
                                return (
                                    <PanelBody>
                                        <h4>{docObj.title}</h4>
                                        {docObj.documents.map(doc => {
                                            var PanelView = globals.panel_views.lookup(doc);
                                            return <PanelView key={doc['@id']} context={doc} />;
                                        })}
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
        var keyClass = 'document-slider' + (this.state.panelOpen ? ' active' : '');
        var figure = <Attachment context={this.props.context} className="characterization" />;

        var attachmentHref, download;
        if (context.attachment && context.attachment.href && context.attachment.download) {
            attachmentHref = url.resolve(context['@id'], context.attachment.href);
            var dlFileTitle = "Download file " + context.attachment.download;
            download = (
                <div className="dl-bar">
                    <i className="icon icon-download"></i>&nbsp;
                    <a data-bypass="true" title={dlFileTitle} href={attachmentHref} download={context.attachment.download}>
                        {context.attachment.download}
                    </a>
                </div>
            );
        } else {
            download = (
                <div className="dl-bar">
                    <em>Document not available</em>
                </div>
            );
        }

        var characterization = context['@type'].indexOf('Characterization') >= 0;
        var caption = characterization ? context.caption : context.description;
        var excerpt;
        if (caption && caption.length > 100) {
            excerpt = globals.truncateString(caption, 100);
        }
        var panelClass = 'view-item view-detail status-none panel';

        return (
            // Each section is a panel; name all Bootstrap 3 sizes so .multi-columns-row class works
            <section className="col-xs-12 col-sm-6 col-md-6 col-lg-4 doc-panel">
                <div className={globals.itemClass(context, panelClass)}>
                    <div className="panel-header document-title sentence-case">
                        {characterization ? context.characterization_method : context.document_type}
                    </div>
                    <div className="panel-body">
                        <div className="document-header">
                            <figure>
                                {figure}
                            </figure>

                            <dl className="document-intro document-meta-data key-value-left">
                                {excerpt || caption ?
                                    <div data-test="caption">
                                        {characterization ?
                                            <dt>{excerpt ? 'Caption excerpt' : 'Caption'}</dt>
                                        :
                                            <dt>{excerpt ? 'Description excerpt' : 'Description'}</dt>
                                        }
                                        <dd>{excerpt ? excerpt : caption}</dd>
                                    </div>
                                : null}
                            </dl>
                        </div>
                        {download}
                        <div className={keyClass}>
                            <dl className='key-value' id={'panel' + this.props.key} aria-labeledby={'tab' + this.props.key} role="tabpanel">
                                {excerpt && characterization ?
                                    <div data-test="caption">
                                        <dt>Caption</dt>
                                        <dd>{context.caption}</dd>
                                    </div>
                                : null}

                                {excerpt && !characterization ?
                                    <div data-test="caption">
                                        <dt>Description</dt>
                                        <dd>{context.description}</dd>
                                    </div>
                                : null}

                                {context.submitted_by && context.submitted_by.title ?
                                    <div data-test="submitted-by">
                                        <dt>Submitted by</dt>
                                        <dd>{context.submitted_by.title}</dd>
                                    </div>
                                : null}

                                <div data-test="lab">
                                    <dt>Lab</dt>
                                    <dd>{context.lab.title}</dd>
                                </div>

                                {context.award && context.award.name ?
                                    <div data-test="award">
                                        <dt>Grant</dt>
                                        <dd>{context.award.name}</dd>
                                    </div>
                                : null}
                            </dl>
                        </div>
                    </div>

                    <button onClick={this.handleClick} className="key-value-trigger panel-footer" id={'tab' + this.props.key} aria-controls={'panel' + this.props.key} role="tab">
                        {this.state.panelOpen ? 'Less' : 'More'}
                    </button>
                </div>
            </section>
        );
    }
});


// Register document @types so they display in the standard document panel
globals.panel_views.register(Document, 'Document');
globals.panel_views.register(Document, 'BiosampleCharacterization');
globals.panel_views.register(Document, 'DonorCharacterization');
