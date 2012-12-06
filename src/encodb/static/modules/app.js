define(['exports', 'jquery', 'underscore', 'backbone', 'home', 'antibodies', 'navbar'],
function app(exports, $, _, Backbone, home, antibodies, navbar) {

    exports.Config = Backbone.Model.extend({
        title: 'ENCODE 3',
        global_sections: [
            {id: 'home', title: 'Home', url: '/'},
            {id: 'antibodies', title: 'Antibodies registry', url: '/antibodies/'}
        ],
        user_actions: [
            {id: 'login', title: 'Log in', url: '#login'}
        ]
    });

    exports.start = function start() {
        exports.config = new exports.Config();
        exports.router = new exports.Router();
        exports.setupNavigation();
        exports.navbar_view = new navbar.NavBarView({model: exports.config, el: $('#navbar')});
        exports.navbar_view.render();
    };

    exports.setupNavigation = function setupNavigation() {
        // Trigger the initial route and enable HTML5 History API support
        Backbone.history.start({pushState: true});

        // All navigation that is relative should be passed through the navigate
        // method, to be processed by the router.  If the link has a data-bypass
        // attribute, bypass the delegation completely.
        $(document).on('click', 'a:not([data-bypass])', function click(evt) {
            // Get the absolute anchor href.
            var href = {prop: $(this).prop("href"), attr: $(this).attr("href")};
            // Get the absolute root.
            var root = location.protocol + "//" + location.host + '/';
            // Ensure the root is part of the anchor href, meaning it's relative.
            if (href.prop && href.prop.slice(0, root.length) === root) {
                // Stop the default event to ensure the link will not cause a page
                // refresh.
                evt.preventDefault();

                // `Backbone.history.navigate` is sufficient for all Routers and will
                // trigger the correct events. The Router's internal `navigate` method
                // calls this anyways.  The fragment is sliced from the root.
                Backbone.history.navigate(href.attr, true);
            }
        });
    };


    // The Router is responsible for mapping URLs to views
    exports.Router = Backbone.Router.extend({

        routes: {
            '': 'routeHome',
            'antibodies/': 'routeAntibodies'
        },

        routeHome: function routeHome() {
            exports.content_view = new home.HomeView({el: $('#content')});
            exports.content_view.render();
        },

        routeAntibodies: function routeAntibodies() {
            exports.content_view = new antibodies.AntibodiesHomeView({el: $('#content')});
            exports.content_view.render();
        }

    });

    return exports;
});
