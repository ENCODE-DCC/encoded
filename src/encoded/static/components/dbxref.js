/** @jsx React.DOM */
define(['exports', 'react', 'globals'],
function (dbxref, React, globals) {
    /*jshint devel: true*/
    'use strict';

    var Dbxref = dbxref.Dbxref = function (value) {
        if (typeof props != 'string') {
            value = value.value || '';
        }
        var sep = value.indexOf(':');
        if (sep != -1) {
            var prefix = value.slice(0, sep);
            var local = value.slice(sep + 1);
            var url = globals.dbxref_prefix_map[prefix];
            if (url) {
                return <a href={url}>{value}</a>;
            }
        }
        return <span>{value}</span>;
    }

    dbxref.DbxrefList = function (props) {
        return (
            <ul class={props.className}>{props.values.map(function (value) {
                return <li key={value}><Dbxref value={value} /></li>;
            })}</ul>
        );
    }

    return dbxref;
});
