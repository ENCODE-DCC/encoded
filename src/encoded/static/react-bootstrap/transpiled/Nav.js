"use strict";
/** @jsx React.DOM */

var React = require("react");
var classSet = require("react/lib/cx");
var BootstrapMixin = require("./BootstrapMixin")["default"];
var utils = require("./utils")["default"];


var Nav = React.createClass({displayName: 'Nav',
    mixins: [BootstrapMixin],

    propTypes: {
        bsStyle: React.PropTypes.oneOf(['tabs','pills','navbar-nav']),
        stacked: React.PropTypes.bool,
        justified: React.PropTypes.bool,
        navbar: React.PropTypes.bool,
        right: React.PropTypes.bool,
        dropdown: React.PropTypes.bool,
        onSelect: React.PropTypes.func
    },

    getDefaultProps: function () {
        return {
            bsClass: 'nav',
            navbar: false
        };
    },

    getInitialState: function() {
        console.log('getInitialState');
        return {
            dropdownComponent: undefined
        };
    },

    // Document popover context using React context mechanism.
    childContextTypes: {
        dropdownComponent: React.PropTypes.string,
        onDropdownChange: React.PropTypes.func
    },

    getChildContext: function() {
        console.log('getChildContext');
        return {
            dropdownComponent: this.state.dropdownComponent, // ID of component with visible dropdown
            onDropdownChange: this.handleDropdownChange // Function to process click in nav bar
        };
    },

    handleDropdownChange: function(componentID) {
        console.log('handleDropdownChange');
        // Use React _rootNodeID to uniquely identify a nav item with a dropdown;
        // It's passed in as componentID
        var newDropdownComponent;

        // If clicked component is component with visible dropdown, set to undefined to close popover
        newDropdownComponent = (this.state.dropdownComponent === componentID) ? undefined : componentID;
        this.setState({dropdownComponent: newDropdownComponent});
    },

    render: function () {
        var classes = this.getBsClassSet(this.props.navbar);

        classes['nav-stacked'] = this.props.stacked;
        classes['nav-justified'] = this.props.justified;
        classes['navbar-right'] = this.props.right;
        classes['dropdown-menu'] = this.props.dropdown;

        if (this.props.dropdown) {
            classes['nav'] = false;
        }

        if (!this.props.navbar && !this.props.dropdown) {
            return this.transferPropsTo(
                React.DOM.nav(null, 
                    NavItemRender( {classes:classes, children:this.props.children, renderNavItem:this.renderNavItem, id:this.props.id} )
                )
            );
        } else {
            return (
                NavItemRender( {classes:classes, children:this.props.children, renderNavItem:this.renderNavItem, id:this.props.id}  )
            );
        }
    },

    getChildActiveProp: function (child) {
        if (child.props.active) {
            return true;
        }
        if (this.props.activeKey != null) {
            if (child.props.key === this.props.activeKey) {
                return true;
            }
        }
        if (this.props.activeHref != null) {
            if (child.props.href === this.props.activeHref) {
                return true;
            }
        }

        return child.props.active;
    },

    renderNavItem: function (child) {
        return utils.cloneWithProps(
            child,
            {
                active: this.getChildActiveProp(child),
                activeKey: this.props.activeKey,
                activeHref: this.props.activeHref,
                onSelect: utils.createChainedFunction(child.onSelect, this.props.onSelect),
                ref: child.props.ref,
                key: child.props.key
            }
        );
    }
});

var NavItemRender = function (props) {
    return (
        React.DOM.ul( {className:classSet(props.classes), id:props.id}, 
            utils.modifyChildren(props.children, props.renderNavItem)
        )
    );
};

exports["default"] = Nav;