'use strict';
var React = require('react');


// Mixin to use REST APIs conveniently. In this project, this is mostly used to read or write data
// in our own database, but it's also used to retrieve data from external REST services. Any React
// component that needs to work with a REST API can include:
//
// mixins: [RestMixin]
//
// ...at the top of its definition. The component can then use these methods:
//
// this.getRestData(uri): GET data from the given URI. Returns data in the promise.
// this.getRestData(uris): GET data from the array of given URIs. Returns data in the promise.
// this.putRestData(uri,obj): PUT given object to the given URI. Returns written data as a promise.
// this.postRestData(uri,obj): POST given object to the given URI. Returns written data as a promise.

var RestMixin = module.exports.RestMixin = {
    // Borrow 'fetch' function from Persona mixin used by App component
    contextTypes: {
        fetch: React.PropTypes.func
    },

    // GET data from the given URI. Returns data in the promise.
    getRestData: function(uri) {
        return this.context.fetch(uri, {
            method: 'GET',
            headers: {'Accept': 'application/json'}
        }).then(response => {
            // Success response, but might not necessarily be a success; check 'ok' before use
            if (!response.ok) { throw response; }

            // Actual success. Get the response's JSON as a promise.
            return response.json();
        }, error => {
            // Unsuccessful retrieval
            throw error;
        });
    },

    // PUT given object to the given URI. Returns written data as a promise.
    putRestData: function(uri, obj) {
        return this.writeRestData(uri, obj, 'PUT');
    },

    // POST given object to the given URI. Returns written data as a promise.
    postRestData: function(uri, obj) {
        return this.writeRestData(uri, obj, 'POST');
    },

    // Not for use by client components
    writeRestData: function(uri, obj, method) {
        return this.context.fetch(uri, {
            method: method,
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(obj)
        }).then(response => {
            // Success response, but might not necessarily be a success; check 'ok' before use
            if (!response.ok) { throw response; }

            // Actual success. Get the response's JSON as a promise.
            return response.json();
        }, error => {
            // Unsuccessful retrieval
            throw error;
        });
    }
};
