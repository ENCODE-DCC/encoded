'use strict';
var React = require('react');
var _ = require('underscore');
var {Panel, PanelHeading, PanelBody} = require('../libs/bootstrap/panel');
var globals = require('./globals');
var {AuditIndicators, AuditDetail, AuditMixin} = require('./audit');
var {DbxrefList} = require('./dbxref');
var {FetchedItems} = require('./fetched');
var {Breadcrumbs} = require('./navigation');
var {Document, DocumentsPanel, DocumentsSubpanels, DocumentPreview, DocumentFile, AttachmentPanel} = require('./doc');


var GeneticModification = module.exports.GeneticModification = React.createClass({
    mixins: [AuditMixin],

    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-detail key-value');

        // Configure breadcrumbs for the page.
        var crumbs = [
            {id: 'Genetic Modifications'}
        ];

        // Collect and combine documents, including from genetic modification characterizations.
        var documents = [];
        if (context.documents && context.documents.length) {
            documents = context.documents;
        }
        if (context.characterizations && context.characterizations.length) {
            context.characterizations.forEach(characterization => {
                if (characterization.documents && characterization.documents.length) {
                    documents = documents.concat(characterization.documents);
                }
            });
        }
        if (documents.length) {
            documents = globals.uniqueObjectsArray(documents);
        }

        return (
            <div className={globals.itemClass(context, 'view-item')}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs root='/search/?type=GeneticModification' crumbs={crumbs} />
                        <h2>{context.modification_type}</h2>
                        <div className="status-line">
                            <AuditIndicators audits={context.audit} id="biosample-audit" />
                        </div>
                    </div>
                </header>

                <Panel>
                    <PanelBody>
                        <dl className={itemClass}>
                            {context.modification_description ?
                                <div data-test="description">
                                    <dt>Description</dt>
                                    <dd>{context.modification_description}</dd>
                                </div>
                            : null}

                            {context.modification_purpose ?
                                <div data-test="purpose">
                                    <dt>Modification purpose</dt>
                                    <dd>{context.modification_purpose}</dd>
                                </div>
                            : null}

                            {context.target ?
                                <div data-test="target">
                                    <dt>Target</dt>
                                    <dd><a href={context.target['@id']}>{context.target.label}</a></dd>
                                </div>
                            : null}
                        </dl>

                        {context.modification_techniques && context.modification_techniques.length ?
                            <GeneticModificationTechniques techniques={context.modification_techniques} />
                        : null}
                    </PanelBody>
                </Panel>

                {context.characterizations && context.characterizations.length ?
                    <GeneticModificationCharacterizations characterizations={context.characterizations} />
                : null}

                {documents.length ?
                    <DocumentsPanel documentSpecs={[{documents: documents}]} />
                : null}
            </div>
        );
    }
});

globals.content_views.register(GeneticModification, 'GeneticModification');


var GeneticModificationCharacterizations = React.createClass({
    propTypes: {
        characterizations: React.PropTypes.array // Genetic modificiation characterizations to display
    },

    render: function () {
        var {characterizations} = this.props;
        var itemClass = 'view-detail key-value';

        return (
            <Panel>
                <PanelHeading>
                    <h4>Characterizations</h4>
                </PanelHeading>
                <PanelBody>
                    {characterizations.map(characterization => {
                        return <AttachmentPanel context={characterization} attachment={characterization.attachment} title={characterization.characterization_method} />;
                    })}
                </PanelBody>
            </Panel>
        );
    }
});

var GeneticModificationTechniques = React.createClass({
    propTypes: {
        techniques: React.PropTypes.array // Genetic modificiation technique to display
    },

    render: function() {
        var {techniques} = this.props;
        return (
            <div>
                {techniques.map(technique => {
                    var ModificationTechniqueView = globals.panel_views.lookup(technique);
                    return <ModificationTechniqueView context={technique} />;
                })}
            </div>
        );
    }
});


var TechniqueCrispr = React.createClass({
    propTypes: {
        context: React.PropTypes.object // CRISPR genetic modificiation technique to display
    },

    render: function() {
        var {context} = this.props;
        var itemClass = globals.itemClass(context, 'view-detail key-value');

        return (
            <dl className={itemClass}>
                {context.dbxrefs && context.dbxrefs.length ?
                    <div data-test="externalresources">
                        <dt>External resources</dt>
                        <dd><DbxrefList values={context.dbxrefs} /></dd>
                    </div>
                : null}

                {context.insert_sequence ?
                    <div data-test="insertsequence">
                        <dt>Insert sequence</dt>
                        <dd>{context.insert_sequence}</dd>
                    </div>
                : null}
            </dl>
        );
    }
});

globals.panel_views.register(TechniqueCrispr, 'Crispr');


var TechniqueTale = React.createClass({
    propTypes: {
        context: React.PropTypes.object // TALE genetic modificiation technique to display
    },

    render: function() {
        var {context} = this.props;
        var itemClass = globals.itemClass(context, 'view-detail key-value');

        return (
            <dl className={itemClass}>
                {context.dbxrefs && context.dbxrefs.length ?
                    <div data-test="externalresources">
                        <dt>External resources</dt>
                        <dd><DbxrefList values={context.dbxrefs} /></dd>
                    </div>
                : null}

                <div data-test="rvdsequence">
                    <dt>RVD sequence</dt>
                    <dd>{context.RVD_sequence}</dd>
                </div>

                <div data-test="talenplatform">
                    <dt>TALEN platform</dt>
                    <dd>{context.talen_platform}</dd>
                </div>
            </dl>
        );
    }
});

globals.panel_views.register(TechniqueTale, 'Tale');
