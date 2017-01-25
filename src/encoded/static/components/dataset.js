import React from 'react/addons';
import _ from 'underscore';
import { Panel, PanelBody } from '../libs/bootstrap/panel';
import { DropdownButton } from '../libs/bootstrap/button';
import { DropdownMenu } from '../libs/bootstrap/dropdown-menu';
import globals from './globals';
import { Breadcrumbs } from './navigation';
import { DbxrefList } from './dbxref';
import { FetchedItems } from './fetched';
import { AuditIndicators, AuditDetail, AuditMixin } from './audit';
import { StatusLabel } from './statuslabel';
import { pubReferenceList } from './reference';
import { donorDiversity } from './objectutils';
import { softwareVersionList } from './software';
import { SortTablePanel, SortTable } from './sorttable';
import { ProjectBadge } from './image';
import { DocumentsPanel } from './doc';
import { FileGallery, DatasetFiles } from './filegallery';
import { AwardRef } from './typeutils';

// Return a summary of the given biosamples, ready to be displayed in a React component.
export function annotationBiosampleSummary(annotation) {
    const organismName = (annotation.organism && annotation.organism.scientific_name) ? <i>{annotation.organism.scientific_name}</i> : null;
    const lifeStageString = (annotation.relevant_life_stage && annotation.relevant_life_stage !== 'unknown') ? <span>{annotation.relevant_life_stage}</span> : null;
    const timepointString = annotation.relevant_timepoint ? <span>{annotation.relevant_timepoint + (annotation.relevant_timepoint_units ? ` ${annotation.relevant_timepoint_units}` : '')}</span> : null;

    // Build an array of strings we can join, not including empty strings
    const summaryStrings = _.compact([organismName, lifeStageString, timepointString]);

    if (summaryStrings.length) {
        return (
            <span className="biosample-summary">
                {summaryStrings.map((summaryString, i) =>
                    <span key={i}>
                        {i > 0 ? <span>{', '}{summaryString}</span> : <span>{summaryString}</span>}
                    </span>,
                )}
            </span>
        );
    }
    return null;
}


// Break the given camel-cased name into space-separated words just before the interior capital letters.
function breakSetName(name) {
    return name.replace(/(\S)([A-Z])/g, '$1 $2');
}


// Display Annotation page, a subtype of Dataset.
const Annotation = React.createClass({
    propTypes: {
        context: React.PropTypes.object, // Annotation being displayed
    },

    contextTypes: {
        session: React.PropTypes.object, // Login session information
    },

    mixins: [AuditMixin],

    render: function () {
        const context = this.props.context;
        const itemClass = globals.itemClass(context, 'view-item');
        const loggedIn = this.context.session && this.context.session['auth.userid'];
        const statuses = [{ status: context.status, title: 'Status' }];

        // Build up array of documents attached to this dataset
        const datasetDocuments = (context.documents && context.documents.length) ? context.documents : [];

        // Make a biosample summary string
        const biosampleSummary = annotationBiosampleSummary(context);

        // Determine this experiment's ENCODE version
        const encodevers = globals.encodeVersion(context);

        // Set up the breadcrumbs
        const datasetType = context['@type'][1];
        const filesetType = context['@type'][0];
        const crumbs = [
            { id: 'Datasets' },
            { id: datasetType, uri: `/search/?type=${datasetType}`, wholeTip: `Search for ${datasetType}` },
            { id: breakSetName(filesetType), uri: `/search/?type=${filesetType}`, wholeTip: `Search for ${filesetType}` },
        ];

        // Make string of alternate accessions
        const altacc = context.alternate_accessions.join(', ');

        // Make array of superseded_by accessions
        let supersededBys = [];
        if (context.superseded_by && context.superseded_by.length) {
            supersededBys = context.superseded_by.map(supersededBy => globals.atIdToAccession(supersededBy));
        }

        // Get a list of reference links, if any
        const references = pubReferenceList(context.references);

        // Render tags badges
        let tagBadges;
        if (context.internal_tags && context.internal_tags.length) {
            tagBadges = context.internal_tags.map(tag => <img src={`/static/img/tag-${tag}.png`} alt={`${tag} tag`} />);
        }

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs crumbs={crumbs} />
                        <h2>Summary for annotation file set {context.accession}</h2>
                        {altacc ? <h4 className="repl-acc">Replaces {altacc}</h4> : null}
                        {supersededBys.length ? <h4 className="superseded-acc">Superseded by {supersededBys.join(', ')}</h4> : null}
                        <div className="status-line">
                            <div className="characterization-status-labels">
                                <StatusLabel status={statuses} />
                            </div>
                            <AuditIndicators audits={context.audit} id="dataset-audit" />
                        </div>
                    </div>
                </header>
                <AuditDetail audits={context.audit} except={context['@id']} id="dataset-audit" />
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
                                            <dd>{softwareVersionList(context.software_used)}</dd>
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

                                    <AwardRef context={context} />

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

                {/* Display the file widget with the facet, graph, and tables */}
                <FileGallery context={context} encodevers={encodevers} />

                <DocumentsPanel documentSpecs={[{ documents: datasetDocuments }]} />
            </div>
        );
    },
});

