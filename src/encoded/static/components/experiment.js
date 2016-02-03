'use strict';
var React = require('react');
var panel = require('../libs/bootstrap/panel');
var _ = require('underscore');
var moment = require('moment');
var graph = require('./graph');
var navbar = require('./navbar');
var globals = require('./globals');
var dbxref = require('./dbxref');
var dataset = require('./dataset');
var image = require('./image');
var statuslabel = require('./statuslabel');
var audit = require('./audit');
var fetched = require('./fetched');
var AuditMixin = audit.AuditMixin;
var pipeline = require('./pipeline');
var reference = require('./reference');
var software = require('./software');
var sortTable = require('./sorttable');
var objectutils = require('./objectutils');

var Breadcrumbs = navbar.Breadcrumbs;
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
var SingleTreatment = objectutils.SingleTreatment;
var SoftwareVersionList = software.SoftwareVersionList;
var ProjectBadge = image.ProjectBadge;
var SortTable = sortTable.SortTable;
var {Panel, PanelBody, PanelHeading} = panel;


var anisogenicValues = [
    'anisogenic, sex-matched and age-matched',
    'anisogenic, age-matched',
    'anisogenic, sex-matched',
    'anisogenic'
];


var PanelLookup = function (props) {
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

    contextTypes: {
        session: React.PropTypes.object
    },

    replicateColumns: {
        'biological_replicate_number': {title: 'Biological replicate'},
        'technical_replicate_number': {title: 'Technical replicate'},
        'summary': {
            title: 'Summary',
            getValue: function(replicate) {
                return (replicate.library && replicate.library.biosample) ? replicate.library.biosample.summary : null;
            }
        },
        'biosample_accession': {
            title: 'Biosample',
            getValue: replicate => { return (replicate.library && replicate.library.biosample) ? replicate.library.biosample.accession : null; }
        },
        'antibody': {
            title: 'Antibody',
            getValue: function(replicate) {
                return replicate.antibody ? replicate.antibody.accession : '';
            }
        },
        'library': {
            title: 'Library',
            getValue: function(replicate) {
                return replicate.library ? replicate.library.accession : '';
            }
        }
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
                documents[doc['@id']] = PanelLookup({context: doc, key: i + 1});
            });
        });

        // Get the first replicate's library for items needing one library
        var lib = (replicates && replicates.length) ? replicates[0].library : null;
        var libraries = _.compact(replicates.map(replicate => {
            return replicate.library ? replicate.library : null;
        }));

        // Make array of all replicate biosamples, not including biosample-less replicates.
        var biosamples = _.compact(replicates.map(function(replicate) {
            return replicate.library && replicate.library.biosample;
        }));

        // Build the text of the Treatment, synchronization, and mutatedGene string arrays
        var treatments;
        var synchText = [];
        biosamples.map(function(biosample) {
            // Collect treatments
            treatments = treatments || !!(biosample.treatments && biosample.treatments.length);

            // Collect synchronizations
            if (biosample.synchronization) {
                synchText.push(biosample.synchronization +
                    (biosample.post_synchronization_time ?
                        ' + ' + biosample.post_synchronization_time + (biosample.post_synchronization_time_units ? ' ' + biosample.post_synchronization_time_units : '')
                    : ''));
            }
        });
        synchText = synchText && _.uniq(synchText);

        // Generate biosample summaries
        var fullSummaries = biosampleSummaries(biosamples);

        // Adding experiment specific documents
        context.documents.forEach(function (document, i) {
            documents[document['@id']] = PanelLookup({context: document, key: i + 1});
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

        // Determine whether the experiment is isogenic or anisogenic. No replication_type indicates isogenic.
        var anisogenic = context.replication_type ? (anisogenicValues.indexOf(context.replication_type) !== -1) : false;

        // Get a list of related datasets, possibly filtering on their status
        var seriesList = [];
        var loggedIn = this.context.session && this.context.session['auth.userid'];
        if (context.related_series && context.related_series.length) {
            seriesList = _(context.related_series).filter(dataset => {
                return loggedIn || dataset.status === 'released';
            });
        }

        // Set up the breadcrumbs
        var assayTerm = context.assay_term_name ? 'assay_term_name' : 'assay_term_id';
        var assayName = context[assayTerm];
        var assayQuery = assayTerm + '=' + assayName;
        var organismNames = _.chain(biosamples.map(function(biosample) {
            return biosample.donor ? biosample.donor.organism.scientific_name : '';
        })).compact().uniq().value();
        var nameQuery = '';
        var nameTip = '';
        var names = organismNames.map(function(organismName, i) {
            nameTip += (nameTip.length ? ' + ' : '') + organismName;
            nameQuery += (nameQuery.length ? '&' : '') + 'replicates.library.biosample.donor.organism.scientific_name=' + organismName;
            return <span key={i}>{i > 0 ? <span> + </span> : null}<i>{organismName}</i></span>;
        });
        var biosampleTermName = context.biosample_term_name;
        var biosampleTermQuery = biosampleTermName ? 'biosample_term_name=' + biosampleTermName : '';
        var crumbs = [
            {id: 'Experiments'},
            {id: assayName, query: assayQuery, tip: assayName},
            {id: names.length ? names : null, query: nameQuery, tip: nameTip},
            {id: biosampleTermName, query: biosampleTermQuery, tip: biosampleTermName}
        ];

        var experiments_url = '/search/?type=experiment&possible_controls.accession=' + context.accession;

        // Make a list of reference links, if any
        var references = PubReferenceList(context.references);

        // XXX This makes no sense.
        //var control = context.possible_controls[0];
        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs root='/search/?type=experiment' crumbs={crumbs} />
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
                <Panel addClasses="data-display">
                    <PanelBody>
                        <div className="flexrow">
                            <div className="flexcol-sm-6">
                                <dl className="key-value">
                                    <div data-test="assay">
                                        <dt>Assay</dt>
                                        <dd>{context.assay_term_name}</dd>
                                    </div>

                                    {AssayDetails(context)}

                                    {biosamples.length || context.biosample_term_name ?
                                        <div data-test="biosample-summary">
                                            <dt>Biosample summary</dt>
                                            <dd>{context.biosample_term_name ? <span>{context.biosample_term_name}{' '}{fullSummaries}</span> : <span>{fullSummaries}</span>}</dd>
                                        </div>
                                    : null}

                                    {context.biosample_type ?
                                        <div data-test="biosample-type">
                                            <dt>Type</dt>
                                            <dd>{context.biosample_type}</dd>
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
                                </dl>
                            </div>

                            <div className="flexcol-sm-6">
                                <dl className="key-value">
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

                                    {references ?
                                        <div data-test="references">
                                            <dt>References</dt>
                                            <dd>{references}</dd>
                                        </div>
                                    : null}

                                    {context.aliases.length ?
                                        <div data-test="aliases">
                                            <dt>Aliases</dt>
                                            <dd>{aliasList}</dd>
                                        </div>
                                    : null}

                                    {context.date_released ?
                                        <div data-test="date-released">
                                            <dt>Date released</dt>
                                            <dd>{context.date_released}</dd>
                                        </div>
                                    : null}

                                    {seriesList.length ?
                                        <div data-test="relatedseries">
                                            <dt>Related datasets</dt>
                                            <dd><RelatedSeriesList seriesList={seriesList} /></dd>
                                        </div>
                                    : null}
                                </dl>
                                <ProjectBadge award={context.award} center />
                            </div>
                        </div>
                    </PanelBody>

                    {replicates && replicates.length ?
                        <SortTable title="Replicates" list={replicates} columns={this.replicateColumns} />
                    : null}
                </Panel>


                {Object.keys(documents).length ?
                    <div data-test="protocols">
                        <h3>Documents</h3>
                        <div className="row multi-columns-row">
                            {documents}
                        </div>
                    </div>
                : null}

                {context.visualize_ucsc  && context.status == "released" ?
                    <span className="pull-right">
                        <a data-bypass="true" target="_blank" private-browsing="true" className="btn btn-info btn-sm" href={context['visualize_ucsc']}>Visualize Data</a>
                    </span>
                : null }

                <FetchedData>
                    <Param name="data" url={dataset.unreleased_files_url(context)} />
                    <ExperimentGraph context={context} />
                </FetchedData>

                {context.files.length ?
                    <div>
                        <h3>Files linked to {context.accession}</h3>
                        <FileTable items={context.files} encodevers={encodevers} anisogenic={anisogenic} />
                    </div>
                : null }

                {{'released': 1, 'release ready': 1}[context.status] ?
                    <FetchedItems {...this.props} url={dataset.unreleased_files_url(context)} Component={UnreleasedFiles} anisogenic={anisogenic} />
                : null}

                <FetchedItems {...this.props} url={experiments_url} Component={ControllingExperiments} />
            </div>
        );
    }
});

