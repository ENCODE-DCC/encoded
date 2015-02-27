'use strict';
var React = require('react');
var ReactForms = require('react-forms');
var parseError = require('./mixins').parseError;
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
        adviseUnsavedChanges: React.PropTypes.func
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
            externalValidation: {},
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
        var $ = require('jquery');
        var value = this.value().value;
        filterValue(value);
        var method = this.props.method;
        var url = this.props.action;
        var xhr = $.ajax({
            url: url,
            type: method,
            contentType: "application/json",
            data: JSON.stringify(value),
            dataType: 'json',
            headers: {'If-Match': this.props.etag}
        }).fail(this.fail)
        .done(this.receive);
        xhr.href = url;
        this.setState({
            communicating: true,
            putRequest: xhr
        });
        xhr.done(this.finish);
    },

    finish: function (data) {
        if (this.state.unsavedToken) {
            this.state.unsavedToken.release();
            this.setState({unsavedToken: null});
        }
        var url = data['@graph'][0]['@id'];
        this.props.navigate(url);
    },

    fail: function (xhr, status, error) {
        if (status == 'abort') return;
        var data = parseError(xhr, status);
        ga('send', 'exception', {
            'exDescription': 'putRequest:' + status + ':' + xhr.statusText,
            'location': window.location.href
        });
        this.receive(data, status, xhr);
    },

    receive: function (data, status, xhr) {
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
