/** @jsx React.DOM */
'use strict';
var React = require('react');
var _ = require('underscore');
var globals = require('./globals');
var dbxref = require('./dbxref');
var dataset = require('./dataset');

var DbxrefList = dbxref.DbxrefList;
var FileTable = dataset.FileTable;

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
        var dbxrefs = context.encode2_dbxrefs.map(function (item) {
        	return "UCSC_encode_db:" + item;
        });
        var documents = {};
        replicates.forEach(function (replicate) {
            if (!replicate.library) return;
            replicate.library.documents.forEach(function (doc) {
                documents[doc['@id']] = Panel({context: doc});
            });
        })
        // Adding experiment specific documents
        context.documents.forEach(function (document) {
            documents[document['@id']] = Panel({context: document})
        });
        var antibodies = {};
        replicates.forEach(function (replicate) {
            if (replicate.antibody) {
                antibodies[replicate.antibody['@id']] = replicate.antibody;
            }
        });
        var antibody_accessions = []
        for (var key in antibodies) {
            antibody_accessions.push(antibodies[key].accession);
        }
        // XXX This makes no sense.
        //var control = context.possible_controls[0];
        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="span12">
                        <ul className="breadcrumb">
                            <li>Experiment <span className="divider">/</span></li>
                            <li className="active">{context.assay_term_name}</li>
                        </ul>
                        <h2>Experiment summary for {context.accession}</h2>
                    </div>
                </header>
                <div className="panel data-display">
                    <dl className="key-value">
                        <dt>Accession</dt>
                        <dd>{context.accession}</dd>

                        <dt hidden={!context.description}>Description</dt>
                        <dd hidden={!context.description}>{context.description}</dd>

                        <dt hidden={!context.biosample_term_name}>Biosample</dt>
                        <dd hidden={!context.biosample_term_name}>{context.biosample_term_name}</dd>

                        <dt hidden={!context.biosample_type}>Biosample type</dt>
                        <dd hidden={!context.biosample_type}>{context.biosample_type}</dd>

                        {context.target ? <dt>Target</dt> : null}
                        {context.target ? <dd><a href={context.target['@id']}>{context.target.label}</a></dd> : null}

                        {antibody_accessions.length ? <dt>Antibody</dt> : null}
                        {antibody_accessions.length ? <dd>{antibody_accessions.join(', ')}</dd> : null}

                        <dt hidden={!context.possible_controls.length}>Controls</dt>
                        <dd hidden={!context.possible_controls.length}>
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

                        <dt>Lab</dt>
                        <dd>{context.lab.title}</dd>

                        <dt hidden={!context.aliases.length}>Aliases</dt>
                        <dd hidden={!context.aliases.length}>{context.aliases.join(", ")}</dd>

                        <dt>Project</dt>
                        <dd>{context.award.project}</dd>
                        
                        <dt hidden={!context.encode2_dbxrefs.length}>Other identifiers</dt>
                        <dd hidden={!context.encode2_dbxrefs.length}>
                            <DbxrefList values={dbxrefs} />
                        </dd>
                        
                        {context.geo_dbxrefs.length ? <dt>GEO Accessions</dt> : null}
                        {context.geo_dbxrefs.length ? <dd>
                            <DbxrefList values={context.geo_dbxrefs} prefix="GEO" />
                        </dd> : null}

                    </dl>
                </div>

                <BiosamplesUsed replicates={replicates} />
                <AssayDetails replicates={replicates} />

                <div hidden={!Object.keys(documents).length}>
                    <h3>Protocols</h3>
                    {documents}
                </div>

                {replicates.map(function (replicate, index) {
                    return (
                        <Replicate replicate={replicate} key={index} />
                    );
                })}

                {context.files.length ?
                    <div>
                        <h3>Files linked to {context.accession}</h3>
                        <FileTable items={context.files} />
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
        };
    });
    return (
        <div>
            <h3>Biosamples used</h3>
            <table>
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
				{library && library.nucleic_acid_starting_quantity ? <dd>{library.nucleic_acid_starting_quantity}</dd> : null}
				
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
    var library = replicate.library;
    var biosample = library && library.biosample;
    return (
        <div key={props.key}>
            <h3>Biological replicate - {replicate.biological_replicate_number}</h3>
            <dl className="panel key-value">
                <dt>Technical replicate</dt>
                <dd>{replicate.technical_replicate_number}</dd>

                {library ? <dt>Library</dt> : null}
                {library ? <dd>{library.accession}</dd> : null}

                {biosample ? <dt>Biosample</dt> : null}
                {biosample ? <dd>
                    <a href={biosample['@id']}>
                        {biosample.accession}
                    </a>{' '}-{' '}{biosample.biosample_term_name}
                </dd> : null}
            </dl>
        </div>
    );
};

// Can't be a proper panel as the control must be passed in.
//globals.panel_views.register(Replicate, 'replicate');
