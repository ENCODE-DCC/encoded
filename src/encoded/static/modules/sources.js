define(['exports', 'jquery', 'underscore', 'base', 'table_sorter', 'table_filter',
    'text!templates/sources/home.html',
    'text!templates/sources/item.html',
    'text!templates/sources/row.html'],
function sources(exports, $, _, base, table_sorter, table_filter, home_template, item_template, row_template) {

    exports.Source = base.Model.extend({
        urlRoot: '/sources/',
        initialize: function initialize(attrs, options) {
            if (options && options.route_args) {
                this.id = options.route_args[0];
                this.deferred = this.fetch();
            }
        }
    });

    exports.SourceCollection = base.Collection.extend({
        model: exports.Source,
        url: '/sources/'
    });

    exports.SourceRowView = base.View.extend({
        tagName: 'tr',
        initialize: function initialize(options) {
            var model = options.model;
            this.deferred = model.deferred;
        },
        template: _.template(row_template)
    });

    // The sources home screen
    var sourcesHomeView = exports.sourcesHomeView = base.View.extend({
        row: exports.SourceRowView,
        initialize: function initialize(options) {
            var collection = options.model,
                deferred = $.Deferred();
            this.deferred = deferred;
            $.when(collection.fetch()).done(_.bind(function () {
                this.title = collection.title;
                this.description = collection.description;
                this.rows = collection.map(_.bind(function (item) {
                    var subview = new this.row({model: item});
                    $.when(subview.deferred).then(function () {
                        subview.render();
                    });
                    return subview;
                }, this));
                $.when.apply($, _.pluck(this.rows, 'deferred')).then(function () {
                    deferred.resolve();
                });
            }, this));
            // XXX .fail(...)
        },
        template: _.template(home_template),
        render: function render() {
            sourcesHomeView.__super__.render.apply(this, arguments);
            var $table = this.$el.find('table');
            var $tbody = $table.children('tbody:first');
            _.each(this.rows, function (view) {
                $tbody.append(view.el);
            });

            $table.table_sorter().table_filter();
            return this;
        }

    }, {
        route_name: 'sources',
        model_factory: exports.SourceCollection
    });

    var sourceView = exports.SourceView = base.View.extend({
        initialize: function initialize(options) {
            var model = options.model;
            this.deferred = model.deferred;
        },
        template: _.template(item_template)
    }, {
        route_name: 'source',
        model_factory: exports.Source
    });

    return exports;
});
