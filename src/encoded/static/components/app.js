import React from 'react';
import url from 'url';
import jsonScriptEscape from '../libs/jsonScriptEscape';
import globals from './globals';
import DataColors from './datacolors';
import Navigation from './navigation';
import Footer from './footer';
import Home from './home';
import { NewsHead } from './page';

const portal = {
    portal_title: 'ENCODE',
    global_sections: [
        {
            id: 'data',
            title: 'Data',
            children: [
                { id: 'assaymatrix', title: 'Matrix', url: '/matrix/?type=Experiment' },
                { id: 'assaysearch', title: 'Search', url: '/search/?type=Experiment' },
                { id: 'region-search', title: 'Search by region', url: '/region-search/' },
                { id: 'reference-epigenomes', title: 'Reference epigenomes', url: '/search/?type=ReferenceEpigenome' },
                { id: 'publications', title: 'Publications', url: '/publications/' },
            ],
        },
        {
            id: 'encyclopedia',
            title: 'Encyclopedia',
            children: [
                { id: 'aboutannotations', title: 'About', url: '/data/annotations/' },
                { id: 'annotationmatrix', title: 'Matrix', url: '/matrix/?type=Annotation&encyclopedia_version=3' },
                { id: 'annotationsearch', title: 'Search', url: '/search/?type=Annotation&encyclopedia_version=3' },
            ],
        },
        {
            id: 'materialsmethods',
            title: 'Materials & Methods',
            children: [
                { id: 'antibodies', title: 'Antibodies', url: '/search/?type=AntibodyLot' },
                { id: 'biosamples', title: 'Biosamples', url: '/search/?type=Biosample' },
                { id: 'references', title: 'Genome references', url: '/data-standards/reference-sequences/' },
                { id: 'sep-mm-1' },
                { id: 'datastandards', title: 'Standards and guidelines', url: '/data-standards/' },
                { id: 'ontologies', title: 'Ontologies', url: '/help/getting-started/#Ontologies' },
                { id: 'fileformats', title: 'File formats', url: '/help/file-formats/' },
                { id: 'softwaretools', title: 'Software tools', url: '/software/' },
                { id: 'pipelines', title: 'Pipelines', url: '/pipelines/' },
                { id: 'datause', title: 'Release policy', url: '/about/data-use-policy/' },
                { id: 'dataaccess', title: 'Data access', url: '/about/data-access/' },
            ],
        },
        {
            id: 'help',
            title: 'Help',
            children: [
                { id: 'gettingstarted', title: 'Getting started', url: '/help/getting-started/' },
                { id: 'restapi', title: 'REST API', url: '/help/rest-api/' },
                { id: 'projectoverview', title: 'Project overview', url: '/about/contributors/' },
                { id: 'tutorials', title: 'Tutorials', url: '/tutorials/' },
                { id: 'news', title: 'News', url: '/search/?type=Page&news=true&status=released' },
                { id: 'acknowledgements', title: 'Acknowledgements', url: '/acknowledgements/' },
                { id: 'contact', title: 'Contact', url: '/help/contacts/' },
            ],
        },
    ],
};


// Keep lists of currently known project and biosample_type. As new project and biosample_type
// enter the system, these lists must be updated. Used mostly to keep chart and matrix colors
// consistent.
const projectList = [
    'ENCODE',
    'Roadmap',
    'modENCODE',
    'modERN',
    'GGR',
];
const biosampleTypeList = [
    'immortalized cell line',
    'tissue',
    'primary cell',
    'whole organisms',
    'stem cell',
    'in vitro differentiated cells',
    'induced pluripotent stem cell line',
];


// See https://github.com/facebook/react/issues/2323 for an IE8 fix removed for Redmine #4755.
const Title = props => <title {...props}>{props.children}</title>;

Title.propTypes = {
    children: React.PropTypes.node.isRequired,
};


// App is the root component, mounted on document.body.
// It lives for the entire duration the page is loaded.
// App maintains state for the
export default class App extends React.Component {
    constructor(props) {
        super();
        this.state = {
            href: '',
            slow: false,
            errors: [],
            assayTermNameColors: null,
            dropdownComponent: undefined,
            context: props.context,
            session: null,
            session_properties: {},
            session_cookie: '',
        };

        // Bind this to non-React methods.
        this.listActionsFor = this.listActionsFor.bind(this);
        this.currentResource = this.currentResource.bind(this);
        this.currentAction = this.currentAction.bind(this);
    }

    // Data for child components to subscrie to.
    getChildContext() {
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
    }

