'use strict';
var EventEmitter = require('events').EventEmitter;
var React = require('react');
var parseAndLogError = require('./mixins').parseAndLogError;
var closest = require('../libs/closest');
var offset = require('../libs/offset');
var fetched = require('./fetched');
var ga = require('google-analytics');
var _ = require('underscore');


var filterValue = function(value) {
    if (Array.isArray(value)) {
        value.map(filterValue);
    } else if (typeof value == 'object') {
        _.each(value, function(v, k) {
            if (v === null || k == 'schema_version') {
                delete value[k];
            } else {
                filterValue(v);
            }
        });
    }
};



var makeValidationResult = function(validation) {
    var ReactForms = require('react-forms');
    return new ReactForms.ValidationResult(
        validation.error ? validation.error : null,
        validation.children ? _.mapObject(validation.children, function(v, k) {
            return makeValidationResult(v);
        }) : null
    );
};


var RepeatingItem = React.createClass({

  render: function() {
    return (
      <div {...this.props} className="rf-RepeatingFieldset__item">
        {this.props.children}
        <button
          onClick={this.onRemove}
          type="button"
          className="rf-RepeatingFieldset__remove">&times;</button>
      </div>
    );
  },

  onRemove: function(e) {
    if (!confirm('Are you sure you want to remove this item?')) {
        e.preventDefault();
        return;
    }
    if (this.props.onRemove) {
      this.props.onRemove(this.props.name);
    }
  }

});


// Based on RepeatingFieldset from react-forms, but with validation errors shown
var RepeatingFieldset = React.createClass({

  render() {
    var cx = require('react/lib/cx');
    var cloneWithProps = require('react/lib/cloneWithProps');
    var ReactForms = require('react-forms');
    var {
      item: Item, value, className, noAddButton, noRemoveButton,
      onAdd, onRemove, noLabel, label, hint, ...props
    } = this.props;
    var {validation, isDirty, externalValidation} = value;
    return (
      <div {...props} className={cx('rf-RepeatingFieldset', className)}>
        {!noLabel &&
          <ReactForms.Label
            className="rf-RepeatingFieldset__label"
            label={label || value.node.props.get('label')}
            hint={hint || value.node.props.get('hint')}
            />}
        {validation.isFailure && isDirty &&
          <ReactForms.Message>{validation.error}</ReactForms.Message>}
        {externalValidation.isFailure &&
          <ReactForms.Message>{externalValidation.error}</ReactForms.Message>}
        <div className="rf-RepeatingFieldset__items">
          {value.map((value, key) => {
            var props = {
              value,
              key,
              index: key,
              ref: key,
              noRemoveButton,
              onRemove: this.onRemove.bind(null, key),
              children: (
                <ReactForms.Element
                  className="rf-RepeatingFieldset__child"
                  value={value}
                  />
              )
            };
            return React.isValidElement(Item) ?
              cloneWithProps(Item, props) :
              <Item {...props} />;
          })}
        </div>
        {!noAddButton &&
          <button
            type="button"
            onClick={this.onAdd}
            className="rf-RepeatingFieldset__add">
            Add
          </button>}
      </div>
    );
  },

  getDefaultProps() {
    return {
      item: RepeatingItem,
      onAdd: function() {},
      onRemove: function() {}
    };
  },

  onAdd() {
    var defaultValue = require('react-forms').defaultValue;
    var newIdx = this.props.value.size;
    var valueToAdd = defaultValue(this.props.value.node.get(newIdx));
    this.props.value.transform(value => value.push(valueToAdd));
    this.props.onAdd();
  },

  onRemove(index) {
    this.props.value.transform(value => value.splice(index, 1));
    this.props.onRemove(index);
  },

  getItemByIndex(index) {
    return this.refs[index];
  }

});


var FetchedFieldset = React.createClass({

    getInitialState: function() {
        var value = this.props.value;
        var url = typeof value.value == 'string' ? value.value : null;
        var externalValidation = value.externalValidation;
        return {
            url: url,
            collapsed: url && !externalValidation.isFailure,
        };
    },

    render: function() {
        var ReactForms = require('react-forms');
        var inputs = require('./inputs');
        var schema = this.props.schema;
        var value = this.props.value;
        var externalValidation = value.externalValidation;
        var isFailure = externalValidation.isFailure;
        externalValidation = isFailure ? externalValidation : null;
        value = value.value;
        var url = typeof value == 'string' ? value : null;
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
                    <fetched.Param name="defaultValue" url={this.state.url + '?frame=edit'} />
                    <ReactForms.Form schema={schema} onUpdate={this.onUpdate}
                                     externalValidation={externalValidation} />
                </fetched.FetchedData>
            );
        } else {
            preview = (
                <ul className="nav result-table">
                  <li>
                    <div className="accession">{'New ' + schema.props.get('label')}</div>
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
                {isFailure && <ReactForms.Message>{externalValidation.error}</ReactForms.Message>}
                {this.state.collapsed ? preview : fieldset}
            </div>
        );
    },

    toggleCollapsed: function() {
        this.setState({collapsed: !this.state.collapsed});
    },

    onUpdate: function(value) {
        value = value.set('@id', this.state.url);
        this.props.value.setSerialized(value);
    }

});


