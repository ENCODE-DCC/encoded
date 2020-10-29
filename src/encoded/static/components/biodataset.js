import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import { Panel, PanelBody } from '../libs/bootstrap/panel';
import DropdownButton from '../libs/bootstrap/button';
import { DropdownMenu } from '../libs/bootstrap/dropdown-menu';
import { CartToggle, CartAddAllElements } from './cart';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import { DbxrefList } from './dbxref';
import { FetchedItems } from './fetched';
import { auditDecor } from './audit';
import Status from './status';
import pubReferenceList from './reference';
import { donorDiversity, publicDataset, AlternateAccession, DisplayAsJson, InternalTags } from './objectutils';
import { softwareVersionList } from './software';
import { SortTablePanel, SortTable } from './sorttable';
import { ProjectBadge } from './image';
import { DocumentsPanelReq } from './doc';
import { FileGallery, DatasetFiles } from './filegallery';
import { AwardRef, ReplacementAccessions, ControllingExperiments } from './typeutils';


// Break the given camel-cased name into space-separated words just before the interior capital letters.
function breakSetName(name) {
    return name.replace(/(\S)([A-Z])/g, '$1 $2');
}
// Display Annotation page, a subtype of Dataset.
/* eslint-disable react/prefer-stateless-function */
class BioreferenceComponent extends React.Component {
    render() {
        const context = this.props.context;
        console.log(this.props.context);
        const itemClass = globals.itemClass(context, 'view-item');
        const adminUser = !!(this.context.session_properties && this.context.session_properties.admin);
        const experimentsUrl = `/search/?type=Bioexperiment&possible_controls.accession=${context.accession}`;

        // Build up array of documents attached to this dataset
        const datasetDocuments = (context.documents && context.documents.length) ? context.documents : [];

        // Set up the breadcrumbs
        const datasetType = context['@type'][1];
        const filesetType = context['@type'][0];
        const crumbs = [
            { id: 'Biodatasets' },
            { id: datasetType, uri: `/search/?type=${datasetType}`, wholeTip: `Search for ${datasetType}` },
            { id: breakSetName(filesetType), uri: `/search/?type=${filesetType}`, wholeTip: `Search for ${filesetType}` },
        ];

        const crumbsReleased = (context.status === 'released');

        // Get a list of reference links, if any
        const references = pubReferenceList(context.references);

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs crumbs={crumbs} crumbsReleased={crumbsReleased} />
                        <h2>Summary for reference file set {context.accession}</h2>
                        <div className="replacement-accessions">
                            <AlternateAccession altAcc={context.alternate_accessions} />
                        </div>
                        {this.props.auditIndicators(context.audit, 'reference-audit', { session: this.context.session })}
                        <DisplayAsJson />
                    </div>
                </header>
                {this.props.auditDetail(context.audit, 'reference-audit', { session: this.context.session, except: context['@id'] })}
                <Panel addClasses="data-display">
                    <PanelBody addClasses="panel-body-with-header">
                        <div className="flexrow">
                            <div className="flexcol-sm-6">
                                <div className="flexcol-heading experiment-heading"><h4>Summary</h4></div>
                                <dl className="key-value">
                                    <div data-test="status">
                                        <dt>Status</dt>
                                        <dd><Status item={context} inline /></dd>
                                    </div>

                                    <div data-test="accession">
                                        <dt>Accession</dt>
                                        <dd>{context.accession}</dd>
                                    </div>

                                    {context.description ?
                                        <div data-test="description">
                                            <dt>Description</dt>
                                            <dd>{context.description}</dd>
                                        </div>
                                        : null}

                                    {context.reference_type ?
                                        <div data-test="type">
                                            <dt>Reference type</dt>
                                            <dd>{context.reference_type}</dd>
                                        </div>
                                        : null}

                                    {/* {context.biospeimen_summary[0].species ?
                                        <div data-test="organism">
                                            <dt>Organism</dt>
                                            <dd>{context.biospecimen_summary[0].species}</dd>
                                        </div>
                                    : null} */}

                                    {/* {context.software_used && context.software_used.length ?
                                        <div data-test="softwareused">
                                            <dt>Software used</dt>
                                            <dd>{softwareVersionList(context.software_used)}</dd>
                                        </div>
                                    : null} */}
                                </dl>
                            </div>

                            <div className="flexcol-sm-6">
                                <div className="flexcol-heading experiment-heading">
                                    <h4>Attribution</h4>
                                    <ProjectBadge award={context.award} addClasses="badge-heading" />
                                </div>
                                <dl className="key-value">
                                    {context.lab ?
                                        <div data-test="lab">
                                            <dt>Lab</dt>
                                            <dd>{context.lab.title}</dd>
                                        </div>
                                        : null}

                                    <AwardRef context={context} adminUser={adminUser} />

                                    {context.aliases.length ?
                                        <div data-test="aliases">
                                            <dt>Aliases</dt>
                                            <dd><DbxrefList context={context} dbxrefs={context.aliases} /></dd>
                                        </div>
                                        : null}

                                    <div data-test="externalresources">
                                        <dt>External resources</dt>
                                        <dd>
                                            {context.dbxrefs && context.dbxrefs.length ?
                                                <DbxrefList context={context} dbxrefs={context.dbxrefs} />
                                                : <em>None submitted</em>}
                                        </dd>
                                    </div>

                                    {references ?
                                        <div data-test="references">
                                            <dt>Publications</dt>
                                            <dd>{references}</dd>
                                        </div>
                                        : null}

                                    {context.internal_tags && context.internal_tags.length > 0 ?
                                        <div className="tag-badges" data-test="tags">
                                            <dt>Tags</dt>
                                            <dd><InternalTags internalTags={context.internal_tags} objectType={context['@type'][0]} /></dd>
                                        </div>
                                        : null}
                                </dl>
                            </div>
                        </div>
                    </PanelBody>
                </Panel>

                {/* Display the file widget with the facet, graph, and tables */}
                <FileGallery context={context} encodevers={globals.encodeVersion(context)} hideGraph altFilterDefault />

                <FetchedItems {...this.props} url={experimentsUrl} Component={ControllingExperiments} />

                {/* <DocumentsPanelReq documents={datasetDocuments} /> */}
            </div>
        );
    }
}
/* eslint-enable react/prefer-stateless-function */