globals.content_views.register(Annotation, 'Annotation');


// Display Annotation page, a subtype of Dataset.
const PublicationData = React.createClass({
    propTypes: {
        context: React.PropTypes.object, // PublicationData object to display
    },

    contextTypes: {
        session: React.PropTypes.object, // Login session information
    },

    mixins: [AuditMixin],

    render: function () {
        const context = this.props.context;
        const itemClass = globals.itemClass(context, 'view-item');
        const loggedIn = this.context.session && this.context.session['auth.userid'];
        const statuses = [{ status: context.status, title: 'Status' }];

        // Build up array of documents attached to this dataset
        const datasetDocuments = (context.documents && context.documents.length) ? context.documents : [];

        // Set up the breadcrumbs
        const datasetType = context['@type'][1];
        const filesetType = context['@type'][0];
        const crumbs = [
            { id: 'Datasets' },
            { id: datasetType, uri: `/search/?type=${datasetType}`, wholeTip: `Search for ${datasetType}` },
            { id: breakSetName(filesetType), uri: `/search/?type=${filesetType}`, wholeTip: `Search for ${filesetType}` },
        ];

        // Make string of alternate accessions
        const altacc = context.alternate_accessions.join(', ');

        // Render the publication links
        const referenceList = pubReferenceList(context.references);

        // Render tags badges
        let tagBadges;
        if (context.internal_tags && context.internal_tags.length) {
            tagBadges = context.internal_tags.map(tag => <img src={`/static/img/tag-${tag}.png`} alt={`${tag} tag`} />);
        }

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
                <AuditDetail audits={context.audit} except={context['@id']} id="dataset-audit" />
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

                                    <AwardRef context={context} />

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

                {/* Display the file widget with the facet, graph, and tables */}
                <FileGallery context={context} encodevers={globals.encodeVersion(context)} hideGraph />

                <DocumentsPanel documentSpecs={[{ documents: datasetDocuments }]} />
            </div>
        );
    },
});

globals.content_views.register(PublicationData, 'PublicationData');


// Display Annotation page, a subtype of Dataset.
const Reference = React.createClass({
    propTypes: {
        context: React.PropTypes.object, // Reference object to display
    },

    contextTypes: {
        session: React.PropTypes.object, // Login session information
    },

    mixins: [AuditMixin],

    render: function () {
        const context = this.props.context;
        const itemClass = globals.itemClass(context, 'view-item');
        const loggedIn = this.context.session && this.context.session['auth.userid'];
        const statuses = [{ status: context.status, title: 'Status' }];

        // Build up array of documents attached to this dataset
        const datasetDocuments = (context.documents && context.documents.length) ? context.documents : [];

        // Set up the breadcrumbs
        const datasetType = context['@type'][1];
        const filesetType = context['@type'][0];
        const crumbs = [
            { id: 'Datasets' },
            { id: datasetType, uri: `/search/?type=${datasetType}`, wholeTip: `Search for ${datasetType}` },
            { id: breakSetName(filesetType), uri: `/search/?type=${filesetType}`, wholeTip: `Search for ${filesetType}` },
        ];

        // Make string of alternate accessions
        const altacc = context.alternate_accessions.join(', ');

        // Get a list of reference links, if any
        const references = pubReferenceList(context.references);

        // Render tags badges
        let tagBadges;
        if (context.internal_tags && context.internal_tags.length) {
            tagBadges = context.internal_tags.map(tag => <img src={`/static/img/tag-${tag}.png`} alt={`${tag} tag`} />);
        }

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
                <AuditDetail audits={context.audit} except={context['@id']} id="dataset-audit" />
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
                                            <dd>{softwareVersionList(context.software_used)}</dd>
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

                                    <AwardRef context={context} />

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

                {/* Display the file widget with the facet, graph, and tables */}
                <FileGallery context={context} encodevers={globals.encodeVersion(context)} hideGraph altFilterDefault />

                <DocumentsPanel documentSpecs={[{ documents: datasetDocuments }]} />
            </div>
        );
    },
});

