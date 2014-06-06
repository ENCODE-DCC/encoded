/** @jsx React.DOM */
'use strict';
var React = require('react');
var _ = require('underscore');
var globals = require('./globals');
var dbxref = require('./dbxref');
var dataset = require('./dataset');
var antibody = require('./antibody');

var DbxrefList = dbxref.DbxrefList;
var FileTable = dataset.FileTable;
var StatusLabel = antibody.StatusLabel;

var Panel = function (props) {
    // XXX not all panels have the same markup
    var context;
    if (props['@id']) {
        context = props;
        props = {context: context};
    }
    return globals.panel_views.lookup(props.context)(props);
};


var Experiment = module.exports.Experiment = React.createClass({
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-item');
        var replicates = _.sortBy(context.replicates, function(item) {
            return item.biological_replicate_number;
        });
        var aliasList = context.aliases.join(", ");

        var documents = {};
        replicates.forEach(function (replicate) {
            if (!replicate.library) return;
            replicate.library.documents.forEach(function (doc) {
                documents[doc['@id']] = Panel({context: doc});
            });
        });
        // Adding experiment specific documents
        context.documents.forEach(function (document) {
            documents[document['@id']] = Panel({context: document});
        });
        var antibodies = {};
        replicates.forEach(function (replicate) {
            if (replicate.antibody) {
                antibodies[replicate.antibody['@id']] = replicate.antibody;
            }
        });
        var antibody_accessions = [];
        for (var key in antibodies) {
            antibody_accessions.push(antibodies[key].accession);
        }

        // Determine this experiment's ENCODE version
        var encodevers = "";
        if (context.award.rfa) {
            encodevers = globals.encodeVersionMap[context.award.rfa.substring(0,7)];
            if (typeof encodevers === "undefined") {
                encodevers = "";
            }
        }

        // Make list of statuses
        var statuses = [{status: context.status, title: "Status"}];
        if (encodevers === "3" && context.status === "released") {
            statuses.push({status: "pending", title: "Validation"});
        }

        // XXX This makes no sense.
        //var control = context.possible_controls[0];
        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <ul className="breadcrumb">
                            <li>Experiment</li>
                            <li className="active">{context.assay_term_name}</li>
                        </ul>
                        <h2>
                            Experiment summary for {context.accession}
                        </h2>
                        <div className="characterization-status-labels">
                            <StatusLabel status={statuses} />
                        </div>
                   </div>
                </header>
                <div className="panel data-display">
                    <dl className="key-value">
                        <dt>Accession</dt>
                        <dd>{context.accession}</dd>

                        {context.description ? <dt>Description</dt> : null}
                        {context.description ? <dd>{context.description}</dd> : null}

                        {context.biosample_term_name ? <dt>Biosample</dt> : null}
                        {context.biosample_term_name ? <dd>{context.biosample_term_name}</dd> : null}

                        {context.biosample_type ? <dt>Biosample type</dt> : null}
                        {context.biosample_type ? <dd className="sentence-case">{context.biosample_type}</dd> : null}

                        {context.target ? <dt>Target</dt> : null}
                        {context.target ? <dd><a href={context.target['@id']}>{context.target.label}</a></dd> : null}

                        {antibody_accessions.length ? <dt>Antibody</dt> : null}
                        {antibody_accessions.length ? <dd>{antibody_accessions.join(', ')}</dd> : null}

                        {context.possible_controls.length ? <dt>Controls</dt> : null}
                        {context.possible_controls.length ?
                            <dd>
                                <ul>
                                    {context.possible_controls.map(function (control) {
                                        return (
                                            <li key={control['@id']}>
                                                <a href={control['@id']}>
                                                    {control.accession}
                                                </a>
                                            </li>
                                        );
                                    })}
                                </ul>
                            </dd>
                        : null}

                        <dt>Lab</dt>
                        <dd>{context.lab.title}</dd>

                        <dt>Project</dt>
                        <dd>{context.award.project}</dd>
                        
                        {context.aliases.length ? <dt>Aliases</dt> : null}
                        {context.aliases.length ? <dd>{aliasList}</dd> : null}

                        {context.dbxrefs.length ? <dt>External resources</dt> : null}
                        {context.dbxrefs.length ? <dd><DbxrefList values={context.dbxrefs} /></dd> : null}

                    </dl>
                </div>

                <BiosamplesUsed replicates={replicates} />
                <AssayDetails replicates={replicates} />

                {Object.keys(documents).length ?
                    <div>
                        <h3>Protocols</h3>
                        {documents}
                    </div>
                : null}

                {replicates.map(function (replicate, index) {
                    return (
                        <Replicate replicate={replicate} key={index} />
                    );
                })}

                {context.files.length ?
                    <div>
                        <h3>Files linked to {context.accession}</h3>
                        <FileTable items={context.files} encodevers={encodevers} />
                    </div>
                : null }
            </div>
        );
    }
});

globals.content_views.register(Experiment, 'experiment');

