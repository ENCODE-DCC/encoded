'use strict';
var React = require('react');
var _ = require('underscore');
var moment = require('moment');
var graph = require('./graph');
var globals = require('./globals');
var dbxref = require('./dbxref');
var dataset = require('./dataset');
var statuslabel = require('./statuslabel');
var audit = require('./audit');
var fetched = require('./fetched');
var AuditMixin = audit.AuditMixin;
var pipeline = require('./pipeline');
var reference = require('./reference');

var DbxrefList = dbxref.DbxrefList;
var FileTable = dataset.FileTable;
var UnreleasedFiles = dataset.UnreleasedFiles;
var FetchedItems = fetched.FetchedItems;
var FetchedData = fetched.FetchedData;
var Param = fetched.Param;
var StatusLabel = statuslabel.StatusLabel;
var AuditIndicators = audit.AuditIndicators;
var AuditDetail = audit.AuditDetail;
var Graph = graph.Graph;
var JsonGraph = graph.JsonGraph;
var PubReferenceList = reference.PubReferenceList;
var ExperimentTable = dataset.ExperimentTable;

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


var Experiment = module.exports.Experiment = React.createClass({
    mixins: [AuditMixin],

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
            replicate.library.documents.forEach(function (doc, i) {
                documents[doc['@id']] = Panel({context: doc, key: i + 1});
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

        // Build the text of the Treatment, synchronization, and mutatedGene string arrays
        var treatmentText = [];
        var synchText = [];
        var depletedIns = [];
        var mutatedGenes = {};
        var subcellularTerms = {};
        var cellCycles = {};
        biosamples.map(function(biosample) {
            // Collect treatments
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

            // Collect synchronizations
            if (biosample.synchronization) {
                synchText.push(biosample.synchronization +
                    (biosample.post_synchronization_time ?
                        ' + ' + biosample.post_synchronization_time + (biosample.post_synchronization_time_units ? ' ' + biosample.post_synchronization_time_units : '')
                    : ''));
            }

            // Collect depleted_in
            if (biosample.depleted_in_term_name && biosample.depleted_in_term_name.length) {
                depletedIns = depletedIns.concat(biosample.depleted_in_term_name);

            }
            // Collect mutated genes
            if (biosample.donor && biosample.donor.mutated_gene) {
                mutatedGenes[biosample.donor.mutated_gene.label] = true;
            }

            // Collect subcellular fraction term names
            if (biosample.subcellular_fraction_term_name) {
                subcellularTerms[biosample.subcellular_fraction_term_name] = true;
            }

            // Collect cell-cycle phases
            if (biosample.phase) {
                cellCycles[biosample.phase] = true;
            }
        });
        treatmentText = treatmentText && _.uniq(treatmentText);
        synchText = synchText && _.uniq(synchText);
        depletedIns = depletedIns && _.uniq(depletedIns);
        var mutatedGeneNames = Object.keys(mutatedGenes);
        var subcellularTermNames = Object.keys(subcellularTerms);
        var cellCycleNames = Object.keys(cellCycles);

        // Adding experiment specific documents
        context.documents.forEach(function (document, i) {
            documents[document['@id']] = Panel({context: document, key: i + 1});
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

        var experiments_url = '/search/?type=experiment&possible_controls.accession=' + context.accession;

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
                        <div className="status-line">
                            <div className="characterization-status-labels">
                                <StatusLabel status={statuses} />
                            </div>
                            <AuditIndicators audits={context.audit} id="experiment-audit" />
                        </div>
                   </div>
                </header>
                <AuditDetail context={context} id="experiment-audit" />
                <div className="panel data-display">
                    <dl className="key-value">
                        <div data-test="assay">
                            <dt>Assay</dt>
                            <dd>{context.assay_term_name}</dd>
                        </div>

                        <div data-test="accession">
                            <dt>Accession</dt>
                            <dd>{context.accession}</dd>
                        </div>

                        {biosamples.length || context.biosample_term_name ?
                            <div data-test="biosample-summary">
                                <dt>Biosample summary</dt>
                                <dd>
                                    {context.biosample_term_name ? <span>{context.biosample_term_name}</span> : null}
                                    {depletedIns.length ?
                                        <span>{' missing ' + depletedIns.join(', ')}</span>
                                    : null}
                                    {mutatedGeneNames.length ? <span>{', mutated gene: ' + mutatedGeneNames.join('/')}</span> : null}
                                    {subcellularTermNames.length ? <span>{', subcellular fraction: ' + subcellularTermNames.join('/')}</span> : null}
                                    {cellCycleNames.length ? <span>{', cell-cycle phase: ' + cellCycleNames.join('/')}</span> : null}
                                    {organismName.length || lifeAge.length ? ' (' : null}
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
                            </div>
                        : null}

                        {synchText.length ?
                            <div data-test="biosample-synchronization">
                                <dt>Synchronization timepoint</dt>
                                <dd>
                                    {synchText.join(', ')}
                                </dd>
                            </div>
                        : null}

                        {context.biosample_type ?
                            <div data-test="biosample-type">
                                <dt>Type</dt>
                                <dd>{context.biosample_type}</dd>
                            </div>
                        : null}

                        {treatmentText.length ?
                            <div data-test="treatment">
                                <dt>Treatment</dt>
                                <dd>
                                    <ul>
                                        {treatmentText.map(function (treatment) {
                                            return (<li key={treatment}>{treatment}</li>);
                                        })}
                                    </ul>
                                </dd>
                            </div>
                        : null}

                        {context.target ?
                            <div data-test="target">
                                <dt>Target</dt>
                                <dd><a href={context.target['@id']}>{context.target.label}</a></dd>
                            </div>
                        : null}

                        {Object.keys(antibodies).length ?
                            <div data-test="antibody">
                                <dt>Antibody</dt>
                                <dd>{Object.keys(antibodies).map(function(antibody, i) {
                                    return (<span key={antibody}>{i !== 0 ? ', ' : ''}<a href={antibody}>{antibodies[antibody].accession}</a></span>);
                                })}</dd>
                            </div>
                        : null}

                        {context.possible_controls && context.possible_controls.length ?
                            <div data-test="possible-controls">
                                <dt>Controls</dt>
                                <dd>
                                    <ul>
                                        {context.possible_controls.map(function (control) {
                                            return (
                                                <li key={control['@id']} className="multi-comma">
                                                    <a href={control['@id']}>
                                                        {control.accession}
                                                    </a>
                                                </li>
                                            );
                                        })}
                                    </ul>
                                </dd>
                            </div>
                        : null}

                        {context.description ?
                            <div data-test="description">
                                <dt>Description</dt>
                                <dd>{context.description}</dd>
                            </div>
                        : null}

                        <div data-test="lab">
                            <dt>Lab</dt>
                            <dd>{context.lab.title}</dd>
                        </div>

                        {context.award.pi && context.award.pi.lab ?
                            <div data-test="awardpi">
                                <dt>Award PI</dt>
                                <dd>{context.award.pi.lab.title}</dd>
                            </div>
                        : null}

                        <div data-test="project">
                            <dt>Project</dt>
                            <dd>{context.award.project}</dd>
                        </div>

                        {context.dbxrefs.length ?
                            <div data-test="external-resources">
                                <dt>External resources</dt>
                                <dd><DbxrefList values={context.dbxrefs} /></dd>
                            </div>
                        : null}

                        {context.aliases.length ?
                            <div data-test="aliases">
                                <dt>Aliases</dt>
                                <dd>{aliasList}</dd>
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

                        {context.date_released ?
                            <div data-test="date-released">
                                <dt>Date released</dt>
                                <dd>{context.date_released}</dd>
                            </div>
                        : null}
                    </dl>
                </div>

                {AssayDetails({context: context, replicates: replicates})}

                {Object.keys(documents).length ?
                    <div data-test="protocols">
                        <h3>Documents</h3>
                        <div className="row multi-columns-row">
                            {documents}
                        </div>
                    </div>
                : null}

                {replicates.map(function (replicate, index) {
                    return Replicate({replicate: replicate, key: index});
                })}

                {context.visualize_ucsc  && context.status == "released" ?
                    <span className="pull-right">
                        <a data-bypass="true" target="_blank" private-browsing="true" className="btn btn-info btn-sm" href={context['visualize_ucsc']}>Visualize Data</a>
                    </span>
                : null }

                <FetchedData loadingComplete={this.props.loadingComplete}>
                    <Param name="data" url={dataset.unreleased_files_url(context)} />
                    <ExperimentGraph context={context} />
                </FetchedData>

                {context.files.length ?
                    <div>
                        <h3>Files linked to {context.accession}</h3>
                        <FileTable items={context.files} encodevers={encodevers} />
                    </div>
                : null }

                {{'released': 1, 'release ready': 1}[context.status] ?
                    <FetchedItems {...this.props} url={dataset.unreleased_files_url(context)} Component={UnreleasedFiles} />
                : null}

                {context.control_for && context.control_for.length ?
                    <ControllingExperiments {...this.props} url={experiments_url} />
                : null}

            </div>
        );
    }
});

globals.content_views.register(Experiment, 'experiment');


var ControllingExperiments = React.createClass({
    render: function () {
        var context = this.props.context;

        return (
            <div>
                <span className="pull-right">
                    <a className="btn btn-info btn-sm" href={this.props.url}>View all</a>
                </span>

                <div>
                    <h3>Experiments with {context.accession} as a control:</h3>
                    <ExperimentTable {...this.props} items={context.control_for} limit={5} total={context.control_for.length} />
                </div>
            </div>
        );
    }
});


var AssayDetails = module.exports.AssayDetails = function (props) {
    var context = props.context;

    // No replicates, so no assay panel
    if (!props.replicates.length) return null;

    // Sort the replicates first by replicate number, then by technical replicate number
    var replicates = props.replicates.sort(function(a, b) {
        if (b.biological_replicate_number === a.biological_replicate_number) {
            return a.technical_replicate_number - b.technical_replicate_number;
        }
        return a.biological_replicate_number - b.biological_replicate_number;
    });

    // Collect data from the libraries of all of the replicates, ignoring duplicates
    var depleted = [];
    var treatments = [];
    var lib = replicates[0].library;
    if (lib) {
        // Get the array of depleted_in_term_name strings for display
        if (lib.depleted_in_term_name && lib.depleted_in_term_name.length) {
            depleted = lib.depleted_in_term_name;
        }

        // Make an array of treatment term names for display
        if (lib.treatments && lib.treatments.length) {
            treatments = lib.treatments.map(function(treatment) {
                return treatment.treatment_term_name;
            });
        }
    } else {
        // No libraries, so no assay panel
        return null;
    }

    // Create platforms array from file platforms; ignore duplicate platforms
    var platforms = {};
    if (context.files && context.files.length) {
        context.files.forEach(function(file) {
            if (file.platform && file.dataset === context['@id']) {
                platforms[file.platform['@id']] = file.platform;
            }
        });
    }
    var platformKeys = Object.keys(platforms);

    return (
        <div className = "panel-assay">
            <h3>Assay details</h3>
            <dl className="panel key-value">
                {lib.nucleic_acid_term_name ?
                    <div data-test="nucleicacid">
                        <dt>Nucleic acid type</dt>
                        <dd>{lib.nucleic_acid_term_name}</dd>
                    </div>
                : null}

                {depleted.length ?
                    <div data-test="depletedin">
                        <dt>Depleted in</dt>
                        <dd>{depleted.join(', ')}</dd>
                    </div>
                : null}

                {lib.lysis_method ?
                    <div data-test="lysismethod">
                        <dt>Lysis method</dt>
                        <dd>{lib.lysis_method}</dd>
                    </div>
                : null}

                {lib.extraction_method ?
                    <div data-test="extractionmethod">
                        <dt>Extraction method</dt>
                        <dd>{lib.extraction_method}</dd>
                    </div>
                : null}

                {lib.fragmentation_method ?
                    <div data-test="fragmentationmethod">
                        <dt>Fragmentation method</dt>
                        <dd>{lib.fragmentation_method}</dd>
                    </div>
                : null}

                {lib.size_range ?
                    <div data-test="sizerange">
                        <dt>Size range</dt>
                        <dd>{lib.size_range}</dd>
                    </div>
                : null}

                {lib.library_size_selection_method ?
                    <div data-test="sizeselectionmethod">
                        <dt>Size selection method</dt>
                        <dd>{lib.library_size_selection_method}</dd>
                    </div>
                : null}

                {treatments.length ?
                    <div data-test="treatments">
                        <dt>Treatments</dt>
                        <dd>
                            {treatments.join(', ')}
                        </dd>
                    </div>
                : null}

                {platformKeys.length ?
                    <div data-test="platform">
                        <dt>Platform</dt>
                        <dd>
                            {platformKeys.map(function(platformId) {
                                return(
                                    <a className="stacked-link" href={platformId}>{platforms[platformId].title}</a>
                                );
                            })}
                        </dd>
                    </div>
                : null}

                {lib.spikeins_used && lib.spikeins_used.length ?
                    <div data-test="spikeins">
                        <dt>Spike-ins datasets</dt>
                        <dd>
                            {lib.spikeins_used.map(function(dataset, i) {
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
        <div className="panel-replicate" key={props.key}>
            <h3>Biological replicate - {replicate.biological_replicate_number}</h3>
            <dl className="panel key-value">
                <div data-test="techreplicate">
                    <dt>Technical replicate</dt>
                    <dd>{replicate.technical_replicate_number}</dd>
                </div>

                {concentration ?
                    <div data-test="proteinconcentration">
                        <dt>Protein concentration</dt>
                        <dd>{concentration}<span className="unit">{replicate.rbns_protein_concentration_units}</span></dd>
                    </div>
                : null}

                {library ?
                    <div data-test="library">
                        <dt>Library</dt>
                        <dd>{library.accession}</dd>
                    </div>
                : null}

                {library && library.nucleic_acid_starting_quantity ?
                    <div data-test="startingquantity">
                        <dt>Library starting quantity</dt>
                        <dd>{library.nucleic_acid_starting_quantity}<span className="unit">{library.nucleic_acid_starting_quantity_units}</span></dd>
                    </div>
                : null}

                {biosample ?
                    <div data-test="biosample">
                        <dt>Biosample</dt>
                        {biosample ?
                            <dd>
                                <a href={biosample['@id']}>
                                    {biosample.accession}
                                </a>{' '}-{' '}{biosample.biosample_term_name}
                            </dd>
                        : null}
                    </div>
                : null}
            </dl>
        </div>
    );
};
// Can't be a properzz panel as the control must be passed in.
//globals.panel_views.register(Replicate, 'replicate');
// Controls the drawing of the file graph for the experiment. It displays both files and


var assembleGraph = module.exports.assembleGraph = function(context, infoNodeId, files) {

    // Calculate a step ID from a file's derived_from array
    function _derivedFileIds(file) {
        if (file.derived_from) {
            return file.derived_from.map(function(derived) {
                return derived['@id'];
            }).sort().join();
        } else {
            return '';
        }
    }

    function _genQcId(metric, file) {
        return 'qc:' + metric['@id'] + file['@id'];
    }

    function _genFileId(file) {
        return 'file:' + file['@id'];
    }

    function _genStepId(file) {
        return 'step:' + derivedFileIds(file) + file.analysis_step['@id'];
    }

    var jsonGraph; // JSON graph object of entire graph; see graph.js
    var derivedFromFiles = {}; // List of all files that other files derived from
    var allFiles = {}; // All files' accessions as keys
    var allReplicates = {}; // All file's replicates as keys; each key references an array of files
    var allPipelines = {}; // List of all pipelines indexed by step @id
    var allMetricsInfo = []; // List of all QC metrics found attached to files
    var allContributing = {}; // List of all contributing files
    var fileQcMetrics = {}; // List of all file QC metrics indexed by file ID
    var stepExists = false; // True if at least one file has an analysis_step
    var fileOutsideReplicate = false; // True if at least one file exists outside a replicate
    var abortGraph = false; // True if graph shouldn't be drawn
    var abortFileId; // @id of file that caused abort
    var derivedFileIds = _.memoize(_derivedFileIds, function(file) {
        return file['@id'];
    });
    var genQcId = _.memoize(_genQcId, function(metric, file) {
        return metric['@id'] + file['@id'];
    });
    var genStepId = _.memoize(_genStepId, function(file) {
        return file['@id'];
    });
    var genFileId = _.memoize(_genFileId, function(file) {
        return file['@id'];
    });

    // Collect derived_from files, used replicates, and used pipelines
    files.forEach(function(file) {
        // Build an object keyed with all files that other files derive from, and collect QC info if any
        if (file.derived_from) {
            file.derived_from.forEach(function(derived_from) {
                derivedFromFiles[derived_from['@id']] = derived_from;
            });

            // File is derived; collect any QC info that applies to this file
            if (file.step_run && file.step_run.qc_metrics) {
                var matchingQc = [];

                // Search file's step_run's qc_metrics array to find one with an applies_to field referring to this file.
                file.step_run.qc_metrics.forEach(function(metric) {
                    var matchingFile = _(metric.applies_to).find(function(appliesFile) {
                        return file['@id'] === appliesFile;
                    });
                    if (matchingFile) {
                        matchingQc.push(metric);
                    }
                });
                if (matchingQc.length) {
                    fileQcMetrics[file['@id']] = matchingQc;
                }
            }
        }

        // Keep track of all used replicates by keeping track of all file objects for each replicate.
        // Each key is a replicate number, and each references an array of file objects using that replicate.
        if (file.replicate) {
            if (!allReplicates[file.replicate.biological_replicate_number]) {
                // Place a new array in allReplicates if needed
                allReplicates[file.replicate.biological_replicate_number] = [];
            }
            allReplicates[file.replicate.biological_replicate_number].push(file);
        }

        // Track all the pipelines used for each step that's part of a pipeline.
        if (file.pipeline && file.pipeline.analysis_steps) {
            file.pipeline.analysis_steps.forEach(function(step) {
                allPipelines[step] = file.pipeline;
            });
        }

        // Note whether any files have analysis steps.
        stepExists = stepExists || !!file.analysis_step;

        // Build a list of all files in the graph, including contributed files, for convenience
        allFiles[file['@id']] = file;

        // Keep track of whether files exist outside replicates
        fileOutsideReplicate = fileOutsideReplicate || !!file.replicate;
    });
    // At this stage, allFiles and allReplicates points to file objects; allPipelines points to pipelines.
    // derivedFromFiles points to derived_from file objects

    // Don't draw anything if no files have an analysis_step
    if (!stepExists) {
        console.warn('No graph: no files have step runs');
        return null;
    }

    // Now that we know at least some files derive from each other through analysis steps, mark file objects that
    // don't derive from other files — and that no files derive from them — as removed from the graph.
    files.forEach(function(file) {
        file.removed = !(file.derived_from && file.derived_from.length) && !derivedFromFiles[file['@id']];

        // If the file's removed, remember it's removed from the derived_From file objects too
        if (file.removed && derivedFromFiles[file['@id']]) {
            derivedFromFiles[file['@id']].removed = true;
        }
    });

    // Remove any replicates containing only removed files from the last step.
    Object.keys(allReplicates).forEach(function(repNum) {
        var keepRep = false;
        allReplicates[repNum].forEach(function(file) {
            keepRep = keepRep || !file.removed;
        });
        if (!keepRep) {
            allReplicates[repNum] = [];
        }
    });

    // Add contributing files to the allFiles object that other files derive from.
    // Don't worry about files they derive from; they're not included in the graph.
    if (context.contributing_files && context.contributing_files.length) {
        context.contributing_files.forEach(function(file) {
            allContributing[file['@id']] = file;
            if (derivedFromFiles[file['@id']]) {
                allFiles[file['@id']] = file;
            }
        });
    }

    // Check whether any files that others derive from are missing (usually because they're unreleased and we're logged out).
    Object.keys(derivedFromFiles).forEach(function(derivedFromFileId) {
        if (!(derivedFromFileId in allFiles)) {
            // A file others derive from doesn't exist; check if it's in a replicate or not
            // Note the derived_from file object exists even if it doesn't exist in given files array.
            var derivedFromFile = derivedFromFiles[derivedFromFileId];
            if (derivedFromFile.replicate) {
                // Missing derived-from file in a replicate; remove the replicate's files and remove itself.
                if (allReplicates[derivedFromFile.replicate.biological_replicate_number]) {
                    allReplicates[derivedFromFile.replicate.biological_replicate_number].forEach(function(file) {
                        file.removed = true;
                    });
                }

                // Indicate that this replicate is not to be rendered
                allReplicates[derivedFromFile.replicate.biological_replicate_number] = [];
            } else {
                // Missing derived-from file not in a replicate; don't draw any graph
                abortGraph = abortGraph || true;
                abortFileId = derivedFromFileId;
            }
        } // else the derived_from file is in files array; normal case
    });

    // Don't draw anything if a file others derive from outside a replicate doesn't exist
    if (abortGraph) {
        console.warn('No graph: derived_from file outside replicate missing [' + abortFileId + ']');
        return null;
    }

    // Check for other conditions in which to abort graph drawing
    Object.keys(allFiles).forEach(function(fileId) {
        var file = allFiles[fileId];

        // A file derives from a file that's been removed from the graph
        if (file.derived_from && !file.removed && !(file['@id'] in allContributing)) {
            abortGraph = abortGraph || _(file.derived_from).any(function(derivedFromFile) {
                return !(derivedFromFile['@id'] in allFiles);
            });
        }

        // No files exist outside replicates, and all replicates are removed
        abortGraph = abortGraph || (fileOutsideReplicate && _(Object.keys(allReplicates)).all(function(replicateNum) {
            return !allReplicates[replicateNum].length;
        }));

        if (abortGraph) {
            abortFileId = fileId;
        }
    });

    if (abortGraph) {
        console.warn('No graph: other condition [' + abortFileId + ']');
        return null;
    }

    // Create an empty graph architecture that we fill in next.
    jsonGraph = new JsonGraph(context.accession);

    // Create nodes for the replicates
    Object.keys(allReplicates).forEach(function(replicateNum) {
        if (allReplicates[replicateNum] && allReplicates[replicateNum].length) {
            jsonGraph.addNode('rep:' + replicateNum, 'Replicate ' + replicateNum, {
                cssClass: 'pipeline-replicate',
                type: 'rep',
                shape: 'rect',
                cornerRadius: 0
            });
        }
    });

    // Go through each file (released or unreleased) to add it and associated steps to the graph
    files.forEach(function(file) {
        // Only add files derived from others, or that others derive from,
        // and that aren't part of a removed replicate
        if (!file.removed) {
            var stepId;
            var label;
            var pipelineInfo;
            var error;
            var fileId = 'file:' + file['@id'];
            var replicateNode = file.replicate ? jsonGraph.getNode('rep:' + file.replicate.biological_replicate_number) : null;
            var metricsInfo;

            // Add QC metrics info from the file to the list to generate the nodes later
            if (fileQcMetrics[file['@id']] && fileQcMetrics[file['@id']].length && file.analysis_step) {
                metricsInfo = fileQcMetrics[file['@id']].map(function(metric) {
                    var qcId = genQcId(metric, file);
                    return {id: qcId, label: 'QC', class: 'pipeline-node-qc-metric' + (infoNodeId === qcId ? ' active' : ''), ref: metric};
                });
            }

            // Add file to the graph as a node
            jsonGraph.addNode(fileId, file.title + ' (' + file.output_type + ')', {
                cssClass: 'pipeline-node-file' + (infoNodeId === fileId ? ' active' : ''),
                type: 'file',
                shape: 'rect',
                cornerRadius: 16,
                parentNode: replicateNode,
                ref: file
            }, metricsInfo);

            // If the file has an analysis step, prepare it for graph insertion
            if (file.analysis_step) {
                // Make an ID and label for the step
                stepId = 'step:' + derivedFileIds(file) + file.analysis_step['@id'];
                label = file.analysis_step.analysis_step_types;
                pipelineInfo = allPipelines[file.analysis_step['@id']];
                error = false;
            } else if (derivedFileIds(file)) {
                // File derives from others, but no analysis step; make dummy step
                stepId = 'error:' + derivedFileIds(file);
                label = 'Software unknown';
                pipelineInfo = null;
                error = true;
            } else {
                // No analysis step and no derived_from; don't add a step
                stepId = '';
            }

            if (stepId) {
                // Add the step to the graph only if we haven't for this derived-from set already
                if (!jsonGraph.getNode(stepId)) {
                    jsonGraph.addNode(stepId, label, {
                        cssClass: 'pipeline-node-analysis-step' + (infoNodeId === stepId ? ' active' : '') + (error ? ' error' : ''),
                        type: 'step',
                        shape: 'rect',
                        cornerRadius: 4,
                        parentNode: replicateNode,
                        ref: file.analysis_step,
                        pipeline: pipelineInfo,
                        fileId: file['@id']
                    });
                }

                // Connect the file to the step, and the step to the derived_from files
                jsonGraph.addEdge(stepId, fileId);
                file.derived_from.forEach(function(derived) {
                    if (!jsonGraph.getEdge('file:' + derived['@id'], stepId)) {
                        jsonGraph.addEdge('file:' + derived['@id'], stepId);
                    }
                });
            }
        }
    }, this);

    // Add contributing files to the graph
    if (context.contributing_files && context.contributing_files.length) {
        context.contributing_files.forEach(function(file) {
            var fileId = 'file:' + file['@id'];

            // Assemble a single file node; can have file and step nodes in this graph
            jsonGraph.addNode(fileId, file.title + ' (' + file.output_type + ')', {
                cssClass: 'pipeline-node-file contributing' + (infoNodeId === fileId ? ' active' : ''),
                type: 'file',
                shape: 'rect',
                cornerRadius: 16,
                ref: file,
                contributing: true
            });
        }, this);
    }

    return jsonGraph;
};

// analysis steps.
var ExperimentGraph = module.exports.ExperimentGraph = React.createClass({

    getInitialState: function() {
        return {
            infoNodeId: '' // @id of node whose info panel is open
        };
    },

    // Render metadata if a graph node is selected.
    // jsonGraph: JSON graph data.
    // infoNodeId: ID of the selected node
    detailNodes: function(jsonGraph, infoNodeId) {
        var meta;

        // Find data matching selected node, if any
        if (infoNodeId) {
            if (infoNodeId.indexOf('qc:') === -1) {
                // Not a QC subnode; render normally
                var node = jsonGraph.getNode(infoNodeId);
                if (node) {
                    meta = globals.graph_detail.lookup(node)(node);
                }
            } else {
                // QC subnode
                var subnode = jsonGraph.getSubnode(infoNodeId);
                if (subnode) {
                    meta = QcDetailsView(subnode);
                }
            }
        }

        return meta;
    },

    // Handle a click in a graph node
    handleNodeClick: function(nodeId) {
        this.setState({infoNodeId: this.state.infoNodeId !== nodeId ? nodeId : ''});
    },

    render: function() {
        var context = this.props.context;
        var data = this.props.data;
        var items = data ? data['@graph'] : [];
        var files = context.files.concat(items);

        // Build node graph of the files and analysis steps with this experiment
        if (files && files.length) {
            this.jsonGraph = assembleGraph(context, this.state.infoNodeId, files);
            if (this.jsonGraph && Object.keys(this.jsonGraph).length) {
                var meta = this.detailNodes(this.jsonGraph, this.state.infoNodeId);
                return (
                    <div>
                        <h3>Files generated by pipeline</h3>
                        <Graph graph={this.jsonGraph} nodeClickHandler={this.handleNodeClick}>
                            <div id="graph-node-info">
                                {meta ? <div className="panel-insert">{meta}</div> : null}
                            </div>
                        </Graph>
                    </div>
                );
            }
        }
        return null;
    }
});


// Display the metadata of the selected file in the graph
var FileDetailView = function(node) {
    // The node is for a file
    var selectedFile = node.metadata.ref;
    var meta;

    if (selectedFile) {
        var contributingAccession;

        if (node.metadata.contributing) {
            var accessionStart = selectedFile.dataset.indexOf('/', 1) + 1;
            var accessionEnd = selectedFile.dataset.indexOf('/', accessionStart) - accessionStart;
            contributingAccession = selectedFile.dataset.substr(accessionStart, accessionEnd);
        }
        var dateString = !!selectedFile.date_created && moment.utc(selectedFile.date_created).format('YYYY-MM-DD');
        return (
            <dl className="key-value-flex">
                {selectedFile.file_format ?
                    <div data-test="format">
                        <dt>Format</dt>
                        <dd>{selectedFile.file_type}</dd>
                    </div>
                : null}

                {selectedFile.output_type ?
                    <div data-test="output">
                        <dt>Output</dt>
                        <dd>{selectedFile.output_type}</dd>
                    </div>
                : null}

                {selectedFile.paired_end ?
                    <div data-test="pairedend">
                        <dt>Paired end</dt>
                        <dd>{selectedFile.paired_end}</dd>
                    </div>
                : null}

                {selectedFile.replicate ?
                    <div data-test="replicate">
                        <dt>Associated replicates</dt>
                        <dd>{'(' + selectedFile.replicate.biological_replicate_number + ', ' + selectedFile.replicate.technical_replicate_number + ')'}</dd>
                    </div>
                : null}

                {selectedFile.assembly ?
                    <div data-test="assembly">
                        <dt>Mapping assembly</dt>
                        <dd>{selectedFile.assembly}</dd>
                    </div>
                : null}

                {selectedFile.genome_annotation ?
                    <div data-test="annotation">
                        <dt>Genome annotation</dt>
                        <dd>{selectedFile.genome_annotation}</dd>
                    </div>
                : null}

                {selectedFile.lab && selectedFile.lab.title ?
                    <div data-test="submitted">
                        <dt>Lab</dt>
                        <dd>{selectedFile.lab.title}</dd>
                    </div>
                : null}

                {dateString ?
                    <div data-test="datecreated">
                        <dt>Date added</dt>
                        <dd>{dateString}</dd>
                    </div>
                : null}

                {selectedFile.step_run ?
                    <div>
                        <dt>Software</dt>
                        <dd>
                            {selectedFile.analysis_step.software_versions.map(function(version, i) {
                                var versionNum = version.version === 'unknown' ? 'version unknown' : version.version;
                                return (
                                    <a href={version.software['@id']} key={i} className="software-version">
                                        <span className="software">{version.software.name}</span>
                                        {version.version ?
                                            <span className="version">{versionNum}</span>
                                        : null}
                                    </a>
                                );
                            })}
                        </dd>
                    </div>
                : null}

                {node.metadata.contributing && selectedFile.dataset ?
                    <div>
                        <dt>Contributed from</dt>
                        <dd><a href={selectedFile.dataset}>{contributingAccession}</a></dd>
                    </div>
                : null}

                {selectedFile.href ?
                    <div data-test="download">
                        <dt>File download</dt>
                        <dd>
                            <a href={selectedFile.href} download={selectedFile.href.substr(selectedFile.href.lastIndexOf("/") + 1)} data-bypass="true"><i className="icon icon-download"></i>
                                &nbsp;Download
                            </a>
                        </dd>
                    </div>
                : null}
            </dl>
        );
    } else {
        return null;
    }
};

globals.graph_detail.register(FileDetailView, 'file');


var QcDetailsView = function(metrics) {
    var reserved = ['uuid', 'assay_term_name', 'level', 'status', 'date_created', 'step_run', 'schema_version'];

    if (metrics) {
        return (
            <dl className="key-value-flex">
                {Object.keys(metrics.ref).map(function(key) {
                    if ((typeof metrics.ref[key] === 'string' || typeof metrics.ref[key] === 'number') && key[0] !== '@' && reserved.indexOf(key) === -1) {
                        return(
                            <div>
                                <dt>{key}</dt>
                                <dd>{metrics.ref[key]}</dd>
                            </div>
                        );
                    }
                    return null;
                })}
            </dl>
        );
    } else {
        return null;
    }
};
