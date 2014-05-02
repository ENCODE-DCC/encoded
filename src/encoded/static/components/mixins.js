/** @jsx React.DOM */
'use strict';
var React = require('react');
var url = require('url');
var origin = require('origin');

var parseError = module.exports.parseError = function (xhr, status) {
    var data;
    if (status == 'timeout') {
        data = {
            status: 'timeout',
            title: 'Request timeout',
            '@type': ['ajax_error', 'error']
        };
    } else if (status == 'error') {
        var content_type = xhr.getResponseHeader('Content-Type') || '';
        content_type = content_type.split(';')[0];
        if (content_type == 'application/json') {
            try {
                data = JSON.parse(xhr.responseText);
            } catch (exc) {
                status = 'parsererror';
            }
        } else {
            data = {
                status: 'error',
                title: xhr.statusText,
                code: xhr.status,
                '@type': ['ajax_error', 'error']
            };
        }
    }
    if (status == 'parsererror') {
        data = {
            status: 'timeout',
            title: 'Parser error',
            '@type': ['ajax_error', 'error']
        };
    }
    if (!data) {
        data = {
            status: '' + status,
            title: 'Error',
            '@type': ['ajax_error', 'error']
        };
    }
    return data;
};


module.exports.RenderLess = {
    shouldComponentUpdate: function (nextProps, nextState) {
        var key;
        if (nextProps) {
            for (key in nextProps) {
                if (nextProps[key] !== this.props[key]) {
                    console.log('changed props: %s', key);
                    return true;
                }
            }
        }
        if (nextState) {
            for (key in nextState) {
                if (nextState[key] !== this.state[key]) {
                    console.log('changed state: %s', key);
                    return true;
                }
            }
        }
        return false;
    },
};

