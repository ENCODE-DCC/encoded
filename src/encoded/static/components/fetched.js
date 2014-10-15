/** @jsx React.DOM */
'use strict';
var React = require('react');
var cloneWithProps = require('react/lib/cloneWithProps');
var parseError = require('./mixins').parseError;
var globals = require('./globals');
var ga = require('google-analytics');
var merge = require('react/lib/merge');


var Fetched = module.exports.Fetched = React.createClass({
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

    getInitialState: function() {
        return {
            error: false,
            data: {
                Component: undefined,
                url: undefined,
                fetched_prop_name: undefined,
                fetched_etag_name: undefined
            }
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
        }
        if (data) {
            nextState['data'] = merge(this.state.data, data);
        }
        this.setState(nextState);
    },

    render: function () {
        var fetchedProps = [];
        var communicating = false;
        if (this.props.children) {
            React.Children.forEach(this.props.children, function(child) {
                fetchedProps.push(cloneWithProps(child, {
                    key: child.props.name,
                    handleFetch: this.handleFetch,
                    handleFetchStart: this.handleFetchStart,
                    session: this.props.session
                }));
                if (this.state.data[child.props.name] === undefined) {
                    communicating = true;
                }
            }, this);
        } else {
            fetchedProps = [
                <Fetched key={this.props.fetched_prop_name || 'data'}
                         name={this.props.fetched_prop_name || 'data'}
                         url={this.props.url}
                         etagName={this.props.fetched_etag_name}
                         handleFetch={this.handleFetch}
                         handleFetchStart={this.handleFetchStart}
                         session={this.props.session} />
            ];
            communicating = (this.state.data.data === undefined);
        }

        if (!this.props.loadingComplete || !fetchedProps.length) {
            return null;
        }

        if (this.state.error) {
            Component = globals.content_views.lookup(this.state.error);
            return (
                <div className="error done">
                    {this.transferPropsTo(
                        <Component Component={undefined} url={undefined} context={this.state.error} />
                    )}
                </div>
            );
        }

        if (communicating) {
            return (
                <div className="communicating">
                    <div className="loading-spinner"></div>
                    {fetchedProps}
                </div>
            );
        }

        var Component = this.props.Component;
        return (
            <div className="done">
                {this.transferPropsTo(Component(this.state.data))}
                {fetchedProps}
            </div>
        );
    }
});


var Items = React.createClass({

    render: function() {
        var Component = this.props.ItemsComponent;
        var data = this.props.data;
        var items = data ? data['@graph'] : [];
        if (!items.length) return null;
        return this.transferPropsTo(<Component items={items} total={data.total} />);
    }

});


var FetchedItems = module.exports.FetchedItems = React.createClass({
    
    render: function() {
        return this.transferPropsTo(<FetchedData Component={Items} ItemsComponent={this.props.Component} />);
    }

});
