define(['exports', 'jquery', 'underscore', 'base',
    'text!templates/antibodies/home.html',
    'text!templates/antibodies/row.html'],
function antibodies(exports, $, _, base, home_template, row_template) {

    exports.Antibody = base.Model.extend();

    exports.Antibodies = base.Model.extend({
        id: 'antibodies/',
        urlRoot: '/',
        initialize: function initialize() {
            this.deferred = this.fetch();
        },
        parse: function parse(data) {
            this.actions = data.actions;
            this.links = data.links;
            this.items = new exports.AntibodyCollection(data.entities);
            return data.properties;
        }
    });

    exports.AntibodyCollection = base.SirenCollection.extend({
        model: exports.Antibody,
        url: '/antibodies/'
    });

    // The antibodies home screen
    var AntibodiesHomeView = exports.AntibodiesHomeView = base.View.extend({
        row: exports.AntibodyRowView,
        initialize: function initialize(options) {
            var model = options.model,
                deferred = $.Deferred();
            this.deferred = deferred;
            $.when(model.deferred).done(_.bind(function () {
                this.title = model.title;
                this.description = model.description;
                this.rows = _.map(model.items, _.bind(function (item) {
                    return new this.row(item);
                }, this));
                $.when.apply($, _.pluck(this.rows, 'promises')).then(function () {
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
        model_factory: exports.Antibodies
    });

    exports.AntibodyRowView= base.View.extend({
        initialize: function initialize(options) {
            var model = options.model;
            this.deferred = model.deferred;
        },
        template: _.template(row_template)
    });

    return exports;
});
