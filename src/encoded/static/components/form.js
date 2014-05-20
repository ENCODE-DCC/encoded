/** @jsx React.DOM */
'use strict';
var React = require('react');
var ReactForms = require('react-forms');
var parseError = require('./mixins').parseError;
var globals = require('./globals');


var FormFor = ReactForms.FormFor;


var Form = module.exports.Form = React.createClass({
    mixins: [ReactForms.FormMixin],

    // make sure the Form finds the data from FetchedData
    getDefaultProps: function() {
        return {
            value: this.props.data
        }
    },

    render: function() {
        var error = this.state.error;
        return (
          <form>
            <FormFor />
            <div className="pull-right">
                <a href="" className="btn btn-default">Cancel</a>
                {' '}
                <button onClick={this.save} className="btn btn-success" disabled={this.communicating || this.state.editor_error}>Save</button>
            </div>
            <ul style={{clear: 'both'}}>
                {error && error.code === 422 ? error.errors.map(function (error) {
                    return <li className="alert alert-error"><b>{'/' + error.name.join('/') + ': '}</b><span>{error.description}</span></li>;
                }) : error ? <li className="alert alert-error">{JSON.stringify(error)}</li> : null}
            </ul>
          </form>
        )
    },

    save: function() {
        var $ = require('jquery');
        var value = this.state.value;
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
        this.props.navigate(data['@graph'][0]['@id']);
    },

    fail: function (xhr, status, error) {
        if (status == 'abort') return;
        var ga = window.ga;
        var data = parseError(xhr, status);
        ga('send', 'exception', {
            'exDescription': 'putRequest:' + status + ':' + xhr.statusText,
            'location': window.location.href
        });
        this.receive(data, status, xhr, true);
    },

    receive: function (data, status, xhr, erred) {
        this.setState({
            data: data,
            communicating: false,
            erred: erred,
            error: erred ? data : undefined
        });
    }
});
