'use strict';
const React = require('react');
import PropTypes from 'prop-types';
import createReactClass from 'create-react-class';
const panel = require('../libs/bootstrap/panel');
const _ = require('underscore');
const url = require('url');
import { auditDecor } from './audit';
const globals = require('./globals');
const navigation = require('./navigation');
const dataset = require('./dataset');
const dbxref = require('./dbxref');
import StatusLabel from './statuslabel';
const image = require('./image');
const item = require('./item');
const { pubReferenceList } = require('./reference');
const { singleTreatment, treatmentDisplay } = require('./objectutils');
const doc = require('./doc');
const {BiosampleSummaryString, CollectBiosampleDocs, BiosampleTable} = require('./typeutils');
const {GeneticModificationSummary} = require('./genetic_modification');

const Breadcrumbs = navigation.Breadcrumbs;
const DbxrefList = dbxref.DbxrefList;
const {Document, DocumentsPanel, DocumentsSubpanels, DocumentPreview, DocumentFile} = doc;
const ExperimentTable = dataset.ExperimentTable;
const RelatedItems = item.RelatedItems;
const ProjectBadge = image.ProjectBadge;
const {Panel, PanelBody, PanelHeading} = panel;


var PanelLookup = function (props) {
    // XXX not all panels have the same markup
    var context;
    if (props['@id']) {
        context = props;
        props = {context: context, key: context['@id']};
    }
    var PanelView = globals.panel_views.lookup(props.context);
    return <PanelView key={props.context.uuid} {...props} />;
};


var BiosampleComponent = module.exports.Biosample = createReactClass({
    contextTypes: {
        session: PropTypes.object, // Login information from <App>
    },

    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-item');
        var aliasList = context.aliases.join(", ");

        // Set up the breadcrumbs
        var crumbs = [
            {id: 'Biosamples'},
            {id: context.biosample_type, query: 'biosample_type=' + context.biosample_type, tip: context.biosample_type},
            {id: <i>{context.organism.scientific_name}</i>, query: 'organism.scientific_name=' + context.organism.scientific_name, tip: context.organism.scientific_name},
            {id: context.biosample_term_name, query: 'biosample_term_name=' + context.biosample_term_name, tip: context.biosample_term_name}
        ];

        // Build the text of the synchronization string
        var synchText;
        if (context.synchronization) {
            synchText = context.synchronization +
                (context.post_synchronization_time ?
                    ' + ' + context.post_synchronization_time + (context.post_synchronization_time_units ? ' ' + context.post_synchronization_time_units : '')
                : '');
        }

        // Collect all documents in this biosample
        var combinedDocs = CollectBiosampleDocs(context);

        // If this biosample is part of another, collect those documents too, then remove
        // any duplicate documents in the combinedDocs array.
        if (context.part_of) {
            var parentCombinedDocs = CollectBiosampleDocs(context.part_of);
            combinedDocs = combinedDocs.concat(parentCombinedDocs);
        }
        combinedDocs = globals.uniqueObjectsArray(combinedDocs);

        // Collect up biosample and model organism donor constructs
        var constructs = ((context.constructs && context.constructs.length) ? context.constructs : [])
            .concat((context.model_organism_donor_constructs && context.model_organism_donor_constructs.length) ? context.model_organism_donor_constructs : []);

        // Make string of alternate accessions
        var altacc = context.alternate_accessions ? context.alternate_accessions.join(', ') : undefined;

        // Get a list of reference links, if any
        var references = pubReferenceList(context.references);

        // Render tags badges
        var tagBadges;
        if (context.internal_tags && context.internal_tags.length) {
            tagBadges = context.internal_tags.map(tag => <img src={'/static/img/tag-' + tag + '.png'} alt={tag + ' tag'} />);
        }

        // Make the donor panel (if any) title
        var donorPanelTitle;
        if (context.donor) {
            donorPanelTitle = (context.donor.organism.name === 'human' ? 'Donor' : 'Strain') + ' information';
        }

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs root='/search/?type=Biosample' crumbs={crumbs} />
                        <h2>
                            {context.accession}{' / '}<span className="sentence-case">{context.biosample_type}</span>
                        </h2>
                        {altacc ? <h4 className="repl-acc">Replaces {altacc}</h4> : null}
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
                                            <dd className="sentence-case">{context.age}{context.age_units ? ' ' + context.age_units : null}</dd>
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
                                                {context.depleted_in_term_name.map(function(termName, i) {
                                                    return (
                                                        <span key={i}>
                                                            {i > 0 ? ', ' : ''}
                                                            {termName}
                                                        </span>
                                                    );
                                                })}
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
                                            <dd><DbxrefList values={context.dbxrefs} /></dd>
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

                        {context.pooled_from.length ?
                            <section data-test="pooledfrom">
                                <hr />
                                <h4>Pooled from biosamples</h4>
                                <ul className="non-dl-list">
                                    {context.pooled_from.map(function (biosample) {
                                        return (
                                            <li key={biosample['@id']}>
                                                <a href={biosample['@id']}>{biosample.accession}</a>
                                            </li>
                                        );
                                    })}
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

                        {constructs.length ?
                            <section>
                                <hr />
                                <h4>Construct details</h4>
                                <div>
                                    {constructs.map(construct =>
                                        <div key={construct.uuid} className="subpanel">
                                            {PanelLookup(construct)}
                                        </div>
                                    )}
                                </div>
                            </section>
                        : null}

                        {context.rnais.length ?
                            <section>
                                <hr />
                                <h4>RNAi details</h4>
                                {context.rnais.map(PanelLookup)}
                            </section>
                        : null}
                    </PanelBody>
                </Panel>

                {context.genetic_modifications && context.genetic_modifications.length ?
                    <GeneticModificationSummary geneticModifications={context.genetic_modifications} />
                : null}

                {context.donor ?
                    <div>
                        {PanelLookup({ context: context.donor, biosample: context })}
                    </div>
                : null}

                <RelatedItems
                    title="Experiments using this biosample"
                    url={'/search/?type=Experiment&replicates.library.biosample.uuid=' + context.uuid}
                    Component={ExperimentTable} ignoreErrors />

                <RelatedItems title="Biosamples that are part of this biosample"
                              url={'/search/?type=Biosample&part_of.uuid=' + context.uuid}
                              Component={BiosampleTable} ignoreErrors />

                <RelatedItems title="Biosamples originating from this biosample"
                              url={'/search/?type=Biosample&originated_from.uuid=' + context.uuid}
                              Component={BiosampleTable} ignoreErrors />

                <RelatedItems title="Biosamples that are pooled from this biosample"
                              url={'/search/?type=Biosample&pooled_from.uuid=' + context.uuid}
                              Component={BiosampleTable} ignoreErrors />

                {combinedDocs.length ?
                    <DocumentsPanel documentSpecs={[{documents: combinedDocs}]} />
                : null}
            </div>
        );
    }
});

