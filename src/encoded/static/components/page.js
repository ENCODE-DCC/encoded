/** @jsx React.DOM */
'use strict';
var React = require('react');
var ReactForms = require('react-forms');
var Form = require('./form').Form;
var Layout = require('./layout').Layout;
var FetchedData = require('./fetched').FetchedData;
var globals = require('./globals');


var Page = module.exports.Page = React.createClass({
    render: function() {
        return <Layout value={this.props.context.layout} />;
    }
});


globals.content_views.register(Page, 'page');


var Schema    = ReactForms.schema.Schema;
var Property  = ReactForms.schema.Property;

var PageFormSchema = (
    <Schema>
        <Property name="name" label="Name" />
        <Property name="title" label="Title" />
        <Property name="layout" label="Layout"
                  input={Layout({editable: true})}
                  defaultValue={{ 'rows': [ {'blocks': [ {'@type': 'richtextblock', 'data': {'body': '(new layout)'} } ]}] }} />
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
