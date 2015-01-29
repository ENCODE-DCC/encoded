/** @jsx React.DOM */
'use strict';
var React = require('react');
var globals = require('./globals');
var dbxref = require('./dbxref');
var search = require('./search');
var pipeline = require('./pipeline');
var fetched = require('./fetched');
var StatusLabel = require('./statuslabel').StatusLabel;
var Citation = require('./publication').Citation;
var _ = require('underscore');

var DbxrefList = dbxref.DbxrefList;
var PipelineTable = pipeline.PipelineTable;
var FetchedItems = fetched.FetchedItems;

// Count the total number of references in all the publications passed
// in the pubs array parameter.
function refCount(pubs) {
    var total = 0;
    if (pubs) {
        pubs.forEach(function(pub) {
            total += pub.references ? pub.references.length : 0;
        });
    }
    return total;
}


// Display all references in the array of publications in the 'pubs' property.
var References = React.createClass({
    render: function() {
        return (
            <div>
                {this.props.pubs ?
                    <div>
                        {this.props.pubs.map(function(pub) {
                            return (
                                <div className="multi-dd">
                                    <div>
                                        {pub.authors ? pub.authors + '. ' : ''}
                                        {pub.title + ' '}
                                        <Citation context={pub} />
                                    </div>
                                    {pub.references && pub.references.length ? <DbxrefList values={pub.references} className="multi-value" /> : ''}
                                </div>
                            );
                        })}
                    </div>
                : null}
            </div>
        );
    }
});


// Display all PMID/PMCID references in the array of publications in the 'pubs' property.
var PubReferences = React.createClass({
    render: function() {
        // Collect all publications' references into one array
        // and remove duplicates
        var allRefs = [];
        this.props.pubs.forEach(function(pub) {
            allRefs = allRefs.concat(pub.references);
        });
        allRefs = _.uniq(allRefs);

        if (allRefs) {
            return <DbxrefList values={allRefs} className={this.props.listClass} />;
        } else {
            return <span></span>;
        }
    }
});


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
                                <dd><References pubs={context.references} /></dd>
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
                {this.transferPropsTo(
                    <PipelineTable />
                )}
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
                    <td><a href={version.downloaded_url}>{version.version}</a></td>
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