const Biosample = auditDecor(BiosampleComponent);

globals.content_views.register(Biosample, 'Biosample');


var MaybeLink = createReactClass({
    render() {
        if (!this.props.href || this.props.href === 'N/A') {
            return <span>{this.props.children}</span>;
        } else {
            return (
                <a {...this.props}>{this.props.children}</a>
            );
        }
    }
});


// Display the biosample term ID given in `termId`, and link to a corresponding site if the prefix
// of the term ID needs it. Any term IDs with prefixes not maching any in the `urlMap` property
// simply display without a link.
var BiosampleTermId = createReactClass({
    propTypes: {
        termId: PropTypes.string // Biosample whose term is being displayed.
    },

    // Map from prefixes to corresponding URL bases. Not all term ID prefixes covered here.
    // Specific term IDs are appended to these after converting ':' to '_'.
    urlMap: {
        'EFO': 'http://www.ebi.ac.uk/efo/',
        'UBERON': 'http://www.ontobee.org/ontology/UBERON?iri=http://purl.obolibrary.org/obo/',
        'CL': 'http://www.ontobee.org/ontology/CL?iri=http://purl.obolibrary.org/obo/'
    },

    render: function() {
        var termId = this.props.termId;

        if (termId) {
            // All are of the form XXX:nnnnnnn...
            var idPieces = termId.split(':');
            if (idPieces.length === 2) {
                var urlBase = this.urlMap[idPieces[0]];
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
    }
});


var Treatment = module.exports.Treatment = createReactClass({
    render: function() {
        var context = this.props.context;
        var treatmentText = '';

        treatmentText = singleTreatment(context);
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
    }
});

globals.panel_views.register(Treatment, 'Treatment');


var Construct = module.exports.Construct = createReactClass({
    render: function() {
        var context = this.props.context;
        var embeddedDocs = this.props.embeddedDocs;
        var construct_documents = {};
        context.documents.forEach(function (doc) {
            construct_documents[doc['@id']] = PanelLookup({context: doc, embeddedDocs: embeddedDocs});
        });

        return (
            <div>
                <dl className="key-value">
                    {context.target ?
                        <div data-test="target">
                            <dt>Target</dt>
                            <dd><a href={context.target['@id']}>{context.target.name}</a></dd>
                        </div>
                    : null}

                    {context.vector_backbone_name ?
                        <div data-test="vector">
                            <dt>Vector</dt>
                            <dd>{context.vector_backbone_name}</dd>
                        </div>
                    : null}

                    {context.construct_type ?
                        <div data-test="construct-type">
                            <dt>Construct Type</dt>
                            <dd>{context.construct_type}</dd>
                        </div>
                    : null}

                    {context.description ?
                        <div data-test="description">
                            <dt>Description</dt>
                            <dd>{context.description}</dd>
                        </div>
                    : null}

                    {context.tags.length ?
                        <div data-test="tags">
                            <dt>Tags</dt>
                            <dd>
                                <ul>
                                    {context.tags.map(function (tag, index) {
                                        return (
                                            <li key={index}>
                                                {tag.name} (Location: {tag.location})
                                            </li>
                                        );
                                    })}
                                </ul>
                            </dd>
                        </div>
                    : null}

                    {context.source.title ?
                        <div data-test="source">
                            <dt>Source</dt>
                            <dd>{context.source.title}</dd>
                        </div>
                    : null}

                    {context.product_id ?
                        <div data-test="product-id">
                            <dt>Product ID</dt>
                            <dd><MaybeLink href={context.url}>{context.product_id}</MaybeLink></dd>
                        </div>
                    : null}
                </dl>

                {embeddedDocs && Object.keys(construct_documents).length ?
                    <div>
                        <hr />
                        <h4>Construct documents</h4>
                        <div className="row">{construct_documents}</div>
                    </div>
                : null}
            </div>
        );
    }
});

globals.panel_views.register(Construct, 'Construct');


var RNAi = module.exports.RNAi = createReactClass({
    render: function() {
        var context = this.props.context;
        return (
             <dl className="key-value">
                {context.target ?
                    <div data-test="target">
                        <dt>Target</dt>
                        <dd><a href={context.target['@id']}>{context.target.name}</a></dd>
                    </div>
                : null}

                {context.rnai_type ?
                    <div data-test="type">
                        <dt>RNAi type</dt>
                        <dd>{context.rnai_type}</dd>
                    </div>
                : null}

                {context.source && context.source.title ?
                    <div data-test="source">
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

                {context.product_id ?
                    <div data-test="productid">
                        <dt>Product ID</dt>
                        <dd>
                            {context.url ?
                                <a href={context.url}>{context.product_id}</a>
                            :
                                <span>{context.product_id}</span>
                            }
                        </dd>
                    </div>
                : null}

                {context.rnai_target_sequence ?
                    <div data-test="targetsequence">
                        <dt>Target sequence</dt>
                        <dd>{context.rnai_target_sequence}</dd>
                    </div>
                : null}

                {context.vector_backbone_name ?
                    <div data-test="vectorbackbone">
                        <dt>Vector backbone</dt>
                        <dd>{context.vector_backbone_name}</dd>
                    </div>
                : null}
            </dl>
        );
    }
});

globals.panel_views.register(RNAi, 'RNAi');


//**********************************************************************
// Biosample and donor characterization documents

const EXCERPT_LENGTH = 80; // Maximum number of characters in an excerpt

// Document header component -- Characterizations
var CharacterizationHeader = createReactClass({
    propTypes: {
        doc: PropTypes.object.isRequired // Document object to render
    },

    render: function() {
        var doc = this.props.doc;

        return (
            <div className="document__header">
                {doc.characterization_method}
            </div>
        );
    }
});

// Document caption component -- Characterizations
var CharacterizationCaption = createReactClass({
    propTypes: {
        doc: PropTypes.object.isRequired // Document object to render
    },

    render: function() {
        var doc = this.props.doc;
        var excerpt, caption = doc.caption;
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
    }
});

// Document detail component -- default
var CharacterizationDetail = createReactClass({
    propTypes: {
        doc: PropTypes.object.isRequired, // Document object to render
        detailOpen: PropTypes.bool, // True if detail panel is visible
        key: PropTypes.string // Unique key for identification
    },

    render: function() {
        var doc = this.props.doc;
        var keyClass = 'document__detail' + (this.props.detailOpen ? ' active' : '');
        var excerpt = doc.description && doc.description.length > EXCERPT_LENGTH;

        return (
            <div className={keyClass}>
                <dl className='key-value-doc' id={'panel' + this.props.id} aria-labelledby={'tab' + this.props.id} role="tabpanel">
                    {excerpt ?
                        <div data-test="caption">
                            <dt>Caption</dt>
                            <dd>{doc.caption}</dd>
                        </div>
                    : null}

                    {doc.submitted_by && doc.submitted_by.title ?
                        <div data-test="submitted-by">
                            <dt>Submitted by</dt>
                            <dd>{doc.submitted_by.title}</dd>
                        </div>
                    : null}

                    <div data-test="lab">
                        <dt>Lab</dt>
                        <dd>{doc.lab.title}</dd>
                    </div>

                    {doc.award && doc.award.name ?
                        <div data-test="award">
                            <dt>Grant</dt>
                            <dd><a href={doc.award['@id']}>{doc.award.name}</a></dd>
                        </div>
                    : null}
                </dl>
            </div>
        );
    }
});

// Parts of individual document panels
globals.panel_views.register(Document, 'BiosampleCharacterization');
globals.panel_views.register(Document, 'DonorCharacterization');

globals.document_views.header.register(CharacterizationHeader, 'BiosampleCharacterization');
globals.document_views.header.register(CharacterizationHeader, 'DonorCharacterization');

globals.document_views.caption.register(CharacterizationCaption, 'BiosampleCharacterization');
globals.document_views.caption.register(CharacterizationCaption, 'DonorCharacterization');

globals.document_views.preview.register(DocumentPreview, 'BiosampleCharacterization');
globals.document_views.preview.register(DocumentPreview, 'DonorCharacterization');

globals.document_views.file.register(DocumentFile, 'BiosampleCharacterization');
globals.document_views.file.register(DocumentFile, 'DonorCharacterization');

globals.document_views.detail.register(CharacterizationDetail, 'BiosampleCharacterization');
globals.document_views.detail.register(CharacterizationDetail, 'DonorCharacterization');
