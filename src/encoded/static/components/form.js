/* eslint-disable jsx-a11y/label-has-for */

const React = require('react');
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

// Parse object and property from `linkFrom`.
// Backrefs have a linkFrom property in the form
// (object type).(property name)
const parseLinkFrom = function (linkFrom) {
    const parts = linkFrom.split('.');
    return {
        type: parts[0],
        prop: parts[1],
    };
};

// Validate `linkFrom`
validator.attributes.linkFrom = function validateLinkFrom(instance, schema, options, ctx) {
    let result;
    if (instance !== undefined && instance instanceof Object) {
        const linkFrom = parseLinkFrom(schema.linkFrom);
        const subschema = options.schemas[linkFrom.type];
        result = this.attributes.properties.call(this, instance, subschema, options, ctx);
    }
    return result;
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
    if (schema.default !== undefined) {
        return schema.default || undefined;
    } else if (schema.properties !== undefined) {
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
        return (Object.keys(value).length ? value : undefined);
    }
    return schema.default || undefined;
};

const updateChild = function (name, subvalue) {
    // This is the workhorse for passing for field updates
    // up the hierarchy of form fields.
    // It constructs a new value for the current element
    // by replacing the value of one of its children,
    // then propagates the new value to its parent.

    const schema = this.props.schema;
    let oldValue = this.props.value;
    let newValue;
    if (schema.type === 'object') {
        // Clone the old value so we don't mutate it
        newValue = Object.assign({}, oldValue);
        // Set the new value unless it is undefined
        if (subvalue !== undefined) {
            newValue[name] = subvalue;
        } else if (newValue[name] !== undefined) {
            delete newValue[name];
        }
    } else if (schema.type === 'array') {
        // Construct the old value using slices of the old
        // so we don't mutate it
        oldValue = oldValue || [];
        newValue = oldValue.slice(0, name).concat(subvalue).concat(oldValue.slice(name + 1));
    }
    // Pass the new value to the parent
    this.props.updateChild(this.props.name, newValue);
};

const RepeatingItem = React.createClass({
    // A form field for editing one item in an array
    // (part of a RepeatingFieldset).
    // It delegates rendering the field to an actual Field component,
    // but also shows a button to remove the item.

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

    handleRemove(e) {
        // Called when the remove button is clicked.

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
        // When the contained field value is updated,
        // tell our parent RepeatingFieldset to update the correct index.
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
                    onClick={this.handleRemove}
                    type="button"
                    className="rf-RepeatingFieldset__remove"
                >&times;</button>
            : ''}
          </div>
        );
    },

});

const RepeatingFieldset = React.createClass({
    // A form field for editing an array.
    // Each item in the array is rendered via RepeatingItem.
    // Also shows a button to add a new item.

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
        // Counter which is incremented every time an item is removed.
        // This is used as part of the React key for contained RepeatingItems
        // to make sure that we re-render all items after one is removed.
        // After a removal the same array index may point to a different
        // item, so it's not safe to use the array index alone as the key.
        return { generation: 0 };
    },

    onRemove(index) {
        // Called when a contained RepeatingItem is removed.

        // Remove the specified index from the current value.
        const oldValue = this.props.value;
        let value = oldValue.slice(0, index).concat(oldValue.slice(index + 1));
        if (value.length === 0) {
            value = undefined;
        }

        // Increment `this.state.generation` (see explanation in getInitialState)
        this.setState({ generation: this.state.generation + 1 });

        // Pass the new value for the entire array to parent
        this.props.updateChild(this.props.name, value);
    },

    handleAdd() {
        // Called when the add button is clicked.

        // Construct a new subitem from schema defaults.
        let subschema = this.props.schema.items;
        let newValue;
        if (subschema.linkFrom !== undefined) {
            // This is an array of backreferences from separate objects of a different type.
            // We need to construct the default value for that type,
            // and also add a reference to the object being edited.
            const linkFrom = parseLinkFrom(subschema.linkFrom);
            subschema = this.context.schemas[linkFrom.type];
            newValue = defaultValue(subschema);
            newValue[linkFrom.prop] = this.context.id;
        } else {
            // Simple subitem; construct default value from schema.
            newValue = defaultValue(subschema);
        }

        // Add the new subitem to the end of the array.
        const value = (this.props.value || []).concat(newValue);

        // Pass the new value for the entire array to parent
        this.props.updateChild(this.props.name, value);
    },

    // Propagate edits to subitems upward
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
                        onClick={this.handleAdd}
                        className="rf-RepeatingFieldset__add"
                    >Add</button>
                }
            </div>
        );
    },

});

