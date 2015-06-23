'use strict';
var React = require('react');

var Navbar = module.exports.Navbar = React.createClass({
    getInitialState: function() {
        return {mobileMenuOpen: false}; // True if mobile menu is visible; triggered by “
    },

    mobileMenuClick: function() {
        this.setState({mobileMenuOpen: !this.state.mobileMenuOpen});
    },

	render: function() {
		return (
            <nav className="navbar navbar-default navbar-main">
                <div className="navbar-main-bg"></div>
                <div className="container">
                    <div className="container-fluid">
                        <div className="navbar-header">
                            <button type="button" className="navbar-toggle" onClick={this.mobileMenuClick}>
                                <span className="sr-only">Toggle navigation</span>
                                <span className="icon-bar"></span>
                                <span className="icon-bar"></span>
                                <span className="icon-bar"></span>
                            </button>
                           <a className="navbar-brand text-hide" aria-role="banner" href="/">ClinGen</a>
                        </div>
                        <GlobalSections mobileMenuOpen={this.state.mobileMenuOpen} portal={this.props.portal} />
                    </div>
                </div>
            </nav>
		);
	}
});


var GlobalSections = React.createClass({
    render: function() {
        var menus = this.props.portal.global_sections;
        var collapseClasses = 'navbar-collapse' + (this.props.mobileMenuOpen ? '' : ' collapse');

        return (
            <div className={collapseClasses}>
                <ul className="nav navbar-nav navbar-right nav-main">
                    {menus.map(function(menu) {
                        return (
                            <li key={menu.id}>
                                <a href={menu.url}>{menu.title}</a>
                            </li>
                        );
                    })}
                </ul>
            </div>
        );
    }
});
