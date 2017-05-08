'use strict';
var React = require('react');
import createReactClass from 'create-react-class';
var globals = require('./globals');


var TestingRenderErrorPanel = module.exports.TestingRenderErrorPanel = createReactClass({
    render: function() {
        console.log('log');
        console.warn('warn');
        this.method_does_not_exist();
    }
});

globals.panel_views.register(TestingRenderErrorPanel, 'TestingRenderError');
