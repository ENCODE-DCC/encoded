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
        var itemClass = globals.itemClass(context);
        return (
            <div className={itemClass}>
                <p className="lead">{context.authors}</p>

                <div className="view-detail panel">
                    <div>
                      <i>{context.journal}</i>. {context.date_published}; {context.volume}{context.issue ? '(' + context.issue + ')' : '' }:{context.page}. {context.references.length ? <DbxrefList values={context.references} className="multi-value" /> : '' }
                    </div>

                    <h2>Abstract</h2>
                    <div>{context.abstract}</div>
                </div>
            </div>
        );
    }
});

globals.panel_views.register(Panel, 'publication');
