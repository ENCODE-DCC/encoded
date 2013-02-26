define(['exports', 'jquery', 'underscore', 'base', 'table_sorter', 'table_filter',
    'text!templates/sort_filter_table.html',
    'text!templates/biosamples/item.html',
    'text!templates/biosamples/row.html'],
function biosamples(exports, $, _, base, table_sorter, table_filter, home_template, item_template, row_template) {

    exports.Biosample = base.Model.extend({
        urlRoot: '/biosamples/',
        initialize: function initialize(attrs, options) {
            if (options && options.route_args) {
                this.id = options.route_args[0];
                this.deferred = this.fetch();
            }
        }
    });

    exports.BiosampleCollection = base.Collection.extend({
        model: exports.Biosample,
        url: '/biosamples/'
    });

    // The biosamples home screen
    var biosampleHomeView = base.TableView.extend({
        template: _.template(home_template),
        row_template: _.template(row_template),
        table_header: [ 'Accession',
                        'Term',
                        'Type',
                        'Species',
                        'Source',
                        'Submitter',
                        'Status'
                        ],
        sort_initial: 0  // oh the index hack it burns


    },
    {
        route_name: 'biosamples',
        model_factory: exports.BiosampleCollection
    });

    var biosampleView = exports.BiosampleView = base.View.extend({
        initialize: function initialize(options) {
            var model = options.model;
            this.deferred = model.deferred;
        },
        template: _.template(item_template)
    }, {
        route_name: 'biosample',
        model_factory: exports.Biosample
    });

    return exports;
});
