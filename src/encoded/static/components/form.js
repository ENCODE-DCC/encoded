'use strict';
var React = require('react');
var cloneWithProps = require('react/lib/cloneWithProps');
var parseAndLogError = require('./mixins').parseAndLogError;
var closest = require('../libs/closest');
var offset = require('../libs/offset');
var fetched = require('./fetched');
var inputs = require('./inputs');
var jsonschema = require('jsonschema');
var _ = require('underscore');

var v = new jsonschema.Validator();
v.attributes.pattern = function validatePattern(instance, schema, options, ctx) {
  if (typeof instance != 'string') return;
  if (typeof schema.pattern != 'string') throw new jsonschema.SchemaError('"pattern" expects a string', schema);
  if (!instance.match(schema.pattern)) {
    return 'does not match pattern ' + JSON.stringify(schema.pattern);
  }
}

var filterValue = function(value) {
    if (Array.isArray(value)) {
        value.map(filterValue);
    } else if (typeof value == 'object') {
        _.each(value, function(v, k) {
            if (k == 'schema_version') {
                delete value[k];
            } else {
                filterValue(v);
            }
        });
    }
};

var defaultValue = function(schema) {
    if (schema.properties !== undefined) {
        var value = {};
        _.each(schema.properties, function(property, name) {
            if (property.calculatedProperty) return;
            if (!property.readonly) {
                var propertyDefault = defaultValue(property);
                if (propertyDefault !== undefined) {
                    value[name] = propertyDefault;
                }
            }
        });
        return value;
    } else if (schema.items !== undefined) {
        return schema.default || [];
    } else {
        return schema.default || undefined;
    }
};

var updateChild = function(name, subvalue) {
    var oldValue = this.props.value;
    var schema = this.props.schema;
    var newValue;
    if (schema.type === 'object') {
        newValue = Object.assign({}, oldValue);
        if (subvalue !== undefined) {
            newValue[name] = subvalue;
        } else {
            if (newValue[name] !== undefined) {
                delete newValue[name];
            }
        }
    } else if (schema.type === 'array') {
        oldValue = oldValue || [];
        newValue = oldValue.slice(0, name).concat(subvalue).concat(oldValue.slice(name + 1));
    }
    this.props.updateChild(this.props.name, newValue);
}

var RepeatingItem = React.createClass({

    contextTypes: {
        readonly: React.PropTypes.bool
    },

    render: function() {
        var { name, path, schema, value, ...props } = this.props;
        return (
          <div className="rf-RepeatingFieldset__item">
            <Field path={path} schema={schema}
                   value={value} updateChild={this.updateChild}
                   hideLabel={true} />
            {!this.context.readonly ? <button
              onClick={this.onRemove}
              type="button"
              className="rf-RepeatingFieldset__remove">&times;</button>
            : ''}
          </div>
        );
    },

    updateChild: function(name, value) {
        this.props.updateChild(this.props.name, value);
    },

    onRemove: function(e) {
        if (!confirm('Are you sure you want to remove this item?')) {
            e.preventDefault();
            return;
        }
        if (this.props.onRemove) {
          this.props.onRemove();
        }
    }

});

var RepeatingFieldset = React.createClass({

    contextTypes: {
        schemas: React.PropTypes.object,
        readonly: React.PropTypes.bool,
        id: React.PropTypes.string
    },

    getInitialState: function() {
        // counter used to make sure that we get new keys
        // once an item is removed
        return { generation: 0 };
    },

    render() {
        var { path, value, schema, onAdd, onRemove, ...props } = this.props;
        return (
            <div>
                <div className="rf-RepeatingFieldset__items">
                    {value ? value.map((value, key) => {
                        var props = {
                          key: this.state.generation + '.' + key,
                          name: key,
                          path: path + '.' + key,
                          value,
                          schema: schema.items,
                          updateChild: this.updateChild,
                          onRemove: this.onRemove.bind(null, key)
                        };
                        return <RepeatingItem {...props} />;
                    }) : ''}
                </div>
                {!this.context.readonly &&
                  <button
                    type="button"
                    onClick={this.onAdd}
                    className="rf-RepeatingFieldset__add">
                    Add
                  </button>}
            </div>
        );
    },

    updateChild,

    onAdd() {
        var subschema = this.props.schema.items;
        var newValue;
        if (subschema.linkFrom !== undefined) {
            var a = subschema.linkFrom.split('.'),
                linkType = a[0],
                linkProp = a[1];
            subschema = this.context.schemas[linkType];
            newValue = defaultValue(subschema);
            newValue[linkProp] = this.context.id;
        } else {
            newValue = defaultValue(subschema);
        }
        var value = (this.props.value || []).concat(newValue);
        this.props.updateChild(this.props.name, value);
    },

    onRemove(index) {
        var oldValue = this.props.value;
        var value = oldValue.slice(0, index).concat(oldValue.slice(index + 1));
        this.setState({ generation: this.state.generation + 1 });
        this.props.updateChild(this.props.name, value);
    }

});

