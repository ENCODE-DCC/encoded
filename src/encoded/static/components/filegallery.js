'use strict';
var React = require('react');
var globals = require('./globals');
var {Panel, PanelBody, PanelHeading} = require('../libs/bootstrap/panel');
var {DropdownButton} = require('../libs/bootstrap/button');
var {DropdownMenu} = require('../libs/bootstrap/dropdown-menu');
var {AuditIcon} = require('./audit');
var {StatusLabel} = require('./statuslabel');
var {Graph, JsonGraph} = require('./graph');
var {SoftwareVersionList} = require('./software');
var {FetchedItems, FetchedData, Param} = require('./fetched');
var _ = require('underscore');
var moment = require('moment');
var {CollapseIcon} = require('../libs/svg-icons');
var {SortTablePanel, SortTable} = require('./sorttable');
var {AttachmentPanel} = require('./doc');


// Order that assemblies should appear in filtering menu
var assemblyPriority = [
    'GRCh38',
    'hg19',
    'mm10',
    'mm9',
    'ce11',
    'ce10',
    'dm6',
    'dm3',
    'J02459.1'
];

var FileTable = module.exports.FileTable = React.createClass({
    propTypes: {
        context: React.PropTypes.object, // Optional parent object of file list
        items: React.PropTypes.array.isRequired, // Array of files to appear in the table
        originating: React.PropTypes.bool, // TRUE to display originating dataset column
        session: React.PropTypes.object // Persona user session
    },

    getInitialState: function() {
        return {
            maxWidth: 'auto', // Width of widest table
            collapsed: { // Keeps track of which tables are collapsed
                'raw': false,
                'rawArray': false,
                'proc': false,
                'ref': false
            }
        };
    },

    cv: {
        maxWidthRef: '', // ref key of table with this.state.maxWidth width
        maxWidthNode: null // DOM node of table with this.state.maxWidth width 
    },

    // Configuration for raw file table
    rawTableColumns: {
        'accession': {
            title: 'Accession',
            display: item =>
                <span>
                    {item.title}&nbsp;<a href={item.href} download={item.href.substr(item.href.lastIndexOf("/") + 1)} data-bypass="true"><i className="icon icon-download"><span className="sr-only">Download</span></i></a>
                </span>
        },
        'file_type': {title: 'File type'},
        'biological_replicates': {
            title: (list, columns, meta) => <span>{meta.anisogenic ? 'Anisogenic' : 'Biological'} replicate</span>,
            getValue: item => item.biological_replicates ? item.biological_replicates.sort(function(a,b){ return a - b; }).join(', ') : ''
        },
        'library': {
            title: 'Library',
            getValue: item => (item.replicate && item.replicate.library) ? item.replicate.library.accession : null
        },
        'run_type': {
            title: 'Run type',
            display: item => {
                var runType;

                if (item.run_type === 'single-ended') {
                    runType = 'SE';
                } else if (item.run_type === 'paired-ended') {
                    runType = 'PE';
                }

                return (
                    <span>
                        <span>{runType ? runType : null}</span>
                        <span>{item.read_length ? <span>{runType ? <span> </span> : null}{item.read_length + item.read_length_units}</span> : null}</span>
                    </span>
                );
            },
            objSorter: (a, b) => {
                // Sort by their combined string values
                var aStr = (a.run_type ? a.run_type : '') + (a.read_length ? a.read_length : '');
                var bStr = (b.run_type ? b.run_type : '') + (b.read_length ? b.read_length : '');
                return (aStr < bStr) ? -1 : (bStr < aStr ? 1 : 0);
            }
        },
        'paired_end': {
            title: 'Read',
            display: item => <span>{item.paired_end ? <span>R{item.paired_end}</span> : null}</span>
        },
        'title': {
            title: 'Lab',
            getValue: item => item.lab && item.lab.title ? item.lab.title : null
        },
        'date_created': {
            title: 'Date added',
            getValue: item => moment.utc(item.date_created).format('YYYY-MM-DD'),
            sorter: (a, b) => {
                if (a && b) {
                    return Date.parse(a) - Date.parse(b);
                }
                return a ? -1 : (b ? 1 : 0);
            }
        },
        'file_size': {
            title: 'File size',
            display: item => <span>{humanFileSize(item.file_size)}</span>
        },
        'audit': {
            title: 'Audit status',
            display: item => <div>{fileAuditStatus(item)}</div>
        },
        'status': {
            title: 'File status',
            display: item => <div className="characterization-meta-data"><StatusLabel status={item.status} /></div>,
            hide: (list, columns, meta) => !(meta.session && meta.session['auth.userid'])
        }
    },

    // Configuration for raw file table
    rawArrayTableColumns: {
        'accession': {
            title: 'Accession',
            display: item =>
                <span>
                    {item.title}&nbsp;<a href={item.href} download={item.href.substr(item.href.lastIndexOf("/") + 1)} data-bypass="true"><i className="icon icon-download"><span className="sr-only">Download</span></i></a>
                </span>
        },
        'file_type': {title: 'File type'},
        'biological_replicates': {
            title: (list, columns, meta) => <span>{meta.anisogenic ? 'Anisogenic' : 'Biological'} replicate</span>,
            getValue: item => item.biological_replicates ? item.biological_replicates.sort(function(a,b){ return a - b; }).join(', ') : ''
        },
        'library': {
            title: 'Library',
            getValue: item => (item.replicate && item.replicate.library) ? item.replicate.library.accession : null
        },
        'assembly': {title: 'Mapping assembly'},
        'title': {
            title: 'Lab',
            getValue: item => item.lab && item.lab.title ? item.lab.title : null
        },
        'date_created': {
            title: 'Date added',
            getValue: item => moment.utc(item.date_created).format('YYYY-MM-DD'),
            sorter: (a, b) => {
                if (a && b) {
                    return Date.parse(a) - Date.parse(b);
                }
                return a ? -1 : (b ? 1 : 0);
            }
        },
        'file_size': {
            title: 'File size',
            display: item => <span>{humanFileSize(item.file_size)}</span>
        },
        'audit': {
            title: 'Audit status',
            display: item => <div>{fileAuditStatus(item)}</div>
        },
        'status': {
            title: 'File status',
            display: item => <div className="characterization-meta-data"><StatusLabel status={item.status} /></div>,
            hide: (list, columns, meta) => !(meta.session && meta.session['auth.userid'])
        }
    },

    // Configuration for process file table
    procTableColumns: {
        'accession': {
            title: 'Accession',
            display: item => {
                return <span>
                    {item.title}&nbsp;<a href={item.href} download={item.href.substr(item.href.lastIndexOf("/") + 1)} data-bypass="true"><i className="icon icon-download"><span className="sr-only">Download</span></i></a>
                </span>;
            }
        },
        'file_type': {title: 'File type'},
        'output_type': {title: 'Output type'},
        'biological_replicates': {
            title: (list, columns, meta) => <span>{meta.anisogenic ? 'Anisogenic' : 'Biological'} replicate</span>,
            getValue: item => item.biological_replicates ? item.biological_replicates.sort(function(a,b){ return a - b; }).join(', ') : ''
        },
        'assembly': {title: 'Mapping assembly'},
        'genome_annotation': {
            title: 'Genome annotation',
            hide: (list, columns, meta) => _(list).all(item => !item.genome_annotation)
        },
        'title': {
            title: 'Lab',
            getValue: item => item.lab && item.lab.title ? item.lab.title : null
        },
        'date_created': {
            title: 'Date added',
            getValue: item => moment.utc(item.date_created).format('YYYY-MM-DD'),
            sorter: (a, b) => {
                if (a && b) {
                    return Date.parse(a) - Date.parse(b);
                }
                return a ? -1 : (b ? 1 : 0);
            }
        },
        'file_size': {
            title: 'File size',
            display: item => <span>{humanFileSize(item.file_size)}</span>
        },
        'audit': {
            title: 'Audit status',
            display: item => <div>{fileAuditStatus(item)}</div>
        },
        'status': {
            title: 'File status',
            display: item => <div className="characterization-meta-data"><StatusLabel status={item.status} /></div>,
            hide: (list, columns, meta) => !(meta.session && meta.session['auth.userid'])
        }
    },

    // Configuration for reference file table
    refTableColumns: {
        'accession': {
            title: 'Accession',
            display: item =>
                <span>
                    {item.title}&nbsp;<a href={item.href} download={item.href.substr(item.href.lastIndexOf("/") + 1)} data-bypass="true"><i className="icon icon-download"><span className="sr-only">Download</span></i></a>
                </span>
        },
        'file_type': {title: 'File type'},
        'output_type': {title: 'Output type'},
        'assembly': {title: 'Mapping assembly'},
        'genome_annotation': {
            title: 'Genome annotation',
            hide: (list, columns, meta) => _(list).all(item => !item.genome_annotation)
        },
        'title': {
            title: 'Lab',
            getValue: item => item.lab && item.lab.title ? item.lab.title : null
        },
        'date_created': {
            title: 'Date added',
            getValue: item => moment.utc(item.date_created).format('YYYY-MM-DD'),
            sorter: (a, b) => {
                if (a && b) {
                    return Date.parse(a) - Date.parse(b);
                }
                return a ? -1 : (b ? 1 : 0);
            }
        },
        'file_size': {
            title: 'File size',
            display: item => <span>{humanFileSize(item.file_size)}</span>
        },
        'audit': {
            title: 'Audit status',
            display: item => <div>{fileAuditStatus(item)}</div>
        },
        'status': {
            title: 'File status',
            display: item => <div className="characterization-meta-data"><StatusLabel status={item.status} /></div>,
            hide: (list, columns, meta) => !(meta.session && meta.session['auth.userid'])
        }
    },

    handleCollapse: function(table) {
        // Handle a click on a collapse button by toggling the corresponding tableCollapse state var
        var collapsed = _.clone(this.state.collapsed);
        collapsed[table] = !collapsed[table];
        this.setState({collapsed: collapsed});
    },

    render: function() {
        var {
            context,
            items,
            filePanelHeader,
            encodevers,
            selectedFilterValue,
            filterOptions,
            handleFilterChange,
            anisogenic,
            showFileCount,
            session
        } = this.props;
        var selectedAssembly, selectedAnnotation;

        var datasetFiles = _((items && items.length) ? items : []).uniq(file => file['@id']);
        if (datasetFiles.length) {
            var unfilteredCount = datasetFiles.length;

            if (selectedFilterValue && filterOptions[selectedFilterValue]) {
                selectedAssembly = filterOptions[selectedFilterValue].assembly;
                selectedAnnotation = filterOptions[selectedFilterValue].annotation;
            }

            // Filter all the files according to the given filters, and remove duplicates
            datasetFiles = _(datasetFiles).filter(file => {
                if (file.output_category !== 'raw data') {
                    if (selectedAssembly) {
                        if (selectedAnnotation) {
                            return selectedAnnotation === file.genome_annotation && selectedAssembly === file.assembly;
                        } else {
                            return !file.genome_annotation && selectedAssembly === file.assembly;
                        }
                    }
                }
                return true;
            });
            var filteredCount = datasetFiles.length;

            // Extract four kinds of file arrays
            var files = _(datasetFiles).groupBy(file => {
                if (file.output_category === 'raw data') {
                    return file.output_type === 'reads' ? 'raw' : 'rawArray';
                } else if (file.output_category === 'reference') {
                    return 'ref';
                } else {
                    return 'proc';
                }
            });

            return (
                <div>
                    {showFileCount ? <div className="file-gallery-counts">Displaying {filteredCount} of {unfilteredCount} files</div> : null}
                    <SortTablePanel header={filePanelHeader} noDefaultClasses={this.props.noDefaultClasses}>
                        <SortTable title={<CollapsingTitle title="Raw data" collapsed={this.state.collapsed.raw} handleCollapse={this.handleCollapse.bind(null, 'raw')} />} collapsed={this.state.collapsed.raw}
                            list={files.raw} columns={this.rawTableColumns} meta={{encodevers: encodevers, anisogenic: anisogenic, session: session}} sortColumn="biological_replicates" />
                        <SortTable title={<CollapsingTitle title="Raw data" collapsed={this.state.collapsed.rawArray} handleCollapse={this.handleCollapse.bind(null, 'rawArray')} />} collapsed={this.state.collapsed.rawArray}
                            list={files.rawArray} columns={this.rawArrayTableColumns} meta={{encodevers: encodevers, anisogenic: anisogenic, session: session}} sortColumn="biological_replicates" />
                        <SortTable title={<CollapsingTitle title="Processed data" collapsed={this.state.collapsed.proc} handleCollapse={this.handleCollapse.bind(null, 'proc')}
                            selectedFilterValue={selectedFilterValue} filterOptions={filterOptions} handleFilterChange={handleFilterChange} />}
                            collapsed={this.state.collapsed.proc} list={files.proc} columns={this.procTableColumns} meta={{encodevers: encodevers, anisogenic: anisogenic, session: session}} sortColumn="biological_replicates" />
                        <SortTable title={<CollapsingTitle title="Reference data" collapsed={this.state.collapsed.ref} handleCollapse={this.handleCollapse.bind(null, 'ref')} />} collapsed={this.state.collapsed.ref}
                            list={files.ref} columns={this.refTableColumns} meta={{encodevers: encodevers, anisogenic: anisogenic, session: session}} />
                    </SortTablePanel>
                </div>
            );
        }
        return null;
    }
});


