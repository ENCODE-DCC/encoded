'use strict';
var React = require('react');
var panel = require('../libs/bootstrap/panel');
var _ = require('underscore');
var url = require('url');
var globals = require('./globals');
var navigation = require('./navigation');
var dataset = require('./dataset');
var dbxref = require('./dbxref');
var statuslabel = require('./statuslabel');
var audit = require('./audit');
var image = require('./image');
var item = require('./item');
var reference = require('./reference');
var objectutils = require('./objectutils');
var sortTable = require('./sorttable');
var doc = require('./doc');
var {BiosampleSummaryString, CollectBiosampleDocs} = require('./typeutils');

var Breadcrumbs = navigation.Breadcrumbs;
var DbxrefList = dbxref.DbxrefList;
var StatusLabel = statuslabel.StatusLabel;
var AuditIndicators = audit.AuditIndicators;
var AuditDetail = audit.AuditDetail;
var AuditMixin = audit.AuditMixin;
var {Document, DocumentsPanel, DocumentsSubpanels, DocumentPreview, DocumentFile} = doc;
var ExperimentTable = dataset.ExperimentTable;
var PubReferenceList = reference.PubReferenceList;
var RelatedItems = item.RelatedItems;
var SingleTreatment = objectutils.SingleTreatment;
var SortTablePanel = sortTable.SortTablePanel;
var SortTable = sortTable.SortTable;
var ProjectBadge = image.ProjectBadge;
var {Panel, PanelBody, PanelHeading} = panel;


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


// Display a table of retrieved biosamples related to the displayed biosample
var BiosampleTable = React.createClass({
    columns: {
        'accession': {
            title: 'Accession',
            display: function(biosample) {
                return <a href={biosample['@id']}>{biosample.accession}</a>;
            }
        },
        'biosample_type': {title: 'Type'},
        'biosample_term_name': {title: 'Term'},
        'summary': {title: 'Summary', sorter: false}
    },

    render: function() {
        var biosamples;

        // If there's a limit on entries to display and the array is greater than that
        // limit, then clone the array with just that specified number of elements
        if (this.props.limit && (this.props.limit < this.props.items.length)) {
            // Limit the experiment list by cloning first {limit} elements
            biosamples = this.props.items.slice(0, this.props.limit);
        } else {
            // No limiting; just reference the original array
            biosamples = this.props.items;
        }

        return (
            <SortTablePanel title={this.props.title}>
                <SortTable list={this.props.items} columns={this.columns} footer={<BiosampleTableFooter items={biosamples} total={this.props.total} url={this.props.url} />} />
            </SortTablePanel>
        );
    }
});

// Display a count of biosamples in the footer, with a link to the corresponding search if needed
var BiosampleTableFooter = React.createClass({
    render: function() {
        var {items, total, url} = this.props;

        return (
            <div>
                <span>Displaying {items.length} of {total} </span>
                {items.length < total ? <a className="btn btn-info btn-xs pull-right" href={url}>View all</a> : null}
            </div>
        );
    }
});


