/** @jsx React.DOM */
'use strict';
var React = require('react');
var globals = require('./globals');
var dbxref = require('./dbxref');
var search = require('./search');
var StatusLabel = require('./statuslabel').StatusLabel;
var Citation = require('./publication').Citation;

var _ = require('underscore');

var DbxrefList = dbxref.DbxrefList;

var Panel = function (props) {
    // XXX not all panels have the same markup
    var context;
    if (props['@id']) {
        context = props;
        props = {context: context};
    }
    return globals.panel_views.lookup(props.context)(props);
};



var Pipeline = module.exports.Pipeline = React.createClass({
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-item');

        var documents = {};
        if (context.documents) {
            context.documents.forEach(function(doc, i) {
                documents[doc['@id']] = Panel({context: doc, key: i + 1});
            });
        }


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

                        <div data-test="assay">
                            <dt>Assay</dt>
                            <dd>{context.assay_term_name}</dd>
                        </div>
                    </dl>
                      {context.analysis_steps && context.analysis_steps.length ?
                          <div>
                              <h3>Steps</h3>
                              <div className="panel view-detail" data-test="supplementarydata">
                                  {context.analysis_steps.map(function(props, i) {
                                      return AnalysisStep (props, i) ;
                                  })}
                              </div>
                          </div>
                      : null}
                </div>
                     {Object.keys(documents).length ?
                     <div data-test="protocols">
                         <h3>Documents</h3>
                         <div className="row multi-columns-row">
                             {documents}
                         </div>
                     </div>
                      : null}
            </div>


        );
    }
});
globals.content_views.register(Pipeline, 'pipeline');


var Listing = React.createClass({
    mixins: [search.PickerActionsMixin],
    render: function() {
        var context = this.props.context;
        var result = this.props.context;
        return (<li>
                    <div>
                        {this.renderActions()}
                        <div className="pull-right search-meta">
                            <p className="type meta-title">Pipeline</p>
                            {context.status ? <p className="type meta-status">{' ' + context.status}</p> : ''}
                        </div>
                        <div className="accession">
                            <a href={result['@id']}>
                            	{result['title']}
                            </a>
                        </div>
                    </div>
            </li>
        );
    }
});
globals.listing_views.register(Listing, 'pipeline');


var PipelineTable = module.exports.PipelineTable = React.createClass({
    render: function() {
        var pipelines;

        // If there's a limit on entries to display and the array is greater than that
        // limit, then clone the array with just that specified number of elements
        if (this.props.limit && (this.props.limit < this.props.items.length)) {
            // Limit the pipelines list by cloning first {limit} elements
            pipelines = this.props.items.slice(0, this.props.limit);
        } else {
            // No limiting; just reference the original array
            pipelines = this.props.items;
        }

        return (
            <div className="table-responsive">
                <table className="table table-panel table-striped table-hover">
                    <thead>
                        <tr>
                            <th>Version</th>
                            <th>Assay</th>
                            <th>Pipeline</th>
                            <th>Download URL</th>
                            <th>Download checksum</th>
                        </tr>
                    </thead>
                    <tbody>
                    {pipelines.map(function (pipeline) {
                        // Ensure this can work with search result columns too
                        return (
                            <tr key={pipeline['@id']}>
                                <td>{pipeline['analysis_steps.software_versions.version'] || pipeline.analysis_steps.software_versions && pipeline.analysis_steps.software_versions.version}</td>
                                <td>{pipeline.assay_term_name}</td>
                                <td><a href={pipeline['@id']}>{pipeline.accession}</a></td>
                                <td>{pipeline['analysis_steps.software_versions.downloaded_url'] || pipeline.analysis_steps.software_versions && pipeline.analysis_steps.software_versions.downloaded_url}</td>
                                <td>{pipeline['analysis_steps.software_versions.download_checksum'] || pipeline.analysis_steps.software_versions && pipeline.analysis_steps.software_versions.download_checksum}</td>
                            </tr>
                        );
                    })}
                    </tbody>
                    <tfoot>
                        <tr>
                            <td colSpan="6">
                                {this.props.limit && (this.props.limit < this.props.total) ?
                                    <div>
                                        {'Displaying '}{this.props.limit}{' pipelines out of '}{this.props.total}{' total related pipelines'}
                                    </div>
                                : ''}
                            </td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        );
    }
});