'use strict';
var React = require('react');
var globals = require('./globals');
var parseAndLogError = require('./mixins').parseAndLogError;
var fetched = require('./fetched');
var _ = require('underscore');
var ga = require('google-analytics');
var Ace = require('./ace');
var ScriptReady = require('./scriptready');
var Spinner = require('./spinner');
var sorted_json = require('../libs/sorted_json');

var ItemEdit = module.exports.ItemEdit = React.createClass({
    getInitialState: function () {
        return {
            error: false,
        };
    },

    render: function() {
        var error = this.state.error;
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
                    <fetched.Param name="defaultValue" url={url} etagName="etag" />
                    <EditForm
                        method="PUT"
                        action={this.props.context['@id']}
                        onResponse={this.handleResponse} />
                </fetched.FetchedData>
                <ul style={{clear: 'both'}}>
                    {error && error.code === 422 ? error.errors.map(error => {
                        return <li className="alert alert-error"><b>{'/' + (error.name || []).join('/') + ': '}</b><span>{error.description}</span></li>;
                    }) : error ? <li className="alert alert-error">{JSON.stringify(error)}</li> : null}
                </ul>
            </div>
        );
    },

    handleResponse: function (data) {
        var erred = (data['@type'] || []).indexOf('error') > -1;
        if (erred) {
            this.setState({error: data});
        } else {
            this.props.navigate('');
        }
    }
});


var JSONRequest = module.exports.JSONRequest = React.createClass({
    mixins: [require('react/lib/LinkedStateMixin')],
    getInitialState: function () {
        return {
            response: null,
            action: '',
            method: 'GET'
        };
    },
    render: function() {
        return (
            <div className='json-form'>
                <header className="row">
                    <div className="col-sm-12">
                        <h2>JSON Request</h2>
                    </div>
                </header>
                <select valueLink={this.linkState('method')}>
                    <option value="GET">GET</option>
                    <option value="POST">POST</option>
                    <option value="PUT">PUT</option>
                    <option value="PATCH">PATCH</option>
                </select>
                <input type="text" valueLink={this.linkState('action')} placeholder="URL" />
                {this.state.method !== 'GET' ?
                    <EditForm
                        defaultValue=""
                        method={this.state.method}
                        action={this.state.action}
                        onResponse={this.handleResponse} />
                : null}
                {this.state.response ?
                    <section className="view-detail panel" style={{clear: 'both'}}>
                        <div className="container">
                            <pre>{JSON.stringify(sorted_json(this.state.response), null, 4)}</pre>
                        </div>
                    </section>
                : null}
            </div>
        );
    },

    handleResponse: function (data) {
        this.setState({response: data});
    }
});

globals.content_views.register(JSONRequest, 'portal', 'json-request');


var EditForm = module.exports.EditForm = React.createClass({
    contextTypes: {
        fetch: React.PropTypes.func
    },

    render: function () {
        return (
            <div>
                <ScriptReady scripts={['brace']} spinner={<Spinner />}>
                    <Ace
                        value={this.state.value}
                        onChange={this.handleChange}
                        onChangeAnnotation={this.hasErrors}
                        mode="ace/mode/json"
                        options={{
                            maxLines: 1000,
                            minLines: 24
                        }}
                        style={{
                            position: "relative !important",
                            border: "1px solid lightgray",
                            margin: "auto",
                            width: "100%"
                        }} />
                </ScriptReady>
                <div style={{"float": "right", "margin": "10px"}}>
                    <a href="" className="btn btn-default">Cancel</a>
                    {' '}
                    <button onClick={this.save} className="btn btn-success" disabled={this.communicating || this.state.editor_error}>Save</button>
                </div>
            </div>
        );
    },

    handleChange: function (value) {
        this.setState({value: value});
    },

    hasErrors: function (editor) {
        var annotations = editor.getSession().getAnnotations();
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
            value: this.props.defaultValue === '' ? '' : JSON.stringify(sorted_json(this.props.defaultValue), null, 4)
        };
    },

    save: function (e) {
        e.preventDefault();
        var value = this.state.value;
        var headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        };
        if (this.props.etag) {
            headers['If-Match'] = this.props.etag;
        }
        var request = this.context.fetch(this.props.action, {
            method: this.props.method,
            headers: headers,
            body: value
        });
        request.then(response => {
            if (!response.ok) throw response;
            return response.json();
        })
        .catch(parseAndLogError.bind(undefined, 'putRequest'))
        .then(data => {
            this.setState({communicating: false});
            this.props.onResponse && this.props.onResponse(data);
        });
        this.setState({
            communicating: true,
            putRequest: request
        });
    }
});


globals.content_views.register(ItemEdit, 'item', 'edit-json');
