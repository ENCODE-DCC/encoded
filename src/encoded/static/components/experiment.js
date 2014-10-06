/** @jsx React.DOM */
/** @jsx React.DOM */
'use strict';
var React = require('react');
var _ = require('underscore');
var globals = require('./globals');
var dbxref = require('./dbxref');
var dataset = require('./dataset');
var statuslabel = require('./statuslabel');

var DbxrefList = dbxref.DbxrefList;
var FileTable = dataset.FileTable;
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

        // Process biosamples for summary display
        var biosamples = [], lifeAge = [], organismName = [];
        replicates.forEach(function (replicate) {
            var biosample = replicate.library && replicate.library.biosample;
            if (biosample) {
                biosamples.push(biosample);

                // Add to array of scientific names for rare experiments with cross-species biosamples
                organismName.push(biosample.organism.scientific_name);

                // Build a string with non-'unknown' life_stage, age, and age_units concatenated
                var lifeAgeString = (biosample.life_stage && biosample.life_stage != 'unknown') ? biosample.life_stage : '';
                if (biosample.age && biosample.age != 'unknown') {
                    lifeAgeString += (lifeAgeString ? ' ' : '') + biosample.age;
                    lifeAgeString += (biosample.age_units && biosample.age_units != 'unknown') ? ' ' + biosample.age_units : '';
                }
                if (lifeAgeString) {
                    lifeAge.push(lifeAgeString);
                }
            }
        });

        // Eliminate duplicates in lifeAge and organismName arrays so each displayed only once
        if (lifeAge.length) {
            lifeAge = _.uniq(lifeAge);
        }
        if (organismName.length) {
            organismName = _.uniq(organismName);
        }

        // Build the text of the Treatment string
        var treatmentText = [];
        biosamples.map(function(biosample) {
            treatmentText = treatmentText.concat(biosample.treatments.map(function(treatment) {
                var singleTreatment = '';
                if (treatment.concentration) {
                    singleTreatment += treatment.concentration + (treatment.concentration_units ? ' ' + treatment.concentration_units : '') + ' ';
                }
                singleTreatment += treatment.treatment_term_name + (treatment.treatment_term_id ? ' (' + treatment.treatment_term_id + ')' : '') + ' ';
                if (treatment.duration) {
                    singleTreatment += 'for ' + treatment.duration + ' ' + (treatment.duration_units ? treatment.duration_units : '');
                }
                return singleTreatment;
            }));
        });
        if (treatmentText) {
            treatmentText = _.uniq(treatmentText);
        }

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

        // Make string of alternate accessions
        var altacc = context.alternate_accessions ? context.alternate_accessions.join(', ') : undefined;

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
                        {altacc ? <h4 className="repl-acc">Replaces {altacc}</h4> : null}
                        <div className="characterization-status-labels">
                            <StatusLabel status={statuses} />
                        </div>
                   </div>
                </header>
                <div className="panel data-display">
                    <dl className="key-value">
                        <dt>Assay</dt>
                        <dd>{context.assay_term_name}</dd>

                        <dt>Accession</dt>
                        <dd>{context.accession}</dd>

                        {biosamples.length || context.biosample_term_name ? <dt>Biosample summary</dt> : null}
                        {biosamples.length || context.biosample_term_name ?
                            <dd>
                                {context.biosample_term_name ? <span>{context.biosample_term_name + ' '}</span> : null}
                                {organismName.length || lifeAge.length ? '(' : null}
                                {organismName.length ?
                                    <span>
                                        {organismName.map(function(name, i) {
                                            if (i === 0) {
                                                return (<em key={name}>{name}</em>);
                                            } else {
                                                return (<span key={name}>{' and '}<em>{name}</em></span>);
                                            }
                                        })}
                                    </span>
                                : null}
                                {lifeAge.length ? ', ' + lifeAge.join(' and ') : ''}
                                {organismName.length || lifeAge.length ? ')' : null}
                            </dd>
                        : null}

                        {context.biosample_type ? <dt>Type</dt> : null}
                        {context.biosample_type ? <dd>{context.biosample_type}</dd> : null}

                        {treatmentText.length ? <dt>Treatment</dt> : null}
                        {treatmentText.length ?
                            <dd>
                                <ul>
                                    {treatmentText.map(function (treatment) {
                                        return (<li>{treatment}</li>);
                                    })}
                                </ul>
                            </dd>
                        : null}

                        {context.target ? <dt>Target</dt> : null}
                        {context.target ? <dd><a href={context.target['@id']}>{context.target.label}</a></dd> : null}

                        {Object.keys(antibodies).length ?
                            <div>
                                <dt>Antibody</dt>
                                <dd>{Object.keys(antibodies).map(function(antibody, i) {
                                    return (<span>{i !== 0 ? ', ' : ''}<a href={antibody}>{antibodies[antibody].accession}</a></span>);
                                })}</dd>
                            </div>
                        : null}

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

                        {context.description ? <dt>Description</dt> : null}
                        {context.description ? <dd>{context.description}</dd> : null}

                        <dt>Lab</dt>
                        <dd>{context.lab.title}</dd>

                        <dt>Project</dt>
                        <dd>{context.award.project}</dd>

                        {context.dbxrefs.length ? <dt>External resources</dt> : null}
                        {context.dbxrefs.length ? <dd><DbxrefList values={context.dbxrefs} /></dd> : null}

                        {context.aliases.length ? <dt>Aliases</dt> : null}
                        {context.aliases.length ? <dd>{aliasList}</dd> : null}

                        {context.references.length ? <dt>References</dt> : null}
                        {context.references.length ? <dd><DbxrefList values={context.references} /></dd> : null}

                        {context.date_released ? <dt>Date released</dt> : null}
                        {context.date_released ? <dd>{context.date_released}</dd> : null}

                    </dl>
                </div>

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

                {context.visualize_ucsc  && context.status == "released" ?
                    <span className="pull-right">
                        <a data-bypass="true" target="_blank" private-browsing="true" className="btn btn-info btn-sm" href={context['visualize_ucsc']}>Visualize Data</a>
                    </span>
                : null }

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

    if (!library && !depletedIn && !treatments && !platform) {
        return (<div hidden={true}></div>);
    }

    return (
        <div className = "panel-assay">
            <h3>Assay details</h3>
            <dl className="panel key-value">
                {library && library.nucleic_acid_term_name ? <dt>Nucleic acid type</dt> : null}
				{library && library.nucleic_acid_term_name ? <dd>{library.nucleic_acid_term_name}</dd> : null}

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

                {library && library.spikeins_used && library.spikeins_used.length ?
                    <div data-test="spikeins">
                        <dt>Spike-ins datasets</dt>
                        <dd>
                            {library.spikeins_used.map(function(dataset, i) {
                                return (
                                    <span key={i}>
                                        {i > 0 ? ', ' : ''}
                                        <a href={dataset['@id']}>{dataset.accession}</a>
                                    </span>
                                );
                            })}
                        </dd>
                    </div>
                : null}
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
        <div key={props.key} className="panel-replicate">
            <h3>Biological replicate - {replicate.biological_replicate_number}</h3>
            <dl className="panel key-value">
                <dt>Technical replicate</dt>
                <dd>{replicate.technical_replicate_number}</dd>

                {concentration ? <dt>Protein concentration</dt> : null}
                {concentration ? <dd>{concentration}<span className="unit">{replicate.rbns_protein_concentration_units}</span></dd> : null}

                {library ? <dt>Library</dt> : null}
                {library ? <dd>{library.accession}</dd> : null}

                {library && library.nucleic_acid_starting_quantity ? <dt>Library starting quantity</dt> : null}
                {library && library.nucleic_acid_starting_quantity ?
                    <dd>{library.nucleic_acid_starting_quantity}<span className="unit">{library.nucleic_acid_starting_quantity_units}</span></dd>
                : null}
                
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