var Biosample = module.exports.Biosample = React.createClass({
    mixins: [AuditMixin],
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

        // Set up TALENs panel for multiple TALENs
        var talens = null;
        if (context.talens && context.talens.length) {
            talens = context.talens.map(talen => {
                return PanelLookup({context: talen});
            });
        }

        // Collect up biosample and model organism donor constructs
        var constructs = ((context.constructs && context.constructs.length) ? context.constructs : [])
            .concat((context.model_organism_donor_constructs && context.model_organism_donor_constructs.length) ? context.model_organism_donor_constructs : []);

        // Make string of alternate accessions
        var altacc = context.alternate_accessions ? context.alternate_accessions.join(', ') : undefined;

        // Get a list of reference links, if any
        var references = PubReferenceList(context.references);

        // Render tags badges
        var tagBadges;
        if (context.internal_tags && context.internal_tags.length) {
            tagBadges = context.internal_tags.map(tag => <img src={'/static/img/tag-' + tag + '.png'} alt={tag + ' tag'} />);
        }

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs root='/search/?type=biosample' crumbs={crumbs} />
                        <h2>
                            {context.accession}{' / '}<span className="sentence-case">{context.biosample_type}</span>
                        </h2>
                        {altacc ? <h4 className="repl-acc">Replaces {altacc}</h4> : null}
                        <div className="status-line">
                            <div className="characterization-status-labels">
                                <StatusLabel title="Status" status={context.status} />
                            </div>
                            <AuditIndicators audits={context.audit} id="biosample-audit" />
                        </div>
                    </div>
                </header>
                <AuditDetail context={context} id="biosample-audit" />
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

                                    {context.derived_from ?
                                        <div data-test="derivedfrom">
                                            <dt>Derived from biosample</dt>
                                            <dd><a href={context.derived_from['@id']}>{context.derived_from.accession}</a></dd>
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
                                {context.treatments.map(PanelLookup)}
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

                {context.donor ?
                    <div>
                        <h3>{context.donor.organism.name === 'human' ? 'Donor' : 'Strain'} information</h3>
                        <div className="data-display">
                            {PanelLookup({context: context.donor, biosample: context})}
                        </div>
                    </div>
                : null}

                {talens ?
                    <div>
                        <h3>TALENs</h3>
                        <Panel>
                            <div className="data-display">
                                {talens}
                            </div>
                        </Panel>
                    </div>
                : null}

                <RelatedItems
                    title="Experiments using this biosample"
                    url={'/search/?type=experiment&replicates.library.biosample.uuid=' + context.uuid}
                    Component={ExperimentTable} />

                <RelatedItems title="Biosamples that are part of this biosample"
                              url={'/search/?type=biosample&part_of.uuid=' + context.uuid}
                              Component={BiosampleTable} />

                <RelatedItems title="Biosamples that are derived from this biosample"
                              url={'/search/?type=biosample&derived_from.uuid=' + context.uuid}
                              Component={BiosampleTable} />

                <RelatedItems title="Biosamples that are pooled from this biosample"
                              url={'/search/?type=biosample&pooled_from.uuid=' + context.uuid}
                              Component={BiosampleTable} />

                {combinedDocs.length ?
                    <DocumentsPanel documentSpecs={[{documents: combinedDocs}]} />
                : null}
            </div>
        );
    }
});

globals.content_views.register(Biosample, 'Biosample');