globals.content_views.register(Reference, 'Reference');


// Display Annotation page, a subtype of Dataset.
const Project = React.createClass({
    propTypes: {
        context: React.PropTypes.object, // Project object to display
    },

    contextTypes: {
        session: React.PropTypes.object, // Login session information
    },

    mixins: [AuditMixin],

    render: function () {
        const context = this.props.context;
        const itemClass = globals.itemClass(context, 'view-item');
        const loggedIn = this.context.session && this.context.session['auth.userid'];
        const statuses = [{ status: context.status, title: 'Status' }];

        // Build up array of documents attached to this dataset
        const datasetDocuments = (context.documents && context.documents.length) ? context.documents : [];

        // Collect organisms
        const organisms = (context.organism && context.organism.length) ? _.uniq(context.organism.map(organism => organism.name)) : [];

        // Set up the breadcrumbs
        const datasetType = context['@type'][1];
        const filesetType = context['@type'][0];
        const crumbs = [
            { id: 'Datasets' },
            { id: datasetType, uri: `/search/?type=${datasetType}`, wholeTip: `Search for ${datasetType}` },
            { id: breakSetName(filesetType), uri: `/search/?type=${filesetType}`, wholeTip: `Search for ${filesetType}` },
        ];

        // Make string of alternate accessions
        const altacc = context.alternate_accessions.join(', ');

        // Get a list of reference links
        const references = pubReferenceList(context.references);

        // Render tags badges
        let tagBadges;
        if (context.internal_tags && context.internal_tags.length) {
            tagBadges = context.internal_tags.map(tag => <img src={`/static/img/tag-${tag}.png`} alt={`${tag} tag`} />);
        }

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
                <AuditDetail audits={context.audit} except={context['@id']} id="dataset-audit" />
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
                                            <dd>{softwareVersionList(context.software_used)}</dd>
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

                                    <AwardRef context={context} />

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

                {/* Display the file widget with the facet, graph, and tables */}
                <FileGallery context={context} encodevers={globals.encodeVersion(context)} hideGraph />

                <DocumentsPanel documentSpecs={[{ documents: datasetDocuments }]} />
            </div>
        );
    },
});

globals.content_views.register(Project, 'Project');


// Display Annotation page, a subtype of Dataset.
const UcscBrowserComposite = React.createClass({
    propTypes: {
        context: React.PropTypes.object, // UCSC browser composite object to display
    },

    contextTypes: {
        session: React.PropTypes.object, // Login session information
    },

    mixins: [AuditMixin],

    render: function () {
        const context = this.props.context;
        const itemClass = globals.itemClass(context, 'view-item');
        const loggedIn = this.context.session && this.context.session['auth.userid'];
        const statuses = [{ status: context.status, title: 'Status' }];

        // Build up array of documents attached to this dataset
        const datasetDocuments = (context.documents && context.documents.length) ? context.documents : [];

        // Collect organisms
        const organisms = (context.organism && context.organism.length) ? _.uniq(context.organism.map(organism => organism.name)) : [];

        // Set up the breadcrumbs
        const datasetType = context['@type'][1];
        const filesetType = context['@type'][0];
        const crumbs = [
            { id: 'Datasets' },
            { id: datasetType, uri: `/search/?type=${datasetType}`, wholeTip: `Search for ${datasetType}` },
            { id: breakSetName(filesetType), uri: `/search/?type=${filesetType}`, wholeTip: `Search for ${filesetType}` },
        ];

        // Make string of alternate accessions
        const altacc = context.alternate_accessions.join(', ');

        // Get a list of reference links, if any
        const references = pubReferenceList(context.references);

        // Render tags badges
        let tagBadges;
        if (context.internal_tags && context.internal_tags.length) {
            tagBadges = context.internal_tags.map(tag => <img src={`/static/img/tag-${tag}.png`} alt={`${tag} tag`} />);
        }

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
                <AuditDetail audits={context.audit} except={context['@id']} id="dataset-audit" />
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
                                            <dd>{softwareVersionList(context.software_used)}</dd>
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

                                    <AwardRef context={context} />

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

                {/* Display the file widget with the facet, graph, and tables */}
                <FileGallery context={context} encodevers={globals.encodeVersion(context)} hideGraph />

                <DocumentsPanel documentSpecs={[{ documents: datasetDocuments }]} />
            </div>
        );
    },
});

