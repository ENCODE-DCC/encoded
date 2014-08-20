/** @jsx React.DOM */
'use strict';
var React = require('react');
var url = require('url');
var mixins = require('./mixins');
var productionHost = require('./globals').productionHost;
var _ = require('underscore');
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
            context_actions: this.props.context_actions,
            user_actions: this.props.user_actions,
            href: this.props.href,
        });
    }
});


var NavBarLayout = React.createClass({
    getInitialState: function() {
        return {
            testWarning: !productionHost[url.parse(this.props.href).hostname]
        };
    },

    handleClick: function(e) {
        e.preventDefault();
        e.stopPropagation();

        // Remove the warning banner because the user clicked the close icon
        this.setState({testWarning: false});

        // If collection with .sticky-header on page, jiggle scroll position
        // to force the sticky header to jump to the top of the page.
        var hdrs = document.getElementsByClassName('sticky-header');
        if (hdrs.length) {
            window.scrollBy(0,-1);
            window.scrollBy(0,1);
        }
    },

    render: function() {
        console.log('render navbar');
        var portal = this.props.portal;
        var section = this.props.section;
        var session = this.props.session;
        var user_actions = this.props.user_actions;
        var context_actions = this.props.context_actions;
        return (
            <div id="navbar" className="navbar navbar-fixed-top navbar-inverse">
                <div className="container">
                    <Navbar brand={portal.portal_title} brandlink="/" noClasses={true} data-target="main-nav">
                        <GlobalSections global_sections={portal.global_sections} section={section} />
                        {this.transferPropsTo(<UserActions />)}
                        {context_actions ? this.transferPropsTo(<ContextActions />) : null}
                        {this.transferPropsTo(<Search />)}
                    </Navbar>
                </div>
                {this.state.testWarning ?
                    <div className="test-warning">
                        <div className="container">
                            <p>
                                The data displayed on this page is not official and only for testing purposes.
                                <a href="#" className="test-warning-close icon icon-times-circle-o" onClick={this.handleClick}></a>
                            </p>
                        </div>
                    </div>
                : null}
            </div>
        );
    }
});


var GlobalSections = React.createClass({
    render: function() {
        var section = this.props.section;

        // Render top-level main menu
        var actions = this.props.global_sections.map(function (action) {
            var subactions;
            if (action.children) {
                // Has dropdown menu; render it into subactions var
                subactions = action.children.map(function (action) {
                    return (
                        <NavItem href={action.url || ''} key={action.id}>
                            {action.title}
                        </NavItem>
                    );
                });
            }
            return (
                <NavItem dropdown={action.hasOwnProperty('children')} key={action.id} href={action.url || ''}>
                    {action.title}
                    {action.children ?
                        <Nav navbar={true} dropdown={true}>
                            {subactions}
                        </Nav>
                    : null}
                </NavItem>
            );
        });
        return <Nav navbar={true} bsStyle="navbar-nav" activeKey={1}>{actions}</Nav>;
    }
});

var ContextActions = React.createClass({
    render: function() {
        var actions = this.props.context_actions.map(function(action) {
            return (
                <NavItem href={action.href} key={action.name}>
                    <i className="icon icon-pencil"></i> {action.title}
                </NavItem>
            );
        });
        if (this.props.context_actions.length > 1) {
            actions = (
                <NavItem dropdown={true}>
                    <i className="icon icon-gear"></i>
                    <Nav navbar={true} dropdown={true}>
                        {actions}
                    </Nav>
                </NavItem>
            );
        }
        return <Nav bsStyle="navbar-nav" navbar={true} right={true} id="edit-actions">{actions}</Nav>;
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
