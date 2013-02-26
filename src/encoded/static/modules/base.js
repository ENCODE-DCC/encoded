define(['exports', 'jquery', 'underscore', 'backbone', 'backbone.hal', 'assert'],
function base(exports, $, _, Backbone, HAL, assert) {

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

    // The view registry allows for a Pyramid like pattern of view registration.
    var ViewRegistry = exports.ViewRegistry = function ViewRegistry() {
        this.deferred = [];
        this.routes = {};
        this.current_views = {}; // Mapping from slot_name -> currently active view
        this.slots = {};
        this.views = {};
    };

    var DeferredRouter = exports.DeferredRouter = Backbone.Router.extend({
        route: function(route, name, callback) {
          if (!_.isRegExp(route)) route = this._routeToRegExp(route);
          if (!callback) callback = this[name];
          Backbone.history.route(route, _.bind(function(fragment) {
            var args = this._extractParameters(route, fragment);
            if (callback) $.when(callback.apply(this, args)).done(_.bind(function () {
                this.trigger.apply(this, ['route:' + name].concat(args));
                Backbone.history.trigger('route', this, name, args);
                console.log("routed: "+location.href);
            }, this)).fail(_.bind(function () {
                console.log("route failed...");
            }, this));
          }, this));
          return this;
        }
    });

    exports.view_registry = new ViewRegistry();

    _.extend(ViewRegistry.prototype, {
        add_slot: function add_slot(slot_name, selector) {
            this.slots[slot_name] = $(selector);
        },

        add_route: function add_route(route_name, pattern) {
            this.routes[route_name] = pattern;
        },

        add_view: function add_view(route_name, view_factory) {
            this.views[route_name] = view_factory;
        },

        defer: function defer(view) {
            this.deferred.push(view);
        },

        make_route_controller: function make_route_controller(view_factory, model_factory) {
            function route_controller() {
                var options = {},
                    deferred;
                if (model_factory) {
                    options.model = new_(model_factory, [null, {route_args: arguments}]);
                    // possibly redundant
                    deferred = options.model.deferred;
                }
                view = new_(view_factory, [options]);
                if (view.deferred !== undefined) deferred = view.deferred;
                $.when(deferred).done(_.bind(function () {
                    this.switch_to(view);
                }, this));
                return deferred;
            }
            return _.bind(route_controller, this);
        },

        process_deferred: function process_deferred() {
            var view_registry = this;
            _(this.deferred).each(function (view_factory) {
                var route_name = view_factory.route_name;
                if (!route_name) return;
                assert(!view_registry.views[route_name], 'route already defined for ' + route_name);
                view_registry.views[route_name] = view_factory;
                console.log("Adding view for: "+ route_name);
            });
            this.deferred = null;
        },

        make_router: function make_router(routes) {
            this.process_deferred();
            var router = this.router = new DeferredRouter();
            var rev_routes = _(this.routes).map(function (pattern, route_name) {
                return {route_name: route_name, pattern: pattern};
            }).reverse();
            var view_registry = this;
            _(rev_routes).each(function (route) {
                var view_factory = view_registry.views[route.route_name];
                assert(view_factory, 'missing view for route ' + route.route_name);
                var callback = view_registry.make_route_controller(view_factory, view_factory.model_factory);
                router.route(route.pattern, route.route_name, callback);
            });
            return router;
        },

        switch_to: function switch_to(view, no_render) {
            var slot_name = Object.getPrototypeOf(view).constructor.slot_name;
            var current_view = this.current_views[slot_name];
            if (!no_render) view.render();
            if (current_view) current_view.remove();
            if (!no_render) this.slots[slot_name].html(view.el);
            this.current_views[slot_name] = view;
        }
    });


    // Base View class implements conventions for rendering views.
    exports.View = Backbone.View.extend({
        title: undefined,
        description: undefined,

        // Views should define their own `template`
        template: undefined,

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
        slot_name: 'content'
    });

    exports.View.extend = function extend(protoProps, classProps) {
        var view = Backbone.View.extend.apply(this, arguments);
        this.view_registry.defer(view);
        return view;
    };

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