var BiosamplesUsed = module.exports.BiosamplesUsed = function (props) {
    var replicates = props.replicates;
    if (!replicates.length) return (<div hidden={true}></div>);
    var biosamples = {};
    replicates.forEach(function(replicate) {
        var biosample = replicate.library && replicate.library.biosample;
        if (biosample) {
            biosamples[biosample['@id']] = { biosample: biosample, brn: replicate.biological_replicate_number };
        }
    });

    // If no libraries in the replicates, then no biosamples; just output nothing.
    if (!Object.keys(biosamples).length) {
        return (<div hidden={true}></div>);
    }

    return (
        <div>
            <h3>Biosamples used</h3>
            <div className="table-responsive"> 
                <table className="table table-panel table-striped table-hover">
                    <thead>
                        <tr>
                            <th>Accession</th>
                            <th>Biosample</th>
                            <th>Type</th>
                            <th>Species</th>
                            <th>Source</th>
                            <th>Submitter</th>
                        </tr>
                    </thead>
                    <tbody>

                    { Object.keys(biosamples).map(function (key, index) {
                        var biosample = biosamples[key].biosample;
                        return (
                            <tr key={index}>
                                <td><a href={biosample['@id']}>{biosample.accession}</a></td>
                                <td>{biosample.biosample_term_name}</td>
                                <td>{biosample.biosample_type}</td>
                                <td>{biosample.donor && biosample.donor.organism.name}</td>
                                <td>{biosample.source.title}</td>
                                <td>{biosample.submitted_by.title}</td>
                            </tr>
                        );
                    })}
                    </tbody>
                    <tfoot>
                        <tr>
                            <td colSpan="7"></td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        </div>
    );
};


var AssayDetails = module.exports.AssayDetails = function (props) {
    var replicates = props.replicates.sort(function(a, b) {
        if (b.biological_replicate_number === a.biological_replicate_number) {
            return a.technical_replicate_number - b.technical_replicate_number;
        }
        return a.biological_replicate_number - b.biological_replicate_number;
    });
    
    if (!replicates.length) return (<div hidden={true}></div>);
    
    var replicate = replicates[0];
    var library = replicate.library;
    var platform = replicate.platform;
    var depletedIn;
    var treatments;
    
    if (library && library.depleted_in_term_name && library.depleted_in_term_name.length) {
        depletedIn = library.depleted_in_term_name.join(", ");
    }
    
    if (library && library.treatments && library.treatments.length) {
        var i = library.treatments.length;
        var t;
        var treatmentList = [];
        while (i--) {
            t = library.treatments[i];
            treatmentList.push(t.treatment_term_name);
        }
        treatments = treatmentList.join(", ");
    }
    
    return (
        <div>
            <h3>Assay details</h3>
            <dl className="panel key-value">
                {library && library.nucleic_acid_term_name ? <dt>Nucleic acid type</dt> : null}
				{library && library.nucleic_acid_term_name ? <dd>{library.nucleic_acid_term_name}</dd> : null}
    
                {library && library.nucleic_acid_starting_quantity ? <dt>NA starting quantity</dt> : null}
				{library && library.nucleic_acid_starting_quantity ?
                    <dd>{library.nucleic_acid_starting_quantity}<span className="unit">{library.nucleic_acid_starting_quantity_units}</span></dd>
                : null}
				
                {depletedIn ? <dt>Depleted in</dt> : null}
				{depletedIn ? <dd>{depletedIn}</dd> : null}

                {library && library.lysis_method ? <dt>Lysis method</dt> : null}
				{library && library.lysis_method ? <dd>{library.lysis_method}</dd> : null}
    
                {library && library.extraction_method ? <dt>Extraction method</dt> : null}
				{library && library.extraction_method ? <dd>{library.extraction_method}</dd> : null}
                
                {library && library.fragmentation_method ? <dt>Fragmentation method</dt> : null}
				{library && library.fragmentation_method ? <dd>{library.fragmentation_method}</dd> : null}
                
                {library && library.size_range ? <dt>Size range</dt> : null}
				{library && library.size_range ? <dd>{library.size_range}</dd> : null}
                
                {library && library.library_size_selection_method ? <dt>Size selection method</dt> : null}
				{library && library.library_size_selection_method ? <dd>{library.library_size_selection_method}</dd> : null}
                
                {treatments ? <dt>Treatments</dt> : null}
				{treatments ? <dd>{treatments}</dd> : null}
                
                {platform ? <dt>Platform</dt> : null}
				{platform ? <dd><a href={platform['@id']}>{platform.title}</a></dd> : null}
            </dl>
        </div>
    );
};


var Replicate = module.exports.Replicate = function (props) {
    var replicate = props.replicate;
    var concentration = replicate.rbns_protein_concentration;
    var library = replicate.library;
    var biosample = library && library.biosample;
    var paired_end = replicate.paired_ended;
    return (
        <div key={props.key}>
            <h3>Biological replicate - {replicate.biological_replicate_number}</h3>
            <dl className="panel key-value">
                <dt>Technical replicate</dt>
                <dd>{replicate.technical_replicate_number}</dd>

                {concentration ? <dt>Protein concentration</dt> : null}
                {concentration ? <dd>{concentration}<span className="unit">{replicate.rbns_protein_concentration_units}</span></dd> : null}

                {library ? <dt>Library</dt> : null}
                {library ? <dd>{library.accession}</dd> : null}

                {biosample ? <dt>Biosample</dt> : null}
                {biosample ? <dd>
                    <a href={biosample['@id']}>
                        {biosample.accession}
                    </a>{' '}-{' '}{biosample.biosample_term_name}
                </dd> : null}

                {replicate.read_length ? <dt>Run type</dt> : null}
                {replicate.read_length ? <dd>{paired_end ? 'paired-end' : 'single-end'}</dd> : null}

                {replicate.read_length ? <dt>Read length</dt> : null}
                {replicate.read_length ? <dd>{replicate.read_length}<span className="unit">{replicate.read_length_units}</span></dd> : null}
            </dl>
        </div>
    );
};

// Can't be a proper panel as the control must be passed in.
//globals.panel_views.register(Replicate, 'replicate');
