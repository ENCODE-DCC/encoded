'use strict';
var React = require('react/addons');
var panel = require('../libs/bootstrap/panel');
var button = require('../libs/bootstrap/button');
var dropdownMenu = require('../libs/bootstrap/dropdown-menu');
var _ = require('underscore');
var moment = require('moment');
var globals = require('./globals');
var navigation = require('./navigation');
var dbxref = require('./dbxref');
var fetched = require('./fetched');
var audit = require('./audit');
var statuslabel = require('./statuslabel');
var graph = require('./graph');
var reference = require('./reference');
var software = require('./software');
var sortTable = require('./sorttable');
var image = require('./image');
var doc = require('./doc');

var Breadcrumbs = navigation.Breadcrumbs;
var DbxrefList = dbxref.DbxrefList;
var FetchedItems = fetched.FetchedItems;
var StatusLabel = statuslabel.StatusLabel;
var PubReferenceList = reference.PubReferenceList;
var SoftwareVersionList = software.SoftwareVersionList;
var DocumentsPanel = doc.DocumentsPanel;
var AuditIndicators = audit.AuditIndicators;
var AuditDetail = audit.AuditDetail;
var AuditMixin = audit.AuditMixin;
var SortTablePanel = sortTable.SortTablePanel;
var SortTable = sortTable.SortTable;
var ProjectBadge = image.ProjectBadge;
var {Panel, PanelBody, PanelHeading} = panel;
var DropdownButton = button.DropdownButton;
var DropdownMenu = dropdownMenu.DropdownMenu;

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

// Return a summary of the given biosamples, ready to be displayed in a React component.
var annotationBiosampleSummary = module.exports.annotationBiosampleSummary = function(annotation) {
    var organismName = (annotation.organism && annotation.organism.scientific_name) ? <i>{annotation.organism.scientific_name}</i> : null;
    var lifeStageString = (annotation.relevant_life_stage && annotation.relevant_life_stage !== 'unknown') ? <span>{annotation.relevant_life_stage}</span> : null;
    var timepointString = annotation.relevant_timepoint ? <span>{annotation.relevant_timepoint + (annotation.relevant_timepoint_units ? ' ' +  annotation.relevant_timepoint_units : '')}</span> : null;

    // Build an array of strings we can join, not including empty strings
    var summaryStrings = _.compact([organismName, lifeStageString, timepointString]);

    if (summaryStrings.length) {
        return (
            <span className="biosample-summary">
                {summaryStrings.map(function(summaryString, i) {
                    return <span key={i}>{i > 0 ? <span>{', '}{summaryString}</span> : <span>{summaryString}</span>}</span>;
                })}
            </span>
        );
    }
    return null;
};


// Display Annotation page, a subtype of Dataset.
var Annotation = React.createClass({
    mixins: [AuditMixin],

    contextTypes: {
        session: React.PropTypes.object
    },

    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-item');
        var statuses = [{status: context.status, title: "Status"}];

        // Build up array of documents attached to this dataset
        var datasetDocuments = (context.documents && context.documents.length) ? context.documents : [];

        // Make a biosample summary string
        var biosampleSummary = annotationBiosampleSummary(context);

        // Set up the breadcrumbs
        var datasetType = context['@type'][1];
        var filesetType = context['@type'][0];
        var crumbs = [
            {id: 'Datasets'},
            {id: datasetType, uri: '/search/?type=' + datasetType, wholeTip: 'Search for ' + datasetType},
            {id: breakSetName(filesetType), uri: '/search/?type=' + filesetType, wholeTip: 'Search for ' + filesetType}
        ];

        // Make string of alternate accessions
        var altacc = context.alternate_accessions.join(', ');

        // Get a list of reference links, if any
        var references = PubReferenceList(context.references);

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs crumbs={crumbs} />
                        <h2>Summary for annotation file set {context.accession}</h2>
                        {altacc ? <h4 className="repl-acc">Replaces {altacc}</h4> : null}
                        <div className="status-line">
                            <div className="characterization-status-labels">
                                <StatusLabel status={statuses} />
                            </div>
                            <AuditIndicators audits={context.audit} id="dataset-audit" />
                        </div>
                    </div>
                </header>
                <AuditDetail context={context} id="dataset-audit" />
                <Panel addClasses="data-display">
                    <PanelBody addClasses="panel-body-with-header">
                        <div className="flexrow">
                            <div className="flexcol-sm-6">
                                <div className="flexcol-heading experiment-heading"><h4>Summary</h4></div>
                                <dl className="key-value">
                                    <div data-test="accession">
                                        <dt>Accession</dt>
                                        <dd>{context.accession}</dd>
                                    </div>

                                    {context.description ?
                                        <div data-test="description">
                                            <dt>Description</dt>
                                            <dd>{context.description}</dd>
                                        </div>
                                    : null}

                                    {context.biosample_term_name || biosampleSummary ?
                                        <div data-test="biosample">
                                            <dt>Biosample summary</dt>
                                            <dd>
                                                {context.biosample_term_name}
                                                {context.biosample_term_name ? <span>{' '}</span> : null}
                                                {biosampleSummary ? <span>({biosampleSummary})</span> : null}
                                            </dd>
                                        </div>
                                    : null}

                                    {context.biosample_type ?
                                        <div data-test="biosampletype">
                                            <dt>Biosample type</dt>
                                            <dd>{context.biosample_type}</dd>
                                        </div>
                                    : null}

                                    {context.organism ?
                                        <div data-test="organism">
                                            <dt>Organism</dt>
                                            <dd>{context.organism.name}</dd>
                                        </div>
                                    : null}

                                    {context.annotation_type ?
                                        <div data-test="type">
                                            <dt>Annotation type</dt>
                                            <dd className="sentence-case">{context.annotation_type}</dd>
                                        </div>
                                    : null}

                                    {context.target ?
                                        <div data-test="target">
                                            <dt>Target</dt>
                                            <dd><a href={context.target['@id']}>{context.target.label}</a></dd>
                                        </div>
                                    : null}

                                    {context.software_used && context.software_used.length ?
                                        <div data-test="softwareused">
                                            <dt>Software used</dt>
                                            <dd>{SoftwareVersionList(context.software_used)}</dd>
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
                                    {context.encyclopedia_version ?
                                        <div data-test="encyclopediaversion">
                                            <dt>Encyclopedia version</dt>
                                            <dd>{context.encyclopedia_version}</dd>
                                        </div>
                                    : null}

                                    {context.lab ?
                                        <div data-test="lab">
                                            <dt>Lab</dt>
                                            <dd>{context.lab.title}</dd>
                                        </div>
                                    : null}
                                    
                                    {context.aliases.length ?
                                        <div data-test="aliases">
                                            <dt>Aliases</dt>
                                            <dd><DbxrefList values={context.aliases} /></dd>
                                        </div>
                                    : null}

                                    <div data-test="externalresources">
                                        <dt>External resources</dt>
                                        <dd>
                                            {context.dbxrefs && context.dbxrefs.length ?
                                                <DbxrefList values={context.dbxrefs} />
                                            : <em>None submitted</em> }
                                        </dd>
                                    </div>

                                    {references ?
                                        <div data-test="references">
                                            <dt>Publications</dt>
                                            <dd>{references}</dd>
                                        </div>
                                    : null}
                                </dl>
                            </div>
                        </div>
                    </PanelBody>
                </Panel>

                {/* Display list of released and unreleased files */}
                <FetchedItems {...this.props} url={unreleased_files_url(context)} Component={DatasetFiles} filePanelHeader={<FilePanelHeader context={context} />} encodevers={globals.encodeVersion(context)} session={this.context.session} ignoreErrors />

                <DocumentsPanel documentSpecs={[{documents: datasetDocuments}]} />
            </div>
        );
    }
});

