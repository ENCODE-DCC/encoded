import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import * as globals from './globals';
import { AlternateAccession } from './objectutils';
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
// Some biosample-specific utilities
//   Return an array of biosample scientific names from the given array of biosamples.
export function BiospecimenOrganismNames(biosamples) {
    return _.uniq(biosamples.map(biospecimen => biospecimen.species));
}

// Collect up all the documents associated with the given biosample. They get combined all into one array of
// documents (with @type of Document or Characterization). If the given biosample has no documdents, this
// function returns null. Protocol documents and characterizations get included.
export function CollectBiosampleDocs(biosample) {
    // Collect up the various biosample documents
    let protocolDocuments = [];
    if (biosample.documents && biosample.documents.length) {
        protocolDocuments = _.uniq(biosample.documents);
    }
    let characterizations = [];
    if (biosample.characterizations && biosample.characterizations.length) {
        characterizations = _.uniq(biosample.characterizations);
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
    let treatmentDocuments = [];
    if (biosample.treatments && biosample.treatments.length) {
        treatmentDocuments = biosample.treatments.reduce((allDocs, treatment) => ((treatment.documents && treatment.documents.length) ? allDocs.concat(treatment.documents) : allDocs), []);
    }

    // Put together the document list for rendering
    // Compile the document list
    const combinedDocuments = _.uniq([].concat(
        protocolDocuments,
        characterizations,
        donorDocuments,
        donorCharacterizations,
        treatmentDocuments
    ));

    return combinedDocuments;
}


// Display a table of retrieved biosamples related to the displayed biosample
export const BiosampleTable = (props) => {
    const { items, limit, total, url, title } = props;
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
            <SortTable list={items} columns={BiosampleTable.columns} footer={<BiosampleTableFooter items={biosamples} total={total} url={url} />} />
        </SortTablePanel>
    );
};

BiosampleTable.propTypes = {
    items: PropTypes.array.isRequired,
    limit: PropTypes.number,
    total: PropTypes.number,
    url: PropTypes.string,
    title: PropTypes.string,
};

BiosampleTable.defaultProps = {
    limit: 0,
    total: 0,
    url: '',
    title: '',
};

BiosampleTable.columns = {
    accession: {
        title: 'Accession',
        display: biosample => <a href={biosample['@id']}>{biosample.accession}</a>,
    },
    'biosample_ontology.classification': {
        title: 'Type',
        getValue: item => item.biosample_ontology && item.biosample_ontology.classification,
    },
    'biosample_ontology.term_name': {
        title: 'Term',
        getValue: item => item.biosample_ontology && item.biosample_ontology.term_name,
    },
    summary: { title: 'Summary', sorter: false },
};


// Display a count of biosamples in the footer, with a link to the corresponding search if needed
export const BiosampleTableFooter = (props) => {
    const { items, total, url } = props;

    return (
        <div>
            <span>Displaying {items.length} of {total} </span>
            {items.length < total ? <a className="btn btn-info btn-xs pull-right" href={url}>View all</a> : null}
        </div>
    );
};

BiosampleTableFooter.propTypes = {
    items: PropTypes.array, // List of biosamples in the table
    total: PropTypes.number, // Total number of biosamples matching search criteria
    url: PropTypes.string, // URI to get full search results
};

BiosampleTableFooter.defaultProps = {
    items: [],
    total: 0,
    url: '#',
};

// Display a table of retrieved biospecimen related to the displayed biospecimen
export const BiospecimenTable = (props) => {
    const { items, limit, total, url, title } = props;
    let biospecimens;

    // If there's a limit on entries to display and the array is greater than that
    // limit, then clone the array with just that specified number of elements
    if (limit && (limit < items.length)) {
        // Limit the experiment list by cloning first {limit} elements
        biospecimens = items.slice(0, limit);
    } else {
        // No limiting; just reference the original array
        biospecimens = items;
    }

    return (
        <SortTablePanel title={title}>
            <SortTable list={items} columns={BiospecimenTable.columns} footer={<BiospecimenTableFooter items={biospecimens} total={total} url={url} />} />
        </SortTablePanel>
    );
};

BiospecimenTable.propTypes = {
    items: PropTypes.array.isRequired,
    limit: PropTypes.number,
    total: PropTypes.number,
    url: PropTypes.string,
    title: PropTypes.string,
};

BiospecimenTable.defaultProps = {
    limit: 0,
    total: 0,
    url: '',
    title: '',
};

BiospecimenTable.columns = {
    accession: {
        title: 'Accession',
        display: biospecimen => <a href={biospecimen['@id']}>{biospecimen.accession}</a>,
    },
    openspecimen_ID: {
        title: 'OpenSpecimen ID',
        getValue: biospecimen => biospecimen.openspecimen_ID,
    },
    collection_type: {
        title: 'Collection type',
        getValue: biospecimen => biospecimen.collection_type,
    },
    processing_type: {
        title: 'Processing type',
        getValue: biospecimen => biospecimen.processing_type,
    },

    tissue_type: {
        title: 'Tissue type',
        getValue: biospecimen => biospecimen.tissue_type,
    },
    anatomic_site: {
        title: 'Anatomic site',
        getValue: biospecimen => biospecimen.anatomic_site,
    },
    distributed: {
        title: 'Distributed?',
        getValue: biospecimen => biospecimen.distributed,
    },
};


