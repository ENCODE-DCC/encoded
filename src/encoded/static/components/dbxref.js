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
    var base = prefix && globals.dbxref_prefix_map[prefix];
    if (!base) {
        return <span>{value}</span>;
    }
    if (prefix == "HGNC") {
        local = props.target_gene;
    // deal with UCSC links
    }
    if (prefix === "UCSC-ENCODE-cv") {
        local = '"' + local + '"';
    }

    return <a href={base + local}>{value}</a>;
};

module.exports.DbxrefList = function (props) {
    return (
        <ul className={props.className}>{props.values.map(function (value, index) {
            return <li key={index}><Dbxref value={value} prefix={props.prefix} target_gene={props.target_gene} /></li>;
        })}</ul>
    );
};
