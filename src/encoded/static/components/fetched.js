'use strict';
var React = require('react');
var cloneWithProps = require('react/lib/cloneWithProps');
var parseAndLogError = require('./mixins').parseAndLogError;
var globals = require('./globals');
var ga = require('google-analytics');
var _ = require('underscore');


var Param = module.exports.Param = React.createClass({
    contextTypes: {
        fetch: React.PropTypes.func,
        session: React.PropTypes.object
    },

    getDefaultProps: function() {
        return {type: 'json'};
    },

    getInitialState: function () {
        return {
            fetchedRequest: undefined,
        };
    },

    componentDidMount: function () {
        this.fetch(this.props.url);
    },

    componentWillUnmount: function () {
        var xhr = this.state.fetchedRequest;
        if (xhr) {
            console.log('abort param xhr');
            xhr.abort();
        }
    },

    componentWillReceiveProps: function (nextProps, nextContext) {
        if (!this.state.fetchedRequest && nextProps.url === undefined) return;
        if (this.state.fetchedRequest &&
            nextProps.url === this.props.url &&
            nextContext.session === this.context.session) return;
        this.fetch(nextProps.url);
    },

    fetch: function (url) {
        var request = this.state.fetchedRequest;
        if (request) request.abort();

        if (!url) {
            this.props.handleFetch();
            this.setState({
                fetchedRequest: undefined,
            });
        }
        // XXX Errors should really result in a separate component being rendered.
        if (this.props.type === 'json') {
            request = this.context.fetch(url, {
                headers: {'Accept': 'application/json'}
            });
            request.then(response => {
                if (!response.ok) throw response;
                return response.json();
            })
            .catch(parseAndLogError.bind(undefined, 'fetchedRequest'))
            .then(this.receive);
        } else if (this.props.type === 'text') {
            request = this.context.fetch(url);
            request.then(response => {
                if (!response.ok) throw response;
                return response.text();
            })
            .catch(parseAndLogError.bind(undefined, 'fetchedRequest'))
            .then(this.receive);
        } else if (this.props.type === 'blob') {
            request = this.context.fetch(url);
            request.then(response => {
                if (!response.ok) throw response;
                return response.blob();
            })
            .catch(parseAndLogError.bind(undefined, 'fetchedRequest'))
            .then(this.receive);
        } else {
            throw "Unsupported type: " + this.props.type;
        }

        this.setState({
            fetchedRequest: request
        });
    },

    receive: function (data) {
        var result = {};
        result[this.props.name] = data;
        if (this.props.etagName) {
            result[this.props.etagName] = this.state.fetchedRequest.etag;
        }
        this.props.handleFetch(result);
    },

    render: function() { return null; }
});


var FetchedData = module.exports.FetchedData = React.createClass({
    contextTypes: {
        session: React.PropTypes.object
    },

    getInitialState: function() {
        return {};
    },

    handleFetch: function(result) {
        this.setState(result);
    },

    render: function () {
        var params = [];
        var communicating = false;
        var children = [];
        if (this.props.children) {
            React.Children.forEach(this.props.children, function(child) {
                if (child.type === Param.type) {
                    params.push(cloneWithProps(child, {
                        key: child.props.name,
                        handleFetch: this.handleFetch,
                    }));
                    if (this.state[child.props.name] === undefined) {
                        communicating = true;
                    }                    
                } else {
                    children.push(child);
                }
            }, this);
        }

        if (!params.length) {
            return null;
        }
        if (!this.context.session) {
            return (
                <div className="communicating">
                    <div className="loading-spinner"></div>
                </div>
            );
        }

        var errors = params.map(param => this.state[param.props.name])
            .filter(obj => obj && (obj['@type'] || []).indexOf('Error') > -1);

        if (errors.length) {
            return (
                <div className="error done">
                    {errors.map(error => {
                        var ErrorView = globals.content_views.lookup(error);
                        return <ErrorView {...this.props} context={error} />;
                    })}
                </div>
            );
        }

        if (communicating) {
            return (
                <div className="communicating">
                    <div className="loading-spinner"></div>
                    {params}
                </div>
            );
        }

        return (
            <div className="done">
                {children.map((child, i) => cloneWithProps(child, _.extend({key: i}, this.props, this.state)))}
                {params}
            </div>
        );
    }
});


var Items = React.createClass({

    render: function() {
        var Component = this.props.Component;
        var data = this.props.data;
        var items = data ? data['@graph'] : [];
        return <Component {...this.props} items={items} total={data.total} />;
    }

});


var FetchedItems = module.exports.FetchedItems = React.createClass({
    
    render: function() {
        return (
            <FetchedData>
                <Param name="data" url={this.props.url} />
                <Items {...this.props} />
            </FetchedData>
        );
    }

});
