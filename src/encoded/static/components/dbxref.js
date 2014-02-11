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
        var assembly;
        var base = globals.dbxref_prefix_map[prefix];
        if (base) {
            if (prefix == "HGNC") {
                local = props.target_gene;
            } else if (prefix == "UCSC_encode_db") {
                console.log("Local = " + local);
                
                if (local.indexOf("wgEncodeEM") != -1) {
                    assembly = "&db=mm9&hgt_mdbVal1="; // mm9 - mouse
                } else {
                    assembly = "&db=hg19&hgt_mdbVal1="; // hg19 - human
                }   
            }
            return <a href={base + assembly + local}>{value}</a>;
        }
    }
    return <span>{value}</span>;
};

module.exports.DbxrefList = function (props) {
    return (
        <ul className={props.className}>{props.values.map(function (value) {
            return <li key={value}><Dbxref value={value} prefix={props.prefix} target_gene={props.target_gene} /></li>;
        })}</ul>
    );
};