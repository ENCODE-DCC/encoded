'use strict';
var React = require('react');
var _ = require('underscore');
var dbxref = require('./dbxref');
var globals = require('./globals');
var Citation = require('./publication').Citation;

var DbxrefList = dbxref.DbxrefList;


// Count the total number of references in all the publications passed
// in the pubs array parameter.
module.exports.refCount = function refCount(pubs) {
    var total = 0;
    if (pubs) {
        pubs.forEach(function(pub) {
            total += pub.identifers ? pub.identifers.length : 0;
        });
    }
    return total;
}


// Display all PMID/PMCID references in the array of publications in the 'pubs' property.
var PubReferences = module.exports.PubReferences = React.createClass({
    render: function() {
        // Collect all publications' references into one array
        // and remove duplicates
        var allRefs = [];
        this.props.pubs.forEach(function(pub) {
            allRefs = allRefs.concat(pub.identifiers);
        });
        allRefs = _.uniq(allRefs);

        if (allRefs) {
            return <DbxrefList values={allRefs} className={this.props.listClass} />;
        } else {
            return <span></span>;
        }
    }
});