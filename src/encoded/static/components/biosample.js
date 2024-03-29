import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import QueryString from '../libs/query_string';
import { Panel, PanelBody } from '../libs/ui/panel';
import { auditDecor } from './audit';
import { DbxrefList } from './dbxref';
import { Document, DocumentsPanel, DocumentPreview, DocumentFile, CharacterizationDocuments } from './doc';
import GeneticModificationSummary from './genetic_modification';
import * as globals from './globals';
import { ProjectBadge } from './image';
import { RelatedItems } from './item';
import { singleTreatment, treatmentDisplay, treatmentTypeDisplay, PanelLookup, AlternateAccession, ItemAccessories, InternalTags, TopAccessories, requestObjects } from './objectutils';
import pubReferenceList from './reference';
import Status, { getObjectStatuses, sessionToAccessLevel } from './status';
import { BiosampleSummaryDisplay, GeneticModificationOrganismNames, CollectBiosampleDocs, BiosampleTable, ExperimentTable } from './typeutils';
import formatMeasurement from '../libs/formatMeasurement';
import getNumberWithOrdinal from '../libs/ordinal_suffix';


/**
 * Properties to retrieve from downstream biosamples. If you subsequently use any properties of
 * these biosamples, make sure you include those properties in this array.
 */
const biosampleFieldsRetrieved = [
    'accession',
    'biosample_ontology.classification',
    'biosample_ontology.term_name',
    'organism.scientific_name',
    'parent_of',
    'status',
    'summary',
];

/**
 * Collect the entire tree of biosamples under a single biosample through the `parent_of/part_of`
 * relationships. The method descends the tree by layer, with each layer representing all the
 * combined children of all the parent biosamples in the layer above.
 *
 * Some `parent_of` arrays contain complete biosample objects while others only contain biosample
 * @ids. For the latter case, this function requests from the server all the biosample objects for
 * these @ids for the layer.
 *
 * Export for Jest tests.
 * @param {array} rootBiosample Object for biosample to begin descending the tree
 * @param {object} session Login session from React <App> context
 * @param {object} sessionProperties Login session_properties from React <App> context
 *
 * @return {promise} Array of biosample objects below the given biosample in the tree.
 */
export const collectChildren = async (rootBiosample, session, sessionProperties) => {
    // The biosample tree can contain biosamples the user doesn't have privileges to view, so
    // generate an array of viewable biosample statuses so we can filter those out.
    const accessLevel = sessionToAccessLevel(session, sessionProperties);
    const viewableStatuses = getObjectStatuses('Biosample', accessLevel);

    // Build the query string for the biosample properties to retrieve from downstream biosamples.
    const biosampleQuery = new QueryString();
    biosampleFieldsRetrieved.forEach((field) => {
        biosampleQuery.addKeyValue('field', field);
    });

    const totalBiosamples = [];
    let layerContents;
    if (rootBiosample.parent_of.length > 0) {
        // Main loop that ends when we get to all the leaves of the tree of biosamples. Prime the
        // loop by starting with a single-biosample layer comprising the given root biosample.
        let layerBiosamples = [rootBiosample];
        while (layerBiosamples.length > 0) {
            // Collect all parent_of elements in the layer of the tree, which could either comprise
            // biosample objects exclusively or biosample @ids exclusively.
            layerContents = layerBiosamples.reduce((accumulator, biosample) => accumulator.concat(biosample.parent_of), []);
            if (layerContents.length > 0) {
                // If the biosamples in the layer comprise @ids, request the corresponding
                // biosample objects.
                if (typeof layerContents[0] === 'string') {
                    // Only retrieve the properties we need to populate the table and to descend to
                    // the next level of the tree to reduce the size of the resulting search object.
                    layerBiosamples = await requestObjects(
                        layerContents,
                        `/search/?type=Biosample&${biosampleQuery.format()}&limit=all`
                    );
                } else {
                    // We already have biosample objects.
                    layerBiosamples = layerContents;
                }

                // Add the newly acquired biosamples for the current layer to the total collection
                // of biosamples for the entire tree, filtering to those the user has privileges to
                // view.
                layerBiosamples = layerBiosamples.filter((biosample) => viewableStatuses.includes(biosample.status));
                totalBiosamples.push(...layerBiosamples);
            } else {
                // We've reached the bottom layer, which has no children.
                layerBiosamples = [];
            }
        }
    }
    return _.uniq(totalBiosamples, (biosample) => biosample['@id']);
};


