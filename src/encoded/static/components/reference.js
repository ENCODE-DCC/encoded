'use strict';
var React = require('react');
var _ = require('underscore');


var PubReferenceList= module.exports.PubReferenceList = React.createClass({
    render: function() {
        var props = this.props;
        return (
            <ul className={props.className}>
                {props.values.map(function (value, index) {
                    return value.identifiers.map(function (identifier, index) {
                        return (<li key={index}>
                            <a href={value['@id']}>{identifier}</a>
                        </li>);
                    })
                })}
            </ul>
        );
    }
});