'use strict';
var React = require('react');
var _ = require('underscore');
var globals = require('./globals');
var {SortTablePanel, SortTable} = require('./sorttable');


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
};


// Display a table of retrieved biosamples related to the displayed biosample
var BiosampleTable = module.exports.BiosampleTable = React.createClass({
    columns: {
        'accession': {
            title: 'Accession',
            display: function(biosample) {
                return <a href={biosample['@id']}>{biosample.accession}</a>;
            }
        },
        'biosample_type': {title: 'Type'},
        'biosample_term_name': {title: 'Term'},
        'summary': {title: 'Summary', sorter: false}
    },

    render: function() {
        var biosamples;

        // If there's a limit on entries to display and the array is greater than that
        // limit, then clone the array with just that specified number of elements
        if (this.props.limit && (this.props.limit < this.props.items.length)) {
            // Limit the experiment list by cloning first {limit} elements
            biosamples = this.props.items.slice(0, this.props.limit);
        } else {
            // No limiting; just reference the original array
            biosamples = this.props.items;
        }

        return (
            <SortTablePanel title={this.props.title}>
                <SortTable list={this.props.items} columns={this.columns} footer={<BiosampleTableFooter items={biosamples} total={this.props.total} url={this.props.url} />} />
            </SortTablePanel>
        );
    }
});


// Display a count of biosamples in the footer, with a link to the corresponding search if needed
var BiosampleTableFooter = React.createClass({
    render: function() {
        var {items, total, url} = this.props;

        return (
            <div>
                <span>Displaying {items.length} of {total} </span>
                {items.length < total ? <a className="btn btn-info btn-xs pull-right" href={url}>View all</a> : null}
            </div>
        );
    }
});


// Display the table of genetic modifications
var GeneticModificationTable = module.exports.GeneticModificationTable = React.createClass({
    propTypes: {
        geneticModifications: React.PropTypes.array.isRequired // Array of genetic modifications
    },

    columns: {
        'modification_type': {
            title: 'Type',
            display: modification => <a href={modification['@id']} title="View this modification">{modification.modification_type}</a>
        },
        'techniques': {
            title: 'Techniques',
            getValue: modification => {
                if (modification.modification_techniques && modification.modification_techniques.length) {
                    return (
                        modification.modification_techniques.map(technique => {
                            if (technique['@type'][0] === 'Crispr') {
                                return 'CRISPR';
                            } else if (technique['@type'][0] === 'Tale') {
                                return 'TALE';
                            }
                            return technique['@type'][0];
                        }).sort().join(', ')
                    );
                }
                return null;
            }
        },
        'target': {
            title: 'Target',
            display: modification => {
                if (modification.target) {
                    return <a href={modification.target['@id']} title={'View target ' + modification.target.label}>{modification.target.label}</a>;
                }
                return null;
            },
        },
        'modification_purpose': {
            title: 'Purpose'
        },
        'modification_zygocity': {
            title: 'Zygocity'
        },
        'assembly': {
            title: 'Mapping assembly',
            getValue: modification => modification.modification_genome_coordinates && modification.modification_genome_coordinates.assembly ? modification.modification_genome_coordinates.assembly : ''
        },
        'coordinates': {
            title: 'Coordinates',
            display: modification => {
                var coords = modification.modification_genome_coordinates;
                if (coords && coords.chromosome) {
                    return <span>chr{coords.chromosome}:{coords.start}-{coords.end}</span>;
                }
                return null;
            } 
        }
    },

    render: function() {
        var {geneticModifications} = this.props;

        return (
            <SortTablePanel title="Genetic modifications">
                <SortTable list={geneticModifications} columns={this.columns} />
            </SortTablePanel>
        );
    }
});