globals.content_views.register(Experiment, 'Experiment');


var ControllingExperiments = React.createClass({
    render: function () {
        var context = this.props.context;

        return (
            <div>
                <ExperimentTable {...this.props}
                    items={this.props.items} limit={5} url={this.props.url}
                    title={'Experiments with ' + context.accession + ' as a control:'} />
            </div>
        );
    }
});


// Return an array of React components to render into the enclosing panel, given the experiment object in the context parameter
var AssayDetails = module.exports.AssayDetails = function (context) {

    // Little utility to convert a replicate to a unique index we can use for arrays (like libraryValues below)
    function replicateToIndex(replicate) {
        return replicate.biological_replicate_number + '-' + replicate.technical_replicate_number;
    }

    // No replicates, so no assay entries
    if (!context.replicates.length) {
        return [];
    }

    // Sort the replicates first by biological replicate number, then by technical replicate number
    var replicates = context.replicates.sort(function(a, b) {
        if (b.biological_replicate_number === a.biological_replicate_number) {
            return a.technical_replicate_number - b.technical_replicate_number;
        }
        return a.biological_replicate_number - b.biological_replicate_number;
    });

    // Prepare to collect values from each replicate's library. Each key in this object refers to a property in the libraries.
    var libraryValues = {
        nucleic_acid_term_name:         {values: {}, value: undefined, component: {}, title: 'Nucleic acid type',         test: 'nucleicacid'},
        size_range:                     {values: {}, value: undefined, component: {}, title: 'Size range',                test: 'sizerange'},
        nucleic_acid_starting_quantity: {values: {}, value: undefined, component: {}, title: 'Library starting quantity', test: 'startingquantity'},
        depleted_in_term_name:          {values: {}, value: undefined, component: {}, title: 'Depleted in',               test: 'depletedin'},
        lysis_method:                   {values: {}, value: undefined, component: {}, title: 'Lysis method',              test: 'lysismethod'},
        extraction_method:              {values: {}, value: undefined, component: {}, title: 'Extraction method',         test: 'extractionmethod'},
        fragmentation_method:           {values: {}, value: undefined, component: {}, title: 'Fragmentation method',      test: 'fragmentationmethod'},
        library_size_selection_method:  {values: {}, value: undefined, component: {}, title: 'Size selection method',     test: 'sizeselectionmethod'},
        treatments:                     {values: {}, value: undefined, component: {}, title: 'Treatments',                test: 'treatments'},
        spikeins_used:                  {values: {}, value: undefined, component: {}, title: 'Spike-ins datasets',        test: 'spikeins'}
    };

    // For any library properties that aren't simple values, put functions to process them into simple values in this object,
    // keyed by their library property name. Returned JS undefined if no complex value exists so that we can reliably test it
    // momentarily. We have a couple properties too complex even for this, so they'll get added separately at the end.
    var librarySpecials = {
        nucleic_acid_starting_quantity: function(library) {
            var quantity = library.nucleic_acid_starting_quantity;
            if (quantity) {
                return quantity + library.nucleic_acid_starting_quantity_units;
            }
            return undefined;
        },
        depleted_in_term_name: function(library) {
            var terms = library.depleted_in_term_name;
            if (terms && terms.length) {
                return terms.sort().join(', ');
            }
            return undefined;
        },
        treatments: function(library) {
            var treatments = library.treatments;
            if (treatments && treatments.length) {
                return treatments.map(treatment => treatment.treatment_term_name).sort().join(', ');
            }
            return undefined;
        },
        spikeins_used: function(library) {
            var spikeins = library.spikeins_used;

            // Just track @id for deciding if all values are the same or not. Rendering handled in libraryComponents
            if (spikeins && spikeins.length) {
                return spikeins.map(spikein => spikein.accession).sort().join();
            }
            return undefined;
        }
    };

    var libraryComponents = {
        nucleic_acid_starting_quantity: function(library) {
            if (library.nucleic_acid_starting_quantity && library.nucleic_acid_starting_quantity_units) {
                return <span>{library.nucleic_acid_starting_quantity}<span className="unit">{library.nucleic_acid_starting_quantity_units}</span></span>;
            }
            return null;
        },
        spikeins_used: function(library) {
            var spikeins = library.spikeins_used;
            if (spikeins && spikeins.length) {
                return (
                    <span>
                        {spikeins.map(function(dataset, i) {
                            return (
                                <span key={dataset.uuid}>
                                    {i > 0 ? ', ' : ''}
                                    <a href={dataset['@id']}>{dataset.accession}</a>
                                </span>
                            );
                        })}
                    </span>
                );
            }
            return null;
        }
    }

    // Collect library values to display from each replicate. Each key holds an array of values from each replicate's library,
    // indexed by the replicate's biological replicate number. After this loop runs, libraryValues.values should all be filled
    // with objects keyed by <bio rep num>-<tech rep num> and have the corresponding value or undefined if no value exists
    // for that key. The 'value' properties of each object in libraryValues will all be undefined after this loop runs.
    replicates.forEach(replicate => {
        var library = replicate.library;
        var replicateIndex = replicateToIndex(replicate);

        if (library) {
            // Handle "normal" library properties
            Object.keys(libraryValues).forEach(key => {
                var libraryValue;

                // For specific library properties, preprocess non-simple values into simple ones using librarySpecials
                if (librarySpecials[key]) {
                    // Preprocess complex values into simple ones
                    libraryValue = librarySpecials[key](library);
                } else {
                    // Simple value -- just copy it if it exists (copy undefined if it doesn't)
                    libraryValue = library[key];
                }

                // If library property exists, add it to the values we're collecting, keyed by the biological replicate number.
                // We'll prune it after this replicate loop.
                libraryValues[key].values[replicateIndex] = libraryValue;
            });
        }
    });

    // Each property of libraryValues now has every value found in every existing library property in every replicate.
    // Now for each library value in libraryValues, set the 'value' property if all values in the 'values' object are
    // identical and existing. Otherwise, keep 'value' set to undefined.
    var firstBiologicalReplicate = replicateToIndex(replicates[0]);
    Object.keys(libraryValues).forEach(key => {
        // Get the first key's value to compare against the others.
        var firstValue = libraryValues[key].values[firstBiologicalReplicate];

        // See if all values in the values array are identical. Treat 'undefined' as a value
        if (_(Object.keys(libraryValues[key].values)).all(replicateId => {
            var value = libraryValues[key].values[replicateId];
            return value === firstValue;
        })) {
            // All values for the library value are the same. Set the 'value' field with that value.
            libraryValues[key].value = firstValue;

            // If the resulting value is undefined, then all values are undefined for this key. Null out the values array.
            if (firstValue === undefined) {
                libraryValues[key].values = [];
            }

            // If the current key shows a rendering component, call it and save the resulting React object for later rendering.
            if (libraryComponents[key]) {
                libraryValues[key].component[firstBiologicalReplicate] = libraryComponents[key](replicates[0].library);
            }
        } else {
            if (libraryComponents[key]) {
                replicates.forEach(replicate => {
                    // If the current key shows a rendering component, call it and save the resulting React object for later rendering.
                    libraryValues[key].component[replicateToIndex(replicate)] = libraryComponents[key](replicate.library);
                });
            }
        }
    });

    // Now begin the output process -- one React component per array element
    var components = Object.keys(libraryValues).map(key => {
        var libraryEntry = libraryValues[key];
        if (libraryEntry.value !== undefined || (libraryEntry.values && Object.keys(libraryEntry.values).length)) {
            return (
                <div data-test={libraryEntry.test}>
                    <dt>{libraryEntry.title}</dt>
                    <dd>
                        {libraryEntry.value !== undefined ?
                            /* Single value for this property; render it or its React component */
                            <span>{(libraryEntry.component && Object.keys(libraryEntry.component).length) ? <span>{libraryEntry.component}</span> : <span>{libraryEntry.value}</span>}</span>
                        :
                            /* Multiple values for this property */
                            <span>
                                {Object.keys(libraryEntry.values).map((replicateId) => {
                                    var value = libraryEntry.values[replicateId];
                                    if (libraryEntry.component && libraryEntry.component[replicateId]) {
                                        /* Display the pre-rendered component */
                                        return <span key={replicateId} className="line-item">{libraryEntry.component[replicateId]} [{replicateId}]</span>;
                                    } else if (value) {
                                        /* Display the simple value */
                                        return <span key={replicateId} className="line-item">{value} [{replicateId}]</span>;
                                    } else {
                                        /* No value to display; happens when at least one replicate had a value for this property, but this one doesn't */
                                        return null;
                                    }
                                })}
                            </span>
                        }
                    </dd>
                </div>
            );
        }

        // No value exists for this property in any replicate; display nothing for this property.
        return null;
    });

    // Now handle a couple more complex properties to display for assay details.

    // Create platforms array from file platforms; ignore duplicate platforms
    var platforms = {};
    if (context.files && context.files.length) {
        context.files.forEach(function(file) {
            if (file.platform && file.dataset === context['@id']) {
                platforms[file.platform['@id']] = file.platform;
            }
        });
    }

    // Add platforms to the components array
    var platformKeys = Object.keys(platforms);
    if (platformKeys.length) {
        components.push(
            <div data-test="platform">
                <dt>Platform</dt>
                <dd>{platformKeys.map(platformId => <a className="stacked-link" key={platformId} href={platformId}>{platforms[platformId].title}</a>)}</dd>
            </div>
        );
    }

    // Add protein concentration units to components array. First determine if all values in all replicates identical.
    var firstConcentration = replicates[0].rbns_protein_concentration
    var firstConcentraitonUnits = replicates[0].rbns_protein_concentration_units;
    var homogenousConcentrations = _(replicates).all(replicate => {
        return (replicate.rbns_protein_concentration === firstConcentration) && (replicate.rbns_protein_concentration_units === firstConcentraitonUnits);
    });

    // Generate the renderings of each concentration line item. Check against undefined explicitly because some real values might by falsy.
    var concentrationRender = null;
    if (homogenousConcentrations) {
        // All values are the same (possibly undefined). Render just one line item
        concentrationRender = (firstConcentration !== undefined) ? <span className="line-item">{firstConcentration}<span className="unit">{firstConcentraitonUnits}</span></span> : null;
    } else {
        // Not all values are the same
        concentrationRender = replicates.map(replicate => {
            if (replicate.rbns_protein_concentration !== undefined) {
                return (
                    <span className="line-item" key={replicate.uuid}>
                        {replicate.rbns_protein_concentration}
                        <span className="unit">{replicate.rbns_protein_concentration_units}</span> [{replicate.biological_replicate_number}-{replicate.technical_replicate_number}]
                    </span>
                );
            }
        });
    }

    // Add the concentration rendering to the components array
    if (concentrationRender) {
        components.push(
            <div data-test="proteinconcentration">
                <dt>Protein concentration</dt>
                <dd>{concentrationRender}</dd>
            </div>
       );
    }

    return components;
};


