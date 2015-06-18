'use strict';
var React = require('react');
var globals = require('./globals');
var _ = require('underscore');


var Page = module.exports.Page = React.createClass({
    render: function() {
        var context = this.props.context;
        var Template = globals.cg_template.views[''][context.name];
        var content = Template ? <Template context={this.props.context} /> : null;
        if (content) {
            return (
                <div>
                    {content}
                </div>
            );
        } else {
            return null;
        }
    }
});


globals.content_views.register(Page, 'page');
