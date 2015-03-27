'use strict';
var EventEmitter = require('events').EventEmitter;
var React = require('react');
var ReactForms = require('react-forms');
var parseAndLogError = require('./mixins').parseAndLogError;
var closest = require('../libs/closest');
var offset = require('../libs/offset');
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


class JSONNode extends ReactForms.schema.ScalarNode {
    serialize(value) {
        return JSON.stringify(value, null, 4);
    }
    deserialize(value) {
        return (typeof value === 'string') ? JSON.parse(value) : value;
    }
}
module.exports.JSONNode = JSONNode;


var makeValidationResult = function(validation) {
    return new ReactForms.ValidationResult(
        validation.error ? validation.error : null,
        validation.children ? _.mapObject(validation.children, function(v, k) {
            return makeValidationResult(v);
        }) : null
    );
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
        return (
            <div>
                <ReactForms.Form
                    schema={this.props.schema}
                    defaultValue={this.props.defaultValue}
                    externalValidation={this.state.externalValidation}
                    onUpdate={this.handleUpdate} />
                <div className="pull-right">
                    <a href="" className="btn btn-default">Cancel</a>
                    {' '}
                    <button onClick={this.save} className="btn btn-success" disabled={!this.canSave()}>Save</button>
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
        var url = data['@graph'][0]['@id'];
        this.props.navigate(url);
    },

    receive: function (data) {
        var erred = (data['@type'] || []).indexOf('error') > -1;
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
                var match = /u'(\w+)' is a required property/.exec(error.description);
                if (match) {
                    name.push(match[1]);
                }
                if (name.length) {
                    var v = externalValidation;
                    for (var i = 0; i < name.length; i++) {
                        if (v.children[name[i]] === undefined) {
                            v.children[name[i]] = {children: {}, error: null};
                        }
                        v = v.children[name[i]];
                    }
                    v.error = error.description;
                } else {
                    schemaErrors.push(error.description);
                }
            });
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
