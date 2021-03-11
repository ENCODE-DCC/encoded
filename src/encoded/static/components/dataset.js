import React from 'react';
import PropTypes from 'prop-types';
import dayjs from 'dayjs';
import _ from 'underscore';
import url from 'url';
import { Panel, PanelBody } from '../libs/ui/panel';
import { auditDecor } from './audit';
import { DocumentsPanelReq } from './doc';
import * as globals from './globals';
import { DbxrefList } from './dbxref';
import { FetchedItems } from './fetched';
import { FileGallery } from './filegallery';
import { ProjectBadge } from './image';
import { Breadcrumbs } from './navigation';
import { singleTreatment, ItemAccessories, InternalTags } from './objectutils';
import pubReferenceList from './reference';
import urlList from './url';
import { SortTablePanel, SortTable } from './sorttable';
import Status from './status';
import { BiosampleSummaryString, BiosampleOrganismNames, CollectBiosampleDocs, AwardRef, LibraryTableforDS, ReplacementAccessions, ControllingDatasets, DatasetTable } from './typeutils';
import ViewControlRegistry, { ViewControlTypes } from './view_controls';


/**
 * 'Dataset' search results view-control filter. For most dataset searches, this just returns
 * the default views for datasets. But if this displays the reference-epigenome matrix or Stem Cell
 * Matrix, it returns the subset of views relevant to those.
 * @param {array} types Views defined by default for the Dataset @type.
 * @param {object} results Current page's search-results object
 *
 * @return {array} Views that apply to the current search results.
 */
const viewControlFilter = (types, results) => {
    let views;
    const parsedUrl = url.parse(results['@id']);
    const pathname = parsedUrl.pathname;
    if (['/reference-epigenome-matrix/', '/sescc-stem-cell-matrix/'].includes(pathname)) {
        views = ['Search', 'Report'];
    } else {
        views = types.filter(type => type !== results['@type'][0]);
    }
    return views;
};


ViewControlRegistry.register('Dataset', [
    ViewControlTypes.SEARCH,
    ViewControlTypes.MATRIX,
    ViewControlTypes.REPORT,
    ViewControlTypes.SUMMARY,
], viewControlFilter);