// Return a summary of the given biosamples, ready to be displayed in a React component.
var biosampleSummaries = function(biosamples) {
    var organismNames = []; // Array of all organism scientific names in all given biosamples
    var lifeAges = []; // Array of all life stages, ages, and sexes in all given biosamples
    var depletedIns = {}; // Collection of depleted_in_term_name in all biosamples; each one is a key with the value True
    var mutatedGenes = {}; // Collection of donor.mutated_gene in all biosamples; each one is a key with the value True
    var subcellularTerms = {}; // Collection of subcellular_fraction_term_name in all biosamples; each one is a key with the value True
    var cellCycles = {}; // Collection of phase in all biosamples; each one is a key with the value True
    var fullSummary = null; // Complete summary of biosample in a <span>, ready to include in a React component

    // Collect biosample data from all biosamples
    biosamples.forEach(function(biosample) {
        // Collect names of biosample characteristics
        if (biosample.depleted_in_term_name && biosample.depleted_in_term_name.length) {
            biosample.depleted_in_term_name.forEach(function(depletedIn) {
                depletedIns[depletedIn] = true;
            });
        }
        if (biosample.donor && biosample.donor.mutated_gene) {
            mutatedGenes[biosample.donor.mutated_gene.label] = true;
        }
        if (biosample.subcellular_fraction_term_name) {
            subcellularTerms[biosample.subcellular_fraction_term_name] = true;
        }
        if (biosample.phase) {
            cellCycles[biosample.phase] = true;
        }

        // Collect organism scientific names
        if (biosample.organism.scientific_name) {
            organismNames.push(biosample.organism.scientific_name);
        }

        // Collect strings with non-'unknown', non-empty life_stage, age, age_units, and sex, concatenated
        var lifeAgeString = (biosample.life_stage && biosample.life_stage != 'unknown') ? biosample.life_stage : '';
        // Add to the filtering options to generate a <select>
        if (biosample.age && biosample.age != 'unknown') {
            lifeAgeString += (lifeAgeString ? ' ' : '') + biosample.age;
            lifeAgeString += (biosample.age_units && biosample.age_units != 'unknown') ? ' ' + biosample.age_units : '';
        }
        if (biosample.sex && biosample.sex != 'unknown') {
            lifeAgeString += (lifeAgeString ? ' ' : '') + biosample.sex;
        }
        if (lifeAgeString) {
            lifeAges.push(lifeAgeString);
        }
    });

    // Remove duplicates from stage/age/sex strings and organism names
    if (lifeAges.length) {
        lifeAges = _.uniq(lifeAges);
    }
    if (organismNames.length) {
        organismNames = _.uniq(organismNames);
    }

    // Make summary strings of each kind of biosample data
    var nameKeys = Object.keys(depletedIns);
    var depletedInSummary = nameKeys.length ? 'missing: ' + nameKeys.join('/') : '';
    nameKeys = Object.keys(mutatedGenes);
    var mutatedGeneSummary = nameKeys.length ? 'mutated gene: ' + nameKeys.join('/') : '';
    nameKeys = Object.keys(subcellularTerms);
    var subcellularTermSummary = nameKeys.length ? 'subcellular fraction: ' + nameKeys.join('/') : '';
    nameKeys = Object.keys(cellCycles);
    var cellCycleSummary = nameKeys.length ? 'cell-cycle phase: ' + nameKeys.join('/') : '';

    // Combine all summary strings, comma separated and including only non-empty ones
    var summary = _.compact([depletedInSummary, mutatedGeneSummary, subcellularTermSummary, cellCycleSummary]).join(', ');

    // Combine all name and life/age/sex strings
    fullSummary = (
        <span>
            {summary ? summary : null}
            {organismNames.length || lifeAges.length ?
                <span>
                    {summary ? ' (' : '('}
                    {organismNames.map(function(name, i) {
                        if (i === 0) {
                            return (<em key={name}>{name}</em>);
                        } else {
                            return (<span key={name}>{' and '}<em>{name}</em></span>);
                        }
                    })}
                    {lifeAges.length ? ', ' + lifeAges.join(' and ') : ''}
                    {')'}
                </span>
            : null}
        </span>
    );

    return fullSummary;
};


