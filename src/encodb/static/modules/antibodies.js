define(['exports', 'jquery', 'underscore', 'base',
    'text!templates/antibodies/home.html'],
function antibodies(exports, $, _, base, home_template) {

    // The antibodies home screen
    exports.AntibodiesHomeView = base.View.extend({
        template: _.template(home_template)
    });

    return exports;
});
