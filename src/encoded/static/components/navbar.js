/** @jsx React.DOM */
'use strict';
var React = require('react');
var url = require('url');
var mixins = require('./mixins');
var Navbar = require('../react-bootstrap/Navbar');
var Nav = require('../react-bootstrap/Nav');
var NavItem = require('../react-bootstrap/NavItem');

// Hide data from NavBarLayout
var NavBar = React.createClass({
    render: function() {
        var section = url.parse(this.props.href).pathname.split('/', 2)[1] || '';
        return NavBarLayout({
            loadingComplete: this.props.loadingComplete,
            portal: this.props.portal,
            section: section,
            session: this.props.session,
            user_actions: this.props.user_actions,
            href: this.props.href,
        });
    }
});


var NavBarLayout = React.createClass({

    render: function() {
        console.log('render navbar');
        var portal = this.props.portal;
        var section = this.props.section;
        var session = this.props.session;
        var user_actions = this.props.user_actions;
        return (
            <div id="navbar" className="navbar navbar-fixed-top navbar-inverse">
                <div className="container">
                    <Navbar brand={portal.portal_title} brandlink="/" noClasses={true} data-target="main-nav">
                        <GlobalSections global_sections={portal.global_sections} section={section} />
                        {this.transferPropsTo(<UserActions />)}
                        {this.transferPropsTo(<Search />)}
                    </Navbar>
                </div>
            </div>
        );
    }
});


var GlobalSections = React.createClass({
    render: function() {
        var section = this.props.section;
        var actions = this.props.global_sections.map(function (action) {
            var active = (section == action.id);
            return (
                <NavItem active={active} href={action.url} key={action.id}>
                    {action.title}
                </NavItem>
            );
        });
        return <Nav navbar={true} bsStyle="navbar-nav" activeKey={1}>{actions}</Nav>;
    }
});

var Search = React.createClass({
    render: function() {
        var id = url.parse(this.props.href, true);
        var searchTerm = id.query['searchTerm'] || '';
        return (
            <form className="navbar-form navbar-right" action="/search/">
                <div className="search-wrapper">
                    <input className="form-control search-query" id="navbar-search" type="text" placeholder="Search ENCODE" 
                        ref="searchTerm" name="searchTerm" defaultValue={searchTerm} key={searchTerm} />
                </div>
            </form>
        );  
    }
});


var UserActions = React.createClass({
    render: function() {
        var session = this.props.session;
        var disabled = !this.props.loadingComplete;
        if (!(session && session['auth.userid'])) {
            return (
                <Nav bsStyle="navbar-nav" navbar={true} right={true} id="user-actions">
                    <NavItem data-trigger="login" disabled={disabled}>Sign in</NavItem>
                </Nav>
            );
        }
        var actions = this.props.user_actions.map(function (action) {
            return (
                <NavItem href={action.url || ''} key={action.id} data-bypass={action.bypass} data-trigger={action.trigger}>
                    {action.title}
                </NavItem>
            );
        });
        var fullname = (session.user_properties && session.user_properties.title) || 'unknown';
        return (
            <Nav bsStyle="navbar-nav" navbar={true} right={true} id="user-actions">
                <NavItem dropdown={true}>
                    {fullname}
                    <Nav navbar={true} dropdown={true}>
                        {actions}
                    </Nav>
                </NavItem>
            </Nav>
        );
    }
});

module.exports = NavBar;