// Display a list of datasets related to the experiment
var RelatedSeriesList = React.createClass({
    propTypes: {
        seriesList: React.PropTypes.array.isRequired // Array of Series dataset objects to display
    },

    getInitialState: function() {
        return {
            currInfoItem: '', // Accession of item whose detail info appears; empty string to display no detail info
            touchScreen: false, // True if we know we got a touch event; ignore clicks without touch indiciation
            clicked: false // True if info button was clicked (vs hovered)
        }
    },

    // Handle the mouse entering/existing an info icon. Ignore if the info tooltip is open because the icon had
    // been clicked. 'entering' is true if the mouse entered the icon, and false if exiting.
    handleInfoHover: function(series, entering) {
        if (!this.state.clicked) {
            this.setState({currInfoItem: entering ? series.accession : ''});
        }
    },

    // Handle click in info icon by setting the currInfoItem state to the accession of the item to display.
    // If opening the tooltip, note that hover events should be ignored until the icon is clicked to close the tooltip.
    handleInfoClick: function(series, touch, e) {
        var currTouchScreen = this.state.touchScreen;

        // Remember if we know we've had a touch event
        if (touch && !currTouchScreen) {
            currTouchScreen = true;
            this.setState({touchScreen: true});
            console.log('SET TOUCHSCREEN TRUE');
        }

        // Now handle the click. Ignore if we know we have a touch screen, but this wasn't a touch event
        if (!currTouchScreen || touch) {
            console.log('STAT: %s:%o', currTouchScreen, touch);
            if (this.state.currInfoItem === series.accession && this.state.clicked) {
                this.setState({currInfoItem: '', clicked: false});
            } else {
                this.setState({currInfoItem: series.accession, clicked: true});
            }
        }
    },

    render: function() {
        var seriesList = this.props.seriesList;

        return (
            <span>
                {seriesList.map((series, i) => {
                    return (
                        <span key={series.uuid}>
                            {i > 0 ? <span>, </span> : null}
                            <RelatedSeriesItem series={series} detailOpen={this.state.currInfoItem === series.accession}
                                handleInfoHover={this.handleInfoHover} handleInfoClick={this.handleInfoClick} />
                        </span>
                    );
                })}
            </span>
        );
    }
});


