'use strict';
var React = require('react/addons');
var panel = require('../libs/bootstrap/panel');
var _ = require('underscore');
var moment = require('moment');
var globals = require('./globals');
var navbar = require('./navbar');
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

var Breadcrumbs = navbar.Breadcrumbs;
var DbxrefList = dbxref.DbxrefList;
var Dbxref = dbxref.Dbxref;
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

                {context.visualize_ucsc  && context.status == "released" ?
                    <span className="pull-right">
                        <a data-bypass="true" target="_blank" private-browsing="true" className="btn btn-info btn-sm" href={context['visualize_ucsc']}>Visualize Data</a>
                    </span>
                : null }

                {context.files.length ?
                    <div>
                        <h3>Files in annotation file set {context.accession}</h3>
                        <FileTable context={context} items={context.files} originating />
                    </div>
                : null }

                {{'released': 1, 'release ready': 1}[context.status] ?
                    <FetchedItems {...this.props} url={unreleased_files_url(context)} Component={UnreleasedFiles} />
                : null}

                <DocumentsPanel documentSpecs={[{documents: datasetDocuments}]} />
            </div>
        );
    }
});

globals.content_views.register(Annotation, 'Annotation');


// Display Annotation page, a subtype of Dataset.
var PublicationData = React.createClass({
    mixins: [AuditMixin],
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

                {context.visualize_ucsc  && context.status == "released" ?
                    <span className="pull-right">
                        <a data-bypass="true" target="_blank" private-browsing="true" className="btn btn-info btn-sm" href={context['visualize_ucsc']}>Visualize Data</a>
                    </span>
                : null }

                {context.files.length ?
                    <div>
                        <h3>Files for publication file set {context.accession}</h3>
                        <FileTable context={context} items={context.files} originating />
                    </div>
                : null }

                {{'released': 1, 'release ready': 1}[context.status] ?
                    <FetchedItems {...this.props} url={unreleased_files_url(context)} Component={UnreleasedFiles} />
                : null}

                <DocumentsPanel documentSpecs={[{documents: datasetDocuments}]} />
            </div>
        );
    }
});

globals.content_views.register(PublicationData, 'PublicationData');


// Display Annotation page, a subtype of Dataset.
var Reference = React.createClass({
    mixins: [AuditMixin],
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

                {context.files.length ?
                    <div>
                        <h3>Files in reference file set {context.accession}</h3>
                        <FileTable context={context} items={context.files} originating />
                    </div>
                : null }

                {{'released': 1, 'release ready': 1}[context.status] ?
                    <FetchedItems {...this.props} url={unreleased_files_url(context)} Component={UnreleasedFiles} />
                : null}

                <DocumentsPanel documentSpecs={[{documents: datasetDocuments}]} />
            </div>
        );
    }
});

globals.content_views.register(Reference, 'Reference');


// Display Annotation page, a subtype of Dataset.
var Project = React.createClass({
    mixins: [AuditMixin],
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

                {context.visualize_ucsc  && context.status == "released" ?
                    <span className="pull-right">
                        <a data-bypass="true" target="_blank" private-browsing="true" className="btn btn-info btn-sm" href={context['visualize_ucsc']}>Visualize Data</a>
                    </span>
                : null }

                {context.files.length ?
                    <div>
                        <h3>Files in project file set {context.accession}</h3>
                        <FileTable context={context} items={context.files} originating />
                    </div>
                : null }

                {{'released': 1, 'release ready': 1}[context.status] ?
                    <FetchedItems {...this.props} url={unreleased_files_url(context)} Component={UnreleasedFiles} />
                : null}

                <DocumentsPanel documentSpecs={[{documents: datasetDocuments}]} />
            </div>
        );
    }
});

globals.content_views.register(Project, 'Project');


// Display Annotation page, a subtype of Dataset.
var UcscBrowserComposite = React.createClass({
    mixins: [AuditMixin],
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

                {context.visualize_ucsc  && context.status == "released" ?
                    <span className="pull-right">
                        <a data-bypass="true" target="_blank" private-browsing="true" className="btn btn-info btn-sm" href={context['visualize_ucsc']}>Visualize Data</a>
                    </span>
                : null }

                {context.files.length ?
                    <div>
                        <h3>Files in UCSC browser composite file set {context.accession}</h3>
                        <FileTable context={context} items={context.files} originating />
                    </div>
                : null }

                {{'released': 1, 'release ready': 1}[context.status] ?
                    <FetchedItems {...this.props} url={unreleased_files_url(context)} Component={UnreleasedFiles} />
                : null}

                <DocumentsPanel documentSpecs={[{documents: datasetDocuments}]} />
            </div>
        );
    }
});

globals.content_views.register(UcscBrowserComposite, 'UcscBrowserComposite');


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
                            <span>
                                {i > 0 ? <span> and </span> : null}
                                <i key={i}>{species}</i>
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
                                </dl>
                            </div>
                        </div>
                    </PanelBody>
                </Panel>

                {context.related_datasets.length ?
                    <div>
                        <h3>{'Experiments in ' + seriesTitle + ' ' + context.accession}</h3>
                        <SortTablePanel>
                            <SortTable list={context.related_datasets} columns={seriesComponent.table} />
                        </SortTablePanel>
                    </div>
                : null }

                {context.visualize_ucsc  && context.status == "released" ?
                    <span className="pull-right">
                        <a data-bypass="true" target="_blank" private-browsing="true" className="btn btn-info btn-sm" href={context['visualize_ucsc']}>Visualize Data</a>
                    </span>
                : null }

                {context.files && context.files.length ?
                    <div>
                        <h3>Original files in {seriesTitle} {context.accession}</h3>
                        <FileTable items={context.files} />
                    </div>
                : null }

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

