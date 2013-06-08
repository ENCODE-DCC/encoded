define(['exports', 'jquery', 'underscore', 'base', 'table_sorter', 'table_filter',
    'text!templates/sort_filter_table.html',
    'text!templates/generic_item.html',
    'text!templates/generic_row.html'],
function generic(exports, $, _, base, table_sorter, table_filter, home_template, item_template, row_template) {
    'use strict';

    // The generics home screen
    var genericHomeView = base.TableView.extend({
        template: _.template(home_template),
        row_template: _.template(row_template),
        table_header: [
                                ],
        sort_initial: 0  // oh the index hack it burns

    },
    {
        profile: '/profiles/collection'
    });

    var genericView = exports.GenericView = base.View.extend({
        template: _.template(item_template)
    }, {
        profile: '/profiles/item'
    });

    return exports;
});
