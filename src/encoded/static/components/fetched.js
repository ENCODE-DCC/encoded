/** @jsx React.DOM */
'use strict';
var React = require('react');
var parseError = require('./mixins').parseError;
var globals = require('./globals');


var FetchedItems = module.exports.FetchedItems = React.createClass({
    getInitialState: function () {
        return {
            communicating: !!this.props.url,
            data: undefined,
            fetchedItemsRequest: undefined,
            erred: false
        };
    },

    componentDidMount: function () {
        this.fetch(this.props.url);
    },

    componentWillReceiveProps: function (nextProps) {
        if (nextProps.url === this.props.url) return;
        this.fetch(nextProps.url);
    },

    fetch: function (url) {
        var communicating;
        var xhr = this.state.fetchedItemsRequest;
        if (xhr && xhr.state() == 'pending') {
            xhr.abort();
        }
        if (!url) {
            this.setState({
                communicating: false,
                data: undefined,
                fetchedItemsRequest: undefined,
                erred: false
            });
        }
        var $ = require('jquery');
        xhr = $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json'
        }).done(this.receive);
        xhr.href = url;
        this.setState({
            communicating: true,
            fetchedItemsRequest: xhr
        });
    },

    fail: function (xhr, status, error) {
        if (status == 'abort') return;
        var ga = window.ga;
        var data = parseError(xhr, status);
        ga('send', 'exception', {
            'exDescription': 'fetchedRequest:' + status + ':' + xhr.statusText,
            'location': window.location.href
        });
        this.receiveContextResponse(data, status, xhr, true);
    },

    receive: function (data, status, xhr, erred) {
        this.setState({
            data: data,
            communicating: false,
            erred: erred
        });
    },

    render: function() {
        var url = this.props.url;
        var data = this.state.data;
        var key = this.props.key || url || undefined;
        var Component = this.props.Component;
        if (!url) return (
            <div key={key} className="empty done" style={{display: 'none'}}></div>
        );
        if (this.state.communicating) return (
            <div key={key} className="communicating"></div>
        );
        if (this.state.erred) {
            Component = globals.content_views.lookup(data);
            return (
                <div key={key} className="error done">
                    {this.transferPropsTo(
                        <Component Component={undefined} url={undefined} context={data} />
                    )}
                </div>
            );
        }
        var items = data && data['@graph'] || [];
        if (!items.length) return (
            <div key={key} className="empty done" style={{display: 'none'}}></div>
        );
        return (
            <div key={key} className="done">
                {this.transferPropsTo(
                    <Component Component={undefined} url={undefined} items={items} />
                )}
            </div>
        );
    }
});
