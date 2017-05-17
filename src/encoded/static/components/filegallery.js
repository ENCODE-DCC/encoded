import React from 'react';
import PropTypes from 'prop-types';
import createReactClass from 'create-react-class';
import _ from 'underscore';
import moment from 'moment';
import globals from './globals';
import { Panel, PanelHeading } from '../libs/bootstrap/panel';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../libs/bootstrap/modal';
import { auditDecor, auditsDisplayed, AuditIcon } from './audit';
import StatusLabel from './statuslabel';
import { requestFiles, DownloadableAccession, BrowserSelector } from './objectutils';
import { Graph, JsonGraph } from './graph';
import { qcModalContent, qcIdToDisplay } from './quality_metric';
import { softwareVersionList } from './software';
import { FetchedData, Param } from './fetched';
import { collapseIcon } from '../libs/svg-icons';
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


export const FileTable = createReactClass({
    propTypes: {
        items: PropTypes.array.isRequired, // Array of files to appear in the table
        graphedFiles: PropTypes.object, // Specifies which files are in the graph
        filePanelHeader: PropTypes.object, // Table header component
        encodevers: PropTypes.string, // ENCODE version of the experiment
        selectedFilterValue: PropTypes.string, // Selected filter from popup menu
        filterOptions: PropTypes.array, // Array of assambly/annotation from file array
        handleFilterChange: PropTypes.func, // Called when user changes filter
        anisogenic: PropTypes.bool, // True if experiment is anisogenic
        showFileCount: PropTypes.bool, // True to show count of files in table
        setInfoNodeId: PropTypes.func, // Function to call to set the currently selected node ID
        setInfoNodeVisible: PropTypes.func, // Function to call to set the visibility of the node's modal
        session: PropTypes.object, // Persona user session
        adminUser: PropTypes.bool, // True if user is an admin user
        noDefaultClasses: PropTypes.bool, // True to strip SortTable panel of default CSS classes
    },

    getInitialState: function () {
        return {
            maxWidth: 'auto', // Width of widest table
            collapsed: { // Keeps track of which tables are collapsed
                raw: false,
                rawArray: false,
                proc: false,
                ref: false,
            },
        };
    },

    cv: {
        maxWidthRef: '', // ref key of table with this.state.maxWidth width
        maxWidthNode: null, // DOM node of table with this.state.maxWidth width
    },

    // Configuration for process file table
    procTableColumns: {
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
    },

    // Configuration for reference file table
    refTableColumns: {
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
    },

    fileClick: function (nodeId) {
        // Called when the user clicks a file in the table to bring up a file modal in the graph.
        this.props.setInfoNodeId(nodeId);
        this.props.setInfoNodeVisible(true);
    },

    handleCollapse: function (table) {
        // Handle a click on a collapse button by toggling the corresponding tableCollapse state var
        const collapsed = _.clone(this.state.collapsed);
        collapsed[table] = !collapsed[table];
        this.setState({ collapsed: collapsed });
    },

    handleCollapseProc: function () {
        this.handleCollapse('proc');
    },

    handleCollapseRef: function () {
        this.handleCollapse('ref');
    },

    rowClasses: file => (file.restricted ? 'file-restricted' : ''),

    hoverDL: (hovering, fileUuid) => {
        this.setState({ restrictedTip: hovering ? fileUuid : '' });
    },

    render: function () {
        const {
            items,
            graphedFiles,
            filePanelHeader,
            encodevers,
            selectedFilterValue,
            filterOptions,
            handleFilterChange,
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
                                encodevers: encodevers,
                                anisogenic: anisogenic,
                                fileClick: this.fileClick,
                                graphedFiles: graphedFiles,
                                session: session,
                                loggedIn: loggedIn,
                                adminUser: adminUser,
                            }}
                        />
                        <RawFileTable
                            files={files.rawArray}
                            meta={{
                                encodevers: encodevers,
                                anisogenic: anisogenic,
                                fileClick: this.fileClick,
                                graphedFiles: graphedFiles,
                                session: session,
                                loggedIn: loggedIn,
                                adminUser: adminUser,
                            }}
                        />
                        <SortTable
                            title={
                                <CollapsingTitle
                                    title="Processed data" collapsed={this.state.collapsed.proc}
                                    handleCollapse={this.handleCollapseProc}
                                    selectedFilterValue={selectedFilterValue}
                                    filterOptions={filterOptions}
                                    handleFilterChange={handleFilterChange}
                                />
                            }
                            rowClasses={this.rowClasses}
                            collapsed={this.state.collapsed.proc}
                            list={files.proc}
                            columns={this.procTableColumns}
                            sortColumn="biological_replicates"
                            meta={{
                                encodevers: encodevers,
                                anisogenic: anisogenic,
                                hoverDL: this.hoverDL,
                                restrictedTip: this.state.restrictedTip,
                                fileClick: this.fileClick,
                                graphedFiles: graphedFiles,
                                loggedIn: loggedIn,
                                adminUser: adminUser,
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
                            columns={this.refTableColumns}
                            meta={{
                                encodevers: encodevers,
                                anisogenic: anisogenic,
                                hoverDL: this.hoverDL,
                                restrictedTip: this.state.restrictedTip,
                                fileClick: this.fileClick,
                                graphedFiles: graphedFiles,
                                loggedIn: loggedIn,
                                adminUser: adminUser,
                            }}
                        />
                    </SortTablePanel>
                </div>
            );
        }
        return null;
    },
});


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


