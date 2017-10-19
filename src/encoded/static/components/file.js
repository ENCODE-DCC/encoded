import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment';
import _ from 'underscore';
import Pager from '../libs/bootstrap/pager';
import { Panel, PanelHeading, PanelBody } from '../libs/bootstrap/panel';
import { auditDecor } from './audit';
import { DbxrefList } from './dbxref';
import { DocumentsPanel } from './doc';
import * as globals from './globals';
import { requestFiles, requestObjects, requestSearch, RestrictedDownloadButton } from './objectutils';
import { ProjectBadge } from './image';
import { QualityMetricsPanel } from './quality_metric';
import { SortTablePanel, SortTable } from './sorttable';
import StatusLabel from './statuslabel';


// Columns to display in Deriving/Derived From file tables
const derivingCols = {
    accession: {
        title: 'Accession',
        display: file => <a href={file['@id']} title={`View page for file ${file.title}`}>{file.title}</a>,
    },
    dataset: {
        title: 'Dataset',
        display: (file) => {
            const datasetAccession = globals.atIdToAccession(file.dataset);
            return <a href={file.dataset} title={`View page for dataset ${datasetAccession}`}>{datasetAccession}</a>;
        },
    },
    file_format: { title: 'File format' },
    output_type: { title: 'Output type' },
    title: {
        title: 'Lab',
        getValue: file => (file.lab && file.lab.title ? file.lab.title : ''),
    },
    assembly: { title: 'Mapping assembly' },
    status: {
        title: 'File status',
        display: item => <div className="characterization-meta-data"><StatusLabel status={item.status} fileStatus /></div>,
    },
};


// Sort files processed from <PagedFileTable>. The files come in an array of objects with the
// format:
// [{
//     @id: @id of the file
//     accession: accession of the file, if any
//     title: title of the file, if any (either this or accession must have a value)
// }, {next file}, {...}]
//
// This function returns the same array, but sorted by accession, and then by title (all files with
// accessions appear first, followed by all files with titles, each sorted independently).
function sortProcessedPagedFiles(files) {
    // Split the list into two groups for basic sorting first by those with accessions,
    // then those with external_accessions.
    const accessionList = _(files).groupBy(file => (file.accession ? 'accession' : 'external'));

    // Start by sorting the accessioned files.
    let sortedAccession = [];
    let sortedExternal = [];
    if (accessionList.accession && accessionList.accession.length) {
        sortedAccession = accessionList.accession.sort((a, b) => (a.accession > b.accession ? 1 : (a.accession < b.accession ? -1 : 0)));
    }

    // Now sort the external_accession files
    if (accessionList.external && accessionList.external.length) {
        sortedExternal = accessionList.external.sort((a, b) => (a.title > b.title ? 1 : (a.title < b.title ? -1 : 0)));
    }
    return sortedAccession.concat(sortedExternal);
}


// Display a table of files that derive from this one as a paged component. It works by first
// doing a GET request an array of minimal file objects with barely enough information to know what
// files satisfy the search criteria for files that derive from the file passed in the `file` prop.
// We then sort his list of files, and that becomes the master list of all files deriving from this
// one. Finally, we do the first GET request with a search for the complete file objects, but only
// enough to fit the current page (initially page 0, or 1 on the display) based on the
// `PagedFileTableMax` constant below.
//
// When the user clicks on the Pager component, we change our current page (stored in the
// `currentPage` state variable) and do another GET request for the complete file objects for that
// page.
const PagedFileTableMax = 50; // Maximnum number of files per page
const PagedFileCacheMax = 10; // Maximum number of pages to cache

class DerivedFiles extends React.Component {
    constructor() {
        super();
        this.state = {
            currentPage: 0, // Current page of a multi-page table
            pageFiles: [], // Array of file objects displayed for the current page
            totalPages: 0, // Total number of pages; never gets updated after initialized
        };
        this.currentPageFiles = this.currentPageFiles.bind(this);
        this.updateCurrentPage = this.updateCurrentPage.bind(this);
    }

