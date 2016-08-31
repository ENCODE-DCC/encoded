'use strict';
var React = require('react');
var Layout = require('./layout').Layout;
var globals = require('./globals');
var _ = require('underscore');


var Page = module.exports.Page = React.createClass({
    render: function() {
        var context = this.props.context;
        return (
            <div>
                <Layout value={context.layout} />
            </div>
        );
    }
});


globals.content_views.register(Page, 'Page');
