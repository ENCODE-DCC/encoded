/** @jsx React.DOM */
'use strict';
var React = require('react');
var globals = require('./globals');
var dbxref = require('./dbxref');
var search = require('./search');
var antibody = require('./antibody');

var DbxrefList = dbxref.DbxrefList;
var Dbxref = dbxref.Dbxref;
var StatusLabel = antibody.StatusLabel;


var Software = module.exports.Software = React.createClass({
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-item');
        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <div>
                            <h2>{context.title}</h2>
                        </div>
                        <div className="characterization-status-labels">
                            <StatusLabel title="Status" status={context.status} />
                        </div>
                    </div>
                </header>

                <div className="panel data-display">
                    <dl className="key-value">
                        <dt>Title</dt>
                        {context.source_url ?
                            <dd><a href={context.source_url}>{context.title}</a></dd> :
                            <dd>{context.title}</dd>
                        }

                        <dt>Description</dt>
                        <dd>{context.description}</dd>

                        {context.software_type && context.software_type.length ?
                            <div>
                                <dt>Software Type</dt>
                                <dd>{context.software_type.join(", ")}</dd>
                            </div>
                        : null}

                        {context.purpose && context.purpose.length ?
                            <div>
                                <dt>Used for</dt>
                                <dd>{context.purpose.join(", ")}</dd>
                            </div>
                        : null}
                    </dl>
                </div>
            </div>
        );
    }
});

globals.content_views.register(Software, 'software');


var Listing = React.createClass({
    mixins: [search.PickerActionsMixin],
    render: function() {
        var context = this.props.context;
        return (<li>
                    <div>
                        {this.renderActions()}
                        <div className="pull-right search-meta">
                            <p className="type meta-title">Software</p>
                            <p className="type meta-status">{' ' + context.status}</p>
                        </div>
                        <div className="accession">
                            <a href={context['@id']}>{context.title}</a>
                            <span className="accession-note"> <a href={context.source_url}>source</a></span>
                        </div>
                    </div>
                    <div className="data-row">
                        <div>{context.description}</div>

                        {context.software_type && context.software_type.length ?
                            <div>
                                <strong>Software type: </strong>
                                {context.software_type.join(", ")}
                            </div>
                        : null}
                        {context.purpose && context.purpose.length ?
                            <div>
                                <strong>Used for: </strong>
                                {context.purpose.join(", ")}
                            </div>
                        : null}
                        {context.publication && context.publication.length ? <DbxrefList values={context.publication} className="list-reference" /> : '' }
                    </div>
            </li>
        );
    }
});
globals.listing_views.register(Listing, 'software');
