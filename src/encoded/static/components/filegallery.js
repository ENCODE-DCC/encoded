import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import moment from 'moment';
import { Panel, PanelHeading, TabPanel, TabPanelPane } from '../libs/bootstrap/panel';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../libs/bootstrap/modal';
import { collapseIcon } from '../libs/svg-icons';
import { auditDecor, auditsDisplayed, AuditIcon } from './audit';
import { FetchedData, Param } from './fetched';
import * as globals from './globals';
import { Graph, JsonGraph, GraphException } from './graph';
import { requestFiles, DownloadableAccession, BrowserSelector } from './objectutils';
import { qcIdToDisplay } from './quality_metric';
import { softwareVersionList } from './software';
import { SortTablePanel, SortTable } from './sorttable';


const MINIMUM_COALESCE_COUNT = 5; // Minimum number of files in a coalescing group


// Get the audit icon for the highest audit level in the given file.
function fileAuditStatus(file) {
    let highestAuditLevel;

    if (file.audit) {
        const sortedAuditLevels = _(Object.keys(file.audit)).sortBy(level => -file.audit[level][0].level);
        highestAuditLevel = sortedAuditLevels[0];
    } else {
        highestAuditLevel = 'OK';
    }
    return <AuditIcon level={highestAuditLevel} addClasses="file-audit-status" />;
}


// Sort callback to compare the accession/external_accession of two files.
function fileAccessionSort(a, b) {
    if (!a.accession !== !b.accession) {
        // One or the other but not both use an external accession. Sort so regular accession
        // comes first.
        return a.accession ? -1 : 1;
    }

    // We either have two accessions or two external accessions. Do a case-insensitive compare on
    // the calculated property that gets external_accession if accession isn't available.
    const aTitle = a.title.toLowerCase();
    const bTitle = b.title.toLowerCase();
    return aTitle > bTitle ? 1 : (aTitle < bTitle ? -1 : 0);
}


export class FileTable extends React.Component {
    static rowClasses() {
        return '';
    }

    constructor() {
        super();

        // Initialize component state.
        this.state = {
            maxWidth: 'auto', // Width of widest table
            collapsed: { // Keeps track of which tables are collapsed
                raw: false,
                rawArray: false,
                proc: false,
                ref: false,
            },
        };

        // Initialize non-state component variables.
        this.cv = {
            maxWidthRef: '', // ref key of table with this.state.maxWidth width
            maxWidthNode: null, // DOM node of table with this.state.maxWidth width
        };

        this.fileClick = this.fileClick.bind(this);
        this.handleCollapse = this.handleCollapse.bind(this);
        this.handleCollapseProc = this.handleCollapseProc.bind(this);
        this.handleCollapseRef = this.handleCollapseRef.bind(this);
        this.hoverDL = this.hoverDL.bind(this);
    }

    fileClick(file) {
        const node = {
            '@type': ['File'],
            metadata: {
                ref: file,
            },
            schemas: this.props.schemas,
        };
        this.props.setInfoNodeId(node);
        this.props.setInfoNodeVisible(true);
    }

    handleCollapse(table) {
        // Handle a click on a collapse button by toggling the corresponding tableCollapse state var
        const collapsed = _.clone(this.state.collapsed);
        collapsed[table] = !collapsed[table];
        this.setState({ collapsed });
    }

    handleCollapseProc() {
        this.handleCollapse('proc');
    }

    handleCollapseRef() {
        this.handleCollapse('ref');
    }

    hoverDL(hovering, fileUuid) {
        this.setState({ restrictedTip: hovering ? fileUuid : '' });
    }

    render() {
        const {
            items,
            graphedFiles,
            filePanelHeader,
            encodevers,
            selectedFilterValue,
            filterOptions,
            anisogenic,
            showFileCount,
            session,
            adminUser,
        } = this.props;
        let selectedAssembly;
        let selectedAnnotation;
        const loggedIn = !!(session && session['auth.userid']);

        let datasetFiles = _((items && items.length) ? items : []).uniq(file => file['@id']);

        if (datasetFiles.length) {
            const unfilteredCount = datasetFiles.length;

            if (selectedFilterValue && filterOptions[selectedFilterValue]) {
                selectedAssembly = filterOptions[selectedFilterValue].assembly;
                selectedAnnotation = filterOptions[selectedFilterValue].annotation;
            }

            // Filter all the files according to the given filters, and remove duplicates
            datasetFiles = _(datasetFiles).filter((file) => {
                if (file.output_category !== 'raw data') {
                    if (selectedAssembly) {
                        if (selectedAnnotation) {
                            return selectedAnnotation === file.genome_annotation && selectedAssembly === file.assembly;
                        }
                        return !file.genome_annotation && selectedAssembly === file.assembly;
                    }
                }
                return true;
            });
            const filteredCount = datasetFiles.length;

            // Extract four kinds of file arrays
            const files = _(datasetFiles).groupBy((file) => {
                if (file.output_category === 'raw data') {
                    return file.output_type === 'reads' ? 'raw' : 'rawArray';
                }
                if (file.output_category === 'reference') {
                    return 'ref';
                }
                return 'proc';
            });

            return (
                <div>
                    {showFileCount ? <div className="file-gallery-counts">Displaying {filteredCount} of {unfilteredCount} files</div> : null}
                    <SortTablePanel header={filePanelHeader} noDefaultClasses={this.props.noDefaultClasses}>
                        <RawSequencingTable
                            files={files.raw}
                            meta={{
                                encodevers,
                                anisogenic,
                                fileClick: this.fileClick,
                                graphedFiles,
                                session,
                                loggedIn,
                                adminUser,
                            }}
                        />
                        <RawFileTable
                            files={files.rawArray}
                            meta={{
                                encodevers,
                                anisogenic,
                                fileClick: this.fileClick,
                                graphedFiles,
                                session,
                                loggedIn,
                                adminUser,
                            }}
                        />
                        <SortTable
                            title={
                                <CollapsingTitle
                                    title="Processed data" collapsed={this.state.collapsed.proc}
                                    handleCollapse={this.handleCollapseProc}
                                />
                            }
                            rowClasses={this.rowClasses}
                            collapsed={this.state.collapsed.proc}
                            list={files.proc}
                            columns={FileTable.procTableColumns}
                            sortColumn="biological_replicates"
                            meta={{
                                encodevers,
                                anisogenic,
                                hoverDL: this.hoverDL,
                                restrictedTip: this.state.restrictedTip,
                                fileClick: this.fileClick,
                                graphedFiles,
                                loggedIn,
                                adminUser,
                            }}
                        />
                        <SortTable
                            title={
                                <CollapsingTitle
                                    title="Reference data"
                                    collapsed={this.state.collapsed.ref}
                                    handleCollapse={this.handleCollapseRef}
                                />
                            }
                            collapsed={this.state.collapsed.ref}
                            rowClasses={this.rowClasses}
                            list={files.ref}
                            columns={FileTable.refTableColumns}
                            meta={{
                                encodevers,
                                anisogenic,
                                hoverDL: this.hoverDL,
                                restrictedTip: this.state.restrictedTip,
                                fileClick: this.fileClick,
                                graphedFiles,
                                loggedIn,
                                adminUser,
                            }}
                        />
                    </SortTablePanel>
                </div>
            );
        }
        return <p className="browser-error">No files to display.</p>;
    }
}

FileTable.propTypes = {
    items: PropTypes.array.isRequired, // Array of files to appear in the table
    graphedFiles: PropTypes.object, // Specifies which files are in the graph
    filePanelHeader: PropTypes.object, // Table header component
    encodevers: PropTypes.string, // ENCODE version of the experiment
    selectedFilterValue: PropTypes.string, // Selected filter from popup menu
    filterOptions: PropTypes.array, // Array of assambly/annotation from file array
    anisogenic: PropTypes.bool, // True if experiment is anisogenic
    showFileCount: PropTypes.bool, // True to show count of files in table
    setInfoNodeId: PropTypes.func, // Function to call to set the currently selected node ID
    setInfoNodeVisible: PropTypes.func, // Function to call to set the visibility of the node's modal
    session: PropTypes.object, // Persona user session
    adminUser: PropTypes.bool, // True if user is an admin user
    schemas: PropTypes.object, // Object from /profiles/ containing all schemas
    noDefaultClasses: PropTypes.bool, // True to strip SortTable panel of default CSS classes
};

FileTable.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
};


// Configuration for process file table
FileTable.procTableColumns = {
    accession: {
        title: 'Accession',
        display: (item, meta) => {
            const { loggedIn, adminUser } = meta;
            const buttonEnabled = !!(meta.graphedFiles && meta.graphedFiles[item['@id']]);
            return <DownloadableAccession file={item} buttonEnabled={buttonEnabled} clickHandler={meta.fileClick ? meta.fileClick : null} loggedIn={loggedIn} adminUser={adminUser} />;
        },
        objSorter: (a, b) => fileAccessionSort(a, b),
    },
    file_type: { title: 'File type' },
    output_type: { title: 'Output type' },
    biological_replicates: {
        title: (list, columns, meta) => <span>{meta.anisogenic ? 'Anisogenic' : 'Biological'} replicate</span>,
        getValue: item => (item.biological_replicates ? item.biological_replicates.sort((a, b) => a - b).join(', ') : ''),
    },
    mapped_read_length: {
        title: 'Mapped read length',
        hide: list => _(list).all(file => file.mapped_read_length === undefined),
    },
    assembly: { title: 'Mapping assembly' },
    genome_annotation: {
        title: 'Genome annotation',
        hide: list => _(list).all(item => !item.genome_annotation),
    },
    title: {
        title: 'Lab',
        getValue: item => (item.lab && item.lab.title ? item.lab.title : null),
    },
    date_created: {
        title: 'Date added',
        getValue: item => moment.utc(item.date_created).format('YYYY-MM-DD'),
        sorter: (a, b) => {
            if (a && b) {
                return Date.parse(a) - Date.parse(b);
            }
            const bTest = (b ? 1 : 0);
            return a ? -1 : bTest;
        },
    },
    file_size: {
        title: 'File size',
        display: item => <span>{globals.humanFileSize(item.file_size)}</span>,
    },
    audit: {
        title: 'Audit status',
        display: item => <div>{fileAuditStatus(item)}</div>,
    },
    status: {
        title: 'File status',
        display: item => <div className="characterization-meta-data"><FileStatusLabel file={item} /></div>,
    },
};

