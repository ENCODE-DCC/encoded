define(['exports', 'jquery', 'underscore', 'base', 'text!templates/home.html'],
function home(exports, $, _, base, home_template) {

    // The home screen
    exports.HomeView = base.View.extend({
    	section_id: 'home',
        template: _.template(home_template)
    });

    return exports;
});
