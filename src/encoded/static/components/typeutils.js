'use strict';
var React = require('react');
var _ = require('underscore');
var globals = require('./globals');

// BIOSAMPLE UTILITIES

// Construct a biosample summary string from the biosample's organism object.
module.exports.BiosampleSummaryString = function(biosample, supressOrganism) {
    var organismName = biosample.organism.scientific_name;
    var organismlessSummary = biosample.summary.replace(organismName + ' ', '');
    if (supressOrganism) {
        return <span>{organismlessSummary}</span>;
    }
    return <span><i>{biosample.organism.scientific_name}</i> {organismlessSummary}</span>;
};

// Some biosample-specific utilities
//   Return an array of biosample scientific names from the given array of biosamples.
module.exports.BiosampleOrganismNames = function(biosamples) {
    return _.uniq(biosamples.map(biosample => biosample.organism.scientific_name));
};


// Collect up all the documents associated with the given biosample. They get combined all into one array of
// documents (with @type of Document or Characterization). If the given biosample has no documdents, this
// function returns null. Protocol documents, characterizations, construct documents, and RNAi documents
// all get included.
module.exports.CollectBiosampleDocs = function(biosample) {
    // Collect up the various biosample documents
    var protocolDocuments = [];
    if (biosample.protocol_documents && biosample.protocol_documents.length) {
        protocolDocuments = globals.uniqueObjectsArray(biosample.protocol_documents);
    }
    var characterizations = [];
    if (biosample.characterizations && biosample.characterizations.length) {
        characterizations = globals.uniqueObjectsArray(biosample.characterizations);
    }
    var constructDocuments = [];
    if (biosample.constructs && biosample.constructs.length) {
        biosample.constructs.forEach(construct => {
            if (construct.documents && construct.documents.length) {
                constructDocuments = constructDocuments.concat(construct.documents);
            }
        });
    }
    var rnaiDocuments = [];
    if (biosample.rnais && biosample.rnais.length) {
        biosample.rnais.forEach(rnai => {
            if (rnai.documents && rnai.documents.length) {
                rnaiDocuments = rnaiDocuments.concat(rnai.documents);
            }
        });
    }
    var donorDocuments = [];
    var donorCharacterizations = [];
    if (biosample.donor) {
        if (biosample.donor.characterizations && biosample.donor.characterizations.length) {
            donorCharacterizations = biosample.donor.characterizations;
        }
        if (biosample.donor.documents && biosample.donor.documents.length) {
            donorDocuments = biosample.donor.documents;
        }
    }
    var donorConstructs = [];
    if (biosample.model_organism_donor_constructs && biosample.model_organism_donor_constructs.length) {
        biosample.model_organism_donor_constructs.forEach(construct => {
            if (construct.documents && construct.documents.length) {
                donorConstructs = donorConstructs.concat(construct.documents);
            }
        });
    }
    var talenDocuments = [];
    if (biosample.talens && biosample.talens.length) {
        biosample.talens.forEach(talen => {
            talenDocuments = talenDocuments.concat(talen.documents);
        });
    }
    var treatmentDocuments = [];
    if (biosample.treatments && biosample.treatments.length) {
        biosample.treatments.forEach(treatment => {
            treatmentDocuments = treatmentDocuments.concat(treatment.protocols);
        });
    }

    // Put together the document list for rendering
    // Compile the document list
    var combinedDocuments = _([].concat(
        protocolDocuments,
        characterizations,
        constructDocuments,
        rnaiDocuments,
        donorDocuments,
        donorCharacterizations,
        donorConstructs,
        talenDocuments,
        treatmentDocuments
    )).chain().uniq(doc => doc ? doc.uuid : null).compact().value();

    return combinedDocuments;
}
