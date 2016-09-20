'use strict';
const React = require('react');
const _ = require('underscore');
const url = require('url');
const {Panel, PanelHeading, PanelBody} = require('../libs/bootstrap/panel');
const {SvgIcon, CollapseIcon} = require('../libs/svg-icons');
const {SortTable} = require('./sorttable');
const globals = require('./globals');
const {StatusLabel} = require('./statuslabel');
const {ProjectBadge, Attachment} = require('./image');
const {AuditIndicators, AuditDetail, AuditMixin} = require('./audit');
const {RelatedItems} = require('./item');
const {DbxrefList} = require('./dbxref');
const {FetchedItems} = require('./fetched');
const {Breadcrumbs} = require('./navigation');
const {TreatmentDisplay, SingleTreatment} = require('./objectutils');
const {BiosampleTable} = require('./typeutils');
const {Document, DocumentsPanel, DocumentsSubpanels, DocumentPreview, DocumentFile} = require('./doc');
const {PickerActionsMixin} = require('./search');


// Map GM techniques to a presentable string
const GM_TECHNIQUE_MAP = {
    'Crispr': 'CRISPR',
    'Tale': 'TALE'
};


const GeneticModification = module.exports.GeneticModification = React.createClass({
    mixins: [AuditMixin],

    render: function() {
        const context = this.props.context;
        let itemClass = globals.itemClass(context, 'view-detail key-value');
        let coords = context.modified_site;

        // Configure breadcrumbs for the page.
        const crumbs = [
            {id: 'Genetic Modifications'},
            {id: context.target && context.target.label, query: 'target.label=' + (context.target && context.target.label), tip: context.target && context.target.label},
            {id: context.modification_type, query: 'modification_type=' + context.modification_type, tip: context.modification_type}
        ];

        // Collect and combine documents, including from genetic modification characterizations.
        let modDocs = [];
        let charDocs = [];
        let techDocs = [];
        if (context.documents && context.documents.length) {
            modDocs = context.documents;
        }
        if (context.characterizations && context.characterizations.length) {
            context.characterizations.forEach(characterization => {
                if (characterization.documents && characterization.documents.length) {
                    charDocs = charDocs.concat(characterization.documents);
                }
            });
        }
        if (context.modification_techniques && context.modification_techniques.length) {
            context.modification_techniques.forEach(technique => {
                if (technique.documents && technique.documents.length) {
                    techDocs = techDocs.concat(technique.documents);
                }
            });
        }
        if (modDocs.length) {
            modDocs = globals.uniqueObjectsArray(modDocs);
        }
        if (charDocs.length) {
            charDocs = globals.uniqueObjectsArray(charDocs);
        }
        if (techDocs.length) {
            techDocs = globals.uniqueObjectsArray(techDocs);
        }

        return (
            <div className={globals.itemClass(context, 'view-item')}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs root='/search/?type=GeneticModification' crumbs={crumbs} />
                        <h2>{context.modification_type}</h2>
                        <div className="status-line">
                            <div className="characterization-status-labels">
                                <StatusLabel title="Status" status={context.status} />
                            </div>
                            <AuditIndicators audits={context.audit} id="genetic-modification-audit" />
                        </div>
                    </div>
                </header>
                <AuditDetail context={context} id="genetic-modification-audit" />
                <Panel addClasses="data-display">
                    <PanelBody addClasses="panel-body-with-header">
                        <div className="flexrow">
                            <div className="flexcol-sm-6">
                                <div className="flexcol-heading experiment-heading"><h4>Summary</h4></div>
                                <dl className={itemClass}>
                                    {context.description ?
                                        <div data-test="description">
                                            <dt>Description</dt>
                                            <dd>{context.description}</dd>
                                        </div>
                                    : null}

                                    {context.purpose ?
                                        <div data-test="purpose">
                                            <dt>Modification purpose</dt>
                                            <dd>{context.purpose}</dd>
                                        </div>
                                    : null}

                                    {context.zygosity ?
                                        <div data-test="zygosity">
                                            <dt>Modification zygosity</dt>
                                            <dd>{context.zygosity}</dd>
                                        </div>
                                    : null}

                                    {context.url ?
                                        <div data-test="url">
                                            <dt>Product ID</dt>
                                            <dd><a href={context.url}>{context.product_id ? context.product_id : context.url}</a></dd>
                                        </div>
                                    : null}

                                    {context.target ?
                                        <div data-test="target">
                                            <dt>Target</dt>
                                            <dd><a href={context.target['@id']}>{context.target.label}</a></dd>
                                        </div>
                                    : null}

                                    {coords && coords.assembly ?
                                        <div data-test="coordsassembly">
                                            <dt>Mapping assembly</dt>
                                            <dd>{context.modified_site.assembly}</dd>
                                        </div>
                                    : null}

                                    {coords && coords.chromosome && coords.start && coords.end ?
                                        <div data-test="coordssequence">
                                            <dt>Genomic coordinates</dt>
                                            <dd>chr{coords.chromosome}:{coords.start}-{coords.end}</dd>
                                        </div>
                                    : null}
                                </dl>

                                {context.treatments && context.treatments.length ?
                                    <section className="data-display-array">
                                        <hr />
                                        <h4>Treatment details</h4>
                                        {context.treatments.map(treatment => TreatmentDisplay(treatment))}
                                    </section>
                                : null}

                                {context.modification_techniques && context.modification_techniques.length ?
                                    <section className="data-display-array">
                                        <hr />
                                        <h4>Modification techniques</h4>
                                        {GeneticModificationTechniques(context.modification_techniques)}
                                    </section>
                                : null}
                            </div>

                            <div className="flexcol-sm-6">
                                <div className="flexcol-heading experiment-heading">
                                    <h4>Attribution</h4>
                                    <ProjectBadge award={context.award} addClasses="badge-heading" />
                                </div>
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

                                    {context.source.title ?
                                        <div data-test="sourcetitle">
                                            <dt>Source</dt>
                                            <dd>
                                                {context.source.url ?
                                                    <a href={context.source.url}>{context.source.title}</a>
                                                :
                                                    <span>{context.source.title}</span>
                                                }
                                            </dd>
                                        </div>
                                    : null}

                                    <div data-test="project">
                                        <dt>Project</dt>
                                        <dd>{context.award.project}</dd>
                                    </div>

                                    {context.dbxrefs && context.dbxrefs.length ?
                                        <div data-test="externalresources">
                                            <dt>External resources</dt>
                                            <dd><DbxrefList values={context.dbxrefs} /></dd>
                                        </div>
                                    : null}

                                    {context.aliases.length ?
                                        <div data-test="aliases">
                                            <dt>Aliases</dt>
                                            <dd>{context.aliases.join(", ")}</dd>
                                        </div>
                                    : null}
                                </dl>
                            </div>
                        </div>
                    </PanelBody>
                </Panel>

                {context.characterizations && context.characterizations.length ?
                    <GeneticModificationCharacterizations characterizations={context.characterizations} />
                : null}

                <DocumentsPanel documentSpecs={[
                    {label: 'Modification', documents: modDocs},
                    {label: 'Characterization', documents: charDocs},
                    {label: 'Techniques', documents: techDocs}]} />

                <RelatedItems
                    title="Biosamples using this genetic modification"
                    url={'/search/?type=Biosample&genetic_modifications.uuid=' + context.uuid}
                    Component={BiosampleTable} />
            </div>
        );
    }
});

