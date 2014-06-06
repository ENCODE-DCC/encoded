/** @jsx React.DOM */
'use strict';
var React = require('react');
var ReactForms = require('react-forms');
var Layout = require('./layout').Layout;
var globals = require('./globals');
var ItemEdit = require('./item').ItemEdit;


var Page = module.exports.Page = React.createClass({
    render: function() {
        return (
            <div>
                {this.props.actions}
                <Layout value={this.props.context.layout} />
            </div>
        );
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


var PageEdit = React.createClass({
    render: function() {
        return this.transferPropsTo(<ItemEdit context={this.props.context} schema={PageFormSchema} />);
    }
});

globals.content_views.register(PageEdit, 'page', 'edit');
globals.content_views.register(PageEdit, 'page_collection', 'add');