// Display a one dataset related to the experiment
var RelatedSeriesItem = React.createClass({
    propTypes: {
        series: React.PropTypes.object.isRequired, // Series object to display
        detailOpen: React.PropTypes.bool, // TRUE to open the series' detail tooltip
        handleInfoClick: React.PropTypes.func, // Function to call to handle click in info icon
        handleInfoHover: React.PropTypes.func // Function to call when mouse enters or leaves info icon
    },

    getInitialState: function() {
        return {
            touchOn: false // True if icon has been touched
        }
    },

    // Touch screen
    touchStart: function(series, e) {
        this.setState({touchOn: !this.state.touchOn});
        this.props.handleInfoClick(series, true);
    },

    render: function() {
        var {series, detailOpen} = this.props;

        return (
            <span>
                <a href={series['@id']} title={'View page for series dataset ' + series.accession}>{series.accession}</a>&nbsp;
                <div className="tooltip-trigger">
                    <i className="icon icon-info-circle"
                        onMouseEnter={this.props.handleInfoHover.bind(null, series, true)}
                        onMouseLeave={this.props.handleInfoHover.bind(null, series, false)}
                        onClick={this.props.handleInfoClick.bind(null, series, false)}
                        onTouchStart={this.touchStart.bind(null, series)}></i>
                    <div className={'tooltip bottom' + (detailOpen ? ' tooltip-open' : '')}>
                        <div className="tooltip-arrow"></div>
                        <div className="tooltip-inner">
                            {series.description ? <span>{series.description}</span> : <em>No description available</em>}
                        </div>
                    </div>
                </div>
            </span>
        );
    }
});


// Handle graphing throws
function graphException(message, file0, file1) {
/*jshint validthis: true */
    this.message = message;
    if (file0) {
        this.file0 = file0;
    }
    if (file1) {
        this.file1 = file1;
    }
}

module.exports.graphException = graphException;


