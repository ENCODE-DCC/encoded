import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment';
import _ from 'underscore';
import { Panel, PanelBody } from '../libs/bootstrap/panel';
import { auditDecor } from './audit';
import { DocumentsPanelReq } from './doc';
import * as globals from './globals';
import { DbxrefList } from './dbxref';
import { ExperimentTable } from './dataset';
import { FetchedItems } from './fetched';
import { FileGallery } from './filegallery';
import { GeneticModificationSummary } from './genetic_modification';
import { ProjectBadge } from './image';
import { Breadcrumbs } from './navigation';
import { singleTreatment } from './objectutils';
import pubReferenceList from './reference';
import { SortTablePanel, SortTable } from './sorttable';
import StatusLabel from './statuslabel';
import { BiosampleSummaryString, BiosampleOrganismNames, CollectBiosampleDocs, AwardRef } from './typeutils';


const anisogenicValues = [
    'anisogenic, sex-matched and age-matched',
    'anisogenic, age-matched',
    'anisogenic, sex-matched',
    'anisogenic',
];


// Return an array of React components to render into the enclosing panel, given the experiment
// object in the context parameter
function AssayDetails(replicates, libVals, libSpecials, libComps) {
    // Make a deep copy of libVals to avoid side effects.
    const results = Object.assign({}, libVals);

    // Little utility to convert a replicate to a unique index we can use for arrays (like libraryValues below)
    function replicateToIndex(replicate) {
        return `${replicate.biological_replicate_number}-${replicate.technical_replicate_number}`;
    }

    // No replicates, so no assay entries
    if (!replicates.length) {
        return [];
    }

    // Collect library values to display from each replicate. Each key holds an array of values from each replicate's library,
    // indexed by the replicate's biological replicate number. After this loop runs, libraryValues.values should all be filled
    // with objects keyed by <bio rep num>-<tech rep num> and have the corresponding value or undefined if no value exists
    // for that key. The 'value' properties of each object in libraryValues will all be undefined after this loop runs.
    replicates.forEach((replicate) => {
        const library = replicate.library;
        const replicateIndex = replicateToIndex(replicate);

        if (library) {
            // Handle "normal" library properties
            Object.keys(results).forEach((key) => {
                let libraryValue;

                // For specific library properties, preprocess non-simple values into simple ones using librarySpecials
                if (libSpecials && libSpecials[key]) {
                    // Preprocess complex values into simple ones
                    libraryValue = libSpecials[key](library);
                } else {
                    // Simple value -- just copy it if it exists (copy undefined if it doesn't)
                    libraryValue = library[key];
                }

                // If library property exists, add it to the values we're collecting, keyed by the biological replicate number.
                // We'll prune it after this replicate loop.
                results[key].values[replicateIndex] = libraryValue;
            });
        }
    });

    // Each property of libraryValues now has every value found in every existing library property in every replicate.
    // Now for each library value in libraryValues, set the 'value' property if all values in the 'values' object are
    // identical and existing. Otherwise, keep 'value' set to undefined.
    const firstBiologicalReplicate = replicateToIndex(replicates[0]);
    Object.keys(results).forEach((key) => {
        // Get the first key's value to compare against the others.
        const firstValue = results[key].values[firstBiologicalReplicate];

        // See if all values in the values array are identical. Treat 'undefined' as a value
        if (_(Object.keys(results[key].values)).all(replicateId => results[key].values[replicateId] === firstValue)) {
            // All values for the library value are the same. Set the 'value' field with that value.
            results[key].value = firstValue;

            // If the resulting value is undefined, then all values are undefined for this key. Null out the values array.
            if (firstValue === undefined) {
                results[key].values = [];
            } else if (libComps && libComps[key]) {
                // The current key shows a rendering component, call it and save the resulting React object for later rendering.
                results[key].component[firstBiologicalReplicate] = libComps[key](replicates[0].library);
            }
        } else if (libComps && libComps[key]) {
            replicates.forEach((replicate) => {
                // If the current key shows a rendering component, call it and save the resulting React object for later rendering.
                results[key].component[replicateToIndex(replicate)] = libComps[key](replicate.library);
            });
        }
    });

    // Now begin the output process -- one React component per array element
    const components = Object.keys(results).map((key) => {
        const libraryEntry = results[key];
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
                                    const value = libraryEntry.values[replicateId];
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
}


const ControllingExperiments = (props) => {
    const context = props.context;

    if (props.items.length) {
        return (
            <div>
                <ExperimentTable
                    {...props}
                    items={props.items}
                    limit={5}
                    url={props.url}
                    title={`Experiments with ${context.accession} as a control:`}
                />
            </div>
        );
    }
    return null;
};

ControllingExperiments.propTypes = {
    context: PropTypes.object.isRequired, // Experiment object containing the table being rendered
    items: PropTypes.array, // Experiments to display in the table
    url: PropTypes.string, // URL to go to full search results corresponding to the table
};

ControllingExperiments.defaultProps = {
    items: [],
    url: '',
};


class ExperimentComponent extends React.Component {
    constructor() {
        super();

        this.libraryValues = {
            treatments: { values: {}, value: undefined, component: {}, title: 'Treatments', test: 'treatments' },
            nucleic_acid_term_name: { values: {}, value: undefined, component: {}, title: 'Nucleic acid type', test: 'nucleicacid' },
            depleted_in_term_name: { values: {}, value: undefined, component: {}, title: 'Depleted in', test: 'depletedin' },
            nucleic_acid_starting_quantity: { values: {}, value: undefined, component: {}, title: 'Library starting quantity', test: 'startingquantity' },
            size_range: { values: {}, value: undefined, component: {}, title: 'Size range', test: 'sizerange' },
            lysis_method: { values: {}, value: undefined, component: {}, title: 'Lysis method', test: 'lysismethod' },
            extraction_method: { values: {}, value: undefined, component: {}, title: 'Extraction method', test: 'extractionmethod' },
            fragmentation_method: { values: {}, value: undefined, component: {}, title: 'Fragmentation method', test: 'fragmentationmethod' },
            library_size_selection_method: { values: {}, value: undefined, component: {}, title: 'Size selection method', test: 'sizeselectionmethod' },
            strand_specificity: { values: {}, value: undefined, component: {}, title: 'Strand specificity', test: 'strandspecificity' },
            spikeins_used: { values: {}, value: undefined, component: {}, title: 'Spike-ins datasets', test: 'spikeins' },
        };
    }

    render() {
        let librarySpecials = {};
        let libraryComponents = {};
        let condensedReplicates = [];
        const context = this.props.context;
        const adminUser = !!(this.context.session_properties && this.context.session_properties.admin);
        const itemClass = globals.itemClass(context, 'view-item');
        const replicates = context.replicates;
        if (replicates) {
            const condensedReplicatesKeyed = _(replicates).groupBy(replicate => (replicate.library ? replicate.library['@id'] : replicate.uuid));
            if (Object.keys(condensedReplicatesKeyed).length) {
                condensedReplicates = _.toArray(condensedReplicatesKeyed);
            }
        }

        // Collect all documents from the experiment itself.
        const documents = (context.documents && context.documents.length) ? context.documents : [];

        // Make array of all replicate biosamples, not including biosample-less replicates. Also
        // collect up library documents.
        const libraryDocs = [];
        let biosamples = [];
        if (replicates) {
            biosamples = _.compact(replicates.map((replicate) => {
                if (replicate.library) {
                    if (replicate.library.documents && replicate.library.documents.length) {
                        Array.prototype.push.apply(libraryDocs, replicate.library.documents);
                    }

                    return replicate.library.biosample;
                }
                return null;
            }));
        }
        geneticModifications = _(geneticModifications).uniq(gm => gm['@id']);

        // Create platforms array from file platforms; ignore duplicate platforms.
        const platforms = {};
        if (context.files && context.files.length) {
            context.files.forEach((file) => {
                if (file.platform && file.dataset === context['@id']) {
                    platforms[file.platform['@id']] = file.platform;
                }
            });
        }

        // If we have replicates, handle what we used to call Assay Details -- display data about
        // each of the replicates, breaking out details
        // if they differ between replicates.
        if (replicates && replicates.length) {
            // Prepare to collect values from each replicate's library. Each key in this object
            // refers to a property in the libraries. For any library properties that aren't simple
            // values, put functions to process them into simple values in this object, keyed by
            // their library property name. Returned JS undefined if no complex value exists so
            // that we can reliably test it. We have a couple properties too complex even for this,
            // so they'll get added separately at the end.
            librarySpecials = {
                treatments: (library) => {
                    let treatments = []; // Array of treatment_term_name

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
                nucleic_acid_starting_quantity: (library) => {
                    const quantity = library.nucleic_acid_starting_quantity;
                    if (quantity) {
                        return quantity + library.nucleic_acid_starting_quantity_units;
                    }
                    return undefined;
                },
                depleted_in_term_name: (library) => {
                    const terms = library.depleted_in_term_name;
                    if (terms && terms.length) {
                        return terms.sort().join(', ');
                    }
                    return undefined;
                },
                spikeins_used: (library) => {
                    const spikeins = library.spikeins_used;

                    // Just track @id for deciding if all values are the same or not. Rendering
                    // handled in libraryComponents
                    if (spikeins && spikeins.length) {
                        return spikeins.sort().join();
                    }
                    return undefined;
                },
            };
            libraryComponents = {
                nucleic_acid_starting_quantity: (library) => {
                    if (library.nucleic_acid_starting_quantity && library.nucleic_acid_starting_quantity_units) {
                        return <span>{library.nucleic_acid_starting_quantity}<span className="unit">{library.nucleic_acid_starting_quantity_units}</span></span>;
                    }
                    return null;
                },
                strand_specificity: library => <span>{library.strand_specificity ? 'Strand-specific' : 'Non-strand-specific'}</span>,
                spikeins_used: (library) => {
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
                },
            };
        }

        // Collect biosample docs.
        let biosampleDocs = [];
        biosamples.forEach((biosample) => {
            biosampleDocs = biosampleDocs.concat(CollectBiosampleDocs(biosample));
            if (biosample.part_of) {
                biosampleDocs = biosampleDocs.concat(CollectBiosampleDocs(biosample.part_of));
            }
        });

        // Collect pipeline-related documents.
        let analysisStepDocs = [];
        let pipelineDocs = [];
        if (context.files && context.files.length) {
            context.files.forEach((file) => {
                const fileAnalysisStepVersion = file.analysis_step_version;
                if (fileAnalysisStepVersion) {
                    const fileAnalysisStep = fileAnalysisStepVersion.analysis_step;
                    if (fileAnalysisStep) {
                        // Collect analysis step docs
                        if (fileAnalysisStep.documents && fileAnalysisStep.documents.length) {
                            analysisStepDocs = analysisStepDocs.concat(fileAnalysisStep.documents);
                        }

                        // Collect pipeline docs
                        if (fileAnalysisStep.pipelines && fileAnalysisStep.pipelines.length) {
                            fileAnalysisStep.pipelines.forEach((pipeline) => {
                                if (pipeline.documents && pipeline.documents.length) {
                                    pipelineDocs = pipelineDocs.concat(pipeline.documents);
                                }
                            });
                        }
                    }
                }
            });
        }
        analysisStepDocs = analysisStepDocs.length ? _.uniq(analysisStepDocs) : [];
        pipelineDocs = pipelineDocs.length ? _.uniq(pipelineDocs) : [];

        // Determine this experiment's ENCODE version.
        const encodevers = globals.encodeVersion(context);

        // Make list of statuses.
        const statuses = [{ status: context.status, title: 'Status' }];
        if (adminUser && context.internal_status) {
            statuses.push({ status: context.internal_status, title: 'Internal' });
        }

        // Make string of alternate accessions.
        const altacc = context.alternate_accessions ? context.alternate_accessions.join(', ') : undefined;

        // Make array of superseded_by accessions.
        let supersededBys = [];
        if (context.superseded_by && context.superseded_by.length) {
            supersededBys = context.superseded_by.map(supersededBy => globals.atIdToAccession(supersededBy));
        }

        // Make array of supersedes accessions.
        let supersedes = [];
        if (context.supersedes && context.supersedes.length) {
            supersedes = context.supersedes.map(supersede => globals.atIdToAccession(supersede));
        }

        // Determine whether the experiment is isogenic or anisogenic. No replication_type
        // indicates isogenic.
        const anisogenic = context.replication_type ? (anisogenicValues.indexOf(context.replication_type) !== -1) : false;

        // Get a list of related datasets, possibly filtering on their status.
        let seriesList = [];
        const loggedIn = !!(this.context.session && this.context.session['auth.userid']);
        if (context.related_series && context.related_series.length) {
            seriesList = _(context.related_series).filter(dataset => loggedIn || dataset.status === 'released');
        }

        // Set up the breadcrumbs.
        const assayTerm = context.assay_term_name ? 'assay_term_name' : 'assay_term_id';
        const assayName = context[assayTerm];
        const assayQuery = `${assayTerm}=${assayName}`;
        const organismNames = BiosampleOrganismNames(biosamples);
        let nameQuery = '';
        let nameTip = '';
        const names = organismNames.map((organismName, i) => {
            nameTip += (nameTip.length ? ' + ' : '') + organismName;
            nameQuery += `${nameQuery.length ? '&' : ''}replicates.library.biosample.donor.organism.scientific_name=${organismName}`;
            return <span key={i}>{i > 0 ? <span> + </span> : null}<i>{organismName}</i></span>;
        });
        const biosampleTermName = context.biosample_term_name;
        const biosampleTermQuery = biosampleTermName ? `biosample_term_name=${biosampleTermName}` : '';
        const crumbs = [
            { id: 'Experiments' },
            { id: assayName, query: assayQuery, tip: assayName },
            { id: names.length ? names : null, query: nameQuery, tip: nameTip },
            { id: biosampleTermName, query: biosampleTermQuery, tip: biosampleTermName },
        ];

        // Compile the document list.
        const combinedDocuments = _.uniq(documents.concat(
            biosampleDocs,
            libraryDocs,
            pipelineDocs,
            analysisStepDocs
        ));

        const experimentsUrl = `/search/?type=Experiment&possible_controls.accession=${context.accession}`;

        // Make a list of reference links, if any.
        const references = pubReferenceList(context.references);

        // Render tags badges.
        let tagBadges;
        if (context.internal_tags && context.internal_tags.length) {
            tagBadges = context.internal_tags.map(tag => <img key={tag} src={`/static/img/tag-${tag}.png`} alt={`${tag} tag`} />);
        }

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs root="/search/?type=Experiment" crumbs={crumbs} />
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
                                                <span>{` (${context.assay_title})`}</span>
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
                                                        &nbsp;
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

                                    {AssayDetails(replicates, this.libraryValues, librarySpecials, libraryComponents)}

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
                                                    {context.possible_controls.map(control => (
                                                        <li key={control['@id']} className="multi-comma">
                                                            <a href={control['@id']}>
                                                                {control.accession}
                                                            </a>
                                                        </li>
                                                    ))}
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
                                            <dd>{context.aliases.join(', ')}</dd>
                                        </div>
                                    : null}

                                    {context.date_submitted ?
                                        <div data-test="date-submitted">
                                            <dt>Date submitted</dt>
                                            <dd>{moment(context.date_submitted).format('MMMM D, YYYY')}</dd>
                                        </div>
                                    : null}

                                    {context.date_released ?
                                        <div data-test="date-released">
                                            <dt>Date released</dt>
                                            <dd>{moment(context.date_released).format('MMMM D, YYYY')}</dd>
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

                {Object.keys(condensedReplicates).length ?
                    <ReplicateTable condensedReplicates={condensedReplicates} replicationType={context.replication_type} />
                : null}

                {/* Display the file widget with the facet, graph, and tables */}
                <FileGallery context={context} encodevers={encodevers} anisogenic={anisogenic} />

                <FetchedItems {...this.props} url={experimentsUrl} Component={ControllingExperiments} />

                {combinedDocuments.length ?
                    <DocumentsPanelReq documents={combinedDocuments} />
                : null}
            </div>
        );
    }
}

ExperimentComponent.propTypes = {
    context: PropTypes.object.isRequired, // Experiment object to render on this page
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

ExperimentComponent.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
};

// Need to export for Jest tests.
const Experiment = auditDecor(ExperimentComponent);
export default Experiment;

globals.contentViews.register(Experiment, 'Experiment');


const replicateTableColumns = {
    biological_replicate_number: {
        title: 'Biological replicate',
        getValue: condensedReplicate => condensedReplicate[0].biological_replicate_number,
    },

    technical_replicate_number: {
        title: 'Technical replicate',
        getValue: condensedReplicate => condensedReplicate.map(replicate => replicate.technical_replicate_number).sort().join(),
    },

    summary: {
        title: 'Summary',
        display: (condensedReplicate) => {
            const replicate = condensedReplicate[0];

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
        sorter: false,
    },

    biosample_accession: {
        title: 'Biosample',
        display: (condensedReplicate) => {
            const replicate = condensedReplicate[0];
            if (replicate.library && replicate.library.biosample) {
                const biosample = replicate.library.biosample;
                return <a href={biosample['@id']} title={`View biosample ${biosample.accession}`}>{biosample.accession}</a>;
            }
            return null;
        },
        objSorter: (a, b) => {
            const aReplicate = a[0];
            const bReplicate = b[0];
            if ((aReplicate.library && aReplicate.library.biosample) && (bReplicate.library && bReplicate.library.biosample)) {
                const aAccession = aReplicate.library.biosample.accession;
                const bAccession = bReplicate.library.biosample.accession;
                return (aAccession < bAccession) ? -1 : ((aAccession > bAccession) ? 1 : 0);
            }
            return (aReplicate.library && aReplicate.library.biosample) ? -1 : ((bReplicate.library && bReplicate.library.biosample) ? 1 : 0);
        },
    },

    genetic_modification: {
        title: 'Modifications',
        display: (condensedReplicate) => {
            const replicate = condensedReplicate[0];
            const gms = replicate.library && replicate.library.biosample && replicate.library.biosample.applied_modifications;
            if (gms && gms.length) {
                return (
                    <span>
                        {gms.map((gm, i) => (
                            <span key={gm.uuid}>
                                {i > 0 ? <span>, </span> : null}
                                <a href={gm['@id']} title={`View genetic modification ${gm.accession}`}>{gm.accession}</a>
                            </span>
                        ))}
                    </span>
                );
            }
            return null;
        },
        hide: list => _(list).all((condensedReplicate) => {
            const replicate = condensedReplicate[0];
            return !(replicate.library && replicate.library.biosample && replicate.library.biosample.applied_modifications && replicate.library.biosample.applied_modifications.length);
        }),
    },

    antibody_accession: {
        title: 'Antibody',
        display: (condensedReplicate) => {
            const replicate = condensedReplicate[0];
            if (replicate.antibody) {
                return <a href={replicate.antibody['@id']} title={`View antibody ${replicate.antibody.accession}`}>{replicate.antibody.accession}</a>;
            }
            return null;
        },
        objSorter: (a, b) => {
            const aReplicate = a[0];
            const bReplicate = b[0];
            if (aReplicate.antibody && bReplicate.antibody) {
                return (aReplicate.antibody.accession < bReplicate.antibody.accession) ? -1 : ((aReplicate.antibody.accession > bReplicate.antibody.accession) ? 1 : 0);
            }
            return (aReplicate.antibody) ? -1 : ((bReplicate.antibody) ? 1 : 0);
        },
        hide: list => _(list).all(condensedReplicate => !condensedReplicate[0].antibody),
    },

    library: {
        title: 'Library',
        getValue: condensedReplicate => (condensedReplicate[0].library ? condensedReplicate[0].library.accession : ''),
    },
};

// Display the table of replicates
const ReplicateTable = (props) => {
    let tableTitle;
    const { condensedReplicates, replicationType } = props;

    // Determine replicate table title based on the replicate type. Also override the biosample replicate column title
    if (replicationType === 'anisogenic') {
        tableTitle = 'Anisogenic replicates';
        replicateTableColumns.biological_replicate_number.title = 'Anisogenic replicate';
    } else if (replicationType === 'isogenic') {
        tableTitle = 'Isogenic replicates';
        replicateTableColumns.biological_replicate_number.title = 'Isogenic replicate';
    } else {
        tableTitle = 'Replicates';
        replicateTableColumns.biological_replicate_number.title = 'Biological replicate';
    }

    return (
        <SortTablePanel title={tableTitle}>
            <SortTable list={condensedReplicates} columns={replicateTableColumns} />
        </SortTablePanel>
    );
};

ReplicateTable.propTypes = {
    condensedReplicates: PropTypes.array.isRequired, // Condensed 'array' of replicate objects
    replicationType: PropTypes.string, // Type of replicate so we can tell what's isongenic/anisogenic/whatnot
};


// Display a list of datasets related to the experiment
class RelatedSeriesList extends React.Component {
    constructor() {
        super();

        // Initial component state.
        this.state = {
            currInfoItem: '', // Accession of item whose detail info appears; empty string to display no detail info
            touchScreen: false, // True if we know we got a touch event; ignore clicks without touch indiciation
            clicked: false, // True if info button was clicked (vs hovered)
        };

        this.handleInfoHover = this.handleInfoHover.bind(this);
        this.handleInfoClick = this.handleInfoClick.bind(this);
    }

    // Handle the mouse entering/existing an info icon. Ignore if the info tooltip is open because the icon had
    // been clicked. 'entering' is true if the mouse entered the icon, and false if exiting.
    handleInfoHover(series, entering) {
        if (!this.state.clicked) {
            this.setState({ currInfoItem: entering ? series.accession : '' });
        }
    }

    // Handle click in info icon by setting the currInfoItem state to the accession of the item to display.
    // If opening the tooltip, note that hover events should be ignored until the icon is clicked to close the tooltip.
    handleInfoClick(series, touch) {
        let currTouchScreen = this.state.touchScreen;

        // Remember if we know we've had a touch event
        if (touch && !currTouchScreen) {
            currTouchScreen = true;
            this.setState({ touchScreen: true });
        }

        // Now handle the click. Ignore if we know we have a touch screen, but this wasn't a touch event
        if (!currTouchScreen || touch) {
            if (this.state.currInfoItem === series.accession && this.state.clicked) {
                this.setState({ currInfoItem: '', clicked: false });
            } else {
                this.setState({ currInfoItem: series.accession, clicked: true });
            }
        }
    }

    render() {
        const seriesList = this.props.seriesList;

        return (
            <span>
                {seriesList.map((series, i) => (
                    <span key={series.uuid}>
                        {i > 0 ? <span>, </span> : null}
                        <RelatedSeriesItem
                            series={series}
                            detailOpen={this.state.currInfoItem === series.accession}
                            handleInfoHover={this.handleInfoHover}
                            handleInfoClick={this.handleInfoClick}
                        />
                    </span>
                ))}
            </span>
        );
    }
}

RelatedSeriesList.propTypes = {
    seriesList: PropTypes.array.isRequired, // Array of Series dataset objects to display
};


// Display a one dataset related to the experiment
class RelatedSeriesItem extends React.Component {
    constructor() {
        super();

        // Intialize component state.
        this.state = {
            touchOn: false, // True if icon has been touched
        };

        // Bind `this` to non-React methods.
        this.touchStart = this.touchStart.bind(this);
        this.handleInfoHoverIn = this.handleInfoHoverIn.bind(this);
        this.handleInfoHoverOut = this.handleInfoHoverOut.bind(this);
        this.handleInfoClick = this.handleInfoClick.bind(this);
    }

    // Touch screen
    touchStart() {
        this.setState({ touchOn: !this.state.touchOn });
        this.props.handleInfoClick(this.props.series, true);
    }

    handleInfoHoverIn() {
        this.props.handleInfoHover(this.props.series, true);
    }

    handleInfoHoverOut() {
        this.props.handleInfoHover(this.props.series, false);
    }

    handleInfoClick() {
        this.props.handleInfoClick(this.props.series, false);
    }

    render() {
        const { series, detailOpen } = this.props;

        return (
            <span>
                <a href={series['@id']} title={`View page for series dataset ${series.accession}`}>{series.accession}</a>&nbsp;
                <div className="tooltip-trigger">
                    <i
                        className="icon icon-info-circle"
                        onMouseEnter={this.handleInfoHoverIn}
                        onMouseLeave={this.handleInfoHoverOut}
                        onClick={this.handleInfoClick}
                        onTouchStart={this.touchStart}
                    />
                    <div className={`tooltip bottom${detailOpen ? ' tooltip-open' : ''}`}>
                        <div className="tooltip-arrow" />
                        <div className="tooltip-inner">
                            {series.description ? <span>{series.description}</span> : <em>No description available</em>}
                        </div>
                    </div>
                </div>
            </span>
        );
    }
}

RelatedSeriesItem.propTypes = {
    series: PropTypes.object.isRequired, // Series object to display
    detailOpen: PropTypes.bool, // TRUE to open the series' detail tooltip
    handleInfoClick: PropTypes.func, // Function to call to handle click in info icon
    handleInfoHover: PropTypes.func, // Function to call when mouse enters or leaves info icon
};