var FetchedFieldset = React.createClass({

    contextTypes: {
        schemas: React.PropTypes.object,
        errors: React.PropTypes.object
    },

    childContextTypes: {
        id: React.PropTypes.string
    },

    // provide a null id to descendents,
    // to avoid following further backrefs
    getChildContext() {
        return { id: null };
    },

    getInitialState: function() {
        var schema = this.props.schema;
        // Backrefs have a linkFrom property in the form
        // (object type).(property name)
        var a = schema.linkFrom.split('.'),
            linkType = a[0],
            linkProp = a[1];
        var subschema = this.context.schemas[linkType];
        // FIXME Handle linkFrom abstract type.
        if (subschema !== undefined) {
            // The linkProp is the one that refers to the parent object.
            // This should not be shown when accessed from the parent's form.
            // Let's immutably clone the schema and delete it:
            subschema = Object.assign({}, subschema, {
                properties: Object.assign({}, subschema.properties)
            });
            delete subschema.properties[linkProp];
        }

        var value = this.props.value;
        var error = this.context.errors[this.props.path];
        var url = typeof value === 'string' ? value : null;
        return {
            schema: subschema,
            url: url,
            collapsed: url && !error
        };
    },

    render: function() {
        var schema = this.state.schema;
        var name = this.props.name;
        var value = this.props.value;
        var preview, fieldset;

        if (this.state.url) {
            var previewUrl = this.state.url;
            preview = (
                <fetched.FetchedData>
                    <fetched.Param name="data" url={previewUrl} />
                    <inputs.ItemPreview />
                </fetched.FetchedData>
            );
            fieldset = (
                <fetched.FetchedData>
                    <fetched.Param name="value" url={this.state.url + '?frame=edit'} />
                    <Field schema={schema} updateChild={this.updateChild} />
                </fetched.FetchedData>
            );
        } else {
            preview = (
                <ul className="nav result-table">
                  <li>
                    <div className="accession">{'New ' + schema.title}</div>
                  </li>
                </ul>
            );
            fieldset = <Field
                value={value} schema={schema}
                updateChild={this.updateChild} />;
        }

        return (
            <div className="collapsible">
                <span className="collapsible-trigger" onClick={this.toggleCollapsed}>{this.state.collapsed ? '▶ ' : '▼ '}</span>
                {this.state.collapsed ? preview : fieldset}
            </div>
        );
    },

    toggleCollapsed: function() {
        this.setState({collapsed: !this.state.collapsed});
    },

    updateChild: function(name, value) {
        this.setState({url: null});
        this.props.updateChild(this.props.name, value);
    }

});

