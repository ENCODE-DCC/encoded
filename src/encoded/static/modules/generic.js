define(['exports', 'jquery', 'underscore', 'base', 'table_sorter', 'table_filter',
    'text!templates/sort_filter_table.html',
    'text!templates/generic_item.html',
    'text!templates/generic_row.html'],
function generic(exports, $, _, base, table_sorter, table_filter, home_template, item_template, row_template) {
    'use strict';

    exports.generic_factory = function generic_factory(attrs, options) {
        var new_obj = new exports.Generic(attrs, options);
        return new_obj;
    };

    exports.Generic = base.Model.extend({
        initialize: function initialize(attrs, options) {

            if (options && options.route_args) {
                this.url = "/"+options.route_args[1]+options.route_args[0];
                this.id = options.route_args[0];
                this.deferred = this.fetch();
            }
        }
    });

    exports.GenericCollection = base.Collection.extend({
        model: exports.Generic,
        url: undefined, // must be set!
        initialize: function initialize(attrs, options) {
           this.url = '/'+options.route_args[0];
        }
    });

    // The generics home screen
    var genericHomeView = base.TableView.extend({
        template: _.template(home_template),
        row_template: _.template(row_template),
        table_header: [
                                ],
        sort_initial: 0  // oh the index hack it burns

    },
    {
        route_name: 'generics',
        model_factory: exports.GenericCollection
    });

    var genericView = exports.GenericView = base.View.extend({
        initialize: function initialize(options) {
            var model = options.model;
            this.deferred = model.deferred;
        },
        template: _.template(item_template)
    }, {
        route_name: 'generic',
        model_factory: exports.generic_factory
    });

    return exports;
});
