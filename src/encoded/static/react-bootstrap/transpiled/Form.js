"use strict";
/** @jsx React.DOM */

var React = require('react');
var classSet = require("react/lib/cx");
var BootstrapMixin = require("./BootstrapMixin")["default"];


var Form = React.createClass({displayName: 'Form',
  mixins: [BootstrapMixin],

  propTypes: {
    navbar: React.PropTypes.bool,
    align: React.PropTypes.oneOf(['left','right']),
    role: React.PropTypes.string
  },

  getDefaultProps: function () {
    return {
      navbar: false,
      align: 'left',
      role: 'form'
    };
  },

  render: function () {
    var classes = this.getBsClassSet();

    classes['navbar-form'] = this.props.navbar;
    if (this.props.align === 'right') {
      classes['navbar-right'] = true;
    } else {
      classes['navbar-left'] = true;
    }

    return (
      React.DOM.form( {className:classSet(classes), role:this.props.role}, 
        this.props.children
      )
    );
  }
});


exports["default"] = Form;