var assembleGraph = module.exports.assembleGraph = function(context, infoNodeId, files, filterAssembly, filterAnnotation) {

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

    function processFiltering(fileList, filterAssembly, filterAnnotation, allFiles, allContributing, include) {

        function getSubFileList(filesArray) {
            var fileList = {};
            filesArray.forEach(function(file) {
                fileList[file['@id']] = allFiles[file['@id']];
            });
            return fileList;
        }

        var fileKeys = Object.keys(fileList);
        for (var i = 0; i < fileKeys.length; i++) {
            var file = fileList[fileKeys[i]];
            var nextFileList;

            if (file) {
                if (!file.removed) {
                    // This file gets included. Include everything it derives from
                    if (file.derived_from && file.derived_from.length && !allContributing[file['@id']]) {
                        nextFileList = getSubFileList(file.derived_from);
                        processFiltering(nextFileList, filterAssembly, filterAnnotation, allFiles, allContributing, true);
                    }
                } else if (include) {
                    // Unremove the file if this branch is to be included based on files that derive from it
                    file.removed = false;
                    if (file.derived_from && file.derived_from.length && !allContributing[file['@id']]) {
                        nextFileList = getSubFileList(file.derived_from);
                        processFiltering(nextFileList, filterAssembly, filterAnnotation, allFiles, allContributing, true);
                    }
                }
            }
        }
    }

    var jsonGraph; // JSON graph object of entire graph; see graph.js
    var derivedFromFiles = {}; // List of all files that other files derived from
    var allFiles = {}; // All files' accessions as keys
    var allReplicates = {}; // All file's replicates as keys; each key references an array of files
    var allPipelines = {}; // List of all pipelines indexed by step @id
    var allMetricsInfo = []; // List of all QC metrics found attached to files
    var allContributing = {}; // List of all contributing files
    var fileQcMetrics = {}; // List of all file QC metrics indexed by file ID
    var filterOptions = {}; // List of graph filters; annotations and assemblies
    var stepExists = false; // True if at least one file has an analysis_step
    var fileOutsideReplicate = false; // True if at least one file exists outside a replicate
    var abortGraph = false; // True if graph shouldn't be drawn
    var abortMsg; // Console message to display if aborting graph
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

    // Collect all files keyed by their ID as a single source of truth for files.
    // Every reference to a file object should get it from this object. Also serves
    // to de-dup the file array since there can be repeated files in it.
    files.forEach(function(file) {
        if (!allFiles[file['@id']]) {
            allFiles[file['@id']] = file;
        }
    });

    // Add contributing files to the allFiles object that other files derive from.
    // Don't worry about files they derive from; they're not included in the graph.
    // If an allFiles entry already exists for the file, it gets overwritten so that
    // allFiles and allContributingFiles point at the same object.
    if (context.contributing_files && context.contributing_files.length) {
        context.contributing_files.forEach(function(file) {
            if (allFiles[file['@id']]) {
                // Contributing file already existed in file array for some reason; use its existing file object
                allContributing[file['@id']] = allFiles[file['@id']];
            } else {
                // Seeing contributed file for the first time; save it in both allFiles and allContributingFiles
                allFiles[file['@id']] = allContributing[file['@id']] = file;
            }
        });
    }

    // Collect derived_from files, used replicates, and used pipelines
    Object.keys(allFiles).forEach(function(fileId) {
        var file = allFiles[fileId];

        // Build an object keyed with all files that other files derive from. If the file is contributed,
        // we don't care about its derived_from because we don't render that.
        if (!allContributing[fileId] && file.derived_from && file.derived_from.length) {
            file.derived_from.forEach(function(derived_from) {
                var derivedFromId = derived_from['@id'];
                var derivedFile = allFiles[derivedFromId];
                if (!derivedFile) {
                    // The derived-from file wasn't in the given file list. Copy the file object from the file's
                    // derived_from so we can examine it later -- and mark it as missing.
                    derivedFromFiles[derivedFromId] = derived_from;
                    derived_from.missing = true;
                } else if (!derivedFromFiles[derivedFromId]) {
                    // The derived-from file was in the given file list, so record the derived-from file in derivedFromFiles.
                    // ...that is, unless the derived-from file has already been seen. Just move on if it has.
                    derivedFromFiles[derivedFromId] = derivedFile;
                }
            });
        }

        // Keep track of all used replicates by keeping track of all file objects for each replicate.
        // Each key is a replicate number, and each references an array of file objects using that replicate.
        if (file.biological_replicates && file.biological_replicates.length === 1) {
            var biological_replicate_number = file.biological_replicates[0];
            if (!allReplicates[biological_replicate_number]) {
                // Place a new array in allReplicates if needed
                allReplicates[biological_replicate_number] = [];
            }
            allReplicates[biological_replicate_number].push(file);
        }

        // Note whether any files have an analysis step
        var fileAnalysisStep = file.analysis_step_version && file.analysis_step_version.analysis_step;
        stepExists = stepExists || fileAnalysisStep;

        // Save the pipeline array used for each step used by the file.
        if (fileAnalysisStep) {
            allPipelines[fileAnalysisStep['@id']] = fileAnalysisStep.pipelines;
        }

        // File is derived; collect any QC info that applies to this file
        if (file.quality_metrics) {
            var matchingQc = [];

            // Search file's quality_metrics array to find one with a quality_metric_of field referring to this file.
            file.quality_metrics.forEach(function(metric) {
                var matchingFile = _(metric.quality_metric_of).find(function(appliesFile) {
                    return file['@id'] === appliesFile;
                });
                if (matchingFile) {
                    matchingQc.push(metric);
                }
            });
            if (matchingQc.length) {
                fileQcMetrics[fileId] = matchingQc;
            }
        }

        // Keep track of whether files exist outside replicates. That could mean it has no replicate information,
        // or it has more than one replicate.
        fileOutsideReplicate = fileOutsideReplicate || (file.biological_replicates && file.biological_replicates.length !== 1);
    });
    // At this stage, allFiles, allReplicates, and derivedFromFiles point to the same file objects;
    // allPipelines points to pipelines.

    // Don't draw anything if no files have an analysis_step
    if (!stepExists) {
        throw new graphException('No graph: no files have step runs');
    }

    // Now that we know at least some files derive from each other through analysis steps, mark file objects that
    // don't derive from other files — and that no files derive from them — as removed from the graph.
    // Also build the filtering menu here; it genomic annotations and assemblies that ARE involved in the graph.
    Object.keys(allFiles).forEach(function(fileId) {
        var file = allFiles[fileId];

        // File gets removed if doesn’t derive from other files AND no files derive from it.
        var islandFile = file.removed = !(file.derived_from && file.derived_from.length) && !derivedFromFiles[fileId];

        // Add to the filtering options to generate a <select>; don't include island files
        if (!islandFile && file.output_category !== 'raw data' && file.assembly) {
            if (file.genome_annotation) {
                filterOptions[file.assembly + '-' + file.genome_annotation] = file.assembly + ' ' + file.genome_annotation;
            } else {
                filterOptions[file.assembly] = file.assembly;
            }
        }
    });

    // Remove any replicates containing only removed files from the last step.
    Object.keys(allReplicates).forEach(function(repNum) {
        var onlyRemovedFiles = _(allReplicates[repNum]).all(function(file) {
            return file.removed && file.missing === true;
        });
        if (onlyRemovedFiles) {
            allReplicates[repNum] = [];
        }
    });

    // Check whether any files that others derive from are missing (usually because they're unreleased and we're logged out).
    Object.keys(derivedFromFiles).forEach(function(derivedFromFileId) {
        var derivedFromFile = derivedFromFiles[derivedFromFileId];
        if (derivedFromFile.removed || derivedFromFile.missing) {
            // A file others derive from doesn't exist or was removed; check if it's in a replicate or not
            // Note the derived_from file object exists even if it doesn't exist in given files array.
            if (derivedFromFile.biological_replicates && derivedFromFile.biological_replicates.length === 1) {
                // Missing derived-from file in a replicate; remove the replicate's files and remove itself.
                var derivedFromRep = derivedFromFile.biological_replicates[0];
                if (allReplicates[derivedFromRep]) {
                    allReplicates[derivedFromRep].forEach(function(file) {
                        file.removed = true;
                    });
                }
            } else {
                // Missing derived-from file not in a replicate or in multiple replicates; don't draw any graph
                throw new graphException('No graph: derived_from file outside replicate (or in multiple replicates) missing', derivedFromFileId);
            }
        } // else the derived_from file is in files array (allFiles object); normal case
    });

    // Remove files based on the filtering options
    if (filterAssembly) {
        // First remove all raw files, and all other files with mismatched filtering options
        Object.keys(allFiles).forEach(function(fileId) {
            var file = allFiles[fileId];

            if (file.output_category === 'raw data') {
                // File is raw data; just remove it
                file.removed = true;
            } else {
                // At this stage, we know it's a process or reference file. Remove from files if
                // it has mismatched assembly or annotation
                if ((file.assembly !== filterAssembly) || ((file.genome_annotation || filterAnnotation) && (file.genome_annotation !== filterAnnotation))) {
                    file.removed = true;
                }
            }
        });

        // For all files matching the filtering options that derive from others, go up the derivation chain and re-include everything there.
        processFiltering(allFiles, filterAssembly, filterAnnotation, allFiles, allContributing);
    }

    // See if removing files by filtering have emptied a replicate.
    if (Object.keys(allReplicates).length) {
        Object.keys(allReplicates).forEach(function(replicateId) {
            var emptied = _(allReplicates[replicateId]).all(function(file) {
                return file.removed;
            });

            // If all files removed from a replicate, remove the replicate
            if (emptied) {
                allReplicates[replicateId] = [];
            }

        });
    }

    // Check whether all files have been removed
    abortGraph = _(Object.keys(allFiles)).all(function(fileId) {
        return allFiles[fileId].removed;
    });
    if (abortGraph) {
        throw new graphException('No graph: all files removed');
    }

    // No files exist outside replicates, and all replicates are removed
    var replicateIds = Object.keys(allReplicates);
    if (fileOutsideReplicate && replicateIds.length && _(replicateIds).all(function(replicateNum) {
        return !allReplicates[replicateNum].length;
    })) {
        throw new graphException('No graph: All replicates removed and no files outside replicates exist');
    }

    // Last check; see if any files derive from files now missing. This test is child-file based, where the last test
    // was based on the derived-from files.
    Object.keys(allFiles).forEach(function(fileId) {
        var file = allFiles[fileId];

        if (!file.removed && !allContributing[fileId] && file.derived_from && file.derived_from.length) {
            var derivedGoneMissing; // Just to help debugging
            var derivedGoneId; // @id of derived-from file that's either missing or removed

            // A file still in the graph derives from others. See if any of the files it derives from have been removed
            // or are missing.
            file.derived_from.forEach(function(derivedFromFile) {
                var orgDerivedFromFile = derivedFromFiles[derivedFromFile['@id']];
                var derivedGone = orgDerivedFromFile.missing || orgDerivedFromFile.removed;

                // These two just for debugging a unrendered graph
                if (derivedGone) {
                    throw new graphException('file0 derives from file1 which is ' + (orgDerivedFromFile.missing ? 'missing' : 'removed'), fileId, derivedFromFile['@id']);
                }
            });
        }
    });

    // Create an empty graph architecture that we fill in next.
    jsonGraph = new JsonGraph(context.accession);

    // Create nodes for the replicates
    Object.keys(allReplicates).forEach(function(replicateNum) {
        if (allReplicates[replicateNum] && allReplicates[replicateNum].length) {
            jsonGraph.addNode('rep:' + replicateNum, 'Replicate ' + replicateNum, {
                cssClass: 'pipeline-replicate',
                type: 'Rep',
                shape: 'rect',
                cornerRadius: 0
            });
        }
    });

    // Go through each file (released or unreleased) to add it and associated steps to the graph
    Object.keys(allFiles).forEach(function(fileId) {
        var file = allFiles[fileId];

        // Only add files derived from others, or that others derive from,
        // and that aren't part of a removed replicate
        if (!file.removed) {
            var stepId;
            var label;
            var pipelineInfo;
            var error;
            var fileNodeId = 'file:' + file['@id'];
            var replicateNode = (file.biological_replicates && file.biological_replicates.length === 1 ) ? jsonGraph.getNode('rep:' + file.biological_replicates[0]) : null;
            var metricsInfo;
            var fileContributed = allContributing[fileId];

            // Add QC metrics info from the file to the list to generate the nodes later
            if (fileQcMetrics[fileId] && fileQcMetrics[fileId].length && file.step_run) {
                metricsInfo = fileQcMetrics[fileId].map(function(metric) {
                    var qcId = genQcId(metric, file);
                    return {id: qcId, label: 'QC', class: 'pipeline-node-qc-metric' + (infoNodeId === qcId ? ' active' : ''), ref: metric, parent: file};
                });
            }

            // Add file to the graph as a node
            jsonGraph.addNode(fileNodeId, file.title + ' (' + file.output_type + ')', {
                cssClass: 'pipeline-node-file' + (fileContributed ? ' contributing' : '') + (infoNodeId === fileNodeId ? ' active' : ''),
                type: 'File',
                shape: 'rect',
                cornerRadius: 16,
                parentNode: replicateNode,
                ref: file
            }, metricsInfo);

            // If the file has an analysis step, prepare it for graph insertion
            if (!fileContributed) {
                var fileAnalysisStep = file.analysis_step_version && file.analysis_step_version.analysis_step;
                if (fileAnalysisStep) {
                    // Make an ID and label for the step
                    stepId = 'step:' + derivedFileIds(file) + fileAnalysisStep['@id'];
                    label = fileAnalysisStep.analysis_step_types;
                    pipelineInfo = allPipelines[fileAnalysisStep['@id']];
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
                            type: 'Step',
                            shape: 'rect',
                            cornerRadius: 4,
                            parentNode: replicateNode,
                            ref: fileAnalysisStep,
                            pipelines: pipelineInfo,
                            fileId: file['@id'],
                            fileAccession: file.accession,
                            stepVersion: file.analysis_step_version
                        });
                    }

                    // Connect the file to the step, and the step to the derived_from files
                    jsonGraph.addEdge(stepId, fileNodeId);
                    file.derived_from.forEach(function(derived) {
                        if (!jsonGraph.getEdge('file:' + derived['@id'], stepId)) {
                            jsonGraph.addEdge('file:' + derived['@id'], stepId);
                        }
                    });
                }
            }
        }
    }, this);

    jsonGraph.filterOptions = filterOptions;
    return jsonGraph;
};