    listActionsFor(category) {
        if (category === 'context') {
            let context = this.currentResource();
            const name = this.currentAction();
            const contextActions = [];
            Array.prototype.push.apply(contextActions, context.actions || []);
            if (!name && context.default_page) {
                context = context.default_page;
                const actions = context.actions || [];
                for (let i = 0; i < actions.length; i += 1) {
                    const action = actions[i];
                    if (action.href[0] === '#') {
                        action.href = context['@id'] + action.href;
                    }
                    contextActions.push(action);
                }
            }
            return contextActions;
        }
        if (category === 'user') {
            return this.state.session_properties.user_actions || [];
        }
        if (category === 'global_sections') {
            return portal.global_sections;
        }
        return null;
    }

    currentResource() {
        return this.state.context;
    }

    currentAction() {
        const hrefUrl = url.parse(this.state.href);
        const hash = hrefUrl.hash || '';
        let name = '';
        if (hash.slice(0, 2) === '#!') {
            name = hash.slice(2);
        }
        return name;
    }

    render() {
        console.log('render app');
        let content;
        let containerClass;
        let context = this.state.context;
        const hrefUrl = url.parse(this.state.href);
        // Switching between collections may leave component in place
        const key = context && context['@id'] && context['@id'].split('?')[0];
        const currentAction = this.currentAction();
        const isHomePage = context.default_page && context.default_page.name === 'homepage' && (!hrefUrl.hash || hrefUrl.hash === '#logged-out');
        if (isHomePage) {
            context = context.default_page;
            content = <Home context={context} />;
            containerClass = 'container-homepage';
        } else {
            if (!currentAction && context.default_page) {
                context = context.default_page;
            }
            if (context) {
                const ContentView = globals.content_views.lookup(context, currentAction);
                content = <ContentView context={context} />;
                containerClass = 'container';
            }
        }
        const errors = this.state.errors.map(() => <div className="alert alert-error" />);

        let appClass = 'done';
        if (this.state.slow) {
            appClass = 'communicating';
        }

        let title = context.title || context.name || context.accession || context['@id'];
        if (title && title !== 'Home') {
            title = `${title} – ${portal.portal_title}`;
        } else {
            title = portal.portal_title;
        }

        let canonical = this.state.href;
        if (context.canonical_uri) {
            if (hrefUrl.host) {
                canonical = `${hrefUrl.protocol || ''}//${hrefUrl.host + context.canonical_uri}`;
            } else {
                canonical = context.canonical_uri;
            }
        }

        // Google does not update the content of 301 redirected pages
        let base;
        if (({ 'http://www.encodeproject.org/': 1, 'http://encodeproject.org/': 1 })[canonical]) {
            base = 'https://www.encodeproject.org/';
            canonical = base;
            this.historyEnabled = false;
        }

        return (
            <html lang="en">
                <head>
                    <meta charSet="utf-8" />
                    <meta httpEquiv="X-UA-Compatible" content="IE=edge" />
                    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                    <Title>{title}</Title>
                    {base ? <base href={base} /> : null}
                    <link rel="canonical" href={canonical} />
                    <script async src="://www.google-analytics.com/analytics.js" />
                    <script data-prop-name="inline" dangerouslySetInnerHTML={{ __html: this.props.inline }} />
                    <link rel="stylesheet" href={this.props.styles} />
                    {NewsHead(this.props, `${hrefUrl.protocol}//${hrefUrl.host}`)}
                </head>
                <body onClick={this.handleClick} onSubmit={this.handleSubmit}>
                    <script
                        data-prop-name="context"
                        type="application/ld+json"
                        dangerouslySetInnerHTML={{
                            __html: `\n\n'${jsonScriptEscape(JSON.stringify(this.state.context))}\n\n`,
                        }}
                    />
                    <div id="slot-application">
                        <div id="application" className={appClass}>

                        <div className="loading-spinner" />

                            <div id="layout">
                                <Navigation isHomePage={isHomePage} />
                                <div id="content" className={containerClass} key={key}>
                                    {content}
                                </div>
                                {errors}
                                <div id="layout-footer" />
                            </div>
                            <Footer version={this.props.context.app_version} />
                        </div>
                    </div>
                </body>
            </html>
        );
    }
}

App.propTypes = {
    styles: React.PropTypes.string.isRequired,
    inline: React.PropTypes.string.isRequired,
    context: React.PropTypes.object.isRequired,
};

App.childContextTypes = {
    dropdownComponent: React.PropTypes.string,
    listActionsFor: React.PropTypes.func,
    currentResource: React.PropTypes.func,
    location_href: React.PropTypes.string,
    portal: React.PropTypes.object,
    hidePublicAudits: React.PropTypes.bool,
    projectColors: React.PropTypes.object,
    biosampleTypeColors: React.PropTypes.object,
};
