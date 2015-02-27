'use strict';
var React = require('react');
var cloneWithProps = require('react/lib/cloneWithProps');
var parseError = require('./mixins').parseError;
var globals = require('./globals');
var ga = require('google-analytics');
var _ = require('underscore');


var Param = module.exports.Param = React.createClass({
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
        if (xhr && xhr.state() == 'pending') {
            xhr.abort();
        }
    },

    componentWillReceiveProps: function (nextProps) {
        if (!this.state.fetchedRequest && nextProps.url === undefined) return;
        if (this.state.fetchedRequest &&
            nextProps.url === this.props.url &&
            nextProps.session === this.props.session) return;
        this.fetch(nextProps.url);
    },

    fetch: function (url) {
        var xhr = this.state.fetchedRequest;
        if (xhr && xhr.state() == 'pending') {
            xhr.abort();
        }
        if (!url) {
            this.props.handleFetch();
            this.setState({
                fetchedRequest: undefined,
            });
        }
        var $ = require('jquery');
        xhr = $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json'
        }).fail(this.fail)
        .done(this.receive);
        xhr.href = url;
        this.setState({
            fetchedRequest: xhr
        });
    },

    fail: function (xhr, status, error) {
        if (status == 'abort') return;
        var data = parseError(xhr, status);
        ga('send', 'exception', {
            'exDescription': 'fetchedRequest:' + status + ':' + xhr.statusText,
            'location': window.location.href
        });
        this.receive(data, status, xhr, true);
    },

    receive: function (res, status, xhr, erred) {
        var error = erred ? res : null;
        var data = {};
        if (!erred) {
            if (this.props.converter) {
                res = this.props.converter(res);
            }
            data[this.props.name] = res;
            if (this.props.etagName) {
                data[this.props.etagName] = xhr.getResponseHeader('ETag');
            }
        }
        this.props.handleFetch(data, error);
    },

    render: function() { return null; }
});


var FetchedData = module.exports.FetchedData = React.createClass({

    getDefaultProps: function() {
        return {loadingComplete: true};
    },

    getInitialState: function() {
        return {
            error: false,
            data: {},
        };
    },

    shouldComponentUpdate: function(nextProps, nextState) {
        if (!nextProps.loadingComplete) {
            return false;
        } else {
            return true;
        }
    },

    handleFetch: function(data, error) {
        var nextState = {
            error: error
        };
        if (data) {
            nextState['data'] = _.extend({}, this.state.data, data);
        }
        this.setState(nextState);
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
                        handleFetchStart: this.handleFetchStart,
                        session: this.props.session
                    }));
                    if (this.state.data[child.props.name] === undefined) {
                        communicating = true;
                    }                    
                } else {
                    children.push(child);
                }
            }, this);
        }

        if (!this.props.loadingComplete || !params.length) {
            return null;
        }

        if (this.state.error) {
            var ErrorView = globals.content_views.lookup(this.state.error);
            if (!ErrorView) { return <pre>JSON.stringify(this.state.error)</pre>; }
            return (
                <div className="error done">
                    <ErrorView {...this.props} context={this.state.error} />
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
                {children.map(child => cloneWithProps(child, _.extend({}, this.props, this.state.data)))}
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
        if (!items.length) return null;
        return <Component {...this.props} items={items} total={data.total} />;
    }

});


var FetchedItems = module.exports.FetchedItems = React.createClass({
    
    render: function() {
        return (
            <FetchedData loadingComplete={this.props.loadingComplete}>
                <Param name="data" url={this.props.url} />
                <Items {...this.props} />
            </FetchedData>
        );
    }

});
