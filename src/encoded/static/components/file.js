import React from 'react';
import moment from 'moment';
import shortid from 'shortid';
import _ from 'underscore';
import { Panel, PanelHeading, PanelBody } from '../libs/bootstrap/panel';
import { collapseIcon } from '../libs/svg-icons';
import { DbxrefList } from './dbxref';
import { FetchedItems } from './fetched';
import globals from './globals';
import { ProjectBadge } from './image';
import { requestFiles } from './objectutils';
import { SortTablePanel, SortTable } from './sorttable';
import { StatusLabel } from './statuslabel';


// Display an audit icon within the audit indicator button. The type of icon depends on the given
// audit level.
class AuditIcon extends React.Component {
    render() {
        const { level, addClasses } = this.props;
        const levelName = level.toLowerCase();
        const iconClass = `icon audit-activeicon-${levelName}${addClasses ? ` ${addClasses}` : ''}`;

        return <i className={iconClass}><span className="sr-only">Audit {levelName}</span></i>;
    }
}

AuditIcon.propTypes = {
    level: React.PropTypes.string.isRequired, // Level name from an audit object
    addClasses: React.PropTypes.string, // CSS classes to add to default
};

AuditIcon.defaultProps = {
    addClasses: '',
};


// Display details text with embedded links. This gets displayed in each row of the audit details.
class DetailEmbeddedLink extends React.Component {
    render() {
        const { detail } = this.props;

        // Get an array of all paths in the detail string, if any.
        const matches = detail.match(/(\/.*?\/.*?\/)(?=[\t \n,.]|$)/gmi);
        if (matches) {
            // Build an array of React objects containing text followed by a path. In effect, the
            // detail text is broken up into pieces, with each piece ending in a @id, combined
            // with the text leading up to it. Any text following the last @id in the detail text
            // gets picked up after this loop.
            let lastStart = 0;
            const result = matches.map((match) => {
                const linkStart = detail.indexOf(match, lastStart);
                const preText = detail.slice(lastStart, linkStart);
                lastStart = linkStart + match.length;
                const linkText = detail.slice(linkStart, lastStart);

                // Render the text leading up to the path, and then the path as a link.
                if (match !== this.props.except || this.props.forcedEditLink) {
                    return <span key={linkStart}>{preText}<a href={linkText}>{linkText}</a></span>;
                }

                // For the case where we have an @id not to be rendered as a link.
                return <span key={linkStart}>{preText}{linkText}</span>;
            });

            // Pick up any trailing text after the last path, if any
            const postText = detail.slice(lastStart);

            // Render all text and paths, plus the trailing text
            return <span>{result}{postText}</span>;
        }

        // No links in the detail string; just display it with no links.
        return <span>{detail}</span>;
    }
}

DetailEmbeddedLink.propTypes = {
    detail: React.PropTypes.string.isRequired, // Test to display in each audit's detail, possibly containing @ids that this component turns into links automatically
    except: React.PropTypes.string, // @id of object being reported on. Specifying it here prevents it from being converted to a link in the `detail` text
    forcedEditLink: React.PropTypes.bool, // `true` to display the `except` path as a link anyway
};

DetailEmbeddedLink.defaultProps = {
    except: '',
    forcedEditLink: false,
};


class AuditGroup extends React.Component {
    constructor() {
        super();
        this.state = { detailOpen: false };
        this.detailSwitch = this.detailSwitch.bind(this);
    }

    detailSwitch() {
        // Click on the detail disclosure triangle
        this.setState({ detailOpen: !this.state.detailOpen });
    }

    render() {
        const { group, except, auditLevelName, forcedEditLink } = this.props;
        const level = auditLevelName.toLowerCase();
        const { detailOpen } = this.state;
        const alertClass = `audit-detail-${level}`;
        const alertItemClass = `panel-collapse collapse audit-item-${level}${detailOpen ? ' in' : ''}`;
        const iconClass = `icon audit-icon-${level}`;
        const categoryName = group[0].category.uppercaseFirstChar();

        return (
            <div className={alertClass}>
                <div className={`icon audit-detail-trigger-${level}`}>
                    <button onClick={this.detailSwitch} className="collapsing-title">
                        {collapseIcon(!detailOpen)}
                    </button>
                </div>
                <div className="audit-detail-info">
                    <i className={iconClass} />
                    <strong>&nbsp;{categoryName}</strong>
                    <div className="btn-info-audit">
                        <a href={`/data-standards/audits/#${categoryName.toLowerCase().split(' ').join('_')}`} title={`View description of ${categoryName} in a new tab`} rel="noopener noreferrer" target="_blank"><i className="icon icon-question-circle" /></a>
                    </div>
                </div>
                <div className="audit-details-section">
                    <div className="audit-details-decoration" />
                    {group.map(audit =>
                        <div className={alertItemClass} key={audit.id} role="alert">
                            <DetailEmbeddedLink detail={audit.detail} except={except} forcedEditLink={forcedEditLink} />
                        </div>,
                    )}
                </div>
            </div>
        );
    }
}

