define(['exports', 'jquery', 'underscore', 'base', 'table_sorter', 'table_filter',
    'text!templates/sort_filter_table.html',
    'text!templates/platforms/item.html',
    'text!templates/platforms/row.html'],
function platforms(exports, $, _, base, table_sorter, table_filter, home_template, item_template, row_template) {

    exports.Platform = base.Model.extend({
        urlRoot: '/platforms/',
        initialize: function initialize(attrs, options) {
            if (options && options.route_args) {
                this.id = options.route_args[0];
                this.deferred = this.fetch();
            }
        }
    });

    exports.PlatformCollection = base.Collection.extend({
        model: exports.Platform,
        url: '/platforms/'
    });

    // The platforms home screen
    var platformHomeView = base.TableView.extend({
        template: _.template(home_template),
        row_template: _.template(row_template),
        table_header: [ 'Platform Name',
        				'GEO Platform ID(s)'
                        ],
        sort_initial: 0  // oh the index hack it burns
    },
    {
        route_name: 'platforms',
        model_factory: exports.PlatformCollection
    });

    var platformView = exports.PlatformView = base.View.extend({
        initialize: function initialize(options) {
            var model = options.model;
            this.deferred = model.deferred;
        },
        template: _.template(item_template)
    }, {
        route_name: 'platform',
        model_factory: exports.Platform
    });

    return exports;
});