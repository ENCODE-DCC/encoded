import React from 'react';
import cookie from 'cookie-monster';
import Lock from 'auth0-lock';
import _ from 'underscore';
import url from 'url';
import jsonScriptEscape from '../libs/jsonScriptEscape';
import globals from './globals';
import DataColors from './datacolors';
import Navigation from './navigation';
import Footer from './footer';
import Home from './home';
import { newsHead } from './page';

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


function parseError(response) {
    if (response instanceof Error) {
        return Promise.resolve({
            status: 'error',
            title: response.message,
            '@type': ['AjaxError', 'Error'],
        });
    }
    let contentType = response.headers.get('Content-Type') || '';
    contentType = contentType.split(';')[0];
    if (contentType === 'application/json') {
        return response.json();
    }
    return Promise.resolve({
        status: 'error',
        title: response.statusText,
        code: response.status,
        '@type': ['AjaxError', 'Error'],
    });
}


// Get the current browser cookie from the DOM.
function extractSessionCookie() {
    return cookie(document).get('session');
}


// Extract the current session information from the current browser cookie.
function parseSessionCookie(sessionCookie) {
    const buffer = require('buffer').Buffer;
    let session;
    if (sessionCookie) {
        // URL-safe base64
        const mutatedSessionCookie = sessionCookie.replace(/-/g, '+').replace(/_/g, '/');
        // First 64 chars is the sha-512 server signature
        // Payload is [accessed, created, data]
        try {
            session = JSON.parse(buffer(mutatedSessionCookie, 'base64').slice(64).toString())[2];
        } catch (e) {
            console.warn('session parse err %o', session);
        }
    }
    return session || {};
}


// App is the root component, mounted on document.body.
// It lives for the entire duration the page is loaded.
// App maintains state for the
export default class App extends React.Component {
    constructor(props) {
        super();
        this.state = {
            href: '', // Current URL bar
            slow: false, // `true` if we expect response from server, but it seems slow
            errors: [],
            assayTermNameColors: null,
            context: props.context,
            session: null,
            session_properties: {},
            session_cookie: '',
        };

        this.triggers = {
            login: 'triggerLogin',
            profile: 'triggerProfile',
            logout: 'triggerLogout',
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
            listActionsFor: this.listActionsFor,
            currentResource: this.currentResource,
            location_href: this.state.href,
            portal: portal,
            projectColors: projectColors,
            biosampleTypeColors: biosampleTypeColors,
        };
    }

    /* eslint new-cap: ["error", { "properties": false }] */
    componentDidMount() {
        // Login / logout actions must be deferred until Auth0 is ready.
        const sessionCookie = extractSessionCookie();
        const session = parseSessionCookie(sessionCookie);
        if (session['auth.userid']) {
            this.fetchSessionProperties();
        }
        this.setState({
            href: window.location.href,
            session_cookie: sessionCookie,
        });

        // Make a URL for the logo.
        const hrefInfo = url.parse(this.props.href);
        const logoHrefInfo = {
            hostname: hrefInfo.hostname,
            port: hrefInfo.port,
            protocol: hrefInfo.protocol,
            pathname: '/static/img/encode-logo-small-2x.png',
        };
        const logoUrl = url.format(logoHrefInfo);

        this.lock = new Lock.default('WIOr638GdDdEGPJmABPhVzMn6SYUIdIH', 'encode.auth0.com', {
            auth: {
                redirect: false,
            },
            theme: {
                logo: logoUrl,
            },
            socialButtonStyle: 'big',
            languageDictionary: {
                title: 'Log in to ENCODE',
            },
            allowedConnections: ['github', 'google-oauth2', 'facebook', 'linkedin'],
        });
        this.lock.on('authenticated', this.handleAuth0Login);
    }

    componentWillUpdate(nextProps, nextState) {
        if (!this.state.session || (this.state.session_cookie !== nextState.session_cookie)) {
            const updateState = {};
            updateState.session = parseSessionCookie(nextState.session_cookie);
            if (!updateState.session['auth.userid']) {
                updateState.session_properties = {};
            } else if (updateState.session['auth.userid'] !== (this.state.session && this.state.session['auth.userid'])) {
                this.fetchSessionProperties();
            }
            this.setState(updateState);
        }
    }

