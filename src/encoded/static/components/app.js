import React from 'react';
import PropTypes from 'prop-types';
import Auth0Lock from 'auth0-lock';
import serialize from 'form-serialize';
import ga from 'google-analytics';
import { Provider } from 'react-redux';
import _ from 'underscore';
import url from 'url';
import * as cookie from 'js-cookie';
import jsonScriptEscape from '../libs/jsonScriptEscape';
import origin from '../libs/origin';
import { BrowserFeat } from './browserfeat';
import cartStore, {
    CartAlert,
    cartCacheSaved,
    cartSetOperationInProgress,
    cartGetSettings,
    cartSetSettingsCurrent,
    cartSetCurrent,
    cartSwitch,
} from './cart';
import * as globals from './globals';
import Navigation from './navigation';
import Footer from './footer';
import Home from './home';
import jsonldFormatter from '../libs/jsonld';
import newsHead from './page';
import {
    Modal,
    ModalHeader,
    ModalBody,
    ModalFooter,
} from '../libs/ui/modal';


const portal = {
    portal_title: 'ENCODE',
    global_sections: [
        {
            id: 'data',
            title: 'Data',
            children: [
                { id: 'functional-genomics', title: 'Functional Genomics data' },
                { id: 'assaysearch', title: 'Experiment search', url: '/search/?type=Experiment&control_type!=*&status=released&perturbed=false', tag: 'collection' },
                { id: 'assaymatrix', title: 'Experiment matrix', url: '/matrix/?type=Experiment&control_type!=*&status=released&perturbed=false', tag: 'collection' },
                { id: 'chip', title: 'ChIP-seq matrix', url: '/chip-seq-matrix/?type=Experiment&replicates.library.biosample.donor.organism.scientific_name=Homo%20sapiens&assay_title=Histone%20ChIP-seq&assay_title=Mint-ChIP-seq&status=released', tag: 'collection' },
                { id: 'bodymap', title: 'Human body map', url: '/summary/?type=Experiment&replicates.library.biosample.donor.organism.scientific_name=Homo+sapiens', tag: 'collection' },
                { id: 'series', title: 'Functional genomics series', url: '/series-search/?type=OrganismDevelopmentSeries', tag: 'collection' },
                { id: 'single-cell', title: 'Single-cell experiments', url: '/single-cell/?type=Experiment&assay_slims=Single+cell&status!=replaced', tag: 'collection' },
                { id: 'sep-mm-0' },
                { id: 'functional-characterization', title: 'Functional Characterization data' },
                { id: 'functional-char-assays', title: 'High-throughput assays', url: '/search/?type=FunctionalCharacterizationExperiment&control_type!=*&audit.WARNING.category!=lacking+processed+data', tag: 'collection' },
                { id: 'transgenic-enhancer-assays', title: 'In vivo validation assays', url: '/search/?type=TransgenicEnhancerExperiment', tag: 'collection' },
                { id: 'sep-mm-1' },
                { id: 'cloud', title: 'Cloud Resources' },
                { id: 'aws-link', title: 'AWS Open Data', url: 'https://registry.opendata.aws/encode-project/', tag: 'cloud' },
                { id: 'azure-link', title: 'Azure Open Datasets', url: 'https://docs.microsoft.com/en-us/azure/open-datasets/dataset-encode', tag: 'azure' },
                { id: 'sep-mm-2' },
                { id: 'collections', title: 'Collections' },
                { id: 'encore', title: 'RNA-protein interactions (ENCORE)', url: '/encore-matrix/?type=Experiment&status=released&internal_tags=ENCORE', tag: 'collection' },
                { id: 'entex', title: 'Epigenomes from four individuals (ENTEx)', url: '/entex-matrix/?type=Experiment&status=released&internal_tags=ENTEx', tag: 'collection' },
                { id: 'brain', title: 'Rush Alzheimer’s Disease Study', url: '/brain-matrix/?type=Experiment&status=released&internal_tags=RushAD', tag: 'collection' },
                { id: 'sescc', title: 'Stem Cell Development Matrix (SESCC)', url: '/sescc-stem-cell-matrix/?type=Experiment&internal_tags=SESCC', tag: 'collection' },
                { id: 'reference-epigenomes-human', title: 'Human reference epigenomes', url: '/reference-epigenome-matrix/?type=Experiment&related_series.@type=ReferenceEpigenome&replicates.library.biosample.donor.organism.scientific_name=Homo+sapiens', tag: 'collection' },
                { id: 'reference-epigenomes-mouse', title: 'Mouse reference epigenomes', url: '/reference-epigenome-matrix/?type=Experiment&related_series.@type=ReferenceEpigenome&replicates.library.biosample.donor.organism.scientific_name=Mus+musculus', tag: 'collection' },
                { id: 'mouse-development-matrix', title: 'Mouse development matrix', url: '/mouse-development-matrix/?type=Experiment&status=released&related_series.@type=OrganismDevelopmentSeries&replicates.library.biosample.organism.scientific_name=Mus+musculus', tag: 'collection' },
                { id: 'sep-mm-3' },
                { id: 'region-search', title: 'Search by region', url: '/region-search/' },
                { id: 'publications', title: 'Publications', url: '/publications/' },
                { id: 'rna-get', title: 'RNA-Get (gene expression)', url: '/rnaget' },
            ],
        },
        {
            id: 'encyclopedia',
            title: 'Encyclopedia',
            children: [
                { id: 'aboutannotations', title: 'About', url: '/data/annotations/' },
                { id: 'sep-mm-1' },
                { id: 'annotationvisualize', title: 'Visualize (SCREEN)', url: 'https://screen.wenglab.org/' },
                { id: 'annotationmatrix', title: 'Annotation matrix', url: '/matrix/?type=Annotation&encyclopedia_version=current' },
                { id: 'annotationsearch', title: 'Search', url: '/search/?type=Annotation&encyclopedia_version=current' },
                { id: 'annotationmethods', title: 'Methods', url: 'https://screen.wenglab.org/index/about' },
            ],
        },
        {
            id: 'materialsmethods',
            title: 'Materials & Methods',
            children: [
                { id: 'antibodies', title: 'Antibodies', url: '/search/?type=AntibodyLot&status=released' },
                { id: 'references', title: 'Genome references', url: '/data-standards/reference-sequences/' },
                { id: 'sep-mm-1' },
                { id: 'datastandards', title: 'Assays and standards', url: '/data-standards/' },
                { id: 'glossary', title: 'Glossary', url: '/glossary/' },
                { id: 'fileformats', title: 'File formats', url: '/help/file-formats/' },
                { id: 'softwaretools', title: 'Software tools', url: '/encode-software/?type=Software' },
                { id: 'pipelines', title: 'Pipelines', url: '/pipelines/' },
                { id: 'sep-mm-2' },
                { id: 'dataorg', title: 'Data organization', url: '/help/data-organization/' },
                { id: 'datause', title: 'Release policy', url: '/about/data-use-policy/' },
                { id: 'profiles', title: 'Schemas', url: '/profiles/' },
            ],
        },
        {
            id: 'help',
            title: 'Help',
            children: [
                { id: 'gettingstarted', title: 'Using the portal', url: '/help/getting-started/' },
                { id: 'interactivehelp', title: 'Interactive help', url: '/?walkme=19-976547', attr: { 'data-reload': '' } },
                { id: 'cart', title: 'Cart', url: '/help/cart/' },
                { id: 'restapi', title: 'REST API', url: '/help/rest-api/' },
                { id: 'citingencode', title: 'Citing ENCODE', url: '/help/citing-encode' },
                { id: 'faq', title: 'FAQ', url: '/help/faq/' },
                { id: 'sep-mm-1' },
                { id: 'projectoverview', title: 'Project Overview', url: '/help/project-overview/' },
                { id: 'collaborations', title: 'Collaborations', url: '/help/collaborations/' },
                { id: 'sep-mm-2' },
                { id: 'events', title: 'ENCODE workshops', url: '/help/events/' },
                { id: 'contact', title: 'About the DCC', url: '/help/contacts/' },
            ],
        },
    ],
};


