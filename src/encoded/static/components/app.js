'use strict';
import DataColors from './datacolors';

var React = require('react');
var jsonScriptEscape = require('../libs/jsonScriptEscape');
var globals = require('./globals');
var mixins = require('./mixins');
var Navigation = require('./navigation');
var Footer = require('./footer');
var url = require('url');
var {Home} = require('./home');
var {NewsHead} = require('./page');

var portal = {
    portal_title: 'ENCODE',
    global_sections: [
        {id: 'data', title: 'Data', children: [
            {id: 'assaymatrix', title: 'Matrix', url: '/matrix/?type=Experiment'},
            {id: 'assaysearch', title: 'Search', url: '/search/?type=Experiment'},
            {id: 'region-search', title: 'Search by region', url: '/region-search/'},
            {id: 'reference-epigenomes', title: 'Reference epigenomes', url: '/search/?type=ReferenceEpigenome'},
            {id: 'publications', title: 'Publications', url: '/publications/'}
        ]},
        {id: 'encyclopedia', title: 'Encyclopedia', children: [
            {id: 'aboutannotations', title: 'About', url: '/data/annotations/'},
            {id: 'annotationmatrix', title: 'Matrix', url: '/matrix/?type=Annotation&encyclopedia_version=3'},
            {id: 'annotationsearch', title: 'Search', url: '/search/?type=Annotation&encyclopedia_version=3'}
        ]},
        {id: 'materialsmethods', title: 'Materials & Methods', children: [
            {id: 'antibodies', title: 'Antibodies', url: '/search/?type=AntibodyLot'},
            {id: 'biosamples', title: 'Biosamples', url: '/search/?type=Biosample'},
            {id: 'references', title: 'Genome references', url: '/data-standards/reference-sequences/'},
            {id: 'sep-mm-1'},
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
            {id: 'news', title: 'News', url: '/search/?type=Page&news=true&status=released'},
            {id: 'acknowledgements', title: 'Acknowledgements', url: '/acknowledgements/'},
            {id: 'contact', title: 'Contact', url: '/help/contacts/'}
        ]}
    ]
};


// Keep lists of currently known project and biosample_type. As new project and biosample_type
// enter the system, these lists must be updated. Used mostly to keep chart and matrix colors
// consistent.
const projectList = [
    'ENCODE',
    'Roadmap',
    'modENCODE',
    'modERN',
    'GGR'
];
const biosampleTypeList = [
    'immortalized cell line',
    'tissue',
    'primary cell',
    'whole organisms',
    'stem cell',
    'in vitro differentiated cells',
    'induced pluripotent stem cell line'
];


// See https://github.com/facebook/react/issues/2323 for an IE8 fix removed for Redmine #4755.
var Title = React.createClass({
    render: function() {
        return <title {...this.props}>{this.props.children}</title>;
    },
});


// App is the root component, mounted on document.body.
// It lives for the entire duration the page is loaded.
// App maintains state for the
var App = React.createClass({
    mixins: [mixins.Auth0, mixins.HistoryAndTriggers],
    triggers: {
        login: 'triggerLogin',
        profile: 'triggerProfile',
        logout: 'triggerLogout'
    },

    getInitialState: function() {
        return {
            context: this.props.context,
            slow: this.props.slow,
            href: this.props.href,
            errors: [],
            assayTermNameColors: null,
            dropdownComponent: undefined
        };
    },

    // Dropdown context using React context mechanism.
    childContextTypes: {
        dropdownComponent: React.PropTypes.string,
        listActionsFor: React.PropTypes.func,
        currentResource: React.PropTypes.func,
        location_href: React.PropTypes.string,
        portal: React.PropTypes.object,
        hidePublicAudits: React.PropTypes.bool,
        projectColors: React.PropTypes.object,
        biosampleTypeColors: React.PropTypes.object,
    },

    // Retrieve current React context
    getChildContext: function() {
        // Make `project` and `biosample_type` color mappings for downstream modules to use.
        const projectColors = new DataColors(projectList);
        const biosampleTypeColors = new DataColors(biosampleTypeList);

        return {
            dropdownComponent: this.state.dropdownComponent, // ID of component with visible dropdown
            listActionsFor: this.listActionsFor,
            currentResource: this.currentResource,
            location_href: this.state.href,
            portal: portal,
            hidePublicAudits: false, // True if audits should be hidden on the UI while logged out
            projectColors: projectColors,
            biosampleTypeColors: biosampleTypeColors,
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
        return this.state.context;
    },

    currentAction: function() {
        var href_url = url.parse(this.state.href);
        var hash = href_url.hash || '';
        var name;
        if (hash.slice(0, 2) === '#!') {
            name = hash.slice(2);
        }
        return name;
    },

    render: function() {
        console.log('render app');
        var content, containerClass;
        var context = this.state.context;
        var href_url = url.parse(this.state.href);
        // Switching between collections may leave component in place
        var key = context && context['@id'] && context['@id'].split('?')[0];
        var current_action = this.currentAction();
        var isHomePage = context.default_page && context.default_page.name === 'homepage' && (!href_url.hash || href_url.hash === '#logged-out');
        if (isHomePage) {
            context = context.default_page;
            content = <Home context={context} />;
            containerClass = 'container-homepage';
        } else {
            if (!current_action && context.default_page) {
                context = context.default_page;
            }
            if (context) {
                var ContentView = globals.content_views.lookup(context, current_action);
                content = <ContentView context={context} />;
                containerClass = 'container';
            }
        }
        var errors = this.state.errors.map(function (error) {
            return <div className="alert alert-error"></div>;
        });

        var appClass = 'done';
        if (this.state.slow) {
            appClass = 'communicating';
        }

        var title = context.title || context.name || context.accession || context['@id'];
        if (title && title != 'Home') {
            title = title + ' – ' + portal.portal_title;
        } else {
            title = portal.portal_title;
        }

        var canonical = this.state.href;
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
                    <link rel="stylesheet" href={this.props.styles} />
                    {NewsHead(this.props, href_url.protocol + '//' + href_url.host)}
                </head>
                <body onClick={this.handleClick} onSubmit={this.handleSubmit}>
                    <script data-prop-name="context" type="application/ld+json" dangerouslySetInnerHTML={{
                        __html: '\n\n' + jsonScriptEscape(JSON.stringify(this.state.context)) + '\n\n'
                    }}></script>
                    <div id="slot-application">
                        <div id="application" className={appClass}>

                        <div className="loading-spinner"></div>

                            <div id="layout">
                                <Navigation isHomePage={isHomePage} />
                                <div id="content" className={containerClass} key={key}>
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
            props.styles = document.querySelector('link[rel="stylesheet"]').getAttribute('href');
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
