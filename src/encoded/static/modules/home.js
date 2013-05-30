define(['exports', 'jquery', 'underscore', 'app', 'base', 'text!templates/home.html'],
function (home, $, _, app, base, home_template) {
    'use strict';

    // The home screen
    home.HomeView = base.View.extend({
        template: _.template(home_template),
        initialize: function () {
            this.deferred = app.session_deferred;
        },
        update: function () {
            this.authenticated = !!app.session.persona;
        }
    },  {
        route_name: 'home'
    });

    return home;
});