BioreferenceComponent.propTypes = {
    context: PropTypes.object.isRequired, // Reference object to display
    auditIndicators: PropTypes.func.isRequired, // From audit decorator
    auditDetail: PropTypes.func.isRequired, // From audit decorator
};

BioreferenceComponent.contextTypes = {
    session: PropTypes.object, // Login session information
    session_properties: PropTypes.object,
};

const Bioreference = auditDecor(BioreferenceComponent);

globals.contentViews.register(Bioreference, 'Bioreference');


// Display Annotation page, a subtype of Dataset.
/* eslint-disable react/prefer-stateless-function */
class BioprojectComponent extends React.Component {
    render() {
        const context = this.props.context;
        const itemClass = globals.itemClass(context, 'view-item');
        const adminUser = !!(this.context.session_properties && this.context.session_properties.admin);
        const experimentsUrl = `/search/?type=Bioexperiment&possible_controls.accession=${context.accession}`;

        // Build up array of documents attached to this dataset
        const datasetDocuments = (context.documents && context.documents.length) ? context.documents : [];

        // Collect organisms
        // const organisms = (context.bispecimen_summary[0].species && context.biospecimen_summary[0].species.length) ? _.uniq(context.biospecimen_summary[0].species) : [];

        // Set up the breadcrumbs
        const datasetType = context['@type'][1];
        const filesetType = context['@type'][0];
        const crumbs = [
            { id: 'Biodatasets' },
            { id: datasetType, uri: `/search/?type=${datasetType}`, wholeTip: `Search for ${datasetType}` },
            { id: breakSetName(filesetType), uri: `/search/?type=${filesetType}`, wholeTip: `Search for ${filesetType}` },
        ];

        const crumbsReleased = (context.status === 'released');

        // Get a list of reference links
        const references = pubReferenceList(context.references);

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs crumbs={crumbs} crumbsReleased={crumbsReleased} />
                        <h2>Summary for project file set {context.accession}</h2>
                        {/* <div className="replacement-accessions">
                            <AlternateAccession altAcc={context.alternate_accessions} />
                        </div> */}
                        {this.props.auditIndicators(context.audit, 'project-audit', { session: this.context.session })}
                        <DisplayAsJson />
                    </div>
                </header>
                {this.props.auditDetail(context.audit, 'project-audit', { session: this.context.session, except: context['@id'] })}
                <Panel addClasses="data-display">
                    <PanelBody addClasses="panel-body-with-header">
                        <div className="flexrow">
                            <div className="flexcol-sm-6">
                                <div className="flexcol-heading experiment-heading"><h4>Summary</h4></div>
                                <dl className="key-value">
                                    <div data-test="status">
                                        <dt>Status</dt>
                                        <dd><Status item={context} inline /></dd>
                                    </div>

                                    {context.assay_term_name && context.assay_term_name.length ?
                                        <div data-test="assaytermname">
                                            <dt>Assay(s)</dt>
                                            <dd>{context.assay_term_name}</dd>
                                        </div>
                                        : null}

                                    <div data-test="accession">
                                        <dt>Accession</dt>
                                        <dd>{context.accession}</dd>
                                    </div>

                                    {context.description ?
                                        <div data-test="description">
                                            <dt>Description</dt>
                                            <dd>{context.description}</dd>
                                        </div>
                                        : null}

                                    {context.project_type ?
                                        <div data-test="type">
                                            <dt>Project type</dt>
                                            <dd className="sentence-case">{context.project_type}</dd>
                                        </div>
                                        : null}

                                    {/* {context.biospecimen_summary[0].tissue_type ?
                                        <div data-test="biosampletype">
                                            <dt>Biosample type</dt>
                                            <dd>{(context.biospecimen_summary[0].tissue_type)}</dd>
                                            {/* need to test */}
                                    {/* </div> */}
                                    {/* : null} */}

                                    {context.assay_term_name ?
                                        <div data-test="assay_term_name">
                                            <dt>Biospecimen term name </dt>
                                            <dd>{_.uniq(context.assay_term_name)}</dd>
                                        </div>
                                        : null}

                                    {/* {organisms.length ?
                                        <div data-test="organism">
                                            <dt>Organism</dt>
                                            <dd>{organisms.join(', ')}</dd>
                                        </div>
                                    : null} */}


                                </dl>
                            </div>

                            <div className="flexcol-sm-6">
                                <div className="flexcol-heading experiment-heading">
                                    <h4>Attribution</h4>
                                    <ProjectBadge award={context.award} addClasses="badge-heading" />
                                </div>
                                <dl className="key-value">
                                    {context.lab ?
                                        <div data-test="lab">
                                            <dt>Lab</dt>
                                            <dd>{context.lab.title}</dd>
                                        </div>
                                        : null}

                                    <AwardRef context={context} adminUser={adminUser} />

                                    {context.aliases.length ?
                                        <div data-test="aliases">
                                            <dt>Aliases</dt>
                                            <dd><DbxrefList context={context} dbxrefs={context.aliases} /></dd>
                                        </div>
                                        : null}

                                    <div data-test="externalresources">
                                        <dt>External resources</dt>
                                        <dd>
                                            {context.dbxrefs && context.dbxrefs.length ?
                                                <DbxrefList context={context} dbxrefs={context.dbxrefs} />
                                                : <em>None submitted</em>}
                                        </dd>
                                    </div>

                                    {references ?
                                        <div data-test="references">
                                            <dt>Publications</dt>
                                            <dd>{references}</dd>
                                        </div>
                                        : null}

                                </dl>
                            </div>
                        </div>
                    </PanelBody>
                </Panel>

                {/* Display the file widget with the facet, graph, and tables */}
                <FileGallery context={context} encodevers={globals.encodeVersion(context)} hideGraph />

                <FetchedItems {...this.props} url={experimentsUrl} Component={ControllingExperiments} />

                {/* <DocumentsPanelReq documents={datasetDocuments} /> */}
            </div>
        );
    }
}
/* eslint-enable react/prefer-stateless-function */

