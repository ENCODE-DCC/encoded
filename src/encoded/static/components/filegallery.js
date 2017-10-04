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
import { FileGraph } from './graph';
import { requestFiles, DownloadableAccession, BrowserSelector } from './objectutils';
import { qcModalContent, qcIdToDisplay } from './quality_metric';
import { softwareVersionList } from './software';
import { SortTablePanel, SortTable } from './sorttable';
import StatusLabel from './statuslabel';


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
        return file => (file.restricted ? 'file-restricted' : '');
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
            metadata: {
                ref: file,
            },
        };
        const meta = FileDetailView(node, null, null, null, this.context.session, this.context.sessionProperties);
//            meta = globals.graphDetail.lookup(node)(node, this.handleNodeClick, this.props.auditIndicators, this.props.auditDetail, this.context.session, this.context.sessionProperties);
//        meta.type = node['@type'][0];
// Called when the user clicks a file in the table to bring up a file modal in the graph.
        this.props.setInfoNodeId(meta);
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
        display: item => <div className="characterization-meta-data"><StatusLabel status={item.status} /></div>,
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
        display: item => <div className="characterization-meta-data"><StatusLabel status={item.status} /></div>,
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

                                    // Determine if accession should be a button or not
                                    const buttonEnabled = !!(meta.graphedFiles && meta.graphedFiles[file['@id']]);

                                    return (
                                        <tr key={file['@id']} className={file.restricted ? 'file-restricted' : ''}>
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
                                            <td className={`${pairClass} characterization-meta-data`}><StatusLabel status={file.status} /></td>
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
                                    file.restricted ? 'file-restricted' : null,
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
                                        <td className="characterization-meta-data"><StatusLabel status={file.status} /></td>
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
                                        <tr key={file['@id']} className={file.restricted ? 'file-restricted' : ''}>
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
                                            <td className={`${pairClass} characterization-meta-data`}><StatusLabel status={file.status} /></td>
                                        </tr>
                                    );
                                });
                            })}
                            {nonpairedFiles.sort(sortBioReps).map((file, i) => {
                                // Prepare for run_type display
                                const rowClasses = [
                                    pairedKeys.length && i === 0 ? 'table-raw-separator' : null,
                                    file.restricted ? 'file-restricted' : null,
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
                                        <td className="characterization-meta-data"><StatusLabel status={file.status} /></td>
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
                        <label htmlFor="filterIncArchive">Include revoked / archived files
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


// Function to render the file gallery, and it gets called after the file search results (for files associated with
// the displayed experiment) return.

class FileGalleryRendererComponent extends React.Component {
    constructor() {
        super();

        // Initialize React state variables.
        this.state = {
            selectedFilterValue: 'default', // <select> value of selected filter
            meta: null, // @id of node whose info panel is open
            infoModalOpen: false, // True if info modal is open
            relatedFiles: [],
            inclusionOn: false, // True to exclude files with certain statuses
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
    setInfoNodeId(meta) {
        this.setState({ meta });
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
                infoNodeId={this.state.infoNodeId}
                setInfoNodeId={this.setInfoNodeId}
                infoNodeVisible={this.state.infoNodeVisible}
                setInfoNodeVisible={this.setInfoNodeVisible}
                showFileCount
                noDefaultClasses
                adminUser={!!(this.context.session_properties && this.context.session_properties.admin)}
            />
        );

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
                            {!hideGraph ?
                                <FileGraph
                                    dataset={context}
                                    files={includedFiles}
                                    selectedAssembly={selectedAssembly}
                                    selectedAnnotation={selectedAnnotation}
                                    schemas={schemas}
                                    handleNodeClick={this.handleNodeClick}
                                    auditIndicators={this.props.auditIndicators}
                                    auditDetail={this.props.auditDetail}
                                    handleNodeClick={this.handleNodeClick}
                                />
                            : null}
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

                {this.state.meta && this.state.infoNodeVisible ?
                    <Modal closeModal={this.closeModal}>
                        <ModalHeader closeModal={this.closeModal}>
                            {this.state.meta.header}
                        </ModalHeader>
                        <ModalBody>
                            {this.state.meta.body}
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
        const qcId = `qc:${this.props.qc['@id']}${this.props.file['@id']}`;
        this.props.handleClick(qcId);
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
                                    <FileQCButton key={qc['@id']} qc={qc} file={selectedFile} handleClick={qcClick} />,
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
    return { header, body };
};

globals.graphDetail.register(FileDetailView, 'File');
