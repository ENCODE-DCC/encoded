define(['exports', 'jquery', 'underscore', 'app', 'base',
    'text!templates/login.html'],
function session_module(exports, $, _, app, base, navbar_template) {

    var session = exports;
    _.extend(session, Backbone.Events);

    // The top navbar
    exports.NavBarView = base.View.extend({
        template: _.template(navbar_template),

        initialize: function () {
            // TODO: re-renders more than necessary, should split into subviews.
            app.router.on('all', this.render, this);
        },

        // Preprocess the global_sections adding an active class to the current section
        global_sections: function global_sections() {
            return _(this.model.global_sections).map(function (action) {
                return _.extend(action, {
                    'class': app.content_view.section_id === action.id ? 'active': ''
                });
            });
        },

        user_actions: function user_actions() {
            return this.model.user_actions;
        }
    });

    return session;
});