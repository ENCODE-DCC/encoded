define(['exports', 'jquery', 'underscore', 'base', 'table_sorter', 'table_filter',
    'text!templates/sort_filter_table.html',
    'text!templates/libraries/item.html',
    'text!templates/libraries/row.html'],
function libraries(exports, $, _, base, table_sorter, table_filter, home_template, item_template, row_template) {

    exports.Library = base.Model.extend({
        urlRoot: '/libraries/',
        initialize: function initialize(attrs, options) {
            if (options && options.route_args) {
                this.id = options.route_args[0];
                this.deferred = this.fetch();
            }
        }
    });

    exports.LibraryCollection = base.Collection.extend({
        model: exports.Library,
        url: '/libraries/'
    });

    var libraryHomeView = base.TableView.extend({
        template: _.template(home_template),
        row_template: _.template(row_template),
        table_header: [ 'Accession',
        				'Description',
                        'Biosample',
                        ],
        sort_initial: 0  // oh the index hack it burns
    },
    {
        route_name: 'libraries',
        model_factory: exports.LibraryCollection
    });

    var libraryView = exports.LibraryView = base.View.extend({
        initialize: function initialize(options) {
            var model = options.model;
            this.deferred = model.deferred;
        },
        template: _.template(item_template)
    }, {
        route_name: 'library',
        model_factory: exports.Library
    });

    return exports;
});