var Field = module.exports.Field = React.createClass({

    propTypes: {
        path: React.PropTypes.string,
        schema: React.PropTypes.object.isRequired,
        value: React.PropTypes.any
    },

    contextTypes: {
        submitted: React.PropTypes.bool,
        errors: React.PropTypes.object,
        showReadOnly: React.PropTypes.bool,
        readonly: React.PropTypes.bool,
        id: React.PropTypes.string
    },

    childContextTypes: {
        readonly: React.PropTypes.bool
    },

    getChildContext: function() {
        return { readonly: this.context.readonly || this.props.schema.readonly };
    },

    getDefaultProps: function() {
        return {
            path: 'instance',
            hideLabel: false,
            className: ''
        };
    },

    getInitialState() {
        return {};
    },

    render: function() {
        var { name, path, schema, value, className, ...props } = this.props;
        var errors = this.context.errors;
        var isValid = !errors[path];
        var value = this.props.value;
        var type = schema.type || 'string';
        var classBase = 'rf-Field';
        if (type === 'object') {
            classBase = 'rf-Fieldset';
        } else if (type === 'array') {
            classBase = 'rf-RepeatingFieldset';
        }
        var readonly = this.context.readonly || schema.readonly; 
        var inputProps = {
            name,
            value,
            onChange: this.handleChange,
            disabled: readonly
        };
        var input = schema.formInput;
        if (input) {
            if (input === 'file') {
                input = <inputs.FileInput {...inputProps} />;
            } else if (input === 'textarea') {
                input = <textarea rows="4" {...inputProps} />;
            } else if (input === 'layout') {
                var layout = require('./layout');
                input = <layout.Layout {...inputProps} editable={!readonly} />;
            } else {
                input = cloneWithProps(input, inputProps);
            }
        } else {
            if (schema.linkFrom) {
                input = <FetchedFieldset
                    name={this.props.name} path={path} schema={schema}
                    value={value} updateChild={this.props.updateChild} />;
            } else if (type === 'object') {
                input = [];
                for (name in schema.properties) {
                    if (name === 'uuid' || name === 'schema_version') continue;
                    var subschema = schema.properties[name];
                    if (subschema.calculatedProperty) continue;
                    if (!this.context.showReadOnly && subschema.readonly) continue;
                    // we can only edit child objects if we know the current object's id
                    if (subschema.items && subschema.items.linkFrom && !this.context.id) continue;
                    var required = _.contains((schema.required || []), name);
                    input.push(
                        <Field key={name} name={name} path={path + '.' + name}
                               schema={subschema} value={value && value[name]}
                               updateChild={this.updateChild}
                               className={required ? 'required' : ''} />);
                }                
            } else if (type === 'array') {
                input = <RepeatingFieldset
                    name={this.props.name} path={path} schema={schema}
                    value={value} updateChild={this.props.updateChild} />;
            } else if (schema.enum) {
                var options = schema.enum.map((v) => <option key={v} value={v}>{v}</option>);
                if (!schema.default) {
                    options = [<option key="_null_" value={null} />].concat(options);
                }
                input = <select className="form-control" {...inputProps}>{options}</select>;
            } else if (schema.linkTo) {
                var restrictions = { type: [schema.linkTo] };
                input = <inputs.ObjectPicker {...inputProps}
                    searchBase={'?mode=picker&type=' + schema.linkTo}
                    restrictions={restrictions} />;
            } else if (schema.type === 'boolean') {
                input = <input type="checkbox" {...inputProps} />;
            } else if (schema.type === 'integer' || schema.type === 'number') {
                input = <input type="number" {...inputProps} />;
            } else {
                input = <input type="text" {...inputProps} />;
            }
        }
        if (!isValid) {
            className += ' ' + classBase + '--invalid';
        }
        return (
            <div className={classBase + ' ' + className}>
                {!this.props.hideLabel ?
                    <label className={classBase + '__label rf-Label'}>
                        <span className="rf-Label__label">{schema.title}</span>
                        <span className="rf-Hint">{schema.description}</span>
                    </label>
                : ''}
                {(this.context.submitted || this.state.isDirty) && errors[path] ?
                    <span className="rf-Message">{errors[path]}</span>
                : ''}
                {input}
            </div>
        )
    },

    updateChild,

    handleChange: function(e) {
        var value;
        if (e && e.target) {
            if (e.target.type === 'checkbox') {
                value = e.target.checked;
            } else {
                value = e.target.value;
            }
        } else {
            value = e;
        }
        if (value === null || value === "") {
            value = undefined;
        }
        this.setState({ isDirty: true });
        this.props.updateChild(this.props.name, value);
    },

});

