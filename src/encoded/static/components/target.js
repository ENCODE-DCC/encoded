/** @jsx React.DOM */
'use strict';
var React = require('react');
var globals = require('./globals');
var dbxref = require('./dbxref');

var DbxrefList = dbxref.DbxrefList;
var Dbxref = dbxref.Dbxref;

var Panel = module.exports.Panel = React.createClass({
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-detail panel key-value');
        var geneLink;

        if (context.organism.name == "human") {
            geneLink = globals.dbxref_prefix_map.HGNC + context.gene_name;
        } else if (context.organism.name == "mouse") {
            var uniProtValue = JSON.stringify(context.dbxref);
            var sep = uniProtValue.indexOf(":") + 1;
            var uniProtID = uniProtValue.substring(sep, uniProtValue.length - 2);
            geneLink = globals.dbxref_prefix_map.UniProtKB + uniProtID;
        }
        return (
            <dl className={itemClass}>
                <dt>Target name</dt>
                <dd>{context.label}</dd>

                <dt hidden={!context.gene_name}>Target gene</dt>
                <dd hidden={!context.gene_name}><a href={geneLink}>{context.gene_name}</a></dd>

                <dt>External resources</dt>
                <dd>
                    {context.dbxref.length ?
                        <DbxrefList values={context.dbxref} target_gene={context.gene_name} />
                    : <em>None submitted</em> }
                </dd>
            </dl>
        );
    }
});

globals.panel_views.register(Panel, 'target');
