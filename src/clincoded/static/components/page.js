'use strict';
var React = require('react');
var globals = require('./globals');
var _ = require('underscore');


var Page = module.exports.Page = React.createClass({
    render: function() {
        var context = this.props.context;
        var template = globals.cg_template.views[''][context.name];
        var content = template(this.props.context);
        return (
            <div>
                {content}
            </div>
        );
    }
});


globals.content_views.register(Page, 'page');