globals.content_views.register(Annotation, 'Annotation');


// Display Annotation page, a subtype of Dataset.
var PublicationData = React.createClass({
    mixins: [AuditMixin],

    contextTypes: {
        session: React.PropTypes.object
    },

    render: function() {
        var context = this.props.context;
        var files = context.files;
        var itemClass = globals.itemClass(context, 'view-item');
        var statuses = [{status: context.status, title: "Status"}];

        // Build up array of documents attached to this dataset
        var datasetDocuments = (context.documents && context.documents.length) ? context.documents : [];

        // Set up the breadcrumbs
        var datasetType = context['@type'][1];
        var filesetType = context['@type'][0];
        var crumbs = [
            {id: 'Datasets'},
            {id: datasetType, uri: '/search/?type=' + datasetType, wholeTip: 'Search for ' + datasetType},
            {id: breakSetName(filesetType), uri: '/search/?type=' + filesetType, wholeTip: 'Search for ' + filesetType}
        ];

        // Make string of alternate accessions
        var altacc = context.alternate_accessions.join(', ');

        // Render the publication links
        var referenceList = PubReferenceList(context.references);

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs crumbs={crumbs} />
                        <h2>Summary for publication file set {context.accession}</h2>
                        {altacc ? <h4 className="repl-acc">Replaces {altacc}</h4> : null}
                        <div className="status-line">
                            <div className="characterization-status-labels">
                                <StatusLabel status={statuses} />
                            </div>
                            <AuditIndicators audits={context.audit} id="dataset-audit" />
                        </div>
                    </div>
                </header>
                <AuditDetail context={context} id="dataset-audit" />
                <Panel addClasses="data-display">
                    <PanelBody addClasses="panel-body-with-header">
                        <div className="flexrow">
                            <div className="flexcol-sm-6">
                                <div className="flexcol-heading experiment-heading"><h4>Summary</h4></div>
                                <dl className="key-value">
                                    {context.assay_term_name && context.assay_term_name.length ?
                                        <div data-test="assaytermname">
                                            <dt>Assay(s)</dt>
                                            <dd>{context.assay_term_name.join(', ')}</dd>
                                        </div>
                                    : null}

                                    <div data-test="accession">
                                        <dt>Accession</dt>
                                        <dd>{context.accession}</dd>
                                    </div>

                                    {context.description ?
                                        <div data-test="description">
                                            <dt>Description</dt>
                                            <dd>{context.description}</dd>
                                        </div>
                                    : null}

                                    {context.biosample_term_name && context.biosample_term_name.length ?
                                        <div data-test="biosampletermname">
                                            <dt>Biosample term name</dt>
                                            <dd>{context.biosample_term_name.join(', ')}</dd>
                                        </div>
                                    : null}

                                    {context.biosample_type && context.biosample_type.length ?
                                        <div data-test="biosampletype">
                                            <dt>Biosample type</dt>
                                            <dd>{context.biosample_type.join(', ')}</dd>
                                        </div>
                                    : null}

                                    {context.dataset_type ?
                                        <div data-test="type">
                                            <dt>Dataset type</dt>
                                            <dd className="sentence-case">{context.dataset_type}</dd>
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
                                    {context.lab ?
                                        <div data-test="lab">
                                            <dt>Lab</dt>
                                            <dd>{context.lab.title}</dd>
                                        </div>
                                    : null}
                                    
                                    <div data-test="externalresources">
                                        <dt>External resources</dt>
                                        <dd>
                                            {context.dbxrefs && context.dbxrefs.length ?
                                                <DbxrefList values={context.dbxrefs} />
                                            : <em>None submitted</em> }
                                        </dd>
                                    </div>

                                    {referenceList ?
                                        <div data-test="references">
                                            <dt>Publications</dt>
                                            <dd>{referenceList}</dd>
                                        </div>
                                    : null}
                                </dl>
                            </div>
                        </div>
                    </PanelBody>
                </Panel>

                {/* Display list of released and unreleased files */}
                <FetchedItems {...this.props} url={unreleased_files_url(context)} Component={DatasetFiles} filePanelHeader={<FilePanelHeader context={context} />} encodevers={globals.encodeVersion(context)} session={this.context.session} ignoreErrors />

                <DocumentsPanel documentSpecs={[{documents: datasetDocuments}]} />
            </div>
        );
    }
});

globals.content_views.register(PublicationData, 'PublicationData');


