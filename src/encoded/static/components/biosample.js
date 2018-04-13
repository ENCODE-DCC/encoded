import React from 'react';
import PropTypes from 'prop-types';
import { Panel, PanelBody } from '../libs/bootstrap/panel';
import { auditDecor } from './audit';
import { ExperimentTable } from './dataset';
import { DbxrefList } from './dbxref';
import { Document, DocumentsPanel, DocumentPreview, DocumentFile, CharacterizationDocuments } from './doc';
import GeneticModificationSummary from './genetic_modification';
import * as globals from './globals';
import { ProjectBadge } from './image';
import { RelatedItems } from './item';
import { Breadcrumbs } from './navigation';
import { singleTreatment, treatmentDisplay, PanelLookup, AlternateAccession } from './objectutils';
import pubReferenceList from './reference';
import { StatusLabel } from './statuslabel';
import { BiosampleSummaryString, CollectBiosampleDocs, BiosampleTable } from './typeutils';


/* eslint-disable react/prefer-stateless-function */
class BiosampleComponent extends React.Component {
    render() {
        const context = this.props.context;
        const itemClass = globals.itemClass(context, 'view-item');
        const aliasList = context.aliases.join(', ');

        // Set up the breadcrumbs.
        const crumbs = [
            { id: 'Biosamples' },
            { id: context.biosample_type, query: `biosample_type=${context.biosample_type}`, tip: context.biosample_type },
            { id: <i>{context.organism.scientific_name}</i>, query: `organism.scientific_name=${context.organism.scientific_name}`, tip: context.organism.scientific_name },
            { id: context.biosample_term_name, query: `biosample_term_name=${context.biosample_term_name}`, tip: context.biosample_term_name },
        ];

        // Build the text of the synchronization string
        let synchText;
        if (context.synchronization) {
            synchText = context.synchronization +
                (context.post_synchronization_time ?
                    ` + ${context.post_synchronization_time}${context.post_synchronization_time_units ? ` ${context.post_synchronization_time_units}` : ''}`
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

        // Render tags badges
        let tagBadges;
        if (context.internal_tags && context.internal_tags.length) {
            tagBadges = context.internal_tags.map(tag => <img key={tag} src={`/static/img/tag-${tag}.png`} alt={`${tag} tag`} />);
        }

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs root="/search/?type=Biosample" crumbs={crumbs} />
                        <h2>
                            {context.accession}{' / '}<span className="sentence-case">{context.biosample_type}</span>
                        </h2>
                        <AlternateAccession altAcc={context.alternate_accessions} />
                        <div className="status-line">
                            <div className="characterization-status-labels">
                                <StatusLabel title="Status" status={context.status} />
                            </div>
                            {this.props.auditIndicators(context.audit, 'biosample-audit', { session: this.context.session })}
                        </div>
                    </div>
                </header>
                {this.props.auditDetail(context.audit, 'biosample-audit', { session: this.context.session, except: context['@id'] })}
                <Panel addClasses="data-display">
                    <PanelBody addClasses="panel-body-with-header">
                        <div className="flexrow">
                            <div className="flexcol-sm-6">
                                <div className="flexcol-heading experiment-heading"><h4>Summary</h4></div>
                                <dl className="key-value">
                                    <div data-test="term-name">
                                        <dt>Term name</dt>
                                        <dd>{context.biosample_term_name}</dd>
                                    </div>

                                    <div data-test="term-id">
                                        <dt>Term ID</dt>
                                        <dd><BiosampleTermId termId={context.biosample_term_id} /></dd>
                                    </div>

                                    <div data-test="summary">
                                        <dt>Summary</dt>
                                        <dd>{BiosampleSummaryString(context)}</dd>
                                    </div>

                                    {context.description ?
                                        <div data-test="description">
                                            <dt>Description</dt>
                                            <dd className="sentence-case">{context.description}</dd>
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
                                            <dd className="sentence-case">{context.age}{context.age_units ? ` ${context.age_units}` : null}</dd>
                                        </div>
                                    : null}

                                    {synchText ?
                                        <div data-test="biosample-synchronization">
                                            <dt>Synchronization timepoint</dt>
                                            <dd className="sentence-case">{synchText}</dd>
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

                                    {context.depleted_in_term_name && context.depleted_in_term_name.length ?
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

                                    {context.parent_of && context.parent_of.length ?
                                        <div data-test="parentof">
                                            <dt>Parent of biosamples</dt>
                                            <dd>
                                                {context.parent_of.map((biosample, i) =>
                                                    <span>
                                                        {i > 0 ? <span>, </span> : null}
                                                        <a href={biosample['@id']}>{biosample.accession}</a>
                                                    </span>
                                                )}
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

                                    {context.dbxrefs && context.dbxrefs.length ?
                                        <div data-test="externalresources">
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

                                    {context.date_obtained ?
                                        <div data-test="dateobtained">
                                            <dt>Date obtained</dt>
                                            <dd>{context.date_obtained}</dd>
                                        </div>
                                    : null}

                                    {context.aliases.length ?
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

                                    {tagBadges ?
                                        <div className="tag-badges" data-test="tags">
                                            <dt>Tags</dt>
                                            <dd>{tagBadges}</dd>
                                        </div>
                                    : null}
                                </dl>
                            </div>
                        </div>

                        {context.pooled_from && context.pooled_from.length ?
                            <section data-test="pooledfrom">
                                <hr />
                                <h4>Pooled from biosamples</h4>
                                <ul className="non-dl-list">
                                    {context.pooled_from.map(biosample => (
                                        <li key={biosample['@id']}>
                                            <a href={biosample['@id']}>{biosample.accession}</a>
                                        </li>
                                    ))}
                                </ul>
                            </section>
                        : null}

                        {context.treatments.length ?
                            <section>
                                <hr />
                                <h4>Treatment details</h4>
                                {context.treatments.map(treatment => treatmentDisplay(treatment))}
                            </section>
                        : null}
                    </PanelBody>
                </Panel>

                {context.applied_modifications && context.applied_modifications.length ?
                    <GeneticModificationSummary geneticModifications={context.applied_modifications} />
                : null}

                {context.donor ?
                    <div>
                        {PanelLookup({ context: context.donor, biosample: context })}
                    </div>
                : null}

                <RelatedItems
                    title="Experiments using this biosample"
                    url={`/search/?type=Experiment&replicates.library.biosample.uuid=${context.uuid}`}
                    Component={ExperimentTable}
                />

                <RelatedItems
                    title="Biosamples that are part of this biosample"
                    url={`/search/?type=Biosample&part_of.uuid=${context.uuid}`}
                    Component={BiosampleTable}
                />

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

                {combinedDocs.length ?
                    <DocumentsPanel documentSpecs={[{ documents: combinedDocs }]} />
                : null}
            </div>
        );
    }
}
/* eslint-enable react/prefer-stateless-function */

BiosampleComponent.propTypes = {
    context: PropTypes.object.isRequired, // ENCODE biosample object to be rendered
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

BiosampleComponent.contextTypes = {
    session: PropTypes.object, // Login information
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
};

// Display the biosample term ID given in `termId`, and link to a corresponding site if the prefix
// of the term ID needs it. Any term IDs with prefixes not maching any in the `urlMap` property
// simply display without a link.
const BiosampleTermId = (props) => {
    const termId = props.termId;

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

    // biosample_term_id is a required property, but just in case...
    return null;
};

BiosampleTermId.propTypes = {
    termId: PropTypes.string, // Biosample whose term is being displayed.
};

BiosampleTermId.defaultProps = {
    termId: '',
};


const Treatment = (props) => {
    const context = props.context;

    const treatmentText = singleTreatment(context);
    return (
        <dl className="key-value">
            <div data-test="treatment">
                <dt>Treatment</dt>
                <dd>{treatmentText}</dd>
            </div>

            <div data-test="type">
                <dt>Type</dt>
                <dd>{context.treatment_type}</dd>
            </div>
        </dl>
    );
};

Treatment.propTypes = {
    context: PropTypes.object.isRequired, // Treatment context object
};

globals.panelViews.register(Treatment, 'Treatment');


// Biosample and donor characterization documents

const EXCERPT_LENGTH = 80; // Maximum number of characters in an excerpt

// Document header component -- Characterizations
const CharacterizationHeader = props => (
    <div className="document__header">
        {props.doc.characterization_method}
    </div>
);

CharacterizationHeader.propTypes = {
    doc: PropTypes.object.isRequired, // Document object to render
};


// Document caption component -- Characterizations
const CharacterizationCaption = (props) => {
    const doc = props.doc;
    const caption = doc.caption;
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
    const docs = characterization.documents && characterization.documents.length ?
        characterization.documents.filter(doc => !!(doc.attachment && doc.attachment.href && doc.attachment.download))
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

                {docs.length ?
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


// Parts of individual document panels
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