const RawSequencingTable = createReactClass({
    propTypes: {
        files: PropTypes.array, // Raw files to display
        meta: PropTypes.object, // Extra metadata in the same format passed to SortTable
    },

    getInitialState: function () {
        return {
            collapsed: false, // Collapsed/uncollapsed state of table
            restrictedTip: '', // UUID of file with tooltip showing
        };
    },

    handleCollapse: function () {
        // Handle a click on a collapse button by toggling the corresponding tableCollapse state var
        this.setState({ collapsed: !this.state.collapsed });
    },

    hoverDL: function (hovering, fileUuid) {
        this.setState({ restrictedTip: hovering ? fileUuid : '' });
    },

    render: function () {
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
                                                <td rowSpan={groupFiles.length} className={`${bottomClass} merge-right + table-raw-merged`}>{groupFiles[0].replicate.library.accession}</td>
                                            : null}
                                            <td className={pairClass}>
                                                <DownloadableAccession file={file} buttonEnabled={buttonEnabled} clickHandler={meta.fileClick ? meta.fileClick : null} loggedIn={loggedIn} adminUser={adminUser} />
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
    },
});


const RawFileTable = createReactClass({
    propTypes: {
        files: PropTypes.array, // Raw sequencing files to display
        meta: PropTypes.object, // Extra metadata in the same format passed to SortTable
    },

    getInitialState: function () {
        return {
            collapsed: false, // Collapsed/uncollapsed state of table
            restrictedTip: '', // UUID of file with tooltip showing
        };
    },

    handleCollapse: function () {
        // Handle a click on a collapse button by toggling the corresponding tableCollapse state var
        this.setState({ collapsed: !this.state.collapsed });
    },

    hoverDL: function (hovering, fileUuid) {
        this.setState({ restrictedTip: hovering ? fileUuid : '' });
    },

    render: function () {
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
    },
});


// Called once searches for unreleased files returns results in this.props.items. Displays both released and
// unreleased files.
export const DatasetFiles = createReactClass({
    propTypes: {
        items: PropTypes.array, // Array of files retrieved
    },

    render: function () {
        const { items } = this.props;

        const files = _.uniq((items && items.length) ? items : []);
        if (files.length) {
            return <FileTable {...this.props} items={files} />;
        }
        return null;
    },
});


