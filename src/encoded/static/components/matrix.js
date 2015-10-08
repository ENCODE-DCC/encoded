'use strict';
var React = require('react');
var globals = require('./globals');

var Matrix = module.exports.Matrix = React.createClass({

    render: function() {
        var context = this.props.context;
        var notification = context['notification'];
        return (
            <div>
                <h4>{notification}</h4>
            </div>
        );
    }
});

globals.content_views.register(Matrix, 'Matrix');
