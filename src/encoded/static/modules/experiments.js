define(['exports', 'jquery', 'underscore', 'base', 'table_sorter', 'table_filter',
    'text!templates/sort_filter_table.html',
    'text!templates/experiments/item.html',
    'text!templates/experiments/row.html',
     'text!templates/experiments/document.html'],
function experiments(exports, $, _, base, table_sorter, table_filter, home_template, item_template, row_template, document_template) {
    'use strict';

    // The experiments home screen
    var experimentHomeView = base.TableView.extend({
        template: _.template(home_template),
        row_template: _.template(row_template),
        table_header: [ 'Accession',
                        'Assay Type',
                        'Target',
                        'Biosample',
                        'Biological Replicates',
                        'Files',
                        'Lab',
                        'Project'
                        ],
        sort_initial: 1
    },
    {
        profile: '/profiles/experiment_collection'
    });

    exports.DocumentView = base.View.extend({
        tagName: 'section',
        attributes: {'class': 'type-document view-detail panel'},
        initialize: function initialize(options) {
            var model = options.model;
            this.deferred = model.deferred;
        },
        template: _.template(document_template)
    });

    var ExperimentView = exports.ExperimentView = base.View.extend({
        document: exports.DocumentView,
        initialize: function initialize(options) {
            var model = options.model,
                deferred = $.Deferred();
            this.deferred = deferred;
            //model.deferred = model.fetch();
            $.when(model.deferred).done(_.bind(function () {
                if(model.links.replicates.length) {
                    this.documents = _.map(model.links.replicates[0].links.library.links.documents, _.bind(function (item) {
                        item.deferred = item.fetch();
                        var subview = new this.document({model: item});
                        $.when(subview.deferred).then(function () {
                            subview.render();
                        });
                        return subview;
                    }, this));
                }
                $.when.apply($, _.pluck(this.documents, 'deferred')).then(function () {
                    deferred.resolve();
                });
            }, this));
        },
        template: _.template(item_template),
        render: function render() {
            ExperimentView.__super__.render.apply(this, arguments);
            if(this.documents) {
                var div = this.$el.find('div.protocols');
                if(this.documents.length) div.before('<h3>Protocols</h3>');
                _.each(this.documents, function (view) {
                    div.append(view.el);
                });
            }
            return this;
        }
    }, {
        profile: '/profiles/experiment'
    });

    return exports;
});