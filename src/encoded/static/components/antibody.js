/** @jsx React.DOM */
'use strict';
var React = require('react');
var url = require('url');
var _ = require('underscore');
var globals = require('./globals');
var dataset = require('./dataset');
var fetched = require('./fetched');
var dbxref = require('./dbxref');
var image = require('./image');
var statuslabel = require('./statuslabel');

var Attachment = image.Attachment;
var DbxrefList = dbxref.DbxrefList;
var FetchedItems = fetched.FetchedItems;
var ExperimentTable = dataset.ExperimentTable;
var StatusLabel = statuslabel.StatusLabel;


var Lot = module.exports.Lot = React.createClass({
    render: function() {
        var context = this.props.context;

        // Sort characterization arrays, first by species, then by primary/secondary characterization method
        var organismOrder = ['human', 'mouse', 'dmelanogaster', 'celegans'];
        var sortedChars = _(context.characterizations).sortBy(function(characterization) {
            return [_(organismOrder).indexOf(characterization.target.organism), characterization.primary_characterization_method ? 0 : 1];
        });

        // Build array of characterization panels
        var characterizations = sortedChars.map(function(item) {
            return globals.panel_views.lookup(item)({context: item, key: item['@id']});
        });

        // Build antibody status panel
        var antibodyStatuses = globals.panel_views.lookup(context)({context: context, key: context['@id']});

        // Make an array of targets with no falsy entries and no repeats
        var targets = {};
        if (context.characterizations) {
            context.characterizations.forEach(function(characterization) {
                targets[characterization.target['@id']] = characterization.target;
            });
        }
        var targetKeys = Object.keys(targets);

        // Make string of alternate accessions
        var altacc = context.alternate_accessions ? context.alternate_accessions.join(', ') : undefined;

        // To search list of linked experiments
        var experiments_url = '/search/?type=experiment&replicates.antibody.accession=' + context.accession;

        return (
            <div className={globals.itemClass(context, 'view-item')}>
                <header className="row">
                    <div className="col-sm-12">
                        <h2>{context.accession}</h2>
                        {altacc ? <h4 className="repl-acc">Replaces {altacc}</h4> : null}
                        <h3>
                            {targetKeys.length ?
                                <span>Antibody against {Object.keys(targets).map(function(target, i) {
                                    var targetObj = targets[target];
                                    return <span>{i !== 0 ? ', ' : ''}{targetObj.label}{' ('}<em>{targetObj.organism.scientific_name}</em>{')'}</span>;
                                })}</span>
                            :
                                <span>Antibody</span>
                            }
                        </h3>
                    </div>
                </header>

                {characterizations.length ?
                    <div className="antibody-statuses">
                        {antibodyStatuses}
                    </div>
                :
                    <div className="characterization-status-labels">
                        <StatusLabel status="Awaiting lab characterization" />
                    </div>
                }

                <div className="panel data-display">
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
                                        return <span>{i !== 0 ? ', ' : ''}<a href={target}>{targetObj.label}{' ('}<em>{targetObj.organism.scientific_name}</em>{')'}</a></span>;
                                    })}
                                </dd>
                            </div>
                        : null}

                        {context.lot_id_alias.length ?
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

                        {context.purifications.length ?
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
                                <dd>{context.antigen_sequence}</dd>
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
                </div>

                <div className="characterizations">
                    {characterizations}
                </div>

                {this.transferPropsTo(
                    <FetchedItems url={experiments_url} Component={ExperimentsUsingAntibody} />
                )}
            </div>
        );
    }
});

globals.content_views.register(Lot, 'antibody_lot');


var ExperimentsUsingAntibody = React.createClass({
    render: function () {
        var context = this.props.context;
        return (
            <div>
                <h3>Experiments using antibody {context.accession}</h3>
                {this.transferPropsTo(
                    <ExperimentTable />
                )}
            </div>
        );
    }
});


var StandardsDocuments = React.createClass({
    render: function() {
        return (
            <div>
                {this.props.docs.map(function(doc) {
                    return (<div className="multi-dd"><a href={doc['@id']}>{doc.aliases[0]}</a></div>);
                })}
            </div>
        );
    }
});


