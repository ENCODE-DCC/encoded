/** @jsx React.DOM */
'use strict';
var React = require('react');
var parseError = require('./mixins').parseError;
var globals = require('./globals');


var Fetched = module.exports.Fetched = {
    getInitialState: function () {
        return {
            communicating: !!this.props.url,
            data: undefined,
            fetchedRequest: undefined,
            erred: false
        };
    },

    componentDidMount: function () {
        if (!this.props.session) return;
        this.fetch(this.props.url);
    },

    componentWillReceiveProps: function (nextProps) {
        if (!nextProps.session || (
            nextProps.url === this.props.url &&
            nextProps.session === this.props.session)) return;
        this.fetch(nextProps.url);
    },

    fetch: function (url) {
        var communicating;
        var xhr = this.state.fetchedRequest;
        if (xhr && xhr.state() == 'pending') {
            xhr.abort();
        }
        if (!url) {
            this.setState({
                communicating: false,
                data: undefined,
                fetchedRequest: undefined,
                erred: false
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
            communicating: true,
            fetchedRequest: xhr
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
        this.receive(data, status, xhr, true);
    },

    receive: function (data, status, xhr, erred) {
        this.setState({
            data: data,
            communicating: false,
            erred: erred
        });
    }
};


var FetchedData = module.exports.FetchedData = React.createClass({
    mixins: [Fetched],
    render: function () {
        var url = this.props.url;
        var data = this.state.data;
        var key = url;
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
        return (
            <div key={key} className="done">
                {this.transferPropsTo(
                    <Component Component={undefined} url={undefined} data={data} />
                )}
            </div>
        );
    }
});


var FetchedItems = module.exports.FetchedItems = React.createClass({
    mixins: [Fetched],
    render: function () {
        var url = this.props.url;
        var data = this.state.data;
        var key = url;
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
