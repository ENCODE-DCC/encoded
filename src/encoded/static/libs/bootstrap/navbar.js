'use strict';
var React = require('react');
var cloneWithProps = require('react/lib/cloneWithProps');
var {DropdownMenu} = require('./dropdown-menu');

var Navbar = module.exports.Navbar = React.createClass({
    propTypes: {
        brand: React.PropTypes.oneOfType([ // String or component to display for the brand with class `navbar-brand`
            React.PropTypes.string,
            React.PropTypes.object
        ]),
        brandlink: React.PropTypes.string, // href for clicking brand
        label: React.PropTypes.string.isRequired, // id for nav; unique on page
        navClasses: React.PropTypes.string // CSS classes for <nav> in addition to "navbar"; default to "navbar-default"
    },
    
    getInitialState: function() {
        return {
            expanded: false, // True if mobile version of menu is expanded
            openDropdown: '' // String identifier of currently opened DropdownMenu
        };  
    },
    
    collapseClick: function(e) {
        // Click on the Navbar mobile "collapse" button
        this.setState({expanded: !this.state.expanded});
    },
    
    dropdownClick: function(dropdownId) {
        console.log(dropdownId);
        // DropdownMenu with id of `dropdownId` clicked
        this.setState({openDropdown: dropdownId === this.state.dropdownId ? '' : dropdownId});
    },

    render: function() {
        var {brand, brandlink, label, navClasses} = this.props;

        // Add the `openDropdown` property to any <DropdownMenu> child components
        var children = React.Children.map(this.props.children, child =>
            cloneWithProps(child, {
                openDropdown: this.state.openDropdown,
                dropdownClick: this.dropdownClick
            })
        );

        return (
            <nav className={'navbar ' + (navClasses ? navClasses : 'navbar-default')}>
                <div className="navbar-header">
                    <button type="button" className="navbar-toggle collapsed" data-toggle="collapse" data-target={label} aria-expanded={this.state.expanded} onClick={this.collapseClick}>
                        <span className="sr-only">Toggle navigation</span>
                        <span className="icon-bar"></span>
                        <span className="icon-bar"></span>
                        <span className="icon-bar"></span>
                    </button>
                    {brand ?
                        <a className="navbar-brand" href={brandlink}>{brand}</a>
                    : null}
                </div>
                
                <div className="collapse navbar-collapse" id={label}>
                    <ul className="nav navbar-nav">
                        {this.props.children}
                    </ul>
                </div>
            </nav>
        );
    }
});


var NavItem = module.exports.NavItem = React.createClass({
    render: function() {
        var {openDropdown, dropdownClick} = this.props;

        return (
            <li className={dropdownClick ? ('dropdown' + ()) : ''}>
                {this.props.children}
            </li>
        );
    }
});
