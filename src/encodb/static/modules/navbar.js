define(['exports', 'jquery', 'underscore', 'base',
    'text!templates/navbar/navbar.html'],
function antibodies(exports, $, _, base, navbar_template) {

    // The antibodies screen
    exports.NavBarView = base.View.extend({
        template: _.template(navbar_template)
    });

    return exports;
});
