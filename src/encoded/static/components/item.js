/** @jsx React.DOM */
define(['exports', 'react', 'globals'],
function (item, React, globals) {
    'use strict';


    var Item = item.Item = React.createClass({
        render: function() {
            var context = this.props.context;
            var itemClass = globals.itemClass(context, 'view-item');
            var title = globals.listing_titles.lookup(context)({context: context});
            var panel = globals.panel_views.lookup(context)();
            this.transferPropsTo(panel);
            return (
                <div class={itemClass}>
                    <header class="row">
                        <div class="span12">
                            <h2>{title}</h2>
                        </div>
                    </header>
                    <p class="description">{context.description}</p>
                    {panel}
                </div>
            );
        }
    });

    globals.content_views.register(Item, 'item');


    // Also use this view as a fallback for anything we haven't registered
    globals.content_views.fallback = function () {
        return Item;
    };


    var Panel = item.Panel = React.createClass({
        render: function() {
            var context = this.props.context;
            var itemClass = globals.itemClass(context, 'view-detail panel');
            return (
                <section class={itemClass}>
                    <div class="container">
                        <pre>{JSON.stringify(context, null, 4)}</pre>
                    </div>
                </section>
            );
        }
    });

    globals.panel_views.register(Panel, 'item');


    // Also use this view as a fallback for anything we haven't registered
    globals.panel_views.fallback = function () {
        return Panel;
    };


    var title = item.title = function (props) {
        var context = props.context;
        if (context.title) {
            return context.title;
        }
        for (var key in context) {
            if (key.search('accession') != -1) {
                return context[key];
            }
        }
        return context['@id'];
    };

    globals.listing_titles.register(item.generic_title, 'item');


    // Also use this view as a fallback for anything we haven't registered
    globals.listing_titles.fallback = function () {
        return title;
    };


    return item;
});
