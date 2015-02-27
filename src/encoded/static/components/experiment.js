   /** @jsx React.DOM */
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
        var mutatedGenes = [];
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

            // Collect mutated genes
            if (biosample.donor && biosample.donor.mutated_gene) {
                mutatedGenes.push(biosample.donor.mutated_gene.label);
            }
        });
        if (treatmentText) {
            treatmentText = _.uniq(treatmentText);
        }
        if (synchText) {
            synchText = _.uniq(synchText);
        }
        if (mutatedGenes) {
            mutatedGenes = _.uniq(mutatedGenes);
        }

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
                            <AuditIndicators audits={context.audit} key="experiment-audit" />
                        </div>
                   </div>
                </header>
                <AuditDetail audits={context.audit} key="experiment-audit" />
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
                                    {mutatedGenes.length ? <span>{', mutated gene: ' + mutatedGenes.join('/')}</span> : null}
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
                                            return (<li>{treatment}</li>);
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
                                    return (<span>{i !== 0 ? ', ' : ''}<a href={antibody}>{antibodies[antibody].accession}</a></span>);
                                })}</dd>
                            </div>
                        : null}

                        {context.possible_controls.length ?
                            <div data-test="possible-controls">
                                <dt>Controls</dt>
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

                        {context.references.length ?
                            <div data-test="references">
                                <dt>References</dt>
                                <dd><DbxrefList values={context.references} className="horizontal-list"/></dd>
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

                <AssayDetails context={context} replicates={replicates} />

                {Object.keys(documents).length ?
                    <div data-test="protocols">
                        <h3>Documents</h3>
                        <div className="row multi-columns-row">
                            {documents}
                        </div>
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

                {{'released': 1, 'release ready': 1}[context.status] ? this.transferPropsTo(
                    <FetchedItems url={dataset.unreleased_files_url(context)} Component={UnreleasedFiles} />
                ): null}

            </div>
        );
    }
});

