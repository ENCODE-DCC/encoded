'use strict';
var React = require('react');
var globals = require('./globals');
var dbxref = require('./dbxref');
var search = require('./search');
var pipeline = require('./pipeline');
var fetched = require('./fetched');
var reference = require('./reference');
var StatusLabel = require('./statuslabel').StatusLabel;
var _ = require('underscore');

var DbxrefList = dbxref.DbxrefList;
var PipelineTable = pipeline.PipelineTable;
var FetchedItems = fetched.FetchedItems;
var PubReferences = reference.PubReferences;


var Software = module.exports.Software = React.createClass({
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-item');

        var pipeline_url = '/search/?type=pipeline&analysis_steps.software_versions.software.uuid=' + context.uuid;

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <h2>{context.title}</h2>
                        <div className="characterization-status-labels">
                            <StatusLabel title="Status" status={context.status} />
                        </div>
                    </div>
                </header>

                <div className="panel data-display">
                    <dl className="key-value">
                        <div data-test="title">
                            <dt>Title</dt>
                            {context.source_url ?
                                <dd><a href={context.source_url}>{context.title}</a></dd> :
                                <dd>{context.title}</dd>
                            }
                        </div>

                        <div data-test="description">
                            <dt>Description</dt>
                            <dd>{context.description}</dd>
                        </div>

                        {context.software_type && context.software_type.length ?
                            <div data-test="type">
                                <dt>Software type</dt>
                                <dd>{context.software_type.join(", ")}</dd>
                            </div>
                        : null}

                        {context.purpose && context.purpose.length ?
                            <div data-test="purpose">
                                <dt>Used for</dt>
                                <dd>{context.purpose.join(", ")}</dd>
                            </div>
                        : null}

                        {context.references && context.references.length ?
                            <div data-test="references">
                                <dt>References</dt>
                                <dd><PubReferences pubs={context.references} /></dd>
                            </div>
                        : null}
                    </dl>
                </div>

                {context.versions && context.versions.length ?
                    <div>
                        <h3>Software Versions</h3>
                        <SoftwareVersionTable items={context.versions} />
                    </div>
                : null }
            </div>
        );
    }
});
globals.content_views.register(Software, 'software');

// Commenting out until pipelines are used.

var PipelinesUsingSoftwareVersion = module.exports.PipelinesUsingSoftwareVersion = React.createClass({
    render: function () {
        var context = this.props.context;
        return (
            <div>
                <h3>Pipelines using software {context.title}</h3>
                <PipelineTable {...this.props} />
            </div>
        );
    }
});


var SoftwareVersionTable = module.exports.SoftwareVersionTable = React.createClass({
    render: function() {
        var rows = {};
        this.props.items.forEach(function (version) {
            rows[version['@id']] = (
                <tr>
                    <td>
                        {version.downloaded_url ?
                            <a href={version.downloaded_url}>{version.version}</a>
                        :
                            <span>{version.version}</span>
                        }
                    </td>
                    <td>{version.download_checksum}</td>
                </tr>
            );
        });
        return (
            <div className="table-responsive">
                <table className="table table-panel table-striped table-hover">
                    <thead>
                        <tr>
                            <th>Version</th>
                            <th>Download checksum</th>
                        </tr>
                    </thead>
                    <tbody>
                    {rows}
                    </tbody>
                    <tfoot>
                    </tfoot>
                </table>
            </div>
        );
    }
});


var Listing = React.createClass({
    mixins: [search.PickerActionsMixin],
    render: function() {
        var context = this.props.context;
        return (<li>
                    <div>
                        {this.renderActions()}
                        <div className="pull-right search-meta">
                            <p className="type meta-title">Software</p>
                            {context.status ? <p className="type meta-status">{' ' + context.status}</p> : ''}
                        </div>
                        <div className="accession">
                            <a href={context['@id']}>{context.title}</a>
                            {context.source_url ? <span className="accession-note"> &mdash; <a href={context.source_url}>source</a></span> : ''}
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

                        {refCount(context.references) ?
                            <div>
                                <strong>Publication: </strong>
                                <PubReferences pubs={context.references} listClass="list-reference" />
                            </div>
                        : null}
                    </div>
            </li>
        );
    }
});
globals.listing_views.register(Listing, 'software');
