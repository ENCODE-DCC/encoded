'use strict';
var React = require('react');
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

    componentWillReceiveProps: function (nextProps, nextContext) {
        if (!this.state.fetchedRequest && nextProps.url === undefined) return;
        if (this.state.fetchedRequest &&
            nextProps.url === this.props.url &&
            _.isEqual(nextContext.session, this.context.session)) return;
        this.fetch(nextProps.url);
    },

    componentWillUnmount: function () {
        var xhr = this.state.fetchedRequest;
        if (xhr) {
            console.log('abort param xhr');
            xhr.abort();
        }
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
            .catch(globals.parseAndLogError.bind(undefined, 'fetchedRequest'))
            .then(this.receive);
        } else if (this.props.type === 'text') {
            request = this.context.fetch(url);
            request.then(response => {
                if (!response.ok) throw response;
                return response.text();
            })
            .catch(globals.parseAndLogError.bind(undefined, 'fetchedRequest'))
            .then(this.receive);
        } else if (this.props.type === 'blob') {
            request = this.context.fetch(url);
            request.then(response => {
                if (!response.ok) throw response;
                return response.blob();
            })
            .catch(globals.parseAndLogError.bind(undefined, 'fetchedRequest'))
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
        // One state per <Param> child component, keyed by "name" with a value of search results from server
        return {};
    },

    handleFetch: function(result) {
        // Set state to returned search result data to cause rerender of child components
        this.setState(result);
    },

    render: function () {
        var params = [];
        var communicating = false;
        var children = [];

        // Collect <Param> and non-<Param> child components into appropriate arrays
        if (this.props.children) {
            React.Children.forEach(this.props.children, child => {
                if (child.type === Param) {
                    // <Param> child component; add to array of <Param> child components with this.props.key of its name and calling `handleFetch`
                    params.push(React.cloneElement(child, {
                        key: child.props.name,
                        handleFetch: this.handleFetch,
                    }));

                    // Still communicating with server if handleFetch not yet called
                    if (this.state[child.props.name] === undefined) {
                        communicating = true;
                    }                    
                } else {
                    // Some non-<Param> child; just push it unmodified onto `children` array
                    children.push(child);
                }
            });
        }

        // If no <Param> components, nothing to render here
        if (!params.length) {
            return null;
        }

        // If no login info yet, keep displaying the loading spinner
        if (!this.context.session) {
            return (
                <div className="communicating">
                    <div className="loading-spinner"></div>
                </div>
            );
        }

        // Detect whether a <Param> component returned an "Error" @type object
        var errors = params.map(param => this.state[param.props.name])
            .filter(obj => obj && (obj['@type'] || []).indexOf('Error') > -1);

        // If we got an error, display the error string on the web page
        if (errors.length) {

            // Render whatever error we got back from the server on the page.
            return (
                <div className="error done">
                    {errors.map(error => {
                        var ErrorView = globals.content_views.lookup(error);
                        return <ErrorView {...this.props} context={error} />;
                    })}
                </div>
            );
        }

        // If we haven't gotten a response, continue showing the loading spinner
        if (communicating) {
            return (
                <div className="communicating">
                    <div className="loading-spinner"></div>
                    {params}
                </div>
            );
        }

        // Successfully got data. Display in the web page
        return (
            <div className="done">
                {children.map((child, i) => React.cloneElement(child, _.extend({key: i}, this.props, this.state)))}
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
            <FetchedData ignoreErrors={this.props.ignoreErrors}>
                <Param name="data" url={this.props.url} />
                <Items {...this.props} />
            </FetchedData>
        );
    }

});
