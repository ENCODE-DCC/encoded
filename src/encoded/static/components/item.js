/** @jsx React.DOM */
'use strict';
var React = require('react');
var ReactForms = require('react-forms');
var fetched = require('./fetched');
var Form = require('./form').Form;
var globals = require('./globals');
var ObjectPicker = require('./blocks/item').ObjectPicker;


var Fallback = module.exports.Fallback = React.createClass({
    render: function() {
        var url = require('url');
        var context = this.props.context;
        var title = typeof context.title == "string" ? context.title : url.parse(this.props.href).path;
        return (
            <div className="view-item">
                <header className="row">
                    <div className="col-sm-12">
                        <h2>{title}</h2>
                    </div>
                </header>
                {typeof context.description == "string" ? <p className="description">{context.description}</p> : null}
                <section className="view-detail panel">
                    <div className="container">
                        <pre>{JSON.stringify(context, null, 4)}</pre>
                    </div>
                </section>
            </div>
        );
    }
});


var Item = module.exports.Item = React.createClass({
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-item');
        var title = globals.listing_titles.lookup(context)({context: context});
        var panel = globals.panel_views.lookup(context)();

        // Make string of alternate accessions
        var altacc = context.alternate_accessions ? context.alternate_accessions.join(', ') : undefined;

        this.transferPropsTo(panel);
        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <h2>{title}</h2>
                        {altacc ? <h4 className="repl-acc">Replaces {altacc}</h4> : null}
                    </div>
                </header>
                <div className="row">
                    {context.description ? <p className="description">{context.description}</p> : null}
                    {panel}
                </div>
            </div>
        );
    }
});

globals.content_views.register(Item, 'item');


// Also use this view as a fallback for anything we haven't registered
globals.content_views.fallback = function () {
    return Fallback;
};


var Panel = module.exports.Panel = React.createClass({
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


var title = module.exports.title = function (props) {
    var context = props.context;
    return context.title || context.name || context.accession || context['@id'];
};

globals.listing_titles.register(title, 'item');


// Also use this view as a fallback for anything we haven't registered
globals.listing_titles.fallback = function () {
    return title;
};


var jsonSchemaToFormSchema = function(p, name) {
    var props = {};
    if (name) props.name = name;
    if (p.title) props.label = p.title;
    if (p.description) props.hint = p.description;
    if (p.type == 'object') {
        var properties = [];
        for (var name in p.properties) {
            properties.push(jsonSchemaToFormSchema(p.properties[name], name));
        }
        return ReactForms.schema.Schema(props, properties);
    } else if (p.type == 'array') {
        return ReactForms.schema.List(props, jsonSchemaToFormSchema(p.items));
    } else {
        if (p.pattern) {
            props.validate = function(v) { return v.match(p.pattern) };
        }
        if (p.enum) {
            props.input = (
                <select className="form-control">
                    {p.enum.map(v => <option value={v}>{v}</option>)}
                </select>
            );
        }
        if (p.linkTo) {
            props.input = (
                <ObjectPicker searchBase={"?mode=picker&type=" + p.linkTo} />
            );
        }
        return ReactForms.schema.Property(props);
    }
}


var ItemEdit = module.exports.ItemEdit = React.createClass({
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-item');
        var title = globals.listing_titles.lookup(context)({context: context});
        var action, form;
        if (context['@type'][0].indexOf('_collection') !== -1) {  // add form
            title = 'Add ' + title;
            var schemaUrl = context.actions[0].profile;
            action = context['@id'];
            form = (
                <fetched.FetchedData Component={Form} action={action} method="POST">
                    <fetched.Fetched name="schema" url={schemaUrl} converter={jsonSchemaToFormSchema} />
                </fetched.FetchedData>
            );
        } else {  // edit form
            title = 'Edit ' + title;
            var url = this.props.context['@id'] + '?frame=edit';
            var schemaUrl = '/profiles/' + context['@type'][0] + '.json';
            action = this.props.context['@id'];
            form = (
                <fetched.FetchedData Component={Form} action={action} method="PUT">
                    <fetched.Fetched name="defaultValue" url={url} etagName="etag" />
                    <fetched.Fetched name="schema" url={schemaUrl} converter={jsonSchemaToFormSchema} />
                </fetched.FetchedData>
            );
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

globals.content_views.register(ItemEdit, 'item', 'edit');
globals.content_views.register(ItemEdit, 'collection', 'add');