BioprojectComponent.propTypes = {
    context: PropTypes.object.isRequired, // Project object to display
    auditIndicators: PropTypes.func.isRequired, // From audit decorator
    auditDetail: PropTypes.func.isRequired, // From audit decorator
};

BioprojectComponent.contextTypes = {
    session: PropTypes.object, // Login session information
    session_properties: PropTypes.object,
};

const Bioproject = auditDecor(BioprojectComponent);

globals.contentViews.register(Bioproject, 'Bioproject');





export const FilePanelHeader = (props) => {
    const context = props.context;

    return (
        <div>
            {context.visualize && context.status === 'released' ?
                <span className="pull-right">
                    <DropdownButton title="Visualize Data" label="filepaneheader">
                        <DropdownMenu>
                            {Object.keys(context.visualize).sort().map(assembly =>
                                Object.keys(context.visualize[assembly]).sort().map(browser =>
                                    <a key={[assembly, '_', browser].join()} data-bypass="true" target="_blank" rel="noopener noreferrer" href={context.visualize[assembly][browser]}>
                                        {assembly} {browser}
                                    </a>
                                )
                            )}
                        </DropdownMenu>
                    </DropdownButton>
                </span>
                : null}
            <h4>File summary</h4>
        </div>
    );
};

FilePanelHeader.propTypes = {
    context: PropTypes.object.isRequired, // Object being displayed
};


