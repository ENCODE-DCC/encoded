import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import { Panel, PanelHeading, PanelBody } from '../libs/bootstrap/panel';
import { collapseIcon } from '../libs/svg-icons';
import { auditDecor } from './audit';
import { AttachmentPanel, DocumentsPanel } from './doc';
import { FetchedData, Param } from './fetched';
import * as globals from './globals';
import { ProjectBadge, Attachment } from './image';
import { RelatedItems } from './item';
import { Breadcrumbs } from './navigation';
import { singleTreatment } from './objectutils';
import { PickerActions } from './search';
import { SortTablePanel, SortTable } from './sorttable';
import StatusLabel from './statuslabel';
import { BiosampleTable, DonorTable } from './typeutils';


// Map GM techniques to a presentable string
const GM_TECHNIQUE_MAP = {
    Crispr: 'CRISPR',
    Tale: 'TALE',
};


// Display a panel of characterizations associated with a genetic modification object.
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


// Generate a <dt>/<dd> combination to render GeneticModification.epitope_tags into a <dl>. If no
// epitope_tags exist in the given genetic modification object, nothing gets rendered.
const IntroducedTags = (props) => {
    const { geneticModification } = props;

    if (geneticModification.introduced_tags && geneticModification.introduced_tags.length) {
        // Generate an array of React components, each containing one epitope_tags display from
        // the array of epitope_tags in the given genetic modification object. At least one
        // property of each epitope tag element must be present, or else an empty <li></li> will
        // get generated. Seems unlikely to have an empty epitope_tags element in the array, so
        // this currently seems like a good assumption.
        const elements = geneticModification.introduced_tags.map((tag, i) => {
            const targetName = tag.promoter_used ? globals.atIdToAccession(tag.promoter_used) : '';
            const name = tag.name ? <span>{tag.name}</span> : null;
            const location = tag.location ? <span>{name ? <span> &mdash; </span> : null}{tag.location}</span> : null;
            const promoterUsed = tag.promoter_used ? <span>{name || location ? <span> &mdash; </span> : null}<a href={tag.promoter_used} title={`View page for target ${targetName}`}>{targetName}</a></span> : null;
            return <li key={i}>{name}{location}{promoterUsed}</li>;
        });

        // Return a <div> to get rendered within a <dl> being displayed for the given genetic
        // modification.
        return (
            <div data-test="introducedtag">
                <dt>Tags</dt>
                <dd><ul className="multi-value">{elements}</ul></dd>
            </div>
        );
    }
    return null;
};

IntroducedTags.propTypes = {
    geneticModification: PropTypes.object.isRequired, // GeneticModification object being displayed
};


// Render the modification site items into a definition list.
const ModificationSiteItems = (props) => {
    const { geneticModification, itemClass } = props;

    const renderers = {
        modified_site_by_target_id: (gm) => {
            let targetName;
            let targetLink;

            if (typeof gm.modified_site_by_target_id === 'string') {
                // Non-embedded target; get its name from its @id.
                targetName = globals.atIdToAccession(gm.modified_site_by_target_id);
                targetLink = gm.modified_site_by_target_id;
            } else {
                // Embedded target; get its name from the embedded object.
                targetName = gm.modified_site_by_target_id.name;
                targetLink = gm.modified_site_by_target_id['@id'];
            }
            return (
                <div data-test="mstarget">
                    <dt>Target</dt>
                    <dd><a href={targetLink} title={`View page for target ${targetName}`}>{targetName}</a></dd>
                </div>
            );
        },
        modified_site_by_coordinates: (gm) => {
            const { assembly, chromosome, start, end } = gm.modified_site_by_coordinates;
            return (
                <div data-test="mscoords">
                    <dt>Coordinates</dt>
                    <dd>{`${assembly} chr${chromosome}:${start}-${end}`}</dd>
                </div>
            );
        },
        modified_site_by_sequence: gm => (
            <div data-test="msseq">
                <dt>Sequence</dt>
                <dd className="sequence">{gm.modified_site_by_sequence}</dd>
            </div>
        ),
        modified_site_nonspecific: gm => (
            <div data-test="msnonspec">
                <dt>Non-specific</dt>
                <dd>{gm.modified_site_nonspecific}</dd>
            </div>
        ),
    };

    const elements = ['modified_site_by_target_id', 'modified_site_by_coordinates', 'modified_site_by_sequence', 'modified_site_nonspecific'].map((siteType) => {
        if (geneticModification[siteType]) {
            return <div key={siteType}>{renderers[siteType](geneticModification)}</div>;
        }
        return null;
    });

    return (
        <dl className={itemClass}>
            {elements}
        </dl>
    );
};

