define(['exports', 'jquery', 'underscore', 'base',
    'text!templates/antibodies/home.html',
    'text!templates/antibodies/row.html'],
function antibodies(exports, $, _, base, home_template, row_template) {

    exports.Antibody = base.Model.extend({
        initialize: function initialize(data, options) {
            var self_href = _.find(this.links, function (item) {
                return item.rel == 'self';
            }).href;
            this.id = self_href.substr(self_href.lastIndexOf('/') + 1);
        },
        parse: function parse(data) {
            this.actions = data.actions;
            this.links = data.links;
            return data.properties;
        }
    });

    exports.Antibodies = base.Model.extend({
        id: 'antibodies',
        urlRoot: '/',
        urlTrail: '/',
        initialize: function initialize(attrs, options) {
            if (attrs === undefined) {
                this.deferred = this.fetch();
            }
        },
        parse: function parse(data) {
            this.actions = data.actions;
            this.links = data.links;
            this.items = new exports.AntibodyCollection(data, {parse: true});
            return data.properties;
        }
    });

    exports.AntibodyCollection = base.SirenCollection.extend({
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
            var model = options.model,
                deferred = $.Deferred();
            this.deferred = deferred;
            $.when(model.deferred).done(_.bind(function () {
                this.title = model.title;
                this.description = model.description;
                this.rows = model.items.map(_.bind(function (item) {
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
        model_factory: exports.Antibodies
    });

    return exports;
});
