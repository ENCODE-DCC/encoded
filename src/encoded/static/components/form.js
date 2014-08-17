/** @jsx React.DOM */
'use strict';
var React = require('react');
var ReactForms = require('react-forms');
var parseError = require('./mixins').parseError;
var globals = require('./globals');


var FormFor = ReactForms.FormFor;


var Form = module.exports.Form = React.createClass({
    mixins: [ReactForms.FormMixin],

    contextTypes: {
        adviseUnsavedChanges: React.PropTypes.func
    },

    childContextTypes: {
        onTriggerSave: React.PropTypes.func
    },
    getChildContext: function() {
        return {
            onTriggerSave: this.save
        }
    },

    render: function() {
        return (
          <form>
            {(this.state.errors || []).map(error => <div className="alert alert-danger">{error}</div>)}
            <FormFor externalValidation={this.state.externalValidation} />
            <div className="pull-right">
                <a href="" className="btn btn-default">Cancel</a>
                {' '}
                <button onClick={this.save} className="btn btn-success" disabled={this.communicating || this.state.editor_error}>Save</button>
            </div>
          </form>
        )
    },

    valueUpdated: function(value) {
        if (!this.state.unsavedToken) {
            this.setState({unsavedToken: this.context.adviseUnsavedChanges()});
        }
    },

    save: function(e) {
        e.preventDefault();
        var $ = require('jquery');
        var value = this.value().value;
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
        return false;
    },

    finish: function (data) {
        if (this.state.unsavedToken) {
            this.state.unsavedToken.release();
            this.setState({unsavedToken: null});
        }
        this.props.navigate(data['@graph'][0]['@id'] + '?datastore=database');
    },

    fail: function (xhr, status, error) {
        if (status == 'abort') return;
        var ga = window.ga;
        var data = parseError(xhr, status);
        ga('send', 'exception', {
            'exDescription': 'putRequest:' + status + ':' + xhr.statusText,
            'location': window.location.href
        });
        this.receive(data, status, xhr);
    },

    receive: function (data, status, xhr) {
        var externalValidation = {children: {}};
        var schemaErrors = [];
        if (data.errors !== undefined) {
            data.errors.map(function (error) {
                if (error.name.length) {
                    externalValidation.children[error.name[0]] = {validation: {failure: error.description}};
                } else {
                    schemaErrors.push(error.description);
                }
            });
        }

        this.setState({
            data: data,
            communicating: false,
            externalValidation: externalValidation,
            errors: schemaErrors
        });
    }
});
