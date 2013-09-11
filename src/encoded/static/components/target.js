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
                    <dd class="no-cap">{context.label}</dd>

                    <dt>Target Gene</dt>
                    <dd>{context.gene_name}</dd>

                    <dt>External Resources</dt>
                    <dd>
                        {context.dbxref.length ? 
                            <DbxrefList values={context.dbxref} />
                        : <em>None submitted</em> }
                    </dd>

                    <dt>Species</dt>
                    <dd>{context.organism.name}</dd>
                </dl>
            );
        }
    });

    globals.panel_views.register(Panel, 'target');

    return target;
});