var Form = module.exports.Form = React.createClass({
    contextTypes: {
        adviseUnsavedChanges: React.PropTypes.func,
        fetch: React.PropTypes.func
    },

    childContextTypes: {
        schemas: React.PropTypes.object,
        canSave: React.PropTypes.func,
        onTriggerSave: React.PropTypes.func,
        errors: React.PropTypes.object,
        showReadOnly: React.PropTypes.bool,
        id: React.PropTypes.string,
        submitted: React.PropTypes.bool
    },
    getChildContext: function() {
        return {
            schemas: this.props.schemas,
            canSave: this.canSave,
            onTriggerSave: this.save,
            errors: this.state.errors,
            showReadOnly: this.props.showReadOnly,
            id: this.props.id,
            submitted: this.state.submitted
        };
    },

    getDefaultProps: function() {
        return {
            showReadOnly: true,
            submitLabel: 'Save',
        };
    },

    getInitialState: function() {
        return {
            isDirty: false,
            isValid: true,
            value: this.props.defaultValue,
            errors: {},
            submitted: false
        };
    },

    componentDidUpdate: function(prevProps, prevState) {
        if (!_.isEqual(prevState.errors, this.state.errors)) {
            var error = document.querySelector('.rf-Message');
            if (error) {
                window.scrollTo(0, offset(error).top - document.getElementById('navbar').clientHeight);
            }
        }
    },

    render: function() {
        return (
            <form className="rf-Form"
                  onSubmit={this.save}>
                <Field schema={this.props.schema}
                       value={this.state.value}
                       updateChild={this.update} />
                <div className="pull-right">
                    <a href="" className="btn btn-default">Cancel</a>
                    {' '}
                    <button className="btn btn-success" 
                            onClick={this.save}
                            disabled={!this.canSave()}>{this.props.submitLabel}</button>
                </div>
                {this.state.error ? <div className="rf-Message">{this.state.error}</div> : ''}
            </form>
        );
    },

    validate: function(value) {
        var validation = v.validate(value, this.props.schema);
        // console.log(validation);
        var errorsByPath = validation.errorsByPath = {};
        validation.errors.forEach((error) => {
            var path = error.property.replace(/\[/g, '.').replace(/\]/g, '');
            if (error.name === 'required') {
                path += '.' + error.argument;
            }
            errorsByPath[path] = error.message;
        });
        return validation;
    },

    update: function(name, value) {
        // console.log(value);
        var validation = this.validate(value);
        var nextState = {
            value,
            isDirty: true,
            isValid: validation.valid,
            errors: validation.errorsByPath
        };
        if (!this.state.unsavedToken) {
            nextState.unsavedToken = this.context.adviseUnsavedChanges();
        }
        this.setState(nextState);
    },

    canSave: function() {
        return this.state.isDirty && this.state.isValid && !this.state.editor_error && !this.communicating;
    },

    save: function(e) {
        e.preventDefault();
        e.stopPropagation();
        var value = this.state.value;
        filterValue(value);
        var method = this.props.method;
        var url = this.props.action;
        var request = this.context.fetch(url, {
            method: method,
            headers: {
                'If-Match': this.props.etag || '*',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(value)
        });
        request.then(response => {
            if (!response.ok) throw response;
            return response.json();
        })
        .catch(parseAndLogError.bind(undefined, 'putRequest'))
        .then(this.receive);
        this.setState({
            communicating: true,
            putRequest: request
        });
    },

    finish: function (data) {
        if (this.state.unsavedToken) {
            this.state.unsavedToken.release();
            this.setState({unsavedToken: null});
        }
        if(this.props.onFinish) {
          this.props.onFinish(data);
        }
    },

    receive: function (data) {
        var erred = (data['@type'] || []).indexOf('Error') > -1;
        if (erred) {
            return this.showErrors(data);
        } else {
            return this.finish(data);
        }
    },

    showErrors: function (data) {
        var errors = {};
        var error;
        if (data.errors !== undefined) {
            data.errors.forEach((error) => {
                var path = 'instance' + (error.name.length ? '.' + error.name.join('.') : '');
                var match = /^u?'([^']+)' is a required property$/.exec(error.description);
                if (match) {
                    path += '.' + match[1];
                }
                errors[path] = error.description;
            });
        } else if (data.description) {
            error = data.description + ' ' + (data.detail || '');
        }

        // make sure we scroll to error again
        this.setState({ errors: {} });

        this.setState({
            data,
            error,
            errors,
            submitted: true,
            communicating: false
        });
    }
});

var JSONSchemaForm = module.exports.JSONSchemaForm = React.createClass({

    getDefaultProps: function() {
        return {showReadOnly: true};
    },

    getInitialState: function() {
        var type = this.props.type;
        var schemas = this.props.schemas;
        return {
            schema: schemas[type],
            value: this.props.context || defaultValue(schemas[type]),
        };
    },

    render: function() {
        return <Form
            action={this.props.action} method={this.props.method} etag={this.props.etag}
            schemas={this.props.schemas} schema={this.state.schema}
            defaultValue={this.state.value} showReadOnly={this.props.showReadOnly}
            id={this.props.id} onFinish={this.props.onFinish} />;
    }

});