// Display Annotation page, a subtype of Dataset.
var Reference = React.createClass({
    mixins: [AuditMixin],

    contextTypes: {
        session: React.PropTypes.object
    },

    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-item');
        var statuses = [{status: context.status, title: "Status"}];

        // Build up array of documents attached to this dataset
        var datasetDocuments = (context.documents && context.documents.length) ? context.documents : [];

        // Set up the breadcrumbs
        var datasetType = context['@type'][1];
        var filesetType = context['@type'][0];
        var crumbs = [
            {id: 'Datasets'},
            {id: datasetType, uri: '/search/?type=' + datasetType, wholeTip: 'Search for ' + datasetType},
            {id: breakSetName(filesetType), uri: '/search/?type=' + filesetType, wholeTip: 'Search for ' + filesetType}
        ];

        // Make string of alternate accessions
        var altacc = context.alternate_accessions.join(', ');

        // Get a list of reference links, if any
        var references = PubReferenceList(context.references);

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs crumbs={crumbs} />
                        <h2>Summary for reference file set {context.accession}</h2>
                        {altacc ? <h4 className="repl-acc">Replaces {altacc}</h4> : null}
                        <div className="status-line">
                            <div className="characterization-status-labels">
                                <StatusLabel status={statuses} />
                            </div>
                            <AuditIndicators audits={context.audit} id="dataset-audit" />
                        </div>
                    </div>
                </header>
                <AuditDetail context={context} id="dataset-audit" />
                <Panel addClasses="data-display">
                    <PanelBody addClasses="panel-body-with-header">
                        <div className="flexrow">
                            <div className="flexcol-sm-6">
                                <div className="flexcol-heading experiment-heading"><h4>Summary</h4></div>
                                <dl className="key-value">
                                    <div data-test="accession">
                                        <dt>Accession</dt>
                                        <dd>{context.accession}</dd>
                                    </div>

                                    {context.description ?
                                        <div data-test="description">
                                            <dt>Description</dt>
                                            <dd>{context.description}</dd>
                                        </div>
                                    : null}

                                    {context.reference_type ?
                                        <div data-test="type">
                                            <dt>Reference type</dt>
                                            <dd>{context.reference_type}</dd>
                                        </div>
                                    : null}

                                    {context.organism ?
                                        <div data-test="organism">
                                            <dt>Organism</dt>
                                            <dd>{context.organism.name}</dd>
                                        </div>
                                    : null}

                                    {context.software_used && context.software_used.length ?
                                        <div data-test="softwareused">
                                            <dt>Software used</dt>
                                            <dd>{SoftwareVersionList(context.software_used)}</dd>
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
                                    {context.lab ?
                                        <div data-test="lab">
                                            <dt>Lab</dt>
                                            <dd>{context.lab.title}</dd>
                                        </div>
                                    : null}
                                    
                                    {context.aliases.length ?
                                        <div data-test="aliases">
                                            <dt>Aliases</dt>
                                            <dd><DbxrefList values={context.aliases} /></dd>
                                        </div>
                                    : null}

                                    <div data-test="externalresources">
                                        <dt>External resources</dt>
                                        <dd>
                                            {context.dbxrefs && context.dbxrefs.length ?
                                                <DbxrefList values={context.dbxrefs} />
                                            : <em>None submitted</em> }
                                        </dd>
                                    </div>

                                    {references ?
                                        <div data-test="references">
                                            <dt>Publications</dt>
                                            <dd>{references}</dd>
                                        </div>
                                    : null}
                                </dl>
                            </div>
                        </div>
                    </PanelBody>
                </Panel>

                {/* Display list of released and unreleased files */}
                <FetchedItems {...this.props} url={unreleased_files_url(context)} Component={DatasetFiles} filePanelHeader={<FilePanelHeader context={context} />} encodevers={globals.encodeVersion(context)} session={this.context.session} ignoreErrors />

                <DocumentsPanel documentSpecs={[{documents: datasetDocuments}]} />
            </div>
        );
    }
});

globals.content_views.register(Reference, 'Reference');


// Display Annotation page, a subtype of Dataset.
var Project = React.createClass({
    mixins: [AuditMixin],

    contextTypes: {
        session: React.PropTypes.object
    },

    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-item');
        var statuses = [{status: context.status, title: "Status"}];

        // Build up array of documents attached to this dataset
        var datasetDocuments = (context.documents && context.documents.length) ? context.documents : [];

        // Collect organisms
        var organisms = context.organism && context.organism.map(function(organism) {
            return organism.name;
        });
        organisms = _.uniq(organisms);

        // Set up the breadcrumbs
        var datasetType = context['@type'][1];
        var filesetType = context['@type'][0];
        var crumbs = [
            {id: 'Datasets'},
            {id: datasetType, uri: '/search/?type=' + datasetType, wholeTip: 'Search for ' + datasetType},
            {id: breakSetName(filesetType), uri: '/search/?type=' + filesetType, wholeTip: 'Search for ' + filesetType}
        ];

        // Make string of alternate accessions
        var altacc = context.alternate_accessions.join(', ');

        // Get a list of reference links
        var references = PubReferenceList(context.references);

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs crumbs={crumbs} />
                        <h2>Summary for project file set {context.accession}</h2>
                        {altacc ? <h4 className="repl-acc">Replaces {altacc}</h4> : null}
                        <div className="status-line">
                            <div className="characterization-status-labels">
                                <StatusLabel status={statuses} />
                            </div>
                            <AuditIndicators audits={context.audit} id="dataset-audit" />
                        </div>
                    </div>
                </header>
                <AuditDetail context={context} id="dataset-audit" />
                <Panel addClasses="data-display">
                    <PanelBody addClasses="panel-body-with-header">
                        <div className="flexrow">
                            <div className="flexcol-sm-6">
                                <div className="flexcol-heading experiment-heading"><h4>Summary</h4></div>
                                <dl className="key-value">
                                    {context.assay_term_name && context.assay_term_name.length ?
                                        <div data-test="assaytermname">
                                            <dt>Assay(s)</dt>
                                            <dd>{context.assay_term_name.join(', ')}</dd>
                                        </div>
                                    : null}

                                    <div data-test="accession">
                                        <dt>Accession</dt>
                                        <dd>{context.accession}</dd>
                                    </div>

                                    {context.description ?
                                        <div data-test="description">
                                            <dt>Description</dt>
                                            <dd>{context.description}</dd>
                                        </div>
                                    : null}

                                    {context.project_type ?
                                        <div data-test="type">
                                            <dt>Project type</dt>
                                            <dd className="sentence-case">{context.project_type}</dd>
                                        </div>
                                    : null}

                                    {context.biosample_term_name && context.biosample_term_name.length ?
                                        <div data-test="biosampletermname">
                                            <dt>Biosample term name</dt>
                                            <dd>{context.biosample_term_name.join(', ')}</dd>
                                        </div>
                                    : null}

                                    {context.biosample_type && context.biosample_type.length ?
                                        <div data-test="biosampletype">
                                            <dt>Biosample type</dt>
                                            <dd>{context.biosample_type.join(', ')}</dd>
                                        </div>
                                    : null}

                                    {organisms.length ?
                                        <div data-test="organism">
                                            <dt>Organism</dt>
                                            <dd>{organisms.join(', ')}</dd>
                                        </div>
                                    : null}

                                    {context.software_used && context.software_used.length ?
                                        <div data-test="softwareused">
                                            <dt>Software used</dt>
                                            <dd>{SoftwareVersionList(context.software_used)}</dd>
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
                                    {context.lab ?
                                        <div data-test="lab">
                                            <dt>Lab</dt>
                                            <dd>{context.lab.title}</dd>
                                        </div>
                                    : null}
                                    
                                    {context.aliases.length ?
                                        <div data-test="aliases">
                                            <dt>Aliases</dt>
                                            <dd><DbxrefList values={context.aliases} /></dd>
                                        </div>
                                    : null}

                                    <div data-test="externalresources">
                                        <dt>External resources</dt>
                                        <dd>
                                            {context.dbxrefs && context.dbxrefs.length ?
                                                <DbxrefList values={context.dbxrefs} />
                                            : <em>None submitted</em> }
                                        </dd>
                                    </div>

                                    {references ?
                                        <div data-test="references">
                                            <dt>Publications</dt>
                                            <dd>{references}</dd>
                                        </div>
                                    : null}
                                </dl>
                            </div>
                        </div>
                    </PanelBody>
                </Panel>

                {/* Display list of released and unreleased files */}
                <FetchedItems {...this.props} url={unreleased_files_url(context)} Component={DatasetFiles} filePanelHeader={<FilePanelHeader context={context} />} encodevers={globals.encodeVersion(context)} session={this.context.session} ignoreErrors />

                <DocumentsPanel documentSpecs={[{documents: datasetDocuments}]} />
            </div>
        );
    }
});

