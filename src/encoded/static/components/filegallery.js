import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import { Panel, PanelHeading, TabPanel, TabPanelPane } from '../libs/ui/panel';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../libs/ui/modal';
import { collapseIcon } from '../libs/svg-icons';
import { auditDecor, auditsDisplayed, ObjectAuditIcon } from './audit';
import { FetchedData, Param } from './fetched';
import GenomeBrowser from './genome_browser';
import * as globals from './globals';
import { Graph, JsonGraph, GraphException } from './graph';
import { requestFiles, DownloadableAccession, computeAssemblyAnnotationValue, filterForVisualizableFiles } from './objectutils';
import { qcIdToDisplay } from './quality_metric';
import { softwareVersionList } from './software';
import { SortTablePanel, SortTable } from './sorttable';
import Status from './status';
import { visOpenBrowser, visFilterBrowserFiles, visFileSelectable, visSortBrowsers, visMapBrowserName } from './vis_defines';


const MINIMUM_COALESCE_COUNT = 5; // Minimum number of files in a coalescing group
dayjs.extend(utc);

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

// Calculate a string representation of the given replication_type.
const replicationDisplay = replicationType => (
    `${replicationType === 'anisogenic' ? 'Anisogenic' : 'Isogenic'} replicate`
);

export class FileTable extends React.Component {
    static rowClasses() {
        return '';
    }

    constructor() {
        super();

        // Initialize component state.
        this.state = {
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
        const { setInfoNodeId, setInfoNodeVisible } = this.props;
        if (setInfoNodeId && setInfoNodeVisible) {
            const node = {
                '@type': ['File'],
                metadata: {
                    ref: file,
                },
                schemas: this.props.schemas,
            };
            setInfoNodeId(node);
            setInfoNodeVisible(true);
        }
    }

    handleCollapse(table) {
        this.setState((state) => {
            const collapsed = _.clone(state.collapsed);
            collapsed[table] = !collapsed[table];
            return { collapsed };
        });
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
            context,
            items,
            graphedFiles,
            filePanelHeader,
            encodevers,
            showFileCount,
            setInfoNodeId,
            setInfoNodeVisible,
            browserOptions,
            session,
            adminUser,
            showReplicateNumber,
        } = this.props;
        const sessionProperties = this.context.session_properties;
        const loggedIn = !!(session && session['auth.userid']);
        const roles = globals.getRoles(sessionProperties);
        const isAuthorized = ['admin', 'submitter'].some(role => roles.includes(role));

        // Establish the selected assembly and annotation for the tabs
        const selectedAssembly = null;
        const selectedAnnotation = null;

        let datasetFiles = _((items && items.length > 0) ? items : []).uniq(file => file['@id']);
        if (datasetFiles.length > 0) {
            const unfilteredCount = datasetFiles.length;

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
                    if (file.output_type === 'reads') {
                        return 'raw';
                    }
                    if (file.output_type === 'index reads') {
                        return 'index';
                    }
                    return 'rawArray';
                }
                if (file.output_category === 'reference') {
                    return 'ref';
                }
                return 'proc';
            });

            // showReplicateNumber matches with show-functionality. It has to
            // be NOT (!)-ed to match with hide-functionality
            // TODO: (1)Move .hide to FileTable.procTableColumns declaration
            // (2) move showReplicateNumber to meta
            FileTable.procTableColumns.biological_replicates.hide = () => !showReplicateNumber;

            return (
                <div>
                    {showFileCount ? <div className="file-gallery-counts">Displaying {filteredCount} of {unfilteredCount} files</div> : null}
                    <SortTablePanel header={filePanelHeader} noDefaultClasses={this.props.noDefaultClasses}>
                        <RawSequencingTable
                            files={files.raw}
                            indexFiles={files.index}
                            showReplicateNumber={showReplicateNumber}
                            meta={{
                                encodevers,
                                replicationType: context.replication_type,
                                fileClick: (setInfoNodeId && setInfoNodeVisible) ? this.fileClick : null,
                                graphedFiles,
                                session,
                                loggedIn,
                                isAuthorized,
                                adminUser,
                            }}
                        />
                        <RawFileTable
                            files={files.rawArray}
                            showReplicateNumber={showReplicateNumber}
                            meta={{
                                encodevers,
                                replicationType: context.replication_type,
                                fileClick: (setInfoNodeId && setInfoNodeVisible) ? this.fileClick : null,
                                graphedFiles,
                                session,
                                loggedIn,
                                isAuthorized,
                                adminUser,
                            }}
                        />
                        <SortTable
                            title={
                                <CollapsingTitle
                                    title="Processed data"
                                    collapsed={this.state.collapsed.proc}
                                    handleCollapse={this.handleCollapseProc}
                                />
                            }
                            rowClasses={this.rowClasses}
                            collapsed={this.state.collapsed.proc}
                            list={files.proc}
                            columns={FileTable.procTableColumns}
                            sortColumn={showReplicateNumber ? 'biological_replicates' : 'date_created'}
                            meta={{
                                encodevers,
                                replicationType: context.replication_type,
                                hoverDL: this.hoverDL,
                                restrictedTip: this.state.restrictedTip,
                                fileClick: (setInfoNodeId && setInfoNodeVisible) ? this.fileClick : null,
                                graphedFiles,
                                browserOptions,
                                loggedIn,
                                isAuthorized,
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
                                replicationType: context.replication_type,
                                hoverDL: this.hoverDL,
                                restrictedTip: this.state.restrictedTip,
                                fileClick: (setInfoNodeId && setInfoNodeVisible) ? this.fileClick : null,
                                graphedFiles,
                                loggedIn,
                                isAuthorized,
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
    /** Dataset-type object being rendered */
    context: PropTypes.object.isRequired,
    /** Array of files to appear in the table */
    items: PropTypes.array.isRequired,
    /** Specifies which files are in the graph */
    graphedFiles: PropTypes.object,
    /** Table header component */
    filePanelHeader: PropTypes.object,
    /** ENCODE version of the experiment */
    encodevers: PropTypes.string,
    browserOptions: PropTypes.shape({
        /** Currently selected genome browser */
        currentBrowser: PropTypes.string,
        /** Called when user selects a browser */
        browserFileSelectHandler: PropTypes.func,
        /** Files selected for browsing */
        selectedBrowserFiles: PropTypes.array,
    }),
    /** True to show count of files in table */
    showFileCount: PropTypes.bool,
    /** Function to call to set the currently selected node ID */
    setInfoNodeId: PropTypes.func,
    /** Function to call to set the visibility of the node's modal */
    setInfoNodeVisible: PropTypes.func,
    /** User session */
    session: PropTypes.object,
    /** True if user is an admin user */
    adminUser: PropTypes.bool,
    /** Object from /profiles/ containing all schemas */
    schemas: PropTypes.object,
    /** True to strip SortTable panel of default CSS classes */
    noDefaultClasses: PropTypes.bool,
    /** True to show replicate number */
    showReplicateNumber: PropTypes.bool,
};

FileTable.defaultProps = {
    graphedFiles: null,
    filePanelHeader: null,
    encodevers: '',
    showFileCount: false,
    browserOptions: {
        currentBrowser: '',
        browserFileSelectHandler: null,
        selectedBrowserFiles: [],
    },
    setInfoNodeId: null,
    setInfoNodeVisible: null,
    session: null,
    adminUser: false,
    schemas: null,
    noDefaultClasses: false,
    showReplicateNumber: true,
};

FileTable.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
};


// Configuration for process file table
FileTable.procTableColumns = {
    visualize: {
        title: 'Visualize',
        hide: (list, columns, meta) => meta && meta.browserOptions && (meta.browserOptions.browserFileSelectHandler === null || meta.browserOptions.currentBrowser !== 'hic'),
        display: (item, meta) => {
            const selectedFile = meta.browserOptions.selectedBrowserFiles.find(file => file['@id'] === item['@id']);
            const selectable = visFileSelectable(item, meta.browserOptions.selectedBrowserFiles, meta.browserOptions.currentBrowser);
            return (
                <div className="file-table-visualizer">
                    <input name={item['@id']} type="checkbox" checked={!!selectedFile} disabled={!selectable && !selectedFile} onChange={meta.browserOptions.browserFileSelectHandler} />
                </div>
            );
        },
        sorter: false,
    },
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
        title: (list, columns, meta) => <span>{replicationDisplay(meta.replicationType)}</span>,
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
        getValue: item => dayjs.utc(item.date_created).format('YYYY-MM-DD'),
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
        display: (item, meta) => <ObjectAuditIcon object={item} audit={item.audit} isAuthorized={meta.isAuthorized} />,
    },
    status: {
        title: 'File status',
        display: item => <Status item={item} badgeSize="small" css="status__table-cell" />,
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
        getValue: item => dayjs.utc(item.date_created).format('YYYY-MM-DD'),
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
        display: (item, meta) => <ObjectAuditIcon object={item} isAuthorized={meta.isAuthorized} />,
    },
    status: {
        title: 'File status',
        display: item => <Status item={item} badgeSize="small" css="status__table-cell" />,
    },
};

const sortBioReps = (a, b) => {
    if ((!a || !b) || (!a.biological_replicates && !b.biological_replicates)) {
        return 0;
    }

    // Sorting function for biological replicates of the given files.
    let result; // Ends sorting loop once it has a value
    let i = 0;
    let repA = (a.biological_replicates && a.biological_replicates.length > 0) ? a.biological_replicates[i] : undefined;
    let repB = (b.biological_replicates && b.biological_replicates.length > 0) ? b.biological_replicates[i] : undefined;

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
};

class RawSequencingTable extends React.Component {
    constructor() {
        super();

        // Initialize React state variables.
        this.state = {
            collapsed: false, // Collapsed/uncollapsed state of table
        };

        // Bind `this` to non-React methods.
        this.findIndexFile = this.findIndexFile.bind(this);
        this.handleCollapse = this.handleCollapse.bind(this);
    }

    /**
     * Find the index reads file associated with the one or two given files. For paired reads, both
     * files have to match to return a matching index reads file. For singled-ended reads, only
     * `file0` needs to match.
     * @param {object} file0 - First reads file of pair or only file of single
     * @param {object} file1 - Second reads file of pair
     *
     * @return {object} Index reads file with index_of matching given files; undefined if none
     */
    findIndexFile(file0, file1) {
        return this.props.indexFiles.find(indexFile => indexFile.index_of[0] === file0['@id'] && (indexFile.index_of.length === 2 ? indexFile.index_of[1] === file1['@id'] : true));
    }

    handleCollapse() {
        // Handle a click on a collapse button by toggling the corresponding tableCollapse state var
        this.setState({ collapsed: !this.state.collapsed });
    }

