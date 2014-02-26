/** @jsx React.DOM */
'use strict';
var React = require('react');
var jsonScriptEscape = require('jsonScriptEscape');
var globals = require('./globals');
var mixins = require('./mixins');
var NavBar = require('./navbar');
var Footer = require('./footer');
var url = require('url');

var portal = {
    portal_title: 'ENCODE',
    global_sections: [
        {id: 'antibodies', title: 'Antibodies', url: '/search/?type=antibody_approval'},
        {id: 'biosamples', title: 'Biosamples', url: '/search/?type=biosample'},
        {id: 'experiments', title: 'Experiments', url: '/search/?type=experiment'},
        {id: 'targets', title: 'Targets', url: '/search/?type=target'}
    ],
    // Should readlly be singular...
    types: {
        antibody_approval: {title: 'Antibodies'},
        biosample: {title: 'Biosamples'},
        experiment: {title: 'Experiments'},
        target: {title: 'Targets'},
        dataset: {title: 'Datasets'}
    }
};


var user_actions = [
    {id: 'signout', title: 'Sign out', trigger: 'logout'}
];

var ie8compat = [
    "article",
    "aside",
    "footer",
    "header",
    "hgroup",
    "nav",
    "section",
    "figure",
    "figcaption",
].map(function (tag) {
    return 'document.createElement("' + tag + '");';
}).join('\n');

var analytics = [
"(function(i, s, r){",
    "i['GoogleAnalyticsObject'] = r;",
    "i[r] = i[r] || function() {",
        "(i[r].q = i[r].q || []).push(arguments)",
    "},",
    "i[r].l = 1 * new Date();",
    "})(window, document, 'ga');",
// Use a separate tracker for dev / test
"if (({'submit.encodedcc.org':1,'www.encodedcc.org':1,'encodedcc.org':1})[document.location.hostname]) {",
    "ga('create', 'UA-47809317-1', {'cookieDomain': 'encodedcc.org', 'siteSpeedSampleRate': 100});",
"} else {",
    "ga('create', 'UA-47809317-2', {'cookieDomain': 'none', 'siteSpeedSampleRate': 100});",
"}",
"ga('send', 'pageview');"
].join('\n');


// Need to know if onload event has fired for safe history api usage
var onloadcheck = "window.onload = function () { window._onload_event_fired; }";

var inline = [
    analytics,
    ie8compat,
    onloadcheck
].join('\n');

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
            session: null,
            user_actions: user_actions
        };
    },

    render: function() {
        console.log('render app');
        var content;
        var context = this.props.context;
        var hash = url.parse(this.props.href).hash || '';
        var name;
        var key;
        if (hash.slice(0, 2) === '#!') {
            name = hash.slice(2);
        }
        if (context) {
            var ContentView = globals.content_views.lookup(context, name);
            content = this.transferPropsTo(ContentView({
                personaReady: this.state.personaReady,
                session: this.state.session,
                portal: this.state.portal,
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
        };

        var title = globals.listing_titles.lookup(context)({context: context});
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
                    <link rel="stylesheet" href="/static/css/style.css" />
                    <link rel="stylesheet" href="/static/css/responsive.css" />
                    <script dangerouslySetInnerHTML={{__html: inline}}></script>
                    <script src="//www.google-analytics.com/analytics.js" async defer></script>
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
                                        personaReady={this.state.personaReady} />
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
