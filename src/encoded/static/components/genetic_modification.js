'use strict';
var React = require('react');
var _ = require('underscore');
var globals = require('./globals');
var {Breadcrumbs} = require('./navigation');

var GeneticModification = module.exports.GeneticModification = React.createClass({
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-detail key-value');

        var crumbs = [
            {id: 'Genetic Modifications'}
        ];

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
            </div>
        );
    }
});

globals.content_views.register(GeneticModification, 'GeneticModification');