globals.content_views.register(Experiment, 'experiment');


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

    // If no platforms found in files, get the platform from the first replicate, if it has one
    if (Object.keys(platforms).length === 0 && replicates[0].platform) {
        platforms[replicates[0].platform['@id']] = replicates[0].platform;
    }

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

                {Object.keys(platforms).length ?
                    <div data-test="platform">
                        <dt>Platform</dt>
                        <dd>
                            {Object.keys(platforms).map(function(platformId) {
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
        <div key={props.key} className="panel-replicate">
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

                {replicate.read_length ?
                    <div data-test="runtype">
                        <dt>Run type</dt>
                        <dd>{paired_end ? 'paired-end' : 'single-end'}</dd>
                    </div>
                : null}

                {replicate.read_length ?
                    <div data-test="readlength">
                        <dt>Read length</dt>
                        <dd>{replicate.read_length}<span className="unit">{replicate.read_length_units}</span></dd>
                    </div>
                : null}
            </dl>
        </div>
    );
};
// Can't be a proper panel as the control must be passed in.
//globals.panel_views.register(Replicate, 'replicate');



var ExperimentGraph = module.exports.ExperimentGraph = React.createClass({
    // Create nodes based on all files in this experiment
    assembleGraph: function(context, infoNodeId, files) {
        var jsonGraph;

        // Track orphans -- files with no derived_from and no one derives_from them.
        var usedFiles = {}; // Object with file ID keys of all files that belong in graph
        files.forEach(function(file) {
            usedFiles[file['@id']] = usedFiles[file['@id']] ||
                (!!(file.derived_from && file.derived_from.length)); // File included if it's derived from others
            if (file.derived_from && file.derived_from.length) {
                file.derived_from.forEach(function(derived) {
                    usedFiles[derived['@id']] = true; // File included if others derive from it.
                });
            }
        });

        // Only produce a graph if there's at least one file with an analysis step
        // and the file has derived from other files.
        if (files && files.some(function(file) {
            return usedFiles[file['@id']] && file.step_run;
        })) {
            // Create an empty graph architecture
            jsonGraph = new JsonGraph(context.accession);

            // Create nodes for the replicates
            context.replicates.forEach(function(replicate) {
                jsonGraph.addNode(replicate.biological_replicate_number, 'Replicate ' + replicate.biological_replicate_number,
                    {cssClass: 'pipeline-replicate', type: 'rp', shape: 'rect', cornerRadius: 0, ref: replicate});
            });

            // Add files and their steps as nodes to the graph
            files.forEach(function(file) {
                var fileId = file['@id'];
                if (usedFiles[fileId]) {
                    var replicateNode = file.replicate ? jsonGraph.getNode(file.replicate.biological_replicate_number) : null;

                    // Assemble a single file node; can have file and step nodes in this graph, so use 'fi' type
                    // to show that this is a file node.
                    jsonGraph.addNode(fileId, file.accession + ' (' + file.output_type + ')',
                        {cssClass: 'pipeline-node-file' + (this.state.infoNodeId === fileId ? ' active' : ''),
                         type: 'fi', shape: 'rect', cornerRadius: 16, parentNode: replicateNode, ref: file});

                    // If the node has parents, build the edges to the analysis step between this node and its parents
                    if (file.derived_from && file.derived_from.length) {
                        var stepRun = file.step_run;
                        var stepId;

                        // If has derived_from but no step_run, make a dummy step to show error.
                        if (!stepRun) {
                            stepRun = {
                                error: true,
                                analysis_step: {'@id': 'ERROR:' + file.accession, analysis_step_types: 'Error in ' + file.accession}
                            };
                        }

                        // Make a label for the step node
                        var label = stepRun.analysis_step.analysis_step_types;

                        // Virtual step runs need to be duplicated on the graph
                        if (stepRun.status === 'virtual') {
                            // Make the ID of the node using the analysis step ID, and the ID of the file it connects to.
                            // Need to combine these so that duplicated steps have unique IDs.
                            stepId = stepRun.analysis_step['@id'] + '&' + file['@id'];

                            // Insert a node for the analysis step, with an ID combining the IDs of this step and the file that
                            // points to it; there may be more than one copy of this step on the graph if more than one
                            // file points to it, so we have to uniquely ID each analysis step copy with the file's ID.
                            // 'as' type identifies these as analysis step nodes. Also add an edge from the file to the
                            // analysis step.
                            jsonGraph.addNode(stepId, label,
                                {cssClass: 'pipeline-node-analysis-step' + (infoNodeId === stepId ? ' active' : ''),
                                 type: 'as', shape: 'rect', cornerRadius: 4, parentNode: replicateNode, ref: stepRun});
                            jsonGraph.addEdge(stepId, fileId);
                        } else {
                            stepId = stepRun.analysis_step['@id'];

                            // Add the step only if we haven't added it yet.
                            if (!jsonGraph.getNode(stepId)) {
                                jsonGraph.addNode(stepId, label,
                                    {cssClass: 'pipeline-node-analysis-step' + (infoNodeId === stepId ? ' active' : '') + (stepRun.error ? ' error' : ''),
                                     type: 'as', shape: 'rect', cornerRadius: 4, parentNode: replicateNode, accession: file.accession, error: stepRun.error, ref: stepRun});
                            }

                            // Now hook the file to the step
                            jsonGraph.addEdge(stepId, fileId);
                        }

                        // Draw an edge from the analysis step to each of the derived_from files
                        file.derived_from.forEach(function(derived) {
                            jsonGraph.addEdge(derived['@id'], stepId);
                        });
                    }
                }
            }, this);

            // Add contributing files to the graph
            context.contributing_files.forEach(function(file) {
                var fileId = file['@id'];

                // Assemble a single file node; can have file and step nodes in this graph, so use 'fi' type
                // to show that this is a file node.
                if (!jsonGraph.getNode(fileId)) {
                    jsonGraph.addNode(fileId, file.accession + ' (' + file.output_type + ')',
                        {cssClass: 'pipeline-node-file contributing' + (infoNodeId === fileId ? ' active' : ''),
                         type: 'fi', shape: 'rect', cornerRadius: 16, ref: file, contributing: true});
                }
            }, this);
        }
        return jsonGraph;
    },

    getInitialState: function() {
        return {
            infoNodeId: '' // @id of node whose info panel is open
        };
    },

    detailNodes: function(jsonGraph, infoNodeId) {
        var meta;
        var selectedFile;

        // Find data matching selected node, if any
        if (infoNodeId) {
            var node = jsonGraph.getNode(infoNodeId);
            if (node) {
                switch(node.type) {
                    case 'fi':
                        // The node is for a file
                        selectedFile = node.metadata.ref;

                        if (selectedFile) {
                            var contributingAccession;

                            if (node.metadata.contributing) {
                                var accessionStart = selectedFile.dataset.indexOf('/', 1) + 1;
                                var accessionEnd = selectedFile.dataset.indexOf('/', accessionStart) - accessionStart;
                                contributingAccession = selectedFile.dataset.substr(accessionStart, accessionEnd);
                            }
                            var dateString = !!selectedFile.date_created && moment(selectedFile.date_created).format('YYYY-MM-DD');
                            meta = (
                                <dl className="key-value">
                                    {selectedFile.file_format ?
                                        <div data-test="format">
                                            <dt>Format</dt>
                                            <dd>{selectedFile.file_format}</dd>
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

                                    {selectedFile.submitted_by && selectedFile.submitted_by.title ?
                                        <div data-test="submitted">
                                            <dt>Added by</dt>
                                            <dd>{selectedFile.submitted_by.title}</dd>
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
                                                {selectedFile.step_run.analysis_step.software_versions.map(function(version, i) {
                                                    var versionNum = version.version === 'unknown' ? 'version unknown' : version.version;
                                                    return (
                                                        <a href={version.software['@id']} className="software-version">
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
                                            <dd>
                                                <a href={selectedFile.dataset}>{contributingAccession}</a>
                                            </dd>
                                        </div>
                                    : null}

                                   {selectedFile.pipeline ?
                                        <div data-test="pipeline">
                                            <dt>Pipeline</dt>
                                            <dd>{selectedFile.pipeline.title}</dd>
                                        </div>
                                   : null}
                                </dl>
                            );
                        }

                        break;

                    case 'as':
                        // The node is for an analysis step
                        if (node.metadata.error) {
                            meta = (<p className="browser-error">Missing step_run derivation information for {node.metadata.accession}</p>);
                        } else {
                            var step = node.metadata.ref.analysis_step;
                            meta = (
                                <div>
                                    <dl className="key-value">
                                        <div data-test="steptype">
                                            <dt>Step type</dt>
                                            <dd>{step.analysis_step_types.join(', ')}</dd>
                                        </div>

                                        {step.input_file_types && step.input_file_types.length ?
                                            <div data-test="inputtypes">
                                                <dt>Input file types</dt>
                                                <dd>{step.input_file_types.join(', ')}</dd>
                                            </div>
                                        : null}

                                        {step.output_file_types && step.output_file_types.length ?
                                            <div data-test="outputtypes">
                                                <dt>Output file types</dt>
                                                <dd>{step.output_file_types.join(', ')}</dd>
                                            </div>
                                        : null}

                                        {step.qa_stats_generated && step.qa_stats_generated.length ?
                                            <div data-test="steptypes">
                                                <dt>QA statistics</dt>
                                                <dd>{step.qa_stats_generated.join(', ')}</dd>
                                            </div>
                                        : null}

                                        {step.software_versions && step.software_versions.length ?
                                            <div>
                                                <dt>Software</dt>
                                                <dd>
                                                    {step.software_versions.map(function(version) {
                                                        var versionNum = version.version === 'unknown' ? 'version unknown' : version.version;
                                                        return (
                                                            <a href={version.software['@id']} className="software-version">
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
                                    </dl>
                                </div>
                            );
                        }


                        break;

                    default:
                        break;
                }
            }
        }

        return meta;
    },

    handleNodeClick: function(e, nodeId) {
        e.stopPropagation(); e.preventDefault();
        this.setState({infoNodeId: this.state.infoNodeId !== nodeId ? nodeId : ''});
    },

    render: function() {
        var context = this.props.context;
        var data = this.props.data;
        var items = data ? data['@graph'] : [];
        var files = context.files.concat(items);

        // Build node graph of the files and analysis steps with this experiment
        this.jsonGraph = this.assembleGraph(context, this.state.infoNodeId, files);
        if (this.jsonGraph && Object.keys(this.jsonGraph).length) {
            var meta = this.detailNodes(this.jsonGraph, this.state.infoNodeId);
            return (
                <div>
                    <h3>{this.props.files ? 'Unreleased files' : 'Files'} generated by pipeline</h3>
                    <Graph graph={this.jsonGraph} nodeClickHandler={this.handleNodeClick}>
                        <div id="graph-node-info">
                            {meta ? <div className="panel-insert">{meta}</div> : null}
                        </div>
                    </Graph>
                </div>
            );
        } else {
            return null;
        }
    }
});
