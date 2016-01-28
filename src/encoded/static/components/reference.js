'use strict';
var React = require('react');
var _ = require('underscore');


var PubReferenceList = module.exports.PubReferenceList = function(values) {
    // Render each of the links, with null for each value without an identifier property
    if (values && values.length) {
        var links = _.compact(values.map((value, index) => {
            if (value.identifiers) {
                return value.identifiers.map((identifier, index) => {
                    return (
                        <li key={index}>
                            <a href={value['@id']}>{identifier}</a>
                        </li>
                    );
                });
            }
            return null;
        }));

        // Render any links into a ul. Just return null if no links to render.
        if (links.length) {
            return (
                <ul>{links}</ul>
            );
        }
    }
    return null;
}
