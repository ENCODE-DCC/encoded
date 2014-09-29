/** @jsx React.DOM */
'use strict';
var React = require('react');
var BootstrapMixin = require('./BootstrapMixin').BootstrapMixin;

var classSet = React.addons.classSet;

var NavItem = module.exports.NavItem = React.createClass({
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

    handleMouseEnter: function(e) {
        console.log('enter: ' + e);
    },

    handleMouseLeave: function(e) {
        console.log('leave: ' + e);
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
            <li className={classSet(classes)} aria-haspopup={this.props.dropdown}>
                {this.transferPropsTo(
                <a
                    className={anchorClass}
                    onClick={this.handleClick}
                    onMouseEnter={this.handleMouseEnter}
                    onMouseLeave={this.handleMouseLeave}
                    ref={this.rootNodeID}>
                    {this.props.dropdown ? <span>{this.props.children[0]}<span className="caret"></span></span> : this.props.children}
                </a>)}
                {this.props.dropdown ? this.props.children.slice(1) : null}
            </li>
        );
    },

    handleClick: function (e) {
        if (this.props.dropdown) {
            e.preventDefault();
            e.stopPropagation();
            this.setDropdownState(this.context.dropdownComponent !== this._rootNodeID);
        }
    }
});
