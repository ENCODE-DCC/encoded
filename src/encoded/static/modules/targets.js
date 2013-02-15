define(['exports', 'jquery', 'underscore', 'base', 'table_sorter', 'table_filter',
    'text!templates/targets/home.html',
    'text!templates/targets/item.html',
    'text!templates/targets/row.html'],
function targets(exports, $, _, base, table_sorter, table_filter, home_template, item_template, row_template) {

    exports.Target = base.Model.extend({
        urlRoot: '/targets/',
        initialize: function initialize(attrs, options) {
            if (options && options.route_args) {
                this.id = options.route_args[0];
                this.deferred = this.fetch();
            }
        }
    });

    exports.TargetCollection = base.Collection.extend({
        model: exports.Target,
        url: '/targets/'
    });

    exports.TargetRowView = base.View.extend({
        tagName: 'tr',
        initialize: function initialize(options) {
            var model = options.model;
            this.deferred = model.deferred;
        },
        template: _.template(row_template)
    });

    // The targets home screen
    var targetsHomeView = exports.targetsHomeView = base.View.extend({
        row: exports.TargetRowView,
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
            targetsHomeView.__super__.render.apply(this, arguments);
            var $table = this.$el.find('table');
            var $tbody = $table.children('tbody:first');
            _.each(this.rows, function (view) {
                $tbody.append(view.el);
            });

            $table.table_sorter().table_filter();
            return this;
        }

    }, {
        route_name: 'targets',
        model_factory: exports.TargetCollection
    });

    var targetView = exports.TargetView = base.View.extend({
        initialize: function initialize(options) {
            var model = options.model;
            this.deferred = model.deferred;
        },
        template: _.template(item_template)
    }, {
        route_name: 'target',
        model_factory: exports.Target
    });

    return exports;
});
