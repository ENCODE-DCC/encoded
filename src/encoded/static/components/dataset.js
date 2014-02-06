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
                        {context.dataset_type ? <dd>{context.dataset_type}</dd> : null}
                        
                        {context.lab ? <dt>Lab</dt> : null}
                        {context.lab ? <dd>{context.lab.title}</dd> : null}
                        
                        {context.aliases.length ? <dt>Aliases</dt> : null}
                        {context.aliases.length ? <dd>{context.aliases.join(", ")}</dd> : null}
                        
                        <dt>External resources</dt>
						<dd>
							{context.geo_dbxrefs.length ?
								<DbxrefList values={context.geo_dbxrefs} />
							: <em>None submitted</em> }
						</dd>
                    </dl>
                </div>

				 {context.documents.length ?
                    <div>
                        <h3>Dataset documents</h3>
                        {context.documents.map(Panel)}
                    </div>
                : null}

				<ExperimentsLinked context={context} />
                <FilesLinked context={context} />
            </div>
        );
    }
});

globals.content_views.register(Dataset, 'dataset');


var ExperimentsLinked = module.exports.ExperimentsLinked = function (props) {
    var context = props.context;
    var files = context.files;
    if (!files.length) return (<div hidden={true}></div>);
    return (
        <div>
            <h3>Related experiments for dataset {context.accession}</h3>
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
                {files.map(function (file, index) {
                	var experiment = file.replicate.experiment;
                    return (
                        <tr key={index}>
                            <td><a href={experiment['@id']}>{experiment.accession}</a></td>
                            <td>{experiment.assay_term_name}</td>
                            <td>{experiment.biosample_term_name}</td>
                            <td>{experiment.target && experiment.target.label ? experiment.target.label : null}</td>
                            <td>{experiment.description}</td>
                            <td>{experiment.lab.title}</td>            
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
};


var FilesLinked = module.exports.FilesLinked = function (props) {
    var context = props.context;
    var files = context.files;
    if (!files.length) return (<div hidden={true}></div>);
    return (
        <div>
            <h3>Files for dataset {context.accession}</h3>
            <table>
                <thead>
                    <tr>
                        <th>Accession</th>
                        <th>File type</th>
                        <th>Associated replicates</th>
                        <th>Added by</th>
                        <th>Date added</th>
                        <th>File download</th>
                    </tr>
                </thead>
                <tbody>
                {files.map(function (file, index) {
                    var href = 'http://encodedcc.sdsc.edu/warehouse/' + file.download_path;
                    return (
                        <tr key={index}>
                            <td>{file.accession}</td>
                            <td>{file.file_format}</td>
                            <td>{file.replicate ?
                                '(' + file.replicate.biological_replicate_number + ', ' + file.replicate.technical_replicate_number + ')'
                                : null}
                            </td>
                            <td>{file.submitted_by.title}</td>
                            <td>{file.date_created}</td>
                            <td><a href={href} download><i className="icon-download-alt"></i> Download</a></td>
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
};
