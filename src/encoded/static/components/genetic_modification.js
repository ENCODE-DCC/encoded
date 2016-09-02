'use strict';
var React = require('react');
var _ = require('underscore');
var globals = require('./globals');
var {FetchedItems} = require('./fetched');
var {Breadcrumbs} = require('./navigation');
var {Document, DocumentsPanel, DocumentsSubpanels, DocumentPreview, DocumentFile} = require('./doc');


var GeneticModification = module.exports.GeneticModification = React.createClass({
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-detail key-value');

        // Configure breadcrumbs for the page.
        var crumbs = [
            {id: 'Genetic Modifications'}
        ];

        // Collect and combine documents.
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
                    </div>
                </header>

                <div className="panel">
                    <dl className={itemClass}>
                        <div data-test="description">
                            <dt>Modification type</dt>
                            <dd>{context.modification_type}</dd>
                        </div>

                        {context.target ?
                            <div data-test="target">
                                <dt>Target</dt>
                                <dd><a href={context.target['@id']}>{context.target.label}</a></dd>
                            </div>
                        : null}
                    </dl>
                </div>

                {documents.length ?
                    <DocumentsPanel documentSpecs={[{documents: documents}]} />
                : null}
            </div>
        );
    }
});

globals.content_views.register(GeneticModification, 'GeneticModification');


var GeneticModificationCharacterizations = React.createClass({
    render: function () {
        var {items} = this.props;

        console.log('RESULTS: %o', items);
        return null;
    }
});
