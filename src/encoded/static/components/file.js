import React from 'react';
import PropTypes from 'prop-types';
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import _ from 'underscore';
import { Panel, PanelHeading, PanelBody } from '../libs/ui/panel';
import { auditDecor } from './audit';
import { DbxrefList } from './dbxref';
import { DocumentsPanel } from './doc';
import * as globals from './globals';
import { requestFiles, requestObjects, requestSearch, RestrictedDownloadButton, ItemAccessories } from './objectutils';
import { ProjectBadge } from './image';
import { QualityMetricsPanel } from './quality_metric';
import { PickerActions, resultItemClass } from './search';
import { SortTablePanel, SortTable } from './sorttable';
import Status from './status';
import { ReplacementAccessions, FileTablePaged } from './typeutils';


dayjs.extend(utc);

/**
 * Display list of file.matching_md5sum accessions as links to their respective files. This assumes
 * no duplicates exist in the `matching_md5sum` array.
 */
const MatchingMD5Sum = ({ file }) => {
    if (file.matching_md5sum && file.matching_md5sum.length > 0) {
        const matchingMD5Accessions = file.matching_md5sum.map(fileAtId => (
            <a key={fileAtId} href={fileAtId}>{globals.atIdToAccession(fileAtId)}</a>
        ));
        return (
            <div className="supplemental-refs">
                Matching md5sum {matchingMD5Accessions.reduce((prev, curr) => [prev, ', ', curr])}
            </div>
        );
    }
    return null;
};

MatchingMD5Sum.propTypes = {
    /** File to display matching_md5sum info, if that property exists */
    file: PropTypes.object.isRequired,
};


// Columns to display in Deriving/Derived From file tables
const derivingCols = {
    accession: {
        title: 'Accession',
        display: file => <a href={file['@id']} title={`View page for file ${file.title}`}>{file.title}</a>,
    },
    dataset: {
        title: 'Dataset',
        getValue: item => (item.dataset && item.dataset.accession ? item.dataset.accession : null),
    },
    file_format: { title: 'File format' },
    output_types: { title: 'Output type' },
    title: {
        title: 'Lab',
        getValue: file => (file.lab && file.lab.title ? file.lab.title : ''),
    },
    assembly: { title: 'Mapping assembly' },
    status: {
        title: 'File status',
        display: item => <Status item={item} badgeSize="small" inline />,
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
    if (accessionList.accession && accessionList.accession.length > 0) {
        sortedAccession = accessionList.accession.sort((a, b) => (a.accession > b.accession ? 1 : (a.accession < b.accession ? -1 : 0)));
    }

    // Now sort the external_accession files
    if (accessionList.external && accessionList.external.length > 0) {
        sortedExternal = accessionList.external.sort((a, b) => (a.title > b.title ? 1 : (a.title < b.title ? -1 : 0)));
    }
    return sortedAccession.concat(sortedExternal);
}


/**
 * Display a table of files that derive from this one as a paged component. It first needs to find
 * these files with a search for qualifying files that have a `derived_from` of this file. To save
 * time and bandwidth we only request the @id of these files. The resulting list of @ids then gets
 * sent to FileTablePage to fetch the actual file objects and render them.
 */
const DerivedFiles = ({ file }) => {
    const [fileIds, setFileIds] = React.useState([]);

    React.useEffect(() => {
        requestSearch(`type=DataFile&limit=all&field=@id&status!=deleted&status!=revoked&status!=replaced&derived_from=${file['@id']}`).then((result) => {
            // The server has returned file search results. Generate an array of file @ids.
            if (Object.keys(result).length > 0 && result['@graph'] && result['@graph'].length > 0) {
                // Sort the files. We still get an array of search results from the server, just
                // sorted by accessioned files, followed by external_accession files.
                const sortedFiles = sortProcessedPagedFiles(result['@graph']);
                setFileIds(sortedFiles.map(sortedFile => sortedFile['@id']));
            }
        });
    }, [file]);

    return <FileTablePaged fileIds={fileIds} title={`Files deriving from ${file.title}`} />;
};

DerivedFiles.propTypes = {
    /** Query string fragment for the search that ultimately generates the table of files */
    file: PropTypes.object.isRequired,
};


// Display a table of files the current file derives from.
/* eslint-disable react/prefer-stateless-function */
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
/* eslint-enable react/prefer-stateless-function */

DerivedFromFiles.propTypes = {
    file: PropTypes.object.isRequired, // File being analyzed
    derivedFromFiles: PropTypes.array.isRequired, // Array of derived-from files
};


// Display a file download button.
class FileDownloadButton extends React.Component {
    constructor() {
        super();
        this.onMouseEnter = this.onMouseEnter.bind(this);
        this.onMouseLeave = this.onMouseLeave.bind(this);
    }

    onMouseEnter() {
        if (this.props.hoverDL) {
            this.props.hoverDL(true);
        }
    }

    onMouseLeave() {
        if (this.props.hoverDL) {
            this.props.hoverDL(false);
        }
    }

    render() {
        const { file, buttonEnabled } = this.props;

        if (file) {
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
                    >
                        Download {file.title}
                    </a>
                    {!buttonEnabled ?
                        <div className="tooltip-button-overlay" onMouseEnter={file.restricted ? this.onMouseEnter : null} onMouseLeave={file.restricted ? this.onMouseLeave : null} />
                    : null}
                </div>
            );
        }
        return null;
    }
}

