/** @jsx React.DOM */
'use strict';
var React = require('react');
var globals = require('./globals');
var parseError = require('./mixins').parseError;
var fetched = require('./fetched');
var _ = require('underscore');
var $script = require('scriptjs');
var ga = require('google-analytics');


var sorted_json = module.exports.sorted_json = function (obj) {
    if (obj instanceof Array) {
        return obj.map(function (value) {
            return sorted_json(value);
        });
    } else if (obj instanceof Object) {
        var sorted = {};
        Object.keys(obj).sort().forEach(function (key) {
            sorted[key] = obj[key];
        });
        return sorted;
    } else {
        return obj;
    }
};


var ItemEdit = module.exports.ItemEdit = React.createClass({
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-item');
        var title = globals.listing_titles.lookup(context)({context: context});
        var url = this.props.context['@id'] + '?frame=edit';
        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <h2>Edit {title}</h2>
                    </div>
                </header>
                <fetched.FetchedData loadingComplete={this.props.loadingComplete}>
                    <fetched.Param name="data" url={url} etagName="etag" />
                    {this.transferPropsTo(<EditForm />)}
                </fetched.FetchedData>
            </div>
        );
    }
});

var EditForm = module.exports.EditForm = React.createClass({
    render: function () {
        var error = this.state.error;
        return (
            <div>
                <div ref="editor" style={{
                    position: "relative !important",
                    border: "1px solid lightgray",
                    margin: "auto",
                    width: "100%"
                }}></div>
                <div style={{"float": "right", "margin": "10px"}}>
                    <a href="" className="btn btn-default">Cancel</a>
                    {' '}
                    <button onClick={this.save} className="btn btn-success" disabled={this.communicating || this.state.editor_error}>Save</button>
                </div>
                <ul style={{clear: 'both'}}>
                    {error && error.code === 422 ? error.errors.map(error => {
                        return <li className="alert alert-error"><b>{'/' + (error.name || []).join('/') + ': '}</b><span>{error.description}</span></li>;
                    }) : error ? <li className="alert alert-error">{JSON.stringify(error)}</li> : null}
                </ul>
            </div>
        );
    },

    componentDidMount: function () {
        $script('brace', this.setupEditor);
    },

    setupEditor: function () {
        var ace = require('brace');
        require('brace/mode/json');
        require('brace/theme/solarized_light');
        var value = JSON.stringify(sorted_json(this.props.data), null, 4);
        var editor = ace.edit(this.refs.editor.getDOMNode());
        var session = editor.getSession();
        session.setMode('ace/mode/json');
        editor.setValue(value);
        editor.setOptions({
            maxLines: 1000,
            minLines: 24
        });
        editor.clearSelection();
        this.setState({editor: editor});
        session.on("changeAnnotation", this.hasErrors);
    },

    hasErrors: function () {
        var annotations = this.state.editor.getSession().getAnnotations();
        var has_error = annotations.reduce(function (value, anno) {
            return value || (anno.type === "error");
        }, false);
        this.setState({editor_error: has_error});
    },

    getInitialState: function () {
        return {
            communicating: false,
            data: undefined,
            putRequest: undefined,
            erred: false
        };
    },

    save: function (event) {
        var $ = require('jquery');
        var value = this.state.editor.getValue();
        var url = this.props.context['@id'];
        var xhr = $.ajax({
            url: url,
            type: 'PUT',
            contentType: "application/json",
            data: value,
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

    finish: function () {
        this.props.navigate('');
    },

    fail: function (xhr, status, error) {
        if (status == 'abort') return;
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


globals.content_views.register(ItemEdit, 'item', 'edit-json');
