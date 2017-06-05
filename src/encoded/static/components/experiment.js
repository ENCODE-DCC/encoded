'use strict';
var React = require('react');
import PropTypes from 'prop-types';
import createReactClass from 'create-react-class';
var panel = require('../libs/bootstrap/panel');
var button = require('../libs/bootstrap/button');
var dropdownMenu = require('../libs/bootstrap/dropdown-menu');
var _ = require('underscore');
import { auditDecor } from './audit';
var navigation = require('./navigation');
var globals = require('./globals');
var dbxref = require('./dbxref');
var dataset = require('./dataset');
var image = require('./image');
import StatusLabel from './statuslabel';
var fetched = require('./fetched');
var pipeline = require('./pipeline');
var { pubReferenceList } = require('./reference');
var software = require('./software');
var sortTable = require('./sorttable');
var objectutils = require('./objectutils');
var doc = require('./doc');
var {FileGallery} = require('./filegallery');
var {GeneticModificationSummary} = require('./genetic_modification');
var { BiosampleSummaryString, BiosampleOrganismNames, CollectBiosampleDocs, AwardRef } = require('./typeutils');

var Breadcrumbs = navigation.Breadcrumbs;
var DbxrefList = dbxref.DbxrefList;
var FetchedItems = fetched.FetchedItems;
var Param = fetched.Param;
var singleTreatment = objectutils.singleTreatment;
var softwareVersionList = software.softwareVersionList;
var {SortTablePanel, SortTable} = sortTable;
var ProjectBadge = image.ProjectBadge;
var {DocumentsPanel} = doc;
var DropdownButton = button.DropdownButton;
var DropdownMenu = dropdownMenu.DropdownMenu;
var {Panel, PanelBody, PanelHeading} = panel;
var ExperimentTable = dataset.ExperimentTable;


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


