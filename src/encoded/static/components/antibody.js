/** @jsx React.DOM */
'use strict';
var React = require('react');
var cx = require('react/lib/cx');
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
        var sortedChars = _(context.characterizations).sortBy(function(characterization) {
            return [characterization.target.label, characterization.target.organism.name];
        });

        // Build array of characterization panels
        var characterizations = sortedChars.map(function(item) {
            return globals.panel_views.lookup(item)({context: item, key: item['@id']});
        });

        // Build antibody status panel
        var antibodyStatuses = globals.panel_views.lookup(context)({context: context, key: context['@id']});

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

                {context.lot_reviews && context.lot_reviews.length ?
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

                <div className="characterizations row multi-columns-row">
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
                <span className="pull-right">
                    <a className="btn btn-info btn-sm" href={this.props.url}>View all</a>
                </span>

                <div>
                    <h3>Experiments using antibody {context.accession}</h3>
                    {this.transferPropsTo(
                        <ExperimentTable limit={5} />
                    )}
                </div>
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
    getInitialState: function() {
        return {panelOpen: false, panelFixed: false};
    },

    // Clicking the Lab bar inverts visible state of the popover
    handleClick: function(e) {
        e.preventDefault();
        e.stopPropagation();

        // Tell parent (App component) about new popover state
        // Pass it this component's React unique node ID
        this.setState({panelOpen: !this.state.panelOpen});
    },

    componentDidMount: function() {
        if (this.refs.collapse.getDOMNode().scrollHeight <= this.refs.collapse.getDOMNode().clientHeight) {
            this.setState({panelFixed: true});
        }
    },

    render: function() {
        var context = this.props.context;
        var keyClass = cx({
            "characterization-meta-data": true,
            "key-value-left": true,
            "characterization-slider": true,
            "active": this.state.panelOpen && !this.state.panelFixed
        });
        var tabTriggerClass = cx({
            "trigger-tab": true,
            "text-hide": true,
            "active": this.state.panelOpen && !this.state.panelFixed,
            "disabled": this.state.panelFixed
        });
        var kvTriggerClass = cx({
            "key-value-trigger": true,
            "disabled": this.state.panelFixed
        });
        var figure = <Attachment context={this.props.context} className="characterization" />;

        var attachmentHref, download;
        if (context.attachment) {
            attachmentHref = url.resolve(context['@id'], context.attachment.href);
            download = (
                <div className="dl-link">
                    <i className="icon icon-download"></i>&nbsp;<a data-bypass="true" href={attachmentHref} download={context.attachment.download}>
                        {context.attachment.download}
                    </a>
                </div>
            );
        } else {
            download = (
                <em>Document not available</em>
            );
        }

        // Compile a list of attached standards documents
        var standardsDocuments = context.documents.filter(function(doc) {
            return doc.document_type === "standards document";
        });

        return (
            // Each section is a panel; name all Bootstrap 3 sizes so .multi-columns-row class works
            <section className="col-xs-12 col-sm-6 col-md-6 col-lg-6">
                <div className={globals.itemClass(context, 'view-detail panel')}>
                    <div className="characterization-target">
                        {context.target.label} {context.target.organism.scientific_name ? <span>{' ('}<i>{context.target.organism.scientific_name}</i>{')'}</span> : ''}
                    </div>
                    <div className="characterization-header">
                        <figure>
                            {figure}
                            <div className="characterization-badge"><StatusLabel status={context.status} /></div>
                        </figure>
                        <dl className="characterization-intro characterization-meta-data key-value-left">
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

                            <dt>Image</dt>
                            {download}
                        </dl>
                    </div>
                    <dl ref="collapse" className={keyClass}>
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
                    </dl>
                    <dl className={kvTriggerClass}>
                        <a href="#" onClick={this.handleClick}>
                            <dt>Lab</dt>
                            <dd>{context.lab.title}</dd>
                        </a>
                        <a className={tabTriggerClass} href="#" onClick={this.handleClick}>
                            Toggle panel disclosure
                        </a>
                    </dl>
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
            if (lot_review.organisms && lot_review.organisms.length) {
                lot_review.organisms.forEach(function(organism) {
                    // If haven’t seen this organism with this status before, remember it
                    if (!statusNode[organism.scientific_name]) {
                        statusNode[organism.scientific_name] = {};
                        organismCount++;
                    }

                    // If haven't seen this biosample term name for this organism, remember it
                    var organismNode = statusNode[organism.scientific_name];
                    if (!organismNode[lot_review.biosample_term_name]) {
                        organismNode[lot_review.biosample_term_name] = true;
                    }
                });
            } else {
                if (!statusNode[lot_review.biosample_term_name]) {
                    statusNode[lot_review.biosample_term_name] = true;
                }
            }
        });

        return (
            <section className="type-antibody-status view-detail panel">
                <div className="row">
                    <div className="col-xs-12">
                        {Object.keys(statusTree).map(function(status) {
                            if (organismCount) {
                                var organisms = statusTree[status];
                                return (
                                    <div className="row status-status-row">
                                        {Object.keys(organisms).map(function(organism, i) {
                                            var terms = Object.keys(organisms[organism]);
                                            return (
                                                <div className="row status-organism-row">
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
                            } else {
                                var terms = Object.keys(statusTree[status]);
                                return (
                                    <div className="row status-status-row">
                                        <div className="row status-organism-row">
                                            <div className="col-sm-3 col-sm-push-9 status-status sentence-case">
                                                <span>
                                                    <i className={globals.statusClass(status, 'indicator icon icon-circle')}></i>
                                                    {status}
                                                </span>
                                            </div>
                                            <div className="col-sm-2 col-sm-pull-3 status-organism">&nbsp;</div>
                                            <div className="col-sm-7 col-sm-pull-3 status-terms">
                                                {terms.join(', ')}
                                            </div>
                                        </div>
                                    </div>
                                );
                            }
                        })}
                    </div>
                </div>
            </section>
        );
    }
});

globals.panel_views.register(AntibodyStatus, 'antibody_lot');
