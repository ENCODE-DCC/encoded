import React from 'react';
import _ from 'underscore';
import globals from './globals';
import { SortTablePanel, SortTable } from './sorttable';


// BIOSAMPLE UTILITIES

// Construct a biosample summary string from the biosample's organism object.
export function BiosampleSummaryString(biosample, supressOrganism) {
    const organismName = biosample.organism.scientific_name;
    const organismlessSummary = biosample.summary.replace(`${organismName} `, '');
    if (supressOrganism) {
        return <span>{organismlessSummary}</span>;
    }
    return <span><i>{biosample.organism.scientific_name}</i> {organismlessSummary}</span>;
}

// Some biosample-specific utilities
//   Return an array of biosample scientific names from the given array of biosamples.
export function BiosampleOrganismNames(biosamples) {
    return _.uniq(biosamples.map(biosample => biosample.organism.scientific_name));
}


// Collect up all the documents associated with the given biosample. They get combined all into one array of
// documents (with @type of Document or Characterization). If the given biosample has no documdents, this
// function returns null. Protocol documents, characterizations, construct documents, and RNAi documents
// all get included.
export function CollectBiosampleDocs(biosample) {
    // Collect up the various biosample documents
    let protocolDocuments = [];
    if (biosample.documents && biosample.documents.length) {
        protocolDocuments = globals.uniqueObjectsArray(biosample.documents);
    }
    let characterizations = [];
    if (biosample.characterizations && biosample.characterizations.length) {
        characterizations = globals.uniqueObjectsArray(biosample.characterizations);
    }
    let constructDocuments = [];
    if (biosample.constructs && biosample.constructs.length) {
        biosample.constructs.forEach((construct) => {
            if (construct.documents && construct.documents.length) {
                constructDocuments = constructDocuments.concat(construct.documents);
            }
        });
    }
    let rnaiDocuments = [];
    if (biosample.rnais && biosample.rnais.length) {
        biosample.rnais.forEach((rnai) => {
            if (rnai.documents && rnai.documents.length) {
                rnaiDocuments = rnaiDocuments.concat(rnai.documents);
            }
        });
    }
    let donorDocuments = [];
    let donorCharacterizations = [];
    if (biosample.donor) {
        if (biosample.donor.characterizations && biosample.donor.characterizations.length) {
            donorCharacterizations = biosample.donor.characterizations;
        }
        if (biosample.donor.documents && biosample.donor.documents.length) {
            donorDocuments = biosample.donor.documents;
        }
    }
    let donorConstructs = [];
    if (biosample.model_organism_donor_constructs && biosample.model_organism_donor_constructs.length) {
        biosample.model_organism_donor_constructs.forEach((construct) => {
            if (construct.documents && construct.documents.length) {
                donorConstructs = donorConstructs.concat(construct.documents);
            }
        });
    }
    let talenDocuments = [];
    if (biosample.talens && biosample.talens.length) {
        biosample.talens.forEach((talen) => {
            talenDocuments = talenDocuments.concat(talen.documents);
        });
    }
    let treatmentDocuments = [];
    if (biosample.treatments && biosample.treatments.length) {
        biosample.treatments.forEach((treatment) => {
            treatmentDocuments = treatmentDocuments.concat(treatment.protocols);
        });
    }

    // Put together the document list for rendering
    // Compile the document list
    const combinedDocuments = _([].concat(
        protocolDocuments,
        characterizations,
        constructDocuments,
        rnaiDocuments,
        donorDocuments,
        donorCharacterizations,
        donorConstructs,
        talenDocuments,
        treatmentDocuments
    )).chain().uniq(doc => (doc ? doc.uuid : null)).compact()
    .value();

    return combinedDocuments;
}


// Display a table of retrieved biosamples related to the displayed biosample
export const BiosampleTable = React.createClass({
    propTypes: {
        items: React.PropTypes.array, // Array of biosamples to display
        total: React.PropTypes.number, // Total number of biosamples matching search criteria (can be more than biosamples in `items`)
        limit: React.PropTypes.number, // Maximum number of biosamples to display in the table
        title: React.PropTypes.oneOfType([ // Title to display in table header, as string or component
            React.PropTypes.string,
            React.PropTypes.node,
        ]),
        url: React.PropTypes.string, // URL to go to full search results
    },

    columns: {
        accession: {
            title: 'Accession',
            display: biosample => <a href={biosample['@id']}>{biosample.accession}</a>,
        },
        biosample_type: { title: 'Type' },
        biosample_term_name: { title: 'Term' },
        summary: { title: 'Summary', sorter: false },
    },

    render: function () {
        const { items, limit, total, url, title } = this.props;
        let biosamples;

        // If there's a limit on entries to display and the array is greater than that
        // limit, then clone the array with just that specified number of elements
        if (limit && (limit < items.length)) {
            // Limit the experiment list by cloning first {limit} elements
            biosamples = items.slice(0, limit);
        } else {
            // No limiting; just reference the original array
            biosamples = items;
        }

        return (
            <SortTablePanel title={title}>
                <SortTable list={items} columns={this.columns} footer={<BiosampleTableFooter items={biosamples} total={total} url={url} />} />
            </SortTablePanel>
        );
    },
});


// Display a count of biosamples in the footer, with a link to the corresponding search if needed
export const BiosampleTableFooter = React.createClass({
    propTypes: {
        items: React.PropTypes.array, // List of biosamples in the table
        total: React.PropTypes.number, // Total number of biosamples matching search criteria
        url: React.PropTypes.string, // URI to get full search results
    },

    render: function () {
        const { items, total, url } = this.props;

        return (
            <div>
                <span>Displaying {items.length} of {total} </span>
                {items.length < total ? <a className="btn btn-info btn-xs pull-right" href={url}>View all</a> : null}
            </div>
        );
    },
});


// Display a reference to an award page as a definition list item.
export const AwardRef = React.createClass({
    propTypes: {
        context: React.PropTypes.object, // Object containing the award property
    },

    render: function () {
        const { context } = this.props;

        if (context.award && context.award.pi && context.award.pi.lab) {
            return (
                <div data-test="awardpi">
                    <dt>Award</dt>
                    <dd>{context.award.pi.lab.title}</dd>
                </div>
            );
        }
        return null;
    },
});
