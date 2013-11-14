/** @jsx React.DOM */
'use strict';
var React = require('react');
var globals = require('./globals');


var TestingRenderErrorPanel = module.exports.TestingRenderErrorPanel = React.createClass({
    render: function() {
        this.method_does_not_exist();
    }
});

globals.panel_views.register(TestingRenderErrorPanel, 'testing_render_error');
