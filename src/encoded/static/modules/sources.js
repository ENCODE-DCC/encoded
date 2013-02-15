define(['exports', 'jquery', 'underscore', 'base', 'table_sorter', 'table_filter',
    'text!templates/sources/home.html',
    'text!templates/sources/item.html',
    'text!templates/sources/row.html'],
function sources(exports, $, _, base, table_sorter, table_filter, home_template, item_template, row_template) {

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

    exports.SourceRowView = base.View.extend({
        tagName: 'tr',
        initialize: function initialize(options) {
            var model = options.model;
            this.deferred = model.deferred;
        },
        template: _.template(row_template)
    });

    // The sources home screen
    var sourcesHomeView = exports.sourcesHomeView = base.View.extend({
        row: exports.SourceRowView,
        initialize: function initialize(options) {
            var collection = options.model,
                deferred = $.Deferred();
            this.deferred = deferred;
            $.when(collection.fetch()).done(_.bind(function () {
                this.title = collection.title;
                this.description = collection.description;
                this.rows = collection.map(_.bind(function (item) {
                    var subview = new this.row({model: item});
                    $.when(subview.deferred).then(function () {
                        subview.render();
                    });
                    return subview;
                }, this));
                $.when.apply($, _.pluck(this.rows, 'deferred')).then(function () {
                    deferred.resolve();
                });
            }, this));
            // XXX .fail(...)
        },
        template: _.template(home_template),
        render: function render() {
            sourcesHomeView.__super__.render.apply(this, arguments);
            var $table = this.$el.find('table');
            var $tbody = $table.children('tbody:first');
            _.each(this.rows, function (view) {
                $tbody.append(view.el);
            });

            $table.table_sorter().table_filter();
            return this;
        }

    }, {
        route_name: 'sources',
        model_factory: exports.SourceCollection
    });

    var sourceView = exports.SourceView = base.View.extend({
        initialize: function initialize(options) {
            var model = options.model;
            this.deferred = model.deferred;
        },
        template: _.template(item_template),
        render: function render() {
            sourceView.__super__.render.apply(this,arguments);
            var $data_display = this.$el.find("#source-data");
            var props = this.model.toJSON();
            var display_map = [
                { 'Source Name': props.source_name },
                { 'Alias': props.alias || "None"},
                { 'URL' : props.url},
                { 'Project' : props.created_by }, // note this might need a real created by field
                { 'Date Created' : props.date_created }
            ];
            _.each(display_map, function(entry) {
                label = _.keys(entry)[0];
                data = _.values(entry)[0];
                var $group = $(document.createElement('div')).addClass('data-group');
                var $label = $(document.createElement('label')).addClass('data-label').attr('for','source-name');
                $label.text(label+":");
                var data_id = label.toLowerCase().replace(/[\s_]+/g,'-');
                var $values = $(document.createElement('div')).addClass('data-values');
                var $value = $(document.createElement('span')).attr('id','data_id').addClass('data-point').text(data);
                $values.html($value);
                $group.html($label);
                $group.append($values);
                $data_display.append($group);
            });
        }

    }, {
        route_name: 'source',
        model_factory: exports.Source
    });

    return exports;
});
