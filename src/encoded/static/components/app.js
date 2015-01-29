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
        {id: 'data', title: 'Data', children: [
            {id: 'assays', title: 'Assays', url: '/search/?type=experiment'},
            {id: 'biosamples', title: 'Biosamples', url: '/search/?type=biosample'},
            {id: 'antibodies', title: 'Antibodies', url: '/search/?type=antibody_lot'},
            {id: 'annotations', title: 'Annotations', url: '/data/annotations'},
            {id: 'datarelease', title: 'Release policy', url: '/about/data-use-policy'}
        ]},
        {id: 'methods', title: 'Methods', children: [
            {id: 'datastandards', title: 'Data standards', url: '/data-standards'},
            {id: 'softwaretools', title: 'Software tools', url: '/software'},
            {id: 'experimentguides', title: 'Experiment guidelines', url: '/about/experiment-guidelines'}
        ]},
        {id: 'about', title: 'About ENCODE', children: [
            {id: 'projectoverview', title: 'Project overview', url: '/about/contributors'},
            {id: 'news', title: 'News', url: '/news'},
            {id: 'publications', title: 'Publications', url: '/publications'},
            {id: 'datause', title: 'Release policy', url: '/about/data-use-policy'},
            {id: 'dataaccess', title: 'Data access', url: '/about/data-access'}
        ]},
        {id: 'help', title: 'Help', children: [
            {id: 'gettingstarted', title: 'Getting started', url: '/help/getting-started'},
            {id: 'restapi', title: 'REST API', url: '/help/rest-api'},
            {id: 'fileformats', title: 'File formats', url: '/help/file-formats'},
            {id: 'tutorials', title: 'Tutorials', url: '/tutorials'},
            {id: 'contact', title: 'Contact', url: '/help/contacts'}
        ]}
    ]
};


var user_actions = [
    {id: 'signout', title: 'Sign out', trigger: 'logout'}
];

// See https://github.com/facebook/react/issues/2323
var Title = React.createClass({
    render: function() {
        return this.transferPropsTo(<title>{this.props.children}</title>);
    },
    componentDidMount: function() {
        var node = document.querySelector('title');
        if (node && !node.getAttribute('data-reactid')) {
            node.setAttribute('data-reactid', this._rootNodeID);
        }
    }
});


// App is the root component, mounted on document.body.
// It lives for the entire duration the page is loaded.
// App maintains state for the
var App = React.createClass({
    mixins: [mixins.Persona, mixins.HistoryAndTriggers],
    triggers: {
        login: 'triggerLogin',
        logout: 'triggerLogout',
    },

    getInitialState: function() {
        return {
            errors: [],
            portal: portal,
            user_actions: user_actions,
            dropdownComponent: undefined
        };
    },

    // Dropdown context using React context mechanism.
    childContextTypes: {
        dropdownComponent: React.PropTypes.string,
        onDropdownChange: React.PropTypes.func
    },

    // Retrieve current React context
    getChildContext: function() {
        return {
            dropdownComponent: this.state.dropdownComponent, // ID of component with visible dropdown
            onDropdownChange: this.handleDropdownChange // Function to process dropdown state change
        };
    },

    // When current dropdown changes; componentID is _rootNodeID of newly dropped-down component
    handleDropdownChange: function(componentID) {
        // Use React _rootNodeID to uniquely identify a dropdown menu;
        // It's passed in as componentID
        this.setState({dropdownComponent: componentID});
    },

    // Handle a click outside a dropdown menu by clearing currently dropped down menu
    handleLayoutClick: function(e) {
        if (this.state.dropdownComponent !== undefined) {
            this.setState({dropdownComponent: undefined});
        }
    },

    // If ESC pressed while drop-down menu open, close the menu
    handleKey: function(e) {
        if (e.which === 27 && this.state.dropdownComponent !== undefined) {
            e.preventDefault();
            this.handleDropdownChange(undefined);
        }
    },

    // Once the app component is mounted, bind keydowns to handleKey function
    componentDidMount: function() {
        globals.bindEvent(window, 'keydown', this.handleKey);
    },

    render: function() {
        console.log('render app');
        var content;
        var context = this.props.context;
        var href_url = url.parse(this.props.href);
        var hash = href_url.hash || '';
        var name;
        var context_actions = [];
        if (hash.slice(0, 2) === '#!') {
            name = hash.slice(2);
        }
        // Switching between collections may leave component in place
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
            content = this.transferPropsTo(ContentView({
                context: context,
                loadingComplete: this.state.loadingComplete,
                session: this.state.session,
                portal: this.state.portal,
                navigate: this.navigate
            }));
        }
        var errors = this.state.errors.map(function (error) {
            return <div className="alert alert-error"></div>;
        });

        var appClass = 'done';
        if (this.props.slow) {
            appClass = 'communicating'; 
        }

        var title = context.title || context.name || context.accession || context['@id'];
        if (title && title != 'Home') {
            title = title + ' – ' + portal.portal_title;
        } else {
            title = portal.portal_title;
        }

        var canonical = this.props.href;
        if (context.canonical_uri) {
            if (href_url.host) {
                canonical = (href_url.protocol || '') + '//' + href_url.host + context.canonical_uri;
            } else {
                canonical = context.canonical_uri;
            }
        }

        // Google does not update the content of 301 redirected pages
        var base;
        if (({'http://www.encodeproject.org/': 1, 'http://encodeproject.org/': 1})[canonical]) {
            base = canonical = 'https://www.encodeproject.org/';
            this.historyEnabled = false;
        }

        return (
            <html lang="en">
                <head>
                    <meta charSet="utf-8" />
                    <meta httpEquiv="X-UA-Compatible" content="IE=edge" />
                    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                    <Title>{title}</Title>
                    {base ? <base href={base}/> : null}
                    <link rel="canonical" href={canonical} />
                    <script async src='//www.google-analytics.com/analytics.js'></script>
                    <script data-prop-name="inline" dangerouslySetInnerHTML={{__html: this.props.inline}}></script>
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

                            <div id="layout" onClick={this.handleLayoutClick} onKeyPress={this.handleKey}>
                                <NavBar href={this.props.href} portal={this.state.portal}
                                        context_actions={context_actions}
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
    },

    statics: {
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

module.exports = App;