FileDownloadButton.propTypes = {
    file: PropTypes.object, // File we're possibly downloading by clicking this button
    hoverDL: PropTypes.func, // Function to call when hovering starts/stops over button
    buttonEnabled: PropTypes.bool, // `true` if button is enabled
};

FileDownloadButton.defaultProps = {
    file: null,
    hoverDL: null,
    buttonEnabled: false,
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
        const derivedFromFileIds = file.derived_from && file.derived_from.length > 0 ? file.derived_from : [];
        if (derivedFromFileIds.length > 0) {
            requestFiles(derivedFromFileIds).then((derivedFromFiles) => {
                this.setState({ derivedFromFiles });
            });
        }

        // Retrieve an array of file format specification document @ids. Once the array arrives,
        // set the fileFormatSpecs React state that causes the list to render.
        const fileFormatSpecs = file.file_format_specifications && file.file_format_specifications.length > 0 ? file.file_format_specifications : [];
        if (fileFormatSpecs.length > 0) {
            requestObjects(fileFormatSpecs, '/search/?type=Document&limit=all&status!=deleted&status!=revoked&status!=replaced').then((docs) => {
                this.setState({ fileFormatSpecs: docs });
            });
        }
    }

    render() {
        const { context, auditDetail, auditIndicators } = this.props;
        const itemClass = globals.itemClass(context, 'view-item');
        const aliasList = (context.aliases && context.aliases.length > 0) ? context.aliases.join(', ') : '';
        const datasetAccession = (context.dataset) ? globals.atIdToAccession(context.dataset) : globals.atIdToAccession(context.fileset);
        const loggedIn = !!(this.context.session && this.context.session['auth.userid']);
        const adminUser = !!this.context.session_properties.admin;

        const qualityMetrics = (context.quality_metrics && context.quality_metrics.length > 0) ? context.quality_metrics.join(', ') : '';

        return (
            <div className={itemClass}>
                <header>
                    <h2>File summary for {context.title} (<span className="sentence-case">{context.file_format}</span>)</h2>
                    <ReplacementAccessions context={context} />
                    <MatchingMD5Sum file={context} />
                    {context.restricted ?
                        <div className="replacement-accessions">
                            <h4>Restricted file</h4>
                        </div>
                    : null}
                    <ItemAccessories item={context} audit={{ auditIndicators, auditId: 'file-audit', except: context['@id'] }} />
                </header>
                {auditDetail(context.audit, 'file-audit', { session: this.context.session, sessionProperties: this.context.session_properties, except: context['@id'] })}
                <Panel>
                    <PanelBody addClasses="panel__split">
                        <div className="panel__split-element">
                            <div className="panel__split-heading panel__split-heading--file">
                                <h4>Summary</h4>
                            </div>
                            <dl className="key-value">
                                <div data-test="status">
                                    <dt>Status</dt>
                                    <dd><Status item={context} inline /></dd>
                                </div>

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
                                    <dd>{context.output_types}</dd>
                                </div>

                                {context.restriction_enzymes ?
                                    <div data-test="restrictionEnzymes">
                                        <dt>Restriction enzymes</dt>
                                        <dd>{context.restriction_enzymes.join(', ')}</dd>
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

                                {context.s3_uri ?
                                    <div className="file-download-section">
                                        <RestrictedDownloadButton file={context} adminUser={adminUser} downloadComponent={<FileDownloadButton />} />
                                    </div>
                                : null}
                            </dl>
                        </div>

                        <div className="panel__split-element">
                            <div className="panel__split-heading panel__split-heading--file">
                                <h4>Attribution</h4>
                                {context.award ?
                                <ProjectBadge award={context.award} addClasses="badge-heading" />
                                : null}
                            </div>
                            <dl className="key-value">
                                {context.lab ?
                                <div data-test="lab">
                                    <dt>Lab</dt>
                                    <dd>{context.lab.title}</dd>
                                </div>
                                : null}
                                {context.award ?
                                    <div data-test="project">
                                        <dt>Project</dt>
                                        <dd>{context.award.project}</dd>
                                    </div>
                                : null}
                                {context.assembly ?
                                    <div data-test="assembly">
                                        <dt>Assembly</dt>
                                        <dd>{context.assembly}</dd>
                                    </div>
                                : null}
                                {context.genome_annotation ?
                                    <div data-test="genomeannotation">
                                        <dt>Genome annotation</dt>
                                        <dd>{context.genome_annotation}</dd>
                                    </div>
                                : null}
                                {context.date_created ?
                                    <div data-test="datecreated">
                                        <dt>Date added</dt>
                                        <dd>{dayjs.utc(context.date_created).format('YYYY-MM-DD')}</dd>
                                    </div>
                                : null}

                                {context.dbxrefs ?
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

                                {context.submitter_comment ?
                                    <div data-test="submittercomment">
                                        <dt>Submitter comment</dt>
                                        <dd>{context.submitter_comment}</dd>
                                    </div>
                                : null}
                            </dl>
                        </div>
                    </PanelBody>
                </Panel>

                {context.file_format === 'fastq' ?
                    <SequenceFileInfo file={context} />
                : null}

                {this.state.derivedFromFiles && this.state.derivedFromFiles.length > 0 ? <DerivedFromFiles file={context} derivedFromFiles={this.state.derivedFromFiles} /> : null}

                <DerivedFiles file={context} />

                {this.state.fileFormatSpecs.length > 0 ?
                    <DocumentsPanel title="File format specifications" documentSpecs={[{ documents: this.state.fileFormatSpecs }]} />
                : null}

                {qualityMetrics.length > 0 ?
                    <QualityMetricsPanel qcMetrics={qualityMetrics} file={context} />
                : null}
            </div>
        );
    }
}

FileComponent.propTypes = {
    context: PropTypes.object.isRequired, // File object being displayed
    auditIndicators: PropTypes.func.isRequired, // Audit indicator rendering function from auditDecor
    auditDetail: PropTypes.func.isRequired, // Audit detail rendering function from auditDecor
};

FileComponent.contextTypes = {
    session: PropTypes.object, // Login information
    session_properties: PropTypes.object,
};

const File = auditDecor(FileComponent);

globals.contentViews.register(File, 'File');


// Display the sequence file summary panel for fastq files.
/* eslint-disable react/prefer-stateless-function */
class SequenceFileInfo extends React.Component {
    render() {
        const { file } = this.props;
        const pairedWithAccession = file.paired_with ? globals.atIdToAccession(file.paired_with) : '';

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
                                <dd><a href={file.platform['@id']} title="View page for this platform">{file.platform.term_name}</a></dd>
                            </div>
                        : null}

                        {file.flowcell_details && file.flowcell_details.length > 0 ?
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

                        {file.fastq_signature && file.fastq_signature.length > 0 ?
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

                        {file.index_of ?
                            <div data-test="outputtype">
                                <dt>Index of</dt>
                                <dd>
                                    {file.index_of.reduce((fUrls, href) => {
                                        const fileId = href.replace(/\/files\/|\//g, '');
                                        const fUrl = <a key={fileId} href={href} title={fileId}>{fileId}</a>;
                                        return !fUrls ? [fUrl] : [fUrl, ', ', fUrls];
                                    }, '')}
                                </dd>
                            </div>
                        : null}

                        {file.controlled_by && file.controlled_by.length > 0 ?
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
/* eslint-enable react/prefer-stateless-function */


SequenceFileInfo.propTypes = {
    file: PropTypes.object.isRequired, // File being displayed
};


/* eslint-disable react/prefer-stateless-function */
class ListingComponent extends React.Component {
    render() {
        const result = this.props.context;

        return (
            <li className={resultItemClass(result)}>
                <div className="result-item">
                    <div className="result-item__data">
                        <a href={result['@id']} className="result-item__link">
                            {`${result.file_format}${result.file_format_type ? ` (${result.file_format_type})` : ''}`}
                        </a>
                        <div className="result-item__data-row">
                            <div><strong>Lab: </strong>{result.lab.title}</div>
                            {result.award.project ? <div><strong>Project: </strong>{result.award.project}</div> : null}
                        </div>
                    </div>
                    <PickerActions context={result} />
                </div>
                {this.props.auditDetail(result.audit, result['@id'], { session: this.context.session, sessionProperties: this.context.session_properties })}
            </li>
        );
    }
}
/* eslint-enable react/prefer-stateless-function */

ListingComponent.propTypes = {
    context: PropTypes.object.isRequired, // File object being rendered
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

ListingComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
    session_properties: PropTypes.object,
};

const Listing = auditDecor(ListingComponent);

globals.listingViews.register(Listing, 'File');
