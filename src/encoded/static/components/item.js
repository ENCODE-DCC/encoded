/** @jsx React.DOM */
'use strict';
var React = require('react');
var ReactForms = require('react-forms');
var fetched = require('./fetched');
var Form = require('./form').Form;
var globals = require('./globals');
var LayoutType = require('./page').LayoutType;
var Layout = require('./layout').Layout;
var ItemPreview = require('./inputs').ItemPreview;
var ObjectPicker = require('./inputs').ObjectPicker;
var FileInput = require('./inputs').FileInput;
var _ = require('underscore');
var cx = require('react/lib/cx');


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


var RepeatingItem = React.createClass({

  render: function() {
    return this.transferPropsTo(
      <div className="rf-RepeatingFieldset__item">
        {this.props.children}
        <button
          onClick={this.onRemove}
          type="button"
          className="rf-RepeatingFieldset__remove">&times;</button>
      </div>
    );
  },

  onRemove: function() {
    if (this.props.children.constructor.displayName.indexOf('Fieldset') !== -1) {
        var label;
        try {
            label = this.props.children.props.schema.props.label;
        } catch (e) {
            label = 'item';
        }
        if (!confirm('Are you sure you want to remove this ' + label + '?')) {
            return false;
        }
    }
    if (this.props.onRemove) {
      this.props.onRemove(this.props.name);
    }
  }

});


var FetchedFieldset = React.createClass({
    mixins: [ReactForms.FieldsetMixin],

    getInitialState: function() {
        var value = this.value().value;
        var url = typeof value == 'string' ? value : null;
        var externalValidation = this.externalValidation();
        var failure = externalValidation.validation.failure;
        return {
            url: url,
            collapsed: url && !failure,
        };
    },

    render: function() {
        var schema = this.props.schema;
        var value = this.value().value;
        var externalValidation = this.externalValidation();
        var failure = externalValidation.validation.failure;
        var url = typeof value == 'string' ? value : null;
        var preview, fieldset;

        if (this.state.url) {
            var previewUrl = '/search?mode=picker&@id=' + this.state.url;
            preview = (
                <fetched.FetchedData>
                    <fetched.Param name="data" url={previewUrl} />
                    <ItemPreview />
                </fetched.FetchedData>
            );
            fieldset = (
                <fetched.FetchedData>
                    <fetched.Param name="defaultValue" url={this.state.url + '?frame=edit'} />
                    <ReactForms.Form schema={schema} onUpdate={this.onUpdate}
                                     externalValidation={externalValidation} />
                </fetched.FetchedData>
            );
        } else {
            preview = (
                <ul className="nav result-table">
                  <li>
                    <div className="accession">{'New ' + schema.props.label}</div>
                  </li>
                </ul>
            );
            fieldset = <ReactForms.Form
                defaultValue={value} schema={schema} onUpdate={this.onUpdate}
                externalValidation={externalValidation} />;
        }

        return (
            <div className="collapsible">
                <span className="collapsible-trigger" onClick={this.toggleCollapsed}>{this.state.collapsed ? '▶ ' : '▼ '}</span>
                {failure && <ReactForms.Message>{failure}</ReactForms.Message>}
                <div style={{display: this.state.collapsed ? 'block' : 'none'}}>{preview}</div>
                <div style={{display: this.state.collapsed ? 'none' : 'block'}}>{fieldset}</div>
            </div>
        );
    },

    toggleCollapsed: function() {
        this.setState({collapsed: !this.state.collapsed});
    },

    onUpdate: function(value) {
        value['@id'] = this.state.url;
        value = this.value().updateSerialized(value);
        this.onValueUpdate(value);
    }

});


var jsonSchemaToFormSchema = function(attrs) {
    var schemas = attrs.schemas,
        p = attrs.jsonNode,
        props = attrs.props,
        id = attrs.id,
        skip = attrs.skip || [];
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
        var properties = [], name;
        for (name in p.properties) {
            if (name == 'uuid') continue;
            if (p.properties[name].calculatedProperty) continue;
            if (_.contains(skip, name)) continue;
            var required = _.contains(p.required || [], name);
            properties.push(jsonSchemaToFormSchema({
                schemas: schemas,
                jsonNode: p.properties[name],
                props: {name: name, required: required}
            }));
        }
        return ReactForms.schema.Schema(props, properties);
    } else if (p.type == 'array') {
        props.component = <ReactForms.RepeatingFieldset className={props.required ? "required" : ""} item={RepeatingItem} />;
        return ReactForms.schema.List(props, jsonSchemaToFormSchema({schemas: schemas, jsonNode: p.items}));
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
        } else if (p.linkFrom) {
            // Backrefs have a linkFrom property in the form
            // (object type).(property name)
            var a = p.linkFrom.split('.'), linkType = a[0], linkProp = a[1];
            // Get the schema for the child object, omitting the attribute that
            // refers to the parent.
            var linkFormSchema = jsonSchemaToFormSchema({
                schemas: schemas,
                jsonNode: schemas[linkType],
                skip: [linkProp]
            });
            // Use a special FetchedFieldset component which can take either an IRI
            // or a full object as its value, and render a sub-form using the child
            // object schema.
            var component = <FetchedFieldset schema={linkFormSchema} />;
            // Default value for new children needs to refer to the parent.
            var defaultValue = jsonSchemaToDefaultValue(schemas[linkType]);
            defaultValue[linkProp] = id;
            return <ReactForms.schema.Property component={component} defaultValue={defaultValue} />;
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


var FetchedForm = React.createClass({

    render: function() {
        var type = this.props.type;
        var schemas = this.props.schemas;
        var schema = jsonSchemaToFormSchema({
            schemas: schemas,
            jsonNode: schemas[type],
            id: this.props.id
        });
        var value = this.props.context || jsonSchemaToDefaultValue(schemas[type]);
        return this.transferPropsTo(<Form defaultValue={value} schema={schema} />);
    }

});


var ItemEdit = module.exports.ItemEdit = React.createClass({
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-item');
        var title = globals.listing_titles.lookup(context)({context: context});
        var action, form, schemaUrl, type;
        if (context['@type'][0].indexOf('_collection') !== -1) {  // add form
            type = context['@type'][0].substr(0, context['@type'][0].length - 11);
            title = title + ': Add';
            action = context['@id'];
            form = (
                <fetched.FetchedData>
                    <fetched.Param name="schemas" url="/profiles/" />
                    {this.transferPropsTo(<FetchedForm context={null} type={type} action={action} method="POST" />)}
                </fetched.FetchedData>
            );
        } else {  // edit form
            type = context['@type'][0];
            title = 'Edit ' + title;
            var id = this.props.context['@id'];
            var url = id + '?frame=edit';
            form = (
                <fetched.FetchedData>
                    <fetched.Param name="context" url={url} etagName="etag" />
                    <fetched.Param name="schemas" url="/profiles/" />
                    {this.transferPropsTo(<FetchedForm id={id} type={type} action={id} method="PUT" />)}
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
