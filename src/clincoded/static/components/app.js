'use strict';
var React = require('react');
var globals = require('./globals');
var mixins = require('./mixins');
var navbar = require('./navbar');
var jsonScriptEscape = require('../libs/jsonScriptEscape');
var url = require('url');

var Navbar = navbar.Navbar;

var routes = {
    'curator': require('./curator').Curator
};


// Site information, including navigation
var portal = {
    portal_title: 'ClinGen',
    global_sections: [
        {id: 'curator', title: 'Curator', url: '/curator'},
        {id: 'menu2', title: 'Menu 2', url: '/menu2'},
        {id: 'menu3', title: 'Menu 3', url: '/menu3'},
        {id: 'menu4', title: 'Menu 4', url: '/menu4'}
    ]
};


// Renders HTML common to all pages.
var App = module.exports = React.createClass({
    mixins: [mixins.Persona, mixins.HistoryAndTriggers],
    triggers: {
        login: 'triggerLogin',
        logout: 'triggerLogout',
    },

    getInitialState: function() {
        return {
            errors: [],
            portal: portal
        };
    },

    render: function() {
        var content;
        var context = this.props.context;
        var href_url = url.parse(this.props.href);
        var hash = href_url.hash || '';
        var name;
        var context_actions = [];
        if (hash.slice(0, 2) === '#!') {
            name = hash.slice(2);
        }

        var key = context && context['@id'];
        if (context) {
            Array.prototype.push.apply(context_actions, context.actions || []);
            if (!name && context.default_page) {
                context = context.default_page;
                var actions = context.actions || [];
                for (var i = 0; i < actions.length; i++) {
                    var action = actions[i];
                    if (action.href[0] == '#') {
                        action.href = context['@id'] + action.href;
                    }
                    context_actions.push(action);
                }
            }

            var ContentView = globals.content_views.lookup(context, name);
            content = <ContentView {...this.props} context={context}
                loadingComplete={this.state.loadingComplete} session={this.state.session}
                portal={this.state.portal} navigate={this.navigate} />;
        }
        var errors = this.state.errors.map(function (error) {
            return <div className="alert alert-error"></div>;
        });

        var canonical = this.props.href;
        if (context.canonical_uri) {
            if (href_url.host) {
                canonical = (href_url.protocol || '') + '//' + href_url.host + context.canonical_uri;
            } else {
                canonical = context.canonical_uri;
            }
        }

        return (
            <html lang="en">
                <head>
                    <meta charSet="utf-8" />
                    <meta httpEquiv="X-UA-Compatible" content="IE=edge" />
                    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                    <title>ClinGen</title>
                    <link rel="canonical" href={canonical} />
                    <script data-prop-name="inline" dangerouslySetInnerHTML={{__html: this.props.inline}}></script>
                    <link rel="stylesheet" href="/static/css/style.css" />
                    <script src="/static/build/bundle.js" async defer></script>
                </head>
                <body onClick={this.handleClick} onSubmit={this.handleSubmit}>
                    <script data-prop-name="context" type="application/ld+json" dangerouslySetInnerHTML={{
                        __html: '\n\n' + jsonScriptEscape(JSON.stringify(this.props.context)) + '\n\n'
                    }}></script>
                    <div>
                        <Header session={this.state.session} />
                        {content}
                    </div>
                </body>
            </html>
        );
    },

    statics: {
        // Get data to display from page <script> tag
        getRenderedProps: function (document) {
            var props = {};
            // Ensure the initial render is exactly the same
            props.href = document.querySelector('link[rel="canonical"]').href;
            var script_props = document.querySelectorAll('script[data-prop-name]');
            for (var i = 0; i < script_props.length; i++) {
                var elem = script_props[i];
                var value = elem.text;
                var elem_type = elem.getAttribute('type') || '';
                if (elem_type == 'application/json' || elem_type.slice(-5) == '+json') {
                    value = JSON.parse(value);
                }
                props[elem.getAttribute('data-prop-name')] = value;
            }
            return props;
        }
    }
});


// Render the common page header.
var Header = React.createClass({
    render: function() {
        var session = this.props.session;
        var sessionRender;

        if (!(session && session['auth.userid'])) {
            sessionRender = (
                <a data-trigger="login" href="#">Sign in</a>
            );
        } else {
            var fullname = (session.user_properties && session.user_properties.title) || 'unknown';
            sessionRender = (
                <a data-trigger="logout" href="#">{'Sign Out ' + fullname}</a>
            );
        }

        return (
            <header className="site-header">
                <div className="session-temp">
                    {sessionRender}
                </div>
                <Navbar portal={portal} />
            </header>
        );
    }
});