function displayPossibleControls(item, adminUser) {
    if (item.possible_controls && item.possible_controls.length) {
        return (
            <span>
                {item.possible_controls.map((control, i) =>
                    <span key={control.uuid}>
                        {i > 0 ? <span>, </span> : null}
                        {adminUser || publicDataset(control) ?
                            <a href={control['@id']}>{control.accession}</a>
                            :
                            <span>{control.accession}</span>
                        }
                    </span>
                )}
            </span>
        );
    }
    return null;
}


const basicTableColumns = {
    accession: {
        title: 'Accession',
        display: (bioexperiment, meta) =>
            <span>
                {meta.adminUser || publicDataset(bioexperiment) ?
                    <a href={bioexperiment['@id']} title={`View page for experiment ${bioexperiment.accession}`}>{bioexperiment.accession}</a>
                    :
                    <span>{bioexperiment.accession}</span>
                }
            </span>,
    },

    assay_term_name: {
        title: 'Assay',
    },

    // target: {
    //     title: 'Target',
    //     getValue: experiment => (experiment.target ? experiment.target.label : null),
    // },

    description: {
        title: 'Description',
    },

    lab: {
        title: 'Lab',
        getValue: experiment => (experiment.lab ? experiment.lab.title : null),

    },
    status: {
        title: 'Status',
        display: experiment => <Status item={experiment} badgeSize="small" />,
    },
    cart: {
        title: 'Cart',
        display: experiment => <CartToggle element={experiment} />,
        sorter: false,
    },
};



// Map series @id to title and table columns
const seriesComponents = {

    BioexperimentSeries: { title: 'bioexperiment series', table: basicTableColumns },

    MatchedSet: { title: 'matched set series', table: basicTableColumns },
    // OrganismDevelopmentSeries: { title: 'organism development series', table: organismDevelopmentSeriesTableColumns },
    ReferenceEpigenome: { title: 'reference epigenome series', table: basicTableColumns },
};

