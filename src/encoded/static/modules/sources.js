define(['exports', 'jquery', 'underscore', 'base', 'table_sorter', 'table_filter',
    'text!templates/sort_filter_table.html',
    'text!templates/sources/item.html',
    'text!templates/sources/row.html'],
function sources(exports, $, _, base, table_sorter, table_filter, home_template, item_template, row_template) {
    'use strict';

    exports.Source = base.Model.extend({
        urlRoot: '/sources/',
        initialize: function initialize(attrs, options) {
            if (options && options.route_args) {
                this.id = options.route_args[0];
                this.deferred = this.fetch();
            }
        }
    });

    exports.SourceCollection = base.Collection.extend({
        model: exports.Source,
        url: '/sources/'
    });

    // The sources home screen
    var sourcesHomeView = exports.sourcesHomeView = base.TableView.extend({
        template: _.template(home_template),
        row_template: _.template(row_template),
        table_header: [
                       'Alias',
                       'Source (Vendor)'
                      ],
        sort_initial: 0  // oh the index hack it burns


    }, {
        route_name: 'sources',
        model_factory: exports.SourceCollection
    });

    var sourceView = exports.SourceView = base.View.extend({
        initialize: function initialize(options) {
            var model = options.model;
            this.deferred = model.deferred;
        },
        template: _.template(item_template)
    }, {
        route_name: 'source',
        model_factory: exports.Source
    });
    return exports;
});