// Display a count of biospecimen in the footer, with a link to the corresponding search if needed
export const BiospecimenTableFooter = (props) => {
    const { items, total, url } = props;

    return (
        <div>
            <span>Displaying {items.length} of {total} </span>
            {items.length < total ? <a className="btn btn-info btn-xs pull-right" href={url}>View all</a> : null}
        </div>
    );
};

BiospecimenTableFooter.propTypes = {
    items: PropTypes.array, // List of biospecimen in the table
    total: PropTypes.number, // Total number of biospecimen matching search criteria
    url: PropTypes.string, // URI to get full search results
};

BiospecimenTableFooter.defaultProps = {
    items: [],
    total: 0,
    url: '#',
};

// Display a table of donors retrieved from a GET request.
export const DonorTable = (props) => {
    const { items, limit, total, url, title } = props;
    let donors;

    // If there's a limit on entries to display and the array is greater than that limit, then
    // clone the array with just that specified number of elements
    if (limit && (limit < items.length)) {
        // Limit the donor list by cloning first {limit} elements
        donors = items.slice(0, limit);
    } else {
        // No limiting; just reference the original array
        donors = items;
    }

    return (
        <SortTablePanel title={title}>
            <SortTable list={items} columns={DonorTable.columns} footer={<DonorTableFooter items={donors} total={total} url={url} />} />
        </SortTablePanel>
    );
};

DonorTable.propTypes = {
    items: PropTypes.array.isRequired, // List of donors as an array of search results
    limit: PropTypes.number, // Maximum number of donors to display in the table
    total: PropTypes.number, // Total number of donors in the search results; might be more than we display in the table
    url: PropTypes.string, // URL to use for the complete donor search reuslts
    title: PropTypes.string, // Title to use for the table of donors
};

DonorTable.defaultProps = {
    limit: 0,
    total: 0,
    url: '',
    title: '',
};

// <SortTable> column specificiation for the table of donors.
DonorTable.columns = {
    accession: {
        title: 'Accession',
        display: donor => <a href={donor['@id']}>{donor.accession}</a>,
    },
    species: {
        title: 'Species',
        display: donor => (donor.organism && donor.organism.scientific_name ? <i>{donor.organism.scientific_name}</i> : null),
    },
    sex: {
        title: 'Sex',
    },
};


// Display a count of donors in the footer, with a link to the corresponding search if needed
const DonorTableFooter = (props) => {
    const { items, total, url } = props;

    return (
        <div>
            <span>Displaying {items.length} of {total} </span>
            {items.length < total ? <a className="btn btn-info btn-xs pull-right" href={url}>View all</a> : null}
        </div>
    );
};

DonorTableFooter.propTypes = {
    items: PropTypes.array, // List of biosamples in the table
    total: PropTypes.number, // Total number of biosamples matching search criteria
    url: PropTypes.string, // URI to get full search results
};

DonorTableFooter.defaultProps = {
    items: [],
    total: 0,
    url: '',
};


// Display a reference to an award page as a definition list item.
export const AwardRef = (props) => {
    const { context, adminUser } = props;
    const award = context.award;

    if (award && award.pi && award.pi.lab) {
        return (
            <div data-test="awardpi">
                <dt>Award</dt>
                <dd>
                    {adminUser || award.status === 'current' || award.status === 'disabled' ?
                        <a href={award['@id']} title={`View page for award ${award.name}`}>{award.name}</a>
                    :
                        <span>{award.name}</span>
                    }
                    {award.pi && award.pi.lab ?
                        <span> ({award.pi.lab.title})</span>
                    : null}
                </dd>
            </div>
        );
    }
    return null;
};

AwardRef.propTypes = {
    context: PropTypes.object.isRequired, // Object containing the award property
    adminUser: PropTypes.bool.isRequired, // True if current user is a logged-in admin
};


/**
 * Return an array of all possible file statuses, given the current logged-in status. Note that if
 * the file.json schema changes the file statuses, this has to change too.
 *
 * @param {object} session - encoded login information from <App> context.
 * @param (object) sessionProperties - encoded login session properties from <App> context.
 */
export function fileStatusList(session, sessionProperties) {
    const loggedIn = !!(session && session['auth.userid']);
    const adminUser = !!(sessionProperties && sessionProperties.admin);

    // These statuses are the only ones logged-out users can see.
    let statuses = [
        'released',
        'revoked',
        'archived',
    ];

    // If the user's logged in, add in more statuses.
    if (loggedIn) {
        statuses = statuses.concat([
            'uploading',
            'in progress',
            'content error',
            'upload failed',
        ]);
    }

    // If the user's logged in as an admin, add in the last statuses.
    if (adminUser) {
        statuses = statuses.concat([
            'deleted',
            'replaced',
        ]);
    }

    return statuses.concat(['status unknown']);
}


