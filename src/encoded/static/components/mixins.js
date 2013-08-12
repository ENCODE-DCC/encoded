define(['exports', 'jquery', 'react', 'uri', 'persona'],
function (mixins, $, React, URI) {
    /*jshint devel: true*/
    'use strict';

        
    var parseError = mixins.parseError = function (xhr, status) {
        var data;
        if (status == 'abort') return;
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


    mixins.RenderLess = {
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

    mixins.Persona = {
        componentDidMount: function () {
            // Login / logout actions must be deferred until persona is ready.
            $.ajaxPrefilter(this.ajaxPrefilter);
            this.personaDeferred = $.Deferred();
            this.refreshSession();
        },

        ajaxPrefilter: function (options, original, xhr) {
            var http_method = options.type;
            var csrf_token = this.state.session && this.state.session.csrf_token;
            if (http_method === 'GET' || http_method === 'HEAD') return;
            if (!csrf_token) return;
            xhr.setRequestHeader('X-CSRF-Token', csrf_token);
        },

        refreshSession: function () {
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

        componentDidUpdate: function (prevProps, prevState) {
            // Defer persona setup until we have the session
            if (!prevState.session && this.state.session) {
                navigator.id.watch({
                    loggedInUser: this.state.session.persona,
                    onlogin: this.handlePersonaLogin,
                    onlogout: this.handlePersonaLogout,
                    onready: this.handlePersonaReady
                });
            }
        },

        handlePersonaLogin: function (assertion, retrying) {
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
                self.navigate(next_url, {replace: true});
            }).fail(function (xhr, status, err) {
                // If there is an error, show the error messages
                navigator.id.logout();
                var data = parseError(xhr, status)
                if (xhr.status === 400 && data.detail.indexOf('CSRF') !== -1) {
                    if (!retrying) {
                        self.refreshSession().done(function () {
                            self.handlePersonaLogin(assertion, true);
                        })
                    return;
                    }
                }
                self.setState({context: data});
            });
        },

        handlePersonaLogout: function () {
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
                self.setState({context: data});
            });
        },

        handlePersonaReady: function () {
            this.personaDeferred.resolve();
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


    mixins.HistoryAndTriggers = {
        // Detect HTML5 history support
        historyEnabled: !!(window.history && window.history.pushState),

        componentDidMount: function () {
            if (this.historyEnabled) {
                if (this.state.context) {
                    var data = this.state.context;
                    try {
                        window.history.replaceState(data, '', window.location.href);
                    } catch (exc) {
                        // Might fail due to too large data
                        window.history.replaceState(null, '', window.location.href);
                    }
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

        handleClick: function(event) {
            var target = event.target;
            var nativeEvent = event.nativeEvent;

            while (target && (target.tagName != 'A' || target.getAttribute('data-href'))) {
                target = target.parentElement;
            }
            if (!target) return;

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
            if (!URI(href).sameOrigin()) return;

            // With HTML5 history supported, local navigation is passed
            // through the navigate method.
            if (this.historyEnabled) {
                event.preventDefault();
                this.navigate(href);
            }
        },

        // Submitted forms are treated the same as links
        handleSubmit: function(event) {
            var target = event.target;

            // Skip POST forms
            if (target.method != 'get') return;

            // Skip forms with a data-bypass attribute.
            if (target.getAttribute('data-bypass')) return;

            // Skip external forms
            var uri = URI(target.action);
            if (!uri.sameOrigin()) return;

            var options = {}
            options.replace = uri.pathname == URI(this.props.href).pathname;
            var search = $(target).serialize();
            if (target.getAttribute('data-removeempty')) {
                search = search.split('&').filter(function (item) {
                    return item.slice(-1) != '=';
                }).join('&');
            }
            var href = uri.pathname;
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
            var href = window.location.href;
            if (event.state) {
                this.setState({context: event.state})
            }
            // Always async update in case of server side changes
            this.navigate(href, {replace: true});
        },

        navigate: function (href, options) {
            options = options || {}; 
            var self = this;
            this.setProps({href: href});

            if (this.contextRequest && this.contextRequest.state() == 'pending') {
                this.contextRequest.abort();
            }

            if (options.replace) {
                window.history.replaceState(window.state, '', href);
            } else {
                window.history.pushState(window.state, '', href);
            }
            if (options.skipRequest) return;

            this.setState({communicating: true});

            // The contextDataElement is kept in sync with the context request result.
            this.props.contextDataElement.text = '';

            this.contextRequest = $.ajax({
                url: href,
                type: 'GET',
                dataType: 'json'
            }).fail(this.receiveContextFailure)
            .done(this.receiveContextResponse);
        },

        receiveContextFailure: function (xhr, status, error) {
            var data = parseError(xhr, status);
            this.receiveContextResponse(data, status, xhr);
        },

        receiveContextResponse: function (data, status, xhr) {
            this.setState({
                communicating: false,
                context: data
            });

            // title currently ignored by browsers
            try {
                window.history.replaceState(data, '', window.location.href);
            } catch (exc) {
                // Might fail due to too large data
                window.history.replaceState(null, '', window.location.href);
            }
            // Set the contextDataElement as a debugging aid
            if (this.props.contextDataElement) {
                this.props.contextDataElement.text = xhr.responseText;
            }
        }
    };

    return mixins;
});
