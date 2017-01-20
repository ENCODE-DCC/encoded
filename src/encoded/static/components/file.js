import React from 'react';
import moment from 'moment';
import { Panel, PanelHeading, PanelBody } from '../libs/bootstrap/panel';
import globals from './globals';
import { DbxrefList } from './dbxref';
import { FetchedItems } from './fetched';
import { requestFiles } from './objectutils';
import { ProjectBadge } from './image';
import { SortTablePanel, SortTable } from './sorttable';
import { StatusLabel } from './statuslabel';


const audit = AuditComponent => class extends React.Component {
    constructor() {
        super();
        this.state = { data: null };
    }

    render() {
        return <AuditComponent {...this.props} data={this.state.data} />;
    }
};


// Columns to display in Deriving/Derived From file tables
const derivingCols = {
    accession: {
        title: 'Accession',
        display: file => <a href={file['@id']} title={`View page for file ${file.accession}`}>{file.accession}</a>,
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
        display: item => <div className="characterization-meta-data"><StatusLabel status={item.status} /></div>,
    },
};


// Display a table of files deriving from the one being displayed. This component gets called once
// a GET request's data returns.
class DerivedFiles extends React.Component {
    render() {
        const { items, context } = this.props;

        if (items.length) {
            return (
                <SortTablePanel header={<h4>{`Files deriving from ${context.accession}`}</h4>}>
                    <SortTable
                        list={items}
                        columns={derivingCols}
                        sortColumn="accession"
                    />
                </SortTablePanel>
            );
        }
        return null;
    }
}

DerivedFiles.propTypes = {
    items: React.PropTypes.array, // Array of files from the GET request
    context: React.PropTypes.object, // File that requested this list
};


// Display a table of files the current file derives from.
class DerivedFromFiles extends React.Component {
    render() {
        const { file, derivedFromFiles } = this.props;

        return (
            <SortTablePanel header={<h4>{`Files ${file.accession} derives from`}</h4>}>
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
    file: React.PropTypes.object.isRequired, // File being analyzed
    derivedFromFiles: React.PropTypes.array.isRequired, // Array of derived-from files
};


class FileComponent extends React.Component {
    constructor() {
        super();
        this.state = {
            derivedFromFiles: [], // List of derived-from files
        };
    }

    componentDidMount() {
        const { context } = this.props;
        const derivedFromFileIds = context.derived_from && context.derived_from.length ? context.derived_from : [];
        if (derivedFromFileIds.length) {
            requestFiles(derivedFromFileIds).then((derivedFromFiles) => {
                this.setState({ derivedFromFiles: derivedFromFiles });
            });
        }
    }

    render() {
        const { context } = this.props;
        const itemClass = globals.itemClass(context, 'view-item');
        const altacc = (context.alternate_accessions && context.alternate_accessions.length) ? context.alternate_accessions.join(', ') : null;
        const aliasList = (context.aliases && context.aliases.length) ? context.aliases.join(', ') : '';
        const datasetAccession = globals.atIdToAccession(context.dataset);

        // Make array of superceded_by accessions.
        let supersededBys = [];
        if (context.superseded_by && context.superseded_by.length) {
            supersededBys = context.superseded_by.map(supersededBy => globals.atIdToAccession(supersededBy));
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
                        <h2>{context.accession}{' / '}<span className="sentence-case">{`${context.file_format}${context.file_format_type ? ` (${context.file_format_type})` : ''}`}</span></h2>
                        {altacc ? <h4 className="repl-acc">Replaces {altacc}</h4> : null}
                        {supersededBys.length ? <h4 className="superseded-acc">Superseded by {supersededBys.join(', ')}</h4> : null}
                        <div className="status-line">
                            {context.status ?
                                <div className="characterization-status-labels">
                                    <StatusLabel title="Status" status={context.status} />
                                </div>
                            : null}
                        </div>
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
                                            <dt>Mapped read length</dt>
                                            <dd>{context.read_length}</dd>
                                        </div>
                                    : null}

                                    {context.file_size ?
                                        <div data-test="filesize">
                                            <dt>File size</dt>
                                            <dd>{context.file_size}</dd>
                                        </div>
                                    : null}

                                    {context.mapped_read_length ?
                                        <div data-test="mappreadlength">
                                            <dt>Mapped read length</dt>
                                            <dd>{context.mapped_read_length}</dd>
                                        </div>
                                    : null}
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
                                            <dd><DbxrefList values={context.dbxrefs} /></dd>
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

                <FetchedItems
                    {...this.props}
                    url={`/search/?type=File&limit=all&derived_from.accession=${context.accession}`}
                    Component={DerivedFiles}
                    encodevers={globals.encodeVersion(context)}
                    session={this.context.session}
                    ignoreErrors
                />
            </div>
        );
    }
}

FileComponent.propTypes = {
    context: React.PropTypes.object, // File object being displayed
};

FileComponent.contextTypes = {
    session: React.PropTypes.object, // Login information
};

const File = audit(FileComponent);

globals.content_views.register(File, 'File');


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
                                    {file.flowcell_details.map((detail) => {
                                        const items = [
                                            detail.machine ? detail.machine : '',
                                            detail.flowcell ? detail.flowcell : '',
                                            detail.lane ? detail.lane : '',
                                            detail.barcode ? detail.barcode : '',
                                        ];
                                        return <span className="line-item">{items.join(':')}</span>;
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
                                            <span>
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
    file: React.PropTypes.object.isRequired, // File being displayed
};


class Listing extends React.Component {
    render() {
        const result = this.props.context;

        return (
            <li>
                <div className="clearfix">
                    <div className="pull-right search-meta">
                        <p className="type meta-title">File</p>
                        <p className="type">{` ${result.accession}`}</p>
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
    context: React.PropTypes.object, // File object being rendered
};

globals.listing_views.register(Listing, 'File');
