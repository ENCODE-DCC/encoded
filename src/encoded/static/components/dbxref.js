/** @jsx React.DOM */
'use strict';
var React = require('react');
var globals = require('./globals');

var Dbxref = module.exports.Dbxref = function (props) {
    var value = props.value || '';
    var sep = value.indexOf(':');
    var prefix = props.prefix;
    var local;
    if (prefix) {
        local = value;
    } else if (sep != -1) {
        prefix = value.slice(0, sep);
        local = value.slice(sep + 1);
    }
    if (prefix) {
        var base = globals.dbxref_prefix_map[prefix];
        if (base) {
            if (prefix == "HGNC") {
                local = props.target_gene;
            }
            return <a href={base + local}>{value}</a>;
        }
    }
    return <span>{value}</span>;
};

module.exports.DbxrefList = function (props) { console.log(props);
    return (
        <ul className={props.className}>{props.values.map(function (value) {
            return <li key={value}><Dbxref value={value} prefix={props.prefix} target_gene={props.target_gene} /></li>;
        })}</ul>
    );
};
