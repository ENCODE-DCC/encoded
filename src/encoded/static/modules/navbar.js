define(['exports', 'jquery', 'underscore', 'app', 'base',
    'text!templates/navbar.html'],
function navbar(exports, $, _, app, base, navbar_template) {

    // The top navbar
    exports.NavBarView = base.View.extend({
        template: _.template(navbar_template),

        initialize: function () {
            // TODO: re-renders more than necessary, should split into subviews.
            this.listenTo(app.router, 'all', this.on_route);
        },

        // Preprocess the global_sections adding an active class to the current section
        global_sections: function global_sections() {
            var view = this;
            return _(this.model.global_sections).map(function (action) {
                return _.extend(action, {
                    'class': view.current_route === action.id ? 'active': ''
                });
            });
        },

        user_actions: function user_actions() {
            return this.model.user_actions;
        },

        on_route: function on_route(evt) {
            this.current_route = evt.substring(evt.indexOf(':')+1);
            this.render();
        }

    }, {
        slot_name: 'navbar'
    });

    return exports;
});
