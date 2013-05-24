define(['exports', 'jquery', 'underscore', 'base', 'table_sorter', 'table_filter',
    'text!templates/sort_filter_table.html',
    'text!templates/experiments/item.html',
    'text!templates/experiments/row.html',
     'text!templates/experiments/document.html'],
function experiments(exports, $, _, base, table_sorter, table_filter, home_template, item_template, row_template, document_template) {

    exports.experiment_factory = function experiment_factory(attrs, options) {
        var new_obj = new base.Model(attrs, options);
        new_obj.url = '/experiments/' + options.route_args[0];
        return new_obj;
    };

    exports.Experiment = base.Model.extend({
        urlRoot: '/experiments/',
        initialize: function initialize(attrs, options) {
            if (options && options.route_args) {
                this.id = options.route_args[0];
                this.deferred = this.fetch();
            }
        }
    });

    exports.ExperimentCollection = base.Collection.extend({
        model: exports.Experiment,
        url: '/experiments/'
    });

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
        route_name: 'experiments',
        model_factory: exports.ExperimentCollection
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
            model.deferred = model.fetch();
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
        route_name: 'experiment',
        model_factory: exports.experiment_factory
    });
    return exports;
});