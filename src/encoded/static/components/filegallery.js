const React = require('react');
const globals = require('./globals');
const { Panel, PanelHeading } = require('../libs/bootstrap/panel');
const { Modal, ModalHeader, ModalBody, ModalFooter } = require('../libs/bootstrap/modal');
const { DropdownButton } = require('../libs/bootstrap/button');
const { DropdownMenu } = require('../libs/bootstrap/dropdown-menu');
const { AuditIcon } = require('./audit');
const { StatusLabel } = require('./statuslabel');
const { Graph, JsonGraph } = require('./graph');
const { softwareVersionList } = require('./software');
const { FetchedItems, FetchedData, Param } = require('./fetched');
const _ = require('underscore');
const moment = require('moment');
const { collapseIcon } = require('../libs/svg-icons');
const { SortTablePanel, SortTable } = require('./sorttable');
const { AttachmentPanel } = require('./doc');


// Order that assemblies should appear in filtering menu
const assemblyPriority = [
    'GRCh38',
    'hg19',
    'mm10',
    'mm10-minimal',
    'mm9',
    'ce11',
    'ce10',
    'dm6',
    'dm3',
    'J02459.1',
];


// Render an accession as a button if clicking it sets a graph node, or just as text if not.
const FileAccessionButton = React.createClass({
    propTypes: {
        file: React.PropTypes.object.isRequired, // File whose button is being rendered
        buttonEnabled: React.PropTypes.bool, // True if accession should be a button
        clickHandler: React.PropTypes.func, // Function to call when the button is clicked
    },

    onClick: function () {
        this.props.clickHandler(`file:${this.props.file['@id']}`);
    },

    render: function () {
        const { file, buttonEnabled } = this.props;
        return (
            <span>
                {buttonEnabled ?
                    <span><button className="file-table-btn" onClick={this.onClick}>{file.accession}</button>&nbsp;</span>
                :
                    <span>{file.accession}&nbsp;</span>
                }
            </span>
        );
    },
});


// Render a download button for a file that reacts to login state and admin status to render a
// tooltip about the restriction based on those things.
const RestrictedDownloadButton = React.createClass({
    propTypes: {
        file: React.PropTypes.object, // File containing `href` to use as download link
        adminUser: React.PropTypes.bool, // True if logged in user is admin
    },

    getInitialState: function () {
        return {
            tip: false, // True if tip is visible
        };
    },

    timer: null, // Holds timer for the tooltip
    tipHovering: false, // True if currently hovering over the tooltip

    hoverDL: function (hovering) {
        if (hovering) {
            // Started hovering over the DL button; show the tooltip.
            this.setState({ tip: true });

            // If we happen to have a running timer, clear it so we don't clear the tooltip while
            // hovering over the DL button.
            if (this.timer) {
                clearTimeout(this.timer);
                this.timer = null;
            }
        } else {
            // No longer hovering over the DL button; start a timer that might hide the tooltip
            // after a second passes. It won't hide the tooltip if they're now hovering over the
            // tooltip itself.
            this.timer = setTimeout(() => {
                this.timer = null;
                if (!this.tipHovering) {
                    this.setState({ tip: false });
                }
            }, 1000);
        }
    },

    hoverTip: function (hovering) {
        if (hovering) {
            // Started hovering over the tooltip. This prevents the timer from hiding the tooltip.
            this.tipHovering = true;
        } else {
            // Stopped hovering over the tooltip. If the DL button hover time isn't running, hide
            // the tooltip here.
            this.tipHovering = false;
            if (!this.timer) {
                this.setState({ tip: false });
            }
        }
    },

    hoverTipIn: function () {
        this.hoverTip(true);
    },

    hoverTipOut: function () {
        this.hoverTip(false);
    },

    render: function () {
        const { file, adminUser } = this.props;
        const tooltipOpenClass = this.state.tip ? ' tooltip-open' : '';
        const icon = (
            <DownloadIcon file={file} adminUser={adminUser} hoverDL={this.hoverDL} />
        );

        return (
            <div className="dl-tooltip-trigger">
                {!file.restricted || adminUser ?
                    <a href={file.href} download={file.href.substr(file.href.lastIndexOf('/') + 1)} data-bypass="true">
                        {icon}
                    </a>
                :
                    <span>{icon}</span>
                }
                {file.restricted ?
                    <div className={`tooltip right${tooltipOpenClass}`} role="tooltip" onMouseEnter={this.hoverTipIn} onMouseLeave={this.hoverTipOut}>
                        <div className="tooltip-arrow" />
                        <div className="tooltip-inner">
                            If you are a collaborator or owner of this file,<br />
                            please contact <a href="mailto:encode-help@lists.stanford.edu">encode-help@lists.stanford.edu</a><br />
                            to receive a copy of this file
                        </div>
                    </div>
                : null}
            </div>
        );
    },
});


const DownloadableAccession = React.createClass({
    propTypes: {
        file: React.PropTypes.object.isRequired, // File whose accession to render
        buttonEnabled: React.PropTypes.bool, // True if accession should be a button
        clickHandler: React.PropTypes.func, // Function to call when button is clicked
        loggedIn: React.PropTypes.bool, // True if current user is logged in
        adminUser: React.PropTypes.bool, // True if current user is logged in and admin
    },

    render: function () {
        const { file, buttonEnabled, clickHandler, loggedIn, adminUser } = this.props;
        return (
            <span className="file-table-accession">
                <FileAccessionButton file={file} buttonEnabled={buttonEnabled} clickHandler={clickHandler} />
                <RestrictedDownloadButton file={file} loggedIn={loggedIn} adminUser={adminUser} />
            </span>
        );
    },
});


// Display a human-redable form of the file size given the size of a file in bytes. Returned as a
// string
function humanFileSize(size) {
    if (size >= 0) {
        const i = Math.floor(Math.log(size) / Math.log(1024));
        const adjustedSize = (size / Math.pow(1024, i)).toPrecision(3) * 1;
        const units = ['B', 'kB', 'MB', 'GB', 'TB'][i];
        return `${units} ${adjustedSize}`;
    }
    return undefined;
}


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


// Render the Download icon while allowing the hovering tooltip.
const DownloadIcon = React.createClass({
    propTypes: {
        hoverDL: React.PropTypes.func, // Function to call when hovering or stop hovering over the icon
        file: React.PropTypes.object, // File associated with this download button
        adminUser: React.PropTypes.bool, // True if logged-in user is an admin
    },

    onMouseEnter: function () {
        this.props.hoverDL(true);
    },

    onMouseLeave: function () {
        this.props.hoverDL(false);
    },

    render: function () {
        const { file, adminUser } = this.props;

        return (
            <i className="icon icon-download" style={!file.restricted || adminUser ? {} : { opacity: '0.3' }} onMouseEnter={file.restricted ? this.onMouseEnter : null} onMouseLeave={file.restricted ? this.onMouseLeave : null}>
                <span className="sr-only">Download</span>
            </i>
        );
    },
});


