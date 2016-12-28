/* eslint-disable jsx-a11y/label-has-for */

const React = require('react');
const cloneWithProps = require('react/lib/cloneWithProps');
const parseAndLogError = require('./mixins').parseAndLogError;
const offset = require('../libs/offset');
const fetched = require('./fetched');
const inputs = require('./inputs');
const layout = require('./layout');
const jsonschema = require('jsonschema');
const _ = require('underscore');

const validator = new jsonschema.Validator();

// Add validator for regex patterns in our schemas
validator.attributes.pattern = function validatePattern(instance, schema) {
    let error;
    if (typeof instance === 'string') {
        if (typeof schema.pattern !== 'string') throw new jsonschema.SchemaError('"pattern" expects a string', schema);
        if (!instance.match(schema.pattern)) {
            error = `does not match pattern ${JSON.stringify(schema.pattern)}`;
        }
    }
    return error;
};

// Recursively filter an object to remove `schema_version`.
// This is used before sending the value to the server.
const filterValue = function (value) {
    if (Array.isArray(value)) {
        value.map(filterValue);
    } else if (typeof value === 'object') {
        _.each(value, (v, k) => {
            if (k === 'schema_version') {
                delete value[k];
            } else {
                filterValue(v);
            }
        });
    }
};

// Given a schema, construct a default object.
// The default object includes the `default` value
// for any property that defines one,
// with the exception of read-only and calculated properties.
const defaultValue = function (schema) {
    if (schema.properties !== undefined) {
        const value = {};
        _.each(schema.properties, (property, name) => {
            if (property.calculatedProperty) return;
            if (!property.readonly) {
                const propertyDefault = defaultValue(property);
                if (propertyDefault !== undefined) {
                    value[name] = propertyDefault;
                }
            }
        });
        return value;
    } else if (schema.items !== undefined) {
        return schema.default || [];
    }
    return schema.default || undefined;
};

const updateChild = function (name, subvalue) {
    const schema = this.props.schema;
    let oldValue = this.props.value;
    let newValue;
    if (schema.type === 'object') {
        newValue = Object.assign({}, oldValue);
        if (subvalue !== undefined) {
            newValue[name] = subvalue;
        } else if (newValue[name] !== undefined) {
            delete newValue[name];
        }
    } else if (schema.type === 'array') {
        oldValue = oldValue || [];
        newValue = oldValue.slice(0, name).concat(subvalue).concat(oldValue.slice(name + 1));
    }
    this.props.updateChild(this.props.name, newValue);
};

const RepeatingItem = React.createClass({

    propTypes: {
        name: React.PropTypes.number,
        path: React.PropTypes.string,
        schema: React.PropTypes.object,
        onRemove: React.PropTypes.func,
        value: React.PropTypes.any,
        updateChild: React.PropTypes.func,
    },

    contextTypes: {
        readonly: React.PropTypes.bool,
    },

    onRemove(e) {
        e.preventDefault();
        // eslint-disable-next-line no-alert
        if (!confirm('Are you sure you want to remove this item?')) {
            return;
        }
        if (this.props.onRemove) {
            this.props.onRemove(this.props.name);
        }
    },

    updateChild(name, value) {
        this.props.updateChild(this.props.name, value);
    },

    render() {
        const { path, schema, value } = this.props;
        return (
          <div className="rf-RepeatingFieldset__item">
            <Field
                path={path} schema={schema}
                value={value} updateChild={this.updateChild}
                hideLabel
            />
            {!this.context.readonly ?
                <button
                    onClick={this.onRemove}
                    type="button"
                    className="rf-RepeatingFieldset__remove"
                >&times;</button>
            : ''}
          </div>
        );
    },

});

const RepeatingFieldset = React.createClass({

    propTypes: {
        schema: React.PropTypes.object,
        name: React.PropTypes.string,
        path: React.PropTypes.string,
        value: React.PropTypes.any,
        updateChild: React.PropTypes.func,
    },

    contextTypes: {
        schemas: React.PropTypes.object,
        readonly: React.PropTypes.bool,
        id: React.PropTypes.string,
    },

    getInitialState: function () {
        // counter used to make sure that we get new keys
        // once an item is removed
        return { generation: 0 };
    },

    onAdd() {
        let subschema = this.props.schema.items;
        let newValue;
        if (subschema.linkFrom !== undefined) {
            const a = subschema.linkFrom.split('.');
            const linkType = a[0];
            const linkProp = a[1];
            subschema = this.context.schemas[linkType];
            newValue = defaultValue(subschema);
            newValue[linkProp] = this.context.id;
        } else {
            newValue = defaultValue(subschema);
        }
        const value = (this.props.value || []).concat(newValue);
        this.props.updateChild(this.props.name, value);
    },

    onRemove(index) {
        const oldValue = this.props.value;
        const value = oldValue.slice(0, index).concat(oldValue.slice(index + 1));
        this.setState({ generation: this.state.generation + 1 });
        this.props.updateChild(this.props.name, value);
    },

    updateChild,

    render() {
        const { path, value, schema } = this.props;
        return (
            <div>
                <div className="rf-RepeatingFieldset__items">
                    {value ? value.map((subvalue, key) => {
                        const props = {
                            key: `${this.state.generation}.${key}`,
                            name: key,
                            path: `${path}.${key}`,
                            value: subvalue,
                            schema: schema.items,
                            updateChild: this.updateChild,
                            onRemove: this.onRemove,
                        };
                        return <RepeatingItem {...props} />;
                    }) : ''}
                </div>
                {!this.context.readonly &&
                    <button
                        type="button"
                        onClick={this.onAdd}
                        className="rf-RepeatingFieldset__add"
                    >Add</button>
                }
            </div>
        );
    },

});