const anisogenicValues = [
    'anisogenic, sex-matched and age-matched',
    'anisogenic, age-matched',
    'anisogenic, sex-matched',
    'anisogenic',
];


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
    { property: 'lysis_method', title: 'Lysis method', test: 'lysismethod' },
    { property: 'extraction_method', title: 'Extraction method', test: 'extractionmethod' },
    { property: 'fragmentation_methods', title: 'Fragmentation methods', test: 'fragmentationmethod' },
    { property: 'library_size_selection_method', title: 'Size selection method', test: 'sizeselectionmethod' },
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

        const treatments = library.treatments;
        if (treatments && treatments.length > 0) {
            libraryTreatments = libraryTreatments.concat(treatments.map(treatment => singleTreatment(treatment)));
        }
        const biosampleTreatments = library.biosample && library.biosample.treatments;
        if (biosampleTreatments && biosampleTreatments.length > 0) {
            libraryTreatments = libraryTreatments.concat(biosampleTreatments.map(treatment => singleTreatment(treatment)));
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
        const strandSpecificity = library.strand_specificity;
        let libraryPropertyString = null;

        // A strand_specificity of "false" is still a displayable value.
        if (strandSpecificity !== undefined) {
            libraryPropertyString = strandSpecificity ? 'Strand-specific' : 'Non-strand-specific';
        }
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
                // numbers to `libraryPropertyDisplays`.
                displayedLibraryProperties.forEach(({ property }) => {
                    let libraryPropertyString = '';
                    let libraryPropertyComponent = null;
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
                        const extractedProperty = libraryPropertyExtractors[property](replicate.library);
                        libraryPropertyString = extractedProperty.libraryPropertyString;
                        libraryPropertyComponent = extractedProperty.libraryPropertyComponent;
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
                const homogeneous = !libraryPropertyElements.some(libraryProperty => libraryProperty.value !== libraryPropertyElements[0].value);
                if (!homogeneous) {
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
                    // Only one value collected for this property, or more than one but all have
                    // the same value, so just display the one value without a replicate
                    // identifier.
                    renderedLibraryProperties.push(
                        <div key={displayedLibraryProperty.property} data-test={displayedLibraryProperty.test}>
                            <dt>{displayedLibraryProperty.title}</dt>
                            <dd>{libraryPropertyElements[0].component || libraryPropertyElements[0].value}</dd>
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
    // Make a list of all libraries in all replicates, deduped.
    const libraries = _.uniq(replicates.reduce((libraryAcc, replicate) => (replicate.library ? libraryAcc.concat([replicate.library]) : libraryAcc), []), library => library['@id']);
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
 * Renders both Dataset and FunctionalCharacterizationDataset objects.
 */
const DatasetComponent = ({ context, auditIndicators, auditDetail }, reactContext) => {
    const loggedIn = !!(reactContext.session && reactContext.session['auth.userid']);
    const adminUser = !!(reactContext.session_properties && reactContext.session_properties.admin);
    const itemClass = globals.itemClass(context, 'view-item');

    // Determine whether object is Dataset or FunctionalCharacterizationDataset.
    const datasetType = context['@type'][0];
    let displayType;
    let displayTypeBreadcrumbs;
    displayTypeBreadcrumbs = 'Datasets';
    displayType = 'Dataset';

    const libraries = context.libraries && context.libraries.length > 0 ? context.libraries : [];

    // Collect all documents from the dataset itself.
    const documents = (context.documents && context.documents.length > 0) ? context.documents : [];

    // Make array of all replicate biosamples, not including biosample-less replicates. Also
    // collect up library documents.
    const libraryDocs = [];
    let biosamples = [];
    if (libraries.length > 0) {
        biosamples = _.compact(libraries.map((replicate) => {
            if (replicate.library) {
                if (replicate.library.documents && replicate.library.documents.length > 0) {
                    Array.prototype.push.apply(libraryDocs, replicate.library.documents);
                }

                return replicate.library.biosample;
            }
            return null;
        }));
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

    // Determine this dataset's ENCODE version.
    const encodevers = globals.encodeVersion(context);

    // Make list of statuses.
    const statuses = [{ status: context.status, title: 'Status' }];
    if (adminUser && context.internal_status) {
        statuses.push({ status: context.internal_status, title: 'Internal' });
    }

    // Determine whether the dataset is isogenic or anisogenic. No replication_type
    // indicates isogenic.
    const anisogenic = context.replication_type ? (anisogenicValues.indexOf(context.replication_type) !== -1) : false;

    // Get a map of related datasets, possibly filtering on their status and
    // categorized by their type.
    let seriesMap = {};
    if (context.related_series && context.related_series.length > 0) {
        seriesMap = _.groupBy(
            context.related_series.filter(
                dataset => loggedIn || dataset.status === 'released'
            ),
            series => series['@type'][0]
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
        nameQuery += `${nameQuery.length > 0 ? '&' : ''}replicates.library.biosample.donor.organism.scientific_name=${organismName}`;
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
    const crumbsReleased = (context.status === 'released');

    // Compile the document list.
    const combinedDocuments = _.uniq(documents.concat(
        biosampleDocs,
        libraryDocs,
        pipelineDocs,
        analysisStepDocs
    ));

    // Make a list of reference links, if any.
    const references = pubReferenceList(context.references);

    // Make a list of url links, if any.
    const urls = urlList(context.urls);

    function libraryProtocolList(values, field) {
        if (values && values.length > 0) {
            return Array.from(new Set(values.map(function(value) { return value.protocol[field] }))).join(", ");
        }
        return null;
    }

    function libraryList(values, field) {
        if (values && values.length > 0) {
            return Array.from(new Set(values.map(function(value) { return value[field] }))).join(", ");
        }
        return null;
    }

    function libraryListList(values, field) {
        if (values && values.length > 0) {
            const mySet = new Set();
            values.forEach(x => x[field].forEach(y => mySet.add(y)));
            const myList = Array.from(mySet).join(", ");
            return myList;
        }
        return null;
    }

    const library_types  = libraryList(context.libraries, 'assay');
    const library_titles = libraryProtocolList(context.libraries, 'title');
    const biosample_classification = libraryListList(context.libraries, 'biosample_classification');

    return (
        <div className={itemClass}>
            <header>
                <Breadcrumbs root={`/search/?type=${datasetType}`} crumbs={crumbs} crumbsReleased={crumbsReleased} />
                <h1>{displayType} summary for {context.accession}</h1>
                <ReplacementAccessions context={context} />
                <ItemAccessories item={context} audit={{ auditIndicators, auditId: 'dataset-audit' }} hasCartControls />
            </header>
            {auditDetail(context.audit, 'dataset-audit', { session: reactContext.session, sessionProperties: reactContext.session_properties, except: context['@id'] })}
            <Panel>
                <PanelBody addClasses="panel__split">
                    <div className="panel__split-element">
                        <div className="panel__split-heading panel__split-heading--dataset">
                            <h4>Summary</h4>
                        </div>
                        <dl className="key-value">
                            <div data-test="status">
                                <dt>Status</dt>
                                <dd>
                                    <Status item={context} css="dd-status" title="Dataset status" inline />
                                </dd>
                            </div>

                            {context.description ?
                                <div data-test="description">
                                    <dt>Description</dt>
                                    <dd>{context.description}</dd>
                                </div>
                            : null}

                            {biosample_classification ?
                                <div data-test="biosample_classification">
                                    <dt>Biosample classification</dt>
                                    <dd>{biosample_classification}</dd>
                                </div>
                            : null}

                            {library_types ?
                                <div data-test="library_types">
                                    <dt>Library types</dt>
                                    <dd>{library_types}</dd>
                                </div>
                            : null}

                            {library_titles ?
                                <div data-test="library_titles">
                                    <dt>Library protocols</dt>
                                    <dd>{library_titles}</dd>
                                </div>
                            : null}
                        </dl>
                    </div>

                    <div className="panel__split-element">
                        <div className="panel__split-heading panel__split-heading--dataset">
                            <h4>Attribution</h4>
                            <ProjectBadge award={context.award} addClasses="badge-heading" />
                        </div>
                        <dl className="key-value">

                            <AwardRef context={context} adminUser={adminUser} />

                            <div data-test="project">
                                <dt>Project</dt>
                                <dd>{context.award.project}</dd>
                            </div>

                            <div data-test="award">
                                <dt>Award</dt>
                                <dd><a href={context.award['@id']}>{context.award.name}</a></dd>
                            </div>

                            {context.dbxrefs ?
                                <div data-test="external-resources">
                                    <dt>External resources</dt>
                                    <dd><DbxrefList context={context} dbxrefs={context.dbxrefs} /></dd>
                                </div>
                            : null}

                            {references ?
                                <div data-test="references">
                                    <dt>References</dt>
                                    <dd>{references}</dd>
                                </div>
                            : null}

                            {urls ?
                                <div data-test="urls">
                                    <dt>URLs</dt>
                                    <dd>{urls}</dd>
                                </div>
                            : null}

                            {context.aliases ?
                                <div data-test="aliases">
                                    <dt>Aliases</dt>
                                    <dd>{context.aliases.join(', ')}</dd>
                                </div>
                            : null}

                            {context.date_released ?
                                <div data-test="date-released">
                                    <dt>Date released</dt>
                                    <dd>{dayjs(context.date_released).format('MMMM D, YYYY')}</dd>
                                </div>
                            : null}

                            {context.submitter_comment ?
                                <div data-test="submittercomment">
                                    <dt>Submitter comment</dt>
                                    <dd>{context.submitter_comment}</dd>
                                </div>
                            : null}
                        </dl>
                    </div>
                </PanelBody>
            </Panel>


            {context.libraries && context.libraries.length > 0 ?
                <LibraryTableforDS
                    title="Libraries"
                    items={context.libraries}
                    total={context.libraries.length}
                />
            : null}

            {/* Display the file widget with the facet, graph, and tables */}
            <FileGallery context={context} encodevers={encodevers} anisogenic={anisogenic} />

            {combinedDocuments.length > 0 ?
                <DocumentsPanelReq documents={combinedDocuments} />
            : null}
        </div>
    );
};

DatasetComponent.propTypes = {
    context: PropTypes.object.isRequired, // Dataset object to render on this page
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

DatasetComponent.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
};

// Need to export for Jest tests.
const Dataset = auditDecor(DatasetComponent);
export default Dataset;

globals.contentViews.register(Dataset, 'Dataset');
globals.contentViews.register(Dataset, 'FunctionalCharacterizationDataset');