    componentDidMount() {
        this.allFileIds = [];
        this.pageCache = {};
        const { file } = this.props;

        // Search for all files that derive from the given one, but because we could get tens of
        // thousands of results, we do a search only on the @ids of the matching results to vastly
        // reduce the JSON size. We can then get take just a page of those to retrieve their
        // details for display in the table.
        requestSearch(`type=File&limit=all&field=@id&status!=deleted&status!=revoked&status!=replaced&field=accession&field=title&field=accession&derived_from=${file['@id']}`).then((result) => {
            // The server has returned search results. See if we got matching files to display
            // in the table.
            if (Object.keys(result).length && result['@graph'] && result['@graph'].length) {
                // Sort the files. We still get an array of search results from the server, just
                // sorted by accessioned files, followed by external_accession files.
                const sortedFiles = sortProcessedPagedFiles(result['@graph']);

                // Make a list of file @ids of all files for the current page and retrieve them
                // with a GET request. Also, now that we know how many total results we have, save
                // the total number of pages of results we'll show.
                this.allFileIds = sortedFiles.map(sortedFile => sortedFile['@id']);
                this.setState({ totalPages: parseInt(this.allFileIds.length / PagedFileTableMax, 10) + (this.allFileIds.length % PagedFileTableMax ? 1 : 0) });
                return requestFiles(this.currentPageFiles());
            }

            // No results. Just resolve with null.
            return Promise.resolve(null);
        }).then((files) => {
            this.setState({ pageFiles: files || [] });
        });
    }

    componentDidUpdate(prevProps, prevState) {
        if (prevState.currentPage !== this.state.currentPage) {
            // The currently displayed page of files has changed. First keep a reference to the
            // current page of files to keep it from getting GC'd, if it's not already referenced.
            if (!this.pageCache[prevState.currentPage]) {
                this.pageCache[prevState.currentPage] = prevState.pageFiles;

                // To save memory, see if we can lose a reference to a page so that it gets GC'd.
                const cachedPageNos = Object.keys(this.pageCache);
                if (cachedPageNos.length > PagedFileCacheMax) {
                    // Our cache with an arbitrarily determined size has filled. Find the entry
                    // with a page farthest from the current and kick it out.
                    let maxDiff = 0;
                    let maxDiffKey;
                    cachedPageNos.forEach((pageNo) => {
                        const diff = Math.abs(this.state.currentPage - parseInt(pageNo, 10));
                        if (diff > maxDiff) {
                            maxDiff = diff;
                            maxDiffKey = parseInt(pageNo, 10);
                        }
                    });
                    delete this.pageCache[maxDiffKey];
                }
            }

            // Get the requested page of files, either from the cache if it's there, or by
            // requesting them from the serer.
            if (this.pageCache[this.state.currentPage]) {
                // Page is in the cache; just get the cached reference.
                this.setState({ pageFiles: this.pageCache[this.state.currentPage] });
            } else {
                // Send a request for the file objects for that page, and update the state with
                // those files once the request completes so that the table redraws with the new
                // set of files.
                requestFiles(this.currentPageFiles()).then((files) => {
                    this.setState({ pageFiles: files || [] });
                });
            }
        }
    }

    // Get an array of file IDs for the current page. Requires this.allFileIds to hold all the file
    // @id of files that derive from the one being displayed, and this.state.currentPage to hold
    // the currently displayed page of files in the table.
    currentPageFiles() {
        if (this.allFileIds && this.allFileIds.length) {
            const start = this.state.currentPage * PagedFileTableMax;
            return this.allFileIds.slice(start, start + PagedFileTableMax);
        }
        return [];
    }

    updateCurrentPage(newCurrent) {
        this.setState({ currentPage: newCurrent });
    }

    render() {
        const { file } = this.props;

        if (this.state.pageFiles.length) {
            // If we have more than one page of files to display, render a pager component in the
            // footer.
            const pager = this.state.totalPages > 1 ? <Pager total={this.state.totalPages} current={this.state.currentPage} updateCurrentPage={this.updateCurrentPage} /> : null;

            return (
                <SortTablePanel header={<h4>{`Files deriving from ${file.title}`}</h4>}>
                    <SortTable
                        list={this.state.pageFiles}
                        columns={derivingCols}
                        sortColumn="accession"
                        footer={pager}
                    />
                </SortTablePanel>
            );
        }
        return null;
    }
}