module.exports.Persona = {
    componentDidMount: function () {
        var $ = require('jquery');
        // Login / logout actions must be deferred until persona is ready.
        $.ajaxPrefilter(this.ajaxPrefilter);
        this.personaDeferred = $.Deferred();
        if (!navigator.id) {
            // Ensure DOM is clean for React when mounting
            // Unminified: https://login.persona.org/include.orig.js
            this.personaLoaded = $.getScript("https://login.persona.org/include.js");
        }
        this.configurePersona(this.parseSessionCookie());
    },

    ajaxPrefilter: function (options, original, xhr) {
        xhr.xhr_begin = 1 * new Date();
        var http_method = options.type;
        if (http_method === 'GET' || http_method === 'HEAD') return;
        var userid = this.state.session && this.state.session['auth.userid']
        if (userid) {
            // XXX Server should use this to check user is logged in
            xhr.setRequestHeader('X-Session-Userid', userid);
        }
        if (this.csrf_token) {
            xhr.setRequestHeader('X-CSRF-Token', this.csrf_token);
        }
    },

    parseSessionCookie: function () {
        var Buffer = require('buffer').Buffer;
        var cookie = require('cookie-cutter');
        var session_cookie = cookie(document).get('session');
        if (!session_cookie) return null;
        // URL-safe base64
        session_cookie = session_cookie.replace(/\-/g, '+').replace(/\_/g, '/');
        try {
            // First 64 chars is the sha-512 server signature
            // Payload is [accessed, created, data]
            var session = JSON.parse(Buffer(session_cookie, 'base64').slice(64).toString())[2]
        } catch (e) {
            return null;
        }
        this.csrf_token = session._csrft_;
        this.setState({session: session});
        return session;
    },

    reloadSession: function () {
        var $ = require('jquery');
        if (this.sessionRequest && this.sessionRequest.state() == 'pending') {
            this.sessionRequest.abort();
        }
        this.sessionRequest = $.ajax({
            url: '/session?reload=true',
            type: 'GET',
            dataType: 'json'
        }).done(function (session) {
            this.parseSessionCookie();
        }.bind(this));
        return this.sessionRequest;
    },

    configurePersona: function (session) {
        this.personaLoaded.done(function () {
            navigator.id.watch({
                loggedInUser: session && session['auth.userid'] || null,
                onlogin: this.handlePersonaLogin,
                onlogout: this.handlePersonaLogout,
                onmatch: this.handlePersonaMatch,
                onready: this.handlePersonaReady
            });
        }.bind(this));
    },

    handlePersonaLogin: function (assertion, retrying) {
        this._persona_watched = true;
        var $ = require('jquery');
        if (!assertion) return;
        $.ajax({
            url: '/login',
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify({assertion: assertion}),
            contentType: 'application/json'
        }).done(function (session) {
            this.parseSessionCookie();
            var next_url = window.location.href;
            if (window.location.hash == '#logged-out') {
                next_url = window.location.pathname + window.location.search;
            }
            if (this.historyEnabled) {
                this.navigate(next_url, {replace: true}).done(function () {
                    this.setState({loadingComplete: true})
                }.bind(this));
            } else {
                var old_path = window.location.pathname + window.location.search;
                window.location.assign(next_url);
                if (old_path == next_url) {
                    window.location.reload();
                }
            }
        }.bind(this)).fail(function (xhr, status, err) {
            var data = parseError(xhr, status);
            this.parseSessionCookie();
            if (xhr.status === 400 && data.detail.indexOf('CSRF') !== -1) {
                if (!retrying) {
                    return this.handlePersonaLogin(assertion, true);
                }
            }
            // If there is an error, show the error messages
            navigator.id.logout();
            this.setProps({context: data});
            this.setState({loadingComplete: true});
        }.bind(this));
    },

    handlePersonaLogout: function () {
        this._persona_watched = true;
        var $ = require('jquery');
        console.log("Persona thinks we need to log out");
        var session = this.state.session;
        if (!(session && session['auth.userid'])) return;
        $.ajax({
            url: '/logout?redirect=false',
            type: 'GET',
            dataType: 'json'
        }).done(function (data) {
            this.DISABLE_POPSTATE = true;
            var old_path = window.location.pathname + window.location.search;
            window.location.assign('/#logged-out');
            if (old_path == '/') {
                window.location.reload();
            }
        }.bind(this)).fail(function (xhr, status, err) {
            data = parseError(xhr, status);
            data.title = 'Logout failure: ' + data.title;
            this.setProps({context: data});
        }.bind(this));
    },

    handlePersonaMatch: function () {
        this._persona_watched = true;
        this.setState({loadingComplete: true});
    },

    handlePersonaReady: function () {
        this.personaDeferred.resolve();
        console.log('persona ready');
        this.setState({personaReady: true});
        // Handle Safari https://github.com/mozilla/persona/issues/3905
        if (!this._persona_watched) {
            this.setState({loadingComplete: true});
        }
    },

    triggerLogin: function (event) {
        this.personaDeferred.done(function () {
            var request_params = {}; // could be site name
            console.log('Logging in (persona) ');
            navigator.id.request(request_params);
        });
    },

    triggerLogout: function (event) {
        this.personaDeferred.done(function () {
            console.log('Logging out (persona)');
            navigator.id.logout();
        });
    }
};


