import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import * as Pager from '../libs/ui/pager';
import { dbxrefHref } from './dbxref';
import * as globals from './globals';
import { requestFiles, AlternateAccession, CopyButton } from './objectutils';
import { SortTablePanel, SortTable } from './sorttable';
import Status from './status';
import {
    BatchDownloadActuator,
    DatasetBatchDownloadController,
} from './batch_download';
import QueryString from '../libs/query_string';


// Maximum number of files before the user can't download them.
const MAX_DOWNLOADABLE_FILES = 5000000;


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

/**
 * Display the given biosample summary string with any of the given organism names italicized.
 */
export const BiosampleSummaryDisplay = ({ summary, organisms }) => {
    if (organisms.length > 0) {
        // Generate the equivalent shortened organism scientific names.
        const organismsWithShortenedNames = organisms.concat(organisms.map((organism) => organism.replace(/^(\S)\S* (\S+)$/, '$1. $2')));

        let cursor = 0;
        let maybeMoreMatches = true;
        const allOrganismsRegex = new RegExp(organismsWithShortenedNames.join('|'));
        const displayedElements = [];
        while (cursor < summary.length && maybeMoreMatches) {
            const remainingString = summary.slice(cursor);
            const matchData = remainingString.match(new RegExp(allOrganismsRegex));
            if (matchData) {
                if (matchData.index > 0) {
                    // Add the text before the match.
                    const preMatch = remainingString.slice(0, matchData.index);
                    displayedElements.push(<React.Fragment key={cursor}>{preMatch}</React.Fragment>);
                    cursor += preMatch.length;
                }

                // Add the italicized organism name.
                displayedElements.push(<i key={cursor}>{matchData[0]}</i>);
                cursor += matchData[0].length;
            } else {
                maybeMoreMatches = false;
            }
        }

        // Add the remaining text after any matches.
        displayedElements.push(<React.Fragment key="remaining">{summary.slice(cursor)}</React.Fragment>);
        return displayedElements;
    }

    // No organisms to italicize.
    return <>{summary}</>;
};

BiosampleSummaryDisplay.propTypes = {
    /** Biosample summary string possibly containing organism scientific names */
    summary: PropTypes.string.isRequired,
    /** List of organism scientific names to check against */
    organisms: PropTypes.arrayOf(PropTypes.string).isRequired,
};


// Some biosample-specific utilities
//   Return an array of biosample scientific names from the given array of biosamples.
export function BiosampleOrganismNames(biosamples) {
    return _.uniq(biosamples.map((biosample) => biosample.organism.scientific_name));
}

//   Return an array of biosample scientific names from the given array of genetic modifications.
export function GeneticModificationOrganismNames(biosamples) {
    const geneticModificationOrganisms = [];
    biosamples.forEach((biosample) => {
        if (biosample.applied_modifications && biosample.applied_modifications.length > 0) {
            const appliedModifications = biosample.applied_modifications;
            appliedModifications.forEach((modification) => {
                if (modification.introduced_gene && modification.introduced_gene.organism) {
                    geneticModificationOrganisms.push(modification.introduced_gene.organism.scientific_name);
                } else if (modification.modified_site_by_target_id && modification.modified_site_by_target_id.organism) {
                    geneticModificationOrganisms.push(modification.modified_site_by_target_id.organism.scientific_name);
                }
            });
        }
    });
    const reducedGeneticModificationOrganisms = geneticModificationOrganisms.reduce((previousValue, currentValue) => {
        if (!(previousValue.includes(currentValue))) {
            previousValue.push(currentValue);
        }
        return previousValue;
    }, []);
    return reducedGeneticModificationOrganisms;
}

