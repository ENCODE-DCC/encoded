/** @jsx React.DOM */
define(['exports', 'react', 'globals'],
function (target, React, globals) {
    'use strict';


    var Panel = target.Panel = React.createClass({
        render: function() {
            var context = this.props.context;
            var itemClass = globals.itemClass(context, 'view-detail panel key-value');
            return (
                <dl class={itemClass}>
                    <dt>Target name</dt>
                    <dd>{context.target_label}</dd>

                    <dt>Target Gene</dt>
                    <dd>{context.target_gene_name}</dd>

                    <dt>UniProt ID</dt>
                    <dd>
                        {context.dbxref.uniprot.length ? 
                            context.dbxref.uniprot.map(function (id, index) {
                                // XXX should be an &nbsp; below, see: https://github.com/facebook/react/issues/183
                                return (
                                    <span key={index}><a href={'http://www.uniprot.org/uniprot/' + id}>{id}</a>{' '}</span>
                                );
                            })
                        : <em>None submitted</em> }
                    </dd>

                    <dt>Species</dt>
                    <dd>{context.organism.organism_name}</dd>

                    <dt>Target Class</dt>
                    <dd>{context.target_class}</dd>

                    <dt>Project</dt>
                    <dd>{context.project}</dd>

                    <dt>Lab</dt>
                    <dd>{context.lab.name}</dd>

                    <dt>Grant</dt>
                    <dd>{context.award.number}</dd>

                    <dt>Date createad</dt>
                    <dd>{context.date_created}</dd>
                </dl>
            );
        }
    });

    globals.panel_views.register(Panel, 'target');


    var title = target.title = function (props) {
        return props.context.organism.organism_name + ' ' + props.context.target_label;
    };

    globals.listing_titles.register(title, 'target');


    return target;
});