const FetchedFieldset = React.createClass({

    propTypes: {
        schema: React.PropTypes.object,
        name: React.PropTypes.any,
        path: React.PropTypes.string,
        value: React.PropTypes.any,
        updateChild: React.PropTypes.func,
    },

    contextTypes: {
        schemas: React.PropTypes.object,
        errors: React.PropTypes.object,
    },

    childContextTypes: {
        id: React.PropTypes.string,
    },

    getInitialState() {
        const schema = this.props.schema;
        // Backrefs have a linkFrom property in the form
        // (object type).(property name)
        const a = schema.linkFrom.split('.');
        const linkType = a[0];
        const linkProp = a[1];
        let subschema = this.context.schemas[linkType];
        // FIXME Handle linkFrom abstract type.
        if (subschema !== undefined) {
            // The linkProp is the one that refers to the parent object.
            // This should not be shown when accessed from the parent's form.
            // Let's immutably clone the schema and delete it:
            subschema = Object.assign({}, subschema, {
                properties: Object.assign({}, subschema.properties),
            });
            delete subschema.properties[linkProp];
        }

        const value = this.props.value;
        const error = this.context.errors[this.props.path];
        const url = typeof value === 'string' ? value : null;
        return {
            schema: subschema,
            url: url,
            collapsed: url && !error,
        };
    },

    toggleCollapsed() {
        this.setState({ collapsed: !this.state.collapsed });
    },

    updateChild(name, value) {
        this.setState({ url: null });
        this.props.updateChild(this.props.name, value);
    },

    render() {
        const schema = this.state.schema;
        const value = this.props.value;
        let preview;
        let fieldset;

        if (this.state.url) {
            const previewUrl = this.state.url;
            preview = (
                <fetched.FetchedData>
                    <fetched.Param name="data" url={previewUrl} />
                    <inputs.ItemPreview />
                </fetched.FetchedData>
            );
            fieldset = (
                <fetched.FetchedData>
                    <fetched.Param name="value" url={`${this.state.url}?frame=edit`} />
                    <Field schema={schema} updateChild={this.updateChild} />
                </fetched.FetchedData>
            );
        } else {
            preview = (
                <ul className="nav result-table">
                  <li>
                    <div className="accession">{`New ${schema.title}`}</div>
                  </li>
                </ul>
            );
            fieldset = (<Field
                value={value} schema={schema}
                updateChild={this.updateChild}
            />);
        }

        return (
            <div className="collapsible">
                <button
                    type="button" className="collapsible-trigger"
                    onClick={this.toggleCollapsed}
                >{this.state.collapsed ? '▶ ' : '▼ '}</button>
                {this.state.collapsed ? preview : fieldset}
            </div>
        );
    },

});

