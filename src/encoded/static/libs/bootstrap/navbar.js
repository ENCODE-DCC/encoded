'use strict';
var React = require('react');
import PropTypes from 'prop-types';
import createReactClass from 'create-react-class';
var {DropdownMenu} = require('./dropdown-menu');


// This module handles menu bars, and combined with the <DropdownMenu> component, handles dropdown
// menus within menu bars. To use it, you must first include the `Navbars` mixin in the component
// that renders the menu bars.
//
// Use these components like this:
//
// mixin: [Navbars],
// render: function () {
//     return (
//         <Navbar>
//             <Nav>
//                 <NavItem>
//                     <a href="/">Standalone Item</a>
//                 </NavItem>
//                 <NavItem title="Dropdown Menu">
//                     <DropdownMenu>
//                         <a href="/">Dropdown Item</a>
//                     </DropdownMenu>
//                 </NavItem>
//              </Nav>
//              <Nav>
//                  ...
//              </Nav>
//          </Navbar>
//     );
// }

var Navbars = module.exports.Navbars = {
    childContextTypes: {
        openDropdown: PropTypes.string, // Identifies dropdown currently dropped down; '' if none
        dropdownClick: PropTypes.func // Called when a dropdown title gets clicked
    },

    // Retrieve current React context
    getChildContext: function() {
        return {
            openDropdown: this.state.openDropdown,
            dropdownClick: this.dropdownClick
        };
    },

    getInitialState: function() {
        return {openDropdown: ''};
    },

    componentDidMount: function() {
        // Add a click handler to the DOM document -- the entire page
        document.addEventListener('click', this.documentClickHandler);
    },

    componentWillUnmount: function() {
        // Remove the DOM document click handler now that the DropdownButton is going away.
        document.removeEventListener('click', this.documentClickHandler);
    },

    documentClickHandler: function() {
        // A click outside the DropdownButton closes the dropdown
        this.setState({openDropdown: ''});
    },

    dropdownClick: function(dropdownId, e) {
        // After clicking the dropdown trigger button, don't allow the event to bubble to the rest of the DOM.
        e.nativeEvent.stopImmediatePropagation();
        this.setState({openDropdown: dropdownId === this.state.openDropdown ? '' : dropdownId});
    }
};


// Controls an entire navigation menu with one or more navigation areas defined by <Nav>
// components. Handles the toggling of the mobile menu expansion.
var Navbar = module.exports.Navbar = createReactClass({
    propTypes: {
        brand: PropTypes.oneOfType([ // String or component to display for the brand with class `navbar-brand`
            PropTypes.string,
            PropTypes.object
        ]),
        brandlink: PropTypes.string, // href for clicking brand
        label: PropTypes.string.isRequired, // id for nav; unique on page
        navClasses: PropTypes.string // CSS classes for <nav> in addition to "navbar"; default to "navbar-default"
    },

    getInitialState: function() {
        return {
            expanded: false // True if mobile version of menu is expanded
        };
    },
    
    collapseClick: function(e) {
        // Click on the Navbar mobile "collapse" button
        console.log('collapse: %s', this.state.expanded);
        this.setState({expanded: !this.state.expanded});
    },

    render: function() {
        var {brand, brandlink, label, navClasses} = this.props;

        return (
            <nav className={'navbar ' + (navClasses ? navClasses : 'navbar-default')}>
                <div className="navbar-header">
                    <a href="#" data-trigger className="navbar-toggle collapsed" data-toggle="collapse" data-target={label} aria-expanded={this.state.expanded} onClick={this.collapseClick}>
                        <span className="sr-only">Toggle navigation</span>
                        <span className="icon-bar"></span>
                        <span className="icon-bar"></span>
                        <span className="icon-bar"></span>
                    </a>
                    {brand ?
                        <a className="navbar-brand" href={brandlink}>{brand}</a>
                    : null}
                </div>
                
                <div className={'collapse navbar-collapse' + (this.state.expanded ? ' in' : '')} id={label}>
                    {this.props.children}
                </div>
            </nav>
        );
    }
});


// Controls one navigation area within a <Navbar>
var Nav = module.exports.Nav = createReactClass({
    propTypes: {
        right: PropTypes.bool // True if right-justified navigation area
    },

    render: function() {
        return (
            <ul className={'nav navbar-nav' + (this.props.right ? ' navbar-right' : '')}>
                {this.props.children}
            </ul>
        );
    }
});


// Controls one top-level item within a <Nav>. It can be a stand-alone item or a dropdown menu
var NavItem = module.exports.NavItem = createReactClass({
    propTypes: {
        dropdownId: PropTypes.string, // If this item has a dropdown, this ID helps manage it; must be unique
        dropdownTitle: PropTypes.oneOfType([ // If this item has a dropdown, this is the title
            PropTypes.string,
            PropTypes.object
        ])
    },

    contextTypes: {
        openDropdown: PropTypes.string,
        dropdownClick: PropTypes.func
    },

    render: function() {
        var {dropdownId, dropdownTitle} = this.props;
        var dropdownOpen = dropdownId && (this.context.openDropdown === dropdownId);

        return (
            <li className={dropdownId ? ('dropdown' + (dropdownOpen ? ' open' : '')) : ''}>
                {dropdownTitle ?
                    <a href="#" data-trigger className="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded={dropdownOpen} onClick={this.context.dropdownClick.bind(null, dropdownId)}>
                        {dropdownTitle}
                    </a>
                : null}
                {this.props.children}
            </li>
        );
    }
});
