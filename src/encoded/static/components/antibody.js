'use strict';
var React = require('react');
var cx = require('react/lib/cx');
var url = require('url');
var _ = require('underscore');
var panel = require('../libs/bootstrap/panel');
var { collapseIcon } = require('../libs/svg-icons');
var globals = require('./globals');
var navigation = require('./navigation');
var dataset = require('./dataset');
var dbxref = require('./dbxref');
var image = require('./image');
var item = require('./item');
var audit = require('./audit');
var statuslabel = require('./statuslabel');
var doc = require('./doc');

var Breadcrumbs = navigation.Breadcrumbs;
var AuditIndicators = audit.AuditIndicators;
var AuditDetail = audit.AuditDetail;
var AuditMixin = audit.AuditMixin;
var DbxrefList = dbxref.DbxrefList;
var ExperimentTable = dataset.ExperimentTable;
var StatusLabel = statuslabel.StatusLabel;
var statusOrder = globals.statusOrder;
var RelatedItems = item.RelatedItems;
var {Panel, PanelBody} = panel;
var {DocumentsPanel, Document, DocumentPreview, DocumentFile} = doc;


var Lot = module.exports.Lot = React.createClass({
    mixins: [AuditMixin],
    render: function() {
        var context = this.props.context;

        // Sort characterization arrays
        var characterizations = _(context.characterizations).sortBy(function(characterization) {
            return [characterization.target.label, characterization.target.organism.name];
        });

        // Compile the document list
        var documentSpecs = [
            {documents: characterizations}
        ];

        // Build antibody status panel
        var PanelView = globals.panel_views.lookup(context);
        var antibodyStatuses = <PanelView context={context} key={context['@id']} />;

        // Make an array of targets with no falsy entries and no repeats
        var targets = {};
        if (context.lot_reviews && context.lot_reviews.length) {
            context.lot_reviews.forEach(function(lot_review) {
                lot_review.targets.forEach(function(target) {
                    targets[target['@id']] = target;
                });
            });
        }
        var targetKeys = Object.keys(targets);

        // Set up the breadcrumbs
        var organismComponents = [];
        var organismTerms = [];
        var organismTips = [];
        var geneComponents = [];
        var geneTerms = [];
        var geneTips = [];
        targetKeys.forEach(function(key, i) {
            var scientificName = targets[key].organism.scientific_name;
            var geneName = targets[key].gene_name;

            // Add to the information on organisms from the targets
            organismComponents.push(<span key={key}>{i > 0 ? <span> + <i>{scientificName}</i></span> : <i>{scientificName}</i>}</span>);
            organismTerms.push('targets.organism.scientific_name=' + scientificName);
            organismTips.push(scientificName);

            // Add to the information on gene names from the targets
            if (geneName && geneName !== 'unknown') {
                geneComponents.push(<span key={key}>{i > 0 ? <span> + {geneName}</span> : <span>{geneName}</span>}</span>);
                geneTerms.push('targets.gene_name=' + geneName);
                geneTips.push(geneName);
            }
        });

        var organismQuery = organismTerms.join('&');
        var geneQuery = geneTerms.join('&');
        var crumbs = [
            {id: 'Antibodies'},
            {id: organismComponents, query: organismQuery, tip: organismTips.join(' + ')},
            {id: geneComponents.length ? geneComponents : null, query: geneQuery, tip: geneTips.join(' + ')}
        ];

        // Make string of alternate accessions
        var altacc = context.alternate_accessions ? context.alternate_accessions.join(', ') : undefined;

        return (
            <div className={globals.itemClass(context, 'view-item')}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs root='/search/?type=antibody_lot' crumbs={crumbs} />
                        <h2>{context.accession}</h2>
                        {altacc ? <h4 className="repl-acc">Replaces {altacc}</h4> : null}
                        <h3>
                            {targetKeys.length ?
                                <span>Antibody against {Object.keys(targets).map(function(target, i) {
                                    var targetObj = targets[target];
                                    return <span key={i}>{i !== 0 ? ', ' : ''}<em>{targetObj.organism.scientific_name}</em>{' ' + targetObj.label}</span>;
                                })}</span>
                            :
                                <span>Antibody</span>
                            }
                        </h3>
                        <div className="status-line">
                            <div className="characterization-status-labels">
                                <StatusLabel title="Status" status={context.status} />
                            </div>
                            <AuditIndicators audits={context.audit} id="antibody-audit" />
                        </div>
                    </div>
                </header>
                <AuditDetail audits={context.audit} except={context['@id']} id="antibody-audit" />

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
                                        {targetKeys.map(function(target, i) {
                                            var targetObj = targets[target];
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
                                    <dd>{context.aliases.join(", ")}</dd>
                                </div>
                            : null}
                            
                            {context.dbxrefs && context.dbxrefs.length ?
                                <div data-test="dbxrefs">
                                    <dt>External resources</dt>
                                    <dd><DbxrefList values={context.dbxrefs} /></dd>
                                </div>
                            : null}

                        </dl>
                    </PanelBody>
                </Panel>

                <RelatedItems title={'Experiments using this antibody'}
                              url={'/search/?type=experiment&replicates.antibody.accession=' + context.accession}
                              Component={ExperimentTable} />

                <DocumentsPanel title="Characterizations" documentSpecs={documentSpecs} />
            </div>
        );
    }
});

globals.content_views.register(Lot, 'AntibodyLot');


var Documents = React.createClass({
    render: function() {
        return (
            <dd>
                {this.props.docs.map(function(doc, i) {
                    var attachmentHref = url.resolve(doc['@id'], doc.attachment.href);
                    var docName = (doc.aliases && doc.aliases.length) ? doc.aliases[0] :
                        ((doc.attachment && doc.attachment.download) ? doc.attachment.download : '');
                    return (
                        <div className="multi-dd dl-link" key={doc.uuid}>
                            <i className="icon icon-download"></i>&nbsp;
                            <a data-bypass="true" href={attachmentHref} download={doc.attachment.download}>
                                {docName}
                            </a>
                        </div>
                    );
                })}
            </dd>
        );
    }
});


var AntibodyStatus = module.exports.AntibodyStatus = React.createClass({
    render: function() {
        var context = this.props.context;

        // Sort the lot reviews by their status according to our predefined order
        // given in the statusOrder array.
        var lot_reviews = _.sortBy(context.lot_reviews, function(lot_review) {
            return _.indexOf(statusOrder, lot_review.status); // Use underscore indexOf so that this works in IE8
        });

        // Build antibody display object as a hierarchy: status=>organism=>biosample_term_name
        var statusTree = {};
        lot_reviews.forEach(function(lot_review) {
            // Status at top of hierarchy. If haven’t seen this status before, remember it
            if (!statusTree[lot_review.status]) {
                statusTree[lot_review.status] = {};
            }

            // Look at all organisms in current lot_review. They go under this lot_review's status
            var statusNode = statusTree[lot_review.status];
            lot_review.organisms.forEach(function(organism) {
                // If haven’t seen this organism with this status before, remember it
                if (!statusNode[organism.scientific_name]) {
                    statusNode[organism.scientific_name] = {};
                }

                // If haven't seen this biosample term name for this organism, remember it
                var organismNode = statusNode[organism.scientific_name];
                if (!organismNode[lot_review.biosample_term_name]) {
                    organismNode[lot_review.biosample_term_name] = true;
                }
            });
        });

        return (
            <section className="type-antibody-status view-detail panel">
                <div className="row">
                    <div className="col-xs-12">
                        {Object.keys(statusTree).map(function(status) {
                            var organisms = statusTree[status];
                            return (
                                <div key={status} className="row status-status-row">
                                    {Object.keys(organisms).map(function(organism, i) {
                                        var terms = Object.keys(organisms[organism]);
                                        return (
                                            <div key={i} className="row status-organism-row">
                                                <div className="col-sm-3 col-sm-push-9 status-status sentence-case">
                                                    {i === 0 ? <span><i className={globals.statusClass(status, 'indicator icon icon-circle')}></i>{status}</span> : ''}
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
    }
});

globals.panel_views.register(AntibodyStatus, 'AntibodyLot');


//**********************************************************************
// Antibody characterization documents

const EXCERPT_LENGTH = 80; // Maximum number of characters in an excerpt

// Document header component -- antibody characterization
var CharacterizationHeader = React.createClass({
    propTypes: {
        doc: React.PropTypes.object.isRequired // Document object to render
    },

    render: function() {
        var doc = this.props.doc;

        return (
            <div>
                <div className="document__header">
                    {doc.target.label} {doc.target.organism.scientific_name ? <span>{' ('}<i>{doc.target.organism.scientific_name}</i>{')'}</span> : ''}
                </div>
                {doc.characterization_reviews && doc.characterization_reviews.length ?
                    <div className="document__characterization-reviews">
                        {doc.characterization_reviews.map((review) => {
                            return <span key={review.biosample_term_name} className="document__characterization-biosample-term">{review.biosample_term_name}</span>;
                        })}
                    </div>
                : null}
            </div>
        );
    }
});

// Document caption component -- antibody characterization
var CharacterizationCaption = React.createClass({
    propTypes: {
        doc: React.PropTypes.object.isRequired // Document object to render
    },

    render: function() {
        var doc = this.props.doc;

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
    }
});

var CharacterizationFile = React.createClass({
    propTypes: {
        doc: React.PropTypes.object.isRequired, // Document object to render
        detailOpen: React.PropTypes.bool, // True if detail panel is visible
        detailSwitch: React.PropTypes.func // Parent component function to call when detail switch clicked
    },

    render: function() {
        var {doc, detailOpen, detailSwitch} = this.props;
        var excerpt, caption = doc.caption;
        if (caption && caption.length > EXCERPT_LENGTH) {
            excerpt = globals.truncateString(caption, 44);
        }

        return (
            <div className="document__file">
                <div className="document__characterization-badge"><StatusLabel status={doc.status} /></div>
                {detailSwitch ?
                    <a href="#" data-trigger onClick={detailSwitch} className="document__file-detail-switch">
                        {collapseIcon(!this.props.detailOpen)}
                    </a>
                : null}
            </div>
        );
    }
});

var CharacterizationDetail = React.createClass({
    propTypes: {
        doc: React.PropTypes.object.isRequired, // Document object to render
        detailOpen: React.PropTypes.bool, // True if detail panel is visible
        key: React.PropTypes.string // Unique key for identification
    },

    render: function() {
        var doc = this.props.doc;
        var keyClass = 'document__detail' + (this.props.detailOpen ? ' active' : '');
        var excerpt = doc.caption && doc.caption.length > EXCERPT_LENGTH;

        var download, attachmentHref;
        if (doc.attachment && doc.attachment.href && doc.attachment.download) {
            attachmentHref = url.resolve(doc['@id'], doc.attachment.href);
            download = (
                <dd className="dl-link">
                    <i className="icon icon-download"></i>&nbsp;
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
                <dl className='key-value-doc' id={'panel' + this.props.id} aria-labeledby={'tab' + this.props.id} role="tabpanel">
                    {excerpt ?
                        <div data-test="caption">
                            <dt>Caption</dt>
                            <dd className="sentence-case para-text">{doc.caption}</dd>
                        </div>
                    : null}

                    {doc.comment ?
                        <div data-test="comment">
                            <dt>Submitter comment</dt>
                            <dd className="para-text">{doc.comment}</dd>
                        </div>
                    : null}

                    {doc.notes ?
                        <div data-test="comment">
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
                            <Documents docs={doc.documents} />
                        </div>
                    : null}
                </dl>
            </div>
        );
    }
});

// Parts of individual document panels
globals.panel_views.register(Document, 'AntibodyCharacterization');
globals.document_views.header.register(CharacterizationHeader, 'AntibodyCharacterization');
globals.document_views.caption.register(CharacterizationCaption, 'AntibodyCharacterization');
globals.document_views.preview.register(DocumentPreview, 'AntibodyCharacterization');
globals.document_views.file.register(CharacterizationFile, 'AntibodyCharacterization');
globals.document_views.detail.register(CharacterizationDetail, 'AntibodyCharacterization');