globals.content_views.register(Project, 'Project');


// Display Annotation page, a subtype of Dataset.
var UcscBrowserComposite = React.createClass({
    mixins: [AuditMixin],

    contextTypes: {
        session: React.PropTypes.object
    },

    render: function() {
        var context = this.props.context;
        var files = context.files;
        var itemClass = globals.itemClass(context, 'view-item');
        var statuses = [{status: context.status, title: "Status"}];

        // Build up array of documents attached to this dataset
        var datasetDocuments = (context.documents && context.documents.length) ? context.documents : [];

        // Collect organisms
        var organisms = context.organism && context.organism.map(function(organism) {
            return organism.name;
        });
        organisms = _.uniq(organisms);

        // Set up the breadcrumbs
        var datasetType = context['@type'][1];
        var filesetType = context['@type'][0];
        var crumbs = [
            {id: 'Datasets'},
            {id: datasetType, uri: '/search/?type=' + datasetType, wholeTip: 'Search for ' + datasetType},
            {id: breakSetName(filesetType), uri: '/search/?type=' + filesetType, wholeTip: 'Search for ' + filesetType}
        ];

        // Make string of alternate accessions
        var altacc = context.alternate_accessions.join(', ');

        // Get a list of reference links, if any
        var references = PubReferenceList(context.references);

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs crumbs={crumbs} />
                        <h2>Summary for UCSC browser composite file set {context.accession}</h2>
                        {altacc ? <h4 className="repl-acc">Replaces {altacc}</h4> : null}
                        <div className="status-line">
                            <div className="characterization-status-labels">
                                <StatusLabel status={statuses} />
                            </div>
                            <AuditIndicators audits={context.audit} id="dataset-audit" />
                        </div>
                    </div>
                </header>
                <AuditDetail context={context} id="dataset-audit" />
                <Panel addClasses="data-display">
                    <PanelBody addClasses="panel-body-with-header">
                        <div className="flexrow">
                            <div className="flexcol-sm-6">
                                <div className="flexcol-heading experiment-heading"><h4>Summary</h4></div>
                                <dl className="key-value">
                                    {context.assay_term_name && context.assay_term_name.length ?
                                        <div data-test="assays">
                                            <dt>Assay(s)</dt>
                                            <dd>{context.assay_term_name.join(', ')}</dd>
                                        </div>
                                    : null}

                                    <div data-test="accession">
                                        <dt>Accession</dt>
                                        <dd>{context.accession}</dd>
                                    </div>

                                    {context.description ?
                                        <div data-test="description">
                                            <dt>Description</dt>
                                            <dd>{context.description}</dd>
                                        </div>
                                    : null}

                                    {context.dataset_type ?
                                        <div data-test="type">
                                            <dt>Dataset type</dt>
                                            <dd className="sentence-case">{context.dataset_type}</dd>
                                        </div>
                                    : null}

                                    {organisms.length ?
                                        <div data-test="organism">
                                            <dt>Organism</dt>
                                            <dd>{organisms.join(', ')}</dd>
                                        </div>
                                    : null}

                                    {context.software_used && context.software_used.length ?
                                        <div data-test="software-used">
                                            <dt>Software used</dt>
                                            <dd>{SoftwareVersionList(context.software_used)}</dd>
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
                                    {context.lab ?
                                        <div data-test="lab">
                                            <dt>Lab</dt>
                                            <dd>{context.lab.title}</dd>
                                        </div>
                                    : null}
                                    
                                    {context.aliases.length ?
                                        <div data-test="aliases">
                                            <dt>Aliases</dt>
                                            <dd><DbxrefList values={context.aliases} /></dd>
                                        </div>
                                    : null}

                                    <div data-test="externalresources">
                                        <dt>External resources</dt>
                                        <dd>
                                            {context.dbxrefs && context.dbxrefs.length ?
                                                <DbxrefList values={context.dbxrefs} />
                                            : <em>None submitted</em> }
                                        </dd>
                                    </div>

                                    {references ?
                                        <div data-test="references">
                                            <dt>Publications</dt>
                                            <dd>{references}</dd>
                                        </div>
                                    : null}
                                </dl>
                            </div>
                        </div>
                    </PanelBody>
                </Panel>

                {/* Display list of released and unreleased files */}
                <FetchedItems {...this.props} url={unreleased_files_url(context)} Component={DatasetFiles} filePanelHeader={<FilePanelHeader context={context} />} encodevers={globals.encodeVersion(context)} session={this.context.session} ignoreErrors />

                <DocumentsPanel documentSpecs={[{documents: datasetDocuments}]} />
            </div>
        );
    }
});

