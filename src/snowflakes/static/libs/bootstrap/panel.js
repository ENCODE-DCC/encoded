'use strict';
var React = require('react');


var Panel = module.exports.Panel = React.createClass({
    propTypes: {
        addClasses: React.PropTypes.string // Classes to add to outer panel div
    },

    render: function() {
        return (
            <div className={'panel panel-default' + (this.props.addClasses ? ' ' + this.props.addClasses : '')}>
                {this.props.children}
            </div>
        );
    }
});


var PanelBody = module.exports.PanelBody = React.createClass({
    propTypes: {
        addClasses: React.PropTypes.string // Classes to add to outer panel div
    },

    render: function() {
        return (
            <div className={'panel-body' + (this.props.addClasses ? ' ' + this.props.addClasses : '')}>
                {this.props.children}
            </div>
        );
    }
});


var PanelHeading = module.exports.PanelHeading = React.createClass({
    propTypes: {
        addClasses: React.PropTypes.string // Classes to add to outer panel div
    },

    render: function() {
        return (
            <div className={'panel-heading' + (this.props.addClasses ? ' ' + this.props.addClasses : '')}>
                {this.props.children}
            </div>
        );
    }
});