ModificationSiteItems.propTypes = {
    geneticModification: PropTypes.object.isRequired, // Genetic modification object whose modification_site we're rendering here
    itemClass: PropTypes.string, // CSS class string to add to <dl>
};

ModificationSiteItems.defaultProps = {
    itemClass: '',
};


// Display a section for the modification site data from the given genetic modification object. to
// render into the GM summary panel as its own section;
const ModificationSite = (props) => {
    const { geneticModification } = props;
    const itemClass = globals.itemClass(geneticModification, 'view-detail key-value');

    return (
        <div>
            <hr />
            <h4>Modification site</h4>
            <ModificationSiteItems geneticModification={geneticModification} itemClass={itemClass} />
        </div>
    );
};

ModificationSite.propTypes = {
    geneticModification: PropTypes.object.isRequired, // GM object with modification site data to display
};


// Render data for the Modification Technique section of the GM summary panel, for the given
// GeneticModification object.
const ModificationTechnique = (props) => {
    const { geneticModification } = props;
    const itemClass = globals.itemClass(geneticModification, 'view-detail key-value');

    // Make an array of treatment text summaries within <li> elements that can get inserted
    // directly into a <ul> element.
    let treatments = [];
    if (geneticModification.treatments && geneticModification.treatments.length) {
        treatments = geneticModification.treatments.map(treatment => <li key={treatment.uuid}>{singleTreatment(treatment)}</li>);
    }

    return (
        <div>
            <hr />
            <h4>Modification technique</h4>
            <dl className={itemClass}>
                <div data-test="technique">
                    <dt>Technique</dt>
                    <dd>{geneticModification.method}</dd>
                </div>

                {treatments.length ?
                    <div data-test="treatments">
                        <dt>Treatments</dt>
                        <dd>
                            <ul className="multi-value">
                                {treatments}
                            </ul>
                        </dd>
                    </div>
                : null}

                {geneticModification.guide_rna_sequences && geneticModification.guide_rna_sequences.length ?
                    <div data-test="guiderna">
                        <dt>Guide RNA</dt>
                        <dd>
                            <ul className="multi-value">
                                {geneticModification.guide_rna_sequences.map((seq, i) => <li key={i}>{seq}</li>)}
                            </ul>
                        </dd>
                    </div>
                : null}

                {geneticModification.RVD_sequence_pairs && geneticModification.RVD_sequence_pairs.length ?
                    <div data-test="rvdseq">
                        <dt>RVD sequence pairs</dt>
                        <dd>
                            <ul className="multi-value">
                                {geneticModification.RVD_sequence_pairs.map((pair, i) => (
                                    <li key={i}>{pair.left_RVD_sequence} : {pair.right_RVD_sequence}</li>
                                ))}
                            </ul>
                        </dd>
                    </div>
                : null}

                {geneticModification.reagents && geneticModification.reagents.length ?
                    <div data-test="reagent">
                        <dt>Reagents</dt>
                        <dd>
                            <ul className="multi-value">
                                {geneticModification.reagents.map((reagent, i) => {
                                    const reagentId = <span>{globals.atIdToAccession(reagent.source)}:{reagent.identifier}</span>;
                                    if (reagent.url) {
                                        return <a key={i} href={reagent.url}>{reagentId}</a>;
                                    }
                                    return <span key={i}>{reagentId}</span>;
                                })}
                            </ul>
                        </dd>
                    </div>
                : null}
            </dl>
        </div>
    );
};

ModificationTechnique.propTypes = {
    geneticModification: PropTypes.object.isRequired, // GM object being rendered
};