export const FileTable = React.createClass({
    propTypes: {
        items: React.PropTypes.array.isRequired, // Array of files to appear in the table
        graphedFiles: React.PropTypes.object, // Specifies which files are in the graph
        filePanelHeader: React.PropTypes.object, // Table header component
        encodevers: React.PropTypes.string, // ENCODE version of the experiment
        selectedFilterValue: React.PropTypes.string, // Selected filter from popup menu
        filterOptions: React.PropTypes.array, // Array of assambly/annotation from file array
        handleFilterChange: React.PropTypes.func, // Called when user changes filter
        anisogenic: React.PropTypes.bool, // True if experiment is anisogenic
        showFileCount: React.PropTypes.bool, // True to show count of files in table
        setInfoNodeId: React.PropTypes.func, // Function to call to set the currently selected node ID
        setInfoNodeVisible: React.PropTypes.func, // Function to call to set the visibility of the node's modal
        session: React.PropTypes.object, // Persona user session
        adminUser: React.PropTypes.bool, // True if user is an admin user
        noDefaultClasses: React.PropTypes.bool, // True to strip SortTable panel of default CSS classes
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
                const buttonEnabled = !!meta.graphedFiles[item['@id']];
                return <DownloadableAccession file={item} buttonEnabled={buttonEnabled} clickHandler={meta.fileClick} loggedIn={loggedIn} adminUser={adminUser} />;
            },
        },
        file_type: { title: 'File type' },
        output_type: { title: 'Output type' },
        biological_replicates: {
            title: (list, columns, meta) => <span>{meta.anisogenic ? 'Anisogenic' : 'Biological'} replicate</span>,
            getValue: item => (item.biological_replicates ? item.biological_replicates.sort((a, b) => a - b).join(', ') : ''),
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
            display: item => <span>{humanFileSize(item.file_size)}</span>,
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
                const buttonEnabled = !!meta.graphedFiles[item['@id']];
                return <DownloadableAccession file={item} buttonEnabled={buttonEnabled} clickHandler={meta.fileClick} loggedIn={loggedIn} adminUser={adminUser} />;
            },
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
        file_size: {
            title: 'File size',
            display: item => <span>{humanFileSize(item.file_size)}</span>,
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


const RawSequencingTable = React.createClass({
    propTypes: {
        files: React.PropTypes.array, // Raw files to display
        meta: React.PropTypes.object, // Extra metadata in the same format passed to SortTable
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
                if (file.paired_with &&
                    file.biological_replicates && file.biological_replicates.length === 1 &&
                    file.replicate && file.replicate.library) {
                    // File is paired and has exactly one biological replicate. Now make sure its
                    // partner exists and also qualifies.
                    const partner = filesKeyed[file.paired_with];
                    if (partner && partner.paired_with === file['@id'] &&
                        partner.biological_replicates && partner.biological_replicates.length === 1 &&
                        partner.replicate && partner.replicate.library &&
                        partner.biological_replicates[0] === file.biological_replicates[0]) {
                        // Both the file and its partner qualify as good pairs of each other. Let
                        // them pass the filter, and record set their sort keys to the lower of
                        // the two accessions -- that's how pairs will sort within a biological
                        // replicate
                        file.pairSortKey = partner.pairSortKey = file.accession < partner.accession ? file.accession : partner.accession;
                        file.pairSortKey += file.paired_end;
                        partner.pairSortKey += partner.paired_end;
                        return true;
                    }
                }

                // File not part of a pair; add to non-paired list and filter it out
                nonpairedFiles.push(file);
                return false;
            });

            // Group paired files by biological replicate and library -- four-digit biological
            // replicate concatenated with library accession becomes the group key, and all files
            // with that biological replicate and library form an array under that key.
            let pairedRepGroups = {};
            let pairedRepKeys = [];
            if (pairedFiles.length) {
                pairedRepGroups = _(pairedFiles).groupBy(file => globals.zeroFill(file.biological_replicates[0]) + file.replicate.library.accession);

                // Make a sorted list of keys
                pairedRepKeys = Object.keys(pairedRepGroups).sort();
            }

            return (
                <table className="table table-sortable table-raw">
                    <thead>
                        <tr className="table-section">
                            <th colSpan={loggedIn ? '11' : '10'}>
                                <CollapsingTitle title="Raw sequencing data" collapsed={this.state.collapsed} handleCollapse={this.handleCollapse} />
                            </th>
                        </tr>

                        {!this.state.collapsed ?
                            <tr key="header">
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
                                {loggedIn ? <th>File status</th> : null}
                            </tr>
                        : null}
                    </thead>

                    {!this.state.collapsed ?
                        <tbody>
                            {pairedRepKeys.map((pairedRepKey, j) => {
                                // groupFiles is an array of files under a bioreplicate/library
                                const groupFiles = pairedRepGroups[pairedRepKey];
                                const bottomClass = j < (pairedRepKeys.length - 1) ? 'merge-bottom' : '';

                                // Render an array of biological replicate and library to display on
                                // the first row of files, spanned to all rows for that replicate and
                                // library
                                const spanned = [
                                    <td key="br" rowSpan={groupFiles.length} className={`${bottomClass} merge-right table-raw-merged table-raw-biorep`}>{groupFiles[0].biological_replicates[0]}</td>,
                                    <td key="lib" rowSpan={groupFiles.length} className={`${bottomClass} merge-right + table-raw-merged`}>{groupFiles[0].replicate.library.accession}</td>,
                                ];

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
                                    const buttonEnabled = !!meta.graphedFiles[file['@id']];

                                    return (
                                        <tr key={i} className={file.restricted ? 'file-restricted' : ''}>
                                            {i === 0 ? { spanned } : null}
                                            <td className={pairClass}>
                                                <DownloadableAccession file={file} buttonEnabled={buttonEnabled} clickHandler={meta.fileClick} loggedIn={loggedIn} adminUser={adminUser} />;
                                            </td>
                                            <td className={pairClass}>{file.file_type}</td>
                                            <td className={pairClass}>{runType}{file.read_length ? <span>{runType ? <span /> : null}{file.read_length + file.read_length_units}</span> : null}</td>
                                            <td className={pairClass}>{file.paired_end}</td>
                                            <td className={pairClass}>{file.lab && file.lab.title ? file.lab.title : null}</td>
                                            <td className={pairClass}>{moment.utc(file.date_created).format('YYYY-MM-DD')}</td>
                                            <td className={pairClass}>{humanFileSize(file.file_size)}</td>
                                            <td className={pairClass}>{fileAuditStatus(file)}</td>
                                            {loggedIn ? <td className={`${pairClass} characterization-meta-data`}><StatusLabel status={file.status} /></td> : null}
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
                                const buttonEnabled = !!meta.graphedFiles[file['@id']];

                                return (
                                    <tr key={i} className={rowClasses.join(' ')}>
                                        <td className="table-raw-biorep">{file.biological_replicates ? file.biological_replicates.sort((a, b) => a - b).join(', ') : ''}</td>
                                        <td>{(file.replicate && file.replicate.library) ? file.replicate.library.accession : ''}</td>
                                        <td>
                                            <DownloadableAccession file={file} buttonEnabled={buttonEnabled} clickHandler={meta.fileClick} loggedIn={loggedIn} adminUser={adminUser} />;
                                        </td>
                                        <td>{file.file_type}</td>
                                        <td>{runType}{file.read_length ? <span>{runType ? <span /> : null}{file.read_length + file.read_length_units}</span> : null}</td>
                                        <td>{file.paired_end}</td>
                                        <td>{file.lab && file.lab.title ? file.lab.title : null}</td>
                                        <td>{moment.utc(file.date_created).format('YYYY-MM-DD')}</td>
                                        <td>{humanFileSize(file.file_size)}</td>
                                        <td>{fileAuditStatus(file)}</td>
                                        {loggedIn ? <td className="characterization-meta-data"><StatusLabel status={file.status} /></td> : null}
                                    </tr>
                                );
                            })}
                        </tbody>
                    : null}

                    <tfoot>
                        <tr>
                            <td className={`file-table-footer${this.state.collapsed ? ' hiding' : ''}`} colSpan={loggedIn ? '11' : '10'} />
                        </tr>
                    </tfoot>
                </table>
            );
        }

        // No files to display
        return null;
    },
});


