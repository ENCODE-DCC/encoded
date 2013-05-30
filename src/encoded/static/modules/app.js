define(['exports', 'jquery', 'underscore', 'backbone', 'base', 'home', 'antibodies', 'biosamples', 'libraries', 'targets', 'sources', 'platforms', 'experiments', 'navbar', 'generic'],
function (exports, $, _, Backbone, base, home, antibodies, biosamples, targets, sources, platforms, libraries, experiments, navbar, generic) {
    'use strict';

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
        global_sections: '#global-sections',
        user_actions: '#user-actions',
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
            this.router.on('switched:content', function () {
                // XXX The templates should be updated to always define an h1.
                $('title').text($('h1, h2').first().text() + ' - ' + $('#navbar .brand').first().text());
            });
            this.session_deferred = $.Deferred();
            this.persona_deferred = $.Deferred();
            // Render navbar when navigation triggers route.
            var global_sections_view = new navbar.GlobalSectionsView({el: slots.global_sections, model: this.config});
            view_registry.current_views['global_sections'] = global_sections_view;
            $.when(global_sections_view.deferred).done(function () {
                global_sections_view.render();
            });
            var user_actions_view = new navbar.UserActionsView({el: slots.user_actions, model: this.config});
            view_registry.current_views['user_actions'] = user_actions_view;
            $.when(user_actions_view.deferred).done(function () {
                user_actions_view.render();
            });
            this.setupNavigation();
            this.trigger('started');
            console.log(view_registry);
            console.log(this.router);

            var trigger = _.bind(this.trigger, this);
            $(document).on('click', 'a[data-trigger]', function click(evt) {
                trigger($(this).attr('data-trigger'));
            });
        },

        setupNavigation: function setupNavigation() {
            // Trigger the initial route and enable HTML5 History API support
            Backbone.history.start({pushState: true});

            // All navigation that is relative should be passed through the navigate
            // method, to be processed by the router.  If the link has a data-bypass
            // attribute, bypass the delegation completely.
            $(document).on('click', 'a[href]:not([data-bypass])', function click(evt) {
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
            {id: 'antibodies', title: 'Antibodies', url: '/antibodies/'},
            {id: 'biosamples', title: 'Biosamples', url: '/biosamples/'},
            {id: 'experiments', title: 'Experiments', url: '/experiments/'},
            {id: 'targets', title: 'Targets', url: '/targets/'}
        ],
        user_actions: [
            {id: 'signout', title: 'Sign out', trigger: 'logout'}
        ],
        user_properties: undefined
    });

    return exports;
});
