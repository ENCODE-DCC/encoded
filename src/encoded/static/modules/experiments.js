define(['exports', 'jquery', 'underscore', 'base', 'table_sorter', 'table_filter',
    'text!templates/sort_filter_table.html',
    'text!templates/experiments/item.html',
    'text!templates/experiments/row.html'],
function experiments(exports, $, _, base, table_sorter, table_filter, home_template, item_template, row_template) {

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
        url: '/Experiment/'
    });

    // The targets home screen
    var experimentHomeView = base.TableView.extend({
        template: _.template(home_template),
        row_template: _.template(row_template),
        table_header: [ 'Experiments Name',
                        'Some Header - 1',
                        'Some Header - 2',
                        'Some Header - 3'
                        ],
        sort_initial: 0  // oh the index hack it burns
    },
    {
        route_name: 'experiments',
        model_factory: exports.ExperimentCollection
    });

    var experimentView = exports.ExperimentView = base.View.extend({
        initialize: function initialize(options) {
            var model = options.model;
            this.deferred = model.deferred;
        },
        template: _.template(item_template)
    }, {
        route_name: 'platform',
        model_factory: exports.Experiment
    });

    return exports;
});