    componentDidUpdate(prevProps, prevState) {
        if (this.props) {
            Object.keys(this.props).forEach((propKey) => {
                if (this.props[propKey] !== prevProps[propKey]) {
                    console.log('changed props: %s', propKey);
                }
            });
        }
        if (this.state) {
            Object.keys(this.state).forEach((stateKey) => {
                if (this.state[stateKey] !== prevState[stateKey]) {
                    console.log('changed state: %s', stateKey);
                }
            });
        }
    }

    // Handle http requests to the server, using the given URL and options.
    fetch(uri, options) {
        let reqUri = uri;
        const extendedOptions = _.extend({ credentials: 'same-origin' }, options);
        const httpMethod = extendedOptions.method || 'GET';
        if (!(httpMethod === 'GET' || httpMethod === 'HEAD')) {
            const headers = _.extend({}, extendedOptions.headers);
            extendedOptions.headers = headers;
            const session = this.state.session;
            if (session && session._csrft_) {
                headers['X-CSRF-Token'] = session._csrft_;
            }
        }
        // Strip url fragment.
        const urlHash = reqUri.indexOf('#');
        if (urlHash > -1) {
            reqUri = reqUri.slice(0, urlHash);
        }
        const request = fetch(reqUri, extendedOptions);
        request.xhr_begin = 1 * new Date();
        request.then((response) => {
            request.xhr_end = 1 * new Date();
            const statsHeader = response.headers.get('X-Stats') || '';
            request.server_stats = require('querystring').parse(statsHeader);
            request.etag = response.headers.get('ETag');
            const sessionCookie = extractSessionCookie();
            this.setState({ session_cookie: sessionCookie });
        });
        return request;
    }

    fetchSessionProperties() {
        if (this.sessionPropertiesRequest) {
            return;
        }
        this.sessionPropertiesRequest = true;
        this.fetch('/session-properties', {
            headers: { Accept: 'application/json' },
        }).then((response) => {
            this.sessionPropertiesRequest = null;
            if (!response.ok) {
                throw response;
            }
            return response.json();
        }).then((sessionProperties) => {
            this.setState({ session_properties: sessionProperties });
        });
    }

    handleAuth0Login(authResult, retrying) {
        const accessToken = authResult.accessToken;
        if (!accessToken) {
            return;
        }
        this.sessionPropertiesRequest = true;
        this.fetch('/login', {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ accessToken: accessToken }),
        }).then((response) => {
            this.lock.hide();
            if (!response.ok) {
                throw response;
            }
            return response.json();
        }).then((sessionProperties) => {
            this.setState({ session_properties: sessionProperties });
            this.sessionPropertiesRequest = null;
            let nextUrl = window.location.href;
            if (window.location.hash === '#logged-out') {
                nextUrl = window.location.pathname + window.location.search;
            }
            this.navigate(nextUrl, { replace: true });
        }, (err) => {
            this.sessionPropertiesRequest = null;
            parseError(err).then((data) => {
                // Server session creds might have changed.
                if (data.code === 400 && data.detail.indexOf('CSRF') !== -1) {
                    if (!retrying) {
                        window.setTimeout(this.handleAuth0Login.bind(this, accessToken, true));
                        return;
                    }
                }
                // If there is an error, show the error messages
                this.setState({ context: data });
            });
        });
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
                    {newsHead(this.props, `${hrefUrl.protocol}//${hrefUrl.host}`)}
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
    href: React.PropTypes.string.isRequired,
    styles: React.PropTypes.string.isRequired,
    inline: React.PropTypes.string.isRequired,
    context: React.PropTypes.object.isRequired,
};

App.childContextTypes = {
    listActionsFor: React.PropTypes.func,
    currentResource: React.PropTypes.func,
    location_href: React.PropTypes.string,
    portal: React.PropTypes.object,
    projectColors: React.PropTypes.object,
    biosampleTypeColors: React.PropTypes.object,
};