AuditGroup.propTypes = {
    group: React.PropTypes.array.isRequired, // Array of audits in one name/category
    auditLevelName: React.PropTypes.string.isRequired, // Audit level name
    except: React.PropTypes.string, // @id of object whose audits are being displayed.
    forcedEditLink: React.PropTypes.bool, // `true` to display the `except` path as a link anyway
};

AuditGroup.defaultProps = {
    except: '',
    forcedEditLink: false,
};


function idAudits(audits) {
    Object.keys(audits).forEach((auditType) => {
        const typeAudits = audits[auditType];
        typeAudits.forEach((audit) => {
            audit.id = shortid.generate();
        });
    });
}


const auditDecor = AuditComponent => class extends React.Component {
    constructor() {
        super();
        this.state = { auditDetailOpen: false };
        this.toggleAuditDetail = this.toggleAuditDetail.bind(this);
        this.auditIndicators = this.auditIndicators.bind(this);
        this.auditDetail = this.auditDetail.bind(this);
    }

    toggleAuditDetail() {
        this.setState(prevState => ({ auditDetailOpen: !prevState.auditDetailOpen }));
    }

    auditIndicators(audits, id, session, search) {
        const loggedIn = session && session['auth.userid'];

        if (audits && Object.keys(audits).length) {
            // Attach unique IDs to each audit to use as React keys.
            idAudits(audits);

            // Sort the audit levels by their level number, using the first element of each warning category
            const sortedAuditLevels = _(Object.keys(audits)).sortBy(level => -audits[level][0].level);

            const indicatorClass = `audit-indicators btn btn-info${this.context.auditDetailOpen ? ' active' : ''}${search ? ' audit-search' : ''}`;
            if (loggedIn || !(sortedAuditLevels.length === 1 && sortedAuditLevels[0] === 'INTERNAL_ACTION')) {
                return (
                    <button className={indicatorClass} aria-label="Audit indicators" aria-expanded={this.context.auditDetailOpen} aria-controls={id} onClick={this.toggleAuditDetail}>
                        {sortedAuditLevels.map((level) => {
                            if (loggedIn || level !== 'INTERNAL_ACTION') {
                                // Calculate the CSS class for the icon
                                const levelName = level.toLowerCase();
                                const btnClass = `btn-audit btn-audit-${levelName} audit-level-${levelName}`;
                                const groupedAudits = _(audits[level]).groupBy('category');

                                return (
                                    <span className={btnClass} key={level}>
                                        <AuditIcon level={level} />
                                        {Object.keys(groupedAudits).length}
                                    </span>
                                );
                            }
                            return null;
                        })}
                    </button>
                );
            }

            // Logged out and the only audit level is DCC action, so don't show a button
            return null;
        }

        // No audits provided.
        return null;
    }

    auditDetail(audits, except, id, forcedEditLink, session) {
        if (audits && this.state.auditDetailOpen) {
            // Sort the audit levels by their level number, using the first element of each warning category
            const sortedAuditLevelNames = _(Object.keys(audits)).sortBy(level => -audits[level][0].level);
            const loggedIn = session && session['auth.userid'];

            // First loop by audit level, then by audit group
            return (
                <Panel addClasses="audit-details" id={id.replace(/\W/g, '')} aria-hidden={!this.state.auditDetailOpen}>
                    {sortedAuditLevelNames.map((auditLevelName) => {
                        if (loggedIn || auditLevelName !== 'INTERNAL_ACTION') {
                            const audit = audits[auditLevelName];

                            // Group audits within a level by their category ('name' corresponds to
                            // 'category' in a more machine-like form)
                            const groupedAudits = _(audit).groupBy('category');

                            return Object.keys(groupedAudits).map(groupName =>
                                <AuditGroup
                                    group={groupedAudits[groupName]}
                                    groupName={groupName}
                                    auditLevelName={auditLevelName}
                                    except={except}
                                    forcedEditLink={forcedEditLink}
                                    key={groupName}
                                />,
                            );
                        }
                        return null;
                    })}
                </Panel>
            );
        }
        return null;
    }

    render() {
        return (
            <AuditComponent
                {...this.props}
                auditIndicators={this.auditIndicators}
                auditDetail={this.auditDetail}
            />
        );
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
                        {this.props.auditIndicators(context.audit, 'file-audit', this.context.session)}
                        <div className="status-line">
                            {context.status ?
                                <div className="characterization-status-labels">
                                    <StatusLabel title="Status" status={context.status} />
                                </div>
                            : null}
                        </div>
                        {this.props.auditDetail(context.audit, context['@id'], 'file-audit', false, this.context.session)}
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
                    url={`/search/?type=File&limit=all&derived_from=${context['@id']}`}
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

const File = auditDecor(FileComponent);

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
