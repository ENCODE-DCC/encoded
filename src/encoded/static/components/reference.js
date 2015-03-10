'use strict';
var React = require('react');
var globals = require('./globals');
var Citation = require('./publication').Citation;


// Count the total number of references in all the publications passed
// in the pubs array parameter.
function refCount(pubs) {
    var total = 0;
    if (pubs) {
        pubs.forEach(function(pub) {
            total += pub.references ? pub.references.length : 0;
        });
    }
    return total;
}


// Display all PMID/PMCID references in the array of publications in the 'pubs' property.
var PubReferences = React.createClass({
    render: function() {
        // Collect all publications' references into one array
        // and remove duplicates
        var allRefs = [];untitled
        this.props.pubs.forEach(function(pub) {
            allRefs = allRefs.concat(pub.references);
        });
        allRefs = _.uniq(allRefs);

        if (allRefs) {
            return <DbxrefList values={allRefs} className={this.props.listClass} />;
        } else {
            return <span></span>;
        }
    }
});