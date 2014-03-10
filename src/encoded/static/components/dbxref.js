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
// DEV
    // This assumes a new UCSC_cv string. Have to do something else if not
    if (false) {
        prefix = "UCSC_cv";
    }
// /DEV
    var base = prefix && globals.dbxref_prefix_map[prefix];
    if (!base) {
        return <span>{value}</span>;
    }
    if (prefix == "HGNC") {
        local = props.target_gene;
    // deal with UCSC links
    }
    if (prefix === "UCSC_cv") {
        // UCSC_cv terms must be in double quotes
        local = '"' + local + '"';
    } else if (prefix == "UCSC_encode_db" || prefix == "ucsc_encode_db") {
        if (local.indexOf("wgEncodeEM") === 0) {
            base += "&db=mm9&hgt_mdbVal1="; // mm9 - db is mouse
        } else if (local.indexOf("wgEncodeEH") === 0){
            base += "&db=hg19&hgt_mdbVal1="; // hg19 - db is human
        } else if (local.indexOf("-wgEncode") > 0) {
            // -wgEncode used for composite dataset types
            // Get the 'db' and 'g' from local; rewrite local from 'g'
            var dashSep = local.indexOf("-");
            var db = local.slice(0, dashSep);
            var local = local.slice(dashSep + 1);

            // Use a fake index for dataset Aliases because URL is different
            // from other ucsc_encode_db types
            base = globals.dbxref_prefix_map["UCSC_ds"] + db + '&g=';
        } else {
            return <span>{value}</span>;
        }
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