// analysis steps.
var ExperimentGraph = module.exports.ExperimentGraph = React.createClass({

    getInitialState: function() {
        return {
            infoNodeId: '', // @id of node whose info panel is open
            selectedAssembly: '', // Value of selected mapping assembly filter
            selectedAnnotation: '' // Value of selected genome annotation filter
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

    handleFilterChange: function(e) {
        var value = e.target.value;
        if (value !== 'default') {
            var filters = value.split('-');
            this.setState({selectedAssembly: filters[0], selectedAnnotation: filters[1]});
        } else {
            this.setState({selectedAssembly: '', selectedAnnotation: ''});
        }
    },

    render: function() {
        var context = this.props.context;
        var data = this.props.data;
        var items = data ? data['@graph'] : [];
        var files = context.files.concat(items);

        // Build node graph of the files and analysis steps with this experiment
        if (files && files.length) {
            // Build the graph; place resulting graph in this.jsonGraph
            var filterOptions = {};
            try {
                this.jsonGraph = assembleGraph(context, this.state.infoNodeId, files, this.state.selectedAssembly, this.state.selectedAnnotation);
            } catch(e) {
                this.jsonGraph = null;
                console.warn(e.message + (e.file0 ? ' -- file0:' + e.file0 : '') + (e.file1 ? ' -- file1:' + e.file1: ''));
            }
            var goodGraph = this.jsonGraph && Object.keys(this.jsonGraph).length;
            filterOptions = goodGraph && this.jsonGraph.filterOptions;

            // If we have a graph, or if we have a selected assembly/annotation, draw the graph panel
            if (goodGraph || this.state.selectedAssembly || this.state.selectedAnnotation) {
                var meta = this.detailNodes(this.jsonGraph, this.state.infoNodeId);
                return (
                    <div>
                        <h3>Files generated by pipeline</h3>
                        {filterOptions && Object.keys(filterOptions).length ?
                            <div className="form-inline">
                                <select className="form-control" defaultValue="default" onChange={this.handleFilterChange}>
                                    <option value="default" key="title">All Assemblies and Annotations</option>
                                    <option disabled="disabled"></option>
                                    {Object.keys(filterOptions).map(function(option) {
                                        return (
                                            <option key={option} value={option}>{filterOptions[option]}</option>
                                        );
                                    })}
                                </select>
                            </div>
                        : null}
                        {goodGraph ?
                            <Graph graph={this.jsonGraph} nodeClickHandler={this.handleNodeClick}>
                                <div id="graph-node-info">
                                    {meta ? <div className="panel-insert">{meta}</div> : null}
                                </div>
                            </Graph>
                        :
                            <div className="panel-full">
                                <p className="browser-error">Currently selected assembly and genomic annocation hides the graph</p>
                            </div>
                        }
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
            <dl className="key-value">
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
                    <div data-test="bioreplicate">
                        <dt>Biological replicate(s)</dt>
                        <dd>{'[' + selectedFile.replicate.biological_replicate_number + ']'}</dd>
                    </div>
                : selectedFile.biological_replicates && selectedFile.biological_replicates.length ?
                    <div data-test="bioreplicate">
                        <dt>Biological replicate(s)</dt>
                        <dd>{'[' + selectedFile.biological_replicates.join(', ') + ']'}</dd>
                    </div>
                : null}

                {selectedFile.replicate ?
                    <div data-test="techreplicate">
                        <dt>Technical replicate</dt>
                        <dd>{selectedFile.replicate.technical_replicate_number}</dd>
                    </div>
                : selectedFile.biological_replicates && selectedFile.biological_replicates.length ?
                    <div data-test="techreplicate">
                        <dt>Technical replicate</dt>
                        <dd>{'-'}</dd>
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

                {selectedFile.analysis_step_version ?
                    <div data-test="software">
                        <dt>Software</dt>
                        <dd>{SoftwareVersionList(selectedFile.analysis_step_version.software_versions)}</dd>
                    </div>
                : null}

                {node.metadata.contributing && selectedFile.dataset ?
                    <div data-test="contributedfrom">
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

globals.graph_detail.register(FileDetailView, 'File');


// Display QC metrics of the selected QC sub-node in a file node.
var QcDetailsView = function(metrics) {
    // QC metrics properties to NOT display.
    var reserved = ['uuid', 'assay_term_name', 'assay_term_id', 'attachment', 'submitted_by', 'level', 'status', 'date_created', 'step_run', 'schema_version'];
    var sortedKeys = Object.keys(metrics.ref).sort();

    if (metrics) {
        return (
            <div>
                <h4 className="quality-metrics-title">Quality metrics of {metrics.parent.accession}</h4>
                <dl className="key-value-flex">
                    {sortedKeys.map(function(key) {
                        if ((typeof metrics.ref[key] === 'string' || typeof metrics.ref[key] === 'number') && key[0] !== '@' && reserved.indexOf(key) === -1) {
                            return(
                                <div key={key}>
                                    <dt>{key}</dt>
                                    <dd>{metrics.ref[key]}</dd>
                                </div>
                            );
                        }
                        return null;
                    })}
                </dl>
            </div>
        );
    } else {
        return null;
    }
};
