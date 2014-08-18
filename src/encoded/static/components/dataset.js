/** @jsx React.DOM */
'use strict';
var React = require('react');
var _ = require('underscore');
var globals = require('./globals');
var dbxref = require('./dbxref');
var statuslabel = require('./statuslabel');

var DbxrefList = dbxref.DbxrefList;
var Dbxref = dbxref.Dbxref;
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
        context.documents.forEach(function (document) {
            datasetDocuments[document['@id']] = Panel({context: document, popoverContent: StdContent});
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

            </div>
        );
    }
});

globals.content_views.register(Dataset, 'dataset');


var StdContent = module.exports.StdContent = React.createClass({
    render: function() {
        var context = this.props.context;
        return(
            <div>
                {context.caption ? <dt>Caption</dt> : null}
                {context.caption ? <dd>{context.caption}</dd> : null}

                <dt>Submitted by</dt>
                <dd>{context.submitted_by.title}</dd>

                <dt>Grant</dt>
                <dd>{context.award.name}</dd>
            </div>
        );
    }
});


var ExperimentTable = module.exports.ExperimentTable = React.createClass({
    render: function() {
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
                    {this.props.items.map(function (experiment) {
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
                            <td colSpan="6"></td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        );
    }
});


var FileTable = module.exports.FileTable = React.createClass({
    render: function() {
        // Creating an object here dedupes when a file is listed under both related_files and original_files
        var rows = {};
        var encodevers = this.props.encodevers;
        this.props.items.forEach(function (file) {
            rows[file['@id']] = (
                <tr>
                    <td>{file.accession}</td>
                    <td>{file.file_format}</td>
                    <td>{file.output_type}</td>
                    <td>{file.paired_end}</td>
                    <td>{file.replicate ?
                        '(' + file.replicate.biological_replicate_number + ', ' + file.replicate.technical_replicate_number + ')'
                        : null}
                    </td>
                    <td>{file.submitted_by.title}</td>
                    <td>{file.date_created}</td>
                    <td><a href={file.href} download={file.href.substr(file.href.lastIndexOf("/") + 1)} data-bypass="true"><i className="icon icon-download"></i> Download</a></td>
                    {encodevers == "3" ? <td className="characterization-meta-data"><StatusLabel status="pending" /></td> : null}
                </tr>
            );
        });
        return (
            <div className="table-responsive">
                <table className="table table-panel table-striped table-hover">
                    <thead>
                        <tr>
                            <th>Accession</th>
                            <th>File type</th>
                            <th>Output type</th>
                            <th>Paired end</th>
                            <th>Associated replicates</th>
                            <th>Added by</th>
                            <th>Date added</th>
                            <th>File download</th>
                            {encodevers == "3" ? <th>Validation status</th> : null}
                        </tr>
                    </thead>
                    <tbody>
                    {rows}
                    </tbody>
                    <tfoot>
                        <tr>
                            <td colSpan={encodevers == "3" ? 9 : 8}></td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        );
    }
});