globals.content_views.register(UcscBrowserComposite, 'UcscBrowserComposite');


var FilePanelHeader = module.exports.FilePanelHeader = React.createClass({
    render: function() {
        var context = this.props.context;

        return (
            <div>
                {context.visualize_ucsc  && context.status == "released" ?
                    <span className="pull-right">
                        <DropdownButton title='Visualize Data' label="filepaneheader">
                            <DropdownMenu>
                                {Object.keys(context.visualize_ucsc).map(assembly =>
                                    <a key={assembly} data-bypass="true" target="_blank" href={context.visualize_ucsc[assembly]}>
                                        {assembly}
                                    </a>
                                )}
                            </DropdownMenu>
                        </DropdownButton>
                    </span>
                : null}
                <h4>File summary</h4>
            </div>
        );
    }
});


var getValuePossibleControls = function(item) {
    if (item.possible_controls && item.possible_controls.length) {
        return item.possible_controls.map(function(control) {
            return control.accession;
        }).join(', ');
    }
    return null;
};


var displayPossibleControls = function(item) {
    if (item.possible_controls && item.possible_controls.length) {
        return (
            <span>
                {item.possible_controls.map(function(control, i) {
                    return (
                        <span key={control.uuid}>
                            {i > 0 ? <span>, </span> : null}
                            <a href={control['@id']}>{control.accession}</a>
                        </span>
                    );
                })}
            </span>
        );
    }
    return null;
};

var basicTableColumns = {
    'accession': {
        title: 'Accession',
        display: function(experiment) {
            return <a href={experiment['@id']} title={'View page for experiment ' + experiment.accession}>{experiment.accession}</a>;
        }
    },
    'assay_term_name': {
        title: 'Assay'
    },
    'target': {
        title: 'Target',
        getValue: function(experiment) {
            return experiment.target ? experiment.target.label : null;
        }
    },
    'description': {
        title: 'Description'
    },
    'lab': {
        title: 'Lab',
        getValue: function(experiment) {
            return experiment.lab ? experiment.lab.title : null;
        }
    }
};

var treatmentSeriesTableColumns = {
    'accession': {
        title: 'Accession',
        display: function(experiment) {
            return <a href={experiment['@id']} title={'View page for experiment ' + experiment.accession}>{experiment.accession}</a>;
        }
    },
    'possible_controls': {
        title: 'Possible controls',
        display: displayPossibleControls,
        sorter: false
    },
    'assay_term_name': {
        title: 'Assay'
    },
    'target': {
        title: 'Target',
        getValue: function(experiment) {
            return experiment.target ? experiment.target.label : null;
        }
    },
    'description': {
        title: 'Description'
    },
    'lab': {
        title: 'Lab',
        getValue: function(experiment) {
            return experiment.lab ? experiment.lab.title : null;
        }
    }
};

var replicationTimingSeriesTableColumns = {
    'accession': {
        title: 'Accession',
        display: function(item) {
            return <a href={item['@id']} title={'View page for experiment ' + item.accession}>{item.accession}</a>;
        }
    },
    'possible_controls': {
        title: 'Possible controls',
        display: displayPossibleControls,
        sorter: false
    },
    'assay_term_name': {
        title: 'Assay'
    },
    'phase': {
        title: 'Biosample phase',
        display: function(experiment) {
            var phases = [];

            if (experiment.replicates && experiment.replicates.length) {
                var biosamples = experiment.replicates.map(function(replicate) {
                    return replicate.library && replicate.library.biosample;
                });
                phases = _.chain(biosamples.map(function(biosample) {
                    return biosample.phase;
                })).compact().uniq().value();
            }
            return phases.join(', ');
        },
        sorter: false
    },
    'target': {
        title: 'Target',
        getValue: function(experiment) {
            return experiment.target ? experiment.target.label : null;
        }
    },
    'description': {
        title: 'Description'
    },
    'lab': {
        title: 'Lab',
        getValue: function(experiment) {
            return experiment.lab ? experiment.lab.title : null;
        }
    }
};

var organismDevelopmentSeriesTableColumns = {
    'accession': {
        title: 'Accession',
        display: function(experiment) {
            return <a href={experiment['@id']} title={'View page for experiment ' + experiment.accession}>{experiment.accession}</a>;
        }
    },
    'possible_controls': {
        title: 'Possible controls',
        display: displayPossibleControls,
        sorter: false
    },
    'assay_term_name': {
        title: 'Assay'
    },
    'relative_age': {
        title: 'Relative age',
        display: function(experiment) {
            var biosamples, synchronizationBiosample, lifeStageBiosample, ages;
            if (experiment.replicates && experiment.replicates.length) {
                biosamples = experiment.replicates.map(function(replicate) {
                    return replicate.library && replicate.library.biosample;
                });
            }
            if (biosamples && biosamples.length) {
                synchronizationBiosample = _(biosamples).find(function(biosample) {
                    return biosample.synchronization;
                });
                lifeStageBiosample = _(biosamples).find(function(biosample) {
                    return biosample.life_stage;
                });
                if (!synchronizationBiosample) {
                    ages = _.chain(biosamples.map(function(biosample) {
                        return biosample.age_display;
                    })).compact().uniq().value();
                }
            }
            return (
                <span>
                    {synchronizationBiosample ?
                        <span>{synchronizationBiosample.synchronization + ' + ' + synchronizationBiosample.age_display}</span>
                    :
                        <span>{ages.length ? <span>{ages.join(', ')}</span> : null}</span>
                    }
                </span>
            );
        },
        sorter: false
    },
    'life_stage': {
        title: 'Life stage',
        getValue: function(experiment) {
            var biosamples, lifeStageBiosample;

            if (experiment.replicates && experiment.replicates.length) {
                biosamples = experiment.replicates.map(function(replicate) {
                    return replicate.library && replicate.library.biosample;
                });
            }
            if (biosamples && biosamples.length) {
                lifeStageBiosample = _(biosamples).find(function(biosample) {
                    return biosample.life_stage;
                });
            }
            return lifeStageBiosample.life_stage;
        }
    },
    'target': {
        title: 'Target',
        getValue: function(item) {
            return item.target ? item.target.label : null;
        }
    },
    'description': {
        title: 'Description'
    },
    'lab': {
        title: 'Lab',
        getValue: function(item) {
            return item.lab ? item.lab.title : null;
        }
    }
};