const BiosampleComponent = ({ context, auditIndicators, auditDetail }, reactContext) => {
    /** Array of child biosamples to the current biosample; undefined until determined */
    const [biosampleChildren, setBiosampleChildren] = React.useState();
    /** Array of experiments using this biosample or a child of this biosample */
    const [experimentsUsing, setExperimentsUsing] = React.useState();

    const itemClass = globals.itemClass(context, 'view-item');
    const aliasList = context.aliases.join(', ');

    // Set up the breadcrumbs.
    const crumbs = [
        { id: 'Biosamples' },
        { id: context.biosample_ontology.classification, query: `biosample_ontology.classification=${context.biosample_ontology.classification}`, tip: context.biosample_ontology.classification },
        { id: <i>{context.organism.scientific_name}</i>, query: `organism.scientific_name=${context.organism.scientific_name}`, tip: context.organism.scientific_name },
        { id: context.biosample_ontology.term_name, query: `biosample_ontology.term_name=${context.biosample_ontology.term_name}`, tip: context.biosample_ontology.term_name },
    ];

    // Build the text of the synchronization string
    let synchText;
    if (context.synchronization) {
        const synchronizationTime = formatMeasurement(context.post_synchronization_time, context.post_synchronization_time_units);

        synchText = context.synchronization +
            (context.post_synchronization_time ?
                ` + ${synchronizationTime}`
            : '');
    }

    // Collect all documents in this biosample
    let combinedDocs = CollectBiosampleDocs(context);

    // If this biosample is part of another, collect those documents too, then remove
    // any duplicate documents in the combinedDocs array.
    if (context.part_of) {
        const parentCombinedDocs = CollectBiosampleDocs(context.part_of);
        combinedDocs = combinedDocs.concat(parentCombinedDocs);
    }
    combinedDocs = globals.uniqueObjectsArray(combinedDocs);

    // Get a list of reference links, if any
    const references = pubReferenceList(context.references);

    // Collect dbxrefs from biosample.dbxrefs and biosample.biosample_ontology.dbxrefs.
    const dbxrefs = (context.dbxrefs || []).concat(context.biosample_ontology.dbxrefs || []);

    React.useEffect(() => {
        // Only request the child biosample tree after login session set to prevent needless
        // re-renders.
        if (reactContext.session) {
            collectChildren(context, reactContext.session, reactContext.session_properties).then((children) => {
                setBiosampleChildren(children);
            });
        }
    }, [context.parent_of, reactContext.session, reactContext.session_properties]);

    React.useEffect(() => {
        // Once we have all children of this biosample, search for experiments relying on the
        // current biosample as well as all its children.
        if (biosampleChildren) {
            const biosampleAtIds = biosampleChildren.map((biosample) => biosample['@id']).concat(context['@id']);
            requestObjects(
                biosampleAtIds,
                '/search/?type=Experiment&status=released&status=submitted&status=in+progress&field=accession&field=assay_term_name&field=replicates.library.biosample.@id&field=replicates.library.biosample.accession&field=biosample_ontology.term_name&field=target&field=description&field=title&field=lab.title&limit=all',
                'replicates.library.biosample.@id'
            ).then((experiments) => {
                setExperimentsUsing(_.uniq(experiments, (experiment) => experiment['@id']));
            });
        }
    }, [biosampleChildren]);

    return (
        <div className={itemClass}>
            <header>
                <TopAccessories context={context} crumbs={crumbs} />
                <h1>{context.accession}{' / '}<span className="sentence-case">{context.biosample_ontology.classification}</span></h1>
                <div className="replacement-accessions">
                    <AlternateAccession altAcc={context.alternate_accessions} />
                </div>
                <ItemAccessories item={context} audit={{ auditIndicators, auditId: 'biosample-audit' }} />
            </header>
            {auditDetail(context.audit, 'biosample-audit', { session: reactContext.session, sessionProperties: reactContext.session_properties, except: context['@id'] })}
            <Panel>
                <PanelBody addClasses="panel__split">
                    <div className="panel__split-element">
                        <div className="panel__split-heading panel__split-heading--biosample">
                            <h4>Summary</h4>
                        </div>
                        <dl className="key-value">
                            <div data-test="status">
                                <dt>Status</dt>
                                <dd><Status item={context} inline /></dd>
                            </div>

                            <div data-test="term-name">
                                <dt>Term name</dt>
                                <dd>{context.biosample_ontology.term_name}</dd>
                            </div>

                            <div data-test="term-id">
                                <dt>Term ID</dt>
                                <dd><BiosampleTermId termId={context.biosample_ontology.term_id} /></dd>
                            </div>

                            <div data-test="summary">
                                <dt>Summary</dt>
                                <dd>{context.summary ? <div> <BiosampleSummaryDisplay summary={context.summary} organisms={[context.organism.scientific_name].concat(GeneticModificationOrganismNames([context]))} /> </div> : null}</dd>
                            </div>

                            {context.description ?
                                <div data-test="description">
                                    <dt>Description</dt>
                                    <dd className="sentence-case">{context.description}</dd>
                                </div>
                            : null}

                            {context.disease_term_name && context.disease_term_name.length > 0 ?
                                <div data-test="possible-controls">
                                    <dt>Health status</dt>
                                    <dd>
                                        <ul>
                                            {context.disease_term_name.map((disease) => (
                                                <li key={disease} className="multi-comma">
                                                    {disease}
                                                </li>
                                            ))}
                                        </ul>
                                    </dd>
                                </div>
                            : null}

                            {context.donor && context.donor.organism.name !== 'human' && context.life_stage ?
                                <div data-test="life-stage">
                                    <dt>Life stage</dt>
                                    <dd className="sentence-case">{context.life_stage}</dd>
                                </div>
                            : null}

                            {context.donor && context.donor.organism.name !== 'human' && context.age ?
                                <div data-test="age">
                                    <dt>Age</dt>
                                    <dd className="sentence-case">
                                        {formatMeasurement(context.age, context.age_units)}
                                    </dd>
                                </div>
                            : null}

                            {context.PMI ?
                                <div data-test="pmi">
                                    <dt>Post-mortem interval</dt>
                                    <dd>
                                        {formatMeasurement(context.PMI, context.PMI_units)}
                                    </dd>
                                </div>
                            : null}

                            {synchText ?
                                <div data-test="biosample-synchronization">
                                    <dt>Synchronization timepoint</dt>
                                    <dd className="sentence-case">{synchText}</dd>
                                </div>
                            : null}

                            {context.post_differentiation_time && context.post_differentiation_time_units ?
                                <div data-test="postdifferentiationtime">
                                    <dt>Post-differentiation time</dt>
                                    <dd>
                                        {formatMeasurement(context.post_differentiation_time, context.post_differentiation_time_units)}
                                    </dd>
                                </div>
                            : null}

                            {context.post_nucleic_acid_delivery_time && context.post_nucleic_acid_delivery_time_units ?
                                <div data-test="postnucleicaciddeliverytime">
                                    <dt>Post-nucleic acid delivery time</dt>
                                    <dd>
                                        {formatMeasurement(context.post_nucleic_acid_delivery_time, context.post_nucleic_acid_delivery_time_units)}
                                    </dd>
                                </div>
                            : null}

                            {context.pulse_chase_time && context.pulse_chase_time_units ?
                                <div data-test="pulsechasetime">
                                    <dt>Pulse-chase time</dt>
                                    <dd>
                                        {formatMeasurement(context.pulse_chase_time, context.pulse_chase_time_units)}
                                    </dd>
                                </div>
                            : null}

                            {context.expressed_genes && context.expressed_genes.length > 0 ?
                                <div data-test="expressed-genes">
                                    <dt>Sorted gene expression</dt>
                                    <dd>
                                        {/* A user can have a gene repeat. Therefore, uuid alone is not sufficient as an identifier */}
                                        {context.expressed_genes.map((loci, i) => (
                                            loci.gene ?
                                                <span key={`${loci.gene.uuid}-${i}`}>
                                                    {i > 0 ? <span>, </span> : null}
                                                    <a href={loci.gene['@id']}>{loci.gene.symbol}</a>
                                                    {/* 0 is falsy but we still want it to display, so 0 is explicitly checked for */}
                                                    {loci.expression_percentile || loci.expression_percentile === 0 ? <span>{' '}({getNumberWithOrdinal(loci.expression_percentile)} percentile)</span> : null}
                                                    {(loci.expression_range_maximum && loci.expression_range_minimum) || (loci.expression_range_maximum === 0 || loci.expression_range_minimum === 0) ? <span>{' '}({loci.expression_range_minimum}-{loci.expression_range_maximum}%)</span> : null}
                                                </span>
                                            : null
                                        ))}
                                    </dd>
                                </div>
                            : null}

                            {context.subcellular_fraction_term_name ?
                                <div data-test="subcellulartermname">
                                    <dt>Subcellular fraction</dt>
                                    <dd>{context.subcellular_fraction_term_name}</dd>
                                </div>
                            : null}

                            {context.subcellular_fraction_term_id ?
                                <div data-test="subcellularid">
                                    <dt>Subcellular fraction ID</dt>
                                    <dd>{context.subcellular_fraction_term_id}</dd>
                                </div>
                            : null}

                            {context.depleted_in_term_name && context.depleted_in_term_name.length > 0 ?
                                <div data-test="depletedin">
                                    <dt>Depleted in</dt>
                                    <dd>
                                        {context.depleted_in_term_name.map((termName, i) => (
                                            <span key={i}>
                                                {i > 0 ? ', ' : ''}
                                                {termName}
                                            </span>
                                        ))}
                                    </dd>
                                </div>
                            : null}

                            {context.product_id ?
                                <div data-test="productid">
                                    <dt>Product ID</dt>
                                    <dd><MaybeLink href={context.url}>{context.product_id}</MaybeLink></dd>
                                </div>
                            : null}

                            {context.lot_id ?
                                <div data-test="lotid">
                                    <dt>Lot ID</dt>
                                    <dd>{context.lot_id}</dd>
                                </div>
                            : null}

                            {context.note ?
                                <div data-test="note">
                                    <dt>Note</dt>
                                    <dd>{context.note}</dd>
                                </div>
                            : null}

                            {context.starting_amount ?
                                <div data-test="startingamount">
                                    <dt>Starting amount</dt>
                                    <dd>{context.starting_amount}<span className="unit">{context.starting_amount_units}</span></dd>
                                </div>
                            : null}

                            {context.culture_start_date ?
                                <div data-test="culturestartdate">
                                    <dt>Culture start date</dt>
                                    <dd>{context.culture_start_date}</dd>
                                </div>
                            : null}

                            {context.culture_harvest_date ?
                                <div data-test="cultureharvestdate">
                                    <dt>Culture harvest date</dt>
                                    <dd>{context.culture_harvest_date}</dd>
                                </div>
                            : null}

                            {context.passage_number ?
                                <div data-test="passagenumber">
                                    <dt>Passage number</dt>
                                    <dd>{context.passage_number}</dd>
                                </div>
                            : null}

                            {context.phase ?
                                <div data-test="phase">
                                    <dt>Cell cycle</dt>
                                    <dd>{context.phase}</dd>
                                </div>
                            : null}

                            {context.originated_from ?
                                <div data-test="originatedfrom">
                                    <dt>Originated from biosample</dt>
                                    <dd><a href={context.originated_from['@id']}>{context.originated_from.accession}</a></dd>
                                </div>
                            : null}

                            {context.part_of ?
                                <div data-test="separatedfrom">
                                    <dt>Separated from biosample</dt>
                                    <dd><a href={context.part_of['@id']}>{context.part_of.accession}</a></dd>
                                </div>
                            : null}

                            {context.parent_of && context.parent_of.length > 0 ?
                                <div data-test="parentof">
                                    <dt>Parent of biosamples</dt>
                                    <dd>
                                        {context.parent_of.map((biosample, i) => (
                                            <React.Fragment key={biosample['@id']}>
                                                {i > 0 ? <span>, </span> : null}
                                                <a href={biosample['@id']}>{biosample.accession}</a>
                                            </React.Fragment>
                                        ))}
                                    </dd>
                                </div>
                            : null}
                        </dl>
                    </div>

                    <div className="panel__split-element">
                        <div className="panel__split-heading panel__split-heading--biosample">
                            <h4>Attribution</h4>
                            <ProjectBadge award={context.award} addClasses="badge-heading" />
                        </div>
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

                            <div data-test="submittedby">
                                <dt>Submitted by</dt>
                                <dd>{context.submitted_by.title}</dd>
                            </div>

                            {context.source.title ?
                                <div data-test="sourcetitle">
                                    <dt>Source</dt>
                                    <dd>
                                        {context.source.url ?
                                            <a href={context.source.url}>{context.source.title}</a>
                                        :
                                            <span>{context.source.title}</span>
                                        }
                                    </dd>
                                </div>
                            : null}

                            <div data-test="project">
                                <dt>Project</dt>
                                <dd>{context.award.project}</dd>
                            </div>

                            {dbxrefs.length > 0 ?
                                <div data-test="externalresources">
                                    <dt>External resources</dt>
                                    <dd><DbxrefList context={context} dbxrefs={dbxrefs} /></dd>
                                </div>
                            : null}

                            {references ?
                                <div data-test="references">
                                    <dt>References</dt>
                                    <dd>{references}</dd>
                                </div>
                            : null}

                            {context.date_obtained ?
                                <div data-test="dateobtained">
                                    <dt>Date obtained</dt>
                                    <dd>{context.date_obtained}</dd>
                                </div>
                            : null}

                            {context.aliases.length > 0 ?
                                <div data-test="aliases">
                                    <dt>Aliases</dt>
                                    <dd>{aliasList}</dd>
                                </div>
                            : null}

                            {context.submitter_comment ?
                                <div data-test="submittercomment">
                                    <dt>Submitter comment</dt>
                                    <dd>{context.submitter_comment}</dd>
                                </div>
                            : null}

                            {context.internal_tags && context.internal_tags.length > 0 ?
                                <div className="tag-badges" data-test="tags">
                                    <dt>Tags</dt>
                                    <dd><InternalTags internalTags={context.internal_tags} objectType={context['@type'][0]} /></dd>
                                </div>
                            : null}
                        </dl>
                    </div>
                </PanelBody>

                {context.treatments.length > 0 ?
                    <PanelBody addClasses="panel__below-split">
                        <h4>Treatment details</h4>
                        {context.treatments.map((treatment) => treatmentDisplay(treatment))}
                    </PanelBody>
                : null}
            </Panel>

            {context.pooled_from && context.pooled_from.length > 0 ?
                <BiosampleTable
                    title="Pooled from biosamples"
                    items={context.pooled_from}
                    total={context.pooled_from.length}
                    organisms={[context.organism.scientific_name]}
                />
            : null}

            {context.applied_modifications && context.applied_modifications.length > 0 ?
                <GeneticModificationSummary geneticModifications={context.applied_modifications} />
            : null}

            {context.donor ?
                <div>
                    {PanelLookup({ context: context.donor, biosample: context })}
                </div>
            : null}

            {experimentsUsing ?
                <ExperimentTable
                    items={experimentsUsing}
                    limit={0}
                    total={experimentsUsing.length}
                    title="Functional genomics experiments using this biosample"
                    showBiosamples
                />
            : null}

            <RelatedItems
                title="Functional characterization experiments using this biosample"
                url={`/search/?type=FunctionalCharacterizationExperiment&replicates.library.biosample.uuid=${context.uuid}`}
                Component={ExperimentTable}
            />

            <RelatedItems
                title="Transgenic enhancer experiments using this biosample"
                url={`/search/?type=TransgenicEnhancerExperiment&biosamples.uuid=${context.uuid}`}
                Component={ExperimentTable}
            />

            {biosampleChildren && biosampleChildren.length > 0 ?
                <BiosampleTable
                    items={biosampleChildren}
                    limit={0}
                    total={biosampleChildren.length}
                    title="Biosamples that are part of this biosample"
                    organisms={[context.organism.scientific_name]}
                />
            : null}

            <RelatedItems
                title="Biosamples originating from this biosample"
                url={`/search/?type=Biosample&originated_from.uuid=${context.uuid}`}
                Component={BiosampleTable}
            />

            <RelatedItems
                title="Biosamples that are pooled from this biosample"
                url={`/search/?type=Biosample&pooled_from.uuid=${context.uuid}`}
                Component={BiosampleTable}
            />

            {combinedDocs.length > 0 ?
                <DocumentsPanel documentSpecs={[{ documents: combinedDocs }]} />
            : null}
        </div>
    );
};

