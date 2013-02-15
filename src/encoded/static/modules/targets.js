define(['exports', 'jquery', 'underscore', 'base', 'table_sorter', 'table_filter',
    'text!templates/targets/home.html',
    'text!templates/targets/item.html',
    'text!templates/targets/row.html'],
function targets(exports, $, _, base, table_sorter, table_filter, home_template, item_template, row_template) {

    exports.Target = base.Model.extend({
        urlRoot: '/targets/',
        initialize: function initialize(attrs, options) {
            if (options && options.route_args) {
                this.id = options.route_args[0];
                this.deferred = this.fetch();
            }
        }
    });

    exports.TargetCollection = base.Collection.extend({
        model: exports.Target,
        url: '/targets/'
    });

    exports.TargetRowView = base.View.extend({
        tagName: 'tr',
        initialize: function initialize(options) {
            var model = options.model;
            this.deferred = model.deferred;
        },
        template: _.template(row_template)
    });

    // The targets home screen
    var targetsHomeView = exports.targetsHomeView = base.View.extend({
        row: exports.TargetRowView,
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
            targetsHomeView.__super__.render.apply(this, arguments);
            var $table = this.$el.find('table');
            var $tbody = $table.children('tbody:first');
            _.each(this.rows, function (view) {
                $tbody.append(view.el);
            });

            $table.table_sorter().table_filter();
            return this;
        }

    }, {
        route_name: 'targets',
        model_factory: exports.TargetCollection
    });

    var targetView = exports.TargetView = base.View.extend({
        initialize: function initialize(options) {
            var model = options.model;
            this.deferred = model.deferred;
        },
        template: _.template(item_template),
        render: function render() {
            targetView.__super__.render.apply(this,arguments);
            var $data_display = this.$el.find("#target-data");
            var props = this.model.toJSON();
            var display_map = [
                { 'Target Name': props.target_label },
                { 'Target Gene': props.target_gene_name },
                { 'UniProt Id' : props.taret_term_uniprot},
                { 'Species': this.model.links.organism.get('organism_name') },
                { 'Target Class': props.target_class || 'None'},
                { 'Project' : props.project },
                { 'Created By' : props.created_by + ' ( ' + props['lab pi'] + '-' + props.grant + ' )'},
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
        route_name: 'target',
        model_factory: exports.Target
    });

    return exports;
});
