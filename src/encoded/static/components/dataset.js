'use strict';
var React = require('react');
var _ = require('underscore');
var cx = require('react/lib/cx');
var moment = require('moment');
var globals = require('./globals');
var dbxref = require('./dbxref');
var fetched = require('./fetched');
var audit = require('./audit');
var statuslabel = require('./statuslabel');
var graph = require('./graph');
var reference = require('./reference');

var DbxrefList = dbxref.DbxrefList;
var Dbxref = dbxref.Dbxref;
var FetchedItems = fetched.FetchedItems;
var StatusLabel = statuslabel.StatusLabel;
var PubReferenceList = reference.PubReferenceList;
var AuditIndicators = audit.AuditIndicators;
var AuditDetail = audit.AuditDetail;
var AuditMixin = audit.AuditMixin;

var Panel = function (props) {
    // XXX not all panels have the same markup
    var context;
    if (props['@id']) {
        context = props;
        props = {context: context};
    }
    var PanelView = globals.panel_views.lookup(props.context);
    return <PanelView {...props} />;
};

var Dataset = module.exports.Dataset = React.createClass({
    mixins: [AuditMixin],
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-item');
        var experiments = {};
        var statuses = [{status: context.status, title: "Status"}];
        context.files.forEach(function(file) {
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
                        <div className="status-line">
                            <div className="characterization-status-labels">
                                <StatusLabel status={statuses} />
                            </div>
                            <AuditIndicators audits={context.audit} id="dataset-audit" />
                        </div>
                    </div>
                </header>
                <AuditDetail context={context} id="dataset-audit" />
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

                        {context.references && context.references.length ?
                            <div data-test="references">
                                <dt>References</dt>
                                <dd><PubReferenceList values={context.references} /></dd>
                            </div>
                        : null}
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
                    <ExperimentTable
                        items={experiments}
                        title={'Related experiments for dataset ' + context.accession} />
                : null }

                {context.files.length ?
                    <div>
                        <h3>Files for dataset {context.accession}</h3>
                        <FileTable items={context.files} />
                    </div>
                : null }

                {{'released': 1, 'release ready': 1}[context.status] ?
                    <FetchedItems {...this.props} url={unreleased_files_url(context)} Component={UnreleasedFiles} />
                : null}

            </div>
        );
    }
});