const Field = module.exports.Field = React.createClass({

    propTypes: {
        name: React.PropTypes.any,
        path: React.PropTypes.string,
        schema: React.PropTypes.object.isRequired,
        value: React.PropTypes.any,
        className: React.PropTypes.string,
        updateChild: React.PropTypes.func,
        hideLabel: React.PropTypes.bool,
    },

    contextTypes: {
        submitted: React.PropTypes.bool,
        errors: React.PropTypes.object,
        showReadOnly: React.PropTypes.bool,
        readonly: React.PropTypes.bool,
        id: React.PropTypes.string,
    },

    childContextTypes: {
        readonly: React.PropTypes.bool,
    },

    getDefaultProps() {
        return {
            path: 'instance',
            hideLabel: false,
            className: '',
        };
    },

    getInitialState() {
        return {};
    },

    getChildContext() {
        return { readonly: this.context.readonly || this.props.schema.readonly };
    },

    updateChild,

    handleChange(e) {
        let value;
        if (e && e.target) {
            if (e.target.type === 'checkbox') {
                value = e.target.checked;
            } else {
                value = e.target.value;
            }
        } else {
            value = e;
        }
        if (value === null || value === '') {
            value = undefined;
        }
        this.setState({ isDirty: true });
        this.props.updateChild(this.props.name, value);
    },

    render() {
        const { name, path, schema, value } = this.props;
        const errors = this.context.errors;
        const isValid = !errors[path];
        const type = schema.type || 'string';
        let classBase = 'rf-Field';
        if (type === 'object') {
            classBase = 'rf-Fieldset';
        } else if (type === 'array') {
            classBase = 'rf-RepeatingFieldset';
        }
        let className = this.props.className;
        const readonly = this.context.readonly || schema.readonly;
        const inputProps = {
            name,
            value,
            onChange: this.handleChange,
            disabled: readonly,
        };
        let input = schema.formInput;
        if (input) {
            if (input === 'file') {
                input = <inputs.FileInput {...inputProps} />;
            } else if (input === 'textarea') {
                input = <textarea rows="4" {...inputProps} />;
            } else if (input === 'layout') {
                input = <layout.Layout {...inputProps} editable={!readonly} />;
            } else {
                input = cloneWithProps(input, inputProps);
            }
        } else if (schema.linkFrom) {
            input = (<FetchedFieldset
                name={this.props.name} path={path} schema={schema}
                value={value} updateChild={this.props.updateChild}
            />);
        } else if (type === 'object') {
            input = [];
            Object.keys(schema.properties).forEach((key) => {
                if (key === 'uuid' || key === 'schema_version') return;
                const subschema = schema.properties[key];
                if (subschema.calculatedProperty) return;
                if (!this.context.showReadOnly && subschema.readonly) return;
                // we can only edit child objects if we know the current object's id
                if (subschema.items && subschema.items.linkFrom && !this.context.id) return;
                const required = _.contains((schema.required || []), key);
                input.push(<Field
                    key={key} name={key} path={`${path}.${key}`}
                    schema={subschema} value={value && value[key]}
                    updateChild={this.updateChild}
                    className={required ? 'required' : ''}
                />);
            });
        } else if (type === 'array') {
            input = (<RepeatingFieldset
                name={this.props.name} path={path} schema={schema}
                value={value} updateChild={this.props.updateChild}
            />);
        } else if (schema.enum) {
            let options = schema.enum.map(v => <option key={v} value={v}>{v}</option>);
            if (!schema.default) {
                options = [<option key="_null_" value={null} />].concat(options);
            }
            input = <select className="form-control" {...inputProps}>{options}</select>;
        } else if (schema.linkTo) {
            const restrictions = { type: [schema.linkTo] };
            input = (<inputs.ObjectPicker
                {...inputProps}
                searchBase={`?mode=picker&type=${schema.linkTo}`}
                restrictions={restrictions}
            />);
        } else if (schema.type === 'boolean') {
            input = <input type="checkbox" {...inputProps} />;
        } else if (schema.type === 'integer' || schema.type === 'number') {
            input = <input type="number" {...inputProps} />;
        } else {
            input = <input type="text" {...inputProps} />;
        }
        if (!isValid) {
            className = `${className} ${classBase}--invalid`;
        }
        return (
            <div className={`${classBase} ${className}`}>
                {!this.props.hideLabel ?
                    <label className={`${classBase}__label rf-Label`}>
                        <span className="rf-Label__label">{schema.title}</span>
                        <span className="rf-Hint">{schema.description}</span>
                    </label>
                : ''}
                {(this.context.submitted || this.state.isDirty) && errors[path] ?
                    <span className="rf-Message">{errors[path]}</span>
                : ''}
                {input}
            </div>
        );
    },

});