// Configuration for reference file table
FileTable.refTableColumns = {
    accession: {
        title: 'Accession',
        display: (item, meta) => {
            const { loggedIn, adminUser } = meta;
            const buttonEnabled = !!(meta.graphedFiles && meta.graphedFiles[item['@id']]);
            return <DownloadableAccession file={item} buttonEnabled={buttonEnabled} clickHandler={meta.fileClick ? meta.fileClick : null} loggedIn={loggedIn} adminUser={adminUser} />;
        },
        objSorter: (a, b) => fileAccessionSort(a, b),
    },
    file_type: { title: 'File type' },
    output_type: { title: 'Output type' },
    mapped_read_length: {
        title: 'Mapped read length',
        hide: list => _(list).all(file => file.mapped_read_length === undefined),
    },
    assembly: { title: 'Mapping assembly' },
    genome_annotation: {
        title: 'Genome annotation',
        hide: list => _(list).all(item => !item.genome_annotation),
    },
    title: {
        title: 'Lab',
        getValue: item => (item.lab && item.lab.title ? item.lab.title : null),
    },
    date_created: {
        title: 'Date added',
        getValue: item => moment.utc(item.date_created).format('YYYY-MM-DD'),
        sorter: (a, b) => {
            if (a && b) {
                return Date.parse(a) - Date.parse(b);
            }
            const bTest = b ? 1 : 0;
            return a ? -1 : bTest;
        },
    },
    file_size: {
        title: 'File size',
        display: item => <span>{globals.humanFileSize(item.file_size)}</span>,
    },
    audit: {
        title: 'Audit status',
        display: item => <div>{fileAuditStatus(item)}</div>,
    },
    status: {
        title: 'File status',
        display: item => <div className="characterization-meta-data"><FileStatusLabel file={item} /></div>,
    },
};


function sortBioReps(a, b) {
    // Sorting function for biological replicates of the given files.
    let result; // Ends sorting loop once it has a value
    let i = 0;
    let repA = (a.biological_replicates && a.biological_replicates.length) ? a.biological_replicates[i] : undefined;
    let repB = (b.biological_replicates && b.biological_replicates.length) ? b.biological_replicates[i] : undefined;
    while (result === undefined) {
        if (repA !== undefined && repB !== undefined) {
            // Both biological replicates have a value
            if (repA !== repB) {
                // We got a real sorting result
                result = repA - repB;
            } else {
                // They both have values, but they're equal; go to next
                // biosample replicate array elements
                i += 1;
                repA = a.biological_replicates[i];
                repB = b.biological_replicates[i];
            }
        } else if (repA !== undefined || repB !== undefined) {
            // One and only one replicate empty; sort empty one after
            result = repA ? 1 : -1;
        } else {
            // Both empty; sorting result same
            result = 0;
        }
    }
    return result;
}


const FileStatusLabel = (props) => {
    const { file } = props;
    const status = file.status;
    const statusClass = globals.statusClass(status, 'status-indicator status-indicator--', true);

    // Display simple string and optional title in badge
    return (
        <div key={status} className={statusClass}>
            <i className="icon icon-circle status-indicator__icon" />
            <div className="status-indicator__label">{status}</div>
        </div>
    );
};

FileStatusLabel.propTypes = {
    file: PropTypes.object.isRequired, // File whose status we're displaying
};


class RawSequencingTable extends React.Component {
    constructor() {
        super();

        // Initialize React state variables.
        this.state = {
            collapsed: false, // Collapsed/uncollapsed state of table
            restrictedTip: '', // UUID of file with tooltip showing
        };

        // Bind `this` to non-React methods.
        this.handleCollapse = this.handleCollapse.bind(this);
        this.hoverDL = this.hoverDL.bind(this);
    }

    handleCollapse() {
        // Handle a click on a collapse button by toggling the corresponding tableCollapse state var
        this.setState({ collapsed: !this.state.collapsed });
    }

    hoverDL(hovering, fileUuid) {
        this.setState({ restrictedTip: hovering ? fileUuid : '' });
    }