// Collect up all the documents associated with the given biosample. They get combined all into one array of
// documents (with @type of Document or Characterization). If the given biosample has no documents, this
// function returns null. Protocol documents and characterizations get included.
export function CollectBiosampleDocs(biosample) {
    // Collect up the various biosample documents
    let protocolDocuments = [];
    if (biosample.documents && biosample.documents.length > 0) {
        protocolDocuments = _.uniq(biosample.documents);
    }
    let characterizations = [];
    if (biosample.characterizations && biosample.characterizations.length > 0) {
        characterizations = _.uniq(biosample.characterizations);
    }
    let donorDocuments = [];
    let donorCharacterizations = [];
    if (biosample.donor) {
        if (biosample.donor.characterizations && biosample.donor.characterizations.length > 0) {
            donorCharacterizations = biosample.donor.characterizations;
        }
        if (biosample.donor.documents && biosample.donor.documents.length > 0) {
            donorDocuments = biosample.donor.documents;
        }
    }
    let treatmentDocuments = [];
    if (biosample.treatments && biosample.treatments.length > 0) {
        treatmentDocuments = biosample.treatments.reduce((allDocs, treatment) => ((treatment.documents && treatment.documents.length > 0) ? allDocs.concat(treatment.documents) : allDocs), []);
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
export const BiosampleTable = ({ items, limit, total, url, title, organisms }) => {
    let biosamples = items;
    let footer = null;
    let subheader = null;
    if (limit > 0) {
        // If limit isn't zero, include a footer with search link.
        footer = <BiosampleTableFooter items={items} total={total} url={url} />;
    } else {
        // The limit contains zero, so no footer or search link; just a count in the header.
        subheader = <div className="table-paged__count">{`${total} biosample${total === 1 ? '' : 's'}`}</div>;
    }

    // If there's a limit on entries to display and the array is greater than that
    // limit, then clone the array with just that specified number of elements
    if (limit > 0 && (limit < items.length)) {
        // Limit the experiment list by cloning first {limit} elements
        biosamples = items.slice(0, limit);
    }

    return (
        <SortTablePanel title={title} subheader={subheader}>
            <SortTable list={biosamples} columns={BiosampleTable.columns} meta={{ organisms }} footer={footer} />
        </SortTablePanel>
    );
};

BiosampleTable.propTypes = {
    items: PropTypes.array.isRequired,
    limit: PropTypes.number,
    total: PropTypes.number,
    url: PropTypes.string,
    title: PropTypes.string,
    organisms: PropTypes.array,
};

BiosampleTable.defaultProps = {
    limit: 0,
    total: 0,
    url: '',
    title: '',
    organisms: [],
};

BiosampleTable.columns = {
    accession: {
        title: 'Accession',
        display: (biosample) => <a href={biosample['@id']}>{biosample.accession}</a>,
    },
    'biosample_ontology.classification': {
        title: 'Type',
        getValue: (item) => item.biosample_ontology && item.biosample_ontology.classification,
    },
    'biosample_ontology.term_name': {
        title: 'Term',
        getValue: (item) => item.biosample_ontology && item.biosample_ontology.term_name,
    },
    summary: {
        title: 'Summary',
        sorter: false,
        display: (biosample, meta) => {
            const organismNames = typeof biosample.organism === 'string'
                ? meta.organisms
                : [biosample.organism.scientific_name].concat(GeneticModificationOrganismNames([biosample]));
            return <BiosampleSummaryDisplay summary={biosample.summary} organisms={organismNames} />;
        },
    },
};


// Display a count of biosamples in the footer, with a link to the corresponding search if needed
export const BiosampleTableFooter = (props) => {
    const { items, total, url } = props;

    return (
        <div className="table-panel__std-footer">
            <div className="table-panel__std-footer-count">Displaying {items.length} of {total}</div>
            {items.length < total ? <a className="table-panel__std-footer-search" href={url}>View all</a> : null}
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
    url: PropTypes.string, // URL to use for the complete donor search results
    title: PropTypes.string, // Title to use for the table of donors
};

DonorTable.defaultProps = {
    limit: 0,
    total: 0,
    url: '',
    title: '',
};

// <SortTable> column specification for the table of donors.
DonorTable.columns = {
    accession: {
        title: 'Accession',
        display: (donor) => <a href={donor['@id']}>{donor.accession}</a>,
    },
    species: {
        title: 'Species',
        display: (donor) => (donor.organism && donor.organism.scientific_name ? <i>{donor.organism.scientific_name}</i> : null),
    },
    sex: {
        title: 'Sex',
    },
};


// Display a count of donors in the footer, with a link to the corresponding search if needed
const DonorTableFooter = (props) => {
    const { items, total, url } = props;

    return (
        <div className="table-panel__std-footer">
            <div className="table-panel__std-footer-count">Displaying {items.length} of {total}</div>
            {items.length < total ? <a className="table-panel__std-footer-search" href={url}>View all</a> : null}
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
    const { award } = context;

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
    const supersedes = (context.supersedes && context.supersedes.map((supersedesAtId) => globals.atIdToAccession(supersedesAtId))) || [];

    if (alternateAccessions.length > 0 || supersededByAtIds.length > 0 || supersedes.length > 0) {
        return (
            <div className="replacement-accessions">
                <AlternateAccession altAcc={alternateAccessions} />
                {supersededByAtIds.length > 0 ?
                    <h4 className="replacement-accessions">
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
                    <h4 className="replacement-accessions">Supersedes {supersedes.join(', ')}</h4>
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
    <div className="table-panel__std-footer">
        <div className="table-panel__std-footer-count">Displaying {items.length} of {total}</div>
        {items.length < total ? <a className="table-panel__std-footer-search" href={url}>View all</a> : null}
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


export const experimentTableColumns = {
    accession: {
        title: 'Accession',
        display: (item) => <a href={item['@id']} title={`View page for experiment ${item.accession}`}>{item.accession}</a>,
    },

    assay_term_name: {
        title: 'Assay',
    },

    'replicates.library.biosample': {
        title: 'Biosamples',
        display: (item) => {
            if (item.replicates.length > 0) {
                const biosamples = _.uniq(
                    item.replicates.reduce((accBiosamples, replicate) => accBiosamples.concat(replicate.library.biosample), []),
                    (biosample) => biosample['@id']
                );
                if (biosamples.length > 0) {
                    return biosamples.map((biosample, index) => (
                        <span key={biosample['@id']}>
                            {index > 0 ? <>, </> : null}
                            <a href={biosample['@id']}>{biosample.accession}</a>
                        </span>
                    ));
                }
                return null;
            }
            return null;
        },
        hide: (list, columns, meta) => !(meta && meta.showBiosamples),
    },

    'biosample_ontology.term_name': {
        title: 'Biosample term name',
        getValue: (item) => item.biosample_ontology && item.biosample_ontology.term_name,
    },

    target: {
        title: 'Target',
        getValue: (item) => item.target && item.target.label,
    },

    description: {
        title: 'Description',
    },

    title: {
        title: 'Lab',
        getValue: (item) => (item.lab && item.lab.title ? item.lab.title : null),
    },
};


export const ExperimentTable = ({ items, limit, total, url, title, showBiosamples }) => {
    // If there's a limit on entries to display and the array is greater than that limit, then
    // clone the array with just that specified number of elements.
    if (items.length > 0) {
        let experiments;
        let footer = null;
        let subheader = null;
        if (limit > 0) {
            // Limit given, so use a footer with a search link.
            experiments = limit > 0 && limit < items.length ? items.slice(0, limit) : items;
            footer = <ExperimentTableFooter items={experiments} total={total} url={url} />;
        } else {
            // No limit given, so don't include a footer; have a count in the table header.
            experiments = items;
            subheader = <div className="table-paged__count">{`${total} experiment${total === 1 ? '' : 's'}`}</div>;
        }

        return (
            <div>
                <SortTablePanel title={title} subheader={subheader}>
                    <SortTable
                        list={experiments}
                        columns={experimentTableColumns}
                        footer={footer}
                        meta={{ showBiosamples }}
                    />
                </SortTablePanel>
            </div>
        );
    }
    return null;
};

ExperimentTable.propTypes = {
    /** List of experiments to display in the table */
    items: PropTypes.array.isRequired,
    /** Maximum number of experiments to display in the table */
    limit: PropTypes.number,
    /** Total number of experiments */
    total: PropTypes.number,
    /** URI to go to equivalent search results */
    url: PropTypes.string,
    /** Title for the table of experiments; can be string or component */
    title: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.node,
    ]),
    /** True to show column of experiment biosamples */
    showBiosamples: PropTypes.bool,
};

ExperimentTable.defaultProps = {
    limit: 0,
    total: 0,
    url: '',
    title: '',
    showBiosamples: false,
};


const tableContentMap = {
    Experiment: 'Experiments',
    FunctionalCharacterizationExperiment: 'Functional characterization experiments',
    SingleCellUnit: 'Single cell units',
    TransgenicEnhancerExperiment: 'Transgenic enhancer experiments',
};
/**
 * Display a table of experiments with the dataset in `context` as a possible_controls.
 */
export const ControllingExperiments = ({ context, items, total, url }) => {
    if (items.length > 0) {
        const tableContent = tableContentMap[context['@type'][0]] || 'Experiments';
        return (
            <div>
                <ExperimentTable
                    items={items}
                    limit={5}
                    total={total}
                    url={url}
                    title={`${tableContent} with ${context.accession} as a control:`}
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

/**
 * Display a count of biosample characterizations in the footer, with a link to the corresponding search if needed.
 */
const BiosampleCharacterizationTableFooter = ({ items, total, url }) => (
    <>
        <span>Displaying {items.length} of {total} </span>
        {items.length < total ? <a className="btn btn-info btn-xs pull-right" href={url}>View all</a> : null}
    </>
);

BiosampleCharacterizationTableFooter.propTypes = {
    /** Array of biosample characterizations that were displayed in the table */
    items: PropTypes.array.isRequired,
    /** Total number of biosample characterizations */
    total: PropTypes.number,
    /** URL to link to equivalent biosample characterization search results */
    url: PropTypes.string.isRequired,
};

BiosampleCharacterizationTableFooter.defaultProps = {
    total: 0,
};


const biosampleCharacterizationTableColumns = {
    'characterizes.biosample_ontology.term_name': {
        title: 'Biosample term',
        display: (char) => <a href={char['@id']}>{char.characterizes.biosample_ontology.term_name}</a>,
    },
    characterization_method: {
        title: 'Characterization method',
        getValue: (char) => char.characterization_method && char.characterization_method.uppercaseFirstChar(),
    },
    'lab.title': {
        title: 'Characterization lab',
        getValue: (char) => char.lab.title,
    },
    'review.lab.title': {
        title: 'Review lab',
        getValue: (char) => char.review && char.review.lab.title,
    },
    'review.status': {
        title: 'Review status',
        display: (char) => char.review && char.review.status && <Status item={char.review.status} badgeSize="small" inline />,
    },
};


export const BiosampleCharacterizationTable = ({ items, limit, total, url, title }) => {
    // If there's a limit on entries to display and the array is greater than that limit, then
    // clone the array with just that specified number of elements.
    const biosampleCharacterizations = limit > 0 && limit < items.length ? items.slice(0, limit) : items;

    return (
        <SortTablePanel title={title}>
            <SortTable list={biosampleCharacterizations} columns={biosampleCharacterizationTableColumns} footer={<BiosampleCharacterizationTableFooter items={biosampleCharacterizations} total={total} url={url} />} />
        </SortTablePanel>
    );
};

BiosampleCharacterizationTable.propTypes = {
    /** List of biosample characterizations to display in the table */
    items: PropTypes.array.isRequired,
    /** Maximum number of biosample characterizations to display in the table */
    limit: PropTypes.number,
    /** Total number of biosample characterizations */
    total: PropTypes.number,
    /** URI to go to equivalent search results */
    url: PropTypes.string.isRequired,
    /** Title for the table of biosample characterizations */
    title: PropTypes.string,
};

BiosampleCharacterizationTable.defaultProps = {
    limit: 0,
    total: 0,
    title: '',
};


// Columns to display in Deriving/Derived From file tables.
const derivingCols = {
    accession: {
        title: 'Accession',
        display: (file) => <a href={file['@id']} title={`View page for file ${file.title}`}>{file.title}</a>,
        sorter: false,
    },
    dataset: {
        title: 'Dataset',
        display: (file) => {
            const datasetAccession = globals.atIdToAccession(file.dataset);
            return <a href={file.dataset} title={`View page for dataset ${datasetAccession}`}>{datasetAccession}</a>;
        },
        sorter: false,
    },
    file_format: { title: 'File format', sorter: false },
    output_type: { title: 'Output type', sorter: false },
    title: {
        title: 'Lab',
        getValue: (file) => (file.lab && file.lab.title ? file.lab.title : ''),
        sorter: false,
    },
    assembly: { title: 'Mapping assembly', sorter: false },
    status: {
        title: 'File status',
        display: (item) => <Status item={item} badgeSize="small" inline />,
        sorter: false,
    },
};


const PAGED_FILE_TABLE_MAX = 25; // Maximum number of files per page
const PAGED_FILE_CACHE_MAX = 10; // Maximum number of pages to cache


/**
 * Calculates the number of pages of files given the total number of files.
 * @param {number} count Total number of files in array
 *
 * @return {number} Total number of pages to hold these files
 */
const getTotalPages = (count) => parseInt(count / PAGED_FILE_TABLE_MAX, 10) + (count % PAGED_FILE_TABLE_MAX ? 1 : 0);


/**
 * Calculate array of complete file objects or file @ids to be displayed on the current page of
 * files, given the complete set of files and the current page number.
 * @param {array} files File @ids or complete file objects
 *
 * @return {array} File @ids displayed on the current page
 */
const getPageFiles = (files, pageNo) => {
    if (files.length > 0) {
        const start = pageNo * PAGED_FILE_TABLE_MAX;
        return files.slice(start, start + PAGED_FILE_TABLE_MAX);
    }
    return [];
};


/**
 * Display the header for the file table, including the pager.
 */
const FileTableHeader = ({ title, currentPage, totalPageCount, control, updateCurrentPage }) => (
    <div className="header-paged-sorttable">
        {title}
        <div className="header-paged-sorttable__controls">
            {control}
            {totalPageCount > 1 ? <Pager.Simple total={totalPageCount} current={currentPage} updateCurrentPage={updateCurrentPage} /> : null}
        </div>
    </div>
);

FileTableHeader.propTypes = {
    /** Title of table */
    title: PropTypes.oneOfType([
        PropTypes.element, // Title is a React component
        PropTypes.string, // Title is an unformatted string
    ]).isRequired,
    /** Current displayed page number, 0 based */
    currentPage: PropTypes.number.isRequired,
    /** Total number of pages */
    totalPageCount: PropTypes.number.isRequired,
    /** React component to render in the header next to the pager */
    control: PropTypes.element,
    /** Called with the new page number the user selected */
    updateCurrentPage: PropTypes.func.isRequired,
};

FileTableHeader.defaultProps = {
    control: null,
};


/**
 * Alternate message for the batch-download modal, to indicate the PublicationData set has too many
 * files to practically download.
 */
const AltModalMessage = () => (
    <div>
        <p>
            This dataset is too large to automatically generate a manifest or metadata file. Please
            see the documents attached on the previous page, files.txt and metadata.tsv. You can
            save files.txt to any server and use the following command using cURL to download all
            the files in the list:
        </p>

        <code>xargs -L 1 curl -O -J -L &lt; files.txt</code>

        <p>Or you can directly access the files in AWS S3: <a href="https://registry.opendata.aws/encode-project/">https://registry.opendata.aws/encode-project/</a></p>
    </div>
);


/**
 * Display a panel containing a table of files given an array of file @ids or complete file
 * objects, performing fetches of the complete file objects for the former. If the number of files
 * exceeds PAGED_FILE_TABLE_MAX, the user can use a pager to scroll between pages of files.
 */
export const FileTablePaged = ({ context, fileIds, files, title }) => {
    // Initialize or load the page cache. Keyed by `currentPageNum`.
    const pageCache = React.useRef({});
    // Calculate the total number of pages given the array of files.
    const totalPages = React.useMemo(() => getTotalPages(fileIds ? fileIds.length : files.length), [fileIds, files]);
    // Current page of a multi-page table, zero-based.
    const [currentPageNum, setCurrentPageNum] = React.useState(0);
    // Array of file objects displayed for the current page.
    const [currentPageFiles, setCurrentPageFiles] = React.useState(files ? getPageFiles(files, currentPageNum) : []);

    // Called when the user selects a new page of files using the pager.
    const updateCurrentPage = React.useCallback((newCurrentPageNum) => {
        // For fetched files, cache the current page of files to keep it from getting GC'd if it's
        // not already cached.
        if (fileIds) {
            if (!pageCache.current[currentPageNum]) {
                // Save the current page's array of fetched complete file objects to the cache.
                pageCache.current[currentPageNum] = currentPageFiles;

                // To save memory, see if we can lose a reference to a page so that it gets GC'd. Need
                // to convert cache page number keys to strings because numeric keys always become
                // strings.
                const cachedPageNos = Object.keys(pageCache.current).map((pageNo) => parseInt(pageNo, 10));
                if (cachedPageNos.length > PAGED_FILE_CACHE_MAX) {
                    // Our cache has filled. Find the cache entry with a page farthest from the current
                    // and kick it out. A bit complicated because it finds both the maximum page-number
                    // difference as well as its page number.
                    let maxDiff = 0;
                    let maxDiffPageNo;
                    cachedPageNos.forEach((pageNo) => {
                        const diff = Math.abs(currentPageNum - pageNo);
                        if (diff > maxDiff) {
                            maxDiff = diff;
                            maxDiffPageNo = pageNo;
                        }
                    });

                    // Dump a page from the cache.
                    delete pageCache.current[maxDiffPageNo];
                }
            }

            // Trigger a rerender if we get a cache hit for the new page of files.
            if (pageCache.current[newCurrentPageNum]) {
                setCurrentPageFiles(pageCache.current[newCurrentPageNum]);
            }
        } else {
            // Extract the new current page of files from the existing array of file objects and
            // immediately trigger a rerender.
            setCurrentPageFiles(getPageFiles(files, newCurrentPageNum));
        }

        // Update the current page number for all cases.
        setCurrentPageNum(newCurrentPageNum);
    }, [currentPageNum, currentPageFiles, fileIds, files]);

    React.useEffect(() => {
        if (fileIds && !pageCache.current[currentPageNum]) {
            // Send a request for the file objects for the current page and save the resulting full
            // file objects in state for rendering in the table.
            const pageFileIds = getPageFiles(fileIds, currentPageNum);
            if (pageFileIds.length > 0) {
                // Fetch the non-cached page's files and re-render once retrieved.
                requestFiles(pageFileIds).then((pageFiles) => {
                    setCurrentPageFiles(pageFiles || []);
                });
            }
        }
    }, [fileIds, currentPageNum]);

    // Rendering portion of component.
    if (currentPageFiles.length > 0) {
        const headerTitle = typeof title === 'string' ? <h4>{title}</h4> : title;
        const fileCount = fileIds ? fileIds.length : files.length;
        const fileCountDisplay = <div className="table-paged__count">{`${fileCount} file${fileCount === 1 ? '' : 's'}`}</div>;

        // Determine whether too many files exist to download.
        const canDownload = fileCount <= MAX_DOWNLOADABLE_FILES;
        let batchDownloadController;
        if (context) {
            const query = new QueryString();
            batchDownloadController = new DatasetBatchDownloadController(context, query);
        }

        return (
            <SortTablePanel
                header={
                    <FileTableHeader
                        title={headerTitle}
                        currentPage={currentPageNum}
                        totalPageCount={totalPages}
                        control={
                            batchDownloadController
                                ? (
                                    <BatchDownloadActuator
                                        controller={batchDownloadController}
                                        modalContent={!canDownload ? <AltModalMessage /> : null}
                                        disabled={!canDownload}
                                    />
                                )
                                : null}
                        updateCurrentPage={updateCurrentPage}
                    />
                }
                subheader={fileCountDisplay}
                css="table-paged"
            >
                <SortTable
                    list={currentPageFiles}
                    columns={derivingCols}
                />
            </SortTablePanel>
        );
    }
    return null;
};

/**
 * Custom PropType validator to have either `fileIds` or `files` but not both, and either must be
 * an array.
 */
const testFileTablePagedProps = (props, propName, componentName) => {
    if (!(props.fileIds || props.files) || (props.fileIds && props.files)) {
        return new Error(`Props 'fileIds' or 'files' but not both required in '${componentName}'.`);
    }
    if (props[propName] && (typeof props[propName] !== 'object' || !Array.isArray(props[propName]))) {
        return new Error(`Prop '${propName}' in '${componentName}' must be an array.`);
    }
    return null;
};

FileTablePaged.propTypes = {
    /** Object being displayed that includes the file table */
    context: PropTypes.object,
    /** Array of all file @ids to include in table on all pages */
    fileIds: testFileTablePagedProps,
    /** Alternative array of file objects to include in table on all pages */
    files: testFileTablePagedProps,
    /** Title for the panel containing the table of files */
    title: PropTypes.oneOfType([
        PropTypes.element, // Title is a React component
        PropTypes.string, // Title is an unformatted string
    ]).isRequired,
};

FileTablePaged.defaultProps = {
    context: null,
    fileIds: null,
    files: null,
};


/**
 * Display a DOI dbxref and a button to copy the link to the clipboard.
 */
export const DoiRef = ({ context }) => {
    if (context.doi) {
        const doiDbxref = `doi:${context.doi}`;
        const doiHref = dbxrefHref(doiDbxref, context);
        if (doiHref) {
            return (
                <div className="doi-ref">
                    <CopyButton
                        label="Copy DOI URL"
                        copyText={doiHref}
                        css="btn-xs doi-ref__copy-button"
                    />
                    <div className="doi-ref__id">{doiDbxref}</div>
                </div>
            );
        }
    }
    return null;
};

DoiRef.propTypes = {
    /** Target of doi -- currently displayed dataset object */
    context: PropTypes.object.isRequired,
};
