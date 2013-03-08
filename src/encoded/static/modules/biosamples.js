define(['exports', 'jquery', 'underscore', 'base', 'table_sorter', 'table_filter',
    'text!templates/sort_filter_table.html',
    'text!templates/biosamples/item.html',
    'text!templates/biosamples/row.html'],
function biosamples(exports, $, _, base, table_sorter, table_filter, home_template, item_template, row_template) {

    exports.biosample_factory = function biosample_factory(attrs, options) {
        var new_obj = new base.Model(attrs, options);
        new_obj.url = '/biosamples/' + options.route_args[0];
        return new_obj;
    };

    exports.BiosampleCollection = base.Collection.extend({
        model: base.Model,
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
                        ],
        sort_initial: 2  // oh the index hack it burns


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
        model_factory: exports.biosample_factory
    });

    return exports;
});
