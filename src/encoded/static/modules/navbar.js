define(['exports', 'jquery', 'underscore', 'navigator', 'app', 'base',
    'text!templates/global_sections.html',
    'text!templates/user_actions.html'],
function (navbar, $, _, navigator, app, base, global_sections_template, user_actions_template) {


    navbar.GlobalSectionsView = base.BaseView.extend({
        template: _.template(global_sections_template),

        initialize: function () {
            this.listenTo(app.router, 'all', this.on_route);
        },

        // Preprocess the global_sections adding an active class to the current section
        global_sections: function () {
            var view = this;
            return _(this.model.global_sections).map(function (action) {
                return _.extend(action, {
                    'class': view.current_route === action.id ? 'active': ''
                });
            });
        },

        on_route: function (event) {
            var route_parts = event.split(':');
            // Only render on the main route not the overlay route.
            if (route_parts[0] !== 'route') return;
            this.current_route = route_parts[1];
            this.render();
        }
    });


    navbar.UserActionsView = base.BaseView.extend({
        template: _.template(user_actions_template),

        initialize: function () {
            this.listenTo(app, 'started', this.update_session);
            this.listenTo(app, 'login', this.login);
            this.listenTo(app, 'logout', this.logout);
            this.deferred = app.persona_deferred;
        },

        update: function () {
            var user_properties = app.session.user_properties;
            this.authenticated = !!app.session.persona;
            if (this.authenticated) {
                this.fullname = user_properties.first_name + ' ' + user_properties.last_name;
            }
        },

        user_actions: function () {
            return _.filter(this.model.user_actions, function (action) {
                return action.condition === undefined || action.condition();
            });
        },

        update_session: function (event) {
            var onlogin = _.bind(this.onlogin, this);
            var onlogout = _.bind(this.onlogout, this);
            var onready = _.bind(this.onready, this);

             $.ajax({
                url: '/session',
                type: 'GET',
                dataType: 'json'
            }).done(function (data) {
                app.session = data;
                app.session_deferred.resolve(data);
                navigator.id.watch({
                    loggedInUser: app.session.persona,
                    onlogin: onlogin,
                    onlogout: onlogout,
                    onready: onready
                });
            });
        },

        signout: function (event) {
            event.preventDefault();
            console.log('Logging out (persona)');
            navigator.id.logout();
        },

        signin: function (event) {
            event.preventDefault(); // Don't let this button submit the form
            $('.alert-error').hide(); // Hide any errors on a new submit

            var request_params = {}; // could be site name
            console.log('Logging in (persona) ');
            navigator.id.request(request_params);
        },

        onlogin: function (assertion) {
            if (!assertion) return;
            $.ajax({
                url: '/login',
                type: 'POST',
                dataType: 'json',
                data: JSON.stringify({assertion: assertion}),
                contentType: 'application/json'
            }).done(function (data) {
                window.location.reload();
            }).fail(function (xhr, status, err) {
                // If there is an error, show the error messages
                var msg, html, data, content_type;
                navigator.id.logout();
                if (status === 'error') {
                    content_type = xhr.getResponseHeader('Content-Type').split(';')[0];
                    if (content_type === 'application/json') {
                        data = JSON.parse(xhr.responseText);
                        msg = data.title + '. ' + (data.detail || '');
                    } else {
                        msg = err + '.';
                    }
                    if (xhr.status === 400 && data.detail.indexOf('CSRF') !== -1) {
                        window.location.reload();  // CSRF failure
                    } else if (xhr.status === 422) {
                        msg = data.errors[0].description;
                    } else if (xhr.status === 403) {
                        html = "Login failure. Access is restricted to ENCODE consortium members.  <a href='mailto:encode-help@lists.stanford.edu'>Request an account</a>";
                    }
                } else {
                    msg = "Error communicating with server: " + status;
                }
                if (html) {
                    $('.alert-error').html(html).show();
                } else {
                    $('.alert-error').text("Login failure. " + msg).show();
                }
            });
        },

        onlogout: function () {
            console.log("Persona thinks we need to log out");
            if (app.session.persona === null) return;
            $.ajax({
                url: '/logout?redirect=false',
                type: 'GET',
                dataType: 'json'
            }).done(function (data) {
                window.location.reload();
            }).fail(function (xhr, status, err) {
                alert("Logout failure: "+err+" ("+status+")");
            });
        },

        onready: function () {
            this.ready = true;
            app.persona_deferred.resolve();
        },

        login: function (event) {
            app.persona_deferred.done(function () {
                $('.alert-error').hide(); // Hide any errors on a new submit
                var request_params = {}; // could be site name
                console.log('Logging in (persona) ');
                navigator.id.request(request_params);
            });
        },

        logout: function (event) {
            app.persona_deferred.done(function () {
                console.log('Logging out (persona)');
                navigator.id.logout();
            });
        }

    });

    return navbar;
});
