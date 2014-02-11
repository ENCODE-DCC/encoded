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
            this.personaLoaded = $.getScript("https://login.persona.org/include.js");
        }
        $.when(this.refreshSession(), this.personaLoaded).done(this.configurePersona);
    },

    ajaxPrefilter: function (options, original, xhr) {
        xhr.xhr_begin = 1 * new Date();
        var http_method = options.type;
        var csrf_token = this.state.session && this.state.session.csrf_token;
        if (http_method === 'GET' || http_method === 'HEAD') return;
        if (!csrf_token) return;
        xhr.setRequestHeader('X-CSRF-Token', csrf_token);
    },

    refreshSession: function () {
        var $ = require('jquery');
        var self = this;
        if (this.sessionRequest && this.sessionRequest.state() == 'pending') {
            this.sessionRequest.abort();
        }
        this.sessionRequest = $.ajax({
            url: '/session',
            type: 'GET',
            dataType: 'json'
        }).done(function (data) {
            self.setState({session: data});
        });
        return this.sessionRequest;
    },

    configurePersona: function (refresh, loaded) {
        var session = refresh[0];
        navigator.id.watch({
            loggedInUser: session.persona,
            onlogin: this.handlePersonaLogin,
            onlogout: this.handlePersonaLogout,
            onready: this.handlePersonaReady
        });
    },

    handlePersonaLogin: function (assertion, retrying) {
        var $ = require('jquery');
        var self = this;
        if (!assertion) return;
        $.ajax({
            url: '/login',
            type: 'POST',
            dataType: 'json',
            data: JSON.stringify({assertion: assertion}),
            contentType: 'application/json'
        }).done(function (data) {
            self.refreshSession();
            var next_url = window.location.href;
            if (window.location.hash == '#logged-out') {
                next_url = window.location.pathname + window.location.search;
            }
            if (this.historyEnabled) {
                self.navigate(next_url, {replace: true});
            } else {
                var old_path = window.location.pathname + window.location.search;
                window.location.assign(next_url);
                if (old_path == next_url) {
                    window.location.reload();
                }
            }
        }).fail(function (xhr, status, err) {
            // If there is an error, show the error messages
            navigator.id.logout();
            var data = parseError(xhr, status);
            if (xhr.status === 400 && data.detail.indexOf('CSRF') !== -1) {
                if (!retrying) {
                    self.refreshSession().done(function () {
                        self.handlePersonaLogin(assertion, true);
                    });
                return;
                }
            }
            self.setProps({context: data});
        });
    },

    handlePersonaLogout: function () {
        var $ = require('jquery');
        console.log("Persona thinks we need to log out");
        if (this.state.session.persona === null) return;
        var self = this;
        $.ajax({
            url: '/logout?redirect=false',
            type: 'GET',
            dataType: 'json'
        }).done(function (data) {
            self.DISABLE_POPSTATE = true;
            var old_path = window.location.pathname + window.location.search;
            window.location.assign('/#logged-out');
            if (old_path == '/') {
                window.location.reload();
            }
        }).fail(function (xhr, status, err) {
            data = parseError(xhr, status);
            data.title = 'Logout failure: ' + data.title;
            self.setProps({context: data});
        });
    },

    handlePersonaReady: function () {
        this.personaDeferred.resolve();
        console.log('persona ready');
        this.setState({personaReady: true});
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
            window.addEventListener('error', this.handleError, false);            
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
            window.addEventListener('popstate', this.handlePopState, true);
        }
    },

    trigger: function (name) {
        var method_name = this.triggers[name];
        if (method_name) {
            this[method_name].call(this);
        }
    },

    handleError: function(err, url, line) {
        // When an unhandled exception occurs, reload the page on navigation
        this.historyEnabled = false;
        window.ga('send', 'event', {
            'eventCategory': 'error',
            'eventAction': 'unhandled:' + (err.message) || err,
            'eventLabel': url + ':' + line,
            'location': window.location.href,
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
        // Avoid popState on load, see: http://stackoverflow.com/q/6421769/199100
        if (!this.havePushedState) return;
        if (!this.historyEnabled) {
            window.location.reload();
            return;
        }
        var href = window.location.href;
        if (event.state) {
            this.setProps({
                context: event.state,
                href: href  // href should be consistent with context
            });
        }
        // Always async update in case of server side changes
        this.navigate(href, {replace: true});
    },

    navigate: function (href, options) {
        var $ = require('jquery');
        options = options || {};
        href = url.resolve(this.props.href, href);
        var xhr = this.props.contextRequest;
        this.havePushedState = true;

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

    },

    detectSlowRequest: function (xhr) {
        if (xhr.state() == 'pending') {
            this.setProps({'slow': true});
        }
    },

    receiveContextFailure: function (xhr, status, error) {
        if (status == 'abort') return;
        var data = parseError(xhr, status);
        window.ga('send', 'event', {
            'eventCategory': 'error',
            'eventAction': 'contextRequest:' + status + ':' + xhr.statusText,
            'eventLabel': xhr.href
        });
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
        xhr.browser_stats = {};
        var stats_header = xhr.getResponseHeader('X-Stats') || '';
        xhr.server_stats = require('url').parse('?' + stats_header, true).query;

        var ga = window.ga;

        ga('set', 'location', window.location.href);
        ga('send', 'pageview');

        // At this point all of the _time keys are server generated
        // microsecond values...
        Object.keys(xhr.server_stats).forEach(function (name) {
            if (name.indexOf('_time') === -1) return;
            ga('send', 'timing', {
                'timingCategory': 'contextRequest',
                'timingVar': name,
                'timingValue': Math.round(xhr.server_stats[name] / 1000)
            });
        });

        xhr.browser_stats['xhr_time'] = xhr.xhr_end - xhr.xhr_begin;
        xhr.browser_stats['browser_time'] = browser_end - xhr.xhr_end;
        xhr.browser_stats['total_time'] = browser_end - xhr.xhr_begin;

        Object.keys(xhr.browser_stats).forEach(function (name) {
            if (name.indexOf('_time') === -1) return;
            ga('send', 'timing', {
                'timingCategory': 'contextRequest',
                'timingVar': name,
                'timingValue': xhr.browser_stats[name]
            });
        });

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
