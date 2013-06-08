define(['exports', 'jquery', 'underscore', 'base', 'table_sorter', 'table_filter',
    'text!templates/sort_filter_table.html',
    'text!templates/sources/item.html',
    'text!templates/sources/row.html'],
function sources(exports, $, _, base, table_sorter, table_filter, home_template, item_template, row_template) {
    'use strict';

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
        profile: '/profiles/source_collection'
    });

    var sourceView = exports.SourceView = base.View.extend({
        template: _.template(item_template)
    }, {
        profile: 'source'
    });
    return exports;
});