var Series = module.exports.Series = React.createClass({
    mixins: [AuditMixin],

    contextTypes: {
        session: React.PropTypes.object
    },

    // Map series @id to title and table columns
    seriesComponents: {
        'MatchedSet': {title: 'matched set series', table: basicTableColumns},
        'OrganismDevelopmentSeries': {title: 'organism development series', table: organismDevelopmentSeriesTableColumns},
        'ReferenceEpigenome': {title: 'reference epigenome series', table: basicTableColumns},
        'ReplicationTimingSeries': {title: 'replication timing series', table: replicationTimingSeriesTableColumns},
        'TreatmentConcentrationSeries': {title: 'treatment concentration series', table: treatmentSeriesTableColumns},
        'TreatmentTimeSeries': {title: 'treatment time series', table: treatmentSeriesTableColumns}
    },

    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-item');
        var experiments = {};
        var statuses = [{status: context.status, title: "Status"}];
        context.files.forEach(function(file) {
            var experiment = file.replicate && file.replicate.experiment;
            if (experiment) {
                experiments[experiment['@id']] = experiment;
            }
        });
        experiments = _.values(experiments);

        // Build up array of documents attached to this dataset
        var datasetDocuments = (context.documents && context.documents.length) ? context.documents : [];

        // Set up the breadcrumbs
        var datasetType = context['@type'][1];
        var seriesType = context['@type'][0];
        var crumbs = [
            {id: 'Datasets'},
            {id: datasetType, uri: '/search/?type=' + datasetType, wholeTip: 'Search for ' + datasetType},
            {id: breakSetName(seriesType), uri: '/search/?type=' + seriesType, wholeTip: 'Search for ' + seriesType}
        ];

        // Make string of alternate accessions
        var altacc = context.alternate_accessions.join(', ');

        // Get a list of reference links, if any
        var references = PubReferenceList(context.references);

        // Make the series title
        var seriesComponent = this.seriesComponents[context['@type'][0]];
        var seriesTitle = seriesComponent ? seriesComponent.title : 'series';

        // Calculate the biosample summary
        var speciesRender = null;
        if (context.organism && context.organism.length) {
            var speciesList = _.uniq(context.organism.map(organism => {
                return organism.scientific_name;
            }));
            speciesRender = (
                <span>
                    {speciesList.map((species, i) => {
                        return (
                            <span key={i}>
                                {i > 0 ? <span> and </span> : null}
                                <i>{species}</i>
                            </span>
                        );
                    })}
                </span>
            );
        }
        var terms = (context.biosample_term_name && context.biosample_term_name.length) ? _.uniq(context.biosample_term_name) : [];

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs crumbs={crumbs} />
                        <h2>Summary for {seriesTitle} {context.accession}</h2>
                        {altacc ? <h4 className="repl-acc">Replaces {altacc}</h4> : null}
                        <div className="status-line">
                            <div className="characterization-status-labels">
                                <StatusLabel status={statuses} />
                            </div>
                            <AuditIndicators audits={context.audit} id="dataset-audit" />
                        </div>
                    </div>
                </header>
                <AuditDetail context={context} id="dataset-audit" />
                <Panel addClasses="data-display">
                    <PanelBody addClasses="panel-body-with-header">
                        <div className="flexrow">
                            <div className="flexcol-sm-6">
                                <div className="flexcol-heading experiment-heading"><h4>Summary</h4></div>
                                <dl className="key-value">
                                    {context.description ?
                                        <div data-test="description">
                                            <dt>Description</dt>
                                            <dd>{context.description}</dd>
                                        </div>
                                    : null}

                                    {context.assay_term_name && context.assay_term_name.length ?
                                        <div data-test="description">
                                            <dt>Assay</dt>
                                            <dd>{context.assay_term_name.join(', ')}</dd>
                                        </div>
                                    : null}

                                    {terms.length || speciesRender ?
                                        <div data-test="biosamplesummary">
                                            <dt>Biosample summary</dt>
                                            <dd>
                                                {terms.length ? <span>{terms.join(' and ')} </span> : null}
                                                {speciesRender ? <span>({speciesRender})</span> : null}
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

                                    <div data-test="project">
                                        <dt>Project</dt>
                                        <dd>{context.award.project}</dd>
                                    </div>

                                    {context.aliases.length ?
                                        <div data-test="aliases">
                                            <dt>Aliases</dt>
                                            <dd>{context.aliases.join(", ")}</dd>
                                        </div>
                                    : null}

                                    <div data-test="externalresources">
                                        <dt>External resources</dt>
                                        <dd>
                                            {context.dbxrefs && context.dbxrefs.length ?
                                                <DbxrefList values={context.dbxrefs} />
                                            : <em>None submitted</em> }
                                        </dd>
                                    </div>

                                    {references ?
                                        <div data-test="references">
                                            <dt>References</dt>
                                            <dd>{references}</dd>
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
                        </div>
                    </PanelBody>
                </Panel>

                {context.related_datasets.length ?
                    <div>
                        <SortTablePanel title={'Experiments in ' + seriesTitle + ' ' + context.accession}>
                            <SortTable list={context.related_datasets} columns={seriesComponent.table} />
                        </SortTablePanel>
                    </div>
                : null }

                {/* Display list of released and unreleased files */}
                <FetchedItems {...this.props} url={unreleased_files_url(context)} Component={DatasetFiles} filePanelHeader={<FilePanelHeader context={context} />} encodevers={globals.encodeVersion(context)} session={this.context.session} ignoreErrors />

                <DocumentsPanel documentSpecs={[{documents: datasetDocuments}]} />
            </div>
        );
    }
});

globals.content_views.register(Series, 'Series');


var unreleased_files_url = module.exports.unreleased_files_url = function (context) {
    var file_states = [
        '',
        "uploading",
        "uploaded",
        "upload failed",
        "format check failed",
        "in progress"
    ].map(encodeURIComponent).join('&status=');
    return '/search/?limit=all&frame=embedded&type=file&dataset=' + context['@id'] + file_states;
};


