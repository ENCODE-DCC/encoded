"use strict";
/** @jsx React.DOM */

var React = require("react");
var classSet = require("react/lib/cx");
var BootstrapMixin = require("./BootstrapMixin")["default"];

var NavItem = React.createClass({displayName: 'NavItem',
    mixins: [BootstrapMixin],

    propTypes: {
        onSelect: React.PropTypes.func,
        active: React.PropTypes.bool,
        disabled: React.PropTypes.bool,
        href: React.PropTypes.string,
        title: React.PropTypes.string,
        trigger: React.PropTypes.string,
        dropdown: React.PropTypes.bool
    },

    // Dropdown context using React context mechanism.
    contextTypes: {
        dropdownComponent: React.PropTypes.string,
        onDropdownChange: React.PropTypes.func
    },

    getDefaultProps: function () {
        return {
            href: '#'
        };
    },

    // Call app with our React node ID if opening drop-down menu, or undefined if closing
    setDropdownState: function (newState) {
        this.context.onDropdownChange(newState ? this._rootNodeID : undefined);
    },

    render: function () {
        var classes = {
            'active': this.props.active,
            'disabled': this.props.disabled,
            'dropdown': this.props.dropdown,
            'open': this.context.dropdownComponent === this._rootNodeID
        };

        var anchorClass = this.props.dropdown ? 'dropdown-toggle' : '';

        return (
            React.DOM.li( {className:classSet(classes), 'aria-haspopup':this.props.dropdown}, 
                this.transferPropsTo(
                React.DOM.a(
                    {className:anchorClass,
                    onClick:this.handleClick,
                    ref:"anchor"}, 
                    this.props.dropdown ? React.DOM.span(null, this.props.children[0],React.DOM.span( {className:"caret"})) : this.props.children
                )),
                this.props.dropdown ? this.props.children.slice(1) : null
            )
        );
    },

    handleClick: function (e) {
        if (this.props.dropdown) {
            e.preventDefault();
            e.stopPropagation();
            this.setDropdownState(true);
        }
    }
});

exports["default"] = NavItem;