DerivedFiles.propTypes = {
    file: React.PropTypes.object.isRequired, // Query string fragment for the search that ultimately generates the table of files
};


// Display a table of files the current file derives from.
class DerivedFromFiles extends React.Component {
    render() {
        const { file, derivedFromFiles } = this.props;

        return (
            <SortTablePanel header={<h4>{`Files ${file.title} derives from`}</h4>}>
                <SortTable
                    list={derivedFromFiles}
                    columns={derivingCols}
                    sortColumn="accession"
                />
            </SortTablePanel>
        );
    }
}

DerivedFromFiles.propTypes = {
    file: PropTypes.object.isRequired, // File being analyzed
    derivedFromFiles: PropTypes.array.isRequired, // Array of derived-from files
};


// Display a file download button.
class FileDownloadButton extends React.Component {
    onMouseEnter() {
        this.props.hoverDL(true);
    }

    onMouseLeave() {
        this.props.hoverDL(false);
    }

    render() {
        const { file, buttonEnabled } = this.props;

        return (
            <div className="tooltip-button-wrapper">
                <a
                    className="btn btn-info"
                    href={file.href}
                    download={file.href.substr(file.href.lastIndexOf('/') + 1)}
                    data-bypass="true"
                    disabled={!buttonEnabled}
                    onMouseEnter={file.restricted ? this.onMouseEnter : null}
                    onMouseLeave={file.restricted ? this.onMouseLeave : null}
                >Download {file.title}</a>
                {!buttonEnabled ?
                    <div className="tooltip-button-overlay" onMouseEnter={file.restricted ? this.onMouseEnter : null} onMouseLeave={file.restricted ? this.onMouseLeave : null} />
                : null}
            </div>
        );
    }
}

FileDownloadButton.propTypes = {
    file: PropTypes.object, // File we're possibly downloading by clicking this button
    hoverDL: PropTypes.func, // Function to call when hovering starts/stops over button
    buttonEnabled: PropTypes.bool, // `true` if button is enabled
};


class FileComponent extends React.Component {
    constructor() {
        super();
        this.state = {
            derivedFromFiles: [], // List of derived-from files
            fileFormatSpecs: [], // List of file_format_specifications
        };
    }

    componentDidMount() {
        // Now that this page is mounted, request the list of derived_from files and file
        // documents.
        this.requestFileDependencies();

        // In case the logged-in state changes, we have to keep track of the old logged-in state.
        this.loggedIn = !!(this.context.session && this.context.session['auth.userid']);
    }

    componentWillReceiveProps() {
        // If the logged-in state has changed since the last time we rendered, request files again
        // in case logging in changes the list of dependent files.
        const currLoggedIn = !!(this.context.session && this.context.session['auth.userid']);
        if (this.loggedIn !== currLoggedIn) {
            this.requestFileDependencies();
            this.loggedIn = currLoggedIn;
        }
    }

    requestFileDependencies() {
        // Perform GET requests of files that derive from this one, as well as file format
        // specification documents. This avoids embedding these arrays of objects in the file
        // object.
        const file = this.props.context;

        // Retrieve an array of file @ids that this file derives from. Once this array arrives.
        // it sets the derivedFromFiles React state that causes the list to render.
        const derivedFromFileIds = file.derived_from && file.derived_from.length ? file.derived_from : [];
        if (derivedFromFileIds.length) {
            requestFiles(derivedFromFileIds).then((derivedFromFiles) => {
                this.setState({ derivedFromFiles });
            });
        }

        // Retrieve an array of file format specification document @ids. Once the array arrives,
        // set the fileFormatSpecs React state that causes the list to render.
        const fileFormatSpecs = file.file_format_specifications && file.file_format_specifications.length ? file.file_format_specifications : [];
        if (fileFormatSpecs.length) {
            requestObjects(fileFormatSpecs, '/search/?type=Document&limit=all&status!=deleted&status!=revoked&status!=replaced').then((docs) => {
                this.setState({ fileFormatSpecs: docs });
            });
        }
    }

