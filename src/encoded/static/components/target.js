/** @jsx React.DOM */
define(['exports', 'react', 'globals', 'jsx!dbxref'],
function (target, React, globals, dbxref) {
    'use strict';

    var DbxrefList = dbxref.DbxrefList;

    var Panel = target.Panel = React.createClass({
        render: function() {
            var context = this.props.context;
            var itemClass = globals.itemClass(context, 'view-detail panel key-value');
            return (
                <dl class={itemClass}>
                    <dt>Target name</dt>
                    <dd>{context.label}</dd>

                    <dt>Target Gene</dt>
                    <dd>{context.target_gene_name}</dd>

                    <dt>DB cross references</dt>
                    <dd>
                        {context.dbxref.length ? 
                            <DbxrefList values={context.dbxref} />
                        : <em>None submitted</em> }
                    </dd>

                    <dt>Species</dt>
                    <dd>{context.organism.name}</dd>

                    <dt>Target Class</dt>
                    <dd>{context.target_class}</dd>

                    <dt>RFA</dt>
                    <dd>{context.award.rfa}</dd>

                    <dt>Lab</dt>
                    <dd>{context.lab.title}</dd>

                    <dt>Grant</dt>
                    <dd>{context.award.name}</dd>

                    <dt>Date created</dt>
                    <dd>{context.date_created}</dd>
                </dl>
            );
        }
    });

    globals.panel_views.register(Panel, 'target');

    return target;
});