BiosampleComponent.propTypes = {
    context: PropTypes.object.isRequired, // ENCODE biosample object to be rendered
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

BiosampleComponent.contextTypes = {
    session: PropTypes.object, // Login information
    session_properties: PropTypes.object,
};

const Biosample = auditDecor(BiosampleComponent);

globals.contentViews.register(Biosample, 'Biosample');


// Certain hrefs in a biosample context object could be empty, or have the value 'N/A'. This
// component renders the child components of this one (likely just a string) as just an unadorned
// component. But if href has any value besides this, the child component is rendered as a link
// with this href.

const MaybeLink = (props) => {
    const { href, children } = props;

    if (!href || href === 'N/A') {
        return <span>{children}</span>;
    }
    return <a {...props}>{children}</a>;
};

MaybeLink.propTypes = {
    href: PropTypes.string, // String
    children: PropTypes.node.isRequired, // React child components to this one
};

MaybeLink.defaultProps = {
    href: '',
};


// Map from prefixes to corresponding URL bases. Not all term ID prefixes covered here. Specific
// term IDs are appended to these after converting ':' to '_'.
const urlMap = {
    EFO: 'http://www.ebi.ac.uk/efo/',
    UBERON: 'http://www.ontobee.org/ontology/UBERON?iri=http://purl.obolibrary.org/obo/',
    CL: 'http://www.ontobee.org/ontology/CL?iri=http://purl.obolibrary.org/obo/',
    CLO: 'http://www.ontobee.org/ontology/CLO?iri=http://purl.obolibrary.org/obo/',
};

// Display the biosample term ID given in `termId`, and link to a corresponding site if the prefix
// of the term ID needs it. Any term IDs with prefixes not matching any in the `urlMap` property
// simply display without a link.
const BiosampleTermId = (props) => {
    const { termId } = props;

    if (termId) {
        // All are of the form XXX:nnnnnnn...
        const idPieces = termId.split(':');
        if (idPieces.length === 2) {
            const urlBase = urlMap[idPieces[0]];
            if (urlBase) {
                return <a href={urlBase + termId.replace(':', '_')}>{termId}</a>;
            }
        }

        // Either term ID not in specified form (schema should disallow) or not one of the ones
        // we link to. Just display the term ID without linking out.
        return <span>{termId}</span>;
    }

    // biosample_ontology is a required property, but just in case...
    return null;
};

BiosampleTermId.propTypes = {
    termId: PropTypes.string, // Biosample whose term is being displayed.
};

BiosampleTermId.defaultProps = {
    termId: '',
};

export default BiosampleTermId;


const Treatment = (props) => {
    const { context } = props;

    const treatmentText = singleTreatment(context);
    const treatmentDetails = treatmentTypeDisplay(context);
    return (
        <dl className="key-value">
            <div data-test="treatment">
                <dt>Treatment</dt>
                <dd>{treatmentText}</dd>
            </div>

            <div data-test="type">
                <dt>Type</dt>
                <dd>{treatmentDetails}</dd>
            </div>

            {context.purpose ?
                <div data-test="purpose">
                    <dt>Purpose</dt>
                    <dd>{context.purpose}</dd>
                </div>
            : null}
        </dl>
    );
};

Treatment.propTypes = {
    context: PropTypes.object.isRequired, // Treatment context object
};

globals.panelViews.register(Treatment, 'Treatment');


const TreatmentContent = ({ context }) => {
    const itemClass = globals.itemClass(context, 'view-item');
    return (
        <div className={itemClass}>
            <header>
                <h1>{context.treatment_term_name}</h1>
                <ItemAccessories item={context} />
            </header>
            <Panel>
                <PanelBody>
                    <Treatment context={context} />
                </PanelBody>
            </Panel>
        </div>
    );
};

TreatmentContent.propTypes = {
    /** Treatment object to display on its own page */
    context: PropTypes.object.isRequired,
};

globals.contentViews.register(TreatmentContent, 'Treatment');


// Biosample and donor characterization documents

const EXCERPT_LENGTH = 80; // Maximum number of characters in an excerpt

// Document header component -- Characterizations
const CharacterizationHeader = (props) => (
    <div className="document__header">
        {props.doc.characterization_method}
    </div>
);

CharacterizationHeader.propTypes = {
    doc: PropTypes.object.isRequired, // Document object to render
};


// Document caption component -- Characterizations
const CharacterizationCaption = (props) => {
    const { doc } = props;
    const { caption } = doc;
    let excerpt;

    if (caption && caption.length > EXCERPT_LENGTH) {
        excerpt = globals.truncateString(caption, EXCERPT_LENGTH);
    }

    return (
        <div className="document__caption">
            {excerpt || caption ?
                <div data-test="caption">
                    <strong>{excerpt ? 'Caption excerpt: ' : 'Caption: '}</strong>
                    {excerpt ? <span>{excerpt}</span> : <span>{caption}</span>}
                </div>
            : <em>No caption</em>}
        </div>
    );
};

CharacterizationCaption.propTypes = {
    doc: PropTypes.object.isRequired, // Document object to render
};


// Document detail component -- default
const CharacterizationDetail = (props) => {
    const characterization = props.doc;
    const keyClass = `document__detail${props.detailOpen ? ' active' : ''}`;
    const excerpt = characterization.caption && characterization.caption.length > EXCERPT_LENGTH;

    // See if we need a list of documents or not. Documents without attachments don't get
    // displayed.
    const docs = characterization.documents && characterization.documents.length > 0 ?
        characterization.documents.filter((doc) => !!(doc.attachment && doc.attachment.href && doc.attachment.download))
    : [];

    return (
        <div className={keyClass}>
            <dl className="key-value-doc" id={`panel${props.id}`} aria-labelledby={`tab${props.id}`} role="tabpanel">
                {excerpt ?
                    <div data-test="caption">
                        <dt>Caption</dt>
                        <dd>{characterization.caption}</dd>
                    </div>
                : null}

                {characterization.submitted_by && characterization.submitted_by.title ?
                    <div data-test="submitted-by">
                        <dt>Submitted by</dt>
                        <dd>{characterization.submitted_by.title}</dd>
                    </div>
                : null}

                <div data-test="lab">
                    <dt>Lab</dt>
                    <dd>{characterization.lab.title}</dd>
                </div>

                {characterization.award && characterization.award.name ?
                    <div data-test="award">
                        <dt>Grant</dt>
                        <dd><a href={characterization.award['@id']}>{characterization.award.name}</a></dd>
                    </div>
                : null}

                {characterization.submitter_comment ?
                    <div data-test="submittercomment">
                        <dt>Submitter comment</dt>
                        <dd>{characterization.submitter_comment}</dd>
                    </div>
                : null}

                {docs.length > 0 ?
                    <div data-test="documents">
                        <dt>Documents</dt>
                        <CharacterizationDocuments docs={docs} />
                    </div>
                : null}
            </dl>
        </div>
    );
};

CharacterizationDetail.propTypes = {
    doc: PropTypes.object.isRequired, // Document object to render
    id: PropTypes.string.isRequired, // Unique ID string for the detail panel
    detailOpen: PropTypes.bool, // True if detail panel is visible
};

CharacterizationDetail.defaultProps = {
    detailOpen: false,
};


/**
 * Display an biosample characterization object.
 */
const BiosampleCharacterization = ({ context }) => {
    const documentSpecs = [
        { documents: [context] },
    ];
    return <DocumentsPanel title="Characterizations" documentSpecs={documentSpecs} />;
};

BiosampleCharacterization.propTypes = {
    /** BiosampleCharacterization object (not inside AntibodyLot) */
    context: PropTypes.object.isRequired,
};


/**
 * Display an biosample characterization object.
 */
const DonorCharacterization = ({ context }) => {
    const documentSpecs = [
        { documents: [context] },
    ];
    return <DocumentsPanel title="Characterizations" documentSpecs={documentSpecs} />;
};

DonorCharacterization.propTypes = {
    /** DonorCharacterization object */
    context: PropTypes.object.isRequired,
};


// Parts of individual document panels
globals.contentViews.register(BiosampleCharacterization, 'BiosampleCharacterization');
globals.contentViews.register(DonorCharacterization, 'DonorCharacterization');

globals.panelViews.register(Document, 'BiosampleCharacterization');
globals.panelViews.register(Document, 'DonorCharacterization');

globals.documentViews.header.register(CharacterizationHeader, 'BiosampleCharacterization');
globals.documentViews.header.register(CharacterizationHeader, 'DonorCharacterization');

globals.documentViews.caption.register(CharacterizationCaption, 'BiosampleCharacterization');
globals.documentViews.caption.register(CharacterizationCaption, 'DonorCharacterization');

globals.documentViews.preview.register(DocumentPreview, 'BiosampleCharacterization');
globals.documentViews.preview.register(DocumentPreview, 'DonorCharacterization');

globals.documentViews.file.register(DocumentFile, 'BiosampleCharacterization');
globals.documentViews.file.register(DocumentFile, 'DonorCharacterization');

globals.documentViews.detail.register(CharacterizationDetail, 'BiosampleCharacterization');
globals.documentViews.detail.register(CharacterizationDetail, 'DonorCharacterization');
