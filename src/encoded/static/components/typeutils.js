'use strict';
var React = require('react');
var _ = require('underscore');


// BIOSAMPLE UTILITIES

// Construct a biosample summary string from the biosample's summary_object object.
module.exports.BiosampleSummaryString = function(biosample, supressOrganism) {
    var organismName = biosample.organism.scientific_name;
    var organismlessSummary = biosample.summary.replace(organismName + ' ', '');
    if (supressOrganism) {
        return <span>{organismlessSummary}</span>;
    }
    return <span><i>{biosample.summary_object.organism_name}</i> {organismlessSummary}</span>;
};

// Some biosample-specific utilities
//   Return an array of biosample scientific names from the given array of biosamples.
module.exports.BiosampleOrganismNames = function(biosamples) {
    return _.uniq(biosamples.map(biosample => biosample.organism.scientific_name));
};

