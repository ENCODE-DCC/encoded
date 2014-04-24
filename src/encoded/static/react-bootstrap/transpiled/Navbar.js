"use strict";
/** @jsx React.DOM */

var React = require("react");
var classSet = require("react/lib/cx");
var BootstrapMixin = require("./BootstrapMixin")["default"];
var utils = require("./utils")["default"];


var Navbar = React.createClass({displayName: 'Navbar',
  mixins: [BootstrapMixin],

  propTypes: {
    fixedTop: React.PropTypes.bool,
    fixedBottom: React.PropTypes.bool,
    staticTop: React.PropTypes.bool,
    inverse: React.PropTypes.bool
  },

  getInitialState: function() {
    return {
      collapsed: true
    };
  },

  getDefaultProps: function () {
    return {
      bsClass: 'navbar',
      bsStyle: 'default',
      brandlink: '#'
    };
  },

  handleCollapse: function() {
    var collapsed = !this.state.collapsed;
    this.setState({collapsed: collapsed});
  },

  render: function () {
    var classes = this.getBsClassSet();

    var toggleClass = classSet({
      "navbar-toggle": true,
      "collapsed": this.state.collapsed
    });
    var collapseClass = classSet({
      "navbar-collapse": true,
      "collapse": true,
      "in": !this.state.collapsed
    });

    classes['navbar-fixed-top'] = this.props.fixedTop;
    classes['navbar-fixed-bottom'] = this.props.fixedBottom;
    classes['navbar-static-top'] = this.props.staticTop;
    classes['navbar-inverse'] = this.props.inverse;

    return this.transferPropsTo(
      React.DOM.nav( {className:classSet(classes), role:"navigation"}, 
        React.DOM.div( {className:"container-fluid"}, 

          React.DOM.div( {className:"navbar-header"}, 
            React.DOM.button( {type:"button", className:toggleClass, 'data-toggle':"collapse",
                'data-target':'#' + this.props.target, onClick:this.handleCollapse}, 
              React.DOM.span( {className:"sr-only"}, "Toggle navigation"),
              React.DOM.span( {className:"icon-bar"}),
              React.DOM.span( {className:"icon-bar"}),
              React.DOM.span( {className:"icon-bar"})
            ),
            React.DOM.a( {className:"navbar-brand", href:this.props.brandlink}, this.props.brand)
          ),

          React.DOM.div( {className:collapseClass, id:this.props.target}, 
            this.props.children
          )
        )
      )
    );
  }
});

exports["default"] = Navbar;