// Called once searches for unreleased files returns results in this.props.items. Displays both released and
// unreleased files.
var DatasetFiles = module.exports.DatasetFiles = React.createClass({
    render: function () {
        var context = this.props.context;
        var items = this.props.items;

        var files = _.uniq(((context.files && context.files.length) ? context.files : []).concat((items && items.length) ? items : []));
        if (files.length) {
            return <FileTable {...this.props} items={files} />;
        } else {
            return null;
        }
    }
});


// File display widget, showing a facet list, a table, and a graph (and maybe a BioDalliance).
// This component only triggers the data retrieval, which is done with a search for files associated
// with the given experiment (in this.props.context). An odd thing is we specify query-string parameters
// to the experiment URL, but they apply to the file search -- not the experiment itself.
var FileGallery = module.exports.FileGallery = React.createClass({
    propTypes: {
        encodevers: React.PropTypes.string, // ENCODE version number
        anisogenic: React.PropTypes.bool, // True if anisogenic experiment
        hideGraph: React.PropTypes.bool, // T to hide graph display
        altFilterDefault: React.PropTypes.bool // T to default to All Assemblies and Annotations
    },

    contextTypes: {
        session: React.PropTypes.object, // Login information
        location_href: React.PropTypes.string // URL of this experiment page, including query string stuff
    },

    render: function() {
        var {context, encodevers, anisogenic, hideGraph, altFilterDefault} = this.props;

        return (
            <FetchedData ignoreErrors>
                <Param name="data" url={globals.unreleased_files_url(context)} />
                <FileGalleryRenderer context={context} session={this.context.session} encodevers={encodevers} anisogenic={anisogenic} hideGraph={hideGraph} altFilterDefault={altFilterDefault} />
            </FetchedData>
        );
    }
});


