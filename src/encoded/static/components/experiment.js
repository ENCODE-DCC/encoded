import React from 'react';
import PropTypes from 'prop-types';
import dayjs from 'dayjs';
import _ from 'underscore';
import { Panel, PanelBody } from '../libs/ui/panel';
import { auditDecor } from './audit';
import { DocumentsPanelReq } from './doc';
import * as globals from './globals';
import { DbxrefList } from './dbxref';
import { FetchedItems } from './fetched';
import { FileGallery } from './filegallery';
import { ProjectBadge } from './image';
import { singleTreatment, ItemAccessories, InternalTags, TopAccessories } from './objectutils';
import pubReferenceList from './reference';
import { SortTablePanel, SortTable } from './sorttable';
import Status from './status';
import {
    AwardRef,
    BiosampleSummaryString,
    BiosampleOrganismNames,
    CollectBiosampleDocs,
    ControllingExperiments,
    DoiRef,
    ExperimentTable,
    ReplacementAccessions,
} from './typeutils';
import Tooltip from '../libs/ui/tooltip';
import getNumberWithOrdinal from '../libs/ordinal_suffix';


/**
 * List of displayable library properties, the title to display it with, and the value to use for
 * its data-test attribute.
 */
const displayedLibraryProperties = [
    { property: 'treatments', title: 'Treatments', test: 'treatments' },
    { property: 'nucleic_acid_term_name', title: 'Nucleic acid type', test: 'nucleicacid' },
    { property: 'rna_integrity_number', title: 'RNA integrity number', test: 'rnaintegritynumber' },
    { property: 'depleted_in_term_name', title: 'Depleted in', test: 'depletedin' },
    { property: 'nucleic_acid_starting_quantity', title: 'Library starting quantity', test: 'startingquantity' },
    { property: 'size_range', title: 'Size range', test: 'sizerange' },
    { property: 'average_fragment_size', title: 'Average fragment size', test: 'avgfragmentsize' },
    { property: 'lysis_method', title: 'Lysis method', test: 'lysismethod' },
    { property: 'extraction_method', title: 'Extraction method', test: 'extractionmethod' },
    { property: 'fragmentation_methods', title: 'Fragmentation methods', test: 'fragmentationmethod' },
    { property: 'library_size_selection_method', title: 'Size selection method', test: 'sizeselectionmethod' },
    { property: 'construction_method', title: 'Library construction method', test: 'libraryconstructionmethod' },
    { property: 'strand_specificity', title: 'Strand specificity', test: 'strandspecificity' },
    { property: 'spikeins_used', title: 'Spike-ins datasets', test: 'spikeins' },
];


/**
 * Specifies the property extractors for each library property that doesn't get displayed directly
 * as text, maybe because an object represents the value or the value needs some other property to
 * render. Each property extractor gets selected with the corresponding library property name, and
 * each returns a one- or two-property object. All must return `libraryPropertyString` which either
 * contains the text to display, or a string uniquely identifying that property's value between
 * replicates, in which case `libraryPropertyComponent` gets returned which contains the JSX to
 * render the property's value in a complex way, e.g. a link, italic text, etc. Property extractors
 * must return an object, but they set `libraryPropertyString` to null to indicate no value to
 * display.
 */
const libraryPropertyExtractors = {
    treatments: (library) => {
        // Collect and combine treatments from the library as well as the library's biosample.
        let libraryTreatments = [];

        const { treatments } = library;
        if (treatments && treatments.length > 0) {
            libraryTreatments = libraryTreatments.concat(treatments.map((treatment) => singleTreatment(treatment)));
        }
        const biosampleTreatments = library.biosample && library.biosample.treatments;
        if (biosampleTreatments && biosampleTreatments.length > 0) {
            libraryTreatments = libraryTreatments.concat(biosampleTreatments.map((treatment) => singleTreatment(treatment)));
        }

        return { libraryPropertyString: libraryTreatments.join(', ') };
    },

    nucleic_acid_starting_quantity: (library) => {
        let libraryPropertyString = null;
        let libraryPropertyComponent = null;
        const quantity = library.nucleic_acid_starting_quantity;
        if (quantity) {
            const units = library.nucleic_acid_starting_quantity_units;
            libraryPropertyString = `${quantity}-${units}`;
            libraryPropertyComponent = <span>{quantity}<span className="unit">{units}</span></span>;
        }
        return { libraryPropertyString, libraryPropertyComponent };
    },

    size_range: (library, replicates) => {
        // Always display replicate if any other replicate libraries have `average_fragment_size`.
        const libraryPropertyForceRepDisplay = replicates.some((replicate) => replicate.library && replicate.library.average_fragment_size);
        return { libraryPropertyString: library.size_range, libraryPropertyForceRepDisplay };
    },

    average_fragment_size: (library, replicates) => {
        // Always display replicate if any other replicate libraries have `size_range`.
        const libraryPropertyForceRepDisplay = replicates.some((replicate) => replicate.library && replicate.library.size_range);
        return { libraryPropertyString: library.average_fragment_size, libraryPropertyForceRepDisplay };
    },

    depleted_in_term_name: (library) => {
        const terms = library.depleted_in_term_name;
        let libraryPropertyString = null;
        if (terms && terms.length > 0) {
            libraryPropertyString = terms.sort().join(', ');
        }
        return { libraryPropertyString };
    },

    spikeins_used: (library) => {
        const spikeins = library.spikeins_used;
        let libraryPropertyString = null;
        let libraryPropertyComponent = null;
        if (spikeins && spikeins.length > 0) {
            libraryPropertyString = spikeins.sort().join();
            libraryPropertyComponent = (
                spikeins.map((spikeinsAtId, i) => (
                    <span key={i}>
                        {i > 0 ? ', ' : ''}
                        <a href={spikeinsAtId}>{globals.atIdToAccession(spikeinsAtId)}</a>
                    </span>
                ))
            );
        }
        return { libraryPropertyString, libraryPropertyComponent };
    },

    fragmentation_methods: (library) => {
        const fragMethods = library.fragmentation_methods;
        let libraryPropertyString = null;
        if (fragMethods && fragMethods.length > 0) {
            libraryPropertyString = fragMethods.sort().join(', ');
        }
        return { libraryPropertyString };
    },

    strand_specificity: (library) => {
        const libraryPropertyString = library.strand_specificity;
        return { libraryPropertyString };
    },
};