var UnreleasedFiles = module.exports.UnreleasedFiles = React.createClass({
    render: function () {
        var context = this.props.context;
        return (
            <div>
                <h3>Unreleased files linked to {context.accession}</h3>
                <FileTable {...this.props} />
            </div>
        );
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
                {this.props.title ? <h3>{this.props.title}</h3> : null}
                <SortTablePanel>
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
        originating: React.PropTypes.bool // TRUE to display originating dataset column
    },

    // Configuration for raw file table
    rawTableColumns: {
        'accession': {
            title: 'Accession',
            display: item =>
                <span>
                    {item.title}&nbsp;<a href={item.href} download={item.href.substr(item.href.lastIndexOf("/") + 1)} data-bypass="true">
                        <i className="icon icon-download">
                            <span className="sr-only">Download</span>
                        </i>
                    </a>
                </span>
        },
        'file_type': {title: 'File type'},
        'file_size': {
            title: 'File size',
            display: item => <span>{humanFileSize(item.file_size)}</span>
        },
        'biological_replicates': {
            title: (list, columns, meta) => <span>{meta.anisogenic ? 'Anisogenic' : 'Biological'} replicate</span>,
            getValue: item => item.biological_replicates ? item.biological_replicates.sort(function(a,b){ return a - b; }).join(', ') : ''
        },
        'technical_replicate_number': {
            title: 'Technical replicate',
            getValue: item => item.replicate ? item.replicate.technical_replicate_number : null
        },
        'read_length': {
            title: 'Read length',
            display: item => <span>{item.read_length ? <span>{item.read_length + ' ' + item.read_length_units}</span> : null}</span>
        },
        'run_type': {title: 'Run type'},
        'paired_end': {title: 'Paired end'},
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
        'status': {
            title: 'Validation status',
            display: item => <div className="characterization-meta-data"><StatusLabel status="pending" /></div>,
            hide: (list, columns, meta) => meta.encodevers !== '3',
            sorter: false
        }
    },

    // Configuration for process file table
    procTableColumns: {
        'accession': {
            title: 'Accession',
            display: item =>
                <span>
                    {item.title}&nbsp;<a href={item.href} download={item.href.substr(item.href.lastIndexOf("/") + 1)} data-bypass="true">
                        <i className="icon icon-download">
                            <span className="sr-only">Download</span>
                        </i>
                    </a>
                </span>
        },
        'file_type': {title: 'File type'},
        'file_size': {
            title: 'File size',
            display: item => <span>{humanFileSize(item.file_size)}</span>
        },
        'output_type': {title: 'Output type'},
        'biological_replicates': {
            title: (list, columns, meta) => <span>{meta.anisogenic ? 'Anisogenic' : 'Biological'} replicate</span>,
            getValue: item => item.biological_replicates ? item.biological_replicates.sort(function(a,b){ return a - b; }).join(', ') : ''
        },
        'technical_replicate_number': {
            title: 'Technical replicate',
            getValue: item => item.replicate ? item.replicate.technical_replicate_number : null
        },
        'assembly': {title: 'Mapping assembly'},
        'genome_annotation': {title: 'Genome annotation'},
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
        'status': {
            title: 'Validation status',
            display: item => <div className="characterization-meta-data"><StatusLabel status="pending" /></div>,
            hide: (list, columns, meta) => meta.encodevers !== '3',
            sorter: false
        }
    },

    // Configuration for reference file table
    refTableColumns: {
        'accession': {
            title: 'Accession',
            display: item =>
                <span>
                    {item.title}&nbsp;<a href={item.href} download={item.href.substr(item.href.lastIndexOf("/") + 1)} data-bypass="true">
                        <i className="icon icon-download">
                            <span className="sr-only">Download</span>
                        </i>
                    </a>
                </span>
        },
        'file_type': {title: 'File type'},
        'file_size': {
            title: 'File size',
            display: item => <span>{humanFileSize(item.file_size)}</span>
        },
        'output_type': {title: 'Output type'},
        'assembly': {title: 'Mapping assembly'},
        'genome_annotation': {title: 'Genome annotation'},
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
        }
    },

    render: function() {
        // Extract three kinds of file arrays
        var files = _(this.props.items).groupBy(file => {
            if (file.output_category === 'raw data') {
                return 'raw';
            } else if (file.output_category === 'reference') {
                return 'ref';
            } else {
                return 'proc';
            }
        });

        return (
            <SortTablePanel>
                <SortTable title="Raw data" list={files.raw} columns={this.rawTableColumns} meta={{encodevers: this.props.encodevers, anisogenic: this.props.anisogenic}} />
                <SortTable title="Processed data" list={files.proc} columns={this.procTableColumns} meta={{encodevers: this.props.encodevers, anisogenic: this.props.anisogenic}} />
                <SortTable title="Reference data" list={files.ref} columns={this.refTableColumns} meta={{encodevers: this.props.encodevers, anisogenic: this.props.anisogenic}} />
            </SortTablePanel>
        );
    }
});


// Break the given camel-cased name into space-separated words just before the interior capital letters.
function breakSetName(name) {
    return name.replace(/(\S)([A-Z])/g, '$1 $2');
}