globals.content_views.register(GeneticModification, 'GeneticModification');


const GeneticModificationCharacterizations = React.createClass({
    propTypes: {
        characterizations: React.PropTypes.array // Genetic modificiation characterizations to display
    },

    render: function () {
        const {characterizations} = this.props;
        const itemClass = 'view-detail key-value';

        return (
            <Panel>
                <PanelHeading>
                    <h4>Characterization attachments</h4>
                </PanelHeading>
                <PanelBody addClasses="attachment-panel-outer">
                    <section className="flexrow attachment-panel-inner">
                        {characterizations.map(characterization => {
                            return <AttachmentPanel key={characterization.uuid} context={characterization} attachment={characterization.attachment} title={characterization.characterization_method} />;
                        })}
                    </section>
                </PanelBody>
            </Panel>
        );
    }
});


// Returns array of genetic modification technique components. The type of each technique can vary,
// so we need to look up the display component based on the @type of each technique.
const GeneticModificationTechniques = function(techniques) {
    if (techniques && techniques.length) {
        return techniques.map(technique => {
            const ModificationTechniqueView = globals.panel_views.lookup(technique);
            return <ModificationTechniqueView key={technique.uuid} context={technique} />;
        });
    }
    return null;
};


// Display modification technique specific to the CRISPR type.
const TechniqueCrispr = React.createClass({
    propTypes: {
        context: React.PropTypes.object // CRISPR genetic modificiation technique to display
    },

    render: function() {
        const {context} = this.props;
        const itemClass = globals.itemClass(context, 'view-detail key-value');

        return (
            <dl className={itemClass}>
                <div data-test="techniquetype">
                    <dt>Technique type</dt>
                    <dd>CRISPR</dd>
                </div>

                {context.insert_sequence ?
                    <div data-test="insertsequence">
                        <dt>Insert sequence</dt>
                        <dd>{context.insert_sequence}</dd>
                    </div>
                : null}

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

                {context.source.title ?
                    <div data-test="sourcetitle">
                        <dt>Source</dt>
                        <dd>
                            {context.source.url ?
                                <a href={context.source.url}>{context.source.title}</a>
                            :
                                <span>{context.source.title}</span>
                            }
                        </dd>
                    </div>
                : null}

                {context.dbxrefs && context.dbxrefs.length ?
                    <div data-test="externalresources">
                        <dt>External resources</dt>
                        <dd><DbxrefList values={context.dbxrefs} /></dd>
                    </div>
                : null}
            </dl>
        );
    }
});