// See https://github.com/facebook/react/issues/2323 for an IE8 fix removed for Redmine #4755.
const Title = (props) => <title {...props}>{props.children}</title>;

Title.propTypes = {
    children: PropTypes.node.isRequired,
};


// Get the current browser cookie from the DOM.
function extractSessionCookie() {
    return cookie.get('session');
}


function contentTypeIsJSON(contentType) {
    return (contentType || '').split(';')[0].split('/').pop().split('+').pop() === 'json';
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


function recordServerStats(serverStats, timingVar) {
    // server_stats *_time are microsecond values...
    Object.keys(serverStats).forEach((name) => {
        if (name.indexOf('_time') !== -1) {
            ga('send', 'timing', {
                timingCategory: name,
                timingVar,
                timingValue: Math.round(serverStats[name] / 1000),
            });
        }
    });
}


function recordBrowserStats(browserStats, timingVar) {
    Object.keys(browserStats).forEach((name) => {
        if (name.indexOf('_time') !== -1) {
            ga('send', 'timing', {
                timingCategory: name,
                timingVar,
                timingValue: browserStats[name],
            });
        }
    });
}


class UnsavedChangesToken {
    constructor(manager) {
        this.manager = manager;
    }

    release() {
        this.manager.releaseUnsavedChanges(this);
    }
}


const SLOW_REQUEST_TIME = 250;
class Timeout {
    constructor(timeout) {
        this.promise = new Promise((resolve) => setTimeout(resolve.bind(undefined, this), timeout));
    }
}

const EulaModal = ({ closeModal, signup }) => (
    <Modal>
        <ModalHeader title="Creating a new account" closeModal={closeModal} />
        <ModalBody>
            <p>
                You are about to create an ENCODE account. Please have a look at the <a href="https://www.stanford.edu/site/terms/">terms of service</a> and <a href="https://www.stanford.edu/site/privacy/">privacy policy</a>.
            </p>
        </ModalBody>
        <ModalFooter
            closeModal={closeModal}
            submitBtn={signup}
            submitTitle="Proceed"
        />
    </Modal>
);

EulaModal.propTypes = {
    closeModal: PropTypes.func.isRequired,
    signup: PropTypes.func.isRequired,
};

const AccountCreationFailedModal = ({ closeModal, date }) => (
    <Modal>
        <ModalHeader title="Failed to create a new account." closeModal={closeModal} />
        <ModalBody>
            <p>
                Creating a new account failed. Please contact <a href={`mailto:encode-help@lists.stanford.edu?subject=Creating e-mail account failed&body=Creating an account failed at time: ${date}`}>support</a>.
            </p>
        </ModalBody>
        <ModalFooter
            cancelTitle="Close"
            closeModal={closeModal}
        />
    </Modal>
);

AccountCreationFailedModal.propTypes = {
    closeModal: PropTypes.func.isRequired,
    date: PropTypes.string.isRequired,
};


const AccountCreatedModal = ({ closeModal }) => (
    <Modal>
        <ModalHeader title="Account Created" closeModal={closeModal} />
        <ModalBody>
            <p>
                Welcome! A new user account is now created for you and you are automatically logged in.
            </p>
        </ModalBody>
        <ModalFooter
            closeModal={closeModal}
            cancelTitle="Close"
        />
    </Modal>
);

AccountCreatedModal.propTypes = {
    closeModal: PropTypes.func.isRequired,
};


// Include paths of all pages that require full-page reloads even when navigating within the page.
const fullPageReloadPaths = [
    '/chip-seq-matrix/',
    '/reference-epigenome-matrix/',
    '/single-cell/',
    '/summary/',
];


// App is the root component, mounted on document.body.
// It lives for the entire duration the page is loaded.
// App maintains state for the
class App extends React.Component {
    static historyEnabled() {
        return !!(typeof window !== 'undefined' && window.history && window.history.pushState);
    }

    static scrollTo() {
        const { hash } = window.location;
        if (hash && document.getElementById(hash.slice(1))) {
            window.location.replace(hash);
        } else {
            window.scrollTo(0, 0);
        }
    }

    constructor(props) {
        super();
        this.state = {
            href: props.href, // Current URL bar
            slow: false, // `true` if we expect response from server, but it seems slow
            errors: [],
            assayTermNameColors: null,
            context: props.context,
            session: null,
            session_properties: {},
            session_cookie: '',
            profilesTitles: {},
            contextRequest: null,
            unsavedChanges: [],
            promisePending: false,
            eulaModalVisibility: false,
            accountCreatedModalVisibility: false,
            accountCreationFailedVisibility: false,
            authResult: '',
        };

        this.triggers = {
            login: 'triggerLogin',
            profile: 'triggerProfile',
            logout: 'triggerLogout',
        };

        this.domain = 'encode.auth0.com';
        this.clientId = 'WIOr638GdDdEGPJmABPhVzMn6SYUIdIH';

        // Bind this to non-React methods.
        this.fetch = this.fetch.bind(this);
        this.fetchSessionProperties = this.fetchSessionProperties.bind(this);
        this.fetchProfilesTitles = this.fetchProfilesTitles.bind(this);
        this.handleAuth0Login = this.handleAuth0Login.bind(this);
        this.triggerLogin = this.triggerLogin.bind(this);
        this.triggerLogout = this.triggerLogout.bind(this);
        this.adviseUnsavedChanges = this.adviseUnsavedChanges.bind(this);
        this.releaseUnsavedChanges = this.releaseUnsavedChanges.bind(this);
        this.trigger = this.trigger.bind(this);
        this.handleError = this.handleError.bind(this);
        this.handleClick = this.handleClick.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.handlePopState = this.handlePopState.bind(this);
        this.confirmNavigation = this.confirmNavigation.bind(this);
        this.handleBeforeUnload = this.handleBeforeUnload.bind(this);
        this.navigate = this.navigate.bind(this);
        this.receiveContextResponse = this.receiveContextResponse.bind(this);
        this.listActionsFor = this.listActionsFor.bind(this);
        this.currentResource = this.currentResource.bind(this);
        this.currentAction = this.currentAction.bind(this);
        this.closeSignupModal = this.closeSignupModal.bind(this);
        this.closeAccountCreationErrorModal = this.closeAccountCreationErrorModal.bind(this);
        this.closeAccountCreationNotification = this.closeAccountCreationNotification.bind(this);
        this.signup = this.signup.bind(this);
    }

    // Data for child components to subscribe to.
    getChildContext() {
        return {
            listActionsFor: this.listActionsFor,
            currentResource: this.currentResource,
            location_href: this.state.href,
            portal,
            fetch: this.fetch,
            fetchSessionProperties: this.fetchSessionProperties,
            navigate: this.navigate,
            adviseUnsavedChanges: this.adviseUnsavedChanges,
            session: this.state.session,
            session_properties: this.state.session_properties,
            profilesTitles: this.state.profilesTitles,
            localInstance: url.parse(this.props.href).hostname === 'localhost',
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
        this.fetchProfilesTitles();
        this.setState({
            href: window.location.href,
            session_cookie: sessionCookie,
            session,
        });

        // Set browser features in the <html> CSS class.
        BrowserFeat.setHtmlFeatClass();

        // Make a URL for the logo.
        const hrefInfo = url.parse(this.state.href);
        const logoHrefInfo = {
            hostname: hrefInfo.hostname,
            port: hrefInfo.port,
            protocol: hrefInfo.protocol,
            pathname: '/static/img/encode-logo-small-2x.png',
        };
        const logoUrl = url.format(logoHrefInfo);

        this.lock = new Auth0Lock(this.clientId, this.domain, {
            auth: {
                responseType: 'token',
                redirect: false,
                redirectUrl: `${hrefInfo.protocol}//${hrefInfo.host}/callback`,
            },
            theme: {
                logo: logoUrl,
            },
            socialButtonStyle: 'big',
            languageDictionary: {
                title: 'Log in or Create Account',
            },
            allowedConnections: ['github', 'google-oauth2', 'facebook', 'linkedin'],
        });
        this.lock.on('authenticated', this.handleAuth0Login);

        // Add privacy link to auth0 login modal.
        this.lock.on('signin ready', () => {
            const lockElements = document.getElementsByClassName('auth0-lock-form');
            if (lockElements && lockElements.length > 0) {
                const privacyDiv = document.createElement('div');
                const privacyLink = document.createElement('a');
                const privacyLinkText = document.createTextNode('Privacy policy');
                privacyLink.appendChild(privacyLinkText);
                privacyDiv.className = 'auth0__privacy-notice';
                privacyLink.href = 'https://www.stanford.edu/site/privacy/';
                privacyLink.title = 'View Stanford University privacy policy';
                privacyDiv.appendChild(privacyLink);
                lockElements[0].appendChild(privacyDiv);
            }
        });

        // Initialize browser history mechanism
        if (this.constructor.historyEnabled()) {
            const data = this.props.context;
            try {
                window.history.replaceState(data, '', window.location.href);
            } catch (exc) {
                // Might fail due to too large data
                window.history.replaceState(null, '', window.location.href);
            }

            // If it looks like an anchor target link, scroll to it, plus an offset for the fixed navbar
            // Hints from https://dev.opera.com/articles/fixing-the-scrolltop-bug/
            if (window.location.href) {
                const splitHref = this.state.href.split('#');
                if (splitHref.length >= 2 && splitHref[1][0] !== '!') {
                    // URL has hash tag, but not the '#!edit' type
                    const hashTarget = splitHref[1];
                    const domTarget = document.getElementById(hashTarget);
                    if (domTarget) {
                        // DOM has a matching anchor; scroll to it
                        const elTop = domTarget.getBoundingClientRect().top;
                        const docTop = document.documentElement.scrollTop || document.body.scrollTop;
                        const scrollTop = (elTop + docTop) - (window.innerWidth >= 960 ? 75 : 0);
                        document.documentElement.scrollTop = scrollTop;
                        document.body.scrollTop = scrollTop;
                    }
                }
            }

            // Avoid popState on load, see: http://stackoverflow.com/q/6421769/199100
            const register = window.addEventListener.bind(window, 'popstate', this.handlePopState, true);
            if (window._onload_event_fired) {
                register();
            } else {
                window.addEventListener('load', setTimeout.bind(window, register));
            }
        } else {
            window.onhashchange = this.onHashChange;
        }
        window.onbeforeunload = this.handleBeforeUnload;
    }

    shouldComponentUpdate(nextProps, nextState) {
        if (nextState) {
            return !(_.isEqual(nextState, this.state));
        }
        return false;
    }

    /* eslint-disable react/no-did-update-set-state */
    componentDidUpdate(prevProps, prevState) {
        if (!this.state.session || (this.state.session_cookie !== prevState.session_cookie)) {
            const updateState = {};
            updateState.session = parseSessionCookie(this.state.session_cookie);
            if (!updateState.session['auth.userid']) {
                updateState.session_properties = {};
            } else if (updateState.session['auth.userid'] !== (this.state.session && this.state.session['auth.userid'])) {
                this.fetchSessionProperties();
            }
            this.setState(updateState);
        }

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

        const xhr = this.state.contextRequest;
        if (!xhr || !xhr.xhr_end || xhr.browser_stats) {
            return;
        }
        const browserEnd = 1 * new Date();

        ga('set', 'location', window.location.href);
        ga('send', 'pageview');
        recordServerStats(xhr.server_stats, 'contextRequest');

        xhr.browser_stats = {};
        xhr.browser_stats.xhr_time = xhr.xhr_end - xhr.xhr_begin;
        xhr.browser_stats.browser_time = browserEnd - xhr.xhr_end;
        xhr.browser_stats.total_time = browserEnd - xhr.xhr_begin;
        recordBrowserStats(xhr.browser_stats, 'contextRequest');
    }
    /* eslint-enable react/no-did-update-set-state */

    /**
    * Login with existing user or bring up account-creation modal
    *
    * @param {object} authResult- Authorization information
    * @param {boolean} retrying- Attempt to retry login or not
    * @param {boolean} createAccount- Where or not to attempt to create an account
    * @returns Null
    * @memberof App
    */
    handleAuth0Login(authResult, retrying, createAccount = true) {
        const { accessToken } = authResult;
        if (!accessToken) {
            return;
        }
        this.sessionPropertiesRequest = true;
        this.setState({ authResult });
        this.fetch('/login', {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ accessToken }),
        }).then((response) => {
            this.lock.hide();
            if (!response.ok) {
                throw response;
            }
            return response.json();
        }).then((sessionProperties) => {
            this.setState({ session_properties: sessionProperties });
            this.sessionPropertiesRequest = null;
            return this.initializeCartFromSessionProperties(sessionProperties);
        }).then(() => {
            let nextUrl = window.location.href;
            if (window.location.hash === '#logged-out') {
                nextUrl = window.location.pathname + window.location.search;
            }
            this.navigate(nextUrl, { replace: true });
        }, (err) => {
            if (err.status === 403 && createAccount) {
                this.setState({ eulaModalVisibility: true });
            } else {
                this.sessionPropertiesRequest = null;
                globals.parseError(err).then((data) => {
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
            }
        });
    }

    handleError(msg, uri, line, column) {
        let mutatableUri = uri;

        // When an unhandled exception occurs, reload the page on navigation
        this.constructor.historyEnabled = false;
        const parsed = mutatableUri && require('url').parse(mutatableUri);
        if (mutatableUri && parsed.hostname === window.location.hostname) {
            mutatableUri = parsed.path;
        }
        ga('send', 'exception', {
            exDescription: `${mutatableUri}@${line},${column}: ${msg}`,
            exFatal: true,
            location: window.location.href,
        });
    }

    /* eslint no-script-url: 0 */ // We're not *using* a javascript: link -- just checking them.
    handleClick(event) {
        const options = {};

        // https://github.com/facebook/react/issues/1691
        if (event.isDefaultPrevented()) {
            return;
        }

        let { target } = event;
        const { nativeEvent } = event;

        // SVG anchor elements have tagName == 'a' while HTML anchor elements have tagName == 'A'
        while (
            target
            && (target.tagName.toLowerCase() !== 'a' || target.getAttribute('data-href'))
            && (target.tagName.toLowerCase() !== 'button' || !target.getAttribute('data-trigger'))
        ) {
            target = target.parentElement;
        }
        if (!target) {
            return;
        }

        if (target.getAttribute('disabled')) {
            event.preventDefault();
            return;
        }

        // data-trigger links invoke custom handlers.
        const dataTrigger = target.getAttribute('data-trigger');
        if (dataTrigger !== null) {
            event.preventDefault();
            this.trigger(dataTrigger);
            return;
        }

        // data-noscroll attribute prevents scrolling to the top when clicking a link.
        if (target.getAttribute('data-noscroll') === 'true') {
            options.noscroll = true;
        }

        // data-reload forces a page reload after navigating.
        if (target.getAttribute('data-reload') === 'true') {
            options.reload = true;
        }

        // Ensure this is a plain click
        if (nativeEvent.which > 1 || nativeEvent.shiftKey || nativeEvent.altKey || nativeEvent.metaKey) {
            return;
        }

        // Skip links with a data-bypass attribute.
        if (target.getAttribute('data-bypass')) {
            return;
        }

        let href = target.getAttribute('href');
        if (href === null) {
            href = target.getAttribute('data-href');
        }
        if (href === null) {
            return;
        }

        // Skip javascript links
        if (href.indexOf('javascript:') === 0) {
            return;
        }

        // Skip external links
        if (!origin.same(href)) {
            return;
        }

        // Skip links with a different target
        if (target.getAttribute('target')) {
            return;
        }

        // Skip @@download links
        if (href.indexOf('/@@download') !== -1) {
            return;
        }

        // With HTML5 history supported, local navigation is passed
        // through the navigate method.
        if (this.constructor.historyEnabled) {
            event.preventDefault();
            this.navigate(href, options);
        }
    }

    // Submitted forms are treated the same as links
    handleSubmit(event) {
        const { target } = event;

        // Skip POST forms
        if (target.method !== 'get') {
            return;
        }

        // Skip forms with a data-bypass attribute.
        if (target.getAttribute('data-bypass')) {
            return;
        }

        // Skip external forms
        if (!origin.same(target.action)) {
            return;
        }

        const options = {};
        const actionUrl = url.parse(url.resolve(this.state.href, target.action));
        let search = serialize(target);
        if (target.getAttribute('data-removeempty')) {
            search = search.split('&').filter((item) => item.slice(-1) !== '=').join('&');
        }
        let href = actionUrl.pathname;
        if (search) {
            href += `?${search}`;
        }
        options.skipRequest = target.getAttribute('data-skiprequest');

        if (this.constructor.historyEnabled) {
            event.preventDefault();
            this.navigate(href, options);
        }
    }

    handlePopState(event) {
        if (this.DISABLE_POPSTATE) {
            return;
        }
        if (!this.confirmNavigation()) {
            window.history.pushState(window.state, '', this.state.href);
            return;
        }
        if (!this.constructor.historyEnabled) {
            window.location.reload();
            return;
        }
        const request = this.state.contextRequest;
        const { href } = window.location;
        if (event.state) {
            // Abort inflight xhr before setProps
            if (request && this.requestCurrent) {
                // Abort the current request, then remember we've aborted it so that we don't render
                // the Network Request Error page.
                request.abort();
                this.requestAborted = true;
                this.requestCurrent = false;
            }
            this.setState({
                href, // href should be consistent with context
                context: event.state,
            });
        }
        // Always async update in case of server side changes.
        // Triggers standard analytics handling.
        this.navigate(href, { replace: true });
    }

    handleBeforeUnload() {
        if (this.state.unsavedChanges.length > 0) {
            return 'You have unsaved changes.';
        }
        return undefined;
    }

    onHashChange() {
        // IE8/9
        this.setState({ href: window.location.href });
    }

    // Handle http requests to the server, using the given URL and options.
    fetch(uri, options) {
        let reqUri = uri;
        const extendedOptions = _.extend({ credentials: 'same-origin' }, options);
        const httpMethod = extendedOptions.method || 'GET';
        if (!(httpMethod === 'GET' || httpMethod === 'HEAD')) {
            const headers = _.extend({}, extendedOptions.headers);
            extendedOptions.headers = headers;
            const { session } = this.state;
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
            if (this.state.session_cookie !== sessionCookie) {
                this.setState({ session_cookie: sessionCookie });
            }
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
            return this.initializeCartFromSessionProperties(sessionProperties);
        });
    }

    /**
     * Perform a GET request on the titles of schemas corresponding to an @type, to be placed into
     * <App> context and usable by any component.
     */
    fetchProfilesTitles() {
        this.fetch('/profiles-titles/', {
            headers: { Accept: 'application/json' },
        }).then((response) => {
            if (response.ok) {
                return response.json();
            }
            throw response;
        }).then((profilesTitles) => {
            this.setState({ profilesTitles });
        });
    }

    closeSignupModal() {
        this.setState({ eulaModalVisibility: false });
    }

    closeAccountCreationNotification() {
        this.setState({ accountCreatedModalVisibility: false });
    }

    closeAccountCreationErrorModal() {
        this.setState({ accountCreationFailedVisibility: false });
    }

    signup() {
        const { authResult } = this.state;

        if (!authResult || !authResult.accessToken) {
            console.warn('authResult object or access token not available');
            return;
        }
        const { accessToken } = authResult;
        this.closeSignupModal();
        this.fetch(`${window.location.origin}/users/@@sign-up`, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ accessToken }),
        }).then((response) => {
            if (!response.ok) {
                throw new Error('Failed to create new account');
            }
            this.setState({ accountCreatedModalVisibility: true }); // tell user account was created
            this.handleAuth0Login(authResult, false, false); // sign in after account creation
        }).catch(() => {
            this.setState({ accountCreationFailedVisibility: true });
        });
    }

    triggerLogin() {
        if (this.state.session && !this.state.session._csrft_) {
            this.fetch('/session');
        }
        this.lock.show();
    }

    triggerLogout() {
        const { session } = this.state;
        if (!(session && session['auth.userid'])) return;
        this.fetch('/logout?redirect=false', {
            headers: { Accept: 'application/json' },
        }).then((response) => {
            if (!response.ok) throw response;
            return response.json();
        }).then(() => {
            this.DISABLE_POPSTATE = true;
            const oldPath = window.location.pathname + window.location.search;
            window.location.assign('/#logged-out');
            if (oldPath === '/') {
                window.location.reload();
            }
        }, (err) => {
            globals.parseError(err).then((data) => {
                const newContext = { ...data };
                newContext.title = `Logout failure: ${data.title}`;
                this.setState({ context: newContext });
            });
        });
    }

    adviseUnsavedChanges() {
        const token = new UnsavedChangesToken(this);
        this.setState((state) => ({ unsavedChanges: state.unsavedChanges.concat([token]) }));
        return token;
    }

    releaseUnsavedChanges(token) {
        console.assert(this.state.unsavedChanges.indexOf(token) !== -1);
        this.setState((state) => ({ unsavedChanges: state.unsavedChanges.filter((x) => x !== token) }));
    }

    trigger(name) {
        const methodName = this.triggers[name];
        if (methodName) {
            this[methodName].call(this);
        }
    }

    // Called when the user logs in, or the page loads for a logged-in user. Handle any items
    // collected in the cart while logged out. Retrieve the cart contents for the current logged-
    // in user.
    initializeCartFromSessionProperties(sessionProperties) {
        // Retrieve the logged-in user's carts. If the user has never logged in before, an initial
        // empty cart gets created and returned here.
        cartCacheSaved({}, cartStore.dispatch);
        cartSetOperationInProgress(true, cartStore.dispatch);
        this.fetch('/carts/@@get-cart', {
            method: 'GET',
            headers: {
                Accept: 'application/json',
            },
        }).then((response) => {
            cartSetOperationInProgress(false, cartStore.dispatch);
            if (response.ok) {
                return response.json();
            }
            throw new Error(response);
        }).then((userCarts) => {
            // Retrieve user's current cart @id from cart settings if available in browser
            // localstorage. Set it as the current cart in the cart Redux store.
            let cartSettings = cartGetSettings(sessionProperties.user);
            if (!cartSettings.current || userCarts['@graph'].indexOf(cartSettings.current) === -1) {
                // Cart settings are new -- not from localstorage -- OR the current cart @id
                // doesn't match any of the logged-in user's saved carts. Use the first cart in the
                // user's saved carts as the current and save the new settings to localstorage.
                cartSettings = cartSetSettingsCurrent(sessionProperties.user, userCarts['@graph'][0]);
            }
            cartSetCurrent(cartSettings.current, cartStore.dispatch);

            // With the logged-in user's current cart @id, retrieve the cart object and copy it to
            // the cart Redux store.
            return cartSwitch(cartSettings.current, this.fetch, cartStore.dispatch);
        });
    }

    /* eslint no-alert: 0 */
    confirmNavigation() {
        // check for beforeunload confirmation
        if (this.state.unsavedChanges.length > 0) {
            const res = window.confirm('You have unsaved changes. Are you sure you want to lose them?');
            if (res) {
                this.setState({ unsavedChanges: [] });
            }
            return res;
        }
        return true;
    }

    navigate(href, options) {
        const mutatableOptions = options || {};
        if (!this.confirmNavigation()) {
            return null;
        }

        // options.skipRequest only used by collection search form
        // options.replace only used handleSubmit, handlePopState, handleAuth0Login
        // options.noscroll to prevent scrolling to the top of the page after navigating
        // options.reload to force reloading the URL
        let mutatableHref = url.resolve(this.state.href, href);

        // Strip url fragment.
        let fragment = '';
        const hrefHashPos = mutatableHref.indexOf('#');
        if (hrefHashPos > -1) {
            fragment = mutatableHref.slice(hrefHashPos);
            mutatableHref = mutatableHref.slice(0, hrefHashPos);
        }

        // Bypass loading and rendering from JSON if history is disabled
        // or if the href looks like a download.
        let decodedHref;
        try {
            decodedHref = decodeURIComponent(mutatableHref);
        } catch (exc) {
            decodedHref = mutatableHref;
        }
        const isDownload = decodedHref.includes('/@@download') || decodedHref.includes('/batch_download/');
        if (!this.constructor.historyEnabled() || isDownload || mutatableOptions.reload) {
            this.fallbackNavigate(mutatableHref, fragment, mutatableOptions);
            return null;
        }

        const { contextRequest } = this.state;

        if (contextRequest && this.requestCurrent) {
            // Abort the current request, then remember we've aborted the request so that we
            // don't render the Network Request Error page.
            contextRequest.abort();
            this.requestAborted = true;
            this.requestCurrent = false;
        }

        if (mutatableOptions.skipRequest) {
            if (mutatableOptions.replace) {
                window.history.replaceState(window.state, '', mutatableHref + fragment);
            } else {
                window.history.pushState(window.state, '', mutatableHref + fragment);
            }
            this.setState({ href: mutatableHref + fragment });
            return null;
        }

        const request = this.fetch(mutatableHref, {
            headers: { Accept: 'application/json' },
        });
        this.requestCurrent = true; // Remember we have an outstanding GET request

        const timeout = new Timeout(SLOW_REQUEST_TIME);

        Promise.race([request, timeout.promise]).then((v) => {
            if (v instanceof Timeout) {
                this.setState({ slow: true });
            } else {
                // Request has returned data
                this.requestCurrent = false;
            }
        });

        const promise = request.then((response) => {
            // Request has returned data
            this.requestCurrent = false;

            // navigate normally to URL of unexpected non-JSON response so back button works.
            if (!contentTypeIsJSON(response.headers.get('Content-Type'))) {
                this.fallbackNavigate(mutatableHref, fragment, mutatableOptions);
                return null;
            }
            // The URL may have redirected
            const responseUrl = (response.url || mutatableHref) + fragment;
            if (mutatableOptions.replace) {
                window.history.replaceState(null, '', responseUrl);
            } else {
                window.history.pushState(null, '', responseUrl);
            }
            this.setState({
                href: responseUrl,
            });
            if (!response.ok) {
                throw response;
            }
            return response.json();
        }).catch(globals.parseAndLogError.bind(undefined, 'contextRequest')).then(this.receiveContextResponse);

        // Scroll to the top of the page unless replacing the URL or option to not scroll given.
        if (!mutatableOptions.replace && !mutatableOptions.noscroll) {
            promise.then(this.constructor.scrollTo);
        }

        this.setState({
            contextRequest: request,
        });
        return request;
    }

    /* eslint-disable class-methods-use-this */
    fallbackNavigate(href, fragment, options) {
        // Navigate using window.location
        if (options.replace) {
            window.location.replace(href + fragment);
        } else {
            const oldPath = (window.location.toString()).split('#')[0];
            window.location.assign(href + fragment);
            if (oldPath === href) {
                window.location.reload();
            }
        }
    }
    /* eslint-enable class-methods-use-this */

    receiveContextResponse(data) {
        // title currently ignored by browsers
        try {
            window.history.replaceState(data, '', window.location.href);
        } catch (exc) {
            // Might fail due to too large data
            window.history.replaceState(null, '', window.location.href);
        }

        // Set up new properties for the page after a navigation click. First disable slow now that we've
        // gotten a response. If the requestAborted flag is set, then a request was aborted and so we have
        // the data for a Network Request Error. Don't render that, but clear the requestAborted flag.
        // Otherwise we have good page data to render.
        const newState = { slow: false };
        if (!this.requestAborted) {
            // Real page to render
            this.setState({ context: data });
        } else {
            // data holds network error. Don't render that, but clear the requestAborted flag so we're ready
            // for the next navigation click.
            this.requestAborted = false;
        }
        this.setState(newState);
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
        let { context } = this.state;
        const hrefUrl = url.parse(this.state.href);

        // Determine conditions to unmount the entire page and rerender from scratch. Any paths
        // included in `fullPageReloadPaths` rerender the entire page on navigation. Other paths
        // cause a rerender only when the path changes.
        const key = fullPageReloadPaths.includes(hrefUrl.pathname) ? context['@id'] : hrefUrl.pathname;

        const currentAction = this.currentAction();
        const isHomePage = context.default_page && context.default_page.name === 'homepage' && (!hrefUrl.hash || hrefUrl.hash === '#logged-out');
        if (isHomePage) {
            context = context.default_page;
            content = <Home context={context} />;
        } else {
            if (!currentAction && context.default_page) {
                context = context.default_page;
            }
            if (context) {
                const ContentView = globals.contentViews.lookup(context, currentAction);
                content = <ContentView context={context} />;
            }
        }
        const errors = this.state.errors.map((i) => <div key={i} className="alert alert-error" />);

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
            this.constructor.historyEnabled = false;
        }

        /* eslint-disable jsx-a11y/click-events-have-key-events, jsx-a11y/no-noninteractive-element-interactions */
        return (
            <html lang="en" ref={this.props.domReader ? (node) => this.props.domReader(node) : null}>
                <head>
                    <meta charSet="utf-8" />
                    <meta httpEquiv="X-UA-Compatible" content="IE=edge" />
                    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                    {/* The following line is a get around for GO server not being HTTPS */}
                    {/* https://encodedcc.atlassian.net/browse/ENCD-5005 */}
                    {/* https://stackoverflow.com/questions/33507566/mixed-content-blocked-when-running-an-http-ajax-operation-in-an-https-page#answer-48700852 */}
                    {this.props.context['@type'] && this.props.context['@type'].includes('Gene') ? <meta httpEquiv="Content-Security-Policy" content="upgrade-insecure-requests" /> : null}
                    <Title>{title}</Title>
                    {base ? <base href={base} /> : null}
                    <link rel="canonical" href={canonical} />
                    {this.props.styles ? <link rel="stylesheet" href={this.props.styles} /> : null}
                    <link href="https://fonts.googleapis.com/css2?family=Mada:wght@200;400;500;600;700&family=Oswald:wght@200;300;400;500&family=Quicksand:wght@300;400;600&display=swap" rel="stylesheet" />
                    <script async src="//www.google-analytics.com/analytics.js" />
                    <script async src={`https://cdn.walkme.com/users/8c7ff9322d01408798869806f9f5a132/${globals.isProductionHost(this.props.href) ? '' : 'test/'}walkme_8c7ff9322d01408798869806f9f5a132_https.js`} />
                    {this.props.inline ? <script data-prop-name="inline" dangerouslySetInnerHTML={{ __html: this.props.inline }} /> : null}
                    {newsHead(this.props, `${hrefUrl.protocol}//${hrefUrl.host}`)}
                    {this.state.context && this.state.context['@type'] && this.state.context['@type'].some((type) => ['experiment', 'functionalcharacterizationexperiment', 'annotation'].includes(type.toLowerCase())) ?
                        <script
                            data-prop-name="context"
                            type="application/ld+json"
                            dangerouslySetInnerHTML={{
                                __html: `\n\n${jsonScriptEscape(JSON.stringify(jsonldFormatter(this.state.context, hrefUrl.host)))}\n\n`,
                            }}
                        />
                    : null
                    }
                </head>
                <body onClick={this.handleClick} onSubmit={this.handleSubmit}>
                    <script
                        data-prop-name="context"
                        type="application/json"
                        dangerouslySetInnerHTML={{
                            __html: `\n\n${jsonScriptEscape(JSON.stringify((this.state.context)))}\n\n`,
                        }}
                    />
                    <div id="slot-application" className={appClass}>
                        <div id="application">
                            <div className="loading-spinner" />
                            <Provider store={cartStore}>
                                <div id="layout">
                                    <Navigation isHomePage={isHomePage} />
                                    <div id="content" className={context['@type'] ? `container ${context['@type'].join(' ')}` : 'container'} key={key}>
                                        {content}
                                    </div>
                                    {errors}
                                    <div id="layout-footer" />
                                    <CartAlert />
                                </div>
                            </Provider>
                            {this.state.eulaModalVisibility ?
                                <EulaModal
                                    closeModal={this.closeSignupModal}
                                    signup={this.signup}
                                />
                            : null}
                            { this.state.accountCreatedModalVisibility ?
                                <AccountCreatedModal
                                    closeModal={this.closeAccountCreationNotification}
                                />
                            : null}
                            {this.state.accountCreationFailedVisibility ?
                                <AccountCreationFailedModal
                                    closeModal={this.closeAccountCreationErrorModal}
                                    date={(new Date()).toUTCString()}
                                />
                            : null}
                            <Footer version={this.props.context.app_version} />
                        </div>
                    </div>
                    <div id="modal-root" />
                </body>
            </html>
        );
        /* eslint-enable jsx-a11y/click-events-have-key-events */
    }
}

