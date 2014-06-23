/** @jsx React.DOM */
'use strict';
var React = require('react');
var jsonScriptEscape = require('../libs/jsonScriptEscape');
var globals = require('./globals');
var mixins = require('./mixins');
var NavBar = require('./navbar');
var Footer = require('./footer');
var fs = require('fs');
var url = require('url');

var portal = {
    portal_title: 'ENCODE',
    global_sections: [
        {id: 'antibodies', title: 'Antibodies', url: '/search/?type=antibody_approval'},
        {id: 'biosamples', title: 'Biosamples', url: '/search/?type=biosample'},
        {id: 'experiments', title: 'Experiments', url: '/search/?type=experiment'},
        {id: 'targets', title: 'Targets', url: '/search/?type=target'}
    ]
};


var user_actions = [
    {id: 'signout', title: 'Sign out', trigger: 'logout'}
];

var scriptjs = fs.readFileSync(__dirname + '/../../../../node_modules/scriptjs/dist/script.min.js', 'utf-8');
var inline = fs.readFileSync(__dirname + '/../inline.js', 'utf8');

// App is the root component, mounted on document.body.
// It lives for the entire duration the page is loaded.
// App maintains state for the
var App = React.createClass({
    mixins: [mixins.Persona, mixins.HistoryAndTriggers],
    triggers: {
        login: 'triggerLogin',
        logout: 'triggerLogout'
    },

    getInitialState: function() {
        return {
            errors: [],
            portal: portal,
            user_actions: user_actions
        };
    },

    render: function() {
        console.log('render app');
        var content;
        var context = this.props.context;
        var hash = url.parse(this.props.href).hash || '';
        var name;
        if (hash.slice(0, 2) === '#!') {
            name = hash.slice(2);
        }
        if (context) {
            var actions = this.props.context.actions;
            if (actions && actions.length) {
                actions = (
                    <div className="navbar navbar-default">
                        <div className="container">
                            {actions.map(action => <a href={action.href}><button className={action.className}>{action.title}</button></a>)}
                        </div>
                    </div>
                );
            } else {
                actions = null;
            }

            var ContentView = globals.content_views.lookup(context, name);
            content = this.transferPropsTo(ContentView({
                loadingComplete: this.state.loadingComplete,
                session: this.state.session,
                portal: this.state.portal,
                actions: actions,
                navigate: this.navigate
            }));
        }
        // Switching between collections may leave component in place
        var key = context && context['@id'];
        var errors = this.state.errors.map(function (error) {
            return <div className="alert alert-error"></div>;
        });

        var appClass = 'done';
        if (this.props.slow) {
            appClass = 'communicating'; 
        }

        var title = globals.listing_titles.lookup(context)({
            context: context,
            loadingComplete: this.state.loadingComplete
        });
        if (title && title != 'Home') {
            title = title + ' – ' + portal.portal_title;
        } else {
            title = portal.portal_title;
        }

        return (
            <html lang="en">
                <head>
                    <meta charSet="utf-8" />
                    <meta httpEquiv="X-UA-Compatible" content="IE=edge" />
                    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                    <title>{title}</title>
                    <link rel="canonical" href={this.props.href} />
                    <script dangerouslySetInnerHTML={{__html: scriptjs + '\n'}}></script>
                    <script dangerouslySetInnerHTML={{__html: inline}}></script>
                    <link rel="stylesheet" href="/static/css/style.css" />
                    <script src="/static/build/bundle.js" async defer></script>
                </head>
                <body onClick={this.handleClick} onSubmit={this.handleSubmit}>
                    <script data-prop-name="context" type="application/ld+json" dangerouslySetInnerHTML={{
                        __html: '\n\n' + jsonScriptEscape(JSON.stringify(this.props.context)) + '\n\n'
                    }}></script>
                    <div id="slot-application">
                        <div id="application" className={appClass}>
                        
                        <div className="loading-spinner"></div>
                                   
                            <div id="layout">
                                <NavBar href={this.props.href} portal={this.state.portal}
                                        user_actions={this.state.user_actions} session={this.state.session}
                                        loadingComplete={this.state.loadingComplete} />
                                <div id="content" className="container" key={key}>
                                    {content}
                                </div>
                                {errors}
                                <div id="layout-footer"></div>
                            </div>
                            <Footer />
                        </div>
                    </div>
                </body>
            </html>
        );
    }

});

module.exports = App;
