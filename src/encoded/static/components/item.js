/** @jsx React.DOM */
define(['exports', 'react', './globals'],
function (exports, React, globals) {
    'use strict';


    var Item = exports.Item = React.createClass({
        render: function() {
            var context = this.props.context;
            var itemClass = globals.itemClass(context, 'view-item');
            var title = globals.listing_titles.lookup(context)({context: context});
            var panel = globals.panel_views.lookup(context)();
            this.transferPropsTo(panel);
            return (
                <div className={itemClass}>
                    <header className="row">
                        <div className="span12">
                            <h2>{title}</h2>
                        </div>
                    </header>
                    <p className="description">{context.description}</p>
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


    var Panel = exports.Panel = React.createClass({
        render: function() {
            var context = this.props.context;
            var itemClass = globals.itemClass(context, 'view-detail panel');
            return (
                <section className={itemClass}>
                    <div className="container">
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


    var title = exports.title = function (props) {
        var context = props.context;
        return context.title || context.name || context.accession || context['@id'];
    };

    globals.listing_titles.register(title, 'item');


    // Also use this view as a fallback for anything we haven't registered
    globals.listing_titles.fallback = function () {
        return title;
    };


    return exports;
});