/**
 *  Display supersedes/superseded_by/alternate_accessions lists.
 */
export const ReplacementAccessions = ({ context }) => {
    const alternateAccessions = context.alternate_accessions || [];
    const supersededByAtIds = context.superseded_by || [];
    const supersedes = (context.supersedes && context.supersedes.map(supersedesAtId => globals.atIdToAccession(supersedesAtId))) || [];

    if (alternateAccessions.length > 0 || supersededByAtIds.length > 0 || supersedes.length > 0) {
        return (
            <div className="replacement-accessions">
                <AlternateAccession altAcc={alternateAccessions} />
                {supersededByAtIds.length > 0 ?
                    <h4 className="replacement-accessions__superseded-by">
                        <span>Superseded by </span>
                        {supersededByAtIds.map((supersededByAtId, index) => (
                            <span key={supersededByAtId}>
                                {index > 0 ? <span>, </span> : null}
                                <a href={supersededByAtId}>{globals.atIdToAccession(supersededByAtId)}</a>
                            </span>
                        ))}
                    </h4>
                : null}
                {supersedes.length > 0 ?
                    <h4 className="replacement-accessions__supersedes">Supersedes {supersedes.join(', ')}</h4>
                : null}
            </div>
        );
    }
    return null;
};

ReplacementAccessions.propTypes = {
    context: PropTypes.object.isRequired, // Object containing supersedes/superseded_by to display
};


/**
 * Display a count of experiments in the footer, with a link to the corresponding search if needed.
 */
const ExperimentTableFooter = ({ items, total, url }) => (
    <div>
        <span>Displaying {items.length} of {total} </span>
        {items.length < total ? <a className="btn btn-info btn-xs pull-right" href={url}>View all</a> : null}
    </div>
);

ExperimentTableFooter.propTypes = {
    /** Array of experiments that were displayed in the table */
    items: PropTypes.array.isRequired,
    /** Total number of experiments */
    total: PropTypes.number,
    /** URL to link to equivalent experiment search results */
    url: PropTypes.string.isRequired,
};

ExperimentTableFooter.defaultProps = {
    total: 0,
};


const experimentTableColumns = {
    accession: {
        title: 'Accession',
        display: item => <a href={item['@id']} title={`View page for experiment ${item.accession}`}>{item.accession}</a>,
    },

    assay_term_name: {
        title: 'Assay',
    },

    'biosample_ontology.term_name': {
        title: 'Biosample term name',
        getValue: item => item.biosample_ontology && item.biosample_ontology.term_name,
    },

    target: {
        title: 'Target',
        getValue: item => item.target && item.target.label,
    },

    description: {
        title: 'Description',
    },

    title: {
        title: 'Lab',
        getValue: item => (item.lab && item.lab.title ? item.lab.title : null),
    },
};


export const ExperimentTable = ({ items, limit, total, url, title }) => {
    // If there's a limit on entries to display and the array is greater than that limit, then
    // clone the array with just that specified number of elements.
    const experiments = limit > 0 && limit < items.length ? items.slice(0, limit) : items;

    return (
        <div>
            <SortTablePanel title={title}>
                <SortTable list={experiments} columns={experimentTableColumns} footer={<ExperimentTableFooter items={experiments} total={total} url={url} />} />
            </SortTablePanel>
        </div>
    );
};

ExperimentTable.propTypes = {
    /** List of experiments to display in the table */
    items: PropTypes.array.isRequired,
    /** Maximum number of experiments to display in the table */
    limit: PropTypes.number,
    /** Total number of experiments */
    total: PropTypes.number,
    /** URI to go to equivalent search results */
    url: PropTypes.string.isRequired,
    /** Title for the table of experiments; can be string or component */
    title: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.node,
    ]),
};

ExperimentTable.defaultProps = {
    limit: 0,
    total: 0,
    title: '',
};


/**
 * Display a table of experiments with the dataset in `context` as a possible_controls.
 */
export const ControllingExperiments = ({ context, items, total, url }) => {
    if (items.length > 0) {
        return (
            <div>
                <ExperimentTable
                    items={items}
                    limit={5}
                    total={total}
                    url={url}
                    title={`Experiments with ${context.accession} as a control:`}
                />
            </div>
        );
    }
    return null;
};

ControllingExperiments.propTypes = {
    /** Dataset object containing the table being rendered */
    context: PropTypes.object.isRequired,
    /** Experiments to display in the table */
    items: PropTypes.array,
    /** Total number of items from search (can be larger than items.length) */
    total: PropTypes.number,
    /** URL to retrieve search results to fill the table */
    url: PropTypes.string,
};

ControllingExperiments.defaultProps = {
    items: [],
    total: 0,
    url: '',
};