    render() {
        const { context } = this.props;
        const itemClass = globals.itemClass(context, 'view-item');
        const altacc = (context.alternate_accessions && context.alternate_accessions.length) ? context.alternate_accessions.join(', ') : null;
        const aliasList = (context.aliases && context.aliases.length) ? context.aliases.join(', ') : '';
        const datasetAccession = globals.atIdToAccession(context.dataset);
        const adminUser = !!this.context.session_properties.admin;

        // Make array of superceded_by accessions.
        let supersededBys = [];
        if (context.superseded_by && context.superseded_by.length) {
            supersededBys = context.superseded_by.map(supersededBy => globals.atIdToAccession(supersededBy));
        }

        // Make array of supersedes accessions
        let supersedes = [];
        if (context.supersedes && context.supersedes.length) {
            supersedes = context.supersedes.map(supersede => globals.atIdToAccession(supersede));
        }

        // Collect up relevant pipelines.
        let pipelines = [];
        if (context.analysis_step_version && context.analysis_step_version.analysis_step.pipelines && context.analysis_step_version.analysis_step.pipelines.length) {
            pipelines = context.analysis_step_version.analysis_step.pipelines;
        }

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <h2>File summary for {context.title} (<span className="sentence-case">{context.file_format}</span>)</h2>
                        {altacc ? <h4 className="repl-acc">Replaces {altacc}</h4> : null}
                        {supersededBys.length ? <h4 className="superseded-acc">Superseded by {supersededBys.join(', ')}</h4> : null}
                        {supersedes.length ? <h4 className="superseded-acc">Supersedes {supersedes.join(', ')}</h4> : null}
                        <div className="status-line">
                            {context.status ?
                                <div className="characterization-status-labels">
                                    <StatusLabel title="Status" status={context.status} fileStatus />
                                </div>
                            : null}
                            {this.props.auditIndicators(context.audit, 'file-audit', { session: this.context.session })}
                        </div>
                        {this.props.auditDetail(context.audit, 'file-audit', { session: this.context.session, except: context['@id'] })}
                    </div>
                </header>
                <Panel addClasses="data-display">
                    <div className="split-panel">
                        <div className="split-panel__part split-panel__part--p50">
                            <div className="split-panel__heading"><h4>Summary</h4></div>
                            <div className="split-panel__content">
                                <dl className="key-value">
                                    <div data-test="term-name">
                                        <dt>Dataset</dt>
                                        <dd><a href={context.dataset} title={`View page for dataset ${datasetAccession}`}>{datasetAccession}</a></dd>
                                    </div>

                                    <div data-test="outputtype">
                                        <dt>File format</dt>
                                        <dd>{`${context.file_format}${context.file_format_type ? ` ${context.file_format_type}` : ''}`}</dd>
                                    </div>

                                    <div data-test="outputtype">
                                        <dt>Output type</dt>
                                        <dd>{context.output_type}</dd>
                                    </div>

                                    <div data-test="bioreplicate">
                                        <dt>Biological replicate(s)</dt>
                                        <dd>{`[${context.biological_replicates && context.biological_replicates.length ? context.biological_replicates.join(', ') : '-'}]`}</dd>
                                    </div>

                                    <div data-test="techreplicate">
                                        <dt>Technical replicate(s)</dt>
                                        <dd>{`[${context.technical_replicates && context.technical_replicates.length ? context.technical_replicates.join(', ') : '-'}]`}</dd>
                                    </div>

                                    {pipelines.length ?
                                        <div data-test="pipelines">
                                            <dt>Pipelines</dt>
                                            <dd>
                                                {pipelines.map((pipeline, i) =>
                                                    <span key={pipeline['@id']}>
                                                        {i > 0 ? <span>{','}<br /></span> : null}
                                                        <a href={pipeline['@id']} title="View page for this pipeline">{pipeline.title}</a>
                                                    </span>,
                                                )}
                                            </dd>
                                        </div>
                                    : null}

                                    <div data-test="md5sum">
                                        <dt>MD5sum</dt>
                                        <dd>{context.md5sum}</dd>
                                    </div>

                                    {context.content_md5sum ?
                                        <div data-test="contentmd5sum">
                                            <dt>Content MD5sum</dt>
                                            <dd>{context.content_md5sum}</dd>
                                        </div>
                                    : null}

                                    {context.read_count ?
                                        <div data-test="readcount">
                                            <dt>Read count</dt>
                                            <dd>{context.read_count}</dd>
                                        </div>
                                    : null}

                                    {context.read_length ?
                                        <div data-test="readlength">
                                            <dt>Read length</dt>
                                            <dd>{context.read_length}</dd>
                                        </div>
                                    : null}

                                    {context.file_size ?
                                        <div data-test="filesize">
                                            <dt>File size</dt>
                                            <dd>{globals.humanFileSize(context.file_size)}</dd>
                                        </div>
                                    : null}

                                    {context.mapped_read_length ?
                                        <div data-test="mappreadlength">
                                            <dt>Mapped read length</dt>
                                            <dd>{context.mapped_read_length}</dd>
                                        </div>
                                    : null}

                                    <div className="file-download-section">
                                        <RestrictedDownloadButton file={context} adminUser={adminUser} downloadComponent={<FileDownloadButton />} />
                                    </div>
                                </dl>
                            </div>
                        </div>

                        <div className="split-panel__part split-panel__part--p50">
                            <div className="split-panel__heading">
                                <h4>Attribution</h4>
                                <ProjectBadge award={context.award} addClasses="badge-heading" />
                            </div>
                            <div className="split-panel__content">
                                <dl className="key-value">
                                    <div data-test="lab">
                                        <dt>Lab</dt>
                                        <dd>{context.lab.title}</dd>
                                    </div>

                                    {context.award.pi && context.award.pi.lab ?
                                        <div data-test="awardpi">
                                            <dt>Award PI</dt>
                                            <dd>{context.award.pi.lab.title}</dd>
                                        </div>
                                    : null}

                                    <div data-test="submittedby">
                                        <dt>Submitted by</dt>
                                        <dd>{context.submitted_by.title}</dd>
                                    </div>

                                    {context.award.project ?
                                        <div data-test="project">
                                            <dt>Project</dt>
                                            <dd>{context.award.project}</dd>
                                        </div>
                                    : null}

                                    {context.date_created ?
                                        <div data-test="datecreated">
                                            <dt>Date added</dt>
                                            <dd>{moment.utc(context.date_created).format('YYYY-MM-DD')}</dd>
                                        </div>
                                    : null}

                                    {context.dbxrefs && context.dbxrefs.length ?
                                        <div data-test="externalresources">
                                            <dt>External resources</dt>
                                            <dd><DbxrefList context={context} dbxrefs={context.dbxrefs} /></dd>
                                        </div>
                                    : null}

                                    {context.content_error_detail ?
                                        <div data-test="contenterrordetail">
                                            <dt>Content error detail</dt>
                                            <dd>{context.content_error_detail}</dd>
                                        </div>
                                    : null}

                                    {aliasList ?
                                        <div data-test="aliases">
                                            <dt>Aliases</dt>
                                            <dd className="sequence">{aliasList}</dd>
                                        </div>
                                    : null}

                                    {context.submitted_file_name ?
                                        <div data-test="submittedfilename">
                                            <dt>Original file name</dt>
                                            <dd className="sequence">{context.submitted_file_name}</dd>
                                        </div>
                                    : null}
                                </dl>
                            </div>
                        </div>
                    </div>
                </Panel>

                {context.file_format === 'fastq' ?
                    <SequenceFileInfo file={context} />
                : null}

                {this.state.derivedFromFiles && this.state.derivedFromFiles.length ? <DerivedFromFiles file={context} derivedFromFiles={this.state.derivedFromFiles} /> : null}

                <DerivedFiles file={context} />

                {this.state.fileFormatSpecs.length ?
                    <DocumentsPanel title="File format specifications" documentSpecs={[{ documents: this.state.fileFormatSpecs }]} />
                : null}

                {context.quality_metrics && context.quality_metrics.length ?
                    <QualityMetricsPanel qcMetrics={context.quality_metrics} file={context} />
                : null}
            </div>
        );
    }
}