// Rendering component for the attribution pane of the summary panel. This gets called as a result
// of a successful GET request for the GM's award and lab objects which are no longer embedded in
// the GM object.
const AttributionRenderer = (props) => {
    const { geneticModification, award } = props;

    return (
        <div>
            <div className="flexcol-heading experiment-heading">
                <h4>Attribution</h4>
                <ProjectBadge award={award} addClasses="badge-heading" />
            </div>
            <dl className="key-value">
                <div data-test="lab">
                    <dt>Lab</dt>
                    <dd>{geneticModification.lab.title}</dd>
                </div>

                {award.pi && award.pi.lab ?
                    <div data-test="awardpi">
                        <dt>Award PI</dt>
                        <dd>{award.pi.lab.title}</dd>
                    </div>
                : null}

                <div data-test="project">
                    <dt>Project</dt>
                    <dd>{award.project}</dd>
                </div>

                {geneticModification.aliases && geneticModification.aliases.length ?
                    <div data-test="aliases">
                        <dt>Aliases</dt>
                        <dd>{geneticModification.aliases.join(', ')}</dd>
                    </div>
                : null}
            </dl>
        </div>
    );
};

AttributionRenderer.propTypes = {
    geneticModification: PropTypes.object.isRequired, // GeneticModification object being displayed
    award: PropTypes.object, // Award object retreived from an individual GET request; don't make isRequired because React's static analysizer will ding it
};

AttributionRenderer.defaultProps = {
    award: null, // Actually required, but React can't tell this property's coming from a GET request, so treat as optional
};


// Display the contents of the attribution panel (currently the right-hand side of the summary
// panel) for the given genetic modification object. Because the award and lab informatino isn't
// embedded in the GM object, we have to retrieve it with a couple GET requests here, and have
// <AttributionRenderer> actually render the panel contents after the GET request completes.
const Attribution = (props) => {
    const { geneticModification } = props;

    return (
        <FetchedData>
            <Param name="award" url={geneticModification.award} />
            <AttributionRenderer geneticModification={geneticModification} />
        </FetchedData>
    );
};

Attribution.propTypes = {
    geneticModification: PropTypes.object.isRequired, // Genetic modificastion object for which we're getting the attribution information
};


const DocumentsRenderer = (props) => {
    const modDocs = props.modDocs ? props.modDocs['@graph'] : [];
    const charDocs = props.charDocs ? props.charDocs['@graph'] : [];

    return (
        <DocumentsPanel
            documentSpecs={[
                { label: 'Modification', documents: modDocs },
                { label: 'Characterization', documents: charDocs },
            ]}
        />
    );
};

DocumentsRenderer.propTypes = {
    modDocs: PropTypes.object, // GM document search results
    charDocs: PropTypes.object, // GM characterization document search results
};

DocumentsRenderer.defaultProps = {
    modDocs: null,
    charDocs: null,
};