    render() {
        const { files, indexFiles, meta, showReplicateNumber } = this.props;
        const { loggedIn, adminUser, isAuthorized } = meta;

        if (files && files.length > 0) {
            // Make object keyed by all files' @ids to make searching easy. Each key's value
            // points to the corresponding file object.
            const filesKeyed = {};
            files.forEach((file) => {
                filesKeyed[file['@id']] = file;
            });

            // Make lists of files that are and aren't paired. Paired files with missing partners
            // count as not paired. Files with more than one biological replicate don't count as
            // paired.
            let nonpairedFiles = [];
            let pairedFiles = _(files).filter((file) => {
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
                            // Both the file and its partner qualify as good pairs of each other.
                            // Let them pass the filter, and set their sort keys to the lower of
                            // the two accessions -- that's how pairs will sort within a biological
                            // replicate. The sort keys also get their paired_end value
                            // concatenated so they sort as pairs correctly. Also track the
                            // `pairSortId` which is the same as portSortKey` but without the
                            // paired_end property concatenated.
                            partner.pairSortId = file.title < partner.title ? file.title : partner.title;
                            partner.pairSortKey = `${partner.pairSortId}-${partner.paired_end}`;
                            file.pairSortId = partner.pairSortId;
                            file.pairSortKey = `${partner.pairSortId}-${file.paired_end}`;
                            return true;
                        }
                    }
                }

                // File not part of a pair; add it to the non-paired list as a copy so we can
                // mutate them later.
                nonpairedFiles.push(Object.assign({}, file));
                return false;
            });

            // Sort the non-paired files by biological replicate, but corresponding index reads
            // files still need weaving into this array.
            nonpairedFiles = nonpairedFiles.sort(sortBioReps);

            // Weave index files after each corresponding single-ended raw sequencing file.
            const nonPairedFilesWithIndex = [];
            if (indexFiles) {
                nonpairedFiles.forEach((nonpairedFile) => {
                    nonPairedFilesWithIndex.push(nonpairedFile);
                    const matchingIndexFile = indexFiles.find(indexFile => indexFile.index_of.includes(nonpairedFile['@id']));
                    if (matchingIndexFile) {
                        nonPairedFilesWithIndex.push(matchingIndexFile);
                    }
                });
                nonpairedFiles = nonPairedFilesWithIndex;
            }

            // Copy indexFiles to have `pairSortId` and  `pairSortKey` properties similar to the
            // corresponding reads files’ pairSortKeys. For ease-of-implementation and performance,
            // we only look for the one file of the pair in `pairedFiles` to get its pairSortKey
            // root (without appended `paired_end` string) -- not both files. Append "-I" to
            // `poirSortKey` to index reads files sort after the pairs they associate with.
            const pairedFileIndexReads = [];
            if (indexFiles) {
                indexFiles.forEach((indexFile) => {
                    const indexFileCopy = Object.assign({}, indexFile);
                    const matchingPairFile = pairedFiles.find(pairedFile => indexFile.index_of.includes(pairedFile['@id']));
                    if (matchingPairFile) {
                        indexFileCopy.pairSortId = matchingPairFile.pairSortId;
                        indexFileCopy.pairSortKey = `${matchingPairFile.pairSortId}-I`;
                        pairedFileIndexReads.push(indexFileCopy);
                    }
                });
                pairedFiles = pairedFiles.concat(pairedFileIndexReads);
            }

            // Group paired files by biological replicate and library -- four-digit biological
            // replicate concatenated with library accession becomes the group key, and all files
            // with that biological replicate and library form an array under that key. If the pair
            // don't belong to a biological replicate, sort them under the fake replicate `Z   `
            // so that they'll sort at the end.
            let pairedRepGroups = {};
            let pairedRepKeys = [];
            if (pairedFiles.length > 0) {
                pairedRepGroups = _(pairedFiles).groupBy((file) => {
                    if (file.biological_replicates && file.biological_replicates.length === 1) {
                        return globals.zeroFill(file.biological_replicates[0]) + ((file.replicate && file.replicate.library) ? file.replicate.library.accession : '');
                    }
                    return 'Z';
                });

                // Make a sorted list of keys
                pairedRepKeys = Object.keys(pairedRepGroups).sort();
            }

            return (
                <table className="table table__sortable table-raw">
                    <thead>
                        <tr className="table-section">
                            <th colSpan="12">
                                <CollapsingTitle title="Raw sequencing data" collapsed={this.state.collapsed} handleCollapse={this.handleCollapse} />
                            </th>
                        </tr>

                        {!this.state.collapsed ?
                            <tr>
                                {showReplicateNumber ? <th>{replicationDisplay(meta.replicationType)}</th> : null}
                                <th>Library</th>
                                <th>Accession</th>
                                <th>File type</th>
                                <th>Run type</th>
                                <th>Read</th>
                                <th>Output type</th>
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
                                const groupFiles = pairedRepGroups[pairedRepKey].sort((a, b) => (a.pairSortKey < b.pairSortKey ? -1 : 1));

                                // Draw bottom border if this isn't the last paired replicate, or
                                // it is but non-paired files follow.
                                const bottomClass = j < (pairedRepKeys.length - 1) || nonpairedFiles.length > 0 ? 'merge-bottom' : '';

                                // Render each file's row, with the biological replicate and library
                                // cells only on the first row.
                                return groupFiles.map((file, i) => {
                                    let pairClass;
                                    if (file.run_type === 'paired-ended') {
                                        pairClass = file.paired_end === '1' ? 'align-pair1' : 'align-pair2';
                                    } else {
                                        // Must be an index reads file if it's not paired-ended.
                                        pairClass = 'index-reads';
                                    }

                                    // Draw bottom border if second file of pair and no index reads
                                    // follow, or file *is* index reads, but not if last row of
                                    // table.
                                    const isNextInGroupIndexReads = groupFiles[i + 1] && groupFiles[i + 1].output_type === 'index reads';
                                    if (
                                        (file.output_type === 'index reads' || (file.paired_end === '2' && !isNextInGroupIndexReads))
                                        && !(i === groupFiles.length - 1 && j === pairedRepKeys.length - 1 && nonpairedFiles.length === 0)
                                    ) {
                                        pairClass = `${pairClass} pair-bottom`;
                                    }

                                    return (
                                        <tr key={file['@id']}>
                                            {showReplicateNumber && i === 0 ?
                                                <td rowSpan={groupFiles.length} className={`${bottomClass} merge-right table-raw-merged table-raw-biorep`}>{groupFiles[0].biological_replicates[0]}</td>
                                            : null}
                                            {i === 0 ?
                                                <td rowSpan={groupFiles.length} className={`${bottomClass} merge-right + table-raw-merged`}>{(groupFiles[0].replicate && groupFiles[0].replicate.library) ? groupFiles[0].replicate.library.accession : null}</td>
                                            : null}
                                            <td className={pairClass}>
                                                <DownloadableAccession file={file} clickHandler={meta.fileClick ? meta.fileClick : null} loggedIn={loggedIn} adminUser={adminUser} />
                                            </td>
                                            <td className={pairClass}>{file.file_type}</td>
                                            <td className={pairClass}>{file.run_type === 'paired-ended' ? 'PE' : ''}{file.read_length ? <span>{file.read_length + file.read_length_units}</span> : null}</td>
                                            <td className={pairClass}>{file.paired_end}</td>
                                            <td className={pairClass}>{file.output_type}</td>
                                            <td className={pairClass}>{file.lab && file.lab.title ? file.lab.title : null}</td>
                                            <td className={pairClass}>{dayjs.utc(file.date_created).format('YYYY-MM-DD')}</td>
                                            <td className={pairClass}>{globals.humanFileSize(file.file_size)}</td>
                                            <td className={pairClass}><ObjectAuditIcon object={file} isAuthorized={isAuthorized} /></td>
                                            <td className={pairClass}><Status item={file} badgeSize="small" css="status__table-cell" /></td>
                                        </tr>
                                    );
                                });
                            })}
                            {nonpairedFiles.map((file, i) => {
                                // Draw a row over the first single-ended file if a paired file
                                // preceded it.
                                const rowClasses = [
                                    pairedRepKeys.length > 0 && i === 0 ? 'table-raw-separator' : null,
                                ];

                                // Work out CSS classes and row spans for raw sequencing files with
                                // a corresponding index reads file.
                                let singleClass = null;
                                const rawHasIndex = file.output_type !== 'index reads' && nonpairedFiles[i + 1] && nonpairedFiles[i + 1].output_type === 'index reads';
                                const rawIsIndex = file.output_type === 'index reads';
                                const nextRawIsIndex = nonpairedFiles[i + 1] && nonpairedFiles[i + 1].output_type === 'index reads';
                                if (rawIsIndex) {
                                    singleClass = 'index-reads pair-bottom';
                                }

                                // Determine if accession should be a button or not.
                                const buttonEnabled = !!(meta.graphedFiles && meta.graphedFiles[file['@id']]);

                                return (
                                    <tr key={file['@id']} className={rowClasses.join(' ')}>
                                        {showReplicateNumber && !rawIsIndex ?
                                            <td rowSpan={rawHasIndex ? 2 : null} className={`table-raw-biorep${nextRawIsIndex ? ' pair-bottom merge-right + table-raw-merged' : ''}`}>{file.biological_replicates && file.biological_replicates.length > 0 ? file.biological_replicates.sort((a, b) => a - b).join(', ') : 'N/A'}</td>
                                        : null}
                                        {!rawIsIndex ?
                                            <td rowSpan={rawHasIndex ? 2 : null} className={nextRawIsIndex ? 'pair-bottom merge-right + table-raw-merged' : null}>{(file.replicate && file.replicate.library) ? file.replicate.library.accession : 'N/A'}</td>
                                        : null}
                                        <td className={singleClass}>
                                            <DownloadableAccession file={file} buttonEnabled={buttonEnabled} clickHandler={meta.fileClick ? meta.fileClick : null} loggedIn={loggedIn} adminUser={adminUser} />
                                        </td>
                                        <td className={singleClass}>{file.file_type}</td>
                                        <td className={singleClass}>{rawIsIndex ? null : 'SE'}{file.read_length ? <span>{file.read_length + file.read_length_units}</span> : null}</td>
                                        <td className={singleClass}>{file.paired_end}</td>
                                        <td className={singleClass}>{file.output_type}</td>
                                        <td className={singleClass}>{file.lab && file.lab.title ? file.lab.title : null}</td>
                                        <td className={singleClass}>{dayjs.utc(file.date_created).format('YYYY-MM-DD')}</td>
                                        <td className={singleClass}>{globals.humanFileSize(file.file_size)}</td>
                                        <td className={singleClass}><ObjectAuditIcon object={file} isAuthorized={isAuthorized} /></td>
                                        <td className={singleClass}><Status item={file} badgeSize="small" css="status__table-cell" /></td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    : null}

                    <tfoot>
                        <tr>
                            <td className={`file-table-footer${this.state.collapsed ? ' hiding' : ''}`} colSpan="12" />
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
    indexFiles: PropTypes.array, // Index reads files that refer to actual files in `files`
    meta: PropTypes.object.isRequired, // Extra metadata in the same format passed to SortTable
    showReplicateNumber: PropTypes.bool,
};

RawSequencingTable.defaultProps = {
    files: null,
    indexFiles: null,
    showReplicateNumber: true,
};


class RawFileTable extends React.Component {
    constructor() {
        super();

        // Initialize React state variables.
        this.state = {
            collapsed: false, // Collapsed/uncollapsed state of table
        };

        // Bind `this` to non-React methods.
        this.handleCollapse = this.handleCollapse.bind(this);
    }

    handleCollapse() {
        // Handle a click on a collapse button by toggling the corresponding tableCollapse state var
        this.setState({ collapsed: !this.state.collapsed });
    }

    render() {
        const { files, meta, showReplicateNumber } = this.props;
        const { loggedIn, adminUser, isAuthorized } = meta;

        if (files && files.length > 0) {
            // Group all files by their library accessions. Any files without replicates or
            // libraries get grouped under library 'Z' so they get sorted at the end.
            const libGroups = _(files).groupBy((file) => {
                // Groups have a 4-digit zero-filled biological replicate number concatenated with
                // the library accession, e.g. 0002ENCLB158ZZZ.
                const bioRep = file.biological_replicates ? globals.zeroFill(file.biological_replicates[0], 4) : '';
                return bioRep + (file.replicate && file.replicate.library && file.replicate.library.accession ? file.replicate.library.accession : 'Z');
            });

            // Split library/file groups into paired and non-paired library/file groups.
            const grouped = {};
            const nonGrouped = [];
            Object.keys(libGroups).forEach((libGroupKey) => {
                if (libGroups[libGroupKey].length > 1) {
                    grouped[libGroupKey] = libGroups[libGroupKey];
                } else {
                    nonGrouped.push(libGroups[libGroupKey][0]);
                }
            });
            const groupKeys = Object.keys(grouped).sort();

            return (
                <table className="table table__sortable table-raw">
                    <thead>
                        <tr className="table-section">
                            <th colSpan="11">
                                <CollapsingTitle title="Raw data" collapsed={this.state.collapsed} handleCollapse={this.handleCollapse} />
                            </th>
                        </tr>

                        {!this.state.collapsed ?
                            <tr>
                                {showReplicateNumber ?
                                    <th>{replicationDisplay(meta.replicationType)}</th> :
                                null}
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
                            {groupKeys.map((groupKey, j) => {
                                // groupFiles is an array of files under a bioreplicate/library.
                                // Determine whether to draw a bottom border based on whether this
                                // is the last group displayed (don't draw) or not (do draw).
                                const groupFiles = grouped[groupKey];
                                const groupBottom = j < groupKeys.length - 1 ? 'group-bottom' : '';

                                // Render each file's row, with the biological replicate and library
                                // cells only on the first row.
                                return groupFiles.sort((a, b) => (a.title < b.title ? -1 : 1)).map((file, i) => {
                                    // Determine whether to draw a bottom border based on whether
                                    // this is the last file in a group (do draw) or not (don't
                                    // draw) and it's not within the last group (don't draw).
                                    const fileBottom = (i === groupFiles.length - 1 && groupBottom) ? 'group-bottom' : '';

                                    // Determine if the accession should be a button or not.
                                    const buttonEnabled = !!(meta.graphedFiles && meta.graphedFiles[file['@id']]);

                                    // Prepare for run_type display
                                    return (
                                        <tr key={file['@id']}>
                                            {showReplicateNumber && i === 0 ?
                                                <td rowSpan={groupFiles.length} className={`${groupBottom} merge-right table-raw-merged table-raw-biorep`}>
                                                    {groupFiles[0].biological_replicates.length > 0 ? <span>{groupFiles[0].biological_replicates[0]}</span> : <i>N/A</i>}
                                                </td>
                                            : null}
                                            {i === 0 ?
                                                <td rowSpan={groupFiles.length} className={`${groupBottom} merge-right table-raw-merged`}>
                                                    {groupFiles[0].replicate && groupFiles[0].replicate.library ? <span>{groupFiles[0].replicate.library.accession}</span> : <i>N/A</i>}
                                                </td>
                                            : null}
                                            <td className={fileBottom}>
                                                <DownloadableAccession file={file} buttonEnabled={buttonEnabled} clickHandler={meta.fileClick ? meta.fileClick : null} loggedIn={loggedIn} adminUser={adminUser} />
                                            </td>
                                            <td className={fileBottom}>{file.file_type}</td>
                                            <td className={fileBottom}>{file.output_type}</td>
                                            <td className={fileBottom}>{file.assembly}</td>
                                            <td className={fileBottom}>{file.lab && file.lab.title ? file.lab.title : null}</td>
                                            <td className={fileBottom}>{dayjs.utc(file.date_created).format('YYYY-MM-DD')}</td>
                                            <td className={fileBottom}>{globals.humanFileSize(file.file_size)}</td>
                                            <td className={fileBottom}><ObjectAuditIcon object={file} isAuthorized={isAuthorized} /></td>
                                            <td className={fileBottom}><Status item={file} badgeSize="small" css="status__table-cell" /></td>
                                        </tr>
                                    );
                                });
                            })}
                            {nonGrouped.sort(sortBioReps).map((file, i) => {
                                // Prepare for run_type display
                                const rowClasses = [
                                    groupKeys.length > 0 && i === 0 ? 'table-raw-separator' : null,
                                ];

                                // Determine if accession should be a button or not.
                                const buttonEnabled = !!(meta.graphedFiles && meta.graphedFiles[file['@id']]);

                                return (
                                    <tr key={file['@id']} className={rowClasses.join(' ')}>
                                        {showReplicateNumber ?
                                            <td className="table-raw-biorep">{(file.biological_replicates && file.biological_replicates.length > 0) ? file.biological_replicates.sort((a, b) => a - b).join(', ') : 'N/A'}</td> :
                                        null}
                                        <td>{(file.replicate && file.replicate.library) ? file.replicate.library.accession : 'N/A'}</td>
                                        <td>
                                            <DownloadableAccession file={file} buttonEnabled={buttonEnabled} clickHandler={meta.fileClick ? meta.fileClick : null} loggedIn={loggedIn} adminUser={adminUser} />
                                        </td>
                                        <td>{file.file_type}</td>
                                        <td>{file.output_type}</td>
                                        <td>{file.assembly}</td>
                                        <td>{file.lab && file.lab.title ? file.lab.title : null}</td>
                                        <td>{dayjs.utc(file.date_created).format('YYYY-MM-DD')}</td>
                                        <td>{globals.humanFileSize(file.file_size)}</td>
                                        <td><ObjectAuditIcon object={file} isAuthorized={isAuthorized} /></td>
                                        <td><Status item={file} badgeSize="small" css="status__table-cell" /></td>
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
    meta: PropTypes.object.isRequired, // Extra metadata in the same format passed to SortTable
    showReplicateNumber: PropTypes.bool, // True to show replicate number
};

RawFileTable.defaultProps = {
    files: null,
    showReplicateNumber: true,
};


// Called once searches for unreleased files returns results in props.items. Displays both released and
// unreleased files.
export const DatasetFiles = (props) => {
    const { items } = props;

    const files = _.uniq((items && items.length > 0) ? items : []);
    if (files.length > 0) {
        return <FileTable {...props} items={files} />;
    }
    return null;
};

DatasetFiles.propTypes = {
    items: PropTypes.array, // Array of files retrieved
};

DatasetFiles.defaultProps = {
    items: null,
};


// File display widget, showing a facet list, a table, and a graph (and maybe a BioDalliance).
// This component only triggers the data retrieval, which is done with a search for files associated
// with the given experiment (in this.props.context). An odd thing is we specify query-string parameters
// to the experiment URL, but they apply to the file search -- not the experiment itself.
export const FileGallery = ({ context, encodevers, hideGraph, altFilterDefault, showReplicateNumber }, reactContext) => (
    <FetchedData>
        <Param name="data" url={`/search/?limit=all&type=File&dataset=${context['@id']}`} />
        <Param name="schemas" url="/profiles/" />
        <FileGalleryRenderer context={context} session={reactContext.session} encodevers={encodevers} hideGraph={hideGraph} altFilterDefault={altFilterDefault} showReplicateNumber={showReplicateNumber} />
    </FetchedData>
);

FileGallery.propTypes = {
    context: PropTypes.object.isRequired, // Dataset object whose files we're rendering
    encodevers: PropTypes.string, // ENCODE version number
    hideGraph: PropTypes.bool, // T to hide graph display
    altFilterDefault: PropTypes.bool, // T to default to All Assemblies and Annotations
    showReplicateNumber: PropTypes.bool, // True to show replicate number
};

FileGallery.defaultProps = {
    encodevers: '',
    hideGraph: false,
    altFilterDefault: false,
    showReplicateNumber: true,
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
    filterOptions = filterOptions.length > 0 ? _(filterOptions).uniq(option => `${option.assembly}!${option.annotation ? option.annotation : ''}`) : [];

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


/**
 * Render the visualization controls, including the browser selector and Visulize button.
 */
class VisualizationControls extends React.Component {
    constructor() {
        super();
        this.handleBrowserChange = this.handleBrowserChange.bind(this);
        this.handleVisualize = this.handleVisualize.bind(this);
    }

    /**
     * Called when the user selects a new option from the browser menu.
     */
    handleBrowserChange(e) {
        const { browserChangeHandler } = this.props;
        browserChangeHandler(e.target.value);
    }

    /**
     * Called when the user clicks the Visualize button.
     */
    handleVisualize() {
        const { visualizeHandler } = this.props;
        visualizeHandler();
    }

    render() {
        const { browsers, currentBrowser } = this.props;

        return (
            <div className="file-gallery-controls__visualization-selector">
                {browsers.length > 0 ?
                    <select className="form-control--select" value={currentBrowser} onChange={this.handleBrowserChange}>
                        {browsers.map(browser => (
                            <option key={browser} value={browser}>{visMapBrowserName(browser)}</option>
                        ))}
                    </select>
                : null}
                <button className="btn btn-info" onClick={this.handleVisualize} type="button" disabled={this.props.visualizeDisabled}>Visualize</button>
            </div>
        );
    }
}

VisualizationControls.propTypes = {
    /** All available browsers */
    browsers: PropTypes.array.isRequired,
    /** Currently selected browser */
    currentBrowser: PropTypes.string,
    /** Callback to handle new browser selection */
    browserChangeHandler: PropTypes.func.isRequired,
    /** Callback to handle click in Visualize button */
    visualizeHandler: PropTypes.func.isRequired,
    /** Flag that button should be disabled */
    visualizeDisabled: PropTypes.bool,
};

VisualizationControls.defaultProps = {
    currentBrowser: '',
    visualizeDisabled: false,
};


// Displays the file filtering controls for the file association graph and file tables.

class FilterControls extends React.Component {
    constructor() {
        super();

        // Bind this to non-React methods.
        this.handleAssemblyAnnotationChange = this.handleAssemblyAnnotationChange.bind(this);
    }

    handleAssemblyAnnotationChange(e) {
        this.props.handleAssemblyAnnotationChange(e.target.value);
    }

    render() {
        const { filterOptions, selectedFilterValue, browsers, currentBrowser, browserChangeHandler, visualizeHandler } = this.props;

        if (filterOptions.length > 0 || browsers.length > 0) {
            return (
                <div className="file-gallery-controls">
                    {filterOptions.length > 0 ?
                        <div className="file-gallery-controls__assembly-selector">
                            <FilterMenu selectedFilterValue={selectedFilterValue} filterOptions={filterOptions} handleFilterChange={this.handleAssemblyAnnotationChange} />
                        </div>
                    : null}
                    <VisualizationControls browsers={browsers} currentBrowser={currentBrowser} browserChangeHandler={browserChangeHandler} visualizeHandler={visualizeHandler} visualizeDisabled={!(browsers.length > 0)} />
                </div>
            );
        }
        return null;
    }
}

FilterControls.propTypes = {
    /** Assembly/annotation combos available */
    filterOptions: PropTypes.array.isRequired,
    /** Currently-selected assembly/annotation <select> value */
    selectedFilterValue: PropTypes.string,
    /** Array of browsers available in this experiment */
    browsers: PropTypes.array,
    /** Name of currently selected browser */
    currentBrowser: PropTypes.string,
    /** File @ids selected for the browser */
    handleAssemblyAnnotationChange: PropTypes.func.isRequired,
    /** Called then the user selects a different browser */
    browserChangeHandler: PropTypes.func.isRequired,
    /** Called when the user clicks the Visualize button */
    visualizeHandler: PropTypes.func.isRequired,
};

FilterControls.defaultProps = {
    selectedFilterValue: '0',
    browsers: [],
    currentBrowser: '',
};


// Map a QC object to its corresponding two-letter abbreviation for the graph.
function qcAbbr(qc) {
    // As we add more QC object types, add to this object.
    const qcAbbrMap = {
        AtacAlignmentQualityMetric: 'AL',
        AtacAlignmentEnrichmentQualityMetric: 'AE',
        AtacLibraryQualityMetric: 'LB',
        AtacPeakEnrichmentQualityMetric: 'PE',
        AtacReplicationQualityMetric: 'RP',
        BigwigcorrelateQualityMetric: 'BC',
        BismarkQualityMetric: 'BK',
        ChipAlignmentQualityMetric: 'AL',
        ChipAlignmentEnrichmentQualityMetric: 'AE',
        ChipLibraryQualityMetric: 'LB',
        ChipPeakEnrichmentQualityMetric: 'PE',
        ChipReplicationQualityMetric: 'RP',
        ChipSeqFilterQualityMetric: 'CF',
        ComplexityXcorrQualityMetric: 'CX',
        CorrelationQualityMetric: 'CN',
        CpgCorrelationQualityMetric: 'CC',
        DnaseAlignmentQualityMetric: 'DA',
        DuplicatesQualityMetric: 'DS',
        EdwbamstatsQualityMetric: 'EB',
        FilteringQualityMetric: 'FG',
        GeneQuantificationQualityMetric: 'GQ',
        GenericQualityMetric: 'GN',
        GeneTypeQuantificationQualityMetric: 'GT',
        HistoneChipSeqQualityMetric: 'HC',
        HotspotQualityMetric: 'HS',
        IDRQualityMetric: 'ID',
        IdrSummaryQualityMetric: 'IS',
        MadQualityMetric: 'MD',
        SamtoolsFlagstatsQualityMetric: 'SF',
        SamtoolsStatsQualityMetric: 'SS',
        StarQualityMetric: 'SR',
        TrimmingQualityMetric: 'TG',
        MicroRnaMappingQualityMetric: 'MM',
        MicroRnaQuantificationQualityMetric: 'MQ',
        LongReadRnaMappingQualityMetric: 'LM',
        LongReadRnaQuantificationQualityMetric: 'LQ',
        GembsAlignmentQualityMetric: 'AL',
        DnaseFootprintingQualityMetric: 'DF',
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
    if (file.derived_from && file.derived_from.length > 0 && file.dataset === fileDataset['@id']) {
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


/**
 * Generate a string of CSS classes for a file node. Plass the result into a `className` property of a component.
 *
 * @param {object-required} file - File we're generating the statuses for.
 * @param {bool} active - True if the file is active and should be highlighted as such.
 * @param (bool) colorize - True to colorize the nodes according to their status by adding a CSS class for their status
 * @param {string} addClasses - CSS classes to add in addition to the ones generated by the file statuses.
 */
const fileCssClassGen = (file, active, highlight, colorizeNode, addClasses) => {
    const statusClass = colorizeNode ? ` graph-node--${globals.statusToClassElement(file.status)}` : '';
    return `pipeline-node-file${active ? ' active' : ''}${highlight ? ' highlight' : ''}${statusClass}${addClasses ? ` ${addClasses}` : ''}`;
};


// Assembly a graph of files, the QC objects that belong to them, and the steps that connect them.
export function assembleGraph(files, highlightedFiles, dataset, options, loggedIn = false) {
    // Calculate a step ID from a file's derived_from array.
    function rDerivedFileIds(file) {
        if (file.derived_from && file.derived_from.length > 0) {
            return file.derived_from.sort().join();
        }
        return '';
    }

    // Calculate a QC node ID.
    function rGenQcId(metric, file) {
        return `qc:${metric['@id'] + file['@id']}`;
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
    const allowNoAssembly = dataset.assay_term_name === 'RNA Bind-n-Seq';
    files.forEach((file) => {
        // allFiles gets all files from search regardless of filtering.
        allFiles[file['@id']] = file;

        // matchingFiles gets just the files matching the given filtering assembly/annotation.
        // Note that if all assemblies and annotations are selected, this function isn't called
        // because no graph gets displayed in that case.
        if (allowNoAssembly || ((file.assembly === selectedAssembly) && ((!file.genome_annotation && !selectedAnnotation) || (file.genome_annotation === selectedAnnotation)))) {
            // Note whether any files have an analysis step
            const fileAnalysisStep = file.analysis_step_version && file.analysis_step_version.analysis_step;
            if (!fileAnalysisStep || (file.derived_from && file.derived_from.length > 0)) {
                // File has no analysis step or derives from other files, so it can be included in
                // the graph.
                matchingFiles[file['@id']] = file;

                // Collect any QC info that applies to this file and make it searchable by file
                // @id.
                if (file.quality_metrics && file.quality_metrics.length > 0) {
                    fileQcMetrics[file['@id']] = file.quality_metrics.filter(qc => loggedIn || qc.status === 'released');
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
            const hasDerivedFroms = matchingFile && matchingFile.derived_from && matchingFile.derived_from.length > 0 &&
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
    if (dataset.contributing_files && dataset.contributing_files.length > 0) {
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
    if (Object.keys(usedContributingFiles).length > 0) {
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
        if (coalescingGroupKeys && coalescingGroupKeys.length > 0) {
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
        if (allReplicates[replicateNum] && allReplicates[replicateNum].length > 0) {
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

        // check to see if file should be highlighted (if it is part of a filtered list)
        const highlightToggle = highlightedFiles.some(highlight => highlight['@id'] === fileId);

        if (!file) {
            if (allMissingFiles.indexOf(fileId) === -1) {
                const fileNodeId = `file:${fileId}`;
                const fileNodeLabel = `${globals.atIdToAccession(fileId)}`;
                const fileCssClass = `pipeline-node-file contributing${infoNode && infoNode.id === fileNodeId ? ' active' : ''} ${highlightToggle ? ' highlight' : ''}`;

                jsonGraph.addNode(fileNodeId, fileNodeLabel, {
                    cssClass: fileCssClass,
                    type: 'File',
                    shape: 'rect',
                    cornerRadius: 16,
                    contributing: fileId,
                    ref: {},
                    displayDecoration: true,
                    decorationClass: infoNode && infoNode.id === fileNodeId ? 'decoration--active' : '',
                });
            }
        } else {
            const fileNodeId = `file:${file['@id']}`;
            const fileNodeLabel = `${file.title} (${file.output_type})`;
            const fileCssClass = fileCssClassGen(file, !!(infoNode && infoNode.id === fileNodeId), highlightToggle, colorize);
            const fileRef = file;
            const replicateNode = (file.biological_replicates && file.biological_replicates.length === 1) ? jsonGraph.getNode(`rep:${file.biological_replicates[0]}`) : null;
            let metricsInfo;

            // Add QC metrics info from the file to the list to generate the nodes later.
            if (fileQcMetrics[fileId] && fileQcMetrics[fileId].length > 0) {
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
                displayDecoration: true,
                decorationClass: infoNode && infoNode.id === fileNodeId ? 'decoration--active' : '',
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
                        displayDecoration: true,
                        decorationClass: infoNode && infoNode.id === stepId ? 'decoration--active' : '',
                    });
                }

                // Connect the file to the step, and the step to the derived_from files
                const infoNodeId = infoNode && infoNode.id;
                const fileNodeHighlighted = (infoNodeId === fileNodeId) || (infoNodeId === stepId);
                jsonGraph.addEdge(stepId, fileNodeId, { class: fileNodeHighlighted ? 'highlighted' : '' });
                file.derived_from.forEach((derivedFromAtId) => {
                    if (!allDerivedFroms[derivedFromAtId]) {
                        return;
                    }
                    const derivedFromFile = allFiles[derivedFromAtId] || allMissingFiles.some(missingFileId => missingFileId === derivedFromAtId);
                    if (derivedFromFile) {
                        // Not derived from a contributing file; just add edges normally.
                        const derivedFileId = `file:${derivedFromAtId}`;
                        const derivedFileNodeHighlighted = (infoNodeId === derivedFileId) || (infoNodeId === stepId);
                        if (!jsonGraph.getEdge(derivedFileId, stepId)) {
                            jsonGraph.addEdge(derivedFileId, stepId, { class: derivedFileNodeHighlighted ? 'highlighted' : '' });
                        }
                    } else {
                        // File derived from a contributing file; add edges to a coalesced node
                        // that we'll add to the graph later.
                        const coalescedContributing = allCoalesced[derivedFromAtId];
                        if (coalescedContributing) {
                            // Rendering a coalesced contributing file.
                            const derivedFileId = `coalesced:${coalescedContributing}`;
                            const derivedFileNodeHighlighted = (infoNodeId === derivedFileId) || (infoNodeId === stepId);
                            if (!jsonGraph.getEdge(derivedFileId, stepId)) {
                                jsonGraph.addEdge(derivedFileId, stepId, { class: derivedFileNodeHighlighted ? 'highlighted' : '' });
                            }
                        } else if (usedContributingFiles[derivedFromAtId]) {
                            const derivedFileId = `file:${derivedFromAtId}`;
                            const derivedFileNodeHighlighted = (infoNodeId === derivedFileId) || (infoNodeId === stepId);
                            if (!jsonGraph.getEdge(derivedFileId, stepId)) {
                                jsonGraph.addEdge(derivedFileId, stepId, { class: derivedFileNodeHighlighted ? 'highlighted' : '' });
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
        if (coalescingGroup.length > 0) {
            const fileNodeId = `coalesced:${groupHash}`;
            const fileCssClass = `pipeline-node-file contributing${infoNode && infoNode.id === fileNodeId ? ' active' : ''}`;
            jsonGraph.addNode(fileNodeId, `${coalescingGroup.length} contributing files`, {
                cssClass: fileCssClass,
                type: 'Coalesced',
                shape: 'stack',
                cornerRadius: 16,
                contributing: groupHash,
                ref: coalescingGroup,
                displayDecoration: true,
                decorationClass: infoNode && infoNode.id === fileNodeId ? 'decoration--active' : '',
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
    const { files, highlightedFiles, dataset, infoNode, selectedAssembly, selectedAnnotation, colorize, handleNodeClick, schemas, loggedIn } = props;

    // Build node graph of the files and analysis steps with this experiment
    let graph;
    if (files.length > 0) {
        try {
            graph = assembleGraph(
                files,
                highlightedFiles,
                dataset,
                {
                    infoNode,
                    selectedAssembly,
                    selectedAnnotation,
                    colorize,
                },
                loggedIn
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
    highlightedFiles: PropTypes.array.isRequired, // Array of files that should be highlighted on graph
    dataset: PropTypes.object.isRequired, // dataset these files are being rendered into
    selectedAssembly: PropTypes.string, // Currently selected assembly
    selectedAnnotation: PropTypes.string, // Currently selected annotation
    infoNode: PropTypes.object, // Currently highlighted node
    schemas: PropTypes.object, // Schemas for QC metrics
    handleNodeClick: PropTypes.func.isRequired, // Parent function to call when a graph node is clicked
    colorize: PropTypes.bool, // True to enable node colorization based on status
    loggedIn: PropTypes.bool, // True if current user has logged in
    auditIndicators: PropTypes.func, // Inherited from auditDecor HOC
    auditDetail: PropTypes.func, // Inherited from auditDecor HOC
};

FileGraph.defaultProps = {
    selectedAssembly: '',
    selectedAnnotation: '',
    infoNode: null,
    schemas: null,
    colorize: false,
    loggedIn: false,
    auditIndicators: null,
    auditDetail: null,
};


/**
 * Display the checkbox for the user to choose whether to include depcrecated files in the graph
 * and table displays.
 */
const InclusionSelector = ({ inclusionOn, handleInclusionChange }) => (
    <div className="checkbox--right">
        <label htmlFor="filterIncArchive">
            Include deprecated files
            <input
                name="filterIncArchive"
                type="checkbox"
                checked={inclusionOn}
                onChange={handleInclusionChange}
            />
        </label>
    </div>
);

InclusionSelector.propTypes = {
    /** True if the inclusion checkbox should be on */
    inclusionOn: PropTypes.bool.isRequired,
    /** Function to call when checkbox is clicked */
    handleInclusionChange: PropTypes.func.isRequired,
};

// Display facets for files
// Only one assembly can be chosen so controls for 'Assembly' facet look like radiobuttons
// Multiple terms may be chosen for facets that are not Assembly so those look like regular buttons
const FileFacet = (props) => {
    const { facetObject, facetTitle, filterFiles, facetKey, selectedFilters, currentTab } = props;
    // Determine how many total files there are
    let objSum = 0;
    // Create object to keep track of selected filters
    const selectedObj = {};
    Object.keys(facetObject).forEach((key) => {
        objSum += facetObject[key];
        if (Object.keys(selectedFilters).length > 0) {
            Object.keys(selectedFilters).forEach((filter) => {
                if (selectedFilters[filter].indexOf(key) > -1) {
                    selectedObj[key] = 'selected';
                }
            });
        }
    });
    // Sort results
    const sortedKeys = Object.keys(facetObject).sort((a, b) => (facetObject[b] - facetObject[a]));
    // Gray out facets with no terms for filtering
    const facetClass = Object.keys(facetObject).length === 0 ? ' empty-facet' : '';

    return (
        <div className={`facet ${facetTitle === 'Assembly' ? 'assembly-facet' : ''}${facetClass}`}>
            {facetTitle !== 'Assembly' ?
                <h5>{facetTitle}</h5>
            : null}
            {sortedKeys.map(item =>
                <button className={`facet-term-${item.replace(/\s/g, '')}-${currentTab} facet-term${selectedObj[item] ? ' selected' : ''}`} onClick={() => filterFiles(item, facetKey)} key={item}>
                    {facetTitle === 'Assembly' ?
                        <i className={`${selectedObj[item] ? 'icon icon-circle' : 'icon icon-circle-o'}`} />
                    : null}
                    <div className="facet-term__item">
                        <div className="facet-term__text">
                            <span>{item}</span>
                        </div>
                        { (facetTitle !== 'Assembly') ?
                            <div>
                                <div className="facet-term__count">{facetObject[item]}</div>
                                <div className="facet-term__bar" style={{ width: `${Math.ceil((facetObject[item] / objSum) * 100)}%` }} />
                            </div>
                        : null}
                    </div>
                </button>
            )}
        </div>
    );
};

FileFacet.propTypes = {
    facetObject: PropTypes.object.isRequired,
    facetTitle: PropTypes.string.isRequired,
    filterFiles: PropTypes.func.isRequired,
    facetKey: PropTypes.string.isRequired,
    selectedFilters: PropTypes.object.isRequired,
    currentTab: PropTypes.string.isRequired,
};

function addFilter(filterList, value, facet) {
    const currentFilters = filterList;
    // Check to see if there is already a filter for a facet or if it is the assembly facet which can only have one value
    if ((currentFilters[facet]) && facet !== 'assembly') {
        // If so, append the new falue
        currentFilters[facet] = [...currentFilters[facet], value];
    } else {
        // If not, create a new filter with the new value
        currentFilters[facet] = [value];
    }
    return currentFilters;
}

// Filter an array of objects by checking if the value of a property ('key') matches a given value ('keyValue')
function filterItems(array, key, keyValue) {
    return array.filter((el) => {
        // Check to see if there are multiple values selected for a facet
        if (keyValue.length > 1) {
            // if replicate facet, need to construct replicate value and check if value is present in selected values
            if (key === 'biological_replicates') {
                const replicate = (el.biological_replicates ? el.biological_replicates.sort((a, b) => a - b).join(', ') : '');
                return keyValue.indexOf(replicate) > -1;
            }
            // otherwise check if value is present in selected values
            return keyValue.indexOf(el[key]) > -1;
        }
        // if there is only one value selected for a facet, can just compare value to selected value
        if (key === 'biological_replicates') {
            const replicate = (el.biological_replicates ? el.biological_replicates.sort((a, b) => a - b).join(', ') : '');
            return replicate === keyValue[0];
        }
        if (key === 'assembly') {
            if (keyValue[0] === 'All assemblies' || (el.output_category === 'raw data')) {
                return true;
            }
            if (el.genome_annotation) {
                return (`${el[key]} ${el.genome_annotation}` === keyValue[0]);
            }
            return (el[key] === keyValue[0]);
        }
        return el[key] === keyValue[0];
    });
}

// Create objects for non-Assembly facets
function createFacetObject(propertyKey, fileList, filters) {
    // Initialize facet object
    const facetObject = {};
    // 'singleFilter' checks to see if there is only one filter selected (Assembly)
    const singleFilter = Object.keys(filters).length === 1;
    // Create list of files that satisfy all filters ('fileListFiltered')
    // Create list of files that is filtered by assembly only ('newFileList')
    let fileListFiltered = [...fileList];
    let newFileList = [...fileList];
    Object.keys(filters).forEach((filter) => {
        if (filter === 'assembly') {
            newFileList = filterItems(newFileList, filter, filters[filter]);
        }
        fileListFiltered = filterItems(fileListFiltered, filter, filters[filter]);
    });
    // If only 'Assembly' filter is selected, we want to collect all possible terms from 'newFile List' and then we are done
    if (singleFilter) {
        newFileList.forEach((file) => {
            let property = file[propertyKey];
            if (propertyKey === 'biological_replicates') {
                property = (file.biological_replicates ? file.biological_replicates.sort((a, b) => a - b).join(', ') : '');
                if (property === '') {
                    return;
                }
            }
            if (facetObject[property]) {
                facetObject[property] += 1;
            } else {
                facetObject[property] = 1;
            }
        });
    // If multiple filters are selected, it gets more complicated
    } else {
        // Start by adding properties from filtered list of files
        fileListFiltered.forEach((file) => {
            let property = file[propertyKey];
            if (propertyKey === 'biological_replicates') {
                property = (file.biological_replicates ? file.biological_replicates.sort((a, b) => a - b).join(', ') : '');
                if (property === '') {
                    return;
                }
            }
            if (facetObject[property]) {
                facetObject[property] += 1;
            } else {
                facetObject[property] = 1;
            }
        });
        // We also want to display terms that could be added if the user wants to increase the displayed results
        // These terms need to satisfy all of the filters that are already selected
        newFileList.forEach((file) => {
            let property = file[propertyKey];
            if (propertyKey === 'biological_replicates') {
                property = (file.biological_replicates ? file.biological_replicates.sort((a, b) => a - b).join(', ') : '');
                if (property === '') {
                    return;
                }
            }
            // We only want to look at files that are not in 'fileListFiltered'
            if (!(fileListFiltered.includes(file))) {
                // If this file's property was a filter, how many results would there be?
                let fakeFilters = Object.assign({}, filters);
                fakeFilters = addFilter(fakeFilters, property, propertyKey);
                let fakeFileList = newFileList;
                Object.keys(fakeFilters).forEach((f) => {
                    fakeFileList = filterItems(fakeFileList, f, fakeFilters[f]);
                });
                // If there would be results, add them
                if (fakeFileList.includes(file)) {
                    if (facetObject[property]) {
                        facetObject[property] += 1;
                    } else {
                        facetObject[property] = 1;
                    }
                // If there would be no results but this term is a filter, add it
                } else if (!(facetObject[property]) && filters[propertyKey] && filters[propertyKey].includes(property)) {
                    facetObject[property] = 0;
                }
            }
        });
    }
    return facetObject;
}


/**
 * Compile the usable experiment analysis objects into a form for rendering a dropdown of pipeline
 * labs. Export for Jest test.
 * @param {object} experiment Contains the analyses to convert into an pipeline labs dropdown
 * @param {array} files Array of all files from search that gets included in file gallery
 *
 * @return {array} Compiled analyses information, each element with the form:
 * {
 *      title: Analyses dropdown title -- `pipelineLab`+`assembly`
 *      pipelineLab: Pipeline processing lab title, e.g. "ENCODE4 uniform"
 *      assembly: Assembly and annotation string matching assembly facet terms
 *      assemblyAnnotationValue: Value used to sort the compiled analyses
 *      files: Array of files selected with the pipline lab and assembly
 * }
 */
const UNIFORM_PIPELINE_LAB = '/labs/encode-processing-pipeline/';
export const compileAnalyses = (experiment, files) => {
    let compiledAnalyses = [];
    if (experiment.analysis_objects && experiment.analysis_objects.length > 0) {
        // Get all the analysis objects that qualify for inclusion in the Pipeline facet.
        const qualifyingAnalyses = experiment.analysis_objects.filter((analysis) => {
            const rfas = _.uniq(analysis.pipeline_award_rfas);

            // More than one lab OK, as long as none of them is `UNIFORM_PIPELINE_LAB` --
            // `UNIFORM_PIPELINE_LAB` is only valid if alone.
            return (
                analysis.assembly
                && analysis.assembly !== 'mixed'
                && analysis.genome_annotation !== 'mixed'
                && analysis.pipeline_award_rfas.length === 1
                && analysis.pipeline_labs.length > 0
                && !(analysis.pipeline_labs.length === 1 && analysis.pipeline_labs[0] === UNIFORM_PIPELINE_LAB && rfas.length > 1)
            );
        });

        if (qualifyingAnalyses.length > 0) {
            // Group all the qualifying analyses' files by pipeline lab. Each pipeline lab title is
            // an object key with the value of an array containing all analysis objects included in
            // that lab. Also form the lab title here, prepending with the rfa (e.g. ENCODE3) for
            // `UNIFORM_PIPELINE_LAB`.
            const analysesByLab = _(qualifyingAnalyses).groupBy((analysis) => {
                if (analysis.pipeline_labs.length > 1) {
                    return 'Mixed';
                }

                // At this stage, we know analysis.pipeline_labs has one and only one element.
                if (analysis.pipeline_labs[0] !== UNIFORM_PIPELINE_LAB) {
                    return 'Lab custom';
                }
                return `${analysis.pipeline_award_rfas[0]} uniform`;
            });

            // Fill in the compiled object with the labs that group the files.
            compiledAnalyses = [];
            const fileIds = files.map(file => file['@id']);
            Object.keys(analysesByLab).forEach((pipelineLab) => {
                // For one lab, group all analyses by their assembly/annotation, then combine all
                // file arrays for those with matching pipeline lab, assembly/annotation, and RFA.
                const analysesByAssembly = _(analysesByLab[pipelineLab]).groupBy(analysis => `${analysis.assembly}${analysis.genome_annotation ? ` ${analysis.genome_annotation}` : ''}`);
                Object.keys(analysesByAssembly).forEach((assembly) => {
                    // Combine all analyses files that share the same pipeline lab, assembly, and
                    // annotation and add each to the compiled list. Filter out any not included in
                    // the experiment's files.
                    const assemblyFiles = _.uniq(analysesByAssembly[assembly].reduce((accFiles, analysis) => accFiles.concat(analysis.files), []).filter(file => fileIds.includes(file)));
                    if (assemblyFiles.length > 0) {
                        compiledAnalyses.push({
                            title: `${pipelineLab} ${assembly}`,
                            pipelineLab,
                            assembly,
                            assemblyAnnotationValue: computeAssemblyAnnotationValue(analysesByAssembly[assembly][0].assembly, analysesByAssembly[assembly][0].genome_annotation),
                            files: _.uniq(assemblyFiles),
                        });
                    }
                });
            });
        }
    }
    return _(compiledAnalyses).sortBy(compiledAnalysis => -compiledAnalysis.assemblyAnnotationValue);
};


/**
 * Display the analyses selector, a dropdown menu to choose which pipeline lab's files to view in
 * the file association graph.
 */
const AnalysesSelector = ({ analyses, selectedAnalysesIndex, handleAnalysesSelection }) => {
    React.useEffect(() => {
        if (selectedAnalysesIndex === -1 && analyses.length > 0) {
            // No selected pipeline lab analyses, but if we have at least one qualifying one,
            // automatically select the first one.
            handleAnalysesSelection(0);
        }
    });

    // Called when the user changes the dropdown selection. Tells the file gallery so it can update
    // its state that tracks this.
    const handleSelection = (e) => {
        handleAnalysesSelection(e.target.value);
    };

    // Only present the pipeline lab analyses matching the currently selected assembly/annotation.
    return (
        analyses.length > 0 ?
            <div className="analyses-selector analyses-selector--file-gallery-facets">
                <h4>Choose analysis</h4>
                <select className="analyses-selector" value={selectedAnalysesIndex} onChange={handleSelection}>
                    {analyses.map((analysis, index) => (
                        <option key={analysis.title} value={index}>{analysis.title}</option>
                    ))}
                </select>
            </div>
        : null
    );
};

AnalysesSelector.propTypes = {
    /** Compiled analyses for the currently viewed dataset */
    analyses: PropTypes.array.isRequired,
    /** Currently selected analysis index */
    selectedAnalysesIndex: PropTypes.number.isRequired,
    /** Called when the user chooses a pipeline lab from the menu */
    handleAnalysesSelection: PropTypes.func.isRequired,
};


const TabPanelFacets = (props) => {
    const { open, currentTab, filters, allFiles, filterFiles, toggleFacets, clearFileFilters, experimentType, analyses, selectedAnalysesIndex, handleAnalysesSelection } = props;

    // Filter file list to make sure it includes only files that should be displayed
    let fileList = allFiles;
    if (currentTab === 'browser') {
        fileList = filterForVisualizableFiles(fileList);
    }

    // Initialize assembly object
    const assembly = { 'All assemblies': 100 };

    // Create object for Assembly facet from list of all files
    // We do not count how many results there are for a given assembly because we will not display the bars
    fileList.forEach((file) => {
        if (file.genome_annotation && file.assembly && !assembly[`${file.assembly} ${file.genome_annotation}`]) {
            assembly[`${file.assembly} ${file.genome_annotation}`] = computeAssemblyAnnotationValue(file.assembly, file.genome_annotation);
        } else if (file.assembly && !assembly[file.assembly] && !(file.genome_annotation)) {
            assembly[file.assembly] = computeAssemblyAnnotationValue(file.assembly);
        }
    });

    // Create objects for non-Assembly facets
    const fileType = createFacetObject('file_type', fileList, filters);
    const outputType = createFacetObject('output_type', fileList, filters);
    let replicate;
    if (experimentType !== 'Annotation') {
        replicate = createFacetObject('biological_replicates', fileList, filters);
    }

    return (
        <div className={`file-gallery-facets ${open ? 'expanded' : 'collapsed'}`}>
            {(currentTab === 'graph' || currentTab === 'browser') && analyses.length > 0 && fileList.length > 0 ?
                <AnalysesSelector analyses={analyses} selectedAnalysesIndex={selectedAnalysesIndex} handleAnalysesSelection={handleAnalysesSelection} />
            :
                <React.Fragment>
                    <h4>Choose an assembly </h4>
                    <FileFacet facetTitle={'Assembly'} facetObject={assembly} filterFiles={filterFiles} facetKey={'assembly'} selectedFilters={filters} currentTab={currentTab} />
                </React.Fragment>
            }
            <h4>Filter files </h4>
            <button className="show-hide-facets" onClick={toggleFacets}>
                <i className={`${open ? 'icon icon-chevron-left' : 'icon icon-chevron-right'}`} />
            </button>
            { (Object.keys(filters).length >= 1 && !(Object.keys(filters).length === 1 && filters.assembly)) ?
                <button className="clear-file-facets" onClick={clearFileFilters}>
                    <i className="icon icon-times-circle" />
                    <span> Clear all filters</span>
                </button>
            : null }
            <FileFacet facetTitle={'File format'} facetObject={fileType} filterFiles={filterFiles} facetKey={'file_type'} selectedFilters={filters} currentTab={currentTab} />
            <FileFacet facetTitle={'Output type'} facetObject={outputType} filterFiles={filterFiles} facetKey={'output_type'} selectedFilters={filters} currentTab={currentTab} />
            {replicate ?
                <FileFacet facetTitle={'Replicates'} facetObject={replicate} filterFiles={filterFiles} facetKey={'biological_replicates'} selectedFilters={filters} currentTab={currentTab} />
            : null}
        </div>
    );
};

TabPanelFacets.propTypes = {
    open: PropTypes.bool.isRequired,
    currentTab: PropTypes.string.isRequired,
    filters: PropTypes.object.isRequired,
    allFiles: PropTypes.array.isRequired,
    filterFiles: PropTypes.func.isRequired,
    toggleFacets: PropTypes.func.isRequired,
    clearFileFilters: PropTypes.func.isRequired,
    experimentType: PropTypes.string.isRequired,
    /** Compiled analysis objects from the currently viewed dataset */
    analyses: PropTypes.array,
    /** Index of selected analysis */
    selectedAnalysesIndex: PropTypes.number.isRequired,
    /** Function to call when the user changes the currently selected pipeline lab analyses */
    handleAnalysesSelection: PropTypes.func.isRequired,
};

TabPanelFacets.defaultProps = {
    analyses: [],
};


// Function to render the file gallery, and it gets called after the file search results (for files associated with
// the displayed experiment) return.

class FileGalleryRendererComponent extends React.Component {
    constructor(props, context) {
        super(props, context);

        const loggedIn = !!(context.session && context.session['auth.userid']);
        const adminUser = loggedIn && !!(context.session_properties && context.session_properties.admin);
        const datasetFiles = props.data ? props.data['@graph'] : [];

        this.experimentType = props.context['@type'][0];

        // Initialize React state variables.
        this.state = {
            /** <select> value of selected assembly/annotation */
            selectedFilterValue: 'default',
            /** <select> value of selected browser */
            currentBrowser: '',
            /** Files selected for a browser */
            selectedBrowserFiles: [],
            /** Files associated with this dataset, filtered by all facets (assembly and others) */
            files: datasetFiles,
            /** Files associated with this dataset, filtered by assembly  */
            filesFilteredByAssembly: datasetFiles,
            /** Files associated with this dataset, for graph (filtered by everything but assembly)  */
            graphFiles: datasetFiles,
            /** All files associated with this dataset, with only assembly filtering  */
            allFiles: datasetFiles,
            /** True to exclude files with certain statuses */
            inclusionOn: adminUser,
            /** Array of objects with the assemblies and annotations available for the files */
            availableAssembliesAnnotations: collectAssembliesAnnotations(datasetFiles),
            /** Display facets sidebar */
            facetsOpen: true,
            /** Filters for files */
            fileFilters: {},
            /** Current tab: 'browser', 'graph', or 'tables' */
            currentTab: 'tables',
            /** Sorted compiled dataset analysis objects filtered by available assemblies */
            compiledAnalyses: compileAnalyses(props.context, datasetFiles),
            /** Index of currently/last selected `compiledAnalyses`. */
            selectedAnalysesIndex: 0,
        };

        /** Store characteristics of currently selected analyses menu item */
        this.selectedAnalysisProps = {
            assembly: '', // Assembly/annotation of currently selected analysis
            pipelineLab: '', // Pipeline lab of currently selected analysis
        };

        /** Used to see if related_files has been updated */
        this.prevRelatedFiles = [];
        this.relatedFilesRequested = false;

        // Bind `this` to non-React methods.
        this.setInfoNodeId = this.setInfoNodeId.bind(this);
        this.setInfoNodeVisible = this.setInfoNodeVisible.bind(this);
        this.updateFiles = this.updateFiles.bind(this);
        this.handleInclusionChange = this.handleInclusionChange.bind(this);
        this.filterForInclusion = this.filterForInclusion.bind(this);
        this.closeModal = this.closeModal.bind(this);
        this.handleNodeClick = this.handleNodeClick.bind(this);
        this.toggleFacets = this.toggleFacets.bind(this);
        this.filterFiles = this.filterFiles.bind(this);
        this.clearFileFilters = this.clearFileFilters.bind(this);
        this.handleTabClick = this.handleTabClick.bind(this);
        this.setAssemblyList = this.setAssemblyList.bind(this);

        this.handleBrowserChange = this.handleBrowserChange.bind(this);
        this.handleBrowserFileSelect = this.handleBrowserFileSelect.bind(this);
        this.handleVisualize = this.handleVisualize.bind(this);
        this.handleAssemblyAnnotationChange = this.handleAssemblyAnnotationChange.bind(this);
        this.getSelectedAssemblyAnnotation = this.getSelectedAssemblyAnnotation.bind(this);
        this.getAvailableBrowsers = this.getAvailableBrowsers.bind(this);
        this.saveSelectedAnalysesProps = this.saveSelectedAnalysesProps.bind(this);
        this.findCompiledAnalysesIndex = this.findCompiledAnalysesIndex.bind(this);
        this.resetCurrentBrowser = this.resetCurrentBrowser.bind(this);
        this.handleAnalysesSelection = this.handleAnalysesSelection.bind(this);
    }

    componentDidMount() {
        // Set the default filter after the graph has been analyzed once.
        if (!this.props.altFilterDefault) {
            this.setState({ selectedFilterValue: '0' });
        }
        // Determine how many visualizable files there are
        // const tempFiles = filterForVisualizableFiles(this.state.files);
        // If the graph is hidden and there are no visualizable files, set default tab to be table and set default assembly to be 'All assemblies'
        // if (this.props.hideGraph && tempFiles.length < 1) {
        if (this.props.hideGraph) {
            this.setState({ currentTab: 'tables' }, () => {
                this.filterFiles('All assemblies', 'assembly');
            });
        // If the graph is not hidden and there are no visualizable files, set default tab to be graph and set default assembly to be the most recent assembly
        } else {
        // } else if (tempFiles.length < 1) {
            // Display graph as default if there are no visualizable files
            let assemblyList = [];
            this.setState({ currentTab: 'graph' }, () => {
                // Determine available assemblies
                assemblyList = this.setAssemblyList(this.state.files);
                // We want to get the assembly with the highest assembly number (but not 'All assemblies')
                const newAssembly = Object.keys(assemblyList).reduce((a, b) => (((assemblyList[a] > assemblyList[b]) && (a !== 'All assemblies')) ? a : b));
                this.filterFiles(newAssembly, 'assembly');
            });
        // If there are visualizable files, set default tab to be browser and set default assembly to be the most recent assembly
        }
        //  else {
        //     // Determine available assemblies
        //     const assemblyList = this.setAssemblyList(this.state.files);
        //     // We want to get the assembly with the highest assembly number (but not 'All assemblies')
        //     const newAssembly = Object.keys(assemblyList).reduce((a, b) => (((assemblyList[a] > assemblyList[b]) && (a !== 'All assemblies')) ? a : b));
        //     this.filterFiles(newAssembly, 'assembly');
        // }
    }

    componentDidUpdate(prevProps, prevState) {
        const updateAssembly = prevState.currentTab !== this.state.currentTab || prevState.inclusionOn !== this.state.inclusionOn || prevProps.data !== this.props.data;
        this.updateFiles(!!(prevProps.session && prevProps.session['auth.userid']), updateAssembly);
    }

    // Called from child components when the selected node changes.
    setInfoNodeId(node) {
        this.setState({ infoNode: node });
    }

    setInfoNodeVisible(visible) {
        this.setState({ infoNodeVisible: visible });
    }

    setAssemblyList(allFiles) {
        const assembly = { 'All assemblies': 100 };
        let fileList = allFiles;
        if (this.state.currentTab === 'browser') {
            fileList = filterForVisualizableFiles(fileList);
        }
        fileList.forEach((file) => {
            if (file.genome_annotation && file.assembly && !assembly[`${file.assembly} ${file.genome_annotation}`]) {
                assembly[`${file.assembly} ${file.genome_annotation}`] = computeAssemblyAnnotationValue(file.assembly, file.genome_annotation);
            } else if (file.assembly && !assembly[file.assembly] && !(file.genome_annotation)) {
                assembly[file.assembly] = computeAssemblyAnnotationValue(file.assembly);
            }
        });
        return assembly;
    }

    /**
     * Get the currently selected assembly and annotation.
     * @param {string} filterValue Optional <select> value for current assembly/annotation.
     *                             Retrieved from state.selectedFilterValue if not given.
     */
    getSelectedAssemblyAnnotation(filterValue) {
        const currentFilterValue = filterValue || this.state.selectedFilterValue;
        if (currentFilterValue && this.state.availableAssembliesAnnotations[currentFilterValue]) {
            const selectedAssemblyAnnotation = this.state.availableAssembliesAnnotations[currentFilterValue];
            // On load, set assembly filter to be dropdown value
            if (!this.state.fileFilters.assembly) {
                this.filterFiles(selectedAssemblyAnnotation.assembly, 'assembly');
            }
            return {
                selectedBrowserAssembly: selectedAssemblyAnnotation.assembly,
                selectedBrowserAnnotation: selectedAssemblyAnnotation.annotation,
            };
        }
        return { selectedBrowserAssembly: null, selectedBrowserAnnotation: null };
    }

    /**
     * Given the currently selected assembly/annotation, get a list of the available browsers.
     * @param {string} filterValue Optional <select> value for current assembly/annotation.
     *                             state.selectedFilterValue used if not given.
     */
    getAvailableBrowsers(filterValue) {
        const { selectedBrowserAssembly } = this.getSelectedAssemblyAnnotation(filterValue);
        if (selectedBrowserAssembly && this.props.context.visualize && this.props.context.visualize[selectedBrowserAssembly]) {
            return visSortBrowsers(this.props.context.visualize[selectedBrowserAssembly]);
        }
        return [];
    }

    /**
     * Sets the `selectedAnalysisProps` property to track the corresponding selected assembly/annotation
     * and pipeline lab. Only pass in `compiledAnalyses` if it has been newly determined and might
     * not yet have propagated to `this.state.compiledAnalyses`.
     * @param {number} selectedAnalysesIndex New index of selected `compiledAnalyses`
     * @param {array} compiledAnalyses Compiled analyses for the experiment if newly determined
     */
    saveSelectedAnalysesProps(selectedAnalysesIndex, compiledAnalyses) {
        const localCompiledAnalyses = compiledAnalyses || this.state.compiledAnalyses;
        const selectedAnalyses = localCompiledAnalyses[selectedAnalysesIndex];
        this.selectedAnalysisProps = { assembly: selectedAnalyses.assembly, pipelineLab: selectedAnalyses.pipelineLab };
    }

    /**
     * Find the compiled analysis object best matching the given assembly/annotation and the last
     * selected pipeline lab and return its index into the compiled analyses array. Only pass in
     * `compiledAnalyses` if it has been newly determined and might not yet have propagated to
     * `this.state.compiledAnalyses`. If no appropriate compiled analyses can be found, return 0
     * which selects the first compiled analysis object.
     * @param {string} assembly Suggested assembly for matching an analysis
     * @param {array} compiledAnalyses Compiled analyses for the experiment if newly determined
     *
     * @return {object} Array index of most appropriate compiled analysis object
     */
    findCompiledAnalysesIndex(assembly, compiledAnalyses) {
        let compiledAnalysisIndex = 0;
        const localCompiledAnalyses = compiledAnalyses || this.state.compiledAnalyses;

        // Find all analyses matching the given assembly, then of those find one that also matches
        // the pipeline lab.
        const analysesWithMatchingAssembly = localCompiledAnalyses.filter(analysis => analysis.assembly === assembly);
        if (analysesWithMatchingAssembly.length > 0) {
            const matchingAnalysis = analysesWithMatchingAssembly.find(analysis => analysis.pipelineLab === this.selectedAnalysisProps.pipelineLab);
            if (matchingAnalysis) {
                // An analysis matched both assembly and pipeline lab. Get the index of its object
                // in the array of compiled analyses.
                compiledAnalysisIndex = localCompiledAnalyses.findIndex(analysis => analysis === matchingAnalysis);
            } else {
                // An analysis matched just the assembly. Get the index of the first compiled
                // analysis object with the matching assembly regardless of its pipeline lab.
                compiledAnalysisIndex = localCompiledAnalyses.findIndex(analysis => analysis === analysesWithMatchingAssembly[0]);
            }
        }
        return compiledAnalysisIndex;
    }

    /**
     * Called when the set of relevant files might have changed based on a user action. This makes
     * sure the current browser still makes sense, and resets it if not.
     * @param {string} filterValue Optional <select> value for current assembly/annotation or
     *                             state.selectedFilterValue if not given
     * @param {array}  currentFiles Optional files array or state.files if not given
     */
    resetCurrentBrowser(filterValue, currentFiles) {
        const browsers = this.getAvailableBrowsers(filterValue);
        const files = currentFiles || this.state.files;
        if (browsers.length > 0 && browsers.indexOf(this.state.currentBrowser) === -1) {
            // Current browser not available for new assembly/annotation. Set the current browser
            // to the first available.
            this.setState({
                currentBrowser: browsers[0],
                selectedBrowserFiles: visFilterBrowserFiles(files, browsers[0], true),
            });
        }
    }

    /**
     * Retrieve dataset.related_files to combine with the files directly associated with the
     * dataset and update the `files` state variable. I only check for length changes and not
     * content changes. In addition, collect all the assemblies/annotations associated with the
     * combined files so we can choose a visualization browser.
     */
    updateFiles(prevLoggedIn, updateAssembly) {
        const { context, data } = this.props;
        const { session } = this.context;
        const loggedIn = !!(session && session['auth.userid']);
        const relatedFileAtIds = context.related_files && context.related_files.length > 0 ? context.related_files : [];
        const datasetFiles = data ? data['@graph'] : [];

        // The number of related_files has changed (or we have related_files for the first time).
        // Request them and add them to the files from the original file request.
        let relatedPromise;
        if (loggedIn !== prevLoggedIn || !this.relatedFilesRequested) {
            relatedPromise = requestFiles(relatedFileAtIds, datasetFiles);
            this.relatedFilesRequested = true;
        } else {
            relatedPromise = Promise.resolve(this.prevRelatedFiles);
        }

        // Whether we have related_files or not, get all files' assemblies and annotations, and
        // the first genome browser for them.
        relatedPromise.then((relatedFiles) => {
            this.prevRelatedFiles = relatedFiles;
            let allFiles = datasetFiles.concat(relatedFiles);
            allFiles = this.filterForInclusion(allFiles);

            // If there are filters, filter the new files
            let filteredFiles = allFiles;
            const graphFiles = allFiles;
            let filesFilteredByAssembly = allFiles;
            if (Object.keys(this.state.fileFilters).length > 0) {
                Object.keys(this.state.fileFilters).forEach((fileFilter) => {
                    if (fileFilter === 'assembly') {
                        filesFilteredByAssembly = filterItems(filesFilteredByAssembly, fileFilter, this.state.fileFilters[fileFilter]);
                    }
                    filteredFiles = filterItems(filteredFiles, fileFilter, this.state.fileFilters[fileFilter]);
                });
            }

            if (!(_.isEqual(allFiles, this.state.allFiles))) {
                this.setState({ allFiles });
                this.setAssemblyList(this.state.allFiles);
                // From the new set of files, calculate the currently selected assembly and annotation to display in the graph and tables.
                this.setState({ availableAssembliesAnnotations: collectAssembliesAnnotations(allFiles) });
            }

            if (!(_.isEqual(filesFilteredByAssembly, this.state.filesFilteredByAssembly))) {
                this.setState({ filesFilteredByAssembly });
                this.setAssemblyList(this.state.allFiles);
            }

            if (!(_.isEqual(graphFiles, this.state.graphFiles))) {
                this.setState({ graphFiles });
            }

            if (!(_.isEqual(filteredFiles, this.state.files))) {
                this.setState({ files: filteredFiles });
            }
            this.resetCurrentBrowser(null, allFiles);

            // If new tab has been selected, we may need to update which assembly is chosen
            if (updateAssembly || loggedIn !== prevLoggedIn) {
                if (this.state.currentTab === 'tables') {
                    // Always set the table assembly to be 'All assemblies'
                    this.filterFiles('All assemblies', 'assembly');
                } else if (this.state.currentTab === 'browser' || this.state.currentTab === 'graph') {
                    let availableCompiledAnalyses = this.state.compiledAnalyses;
                    // Determine available assemblies
                    const assemblyList = this.setAssemblyList(allFiles);
                    // Update compiled analyses filtered by available assemblies
                    if (context.analysis_objects && context.analysis_objects.length > 0) {
                        const availableAssemblies = Object.keys(assemblyList);
                        availableCompiledAnalyses = compileAnalyses(context, allFiles).filter(analysis => availableAssemblies.includes(analysis.assembly));
                    }
                    if (availableCompiledAnalyses.length > 0) {
                        // Update the list of relevant compiled analyses and use it to select an
                        // appropriate selected pipeline menu based on the current assembly and the
                        // last-selected pipeline lab.
                        const currentAssembly = this.state.fileFilters.assembly[0];
                        const compiledAnalysesIndex = this.findCompiledAnalysesIndex(currentAssembly, availableCompiledAnalyses);
                        this.saveSelectedAnalysesProps(compiledAnalysesIndex, availableCompiledAnalyses);
                        this.setState({ compiledAnalyses: availableCompiledAnalyses, selectedAnalysesIndex: compiledAnalysesIndex });
                        // Find the matching assembly in compiledAnalyses, or the first otherwise.
                        const newAnalyses = availableCompiledAnalyses[compiledAnalysesIndex];
                        const newAssembly = newAnalyses.assembly;
                        if (newAssembly !== currentAssembly) {
                            this.filterFiles(newAssembly, 'assembly');
                        }
                    } else {
                        // Reset assembly filter if it is 'All assemblies' or is not in assemblyList
                        // Assembly is required for browser / graph and available assemblies may be different for graph and browser
                        // Do not reset if a particular assembly has already been chosen and it is an available option
                        this.setState({ compiledAnalyses: [] });
                        const currentAssembly = this.state.fileFilters.assembly[0];
                        let newAssembly;
                        if (currentAssembly === 'All assemblies' || !(assemblyList[currentAssembly])) {
                            // We want to get the assembly with the highest assembly number (but not 'All assemblies')
                            newAssembly = Object.keys(assemblyList).reduce((a, b) => (((assemblyList[a] > assemblyList[b]) && (a !== 'All assemblies')) ? a : b));
                            this.filterFiles(newAssembly, 'assembly');
                        }
                    }
                }
            }
        });
    }

    /**
     * Clear selected filters
     */
    clearFileFilters() {
        // Never delete the assembly filter
        this.setState({ fileFilters: { assembly: [this.state.fileFilters.assembly[0]] } });
    }

    /**
     * Called when the user selects an assembly/annotation to view.
     */
    handleAssemblyAnnotationChange(value) {
        this.setState({ selectedFilterValue: value });
        this.resetCurrentBrowser(value);
    }

    /**
     * Called when the user checks/unchecks the inclusion filter checkbox.
     */
    handleInclusionChange() {
        this.setState(state => ({ inclusionOn: !state.inclusionOn }));
    }

    // If the inclusionOn state property is enabled, we'll just display all the files we got. If
    // inclusionOn is disabled, we filter out any files with states in
    // FileGalleryRenderer.inclusionStatuses.
    filterForInclusion(files) {
        if (!this.state.inclusionOn) {
            // The user has chosen to not see files with statuses in
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
    handleNodeClick(meta, openInfoModal) {
        if (openInfoModal) {
            // Select the node and open the modal when the user clicks the node.
            this.setInfoNodeVisible(true);
            this.setInfoNodeId(meta);
        } else if (this.state.infoNode && (meta.id === this.state.infoNode.id)) {
            // If the user had already selected the node, deselect it.
            this.setInfoNodeId(null);
        } else {
            // Select the node without opening the modal when the user clicks the decoration.
            this.setInfoNodeId(meta);
        }
    }

    closeModal() {
        // Called when user wants to close modal somehow
        this.setInfoNodeVisible(false);
    }

    /**
     * Called when the user chooses a new browser from the menu.
     * @param {string} browser Name of browser user selected
     */
    handleBrowserChange(browser) {
        this.setState({
            currentBrowser: browser,
            selectedBrowserFiles: visFilterBrowserFiles(this.state.files, browser),
        });
    }

    /**
     * Called when the user clicks the Visualize button.
     */
    handleVisualize() {
        const { selectedBrowserAssembly } = this.getSelectedAssemblyAnnotation();
        visOpenBrowser(this.props.context, this.state.currentBrowser, selectedBrowserAssembly, this.state.selectedBrowserFiles, this.context.location_href);
    }

    /**
     * Called when the user selects/deselects a file for visualization in the file table.
     * @param {object} synthEvent Event from React event handler
     */
    handleBrowserFileSelect(synthEvent) {
        // The @id of the affected file is in the name of the clicked <input>.
        const clickedFileAtId = synthEvent.target.name;
        this.setState((state) => {
            const matchingIndex = state.selectedBrowserFiles.findIndex(file => file['@id'] === clickedFileAtId);
            if (matchingIndex === -1) {
                // Add clicked file to array of selected files.
                const matchingFile = state.files.find(file => file['@id'] === clickedFileAtId);
                return { selectedBrowserFiles: state.selectedBrowserFiles.concat(matchingFile) };
            }
            // Remove clicked file from array of selected files.
            return { selectedBrowserFiles: state.selectedBrowserFiles.slice(0, matchingIndex).concat(state.selectedBrowserFiles.slice(matchingIndex + 1)) };
        });
    }

    toggleFacets() {
        this.setState(prevState => ({ facetsOpen: !prevState.facetsOpen }));
    }

    filterFiles(value, facet) {
        if (facet === 'assembly') {
            this.setState({ selectedAssembly: value });
        }
        // Check to see if there are already filters
        if (Object.keys(this.state.fileFilters).length > 0) {
            const currentFilters = this.state.fileFilters;
            // Check to see if a filter for this facet exists, or an assembly filter which is an "OR" type filter not an "AND" type filter like the others
            if ((currentFilters[facet]) && facet !== 'assembly') {
                // There is a filter for this facet and this value
                if (currentFilters[facet].indexOf(value) > -1) {
                    // The value already exists in the filter so we want to reverse it
                    if (currentFilters[facet].length > 1) {
                        // This value is not the only value in the filter so we delete just that value
                        const allValues = currentFilters[facet];
                        allValues.splice(allValues.indexOf(value), 1);
                        currentFilters[facet] = allValues;
                    } else {
                        // There was only one value in the filter so we just delete the whole filter
                        delete currentFilters[facet];
                    }
                // There is a filter for this facet but not this value so we add it
                } else {
                    // Add a value to an existing filter
                    currentFilters[facet] = [...currentFilters[facet], value];
                }
            } else {
                // Create a new filter with the new value
                currentFilters[facet] = [value];
            }

            this.setState({ fileFilters: currentFilters });
        // If there are no filters yet, set this to be the first filter
        } else {
            this.setState({ fileFilters: { [facet]: [value] } });
        }
    }

    // Handle a click on a tab
    handleTabClick(tab) {
        if (tab !== this.state.currentTab) {
            this.setState({ currentTab: tab });
        }
    }

    // Called when the user selects a pipeline lab analyses.
    // @param {string} selectedAnalysesIndex Index in state.compiledAnalyses of newly selected pipeline
    handleAnalysesSelection(selectedAnalysesIndex) {
        this.saveSelectedAnalysesProps(selectedAnalysesIndex);
        this.setState({ selectedAnalysesIndex: +selectedAnalysesIndex });
        this.filterFiles(this.state.compiledAnalyses[selectedAnalysesIndex].assembly, 'assembly');
    }

    render() {
        const { context, schemas, hideGraph, showReplicateNumber } = this.props;
        let allGraphedFiles;
        let meta;
        // If filters other than assembly are chosen, we want to highlight the filtered files
        let highlightedFiles = [];
        if (Object.keys(this.state.fileFilters).length > 1) {
            highlightedFiles = this.filterForInclusion(this.state.files);
        }
        let graphIncludedFiles = this.filterForInclusion(this.state.graphFiles);
        const includedFiles = this.filterForInclusion(this.state.files);
        const facetFiles = this.filterForInclusion(this.state.allFiles);

        // Compile pipeline lab information for pipeline lab dropdown.
        if (this.state.compiledAnalyses.length > 0 && this.state.selectedAssembly) {
            // Filter renderable and visualizable files to include only those in the matching
            // analyses plus raw-data files. If no matching analyses, all files get included.
            const selectedAnalysis = this.state.compiledAnalyses[this.state.selectedAnalysesIndex];
            const graphAnalysesFiles = graphIncludedFiles.filter(file => selectedAnalysis.files.includes(file['@id']));
            if (graphAnalysesFiles.length > 0) {
                // Collect files that these files derive from, and add any missing ones to the
                // list of files to include in the graph.
                const assemblyAnnotation = this.state.selectedAssembly.split(' ');
                const additionalFiles = [];
                graphAnalysesFiles.forEach((analysisFile) => {
                    // Get the chain of files that analysisFile derives from, then check
                    // whether it needs to be added to the graph.
                    const derivedFiles = collectDerivedFroms(analysisFile, context, assemblyAnnotation[0], assemblyAnnotation[1], this.state.allFiles);
                    Object.keys(derivedFiles).forEach((derivedFileId) => {
                        if (derivedFiles[derivedFileId]) {
                            // See if the file is already included in the analysis' files.
                            const includedFile = graphAnalysesFiles.find(file => file['@id'] === derivedFileId);
                            if (!includedFile) {
                                // The derived-from file isn't already included, so add it
                                // if it can be found in allFiles (won't necessarily be).
                                const derivedFile = this.state.allFiles.find(file => file['@id'] === derivedFileId);
                                if (derivedFile) {
                                    additionalFiles.push(derivedFile);
                                }
                            }
                        }
                    });
                });

                // The graphed files now also include the derived-from files and raw files.
                graphIncludedFiles = graphAnalysesFiles.concat(_.uniq(additionalFiles), graphIncludedFiles.filter(file => file.output_category === 'raw data'));
            } else {
                // We know at this point there's nothing to graph nor browse for the selected
                // analysis.
                graphIncludedFiles = [];
            }
        }

        const fileTable = (
            <FileTable
                {...this.props}
                items={includedFiles}
                selectedFilterValue={this.state.selectedFilterValue}
                filterOptions={this.state.availableAssembliesAnnotations}
                graphedFiles={allGraphedFiles}
                handleFilterChange={this.handleFilterChange}
                browserOptions={{
                    browserFileSelectHandler: this.handleBrowserFileSelect,
                    currentBrowser: this.state.currentBrowser,
                    selectedBrowserFiles: this.state.selectedBrowserFiles,
                }}
                encodevers={globals.encodeVersion(context)}
                session={this.context.session}
                infoNodeId={this.state.infoNode}
                setInfoNodeId={this.setInfoNodeId}
                infoNodeVisible={this.state.infoNodeVisible}
                setInfoNodeVisible={this.setInfoNodeVisible}
                showFileCount
                noDefaultClasses
                adminUser={!!(this.context.session_properties && this.context.session_properties.admin)}
                showReplicateNumber={showReplicateNumber}
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
        const modalClass = meta ? `graph-modal--${modalTypeMap[meta.type]}` : '';
        const browsers = this.getAvailableBrowsers();
        const tabs = { browser: 'Genome browser', graph: 'Association graph', tables: 'File details' };

        return (
            <Panel>
                <PanelHeading addClasses="file-gallery-heading">
                    <h4>Files</h4>
                </PanelHeading>

                { (!hideGraph) ?
                    <div className="file-gallery-container">
                        <TabPanelFacets
                            open={this.state.facetsOpen}
                            currentTab={this.state.currentTab}
                            filters={this.state.fileFilters}
                            allFiles={facetFiles}
                            filterFiles={this.filterFiles}
                            toggleFacets={this.toggleFacets}
                            clearFileFilters={this.clearFileFilters}
                            experimentType={this.experimentType}
                            analyses={this.state.compiledAnalyses}
                            selectedAnalysesIndex={this.state.selectedAnalysesIndex}
                            handleAnalysesSelection={this.handleAnalysesSelection}
                        />
                        <TabPanel
                            tabPanelCss={`file-gallery-tab-bar ${this.state.facetsOpen ? '' : 'expanded'}`}
                            tabs={tabs}
                            decoration={<InclusionSelector inclusionOn={this.state.inclusionOn} handleInclusionChange={this.handleInclusionChange} />}
                            decorationClasses="file-gallery__inclusion-selector"
                            selectedTab={this.state.currentTab}
                            handleTabClick={this.handleTabClick}
                        >
                            <TabPanelPane key="browser">
                                <GenomeBrowser
                                    files={includedFiles}
                                    label={'file gallery'}
                                    expanded={this.state.facetsOpen}
                                    assembly={this.state.selectedAssembly}
                                    displaySort
                                />
                            </TabPanelPane>
                            <TabPanelPane key="graph">
                                <FileGraph
                                    dataset={context}
                                    files={graphIncludedFiles}
                                    highlightedFiles={highlightedFiles}
                                    infoNode={this.state.infoNode}
                                    selectedAssembly={this.state.selectedAssembly ? this.state.selectedAssembly.split(' ')[0] : undefined}
                                    selectedAnnotation={this.state.selectedAssembly ? this.state.selectedAssembly.split(' ')[1] : undefined}
                                    schemas={schemas}
                                    colorize={this.state.inclusionOn}
                                    handleNodeClick={this.handleNodeClick}
                                    loggedIn={!!(this.context.session && this.context.session['auth.userid'])}
                                    auditIndicators={this.props.auditIndicators}
                                    auditDetail={this.props.auditDetail}
                                />
                            </TabPanelPane>
                            <TabPanelPane key="tables">
                                <FilterControls
                                    selectedFilterValue={this.state.selectedFilterValue}
                                    filterOptions={this.state.availableAssembliesAnnotations}
                                    inclusionOn={this.state.inclusionOn}
                                    browsers={browsers}
                                    currentBrowser={this.state.currentBrowser}
                                    selectedBrowserFiles={this.state.selectedBrowserFiles}
                                    handleAssemblyAnnotationChange={this.handleAssemblyAnnotationChange}
                                    handleInclusionChange={this.handleInclusionChange}
                                    browserChangeHandler={this.handleBrowserChange}
                                    visualizeHandler={this.handleVisualize}
                                />
                                {/* If logged in and dataset is released, need to combine search of files that reference
                                    this dataset to get released and unreleased ones. If not logged in, then just get
                                    files from dataset.files */}
                                {fileTable}
                            </TabPanelPane>
                        </TabPanel>
                    </div>
                :
                    <div>
                        <FilterControls
                            selectedFilterValue={this.state.selectedFilterValue}
                            filterOptions={this.state.availableAssembliesAnnotations}
                            inclusionOn={this.state.inclusionOn}
                            browsers={browsers}
                            currentBrowser={this.state.currentBrowser}
                            selectedBrowserFiles={this.state.selectedBrowserFiles}
                            handleAssemblyAnnotationChange={this.handleAssemblyAnnotationChange}
                            handleInclusionChange={this.handleInclusionChange}
                            browserChangeHandler={this.handleBrowserChange}
                            visualizeHandler={this.handleVisualize}
                        />
                        {fileTable}
                    </div>
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
    /** Dataset whose files we're rendering */
    context: PropTypes.object.isRequired,
    /** File data retrieved from search request */
    data: PropTypes.object,
    /** Schemas for the entire system; used for QC property titles */
    schemas: PropTypes.object,
    /** True to hide graph display */
    hideGraph: PropTypes.bool,
    /** True to default to All Assemblies and Annotations */
    altFilterDefault: PropTypes.bool,
    /** Inherited from auditDecor HOC */
    auditIndicators: PropTypes.func.isRequired,
    /** Inherited from auditDecor HOC */
    auditDetail: PropTypes.func.isRequired,
    /** True to show replicate number */
    showReplicateNumber: PropTypes.bool,
    /** ENCODE session object from <App> */
    session: PropTypes.object.isRequired,
};

FileGalleryRendererComponent.defaultProps = {
    data: null,
    schemas: null,
    hideGraph: false,
    altFilterDefault: false,
    showReplicateNumber: true,
};

FileGalleryRendererComponent.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
    location_href: PropTypes.string,
    navigate: PropTypes.func,
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

CollapsingTitle.defaultProps = {
    collapsed: false,
};


// Display a filtering <select>. `filterOptions` is an array of objects with two properties:
// `assembly` and `annotation`. Both are strings that get concatenated to form each menu item. The
// value of each <option> is its zero-based index.
const FilterMenu = (props) => {
    const { filterOptions, handleFilterChange, selectedFilterValue } = props;

    return (
        <select className="form-control--select" value={selectedFilterValue} onChange={handleFilterChange}>
            {filterOptions.map((option, i) =>
                <option key={`${option.assembly}${option.annotation}`} value={i}>{`${option.assembly + (option.annotation ? ` ${option.annotation}` : '')}`}</option>
            )}
        </select>
    );
};

FilterMenu.propTypes = {
    selectedFilterValue: PropTypes.string, // Currently selected filter
    filterOptions: PropTypes.array.isRequired, // Contents of the filtering menu
    handleFilterChange: PropTypes.func.isRequired, // Call when a filtering option changes
};

FilterMenu.defaultProps = {
    selectedFilterValue: 'default',
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

    if (selectedFile && Object.keys(selectedFile).length > 0) {
        let contributingAccession;

        if (node.metadata.contributing) {
            const accessionStart = selectedFile.dataset.indexOf('/', 1) + 1;
            const accessionEnd = selectedFile.dataset.indexOf('/', accessionStart) - accessionStart;
            contributingAccession = selectedFile.dataset.substr(accessionStart, accessionEnd);
        }
        const dateString = !!selectedFile.date_created && dayjs.utc(selectedFile.date_created).format('YYYY-MM-DD');
        header = (
            <div className="graph-modal-header__content">
                <h2>{selectedFile.file_type} <a href={selectedFile['@id']}>{selectedFile.title}</a></h2>
            </div>
        );
        const fileQualityMetrics = selectedFile.quality_metrics.filter(qc => loggedIn || qc.status === 'released');

        body = (
            <div>
                <dl className="key-value">
                    <div data-test="status">
                        <dt>Status</dt>
                        <dd><Status item={selectedFile} inline /></dd>
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

                    {selectedFile.biological_replicates && selectedFile.biological_replicates.length > 0 ?
                        <div data-test="bioreplicate">
                            <dt>Biological replicate(s)</dt>
                            <dd>{`[${selectedFile.biological_replicates.join(',')}]`}</dd>
                        </div>
                    : null}

                    {selectedFile.biological_replicates && selectedFile.biological_replicates.length > 0 ?
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

                    {selectedFile.cropped_read_length !== undefined ?
                        <div data-test="croppedreadlength">
                            <dt>Cropped read length</dt>
                            <dd>{selectedFile.cropped_read_length}</dd>
                        </div>
                    : null}

                    {selectedFile.cropped_read_length_tolerance !== undefined ?
                        <div data-test="croppedreadlengthtolerance">
                            <dt>Cropped read length tolerance</dt>
                            <dd>{selectedFile.cropped_read_length_tolerance}</dd>
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

                    {selectedFile.analysis_step_version && selectedFile.analysis_step_version.software_versions && selectedFile.analysis_step_version.software_versions.length > 0 ?
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

                    {fileQualityMetrics.length > 0 ?
                        <div data-test="fileqc">
                            <dt>File quality metrics</dt>
                            <dd className="file-qc-buttons">
                                {fileQualityMetrics.map(qc =>
                                    <FileQCButton key={qc['@id']} qc={qc} file={selectedFile} schemas={node.schemas} handleClick={qcClick} />
                                )}
                            </dd>
                        </div>
                    : null}

                    {selectedFile.submitter_comment ?
                        <div data-test="submittercomment">
                            <dt>Submitter comment</dt>
                            <dd>{selectedFile.submitter_comment}</dd>
                        </div>
                    : null}
                </dl>

                {auditsDisplayed(selectedFile.audit, session) ?
                    <div className="graph-modal-audits">
                        <h5>File audits:</h5>
                        {auditIndicators ? auditIndicators(selectedFile.audit, 'file-audit', { session, sessionProperties }) : null}
                        {auditDetail ? auditDetail(selectedFile.audit, 'file-audit', { session, sessionProperties }) : null}
                    </div>
                : null}
            </div>
        );
    } else {
        header = (
            <div className="graph-modal-header__content"><h2>Unknown file</h2></div>
        );
        body = <p className="browser-error">No information available</p>;
    }
    return { header, body, type: 'File' };
};

globals.graphDetail.register(FileDetailView, 'File');


export const CoalescedDetailsView = function CoalescedDetailsView(node) {
    let header;
    let body;

    if (node.metadata.coalescedFiles && node.metadata.coalescedFiles.length > 0) {
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
                getValue: item => dayjs.utc(item.date_created).format('YYYY-MM-DD'),
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
                display: item => <Status item={item} badgeSize="small" />,
            },
        };

        header = (
            <div className="graph-modal-header__content">
                <h2>Selected contributing files</h2>
            </div>
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
            <div className="graph-modal-header__content">
                <h2>Unknown files</h2>
            </div>
        );
        body = <p className="browser-error">No information available</p>;
    }
    return { header, body, type: 'File' };
};

globals.graphDetail.register(CoalescedDetailsView, 'Coalesced');
