/** @jsx React.DOM */
'use strict';
var React = require('react');
var ReactForms = require('react-forms');
var fetched = require('./fetched');
var Form = require('./form').Form;
var globals = require('./globals');
var LayoutType = require('./page').LayoutType;
var Layout = require('./layout').Layout;
var ObjectPicker = require('./inputs').ObjectPicker;
var FileInput = require('./inputs').FileInput;
var audit = require('./audit');
var _ = require('underscore');

var AuditIndicators = audit.AuditIndicators;
var AuditDetail = audit.AuditDetail;
var AuditMixin = audit.AuditMixin;


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
    mixins: [AuditMixin],
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
                        <div className="status-line">
                            <AuditIndicators context={context} key="biosample-audit" />
                        </div>
                    </div>
                </header>
                <AuditDetail context={context} key="biosample-audit" />
                <div className="row item-row">
                    <div className="col-sm-12">
                        {context.description ? <p className="description">{context.description}</p> : null}
                    </div>
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
            <section className="col-sm-12">
                <div className={itemClass}>
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


var jsonSchemaToFormSchema = function(p, props) {
    if (props === undefined) {
        props = {};
    }
    if (p.title) props.label = p.title;
    if (p.description) props.hint = p.description;
    if (p.type == 'object') {
        if (required) props.component = <ReactForms.Fieldset className="required" />;
        if (p.formInput == 'file') {
            props.input = <FileInput />;
            return ReactForms.schema.Property(props);
        } else if (p.formInput == 'layout') {
            props.type = LayoutType;
            props.input = <Layout editable={true} />;
            return ReactForms.schema.Property(props);
        }
        var properties = [];
        for (var name in p.properties) {
            if (name == 'uuid') continue;
            var required = _.contains(p.required || [], name);
            properties.push(jsonSchemaToFormSchema(p.properties[name], {name: name, required: required}));
        }
        return ReactForms.schema.Schema(props, properties);
    } else if (p.type == 'array') {
        if (props.required) props.component = <ReactForms.RepeatingFieldset className="required" />;
        return ReactForms.schema.List(props, jsonSchemaToFormSchema(p.items));
    } else {
        if (props.required) props.component = <ReactForms.Field className="required" />;
        if (p.pattern) {
            props.validate = function(v) { return v.match(p.pattern); };
        }
        if (p['enum']) {
            var options = p['enum'].map(v => <option value={v}>{v}</option>);
            if (!props.required) {
                options = [<option value={null} />].concat(options);
            }
            props.input = <select className="form-control">{options}</select>;
        }
        if (p.linkTo) {
            var restrictions = {type: [p.linkTo]};
            props.input = (
                <ObjectPicker searchBase={"?mode=picker&type=" + p.linkTo} restrictions={restrictions} />
            );
        }
        if (p.type == 'integer' || p.type == 'number') {
            props.type = 'number';
        }
        if (props.name == 'schema_version') {
            props.input = <input type="text" disabled />;
        }
        return ReactForms.schema.Property(props);
    }
};


var jsonSchemaToDefaultValue = function(schema) {
    var defaultValue = {};
    _.each(schema.properties, function(property, name) {
        if (property['default'] !== undefined) {
            defaultValue[name] = property['default'];
        }
    });
    return defaultValue;
};


var ItemEdit = module.exports.ItemEdit = React.createClass({
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-item');
        var title = globals.listing_titles.lookup(context)({context: context});
        var action, form, schemaUrl;
        if (context['@type'][0].indexOf('_collection') !== -1) {  // add form
            title = title + ': Add';
            schemaUrl = context.actions[0].profile;
            action = context['@id'];
            form = (
                <fetched.FetchedData>
                    <fetched.Param name="defaultValue" url={schemaUrl} converter={jsonSchemaToDefaultValue} />
                    <fetched.Param name="schema" url={schemaUrl} converter={jsonSchemaToFormSchema} />
                    {this.transferPropsTo(<Form action={action} method="POST" />)}
                </fetched.FetchedData>
            );
        } else {  // edit form
            title = 'Edit ' + title;
            var url = this.props.context['@id'] + '?frame=edit';
            schemaUrl = '/profiles/' + context['@type'][0] + '.json';
            action = this.props.context['@id'];
            form = (
                <fetched.FetchedData>
                    <fetched.Param name="defaultValue" url={url} etagName="etag" />
                    <fetched.Param name="schema" url={schemaUrl} converter={jsonSchemaToFormSchema} />
                    {this.transferPropsTo(<Form action={action} method="PUT" />)}
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
                {form}
            </div>
        );
    }
});

globals.content_views.register(ItemEdit, 'item', 'edit');
globals.content_views.register(ItemEdit, 'collection', 'add');
