import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import { Panel, PanelHeading, PanelBody } from '../libs/bootstrap/panel';
import { collapseIcon } from '../libs/svg-icons';
import { auditDecor } from './audit';
import { SortTable } from './sorttable';
import globals from './globals';
import StatusLabel from './statuslabel';
import { ProjectBadge, Attachment } from './image';
import { RelatedItems } from './item';
import { DbxrefList } from './dbxref';
import { Breadcrumbs } from './navigation';
import { treatmentDisplay, singleTreatment } from './objectutils';
import { BiosampleTable } from './typeutils';
import { AttachmentPanel, DocumentsPanel } from './doc';
import { PickerActions } from './search';


// Map GM techniques to a presentable string
const GM_TECHNIQUE_MAP = {
    Crispr: 'CRISPR',
    Tale: 'TALE',
};


const GeneticModificationCharacterizations = (props) => {
    const { characterizations } = props;

    return (
        <Panel>
            <PanelHeading>
                <h4>Characterization attachments</h4>
            </PanelHeading>
            <PanelBody addClasses="attachment-panel-outer">
                <section className="flexrow attachment-panel-inner">
                    {characterizations.map(characterization =>
                        <AttachmentPanel key={characterization.uuid} context={characterization} attachment={characterization.attachment} title={characterization.characterization_method} />,
                    )}
                </section>
            </PanelBody>
        </Panel>
    );
};

GeneticModificationCharacterizations.propTypes = {
    characterizations: PropTypes.array.isRequired, // Genetic modificiation characterizations to display
};


// Returns array of genetic modification technique components. The type of each technique can vary,
// so we need to look up the display component based on the @type of each technique.
function geneticModificationTechniques(techniques) {
    if (techniques && techniques.length) {
        return techniques.map((technique) => {
            const ModificationTechniqueView = globals.panel_views.lookup(technique);
            return <ModificationTechniqueView key={technique.uuid} context={technique} />;
        });
    }
    return null;
}


