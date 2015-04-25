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
                    <EditForm {...this.props} />
                </fetched.FetchedData>
            </div>
        );
    }
});

var EditForm = module.exports.EditForm = React.createClass({
    contextTypes: {
        fetch: React.PropTypes.func
    },

    render: function () {
        var error = this.state.error;
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
                <ul style={{clear: 'both'}}>
                    {error && error.code === 422 ? error.errors.map(error => {
                        return <li className="alert alert-error"><b>{'/' + (error.name || []).join('/') + ': '}</b><span>{error.description}</span></li>;
                    }) : error ? <li className="alert alert-error">{JSON.stringify(error)}</li> : null}
                </ul>
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
            erred: false,
            value: JSON.stringify(sorted_json(this.props.data), null, 4)
        };
    },

    save: function (e) {
        e.preventDefault();
        var value = this.state.value;
        var url = this.props.context['@id'];
        var request = this.context.fetch(url, {
            method: 'PUT',
            headers: {
                'If-Match': this.props.etag,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: value
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

    receive: function (data) {
        var erred = (data['@type'] || []).indexOf('error') > -1;
        this.setState({
            data: data,
            communicating: false,
            erred: erred,
            error: erred ? data : undefined
        });
        if (!erred) this.props.navigate('');
    }
});


globals.content_views.register(ItemEdit, 'item', 'edit-json');
