/** @jsx React.DOM */
define(['exports', 'react', 'globals'],
function (dbxref, React, globals) {
    /*jshint devel: true*/
    'use strict';

    var Dbxref = dbxref.Dbxref = function (props) {
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
        console.log(props);
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
    }

    dbxref.DbxrefList = function (props) { console.log(props);
        return (
            <ul class={props.className}>{props.values.map(function (value) {
                return <li key={value}><Dbxref value={value} prefix={props.prefix} target_gene={props.target_gene} /></li>;
            })}</ul>
        );
    }

    return dbxref;
});
