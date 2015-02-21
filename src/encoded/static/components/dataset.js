/** @jsx React.DOM */
'use strict';
var React = require('react');
var _ = require('underscore');
var cx = require('react/lib/cx');
var moment = require('moment');
var globals = require('./globals');
var dbxref = require('./dbxref');
var fetched = require('./fetched');
var statuslabel = require('./statuslabel');
var graph = require('./graph');

var DbxrefList = dbxref.DbxrefList;
var Dbxref = dbxref.Dbxref;
var FetchedItems = fetched.FetchedItems;
var StatusLabel = statuslabel.StatusLabel;

var Panel = function (props) {
    // XXX not all panels have the same markup
    var context;
    if (props['@id']) {
        context = props;
        props = {context: context};
    }
    return globals.panel_views.lookup(props.context)(props);
};

var Dataset = module.exports.Dataset = React.createClass({
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-item');
        var experiments = {};
        context.files.forEach(function (file) {
            var experiment = file.replicate && file.replicate.experiment;
            if (experiment) {
                experiments[experiment['@id']] = experiment;
            }
        });
        experiments = _.values(experiments);

        // Build up array of documents attached to this dataset
        var datasetDocuments = {};
        context.documents.forEach(function (document, i) {
            datasetDocuments[document['@id']] = Panel({context: document, key: i});
        }, this);

        // Make string of alternate accessions
        var altacc = context.alternate_accessions.join(', ');

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <h2>Dataset {context.accession}</h2>
                        {altacc ? <h4 className="repl-acc">Replaces {altacc}</h4> : null}
                    </div>
                </header>
                <div className="panel data-display">
                    <dl className="key-value">
                        <dt>Accession</dt>
                        <dd>{context.accession}</dd>

                        {context.description ? <dt>Description</dt> : null}
                        {context.description ? <dd>{context.description}</dd> : null}

                        {context.dataset_type ? <dt>Dataset type</dt> : null}
                        {context.dataset_type ? <dd className="sentence-case">{context.dataset_type}</dd> : null}
                        
                        {context.lab ? <dt>Lab</dt> : null}
                        {context.lab ? <dd>{context.lab.title}</dd> : null}
                        
                        {context.aliases.length ? <dt>Aliases</dt> : null}
                        {context.aliases.length ? <dd>
                            <DbxrefList values={context.aliases} />
                         </dd> : null}
                        
                        <dt>External resources</dt>
                        <dd>
                            {context.dbxrefs.length ?
                                <DbxrefList values={context.dbxrefs} />
                            : <em>None submitted</em> }
                        </dd>

                        {context.references.length ? <dt>References</dt> : null}
                        {context.references.length ? <dd><DbxrefList values={context.references} className="horizontal-list"/></dd> : null}
                    </dl>
                </div>

                {Object.keys(datasetDocuments).length ?
                    <div>
                        <h3>Dataset documents</h3>
                        <div className="row">
                            {datasetDocuments}
                        </div>
                    </div>
                : null}

                {experiments.length ?
                    <div>
                        <h3>Related experiments for dataset {context.accession}</h3>
                        <ExperimentTable items={experiments} />
                    </div>
                : null }

                {context.files.length ?
                    <div>
                        <h3>Files for dataset {context.accession}</h3>
                        <FileTable items={context.files} />
                    </div>
                : null }

                {{'released': 1, 'release ready': 1}[context.status] ? this.transferPropsTo(
                    <FetchedItems url={unreleased_files_url(context)} Component={UnreleasedFiles} />
                ): null}

            </div>
        );
    }
});

globals.content_views.register(Dataset, 'dataset');


var unreleased_files_url = module.exports.unreleased_files_url = function (context) {
    var file_states = [
        '',
        "uploading",
        "uploaded",
        "upload failed",
        "format check failed",
        "in progress"
    ].map(encodeURIComponent).join('&status=');
    return '/search/?limit=all&frame=embedded&type=file&dataset=' + context['@id'] + file_states;
};

