'use strict';
var React = require('react');
var jsonScriptEscape = require('../libs/jsonScriptEscape');
var globals = require('./globals');
var mixins = require('./mixins');
var Navigation = require('./navigation');
var Footer = require('./footer');
var url = require('url');
var Home = require('./home').Home;

var portal = {
    portal_title: 'ENCODE',
    global_sections: [
        {id: 'data', title: 'Data', children: [
            {id: 'assaymatrix', title: 'Matrix', url: '/matrix/?type=Experiment'},
            {id: 'assaysearch', title: 'Search', url: '/search/?type=Experiment'},
            {id: 'region-search', title: 'Search by region', url: '/region-search/'},
            {id: 'publications', title: 'Publications', url: '/publications/'}
        ]},
        {id: 'encyclopedia', title: 'Encyclopedia', children: [
            {id: 'aboutannotations', title: 'About', url: '/data/annotations/'},
            {id: 'annotationmatrix', title: 'Matrix', url: '/matrix/?type=Annotation'},
            {id: 'annotationsearch', title: 'Search', url: '/search/?type=Annotation'}
        ]},
        {id: 'materialsmethods', title: 'Materials & Methods', children: [
            {id: 'antibodies', title: 'Antibodies', url: '/search/?type=AntibodyLot'},
            {id: 'biosamples', title: 'Biosamples', url: '/search/?type=Biosample'},
            {id: 'datastandards', title: 'Standards and guidelines', url: '/data-standards/'},
            {id: 'ontologies', title: 'Ontologies', url: '/help/getting-started/#Ontologies'},
            {id: 'fileformats', title: 'File formats', url: '/help/file-formats/'},
            {id: 'softwaretools', title: 'Software tools', url: '/software/'},
            {id: 'pipelines', title: 'Pipelines', url: '/pipelines/'},
            {id: 'datause', title: 'Release policy', url: '/about/data-use-policy/'},
            {id: 'dataaccess', title: 'Data access', url: '/about/data-access/'}
        ]},
        {id: 'help', title: 'Help', children: [
            {id: 'gettingstarted', title: 'Getting started', url: '/help/getting-started/'},
            {id: 'restapi', title: 'REST API', url: '/help/rest-api/'},
            {id: 'projectoverview', title: 'Project overview', url: '/about/contributors/'},
            {id: 'tutorials', title: 'Tutorials', url: '/tutorials/'},
            {id: 'news', title: 'News', url: '/news'},
            {id: 'acknowledgements', title: 'Acknowledgements', url: '/acknowledgements/'},
            {id: 'contact', title: 'Contact', url: '/help/contacts/'}
        ]}
    ]
};


// See https://github.com/facebook/react/issues/2323
var Title = React.createClass({
    render: function() {
        return <title {...this.props}>{this.props.children}</title>;
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
        profile: 'triggerProfile',
        logout: 'triggerLogout'
    },

    getInitialState: function() {
        return {
            errors: [],
            dropdownComponent: undefined
        };
    },

    // Dropdown context using React context mechanism.
    childContextTypes: {
        dropdownComponent: React.PropTypes.string,
        listActionsFor: React.PropTypes.func,
        currentResource: React.PropTypes.func,
        location_href: React.PropTypes.string,
        onDropdownChange: React.PropTypes.func,
        portal: React.PropTypes.object,
        hidePublicAudits: React.PropTypes.bool
    },

    // Retrieve current React context
    getChildContext: function() {
        return {
            dropdownComponent: this.state.dropdownComponent, // ID of component with visible dropdown
            listActionsFor: this.listActionsFor,
            currentResource: this.currentResource,
            location_href: this.props.href,
            onDropdownChange: this.handleDropdownChange, // Function to process dropdown state change
            portal: portal,
            hidePublicAudits: true // True if audits should be hidden on the UI while logged out
        };
    },

    listActionsFor: function(category) {
        if (category === 'context') {
            var context = this.currentResource();
            var name = this.currentAction();
            var context_actions = [];
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
            return context_actions;
        }
        if (category === 'user') {
            return this.state.session_properties.user_actions || [];
        }
        if (category === 'global_sections') {
            return portal.global_sections;
        }
    },

    currentResource: function() {
        return this.props.context;
    },

    currentAction: function() {
        var href_url = url.parse(this.props.href);
        var hash = href_url.hash || '';
        var name;
        if (hash.slice(0, 2) === '#!') {
            name = hash.slice(2);
        }
        return name;
    },

    // When current dropdown changes; componentID is _rootNodeID of newly dropped-down component
    handleDropdownChange: function(componentID) {
        // Use React _rootNodeID to uniquely identify a dropdown menu;
        // It's passed in as componentID
        this.setState({dropdownComponent: componentID});
    },

    handleAutocompleteChosenChange: function(chosen) {
        this.setState({autocompleteTermChosen: chosen});
    },

    handleAutocompleteFocusChange: function(focused) {
        this.setState({autocompleteFocused: focused});
    },

    handleAutocompleteHiddenChange: function(hidden) {
        this.setState({autocompleteHidden: hidden});
    },

    // Handle a click outside a dropdown menu by clearing currently dropped down menu
    handleLayoutClick: function(e) {
        if (this.state.dropdownComponent !== undefined) {
            this.setState({dropdownComponent: undefined});
        }
    },

    // If ESC pressed while drop-down menu open, close the menu
    handleKey: function(e) {
        if (e.which === 27) {
            if (this.state.dropdownComponent !== undefined) {
                e.preventDefault();
                this.handleDropdownChange(undefined);
            } else if (!this.state.autocompleteHidden) {
                e.preventDefault();
                this.handleAutocompleteHiddenChange(true);
            }
        } else if (e.which === 13 && this.state.autocompleteFocused && !this.state.autocompleteTermChosen) {
            e.preventDefault();
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
        // Switching between collections may leave component in place
        var key = context && context['@id'] && context['@id'].split('?')[0];
        var current_action = this.currentAction();
        if (!current_action && context.default_page) {
            context = context.default_page;
            content = <Home context={context} />;
        } else if (context) {
            var ContentView = globals.content_views.lookup(context, current_action);
            content = <ContentView context={context} />;
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
                </head>
                <body onClick={this.handleClick} onSubmit={this.handleSubmit}>
                    <script data-prop-name="context" type="application/ld+json" dangerouslySetInnerHTML={{
                        __html: '\n\n' + jsonScriptEscape(JSON.stringify(this.props.context)) + '\n\n'
                    }}></script>
                    <div id="slot-application">
                        <div id="application" className={appClass}>

                        <div className="loading-spinner"></div>

                            <div id="layout" onClick={this.handleLayoutClick} onKeyPress={this.handleKey}>
                                <Navigation />
                                <div id="content" className="container" key={key}>
                                    {content}
                                </div>
                                {errors}
                                <div id="layout-footer"></div>
                            </div>
                            <Footer version={this.props.context.app_version} />
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
            props.href = document.querySelector('link[rel="canonical"]').getAttribute('href');
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
