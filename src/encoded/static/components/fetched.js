/** @jsx React.DOM */
'use strict';
var React = require('react');


var FetchedItems = module.exports.FetchedItems = React.createClass({
    getInitialState: function () {
        return {
            communicating: !!this.props.url,
            data: undefined
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
        if (this.request && this.request.state() == 'pending') {
            this.request.abort();
        }
        this.setState({
            communicating: !!url,
            data: undefined
        });
        if (!url) return;
        var $ = require('jquery');
        this.request = $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json'
        }).done(this.receive);
    },

    receive: function (data) {
        this.setState({
            data: data,
            communicating: false
        });
    },

    render: function() {
        if (!this.props.url) return;
        var Component = this.props.Component;
        var items = this.state.data && this.state.data['@graph'] || [];
        return (
            <div className={this.state.cummunicating ? 'communicating' : 'done'}>
                {this.transferPropsTo(
                    <Component Component={undefined} url={undefined} items={items} />
                )}
            </div>
        );
    }
});
