define(['exports', 'jquery', 'underscore', 'base', 'table_sorter', 'table_filter',
    'text!templates/sort_filter_table.html',
    'text!templates/antibodies/item.html',
    'text!templates/antibodies/row.html',
    'text!templates/antibodies/validation.html'],
function antibodies(exports, $, _, base, table_sorter, table_filter, home_template, item_template, row_template, validation_template) {
    'use strict';

    exports.antibody_factory = function antibody_factory(attrs, options) {
        var new_obj = new base.Model(attrs, options);
        new_obj.url = '/antibodies/' + options.route_args[0];
        return new_obj;
    };

    var AntibodyCollection = exports.AntibodyCollection = base.Collection.extend({

        model: base.Model,
        url: '/antibodies/'
    });

    // The antibodies home screen
    var AntibodiesHomeView = exports.AntibodiesHomeView = base.TableView.extend({
        template: _.template(home_template),
        row_template: _.template(row_template),
        table_header: [ 'Accession',
                        'Target',
                        'Species',
                        'Source',
                        'Product ID',
                        'Lot ID',
                        'Validations',
                        'Status'
                       ],
        sort_initial: 1  // oh the index hack it burns

    }, {
        route_name: 'antibodies',
        model_factory: exports.AntibodyCollection
    });

    exports.ValidationView = base.View.extend({
        tagName: 'section',
        attributes: {'class': 'type-validation view-detail panel'},
        initialize: function initialize(options) {
            var model = options.model;
            this.deferred = model.deferred;
        },
        update: function update() {
            var status = this.model.get('validation_status');
            if (status) {
                this.$el.addClass('status-' + status.toLowerCase());
            }
        },
        template: _.template(validation_template)
    });

    var AntibodyView = exports.AntibodyView = base.View.extend({
        attributes: {'class': 'type-antibody_approval view-detail'},
        validation: exports.ValidationView,
        initialize: function initialize(options) {
            var model = options.model,
                deferred = $.Deferred();
            this.deferred = deferred;
            model.deferred = model.fetch();
            $.when(model.deferred).done(_.bind(function () {
                this.validations = _.map(model.links.validations, _.bind(function (item) {
                    item.deferred = item.fetch();
                    var subview = new this.validation({model: item});
                    $.when(subview.deferred).then(function () {
                        subview.render();
                    });
                    return subview;
                }, this));
                $.when.apply($, _.pluck(this.validations, 'deferred')).then(function () {
                    deferred.resolve();
                });
            }, this));
            // XXX .fail(...)
        },
        template: _.template(item_template),
        update: function update() {
            var source = this.model.links.antibody_lot.links.source,
                title = source.get('source_name') + ' - ' + source.get('product_id'),
                lot_id = source.get('lot_id');
            if (lot_id) title += ' - ' + lot_id;
            this.title = title;
            var status = this.model.get('approval_status');
            if (status) {
                this.$el.addClass('status-' + status.toLowerCase());
            }
        },
        render: function render() {
            AntibodyView.__super__.render.apply(this, arguments);
            var div = this.$el.find('div.validations');
            _.each(this.validations, function (view) {
                div.append(view.el);
            });
            return this;
        }
    }, {
        route_name: 'antibody',
        model_factory: exports.antibody_factory
    });

     return exports;
});
