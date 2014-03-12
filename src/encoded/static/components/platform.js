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
        return (
            <dl className={itemClass}>
                <dt>Platform name</dt>
                <dd><a href={context.url}>{context.title}</a></dd>

                <dt>OBI ID</dt>
                <dd><Dbxref value={context.term_id} /></dd>

                <dt>External resources</dt>
                <dd>
                    {context.dbxrefs.length ?
                        <DbxrefList values={context.dbxrefs} />
                    : <em>None submitted</em> }
                </dd>
            </dl>
        );
    }
});

globals.panel_views.register(Panel, 'platform');