globals.content_views.register(Dataset, 'Dataset');


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
                <FileTable {...this.props} />
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
            <div>
                {this.props.title ? <h3>{this.props.title}</h3> : ''}
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
        return {
            col: {raw: 'accession', proc: 'accession'},
            reversed: {raw: false, proc: false, ref: false}
        };
    },

    sortDir: function(section, colName) {
        this.state.reversed[section] = colName === this.state.col[section] ? !this.state.reversed[section] : false;
        this.state.col[section] = colName;
        this.setState({col: this.state.col, reversed: this.state.reversed});
    },

    sortColRaw: function(a, b) {
        var diff;

        switch (this.state.col.raw) {
            case 'accession':
                diff = a.accession > b.accession ? 1 : -1;
                break;
            case 'file_type':
                diff = a.file_type > b.file_type ? 1 : (a.file_type === b.file_type ? 0 : -1);
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
            case 'read_length':
                if (a.read_length && b.read_length) {
                    diff = a.read_length - b.read_length;
                } else {
                    diff = a.read_length ? -1 : (b.read_length ? 1 : 0);
                }
                break;
            case 'run_type':
                if (a.run_type && b.run_type) {
                    diff = a.run_type - b.run_type;
                } else {
                    diff = a.run_type ? -1 : (b.run_type ? 1 : 0);
                }
                break;
            case 'assembly':
                if (a.assembly && b.assembly) {
                    diff = a.assembly > b.assembly ? 1 : (a.assembly === b.assembly ? 0 : -1);
                } else {
                    diff = a.assembly ? -1 : (b.assembly ? 1 : 0);
                }
                break;
            case 'date_created':
                if (a.date_created && b.date_created) {
                    diff = Date.parse(a.date_created) - Date.parse(b.date_created);
                } else {
                    diff = a.date_created ? -1 : (b.date_created ? 1 : 0);
                }
                break;
            default:
                diff = 0;
                break;
        }
        return this.state.reversed.raw ? -diff : diff;
    },

    sortColProc: function(a, b) {
        var diff;

        switch (this.state.col.proc) {
            case 'title':
                diff = a.title > b.title ? 1 : -1;
                break;
            case 'file_type':
                diff = a.file_type > b.file_type ? 1 : (a.file_type === b.file_type ? 0 : -1);
                break;
            case 'output_type':
                var aLower = a.output_type.toLowerCase();
                var bLower = b.output_type.toLowerCase();
                diff = aLower > bLower ? 1 : (aLower === bLower ? 0 : -1);
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
            case 'lab':
                diff = a.lab.title > b.lab.title ? 1 : (a.lab.title === b.lab.title ? 0 : -1);
                break;
            case 'date_created':
                if (a.date_created && b.date_created) {
                    diff = Date.parse(a.date_created) - Date.parse(b.date_created);
                } else {
                    diff = a.date_created ? -1 : (b.date_created ? 1 : 0);
                }
                break;
            default:
                diff = 0;
                break;
        }
        return this.state.reversed.proc ? -diff : diff;
    },

    sortColRef: function(a, b) {
        var diff;

        switch (this.state.col.ref) {
            case 'title':
                diff = a.title > b.title ? 1 : -1;
                break;
            case 'file_type':
                diff = a.file_type > b.file_type ? 1 : (a.file_type === b.file_type ? 0 : -1);
                break;
            case 'output_type':
                var aLower = a.output_type.toLowerCase();
                var bLower = b.output_type.toLowerCase();
                diff = aLower > bLower ? 1 : (aLower === bLower ? 0 : -1);
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
            case 'lab':
                diff = a.lab.title > b.lab.title ? 1 : (a.lab.title === b.lab.title ? 0 : -1);
                break;
            case 'date_created':
                if (a.date_created && b.date_created) {
                    diff = Date.parse(a.date_created) - Date.parse(b.date_created);
                } else {
                    diff = a.date_created ? -1 : (b.date_created ? 1 : 0);
                }
                break;
            default:
                diff = 0;
                break;
        }
        return this.state.reversed.ref ? -diff : diff;
    },

    render: function() {
        // Creating an object here dedupes when a file is listed under both related_files and original_files
        var rowsRaw = {};
        var rowsProc = {};
        var rowsRef = {};
        var encodevers = this.props.encodevers;
        var bioRepTitle = this.props.anisogenic ? 'Anisogenic' : 'Biological';
        var cellClassRaw = {
            title: 'tcell-sort',
            file_type: 'tcell-sort',
            bio_replicate: 'tcell-sort',
            tech_replicate: 'tcell-sort',
            read_length: 'tcell-sort',
            run_type: 'tcell-sort',
            paired_end: 'tcell-sort',
            assembly: 'tcell-sort',
            lab: 'tcell-sort',
            date_created: 'tcell-sort'
        };
        var cellClassProc = {
            title: 'tcell-sort',
            file_type: 'tcell-sort',
            output_type: 'tcell-sort',
            bio_replicate: 'tcell-sort',
            tech_replicate: 'tcell-sort',
            assembly: 'tcell-sort',
            annotation: 'tcell-sort',
            lab: 'tcell-sort',
            date_created: 'tcell-sort'
        };
        var cellClassRef = {
            title: 'tcell-sort',
            file_type: 'tcell-sort',
            output_type: 'tcell-sort',
            assembly: 'tcell-sort',
            annotation: 'tcell-sort',
            lab: 'tcell-sort',
            date_created: 'tcell-sort'
        };

        var colCountRaw = Object.keys(cellClassRaw).length + (encodevers == "3" ? 1 : 0);
        var colCountProc = Object.keys(cellClassProc).length + (encodevers == "3" ? 1 : 0);
        var colCountRef = Object.keys(cellClassRef).length + (encodevers == "3" ? 1 : 0);
        cellClassRaw[this.state.col.raw] = this.state.reversed.raw ? 'tcell-desc' : 'tcell-asc';
        cellClassProc[this.state.col.proc] = this.state.reversed.proc ? 'tcell-desc' : 'tcell-asc';
        cellClassRef[this.state.col.ref] = this.state.reversed.ref ? 'tcell-desc' : 'tcell-asc';
        var files = _(this.props.items).groupBy(function(file) {
            if (file.output_category === 'raw data') {
               return 'raw';
            } else if (file.output_category === 'reference') {
               return 'ref';
            } else {
               return 'proc';
            }
        });
        if (files.raw) {
            files.raw.sort(this.sortColRaw).forEach(function (file) {
                rowsRaw[file['@id']] = (
                    <tr>
                        <td>
                            {file.title}<br />
                            <a href={file.href} download={file.href.substr(file.href.lastIndexOf("/") + 1)} data-bypass="true"><i className="icon icon-download"></i> Download</a><br />
                            {humanFileSize(file.file_size)}
                        </td>
                        <td>{file.file_type}</td>
                        <td>{file.biological_replicates ? file.biological_replicates.sort(function(a,b){ return a - b; }).join(', ') : null}</td>
                        <td>{file.replicate ? file.replicate.technical_replicate_number : null}</td>
                        <td>{file.read_length ? <span>{file.read_length + ' ' + file.read_length_units}</span> : null}</td>
                        <td>{file.run_type ? file.run_type : null}</td>
                        <td>{file.paired_end}</td>
                        <td>{file.assembly}</td>
                        <td>{file.lab && file.lab.title ? file.lab.title : null}</td>
                        <td>{moment.utc(file.date_created).format('YYYY-MM-DD')}</td>
                        {encodevers == "3" ? <td className="characterization-meta-data"><StatusLabel status="pending" /></td> : null}
                    </tr>
                );
            });
        }
        if (files.proc) {
            files.proc.sort(this.sortColProc).forEach(function (file) {
                rowsProc[file['@id']] = (
                    <tr>
                        <td>
                            {file.title}<br />
                            <a href={file.href} download={file.href.substr(file.href.lastIndexOf("/") + 1)} data-bypass="true"><i className="icon icon-download"></i> Download</a><br />
                            {humanFileSize(file.file_size)}
                        </td>
                        <td>{file.file_type}</td>
                        <td>{file.output_type}</td>
                        <td>{file.biological_replicates ? file.biological_replicates.sort(function(a,b){ return a - b; }).join(', ') : null}</td>
                        <td>{file.replicate ? file.replicate.technical_replicate_number : null}</td>
                        <td>{file.assembly}</td>
                        <td>{file.genome_annotation}</td>
                        <td>{file.lab && file.lab.title ? file.lab.title : null}</td>
                        <td>{moment.utc(file.date_created).format('YYYY-MM-DD')}</td>
                        {encodevers == "3" ? <td className="characterization-meta-data"><StatusLabel status="pending" /></td> : null}
                    </tr>
                );
            });
        }
        if (files.ref) {
            files.ref.sort(this.sortColRef).forEach(function (file) {
                rowsRef[file['@id']] = (
                    <tr>
                        <td>
                            {file.title}<br />
                            <a href={file.href} download={file.href.substr(file.href.lastIndexOf("/") + 1)} data-bypass="true"><i className="icon icon-download"></i> Download</a><br />
                            {humanFileSize(file.file_size)}
                        </td>
                        <td>{file.file_type}</td>
                        <td>{file.output_type}</td>
                        <td>{file.assembly}</td>
                        <td>{file.genome_annotation}</td>
                        <td>{file.lab && file.lab.title ? file.lab.title : null}</td>
                        <td>{moment.utc(file.date_created).format('YYYY-MM-DD')}</td>
                        {encodevers == "3" ? <td className="characterization-meta-data"><StatusLabel status="pending" /></td> : null}
                    </tr>
                );
            });
        }
        return (
            <div className="table-panel table-file">
                {files.raw ?
                    <div className="table-responsive">
                        <table className="table table-responsive table-striped">
                            <thead>
                                <tr className="table-section"><th colSpan={colCountRaw}>Raw data</th></tr>
                                <tr>
                                    <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'raw', 'title')}>Accession<i className={cellClassRaw.title}></i></th>
                                    <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'raw', 'file_type')}>File type<i className={cellClassRaw.file_type}></i></th>
                                    <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'raw', 'bio_replicate')}>{bioRepTitle} replicate<i className={cellClassRaw.bio_replicate}></i></th>
                                    <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'raw', 'tech_replicate')}>Technical replicate<i className={cellClassRaw.tech_replicate}></i></th>
                                    <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'raw', 'read_length')}>Read length<i className={cellClassRaw.read_length}></i></th>
                                    <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'raw', 'run_type')}>Run type<i className={cellClassRaw.run_type}></i></th>
                                    <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'raw', 'paired_end')}>Paired end<i className={cellClassRaw.paired_end}></i></th>
                                    <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'raw', 'assembly')}>Mapping assembly<i className={cellClassRaw.assembly}></i></th>
                                    <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'raw', 'lab')}>Lab<i className={cellClassRaw.lab}></i></th>
                                    <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'raw', 'date_created')}>Date added<i className={cellClassRaw.date_created}></i></th>
                                    {encodevers == "3" ? <th>Validation status</th> : null}
                                </tr>
                            </thead>
                            <tbody>
                                {rowsRaw}
                            </tbody>
                            <tfoot>
                                <tr>
                                    <td colSpan={colCountRaw}></td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                : null}

                {files.proc ?
                    <div className="table-responsive">
                        <table className="table table-striped">
                            <thead>
                                <tr className="table-section"><th colSpan={colCountProc}>Processed data</th></tr>
                                <tr>
                                    <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'proc', 'title')}>Accession<i className={cellClassProc.title}></i></th>
                                    <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'proc', 'file_type')}>File type<i className={cellClassProc.file_type}></i></th>
                                    <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'proc', 'output_type')}>Output type<i className={cellClassProc.output_type}></i></th>
                                    <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'proc', 'bio_replicate')}>{bioRepTitle} replicate(s)<i className={cellClassProc.bio_replicate}></i></th>
                                    <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'proc', 'tech_replicate')}>Technical replicate<i className={cellClassProc.tech_replicate}></i></th>
                                    <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'proc', 'assembly')}>Mapping assembly<i className={cellClassProc.assembly}></i></th>
                                    <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'proc', 'annotation')}>Genome annotation<i className={cellClassProc.annotation}></i></th>
                                    <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'proc', 'lab')}>Lab<i className={cellClassProc.lab}></i></th>
                                    <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'proc', 'date_created')}>Date added<i className={cellClassProc.date_created}></i></th>
                                    {encodevers == "3" ? <th>Validation status</th> : null}
                                </tr>
                            </thead>
                            <tbody>
                                {rowsProc}
                            </tbody>
                            <tfoot>
                                <tr>
                                    <td colSpan={colCountProc}></td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                : null}

                {files.ref ?
                    <div className="table-responsive">
                        <table className="table table-striped">
                            <thead>
                                <tr className="table-section"><th colSpan={colCountRef}>Reference data</th></tr>
                                <tr>
                                    <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'ref', 'title')}>Accession<i className={cellClassRef.title}></i></th>
                                    <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'ref', 'file_type')}>File type<i className={cellClassRef.file_type}></i></th>
                                    <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'ref', 'output_type')}>Output type<i className={cellClassRef.output_type}></i></th>
                                    <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'ref', 'assembly')}>Mapping assembly<i className={cellClassRef.assembly}></i></th>
                                    <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'ref', 'annotation')}>Genome annotation<i className={cellClassRef.annotation}></i></th>
                                    <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'ref', 'lab')}>Lab<i className={cellClassRef.lab}></i></th>
                                    <th className="tcell-sortable" onClick={this.sortDir.bind(null, 'ref', 'date_created')}>Date added<i className={cellClassRef.date_created}></i></th>
                                    {encodevers == "3" ? <th>Validation status</th> : null}
                                </tr>
                            </thead>
                            <tbody>
                                {rowsRef}
                            </tbody>
                            <tfoot>
                                <tr>
                                    <td colSpan={colCountRef}></td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                : null}
            </div>
        );
    }
});
