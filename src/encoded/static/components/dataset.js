/** @jsx React.DOM */
'use strict';
var React = require('react');
var _ = require('underscore');
var globals = require('./globals');
var dbxref = require('./dbxref');

var DbxrefList = dbxref.DbxrefList;
var Dbxref = dbxref.Dbxref;

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
        var pubmed_url = "http://www.ncbi.nlm.nih.gov/pubmed/?term=";
        var pubmed_links = context.references.map(function(id) {
        	return <li><a href={pubmed_url + id.slice(5)}>{id}</a></li>;
        });
        var experiments = {};
        context.files.forEach(function (file) {
            var experiment = file.replicate && file.replicate.experiment;
            if (experiment) {
                experiments[experiment['@id']] = experiment;
            }
        });
        experiments = _.values(experiments);
        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="span12">
                        <h2>Dataset {context.accession}</h2>
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
                            {context.geo_dbxrefs.length ?
                                <DbxrefList values={context.geo_dbxrefs} prefix="GEO" />
                            : <em>None submitted</em> }
                        </dd>

                        {context.references.length ? <dt>References</dt> : null}
                        {context.references.length ? <dd>
                        	<ul className="horizontal-list">
                        		{pubmed_links}
                        	</ul>
                        </dd> : null}
                    </dl>
                </div>

				{context.documents.length ?
                    <div>
                        <h3>Dataset documents</h3>
                        {context.documents.map(Panel)}
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


var ExperimentTable = module.exports.ExperimentTable = React.createClass({
    render: function() {
        return (
            <table>
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
        );
    }
});


var FileTable = module.exports.FileTable = React.createClass({
    render: function() {
        // Creating an object here dedupes when a file is listed under both related_files and original_files
        var rows = {};
        this.props.items.forEach(function (file) {
            var href = 'http://encodedcc.sdsc.edu/warehouse/' + file.download_path;
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
                    <td><a href={href} download><i className="icon-download-alt"></i> Download</a></td>
                </tr>
            );
        });
        return (
            <table>
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
                    </tr>
                </thead>
                <tbody>
                {rows}
                </tbody>
                <tfoot>
                    <tr>
                        <td colSpan="8"></td>
                    </tr>
                </tfoot>
            </table>
        );
    }
});
