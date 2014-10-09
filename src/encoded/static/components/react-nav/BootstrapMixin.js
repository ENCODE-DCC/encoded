/** @jsx React.DOM */
'use strict';
var React = require('react');
var constants = require('./constants').constants;

var classSet = React.addons.classSet;

var BootstrapMixin = module.exports.BootstrapMixin = {
    propTypes: {
        bsClass: React.PropTypes.oneOf(Object.keys(constants.CLASSES)),
        bsStyle: React.PropTypes.oneOf(Object.keys(constants.STYLES)),
        bsSize: React.PropTypes.oneOf(Object.keys(constants.SIZES))
    },

    getBsClassSet: function (noprefix) {
        var classes = {};

        var bsClass = this.props.bsClass && constants.CLASSES[this.props.bsClass];
        if (bsClass) {
            classes[bsClass] = true;

            var prefix = noprefix ? '' : bsClass + '-';

            var bsSize = this.props.bsSize && constants.SIZES[this.props.bsSize];
            if (bsSize) {
                classes[prefix + bsSize] = true;
            }

            var bsStyle = this.props.bsStyle && constants.STYLES[this.props.bsStyle];
            if (this.props.bsStyle) {
                classes[prefix + bsStyle] = true;
            }
        }

        return classes;
    }
};