const FetchedFieldset = React.createClass({
    // A form field for editing a child object
    // (a subitem of an array property using linkFrom).
    // Initially the value is a URI and we render a preview of the object.
    // If the user expands the item we fetch its edit frame and render form fields.
    // If the user updates any fields the new value is the updated object
    // rather than just the URI.

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

        // We need to construct a modified schema for the child type,
        // to avoid showing the field that links back to the main object being edited.

        const linkFrom = parseLinkFrom(schema.linkFrom);
        let subschema = this.context.schemas[linkFrom.type];
        // FIXME Handle linkFrom abstract type.
        if (subschema !== undefined) {
            // The linkProp is the one that refers to the parent object.
            // This should not be shown when accessed from the parent's form.
            // Let's immutably clone the schema and delete it:
            subschema = Object.assign({}, subschema, {
                properties: Object.assign({}, subschema.properties),
            });
            delete subschema.properties[linkFrom.prop];
        }

        const value = this.props.value;
        const error = this.context.errors[this.props.path];
        const url = typeof value === 'string' ? value : null;
        return {
            schema: subschema,
            url: url,
            // Start collapsed for existing children,
            // expanded when adding a new one or if there are errors
            collapsed: url && !error,
        };
    },

    toggleCollapsed() {
        // Toggle collapsed state when collapsible trigger is clicked.
        this.setState({ collapsed: !this.state.collapsed });
    },

    updateChild(name, value) {
        // Pass new value up to our parent.
        value['@id'] = this.state.url;
        this.props.updateChild(this.props.name, value);
    },

    render() {
        const schema = this.state.schema;
        const { path, value } = this.props;
        let preview;
        let fieldset;

        if (this.state.url) {
            // We have a URI for an existing object.
            const previewUrl = this.state.url;
            // When collapsed, fetch the object and render it using ItemPreview.
            preview = (
                <fetched.FetchedData>
                    <fetched.Param name="data" url={previewUrl} />
                    <inputs.ItemPreview />
                </fetched.FetchedData>
            );
            // When expanded, fetch the edit frame and render form fields.
            if (typeof value === 'string') {
                fieldset = (
                    <fetched.FetchedData>
                        <fetched.Param name="value" url={`${this.state.url}?frame=edit`} />
                        <Field path={path} schema={schema} updateChild={this.updateChild} />
                    </fetched.FetchedData>
                );
            } else {
                fieldset = <Field path={path} schema={schema} value={value} updateChild={this.updateChild} />;
            }
        } else {
            // We don't have a URI yet (it's a new object).
            // When collapsed, render a placeholder.
            preview = (
                <ul className="nav result-table">
                  <li>
                    <div className="accession">{`New ${schema.title}`}</div>
                  </li>
                </ul>
            );
            // When expanded, render form fields (but there's no edit frame to fetch)
            fieldset = (<Field
                path={path} value={value} schema={schema}
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
    // Build form input components based on a JSON schema
    // (or a portion thereof).

    // An entire form is comprised of a hierarchy of Field components;
    // each field propagates updates to its parent (via the `updateChild` prop)
    // until it reaches the Form itself.

    // For each field we render a label (from the schema `title` and `description`),
    // any validation error messages, and the input itself.

    // The Field determines what kind of input to render based on the schema:
    // - `type: 'object'`: Renders a separate sub-Field for each object property
    //   except `uuid`, `schema_version`, and computed properties.
    // - `type: 'array'`: Renders using `RepeatingFieldset`.
    // - `type: 'boolean'`: Renders an HTML checkbox `input` element.
    // - `type: 'integer' or 'number'`: Renders an HTML number `input` elemtn.
    // - schema with `enum`: Renders an HTML `select` element.
    // - schema with `linkTo`: Renders an `ObjectPicker` for searching and selecting other objects.
    // - schema with `linkFrom`: Renders using `FetchedFieldset`.
    // - schema with `formInput: 'file'`: Renders a `FileInput` to handle file uploads.
    // - schema with `formInput: 'textarea`: Renders an HTML `textarea` element.
    // - schema with `formInput: 'layout'`: Renders a `Layout` for drag-and-drop placement of content blocks.
    // - anything else with `type: 'string'`: Renders an HTML text `input` element.
    // - Custom form inputs for particular properties can be specified in the schema's `formInput` property.

    // If the schema (or the schema for any parent field) has `readonly: true`,
    // the input is disabled and the field value cannot be edited.

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
        return { isDirty: false };
    },

    getChildContext() {
        // Allow contained fields to tell whether they are inside a readonly field.
        return { readonly: !!(this.context.readonly || this.props.schema.readonly) };
    },

    // Propagate updates from children to parent
    updateChild,

    handleChange(e) {
        // Handles change events on (leaf) input elements.
        let value;
        if (e && e.target) {
            // We were passed an event; get the value from its target.
            if (e.target.type === 'checkbox') {
                value = e.target.checked;
            } else {
                value = e.target.value;
            }
        } else {
            // We were passed the value itself, not an event.
            value = e;
        }
        // Remove empty and null values so they won't pass validation for required fields.
        if (value === null || value === '') {
            value = undefined;
        }
        const type = this.props.schema.type;
        if (value && (type === 'integer' || type === 'number')) {
            try {
                value = parseFloat(value);
            } catch (err) {
                // Keep string, which should fail schema validation
            }
        }
        // Record that this field was modified.
        this.setState({ isDirty: true });
        // Pass the new value to the parent.
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
                // We were passed an arbitrary custom input,
                // which we need to clone to specify the correct props.
                input = React.cloneElement(input, inputProps);
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
                // Readonly fields are omitted when showReadOnly is false
                // (i.e. when adding a new object).
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
                // "_null_" is a placeholder; it'd be nice if we could actually use null
                // to avoid potential collision with real options, but it's not a valid
                // React key.
                options = [<option key="_null_" value={null} />].concat(options);
            }
            input = <select className="form-control" {...inputProps}>{options}</select>;
        } else if (schema.linkTo) {
            // Restrict ObjectPicker to finding the specified type
            // FIXME this should handle an array of types too
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
        // Provide a CSS hook to indicate fields with errors
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
    // The Form component renders a form based on a JSON schema.

    // It renders an actual HTML `form` element which contains
    // form fields (via the `Field` component)
    // and Cancel and Save buttons.

    // The initial form value is taken from the `defaultValue` prop.
    // The JSON schema is specified in the `schema` prop.

    // As the form is edited, validation against the schema
    // is performed (on the client side) and errors are reported.
    // Once the form has been edited, the user must confirm a dialog
    // to navigate away from the form.

    // The Save button is enabled if the form has been edited
    // and input is valid. Submitting the form
    // (by hitting Enter or clicking the Save button)
    // serializes the form value to JSON and sends it to the
    // server endpoint specified in the `action` and `method`
    // props.

    // If saving was successful, the form's `onFinish` prop
    // is called. Otherwise, it renders error messages
    // (either formwide errors below the save button
    // or field-specific errors in the context of the field)
    // and scrolls to the first one.

    // Clicking the Cancel button returns to the homepage.

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
        // Provide various props to contained fields via React's
        // `context` mechanism to avoid needing to explicitly
        // pass them through multiple layers of nested components.
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
        // If form error state changed, scroll to first error message
        // to make sure the user notices it.
        if (!_.isEqual(prevState.errors, this.state.errors)) {
            const error = document.querySelector('.rf-Message');
            if (error) {
                window.scrollTo(0, offset(error).top - document.getElementById('navbar').clientHeight);
            }
        }
    },

    validate(value) {
        // Get validation errors from jsonschema validator.
        const validation = validator.validate(value, this.props.schema, {
            schemas: this.props.schemas,
            // Don't validate `dependencies` in schema,
            // because the errors don't get reported at the correct path.
            // These should still be reported by server-side validation on form submit.
            skipAttributes: ['dependencies'],
        });

        // for debugging:
        console.log(validation);

        // `jsonschema` uses field paths like
        //   `instance.aliases[0]`
        // but we use paths like
        //   `instance.aliases.0`
        // so we have to convert them here.
        const errorsByPath = validation.errorsByPath = {};
        validation.errors.forEach((error) => {
            let path = error.property.replace(/\[/g, '.').replace(/]/g, '');
            // Missing values for required properties are reported
            // on the parent property (the one that lists it as required)
            // so we have to append the error's `argument`
            // to make sure we show the missing value
            // in the most helpful place (next to the empty input).
            if (error.name === 'required') {
                path = `${path}.${error.argument}`;
            }
            errorsByPath[path] = error.message;
        });
        return validation;
    },

    update(name, value) {
        // Called whenever the form value was changed.
        // (The `name` arg is ignored; most Field components have a
        // name and pass it when propagating an update
        // to their parent via the `updateChild` prop,
        // but the top-level Field does not have a name.)

        // for debugging:
        // console.log(value);

        // Update validation state.
        const validation = this.validate(value);
        const nextState = {
            value,
            isDirty: true,
            isValid: validation.valid,
            errors: validation.errorsByPath,
        };
        // Notify app that the page is dirty and we should
        // show a confirmation dialog before allowing navigation.
        if (!this.state.unsavedToken) {
            nextState.unsavedToken = this.context.adviseUnsavedChanges();
        }
        this.setState(nextState);
    },

    canSave() {
        // Called to determine whether to enable the Save button or not.
        // It is enabled if the form has been edited, the value is valid
        // according to the schema, and the form submission is not in progress.
        return this.state.isDirty && this.state.isValid && !this.state.editor_error && !this.communicating;
    },

    save(e) {
        // Send the form value to the server.

        // Avoid non-AJAX submission of form.
        e.preventDefault();
        e.stopPropagation();

        // Filter out `schema_version` property
        const value = this.state.value;
        filterValue(value);

        // Make the request
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
        // Handle errors using `parseAndLogError`;
        // otherwise convert response to JSON and pass it to `this.receive`
        request.then((response) => {
            if (!response.ok) throw response;
            return response.json();
        })
        .catch(parseAndLogError.bind(undefined, 'putRequest'))
        .then(this.receive);
        // Set `communicating` to true so the Save button becomes disabled.
        this.setState({
            communicating: true,
            putRequest: request,
        });
    },

    receive(data) {
        // Handle a response that is not an HTTP error status.

        // Handle server-side validation errors using `this.showErrors`.
        const erred = (data['@type'] || []).indexOf('Error') > -1;
        if (erred) {
            return this.showErrors(data);
        }
        // Handle a successful form submission using `this.finish`.
        return this.finish(data);
    },

    showErrors(data) {
        // Translate server-side validation errors.

        // The Field component uses paths like
        //   `instance.aliases.0`
        // but the server gives us paths like
        //   `['aliases', 0]`
        // so we have to translate here.

        const errors = {};
        let error;
        if (data.errors !== undefined) {
            data.errors.forEach((err) => {
                let path = `instance${err.name.length ? `.${err.name.join('.')}` : ''}`;
                // Missing values for required properties are reported
                // on the parent property (the one that specifies `required`)
                // so we have to add the property that is actually missing here.
                const match = /^u?'([^']+)' is a required property$/.exec(err.description);
                if (match) {
                    path = `${path}.${match[1]}`;
                }
                errors[path] = err.description;
            });
        } else if (data.description) {
            // This is a form-wide error rather than a field-specific one.
            error = `${data.description} ${data.detail || ''}`;
        }

        // First clear errors to make sure componentDidUpdate
        // will decide we need to scroll again even if the
        // errors are the same as the last attempted submission.
        this.setState({ errors: {} });

        this.setState({
            data,
            error,
            errors,
            submitted: true,
            communicating: false,
        });
    },

    finish(data) {
        // Handle a successful form submission.

        // Let the app know navigation is now allowed again
        // without showing a confirmation dialog
        // (i.e. the form is no longer dirty)
        if (this.state.unsavedToken) {
            this.state.unsavedToken.release();
            this.setState({ unsavedToken: null });
        }

        // Call the `onFinish` prop, if specified.
        if (this.props.onFinish) {
            this.props.onFinish(data);
        }
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
    // JSONSchemaForm is a wrapper of Form
    // that is used from the ItemEdit component after
    // it fetches the `schemas` and the `context`
    // (which is the edit frame of the object being edited).

    // It exists to:
    // 1. Look up a specific type schema within the full schemas object.
    // 2. Construct a default value, based on the schema,
    //    if we're adding a new object.

    // Other properties are passed through to the Form.

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
