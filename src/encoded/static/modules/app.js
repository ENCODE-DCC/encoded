define(['exports', 'jquery', 'underscore', 'backbone', 'base', 'home', 'antibodies', 'biosamples', 'libraries', 'targets', 'sources', 'platforms', 'experiments', 'navbar', 'generic'],
function (exports, $, _, Backbone, base, home, antibodies, biosamples, targets, sources, platforms, libraries, experiments, navbar, generic) {

    var routes = {
        home: [''],
        antibodies: ['antibodies/'],
        antibody: ['antibodies/:uuid'],
        targets: ['targets/'],
        target: ['targets/:uuid'],
        sources: ['sources/'],
        source: ['sources/:uuid'],
        biosamples: ['biosamples/'],
        biosample: ['biosamples/:uuid'],
        libraries: ['libraries/'],
        library: ['libraries/:uuid'],
        platforms: ['platforms/'],
        platform: ['platforms/:uuid'],
        experiments: ['experiments/'],
        experiment: ['experiments/:uuid'],
        generics: [
            'labs/',
            'users/',
            'documents/',
            'donors/',
            'awards/',
            'treatments/',
            'constructs/',
            'organisms/',
            'validations/',
            'antibody-lots/',
            'assays/',
            'replicates/',
            'files/'
        ],
        generic: [
            'labs/:uuid',
            'users/:uuid',
            'documents/:uuid',
            'donors/:uuid',
            'awards/:uuid',
            'treatments/:uuid',
            'constructs/:uuid',
            'organisms/:uuid',
            'validations/:uuid',
            'antibody-lots/:uuid',
            'assays/:uuid',
            'replicates/:uuid',
            'files/:uuid'
        ]
        //login: '#login'
        //logout: '#logout'
    };

    var overlay_routes = {
        edit: ['edit'],
        add:['add']
    };

    var slots = {
        content: '#content',
        navbar: '#navbar',
        overlay: '#overlay'
    };

    var app = exports;

    _.extend(app, Backbone.Events, {

        navbar_view: undefined,

        session: undefined,

        // CSRF protection
        ajaxPrefilter: function (options, original, xhr) {
            var http_method = options.type;
            var csrf_token = this.session && this.session.csrf_token;
            if (http_method === 'GET' || http_method === 'HEAD') return;
            if (!csrf_token) return;
            xhr.setRequestHeader('X-CSRF-Token', csrf_token);
        },

        start: function start() {
            $.ajaxPrefilter(_.bind(this.ajaxPrefilter, this));
            this.config = new exports.Config();
            var view_registry = this.view_registry = base.View.view_registry;
            _(routes).each(function (patterns, route_name) {
                view_registry.add_route(route_name, patterns);
            });
            _(overlay_routes).each(function (patterns, route_name) {
                view_registry.add_route(route_name, patterns, 'overlay');
            });
            _(slots).each(function (selector, slot_name) {
                view_registry.add_slot(slot_name, selector);
            });
            this.router = this.view_registry.make_router();
            // Render navbar when navigation triggers route.
            var navbar_view = new navbar.NavBarView({el: slots.navbar, model: this.config});
            view_registry.current_views['navbar'] = navbar_view;
            this.setupNavigation();
            this.trigger('started');
            console.log(view_registry);
            console.log(this.router);
        },

        setupNavigation: function setupNavigation() {
            // Trigger the initial route and enable HTML5 History API support
            Backbone.history.start({pushState: true});

            // All navigation that is relative should be passed through the navigate
            // method, to be processed by the router.  If the link has a data-bypass
            // attribute, bypass the delegation completely.
            $(document).on('click', 'a:not([data-bypass])', function click(evt) {
                if (evt.which > 1 || evt.shiftKey || evt.altKey || evt.metaKey) {
                    return;
                }
                // Get the absolute anchor href.
                console.log("anchor link clicked");
                var href = $(this).prop("href");
                // Get the absolute root.
                var root = location.protocol + "//" + location.host + '/';
                // Ensure the root is part of the anchor href, meaning it's relative.
                if (href && href.slice(0, root.length) === root) {
                    // Stop the default event to ensure the link will not cause a page
                    // refresh.
                    evt.preventDefault();
                    // `Backbone.history.navigate` is sufficient for all Routers and will
                    // trigger the correct events. The Router's internal `navigate` method
                    // calls this anyways.  The fragment is sliced from the root.
                    Backbone.history.navigate(href.slice(root.length), {trigger: true});
                }
            });
        }
    });

    exports.Config = Backbone.Model.extend({
        title: 'ENCODE',
        global_sections: [
            {id: 'home', title: 'Home', url: '/'},
            {id: 'antibodies', title: 'Antibodies', url: '/antibodies/'},
            {id: 'biosamples', title: 'Biosamples', url: '/biosamples/'},
            {id: 'targets', title: 'Targets', url: '/targets/'},
            {id: 'sources', title: 'Sources', url: '/sources/'},
            {id: 'platforms', title: 'Platforms', url: '/platforms/'},
            {id: 'experiments', title: 'Experiments', url: '/experiments/'}
        ],
        user_actions: [
            {id: 'signout', title: 'Log out', url: '#logout', bypass: 'true'}
        ],
        user_properties: undefined
    });

    return exports;
});
