'use strict';
var React = require('react');

var Navbar = module.exports.Navbar = React.createClass({
	render: function() {
		return (
            <GlobalSections portal={this.props.portal} />
		);
	}
});


var GlobalSections = React.createClass({
    render: function() {
        var menus = this.props.portal.global_sections;

        return (
            <nav className="navbar navbar-default navbar-main">
                <div className="navbar-main-bg"></div>
                <div className="container">
                    <div className="container-fluid">
                        <div className="navbar-header">
                            <button type="button" className="navbar-toggle collapsed" data-toggle="collapse" data-target="#clingen-navbar-collapse">
                                <span className="sr-only">Toggle navigation</span>
                                <span className="icon-bar"></span>
                                <span className="icon-bar"></span>
                                <span className="icon-bar"></span>
                            </button>
                           <a className="navbar-brand text-hide" aria-role="banner" href="/">ClinGen</a>
                        </div>

                        <div className="collapse navbar-collapse" id="clingen-navbar-collapse">
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
                    </div>
                </div>
            </nav>
        );
    }
});
