define(['exports', 'jquery', 'underscore', 'navigator', 'app', 'base',
    'text!templates/navbar.html'],
function (navbar, $, _, navigator, app, base, navbar_template) {

    function reload() {
        var url = window.location.href;
        window.history.replaceState(null, document.title, '#reloading');
        window.location.replace(url);
    }

    // The top navbar
    navbar.NavBarView = base.View.extend({
        template: _.template(navbar_template),

        initialize: function () {
            // TODO: re-renders more than necessary, should split into subviews.
            console.log("Initializing navbar");
            this.listenTo(app.router, 'all', this.on_route);
            this.listenTo(app, 'started', this.update_session);
            this.listenTo(app, 'user-ready', this.render);
            this.ready = false;
        },

        update: function () {
            var user_properties = app.session.user_properties;
            this.authenticated = !!app.session.persona;
            if (this.authenticated) {
                this.fullname = user_properties.first_name + ' ' + user_properties.last_name;
            }
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

        user_actions: function () {
            return _.filter(this.model.user_actions, function (action) {
                return action.condition === undefined || action.condition();
            });
        },

        events: {
            "click #signin": "signin",
            "click #signout": "signout"
        },

        on_route: function (event) {
            var route_parts = event.split(':');
            // Only render on the main route not the overlay route.
            if (route_parts[0] !== 'route') return;
            this.current_route = route_parts[1];
            if (this.ready) this.render();
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
            }).done(reload).fail(function (xhr, status, err) {
                // If there is an error, show the error messages
                var msg = "Login Failure.  Access is restricted to ENCODE consortium members.  <a href='mailto:encode-help@lists.stanford.edu'>Request an account</a>";
                $('.alert-error').html(msg).show();
                console.log("Persona error: "+err+" ("+status+")");
                navigator.id.logout();
            });
        },

        onlogout: function () {
            console.log("Persona thinks we need to log out");
            if (app.session.persona === null) return;
            $.ajax({
                url: '/logout?redirect=false',
                type: 'GET',
                dataType: 'json'
            }).done(reload).fail(function (xhr, status, err) {
                alert("Logout failure: "+err+" ("+status+")");
            });
        },

        onready: function () {
            this.ready = true;
            app.trigger('user-ready');
        }
    },
    {
        slot_name: 'navbar'
    });


    return navbar;
});