// Function to render the file gallery, and it gets called after the file search results (for files associated with
// the displayed experiment) return.
var FileGalleryRenderer = React.createClass({
    propTypes: {
        encodevers: React.PropTypes.string, // ENCODE version number
        anisogenic: React.PropTypes.bool, // True if anisogenic experiment
        hideGraph: React.PropTypes.bool, // T to hide graph display
        altFilterDefault: React.PropTypes.bool // T to default to All Assemblies and Annotations
    },

    contextTypes: {
        session: React.PropTypes.object,
        location_href: React.PropTypes.string
    },

    getInitialState: function() {
        return {
            selectedFilterValue: '' // <select> value of selected filter
        };
    },

    // Set the graph filter based on the given <option> value
    setFilter: function(value) {
        if (value === 'default') {
            value = '';
        }
        this.setState({selectedFilterValue: value});
    },

    // React to a filter menu selection. The synthetic event given in `e`
    handleFilterChange: function(e) {
        this.setFilter(e.target.value);
    },

    // Set the default filter after the graph has been analayzed once.
    componentDidMount: function() {
        if (!this.props.altFilterDefault) {
            this.setFilter('0');
        }
    },

    render: function() {
        var {context, data} = this.props;
        var selectedAssembly = '';
        var selectedAnnotation = '';
        var items = data ? data['@graph'] : []; // Array of searched files arrives in data.@graph result

        // Combined object's files and search results files for display
        var files = _.uniq(((context.files && context.files.length) ? context.files : []).concat((items && items.length) ? items : []));
        if (files.length === 0) {
            return null;
        }

        var filterOptions = files.length ? collectAssembliesAnnotations(files) : [];
        var loggedIn = this.context.session && this.context.session['auth.userid'];

        if (this.state.selectedFilterValue && filterOptions[this.state.selectedFilterValue]) {
            selectedAssembly = filterOptions[this.state.selectedFilterValue].assembly;
            selectedAnnotation = filterOptions[this.state.selectedFilterValue].annotation;
        }

        return (
            <Panel>
                <PanelHeading addClasses="file-gallery-heading">
                    <h4>Files</h4>
                    <div className="file-gallery-controls">
                        {context.visualize_ucsc  && context.status == "released" ?
                            <div className="file-gallery-control">
                                <DropdownButton title='Visualize Data' label="visualize-data">
                                    <DropdownMenu>
                                        {Object.keys(context.visualize_ucsc).map(assembly =>
                                            <a key={assembly} data-bypass="true" target="_blank" private-browsing="true" href={context.visualize_ucsc[assembly]}>
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
                    <FileGraph context={context} items={files} selectedAssembly={selectedAssembly} selectedAnnotation={selectedAnnotation} session={this.context.session} forceRedraw />
                : null}

                {/* If logged in and dataset is released, need to combine search of files that reference
                    this dataset to get released and unreleased ones. If not logged in, then just get
                    files from dataset.files */}
                {loggedIn && (context.status === 'released' || context.status === 'release ready') ?
                    <FetchedItems {...this.props} url={globals.unreleased_files_url(context)} Component={DatasetFiles}
                        selectedFilterValue={this.state.selectedFilterValue} filterOptions={filterOptions} handleFilterChange={this.handleFilterChange}
                        encodevers={globals.encodeVersion(context)} session={this.context.session} showFileCount ignoreErrors noDefaultClasses />
                :
                    <FileTable {...this.props} items={context.files} selectedFilterValue={this.state.selectedFilterValue}
                        filterOptions={filterOptions} handleFilterChange={this.handleFilterChange}
                        encodevers={globals.encodeVersion(context)} session={this.context.session} showFileCount noDefaultClasses />
                }
            </Panel>
        );
    }
});


var CollapsingTitle = React.createClass({
    propTypes: {
        title: React.PropTypes.string.isRequired, // Title to display in the title bar
        handleCollapse: React.PropTypes.func.isRequired, // Function to call to handle click in collapse button
        selectedFilterValue: React.PropTypes.string, // Currently selected filter
        filterOptions: React.PropTypes.array, // Array of filtering options
        handleFilterChange: React.PropTypes.func, // Function to call when filter menu item is chosen
        collapsed: React.PropTypes.bool // T if the panel this is over has been collapsed
    },

    render: function() {
        var {title, handleCollapse, collapsed, filterOptions, selectedFilterValue, handleFilterChange} = this.props;
        return (
            <div className="collapsing-title">
                <a href="#" className="collapsing-title-trigger pull-left" data-trigger onClick={handleCollapse}>{CollapseIcon(collapsed, 'collapsing-title-icon')}</a>
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
    }
});


// Display a filtering <select>. `filterOptions` is an array of objects with two properties:
// `assembly` and `annotation`. Both are strings that get concatenated to form each menu item. The
// value of each <option> is its zero-based index.
var FilterMenu = React.createClass({
    propTypes: {
        selectedFilterValue: React.PropTypes.string, // Currently selected filter
        filterOptions: React.PropTypes.array.isRequired, // Contents of the filtering menu
        handleFilterChange: React.PropTypes.func.isRequired // Call when a filtering option changes
    },

    render: function() {
        var {selectedFilterValue, filterOptions, handleFilterChange} = this.props;
        selectedFilterValue = selectedFilterValue ? selectedFilterValue : 'default';
        return (
            <select className="form-control" defaultValue="0" value={selectedFilterValue} onChange={handleFilterChange}>
                <option value="default" key="title">All Assemblies and Annotations</option>
                <option disabled="disabled"></option>
                {filterOptions.map((option, i) =>
                    <option key={i} value={i}>{option.assembly + (option.annotation ? ' ' + option.annotation : '')}</option>
                )}
            </select>
        );
    }
});


// Handle graphing throws
function graphException(message, file0, file1) {
/*jshint validthis: true */
    this.message = message;
    if (file0) {
        this.file0 = file0;
    }
    if (file1) {
        this.file1 = file1;
    }
}

module.exports.graphException = graphException;


var assembleGraph = module.exports.assembleGraph = function(context, session, infoNodeId, files, filterAssembly, filterAnnotation) {

    // Calculate a step ID from a file's derived_from array
    function _derivedFileIds(file) {
        if (file.derived_from) {
            return file.derived_from.map(function(derived) {
                return derived['@id'];
            }).sort().join();
        } else {
            return '';
        }
    }

    function _genQcId(metric, file) {
        return 'qc:' + metric['@id'] + file['@id'];
    }

    function _genFileId(file) {
        return 'file:' + file['@id'];
    }

    function _genStepId(file) {
        return 'step:' + derivedFileIds(file) + file.analysis_step['@id'];
    }

    function processFiltering(fileList, filterAssembly, filterAnnotation, allFiles, allContributing, include) {

        function getSubFileList(filesArray) {
            var fileList = {};
            filesArray.forEach(function(file) {
                fileList[file['@id']] = allFiles[file['@id']];
            });
            return fileList;
        }

        var fileKeys = Object.keys(fileList);
        for (var i = 0; i < fileKeys.length; i++) {
            var file = fileList[fileKeys[i]];
            var nextFileList;

            if (file) {
                if (!file.removed) {
                    // This file gets included. Include everything it derives from
                    if (file.derived_from && file.derived_from.length && !allContributing[file['@id']]) {
                        nextFileList = getSubFileList(file.derived_from);
                        processFiltering(nextFileList, filterAssembly, filterAnnotation, allFiles, allContributing, true);
                    }
                } else if (include) {
                    // Unremove the file if this branch is to be included based on files that derive from it
                    file.removed = false;
                    if (file.derived_from && file.derived_from.length && !allContributing[file['@id']]) {
                        nextFileList = getSubFileList(file.derived_from);
                        processFiltering(nextFileList, filterAssembly, filterAnnotation, allFiles, allContributing, true);
                    }
                }
            }
        }
    }

    var jsonGraph; // JSON graph object of entire graph; see graph.js
    var derivedFromFiles = {}; // List of all files that other files derived from
    var allFiles = {}; // All files' accessions as keys
    var allReplicates = {}; // All file's replicates as keys; each key references an array of files
    var allPipelines = {}; // List of all pipelines indexed by step @id
    var allMetricsInfo = []; // List of all QC metrics found attached to files
    var fileQcMetrics = {}; // List of all file QC metrics indexed by file ID
    var filterOptions = []; // List of graph filters; annotations and assemblies
    var stepExists = false; // True if at least one file has an analysis_step
    var fileOutsideReplicate = false; // True if at least one file exists outside a replicate
    var abortGraph = false; // True if graph shouldn't be drawn
    var abortMsg; // Console message to display if aborting graph
    var abortFileId; // @id of file that caused abort
    var derivedFileIds = _.memoize(_derivedFileIds, function(file) {
        return file['@id'];
    });
    var genQcId = _.memoize(_genQcId, function(metric, file) {
        return metric['@id'] + file['@id'];
    });
    var genStepId = _.memoize(_genStepId, function(file) {
        return file['@id'];
    });
    var genFileId = _.memoize(_genFileId, function(file) {
        return file['@id'];
    });

    // Collect all files keyed by their ID as a single source of truth for files.
    // Every reference to a file object should get it from this object. Also serves
    // to de-dup the file array since there can be repeated files in it.
    files.forEach(function(file) {
        if (!allFiles[file['@id']]) {
            allFiles[file['@id']] = file;
        }
    });

    // Collect derived_from files, used replicates, and used pipelines. allFiles has all files directly involved
    // with this experiment if we're logged in, or just released files directly involved with experiment if we're not.
    Object.keys(allFiles).forEach(function(fileId) {
        var file = allFiles[fileId];

        // Build an object keyed with all files that other files derive from. If the file is contributed,
        // we don't care about its derived_from because we don't render that.
        if (file.derived_from && file.derived_from.length) {
            file.derived_from.forEach(function(derived_from) {
                var derivedFromId = derived_from['@id'];
                var derivedFile = allFiles[derivedFromId];
                if (!derivedFile) {
                    // The derived-from file wasn't in the given file list. Copy the file object from the file's
                    // derived_from so we can examine it later -- and mark it as missing. It could be because a
                    // derived-from file isn't released and we're not logged in, or because it's a contributing file.
                    derivedFromFiles[derivedFromId] = derived_from;
                    derived_from.missing = true;
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
            var biological_replicate_number = file.biological_replicates[0];
            if (!allReplicates[biological_replicate_number]) {
                // Place a new array in allReplicates if needed
                allReplicates[biological_replicate_number] = [];
            }
            allReplicates[biological_replicate_number].push(file);
        }

        // Note whether any files have an analysis step
        var fileAnalysisStep = file.analysis_step_version && file.analysis_step_version.analysis_step;
        stepExists = stepExists || fileAnalysisStep;

        // Save the pipeline array used for each step used by the file.
        if (fileAnalysisStep) {
            allPipelines[fileAnalysisStep['@id']] = fileAnalysisStep.pipelines;
        }

        // File is derived; collect any QC info that applies to this file
        if (file.quality_metrics && file.quality_metrics.length) {
            var matchingQc = [];

            // Search file's quality_metrics array to find one with a quality_metric_of field referring to this file.
            file.quality_metrics.forEach(function(metric) {
                var matchingFile = _(metric.quality_metric_of).find(function(appliesFile) {
                    return file['@id'] === appliesFile;
                });
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
    var allContributingArray = _(derivedFromFiles).filter((derivedFromFile, derivedFromId) => {
        return _(context.contributing_files).any(contributingFile => contributingFile['@id'] === derivedFromId);
    });

    // Process the contributing files array
    var allContributing = {};
    allContributingArray.forEach(contributingFile => {
        // Convert array of contributing files to a keyed object to help with searching later
        contributingFile.missing = false;
        var contributingFileId = contributingFile['@id'];
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

    // Don't draw anything if no files have an analysis_step
    if (!stepExists) {
        throw new graphException('No graph: no files have step runs');
    }

    // Now that we know at least some files derive from each other through analysis steps, mark file objects that
    // don't derive from other files — and that no files derive from them — as removed from the graph.
    // Also build the filtering menu here; it genomic annotations and assemblies that ARE involved in the graph.
    Object.keys(allFiles).forEach(function(fileId) {
        var file = allFiles[fileId];

        // File gets removed if doesn’t derive from other files AND no files derive from it.
        var islandFile = file.removed = !(file.derived_from && file.derived_from.length) && !derivedFromFiles[fileId];

        // Add to the filtering options to generate a <select>; don't include island files
        if (!islandFile && file.output_category !== 'raw data' && file.assembly) {
            filterOptions.push({assembly: file.assembly, annotation: file.genome_annotation});
        }
    });

    // Remove any replicates containing only removed files from the last step.
    Object.keys(allReplicates).forEach(function(repNum) {
        var onlyRemovedFiles = _(allReplicates[repNum]).all(function(file) {
            return file.removed && file.missing === true;
        });
        if (onlyRemovedFiles) {
            allReplicates[repNum] = [];
        }
    });

    // Check whether any files that others derive from are missing (usually because they're unreleased and we're logged out).
    Object.keys(derivedFromFiles).forEach(function(derivedFromFileId) {
        var derivedFromFile = derivedFromFiles[derivedFromFileId];
        if (derivedFromFile.removed || derivedFromFile.missing) {
            // A file others derive from doesn't exist or was removed; check if it's in a replicate or not
            // Note the derived_from file object exists even if it doesn't exist in given files array.
            if (derivedFromFile.biological_replicates && derivedFromFile.biological_replicates.length === 1) {
                // Missing derived-from file in a replicate; remove the replicate's files and remove itself.
                var derivedFromRep = derivedFromFile.biological_replicates[0];
                if (allReplicates[derivedFromRep]) {
                    allReplicates[derivedFromRep].forEach(function(file) {
                        file.removed = true;
                    });
                }
            } else {
                // Missing derived-from file not in a replicate or in multiple replicates; don't draw any graph
                throw new graphException('No graph: derived_from file outside replicate (or in multiple replicates) missing', derivedFromFileId);
            }
        } // else the derived_from file is in files array (allFiles object); normal case
    });

    // Remove files based on the filtering options
    if (filterAssembly) {
        // First remove all raw files, and all other files with mismatched filtering options
        Object.keys(allFiles).forEach(function(fileId) {
            var file = allFiles[fileId];

            if (file.output_category === 'raw data') {
                // File is raw data; just remove it
                file.removed = true;
            } else {
                // At this stage, we know it's a process or reference file. Remove from files if
                // it has mismatched assembly or annotation
                if ((file.assembly !== filterAssembly) || ((file.genome_annotation || filterAnnotation) && (file.genome_annotation !== filterAnnotation))) {
                    file.removed = true;
                }
            }
        });

        // For all files matching the filtering options that derive from others, go up the derivation chain and re-include everything there.
        processFiltering(allFiles, filterAssembly, filterAnnotation, allFiles, allContributing);
    }

    // See if removing files by filtering have emptied a replicate.
    if (Object.keys(allReplicates).length) {
        Object.keys(allReplicates).forEach(function(replicateId) {
            var emptied = _(allReplicates[replicateId]).all(function(file) {
                return file.removed;
            });

            // If all files removed from a replicate, remove the replicate
            if (emptied) {
                allReplicates[replicateId] = [];
            }

        });
    }

    // Check whether all files have been removed
    abortGraph = _(Object.keys(allFiles)).all(function(fileId) {
        return allFiles[fileId].removed;
    });
    if (abortGraph) {
        throw new graphException('No graph: all files removed');
    }

    // No files exist outside replicates, and all replicates are removed
    var replicateIds = Object.keys(allReplicates);
    if (fileOutsideReplicate && replicateIds.length && _(replicateIds).all(function(replicateNum) {
        return !allReplicates[replicateNum].length;
    })) {
        throw new graphException('No graph: All replicates removed and no files outside replicates exist');
    }

    // Last check; see if any files derive from files now missing. This test is child-file based, where the last test
    // was based on the derived-from files.
    Object.keys(allFiles).forEach(function(fileId) {
        var file = allFiles[fileId];

        if (!file.removed && !allContributing[fileId] && file.derived_from && file.derived_from.length) {
            var derivedGoneMissing; // Just to help debugging
            var derivedGoneId; // @id of derived-from file that's either missing or removed

            // A file still in the graph derives from others. See if any of the files it derives from have been removed
            // or are missing.
            file.derived_from.forEach(function(derivedFromFile) {
                var orgDerivedFromFile = derivedFromFiles[derivedFromFile['@id']];
                var derivedGone = orgDerivedFromFile.missing || orgDerivedFromFile.removed;

                // These two just for debugging a unrendered graph
                if (derivedGone) {
                    throw new graphException('file0 derives from file1 which is ' + (orgDerivedFromFile.missing ? 'missing' : 'removed'), fileId, derivedFromFile['@id']);
                }
            });
        }
    });

    // Create an empty graph architecture that we fill in next.
    jsonGraph = new JsonGraph(context.accession);

    // Create nodes for the replicates
    Object.keys(allReplicates).forEach(function(replicateNum) {
        if (allReplicates[replicateNum] && allReplicates[replicateNum].length) {
            jsonGraph.addNode('rep:' + replicateNum, 'Replicate ' + replicateNum, {
                cssClass: 'pipeline-replicate',
                type: 'Rep',
                shape: 'rect',
                cornerRadius: 0
            });
        }
    });

    // Go through each file (released or unreleased) to add it and associated steps to the graph
    Object.keys(allFiles).forEach(function(fileId) {
        var file = allFiles[fileId];

        // Only add files derived from others, or that others derive from,
        // and that aren't part of a removed replicate
        if (!file.removed) {
            var stepId;
            var label;
            var pipelineInfo;
            var error;
            var fileNodeId = 'file:' + file['@id'];
            var replicateNode = (file.biological_replicates && file.biological_replicates.length === 1 ) ? jsonGraph.getNode('rep:' + file.biological_replicates[0]) : null;
            var metricsInfo;
            var fileContributed = allContributing[fileId];

            // Add QC metrics info from the file to the list to generate the nodes later
            if (fileQcMetrics[fileId] && fileQcMetrics[fileId].length && file.step_run) {
                metricsInfo = fileQcMetrics[fileId].map(function(metric) {
                    var qcId = genQcId(metric, file);
                    return {id: qcId, label: 'QC', class: 'pipeline-node-qc-metric' + (infoNodeId === qcId ? ' active' : ''), ref: metric, parent: file};
                });
            }

            // Add file to the graph as a node
            var fileNodeLabel, fileCssClass, fileRef;
            var loggedIn = session && session['auth.userid'];
            if (fileContributed && fileContributed.status !== 'released' && !loggedIn) {
                // A contributed file isn't released and we're not logged in
                fileNodeLabel = 'Unreleased';
                fileCssClass = 'pipeline-node-file contributing error' + (infoNodeId === fileNodeId ? ' active' : '');
                fileRef = null;
            } else {
                fileNodeLabel = file.title + ' (' + file.output_type + ')';
                fileCssClass = 'pipeline-node-file' + (fileContributed ? ' contributing' : '') + (infoNodeId === fileNodeId ? ' active' : '');
                fileRef = file;
            }
            jsonGraph.addNode(fileNodeId, fileNodeLabel, {
                cssClass: fileCssClass,
                type: 'File',
                shape: 'rect',
                cornerRadius: 16,
                parentNode: replicateNode,
                contributing: fileContributed,
                ref: fileRef
            }, metricsInfo);

            // If the file has an analysis step, prepare it for graph insertion
            if (!fileContributed) {
                var fileAnalysisStep = file.analysis_step_version && file.analysis_step_version.analysis_step;
                if (fileAnalysisStep) {
                    // Make an ID and label for the step
                    stepId = 'step:' + derivedFileIds(file) + fileAnalysisStep['@id'];
                    label = fileAnalysisStep.analysis_step_types;
                    pipelineInfo = allPipelines[fileAnalysisStep['@id']];
                    error = false;
                } else if (derivedFileIds(file)) {
                    // File derives from others, but no analysis step; make dummy step
                    stepId = 'error:' + derivedFileIds(file);
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
                            cssClass: 'pipeline-node-analysis-step' + (infoNodeId === stepId ? ' active' : '') + (error ? ' error' : ''),
                            type: 'Step',
                            shape: 'rect',
                            cornerRadius: 4,
                            parentNode: replicateNode,
                            ref: fileAnalysisStep,
                            pipelines: pipelineInfo,
                            fileId: file['@id'],
                            fileAccession: file.accession,
                            stepVersion: file.analysis_step_version
                        });
                    }

                    // Connect the file to the step, and the step to the derived_from files
                    jsonGraph.addEdge(stepId, fileNodeId);
                    file.derived_from.forEach(function(derived) {
                        if (!jsonGraph.getEdge('file:' + derived['@id'], stepId)) {
                            jsonGraph.addEdge('file:' + derived['@id'], stepId);
                        }
                    });
                }
            }
        }
    }, this);

    jsonGraph.filterOptions = filterOptions.length ? _(filterOptions).uniq(option => option.assembly + '!' + (option.annotation ? option.annotation : '')) : [];
    return jsonGraph;
};


var FileGraph = React.createClass({

    getInitialState: function() {
        return {
            infoNodeId: '', // @id of node whose info panel is open
            collapsed: false // T if graphing panel is collapsed
        };
    },

    // Render metadata if a graph node is selected.
    // jsonGraph: JSON graph data.
    // infoNodeId: ID of the selected node
    detailNodes: function(jsonGraph, infoNodeId) {
        var meta;

        // Find data matching selected node, if any
        if (infoNodeId) {
            if (infoNodeId.indexOf('qc:') === -1) {
                // Not a QC subnode; render normally
                var node = jsonGraph.getNode(infoNodeId);
                if (node) {
                    meta = globals.graph_detail.lookup(node)(node);
                }
            } else {
                // QC subnode
                var subnode = jsonGraph.getSubnode(infoNodeId);
                if (subnode) {
                    meta = QcDetailsView(subnode);
                }
            }
        }

        return meta;
    },

    // Handle a click in a graph node
    handleNodeClick: function(nodeId) {
        this.setState({infoNodeId: this.state.infoNodeId !== nodeId ? nodeId : ''});
    },

    handleCollapse: function() {
        // Handle click on panel collapse icon
        this.setState({collapsed: !this.state.collapsed});
    },

    render: function() {
        var {context, session, items, selectedAssembly, selectedAnnotation} = this.props;
        var files = items;

        // Build node graph of the files and analysis steps with this experiment
        if (files && files.length) {
            try {
                this.jsonGraph = assembleGraph(context, session, this.state.infoNodeId, files, selectedAssembly, selectedAnnotation);
            } catch(e) {
                this.jsonGraph = null;
                console.warn(e.message + (e.file0 ? ' -- file0:' + e.file0 : '') + (e.file1 ? ' -- file1:' + e.file1: ''));
            }
            var goodGraph = this.jsonGraph && Object.keys(this.jsonGraph).length;

            // If we have a graph, or if we have a selected assembly/annotation, draw the graph panel
            if (goodGraph) {
                if (selectedAssembly || selectedAnnotation) {
                    var meta = this.detailNodes(this.jsonGraph, this.state.infoNodeId);
                    return (
                        <div>
                            <div className="file-gallery-graph-header collapsing-title">
                                <a href="#" className="collapsing-title-trigger" data-trigger onClick={this.handleCollapse}>{CollapseIcon(this.state.collapsed, 'collapsing-title-icon')}</a>
                                <h4>Association graph</h4>
                            </div>
                            {!this.state.collapsed ?
                                <div>
                                    {goodGraph ?
                                        <Graph graph={this.jsonGraph} nodeClickHandler={this.handleNodeClick} noDefaultClasses forceRedraw>
                                            <div id="graph-node-info">
                                                {meta ? <PanelBody>{meta}</PanelBody> : null}
                                            </div>
                                        </Graph>
                                    :
                                        <p className="browser-error">Currently selected assembly and genomic annotation hides the graph</p>
                                    }
                                </div>
                            : null}
                            <div className={'file-gallery-graph-footer' + (this.state.collapsed ? ' hiding' : '')}></div>
                        </div>
                    );
                } else {
                    return <p className="browser-error">Choose an assembly to see file association graph</p>;
                }
            } else {
                return <p className="browser-error">Graph not applicable to this experiment’s files.</p>;
            }
        }
        return null;
    }
});


// Display the metadata of the selected file in the graph
var FileDetailView = function(node) {
    // The node is for a file
    var selectedFile = node.metadata.ref;
    var meta;

    if (selectedFile) {
        var contributingAccession;

        if (node.metadata.contributing) {
            var accessionStart = selectedFile.dataset.indexOf('/', 1) + 1;
            var accessionEnd = selectedFile.dataset.indexOf('/', accessionStart) - accessionStart;
            contributingAccession = selectedFile.dataset.substr(accessionStart, accessionEnd);
        }
        var dateString = !!selectedFile.date_created && moment.utc(selectedFile.date_created).format('YYYY-MM-DD');
        return (
            <dl className="key-value">
                {selectedFile.file_format ?
                    <div data-test="format">
                        <dt>Format</dt>
                        <dd>{selectedFile.file_type}</dd>
                    </div>
                : null}

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
                        <dd>{'[' + selectedFile.replicate.biological_replicate_number + ']'}</dd>
                    </div>
                : selectedFile.biological_replicates && selectedFile.biological_replicates.length ?
                    <div data-test="bioreplicate">
                        <dt>Biological replicate(s)</dt>
                        <dd>{'[' + selectedFile.biological_replicates.join(', ') + ']'}</dd>
                    </div>
                : null}

                {selectedFile.replicate ?
                    <div data-test="techreplicate">
                        <dt>Technical replicate</dt>
                        <dd>{selectedFile.replicate.technical_replicate_number}</dd>
                    </div>
                : selectedFile.biological_replicates && selectedFile.biological_replicates.length ?
                    <div data-test="techreplicate">
                        <dt>Technical replicate</dt>
                        <dd>{'-'}</dd>
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
                        <dd>{SoftwareVersionList(selectedFile.analysis_step_version.software_versions)}</dd>
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
                        <dd>
                            <a href={selectedFile.href} download={selectedFile.href.substr(selectedFile.href.lastIndexOf("/") + 1)} data-bypass="true"><i className="icon icon-download"></i>
                                &nbsp;Download
                            </a>
                        </dd>
                    </div>
                : null}
            </dl>
        );
    } else {
        return <p className="browser-error">No information available</p>;
    }
};

globals.graph_detail.register(FileDetailView, 'File');


// For each type of quality metric, make a list of attachment properties. If the quality_metric object has an attachment
// property called `attachment`, it doesn't need to be added here -- this is only for attachment properties with arbitrary names.
// Each property in the list has an associated human-readable description for display on the page.
var qcAttachmentProperties = {
    'IDRQualityMetric': [
        {'IDR_plot_true': 'IDR dispersion plot for true replicates'},
        {'IDR_plot_rep1_pr': 'IDR dispersion plot for replicate 1 pseudo-replicates'},
        {'IDR_plot_rep2_pr': 'IDR dispersion plot for replicate 2 pseudo-replicates'},
        {'IDR_plot_pool_pr': 'IDR dispersion plot for pool pseudo-replicates'},
        {'IDR_parameters_true': 'IDR run parameters for true replicates'},
        {'IDR_parameters_rep1_pr': 'IDR run parameters for replicate 1 pseudo-replicates'},
        {'IDR_parameters_rep2_pr': 'IDR run parameters for replicate 2 pseudo-replicates'},
        {'IDR_parameters_pool_pr': 'IDR run parameters for pool pseudo-replicates'}
    ],
    'ChipSeqFilterQualityMetric': [
        {'cross_correlation_plot': 'Cross-correlation plot'}
    ]
};

// List of quality metric properties to not display
var qcReservedProperties = ['uuid', 'assay_term_name', 'assay_term_id', 'attachment', 'award', 'lab', 'submitted_by', 'level', 'status', 'date_created', 'step_run', 'schema_version'];

// Display QC metrics of the selected QC sub-node in a file node.
var QcDetailsView = function(metrics) {
    if (metrics) {
        var qcPanels = []; // Each QC metric panel to display
        var id2accessionRE = /\/\w+\/(\w+)\//;
        var filesOfMetric = []; // Array of accessions of files that share this metric

        // Make an array of the accessions of files that share this quality metrics object.
        // quality_metric_of is an array of @ids because they're not embedded, and we're trying
        // to avoid embedding where not absolutely needed. So use a regex to extract the files'
        // accessions from the @ids. After generating the array, filter out empty entries.
        if (metrics.ref.quality_metric_of && metrics.ref.quality_metric_of.length) {
            filesOfMetric = metrics.ref.quality_metric_of.map(metricId => {
                // Extract the file's accession from the @id
                var match = id2accessionRE.exec(metricId);

                // Return matches that *don't* match the file whose QC node we've clicked
                if (match && (match[1] !== metrics.parent.accession)) {
                    return match[1];
                }
                return '';
            }).filter(acc => !!acc);
        }

        // Filter out QC metrics properties not to display based on the qcReservedProperties list, as well as those properties with keys
        // beginning with '@'. Sort the list of property keys as well.
        var sortedKeys = Object.keys(metrics.ref).filter(key => key[0] !== '@' && qcReservedProperties.indexOf(key) === -1).sort();

        // Get the list of attachment properties for the given qc object @type. and generate the JSX for their display panels.
        // The list of keys for attachment properties to display comes from qcAttachmentProperties. Use the @type for the attachment
        // property as a key to retrieve the list of properties appropriate for that QC type.
        var qcAttachmentPropertyList = qcAttachmentProperties[metrics.ref['@type'][0]];
        if (qcAttachmentPropertyList) {
            qcPanels = _(qcAttachmentPropertyList.map(attachmentPropertyInfo => {
                // Each object in the list has only one key (the metric attachment property name), so get it here.
                var attachmentPropertyName = Object.keys(attachmentPropertyInfo)[0];
                var attachment = metrics.ref[attachmentPropertyName];

                // Generate the JSX for the panel. Use the property name as the key to get the corresponding human-readable description for the title
                if (attachment) {
                    return <AttachmentPanel context={metrics.ref} attachment={metrics.ref[attachmentPropertyName]} title={attachmentPropertyInfo[attachmentPropertyName]} />;
                }
                return null;
            })).compact();
        }

        // Convert the QC metric object @id to a displayable string
        var qcName = metrics.ref['@id'].match(/^\/([a-z0-9-]*)\/.*$/i);
        if (qcName && qcName[1]) {
            qcName = qcName[1].replace(/-/g, ' ');
            qcName = qcName[0].toUpperCase() + qcName.substring(1);
        }

        return (
            <div>
                <div className="quality-metrics-header">
                    <div className="quality-metrics-info">
                        <h4>{qcName} of {metrics.parent.accession}</h4>
                        {filesOfMetric.length ? <h5>Shared with {filesOfMetric.join(', ')}</h5> : null}
                    </div>
                </div>
                <div className="row">
                    <div className="col-md-4 col-sm-6 col-xs-12">
                        <dl className="key-value-flex">
                            {sortedKeys.map(key => 
                                (typeof metrics.ref[key] === 'string' || typeof metrics.ref[key] === 'number') ?
                                    <div key={key}>
                                        <dt>{key}</dt>
                                        <dd>{metrics.ref[key]}</dd>
                                    </div>
                                : null
                            )}
                        </dl>
                    </div>

                    {(qcPanels && qcPanels.length) || metrics.ref.attachment ?
                        <div className="col-md-8 col-sm-12 quality-metrics-attachments">
                            <h5>Quality metric attachments</h5>
                            <div className="row">
                                {/* If the metrics object has an `attachment` property, display that first, then display the properties
                                    not named `attachment` but which have their own schema attribute, `attachment`, set to true */}
                                {metrics.ref.attachment ?
                                    <AttachmentPanel context={metrics.ref} attachment={metrics.ref.attachment} />
                                : null}
                                {qcPanels}
                            </div>
                        </div>
                    : null}
                </div>
            </div>
        );
    } else {
        return null;
    }
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
    var filterOptions = [];

    // Get the assembly and annotation of each file. Assembly is required to be included in the list
    files.forEach(file => {
        if (file.output_category !== 'raw data' && file.assembly) {
            filterOptions.push({assembly: file.assembly, annotation: file.genome_annotation});
        }
    });

    // Eliminate duplicate entries in filterOptions. Duplicates are detected by combining the
    // assembly and annotation into a long string. Use the '!' separator so that highly unlikely
    // anomalies don't pass undetected (e.g. hg19!V19 and hg1!9V19 -- again, highly unlikely).
    filterOptions = filterOptions.length ? _(filterOptions).uniq(option => option.assembly + '!' + (option.annotation ? option.annotation : '')) : [];

    // Now begin a two-stage sort, with the primary key being the assembly in a specific priority
    // order specified by the assemblyPriority array, and the secondary key being the annotation
    // in which we attempt to suss out the ordering from the way it looks, highest-numbered first.
    // First, sort by annotation and reverse the sort at the end.
    filterOptions = _(filterOptions).sortBy(option => {
        if (option.annotation) {
            // Extract any number from the annotation.
            var annotationMatch = option.annotation.match(/^[A-Z]+(\d+).*$/);
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

var fileAuditStatus = function(file) {
    var highestAuditStatus;
    if (file.audit) {
        var sortedAuditLevels = _(Object.keys(file.audit)).sortBy(level => -file.audit[level][0].level);
        var highestAuditLevel = sortedAuditLevels[0];
        highestAuditStatus = highestAuditLevel.toLowerCase();
    } else {
        highestAuditStatus = 'default';
        highestAuditLevel = 'OK';
    }
    return <AuditIcon level={highestAuditLevel} />;
};

function humanFileSize(size) {
    if (size === undefined) return undefined;
    var i = Math.floor( Math.log(size) / Math.log(1024) );
    return ( size / Math.pow(1024, i) ).toPrecision(3) * 1 + ' ' + ['B', 'kB', 'MB', 'GB', 'TB'][i];
}