globals.panel_views.register(TechniqueCrispr, 'Crispr');


// Display modification technique specific to the TALE type.
const TechniqueTale = React.createClass({
    propTypes: {
        context: React.PropTypes.object // TALE genetic modificiation technique to display
    },

    render: function() {
        const {context} = this.props;
        const itemClass = globals.itemClass(context, 'view-detail key-value');

        return (
            <dl className={itemClass}>
                <div data-test="techniquetype">
                    <dt>Technique type</dt>
                    <dd>TALE</dd>
                </div>

                <div data-test="rvdsequence">
                    <dt>RVD sequence</dt>
                    <dd>{context.RVD_sequence}</dd>
                </div>

                <div data-test="talenplatform">
                    <dt>TALEN platform</dt>
                    <dd>{context.talen_platform}</dd>
                </div>

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

                {context.source.title ?
                    <div data-test="sourcetitle">
                        <dt>Source</dt>
                        <dd>
                            {context.source.url ?
                                <a href={context.source.url}>{context.source.title}</a>
                            :
                                <span>{context.source.title}</span>
                            }
                        </dd>
                    </div>
                : null}

                {context.dbxrefs && context.dbxrefs.length ?
                    <div data-test="externalresources">
                        <dt>External resources</dt>
                        <dd><DbxrefList values={context.dbxrefs} /></dd>
                    </div>
                : null}
            </dl>
        );
    }
});

globals.panel_views.register(TechniqueTale, 'Tale');


// Display a panel for attachments that aren't a part of an associated document
const AttachmentPanel = module.exports.AttachmentPanel = React.createClass({
    propTypes: {
        context: React.PropTypes.object.isRequired, // Object that owns the attachment; needed for attachment path
        attachment: React.PropTypes.object.isRequired, // Attachment being rendered
        title: React.PropTypes.string // Title to display in the caption area
    },

    render: function() {
        const {context, attachment, title} = this.props;

        // Make the download link
        var download, attachmentHref;
        if (attachment.href && attachment.download) {
            attachmentHref = url.resolve(context['@id'], attachment.href);
            download = (
                <div className="dl-link">
                    <i className="icon icon-download"></i>&nbsp;
                    <a data-bypass="true" href={attachmentHref} download={attachment.download}>
                        Download
                    </a>
                </div>
            );
        } else {
            download = <em>Attachment not available to download</em>;
        }

        return (
            <div className="flexcol panel-attachment">
                <Panel addClasses={globals.itemClass(context, 'view-detail')}>
                    <figure>
                        <Attachment context={context} attachment={attachment} className="characterization" />
                    </figure>
                    <div className="document-intro document-meta-data">
                        {title ?
                            <div data-test="attachments">
                                <strong>Method: </strong>
                                {title}
                            </div>
                        : null}
                        {download}
                    </div>
                </Panel>
            </div>
        );
    }
});


