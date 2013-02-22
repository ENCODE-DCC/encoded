define(['exports', 'jquery', 'underscore', 'base', 'table_sorter', 'table_filter',
    'text!templates/sort_filter_table.html',
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

    // The targets home screen
    var targetHomeView = base.TableView.extend({
        template: _.template(home_template),
        row_template: _.template(row_template),
        table_header: [ 'Target',
                        'Species',
                        'External Resources',
                        'Project'
                        ],
        sort_initial: 0  // oh the index hack it burns


    },
    {
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