const RawFileTable = React.createClass({
    propTypes: {
        files: React.PropTypes.array, // Raw sequencing files to display
        meta: React.PropTypes.object, // Extra metadata in the same format passed to SortTable
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
                            <th colSpan={loggedIn ? '11' : '10'}>
                                <CollapsingTitle title="Raw data" collapsed={this.state.collapsed} handleCollapse={this.handleCollapse} />
                            </th>
                        </tr>

                        {!this.state.collapsed ?
                            <tr key="header">
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
                                {loggedIn ? <th>File status</th> : null}
                            </tr>
                        : null}
                    </thead>

                    {!this.state.collapsed ?
                        <tbody>
                            {pairedKeys.map((pairedKey, j) => {
                                // groupFiles is an array of files under a bioreplicate/library
                                const groupFiles = pairedGroups[pairedKey];
                                const bottomClass = j < (pairedKeys.length - 1) ? 'merge-bottom' : '';

                                // Render an array of biological replicate and library to display on
                                // the first row of files, spanned to all rows for that replicate and
                                // library
                                const spanned = [
                                    <td key="br" rowSpan={groupFiles.length} className={`${bottomClass} merge-right table-raw-merged table-raw-biorep`}>{groupFiles[0].biological_replicates[0]}</td>,
                                    <td key="lib" rowSpan={groupFiles.length} className={`${bottomClass} merge-right table-raw-merged`}>{groupFiles[0].replicate.library.accession}</td>,
                                ];

                                // Render each file's row, with the biological replicate and library
                                // cells only on the first row.
                                return groupFiles.sort((a, b) => (a.accession < b.accession ? -1 : 1)).map((file, i) => {
                                    let pairClass;
                                    if (i === 1) {
                                        pairClass = `align-pair2${(i === groupFiles.length - 1) && (j === pairedKeys.length - 1) ? '' : ' pair-bottom'}`;
                                    } else {
                                        pairClass = 'align-pair1';
                                    }

                                    // Determine if the accession should be a button or not.
                                    const buttonEnabled = !!meta.graphedFiles[file['@id']];

                                    // Prepare for run_type display
                                    return (
                                        <tr key={i} className={file.restricted ? 'file-restricted' : ''}>
                                            {i === 0 ? { spanned } : null}
                                            <td className={pairClass}>
                                                <DownloadableAccession file={file} buttonEnabled={buttonEnabled} clickHandler={meta.fileClick} loggedIn={loggedIn} adminUser={adminUser} />;
                                            </td>
                                            <td className={pairClass}>{file.file_type}</td>
                                            <td className={pairClass}>{file.output_type}</td>
                                            <td className={pairClass}>{file.assembly}</td>
                                            <td className={pairClass}>{file.lab && file.lab.title ? file.lab.title : null}</td>
                                            <td className={pairClass}>{moment.utc(file.date_created).format('YYYY-MM-DD')}</td>
                                            <td className={pairClass}>{humanFileSize(file.file_size)}</td>
                                            <td className={pairClass}>{fileAuditStatus(file)}</td>
                                            {loggedIn ? <td className={`${pairClass} characterization-meta-data`}><StatusLabel status={file.status} /></td> : null}
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
                                const buttonEnabled = !!meta.graphedFiles[file['@id']];

                                return (
                                    <tr key={i} className={rowClasses.join(' ')}>
                                        <td className="table-raw-biorep">{file.biological_replicates ? file.biological_replicates.sort((a, b) => a - b).join(', ') : ''}</td>
                                        <td>{(file.replicate && file.replicate.library) ? file.replicate.library.accession : ''}</td>
                                        <td>
                                            <DownloadableAccession file={file} buttonEnabled={buttonEnabled} clickHandler={meta.fileClick} loggedIn={loggedIn} adminUser={adminUser} />;
                                        </td>
                                        <td>{file.file_type}</td>
                                        <td>{file.output_type}</td>
                                        <td>{file.assembly}</td>
                                        <td>{file.lab && file.lab.title ? file.lab.title : null}</td>
                                        <td>{moment.utc(file.date_created).format('YYYY-MM-DD')}</td>
                                        <td>{humanFileSize(file.file_size)}</td>
                                        <td>{fileAuditStatus(file)}</td>
                                        {loggedIn ? <td className="characterization-meta-data"><StatusLabel status={file.status} /></td> : null}
                                    </tr>
                                );
                            })}
                        </tbody>
                    : null}

                    <tfoot>
                        <tr>
                            <td className={`file-table-footer${this.state.collapsed ? ' hiding' : ''}`} colSpan={loggedIn ? '11' : '10'} />
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
export const DatasetFiles = React.createClass({
    propTypes: {
        context: React.PropTypes.object, // Dataset whose files we're getting
        items: React.PropTypes.array, // Array of files retrieved
    },

    render: function () {
        const { context, items } = this.props;

        const files = _.uniq(((context.files && context.files.length) ? context.files : []).concat((items && items.length) ? items : []));
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
export const FileGallery = React.createClass({
    propTypes: {
        context: React.PropTypes.object, // Dataset object whose files we're rendering
        encodevers: React.PropTypes.string, // ENCODE version number
        anisogenic: React.PropTypes.bool, // True if anisogenic experiment
        hideGraph: React.PropTypes.bool, // T to hide graph display
        altFilterDefault: React.PropTypes.bool, // T to default to All Assemblies and Annotations
    },

    contextTypes: {
        session: React.PropTypes.object, // Login information
        location_href: React.PropTypes.string, // URL of this experiment page, including query string stuff
    },

    render: function () {
        const { context, encodevers, anisogenic, hideGraph, altFilterDefault } = this.props;

        return (
            <FetchedData ignoreErrors>
                <Param name="data" url={globals.unreleased_files_url(context)} />
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
    // array at the top of the file.
    return _(filterOptions).sortBy(option => _(assemblyPriority).indexOf(option.assembly));
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


export function assembleGraph(context, session, infoNodeId, files, filterAssembly, filterAnnotation) {
    // Calculate a step ID from a file's derived_from array
    function rDerivedFileIds(file) {
        if (file.derived_from) {
            return file.derived_from.map(derived => derived['@id']).sort().join();
        }
        return '';
    }

    function rGenQcId(metric, file) {
        return `qc:${metric['@id'] + file['@id']}`;
    }

    function processFiltering(fileList, assemblyFilter, annotationFilter, allFiles, allContributing, include) {
        function getSubFileList(filesArray) {
            const subFileList = {};
            filesArray.forEach((file) => {
                subFileList[file['@id']] = allFiles[file['@id']];
            });
            return subFileList;
        }

        const fileKeys = Object.keys(fileList);
        for (let i = 0; i < fileKeys.length; i += 1) {
            const file = fileList[fileKeys[i]];
            let nextFileList;

            if (file) {
                if (!file.removed) {
                    // This file gets included. Include everything it derives from
                    if (file.derived_from && file.derived_from.length && !allContributing[file['@id']]) {
                        nextFileList = getSubFileList(file.derived_from);
                        processFiltering(nextFileList, assemblyFilter, annotationFilter, allFiles, allContributing, true);
                    }
                } else if (include) {
                    // Unremove the file if this branch is to be included based on files that derive from it
                    file.removed = false;
                    if (file.derived_from && file.derived_from.length && !allContributing[file['@id']]) {
                        nextFileList = getSubFileList(file.derived_from);
                        processFiltering(nextFileList, assemblyFilter, annotationFilter, allFiles, allContributing, true);
                    }
                }
            }
        }
    }

    const derivedFromFiles = {}; // List of all files that other files derived from
    const allFiles = {}; // All files' accessions as keys
    const allReplicates = {}; // All file's replicates as keys; each key references an array of files
    const allPipelines = {}; // List of all pipelines indexed by step @id
    const fileQcMetrics = {}; // List of all file QC metrics indexed by file ID
    const filterOptions = []; // List of graph filters; annotations and assemblies
    const derivedFileIds = _.memoize(rDerivedFileIds, file => file['@id']);
    const genQcId = _.memoize(rGenQcId, (metric, file) => metric['@id'] + file['@id']);
    let stepExists = false; // True if at least one file has an analysis_step
    let fileOutsideReplicate = false; // True if at least one file exists outside a replicate
    let abortGraph = false; // True if graph shouldn't be drawn

    // Collect all files keyed by their ID as a single source of truth for files.
    // Every reference to a file object should get it from this object. Also serves
    // to de-dup the file array since there can be repeated files in it.
    files.forEach((file) => {
        if (!allFiles[file['@id']]) {
            file.removed = false;
            allFiles[file['@id']] = file;
        }
    });

    // Collect derived_from files, used replicates, and used pipelines. allFiles has all files directly involved
    // with this experiment if we're logged in, or just released files directly involved with experiment if we're not.
    Object.keys(allFiles).forEach((fileId) => {
        const file = allFiles[fileId];

        // Build an object keyed with all files that other files derive from. If the file is contributed,
        // we don't care about its derived_from because we don't render that.
        if (file.derived_from && file.derived_from.length) {
            file.derived_from.forEach((derivedFrom) => {
                const derivedFromId = derivedFrom['@id'];
                const derivedFile = allFiles[derivedFromId];
                if (!derivedFile) {
                    // The derived-from file wasn't in the given file list. Copy the file object from the file's
                    // derived_from so we can examine it later -- and mark it as missing. It could be because a
                    // derived-from file isn't released and we're not logged in, or because it's a contributing file.
                    derivedFromFiles[derivedFromId] = derivedFrom;
                    derivedFrom.missing = true;
                    derivedFrom.removed = false; // Clears previous value Redmine #4536
                } else if (!derivedFromFiles[derivedFromId]) {
                    // The derived-from file was in the given file list, so record the derived-from file in derivedFromFiles.
                    // ...that is, unless the derived-from file has already been seen. Just move on if it has.
                    derivedFromFiles[derivedFromId] = derivedFile;
                }
            });
        }

        // Keep track of all used replicates by keeping track of all file objects for each replicate.
        // Each key is a replicate number, and each references an array of file objects using that replicate.
        if (file.biological_replicates && file.biological_replicates.length === 1) {
            const bioRep = file.biological_replicates[0];
            if (!allReplicates[bioRep]) {
                // Place a new array in allReplicates if needed
                allReplicates[bioRep] = [];
            }
            allReplicates[bioRep].push(file);
        }

        // Note whether any files have an analysis step
        const fileAnalysisStep = file.analysis_step_version && file.analysis_step_version.analysis_step;
        stepExists = stepExists || fileAnalysisStep;
        if (fileAnalysisStep && !(file.derived_from && file.derived_from.length)) {
            // File has an analysis step but no derived_from. We can't include the file in the graph
            file.removed = true;
        }

        // Save the pipeline array used for each step used by the file.
        if (fileAnalysisStep) {
            allPipelines[fileAnalysisStep['@id']] = fileAnalysisStep.pipelines;
        }

        // File is derived; collect any QC info that applies to this file
        if (file.quality_metrics && file.quality_metrics.length) {
            const matchingQc = [];

            // Search file's quality_metrics array to find one with a quality_metric_of field referring to this file.
            file.quality_metrics.forEach((metric) => {
                const matchingFile = _(metric.quality_metric_of).find(appliesFile => file['@id'] === appliesFile);
                if (matchingFile) {
                    matchingQc.push(metric);
                }
            });
            if (matchingQc.length) {
                fileQcMetrics[fileId] = matchingQc;
            }
        }

        // Keep track of whether files exist outside replicates. That could mean it has no replicate information,
        // or it has more than one replicate.
        fileOutsideReplicate = fileOutsideReplicate || (file.biological_replicates && file.biological_replicates.length !== 1);
    });
    // At this stage, allFiles, allReplicates, and derivedFromFiles point to the same file objects;
    // allPipelines points to pipelines.

    // Now find contributing files by subtracting original_files from the list of derived_from files. Note: derivedFromFiles is
    // an object keyed by each file's @id. allContributingArray is an array of file objects.
    const allContributingArray = _(derivedFromFiles).filter((derivedFromFile, derivedFromId) => _(context.contributing_files).any(contributingFile => contributingFile['@id'] === derivedFromId));

    // Process the contributing files array
    const allContributing = {};
    allContributingArray.forEach((contributingFile) => {
        // Convert array of contributing files to a keyed object to help with searching later
        contributingFile.missing = false;
        const contributingFileId = contributingFile['@id'];
        allContributing[contributingFileId] = contributingFile;

        // Also add contributing files to the allFiles object
        if (allFiles[contributingFileId]) {
            // Contributing file already existed in file array for some reason; use its existing file object
            allContributing[contributingFileId] = allFiles[contributingFileId];
        } else {
            // Seeing contributed file for the first time; save it in allFiles
            allFiles[contributingFileId] = allContributing[contributingFileId];
        }
    });

    // Now that we know at least some files derive from each other through analysis steps, mark file objects that
    // don't derive from other files — and that no files derive from them — as removed from the graph.
    // Also build the filtering menu here; it genomic annotations and assemblies that ARE involved in the graph.
    Object.keys(allFiles).forEach((fileId) => {
        const file = allFiles[fileId];

        // File gets removed if doesn’t derive from other files AND no files derive from it.
        const islandFile = !(file.derived_from && file.derived_from.length) && !derivedFromFiles[fileId];
        file.removed = file.removed || islandFile;

        // Add to the filtering options to generate a <select>; don't include island files
        if (!islandFile && file.output_category !== 'raw data' && file.assembly) {
            filterOptions.push({ assembly: file.assembly, annotation: file.genome_annotation });
        }
    });

    // Remove any replicates containing only removed files from the last step.
    Object.keys(allReplicates).forEach((repNum) => {
        const onlyRemovedFiles = _(allReplicates[repNum]).all(file => file.removed && file.missing === true);
        if (onlyRemovedFiles) {
            allReplicates[repNum] = [];
        }
    });

    // Check whether any files that others derive from are missing (usually because they're unreleased and we're logged out).
    Object.keys(derivedFromFiles).forEach((derivedFromFileId) => {
        const derivedFromFile = derivedFromFiles[derivedFromFileId];
        if (derivedFromFile.removed || derivedFromFile.missing) {
            // A file others derive from doesn't exist or was removed; check if it's in a replicate or not
            // Note the derived_from file object exists even if it doesn't exist in given files array.
            if (derivedFromFile.biological_replicates && derivedFromFile.biological_replicates.length === 1) {
                // Missing derived-from file in a replicate; remove the replicate's files and remove itself.
                const derivedFromRep = derivedFromFile.biological_replicates[0];
                if (allReplicates[derivedFromRep]) {
                    allReplicates[derivedFromRep].forEach((file) => {
                        file.removed = true;
                    });
                }
            } else {
                // Missing derived-from file not in a replicate or in multiple replicates; don't draw any graph
                throw new GraphException('No graph: derived_from file outside replicate (or in multiple replicates) missing', derivedFromFileId);
            }
        } // else the derived_from file is in files array (allFiles object); normal case
    });

    // Remove files based on the filtering options
    if (filterAssembly) {
        // First remove all raw files, and all other files with mismatched filtering options
        Object.keys(allFiles).forEach((fileId) => {
            const file = allFiles[fileId];

            if (file.output_category === 'raw data') {
                // File is raw data; just remove it
                file.removed = true;
            } else if ((file.assembly !== filterAssembly) || ((file.genome_annotation || filterAnnotation) && (file.genome_annotation !== filterAnnotation))) {
                file.removed = true;
            }
        });

        // For all files matching the filtering options that derive from others, go up the derivation chain and re-include everything there.
        processFiltering(allFiles, filterAssembly, filterAnnotation, allFiles, allContributing);
    }

    // See if removing files by filtering have emptied a replicate.
    if (Object.keys(allReplicates).length) {
        Object.keys(allReplicates).forEach((replicateId) => {
            const emptied = _(allReplicates[replicateId]).all(file => file.removed);

            // If all files removed from a replicate, remove the replicate
            if (emptied) {
                allReplicates[replicateId] = [];
            }
        });
    }

    // Check whether all files have been removed
    abortGraph = _(Object.keys(allFiles)).all(fileId => allFiles[fileId].removed);
    if (abortGraph) {
        throw new GraphException('No graph: all files removed');
    }

    // No files exist outside replicates, and all replicates are removed
    const replicateIds = Object.keys(allReplicates);
    if (!fileOutsideReplicate && replicateIds.length && _(replicateIds).all(replicateNum => !allReplicates[replicateNum].length)) {
        throw new GraphException('No graph: All replicates removed and no files outside replicates exist');
    }

    // Last check; see if any files derive from files now missing. This test is child-file based, where the last test
    // was based on the derived-from files.
    Object.keys(allFiles).forEach((fileId) => {
        const file = allFiles[fileId];

        if (!file.removed && !allContributing[fileId] && file.derived_from && file.derived_from.length) {
            // A file still in the graph derives from others. See if any of the files it derives from have been removed
            // or are missing.
            file.derived_from.forEach((derivedFromFile) => {
                const orgDerivedFromFile = derivedFromFiles[derivedFromFile['@id']];
                const derivedGone = orgDerivedFromFile.missing || orgDerivedFromFile.removed;

                // These two just for debugging a unrendered graph
                if (derivedGone) {
                    throw new GraphException(`file0 derives from file1 which is ${(orgDerivedFromFile.missing ? 'missing' : 'removed')}`, fileId, derivedFromFile['@id']);
                }
            });
        }
    });

    // Create an empty graph architecture that we fill in next.
    const jsonGraph = new JsonGraph(context.accession);

    // Create nodes for the replicates
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

    // Go through each file (released or unreleased) to add it and associated steps to the graph
    const graphedFiles = {};
    Object.keys(allFiles).forEach((fileId) => {
        const file = allFiles[fileId];

        // Only add files derived from others, or that others derive from,
        // and that aren't part of a removed replicate
        if (!file.removed) {
            let stepId;
            let label;
            let pipelineInfo;
            let error;
            let metricsInfo;
            const fileNodeId = `file:${file['@id']}`;
            const replicateNode = (file.biological_replicates && file.biological_replicates.length === 1) ? jsonGraph.getNode(`rep:${file.biological_replicates[0]}`) : null;
            const fileContributed = allContributing[fileId];

            // Add QC metrics info from the file to the list to generate the nodes later
            if (fileQcMetrics[fileId] && fileQcMetrics[fileId].length && file.step_run) {
                metricsInfo = fileQcMetrics[fileId].map((metric) => {
                    const qcId = genQcId(metric, file);
                    return { id: qcId, label: 'QC', class: `pipeline-node-qc-metric${infoNodeId === qcId ? ' active' : ''}`, ref: metric, parent: file };
                });
            }

            // Add file to the graph as a node
            let fileNodeLabel;
            let fileCssClass;
            let fileRef;
            const loggedIn = session && session['auth.userid'];
            if (fileContributed && fileContributed.status !== 'released' && !loggedIn) {
                // A contributed file isn't released and we're not logged in
                fileNodeLabel = 'Unreleased';
                fileCssClass = `pipeline-node-file contributing error${infoNodeId === fileNodeId ? ' active' : ''}`;
                fileRef = null;
            } else {
                fileNodeLabel = `${file.title} (${file.output_type})`;
                fileCssClass = `pipeline-node-file${fileContributed ? ' contributing' : ''}${file.restricted ? ' restricted' : ''}${infoNodeId === fileNodeId ? ' active' : ''}`;
                fileRef = file;
            }
            jsonGraph.addNode(fileNodeId, fileNodeLabel, {
                cssClass: fileCssClass,
                type: 'File',
                shape: 'rect',
                cornerRadius: 16,
                parentNode: replicateNode,
                contributing: fileContributed,
                ref: fileRef,
            }, metricsInfo);
            graphedFiles[file['@id']] = file;

            // If the file has an analysis step, prepare it for graph insertion
            if (!fileContributed) {
                const fileAnalysisStep = file.analysis_step_version && file.analysis_step_version.analysis_step;
                if (fileAnalysisStep) {
                    // Make an ID and label for the step
                    stepId = `step:${derivedFileIds(file) + fileAnalysisStep['@id']}`;
                    label = fileAnalysisStep.analysis_step_types;
                    pipelineInfo = allPipelines[fileAnalysisStep['@id']];
                    error = false;
                } else if (derivedFileIds(file)) {
                    // File derives from others, but no analysis step; make dummy step
                    stepId = `error:${derivedFileIds(file)}`;
                    label = 'Software unknown';
                    pipelineInfo = null;
                    error = true;
                } else {
                    // No analysis step and no derived_from; don't add a step
                    stepId = '';
                }

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
                            fileAccession: file.accession,
                            stepVersion: file.analysis_step_version,
                        });
                    }

                    // Connect the file to the step, and the step to the derived_from files
                    jsonGraph.addEdge(stepId, fileNodeId);
                    file.derived_from.forEach((derived) => {
                        if (!jsonGraph.getEdge(`file:${derived['@id']}`, stepId)) {
                            jsonGraph.addEdge(`file:${derived['@id']}`, stepId);
                        }
                    });
                }
            }
        }
    }, this);

    jsonGraph.filterOptions = filterOptions.length ? _(filterOptions).uniq(option => `${option.assembly}!${option.annotation ? option.annotation : ''}`) : [];
    return { graph: jsonGraph, graphedFiles: graphedFiles };
}


// Function to render the file gallery, and it gets called after the file search results (for files associated with
// the displayed experiment) return.
const FileGalleryRenderer = React.createClass({
    propTypes: {
        context: React.PropTypes.object, // Dataset whose files we're rendering
        data: React.PropTypes.object, // File data retrieved from search request
        hideGraph: React.PropTypes.bool, // T to hide graph display
        altFilterDefault: React.PropTypes.bool, // T to default to All Assemblies and Annotations
    },

    contextTypes: {
        session: React.PropTypes.object,
        session_properties: React.PropTypes.object,
        location_href: React.PropTypes.string,
    },

    getInitialState: function () {
        return {
            selectedFilterValue: '', // <select> value of selected filter
            infoNodeId: '', // @id of node whose info panel is open
            infoModalOpen: false, // True if info modal is open
        };
    },

    // Set the default filter after the graph has been analayzed once.
    componentDidMount: function () {
        if (!this.props.altFilterDefault) {
            this.setFilter('0');
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
        const stateValue = value === 'default' ? '' : value;
        this.setState({ selectedFilterValue: stateValue });
    },

    // React to a filter menu selection. The synthetic event given in `e`
    handleFilterChange: function (e) {
        this.setFilter(e.target.value);
    },

    render: function () {
        const { context, data } = this.props;
        let selectedAssembly = '';
        let selectedAnnotation = '';
        let jsonGraph;
        let allGraphedFiles;
        const items = data ? data['@graph'] : []; // Array of searched files arrives in data.@graph result

        // Combined object's files and search results files for display
        const files = _.uniq(((context.files && context.files.length) ? context.files : []).concat((items && items.length) ? items : []));
        if (files.length === 0) {
            return null;
        }

        const filterOptions = files.length ? collectAssembliesAnnotations(files) : [];
        const loggedIn = this.context.session && this.context.session['auth.userid'];

        if (this.state.selectedFilterValue && filterOptions[this.state.selectedFilterValue]) {
            selectedAssembly = filterOptions[this.state.selectedFilterValue].assembly;
            selectedAnnotation = filterOptions[this.state.selectedFilterValue].annotation;
        }

        // Get a list of files for the graph (filters out archived files)
        const graphFiles = _(files).filter(file => file.status !== 'archived');

        // Build node graph of the files and analysis steps with this experiment
        if (graphFiles && graphFiles.length) {
            try {
                const { graph, graphedFiles } = assembleGraph(context, this.context.session, this.state.infoNodeId, files, selectedAssembly, selectedAnnotation);
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
                        {context.visualize_ucsc && context.status === 'released' ?
                            <div className="file-gallery-control">
                                <DropdownButton title="Visualize Data" label="visualize-data">
                                    <DropdownMenu>
                                        {Object.keys(context.visualize_ucsc).map(assembly =>
                                            <a key={assembly} data-bypass="true" target="_blank" rel="noopener noreferrer" href={context.visualize_ucsc[assembly]}>
                                                {assembly}
                                            </a>
                                        )}
                                    </DropdownMenu>
                                </DropdownButton>
                            </div>
                        : null}
                        {filterOptions.length ?
                            <div className="file-gallery-control file-gallery-control-select">
                                <FilterMenu selectedFilterValue={this.state.selectedFilterValue} filterOptions={filterOptions} handleFilterChange={this.handleFilterChange} />
                            </div>
                        : null}
                    </div>
                </PanelHeading>

                {!this.props.hideGraph ?
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
                        adminUser={!!this.context.session_properties.admin}
                        forceRedraw
                    />
                : null}

                {/* If logged in and dataset is released, need to combine search of files that reference
                    this dataset to get released and unreleased ones. If not logged in, then just get
                    files from dataset.files */}
                {loggedIn && (context.status === 'released' || context.status === 'release ready') ?
                    <FetchedItems
                        {...this.props}
                        url={globals.unreleased_files_url(context)}
                        adminUser={!!this.context.session_properties.admin}
                        Component={DatasetFiles}
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
                        ignoreErrors
                        noDefaultClasses
                    />
                :
                    <FileTable
                        {...this.props}
                        items={context.files}
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
                        adminUser={!!this.context.session_properties.admin}
                    />
                }
            </Panel>
        );
    },
});


const CollapsingTitle = React.createClass({
    propTypes: {
        title: React.PropTypes.string.isRequired, // Title to display in the title bar
        handleCollapse: React.PropTypes.func.isRequired, // Function to call to handle click in collapse button
        selectedFilterValue: React.PropTypes.string, // Currently selected filter
        filterOptions: React.PropTypes.array, // Array of filtering options
        handleFilterChange: React.PropTypes.func, // Function to call when filter menu item is chosen
        collapsed: React.PropTypes.bool, // T if the panel this is over has been collapsed
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
const FilterMenu = React.createClass({
    propTypes: {
        selectedFilterValue: React.PropTypes.string, // Currently selected filter
        filterOptions: React.PropTypes.array.isRequired, // Contents of the filtering menu
        handleFilterChange: React.PropTypes.func.isRequired, // Call when a filtering option changes
    },

    render: function () {
        const { filterOptions, handleFilterChange } = this.props;
        const selectedFilterValue = this.props.selectedFilterValue ? this.props.selectedFilterValue : 'default';

        return (
            <select className="form-control" defaultValue="0" value={selectedFilterValue} onChange={handleFilterChange}>
                <option value="default" key="title">All Assemblies and Annotations</option>
                <option disabled="disabled" />
                {filterOptions.map((option, i) =>
                    <option key={i} value={i}>{`${option.assembly + (option.annotation ? ` ${option.annotation}` : '')}`}</option>
                )}
            </select>
        );
    },
});


// List of quality metric properties to not display
const qcReservedProperties = ['uuid', 'assay_term_name', 'assay_term_id', 'attachment', 'award', 'lab', 'submitted_by', 'level', 'status', 'date_created', 'step_run', 'schema_version'];


// For each type of quality metric, make a list of attachment properties. If the quality_metric object has an attachment
// property called `attachment`, it doesn't need to be added here -- this is only for attachment properties with arbitrary names.
// Each property in the list has an associated human-readable description for display on the page.
const qcAttachmentProperties = {
    IDRQualityMetric: [
        { IDR_plot_true: 'IDR dispersion plot for true replicates' },
        { IDR_plot_rep1_pr: 'IDR dispersion plot for replicate 1 pseudo-replicates' },
        { IDR_plot_rep2_pr: 'IDR dispersion plot for replicate 2 pseudo-replicates' },
        { IDR_plot_pool_pr: 'IDR dispersion plot for pool pseudo-replicates' },
        { IDR_parameters_true: 'IDR run parameters for true replicates' },
        { IDR_parameters_rep1_pr: 'IDR run parameters for replicate 1 pseudo-replicates' },
        { IDR_parameters_rep2_pr: 'IDR run parameters for replicate 2 pseudo-replicates' },
        { IDR_parameters_pool_pr: 'IDR run parameters for pool pseudo-replicates' },
    ],
    ChipSeqFilterQualityMetric: [
        { cross_correlation_plot: 'Cross-correlation plot' },
    ],
};


// Display QC metrics of the selected QC sub-node in a file node.
function qcDetailsView(metrics) {
    if (metrics) {
        const id2accessionRE = /\/\w+\/(\w+)\//;
        let qcPanels = []; // Each QC metric panel to display
        let filesOfMetric = []; // Array of accessions of files that share this metric

        // Make an array of the accessions of files that share this quality metrics object.
        // quality_metric_of is an array of @ids because they're not embedded, and we're trying
        // to avoid embedding where not absolutely needed. So use a regex to extract the files'
        // accessions from the @ids. After generating the array, filter out empty entries.
        if (metrics.ref.quality_metric_of && metrics.ref.quality_metric_of.length) {
            filesOfMetric = metrics.ref.quality_metric_of.map((metricId) => {
                // Extract the file's accession from the @id
                const match = id2accessionRE.exec(metricId);

                // Return matches that *don't* match the file whose QC node we've clicked
                if (match && (match[1] !== metrics.parent.accession)) {
                    return match[1];
                }
                return '';
            }).filter(acc => !!acc);
        }

        // Filter out QC metrics properties not to display based on the qcReservedProperties list, as well as those properties with keys
        // beginning with '@'. Sort the list of property keys as well.
        const sortedKeys = Object.keys(metrics.ref).filter(key => key[0] !== '@' && qcReservedProperties.indexOf(key) === -1).sort();

        // Get the list of attachment properties for the given qc object @type. and generate the JSX for their display panels.
        // The list of keys for attachment properties to display comes from qcAttachmentProperties. Use the @type for the attachment
        // property as a key to retrieve the list of properties appropriate for that QC type.
        const qcAttachmentPropertyList = qcAttachmentProperties[metrics.ref['@type'][0]];
        if (qcAttachmentPropertyList) {
            qcPanels = _(qcAttachmentPropertyList.map((attachmentPropertyInfo) => {
                // Each object in the list has only one key (the metric attachment property name), so get it here.
                const attachmentPropertyName = Object.keys(attachmentPropertyInfo)[0];
                const attachment = metrics.ref[attachmentPropertyName];

                // Generate the JSX for the panel. Use the property name as the key to get the corresponding human-readable description for the title
                if (attachment) {
                    return <AttachmentPanel context={metrics.ref} attachment={metrics.ref[attachmentPropertyName]} title={attachmentPropertyInfo[attachmentPropertyName]} />;
                }
                return null;
            })).compact();
        }

        // Convert the QC metric object @id to a displayable string
        let qcName = metrics.ref['@id'].match(/^\/([a-z0-9-]*)\/.*$/i);
        if (qcName && qcName[1]) {
            qcName = qcName[1].replace(/-/g, ' ');
            qcName = qcName[0].toUpperCase() + qcName.substring(1);
        }

        const header = (
            <div className="details-view-info">
                <h4>{qcName} of {metrics.parent.accession}</h4>
                {filesOfMetric.length ? <h5>Shared with {filesOfMetric.join(', ')}</h5> : null}
            </div>
        );
        const body = (
            <div>
                <div className="row">
                    <div className="col-md-4 col-sm-6 col-xs-12">
                        <dl className="key-value">
                            {sortedKeys.map(key =>
                                ((typeof metrics.ref[key] === 'string' || typeof metrics.ref[key] === 'number') ?
                                    <div key={key}>
                                        <dt>{key}</dt>
                                        <dd>{metrics.ref[key]}</dd>
                                    </div>
                                : null)
                            )}
                        </dl>
                    </div>

                    {(qcPanels && qcPanels.length) || metrics.ref.attachment ?
                        <div className="col-md-8 col-sm-12 quality-metrics-attachments">
                            <div className="row">
                                <h5>Quality metric attachments</h5>
                                <div className="flexrow attachment-panel-inner">
                                    {/* If the metrics object has an `attachment` property, display that first, then display the properties
                                        not named `attachment` but which have their own schema attribute, `attachment`, set to true */}
                                    {metrics.ref.attachment ?
                                        <AttachmentPanel context={metrics.ref} attachment={metrics.ref.attachment} />
                                    : null}
                                    {qcPanels}
                                </div>
                            </div>
                        </div>
                    : null}
                </div>
            </div>
        );
        return { header: header, body: body };
    }
    return { header: null, body: null };
}


const FileGraph = React.createClass({
    propTypes: {
        items: React.PropTypes.array, // Array of files we're graphing
        graph: React.PropTypes.object, // JsonGraph object generated from files
        selectedAssembly: React.PropTypes.string, // Currently selected assembly
        selectedAnnotation: React.PropTypes.string, // Currently selected annotation
        setInfoNodeId: React.PropTypes.func, // Function to call to set the currently selected node ID
        setInfoNodeVisible: React.PropTypes.func, // Function to call to set the visibility of the node's modal
        infoNodeId: React.PropTypes.string, // ID of selected node in graph
        infoNodeVisible: React.PropTypes.bool, // True if node's modal is vibible
        session: React.PropTypes.object, // Current user's login information
        adminUser: React.PropTypes.bool, // True if logged in user is an admin
    },

    getInitialState: function () {
        return {
            infoModalOpen: false, // Graph information modal open
            collapsed: false, // T if graphing panel is collapsed
        };
    },

    // Render metadata if a graph node is selected.
    // jsonGraph: JSON graph data.
    // infoNodeId: ID of the selected node
    detailNodes: function (jsonGraph, infoNodeId, loggedIn, adminUser) {
        let meta;

        // Find data matching selected node, if any
        if (infoNodeId) {
            if (infoNodeId.indexOf('qc:') === -1) {
                // Not a QC subnode; render normally
                const node = jsonGraph.getNode(infoNodeId);
                if (node) {
                    meta = globals.graph_detail.lookup(node)(node, this.handleNodeClick, loggedIn, adminUser);
                }
            } else {
                // QC subnode
                const subnode = jsonGraph.getSubnode(infoNodeId);
                if (subnode) {
                    meta = qcDetailsView(subnode);
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
        const { session, adminUser, items, graph, selectedAssembly, selectedAnnotation, infoNodeId, infoNodeVisible } = this.props;
        const loggedIn = !!(session && session['auth.userid']);
        const files = items;

        // Build node graph of the files and analysis steps with this experiment
        if (files && files.length) {
            // If we have a graph, or if we have a selected assembly/annotation, draw the graph panel
            const goodGraph = graph && Object.keys(graph).length;
            if (goodGraph) {
                if (selectedAssembly || selectedAnnotation) {
                    const meta = this.detailNodes(graph, infoNodeId, loggedIn, adminUser);

                    return (
                        <div>
                            <div className="file-gallery-graph-header collapsing-title">
                                <button className="collapsing-title-trigger" onClick={this.handleCollapse}>{collapseIcon(this.state.collapsed, 'collapsing-title-icon')}</button>
                                <h4>Association graph</h4>
                            </div>
                            {!this.state.collapsed ?
                                <div>
                                    <Graph graph={graph} nodeClickHandler={this.handleNodeClick} noDefaultClasses forceRedraw />
                                </div>
                            : null}
                            <div className={`file-gallery-graph-footer${this.state.collapsed ? ' hiding' : ''}`} />
                            {meta && infoNodeVisible ?
                                <Modal closeModal={this.closeModal}>
                                    <ModalHeader closeModal={this.closeModal}>
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
            return <p className="browser-error">Graph not applicable to this experiment’s files.</p>;
        }
        return null;
    },
});


// Extract a displayable string from a QualityMetric object passed in the `qc` parameter.
function qcIdToDisplay(qc) {
    let qcName = qc['@id'].match(/^\/([a-z0-9-]*)\/.*$/i);
    if (qcName && qcName[1]) {
        qcName = qcName[1].replace(/-/g, ' ');
        qcName = qcName[0].toUpperCase() + qcName.substring(1);
        return qcName;
    }
    return '';
}


// Display a QC button in the file modal.
const FileQCButton = React.createClass({
    propTypes: {
        qc: React.PropTypes.object.isRequired, // QC object we're directing to
        file: React.PropTypes.object.isRequired, // File this QC object is attached to
        handleClick: React.PropTypes.func.isRequired, // Function to open a modal to the given object
    },

    handleClick: function () {
        const qcId = `qc:${this.props.qc['@id']}${this.props.file['@id']}`;
        this.props.handleClick(qcId);
    },

    render: function () {
        const qcName = qcIdToDisplay(this.props.qc);
        if (qcName) {
            return <button className="btn btn-info btn-xs" onClick={this.handleClick}>{qcName}</button>;
        }
        return null;
    },
});


// Display the metadata of the selected file in the graph
const FileDetailView = function (node, qcClick, loggedIn, adminUser) {
    // The node is for a file
    const selectedFile = node.metadata.ref;
    let body = null;
    let header = null;

    if (selectedFile) {
        let contributingAccession;

        if (node.metadata.contributing) {
            const accessionStart = selectedFile.dataset.indexOf('/', 1) + 1;
            const accessionEnd = selectedFile.dataset.indexOf('/', accessionStart) - accessionStart;
            contributingAccession = selectedFile.dataset.substr(accessionStart, accessionEnd);
        }
        const dateString = !!selectedFile.date_created && moment.utc(selectedFile.date_created).format('YYYY-MM-DD');
        header = (
            <div className="details-view-info">
                <h4>{selectedFile.file_type} {selectedFile.accession}</h4>
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

                    {selectedFile.replicate ?
                        <div data-test="bioreplicate">
                            <dt>Biological replicate(s)</dt>
                            <dd>{`[${selectedFile.replicate.biological_replicate_number}]`}</dd>
                        </div>
                    : (selectedFile.biological_replicates && selectedFile.biological_replicates.length ?
                        <div data-test="bioreplicate">
                            <dt>Biological replicate(s)</dt>
                            <dd>{`[${selectedFile.biological_replicates.join(', ')}]`}</dd>
                        </div>
                    : null)}

                    {selectedFile.replicate ?
                        <div data-test="techreplicate">
                            <dt>Technical replicate</dt>
                            <dd>{selectedFile.replicate.technical_replicate_number}</dd>
                        </div>
                    : (selectedFile.biological_replicates && selectedFile.biological_replicates.length ?
                        <div data-test="techreplicate">
                            <dt>Technical replicate</dt>
                            <dd>{'-'}</dd>
                        </div>
                    : null)}

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

                    {selectedFile.quality_metrics && selectedFile.quality_metrics.length ?
                        <div data-test="fileqc">
                            <dt>File quality metrics</dt>
                            <dd className="file-qc-buttons">
                                {selectedFile.quality_metrics.map(qc =>
                                    <FileQCButton qc={qc} file={selectedFile} handleClick={qcClick} />
                                )}
                            </dd>
                        </div>
                    : null}
                </dl>
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
