define(['exports', 'jquery', 'underscore', 'base', 'table_sorter', 'table_filter',
    'text!templates/sort_filter_table.html',
    'text!templates/libraries/item.html',
    'text!templates/libraries/row.html',
    'text!templates/libraries/document.html'
    ],
function libraries(exports, $, _, base, table_sorter, table_filter, home_template, item_template, row_template, document_template) {

    exports.library_factory = function library_factory(attrs, options) {
        var new_obj = new base.Model(attrs, options);
        new_obj.url = '/libraries/' + options.route_args[0];
        return new_obj;
    };

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


    exports.DocumentView = base.View.extend({
        tagName: 'section',
        attributes: {'class': 'type-document view-detail panel'},
        initialize: function initialize(options) {
            var model = options.model;
            this.deferred = model.deferred;
        },
        template: _.template(document_template)
    });

    var LibraryView = exports.LibraryView = base.View.extend({
        document: exports.DocumentView,
        initialize: function initialize(options) {
            var model = options.model,
                deferred = $.Deferred();
            this.deferred = deferred;
            model.deferred = model.fetch();
            $.when(model.deferred).done(_.bind(function () {
                this.documents = _.map(model.links.documents, _.bind(function (item) {
                    item.deferred = item.fetch();
                    var subview = new this.document({model: item});
                    $.when(subview.deferred).then(function () {
                        subview.render();
                    });
                    return subview;
                }, this));
                $.when.apply($, _.pluck(this.documents, 'deferred')).then(function () {
                    deferred.resolve();
                });
            }, this));
        },
        template: _.template(item_template),
        render: function render() {
            LibraryView.__super__.render.apply(this, arguments);
            var div = this.$el.find('div.protocols');
            if(this.documents.length) div.before('<h3>Library Protocols</h3>');
            _.each(this.documents, function (view) {
                div.append(view.el);
            });
            return this;
        }
    }, {
        route_name: 'library',
        model_factory: exports.library_factory
    });
    return exports;
});