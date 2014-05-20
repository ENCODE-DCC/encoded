/** @jsx React.DOM */
'use strict';
var React = require('react');
var ReactForms = require('react-forms');
var form = require('./form');
var FetchedData = require('./fetched').FetchedData;
var globals = require('./globals');


var Block = module.exports.Block = React.createClass({

    render: function() {
        var block = this.props.block;
        if (typeof block['@type'] == 'string') {
            block['@type'] = [block['@type'], 'block'];
        }
        var block_view = globals.block_views.lookup(block);
        return <block_view type={block['@type']} data={block.data} />;
    }
});


var Row = module.exports.Row = React.createClass({
    render: function() {
        var auto_col_class = "";
        switch (this.props.blocks.length) {
            case 2: auto_col_class = 'col-md-6'; break;
            case 3: auto_col_class = 'col-md-4'; break;
            case 4: auto_col_class = 'col-md-3'; break;
            default: auto_col_class = 'col-md-12'; break;
        }
        var blocks = this.props.blocks.map(function(block) {
            return (
                <div className={block.className || auto_col_class}>
                    <Block block={block} />
                </div>
            );
        });
        return (
            <div className="row">
                {blocks}
            </div>
        );
    }
});


var Page = module.exports.Page = React.createClass({
    render: function() {
        return <div>{this.props.context.layout.rows.map(row => <Row blocks={row.blocks} />)}</div>;
    }
});


globals.content_views.register(Page, 'page');


var Schema    = ReactForms.schema.Schema;
var Property  = ReactForms.schema.Property;
var Form      = form.Form;

var PageFormSchema = (
    <Schema>
        <Property name="name" label="Name" />
        <Property name="title" label="Title" />
    </Schema>
);


var PageEdit = module.exports.PageEdit = React.createClass({

    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-item');
        var title = globals.listing_titles.lookup(context)({context: context});
        if (context['@type'].indexOf('page_collection') !== -1) {  // add form
            title = 'Add ' + title;
            var action = this.props.context['@id'];
            var form = <Form schema={PageFormSchema} action={action} method="POST" />;
        } else {  // edit form
            title = 'Edit ' + title;
            var url = this.props.context['@id'] + '?frame=edit';
            var action = this.props.context['@id'];
            var form = <FetchedData Component={Form} url={url} schema={PageFormSchema} action={action} method="PUT" />;
        }
        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <h2>{title}</h2>
                    </div>
                </header>
                {this.transferPropsTo(form)}
            </div>
        );
    }
});


globals.content_views.register(PageEdit, 'page', 'edit');
globals.content_views.register(PageEdit, 'page_collection', 'add');