// File display widget, showing a facet list, a table, and a graph (and maybe a BioDalliance).
// This component only triggers the data retrieval, which is done with a search for files associated
// with the given experiment (in this.props.context). An odd thing is we specify query-string parameters
// to the experiment URL, but they apply to the file search -- not the experiment itself.
export const FileGallery = createReactClass({
    propTypes: {
        context: PropTypes.object, // Dataset object whose files we're rendering
        encodevers: PropTypes.string, // ENCODE version number
        anisogenic: PropTypes.bool, // True if anisogenic experiment
        hideGraph: PropTypes.bool, // T to hide graph display
        altFilterDefault: PropTypes.bool, // T to default to All Assemblies and Annotations
    },

    contextTypes: {
        session: PropTypes.object, // Login information
        location_href: PropTypes.string, // URL of this experiment page, including query string stuff
    },

    render: function () {
        const { context, encodevers, anisogenic, hideGraph, altFilterDefault } = this.props;

        return (
            <FetchedData ignoreErrors>
                <Param name="data" url={globals.unreleased_files_url(context)} />
                <Param name="schemas" url="/profiles/" />
                <FileGalleryRenderer context={context} session={this.context.session} encodevers={encodevers} anisogenic={anisogenic} hideGraph={hideGraph} altFilterDefault={altFilterDefault} />
            </FetchedData>
        );
    },
});


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


// Handle graphing throws. Exported for Jest tests.
export function GraphException(message, file0, file1) {
    this.message = message;
    if (file0) {
        this.file0 = file0;
    }
    if (file1) {
        this.file1 = file1;
    }
}


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