globals.content_views.register(UcscBrowserComposite, 'UcscBrowserComposite');


export const FilePanelHeader = React.createClass({
    propTypes: {
        context: React.PropTypes.object, // Object being displayed
    },

    render: function () {
        const context = this.props.context;

        return (
            <div>
                {context.visualize_ucsc && context.status === 'released' ?
                    <span className="pull-right">
                        <DropdownButton title="Visualize Data" label="filepaneheader">
                            <DropdownMenu>
                                {Object.keys(context.visualize_ucsc).map(assembly =>
                                    <a key={assembly} data-bypass="true" target="_blank" rel="noopener noreferrer" href={context.visualize_ucsc[assembly]}>
                                        {assembly}
                                    </a>,
                                )}
                            </DropdownMenu>
                        </DropdownButton>
                    </span>
                : null}
                <h4>File summary</h4>
            </div>
        );
    },
});


function displayPossibleControls(item) {
    if (item.possible_controls && item.possible_controls.length) {
        return (
            <span>
                {item.possible_controls.map((control, i) =>
                    <span key={control.uuid}>
                        {i > 0 ? <span>, </span> : null}
                        <a href={control['@id']}>{control.accession}</a>
                    </span>,
                )}
            </span>
        );
    }
    return null;
}


const basicTableColumns = {
    accession: {
        title: 'Accession',
        display: experiment => <a href={experiment['@id']} title={`View page for experiment ${experiment.accession}`}>{experiment.accession}</a>,
    },

    assay_term_name: {
        title: 'Assay',
    },

    target: {
        title: 'Target',
        getValue: experiment => (experiment.target ? experiment.target.label : null),
    },

    description: {
        title: 'Description',
    },

    lab: {
        title: 'Lab',
        getValue: experiment => (experiment.lab ? experiment.lab.title : null),
    },
};

const treatmentSeriesTableColumns = {
    accession: {
        title: 'Accession',
        display: experiment => <a href={experiment['@id']} title={`View page for experiment ${experiment.accession}`}>{experiment.accession}</a>,
    },

    possible_controls: {
        title: 'Possible controls',
        display: displayPossibleControls,
        sorter: false,
    },

    assay_term_name: {
        title: 'Assay',
    },

    target: {
        title: 'Target',
        getValue: experiment => (experiment.target ? experiment.target.label : null),
    },

    description: {
        title: 'Description',
    },

    lab: {
        title: 'Lab',
        getValue: experiment => (experiment.lab ? experiment.lab.title : null),
    },
};

const replicationTimingSeriesTableColumns = {
    accession: {
        title: 'Accession',
        display: item => <a href={item['@id']} title={`View page for experiment ${item.accession}`}>{item.accession}</a>,
    },

    possible_controls: {
        title: 'Possible controls',
        display: displayPossibleControls,
        sorter: false,
    },

    assay_term_name: {
        title: 'Assay',
    },

    phase: {
        title: 'Biosample phase',
        display: (experiment) => {
            let phases = [];

            if (experiment.replicates && experiment.replicates.length) {
                const biosamples = experiment.replicates.map(replicate => replicate.library && replicate.library.biosample);
                phases = _.chain(biosamples.map(biosample => biosample.phase)).compact().uniq().value();
            }
            return phases.join(', ');
        },
        sorter: false,
    },

    target: {
        title: 'Target',
        getValue: experiment => (experiment.target ? experiment.target.label : null),
    },

    description: {
        title: 'Description',
    },

    lab: {
        title: 'Lab',
        getValue: experiment => (experiment.lab ? experiment.lab.title : null),
    },
};

