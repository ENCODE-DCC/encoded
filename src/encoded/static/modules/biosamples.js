define(['exports', 'jquery', 'underscore', 'base', 'table_sorter', 'table_filter',
    'text!templates/sort_filter_table.html',
    'text!templates/biosamples/item.html',
    'text!templates/biosamples/row.html',
    'text!templates/biosamples/document.html'
    ],
function biosamples(exports, $, _, base, table_sorter, table_filter, home_template, item_template, row_template, document_template) {

    // cannoot get factory to give correct object!
    exports.biosample_factory = function biosample_factory(attrs, options) {
        var new_obj = new base.Model(attrs, options);
        new_obj.url = '/biosamples/' + options.route_args[0];
        return new_obj;
    };

    exports.Biosample = base.Model.extend({
        urlRoot: '/biosamples/',
        initialize: function initialize(attrs, options) {
            if (options && options.route_args) {
                this.id = options.route_args[0];
                this.deferred = this.fetch();
            }
        }
    });

    var BiosampleCollection = exports.BiosampleCollection = base.Collection.extend({
        model: base.Model, // base.Model???
        url: '/biosamples/'
    });

    // The biosamples home screen
    var biosampleHomeView = exports.BiosamplesHomeView = base.TableView.extend({
        template: _.template(home_template),
        row_template: _.template(row_template),
        table_header: [ 'Accession',
                        'Term',
                        'Type',
                        'Species',
                        'Source',
                        'Submitter',
                        'Treatments',
                        'Constructs'
                        ],
        sort_initial: 2  // oh the index hack it burns
    },
    {
        route_name: 'biosamples',
        model_factory: exports.BiosampleCollection
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

    var BiosampleView = exports.BiosampleView = base.View.extend({
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
            BiosampleView.__super__.render.apply(this, arguments);
            var div = this.$el.find('div.protocols');
            if(this.documents.length) div.before('<h3>Protocols and supporting documents</h3>');
            _.each(this.documents, function (view) {
                div.append(view.el);
            });
            return this;
        }
    }, {
        route_name: 'biosample',
        model_factory: exports.biosample_factory
    });

    return exports;
});