// Render the entire GeneticModification page. This is called by the back end as a result of an
// attempt to render an object with an @type of GeneticModification.
export class GeneticModificationComponent extends React.Component {
    render() {
        const context = this.props.context;
        const itemClass = globals.itemClass(context, 'view-detail key-value');

        // Configure breadcrumbs for the page.
        const crumbs = [
            { id: 'Genetic Modifications' },
            { id: context.target && context.target.label, query: `target.label=${context.target && context.target.label}`, tip: context.target && context.target.label },
            { id: context.modification_type, query: `modification_type=${context.modification_type}`, tip: context.modification_type },
        ];

        // Collect and combine documents, including from genetic modification characterizations.
        let modDocsQuery;
        let charDocsQuery;
        if (context.documents && context.documents.length) {
            // Take the array of document @ids and combine them into one query string for a search
            // of the form "&@id=/documents/{uuid}&@id=/documents/{uuid}..."
            modDocsQuery = context.documents.reduce((acc, document) => `${acc}&@id=${document}`, '');
        }
        if (context.characterizations && context.characterizations.length) {
            let charDocs = [];
            context.characterizations.forEach((characterization) => {
                if (characterization.documents && characterization.documents.length) {
                    charDocs = charDocs.concat(characterization.documents);
                }
            });

            // Take the array of characgterization document @ids and combine them into one query
            // string for a search of the form "&@id=/documents/{uuid}&@id=/documents/{uuid}..."
            charDocsQuery = charDocs.reduce((acc, document) => `${acc}&@id=${document}`, '');
        }

        return (
            <div className={globals.itemClass(context, 'view-item')}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs root="/search/?type=GeneticModification" crumbs={crumbs} />
                        <h2>{context.accession}</h2>
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

                                    <div data-test="type">
                                        <dt>Type</dt>
                                        <dd>
                                            <ul>
                                                <li>{context.category}</li>
                                                {context.introduced_sequence ? <li className="sequence">{context.introduced_sequence}</li> : null}
                                            </ul>
                                        </dd>
                                    </div>

                                    {context.zygosity ?
                                        <div data-test="zygosity">
                                            <dt>Zygosity</dt>
                                            <dd>{context.zygosity}</dd>
                                        </div>
                                    : null}

                                    <IntroducedTags geneticModification={context} />

                                    <div data-test="purpose">
                                        <dt>Purpose</dt>
                                        <dd>{context.purpose}</dd>
                                    </div>
                                </dl>

                                <ModificationSite geneticModification={context} />

                                <ModificationTechnique geneticModification={context} />
                            </div>

                            <div className="flexcol-sm-6">
                                <Attribution geneticModification={context} />
                            </div>
                        </div>
                    </PanelBody>
                </Panel>

                {context.characterizations && context.characterizations.length ?
                    <GeneticModificationCharacterizations characterizations={context.characterizations} />
                : null}

                {modDocsQuery || charDocsQuery ?
                    <FetchedData>
                        {modDocsQuery ? <Param name="modDocs" url={`/search/?type=Document${modDocsQuery}`} /> : null}
                        {charDocsQuery ? <Param name="charDocs" url={`/search/?type=Document${charDocsQuery}`} /> : null}
                        <DocumentsRenderer />
                    </FetchedData>
                : null}

                <RelatedItems
                    title="Donors using this genetic modification"
                    url={`/search/?type=Donor&genetic_modifications.uuid=${context.uuid}`}
                    Component={DonorTable}
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

globals.contentViews.register(GeneticModification, 'GeneticModification');


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
globals.documentViews.caption.register(GMAttachmentCaption, 'GeneticModificationCharacterization');

// Register document preview rendering components
globals.documentViews.preview.register(GMAttachmentPreview, 'GeneticModificationCharacterization');


class ListingComponent extends React.Component {
    render() {
        const result = this.props.context;

        return (
            <li>
                <div className="clearfix">
                    <PickerActions {...this.props} />
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Genetic modifications</p>
                        <p className="type">{` ${result.accession}`}</p>
                        <p className="type meta-status">{` ${result.status}`}</p>
                        {this.props.auditIndicators(result.audit, result['@id'], { session: this.context.session, search: true })}
                    </div>
                    <div className="accession"><a href={result['@id']}>{result.category} &mdash; {result.purpose} &mdash; {result.method}</a></div>
                    <div className="data-row">
                        {result.modified_site_by_target_id ? <div><strong>Target: </strong>{result.modified_site_by_target_id.name}</div> : null}
                        {result.lab ? <div><strong>Lab: </strong>{result.lab.title}</div> : null}
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

globals.listingViews.register(Listing, 'GeneticModification');


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
                        <SortTable list={gms} columns={GeneticModificationGroup.columns} />
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


export const GeneticModificationSummary = (props) => {
    const { geneticModifications } = props;

    return (
        <SortTablePanel title="Genetic modifications">
            <SortTable list={geneticModifications} columns={GeneticModificationSummary.columns} />
        </SortTablePanel>
    );
};

GeneticModificationSummary.propTypes = {
    geneticModifications: PropTypes.array, // Array of genetic modifications to display
};

GeneticModificationSummary.columns = {
    accession: {
        title: 'Accession',
        display: item => <a href={item['@id']}>{item.accession}</a>,
    },
    category: { title: 'Category' },
    method: { title: 'Method' },
    site: {
        title: 'Site',
        display: item => <ModificationSiteItems geneticModification={item} itemClass={'gm-table-modification-site'} />,
    },
};