var jsonSchemaToFormSchema = function(attrs) {
    var ReactForms = require('react-forms');
    var inputs = require('./inputs');
    var schemas = attrs.schemas,
        p = attrs.jsonNode,
        props = attrs.props,
        id = attrs.id,
        skip = attrs.skip || [],
        readonly = p.readonly || attrs.readonly || false,
        showReadOnly = attrs.showReadOnly,
        depth = attrs.depth || 1;
    if (props === undefined) {
        props = {};
    }
    if (p.title) props.label = p.title;
    if (p.description) props.hint = p.description;
    if (p.type == 'object') {
        if (p.formInput == 'file') {
            props.input = <inputs.FileInput />;
            return ReactForms.schema.Scalar(props);
        } else if (p.formInput == 'layout') {
            var layout = require('./layout');
            props.input = <layout.Layout editable={true} />;
            return ReactForms.schema.Scalar(props);
        } else {
            props.component = <ReactForms.Fieldset className={props.required ? "required" : ''} />;
        }
        var properties = {}, name;
        for (name in p.properties) {
            if (name == 'uuid' || name == 'schema_version') continue;
            if (p.properties[name].calculatedProperty) continue;
            if (!showReadOnly && p.properties[name].readonly) continue;
            if (_.contains(skip, name)) continue;
            var required = _.contains(p.required || [], name);
            var subprops = {required: required};
            var subschema = jsonSchemaToFormSchema({
                schemas: schemas,
                jsonNode: p.properties[name],
                props: subprops,
                readonly: readonly,
                showReadOnly: showReadOnly,
                depth: depth,
            });
            if (subschema) {
                properties[name] = subschema;
            }
        }
        return ReactForms.schema.Mapping(props, properties);
    } else if (p.type == 'array') {
        if (depth > 1 && p.items.linkFrom !== undefined) return null;
        var subschema = jsonSchemaToFormSchema({
            schemas: schemas,
            jsonNode: p.items,
            readonly: readonly,
            showReadOnly: showReadOnly,
            depth: depth,
        });
        if (!subschema) {
            return null;
        }
        props.component = <RepeatingFieldset className={props.required ? "required" : ""}
                                             noAddButton={readonly} noRemoveButton={readonly} />;
        return ReactForms.schema.List(props, subschema);
    } else if (p.type == 'boolean') {
        props.type = 'bool';
        return ReactForms.schema.Scalar(props);
    } else {
        var disabled = (readonly || p.readonly);
        if (props.required) props.component = <ReactForms.Field className="required" />;
        if (p.pattern) {
            props.validate = function(schema, value) { return (typeof value == 'string') ? value.match(p.pattern) : true; };
        }
        if (p['enum']) {
            var options = p['enum'].map(v => <option value={v}>{v}</option>);
            if (!p.default) {
                options = [<option value={null} />].concat(options);
            }
            props.input = <select className="form-control" disabled={disabled}>{options}</select>;
        } else if (p.linkTo) {
            var restrictions = {type: [p.linkTo]};
            props.input = (
                <inputs.ObjectPicker searchBase={"?mode=picker&type=" + p.linkTo}
                                     restrictions={restrictions} disabled={disabled} />
            );
        } else if (p.linkFrom) {
            // Backrefs have a linkFrom property in the form
            // (object type).(property name)
            var a = p.linkFrom.split('.'), linkType = a[0], linkProp = a[1];
            // FIXME Handle linkFrom abstract type.
            if (!schemas[linkType]) {
                return null;
            }
            // Get the schema for the child object, omitting the attribute that
            // refers to the parent.
            var linkFormSchema = jsonSchemaToFormSchema({
                schemas: schemas,
                jsonNode: schemas[linkType],
                skip: [linkProp],
                depth: depth + 1,
            });
            // Use a special FetchedFieldset component which can take either an IRI
            // or a full object as its value, and render a sub-form using the child
            // object schema.
            var component = <FetchedFieldset schema={linkFormSchema} />;
            // Default value for new children needs to refer to the parent.
            var defaultValue = jsonSchemaToDefaultValue(schemas[linkType]);
            defaultValue[linkProp] = id;
            return ReactForms.schema.Scalar({component: component, defaultValue: defaultValue});
        } else if (p.type == 'integer' || p.type == 'number') {
            props.type = 'number';
            props.input = <input type="number" disabled={disabled} />;
        } else if (p.formInput == 'textarea') {
            props.input = <textarea rows="4" disabled={disabled} />;
        } else {
            props.input = <input type="text" disabled={disabled} />;
        }
        return ReactForms.schema.Scalar(props);
    }
};