var ExperimentComponent = createReactClass({
    contextTypes: {
        session: PropTypes.object,
        session_properties: PropTypes.object,
    },

    render: function() {
        var condensedReplicates = [];
        var context = this.props.context;
        const adminUser = !!(this.context.session_properties && this.context.session_properties.admin);
        var itemClass = globals.itemClass(context, 'view-item');
        var replicates = context.replicates;
        if (replicates) {
            var condensedReplicatesKeyed = _(replicates).groupBy(replicate => replicate.library ? replicate.library['@id'] : replicate.uuid);
            if (Object.keys(condensedReplicatesKeyed).length) {
                condensedReplicates = _.toArray(condensedReplicatesKeyed);
            }
        }

        // Collect all documents from the experiment itself.
        var documents = (context.documents && context.documents.length) ? context.documents : [];

        // Make array of all replicate biosamples, not including biosample-less replicates. Also collect up library documents.
        var libraryDocs = [];
        var biosamples = [];
        var geneticModifications = [];
        if (replicates) {
            biosamples = _.compact(replicates.map(replicate => {
                if (replicate.library) {
                    if (replicate.library.documents && replicate.library.documents.length){
                        Array.prototype.push.apply(libraryDocs, replicate.library.documents);
                    }

                    // Collect biosample genetic modifications
                    if (replicate.library.biosample && replicate.library.biosample.genetic_modifications && replicate.library.biosample.genetic_modifications.length) {
                        geneticModifications = geneticModifications.concat(replicate.library.biosample.genetic_modifications);
                    }

                    return replicate.library.biosample;
                }
                return null;
            }));
        }

        // Create platforms array from file platforms; ignore duplicate platforms
        var platforms = {};
        if (context.files && context.files.length) {
            context.files.forEach(file => {
                if (file.platform && file.dataset === context['@id']) {
                    platforms[file.platform['@id']] = file.platform;
                }
            });
        }

        // If we have replicates, handle what we used to call Assay Details -- display data about each of the replicates, breaking out details
        // if they differ between replicates.
        if (replicates && replicates.length) {
            // Prepare to collect values from each replicate's library. Each key in this object refers to a property in the libraries.
            var libraryValues = {
                treatments:                     {values: {}, value: undefined, component: {}, title: 'Treatments',                test: 'treatments'},
                nucleic_acid_term_name:         {values: {}, value: undefined, component: {}, title: 'Nucleic acid type',         test: 'nucleicacid'},
                depleted_in_term_name:          {values: {}, value: undefined, component: {}, title: 'Depleted in',               test: 'depletedin'},
                nucleic_acid_starting_quantity: {values: {}, value: undefined, component: {}, title: 'Library starting quantity', test: 'startingquantity'},
                size_range:                     {values: {}, value: undefined, component: {}, title: 'Size range',                test: 'sizerange'},
                lysis_method:                   {values: {}, value: undefined, component: {}, title: 'Lysis method',              test: 'lysismethod'},
                extraction_method:              {values: {}, value: undefined, component: {}, title: 'Extraction method',         test: 'extractionmethod'},
                fragmentation_method:           {values: {}, value: undefined, component: {}, title: 'Fragmentation method',      test: 'fragmentationmethod'},
                library_size_selection_method:  {values: {}, value: undefined, component: {}, title: 'Size selection method',     test: 'sizeselectionmethod'},
                strand_specificity:             {values: {}, value: undefined, component: {}, title: 'Strand specificity',        test: 'strandspecificity'},
                spikeins_used:                  {values: {}, value: undefined, component: {}, title: 'Spike-ins datasets',        test: 'spikeins'}
            };

            // For any library properties that aren't simple values, put functions to process them into simple values in this object,
            // keyed by their library property name. Returned JS undefined if no complex value exists so that we can reliably test it
            // arily. We have a couple properties too complex even for this, so they'll get added separately at the end.
            var librarySpecials = {
                treatments: function(library) {
                    var treatments = []; // Array of treatment_term_name

                    // First get the treatments in the library
                    if (library.treatments && library.treatments.length) {
                        treatments = library.treatments.map(treatment => singleTreatment(treatment));
                    }

                    // Now get the treatments in the biosamples
                    if (library.biosample && library.biosample.treatments && library.biosample.treatments.length) {
                        treatments = treatments.concat(library.biosample.treatments.map(treatment => singleTreatment(treatment)));
                    }

                    if (treatments.length) {
                        return treatments.sort().join(', ');
                    }
                    return undefined;
                },
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
                spikeins_used: function(library) {
                    var spikeins = library.spikeins_used;

                    // Just track @id for deciding if all values are the same or not. Rendering handled in libraryComponents
                    if (spikeins && spikeins.length) {
                        return spikeins.sort().join();
                    }
                    return undefined;
                }
            };
            var libraryComponents = {
                nucleic_acid_starting_quantity: library => {
                    if (library.nucleic_acid_starting_quantity && library.nucleic_acid_starting_quantity_units) {
                        return <span>{library.nucleic_acid_starting_quantity}<span className="unit">{library.nucleic_acid_starting_quantity_units}</span></span>;
                    }
                    return null;
                },
                strand_specificity: library => <span>{library.strand_specificity ? 'Strand-specific' : 'Non-strand-specific'}</span>,
                spikeins_used: library => {
                    const spikeins = library.spikeins_used;
                    if (spikeins && spikeins.length) {
                        return (
                            <span>
                                {spikeins.map((spikeinsAtId, i) =>
                                    <span key={i}>
                                        {i > 0 ? ', ' : ''}
                                        <a href={spikeinsAtId}>{globals.atIdToAccession(spikeinsAtId)}</a>
                                    </span>
                                )}
                            </span>
                        );
                    }
                    return null;
                }
            };
        }

        // Collect biosample docs
        var biosampleDocs = [];
        biosamples.forEach(biosample => {
            biosampleDocs = biosampleDocs.concat(CollectBiosampleDocs(biosample));
            if (biosample.originated_from) {
                biosampleDocs = biosampleDocs.concat(CollectBiosampleDocs(biosample.originated_from));
            }
        });

        // Collect pipeline-related documents
        var analysisStepDocs = [];
        var pipelineDocs = [];
        if (context.files && context.files.length) {
            context.files.forEach(file => {
                var fileAnalysisStepVersion = file.analysis_step_version;
                if (fileAnalysisStepVersion) {
                    var fileAnalysisStep = fileAnalysisStepVersion.analysis_step;
                    if (fileAnalysisStep) {
                        // Collect analysis step docs
                        if (fileAnalysisStep.documents && fileAnalysisStep.documents.length) {
                            analysisStepDocs = analysisStepDocs.concat(fileAnalysisStep.documents);
                        }

                        // Collect pipeline docs
                        if (fileAnalysisStep.pipelines && fileAnalysisStep.pipelines.length) {
                            fileAnalysisStep.pipelines.forEach(pipeline => {
                                if (pipeline.documents && pipeline.documents.length) {
                                    pipelineDocs = pipelineDocs.concat(pipeline.documents);
                                }
                            });
                        }
                    }
                }
            });
        }
        analysisStepDocs = analysisStepDocs.length ? globals.uniqueObjectsArray(analysisStepDocs) : [];
        pipelineDocs = pipelineDocs.length ? globals.uniqueObjectsArray(pipelineDocs) : [];

        // Determine this experiment's ENCODE version
        var encodevers = globals.encodeVersion(context);

        // Make list of statuses
        const statuses = [{ status: context.status, title: 'Status' }];
        if (adminUser && context.internal_status) {
            statuses.push({ status: context.internal_status, title: 'Internal' });
        }

        // Make string of alternate accessions
        var altacc = context.alternate_accessions ? context.alternate_accessions.join(', ') : undefined;

        // Make array of superseded_by accessions
        let supersededBys = [];
        if (context.superseded_by && context.superseded_by.length) {
            supersededBys = context.superseded_by.map(supersededBy => globals.atIdToAccession(supersededBy));
        }

        // Make array of supersedes accessions
        let supersedes = [];
        if (context.supersedes && context.supersedes.length) {
            supersedes = context.supersedes.map(supersede => globals.atIdToAccession(supersede));
        }

        // Determine whether the experiment is isogenic or anisogenic. No replication_type indicates isogenic.
        var anisogenic = context.replication_type ? (anisogenicValues.indexOf(context.replication_type) !== -1) : false;

        // Get a list of related datasets, possibly filtering on their status
        var seriesList = [];
        var loggedIn = !!(this.context.session && this.context.session['auth.userid']);
        if (context.related_series && context.related_series.length) {
            seriesList = _(context.related_series).filter(dataset => loggedIn || dataset.status === 'released');
        }

        // Set up the breadcrumbs
        var assayTerm = context.assay_term_name ? 'assay_term_name' : 'assay_term_id';
        var assayName = context[assayTerm];
        var assayQuery = assayTerm + '=' + assayName;
        var organismNames = BiosampleOrganismNames(biosamples);
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

        // Compile the document list
        var combinedDocuments = _(documents.concat(
            biosampleDocs,
            libraryDocs,
            biosampleDocs,
            pipelineDocs,
            analysisStepDocs
        )).chain().uniq(doc => doc ? doc.uuid : null).compact().value();

        var experiments_url = '/search/?type=Experiment&possible_controls.accession=' + context.accession;

        // Make a list of reference links, if any
        var references = pubReferenceList(context.references);

        // Render tags badges
        var tagBadges;
        if (context.internal_tags && context.internal_tags.length) {
            tagBadges = context.internal_tags.map(tag => <img key={tag} src={'/static/img/tag-' + tag + '.png'} alt={tag + ' tag'} />);
        }

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs root='/search/?type=Experiment' crumbs={crumbs} />
                        <h2>Experiment summary for {context.accession}</h2>
                        {altacc ? <h4 className="repl-acc">Replaces {altacc}</h4> : null}
                        {supersededBys.length ? <h4 className="superseded-acc">Superseded by {supersededBys.join(', ')}</h4> : null}
                        {supersedes.length ? <h4 className="superseded-acc">Supersedes {supersedes.join(', ')}</h4> : null}
                        <div className="status-line">
                            <div className="characterization-status-labels">
                                <StatusLabel status={statuses} />
                            </div>
                            {this.props.auditIndicators(context.audit, 'experiment-audit', { session: this.context.session })}
                        </div>
                   </div>
                </header>
                {this.props.auditDetail(context.audit, 'experiment-audit', { session: this.context.session, except: context['@id'] })}
                <Panel addClasses="data-display">
                    <PanelBody addClasses="panel-body-with-header">
                        <div className="flexrow">
                            <div className="flexcol-sm-6">
                                <div className="flexcol-heading experiment-heading"><h4>Summary</h4></div>
                                <dl className="key-value">
                                    <div data-test="assay">
                                        <dt>Assay</dt>
                                        <dd>
                                            {context.assay_term_name}
                                            {context.assay_term_name !== context.assay_title ?
                                                <span>{' (' + context.assay_title + ')'}</span>
                                            : null}
                                        </dd>
                                    </div>

                                    {context.target ?
                                        <div data-test="target">
                                            <dt>Target</dt>
                                            <dd><a href={context.target['@id']}>{context.target.label}</a></dd>
                                        </div>
                                    : null}

                                    {context.biosample_summary ?
                                        <div data-test="biosample-summary">
                                            <dt>Biosample summary</dt>
                                            <dd>
                                                {organismNames.length ?
                                                    <span>
                                                        {organismNames.map((organismName, i) =>
                                                            <span key={organismName}>
                                                                {i > 0 ? <span> and </span> : null}
                                                                <i>{organismName}</i>
                                                            </span>
                                                        )}
                                                        <span> </span>
                                                    </span>
                                                : null}
                                                <span>{context.biosample_summary}</span>
                                            </dd>
                                        </div>
                                    : null}

                                    {context.biosample_type ?
                                        <div data-test="biosample-type">
                                            <dt>Biosample Type</dt>
                                            <dd>{context.biosample_type}</dd>
                                        </div>
                                    : null}

                                    {context.replication_type ?
                                        <div data-test="replicationtype">
                                            <dt>Replication type</dt>
                                            <dd>{context.replication_type}</dd>
                                        </div>
                                    : null}

                                    {context.description ?
                                        <div data-test="description">
                                            <dt>Description</dt>
                                            <dd>{context.description}</dd>
                                        </div>
                                    : null}

                                    {AssayDetails(replicates, libraryValues, librarySpecials, libraryComponents)}

                                    {Object.keys(platforms).length ?
                                        <div data-test="platform">
                                            <dt>Platform</dt>
                                            <dd>
                                                {Object.keys(platforms).map((platformId, i) =>
                                                    <span key={platformId}>
                                                        {i > 0 ? <span>, </span> : null}
                                                        <a className="stacked-link" href={platformId}>{platforms[platformId].title}</a>
                                                    </span>
                                                )}
                                            </dd>
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
                                <div className="flexcol-heading experiment-heading">
                                    <h4>Attribution</h4>
                                    <ProjectBadge award={context.award} addClasses="badge-heading" />
                                </div>
                                <dl className="key-value">
                                    <div data-test="lab">
                                        <dt>Lab</dt>
                                        <dd>{context.lab.title}</dd>
                                    </div>

                                    <AwardRef context={context} adminUser={adminUser} />

                                    <div data-test="project">
                                        <dt>Project</dt>
                                        <dd>{context.award.project}</dd>
                                    </div>

                                    {context.dbxrefs.length ?
                                        <div data-test="external-resources">
                                            <dt>External resources</dt>
                                            <dd><DbxrefList values={context.dbxrefs} cell_line={context.biosample_term_name} /></dd>
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
                                            <dd>{context.aliases.join(", ")}</dd>
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

                                    {context.submitter_comment ?
                                        <div data-test="submittercomment">
                                            <dt>Submitter comment</dt>
                                            <dd>{context.submitter_comment}</dd>
                                        </div>
                                    : null}

                                    {tagBadges ?
                                        <div className="tag-badges" data-test="tags">
                                            <dt>Tags</dt>
                                            <dd>{tagBadges}</dd>
                                        </div>
                                    : null}
                                </dl>
                            </div>
                        </div>
                    </PanelBody>
                </Panel>

                {geneticModifications.length ?
                    <GeneticModificationSummary geneticModifications={geneticModifications} />
                : null}

                {Object.keys(condensedReplicates).length ?
                    <ReplicateTable condensedReplicates={condensedReplicates} replicationType={context.replication_type} />
                : null}

                {/* Display the file widget with the facet, graph, and tables */}
                <FileGallery context={context} encodevers={encodevers} anisogenic={anisogenic} />

                <FetchedItems {...this.props} url={experiments_url} Component={ControllingExperiments} ignoreErrors />

                {combinedDocuments.length ? <DocumentsPanel documentSpecs={[{documents: combinedDocuments}]} /> : null}
            </div>
        );
    }
});

const Experiment = module.exports.Experiment = auditDecor(ExperimentComponent);

globals.content_views.register(Experiment, 'Experiment');


// Display the table of replicates
var ReplicateTable = createReactClass({
    propTypes: {
        condensedReplicates: PropTypes.array.isRequired, // Condensed 'array' of replicate objects
        replicationType: PropTypes.string // Type of replicate so we can tell what's isongenic/anisogenic/whatnot
    },

    replicateColumns: {
        'biological_replicate_number': {
            title: 'Biological replicate',
            getValue: condensedReplicate => condensedReplicate[0].biological_replicate_number
        },
        'technical_replicate_number': {
            title: 'Technical replicate',
            getValue: condensedReplicate => condensedReplicate.map(replicate => replicate.technical_replicate_number).sort().join()
        },
        'summary': {
            title: 'Summary',
            display: condensedReplicate => {
                var replicate = condensedReplicate[0];

                // Display protein concentration if it exists
                if (typeof replicate.rbns_protein_concentration === 'number') {
                    return (
                        <span>
                            Protein concentration {replicate.rbns_protein_concentration}
                            <span className="unit">{replicate.rbns_protein_concentration_units}</span>
                        </span>
                    );
                }

                // Else, display biosample summary if the biosample exists
                if (replicate.library && replicate.library.biosample) {
                    return <span>{BiosampleSummaryString(replicate.library.biosample, true)}</span>;
                }

                // Else, display nothing
                return null;
            },
            sorter: false
        },
        'biosample_accession': {
            title: 'Biosample',
            display: condensedReplicate => {
                var replicate = condensedReplicate[0];
                if (replicate.library && replicate.library.biosample) {
                    var biosample = replicate.library.biosample;
                    return <a href={biosample['@id']} title={'View biosample ' + biosample.accession}>{biosample.accession}</a>;
                }
                return null;
            },
            objSorter: (a, b) => {
                var aReplicate = a[0];
                var bReplicate = b[0];
                if ((aReplicate.library && aReplicate.library.biosample) && (bReplicate.library && bReplicate.library.biosample)) {
                    var aAccession = aReplicate.library.biosample.accession;
                    var bAccession = bReplicate.library.biosample.accession;
                    return (aAccession < bAccession) ? -1 : ((aAccession > bAccession) ? 1 : 0);
                }
                return (aReplicate.library && aReplicate.library.biosample) ? -1 : ((bReplicate.library && bReplicate.library.biosample) ? 1 : 0);
            }
        },
        'antibody_accession': {
            title: 'Antibody',
            display: condensedReplicate => {
                var replicate = condensedReplicate[0];
                if (replicate.antibody) {
                    return <a href={replicate.antibody['@id']} title={'View antibody ' + replicate.antibody.accession}>{replicate.antibody.accession}</a>;
                }
                return null;
            },
            objSorter: (a, b) => {
                var aReplicate = a[0];
                var bReplicate = b[0];
                if (aReplicate.antibody && bReplicate.antibody) {
                    return (aReplicate.antibody.accession < bReplicate.antibody.accession) ? -1 : ((aReplicate.antibody.accession > bReplicate.antibody.accession) ? 1 : 0);
                }
                return (aReplicate.antibody) ? -1 : ((bReplicate.antibody) ? 1 : 0);
            },
            hide: (list, columns, meta) => {
                return _(list).all(condensedReplicate => !condensedReplicate[0].antibody);
            }
        },
        'library': {
            title: 'Library',
            getValue: condensedReplicate => condensedReplicate[0].library ? condensedReplicate[0].library.accession : ''
        }
    },

    render: function() {
        var tableTitle;
        var {condensedReplicates, replicationType} = this.props;

        // Determine replicate table title based on the replicate type. Also override the biosample replicate column title
        if (replicationType === 'anisogenic') {
            tableTitle = 'Anisogenic replicates';
            this.replicateColumns.biological_replicate_number.title = 'Anisogenic replicate';
        } else if (replicationType === 'isogenic') {
            tableTitle = 'Isogenic replicates';
            this.replicateColumns.biological_replicate_number.title = 'Isogenic replicate';
        } else {
            tableTitle = 'Replicates';
            this.replicateColumns.biological_replicate_number.title = 'Biological replicate';
        }

        return (
            <SortTablePanel title={tableTitle}>
                <SortTable list={condensedReplicates} columns={this.replicateColumns} />
            </SortTablePanel>
        );
    }
});


var ControllingExperiments = createReactClass({
    render: function () {
        var context = this.props.context;

        if (this.props.items && this.props.items.length) {
            return (
                <div>
                    <ExperimentTable {...this.props}
                        items={this.props.items} limit={5} url={this.props.url}
                        title={'Experiments with ' + context.accession + ' as a control:'} />
                </div>
            );
        }
        return null;
    }
});


// Return an array of React components to render into the enclosing panel, given the experiment object in the context parameter
var AssayDetails = function (replicates, libraryValues, librarySpecials, libraryComponents) {

    // Little utility to convert a replicate to a unique index we can use for arrays (like libraryValues below)
    function replicateToIndex(replicate) {
        return replicate.biological_replicate_number + '-' + replicate.technical_replicate_number;
    }

    // No replicates, so no assay entries
    if (!replicates.length) {
        return [];
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
                if (librarySpecials && librarySpecials[key]) {
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
        if (_(Object.keys(libraryValues[key].values)).all(replicateId => libraryValues[key].values[replicateId] === firstValue)) {
            // All values for the library value are the same. Set the 'value' field with that value.
            libraryValues[key].value = firstValue;

            // If the resulting value is undefined, then all values are undefined for this key. Null out the values array.
            if (firstValue === undefined) {
                libraryValues[key].values = [];
            } else if (libraryComponents && libraryComponents[key]) {
                // The current key shows a rendering component, call it and save the resulting React object for later rendering.
                libraryValues[key].component[firstBiologicalReplicate] = libraryComponents[key](replicates[0].library);
            }
        } else {
            if (libraryComponents && libraryComponents[key]) {
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
                <div key={key} data-test={libraryEntry.test}>
                    <dt>{libraryEntry.title}</dt>
                    <dd>
                        {libraryEntry.value !== undefined ?
                            <span>
                                {(libraryEntry.component && Object.keys(libraryEntry.component).length) ?
                                    <span>
                                        {Object.keys(libraryEntry.component).map(componentKey => <span key={componentKey}>{libraryEntry.component[componentKey]}</span>)}
                                    </span>
                                :
                                    <span>{libraryEntry.value}</span>
                                }
                            </span>
                        :
                            <span>
                                {Object.keys(libraryEntry.values).map((replicateId) => {
                                    var value = libraryEntry.values[replicateId];
                                    if (libraryEntry.component && libraryEntry.component[replicateId]) {
                                        // Display the pre-rendered component
                                        return <span key={replicateId} className="line-item">{libraryEntry.component[replicateId]} [{replicateId}]</span>;
                                    }
                                    if (value) {
                                        // Display the simple value
                                        return <span key={replicateId} className="line-item">{value} [{replicateId}]</span>;
                                    }

                                    // No value to display; happens when at least one replicate had a value for this property, but this one doesn't
                                    return null;
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

    // Finally, return the array of JSX renderings of all assay details.
    return components;
};


// Display a list of datasets related to the experiment
var RelatedSeriesList = createReactClass({
    propTypes: {
        seriesList: PropTypes.array.isRequired // Array of Series dataset objects to display
    },

    getInitialState: function() {
        return {
            currInfoItem: '', // Accession of item whose detail info appears; empty string to display no detail info
            touchScreen: false, // True if we know we got a touch event; ignore clicks without touch indiciation
            clicked: false // True if info button was clicked (vs hovered)
        };
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
        }

        // Now handle the click. Ignore if we know we have a touch screen, but this wasn't a touch event
        if (!currTouchScreen || touch) {
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
var RelatedSeriesItem = createReactClass({
    propTypes: {
        series: PropTypes.object.isRequired, // Series object to display
        detailOpen: PropTypes.bool, // TRUE to open the series' detail tooltip
        handleInfoClick: PropTypes.func, // Function to call to handle click in info icon
        handleInfoHover: PropTypes.func // Function to call when mouse enters or leaves info icon
    },

    getInitialState: function() {
        return {
            touchOn: false // True if icon has been touched
        };
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