const Listing = React.createClass({
    mixins: [PickerActionsMixin, AuditMixin],

    render: function() {
        const result = this.props.context;

        let techniques = [];
        if (result.modification_techniques && result.modification_techniques.length) {
            techniques = _.uniq(result.modification_techniques.map(technique => {
                if (technique['@type'][0] === 'Crispr') {
                    return 'CRISPR';
                }
                if (technique['@type'][0] === 'Tale') {
                    return 'TALE';
                }
                return technique['@type'][0];
            }));
        }

        return (
            <li>
                <div className="clearfix">
                    {this.renderActions()}
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Genetic modifications</p>
                        <p className="type meta-status">{' ' + result.status}</p>
                        <AuditIndicators audits={result.audit} id={this.props.context['@id']} search />
                    </div>
                    <div className="accession"><a href={result['@id']}>{result.modification_type}</a></div>
                    <div className="data-row">
                        {techniques.length ? <div><strong>Modification techniques: </strong>{techniques.join(', ')}</div> : null}
                    </div>
                </div>
                <AuditDetail context={result} id={this.props.context['@id']} forcedEditLink />
            </li>
        );
    }
});

globals.listing_views.register(Listing, 'GeneticModification');


// Given a GeneticModification object, get all its modification techniques as an array of strings.
// If the GM object has no modification techniques, this function returns a zero-length array. This
// function is exported so that Jest can test it.
const getGMTechniques = module.exports.getGMTechniques = _.memoize(_getGMTechniques, gm => gm.uuid);

// Root function for getGMModificationTechniques, which caches the results based on the genetic
// modification's uuid.
function _getGMTechniques(gm) {
    let techniques = [];
    if (gm.modification_techniques && gm.modification_techniques.length) {
        techniques = gm.modification_techniques.map(technique => {
            // Map modification technique @type[0] to presentable string.
            let presented = GM_TECHNIQUE_MAP[technique['@type'][0]];
            if (!presented) {
                // If we don't know the technique, just use the technique without mapping.
                presented = technique['@type'][0];
            }
            return presented;
        });
    }
    return techniques.sort();
}


const calcGMSummarySentence = module.exports.calcGMSummarySentence = _.memoize(_calcGMSummarySentence, gm => gm.uuid);

// Calculate a summary sentence for the GM passed in `gm`.
function _calcGMSummarySentence(gm) {
    let treatments = [];

    // modification_type is required, so start the sentence with that.
    let sentence = gm.modification_type;

    // Add the target of the modification if there is one.
    if (gm.target) {
        sentence += ' of ' + gm.target.label;
    }

    // Collect up an array of strings with techniques and treatments.
    let techniques = getGMTechniques(gm);
    if (gm.treatments && gm.treatments.length) {
        treatments = gm.treatments.map(treatment => SingleTreatment(treatment));
    }
    let techtreat = techniques.concat(treatments).join(', ');

    // Add techniques and treatments string if any.
    if (techtreat.length) {
        sentence += ' using ' + techtreat;
    }

    return sentence;
}


