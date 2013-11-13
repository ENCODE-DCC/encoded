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

                <dt>GEO Platform ID(s)</dt>
                <dd>
                    {context.geo_dbxrefs.length ?
                        <DbxrefList values={context.geo_dbxrefs} prefix="GEO" />
                    : <em>None submitted</em> }
                </dd>

                <dt>OBI ID</dt>
                <dd><Dbxref value={context.term_id} /></dd>

                <dt>ENCODE2 ID</dt>
                <dd>
                    {context.encode2_dbxrefs.length ?
                        <DbxrefList values={context.encode2_dbxrefs} prefix="ENCODE2" />
                    : null}
                </dd>
            </dl>
        );
    }
});

globals.panel_views.register(Panel, 'platform');
