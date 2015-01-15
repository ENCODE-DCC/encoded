/** @jsx React.DOM */
'use strict';
var React = require('react');
var _ = require('underscore');
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

    loaded: function() {
        console.log('loaded');
    },

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

        // Build the text of the Treatment string array and the synchronization string array
        var treatmentText = [];
        var synchText = [];
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
        });
        if (treatmentText) {
            treatmentText = _.uniq(treatmentText);
        }
        if (synchText) {
            synchText = _.uniq(synchText);
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

                {context.files.length ?
                    <div>
                        <h3>Files linked to {context.accession}</h3>
                        <FileTable items={context.files} encodevers={encodevers} />
                    </div>
                : null }

                {{'released': 1, 'release ready': 1}[context.status] ? this.transferPropsTo(
                    <FetchedItems url={dataset.unreleased_files_url(context)} Component={UnreleasedFiles} loadingComplete={this.loaded} />
                ): null}

                <ExperimentGraph context={context} />

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


var ExperimentGraph = React.createClass({
    // Create nodes based on all files in this experiment
    assembleGraph: function() {
        var context = this.props.context;
        var jsonGraph;

        // Only produce a graph if there's at least one file with an analysis step
        // and the file has derived from other files.
        if (this.props.context.files && this.props.context.files.some(function(file) {
            return file.derived_from && file.derived_from.length && file.step;
        })) {
            // Create an empty graph architecture
            jsonGraph = new JsonGraph('');

            // Create nodes for the replicates
            context.replicates.forEach(function(replicate) {
                jsonGraph.addNode(replicate.biological_replicate_number, replicate.biological_replicate_number, 'pipeline-replicate', 'rp');
            });

            // Add files and their steps as nodes to the graph
            context.files.forEach(function(file) {
                var fileId = file['@id'];
                var replicateNode = file.replicate ? jsonGraph.getNode(file.replicate.biological_replicate_number) : null;

                // Assemble a single file node; can have file and step nodes in this graph, so use 'fi' type
                // to show that this is a file node.
                jsonGraph.addNode(fileId, file.accession + ' (' + file.output_type + ')',
                    'pipeline-node-file' + (this.state.infoNodeId === fileId ? ' active' : ''), 'fi', replicateNode);

                // If the node has parents, build the edges to the analysis step between this node and its parents
                if (file.derived_from && file.derived_from.length && file.step) {
                    var step = file.step.analysis_step;
                    var stepId = step['@id'] + '&' + file['@id'];

                    // Insert a node for the analysis step, with an ID combining the IDs of this step and the file that
                    // points to it; there may be more than one copy of this step on the graph if more than one
                    // file points to it, so we have to uniquely ID each analysis step copy with the file's ID.
                    // 'as' type identifies these as analysis step nodes. Also add an edge from the file to the
                    // analysis step.
                    jsonGraph.addNode(stepId, step.analysis_step_types.join(', '),
                        'pipeline-node-analysis-step' + (this.state.infoNodeId === stepId ? ' active' : ''), 'as', replicateNode);
                    jsonGraph.addEdge(stepId, fileId);

                    // Draw an edge from the analysis step to each of the derived_from files
                    file.derived_from.forEach(function(derived) {
                        jsonGraph.addEdge(derived, stepId);
                    });
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
            if (!node) console.log('node: ' + node + ', INI: ' + infoNodeId);
            if (node) {
                switch(node.type) {
                    case 'fi':
                        // The node is for a file
                        selectedFile = _(this.props.context.files).find(function(file) {
                            return file['@id'] === infoNodeId;
                        });

                        if (selectedFile) {
                            var analysisStep = selectedFile.step && selectedFile.step.analysis_step;
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

                                    {selectedFile.submitted_by && selectedFile.submitted_by.title ?
                                        <div data-test="submitted">
                                            <dt>Added by</dt>
                                            <dd>{selectedFile.submitted_by.title}</dd>
                                        </div>
                                    : null}

                                    {selectedFile.date_created ?
                                        <div data-test="datecreated">
                                            <dt>Date added</dt>
                                            <dd>{selectedFile.date_created}</dd>
                                        </div>
                                    : null}

                                    {analysisStep && analysisStep.software_versions && analysisStep.software_versions.length ?
                                        <div>
                                            <dt>Software</dt>
                                            <dd>
                                                {<ul>
                                                    {analysisStep.software_versions.map(function(version, i) {
                                                        return (
                                                            <span>
                                                                {i > 0 ? ', ' : ''}
                                                                <a href={version.software['@id']}>{version.software.name}</a>
                                                            </span>
                                                        );
                                                    })}
                                                </ul>}
                                            </dd>
                                        </div>
                                    : null}

                                    {selectedFile.pipeline ?
                                        <div data-test="pipeline">
                                            <dt>Pipeline</dt>
                                            <dd><a href={selectedFile.pipeline['@id']}>{selectedFile.pipeline.title}</a></dd>
                                        </div>
                                    : null}
                                </dl>
                            );
                        }

                        break;

                    case 'as':
                        // The node is for an analysis step
                        var analysisStepId = node.id.slice(0, node.id.indexOf('&'));
                        selectedFile = _(this.props.context.files).find(function(file) {
                            return file.step && file.step.analysis_step['@id'] === analysisStepId;
                        });

                        if (selectedFile) {
                            var selectedStep = selectedFile.step.analysis_step;

                            meta = (
                                <dl className="key-value">
                                    {selectedStep.input_file_types && selectedStep.input_file_types.length ?
                                        <div data-test="inputtypes">
                                            <dt>Input file types</dt>
                                            <dd>{selectedStep.input_file_types.join(', ')}</dd>
                                        </div>
                                    : null}

                                    {selectedStep.output_file_types && selectedStep.output_file_types.length ?
                                        <div data-test="outputtypes">
                                            <dt>Output file types</dt>
                                            <dd>{selectedStep.output_file_types.join(', ')}</dd>
                                        </div>
                                    : null}

                                    {selectedStep.qa_stats_generated && selectedStep.qa_stats_generated.length ?
                                        <div data-test="steptypes">
                                            <dt>QA statistics</dt>
                                            <dd>{selectedStep.qa_stats_generated.join(', ')}</dd>
                                        </div>
                                    : null}

                                    {selectedStep.software_versions && selectedStep.software_versions.length ?
                                        <div>
                                            <dt>Software</dt>
                                            <dd>
                                                {<ul>
                                                    {selectedStep.software_versions.map(function(version, i) {
                                                        return (
                                                            <span>
                                                                {i > 0 ? ', ' : ''}
                                                                <a href={version.software['@id']}>{version.software.name}</a>
                                                            </span>
                                                        );
                                                    })}
                                                </ul>}
                                            </dd>
                                        </div>
                                    : null}
                                </dl>
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

        // Build node graph of the files and analysis steps with this experiment
        var jsonGraph = this.assembleGraph();
        if (jsonGraph) {
            var meta = this.detailNodes(jsonGraph, this.state.infoNodeId);
            return (
                <div>
                    <h3>Pipeline for {context.accession}</h3>
                    <Graph graph={jsonGraph} nodeClickHandler={this.handleNodeClick}>
                        <div className="graph-node-info">
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