// Called once searches for unreleased files returns results in this.props.items. Displays both released and
// unreleased files.
var DatasetFiles = module.exports.DatasetFiles = React.createClass({
    render: function () {
        if (this.props.items) {
            return <FileTable {...this.props} items={this.props.items} />;
        } else {
            return null;
        }
    }
});


// Display a count of experiments in the footer, with a link to the corresponding search if needed
var ExperimentTableFooter = React.createClass({
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


var ExperimentTable = module.exports.ExperimentTable = React.createClass({
    tableColumns: {
        'accession': {
            title: 'Accession',
            display: function(item) {
                return <a href={item['@id']} title={'View page for experiment ' + item.accession}>{item.accession}</a>;
            }
        },
        'assay_term_name': {
            title: 'Assay'
        },
        'biosample_term_name': {
            title: 'Biosample term name'
        },
        'target': {
            title: 'Target',
            getValue: function(item) {
                return item.target && item.target.label;
            }
        },
        'description': {
            title: 'Description'
        },
        'title': {
            title: 'Lab',
            getValue: function(item) {
                return item.lab && item.lab.title ? item.lab.title : null;
            }
        }
    },

    render: function() {
        var experiments;

        // If there's a limit on entries to display and the array is greater than that
        // limit, then clone the array with just that specified number of elements
        if (this.props.limit && (this.props.limit < this.props.items.length)) {
            // Limit the experiment list by cloning first {limit} elements
            experiments = this.props.items.slice(0, this.props.limit);
        } else {
            // No limiting; just reference the original array
            experiments = this.props.items;
        }

        return (
            <div>
                <SortTablePanel title={this.props.title}>
                    <SortTable list={experiments} columns={this.tableColumns} footer={<ExperimentTableFooter items={experiments} total={this.props.total} url={this.props.url} />} />
                </SortTablePanel>
            </div>
        );
    }
});


function humanFileSize(size) {
    if (size === undefined) return undefined;
    var i = Math.floor( Math.log(size) / Math.log(1024) );
    return ( size / Math.pow(1024, i) ).toPrecision(3) * 1 + ' ' + ['B', 'kB', 'MB', 'GB', 'TB'][i];
}


var FileTable = module.exports.FileTable = React.createClass({
    propTypes: {
        context: React.PropTypes.object, // Optional parent object of file list
        items: React.PropTypes.array.isRequired, // Array of files to appear in the table
        originating: React.PropTypes.bool, // TRUE to display originating dataset column
        session: React.PropTypes.object // Persona user session
    },

    getInitialState: function() {
        return {
            maxWidth: 'auto' // Width of widest table
        };
    },

    cv: {
        maxWidthRef: '', // ref key of table with this.state.maxWidth width
        maxWidthNode: null // DOM node of table with this.state.maxWidth width 
    },

    // Configuration for raw file table
    rawTableColumns: {
        'accession': {
            title: 'Accession',
            display: item =>
                <span>
                    {item.title}&nbsp;<a href={item.href} download={item.href.substr(item.href.lastIndexOf("/") + 1)} data-bypass="true"><i className="icon icon-download"><span className="sr-only">Download</span></i></a>
                </span>
        },
        'file_type': {title: 'File type'},
        'biological_replicates': {
            title: (list, columns, meta) => <span>{meta.anisogenic ? 'Anisogenic' : 'Biological'} replicate</span>,
            getValue: item => item.biological_replicates ? item.biological_replicates.sort(function(a,b){ return a - b; }).join(', ') : ''
        },
        'library': {
            title: 'Library',
            getValue: item => (item.replicate && item.replicate.library) ? item.replicate.library.accession : null
        },
        'run_type': {
            title: 'Run type',
            display: item => {
                var runType;

                if (item.run_type === 'single-ended') {
                    runType = 'SE';
                } else if (item.run_type === 'paired-ended') {
                    runType = 'PE';
                }

                return (
                    <span>
                        <span>{runType ? runType : null}</span>
                        <span>{item.read_length ? <span>{runType ? <span> </span> : null}{item.read_length + item.read_length_units}</span> : null}</span>
                    </span>
                );
            },
            objSorter: (a, b) => {
                // Sort by their combined string values
                var aStr = (a.run_type ? a.run_type : '') + (a.read_length ? a.read_length : '');
                var bStr = (b.run_type ? b.run_type : '') + (b.read_length ? b.read_length : '');
                return (aStr < bStr) ? -1 : (bStr < aStr ? 1 : 0);
            }
        },
        'paired_end': {
            title: 'Read',
            display: item => <span>{item.paired_end ? <span>R{item.paired_end}</span> : null}</span>
        },
        'title': {
            title: 'Lab',
            getValue: item => item.lab && item.lab.title ? item.lab.title : null
        },
        'date_created': {
            title: 'Date added',
            getValue: item => moment.utc(item.date_created).format('YYYY-MM-DD'),
            objSorter: (a, b) => {
                if (a.date_created && b.date_created) {
                    return Date.parse(a.date_created) - Date.parse(b.date_created);
                }
                return a.date_created ? -1 : (b.date_created ? 1 : 0);
            }
        },
        'file_size': {
            title: 'File size',
            display: item => <span>{humanFileSize(item.file_size)}</span>
        },
        'validation_status': {
            title: 'Validation status',
            display: item => <div className="characterization-meta-data"><StatusLabel status="pending" /></div>,
            hide: (list, columns, meta) => meta.encodevers !== '3',
            sorter: false
        },
        'status': {
            title: 'File status',
            display: item => <div className="characterization-meta-data"><StatusLabel status={item.status} /></div>,
            hide: (list, columns, meta) => !(meta.session && meta.session['auth.userid'])
        }
    },

    // Configuration for raw file table
    rawArrayTableColumns: {
        'accession': {
            title: 'Accession',
            display: item =>
                <span>
                    {item.title}&nbsp;<a href={item.href} download={item.href.substr(item.href.lastIndexOf("/") + 1)} data-bypass="true"><i className="icon icon-download"><span className="sr-only">Download</span></i></a>
                </span>
        },
        'file_type': {title: 'File type'},
        'biological_replicates': {
            title: (list, columns, meta) => <span>{meta.anisogenic ? 'Anisogenic' : 'Biological'} replicate</span>,
            getValue: item => item.biological_replicates ? item.biological_replicates.sort(function(a,b){ return a - b; }).join(', ') : ''
        },
        'library': {
            title: 'Library',
            getValue: item => (item.replicate && item.replicate.library) ? item.replicate.library.accession : null
        },
        'assembly': {title: 'Mapping assembly'},
        'title': {
            title: 'Lab',
            getValue: item => item.lab && item.lab.title ? item.lab.title : null
        },
        'date_created': {
            title: 'Date added',
            getValue: item => moment.utc(item.date_created).format('YYYY-MM-DD'),
            objSorter: (a, b) => {
                if (a.date_created && b.date_created) {
                    return Date.parse(a.date_created) - Date.parse(b.date_created);
                }
                return a.date_created ? -1 : (b.date_created ? 1 : 0);
            }
        },
        'file_size': {
            title: 'File size',
            display: item => <span>{humanFileSize(item.file_size)}</span>
        },
        'validation_status': {
            title: 'Validation status',
            display: item => <div className="characterization-meta-data"><StatusLabel status="pending" /></div>,
            hide: (list, columns, meta) => meta.encodevers !== '3',
            sorter: false
        },
        'status': {
            title: 'File status',
            display: item => <div className="characterization-meta-data"><StatusLabel status={item.status} /></div>,
            hide: (list, columns, meta) => !(meta.session && meta.session['auth.userid'])
        }
    },

    // Configuration for process file table
    procTableColumns: {
        'accession': {
            title: 'Accession',
            display: item =>
                <span>
                    {item.title}&nbsp;<a href={item.href} download={item.href.substr(item.href.lastIndexOf("/") + 1)} data-bypass="true"><i className="icon icon-download"><span className="sr-only">Download</span></i></a>
                </span>
        },
        'file_type': {title: 'File type'},
        'output_type': {title: 'Output type'},
        'biological_replicates': {
            title: (list, columns, meta) => <span>{meta.anisogenic ? 'Anisogenic' : 'Biological'} replicate</span>,
            getValue: item => item.biological_replicates ? item.biological_replicates.sort(function(a,b){ return a - b; }).join(', ') : ''
        },
        'assembly': {title: 'Mapping assembly'},
        'genome_annotation': {
            title: 'Genome annotation',
            hide: (list, columns, meta) => _(list).all(item => !item.genome_annotation)
        },
        'title': {
            title: 'Lab',
            getValue: item => item.lab && item.lab.title ? item.lab.title : null
        },
        'date_created': {
            title: 'Date added',
            getValue: item => moment.utc(item.date_created).format('YYYY-MM-DD'),
            sorter: (a, b) => {
                if (a.date_created && b.date_created) {
                    return Date.parse(a.date_created) - Date.parse(b.date_created);
                }
                return a.date_created ? -1 : (b.date_created ? 1 : 0);
            }
        },
        'file_size': {
            title: 'File size',
            display: item => <span>{humanFileSize(item.file_size)}</span>
        },
        'validation_status': {
            title: 'Validation status',
            display: item => <div className="characterization-meta-data"><StatusLabel status="pending" /></div>,
            hide: (list, columns, meta) => meta.encodevers !== '3',
            sorter: false
        },
        'status': {
            title: 'File status',
            display: item => <div className="characterization-meta-data"><StatusLabel status={item.status} /></div>,
            hide: (list, columns, meta) => !(meta.session && meta.session['auth.userid'])
        }
    },

    // Configuration for reference file table
    refTableColumns: {
        'accession': {
            title: 'Accession',
            display: item =>
                <span>
                    {item.title}&nbsp;<a href={item.href} download={item.href.substr(item.href.lastIndexOf("/") + 1)} data-bypass="true"><i className="icon icon-download"><span className="sr-only">Download</span></i></a>
                </span>
        },
        'file_type': {title: 'File type'},
        'output_type': {title: 'Output type'},
        'assembly': {title: 'Mapping assembly'},
        'genome_annotation': {
            title: 'Genome annotation',
            hide: (list, columns, meta) => _(list).all(item => !item.genome_annotation)
        },
        'title': {
            title: 'Lab',
            getValue: item => item.lab && item.lab.title ? item.lab.title : null
        },
        'date_created': {
            title: 'Date added',
            getValue: item => moment.utc(item.date_created).format('YYYY-MM-DD'),
            sorter: (a, b) => {
                if (a.date_created && b.date_created) {
                    return Date.parse(a.date_created) - Date.parse(b.date_created);
                }
                return a.date_created ? -1 : (b.date_created ? 1 : 0);
            }
        },
        'file_size': {
            title: 'File size',
            display: item => <span>{humanFileSize(item.file_size)}</span>
        },
        'status': {
            title: 'File status',
            display: item => <div className="characterization-meta-data"><StatusLabel status={item.status} /></div>,
            hide: (list, columns, meta) => !(meta.session && meta.session['auth.userid'])
        }
    },

    render: function() {
        var {context, items, filePanelHeader, encodevers, anisogenic, session} = this.props;
        var datasetFiles = context.files && context.files.concat((items && items.length) ? items : []);
        if (datasetFiles.length) {
            // Extract four kinds of file arrays
            datasetFiles = _(datasetFiles).uniq(file => file['@id']);
            var files = _(datasetFiles).groupBy(file => {
                if (file.output_category === 'raw data') {
                    return file.output_type === 'reads' ? 'raw' : 'rawArray';
                } else if (file.output_category === 'reference') {
                    return 'ref';
                } else {
                    return 'proc';
                }
            });

            return (
                <SortTablePanel header={filePanelHeader}>
                    <SortTable title="Raw data files" list={files.raw} columns={this.rawTableColumns} meta={{encodevers: encodevers, anisogenic: anisogenic, session: session}} sortColumn="biological_replicates" />
                    <SortTable title="Raw data files" list={files.rawArray} columns={this.rawArrayTableColumns} meta={{encodevers: encodevers, anisogenic: anisogenic, session: session}} sortColumn="biological_replicates" />
                    <SortTable title="Processed data files" list={files.proc} columns={this.procTableColumns} meta={{encodevers: encodevers, anisogenic: anisogenic, session: session}} sortColumn="biological_replicates" />
                    <SortTable title="Reference data files" list={files.ref} columns={this.refTableColumns} meta={{encodevers: encodevers, anisogenic: anisogenic, session: session}} />
                </SortTablePanel>
            );
        }
        return null;
    }
});


// Break the given camel-cased name into space-separated words just before the interior capital letters.
function breakSetName(name) {
    return name.replace(/(\S)([A-Z])/g, '$1 $2');
}
