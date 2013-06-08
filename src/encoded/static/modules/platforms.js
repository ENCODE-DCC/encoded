define(['exports', 'jquery', 'underscore', 'base', 'table_sorter', 'table_filter',
    'text!templates/sort_filter_table.html',
    'text!templates/platforms/item.html',
    'text!templates/platforms/row.html'],
function platforms(exports, $, _, base, table_sorter, table_filter, home_template, item_template, row_template) {
    'use strict';

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
        profile: '/profiles/platform_collection'
    });

    var platformView = exports.PlatformView = base.View.extend({
        template: _.template(item_template)
    }, {
        profile: '/profiles/platform'
    });

    return exports;
});