export class GeneticModificationComponent extends React.Component {
    render() {
        const context = this.props.context;
        const itemClass = globals.itemClass(context, 'view-detail key-value');
        const coords = context.modified_site;

        // Configure breadcrumbs for the page.
        const crumbs = [
            { id: 'Genetic Modifications' },
            { id: context.target && context.target.label, query: `target.label=${context.target && context.target.label}`, tip: context.target && context.target.label },
            { id: context.modification_type, query: `modification_type=${context.modification_type}`, tip: context.modification_type },
        ];

        // Collect and combine documents, including from genetic modification characterizations.
        let modDocs = [];
        let charDocs = [];
        let techDocs = [];
        let biosampleDocs = [];
        if (context.documents && context.documents.length) {
            modDocs = context.documents;
        }
        if (context.characterizations && context.characterizations.length) {
            context.characterizations.forEach((characterization) => {
                if (characterization.documents && characterization.documents.length) {
                    charDocs = charDocs.concat(characterization.documents);
                }
            });
        }
        if (context.modification_techniques && context.modification_techniques.length) {
            context.modification_techniques.forEach((technique) => {
                if (technique.documents && technique.documents.length) {
                    techDocs = techDocs.concat(technique.documents);
                }
            });
        }
        if (context.biosamples_modified && context.biosamples_modified) {
            context.biosamples_modified.forEach((biosample) => {
                if (biosample.documents && biosample.documents.length) {
                    biosampleDocs = biosampleDocs.concat(biosample.documents);
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
        if (biosampleDocs.length) {
            biosampleDocs = globals.uniqueObjectsArray(biosampleDocs);
        }

        return (
            <div className={globals.itemClass(context, 'view-item')}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs root="/search/?type=GeneticModification" crumbs={crumbs} />
                        <h2>{context.modification_type}</h2>
                        <div className="status-line">
                            <div className="characterization-status-labels">
                                <StatusLabel title="Status" status={context.status} />
                            </div>
                            {this.props.auditIndicators(context.audit, 'genetic-modification-audit', { session: this.context.session })}
                        </div>
                    </div>
                </header>
                {this.props.auditDetail(context.audit, 'genetic-modification-audit', { session: this.context.session, except: context['@id'] })}
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
                                        {context.treatments.map(treatment => treatmentDisplay(treatment))}
                                    </section>
                                : null}

                                {context.modification_techniques && context.modification_techniques.length ?
                                    <section className="data-display-array">
                                        <hr />
                                        <h4>Modification techniques</h4>
                                        {geneticModificationTechniques(context.modification_techniques)}
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

                                    {context.submitted_by ?
                                        <div data-test="submittedby">
                                            <dt>Submitted by</dt>
                                            <dd>{context.submitted_by.title}</dd>
                                        </div>
                                    : null}

                                    {context.source && context.source.title ?
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

                                    {context.aliases && context.aliases.length ?
                                        <div data-test="aliases">
                                            <dt>Aliases</dt>
                                            <dd>{context.aliases.join(', ')}</dd>
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

                <DocumentsPanel
                    documentSpecs={[
                        { label: 'Modification', documents: modDocs },
                        { label: 'Characterization', documents: charDocs },
                        { label: 'Techniques', documents: techDocs },
                        { label: 'Biosample', documents: biosampleDocs },
                    ]}
                />

                <RelatedItems
                    title="Biosamples using this genetic modification"
                    url={`/search/?type=Biosample&genetic_modifications.uuid=${context.uuid}`}
                    Component={BiosampleTable}
                />
            </div>
        );
    }
}

GeneticModificationComponent.propTypes = {
    context: PropTypes.object.isRequired, // GM object being displayed
    auditIndicators: PropTypes.func.isRequired, // Audit HOC function to display audit indicators
    auditDetail: PropTypes.func.isRequired, // Audit HOC function to display audit details
};

GeneticModificationComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
};


const GeneticModification = auditDecor(GeneticModificationComponent);

globals.content_views.register(GeneticModification, 'GeneticModification');


const GMAttachmentCaption = (props) => {
    const { title } = props;

    return (
        <div className="document__caption">
            <div data-test="caption">
                <strong>Attachment: </strong>
                {title}
            </div>
        </div>
    );
};

GMAttachmentCaption.propTypes = {
    title: PropTypes.string.isRequired, // Title to display for attachment
};


const GMAttachmentPreview = (props) => {
    const { context, attachment } = props;

    return (
        <figure className="document__preview">
            <Attachment context={context} attachment={attachment} className="characterization" />
        </figure>
    );
};

GMAttachmentPreview.propTypes = {
    context: PropTypes.object.isRequired, // QC metric object that owns the attachment to render
    attachment: PropTypes.object.isRequired, // Attachment to render
};

// Register document caption rendering components
globals.document_views.caption.register(GMAttachmentCaption, 'GeneticModificationCharacterization');

// Register document preview rendering components
globals.document_views.preview.register(GMAttachmentPreview, 'GeneticModificationCharacterization');


// Display modification technique specific to the CRISPR type.
const TechniqueCrispr = (props) => {
    const { context } = props;
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
};

TechniqueCrispr.propTypes = {
    context: PropTypes.object.isRequired, // CRISPR genetic modificiation technique to display
};

globals.panel_views.register(TechniqueCrispr, 'Crispr');


// Display modification technique specific to the TALE type.
const TechniqueTale = (props) => {
    const { context } = props;
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
};

TechniqueTale.propTypes = {
    context: PropTypes.object.isRequired, // TALE genetic modificiation technique to display
};

globals.panel_views.register(TechniqueTale, 'Tale');


class ListingComponent extends React.Component {
    render() {
        const result = this.props.context;

        let techniques = [];
        if (result.modification_techniques && result.modification_techniques.length) {
            techniques = _.uniq(result.modification_techniques.map((technique) => {
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
                    <PickerActions {...this.props} />
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Genetic modifications</p>
                        <p className="type meta-status">{` ${result.status}`}</p>
                        {this.props.auditIndicators(result.audit, result['@id'], { session: this.context.session, search: true })}
                    </div>
                    <div className="accession"><a href={result['@id']}>{result.modification_type}</a></div>
                    <div className="data-row">
                        {techniques.length ? <div><strong>Modification techniques: </strong>{techniques.join(', ')}</div> : null}
                    </div>
                </div>
                {this.props.auditDetail(result.audit, result['@id'], { session: this.context.session, except: result['@id'], forcedEditLink: true })}
            </li>
        );
    }
}

ListingComponent.propTypes = {
    context: PropTypes.object.isRequired, // Search results object
    auditDetail: PropTypes.func.isRequired, // Audit HOC function to show audit details
    auditIndicators: PropTypes.func.isRequired, // Audit HOC function to display audit indicators
};

ListingComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
};

const Listing = auditDecor(ListingComponent);

globals.listing_views.register(Listing, 'GeneticModification');


// Root function for getGMModificationTechniques, which caches the results based on the genetic
// modification's uuid.
function rGetGMTechniques(gm) {
    let techniques = [];
    if (gm.modification_techniques && gm.modification_techniques.length) {
        techniques = gm.modification_techniques.map((technique) => {
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

// Given a GeneticModification object, get all its modification techniques as an array of strings.
// If the GM object has no modification techniques, this function returns a zero-length array. This
// function is exported so that Jest can test it.
export const getGMTechniques = _.memoize(rGetGMTechniques, gm => gm.uuid);


function rCalcGMSummarySentence(gm) {
    let treatments = [];

    // modification_type is required, so start the sentence with that.
    let sentence = gm.modification_type;

    // Add the target of the modification if there is one.
    if (gm.target) {
        sentence += ` of ${gm.target.label}`;
    }

    // Collect up an array of strings with techniques and treatments.
    const techniques = getGMTechniques(gm);
    if (gm.treatments && gm.treatments.length) {
        treatments = gm.treatments.map(treatment => singleTreatment(treatment));
    }
    const techtreat = techniques.concat(treatments).join(', ');

    // Add techniques and treatments string if any.
    if (techtreat.length) {
        sentence += ` using ${techtreat}`;
    }

    return sentence;
}

// Calculate a summary sentence for the GM passed in `gm`.
export const calcGMSummarySentence = _.memoize(rCalcGMSummarySentence, gm => gm.uuid);


// Display a summary of genetic modifications given in the geneticModifications prop. This
// component assumes the `geneticModifications` array has at least one entry, so make sure of that
// before calling this component.
export const GeneticModificationSummary = (props) => {
    const geneticModifications = props.geneticModifications;

    // Group genetic modifications by a combination like this:
    // modification_type;modification_technique,modification_technique,...;target.label
    const gmGroups = _(geneticModifications).groupBy((gm) => {
        let groupKey = gm.modification_type;

        // Add any modification techniques to the group key.
        const techniques = getGMTechniques(gm);
        if (techniques.length) {
            groupKey += `; ${techniques.join()}`;
        }

        // Add the target (if any) to the group key.
        if (gm.target) {
            groupKey += `; ${gm.target.label}`;
        }

        // Add the treatment UUIDs (if any) to the group key.
        if (gm.modification_treatments && gm.modification_treatments.length) {
            groupKey += `; ${gm.modification_treatments.map(treatment => treatment.uuid).sort().join()}`;
        }

        return groupKey;
    });

    return (
        <Panel>
            <PanelHeading>
                <h4>Genetic modifications</h4>
            </PanelHeading>
            {Object.keys(gmGroups).map((groupKey) => {
                const group = gmGroups[groupKey];
                const sentence = calcGMSummarySentence(group[0]);
                return <GeneticModificationGroup key={groupKey} groupSentence={sentence} gms={group} />;
            })}
        </Panel>
    );
};

GeneticModificationSummary.propTypes = {
    geneticModifications: PropTypes.array.isRequired, // Array of genetic modifications
};


// Display one GM group, which consists of all GMs that share the same type, technique, target, and
// treatments. A group is an array of GM objects.
export class GeneticModificationGroup extends React.Component {
    constructor() {
        super();

        // Set the initial React component state.
        this.state = {
            detailOpen: false, // True if group is expanded
        };

        // Bind this to non-React methods.
        this.detailSwitch = this.detailSwitch.bind(this);
    }

    detailSwitch() {
        // Click on the detail disclosure triangle
        this.setState({ detailOpen: !this.state.detailOpen });
    }

    render() {
        const { groupSentence, gms } = this.props;
        return (
            <div className="gm-group">
                <div className="gm-group-detail">
                    <div className="icon gm-detail-trigger">
                        <button onClick={this.detailSwitch} className="collapsing-title">
                            {collapseIcon(!this.state.detailOpen)}
                        </button>
                    </div>
                    <div className="gm-detail-sentence">
                        {groupSentence}
                    </div>
                </div>
                {this.state.detailOpen ?
                    <div className="gm-detail-table">
                        <SortTable list={gms} columns={this.columns} />
                        <div className="gm-detail-table-shadow" />
                    </div>
                : null}
            </div>
        );
    }
}

GeneticModificationGroup.propTypes = {
    groupSentence: PropTypes.string.isRequired, // GM group detail sentence to display
    gms: PropTypes.array.isRequired, // GM objects to display within a group
};

GeneticModificationGroup.columns = {
    aliases: {
        title: 'Aliases',
        display: (modification) => {
            const aliases = modification.aliases && modification.aliases.length ? modification.aliases.join(', ') : 'None';
            return <a href={modification['@id']} title="View details about this genetic modification">{aliases}</a>;
        },
        sorter: false,
    },
    purpose: {
        title: 'Purpose',
    },
    zygosity: {
        title: 'Zygosity',
    },
    assembly: {
        title: 'Mapping assembly',
        getValue: modification => (modification.modified_site && modification.modified_site.assembly ? modification.modified_site.assembly : ''),
    },
    coordinates: {
        title: 'Coordinates',
        display: (modification) => {
            const coords = modification.modified_site;
            if (coords && coords.chromosome) {
                return <span>chr{coords.chromosome}:{coords.start}-{coords.end}</span>;
            }
            return null;
        },
        objSorter: (a, b) => {
            let sortRes; // Sorting result
            const aCoord = a.modified_site;
            const bCoord = b.modified_site;
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
        },
    },
};
