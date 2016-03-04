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
        local = encodeURIComponent(value.slice(sep + 1)).replace(/%20/g,'_');
    }

    // Handle two different kinds of GEO -- GSM/GSE vs SAMN
    if (prefix === 'GEO' && local.substr(0, 4) === 'SAMN') {
        prefix = 'GEOSAMN';
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
    if (prefix === "MGI") {
        local = value;
    }

    return <a href={base + local}>{value}</a>;
};

module.exports.DbxrefList = React.createClass({
    render: function () {
        var props = this.props;
        return (
            <ul className={props.className}>{props.values.map(function (value, index) {
                return <li key={index}>{Dbxref({value: value, prefix: props.prefix, target_gene: props.target_gene})}</li>;
            })}</ul>
        );
    }
});
