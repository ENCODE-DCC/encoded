define(['exports', 'jquery', 'underscore', 'base',
    'text!templates/antibodies/home.html',
    'text!templates/antibodies/item.html',
    'text!templates/antibodies/row.html'],
function antibodies(exports, $, _, base, home_template, item_template, row_template) {

    exports.Antibody = base.Model.extend({
        urlRoot: '/antibodies/',
        initialize: function initialize(attrs, options) {
            if (options && options.route_args) {
                this.id = options.route_args[0];
                this.deferred = this.fetch();
            }
        }
    });

    exports.AntibodyCollection = base.Collection.extend({
        model: exports.Antibody,
        url: '/antibodies/'
    });

    exports.AntibodyRowView = base.View.extend({
        tagName: 'tr',
        initialize: function initialize(options) {
            var model = options.model;
            this.deferred = model.deferred;
        },
        template: _.template(row_template)
    });

    // The antibodies home screen
    var AntibodiesHomeView = exports.AntibodiesHomeView = base.View.extend({
        row: exports.AntibodyRowView,
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
            AntibodiesHomeView.__super__.render.apply(this, arguments);
            var table = this.$el.find('tbody');
            _.each(this.rows, function (view) {
                table.append(view.el);
            });
            return this;
        }

    }, {
        route_name: 'antibodies',
        model_factory: exports.AntibodyCollection
    });

    exports.AntibodyView = base.View.extend({
        initialize: function initialize(options) {
            var model = options.model;
            this.deferred = model.deferred;
        },
        template: _.template(item_template)
    }, {
        route_name: 'antibody',
        model_factory: exports.Antibody
    });

    return exports;
});