var jsonSchemaToDefaultValue = function(schema) {
    var defaultValue = {};
    _.each(schema.properties, function(property, name) {
        if (property.default !== undefined && !property.readonly) {
            defaultValue[name] = property['default'];
        }
    });
    return defaultValue;
};


var Form = module.exports.Form = React.createClass({
    contextTypes: {
        adviseUnsavedChanges: React.PropTypes.func,
        fetch: React.PropTypes.func
    },

    childContextTypes: {
        canSave: React.PropTypes.func,
        onTriggerSave: React.PropTypes.func,
        formEvents: React.PropTypes.object
    },
    getChildContext: function() {
        return {
            canSave: this.canSave,
            onTriggerSave: this.save,
            formEvents: this.state.formEvents
        };
    },

    getDefaultProps: function() {
        return {
            submitLabel: 'Save',
        };
    },

    getInitialState: function() {
        return {
            isValid: true,
            value: null,
            externalValidation: null,
            formEvents: new EventEmitter()
        };
    },

    componentDidUpdate: function(prevProps, prevState) {
        if (!_.isEqual(prevState.errors, this.state.errors)) {
            var error = document.querySelector('alert-danger');
            if (!error) {
                error = closest(document.querySelector('.rf-Message'), '.rf-Field,.rf-RepeatingFieldset');
            }
            if (error) {
                window.scrollTo(0, offset(error).top - document.getElementById('navbar').clientHeight);
            }
        }
    },

    render: function() {
        var ReactForms = require('react-forms');
        return (
            <div>
                <ReactForms.Form
                    schema={this.props.schema}
                    defaultValue={this.props.defaultValue}
                    externalValidation={this.state.externalValidation}
                    onUpdate={this.handleUpdate}
                    onSubmit={this.save} />
                <div className="pull-right">
                    <a href="" className="btn btn-default">Cancel</a>
                    {' '}
                    <button onClick={this.save} className="btn btn-success" disabled={!this.canSave()}>{this.props.submitLabel}</button>
                </div>
                {(this.state.errors || []).map(error => <div className="alert alert-danger">{error}</div>)}
            </div>
        );
    },

    handleUpdate: function(value, validation) {
        var nextState = {value: value, isValid: validation.isSuccess};
        if (!this.state.unsavedToken) {
            nextState.unsavedToken = this.context.adviseUnsavedChanges();
        }
        this.setState(nextState);
        this.state.formEvents.emit('update');
    },

    canSave: function() {
        return this.state.value && this.state.isValid && !this.state.editor_error && !this.communicating;
    },

    save: function(e) {
        e.preventDefault();
        e.stopPropagation();
        var value = this.state.value.toJS();
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
        // unflatten validation errors
        var externalValidation = {children: {}, error: null};
        var schemaErrors = [];
        if (data.errors !== undefined) {
            data.errors.map(function (error) {
                var name = error.name;
                var match = /^u?'([^']+)' is a required property$/.exec(error.description);
                if (match) {
                    name.push(match[1]);
                }
                var description = error.description;
                if (name.length) {
                    var v = externalValidation;
                    var schemaNode = this.props.schema;
                    for (var i = 0; i < name.length; i++) {
                        if (v.children[name[i]] === undefined) {
                            v.children[name[i]] = {children: {}, error: null};
                        }
                        if (schemaNode.children !== undefined) {
                            if (typeof name[i] === 'number') { // array
                                // might need to traverse into fetched fieldset
                                var component = schemaNode.children.props.get('component');
                                if (component !== undefined) {
                                    schemaNode = component.props.schema;
                                } else {
                                    schemaNode = schemaNode.children;
                                }
                            } else {
                                schemaNode = schemaNode.children.get(name[i]);
                            }
                        } else {
                            // we've reached a scalar; stop and show error here
                            description = name.slice(i).join('/') + ': ' + description;
                            break;                            
                        }
                        v = v.children[name[i]];
                    }
                    v.error = description;
                } else {
                    schemaErrors.push(description);
                }
            }.bind(this));
        } else if (data.title) {
            schemaErrors.push(data.title);
        }

        // convert to format expected by react-forms
        externalValidation = makeValidationResult(externalValidation);

        // make sure we scroll to error again
        this.setState({errors: null});

        this.setState({
            data: data,
            communicating: false,
            externalValidation: externalValidation,
            errors: schemaErrors
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
            schema: jsonSchemaToFormSchema({
                schemas: schemas,
                jsonNode: schemas[type],
                id: this.props.id,
                showReadOnly: this.props.showReadOnly,
            }),
            value: this.props.context || jsonSchemaToDefaultValue(schemas[type]),
        };
    },

    render: function() {
        return <Form {...this.props} defaultValue={this.state.value} schema={this.state.schema} />;
    }

});
