define(['exports', 'jquery', 'underscore', 'backbone', 'backbone.hal', 'assert',
    'text!templates/modal.html'],
function base(exports, $, _, Backbone, HAL, assert, modal_template) {

    // Underscore template settings
    // `{model.title}` for escaped text
    // `<?raw variable ?>}` for raw html interpolations
    // `<?js expression ?>` for javascript evaluations
    _.templateSettings = {
          escape : /\{(.+?)\}/g,
          interpolate : /<\?raw\s+(.+?)\?>/g,
          evaluate : /<\?js\s+(.+?)\?>/g
    };

    // See: https://gist.github.com/4659318
    // Works with function or class
    function new_(factory, args) {
        var obj = Object.create(factory.prototype);
        var result = factory.apply(obj, args);
        if (result === undefined) {
          result = obj;
        }
        return result;
    }

    // Cached regex for stripping a leading hash/slash and trailing space.
    var routeStripper = /^[#\/]|\s+$/g;

    // Cached regex for removing a trailing slash.
    var trailingSlash = /\/$/;

    var OverlayHistory = exports.overlayHistory = Backbone.History.extend({
        path: null,
        constructor: function() {
            OverlayHistory.__super__.constructor.apply(this, arguments);
            this.type_handlers = {route: this.handlers, overlay: []};
        },
        // Extend with support for multiple route types
        route: function(route, callback, route_type) {
          if (!route_type) route_type = 'route';
          this.type_handlers[route_type].unshift({route: route, callback: callback});
        },
        getFragment: function(fragment, forcePushState) {
          if (fragment == null) {
            if (this._hasPushState || !this._wantsHashChange || forcePushState) {
              fragment = this.location.pathname;
              var root = this.root.replace(trailingSlash, '');
              if (!fragment.indexOf(root)) fragment = fragment.substr(root.length);
              var hash = this.getHash();
              if (hash) fragment = fragment + '#' + hash;
            } else {
              fragment = this.getHash();
            }
          }
          return fragment.replace(routeStripper, '');
        },
        loadOverlay: function(overlay) {
            _.any(this.type_handlers['overlay'], function(handler) {
                if (handler.route.test(overlay)) {
                    handler.callback(overlay);
                    return true;
                }
            });
        },
        loadUrl: function(fragmentOverride) {
            var fragment = this.fragment = this.getFragment(fragmentOverride);
            var hash_pos = fragment.indexOf('#');
            var overlay, path;
            if (hash_pos >= 0) {
                overlay = fragment.substr(hash_pos + 1);
                path = fragment.substr(0, hash_pos);
            } else {
                overlay = '';
                path = fragment;
            }
            if (path === this.path) {
                this.loadOverlay(overlay);
                return true;
            }
            this.path = path;
            var matched = _.any(this.handlers, _.bind(function(handler) {
                if (handler.route.test(path)) {
                    handler.callback(path);
                    return true;
                }
            }, this));
            if (matched) this.once('route', _.bind(this.loadOverlay, this, overlay));
            return matched;
        }
    });

    var DeferredRouter = exports.DeferredRouter = Backbone.Router.extend({
        route: function(route, name, callback, route_type) {
          if (!route_type) route_type = 'route';
          if (!_.isRegExp(route)) route = this._routeToRegExp(route);
          if (!callback) callback = this[name];
          Backbone.history.route(route, _.bind(function(fragment) {
            var args = this._extractParameters(route, fragment);
            args.push(fragment.replace(/\/.*/g, '/'));
            if (callback) $.when(callback.apply(this, args)).done(_.bind(function () {
                this.trigger.apply(this, [route_type + ':' + name].concat(args));
                Backbone.history.trigger(route_type, this, name, args);
                console.log("routed: " + route_type + " " +location.href);
            }, this)).fail(_.bind(function () {
                console.log(route_type + " route failed...");
            }, this));
          }, this), route_type);
          return this;
        }
    });

    // The view registry allows for a Pyramid like pattern of view registration.
    var ViewRegistry = exports.ViewRegistry = function ViewRegistry() {
        this.deferred = [];
        this.routes = {};
        this.current_views = {}; // Mapping from slot_name -> currently active view
        this.slots = {};
        this.views = {};
        this.initialize.apply(this, arguments);
    };

    _.extend(ViewRegistry.prototype, {
        initialize: function initialize() {
            // Replace the history object
            this.history = Backbone.history = new OverlayHistory();
            this.router = new DeferredRouter();
            // Setup the close overlay
            this.router.route('', '', function() {return null;}, 'overlay');
            this.history.on('overlay', function(router, name, args) {
                if (name === '') {
                    this.slots['overlay'].find('.modal').modal('hide');
                } else {
                    this.slots['overlay'].find('.modal').modal({keyboard: false, backdrop: 'static'});
                }
            }, this);
            $(document).keyup(function(e) {
                // esc handler - close overlay by navigating to ''
                if (e.keyCode != 27 || !location.hash) return;
                Backbone.history.navigate(location.pathname + location.search, {trigger: true});
            });

        },

        add_slot: function add_slot(slot_name, selector) {
            this.slots[slot_name] = $(selector);
        },

        add_route: function add_route(route_name, patterns, route_type) {
            if (!route_type) route_type = 'route';
            var routes = this.routes[route_type];
            if (!routes) routes = this.routes[route_type] = {};
            routes[route_name] = patterns;
        },

        defer: function defer(view) {
            this.deferred.push(view);
        },

        make_route_controller: function make_route_controller(view_factory, model_factory, slot_name) {
            function route_controller() {
                var options = {route_args: arguments},
                    deferred;
                if (model_factory) {
                    options.model = new_(model_factory, [null, options]);
                    // possibly redundant
                    deferred = options.model.deferred;
                }
                view = new_(view_factory, [options]);
                if (view.deferred !== undefined) deferred = view.deferred;
                $.when(deferred).done(_.bind(this.switch_to, this, slot_name, view));
                return deferred;
            }
            return _.bind(route_controller, this);
        },

        process_deferred: function process_deferred() {
            var view_registry = this;
            _(this.deferred).each(function (view_factory) {
                var route_name = view_factory.route_name;
                var route_type = view_factory.route_type;
                var key;
                if (route_name === undefined) return;
                if (!route_type) route_type = view_factory.route_type = 'route';
                key = [route_type, route_name];
                assert(!view_registry.views[key], 'route already defined for ' + route_type + ', ' + route_name);
                view_registry.views[key] = view_factory;
                console.log("Adding view for: " + route_type + ', ' + route_name);
            });
            this.deferred = null;
        },

        make_router: function make_router(routes) {
            this.process_deferred();
            var router = this.router;
            _.each(this.routes, _.bind(function(routes, route_type) {
                var rev_routes = _(_(routes).map(function (patterns, route_name) {
                    return _(patterns).map(function (patt) {
                        return { route_name: route_name, pattern: patt };
                    });
                })).flatten().reverse();
                _(rev_routes).each(_.bind(function (route) {
                    var view_factory = this.views[[route_type, route.route_name]];
                    assert(view_factory, 'missing view for route ' + route_type + ', ' + route.route_name);
                    var callback = this.make_route_controller(view_factory, view_factory.model_factory, view_factory.slot_name);
                    router.route(route.pattern, route.route_name, callback, route_type);
                }, this));
            }, this));
            return router;
        },

        switch_to: function switch_to(slot_name, view) {
            var current_view = this.current_views[slot_name];
            var view_html = '';
            if (view) view_html = view.render().el;
            if (current_view) current_view.remove();
            this.slots[slot_name].html(view_html);
            this.current_views[slot_name] = view;
        }
    });

    exports.view_registry = new ViewRegistry();


    // Base View class implements conventions for rendering views.
    exports.View = Backbone.View.extend({
        title: undefined,
        description: undefined,

        // Views should define their own `template`
        template: undefined,
        // surprisingly this function is necessary...
        update: function update() {},
        // Render the view
        render: function render() {
            this.update();
            var properties = this.model && this.model.toJSON();
            this.$el.html(this.template({model: this.model, properties: properties, view: this, '_': _}));
            return this;
        }

    }, {
        view_registry: exports.view_registry,
        route_type: 'route',
        slot_name: 'content'
    });

    exports.View.extend = function extend(protoProps, classProps) {
        var view = Backbone.View.extend.apply(this, arguments);
        this.view_registry.defer(view);
        return view;
    };

    exports.Modal = exports.View.extend({
        className: "modal hide fade",
        submit_button_title: "Save",
        cancel_button_title: "Cancel",
        title: undefined,

        events: {
            "click modal-footer .submit": "submit"
        },

        // Views should define their own `template`
        template: _.template(modal_template),
        // surprisingly this function is necessary...
        update: function update() {},
        // Render the view
        render: function render() {
            this.update();
            var properties = this.model && this.model.toJSON();
            this.$el.html(this.template({model: this.model, properties: properties, view: this, '_': _}));
            return this;
        },
        submit: function submit() {}
    }, {
        route_type: 'overlay',
        slot_name: 'overlay'
    });

    exports.RowView = exports.View.extend({
        tagName: 'tr',

        initialize: function initialize(options) {
            var model = options.model;
            this.deferred = model.deferred;
            this.template = options.template;
        },

        update: function update() {
            this.$el.attr('data-href', this.model.url());
            this.$el.css('cursor', 'pointer');
        }
    });

    exports.CollectionView = exports.View.extend({
        initialize: function initialize(options, type) {
            var collection = options.model,
                deferred = $.Deferred(),
                deferred2 = $.Deferred();
            this.deferred = deferred;
            this.deferred2 = deferred2;
            $.when(collection.fetch({data: {limit: 30}})).done(_.bind(function () {
                this.title = collection.title;
                this.description = collection.description;
                this.rows = collection.map(_.bind(this.render_subviews, this));
                $.when.apply($, _.pluck(this.rows, 'deferred')).then(function () {
                    deferred.resolve();
                });

            }, this));
            $.when(collection.fetch()).done(_.bind(function () {
                this.rows = collection.map(_.bind(this.render_subviews, this));
                $.when.apply($, _.pluck(this.rows, 'deferred')).then(function () {
                    deferred2.resolve();
                });
            }, this));
            deferred2.done(_.bind(function()  {
                console.log("2nd deferred");
                if (deferred.state() === 'resolved') {
                    this.render();
                } else {
                    deferred.resolve();
                }
                var $table = this.$el.find('table');
                $("#table-count").text(function(index, text) {
                    return $("#collection-table > tbody > tr").length;
                });
                $("#table-count").removeClass("label-warning").removeClass("spinner-warning").addClass("label-invert");
                $(".table-filter").removeAttr("disabled");
                $("#total-records").removeClass("hide");
                $table.table_sorter().table_filter();

            }, this));
           // XXX .fail(...)
        },

        row: exports.RowView,

        render_subviews: function (item) {
            var subview = new this.row({model: item, template: this.row_template});
            $.when(subview.deferred).then(function () {
                subview.render();
            });
            return subview;
        }
    });

    var TableView = exports.TableView = exports.CollectionView.extend({
        //row: undefined,  should be set in subclass
        render: function render() {
            console.log("Rendering table for "+this.model.attributes.title);
            TableView.__super__.render.apply(this, arguments);
            var $table = this.$el.find('table');
            var $tbody = $table.children('tbody:first');
            _.each(this.rows, function (view) {
                $tbody.append(view.el);
            });

            return this;
        },

        events: {
            "click td": "link"
        },

        link: function(event) {
            console.log("table cell clicked");
            $td = $(event.currentTarget);
            $anchs = $td.children("a");
            if ($anchs.length == 1) {
                $anchs[0].click();
                return;
            } else if ($anchs.length) {
                // can't pick anchor so do nothing
                return;
            }

            Backbone.history.navigate($td.parents("tr[data-href]").attr("data-href"), true);
        }

    });

    exports.Model = HAL.Model.extend({});

    exports.Collection = HAL.Collection.extend({
        search: function(letters) {
            if(letters === "") return this;

            var pattern = new RegExp(letters,"gi");
            return _(this.filter(function(data) {
                return pattern.test(data.get());
            }));
        }
    });

    return exports;
});
