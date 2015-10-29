'use strict';
var React = require('react');
var globals = require('./globals');
var search = require('./search');
var pipeline = require('./pipeline');
var fetched = require('./fetched');
var reference = require('./reference');
var StatusLabel = require('./statuslabel').StatusLabel;
var audit = require('./audit');
var _ = require('underscore');
var url = require('url');

var PipelineTable = pipeline.PipelineTable;
var FetchedItems = fetched.FetchedItems;
var PubReferenceList = reference.PubReferenceList;
var AuditIndicators = audit.AuditIndicators;
var AuditDetail = audit.AuditDetail;
var AuditMixin = audit.AuditMixin;


var Software = module.exports.Software = React.createClass({
    mixins: [AuditMixin],

    contextTypes: {
        location_href: React.PropTypes.string
    },

    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-item');

        var pipeline_url = '/search/?type=pipeline&analysis_steps.software_versions.software.uuid=' + context.uuid;

        // See if there’s a version number to highlight
        var highlightVersion;
        var queryParsed = this.context.location_href && url.parse(this.context.location_href, true).query;
        if (queryParsed && Object.keys(queryParsed).length) {
            // Find the first 'version' query string item, if any
            var versionKey = _(Object.keys(queryParsed)).find(function(key) {
                return key === 'version';
            });
            if (versionKey) {
                highlightVersion = queryParsed[versionKey];
                if (typeof highlightVersion === 'object') {
                    highlightVersion = highlightVersion[0];
                }
            }
        }

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <h2>{context.title}</h2>
                        <div className="characterization-status-labels">
                            <StatusLabel title="Status" status={context.status} />
                        </div>
                        <AuditIndicators audits={context.audit} id="publication-audit" />
                    </div>
                </header>
                <AuditDetail context={context} id="publication-audit" />

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
                                <dt>Publications</dt>
                                <dd>
                                    <PubReferenceList values={context.references} />
                                </dd>
                            </div>
                        : null}
                    </dl>
                </div>

                {context.versions && context.versions.length ?
                    <div>
                        <h3>Software Versions</h3>
                        <SoftwareVersionTable items={context.versions} highlightVersion={highlightVersion} />
                    </div>
                : null }
            </div>
        );
    }
});
globals.content_views.register(Software, 'Software');

// Commenting out until pipelines are used.

var PipelinesUsingSoftwareVersion = module.exports.PipelinesUsingSoftwareVersion = React.createClass({
    render: function () {
        var context = this.props.context;
        return (
            <div>
                <h3>Pipelines using software {context.title}</h3>
                <PipelineTable {...this.props} softwareId={context['@id']}/>
            </div>
        );
    }
});


var SoftwareVersionTable = module.exports.SoftwareVersionTable = React.createClass({
    render: function() {
        var props = this.props;
        var rows = {};
        props.items.forEach(function (version) {
            rows[version['@id']] = (
                <tr className={props.highlightVersion === version.version ? 'highlight-row' : null}>
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
    mixins: [search.PickerActionsMixin, AuditMixin],
    render: function() {
        var result = this.props.context;
        return (
            <li>
                <div className="clearfix">
                    {this.renderActions()}
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Software</p>
                        {result.status ? <p className="type meta-status">{' ' + result.status}</p> : ''}
                        <AuditIndicators audits={result.audit} id={result['@id']} search />
                    </div>
                    <div className="accession">
                        <a href={result['@id']}>{result.title}</a>
                        {result.source_url ? <span className="accession-note"> &mdash; <a href={result.source_url}>source</a></span> : ''}
                    </div>
                    <div className="data-row">
                        <div>{result.description}</div>
                        {result.software_type && result.software_type.length ?
                            <div>
                                <strong>Software type: </strong>
                                {result.software_type.join(", ")}
                            </div>
                        : null}

                    </div>
                </div>
                <AuditDetail context={result} id={result['@id']} forcedEditLink />
            </li>
        );
    }
});
globals.listing_views.register(Listing, 'Software');


// Display a list of software versions from the given software_version list. This is meant to be displayed
// in a panel.
var SoftwareVersionList = module.exports.SoftwareVersionList = function(softwareVersions) {
    return (
        <div>
            {softwareVersions.map(function(version, i) {
                var versionNum = version.version === 'unknown' ? 'version unknown' : version.version;
                return (
                    <a href={version.software['@id'] + '?version=' + version.version} key={i} className="software-version">
                        <span className="software">{version.software.name}</span>
                        {version.version ?
                            <span className="version">{versionNum}</span>
                        : null}
                    </a>
                );
            })}
        </div>
    );
};
