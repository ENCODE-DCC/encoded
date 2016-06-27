'use strict';
var React = require('react');
var globals = require('./globals');

var Dbxref = module.exports.Dbxref = function (props) {
    var value = props.value || '';
    var sep = value.indexOf(':');
    var prefix = props.prefix;
    var local, id;
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
    if (prefix === 'WormBase' && props.target_ref) {
        prefix = 'WormBaseTargets';
    }

    // Handle two different kinds of FlyBase IDs -- Target vs Stock
    if (prefix === 'FlyBase' && !props.target_ref) {
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
        id = value.substr(sep + 1);
        local = id + '.shtml';
    } else if (prefix === "CGC") {
        id = value.substr(sep + 1);
        local = id + '&field=all&exst=&exfield=all';
    } else if (prefix === "DSSC") {
        id = value.substr(sep + 1);
        local = id + '&table=Species&submit=Search';
    }

    return <a href={base + local}>{value}</a>;
};

module.exports.DbxrefList = React.createClass({
    render: function () {
        var props = this.props;
        return (
            <ul className={props.className}>{props.values.map(function (value, index) {
                return <li key={index}>{Dbxref({value: value, prefix: props.prefix, target_gene: props.target_gene, target_ref: props.target_ref})}</li>;
            })}</ul>
        );
    }
});
