import React from 'react';
import _ from 'underscore';
import url from 'url';
import ga from 'google-analytics';
import serialize from 'form-serialize';
import origin from '../libs/origin';

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

export function parseAndLogError(cause, response) {
    const promise = parseError(response);
    promise.then((data) => {
        ga('send', 'exception', {
            exDescription: `${cause}:${data.code}:${data.title}`,
            location: window.location.href,
        });
    });
    return promise;
}


function contentTypeIsJSON(contentType) {
    return (contentType || '').split(';')[0].split('/').pop().split('+').pop() === 'json';
}


class Timeout {
    constructor(timeout) {
        this.promise = new Promise(resolve => setTimeout(resolve.bind(undefined, this), timeout));
    }
}


function extractSessionCookie() {
    const cookie = require('cookie-monster');
    return cookie(document).get('session');
}


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


/* eslint new-cap: ["error", { "newIsCapExceptions": ["default"] }]*/

export const Auth0Decor = (Auth0Component) => {
    class Auth0Class extends React.Component {
        constructor(props) {
            super();

            // React component state.
            this.state = {
                href: '',
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

            // Bind `this` to non-React methods.
            this.fetch = this.fetch.bind(this);
            this.fetchSessionProperties = this.fetchSessionProperties.bind(this);
            this.handleAuth0Login = this.handleAuth0Login.bind(this);
            this.triggerLogin = this.triggerLogin.bind(this);
            this.triggerLogout = this.triggerLogout.bind(this);
            this.setGlobalState = this.setGlobalState.bind(this);
        }

        getChildContext() {
            return {
                fetch: this.fetch,
                session: this.state.session,
                session_properties: this.state.session_properties,
            };
        }

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

            const lock_ = require('auth0-lock');
            this.lock = new lock_.default('WIOr638GdDdEGPJmABPhVzMn6SYUIdIH', 'encode.auth0.com', {
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

        setGlobalState(newState) {
            this.setState(newState);
        }

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

        triggerLogin() {
            if (this.state.session && !this.state.session._csrft_) {
                this.fetch('/session');
            }
            this.lock.show();
        }

        triggerLogout() {
            console.log('Logging out (Auth0)');
            const session = this.state.session;
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
                parseError(err).then((data) => {
                    data.title = `Logout failure: ${data.title}`;
                    this.setState({ context: data });
                });
            });
        }

        render() {
            return (
                <Auth0Component
                    {...this.props}
                    href={this.state.href}
                    context={this.state.context}
                    setGlobalState={this.setGlobalState}
                    triggers={this.triggers}
                    triggerLogin={this.triggerLogin}
                    triggerLogout={this.triggerLogout}
                />
            );
        }
    }

    Auth0Class.propTypes = {
        href: React.PropTypes.string.isRequired,
        context: React.PropTypes.object.isRequired,
    };

    Auth0Class.childContextTypes = {
        fetch: React.PropTypes.func,
        session: React.PropTypes.object,
        session_properties: React.PropTypes.object,
    };

    return Auth0Class;
};


class UnsavedChangesToken {
    constructor(manager) {
        this.manager = manager;
    }

    release() {
        this.manager.releaseUnsavedChanges(this);
    }
}


const SLOW_REQUEST_TIME = 250;

function recordServerStats(serverStats, timingVar) {
    // server_stats *_time are microsecond values...
    Object.keys(serverStats).forEach((name) => {
        if (name.indexOf('_time') !== -1) {
            ga('send', 'timing', {
                timingCategory: name,
                timingVar: timingVar,
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
                timingVar: timingVar,
                timingValue: browserStats[name],
            });
        }
    });
}


/* eslint no-script-url: 0 */ // We're not *using* a javascript: link -- just checking them.
const HistoryAndTriggersDecor = (HistoryAndTriggersComponent) => {
    class HistoryAndTriggersClass extends React.Component {
        static historyEnabled() {
            return !!(typeof window !== 'undefined' && window.history && window.history.pushState);
        }

        static scrollTo() {
            const hash = window.location.hash;
            if (hash && document.getElementById(hash.slice(1))) {
                window.location.replace(hash);
            } else {
                window.scrollTo(0, 0);
            }
        }

        constructor() {
            super();

            // React component state
            this.state = {
                contextRequest: null,
                unsavedChanges: [],
                promisePending: false,
                slow: false,
            };

            // Bind `this` to non-React methods.
            this.adviseUnsavedChanges = this.adviseUnsavedChanges.bind(this);
            this.releaseUnsavedChanges = this.releaseUnsavedChanges.bind(this);
            this.onHashChange = this.onHashChange.bind(this);
            this.trigger = this.trigger.bind(this);
            this.handleError = this.handleError.bind(this);
            this.handleClick = this.handleClick.bind(this);
            this.handleSubmit = this.handleSubmit.bind(this);
            this.handlePopState = this.handlePopState.bind(this);
            this.confirmNavigation = this.confirmNavigation.bind(this);
            this.handleBeforeUnload = this.handleBeforeUnload.bind(this);
            this.navigate = this.navigate.bind(this);
            this.receiveContextResponse = this.receiveContextResponse.bind(this);
        }

        getChildContext() {
            return {
                adviseUnsavedChanges: this.adviseUnsavedChanges,
                navigate: this.navigate,
            };
        }

        componentDidMount() {
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
                if (this.props.href) {
                    const splitHref = this.props.href.split('#');
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

        componentDidUpdate() {
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

        onHashChange() {
            // IE8/9
            this.props.setGlobalState({ href: window.location.href });
        }

        adviseUnsavedChanges() {
            const token = new UnsavedChangesToken(this);
            this.setState({ unsavedChanges: this.state.unsavedChanges.concat([token]) });
            return token;
        }

        releaseUnsavedChanges(token) {
            console.assert(this.state.unsavedChanges.indexOf(token) !== -1);
            this.setState({ unsavedChanges: this.state.unsavedChanges.filter(x => x !== token) });
        }

        trigger(name) {
            const methodName = this.props.triggers[name];
            if (methodName) {
                this.props[methodName].call(this);
            }
        }

        handleError(msg, uri, line, column) {
            let mutatableUri = uri;

            // When an unhandled exception occurs, reload the page on navigation
            this.historyEnabled = false;
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

        handleClick(event) {
            // https://github.com/facebook/react/issues/1691
            if (event.isDefaultPrevented()) {
                return;
            }

            let target = event.target;
            const nativeEvent = event.nativeEvent;

            // SVG anchor elements have tagName == 'a' while HTML anchor elements have tagName == 'A'
            while (target && (target.tagName.toLowerCase() !== 'a' || target.getAttribute('data-href'))) {
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
            if (this.historyEnabled) {
                event.preventDefault();
                this.navigate(href);
            }
        }

        // Submitted forms are treated the same as links
        handleSubmit(event) {
            const target = event.target;

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
            const actionUrl = url.parse(url.resolve(this.props.href, target.action));
            options.replace = actionUrl.pathname === url.parse(this.props.href).pathname;
            let search = serialize(target);
            if (target.getAttribute('data-removeempty')) {
                search = search.split('&').filter(item => item.slice(-1) !== '=').join('&');
            }
            let href = actionUrl.pathname;
            if (search) {
                href += `?${search}`;
            }
            options.skipRequest = target.getAttribute('data-skiprequest');

            if (this.historyEnabled) {
                event.preventDefault();
                this.navigate(href, options);
            }
        }

        handlePopState(event) {
            if (this.DISABLE_POPSTATE) {
                return;
            }
            if (!this.confirmNavigation()) {
                window.history.pushState(window.state, '', this.props.href);
                return;
            }
            if (!this.historyEnabled) {
                window.location.reload();
                return;
            }
            const request = this.state.contextRequest;
            const href = window.location.href;
            if (event.state) {
                // Abort inflight xhr before setProps
                if (request && this.requestCurrent) {
                    // Abort the current request, then remember we've aborted it so that we don't render
                    // the Network Request Error page.
                    request.abort();
                    this.requestAborted = true;
                    this.requestCurrent = false;
                }
                this.props.setGlobalState({
                    href: href,  // href should be consistent with context
                    context: event.state,
                });
            }
            // Always async update in case of server side changes.
            // Triggers standard analytics handling.
            this.navigate(href, { replace: true });
        }

        /* eslint no-alert: 0 */
        confirmNavigation() {
            // check for beforeunload confirmation
            if (this.state.unsavedChanges.length) {
                const res = window.confirm('You have unsaved changes. Are you sure you want to lose them?');
                if (res) {
                    this.setState({ unsavedChanges: [] });
                }
                return res;
            }
            return true;
        }

        handleBeforeUnload() {
            if (this.state.unsavedChanges.length) {
                return 'You have unsaved changes.';
            }
            return null;
        }

        navigate(href, options) {
            const mutatableOptions = options || {};
            if (!this.confirmNavigation()) {
                return null;
            }

            // options.skipRequest only used by collection search form
            // options.replace only used handleSubmit, handlePopState, handleAuth0Login
            let mutatableHref = url.resolve(this.props.href, href);

            // Strip url fragment.
            let fragment = '';
            const hrefHashPos = mutatableHref.indexOf('#');
            if (hrefHashPos > -1) {
                fragment = mutatableHref.slice(hrefHashPos);
                mutatableHref = mutatableHref.slice(0, hrefHashPos);
            }

            if (!this.constructor.historyEnabled()) {
                if (mutatableOptions.replace) {
                    window.location.replace(mutatableHref + fragment);
                } else {
                    const oldPath = (window.location.toString()).split('#')[0];
                    window.location.assign(mutatableHref + fragment);
                    if (oldPath === mutatableHref) {
                        window.location.reload();
                    }
                }
                return null;
            }

            let request = this.state.contextRequest;

            if (request && this.requestCurrent) {
                // Abort the current request, then remember we've aborted the request so that we
                // don't render the Network Request Error page.
                console.log('REQ %s:%o', this.requestCurrent, request);
                request.abort();
                this.requestAborted = true;
                this.requestCurrent = false;
            }

            if (mutatableOptions.skipRequest) {
                if (mutatableOptions.replace) {
                    window.history.replaceState(window.state, '', mutatableHref + fragment);
                } else {
                    window.history.pushState(window.state, '', mutatableHref + fragment);
                }
                this.props.setGlobalState({ href: mutatableHref + fragment });
                return null;
            }

            request = this.context.fetch(mutatableHref, {
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
                    if (mutatableOptions.replace) {
                        window.location.replace(mutatableHref + fragment);
                    } else {
                        const oldPath = (window.location.toString()).split('#')[0];
                        window.location.assign(mutatableHref + fragment);
                        if (oldPath === mutatableHref) {
                            window.location.reload();
                        }
                    }
                }
                // The URL may have redirected
                const responseUrl = (response.url || mutatableHref) + fragment;
                if (mutatableOptions.replace) {
                    window.history.replaceState(null, '', responseUrl);
                } else {
                    window.history.pushState(null, '', responseUrl);
                }
                this.props.setGlobalState({
                    href: responseUrl,
                });
                if (!response.ok) {
                    throw response;
                }
                return response.json();
            })
            .catch(parseAndLogError.bind(undefined, 'contextRequest'))
            .then(this.receiveContextResponse);

            if (!mutatableOptions.replace) {
                promise.then(this.constructor.scrollTo);
            }

            this.setState({
                contextRequest: request,
            });
            return request;
        }

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
            // the data for a Network Request Error. Don't render that, but clear the requestAboerted flag.
            // Otherwise we have good page data to render.
            const newState = { slow: false };
            if (!this.requestAborted) {
                // Real page to render
                this.props.setGlobalState({ context: data });
            } else {
                // data holds network error. Don't render that, but clear the requestAborted flag so we're ready
                // for the next navigation click.
                this.requestAborted = false;
            }
            this.setState(newState);
        }

        render() {
            return (
                <HistoryAndTriggersComponent
                    {...this.props}
                    handleClick={this.handleClick}
                    handleSubmit={this.handleSubmit}
                />
            );
        }
    }

    HistoryAndTriggersClass.childContextTypes = {
        adviseUnsavedChanges: React.PropTypes.func,
        navigate: React.PropTypes.func,
    };

    HistoryAndTriggersClass.contextTypes = {
        fetch: React.PropTypes.func,
    };

    HistoryAndTriggersClass.defaultProps = {
        context: null,
        href: '',
        triggers: {},
    };

    HistoryAndTriggersClass.propTypes = {
        context: React.PropTypes.object,
        href: React.PropTypes.string,
        triggers: React.PropTypes.object,
        setGlobalState: React.PropTypes.func.isRequired,
    };

    return HistoryAndTriggersClass;
};

module.exports.HistoryAndTriggersDecor = HistoryAndTriggersDecor;