/**
 * Render the properties from all the libraries of a given set of replicates associated with a
 * dataset. If all replicate libraries share the same property values, they get presented as one
 * value. Where different replicate libraries have different values for the same property, every
 * value gets displayed along with an indication of what biological and technical replicate each
 * came from.
 */
const LibraryProperties = ({ replicates }) => {
    if (replicates && replicates.length > 0) {
        // First collect the values and optional components for all displayable replicate library
        // properties. The product of this loop is `libraryPropertyDisplays` containing an object
        // property for every displayable library property.
        const libraryPropertyDisplays = {};
        replicates.forEach((replicate) => {
            if (replicate.library) {
                // For each possible displayed library property within the current replicate,
                // retrieve a string representing its value as well as an optional JSX component
                // from the replicate library and add them along with the corresponding replicate
                // numbers to `libraryPropertyDisplays`, and if a property requires replicate
                // strings displayed.
                displayedLibraryProperties.forEach(({ property }) => {
                    let libraryPropertyString = '';
                    let libraryPropertyComponent = null;
                    let libraryPropertyForceRepDisplay = false;
                    if (!libraryPropertyDisplays[property]) {
                        libraryPropertyDisplays[property] = [];
                    }

                    // Some library properties have simple values you can display directly.
                    // Others have more complex values that need a method to extract the value.
                    // The existence of a property extractor for that property determines which
                    // case we're dealing with.
                    const libraryPropertyRawValue = replicate.library[property];
                    if (libraryPropertyExtractors[property]) {
                        // Library property has a property extractor.
                        ({ libraryPropertyString, libraryPropertyComponent, libraryPropertyForceRepDisplay } = libraryPropertyExtractors[property](replicate.library, replicates));
                    } else if (typeof libraryPropertyRawValue === 'string' || typeof libraryPropertyRawValue === 'number') {
                        // Library property is a simple value, so just use it directly.
                        libraryPropertyString = libraryPropertyRawValue;
                    } // Else ignore the value; might need property extractor we haven't defined.

                    // Add to the list of values and JSX components we're accumulating for the
                    // current library property.
                    if (libraryPropertyString) {
                        libraryPropertyDisplays[property].push({
                            value: libraryPropertyString,
                            component: libraryPropertyComponent,
                            forceRepDisplay: libraryPropertyForceRepDisplay,
                            bioRep: replicate.biological_replicate_number,
                            techRep: replicate.technical_replicate_number,
                        });
                    }
                });
            }
        });

        // Generate JSX for all the collected library property strings.
        const renderedLibraryProperties = [];
        displayedLibraryProperties.forEach((displayedLibraryProperty) => {
            const libraryPropertyElements = libraryPropertyDisplays[displayedLibraryProperty.property];
            if (libraryPropertyElements && libraryPropertyElements.length > 0) {
                const homogeneous = !libraryPropertyElements.some((libraryProperty) => libraryProperty.value !== libraryPropertyElements[0].value);
                const forcedRepDisplay = libraryPropertyElements.some((libraryProperty) => libraryProperty.forceRepDisplay);
                const isStrandSpecificity = displayedLibraryProperty.property === 'strand_specificity';
                if (!isStrandSpecificity && (!homogeneous || forcedRepDisplay)) {
                    // More than one value collected for this property, and at least one had a
                    // different value from the others. Display all values with a replicate
                    // identifier for each one.
                    renderedLibraryProperties.push(
                        <div key={displayedLibraryProperty.property} data-test={displayedLibraryProperty.test}>
                            <dt>{displayedLibraryProperty.title}</dt>
                            <dd>
                                {libraryPropertyElements.map((libraryPropertyElement) => {
                                    const replicateIdentifier = `[${libraryPropertyElement.bioRep}-${libraryPropertyElement.techRep}]`;
                                    return (
                                        <span key={replicateIdentifier} className="line-item">
                                            {libraryPropertyElement.component || libraryPropertyElement.value} {replicateIdentifier}
                                        </span>
                                    );
                                })}
                            </dd>
                        </div>
                    );
                } else {
                    let strandSpecificity = null;

                    if (isStrandSpecificity) {
                        const strandSpecificValues = libraryPropertyElements.map((element) => element.value);
                        const strandSpecificityFirstValue = strandSpecificValues[0];

                        if (strandSpecificValues.every((value) => value === strandSpecificityFirstValue)) {
                            strandSpecificity = strandSpecificityFirstValue === 'unstranded' ? strandSpecificityFirstValue : `Strand-specific${strandSpecificityFirstValue === 'strand-specific' ? '' : ` (${strandSpecificityFirstValue})`}`;
                        } else {
                            strandSpecificity = 'Strand-specific (mixed)';
                        }
                    }

                    // Only one value collected for this property, or more than one but all have
                    // the same value, so just display the one value without a replicate
                    // identifier.
                    renderedLibraryProperties.push(
                        <div key={displayedLibraryProperty.property} data-test={displayedLibraryProperty.test}>
                            <dt>{displayedLibraryProperty.title}</dt>
                            <dd>{strandSpecificity || libraryPropertyElements[0].component || libraryPropertyElements[0].value}</dd>
                        </div>
                    );
                }
            }
        });
        return renderedLibraryProperties;
    }
    return null;
};