const organismDevelopmentSeriesTableColumns = {
    accession: {
        title: 'Accession',
        display: experiment => <a href={experiment['@id']} title={`View page for experiment ${experiment.accession}`}>{experiment.accession}</a>,
    },

    possible_controls: {
        title: 'Possible controls',
        display: displayPossibleControls,
        sorter: false,
    },
    assay_term_name: {
        title: 'Assay',
    },

    relative_age: {
        title: 'Relative age',
        display: (experiment) => {
            let biosamples;
            let synchronizationBiosample;
            let ages;

            if (experiment.replicates && experiment.replicates.length) {
                biosamples = experiment.replicates.map(replicate => replicate.library && replicate.library.biosample);
            }
            if (biosamples && biosamples.length) {
                synchronizationBiosample = _(biosamples).find(biosample => biosample.synchronization);
                if (!synchronizationBiosample) {
                    ages = _.chain(biosamples.map(biosample => biosample.age_display)).compact().uniq().value();
                }
            }
            return (
                <span>
                    {synchronizationBiosample ?
                        <span>{`${synchronizationBiosample.synchronization} + ${synchronizationBiosample.age_display}`}</span>
                    :
                        <span>{ages.length ? <span>{ages.join(', ')}</span> : null}</span>
                    }
                </span>
            );
        },
        sorter: false,
    },

    life_stage: {
        title: 'Life stage',
        getValue: (experiment) => {
            let biosamples;
            let lifeStageBiosample;

            if (experiment.replicates && experiment.replicates.length) {
                biosamples = experiment.replicates.map(replicate => replicate.library && replicate.library.biosample);
            }
            if (biosamples && biosamples.length) {
                lifeStageBiosample = _(biosamples).find(biosample => biosample.life_stage);
            }
            return lifeStageBiosample.life_stage;
        },
    },

    target: {
        title: 'Target',
        getValue: item => (item.target ? item.target.label : null),
    },

    description: {
        title: 'Description',
    },

    lab: {
        title: 'Lab',
        getValue: item => (item.lab ? item.lab.title : null),
    },
};

