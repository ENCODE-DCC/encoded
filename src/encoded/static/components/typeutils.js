'use strict';
var React = require('react');


// BIOSAMPLE UTILITIES

// Construct a biosample summary string from the biosample's summary_object object.
var BiosampleSummaryString = module.exports.BiosampleSummaryString = function(biosample, supressOrganism) {
    var organismlessSummary = biosample.summary.replace(biosample.summary_object.organism_name + ' ', '');
    if (supressOrganism) {
        return <span>{organismlessSummary}</span>;
    }
    return <span><i>{biosample.summary_object.organism_name}</i> {organismlessSummary}</span>;
};