LibraryProperties.propTypes = {
    /** Array of replicates whose library details need display */
    replicates: PropTypes.array,
};

LibraryProperties.defaultProps = {
    replicates: [],
};


/**
 * Display submitter comments from all libraries in all the given replicates.
 */
const LibrarySubmitterComments = ({ replicates }) => {
    // Make a list of all libraries in all replicates, de-duped.
    const libraries = _.uniq(replicates.reduce((libraryAcc, replicate) => (replicate.library ? libraryAcc.concat([replicate.library]) : libraryAcc), []), (library) => library['@id']);
    if (libraries.length > 0) {
        return libraries.map((library) => {
            if (library.submitter_comment) {
                return (
                    <div key={library['@id']} data-test={`submittercomment${library['@id']}`}>
                        <dt>{library.accession} submitter comment</dt>
                        <dd>{library.submitter_comment}</dd>
                    </div>
                );
            }
            return null;
        });
    }
    return null;
};

LibrarySubmitterComments.propTypes = {
    /** Replicates containing libraries whose comments we display */
    replicates: PropTypes.array.isRequired,
};


/**
 * Display, as one element of a "key-value" definition list, all the `construction_platform`
 * properties in a dataset's replicates' library.
 */
const DatasetConstructionPlatform = ({ context }) => {
    // Collect the library construction platforms from all the dataset replicates.
    const constructionPlatforms = context.replicates.reduce((platforms, replicate) => {
        // We easily have duplicates, so only add the replicate library platform if we haven't
        // already seen it.
        if ((replicate.library && replicate.library.construction_platform) &&
            (platforms.findIndex((platform) => platform['@id'] === replicate.library.construction_platform['@id']) === -1)) {
            return platforms.concat(replicate.library.construction_platform);
        }
        return platforms;
    }, []);

    if (constructionPlatforms.length > 0) {
        return (
            <div data-test="constructionplatform">
                <dt>Library construction platform</dt>
                <dd>
                    {constructionPlatforms.map((platform, i) => (
                        <React.Fragment key={platform['@id']}>
                            {i > 0 ? <span>, </span> : null}
                            <a href={platform['@id']}>{platform.term_name}</a>
                        </React.Fragment>
                    ))}
                </dd>
            </div>
        );
    }
    return null;
};

DatasetConstructionPlatform.propTypes = {
    /** Dataset object potentially containing construction platform */
    context: PropTypes.object.isRequired,
};


/**
 * Renders Experiment, FunctionalCharacterizationExperiment, and TransgenicEnhancerExperiment objects.
 */
