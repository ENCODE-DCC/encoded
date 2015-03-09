'use strict';
var React = require('react');
var ReactForms = require('react-forms');
var parseAndLogError = require('./mixins').parseAndLogError;
var globals = require('./globals');
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


var Form = module.exports.Form = React.createClass({
    contextTypes: {
        adviseUnsavedChanges: React.PropTypes.func,
        fetch: React.PropTypes.func
    },

    childContextTypes: {
        onTriggerSave: React.PropTypes.func
    },
    getChildContext: function() {
        return {
            onTriggerSave: this.save
        };
    },

    getInitialState: function() {
        return {
            value: this.props.defaultValue,
            externalValidation: null,
        };
    },

    componentDidUpdate: function(prevProps, prevState) {
        if (!_.isEqual(prevState.errors, this.state.errors)) {
            var $ = require('jquery');
            var $error = $('alert-danger:first');
            if (!$error.length) {
                $error = $('.rf-Message:first').closest('.rf-Field,.rf-RepeatingFieldset');
            }
            if ($error.length) {
                $('body').animate({scrollTop: $error.offset().top - $('#navbar').height()}, 200);
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
                    onChange={this.handleChange} />
                <div className="pull-right">
                    <a href="" className="btn btn-default">Cancel</a>
                    {' '}
                    <button onClick={this.save} className="btn btn-success" disabled={this.communicating || this.state.editor_error}>Save</button>
                </div>
                {(this.state.errors || []).map(error => <div className="alert alert-danger">{error}</div>)}
            </div>
        );
    },

    handleChange: function(value) {
        var nextState = {value: value};
        if (!this.state.unsavedToken) {
            nextState.unsavedToken = this.context.adviseUnsavedChanges();
        }
        this.setState(nextState);
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
                'If-Match': this.props.etag,
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
        var externalValidation = {children: {}, validation: {}};
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
                            v.children[name[i]] = {children: {}, validation: {}};
                        }
                        v = v.children[name[i]];
                    }
                    v.validation = {
                        failure: error.description,
                        validation: {failure: error.description}
                    };
                } else {
                    schemaErrors.push(error.description);
                }
            });
        }

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
