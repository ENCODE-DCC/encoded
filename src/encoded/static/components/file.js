import React from 'react';
import moment from 'moment';
import { Panel, PanelBody } from '../libs/bootstrap/panel';
import globals from './globals';
import { AuditIndicators, AuditDetail, AuditMixin } from './audit';
import { DbxrefList } from './dbxref';
import { ProjectBadge } from './image';
import { StatusLabel } from './statuslabel';


const File = React.createClass({
    propTypes: {
        context: React.PropTypes.object, // File object being displayed
    },

    mixins: [AuditMixin],

    render: function () {
        const { context } = this.props;
        const itemClass = globals.itemClass(context, 'view-item');
        const altacc = (context.alternate_accessions && context.alternate_accessions.length) ? context.alternate_accessions.join(', ') : null;
        const aliasList = (context.aliases && context.aliases.length) ? context.aliases.join(', ') : '';

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
                            {context.audit ? <AuditIndicators audits={context.audit} id="file-audit" /> : null}
                        </div>
                    </div>
                </header>
                <AuditDetail context={context} except={context['@id']} id="file-audit" />
                <Panel addClasses="data-display">
                    <div className="split-panel">
                        <div className="split-panel__part split-panel__part--p50">
                            <div className="split-panel__heading"><h4>Summary</h4></div>
                            <div className="split-panel__content">
                                <dl className="key-value">
                                    <div data-test="term-name">
                                        <dt>Dataset</dt>
                                        <dd><a href={context.dataset}>{globals.atIdToAccession(context.dataset)}</a></dd>
                                    </div>

                                    {context.replicate ?
                                        <div data-test="bioreplicate">
                                            <dt>Biological replicate(s)</dt>
                                            <dd>{`[${context.replicate.biological_replicate_number}]`}</dd>
                                        </div>
                                    : (context.biological_replicates && context.biological_replicates.length ?
                                        <div data-test="bioreplicate">
                                            <dt>Biological replicate(s)</dt>
                                            <dd>{`[${context.biological_replicates.join(', ')}]`}</dd>
                                        </div>
                                    : null)}

                                    {context.replicate ?
                                        <div data-test="techreplicate">
                                            <dt>Technical replicate</dt>
                                            <dd>{context.replicate.technical_replicate_number}</dd>
                                        </div>
                                    : (context.biological_replicates && context.biological_replicates.length ?
                                        <div data-test="techreplicate">
                                            <dt>Technical replicate</dt>
                                            <dd>{'-'}</dd>
                                        </div>
                                    : null)}

                                    {pipelines.length ?
                                        <div data-test="pipelines">
                                            <dt>Pipelines</dt>
                                            <dd>
                                                {pipelines.map((pipeline, i) =>
                                                    <span key={i}>
                                                        {i > 0 ? <span>{','}<br /></span> : null}
                                                        <a href={pipeline['@id']}>{pipeline.title}</a>
                                                    </span>
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
                                            <dd>{aliasList}</dd>
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
            </div>
        );
    },
});

globals.content_views.register(File, 'File');