var UnreleasedFiles = module.exports.UnreleasedFiles = React.createClass({
    render: function () {
        var context = this.props.context;
        return (
            <div>
                <h3>Unreleased files linked to {context.accession}</h3>
                {this.transferPropsTo(
                    <FileTable />
                )}
            </div>
        );
    }
});


var ExperimentTable = module.exports.ExperimentTable = React.createClass({
    render: function() {
        var experiments;

        // If there's a limit on entries to display and the array is greater than that
        // limit, then clone the array with just that specified number of elements
        if (this.props.limit && (this.props.limit < this.props.items.length)) {
            // Limit the experiment list by cloning first {limit} elements
            experiments = this.props.items.slice(0, this.props.limit);
        } else {
            // No limiting; just reference the original array
            experiments = this.props.items;
        }

        return (
            <div className="table-responsive">
                <table className="table table-panel table-striped table-hover">
                    <thead>
                        <tr>
                            <th>Accession</th>
                            <th>Assay</th>
                            <th>Biosample term name</th>
                            <th>Target</th>
                            <th>Description</th>
                            <th>Lab</th>
                        </tr>
                    </thead>
                    <tbody>
                    {experiments.map(function (experiment) {
                        // Ensure this can work with search result columns too
                        return (
                            <tr key={experiment['@id']}>
                                <td><a href={experiment['@id']}>{experiment.accession}</a></td>
                                <td>{experiment.assay_term_name}</td>
                                <td>{experiment.biosample_term_name}</td>
                                <td>{experiment['target.label'] || experiment.target && experiment.target.label}</td>
                                <td>{experiment.description}</td>
                                <td>{experiment['lab.title'] || experiment.lab && experiment.lab.title}</td>
                            </tr>
                        );
                    })}
                    </tbody>
                    <tfoot>
                        <tr>
                            <td colSpan="6">
                                {this.props.limit && (this.props.limit < this.props.total) ?
                                    <div>
                                        {'Displaying '}{this.props.limit}{' experiments out of '}{this.props.total}{' total related experiments'}
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

function humanFileSize(size) {
    if (size === undefined) return undefined;
    var i = Math.floor( Math.log(size) / Math.log(1024) );
    return ( size / Math.pow(1024, i) ).toPrecision(3) * 1 + ' ' + ['B', 'kB', 'MB', 'GB', 'TB'][i];
}

var FileTable = module.exports.FileTable = React.createClass({
    getInitialState: function() {
        return {col: '', reversed: false};
    },

    sortDir: function(col) {
        var reversed = col === this.state.col ? !this.state.reversed : false;
        this.setState({col: col, reversed: reversed});
    },

    sortCol: function(a, b) {
        var diff;

        switch (this.state.col) {
            case 'accession':
                diff = a.accession > b.accession ? 1 : -1;
                break;
            case 'file_format':
                diff = a.file_format > b.file_format ? 1 : (a.file_format === b.file_format ? 0 : -1);
                break;
            case 'output_type':
                var aLower = a.output_type.toLowerCase();
                var bLower = b.output_type.toLowerCase();
                diff = aLower > bLower ? 1 : (aLower === bLower ? 0 : -1);
                break;
            case 'paired_end':
                if (a.paired_end && b.paired_end) {
                    diff = a.paired_end - b.paired_end;
                } else {
                    diff = a.paired_end ? -1 : (b.paired_end ? 1 : 0);
                }
                break;
            case 'bio_replicate':
                if (a.replicate && b.replicate) {
                    diff = a.replicate.biological_replicate_number - b.replicate.biological_replicate_number;
                } else {
                    diff = a.replicate ? -1 : (b.replicate ? 1 : 0);
                }
                break;
            case 'tech_replicate':
                if (a.replicate && b.replicate) {
                    diff = a.replicate.technical_replicate_number - b.replicate.technical_replicate_number;
                } else {
                    diff = a.replicate ? -1 : (b.replicate ? 1 : 0);
                }
                break;
            case 'assembly':
                if (a.assembly && b.assembly) {
                    diff = a.assembly > b.assembly ? 1 : (a.assembly === b.assembly ? 0 : -1);
                } else {
                    diff = a.assembly ? -1 : (b.assembly ? 1 : 0);
                }
                break;
            case 'annotation':
                if (a.genome_annotation && b.genome_annotation) {
                    diff = a.genome_annotation > b.genome_annotation ? 1 : (a.genome_annotation === b.genome_annotation ? 0 : -1);
                } else {
                    diff = a.genome_annotation ? -1 : (b.genome_annotation ? 1 : 0);
                }
                break;
            case 'title':
                diff = a.lab.title > b.lab.title ? 1 : (a.lab.title === b.lab.title ? 0 : -1);
                break;
            case 'date_created':
                if (a.date_created && b.date_created) {
                    diff = Date.parse(a.date_created) - Date.parse(b.date_created);
                } else {
                    diff = a.date_created ? -1 : (b.date_created ? 1 : 0);
                }
                break;
            case 'file_size':
                diff = (a.file_size || 0) - (b.file_size || 0);
                break;
            default:
                diff = 0;
                break;
        }
        return this.state.reversed ? -diff : diff;
    },

    render: function() {
        // Creating an object here dedupes when a file is listed under both related_files and original_files
        var rows = {};
        var encodevers = this.props.encodevers;
        var cellClass = {
            accession: 'tcell-sort',
            file_format: 'tcell-sort',
            output_type: 'tcell-sort',
            paired_end: 'tcell-sort',
            bio_replicate: 'tcell-sort',
            tech_replicate: 'tcell-sort',
            assembly: 'tcell-sort',
            annotation: 'tcell-sort',
            title: 'tcell-sort',
            date_created: 'tcell-sort',
            file_size: 'tcell-sort'
        };
        cellClass[this.state.col] = this.state.reversed ? 'tcell-desc' : 'tcell-asc';
        var files = this.props.items.slice(0);
        files.sort(this.sortCol).forEach(function (file) {
            rows[file['@id']] = (
                <tr>
                    <td>{file.accession}</td>
                    <td>{file.file_format}</td>
                    <td>{file.output_type}</td>
                    <td>{file.paired_end}</td>
                    <td>{file.replicate ? file.replicate.biological_replicate_number : null}</td>
                    <td>{file.replicate ? file.replicate.technical_replicate_number : null}</td>
                    <td>{file.assembly}</td>
                    <td>{file.genome_annotation}</td>
                    <td>{file.lab && file.lab.title ? file.lab.title : null}</td>
                    <td>{moment(file.date_created).format('YYYY-MM-DD')}</td>
                    <td>{humanFileSize(file.file_size)}</td>
                    <td><a href={file.href} download={file.href.substr(file.href.lastIndexOf("/") + 1)} data-bypass="true"><i className="icon icon-download"></i> Download</a></td>
                    {encodevers == "3" ? <td className="characterization-meta-data"><StatusLabel status="pending" /></td> : null}
                </tr>
            );
        });
        return (
            <div className="table-responsive">
                <table className="table table-panel table-striped table-hover table-file">
                    <thead>
                        <tr>
                            <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'accession')}>Accession<i className={cellClass.accession}></i></th>
                            <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'file_format')}>File type<i className={cellClass.file_format}></i></th>
                            <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'output_type')}>Output type<i className={cellClass.output_type}></i></th>
                            <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'paired_end')}>Paired end<i className={cellClass.paired_end}></i></th>
                            <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'bio_replicate')}>Biological replicate<i className={cellClass.bio_replicate}></i></th>
                            <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'tech_replicate')}>Technical replicate<i className={cellClass.tech_replicate}></i></th>
                            <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'assembly')}>Mapping assembly<i className={cellClass.assembly}></i></th>
                            <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'annotation')}>Genome annotation<i className={cellClass.annotation}></i></th>
                            <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'title')}>Lab<i className={cellClass.title}></i></th>
                            <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'date_created')}>Date added<i className={cellClass.date_created}></i></th>
                            <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'file_size')}>File size<i className={cellClass.file_size}></i></th>
                            <th>File download</th>
                            {encodevers == "3" ? <th>Validation status</th> : null}
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                    <tfoot>
                        <tr>
                            <td colSpan={encodevers == "3" ? 13 : 12}></td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        );
    }
});
