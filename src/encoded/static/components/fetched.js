import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import globals from './globals';


export class Param extends React.Component {
    constructor() {
        super();
        this.state = {
            fetchedRequest: undefined,
        };
        this.receive = this.receive.bind(this);
        this.fetch = this.fetch.bind(this);
    }

    componentDidMount() {
        this.fetch(this.props.url);
    }

    componentWillReceiveProps(nextProps, nextContext) {
        if (!this.state.fetchedRequest && nextProps.url === undefined) return;
        if (this.state.fetchedRequest &&
            nextProps.url === this.props.url &&
            _.isEqual(nextContext.session, this.context.session)) return;
        this.fetch(nextProps.url);
    }

    componentWillUnmount() {
        const xhr = this.state.fetchedRequest;
        if (xhr) {
            console.log('abort param xhr');
            xhr.abort();
            this.props.handleAbort();
        }
    }

    fetch(url) {
        let request = this.state.fetchedRequest;
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
                headers: { Accept: 'application/json' },
            });
            request.then((response) => {
                if (!response.ok) throw response;
                return response.json();
            })
            .catch(globals.parseAndLogError.bind(undefined, 'fetchedRequest'))
            .then(this.receive);
        } else if (this.props.type === 'text') {
            request = this.context.fetch(url);
            request.then((response) => {
                if (!response.ok) throw response;
                return response.text();
            })
            .catch(globals.parseAndLogError.bind(undefined, 'fetchedRequest'))
            .then(this.receive);
        } else if (this.props.type === 'blob') {
            request = this.context.fetch(url);
            request.then((response) => {
                if (!response.ok) throw response;
                return response.blob();
            })
            .catch(globals.parseAndLogError.bind(undefined, 'fetchedRequest'))
            .then(this.receive);
        } else {
            throw new Error(`Unsupported type: ${this.props.type}`);
        }

        this.setState({
            fetchedRequest: request,
        });
    }

    receive(data) {
        const result = {};
        result[this.props.name] = data;
        if (this.props.etagName) {
            result[this.props.etagName] = this.state.fetchedRequest.etag;
        }
        this.props.handleFetch(result);
    }

    render() {
        return null;
    }
}

Param.propTypes = {
    url: PropTypes.string.isRequired,
    handleFetch: PropTypes.func, // Actually required, but added in cloneElement
    handleAbort: PropTypes.func, // Actually required, but added in cloneElement
    type: PropTypes.string,
    name: PropTypes.string.isRequired,
    etagName: PropTypes.string,
};

Param.defaultProps = {
    type: 'json',
    etagName: undefined,
    handleFetch: undefined, // Actually required, but added in cloneElement
    handleAbort: undefined, // Actually required, but added in cloneElement
};

Param.contextTypes = {
    fetch: PropTypes.func,
    session: PropTypes.object,
};


export class FetchedData extends React.Component {
    constructor() {
        super();
        this.state = {};
        this.aborted = false;
        this.handleFetch = this.handleFetch.bind(this);
        this.handleAbort = this.handleAbort.bind(this);
    }

    handleFetch(result) {
        // Set state to returned search result data to cause rerender of child components.
        if (!this.aborted) {
            this.setState(result);
        }
    }

    handleAbort() {
        // If <Param> aborts a request, we need to know that.
        this.aborted = true;
    }

    render() {
        const params = [];
        let communicating = false;
        const children = [];

        // Collect <Param> and non-<Param> child components into appropriate arrays
        if (this.props.children) {
            React.Children.forEach(this.props.children, (child) => {
                if (child.type === Param) {
                    // <Param> child component; add to array of <Param> child components with this.props.key of its name and calling `handleFetch`
                    params.push(React.cloneElement(child, {
                        key: child.props.name,
                        handleFetch: this.handleFetch,
                        handleAbort: this.handleAbort,
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
                    <div className="loading-spinner" />
                </div>
            );
        }

        // Detect whether a <Param> component returned an "Error" @type object
        const errors = params.map(param => this.state[param.props.name])
            .filter(obj => obj && (obj['@type'] || []).indexOf('Error') > -1);

        // If we got an error, display the error string on the web page
        if (errors.length) {
            // Render whatever error we got back from the server on the page.
            return (
                <div className="error done">
                    {errors.map((error) => {
                        const ErrorView = globals.content_views.lookup(error);
                        return <ErrorView {...this.props} context={error} />;
                    })}
                </div>
            );
        }

        // If we haven't gotten a response, continue showing the loading spinner
        if (communicating) {
            return (
                <div className="communicating">
                    <div className="loading-spinner" />
                    {params}
                </div>
            );
        }

        // Successfully got data. Display in the web page
        return (
            <div className="done">
                {children.map((child, i) => React.cloneElement(child, _.extend({ key: i }, this.props, this.state)))}
                {params}
            </div>
        );
    }
}

FetchedData.contextTypes = {
    session: PropTypes.object,
};

FetchedData.propTypes = {
    children: PropTypes.node.isRequired,
};


const Items = (props) => {
    const { Component, data } = props;
    const items = data ? data['@graph'] : [];
    return <Component {...props} items={items} total={data.total} />;
};

Items.propTypes = {
    Component: PropTypes.func.isRequired,
    data: PropTypes.object,
};

Items.defaultProps = {
    data: undefined,
};


export const FetchedItems = props => (
    <FetchedData>
        <Param name="data" url={props.url} />
        <Items {...props} />
    </FetchedData>
);

FetchedItems.propTypes = {
    url: PropTypes.string.isRequired,
};
