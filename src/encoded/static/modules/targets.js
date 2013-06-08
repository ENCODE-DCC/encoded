define(['exports', 'jquery', 'underscore', 'base', 'table_sorter', 'table_filter',
    'text!templates/sort_filter_table.html',
    'text!templates/targets/item.html',
    'text!templates/targets/row.html'],
function targets(exports, $, _, base, table_sorter, table_filter, home_template, item_template, row_template) {
    'use strict';

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
        profile: '/profiles/target_collection'
    });

    var targetView = exports.TargetView = base.View.extend({
        template: _.template(item_template)
    }, {
        profile: '/profiles/target'
    });

    return exports;
});
