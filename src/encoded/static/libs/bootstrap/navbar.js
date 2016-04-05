'use strict';
var React = require('react');

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
            expanded: false
        };  
    },
    
    collapseClick: function(e) {
        // Click on the Navbar mobile "collapse" button
        this.setState({expanded: !this.state.expanded});
    },

    render: function() {
        var {brand, brandlink, label, navClasses} = this.props;

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
                    {this.props.children}
                </div>
            </nav>
        );
    }
});


var Nav = module.exports.Nav = React.createClass({
    render: function() {
        return (
            <ul className="nav navbar-nav">
                {this.props.children.map(child => <li>{child}</li>)}
            </ul>
        );
    }
});


var NavItem = module.exports.NavItem = React.createClass({
    render: function() {
        console.log(this.props.children);
        return <li>{this.props.children}</li>;
    }    
});
