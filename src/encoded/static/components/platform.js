/** @jsx React.DOM */
define(['exports', 'react', 'globals'],
function (platform, React, globals) {
    'use strict';


    var Panel = platform.Panel = React.createClass({
        render: function() {
            var context = this.props.context;
            var itemClass = globals.itemClass(context, 'view-detail panel key-value');
            return (
                <dl class={itemClass}>
                    <dt>Platform name</dt>
                    <dd><a href="{context.url}">{context.description}</a></dd>
            
                    <dt>GEO Platform ID(s)</dt>
                    <dd>{context.gpl_ids}</dd>
                
                    <dt>OBI ID</dt>
                    <dd>{context.obi_dbxref_list}</dd>
                
                    <dt>ENCODE2 ID</dt>
                    <dd>{context.encode2_dbxref_list}</dd>
                </dl>
            );
        }
    });

    globals.panel_views.register(Panel, 'platform');


    var title = platform.title = function (props) {
        return props.context.description;
    };

    globals.listing_titles.register(title, 'platform');


    return platform;
});