var Characterization = module.exports.Characterization = React.createClass({
    render: function() {
        var context = this.props.context;
        var figure = <Attachment context={this.props.context} className="characterization" />;

        var attachmentHref, download;
        if (context.attachment) {
            attachmentHref = url.resolve(context['@id'], context.attachment.href);
            download = (
                <a data-bypass="true" href={attachmentHref} download={context.attachment.download}>
                    {context.attachment.download}
                </a>
            );
        } else {
            download = (
                <em>Document not available</em>
            );
        }

        // Compile a list of attached standards documents
        var standardsDocuments = context.documents.filter(function(doc) {
            return (context.status === 'compliant' || context.status === 'not compliant') && doc.document_type === "standards document";
        });

        return (
            <section className={globals.itemClass(context, 'view-detail panel')}>
                <div className="row">
                    <div className="col-sm-4 col-md-6">
                        <figure>
                            {figure}
                            <figcaption>
                                <span>{context.status}</span>
                            </figcaption>
                        </figure>
                    </div>
                    <div className="col-sm-8 col-md-6">
                        <dl className="characterization-meta-data key-value">
                            {context.characterization_method ?
                                <div data-test="method">
                                    <dt className="h3">Method</dt>
                                    <dd className="h3">{context.characterization_method} ({context.primary_characterization_method ? 'primary' : 'secondary'})</dd>
                                </div>
                            : null}

                            <div data-test="targetspecies">
                                <dt className="h4">Target species</dt>
                                <dd className="h4 sentence-case"><em>{context.target.organism.scientific_name}</em></dd>
                            </div>

                            {context.caption ?
                                <div data-test="caption">
                                    <dt>Caption</dt>
                                    <dd className="sentence-case">{context.caption}</dd>
                                </div>
                            : null}

                            {context.submitted_by && context.submitted_by.title ?
                                <div data-test="submitted">
                                    <dt>Submitted by</dt>
                                    <dd>{context.submitted_by.title}</dd>
                                </div>
                            : null}

                            <div data-test="lab">
                                <dt>Lab</dt>
                                <dd>{context.lab.title}</dd>
                            </div>

                            <div data-test="grant">
                                <dt>Grant</dt>
                                <dd>{context.award.name}</dd>
                            </div>

                            <div data-test="image">
                                <dt>Image</dt>
                                <dd><StatusLabel status={context.status} /></dd>
                            </div>

                            {standardsDocuments.length ?
                                <div data-test="standardsdoc">
                                    <dt>Standards documents</dt>
                                    <dd><StandardsDocuments docs={standardsDocuments} /></dd>
                                </div>
                            : null}

                            <div data-test="download">
                                <dt><i className="icon icon-download"></i> Download</dt>
                                <dd>{download}</dd>
                            </div>
                        </dl>
                    </div>
                </div>
            </section>
        );
    }
});

globals.panel_views.register(Characterization, 'antibody_characterization');


var AntibodyStatus = module.exports.AntibodyStatus = React.createClass({
    render: function() {
        var context = this.props.context;

        // Build antibody display object as a hierarchy: status=>organism=>biosample_term_name
        var statusTree = {};
        var organismCount = 0;
        context.lot_reviews.forEach(function(lot_review) {
            // Status at top of hierarchy. If haven’t seen this status before, remember it
            if (!statusTree[lot_review.status]) {
                statusTree[lot_review.status] = {};
            }

            // Look at all organisms in current lot_review. They go under this lot_review's status
            var statusNode = statusTree[lot_review.status];
            lot_review.organisms.forEach(function(organism) {
                // If haven’t seen this organism with this status before, remember it
                if (!statusNode[organism]) {
                    statusNode[organism] = {};
                    organismCount++;
                }

                // If haven't seen this biosample term name for this organism, remember it
                var organismNode = statusNode[organism];
                if (!organismNode[lot_review.biosample_term_name]) {
                    organismNode[lot_review.biosample_term_name] = {};
                }
            });
        });

        // Now have hierarchical object. If no organisms in it, then nothing to display
        if (!organismCount) {
            return null;
        }

        return (
            <section className="type-antibody-status view-detail panel">
                <div className="row">
                    <div className="col-xs-12">
                        {Object.keys(statusTree).map(function(status) {
                            var organisms = statusTree[status];
                            return (
                                <div className="row status-status-row">
                                    {Object.keys(organisms).map(function(organism, i) {
                                        var terms = Object.keys(organisms[organism]);
                                        return (
                                            <div className="row status-organism-row">
                                                <div className="col-sm-3 col-sm-push-9 status-status sentence-case">{i === 0 ? <span><i className={globals.statusClass(status, 'indicator icon icon-circle')}></i>{status}</span> : ''}</div>
                                                <div className="col-sm-2 col-sm-pull-3 status-organism">
                                                    {organism}
                                                </div>
                                                <div className="col-sm-7 col-sm-pull-3 status-terms">
                                                    {terms.join(', ')}
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

globals.panel_views.register(AntibodyStatus, 'antibody_lot');
