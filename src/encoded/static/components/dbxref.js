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

    // Handle two different kinds of WormBase IDs -- Target vs Strain
    if (prefix === 'WormBase' && local.substr(0, 6) === 'WBGene') {
        prefix = 'WormBaseTargets';
    }

    // Handle two different kinds of FlyBase IDs -- Target vs Stock
    if (prefix === 'FlyBase' && local.substr(0, 4) === 'FBst') {
        prefix = 'FlyBaseStock';
    }

    var base = prefix && globals.dbxref_prefix_map[prefix];
    if (!base) {
        return <span>{value}</span>;
    }
    if (prefix === "HGNC") {
        local = props.target_gene;
    // deal with UCSC links
    } else if (prefix === "UCSC-ENCODE-cv") {
        local = '"' + local + '"';
    } else if (prefix === "MGI") {
        local = value;
    } else if (prefix === 'MGI.D') {
        var id = value.substr(sep + 1);
        local = id + '.shtml';
    } else if (prefix === "CGC") {
        var id = value.substr(sep + 1);
        local = id + '&field=all&exst=&exfield=all'
    } else if (prefix === "DSSC") {
        var id = value.substr(sep + 1);
        local = id + '&table=Species&submit=Search'
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