    render() {
        const { files, meta } = this.props;
        const { loggedIn, adminUser } = meta;

        if (files && files.length) {
            // Make object keyed by all files' @ids to make searching easy. Each key's value
            // points to the corresponding file object.
            const filesKeyed = {};
            files.forEach((file) => {
                filesKeyed[file['@id']] = file;
            });

            // Make lists of files that are and aren't paired. Paired files with missing partners
            // count as not paired. Files with more than one biological replicate don't count as
            // paired.
            const nonpairedFiles = [];
            const pairedFiles = _(files).filter((file) => {
                if (file.pairSortKey) {
                    // If we already know this file is part of a good pair from before, just let it
                    // pass the filter
                    return true;
                }

                // See if the file qualifies as a pair element
                if (file.paired_with) {
                    // File is paired; make sure its partner exists and points back at `file`.
                    const partner = filesKeyed[file.paired_with];
                    if (partner && partner.paired_with === file['@id']) {
                        // The file and its partner properly paired with each other. Now see if
                        // their biological replicates and libraries allow them to pair up in the
                        // file table. Either they must share the same single biological replicate
                        // or they must share the fact that neither have a biological replicate
                        // which can be true for csqual and csfasta files.
                        if ((file.biological_replicates && file.biological_replicates.length === 1 &&
                                partner.biological_replicates && partner.biological_replicates.length === 1 &&
                                file.biological_replicates[0] === partner.biological_replicates[0]) ||
                                ((!file.biological_replicates || file.biological_replicates.length === 0) &&
                                (!partner.biological_replicates || partner.biological_replicates.length === 0))) {
                            // Both the file and its partner qualify as good pairs of each other. Let
                            // them pass the filter, and record set their sort keys to the lower of
                            // the two accessions -- that's how pairs will sort within a biological
                            // replicate.
                            partner.pairSortKey = file.title < partner.title ? file.title : partner.title;
                            file.pairSortKey = partner.pairSortKey;
                            file.pairSortKey += file.paired_end;
                            partner.pairSortKey += partner.paired_end;
                            return true;
                        }
                    }
                }

                // File not part of a pair; add to non-paired list and filter it out
                nonpairedFiles.push(file);
                return false;
            });

            // Group paired files by biological replicate and library -- four-digit biological
            // replicate concatenated with library accession becomes the group key, and all files
            // with that biological replicate and library form an array under that key. If the pair
            // don't belong to a biological replicate, sort them under the fake replicate `Z   `
            // so that they'll sort at the end.
            let pairedRepGroups = {};
            let pairedRepKeys = [];
            if (pairedFiles.length) {
                pairedRepGroups = _(pairedFiles).groupBy(file => (
                    (file.biological_replicates && file.biological_replicates.length === 1) ?
                        globals.zeroFill(file.biological_replicates[0]) + ((file.replicate && file.replicate.library) ? file.replicate.library.accession : '')
                    :
                        'Z'
                ));

                // Make a sorted list of keys
                pairedRepKeys = Object.keys(pairedRepGroups).sort();
            }

            return (
                <table className="table table-sortable table-raw">
                    <thead>
                        <tr className="table-section">
                            <th colSpan="11">
                                <CollapsingTitle title="Raw sequencing data" collapsed={this.state.collapsed} handleCollapse={this.handleCollapse} />
                            </th>
                        </tr>

                        {!this.state.collapsed ?
                            <tr>
                                <th>Biological replicate</th>
                                <th>Library</th>
                                <th>Accession</th>
                                <th>File type</th>
                                <th>Run type</th>
                                <th>Read</th>
                                <th>Lab</th>
                                <th>Date added</th>
                                <th>File size</th>
                                <th>Audit status</th>
                                <th>File status</th>
                            </tr>
                        : null}
                    </thead>

                    {!this.state.collapsed ?
                        <tbody>
                            {pairedRepKeys.map((pairedRepKey, j) => {
                                // groupFiles is an array of files under a bioreplicate/library
                                const groupFiles = pairedRepGroups[pairedRepKey];
                                const bottomClass = j < (pairedRepKeys.length - 1) ? 'merge-bottom' : '';

                                // Render each file's row, with the biological replicate and library
                                // cells only on the first row.
                                return groupFiles.sort((a, b) => (a.pairSortKey < b.pairSortKey ? -1 : 1)).map((file, i) => {
                                    let pairClass;
                                    if (file.paired_end === '2') {
                                        pairClass = `align-pair2${(i === groupFiles.length - 1) && (j === pairedRepKeys.length - 1) ? '' : ' pair-bottom'}`;
                                    } else {
                                        pairClass = 'align-pair1';
                                    }

                                    // Prepare for run_type display
                                    let runType;
                                    if (file.run_type === 'single-ended') {
                                        runType = 'SE';
                                    } else if (file.run_type === 'paired-ended') {
                                        runType = 'PE';
                                    }

                                    return (
                                        <tr key={file['@id']}>
                                            {i === 0 ?
                                                <td rowSpan={groupFiles.length} className={`${bottomClass} merge-right table-raw-merged table-raw-biorep`}>{groupFiles[0].biological_replicates[0]}</td>
                                            : null}
                                            {i === 0 ?
                                                <td rowSpan={groupFiles.length} className={`${bottomClass} merge-right + table-raw-merged`}>{(groupFiles[0].replicate && groupFiles[0].replicate.library) ? groupFiles[0].replicate.library.accession : null}</td>
                                            : null}
                                            <td className={pairClass}>
                                                <DownloadableAccession file={file} clickHandler={meta.fileClick ? meta.fileClick : null} loggedIn={loggedIn} adminUser={adminUser} />
                                            </td>
                                            <td className={pairClass}>{file.file_type}</td>
                                            <td className={pairClass}>{runType}{file.read_length ? <span>{runType ? <span /> : null}{file.read_length + file.read_length_units}</span> : null}</td>
                                            <td className={pairClass}>{file.paired_end}</td>
                                            <td className={pairClass}>{file.lab && file.lab.title ? file.lab.title : null}</td>
                                            <td className={pairClass}>{moment.utc(file.date_created).format('YYYY-MM-DD')}</td>
                                            <td className={pairClass}>{globals.humanFileSize(file.file_size)}</td>
                                            <td className={pairClass}>{fileAuditStatus(file)}</td>
                                            <td className={`${pairClass} characterization-meta-data`}><FileStatusLabel file={file} /></td>
                                        </tr>
                                    );
                                });
                            })}
                            {nonpairedFiles.sort(sortBioReps).map((file, i) => {
                                // Prepare for run_type display
                                let runType;
                                if (file.run_type === 'single-ended') {
                                    runType = 'SE';
                                } else if (file.run_type === 'paired-ended') {
                                    runType = 'PE';
                                }
                                const rowClasses = [
                                    pairedRepKeys.length && i === 0 ? 'table-raw-separator' : null,
                                ];

                                // Determine if accession should be a button or not.
                                const buttonEnabled = !!(meta.graphedFiles && meta.graphedFiles[file['@id']]);

                                return (
                                    <tr key={file['@id']} className={rowClasses.join(' ')}>
                                        <td className="table-raw-biorep">{file.biological_replicates && file.biological_replicates.length ? file.biological_replicates.sort((a, b) => a - b).join(', ') : 'N/A'}</td>
                                        <td>{(file.replicate && file.replicate.library) ? file.replicate.library.accession : 'N/A'}</td>
                                        <td>
                                            <DownloadableAccession file={file} buttonEnabled={buttonEnabled} clickHandler={meta.fileClick ? meta.fileClick : null} loggedIn={loggedIn} adminUser={adminUser} />
                                        </td>
                                        <td>{file.file_type}</td>
                                        <td>{runType}{file.read_length ? <span>{runType ? <span /> : null}{file.read_length + file.read_length_units}</span> : null}</td>
                                        <td>{file.paired_end}</td>
                                        <td>{file.lab && file.lab.title ? file.lab.title : null}</td>
                                        <td>{moment.utc(file.date_created).format('YYYY-MM-DD')}</td>
                                        <td>{globals.humanFileSize(file.file_size)}</td>
                                        <td>{fileAuditStatus(file)}</td>
                                        <td className="characterization-meta-data"><FileStatusLabel file={file} /></td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    : null}

                    <tfoot>
                        <tr>
                            <td className={`file-table-footer${this.state.collapsed ? ' hiding' : ''}`} colSpan="11" />
                        </tr>
                    </tfoot>
                </table>
            );
        }

        // No files to display
        return null;
    }
}

RawSequencingTable.propTypes = {
    files: PropTypes.array, // Raw files to display
    meta: PropTypes.object, // Extra metadata in the same format passed to SortTable
};


class RawFileTable extends React.Component {
    constructor() {
        super();

        // Initialize React state variables.
        this.state = {
            collapsed: false, // Collapsed/uncollapsed state of table
            restrictedTip: '', // UUID of file with tooltip showing
        };

        // Bind `this` to non-React methods.
        this.handleCollapse = this.handleCollapse.bind(this);
        this.hoverDL = this.hoverDL.bind(this);
    }

    handleCollapse() {
        // Handle a click on a collapse button by toggling the corresponding tableCollapse state var
        this.setState({ collapsed: !this.state.collapsed });
    }

    hoverDL(hovering, fileUuid) {
        this.setState({ restrictedTip: hovering ? fileUuid : '' });
    }

    render() {
        const { files, meta } = this.props;
        const { loggedIn, adminUser } = meta;

        if (files && files.length) {
            // Group all files by their library accessions. Any files without replicates or
            // libraries get grouped under library 'Z' so they get sorted at the end.
            const libGroups = _(files).groupBy((file) => {
                // Groups have a 4-digit zero-filled biological replicate number concatenated with
                // the library accession, e.g. 0002ENCLB158ZZZ.
                const bioRep = globals.zeroFill(file.biological_replicates[0], 4);
                return bioRep + (file.replicate && file.replicate.library && file.replicate.library.accession ? file.replicate.library.accession : 'Z');
            });

            // Split library/file groups into paired and non-paired library/file groups.
            const pairedGroups = {};
            const nonpairedFiles = [];
            Object.keys(libGroups).forEach((libGroupKey) => {
                if (libGroups[libGroupKey].length > 1) {
                    pairedGroups[libGroupKey] = libGroups[libGroupKey];
                } else {
                    nonpairedFiles.push(libGroups[libGroupKey][0]);
                }
            });
            const pairedKeys = Object.keys(pairedGroups).sort();

            return (
                <table className="table table-sortable table-raw">
                    <thead>
                        <tr className="table-section">
                            <th colSpan="11">
                                <CollapsingTitle title="Raw data" collapsed={this.state.collapsed} handleCollapse={this.handleCollapse} />
                            </th>
                        </tr>

                        {!this.state.collapsed ?
                            <tr>
                                <th>Biological replicate</th>
                                <th>Library</th>
                                <th>Accession</th>
                                <th>File type</th>
                                <th>Output type</th>
                                <th>Mapping assembly</th>
                                <th>Lab</th>
                                <th>Date added</th>
                                <th>File size</th>
                                <th>Audit status</th>
                                <th>File status</th>
                            </tr>
                        : null}
                    </thead>

                    {!this.state.collapsed ?
                        <tbody>
                            {pairedKeys.map((pairedKey, j) => {
                                // groupFiles is an array of files under a bioreplicate/library
                                const groupFiles = pairedGroups[pairedKey];
                                const bottomClass = j < (pairedKeys.length - 1) ? 'merge-bottom' : '';

                                // Render each file's row, with the biological replicate and library
                                // cells only on the first row.
                                return groupFiles.sort((a, b) => (a.title < b.title ? -1 : 1)).map((file, i) => {
                                    let pairClass;
                                    if (i === 1) {
                                        pairClass = `align-pair2${(i === groupFiles.length - 1) && (j === pairedKeys.length - 1) ? '' : ' pair-bottom'}`;
                                    } else {
                                        pairClass = 'align-pair1';
                                    }

                                    // Determine if the accession should be a button or not.
                                    const buttonEnabled = !!(meta.graphedFiles && meta.graphedFiles[file['@id']]);

                                    // Prepare for run_type display
                                    return (
                                        <tr key={file['@id']}>
                                            {i === 0 ?
                                                <td rowSpan={groupFiles.length} className={`${bottomClass} merge-right table-raw-merged table-raw-biorep`}>
                                                    {groupFiles[0].biological_replicates.length ? <span>{groupFiles[0].biological_replicates[0]}</span> : <i>N/A</i>}
                                                </td>
                                            : null}
                                            {i === 0 ?
                                                <td rowSpan={groupFiles.length} className={`${bottomClass} merge-right table-raw-merged`}>
                                                    {groupFiles[0].replicate && groupFiles[0].replicate.library ? <span>{groupFiles[0].replicate.library.accession}</span> : <i>N/A</i>}
                                                </td>
                                            : null}
                                            <td className={pairClass}>
                                                <DownloadableAccession file={file} buttonEnabled={buttonEnabled} clickHandler={meta.fileClick ? meta.fileClick : null} loggedIn={loggedIn} adminUser={adminUser} />
                                            </td>
                                            <td className={pairClass}>{file.file_type}</td>
                                            <td className={pairClass}>{file.output_type}</td>
                                            <td className={pairClass}>{file.assembly}</td>
                                            <td className={pairClass}>{file.lab && file.lab.title ? file.lab.title : null}</td>
                                            <td className={pairClass}>{moment.utc(file.date_created).format('YYYY-MM-DD')}</td>
                                            <td className={pairClass}>{globals.humanFileSize(file.file_size)}</td>
                                            <td className={pairClass}>{fileAuditStatus(file)}</td>
                                            <td className={`${pairClass} characterization-meta-data`}><FileStatusLabel file={file} /></td>
                                        </tr>
                                    );
                                });
                            })}
                            {nonpairedFiles.sort(sortBioReps).map((file, i) => {
                                // Prepare for run_type display
                                const rowClasses = [
                                    pairedKeys.length && i === 0 ? 'table-raw-separator' : null,
                                ];

                                // Determine if accession should be a button or not.
                                const buttonEnabled = !!(meta.graphedFiles && meta.graphedFiles[file['@id']]);

                                return (
                                    <tr key={file['@id']} className={rowClasses.join(' ')}>
                                        <td className="table-raw-biorep">{(file.biological_replicates && file.biological_replicates.length) ? file.biological_replicates.sort((a, b) => a - b).join(', ') : 'N/A'}</td>
                                        <td>{(file.replicate && file.replicate.library) ? file.replicate.library.accession : 'N/A'}</td>
                                        <td>
                                            <DownloadableAccession file={file} buttonEnabled={buttonEnabled} clickHandler={meta.fileClick ? meta.fileClick : null} loggedIn={loggedIn} adminUser={adminUser} />
                                        </td>
                                        <td>{file.file_type}</td>
                                        <td>{file.output_type}</td>
                                        <td>{file.assembly}</td>
                                        <td>{file.lab && file.lab.title ? file.lab.title : null}</td>
                                        <td>{moment.utc(file.date_created).format('YYYY-MM-DD')}</td>
                                        <td>{globals.humanFileSize(file.file_size)}</td>
                                        <td>{fileAuditStatus(file)}</td>
                                        <td className="characterization-meta-data"><FileStatusLabel file={file} /></td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    : null}

                    <tfoot>
                        <tr>
                            <td className={`file-table-footer${this.state.collapsed ? ' hiding' : ''}`} colSpan="11" />
                        </tr>
                    </tfoot>
                </table>
            );
        }

        // No files to display
        return null;
    }
}

RawFileTable.propTypes = {
    files: PropTypes.array, // Raw sequencing files to display
    meta: PropTypes.object, // Extra metadata in the same format passed to SortTable
};


// Called once searches for unreleased files returns results in props.items. Displays both released and
// unreleased files.
export const DatasetFiles = (props) => {
    const { items } = props;

    const files = _.uniq((items && items.length) ? items : []);
    if (files.length) {
        return <FileTable {...props} items={files} />;
    }
    return null;
};

DatasetFiles.propTypes = {
    items: PropTypes.array, // Array of files retrieved
};


// File display widget, showing a facet list, a table, and a graph (and maybe a BioDalliance).
// This component only triggers the data retrieval, which is done with a search for files associated
// with the given experiment (in this.props.context). An odd thing is we specify query-string parameters
// to the experiment URL, but they apply to the file search -- not the experiment itself.
export class FileGallery extends React.Component {
    render() {
        const { context, encodevers, anisogenic, hideGraph, altFilterDefault } = this.props;

        return (
            <FetchedData>
                <Param name="data" url={`/search/?limit=all&type=File&dataset=${context['@id']}`} />
                <Param name="schemas" url="/profiles/" />
                <FileGalleryRenderer context={context} session={this.context.session} encodevers={encodevers} anisogenic={anisogenic} hideGraph={hideGraph} altFilterDefault={altFilterDefault} />
            </FetchedData>
        );
    }
}

FileGallery.propTypes = {
    context: PropTypes.object, // Dataset object whose files we're rendering
    encodevers: PropTypes.string, // ENCODE version number
    anisogenic: PropTypes.bool, // True if anisogenic experiment
    hideGraph: PropTypes.bool, // T to hide graph display
    altFilterDefault: PropTypes.bool, // T to default to All Assemblies and Annotations
};

FileGallery.contextTypes = {
    session: PropTypes.object, // Login information
    location_href: PropTypes.string, // URL of this experiment page, including query string stuff
};


// Given an array of files, make an array of file assemblies and genome annotations to prepare for
// rendering the filtering menu of assemblies and genome annotations. This collects them from all
// files that don't have a "raw data" output_category and that have an assembly. The format of the
// returned array is:
//
// [{assembly: 'assembly1', annotation: 'annotation1'}]
//
// The resulting array has no duplicate entries, nor empty ones. Entries with an assembly but no
// annotation simply have an empty string for the annnotation. The array of assemblies and
// annotations is then sorted with assembly as the primary key and annotation as the secondary.

function collectAssembliesAnnotations(files) {
    let filterOptions = [];

    // Get the assembly and annotation of each file. Assembly is required to be included in the list
    files.forEach((file) => {
        if (file.output_category !== 'raw data' && file.assembly) {
            filterOptions.push({ assembly: file.assembly, annotation: file.genome_annotation });
        }
    });

    // Eliminate duplicate entries in filterOptions. Duplicates are detected by combining the
    // assembly and annotation into a long string. Use the '!' separator so that highly unlikely
    // anomalies don't pass undetected (e.g. hg19!V19 and hg1!9V19 -- again, highly unlikely).
    filterOptions = filterOptions.length ? _(filterOptions).uniq(option => `${option.assembly}!${option.annotation ? option.annotation : ''}`) : [];

    // Now begin a two-stage sort, with the primary key being the assembly in a specific priority
    // order specified by the assemblyPriority array, and the secondary key being the annotation
    // in which we attempt to suss out the ordering from the way it looks, highest-numbered first.
    // First, sort by annotation and reverse the sort at the end.
    filterOptions = _(filterOptions).sortBy((option) => {
        if (option.annotation) {
            // Extract any number from the annotation.
            const annotationMatch = option.annotation.match(/^[A-Z]+(\d+).*$/);
            if (annotationMatch) {
                // Return the number to the sorting algoritm.
                return Number(annotationMatch[1]);
            }
        }

        // No annotation gets sorted to the top.
        return null;
    }).reverse();

    // Now sort by assembly priority order as the primary sorting key. assemblyPriority is a global
    // array.
    return _(filterOptions).sortBy(option => _(globals.assemblyPriority).indexOf(option.assembly));
}


// Displays the file filtering controls for the file association graph and file tables.

class FilterControls extends React.Component {
    constructor() {
        super();

        // Bind this to non-React methods.
        this.handleAssemblyAnnotationChange = this.handleAssemblyAnnotationChange.bind(this);
        this.handleInclusionChange = this.handleInclusionChange.bind(this);
    }

    handleAssemblyAnnotationChange(e) {
        this.props.handleAssemblyAnnotationChange(e.target.value);
    }

    // Called when the switch button is clicked.
    handleInclusionChange() {
        this.props.handleInclusionChange(!this.props.inclusionOn);
    }

    render() {
        const { filterOptions, selectedFilterValue, inclusionOn } = this.props;

        return (
            <div className="file-gallery-controls">
                <div className="file-gallery-controls__assembly-selector">
                    {filterOptions.length ?
                        <FilterMenu selectedFilterValue={selectedFilterValue} filterOptions={filterOptions} handleFilterChange={this.handleAssemblyAnnotationChange} />
                    : null}
                </div>
                <div className="file-gallery-controls__inclusion-selector">
                    <div className="checkbox--right">
                        <label htmlFor="filterIncArchive">Include deprecated files
                            <input name="filterIncArchive" type="checkbox" checked={inclusionOn} onChange={this.handleInclusionChange} />
                        </label>
                    </div>
                </div>
            </div>
        );
    }
}

FilterControls.propTypes = {
    filterOptions: PropTypes.array.isRequired,
    selectedFilterValue: PropTypes.string,
    handleAssemblyAnnotationChange: PropTypes.func.isRequired,
    handleInclusionChange: PropTypes.func.isRequired,
    inclusionOn: PropTypes.bool, // True to make the inclusion box checked
};

FilterControls.defaultProps = {
    selectedFilterValue: '0',
    inclusionOn: false,
};


// Map a QC object to its corresponding two-letter abbreviation for the graph.
function qcAbbr(qc) {
    // As we add more QC object types, add to this object.
    const qcAbbrMap = {
        BigwigcorrelateQualityMetric: 'BC',
        BismarkQualityMetric: 'BK',
        ChipSeqFilterQualityMetric: 'CF',
        ComplexityXcorrQualityMetric: 'CX',
        CorrelationQualityMetric: 'CN',
        CpgCorrelationQualityMetric: 'CC',
        DuplicatesQualityMetric: 'DS',
        EdwbamstatsQualityMetric: 'EB',
        EdwcomparepeaksQualityMetric: 'EP',
        Encode2ChipSeqQualityMetric: 'EC',
        FastqcQualityMetric: 'FQ',
        FilteringQualityMetric: 'FG',
        GenericQualityMetric: 'GN',
        HotspotQualityMetric: 'HS',
        IDRQualityMetric: 'ID',
        IdrSummaryQualityMetric: 'IS',
        MadQualityMetric: 'MD',
        SamtoolsFlagstatsQualityMetric: 'SF',
        SamtoolsStatsQualityMetric: 'SS',
        StarQualityMetric: 'SR',
        TrimmingQualityMetric: 'TG',
    };

    let abbr = qcAbbrMap[qc['@type'][0]];
    if (!abbr) {
        // 'QC' is the generic, unmatched abbreviation if qcAbbrMap doesn't have a match.
        abbr = 'QC';
    }
    return abbr;
}


/**
 * Test whether the given file is compatible with the given assembly and annotation. The file's
 * compatible if it...
 *   * has no assembly
 *   * has an assembly and annotation matching the given ones
 *   * has an assembly matching the given one, and no annotation, nor is there a given one
 *
 * @param {object} file - File whose assembly/annotation we're testing.
 * @param {string} assembly - Currently selected assembly.
 * @param {string} annotation - Currently selected annotation.
 */
function isCompatibleAssemblyAnnotation(file, assembly, annotation) {
    return !file.assembly || (file.assembly === assembly && (file.genome_annotation || '') === annotation);
}


/**
 * Collect qualified derived_from files from a root file. Because derived_from chains can branch
 * and merge, collectDerivedFroms calls itself recursively as it travels up the chains, with
 * progressively higher parent files in `file` for each iterative call. The structure of the
 * returned object describes the entire derived_from chain above the given `file` parameter. This
 * function gets called once for every file that belongs to the current dataset that has an
 * assembly/annotation compatible with the current selection. Here's an example where P1, P2 and
 * P3 are processed files within the current dataset and match the selected assembly and
 * annotation, and R1 and R2 are raw files.
 *
 * R1 ----------- P1
 *              |
 *    +---------+
 *    |
 * R2 ----------- P2 ----------- P3
 *
 * P1 has a derived_from of R1 and R2, P2 has a derived_from of R2 only, and P3 has a derived_from
 * of P2. collectDerivedFroms gets called directly three times (not counting recursive calls) --
 * once each for P1, P2, and P3. Once the dust settles, the result of the call for P1 is
 *
 * { R1@id: null } ---> resulting in { R1@id: P1 }
 *
 * P2
 *
 * { R2@id: null } ---> resulting in { R2@id: P2 }
 *
 * and P3
 *
 * { R2@id: P2, P2@id: null } ---> resulting in { R2@id: P2, P2@id: P3 }
 *
 * You can see that after collectDerivedFroms returns, the processed file puts itself in any null
 * entries in the returned object, which is how the chain gradually gets built, showing what files
 * derive from which.
 *
 * @param {object} file - File to begin the journey up the derived_from chains
 * @param {object} fileDataset - Dataset being displayed
 * @param {string} selectedAssembly - Assembly currently selected for display in the graph
 * @param {string} selectedAnnotation - Genome annotation currently selected for display in the graph
 * @param {object} allFiles - keys are @ids of all files in the current dataset, and the values are
 *         the file objects themselves.
 * @return {object} - Describes the derived_from chaih above the given `file` object. This single-
 *         level object has keys that are the @id of every file that the given `file` directly or
 *         indirectly derives from. Each key's value is the object of the file that directly
 *         derives from it. A file can spawn more than one file, but in that case we'll have
 *         multiple derived_from chains -- within a chain, every file spawns exactly one file.
 *         When this call returns (both when called normally as well as recursively), The given
 *         `file`'s own @id is one key of the returned object, but its value is null, to be filled
 *         when we process the child file.
 */
function collectDerivedFroms(file, fileDataset, selectedAssembly, selectedAnnotation, allFiles) {
    let accumulatedDerivedFroms = {};

    // Only step up the chain of derived froms if the file has one. Otherwise we're at a terminal
    // file of this derived_from branch and can start stepping back down the chain. We also stop
    // going up the chain once we get to a file not in the current dataset, which might be a
    // processed file that doesn't belong in the graph, or a contributing file. Note that we have a
    // risk of infinite recursion if the file data incluees a derived_from loop, which isn't valid.
    if (file.derived_from && file.derived_from.length && file.dataset === fileDataset['@id']) {
        // File is the product of at least one derived_from chain, so for any files this file
        // derives from (parent files), go up the chain continuing to collect the files involved
        // in the current branch of the chain.
        for (let i = 0; i < file.derived_from.length; i += 1) {
            const derivedFileAtId = file.derived_from[i];

            // derived_from doesn't currently embed files; it's just a list of file @ids, and we
            // have to use `allFiles` to get the corresponding file objects.
            const derivedFile = allFiles[derivedFileAtId];
            if (!derivedFile || isCompatibleAssemblyAnnotation(derivedFile, selectedAssembly, selectedAnnotation)) {
                // The derived_from file either has an assembly/annotation compatible with the
                // currently selected ones (including raw files that don't have an assembly nor
                // annotation) -- OR we have the @id of a derived_from file not in this dataset and
                // so doesn't exist in `allFiles`, which indicates a contributing file.
                let branchDerivedFroms;
                if (derivedFile) {
                    // The derived_from file exists in the current dataset, so use that as the new
                    // root of the derived_from chain to recursively go up the chain.
                    branchDerivedFroms = collectDerivedFroms(derivedFile, fileDataset, selectedAssembly, selectedAnnotation, allFiles);
                } else {
                    // The derived_from file does not exist in the current dataset, so this is a
                    // terminal file that gets a clean entry to return to the lower level of the
                    // chain.
                    accumulatedDerivedFroms[derivedFileAtId] = null;
                    branchDerivedFroms = accumulatedDerivedFroms;
                }

                // branchDerivedFroms keys with null values indicate files that are the direct
                // parent of `file`. Replace the null value with `file` itself.
                const branchDerivedFromAtIds = Object.keys(branchDerivedFroms);
                for (let j = 0; j < branchDerivedFromAtIds.length; j += 1) {
                    const oneDerivedFromAtId = branchDerivedFromAtIds[j];
                    if (branchDerivedFroms[oneDerivedFromAtId] === null) {
                        branchDerivedFroms[oneDerivedFromAtId] = file;
                    }
                }

                // Add the current file object to the object that accumulates all the files this
                // file derives from.
                accumulatedDerivedFroms = Object.assign(accumulatedDerivedFroms, branchDerivedFroms);
            }
        }
    }
    // Else the file has no derived_from chain or has a conflicting dataset, and we can stop going
    // up the chain of derived froms.

    // Now add a property to the object of collected derived_froms keyed by the file's @id and
    // containing an null to be filled in by child files.
    accumulatedDerivedFroms[file['@id']] = null;
    return accumulatedDerivedFroms;
}


// Assembly a graph of files, the QC objects that belong to them, and the steps that connect them.
export function assembleGraph(files, dataset, options) {
    // Calculate a step ID from a file's derived_from array.
    function rDerivedFileIds(file) {
        if (file.derived_from && file.derived_from.length) {
            return file.derived_from.sort().join();
        }
        return '';
    }

    // Calculate a QC node ID.
    function rGenQcId(metric, file) {
        return `qc:${metric['@id'] + file['@id']}`;
    }

    /**
     * Generate a string of CSS classes for a file node. Plass the result into a `className` property of a component.
     *
     * @param {object-required} file - File we're generating the statuses for.
     * @param {bool} active - True if the file is active and should be highlighted as such.
     * @param (bool) colorize - True to colorize the nodes according to their status by adding a CSS class for their status
     * @param {string} addClasses - CSS classes to add in addition to the ones generated by the file statuses.
     */
    function fileCssClassGen(file, active, colorizeNode, addClasses) {
        let statusClass;
        if (colorizeNode) {
            statusClass = file.status.replace(/ /g, '-');
        }
        return `pipeline-node-file${active ? ' active' : ''}${colorizeNode ? ` ${statusClass}` : ''}${addClasses ? ` ${addClasses}` : ''}`;
    }

    const { infoNode, selectedAssembly, selectedAnnotation, colorize } = options;
    const derivedFileIds = _.memoize(rDerivedFileIds, file => file['@id']);
    const genQcId = _.memoize(rGenQcId, (metric, file) => metric['@id'] + file['@id']);

    // Begin collecting up information about the files from the search result, and gathering their
    // QC and analysis pipeline information.
    const allFiles = {}; // All searched files, keyed by file @id
    let matchingFiles = {}; // All files that match the current assembly/annotation, keyed by file @id
    const fileQcMetrics = {}; // List of all file QC metrics indexed by file @id
    const allPipelines = {}; // List of all pipelines indexed by step @id
    files.forEach((file) => {
        // allFiles gets all files from search regardless of filtering.
        allFiles[file['@id']] = file;

        // matchingFiles gets just the files matching the given filtering assembly/annotation.
        // Note that if all assemblies and annotations are selected, this function isn't called
        // because no graph gets displayed in that case.
        if ((file.assembly === selectedAssembly) && ((!file.genome_annotation && !selectedAnnotation) || (file.genome_annotation === selectedAnnotation))) {
            // Note whether any files have an analysis step
            const fileAnalysisStep = file.analysis_step_version && file.analysis_step_version.analysis_step;
            if (!fileAnalysisStep || (file.derived_from && file.derived_from.length)) {
                // File has no analysis step or derives from other files, so it can be included in
                // the graph.
                matchingFiles[file['@id']] = file;

                // Collect any QC info that applies to this file and make it searchable by file
                // @id.
                if (file.quality_metrics && file.quality_metrics.length) {
                    fileQcMetrics[file['@id']] = file.quality_metrics;
                }

                // Save the pipeline array used for each step used by the file.
                if (fileAnalysisStep) {
                    allPipelines[fileAnalysisStep['@id']] = fileAnalysisStep.pipelines;
                }
            } // else file has analysis step but no derived from -- can't include in graph.
        }
    });

    // For each matching file (file belonging to this dataset with an assembly/annotation matching
    // the selected one), build an object describing the derived_from chains leading to this file.
    // A detailed description is in the comments for collectDerivedFroms. Place the result in
    // `derivedChains` which the next step uses to build allDerivedFroms.
    const derivedChains = {};
    let matchingFileAtIds = Object.keys(matchingFiles);
    for (let i = 0; i < matchingFileAtIds.length; i += 1) {
        const fileAtId = matchingFileAtIds[i];
        derivedChains[fileAtId] = collectDerivedFroms(matchingFiles[fileAtId], dataset, selectedAssembly, selectedAnnotation, allFiles);
    }

    // Generate a list of file @ids that other files matching the current assembly and annotation
    // derive from (i.e. files referenced in other files' derived_from). allDerivedFroms is keyed
    // by the derived_from file @id (whether it matches the current assembly and annotation or not)
    // and has a value of the array of all files that derive from it. So for example:
    //
    // allDerivedFroms = {
    //     /files/<matching accession>: [matching file, matching file],
    //     /files/<contributing accession>: [matching file, matching file],
    //     /files/<missing accession>: [matching file, matching file],
    // }
    //
    // Also generate `derivedFromList` which is just a convenience object. It contains the @ids of
    // all files in allDerivedFroms, but with a value of the corresponding file object.
    // `derivedFromList` isn't core to the graph-generating algorithm, but helps us avoid having
    // to search arrays for file objects.
    //
    // You can think of this nested loop turning `derivedChains` upside-down because it has the
    // @ids of processed files as keys with files they derived from as values. allDerivedFroms is
    // keyed by all file @ids that have other files derive from them, and an array of all files
    // that derive from each one as values.
    const allDerivedFroms = {};
    const derivedFromList = {};
    matchingFileAtIds = Object.keys(derivedChains);
    for (let i = 0; i < matchingFileAtIds.length; i += 1) {
        const matchingFileAtId = matchingFileAtIds[i];
        const matchingFileChain = derivedChains[matchingFileAtId];

        // For each matching file @id in derivedChains, go through its chain of parents to fill in
        // allDerivedFroms.
        const parentFileAtIds = Object.keys(matchingFileChain);
        for (let j = 0; j < parentFileAtIds.length; j += 1) {
            const parentFileAtId = parentFileAtIds[j];
            if (matchingFileChain[parentFileAtId]) {
                if (allDerivedFroms[parentFileAtId] && allDerivedFroms[parentFileAtId].findIndex(childFile => childFile['@id'] === matchingFileChain[parentFileAtId]['@id']) === -1) {
                    // We've already put this file @id in allDerivedFromss, so add this new parent file to its array.
                    allDerivedFroms[parentFileAtId].push(matchingFileChain[parentFileAtId]);
                } else {
                    // We've never seen this file @id in allDerivedFroms, os start a new array.
                    allDerivedFroms[parentFileAtId] = [matchingFileChain[parentFileAtId]];
                }
                derivedFromList[parentFileAtId] = allFiles[parentFileAtId];
            }
        }
    }
    // Remember, at this stage allDerivedFroms includes keys for missing files, files not matching
    // the chosen assembly/annotation, and contributing files.

    // Add the derivedFromList to matchingFiles so that the rendering code renders them all
    // together. This is a major change made for ENCD-3661 which used to render this all
    // `allDerivedFroms` separately. Now they're all rendered together, an no separate rendering
    // step for derived froms exists anymore.
    matchingFiles = Object.assign(matchingFiles, derivedFromList);

    // Filter any "island" files out of matchingFiles -- that is, files that derive from no other
    // files, and no other files derive from it.
    matchingFiles = (function matchingFilesFunc() {
        const noIslandFiles = {};
        Object.keys(matchingFiles).forEach((matchingFileId) => {
            const matchingFile = matchingFiles[matchingFileId];
            const hasDerivedFroms = matchingFile && matchingFile.derived_from && matchingFile.derived_from.length &&
                matchingFile.derived_from.some(derivedFileAtId => derivedFileAtId in derivedFromList);
            if (hasDerivedFroms || allDerivedFroms[matchingFileId]) {
                // This file either has derived_from set, or other files derive from it. Copy it to
                // our destination object.
                noIslandFiles[matchingFileId] = matchingFile;
            }
        });
        return noIslandFiles;
    }());
    if (Object.keys(matchingFiles).length === 0) {
        throw new GraphException('No graph: no file relationships for the selected assembly/annotation');
    }
    // At this stage, any files in matchingFiles will be rendered.

    const allReplicates = {}; // All file's replicates as keys; each key references an array of files
    Object.keys(matchingFiles).forEach((matchingFileId) => {
        // If the file is part of a single biological replicate, add it to an array of files, where
        // the arrays are in an object keyed by their relevant biological replicate number.
        const matchingFile = matchingFiles[matchingFileId];
        const replicateNum = (matchingFile && matchingFile.biological_replicates && matchingFile.biological_replicates.length === 1) ? matchingFile.biological_replicates[0] : undefined;
        if (replicateNum) {
            if (allReplicates[replicateNum]) {
                allReplicates[replicateNum].push(matchingFile);
            } else {
                allReplicates[replicateNum] = [matchingFile];
            }
        }
    });

    // Make a list of contributing files that matchingFiles files derive from.
    const usedContributingFiles = {};
    if (dataset.contributing_files && dataset.contributing_files.length) {
        dataset.contributing_files.forEach((contributingFileAtId) => {
            if (contributingFileAtId in allDerivedFroms) {
                usedContributingFiles[contributingFileAtId] = allDerivedFroms[contributingFileAtId];
            }
        });
    }

    // Go through each used contributing file and set a property within it showing which files
    // derive from it. We'll need that for coalescing contributing files.
    const allCoalesced = {};
    let coalescingGroups = {};
    if (Object.keys(usedContributingFiles).length) {
        // Now use the derivedFiles property of every contributing file to group them into potential
        // coalescing nodes. `coalescingGroups` gets assigned an object keyed by dataset file ids
        // hashed to a stringified 32-bit integer, and mapped to an array of contributing files they
        // derive from.
        coalescingGroups = _(Object.keys(usedContributingFiles)).groupBy((contributingFileAtId) => {
            const derivedFiles = usedContributingFiles[contributingFileAtId];
            return globals.hashCode(derivedFiles.map(derivedFile => derivedFile['@id']).join(',')).toString();
        });

        // Set a `coalescingGroup` property in each contributing file with its coalescing group's hash
        // value. That'll be important when we add step nodes.
        const coalescingGroupKeys = Object.keys(coalescingGroups);
        if (coalescingGroupKeys && coalescingGroupKeys.length) {
            coalescingGroupKeys.forEach((groupHash) => {
                const group = coalescingGroups[groupHash];
                if (group.length >= MINIMUM_COALESCE_COUNT) {
                    // Number of files in the coalescing group is at least the minimum number of files we
                    // allow in a coalescing group. Mark every contributing file in the group with the
                    // group's hash value in a `coalescingGroup` property that step node can connnect to.
                    group.forEach((contributingFileAtId) => {
                        allCoalesced[contributingFileAtId] = groupHash;

                        // Remove coalesced files from usedContributingFiles because we don't want
                        // to render individual files that have been coalesced.
                        delete usedContributingFiles[contributingFileAtId];
                        delete matchingFiles[contributingFileAtId];
                    });
                } else {
                    // The number of contributing files in a coalescing group isn't above our
                    // threshold. Don't use this coalescingGroup anymore and just render them the
                    // same as normal files.
                    delete coalescingGroups[groupHash];
                }
            });
        }
    }

    // See if we have any derived_from files that we have no information on, likely because they're
    // not released and we're not logged in. We'll render them with information-less dummy nodes.
    const allMissingFiles = [];
    Object.keys(allDerivedFroms).forEach((derivedFromFileAtId) => {
        if (!allFiles[derivedFromFileAtId] && !allCoalesced[derivedFromFileAtId]) {
            // The derived-from file isn't in our dataset file list, nor in coalesced contributing
            // files. Now see if it's in non-coalesced contributing files.
            if (!usedContributingFiles[derivedFromFileAtId]) {
                allMissingFiles.push(derivedFromFileAtId);
            }
        }
    });

    // See if anything in `allDerivedFroms` has its own derived_from. If it does, then treat it
    // like any other file with `derived_from` set. Add it to `matchingFiles` and remove it from
    // `allDerivedFroms`.

    // Create an empty graph architecture that we fill in next.
    const jsonGraph = new JsonGraph(dataset.accession);

    // Create nodes for the replicates.
    Object.keys(allReplicates).forEach((replicateNum) => {
        if (allReplicates[replicateNum] && allReplicates[replicateNum].length) {
            jsonGraph.addNode(`rep:${replicateNum}`, `Replicate ${replicateNum}`, {
                cssClass: 'pipeline-replicate',
                type: 'Rep',
                shape: 'rect',
                cornerRadius: 0,
            });
        }
    });

    // Go through each file matching the currently selected assembly/annotation and add it to our
    // graph.
    Object.keys(matchingFiles).forEach((fileId) => {
        const file = matchingFiles[fileId];

        if (!file) {
            if (allMissingFiles.indexOf(fileId) === -1) {
                const fileNodeId = `file:${fileId}`;
                const fileNodeLabel = `${globals.atIdToAccession(fileId)}`;
                const fileCssClass = `pipeline-node-file contributing${infoNode === fileNodeId ? ' active' : ''}`;

                jsonGraph.addNode(fileNodeId, fileNodeLabel, {
                    cssClass: fileCssClass,
                    type: 'File',
                    shape: 'rect',
                    cornerRadius: 16,
                    contributing: fileId,
                    ref: {},
                });
            }
        } else {
            const fileNodeId = `file:${file['@id']}`;
            const fileNodeLabel = `${file.title} (${file.output_type})`;
            const fileCssClass = fileCssClassGen(file, !!(infoNode && infoNode.id === fileNodeId), colorize);
            const fileRef = file;
            const replicateNode = (file.biological_replicates && file.biological_replicates.length === 1) ? jsonGraph.getNode(`rep:${file.biological_replicates[0]}`) : null;
            let metricsInfo;

            // Add QC metrics info from the file to the list to generate the nodes later.
            if (fileQcMetrics[fileId] && fileQcMetrics[fileId].length) {
                const sortedMetrics = fileQcMetrics[fileId].sort((a, b) => (a['@type'][0] > b['@type'][0] ? 1 : (a['@type'][0] < b['@type'][0] ? -1 : 0)));
                metricsInfo = sortedMetrics.map((metric) => {
                    const qcId = genQcId(metric, file);
                    return {
                        id: qcId,
                        label: qcAbbr(metric),
                        '@type': ['QualityMetric'],
                        class: `pipeline-node-qc-metric${infoNode && infoNode.id === qcId ? ' active' : ''}`,
                        tooltip: true,
                        ref: metric,
                        parent: file,
                    };
                });
            }

            // Add a node for a regular searched file.
            jsonGraph.addNode(fileNodeId, fileNodeLabel, {
                cssClass: fileCssClass,
                type: 'File',
                shape: 'rect',
                cornerRadius: 16,
                parentNode: replicateNode,
                ref: fileRef,
            }, metricsInfo);

            // Figure out the analysis step we need to render between the node we just rendered and its
            // derived_from.
            let stepId;
            let label;
            let pipelineInfo;
            let error;
            const fileAnalysisStep = file.analysis_step_version && file.analysis_step_version.analysis_step;
            if (fileAnalysisStep) {
                // Make an ID and label for the step
                stepId = `step:${derivedFileIds(file) + fileAnalysisStep['@id']}`;
                label = fileAnalysisStep.analysis_step_types;
                pipelineInfo = allPipelines[fileAnalysisStep['@id']];
                error = false;
            } else if (derivedFileIds(file)) {
                // File derives from others, but no analysis step; make dummy step.
                stepId = `error:${derivedFileIds(file)}`;
                label = 'Software unknown';
                pipelineInfo = null;
                error = true;
            } else {
                // No analysis step and no derived_from; don't add a step.
                stepId = '';
            }

            // If we have a step to render, do that here.
            if (stepId) {
                // Add the step to the graph only if we haven't for this derived-from set already
                if (!jsonGraph.getNode(stepId)) {
                    jsonGraph.addNode(stepId, label, {
                        cssClass: `pipeline-node-analysis-step${(infoNode && infoNode.id === stepId ? ' active' : '') + (error ? ' error' : '')}`,
                        type: 'Step',
                        shape: 'rect',
                        cornerRadius: 4,
                        parentNode: replicateNode,
                        ref: fileAnalysisStep,
                        pipelines: pipelineInfo,
                        fileId: file['@id'],
                        fileAccession: file.title,
                        stepVersion: file.analysis_step_version,
                    });
                }

                // Connect the file to the step, and the step to the derived_from files
                jsonGraph.addEdge(stepId, fileNodeId);
                file.derived_from.forEach((derivedFromAtId) => {
                    if (!allDerivedFroms[derivedFromAtId]) {
                        return;
                    }
                    const derivedFromFile = allFiles[derivedFromAtId] || allMissingFiles.some(missingFileId => missingFileId === derivedFromAtId);
                    if (derivedFromFile) {
                        // Not derived from a contributing file; just add edges normally.
                        const derivedFileId = `file:${derivedFromAtId}`;
                        if (!jsonGraph.getEdge(derivedFileId, stepId)) {
                            jsonGraph.addEdge(derivedFileId, stepId);
                        }
                    } else {
                        // File derived from a contributing file; add edges to a coalesced node
                        // that we'll add to the graph later.
                        const coalescedContributing = allCoalesced[derivedFromAtId];
                        if (coalescedContributing) {
                            // Rendering a coalesced contributing file.
                            const derivedFileId = `coalesced:${coalescedContributing}`;
                            if (!jsonGraph.getEdge(derivedFileId, stepId)) {
                                jsonGraph.addEdge(derivedFileId, stepId);
                            }
                        } else if (usedContributingFiles[derivedFromAtId]) {
                            const derivedFileId = `file:${derivedFromAtId}`;
                            if (!jsonGraph.getEdge(derivedFileId, stepId)) {
                                jsonGraph.addEdge(derivedFileId, stepId);
                            }
                        }
                    }
                });
            }
        }
    });

    // Now add coalesced nodes to the graph.
    Object.keys(coalescingGroups).forEach((groupHash) => {
        const coalescingGroup = coalescingGroups[groupHash];
        if (coalescingGroup.length) {
            const fileNodeId = `coalesced:${groupHash}`;
            const fileCssClass = `pipeline-node-file contributing${infoNode === fileNodeId ? ' active' : ''}`;
            jsonGraph.addNode(fileNodeId, `${coalescingGroup.length} contributing files`, {
                cssClass: fileCssClass,
                type: 'Coalesced',
                shape: 'stack',
                cornerRadius: 16,
                contributing: groupHash,
                ref: coalescingGroup,
            });
        }
    });

    // Add missing-file nodes to the graph.
    allMissingFiles.forEach((missingFileAtId) => {
        const fileNodeAccession = globals.atIdToAccession(missingFileAtId);
        const fileNodeId = `file:${missingFileAtId}`;
        const fileNodeLabel = `${fileNodeAccession} (unknown)`;
        const fileCssClass = 'pipeline-node-file error';

        jsonGraph.addNode(fileNodeId, fileNodeLabel, {
            cssClass: fileCssClass,
            type: 'File',
            shape: 'rect',
            cornerRadius: 16,
        });
    });

    return jsonGraph;
}


const FileGraph = (props) => {
    const { files, dataset, infoNode, selectedAssembly, selectedAnnotation, colorize, handleNodeClick, schemas } = props;

    // Build node graph of the files and analysis steps with this experiment
    let graph;
    if (files.length) {
        try {
            graph = assembleGraph(
                files,
                dataset,
                {
                    infoNode,
                    selectedAssembly,
                    selectedAnnotation,
                    colorize,
                }
            );
        } catch (e) {
            console.warn(e.message + (e.file0 ? ` -- file0:${e.file0}` : '') + (e.file1 ? ` -- file1:${e.file1}` : ''));
        }
    }

    // Build node graph of the files and analysis steps with this experiment
    if (graph) {
        return (
            <Graph
                graph={graph}
                nodeClickHandler={handleNodeClick}
                schemas={schemas}
                colorize={colorize}
                auditIndicators={props.auditIndicators}
                auditDetail={props.auditDetail}
            />
        );
    }
    return <p className="browser-error">Graph not applicable.</p>;
};

FileGraph.propTypes = {
    files: PropTypes.array.isRequired, // Array of files we're graphing
    dataset: PropTypes.object.isRequired, // dataset these files are being rendered into
    selectedAssembly: PropTypes.string, // Currently selected assembly
    selectedAnnotation: PropTypes.string, // Currently selected annotation
    infoNode: PropTypes.object, // Currently highlighted node
    schemas: PropTypes.object, // Schemas for QC metrics
    handleNodeClick: PropTypes.func.isRequired, // Parent function to call when a graph node is clicked
    colorize: PropTypes.bool, // True to enable node colorization based on status
    auditIndicators: PropTypes.func, // Inherited from auditDecor HOC
    auditDetail: PropTypes.func, // Inherited from auditDecor HOC
};

FileGraph.defaultProps = {
    selectedAssembly: '',
    selectedAnnotation: '',
    infoNode: null,
    schemas: null,
    colorize: false,
    auditIndicators: null,
    auditDetail: null,
};


// Function to render the file gallery, and it gets called after the file search results (for files associated with
// the displayed experiment) return.

class FileGalleryRendererComponent extends React.Component {
    constructor(props, context) {
        super(props, context);

        // Determine if the user's logged in as admin.
        const loggedIn = !!(context.session && context.session['auth.userid']);
        const adminUser = loggedIn && !!(context.session_properties && context.session_properties.admin);

        // Initialize React state variables.
        this.state = {
            selectedFilterValue: 'default', // <select> value of selected filter
            meta: null, // @id of node whose info panel is open
            infoModalOpen: false, // True if info modal is open
            relatedFiles: [],
            inclusionOn: adminUser, // True to exclude files with certain statuses
            contributingFiles: [], // Cache for contributing files retrieved from the DB
        };

        // Bind `this` to non-React methods.
        this.setInfoNodeId = this.setInfoNodeId.bind(this);
        this.setInfoNodeVisible = this.setInfoNodeVisible.bind(this);
        this.setFilter = this.setFilter.bind(this);
        this.handleAssemblyAnnotationChange = this.handleAssemblyAnnotationChange.bind(this);
        this.handleInclusionChange = this.handleInclusionChange.bind(this);
        this.filterForInclusion = this.filterForInclusion.bind(this);
        this.closeModal = this.closeModal.bind(this);
        this.handleNodeClick = this.handleNodeClick.bind(this);
    }

    componentWillMount() {
        const { context, data } = this.props;
        const relatedFileIds = context.related_files && context.related_files.length ? context.related_files : [];
        if (relatedFileIds.length) {
            const searchedFiles = data ? data['@graph'] : []; // Array of searched files arrives in data.@graph result
            requestFiles(relatedFileIds, searchedFiles).then((relatedFiles) => {
                this.setState({ relatedFiles });
            });
        }
    }

    // Set the default filter after the graph has been analyzed once.
    componentDidMount() {
        if (!this.props.altFilterDefault) {
            this.setFilter('0');
        }
    }

    componentDidUpdate() {
        const { context, data } = this.props;
        const relatedFileIds = context.related_files && context.related_files.length ? context.related_files : [];
        if (relatedFileIds.length) {
            const searchedFiles = data ? data['@graph'] : []; // Array of searched files arrives in data.@graph result
            requestFiles(relatedFileIds, searchedFiles).then((relatedFiles) => {
                if (relatedFiles.length !== this.state.relatedFiles.length) {
                    this.setState({ relatedFiles });
                }
            });
        }
    }

    // Called from child components when the selected node changes.
    setInfoNodeId(node) {
        this.setState({ infoNode: node });
    }

    setInfoNodeVisible(visible) {
        this.setState({ infoNodeVisible: visible });
    }

    // Set the graph filter based on the given <option> value
    setFilter(value) {
        this.setState({ selectedFilterValue: value });
    }

    // React to a filter menu selection. The synthetic event given in `e`
    handleAssemblyAnnotationChange(value) {
        this.setFilter(value);
    }

    // When the exclusion filter changes from typcially the user clicking the checkbox in
    // <FilterControls>,
    handleInclusionChange(checked) {
        this.setState({ inclusionOn: checked });
    }

    // If the inclusionOn state property is enabled, we'll just display all the files we got. If
    // inclusionOn is disabled, we filter out any files with states in
    // FileGalleryRenderer.inclusionStatuses.
    filterForInclusion(files) {
        if (!this.state.inclusionOn) {
            // The user has chosen to not see file swith statuses in
            // FileGalleryRenderer.inclusionStatuses. Create an array with files having those
            // statuses filtered out. Start by making an array of files with a filtered-out status
            return files.filter(file => FileGalleryRendererComponent.inclusionStatuses.indexOf(file.status) === -1);
        }

        // The user requested seeing everything including revoked and archived files, so just
        // return the unmodified array.
        return files;
    }

    // Handle a click in a graph node. This also handles clicks on the info button of files in the
    // file table.
    handleNodeClick(meta) {
        this.setInfoNodeId(meta);
        this.setInfoNodeVisible(true);
    }

    closeModal() {
        // Called when user wants to close modal somehow
        this.setInfoNodeVisible(false);
    }

    render() {
        const { context, data, schemas, hideGraph } = this.props;
        let selectedAssembly = '';
        let selectedAnnotation = '';
        let allGraphedFiles;
        let meta;
        const files = (data ? data['@graph'] : []).concat(this.state.relatedFiles); // Array of searched files arrives in data.@graph result
        if (files.length === 0) {
            return null;
        }

        const filterOptions = files.length ? collectAssembliesAnnotations(files) : [];

        if (this.state.selectedFilterValue && filterOptions[this.state.selectedFilterValue]) {
            selectedAssembly = filterOptions[this.state.selectedFilterValue].assembly;
            selectedAnnotation = filterOptions[this.state.selectedFilterValue].annotation;
        }

        // Get a list of files for the graph (filters out excluded files if requested by the user).
        const includedFiles = this.filterForInclusion(files);

        const fileTable = (
            <FileTable
                {...this.props}
                items={includedFiles}
                selectedFilterValue={this.state.selectedFilterValue}
                filterOptions={filterOptions}
                graphedFiles={allGraphedFiles}
                handleFilterChange={this.handleFilterChange}
                encodevers={globals.encodeVersion(context)}
                session={this.context.session}
                infoNodeId={this.state.infoNode}
                setInfoNodeId={this.setInfoNodeId}
                infoNodeVisible={this.state.infoNodeVisible}
                setInfoNodeVisible={this.setInfoNodeVisible}
                showFileCount
                noDefaultClasses
                adminUser={!!(this.context.session_properties && this.context.session_properties.admin)}
            />
        );

        if (this.state.infoNode) {
            meta = globals.graphDetail.lookup(this.state.infoNode)(this.state.infoNode, this.handleNodeClick, this.props.auditIndicators, this.props.auditDetail, this.context.session, this.context.sessionProperties);
        }

        // Prepare to display the file information modal.
        const modalTypeMap = {
            File: 'file',
            Step: 'analysis-step',
            QualityMetric: 'quality-metric',
        };
        const modalClass = meta ? `graph-modal-${modalTypeMap[meta.type]}` : '';

        return (
            <Panel>
                <PanelHeading addClasses="file-gallery-heading">
                    <h4>Files</h4>
                    <div className="file-gallery-visualize">
                        {context.visualize ?
                            <BrowserSelector visualizeCfg={context.visualize} />
                        : null}
                    </div>
                </PanelHeading>

                {/* Display the strip of filgering controls */}
                <FilterControls
                    selectedFilterValue={this.state.selectedFilterValue}
                    filterOptions={filterOptions}
                    inclusionOn={this.state.inclusionOn}
                    handleAssemblyAnnotationChange={this.handleAssemblyAnnotationChange}
                    handleInclusionChange={this.handleInclusionChange}
                />

                {!hideGraph ?
                    <TabPanel tabs={{ graph: 'Association graph', tables: 'File details' }}>
                        <TabPanelPane key="graph">
                            <FileGraph
                                dataset={context}
                                files={includedFiles}
                                infoNode={this.state.infoNode}
                                selectedAssembly={selectedAssembly}
                                selectedAnnotation={selectedAnnotation}
                                schemas={schemas}
                                colorize={this.state.inclusionOn}
                                handleNodeClick={this.handleNodeClick}
                                auditIndicators={this.props.auditIndicators}
                                auditDetail={this.props.auditDetail}
                            />
                        </TabPanelPane>

                        <TabPanelPane key="tables">
                            {/* If logged in and dataset is released, need to combine search of files that reference
                                this dataset to get released and unreleased ones. If not logged in, then just get
                                files from dataset.files */}
                            {fileTable}
                        </TabPanelPane>
                    </TabPanel>
                :
                    <div>{fileTable}</div>
                }

                {meta && this.state.infoNodeVisible ?
                    <Modal closeModal={this.closeModal}>
                        <ModalHeader closeModal={this.closeModal} addCss={modalClass}>
                            {meta.header}
                        </ModalHeader>
                        <ModalBody>
                            {meta.body}
                        </ModalBody>
                        <ModalFooter closeModal={<button className="btn btn-info" onClick={this.closeModal}>Close</button>} />
                    </Modal>
                : null}
            </Panel>
        );
    }
}

// Keeps a list of file statuses to include or exclude based on the checkbox in FilterControls.
FileGalleryRendererComponent.inclusionStatuses = [
    'archived',
    'revoked',
    'deleted',
    'replaced',
];

FileGalleryRendererComponent.propTypes = {
    context: PropTypes.object, // Dataset whose files we're rendering
    data: PropTypes.object, // File data retrieved from search request
    schemas: PropTypes.object, // Schemas for the entire system; used for QC property titles
    hideGraph: PropTypes.bool, // T to hide graph display
    altFilterDefault: PropTypes.bool, // T to default to All Assemblies and Annotations
    auditIndicators: PropTypes.func, // Inherited from auditDecor HOC
    auditDetail: PropTypes.func, // Inherited from auditDecor HOC
};

FileGalleryRendererComponent.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
    location_href: PropTypes.string,
};

const FileGalleryRenderer = auditDecor(FileGalleryRendererComponent);


const CollapsingTitle = (props) => {
    const { title, handleCollapse, collapsed } = props;
    return (
        <div className="collapsing-title">
            <button className="collapsing-title-trigger pull-left" data-trigger onClick={handleCollapse}>{collapseIcon(collapsed, 'collapsing-title-icon')}</button>
            <h4>{title}</h4>
        </div>
    );
};

CollapsingTitle.propTypes = {
    title: PropTypes.string.isRequired, // Title to display in the title bar
    handleCollapse: PropTypes.func.isRequired, // Function to call to handle click in collapse button
    collapsed: PropTypes.bool, // T if the panel this is over has been collapsed
};


// Display a filtering <select>. `filterOptions` is an array of objects with two properties:
// `assembly` and `annotation`. Both are strings that get concatenated to form each menu item. The
// value of each <option> is its zero-based index.
const FilterMenu = (props) => {
    const { filterOptions, handleFilterChange, selectedFilterValue } = props;

    return (
        <select className="form-control--select" value={selectedFilterValue} onChange={handleFilterChange}>
            <option value="default">All Assemblies and Annotations</option>
            <option disabled="disabled" />
            {filterOptions.map((option, i) =>
                <option key={`${option.assembly}${option.annotation}`} value={i}>{`${option.assembly + (option.annotation ? ` ${option.annotation}` : '')}`}</option>,
            )}
        </select>
    );
};

FilterMenu.propTypes = {
    selectedFilterValue: PropTypes.string, // Currently selected filter
    filterOptions: PropTypes.array.isRequired, // Contents of the filtering menu
    handleFilterChange: PropTypes.func.isRequired, // Call when a filtering option changes
};


// Display a QC button in the file modal.
class FileQCButton extends React.Component {
    constructor() {
        super();

        // Bind `this` to non-React methods.
        this.handleClick = this.handleClick.bind(this);
    }

    handleClick() {
        const node = {
            '@type': ['QualityMetric'],
            parent: this.props.file,
            ref: this.props.qc,
            schemas: this.props.schemas,
        };
        this.props.handleClick(node);
    }

    render() {
        const qcName = qcIdToDisplay(this.props.qc);
        if (qcName) {
            return <button className="file-qc-btn" onClick={this.handleClick}>{qcName}</button>;
        }
        return null;
    }
}

FileQCButton.propTypes = {
    qc: PropTypes.object.isRequired, // QC object we're directing to
    file: PropTypes.object.isRequired, // File this QC object is attached to
    schemas: PropTypes.object.isRequired, // All schemas from /profiles
    handleClick: PropTypes.func.isRequired, // Function to open a modal to the given object
};


// Display the metadata of the selected file in the graph
const FileDetailView = function FileDetailView(node, qcClick, auditIndicators, auditDetail, session, sessionProperties) {
    // The node is for a file
    const selectedFile = node.metadata.ref;
    let body = null;
    let header = null;
    const loggedIn = !!(session && session['auth.userid']);
    const adminUser = !!(sessionProperties && sessionProperties.admin);

    if (selectedFile && Object.keys(selectedFile).length) {
        let contributingAccession;

        if (node.metadata.contributing) {
            const accessionStart = selectedFile.dataset.indexOf('/', 1) + 1;
            const accessionEnd = selectedFile.dataset.indexOf('/', accessionStart) - accessionStart;
            contributingAccession = selectedFile.dataset.substr(accessionStart, accessionEnd);
        }
        const dateString = !!selectedFile.date_created && moment.utc(selectedFile.date_created).format('YYYY-MM-DD');
        header = (
            <div className="details-view-info">
                <h4>{selectedFile.file_type} <a href={selectedFile['@id']}>{selectedFile.title}</a></h4>
            </div>
        );

        body = (
            <div>
                <dl className="key-value">
                    <div data-test="status">
                        <dt>Status</dt>
                        <dd><FileStatusLabel file={selectedFile} /></dd>
                    </div>

                    {selectedFile.output_type ?
                        <div data-test="output">
                            <dt>Output</dt>
                            <dd>{selectedFile.output_type}</dd>
                        </div>
                    : null}

                    {selectedFile.paired_end ?
                        <div data-test="pairedend">
                            <dt>Paired end</dt>
                            <dd>{selectedFile.paired_end}</dd>
                        </div>
                    : null}

                    {selectedFile.biological_replicates && selectedFile.biological_replicates.length ?
                        <div data-test="bioreplicate">
                            <dt>Biological replicate(s)</dt>
                            <dd>{`[${selectedFile.biological_replicates.join(',')}]`}</dd>
                        </div>
                    : null}

                    {selectedFile.biological_replicates && selectedFile.biological_replicates.length ?
                        <div data-test="techreplicate">
                            <dt>Technical replicate(s)</dt>
                            <dd>{`[${selectedFile.technical_replicates.join(',')}]`}</dd>
                        </div>
                    : null}

                    {selectedFile.mapped_read_length !== undefined ?
                        <div data-test="mappedreadlength">
                            <dt>Mapped read length</dt>
                            <dd>{selectedFile.mapped_read_length}</dd>
                        </div>
                    : null}

                    {selectedFile.assembly ?
                        <div data-test="assembly">
                            <dt>Mapping assembly</dt>
                            <dd>{selectedFile.assembly}</dd>
                        </div>
                    : null}

                    {selectedFile.genome_annotation ?
                        <div data-test="annotation">
                            <dt>Genome annotation</dt>
                            <dd>{selectedFile.genome_annotation}</dd>
                        </div>
                    : null}

                    {selectedFile.lab && selectedFile.lab.title ?
                        <div data-test="submitted">
                            <dt>Lab</dt>
                            <dd>{selectedFile.lab.title}</dd>
                        </div>
                    : null}

                    {dateString ?
                        <div data-test="datecreated">
                            <dt>Date added</dt>
                            <dd>{dateString}</dd>
                        </div>
                    : null}

                    {selectedFile.analysis_step_version ?
                        <div data-test="software">
                            <dt>Software</dt>
                            <dd>{softwareVersionList(selectedFile.analysis_step_version.software_versions)}</dd>
                        </div>
                    : null}

                    {node.metadata.contributing && selectedFile.dataset ?
                        <div data-test="contributedfrom">
                            <dt>Contributed from</dt>
                            <dd><a href={selectedFile.dataset}>{contributingAccession}</a></dd>
                        </div>
                    : null}

                    {selectedFile.file_size ?
                        <div data-test="filesize">
                            <dt>File size</dt>
                            <dd>{globals.humanFileSize(selectedFile.file_size)}</dd>
                        </div>
                    : null}

                    {selectedFile.run_type ?
                        <div data-test="runtype">
                            <dt>Run type</dt>
                            <dd>
                                {selectedFile.run_type}
                                {selectedFile.read_length ? <span>{` ${selectedFile.read_length + selectedFile.read_length_units}`}</span> : null}
                            </dd>
                        </div>
                    : null}

                    {selectedFile.replicate && selectedFile.replicate.library ?
                        <div data-test="library">
                            <dt>Library</dt>
                            <dd>{selectedFile.replicate.library.accession}</dd>
                        </div>
                    : null}

                    {selectedFile.href ?
                        <div data-test="download">
                            <dt>File download</dt>
                            <dd><DownloadableAccession file={selectedFile} loggedIn={loggedIn} adminUser={adminUser} /></dd>
                        </div>
                    : null}

                    {selectedFile.quality_metrics && selectedFile.quality_metrics.length && typeof selectedFile.quality_metrics[0] !== 'string' ?
                        <div data-test="fileqc">
                            <dt>File quality metrics</dt>
                            <dd className="file-qc-buttons">
                                {selectedFile.quality_metrics.map(qc =>
                                    <FileQCButton key={qc['@id']} qc={qc} file={selectedFile} schemas={node.schemas} handleClick={qcClick} />,
                                )}
                            </dd>
                        </div>
                    : null}
                </dl>

                {auditsDisplayed(selectedFile.audit, session) ?
                    <div className="row graph-modal-audits">
                        <div className="col-xs-12">
                            <h5>File audits:</h5>
                            {auditIndicators ? auditIndicators(selectedFile.audit, 'file-audit', { session }) : null}
                            {auditDetail ? auditDetail(selectedFile.audit, 'file-audit', { session, except: selectedFile['@id'] }) : null}
                        </div>
                    </div>
                : null}
            </div>
        );
    } else {
        header = (
            <div className="details-view-info">
                <h4>Unknown file</h4>
            </div>
        );
        body = <p className="browser-error">No information available</p>;
    }
    return { header, body, type: 'File' };
};

globals.graphDetail.register(FileDetailView, 'File');


export const CoalescedDetailsView = function CoalescedDetailsView(node) {
    let header;
    let body;

    if (node.metadata.coalescedFiles && node.metadata.coalescedFiles.length) {
        // Configuration for reference file table
        const coalescedFileColumns = {
            accession: {
                title: 'Accession',
                display: item =>
                    <span>
                        {item.title}&nbsp;<a href={item.href} download={item.href.substr(item.href.lastIndexOf('/') + 1)} data-bypass="true"><i className="icon icon-download"><span className="sr-only">Download</span></i></a>
                    </span>,
            },
            file_type: { title: 'File type' },
            output_type: { title: 'Output type' },
            assembly: { title: 'Mapping assembly' },
            genome_annotation: {
                title: 'Genome annotation',
                hide: list => _(list).all(item => !item.genome_annotation),
            },
            title: {
                title: 'Lab',
                getValue: item => (item.lab && item.lab.title ? item.lab.title : null),
            },
            date_created: {
                title: 'Date added',
                getValue: item => moment.utc(item.date_created).format('YYYY-MM-DD'),
                sorter: (a, b) => {
                    if (a && b) {
                        return Date.parse(a) - Date.parse(b);
                    }
                    const bTest = b ? 1 : 0;
                    return a ? -1 : bTest;
                },
            },
            status: {
                title: 'Status',
                display: item => <div className="characterization-meta-data"><FileStatusLabel file={item} /></div>,
            },
        };

        header = (
            <h4>Selected contributing files</h4>
        );
        body = (
            <div className="coalesced-table">
                <SortTable
                    list={node.metadata.coalescedFiles}
                    columns={coalescedFileColumns}
                    sortColumn="accession"
                />
            </div>
        );
    } else {
        header = (
            <div className="details-view-info">
                <h4>Unknown files</h4>
            </div>
        );
        body = <p className="browser-error">No information available</p>;
    }
    return { header, body, type: 'File' };
};

globals.graphDetail.register(CoalescedDetailsView, 'Coalesced');