const Form = module.exports.Form = React.createClass({

    propTypes: {
        defaultValue: React.PropTypes.any,
        schemas: React.PropTypes.object,
        schema: React.PropTypes.object,
        showReadOnly: React.PropTypes.bool,
        id: React.PropTypes.string,
        method: React.PropTypes.string,
        action: React.PropTypes.string,
        etag: React.PropTypes.string,
        onFinish: React.PropTypes.func,
        submitLabel: React.PropTypes.string,
    },

    contextTypes: {
        adviseUnsavedChanges: React.PropTypes.func,
        fetch: React.PropTypes.func,
    },

    childContextTypes: {
        schemas: React.PropTypes.object,
        canSave: React.PropTypes.func,
        onTriggerSave: React.PropTypes.func,
        errors: React.PropTypes.object,
        showReadOnly: React.PropTypes.bool,
        id: React.PropTypes.string,
        submitted: React.PropTypes.bool,
    },

    getDefaultProps() {
        return {
            showReadOnly: true,
            submitLabel: 'Save',
        };
    },

    getInitialState() {
        return {
            isDirty: false,
            isValid: true,
            value: this.props.defaultValue,
            errors: {},
            submitted: false,
        };
    },

    getChildContext() {
        return {
            schemas: this.props.schemas,
            canSave: this.canSave,
            onTriggerSave: this.save,
            errors: this.state.errors,
            showReadOnly: this.props.showReadOnly,
            id: this.props.id,
            submitted: this.state.submitted,
        };
    },

    componentDidUpdate(prevProps, prevState) {
        if (!_.isEqual(prevState.errors, this.state.errors)) {
            const error = document.querySelector('.rf-Message');
            if (error) {
                window.scrollTo(0, offset(error).top - document.getElementById('navbar').clientHeight);
            }
        }
    },

    validate(value) {
        const validation = validator.validate(value, this.props.schema);
        // console.log(validation);
        const errorsByPath = validation.errorsByPath = {};
        validation.errors.forEach((error) => {
            let path = error.property.replace(/\[/g, '.').replace(/]/g, '');
            if (error.name === 'required') {
                path = `${path}.${error.argument}`;
            }
            errorsByPath[path] = error.message;
        });
        return validation;
    },

    update(name, value) {
        // console.log(value);
        const validation = this.validate(value);
        const nextState = {
            value,
            isDirty: true,
            isValid: validation.valid,
            errors: validation.errorsByPath,
        };
        if (!this.state.unsavedToken) {
            nextState.unsavedToken = this.context.adviseUnsavedChanges();
        }
        this.setState(nextState);
    },

    canSave() {
        return this.state.isDirty && this.state.isValid && !this.state.editor_error && !this.communicating;
    },

    save(e) {
        e.preventDefault();
        e.stopPropagation();
        const value = this.state.value;
        filterValue(value);
        const { method, action, etag } = this.props;
        const request = this.context.fetch(action, {
            method: method,
            headers: {
                'If-Match': etag || '*',
                Accept: 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(value),
        });
        request.then((response) => {
            if (!response.ok) throw response;
            return response.json();
        })
        .catch(parseAndLogError.bind(undefined, 'putRequest'))
        .then(this.receive);
        this.setState({
            communicating: true,
            putRequest: request,
        });
    },

    finish(data) {
        if (this.state.unsavedToken) {
            this.state.unsavedToken.release();
            this.setState({ unsavedToken: null });
        }
        if (this.props.onFinish) {
            this.props.onFinish(data);
        }
    },

    receive(data) {
        const erred = (data['@type'] || []).indexOf('Error') > -1;
        if (erred) {
            return this.showErrors(data);
        }
        return this.finish(data);
    },

    showErrors(data) {
        const errors = {};
        let error;
        if (data.errors !== undefined) {
            data.errors.forEach((err) => {
                let path = `instance${err.name.length ? `.${err.name.join('.')}` : ''}`;
                const match = /^u?'([^']+)' is a required property$/.exec(err.description);
                if (match) {
                    path = `${path}.${match[1]}`;
                }
                errors[path] = error.description;
            });
        } else if (data.description) {
            error = `${data.description} ${data.detail || ''}`;
        }

        // make sure we scroll to error again
        this.setState({ errors: {} });

        this.setState({
            data,
            error,
            errors,
            submitted: true,
            communicating: false,
        });
    },

    render() {
        return (
            <form
                className="rf-Form"
                onSubmit={this.save}
            >
                <Field
                    schema={this.props.schema}
                    value={this.state.value}
                    updateChild={this.update}
                />
                <div className="pull-right">
                    <a href="" className="btn btn-default">Cancel</a>
                    {' '}
                    <button
                        className="btn btn-success"
                        onClick={this.save}
                        disabled={!this.canSave()}
                    >{this.props.submitLabel}</button>
                </div>
                {this.state.error ? <div className="rf-Message">{this.state.error}</div> : ''}
            </form>
        );
    },

});

module.exports.JSONSchemaForm = React.createClass({

    propTypes: {
        type: React.PropTypes.string,
        schemas: React.PropTypes.object,
        context: React.PropTypes.any,
        action: React.PropTypes.string,
        method: React.PropTypes.string,
        etag: React.PropTypes.string,
        showReadOnly: React.PropTypes.bool,
        id: React.PropTypes.string,
        onFinish: React.PropTypes.func,
    },

    getDefaultProps() {
        return { showReadOnly: true };
    },

    getInitialState() {
        const { type, schemas } = this.props;
        return {
            schema: schemas[type],
            value: this.props.context || defaultValue(schemas[type]),
        };
    },

    render() {
        return (<Form
            action={this.props.action} method={this.props.method} etag={this.props.etag}
            schemas={this.props.schemas} schema={this.state.schema}
            defaultValue={this.state.value} showReadOnly={this.props.showReadOnly}
            id={this.props.id} onFinish={this.props.onFinish}
        />);
    },

});