var MaybeLink = React.createClass({
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
var BiosampleTermId = React.createClass({
    propTypes: {
        termId: React.PropTypes.string // Biosample whose term is being displayed.
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


var HumanDonor = module.exports.HumanDonor = React.createClass({
    render: function() {
        var context = this.props.context;
        var biosample = this.props.biosample;
        var references = PubReferenceList(context.references);

        // Render tags badges
        var tagBadges;
        if (context.internal_tags && context.internal_tags.length) {
            tagBadges = context.internal_tags.map(tag => <img src={'/static/img/tag-' + tag + '.png'} alt={tag + ' tag'} />);
        }

        return (
            <div>
                <Panel>
                    <PanelBody>
                        <dl className="key-value">
                            <div data-test="accession">
                                <dt>Accession</dt>
                                <dd>{biosample ? <a href={context['@id']}>{context.accession}</a> : context.accession}</dd>
                            </div>

                            {context.aliases.length ?
                                <div data-test="aliases">
                                    <dt>Aliases</dt>
                                    <dd>{context.aliases.join(", ")}</dd>
                                </div>
                            : null}

                            {context.organism.scientific_name ?
                                <div data-test="species">
                                    <dt>Species</dt>
                                    <dd className="sentence-case"><em>{context.organism.scientific_name}</em></dd>
                                </div>
                            : null}

                            {context.life_stage ?
                                <div data-test="life-stage">
                                    <dt>Life stage</dt>
                                    <dd className="sentence-case">{context.life_stage}</dd>
                                </div>
                            : null}

                            {context.age ?
                                <div data-test="age">
                                    <dt>Age</dt>
                                    <dd className="sentence-case">{context.age}{context.age_units ? ' ' + context.age_units : null}</dd>
                                </div>
                            : null}

                            {context.sex ?
                                <div data-test="sex">
                                    <dt>Sex</dt>
                                    <dd className="sentence-case">{context.sex}</dd>
                                </div>
                            : null}

                            {context.health_status ?
                                <div data-test="health-status">
                                    <dt>Health status</dt>
                                    <dd className="sentence-case">{context.health_status}</dd>
                                </div>
                            : null}

                            {context.ethnicity ?
                                <div data-test="ethnicity">
                                    <dt>Ethnicity</dt>
                                    <dd className="sentence-case">{context.ethnicity}</dd>
                                </div>
                            : null}

                            {context.dbxrefs && context.dbxrefs.length ?
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

                            {tagBadges ?
                                <div className="tag-badges" data-test="tags">
                                    <dt>Tags</dt>
                                    <dd>{tagBadges}</dd>
                                </div>
                            : null}
                        </dl>
                    </PanelBody>
                </Panel>
            </div>
        );
    }
});

globals.panel_views.register(HumanDonor, 'HumanDonor');


var MouseDonor = module.exports.MouseDonor = React.createClass({
    render: function() {
        var context = this.props.context;
        var biosample = this.props.biosample;
        var donorUrlDomain;
        var references = PubReferenceList(context.references);

        // Get the domain name of the donor URL
        if (biosample && biosample.donor && biosample.donor.url) {
            var donorUrl = url.parse(biosample.donor.url);
            donorUrlDomain = donorUrl.hostname || '';
        }

        // Render tags badges
        var tagBadges;
        if (context.internal_tags && context.internal_tags.length) {
            tagBadges = context.internal_tags.map(tag => <img src={'/static/img/tag-' + tag + '.png'} alt={tag + ' tag'} />);
        }

        return (
            <div>
                <Panel>
                    <PanelBody>
                        <dl className="key-value">
                            <div data-test="accession">
                                <dt>Accession</dt>
                                <dd>{biosample ? <a href={context['@id']}>{context.accession}</a> : context.accession}</dd>
                            </div>

                            {context.aliases.length ?
                                <div data-test="aliases">
                                    <dt>Aliases</dt>
                                    <dd>{context.aliases.join(", ")}</dd>
                                </div>
                            : null}

                            {context.organism.scientific_name ?
                                <div data-test="organism">
                                    <dt>Species</dt>
                                    <dd className="sentence-case"><em>{context.organism.scientific_name}</em></dd>
                                </div>
                            : null}

                            {context.genotype ?
                                <div data-test="genotype">
                                    <dt>Genotype</dt>
                                    <dd>{context.genotype}</dd>
                                </div>
                            : null}

                            {context.mutated_gene && biosample && biosample.donor && biosample.donor.mutated_gene && biosample.donor.mutated_gene.label ?
                                <div data-test="mutatedgene">
                                    <dt>Mutated gene</dt>
                                    <dd><a href={context.mutated_gene}>{biosample.donor.mutated_gene.label}</a></dd>
                                </div>
                            : null}

                            {biosample && biosample.sex ?
                                <div data-test="sex">
                                    <dt>Sex</dt>
                                    <dd className="sentence-case">{biosample.sex}</dd>
                                </div>
                            : null}

                            {biosample && biosample.health_status ?
                                <div data-test="health-status">
                                    <dt>Health status</dt>
                                    <dd className="sentence-case">{biosample.health_status}</dd>
                                </div>
                            : null}

                            {donorUrlDomain ?
                                <div data-test="mutatedgene">
                                    <dt>Strain reference</dt>
                                    <dd><a href={biosample.donor.url}>{donorUrlDomain}</a></dd>
                                </div>
                            : null}

                            {context.strain_background ?
                                <div data-test="strain-background">
                                    <dt>Strain background</dt>
                                    <dd className="sentence-case">{context.strain_background}</dd>
                                </div>
                            : null}

                            {context.strain_name ?
                                <div data-test="strain-name">
                                    <dt>Strain name</dt>
                                    <dd>{context.strain_name}</dd>
                                </div>
                            : null}

                            {context.dbxrefs && context.dbxrefs.length ?
                                <div data-test="external-resources">
                                    <dt>External resources</dt>
                                    <dd><DbxrefList values={context.dbxrefs} /></dd>
                                </div>
                            : null}

                            {context.references && context.references.length ?
                                <div data-test="references">
                                    <dt>References</dt>
                                    <dd>{PubReferenceList(context.references)}</dd>
                                </div>
                            : null}

                            {tagBadges ?
                                <div className="tag-badges" data-test="tags">
                                    <dt>Tags</dt>
                                    <dd>{tagBadges}</dd>
                                </div>
                            : null}
                        </dl>

                        {biosample && biosample.donor.characterizations && biosample.donor.characterizations.length ?
                            <div>
                                <hr />
                                <h4>Characterizations</h4>
                                <PanelBody addClasses="panel-body-doc-interior">
                                    <DocumentsSubpanels documentSpec={{documents: biosample.donor.characterizations}} />
                                </PanelBody>
                            </div>
                        : null}
                    </PanelBody>
                </Panel>
            </div>
        );
    }
});

globals.panel_views.register(MouseDonor, 'MouseDonor');


var FlyWormDonor = module.exports.FlyDonor = React.createClass({
    render: function() {
        var context = this.props.context;
        var biosample = this.props.biosample;
        var donorUrlDomain;

        // Render tags badges
        var tagBadges;
        if (context.internal_tags && context.internal_tags.length) {
            tagBadges = context.internal_tags.map(tag => <img src={'/static/img/tag-' + tag + '.png'} alt={tag + ' tag'} />);
        }

        return (
            <div>
                <Panel>
                    <PanelBody>
                        <dl className="key-value">
                            <div data-test="accession">
                                <dt>Accession</dt>
                                <dd>{biosample ? <a href={context['@id']}>{context.accession}</a> : context.accession}</dd>
                            </div>

                            {context.aliases.length ?
                                <div data-test="aliases">
                                    <dt>Aliases</dt>
                                    <dd>{context.aliases.join(", ")}</dd>
                                </div>
                            : null}

                            {context.organism.scientific_name ?
                                <div data-test="species">
                                    <dt>Species</dt>
                                    <dd className="sentence-case"><em>{context.organism.scientific_name}</em></dd>
                                </div>
                            : null}

                            {context.genotype ?
                                <div data-test="genotype">
                                    <dt>Genotype</dt>
                                    <dd>{context.genotype}</dd>
                                </div>
                            : null}

                            {context.mutated_gene && biosample && biosample.donor && biosample.donor.mutated_gene && biosample.donor.mutated_gene.label ?
                                <div data-test="mutatedgene">
                                    <dt>Mutated gene</dt>
                                    <dd><a href={context.mutated_gene['@id']}>{biosample.donor.mutated_gene.label}</a></dd>
                                </div>
                            : null}

                            {biosample && biosample.sex ?
                                <div data-test="sex">
                                    <dt>Sex</dt>
                                    <dd className="sentence-case">{biosample.sex}</dd>
                                </div>
                            : null}

                            {biosample && biosample.health_status ?
                                <div data-test="health-status">
                                    <dt>Health status</dt>
                                    <dd className="sentence-case">{biosample.health_status}</dd>
                                </div>
                            : null}

                            {donorUrlDomain ?
                                <div data-test="mutatedgene">
                                    <dt>Strain reference</dt>
                                    <dd><a href={biosample.donor.url}>{donorUrlDomain}</a></dd>
                                </div>
                            : null}

                            {context.strain_background ?
                                <div data-test="strain-background">
                                    <dt>Strain background</dt>
                                    <dd className="sentence-case">{context.strain_background}</dd>
                                </div>
                            : null}

                            {context.strain_name ?
                                <div data-test="strain-name">
                                    <dt>Strain name</dt>
                                    <dd>{context.strain_name}</dd>
                                </div>
                            : null}

                            {context.dbxrefs && context.dbxrefs.length ?
                                <div data-test="external-resources">
                                    <dt>External resources</dt>
                                    <dd><DbxrefList values={context.dbxrefs} /></dd>
                                </div>
                            : null}

                            {tagBadges ?
                                <div className="tag-badges" data-test="tags">
                                    <dt>Tags</dt>
                                    <dd>{tagBadges}</dd>
                                </div>
                            : null}
                        </dl>
                    </PanelBody>
                </Panel>
            </div>
        );
    }
});

globals.panel_views.register(FlyWormDonor, 'FlyDonor');
globals.panel_views.register(FlyWormDonor, 'WormDonor');


var Donor = module.exports.Donor = React.createClass({
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-item');
        var altacc = context.alternate_accessions ? context.alternate_accessions.join(', ') : undefined;
        var characterizationDocuments = [];
        var donorDocuments = [];
        var combinedDocuments = [];

        // Collect the characterization documents
        if (context.characterizations && context.characterizations.length) {
            characterizationDocuments = context.characterizations;
        }

        // Collect the donor documents
        if (context.documents && context.documents.length) {
            donorDocuments = context.documents;
        }

        // Combine characterization and donor documents
        combinedDocuments = [].concat(characterizationDocuments, donorDocuments);

        // Set up breadcrumbs
        var crumbs = [
            {id: 'Donors'},
            {id: <i>{context.organism.scientific_name}</i>}
        ];

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs crumbs={crumbs} />
                        <h2>{context.accession}</h2>
                        {altacc ? <h4 className="repl-acc">Replaces {altacc}</h4> : null}
                        <div className="status-line">
                            <div className="characterization-status-labels">
                                <StatusLabel title="Status" status={context.status} />
                            </div>
                        </div>
                    </div>
                </header>

                <div>{PanelLookup(context)}</div>

                <RelatedItems title={"Biosamples from this " + (context.organism.name == 'human' ? 'donor': 'strain')}
                              url={'/search/?type=biosample&donor.uuid=' + context.uuid}
                              Component={BiosampleTable} />

                {combinedDocuments.length ?
                    <DocumentsPanel documentSpecs={[{documents: combinedDocuments}]} />
                : null}
            </div>
        );
    }
});

globals.content_views.register(Donor, 'Donor');


var Treatment = module.exports.Treatment = React.createClass({
    render: function() {
        var context = this.props.context;
        var treatmentText = '';

        treatmentText = SingleTreatment(context);
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


var Construct = module.exports.Construct = React.createClass({
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


var RNAi = module.exports.RNAi = React.createClass({
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
var CharacterizationHeader = React.createClass({
    propTypes: {
        doc: React.PropTypes.object.isRequired // Document object to render
    },

    render: function() {
        var doc = this.props.doc;

        return (
            <div className="panel-header document-title sentence-case">
                {doc.characterization_method}
            </div>
        );
    }
});

// Document caption component -- Characterizations
var CharacterizationCaption = React.createClass({
    propTypes: {
        doc: React.PropTypes.object.isRequired // Document object to render
    },

    render: function() {
        var doc = this.props.doc;
        var excerpt, caption = doc.caption;
        if (caption && caption.length > EXCERPT_LENGTH) {
            excerpt = globals.truncateString(caption, EXCERPT_LENGTH);
        }

        return (
            <div className="document-intro document-meta-data">
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
var CharacterizationDetail = React.createClass({
    propTypes: {
        doc: React.PropTypes.object.isRequired, // Document object to render
        detailOpen: React.PropTypes.bool, // True if detail panel is visible
        key: React.PropTypes.string // Unique key for identification
    },

    render: function() {
        var doc = this.props.doc;
        var keyClass = 'document-slider' + (this.props.detailOpen ? ' active' : '');
        var excerpt = doc.description && doc.description.length > EXCERPT_LENGTH;

        return (
            <div className={keyClass}>
                <dl className='key-value-doc' id={'panel' + this.props.key} aria-labeledby={'tab' + this.props.key} role="tabpanel">
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
                            <dd>{doc.award.name}</dd>
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
