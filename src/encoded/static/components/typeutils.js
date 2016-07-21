'use strict';
var React = require('react');


// BIOSAMPLE UTILITIES

// Construct a biosample summary string from the biosamples summary_object object.
// `supressOrganism` should be true to NOT render the organism name.

var BiosampleSummaryString = module.exports.BiosampleSummaryString = function(biosample, supressOrganism) {
    var summaryObject = biosample.summary_object;

    // Filter out keys for summary_object properties we never display, and empty properties
    var keys = Object.keys(summaryObject).filter(summaryKey => {
        var value = summaryObject[summaryKey];
        return value && summaryKey != 'organism_name' && summaryKey !== 'term_phrase' && summaryKey !== 'summary_string';
    });

    // Make a list of JSX elements for each summary_object property.
    var elements = keys.map((summaryKey, i) => {
        return <span key={summaryKey}>{i > 0 ? <span> </span> : null}{biosample.summary_object[summaryKey]}</span>;
    });
    return <span>{!supressOrganism ? <i>{biosample.summary_object.organism_name} </i> : null}{elements}</span>;
};
