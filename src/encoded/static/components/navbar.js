/** @jsx React.DOM */
'use strict';
var React = require('react');
var url = require('url');
var mixins = require('./mixins');

// Hide data from NavBarLayout
var NavBar = React.createClass({
    render: function() {
        var section = url.parse(this.props.href).pathname.split('/', 2)[1] || '';
        return NavBarLayout({
            personaReady: this.props.personaReady,
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
                <div className="navbar-inner">
                    <div className="container">
                        <a className="btn btn-navbar" href="" data-toggle="collapse" data-target=".nav-collapse">
                            <span className="icon-bar"></span>
                            <span className="icon-bar"></span>
                            <span className="icon-bar"></span>
                        </a>
                        <a className="brand" href="/">{portal.portal_title}</a>
                        <div className="nav-collapse collapse">
                            <GlobalSections global_sections={portal.global_sections} section={section} />
                            {this.transferPropsTo(<UserActions />)}
                            {this.transferPropsTo(<Search />)}
                        </div>
                    </div>
                </div>
            </div>
        );
    }
});


var GlobalSections = React.createClass({
    render: function() {
        var section = this.props.section;
        var actions = this.props.global_sections.map(function (action) {
            var className = action['class'] || '';
            if (section == action.id) {
                className += ' active';
            }
            return (
                <li className={className} key={action.id}>
                    <a href={action.url}>{action.title}</a>
                </li>
            );
        });
        return <ul id="global-sections" className="nav">{actions}</ul>;
    }
});

var Search = React.createClass({
    render: function() {
        var id = url.parse(this.props.href, true);
        var searchTerm = id.query['searchTerm'] || '';
        return (
        	<form className="navbar-form pull-right" action="/search/">
    			<div className="search-wrapper">
    				<input className="input-medium search-query searchbox-style" type="text" placeholder="Search ENCODE" 
                        ref="searchTerm" name="searchTerm" defaultValue={searchTerm} key={searchTerm} />
    			</div>
    		</form>
        );  
    }
});


var UserActions = React.createClass({
    render: function() {
        var session = this.props.session;
        var disabled = !this.props.personaReady;
        if (!(session && session.persona)) {
            return (
                <ul id="user-actions" className="nav pull-right" hidden={!session}>
                    <li><a href="" disabled={disabled} data-trigger="login" data-id="signin">Sign in</a></li>
                </ul>
            );
        }
        var actions = this.props.user_actions.map(function (action) {
            return (
                <li className={action['class']} key={action.id}>
                    <a href={action.url || ''} data-bypass={action.bypass} data-trigger={action.trigger}>
                        {action.title}
                    </a>
                </li>
            );
        });
        var fullname = session.user_properties.title;
        return (
            <ul id="user-actions" className="nav pull-right">
                <li className="dropdown">
                    <a href="" className="dropdown-toggle" data-toggle="dropdown">{fullname}
                    <b className="caret"></b></a>
                    <ul className="dropdown-menu">
                        {actions}
                    </ul>
                </li>
            </ul>
        );
    }
});

module.exports = NavBar;