FileComponent.propTypes = {
    context: PropTypes.object, // File object being displayed
    auditIndicators: PropTypes.func, // Audit indicator rendering function from auditDecor
    auditDetail: PropTypes.func, // Audit detail rendering function from auditDecor
};

FileComponent.contextTypes = {
    session: PropTypes.object, // Login information
    session_properties: PropTypes.object,
};

const File = auditDecor(FileComponent);

globals.contentViews.register(File, 'File');


// Display the sequence file summary panel for fastq files.
class SequenceFileInfo extends React.Component {
    render() {
        const { file } = this.props;
        const pairedWithAccession = file.paired_with ? globals.atIdToAccession(file.paired_with) : '';
        const platformAccession = file.platform ? decodeURIComponent(globals.atIdToAccession(file.platform)) : '';

        return (
            <Panel>
                <PanelHeading>
                    <h4>Sequencing file information</h4>
                </PanelHeading>

                <PanelBody>
                    <dl className="key-value">
                        {file.platform ?
                            <div data-test="platform">
                                <dt>Platform</dt>
                                <dd><a href={file.platform} title="View page for this platform">{platformAccession}</a></dd>
                            </div>
                        : null}

                        {file.flowcell_details && file.flowcell_details.length ?
                            <div data-test="flowcelldetails">
                                <dt>Flowcell</dt>
                                <dd>
                                    {file.flowcell_details.map((detail, i) => {
                                        const items = [
                                            detail.machine ? detail.machine : '',
                                            detail.flowcell ? detail.flowcell : '',
                                            detail.lane ? detail.lane : '',
                                            detail.barcode ? detail.barcode : '',
                                        ];
                                        return <span className="line-item" key={i}>{items.join(':')}</span>;
                                    })}
                                </dd>
                            </div>
                        : null}

                        {file.fastq_signature && file.fastq_signature.length ?
                            <div data-test="fastqsignature">
                                <dt>Fastq flowcell signature</dt>
                                <dd>{file.fastq_signature.join(', ')}</dd>
                            </div>
                        : null}

                        {file.run_type ?
                            <div data-test="runtype">
                                <dt>Run type</dt>
                                <dd>
                                    {file.run_type}
                                    {file.read_length ? <span>{` ${file.read_length + file.read_length_units}`}</span> : null}
                                </dd>
                            </div>
                        : null}

                        {file.paired_end ?
                            <div data-test="pairedend">
                                <dt>Read</dt>
                                <dd>
                                    {file.paired_end}
                                    {file.paired_with ? <span> paired with <a href={file.paired_with} title={`View page for file ${pairedWithAccession}`}>{pairedWithAccession}</a></span> : null}
                                </dd>
                            </div>
                        : null}

                        {file.controlled_by && file.controlled_by.length ?
                            <div data-test="controlledby">
                                <dt>Controlled by</dt>
                                <dd>
                                    {file.controlled_by.map((controlFile, i) => {
                                        const controlFileAccession = globals.atIdToAccession(controlFile);
                                        return (
                                            <span key={controlFile}>
                                                {i > 0 ? <span>, </span> : null}
                                                <a href={controlFile} title={`View page for file ${controlFileAccession}`}>{controlFileAccession}</a>
                                            </span>
                                        );
                                    })}
                                </dd>
                            </div>
                        : null}
                    </dl>
                </PanelBody>
            </Panel>
        );
    }
}


SequenceFileInfo.propTypes = {
    file: PropTypes.object.isRequired, // File being displayed
};


class Listing extends React.Component {
    render() {
        const result = this.props.context;

        return (
            <li>
                <div className="clearfix">
                    <div className="pull-right search-meta">
                        <p className="type meta-title">File</p>
                        <p className="type">{` ${result.title}`}</p>
                        <p className="type meta-status">{` ${result.status}`}</p>
                    </div>
                    <div className="accession"><a href={result['@id']}>{`${result.file_format}${result.file_format_type ? ` (${result.file_format_type})` : ''}`}</a></div>
                    <div className="data-row">
                        <div><strong>Lab: </strong>{result.lab.title}</div>
                        {result.award.project ? <div><strong>Project: </strong>{result.award.project}</div> : null}
                    </div>
                </div>
            </li>
        );
    }
}

Listing.propTypes = {
    context: PropTypes.object, // File object being rendered
};

globals.listingViews.register(Listing, 'File');