const ExperimentComponent = ({ context, auditIndicators, auditDetail }, reactContext) => {
    let condensedReplicates = [];
    const loggedIn = !!(reactContext.session && reactContext.session['auth.userid']);
    const adminUser = !!(reactContext.session_properties && reactContext.session_properties.admin);
    const itemClass = globals.itemClass(context, 'view-item');

    // Determine whether object is Experiment, FunctionalCharacterizationExperiment, SingleCellUnit or TransgenicEnhancerExperiment.
    const experimentType = context['@type'][0];
    const isFunctionalExperiment = experimentType === 'FunctionalCharacterizationExperiment';
    const isSingleCell = experimentType === 'SingleCellUnit';
    const isEnhancerExperiment = experimentType === 'TransgenicEnhancerExperiment';
    let displayType;
    let displayTypeBreadcrumbs;
    if (isFunctionalExperiment) {
        displayTypeBreadcrumbs = 'Functional Characterization Experiments';
        displayType = 'Functional Characterization Experiment';
    } else if (isEnhancerExperiment) {
        displayTypeBreadcrumbs = 'Transgenic Enhancer Experiments';
        displayType = 'Transgenic Enhancer Experiment';
    } else if (isSingleCell) {
        displayTypeBreadcrumbs = 'Single Cell Units';
        displayType = 'Single Cell Unit';
    } else {
        displayTypeBreadcrumbs = 'Experiments';
        displayType = 'Experiment';
    }

    const replicates = context.replicates && context.replicates.length > 0 ? context.replicates : [];
    if (replicates.length > 0) {
        // Make an array of arrays of replicates, called “condensed replicates" here. Each top-
        // level array element represents a library linked to by the replicates inside that
        // array. Only the first replicate in each library array gets displayed in the table.
        const condensedReplicatesKeyed = _(replicates).groupBy((replicate) => (replicate.library ? replicate.library['@id'] : replicate.uuid));
        if (Object.keys(condensedReplicatesKeyed).length > 0) {
            condensedReplicates = _.toArray(condensedReplicatesKeyed);
        }
    }

    // Collect all dbxrefs. Filter out SCREEN and Factorbook in separate arrays. Only the first SCREEN and Factorbook dbxref will be displayed.
    const groupedDbxrefs = context.dbxrefs && context.dbxrefs.length > 0 ?
        _(context.dbxrefs).groupBy((dbxref) => {
            if (dbxref.startsWith('SCREEN')) {
                return 'SCREEN';
            }
            if (dbxref.startsWith('FactorBook')) {
                return 'FactorBook';
            }
            return 'normal';
        })
    : {};
    // Result -- if nothing exists in any of these three categories, then
    // that category’s key doesn't exist.

    // Collect all documents from the experiment itself.
    const documents = (context.documents && context.documents.length > 0) ? context.documents : [];

    // Make array of all replicate biosamples, not including biosample-less replicates. Also
    // collect up library documents, this only apply to Experiment and FunctionalCharacterizationExperiment.
    // collect biosample characterizations for TransgenicEnhancerExperiment only.
    const libraryDocs = [];
    let biosamples = [];
    let biosampleCharacterizations = [];
    const appliedModifications = [];
    if (isEnhancerExperiment) {
        if (context.biosamples) {
            biosamples = (context.biosamples.length > 0) ? context.biosamples : [];
        }
        if (biosamples.length > 0) {
            biosamples.forEach((biosample) => {
                if (biosample.characterizations && biosample.characterizations.length > 0) {
                    biosampleCharacterizations = biosampleCharacterizations.concat(biosample.characterizations.map((bc) => bc['@id']));
                }
                if (biosample.applied_modifications && biosample.applied_modifications.length > 0) {
                    appliedModifications.push(...biosample.applied_modifications);
                }
            });
        }
    } else if (!isEnhancerExperiment) {
        if (replicates.length > 0) {
            biosamples = _.compact(replicates.map((replicate) => {
                if (replicate.library) {
                    if (replicate.library.documents && replicate.library.documents.length > 0) {
                        Array.prototype.push.apply(libraryDocs, replicate.library.documents);
                    }

                    return replicate.library.biosample;
                }
                return null;
            }));
        }
    }

    // Create platforms array from file platforms; ignore duplicate platforms.
    const platforms = {};
    if (context.files && context.files.length > 0) {
        context.files.forEach((file) => {
            if (file.platform && file.dataset === context['@id']) {
                platforms[file.platform['@id']] = file.platform;
            }
        });
    }

    // Collect biosample docs.
    // Collect plasmid maps from applied_modifications documents.
    let biosampleDocs = [];
    let plasmidMapDocs = [];
    biosamples.forEach((biosample) => {
        biosampleDocs = biosampleDocs.concat(CollectBiosampleDocs(biosample));
        if (biosample.part_of) {
            biosampleDocs = biosampleDocs.concat(CollectBiosampleDocs(biosample.part_of));
        }
        if (biosample.applied_modifications && biosample.applied_modifications.length > 0) {
            biosample.applied_modifications.forEach((am) => {
                const plasmidMapDoc = (am.documents && am.documents.length > 0) ? am.documents.filter((doc) => doc.document_type === 'plasmid map').map((doc) => doc['@id']) : [];
                plasmidMapDocs = plasmidMapDocs.concat(plasmidMapDoc);
            });
        }
        plasmidMapDocs = _.uniq(plasmidMapDocs);
    });

    // Collect pipeline-related documents.
    let analysisStepDocs = [];
    let pipelineDocs = [];
    if (context.files && context.files.length > 0) {
        context.files.forEach((file) => {
            const fileAnalysisStepVersion = file.analysis_step_version;
            if (fileAnalysisStepVersion) {
                const fileAnalysisStep = fileAnalysisStepVersion.analysis_step;
                if (fileAnalysisStep) {
                    // Collect analysis step docs
                    if (fileAnalysisStep.documents && fileAnalysisStep.documents.length > 0) {
                        analysisStepDocs = analysisStepDocs.concat(fileAnalysisStep.documents);
                    }

                    // Collect pipeline docs
                    if (fileAnalysisStep.pipelines && fileAnalysisStep.pipelines.length > 0) {
                        fileAnalysisStep.pipelines.forEach((pipeline) => {
                            if (pipeline.documents && pipeline.documents.length > 0) {
                                pipelineDocs = pipelineDocs.concat(pipeline.documents);
                            }
                        });
                    }
                }
            }
        });
    }
    analysisStepDocs = analysisStepDocs.length > 0 ? _.uniq(analysisStepDocs) : [];
    pipelineDocs = pipelineDocs.length > 0 ? _.uniq(pipelineDocs) : [];

    // Make list of statuses.
    const statuses = [{ status: context.status, title: 'Status' }];
    if (adminUser && context.internal_status) {
        statuses.push({ status: context.internal_status, title: 'Internal' });
    }

    // Get a map of related datasets, possibly filtering on their status and
    // categorized by their type.
    let seriesMap = {};
    if (context.related_series && context.related_series.length > 0) {
        seriesMap = _.groupBy(
            context.related_series.filter(
                (dataset) => loggedIn || dataset.status === 'released'
            ),
            (series) => series['@type'][0]
        );
    }

    // Set up the breadcrumbs.
    const assayTerm = context.assay_term_name ? 'assay_term_name' : 'assay_term_id';
    const assayName = context[assayTerm];
    const assayQuery = `${assayTerm}=${assayName}`;
    const organismNames = BiosampleOrganismNames(biosamples);
    let nameQuery = '';
    let nameTip = '';
    const names = organismNames.map((organismName, i) => {
        nameTip += (nameTip.length > 0 ? ' + ' : '') + organismName;
        if (isEnhancerExperiment) {
            nameQuery += `${nameQuery.length > 0 ? '&' : ''}biosamples.donor.organism.scientific_name=${organismName}`;
        } else {
            nameQuery += `${nameQuery.length > 0 ? '&' : ''}replicates.library.biosample.donor.organism.scientific_name=${organismName}`;
        }
        return <span key={i}>{i > 0 ? <span> + </span> : null}<i>{organismName}</i></span>;
    });
    const crumbs = [
        { id: displayTypeBreadcrumbs },
        { id: assayName, query: assayQuery, tip: assayName },
        { id: names.length > 0 ? names : null, query: nameQuery, tip: nameTip },
    ];
    if (context.biosample_ontology) {
        const biosampleTermName = context.biosample_ontology.term_name;
        const biosampleTermQuery = `biosample_ontology.term_name=${biosampleTermName}`;
        crumbs.push({ id: biosampleTermName, query: biosampleTermQuery, tip: biosampleTermName });
    }

    // Compile the document list.
    const combinedDocuments = _.uniq(documents.concat(
        biosampleDocs,
        libraryDocs,
        pipelineDocs,
        analysisStepDocs
    ));

    const experimentsUrl = `/search/?type=Experiment&possible_controls.accession=${context.accession}`;
    const fcexperimentsUrl = `/search/?type=FunctionalCharacterizationExperiment&possible_controls.accession=${context.accession}`;
    const fcelementsmappingUrl = `/search/?type=FunctionalCharacterizationExperiment&elements_mapping=${context['@id']}`;
    const fcelementscloningUrl = `/search/?type=FunctionalCharacterizationExperiment&elements_cloning=${context['@id']}`;
    const singlecellunitsUrl = `/search/?type=SingleCellUnit&possible_controls.accession=${context.accession}`;


    // Make a list of reference links, if any.
    const references = pubReferenceList(context.references);

    return (
        <div className={itemClass}>
            <header>
                <TopAccessories context={context} crumbs={crumbs} />
                <h1>{displayType} summary for {context.accession}</h1>
                <DoiRef context={context} />
                <ReplacementAccessions context={context} />
                <ItemAccessories item={context} audit={{ auditIndicators, auditId: 'experiment-audit' }} hasCartControls />
            </header>
            {auditDetail(context.audit, 'experiment-audit', { session: reactContext.session, sessionProperties: reactContext.session_properties, except: context['@id'] })}
            <Panel>
                <PanelBody addClasses="panel__split">
                    <div className="panel__split-element">
                        <div className="panel__split-heading panel__split-heading--experiment">
                            <h4>Summary</h4>
                        </div>
                        <dl className="key-value">
                            <div data-test="status">
                                <dt>Status</dt>
                                <dd>
                                    <Status item={context} css="dd-status" title="Experiment status" inline />
                                    {adminUser && context.internal_status ?
                                        <Status item={context.internal_status} title="Internal status" inline />
                                    : null}
                                </dd>
                            </div>

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
                                <>
                                    <div data-test="target">
                                        <dt>Target</dt>
                                        <dd><a href={context.target['@id']}>{context.target.label}</a></dd>
                                    </div>
                                    {context.target_expression_range_minimum !== undefined && context.target_expression_range_maximum !== undefined ?
                                        <div data-test="target-min">
                                            <dt>Target expression range minimum - maximum</dt>
                                            <dd>{context.target_expression_range_minimum}% &ndash; {context.target_expression_range_maximum}%</dd>
                                        </div>
                                    : null}
                                    {context.target_expression_percentile !== undefined ?
                                        <div data-test="target-percentile">
                                            <dt>Target expression percentile</dt>
                                            <dd>{context.target_expression_percentile}</dd>
                                        </div>
                                    : null}
                                </>
                            : null}

                            {context.control_type ?
                                <div data-test="control_type">
                                    <dt>Control type</dt>
                                    <dd>{context.control_type}</dd>
                                </div>
                            : null}

                            {isEnhancerExperiment && biosamples.length > 0 ?
                                <div data-test="biosamples">
                                    <dt>Biosample</dt>
                                    <dd>
                                        <ul>
                                            {biosamples.map((biosample) => (
                                                <li key={biosample['@id']}>
                                                    <a href={biosample['@id']}>
                                                        {biosample.accession}
                                                    </a>
                                                </li>
                                            ))}
                                        </ul>
                                    </dd>
                                </div>
                            : null}

                            {context.biosample_summary ?
                                <div data-test="biosample-summary">
                                    <dt>Biosample summary</dt>
                                    <dd>
                                        {organismNames.length > 0 ?
                                            <span>
                                                {organismNames.map((organismName, i) => (
                                                    <span key={organismName}>
                                                        {i > 0 ? <span> and </span> : null}
                                                        <i>{organismName}</i>
                                                    </span>
                                                ))}
                                                &nbsp;
                                            </span>
                                        : null}
                                        <span>{context.biosample_summary}</span>
                                    </dd>
                                </div>
                            : null}

                            {context.biosample_ontology ?
                                <div data-test="biosample-type">
                                    <dt>Biosample Type</dt>
                                    <dd>{context.biosample_ontology.classification}</dd>
                                </div>
                            : null}

                            {context.examined_loci && context.examined_loci.length > 0 ?
                                <div data-test="examined-loci">
                                    <dt>Examined Loci</dt>
                                    <dd>
                                        {/* A user can have a loci repeat. Therefore, uuid alone is not sufficient as an identifier */}
                                        {context.examined_loci.map((loci, i) => (
                                            loci.gene ?
                                                <span key={`${loci.gene.uuid}-${i}`}>
                                                    {i > 0 ? <span>, </span> : null}
                                                    <a href={loci.gene['@id']}>{loci.gene.symbol}</a>
                                                    {/* 0 is falsy but we still want it to display, so 0 is explicitly checked for */}
                                                    {loci.expression_percentile || loci.expression_percentile === 0 ? <span>{' '}({getNumberWithOrdinal(loci.expression_percentile)} percentile)</span> : null}
                                                    {(loci.expression_range_maximum && loci.expression_range_minimum) || (loci.expression_range_maximum === 0 || loci.expression_range_minimum === 0) ? <span>{' '}({loci.expression_range_minimum}-{loci.expression_range_maximum}%)</span> : null}
                                                    {loci.expression_measurement_method || loci.expression_measurement_method === 0 ? <span>{' by '}{loci.expression_measurement_method}</span> : null}
                                                </span>
                                            : null
                                        ))}
                                    </dd>
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

                            {/* Display library properties for Experiment, FunctionalCharacterizationExperiment, and SingleCellUnit only. */}
                            {!isEnhancerExperiment ?
                                <>
                                    <LibraryProperties replicates={replicates} />
                                    <DatasetConstructionPlatform context={context} />
                                </>
                            : null}


                            {Object.keys(platforms).length > 0 ?
                                <div data-test="platform">
                                    <dt>Platform</dt>
                                    <dd>
                                        {Object.keys(platforms).map((platformId, i) => (
                                            <span key={platformId}>
                                                {i > 0 ? <span>, </span> : null}
                                                <a className="stacked-link" href={platformId}>{platforms[platformId].title}</a>
                                            </span>
                                        ))}
                                    </dd>
                                </div>
                            : null}

                            {context.possible_controls && context.possible_controls.length > 0 ?
                                <div data-test="possible-controls">
                                    <dt>Controls</dt>
                                    <dd>
                                        <ul>
                                            {context.possible_controls.map((control) => (
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

                            {context.elements_references && context.elements_references.length > 0 ?
                                <div data-test="elements-references">
                                    <dt>Elements references</dt>
                                    <dd>
                                        <ul>
                                            {context.elements_references.map((reference) => (
                                                <li key={reference['@id']} className="multi-comma">
                                                    <a href={reference['@id']}>
                                                        {reference.accession}
                                                    </a>
                                                </li>
                                            ))}
                                        </ul>
                                    </dd>
                                </div>
                            : null}

                            {context.elements_mapping ?
                                <div data-test="elements-mapping">
                                    <dt>Elements mapping</dt>
                                    <dd><a href={context.elements_mapping}>{globals.atIdToAccession(context.elements_mapping)}</a></dd>
                                </div>
                            : null}

                            {context.elements_cloning ?
                                <div data-test="elements-cloning">
                                    <dt>Elements cloning</dt>
                                    <dd><a href={context.elements_cloning}>{globals.atIdToAccession(context.elements_cloning)}</a></dd>
                                </div>
                            : null}

                            {appliedModifications.length > 0 ?
                                <div data-test="applied-modifications">
                                    <dt>Genetic modification</dt>
                                    <dd>
                                        <ul>
                                            {appliedModifications.map((am) => (
                                                <li key={am}>
                                                    <a href={am}>
                                                        {am.split('/', 3)[2]}
                                                    </a>
                                                </li>
                                            ))}
                                        </ul>
                                    </dd>
                                </div>
                            : null}

                            {context.element_location ?
                                <div data-test="element-location">
                                    <dt>Element location</dt>
                                    <dd>{`${context.element_location.assembly} ${context.element_location.chromosome}:${context.element_location.start}-${context.element_location.end}`}</dd>
                                </div>
                            : null}

                            {context.tissue_with_enhancer_activity && context.tissue_with_enhancer_activity.length > 0 ?
                                <div data-test="tissue-with-enhancer-activity">
                                    <dt>Tissues with enhancer activity</dt>
                                    <dd>
                                        <ul>
                                            {context.tissue_with_enhancer_activity.map((tissue) => (
                                                <li key={tissue}>
                                                    <span>{tissue}</span>
                                                </li>
                                            ))}
                                        </ul>
                                    </dd>
                                </div>
                            : null}
                        </dl>
                    </div>

                    <div className="panel__split-element">
                        <div className="panel__split-heading panel__split-heading--experiment">
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

                            {groupedDbxrefs.normal ?
                                <div data-test="external-resources">
                                    <dt>External resources</dt>
                                    <dd><DbxrefList context={context} dbxrefs={groupedDbxrefs.normal} /></dd>
                                </div>
                            : null}

                            {references ?
                                <div data-test="references">
                                    <dt>References</dt>
                                    <dd>{references}</dd>
                                </div>
                            : null}

                            {context.aliases.length > 0 ?
                                <div data-test="aliases">
                                    <dt>Aliases</dt>
                                    <dd>{context.aliases.join(', ')}</dd>
                                </div>
                            : null}

                            {context.date_submitted ?
                                <div data-test="date-submitted">
                                    <dt>Date submitted</dt>
                                    <dd>{dayjs(context.date_submitted).format('MMMM D, YYYY')}</dd>
                                </div>
                            : null}

                            {context.date_released ?
                                <div data-test="date-released">
                                    <dt>Date released</dt>
                                    <dd>{dayjs(context.date_released).format('MMMM D, YYYY')}</dd>
                                </div>
                            : null}

                            {Object.keys(seriesMap).map((seriesType) => (
                                <div data-test="relatedseries" key={seriesType}>
                                    <dt>{seriesType.replace(/([A-Z])/g, ' $1')}</dt>
                                    <dd>
                                        <RelatedSeriesList seriesList={seriesMap[seriesType]} />
                                    </dd>
                                </div>
                            ))}

                            {context.submitter_comment ?
                                <div data-test="submittercomment">
                                    <dt>Submitter comment</dt>
                                    <dd>{context.submitter_comment}</dd>
                                </div>
                            : null}

                            {!isEnhancerExperiment ?
                                <LibrarySubmitterComments replicates={replicates} />
                            : null}

                            {context.internal_tags && context.internal_tags.length > 0 ?
                                <div className="tag-badges" data-test="tags">
                                    <dt>Tags</dt>
                                    <dd><InternalTags internalTags={context.internal_tags} objectType={context['@type'][0]} /></dd>
                                </div>
                            : null}

                            {groupedDbxrefs.SCREEN || groupedDbxrefs.FactorBook ?
                                <>
                                    <div className="panel__split-heading panel__split-heading--experiment">
                                        <h4>Encyclopedia Integration</h4>
                                    </div>

                                    {groupedDbxrefs.SCREEN ?
                                        <div data-test="external-resources-screen">
                                            <dt>Registry of cCREs</dt>
                                            <dd><DbxrefList context={context} dbxrefs={[groupedDbxrefs.SCREEN[0]]} title="view regulatory elements in this cell type on SCREEN" /></dd>
                                        </div>
                                    : null}

                                    {groupedDbxrefs.FactorBook ?
                                        <div data-test="external-resources-factorbook">
                                            <dt>Factorbook</dt>
                                            <dd><DbxrefList context={context} dbxrefs={[groupedDbxrefs.FactorBook[0]]} title="view motifs and integrative analysis" /></dd>
                                        </div>
                                    : null}
                                </>
                            : null}
                        </dl>
                    </div>
                </PanelBody>
            </Panel>

            {Object.keys(condensedReplicates).length > 0 ?
                <ReplicateTable condensedReplicates={condensedReplicates} replicationType={context.replication_type} />
            : null}


            {/* Display the file widget with the facet, graph, and tables for Experiment and FunctionalCharacterizationExperiment only. */}
            {!isEnhancerExperiment ?
                <FileGallery context={context} />
            : null}

            {biosampleCharacterizations && biosampleCharacterizations.length > 0 ?
                    <DocumentsPanelReq documents={biosampleCharacterizations} title="Characterizations" />
            : null}

            <FetchedItems context={context} url={experimentsUrl} Component={ControllingExperiments} />

            <FetchedItems context={context} url={fcexperimentsUrl} Component={ControllingExperiments} />

            <FetchedItems context={context} url={singlecellunitsUrl} Component={ControllingExperiments} />

            <FetchedItems
                context={context}
                url={fcelementsmappingUrl}
                Component={ExperimentTable}
                title={`Functional characterization experiments with ${context.accession} as an elements mapping`}
            />

            <FetchedItems
                context={context}
                url={fcelementscloningUrl}
                Component={ExperimentTable}
                title={`Functional characterization experiments with ${context.accession} as an elements cloning`}
            />

            {isFunctionalExperiment && plasmidMapDocs.length > 0 ?
                <DocumentsPanelReq documents={plasmidMapDocs} title="Plasmid maps" />
            : null}

            {combinedDocuments.length > 0 ?
                <DocumentsPanelReq documents={combinedDocuments} />
            : null}
        </div>
    );
};

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
globals.contentViews.register(Experiment, 'FunctionalCharacterizationExperiment');
globals.contentViews.register(Experiment, 'SingleCellUnit');
globals.contentViews.register(Experiment, 'TransgenicEnhancerExperiment');


const replicateTableColumns = {
    biological_replicate_number: {
        title: 'Biological replicate',
        getValue: (condensedReplicate) => condensedReplicate[0].biological_replicate_number,
    },

    technical_replicate_number: {
        title: 'Technical replicate',
        getValue: (condensedReplicate) => condensedReplicate.map((replicate) => replicate.technical_replicate_number).sort().join(),
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
                const { biosample } = replicate.library;
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
            if (gms && gms.length > 0) {
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
        hide: (list) => _(list).all((condensedReplicate) => {
            const replicate = condensedReplicate[0];
            return !(replicate.library && replicate.library.biosample && replicate.library.biosample.applied_modifications && replicate.library.biosample.applied_modifications.length > 0);
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
        hide: (list) => _(list).all((condensedReplicate) => !condensedReplicate[0].antibody),
    },

    library: {
        title: 'Library',
        getValue: (condensedReplicate) => (condensedReplicate[0].library ? condensedReplicate[0].library.accession : ''),
    },
};

// Display the table of replicates.
const ReplicateTable = (props) => {
    let tableTitle;
    const { condensedReplicates, replicationType } = props;

    // Determine replicate table title based on the replicate type. Also override the biosample replicate column title
    if (replicationType === 'anisogenic') {
        tableTitle = 'Anisogenic replicates';
        replicateTableColumns.biological_replicate_number.title = 'Anisogenic replicate';
    } else {
        tableTitle = 'Isogenic replicates';
        replicateTableColumns.biological_replicate_number.title = 'Isogenic replicate';
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

ReplicateTable.defaultProps = {
    replicationType: '',
};


// Display a list of datasets related to the experiment
class RelatedSeriesList extends React.Component {
    constructor() {
        super();

        // Initial component state.
        this.state = {
            currInfoItem: '', // Accession of item whose detail info appears; empty string to display no detail info
            touchScreen: false, // True if we know we got a touch event; ignore clicks without touch indication
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
        const { seriesList } = this.props;

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
const RelatedSeriesItem = (props) => {
    const { series } = props;
    return (
        <span>
            <a href={series['@id']} title={`View page for series dataset ${series.accession}`}>{series.accession}</a>&nbsp;
            <Tooltip
                trigger={<i className="icon icon-question-circle" />}
                tooltipId={series.accession}
                css="series-tooltip"
            >
                {series.description ? <span>{series.description}</span> : <em>No description available</em>}
            </Tooltip>
        </span>
    );
};

RelatedSeriesItem.propTypes = {
    series: PropTypes.object.isRequired, // Series object to display
};