export function assembleGraph(context, session, infoNodeId, files, filterAssembly, filterAnnotation) {
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

    const derivedFileIds = _.memoize(rDerivedFileIds, file => file['@id']);
    const genQcId = _.memoize(rGenQcId, (metric, file) => metric['@id'] + file['@id']);

    // Begin collecting up information about the files from the search result, and gathering their
    // QC and analysis pipeline information.
    const graphedFiles = {}; // All files in the graph, so table can link to it.
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
        if ((file.assembly === filterAssembly) && ((!file.genome_annotation && !filterAnnotation) || (file.genome_annotation === filterAnnotation))) {
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

    // Generate a list of file @ids that other files (matching the current assembly and annotation)
    // derive from (i.e. files referenced in other files' derived_from). allDerivedFroms is keyed
    // by the derived-from file @id (whether it matches the current assembly and annotation or not)
    // and has an array of all files that derive from it for its value. So for example:
    //
    // allDerivedFroms = {
    //     /files/<matching accession>: [matching file, matching file],
    //     /files/<contributing accession>: [matching file, matching file],
    //     /files/<missing accession>: [matching file, matching file],
    // }
    const allDerivedFroms = {};
    Object.keys(matchingFiles).forEach((matchingFileId) => {
        const matchingFile = matchingFiles[matchingFileId];
        if (matchingFile.derived_from && matchingFile.derived_from.length) {
            matchingFile.derived_from.forEach((derivedFromAtId) => {
                // Copy reference to allFiles copy of file. Will be undefined for missing and
                // contributing files.
                if (allDerivedFroms[derivedFromAtId]) {
                    // Already saw a file derive from this one, so add the new reference to the end
                    // of the array of derived-from files.
                    allDerivedFroms[derivedFromAtId].push(matchingFile);
                } else {
                    // Never saw a file derive from this one, so make a new array with a reference
                    // to it.
                    allDerivedFroms[derivedFromAtId] = [matchingFile];
                }
            });
        }
    });
    // Remember, at this stage allDerivedFroms includes keys for missing files, files not matching
    // the chosen assembly/annotation, and contributing files.

    // Filter any "island" files out of matchingFiles -- that is, files that derive from no other
    // files, and no other files derive from it.
    matchingFiles = (function () {
        const noIslandFiles = {};
        Object.keys(matchingFiles).forEach((matchingFileId) => {
            const matchingFile = matchingFiles[matchingFileId];
            if ((matchingFile.derived_from && matchingFile.derived_from.length) || allDerivedFroms[matchingFileId]) {
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
    // At this stage, any files in matchingFiles will be rendered. We just have to figure out what
    // other files need rendering, like raw sequencing files, contributing files, and derived-from
    // files that have a non-matching annotation and assembly.

    const allReplicates = {}; // All file's replicates as keys; each key references an array of files
    Object.keys(matchingFiles).forEach((matchingFileId) => {
        // If the file is part of a single biological replicate, add it to an array of files, where
        // the arrays are in an object keyed by their relevant biological replicate number.
        const matchingFile = matchingFiles[matchingFileId];
        let replicateNum = (matchingFile.biological_replicates && matchingFile.biological_replicates.length === 1) ? matchingFile.biological_replicates[0] : undefined;
        if (replicateNum) {
            if (allReplicates[replicateNum]) {
                allReplicates[replicateNum].push(matchingFile);
            } else {
                allReplicates[replicateNum] = [matchingFile];
            }
        }

        // Add each file that a matching file derives from to the replicates.
        if (matchingFile.derived_from && matchingFile.derived_from.length) {
            matchingFile.derived_from.forEach((derivedFromAtId) => {
                const file = allFiles[derivedFromAtId];
                if (file) {
                    replicateNum = (file.biological_replicates && file.biological_replicates.length === 1) ? file.biological_replicates[0] : undefined;
                    if (replicateNum) {
                        if (allReplicates[replicateNum]) {
                            allReplicates[replicateNum].push(matchingFile);
                        } else {
                            allReplicates[replicateNum] = [matchingFile];
                        }
                    }
                }
            });
        }
    });

    // Make a list of contributing files that matchingFiles files derive from.
    const usedContributingFiles = {};
    if (context.contributing_files && context.contributing_files.length) {
        context.contributing_files.forEach((contributingFileAtId) => {
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

    // Create an empty graph architecture that we fill in next.
    const jsonGraph = new JsonGraph(context.accession);

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
        const fileNodeId = `file:${file['@id']}`;
        const fileNodeLabel = `${file.title} (${file.output_type})`;
        const fileCssClass = `pipeline-node-file${infoNodeId === fileNodeId ? ' active' : ''}`;
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
                    class: `pipeline-node-qc-metric${infoNodeId === qcId ? ' active' : ''}`,
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

        // Add the matching file to our list of "all" graphed files.
        graphedFiles[fileId] = file;

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
                    cssClass: `pipeline-node-analysis-step${(infoNodeId === stepId ? ' active' : '') + (error ? ' error' : '')}`,
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
    });

    // Go through each derived-from file and add it to our graph.
    Object.keys(allDerivedFroms).forEach((fileId) => {
        const file = allFiles[fileId];
        if (file && !matchingFiles[fileId]) {
            const fileNodeId = `file:${file['@id']}`;
            const fileNodeLabel = `${file.title} (${file.output_type})`;
            const fileCssClass = `pipeline-node-file${infoNodeId === fileNodeId ? ' active' : ''}`;
            const fileRef = file;
            const replicateNode = (file.biological_replicates && file.biological_replicates.length === 1) ? jsonGraph.getNode(`rep:${file.biological_replicates[0]}`) : null;

            jsonGraph.addNode(fileNodeId, fileNodeLabel, {
                cssClass: fileCssClass,
                type: 'File',
                shape: 'rect',
                cornerRadius: 16,
                parentNode: replicateNode,
                ref: fileRef,
            });

            // Add the derived-from file to our list of "all" graphed files.
            graphedFiles[fileId] = file;
        }
    });

    // Go through each derived-from contributing file and add it to our graph.
    Object.keys(usedContributingFiles).forEach((fileAtId) => {
        const fileNodeId = `file:${fileAtId}`;
        const fileNodeLabel = `${globals.atIdToAccession(fileAtId)}`;
        const fileCssClass = `pipeline-node-file contributing${infoNodeId === fileNodeId ? ' active' : ''}`;

        jsonGraph.addNode(fileNodeId, fileNodeLabel, {
            cssClass: fileCssClass,
            type: 'File',
            shape: 'rect',
            cornerRadius: 16,
            contributing: fileAtId,
            ref: {},
        });
    });

    // Now add coalesced nodes to the graph.
    Object.keys(coalescingGroups).forEach((groupHash) => {
        const coalescingGroup = coalescingGroups[groupHash];
        if (coalescingGroup.length) {
            const fileNodeId = `coalesced:${groupHash}`;
            const fileCssClass = `pipeline-node-file contributing${infoNodeId === fileNodeId ? ' active' : ''}`;
            jsonGraph.addNode(fileNodeId, `${coalescingGroup.length} contributing files`, {
                cssClass: fileCssClass,
                type: 'File',
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

    return { graph: jsonGraph, graphedFiles: graphedFiles };
}


// Function to render the file gallery, and it gets called after the file search results (for files associated with
// the displayed experiment) return.
const FileGalleryRenderer = createReactClass({
    propTypes: {
        context: PropTypes.object, // Dataset whose files we're rendering
        data: PropTypes.object, // File data retrieved from search request
        schemas: PropTypes.object, // Schemas for the entire system; used for QC property titles
        hideGraph: PropTypes.bool, // T to hide graph display
        altFilterDefault: PropTypes.bool, // T to default to All Assemblies and Annotations
    },

    contextTypes: {
        session: PropTypes.object,
        session_properties: PropTypes.object,
        location_href: PropTypes.string,
    },

    getInitialState: function () {
        return {
            selectedFilterValue: '', // <select> value of selected filter
            infoNodeId: '', // @id of node whose info panel is open
            infoModalOpen: false, // True if info modal is open
            relatedFiles: [], // List of related files
        };
    },

    componentWillMount: function () {
        const { context, data } = this.props;
        const relatedFileIds = context.related_files && context.related_files.length ? context.related_files : [];
        if (relatedFileIds.length) {
            const searchedFiles = data ? data['@graph'] : []; // Array of searched files arrives in data.@graph result
            requestFiles(relatedFileIds, searchedFiles).then((relatedFiles) => {
                this.setState({ relatedFiles: relatedFiles });
            });
        }
    },

    // Set the default filter after the graph has been analayzed once.
    componentDidMount: function () {
        if (!this.props.altFilterDefault) {
            this.setFilter('0');
        }
    },

    componentDidUpdate: function () {
        const { context, data } = this.props;
        const relatedFileIds = context.related_files && context.related_files.length ? context.related_files : [];
        if (relatedFileIds.length) {
            const searchedFiles = data ? data['@graph'] : []; // Array of searched files arrives in data.@graph result
            requestFiles(relatedFileIds, searchedFiles).then((relatedFiles) => {
                if (relatedFiles.length !== this.state.relatedFiles.length) {
                    this.setState({ relatedFiles: relatedFiles });
                }
            });
        }
    },

    // Called from child components when the selected node changes.
    setInfoNodeId: function (nodeId) {
        this.setState({ infoNodeId: nodeId });
    },

    setInfoNodeVisible: function (visible) {
        this.setState({ infoNodeVisible: visible });
    },

    // Set the graph filter based on the given <option> value
    setFilter: function (value) {
        this.setState({ selectedFilterValue: value });
    },

    // React to a filter menu selection. The synthetic event given in `e`
    handleFilterChange: function (e) {
        this.setFilter(e.target.value);
    },

    render: function () {
        const { context, data, schemas, hideGraph } = this.props;
        let selectedAssembly = '';
        let selectedAnnotation = '';
        let jsonGraph;
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

        // Get a list of files for the graph (filters out archived files)
        const graphFiles = _(files).filter(file => file.status !== 'archived');

        // Build node graph of the files and analysis steps with this experiment
        if (graphFiles && graphFiles.length && !hideGraph) {
            try {
                const { graph, graphedFiles } = assembleGraph(context, this.context.session, this.state.infoNodeId, graphFiles, selectedAssembly, selectedAnnotation);
                jsonGraph = graph;
                allGraphedFiles = (selectedAssembly || selectedAnnotation) ? graphedFiles : {};
            } catch (e) {
                jsonGraph = null;
                allGraphedFiles = {};
                console.warn(e.message + (e.file0 ? ` -- file0:${e.file0}` : '') + (e.file1 ? ` -- file1:${e.file1}` : ''));
            }
        }

        return (
            <Panel>
                <PanelHeading addClasses="file-gallery-heading">
                    <h4>Files</h4>
                    <div className="file-gallery-controls">
                        {context.visualize ?
                            <div className="file-gallery-control">
                                <BrowserSelector visualizeCfg={context.visualize} />
                            </div>
                        : null}
                        {filterOptions.length ?
                            <div className="file-gallery-control file-gallery-control-select">
                                <FilterMenu selectedFilterValue={this.state.selectedFilterValue} filterOptions={filterOptions} handleFilterChange={this.handleFilterChange} />
                            </div>
                        : null}
                    </div>
                </PanelHeading>

                {!hideGraph ?
                    <FileGraph
                        context={context}
                        items={graphFiles}
                        graph={jsonGraph}
                        selectedAssembly={selectedAssembly}
                        selectedAnnotation={selectedAnnotation}
                        session={this.context.session}
                        infoNodeId={this.state.infoNodeId}
                        setInfoNodeId={this.setInfoNodeId}
                        infoNodeVisible={this.state.infoNodeVisible}
                        setInfoNodeVisible={this.setInfoNodeVisible}
                        schemas={schemas}
                        sessionProperties={this.context.session_properties}
                        forceRedraw
                    />
                : null}

                {/* If logged in and dataset is released, need to combine search of files that reference
                    this dataset to get released and unreleased ones. If not logged in, then just get
                    files from dataset.files */}
                <FileTable
                    {...this.props}
                    items={files}
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
            </Panel>
        );
    },
});


const CollapsingTitle = createReactClass({
    propTypes: {
        title: PropTypes.string.isRequired, // Title to display in the title bar
        handleCollapse: PropTypes.func.isRequired, // Function to call to handle click in collapse button
        selectedFilterValue: PropTypes.string, // Currently selected filter
        filterOptions: PropTypes.array, // Array of filtering options
        handleFilterChange: PropTypes.func, // Function to call when filter menu item is chosen
        collapsed: PropTypes.bool, // T if the panel this is over has been collapsed
    },

    render: function () {
        const { title, handleCollapse, collapsed, filterOptions, selectedFilterValue, handleFilterChange } = this.props;
        return (
            <div className="collapsing-title">
                <button className="collapsing-title-trigger pull-left" data-trigger onClick={handleCollapse}>{collapseIcon(collapsed, 'collapsing-title-icon')}</button>
                <h4>{title}</h4>
                {filterOptions && filterOptions.length && handleFilterChange ?
                    <div className="file-gallery-controls ">
                        <div className="file-gallery-control file-gallery-control-select">
                            <FilterMenu filterOptions={filterOptions} selectedFilterValue={selectedFilterValue} handleFilterChange={handleFilterChange} />
                        </div>
                    </div>
                : null}
            </div>
        );
    },
});


// Display a filtering <select>. `filterOptions` is an array of objects with two properties:
// `assembly` and `annotation`. Both are strings that get concatenated to form each menu item. The
// value of each <option> is its zero-based index.
const FilterMenu = createReactClass({
    propTypes: {
        selectedFilterValue: PropTypes.string, // Currently selected filter
        filterOptions: PropTypes.array.isRequired, // Contents of the filtering menu
        handleFilterChange: PropTypes.func.isRequired, // Call when a filtering option changes
    },

    render: function () {
        const { filterOptions, handleFilterChange, selectedFilterValue } = this.props;

        return (
            <select className="form-control" value={selectedFilterValue} onChange={handleFilterChange}>
                <option value="default">All Assemblies and Annotations</option>
                <option disabled="disabled" />
                {filterOptions.map((option, i) =>
                    <option key={`${option.assembly}${option.annotation}`} value={i}>{`${option.assembly + (option.annotation ? ` ${option.annotation}` : '')}`}</option>,
                )}
            </select>
        );
    },
});


export function qcDetailsView(metrics, schemas) {
    const qc = metrics.ref;

    // Extract the GenericQualityMetric schema. We don't display properties that exist in this
    // schema because they're generic properties, not interesting QC proeprties.
    const genericQCSchema = schemas.GenericQualityMetric;

    // Extract the schema specific for the given quality metric.
    const qcSchema = schemas[qc['@type'][0]];

    if (metrics && genericQCSchema && qcSchema && qcSchema.properties) {
        const file = metrics.parent;

        return qcModalContent(qc, file, qcSchema, genericQCSchema);
    }
    return { header: null, body: null };
}


function coalescedDetailsView(node) {
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
    return { header: header, body: body };
}

const FileGraphComponent = createReactClass({
    propTypes: {
        items: PropTypes.array, // Array of files we're graphing
        graph: PropTypes.object, // JsonGraph object generated from files
        selectedAssembly: PropTypes.string, // Currently selected assembly
        selectedAnnotation: PropTypes.string, // Currently selected annotation
        setInfoNodeId: PropTypes.func, // Function to call to set the currently selected node ID
        setInfoNodeVisible: PropTypes.func, // Function to call to set the visibility of the node's modal
        infoNodeId: PropTypes.string, // ID of selected node in graph
        infoNodeVisible: PropTypes.bool, // True if node's modal is vibible
        schemas: PropTypes.object, // System-wide schemas
        session: PropTypes.object, // Current user's login information
        sessionProperties: PropTypes.object, // True if logged in user is an admin
        auditIndicators: PropTypes.func, // Inherited from auditDecor HOC
        auditDetail: PropTypes.func, // Inherited from auditDecor HOC
    },

    getInitialState: function () {
        return {
            contributingFiles: {}, // List of contributing file objects we've requested; acts as a cache too
            coalescedFiles: {}, // List of coalesced files we've requested; acts as a cache too
            infoModalOpen: false, // Graph information modal open
            collapsed: false, // T if graphing panel is collapsed
        };
    },

    // Render metadata if a graph node is selected.
    // jsonGraph: JSON graph data.
    // infoNodeId: ID of the selected node
    detailNodes: function (jsonGraph, infoNodeId, session, sessionProperties) {
        let meta;

        // Find data matching selected node, if any
        if (infoNodeId) {
            if (infoNodeId.indexOf('qc:') >= 0) {
                // QC subnode.
                const subnode = jsonGraph.getSubnode(infoNodeId);
                if (subnode) {
                    meta = qcDetailsView(subnode, this.props.schemas);
                    meta.type = subnode['@type'][0];
                }
            } else if (infoNodeId.indexOf('coalesced:') >= 0) {
                // Coalesced contributing files.
                const node = jsonGraph.getNode(infoNodeId);
                if (node) {
                    const currCoalescedFiles = this.state.coalescedFiles;
                    if (currCoalescedFiles[node.metadata.contributing]) {
                        // We have the requested coalesced files in the cache, so just display
                        // them.
                        node.metadata.coalescedFiles = currCoalescedFiles[node.metadata.contributing];
                        meta = coalescedDetailsView(node);
                        meta.type = 'File';
                    } else if (!this.contributingRequestOutstanding) {
                        // We don't have the requested coalesced files in the cache, so we have to
                        // request them from the DB.
                        this.contributingRequestOutstanding = true;
                        requestFiles(node.metadata.ref).then((contributingFiles) => {
                            this.contributingRequestOutstanding = false;
                            currCoalescedFiles[node.metadata.contributing] = contributingFiles;
                            this.setState({ coalescedFiles: currCoalescedFiles });
                        }).catch(() => {
                            this.contributingRequestOutstanding = false;
                            currCoalescedFiles[node.metadata.contributing] = [];
                            this.setState({ coalescedFiles: currCoalescedFiles });
                        });
                    }
                }
            } else {
                // A regular or contributing file.
                const node = jsonGraph.getNode(infoNodeId);
                if (node) {
                    if (node.metadata.contributing) {
                        // This is a contributing file, and its @id is in
                        // node.metadata.contributing. See if the file is in the cache.
                        const currContributing = this.state.contributingFiles;
                        if (currContributing[node.metadata.contributing]) {
                            // We have this file's object in the cache, so just display it.
                            node.metadata.ref = currContributing[node.metadata.contributing];
                            meta = globals.graph_detail.lookup(node)(node, this.handleNodeClick, this.props.auditIndicators, this.props.auditDetail, session, sessionProperties);
                            meta.type = node['@type'][0];
                        } else if (!this.contributingRequestOutstanding) {
                            // We don't have this file's object in the cache, so request it from
                            // the DB.
                            this.contributingRequestOutstanding = true;
                            requestFiles([node.metadata.contributing]).then((contributingFile) => {
                                this.contributingRequestOutstanding = false;
                                currContributing[node.metadata.contributing] = contributingFile[0];
                                this.setState({ contributingFiles: currContributing });
                            }).catch(() => {
                                this.contributingRequestOutstanding = false;
                                currContributing[node.metadata.contributing] = {};
                                this.setState({ contributingFiles: currContributing });
                            });
                        }
                    } else {
                        // Regular File data in the node from when we generated the graph. Just
                        // display the file data from there.
                        meta = globals.graph_detail.lookup(node)(node, this.handleNodeClick, this.props.auditIndicators, this.props.auditDetail, session, sessionProperties);
                        meta.type = node['@type'][0];
                    }
                }
            }
        }

        return meta;
    },

    // Handle a click in a graph node
    handleNodeClick: function (nodeId) {
        this.props.setInfoNodeId(nodeId);
        this.props.setInfoNodeVisible(true);
    },

    handleCollapse: function () {
        // Handle click on panel collapse icon
        this.setState({ collapsed: !this.state.collapsed });
    },

    closeModal: function () {
        // Called when user wants to close modal somehow
        this.props.setInfoNodeVisible(false);
    },

    render: function () {
        const { session, sessionProperties, items, graph, selectedAssembly, selectedAnnotation, infoNodeId, infoNodeVisible } = this.props;
        const files = items;
        const modalTypeMap = {
            File: 'file',
            Step: 'analysis-step',
            QualityMetric: 'quality-metric',
        };

        // Build node graph of the files and analysis steps with this experiment
        if (files && files.length) {
            // If we have a graph, or if we have a selected assembly/annotation, draw the graph panel
            const goodGraph = graph && Object.keys(graph).length;
            if (goodGraph) {
                if (selectedAssembly || selectedAnnotation) {
                    const meta = this.detailNodes(graph, infoNodeId, session, sessionProperties);
                    const modalClass = meta ? `graph-modal-${modalTypeMap[meta.type]}` : '';

                    return (
                        <div>
                            <div className="file-gallery-graph-header collapsing-title">
                                <button className="collapsing-title-trigger" onClick={this.handleCollapse}>{collapseIcon(this.state.collapsed, 'collapsing-title-icon')}</button>
                                <h4>Association graph</h4>
                            </div>
                            {!this.state.collapsed ?
                                <div>
                                    <Graph graph={graph} nodeClickHandler={this.handleNodeClick} nodeMouseenterHandler={this.handleHoverIn} nodeMouseleaveHandler={this.handleHoverOut} noDefaultClasses forceRedraw />
                                </div>
                            : null}
                            <div className={`file-gallery-graph-footer${this.state.collapsed ? ' hiding' : ''}`} />
                            {meta && infoNodeVisible ?
                                <Modal closeModal={this.closeModal}>
                                    <ModalHeader closeModal={this.closeModal} addCss={modalClass}>
                                        {meta ? meta.header : null}
                                    </ModalHeader>
                                    <ModalBody>
                                        {meta ? meta.body : null}
                                    </ModalBody>
                                    <ModalFooter closeModal={<button className="btn btn-info" onClick={this.closeModal}>Close</button>} />
                                </Modal>
                            : null}
                        </div>
                    );
                }
                return <p className="browser-error">Choose an assembly to see file association graph</p>;
            }
            return <p className="browser-error">Graph not applicable for the selected assembly/annotation.</p>;
        }
        return null;
    },
});

const FileGraph = auditDecor(FileGraphComponent);


// Display a QC button in the file modal.
const FileQCButton = createReactClass({
    propTypes: {
        qc: PropTypes.object.isRequired, // QC object we're directing to
        file: PropTypes.object.isRequired, // File this QC object is attached to
        handleClick: PropTypes.func.isRequired, // Function to open a modal to the given object
    },

    handleClick: function () {
        const qcId = `qc:${this.props.qc['@id']}${this.props.file['@id']}`;
        this.props.handleClick(qcId);
    },

    render: function () {
        const qcName = qcIdToDisplay(this.props.qc);
        if (qcName) {
            return <button className="file-qc-btn" onClick={this.handleClick}>{qcName}</button>;
        }
        return null;
    },
});


// Display the metadata of the selected file in the graph
const FileDetailView = function (node, qcClick, auditIndicators, auditDetail, session, sessionProperties) {
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
                            {auditIndicators(selectedFile.audit, 'file-audit', { session: session })}
                            {auditDetail(selectedFile.audit, 'file-audit', { session: session, except: selectedFile['@id'] })}
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
    return { header: header, body: body };
};

globals.graph_detail.register(FileDetailView, 'File');