/* eslint-disable react/prefer-stateless-function */
export class BioseriesComponent extends React.Component {
    render() {
        const context = this.props.context;
        const itemClass = globals.itemClass(context, 'view-item');
        const adminUser = !!(this.context.session_properties && this.context.session_properties.admin);
        const experimentsUrl = `/search/?type=Bioexperiment&possible_controls.accession=${context.accession}`;
        let experiments = {};
        context.files.forEach((file) => {
            const bioexperiment = file.bioreplicate && file.bioreplicate.bioexperiment;
            if (bioexperiment) {
                experiments[bioexperiment['@id']] = bioexperiment;
            }
        });
        experiments = _.values(experiments);

        // Build up array of documents attached to this dataset
        const datasetDocuments = (context.documents && context.documents.length) ? context.documents : [];
        console.log("datasetDoc", datasetDocuments);
        // Set up the breadcrumbs
        const datasetType = context['@type'][1];
        const seriesType = context['@type'][0];
        const crumbs = [
            { id: 'Biodatasets' },
            { id: datasetType, uri: `/search/?type=${datasetType}`, wholeTip: `Search for ${datasetType}` },
            { id: breakSetName(seriesType), uri: `/search/?type=${seriesType}`, wholeTip: `Search for ${seriesType}` },
        ];

        const crumbsReleased = (context.status === 'released');

        // Get a list of reference links, if any
        const references = pubReferenceList(context.references);

        // Make the series title
        const seriesComponent = seriesComponents[seriesType];
        const seriesTitle = seriesComponent ? seriesComponent.title : 'series';

        // Calculate the biosample summary
        // let speciesRender = null;
        // if (context.organism && context.organism.length) {
        //     const speciesList = _.uniq(context.organism.map(organism => organism.scientific_name));
        //     speciesRender = (
        //         <span>
        //             {speciesList.map((species, i) =>
        //                 <span key={i}>
        //                     {i > 0 ? <span> and </span> : null}
        //                     <i>{species}</i>
        //                 </span>
        //             )}
        //         </span>
        //     );
        // }
        const terms = (context.assay_term_name) ? _.uniq(context.assay_term_name) : [];

        // Calculate the donor diversity.
        const diversity = donorDiversity(context);

        // Filter out any files we shouldn't see.
        const experimentList = context.related_datasets.filter(biodataset => biodataset.status !== 'revoked' && biodataset.status !== 'replaced' && biodataset.status !== 'deleted');

        // If we display a table of related experiments, have to render the control to add all of
        // them to the current cart.
        let addAllToCartControl;
        if (experimentList.length > 0) {
            addAllToCartControl = (
                <div className="experiment-table__header">
                    <h4 className="experiment-table__title">{`Bioexperiments in ${seriesTitle} ${context.accession}`}</h4>
                    <CartAddAllElements elements={experimentList} />
                </div>
            );
        }

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs crumbs={crumbs} crumbsReleased={crumbsReleased} />
                        <h2>Summary for {seriesTitle} {context.accession}</h2>
                        <ReplacementAccessions context={context} />
                        {this.props.auditIndicators(context.audit, 'series-audit', { session: this.context.session })}
                        <DisplayAsJson />
                    </div>
                </header>
                {this.props.auditDetail(context.audit, 'series-audit', { session: this.context.session, except: context['@id'] })}
                <Panel addClasses="data-display">
                    <PanelBody addClasses="panel-body-with-header">
                        <div className="flexrow">
                            <div className="flexcol-sm-6">
                                <div className="flexcol-heading experiment-heading"><h4>Summary</h4></div>
                                <dl className="key-value">
                                    <div data-test="status">
                                        <dt>Status</dt>
                                        <dd><Status item={context} inline /></dd>
                                    </div>

                                    {context.description ?
                                        <div data-test="description">
                                            <dt>Description</dt>
                                            <dd>{context.description}</dd>
                                        </div>
                                        : null}

                                    <div data-test="donordiversity">
                                        <dt>Donor diversity</dt>
                                        <dd>{diversity}</dd>
                                    </div>

                                    {context.assay_term_name ?
                                        <div data-test="description">
                                            <dt>Assay</dt>
                                            <dd>{context.assay_term_name}</dd>
                                        </div>
                                        : null}

                                    {/* {terms.length || speciesRender ?
                                        <div data-test="biosamplesummary">
                                            <dt>Biosample summary</dt>
                                            <dd>
                                                {terms.length ? <span>{terms.join(' and ')} </span> : null}
                                                {speciesRender ? <span>({speciesRender})</span> : null}
                                            </dd>
                                        </div>
                                    : null} */}
                                </dl>
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

                                    <AwardRef context={context} adminUser={adminUser} />

                                    <div data-test="project">
                                        <dt>Project</dt>
                                        <dd>{context.award.project}</dd>
                                    </div>

                                    {context.aliases.length ?
                                        <div data-test="aliases">
                                            <dt>Aliases</dt>
                                            <dd>{context.aliases.join(', ')}</dd>
                                        </div>
                                        : null}

                                    <div data-test="externalresources">
                                        <dt>External resources</dt>
                                        <dd>
                                            {context.dbxrefs && context.dbxrefs.length ?
                                                <DbxrefList context={context} dbxrefs={context.dbxrefs} />
                                                : <em>None submitted</em>}
                                        </dd>
                                    </div>

                                    {references ?
                                        <div data-test="references">
                                            <dt>References</dt>
                                            <dd>{references}</dd>
                                        </div>
                                        : null}

                                    {context.submitter_comment ?
                                        <div data-test="submittercomment">
                                            <dt>Submitter comment</dt>
                                            <dd>{context.submitter_comment}</dd>
                                        </div>
                                        : null}

                                    {context.internal_tags && context.internal_tags.length > 0 ?
                                        <div className="tag-badges" data-test="tags">
                                            <dt>Tags</dt>
                                            <dd><InternalTags internalTags={context.internal_tags} objectType={context['@type'][0]} /></dd>
                                        </div>
                                        : null}
                                </dl>
                            </div>
                        </div>
                    </PanelBody>
                </Panel>

                {addAllToCartControl ?
                    <div>
                        <SortTablePanel header={addAllToCartControl}>
                            <SortTable
                                list={experimentList}
                                columns={seriesComponent.table}
                                meta={{ adminUser }}
                            />
                        </SortTablePanel>
                    </div>
                    : null}

                {/* Display list of released and unreleased files */}
                <FetchedItems
                    {...this.props}
                    url={`/search/?limit=all&type=Biofile&biodataset=${context['@id']}`}
                    Component={DatasetFiles}
                    filePanelHeader={<FilePanelHeader context={context} />}
                    encodevers={globals.encodeVersion(context)}
                    session={this.context.session}
                />

                <FetchedItems {...this.props} url={experimentsUrl} Component={ControllingExperiments} />

                {/* <DocumentsPanelReq documents={datasetDocuments} /> */}
            </div>
        );
    }
}
/* eslint-enable react/prefer-stateless-function */

BioseriesComponent.propTypes = {
    context: PropTypes.object.isRequired, // Series object to display
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

BioseriesComponent.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
};

const Bioseries = auditDecor(BioseriesComponent);

globals.contentViews.register(Bioseries, 'Bioseries');