App.propTypes = {
    context: PropTypes.object.isRequired,
    href: PropTypes.string.isRequired,
    styles: PropTypes.string,
    inline: PropTypes.string,
    domReader: PropTypes.func, // Only for Jest test
};

App.defaultProps = {
    styles: '',
    inline: '',
    domReader: null,
};

App.childContextTypes = {
    listActionsFor: PropTypes.func,
    currentResource: PropTypes.func,
    location_href: PropTypes.string,
    fetch: PropTypes.func,
    fetchSessionProperties: PropTypes.func,
    navigate: PropTypes.func,
    portal: PropTypes.object,
    projectColors: PropTypes.object,
    biosampleTypeColors: PropTypes.object,
    adviseUnsavedChanges: PropTypes.func,
    session: PropTypes.object,
    session_properties: PropTypes.object,
    profilesTitles: PropTypes.object,
    localInstance: PropTypes.bool,
};

module.exports = App;


// Only used for Jest tests.
module.exports.getRenderedProps = function getRenderedProps(document) {
    const props = {};

    // Ensure the initial render is exactly the same
    props.href = document.querySelector('link[rel="canonical"]').getAttribute('href');
    props.styles = document.querySelector('link[rel="stylesheet"]').getAttribute('href');
    const scriptProps = document.querySelectorAll('script[data-prop-name]');
    for (let i = 0; i < scriptProps.length; i += 1) {
        const elem = scriptProps[i];
        let value = elem.text;
        const elemType = elem.getAttribute('type') || '';
        if (elemType === 'application/json' || elemType.slice(-5) === '+json') {
            value = JSON.parse(value);
        }
        props[elem.getAttribute('data-prop-name')] = value;
    }
    return props;
};