module.exports.HistoryAndTriggers = {
    SLOW_REQUEST_TIME: 750,
    // Detect HTML5 history support
    historyEnabled: !!(typeof window != 'undefined' && window.history && window.history.pushState),

    componentWillMount: function () {
        if (typeof window !== 'undefined') {
            // IE8 compatible event registration
            window.onerror = this.handleError;
        }
    },

    componentDidMount: function () {
        if (this.historyEnabled) {
            var data = this.props.context;
            try {
                window.history.replaceState(data, '', window.location.href);
            } catch (exc) {
                // Might fail due to too large data
                window.history.replaceState(null, '', window.location.href);
            }
            // Avoid popState on load, see: http://stackoverflow.com/q/6421769/199100
            var register = window.addEventListener.bind(window, 'popstate', this.handlePopState, true);
            if (window._onload_event_fired) {
                register();
            } else {
                window.addEventListener('load', setTimeout.bind(window, register));
            }
        } else {
            window.onhashchange = this.onHashChange;
        }
        this.setProps({href: window.location.href});
    },

    onHashChange: function (event) {
        // IE8/9
        this.setProps({href: window.location.href});
    },

    trigger: function (name) {
        var method_name = this.triggers[name];
        if (method_name) {
            this[method_name].call(this);
        }
    },

    handleError: function(msg, url, line, column) {
        // When an unhandled exception occurs, reload the page on navigation
        this.historyEnabled = false;
        var ga = window.ga;
        var parsed = url && require('url').parse(url);
        if (url && parsed.hostname === window.location.hostname) {
            url = parsed.path;
        }
        ga('send', 'exception', {
            'exDescription': url + '@' + line + ',' + column + ': ' + msg,
            'exFatal': true,
            'location': window.location.href
        });
    },

    handleClick: function(event) {
        var target = event.target;
        var nativeEvent = event.nativeEvent;

        // SVG anchor elements have tagName == 'a' while HTML anchor elements have tagName == 'A'
        while (target && (target.tagName.toLowerCase() != 'a' || target.getAttribute('data-href'))) {
            target = target.parentElement;
        }
        if (!target) return;

        if (target.getAttribute('disabled')) {
            event.preventDefault();
            return;
        }

        // data-trigger links invoke custom handlers.
        var data_trigger = target.getAttribute('data-trigger');
        if (data_trigger !== null) {
            event.preventDefault();
            this.trigger(data_trigger);
            return;
        }

        // Ensure this is a plain click
        if (nativeEvent.which > 1 || nativeEvent.shiftKey || nativeEvent.altKey || nativeEvent.metaKey) return;

        // Skip links with a data-bypass attribute.
        if (target.getAttribute('data-bypass')) return;

        var href = target.getAttribute('href');
        if (href === null) href = target.getAttribute('data-href');
        if (href === null) return;

        // Skip external links
        if (!origin.same(href)) return;

        // With HTML5 history supported, local navigation is passed
        // through the navigate method.
        if (this.historyEnabled) {
            event.preventDefault();
            this.navigate(href);
        }
    },

    // Submitted forms are treated the same as links
    handleSubmit: function(event) {
        var $ = require('jquery');
        var target = event.target;

        // Skip POST forms
        if (target.method != 'get') return;

        // Skip forms with a data-bypass attribute.
        if (target.getAttribute('data-bypass')) return;

        // Skip external forms
        if (!origin.same(target.action)) return;

        var options = {};
        var action_url = url.parse(url.resolve(this.props.href, target.action));
        options.replace = action_url.pathname == url.parse(this.props.href).pathname;
        var search = $(target).serialize();
        if (target.getAttribute('data-removeempty')) {
            search = search.split('&').filter(function (item) {
                return item.slice(-1) != '=';
            }).join('&');
        }
        var href = action_url.pathname;
        if (search) {
            href += '?' + search;
        }

        options.skipRequest = target.getAttribute('data-skiprequest');

        if (this.historyEnabled) {
            event.preventDefault();
            this.navigate(href, options);
        }
    },

    handlePopState: function (event) {
        if (this.DISABLE_POPSTATE) return;
        if (!this.historyEnabled) {
            window.location.reload();
            return;
        }
        var xhr = this.props.contextRequest;
        var href = window.location.href;
        if (event.state) {
            // Abort inflight xhr before setProps
            if (xhr && xhr.state() == 'pending') {
                xhr.abort();
            }
            this.setProps({
                context: event.state,
                href: href  // href should be consistent with context
            });
        }
        // Always async update in case of server side changes.
        // Triggers standard analytics handling.
        this.navigate(href, {replace: true});
    },

    navigate: function (href, options) {
        var $ = require('jquery');
        options = options || {};
        href = url.resolve(this.props.href, href);
        var xhr = this.props.contextRequest;

        if (xhr && xhr.state() == 'pending') {
            xhr.abort();
        }

        if (options.replace) {
            window.history.replaceState(window.state, '', href);
        } else {
            window.history.pushState(window.state, '', href);
        }
        if (options.skipRequest) {
            this.setProps({href: href});
            return;
        }

        xhr = $.ajax({
            url: href,
            type: 'GET',
            dataType: 'json'
        }).fail(this.receiveContextFailure)
        .done(this.receiveContextResponse);

        if (!options.replace) {
            xhr.always(this.scrollTo);
        }

        xhr.slowTimer = setTimeout(
            this.detectSlowRequest.bind(this, xhr),
            this.SLOW_REQUEST_TIME);
        xhr.href = href;

        this.setProps({
            contextRequest: xhr,
            href: href
        });
        return xhr;
    },

    detectSlowRequest: function (xhr) {
        if (xhr.state() == 'pending') {
            this.setProps({'slow': true});
        }
    },

    receiveContextFailure: function (xhr, status, error) {
        if (status == 'abort') {
            clearTimeout(xhr.slowTimer)
            return;
        }
        var ga = window.ga;
        var data = parseError(xhr, status);
        ga('send', 'exception', {
            'exDescription': 'contextRequest:' + status + ':' + xhr.statusText,
            'location': window.location.href
        });
        if (this.state.session && this.state.session['auth.userid']) {
            var session = this.parseSessionCookie();
            if (!session['auth.userid']) {
                this.setState({personaReady: false, loadingComplete: false});
                this.personaDeferred = require('jquery').Deferred();
                this.configurePersona(session);
            }
        }

        this.receiveContextResponse(data, status, xhr);
    },

    receiveContextResponse: function (data, status, xhr) {
        xhr.xhr_end = 1 * new Date();
        clearTimeout(xhr.slowTimer)
        // title currently ignored by browsers
        try {
            window.history.replaceState(data, '', window.location.href);
        } catch (exc) {
            // Might fail due to too large data
            window.history.replaceState(null, '', window.location.href);
        }
        this.setProps({
            context: data,
            slow: false
        });

    },

    componentDidUpdate: function () {
        var xhr = this.props.contextRequest;
        if (!xhr || !xhr.xhr_end || xhr.browser_stats) return;
        var browser_end = 1 * new Date();

        var ga = window.ga;

        ga('set', 'location', window.location.href);
        ga('send', 'pageview');

        var stats_header = xhr.getResponseHeader('X-Stats') || '';
        xhr.server_stats = require('querystring').parse(stats_header);
        recordServerStats(xhr.server_stats, 'contextRequest');

        xhr.browser_stats = {};
        xhr.browser_stats['xhr_time'] = xhr.xhr_end - xhr.xhr_begin;
        xhr.browser_stats['browser_time'] = browser_end - xhr.xhr_end;
        xhr.browser_stats['total_time'] = browser_end - xhr.xhr_begin;
        recordBrowserStats(xhr.browser_stats, 'contextRequest');

    },

    scrollTo: function() {
        var hash = window.location.hash;
        if (hash && document.getElementById(hash.slice(1))) {
            window.location.replace(hash);
        } else {
            window.scrollTo(0, 0);
        }
    }
};


var recordServerStats = module.exports.recordServerStats = function (server_stats, timingVar) {
    // server_stats *_time are microsecond values...
    var ga = window.ga;
    Object.keys(server_stats).forEach(function (name) {
        if (name.indexOf('_time') === -1) return;
        ga('send', 'timing', {
            'timingCategory': name,
            'timingVar': timingVar,
            'timingValue': Math.round(server_stats[name] / 1000)
        });
    });
};


var recordBrowserStats = module.exports.recordBrowserStats = function (browser_stats, timingVar) {
    var ga = window.ga;
    Object.keys(browser_stats).forEach(function (name) {
        if (name.indexOf('_time') === -1) return;
        ga('send', 'timing', {
            'timingCategory': name,
            'timingVar': timingVar,
            'timingValue': browser_stats[name]
        });
    });
};


// Return browser capabilities, a la Modernizr. Can *only* be called from
// mounted components (componentDidMount method would be a good method to
// call this from), because actual DOM is needed.
module.exports.browserCaps = function () {
    var caps = {};

    caps.svg = document.implementation.hasFeature('http://www.w3.org/TR/SVG11/feature#Image', '1.1');
    return caps;
};