export const Series = React.createClass({
    propTypes: {
        context: React.PropTypes.object, // Series object to display
    },

    contextTypes: {
        session: React.PropTypes.object,
    },

    mixins: [AuditMixin],

    // Map series @id to title and table columns
    seriesComponents: {
        MatchedSet: { title: 'matched set series', table: basicTableColumns },
        OrganismDevelopmentSeries: { title: 'organism development series', table: organismDevelopmentSeriesTableColumns },
        ReferenceEpigenome: { title: 'reference epigenome series', table: basicTableColumns },
        ReplicationTimingSeries: { title: 'replication timing series', table: replicationTimingSeriesTableColumns },
        TreatmentConcentrationSeries: { title: 'treatment concentration series', table: treatmentSeriesTableColumns },
        TreatmentTimeSeries: { title: 'treatment time series', table: treatmentSeriesTableColumns },
    },

    render: function () {
        const context = this.props.context;
        const itemClass = globals.itemClass(context, 'view-item');
        const loggedIn = this.context.session && this.context.session['auth.userid'];
        let experiments = {};
        const statuses = [{ status: context.status, title: 'Status' }];
        context.files.forEach((file) => {
            const experiment = file.replicate && file.replicate.experiment;
            if (experiment) {
                experiments[experiment['@id']] = experiment;
            }
        });
        experiments = _.values(experiments);

        // Build up array of documents attached to this dataset
        const datasetDocuments = (context.documents && context.documents.length) ? context.documents : [];

        // Set up the breadcrumbs
        const datasetType = context['@type'][1];
        const seriesType = context['@type'][0];
        const crumbs = [
            { id: 'Datasets' },
            { id: datasetType, uri: `/search/?type=${datasetType}`, wholeTip: `Search for ${datasetType}` },
            { id: breakSetName(seriesType), uri: `/search/?type=${seriesType}`, wholeTip: `Search for ${seriesType}` },
        ];

        // Make string of alternate accessions
        const altacc = context.alternate_accessions.join(', ');

        // Get a list of reference links, if any
        const references = pubReferenceList(context.references);

        // Make the series title
        const seriesComponent = this.seriesComponents[seriesType];
        const seriesTitle = seriesComponent ? seriesComponent.title : 'series';

        // Calculate the biosample summary
        let speciesRender = null;
        if (context.organism && context.organism.length) {
            const speciesList = _.uniq(context.organism.map(organism => organism.scientific_name));
            speciesRender = (
                <span>
                    {speciesList.map((species, i) =>
                        <span key={i}>
                            {i > 0 ? <span> and </span> : null}
                            <i>{species}</i>
                        </span>,
                    )}
                </span>
            );
        }
        const terms = (context.biosample_term_name && context.biosample_term_name.length) ? _.uniq(context.biosample_term_name) : [];

        // Render tags badges
        let tagBadges;
        if (context.internal_tags && context.internal_tags.length) {
            tagBadges = context.internal_tags.map(tag => <img src={`/static/img/tag-${tag}.png`} alt={`${tag} tag`} />);
        }

        // Calculate the donor diversity.
        const diversity = donorDiversity(context);

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
                <AuditDetail audits={context.audit} except={context['@id']} id="dataset-audit" />
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

                                    <div data-test="donordiversity">
                                        <dt>Donor diversity</dt>
                                        <dd>{diversity}</dd>
                                    </div>

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

                                    <AwardRef context={context} />

                                    <div data-test="project">
                                        <dt>Project</dt>
                                        <dd>{context.award.project}</dd>
                                    </div>

                                    {context.aliases.length ?
                                        <div data-test="aliases">
                                            <dt>Aliases</dt>
                                            <dd>{context.aliases.join(', ')}</dd>
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

                {context.related_datasets.length ?
                    <div>
                        <SortTablePanel title={`Experiments in ${seriesTitle} ${context.accession}`}>
                            <SortTable list={context.related_datasets} columns={seriesComponent.table} />
                        </SortTablePanel>
                    </div>
                : null }

                {/* Display list of released and unreleased files */}
                <FetchedItems
                    {...this.props}
                    url={globals.unreleased_files_url(context)}
                    Component={DatasetFiles}
                    filePanelHeader={<FilePanelHeader context={context} />}
                    encodevers={globals.encodeVersion(context)}
                    session={this.context.session}
                    ignoreErrors
                />

                <DocumentsPanel documentSpecs={[{ documents: datasetDocuments }]} />
            </div>
        );
    },
});

globals.content_views.register(Series, 'Series');


// Display a count of experiments in the footer, with a link to the corresponding search if needed
const ExperimentTableFooter = React.createClass({
    propTypes: {
        items: React.PropTypes.array, // Array of experiments that were displayed in the table
        total: React.PropTypes.number, // Total number of experiments
        url: React.PropTypes.string, // URL to link to equivalent experiment search results
    },

    render: function () {
        const { items, total, url } = this.props;

        return (
            <div>
                <span>Displaying {items.length} of {total} </span>
                {items.length < total ? <a className="btn btn-info btn-xs pull-right" href={url}>View all</a> : null}
            </div>
        );
    },
});


export const ExperimentTable = React.createClass({
    propTypes: {
        items: React.PropTypes.array, // List of experiments to display in the table
        limit: React.PropTypes.number, // Maximum number of experiments to display in the table
        total: React.PropTypes.number, // Total number of experiments
        url: React.PropTypes.string, // URI to go to equivalent search results
        title: React.PropTypes.oneOfType([ // Title for the table of experiments; can be string or component
            React.PropTypes.string,
            React.PropTypes.node,
        ]),
    },

    tableColumns: {
        accession: {
            title: 'Accession',
            display: item => <a href={item['@id']} title={`View page for experiment ${item.accession}`}>{item.accession}</a>,
        },

        assay_term_name: {
            title: 'Assay',
        },

        biosample_term_name: {
            title: 'Biosample term name',
        },

        target: {
            title: 'Target',
            getValue: item => item.target && item.target.label,
        },

        description: {
            title: 'Description',
        },

        title: {
            title: 'Lab',
            getValue: item => (item.lab && item.lab.title ? item.lab.title : null),
        },
    },

    render: function () {
        let experiments;

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
    },
});