// Display a summary of genetic modifications given in the geneticModifications prop. This
// component assumes the `geneticModifications` array has at least one entry, so make sure of that
// before calling this component.
const GeneticModificationSummary = module.exports.GeneticModificationSummary = React.createClass({
    propTypes: {
        geneticModifications: React.PropTypes.array.isRequired // Array of genetic modifications
    },

    render: function() {
        let geneticModifications = this.props.geneticModifications;

        // Group genetic modifications by a combination like this:
        // modification_type;modification_technique,modification_technique,...;target.label
        let gmGroups = _(geneticModifications).groupBy(gm => {
            let groupKey = gm.modification_type;

            // Add any modification techniques to the group key.
            let techniques = getGMTechniques(gm);
            if (techniques.length) {
                groupKey += ';' + techniques.join();
            }

            // Add the target (if any) to the group key.
            if (gm.target) {
                groupKey += ';' + gm.target.label;
            }

            // Add the treatment UUIDs (if any) to the group key.
            if (gm.modification_treatments && gm.modification_treatments.length) {
                groupKey += ';' + gm.modification_treatments.map(treatment => treatment.uuid).sort().join();
            }

            return groupKey;
        });

        return (
            <Panel>
                <PanelHeading>
                    <h4>Genetic modifications</h4>
                </PanelHeading>
                {Object.keys(gmGroups).map(groupKey => {
                    let group = gmGroups[groupKey];
                    let sentence = calcGMSummarySentence(group[0]);
                    return <GeneticModificationGroup key={groupKey} groupSentence={sentence} gms={group} />;
                })}
            </Panel>
        );
    }
});


// Display one GM group, which consists of all GMs that share the same type, technique, target, and
// treatments. A group is an array of GM objects.
const GeneticModificationGroup = module.exports.GeneticModificationGroup = React.createClass({
    propTypes: {
        group: React.PropTypes.array // Array of GM objects in the same group
    },

    getInitialState: function() {
        return {
            detailOpen: false // True if group is expanded
        };
    },

    columns: {
        'aliases': {
            title: 'Aliases',
            display: modification => modification.aliases && modification.aliases.length ? modification.aliases.join(', ') : '',
            sorter: false
        },
        'purpose': {
            title: 'Purpose'
        },
        'zygosity': {
            title: 'Zygosity'
        },
        'assembly': {
            title: 'Mapping assembly',
            getValue: modification => modification.modified_site && modification.modified_site.assembly ? modification.modified_site.assembly : ''
        },
        'coordinates': {
            title: 'Coordinates',
            display: modification => {
                var coords = modification.modified_site;
                if (coords && coords.chromosome) {
                    return <span>chr{coords.chromosome}:{coords.start}-{coords.end}</span>;
                }
                return null;
            },
            objSorter: (a, b) => {
                let sortRes; // Sorting result
                var aCoord = a.modified_site;
                var bCoord = b.modified_site;
                if (aCoord && bCoord) {
                    sortRes = (aCoord.chromosome < bCoord.chromosome) ? -1 : ((bCoord.chromosome > aCoord.chromosome) ? 1 : 0);
                    if (!sortRes) {
                        // Identical chromosomes; sort by start coordinates
                        sortRes = aCoord.start - bCoord.start;
                        if (!sortRes) {
                            // Identical start coordinates; sort by end coordinates
                            sortRes = aCoord.end - bCoord.end;
                        }
                    }
                } else {
                    // One or the other or both are missing; sort the non-missing one first
                    sortRes = aCoord ? -1 : (bCoord ? 1 : 0);
                }
                return sortRes;
            }
        }
    },

    detailSwitch: function() {
        // Click on the detail disclosure triangle
        this.setState({detailOpen: !this.state.detailOpen});
    },

    render: function() {
        let {groupSentence, gms} = this.props;
        return (
            <div className="gm-group">
                <div className="gm-group-detail">
                    <div className="icon gm-detail-trigger">
                        <a href="#" data-trigger onClick={this.detailSwitch} className="collapsing-title">
                            {CollapseIcon(!this.state.detailOpen)}
                        </a>
                    </div>
                    <div className="gm-detail-sentence">
                        {groupSentence}
                    </div>
                </div>
                {this.state.detailOpen ?
                    <div className="gm-detail-table">
                        <SortTable list={gms} columns={this.columns} />
                        <div className="gm-detail-table-shadow"></div>
                    </div>
                : null}
            </div>
        );
    }
});
