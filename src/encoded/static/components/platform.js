'use strict';
var React = require('react');
var globals = require('./globals');
var { DbxrefList, dbxref } = require('./dbxref');

var Panel = module.exports.Panel = React.createClass({
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-detail key-value');
        return (
            <div className="panel">
                <dl className={itemClass}>
                    <div data-test="name">
                        <dt>Platform name</dt>
                        <dd><a href={context.url}>{context.title}</a></dd>
                    </div>

                    <div data-test="obiid">
                        <dt>OBI ID</dt>
                        <dd><dbxref value={context.term_id} /></dd>
                    </div>

                    <div data-test="externalresources">
                        <dt>External resources</dt>
                        <dd>
                            {context.dbxrefs.length ?
                                <DbxrefList values={context.dbxrefs} />
                            : <em>None submitted</em> }
                        </dd>
                    </div>
                </dl>
            </div>
        );
    }
});

globals.panel_views.register(Panel, 'Platform');
