import React from 'react';
import PropTypes from 'prop-types';
import Cache from '../libs/cache';
import Pager from '../libs/ui/pager';
import { Panel, PanelHeading, PanelBody } from '../libs/ui/panel';
import { CartAddAllElements, CartToggle } from './cart';
import { auditDecor } from './audit';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import { DbxrefList } from './dbxref';
import { PickerActions, resultItemClass } from './search';
import Status from './status';
import { ItemAccessories, requestObjects } from './objectutils';
import { SortTablePanel, SortTable } from './sorttable';


const datasetsColumns = {
    accession: {
        display: dataset => <a href={dataset['@id']}>{dataset.accession}</a>,
        title: 'Accession',
        sorter: false,
    },
    type: {
        getValue: dataset => (dataset['@type'] || [''])[0], // only the first matters
        title: 'Type',
        sorter: false,
    },
    target: {
        getValue: dataset => (dataset.target ? dataset.target.label : ''),
        title: 'Target',
        sorter: false,
    },
    assay_term_name: {
        getValue: (dataset) => {
            // assay_term_name can be a string or an array
            if (typeof (dataset.assay_term_name) === 'string') {
                return dataset.assay_term_name;
            }
            return (dataset.assay_term_name || []).join(', ');
        },
        title: 'Assay',
        sorter: false,
    },
    description: {
        title: 'Description',
        sorter: false,
    },
    lab: {
        getValue: dataset => (dataset.lab ? dataset.lab.title : ''),
        title: 'Lab',
        sorter: false,
    },
    biosample_summary: {
        title: 'Biosample Summary',
        sorter: false,
    },
    status: {
        display: dataset => <Status item={dataset.status} badgeSize="small" inline />,
        title: 'Status',
        sorter: false,
    },
    cart: {
        title: 'Cart',
        display: dataset => <CartToggle element={dataset} />,
        sorter: false,
    },
};


const publicationDataColumns = {
    accession: {
        display: publicationData => <a href={publicationData['@id']}>{publicationData.accession}</a>,
        title: 'Accession',
        sorter: false,
    },
    fileCount: {
        getValue: publicationData => (publicationData.files ? publicationData.files.length : 0),
        title: 'Number of files',
        sorter: false,
    },
    description: {
        display: publicationData => publicationData.description || <i>No description</i>,
        title: 'Description',
        sorter: false,
    },
    status: {
        display: publicationData => <Status item={publicationData} badgeSize="small" inline />,
        title: 'Status',
        sorter: false,
    },
};


/**
 * Displays the header that shows the pager for the datasets.
 */
const DatasetTableHeader = ({ title, elements, currentPage, totalPageCount, updateCurrentPage }) => (
    <div className="header-paged-sorttable">
        <h4>{title}</h4>
        <div className="header-paged-sorttable__controls">
            <CartAddAllElements elements={elements} />
            {totalPageCount > 1 ? <Pager total={totalPageCount} current={currentPage} updateCurrentPage={updateCurrentPage} /> : null}
        </div>
    </div>
);

DatasetTableHeader.propTypes = {
    /** Title of table */
    title: PropTypes.string.isRequired,
    /** All element @ids to display in table, not just the current visible page's items */
    elements: PropTypes.array.isRequired,
    /** Current displayed page number, 0 based */
    currentPage: PropTypes.number.isRequired,
    /** Total number of pages */
    totalPageCount: PropTypes.number.isRequired,
    /** Called with the new page number the user selected */
    updateCurrentPage: PropTypes.func.isRequired,
};


/**
 * Renders a table of datasets included in this publication. The method to lazy initialize the cache
 * comes from Dan Abramov https://github.com/facebook/react/issues/14490#issuecomment-454973512
 */
const PAGE_DATASET_COUNT = 25;
const DatasetTable = ({ datasets }) => {
    // Page number of currently displayed page of datasets.
    const [currentPage, setCurrentPage] = React.useState(0);
    // Dataset objects displayed on the currently displayed page.
    const [visibleDatasets, setVisibleDatasets] = React.useState([]);
    // Caches past-viewed pages of datasets.
    const pageCache = React.useRef(null);

    // Retrieve or create the dataset page cache.
    // @return {object} dataset page cache
    const getPageCache = () => {
        if (pageCache.current) {
            return pageCache.current;
        }
        pageCache.current = new Cache();
        return pageCache.current;
    };

    // Called when the user clicks the pager to go to a new page, so we know the currently
    // requested page.
    // @param {number} New current page number of datasets to display
    const updateCurrentPage = React.useCallback((newPage) => {
        setCurrentPage(newPage);
    }, []);

    // Calculate the total number of pages based on the total number of datasets and the number of
    // datasets per page.
    const totalPageCount = React.useMemo(() => Math.floor(datasets.length / PAGE_DATASET_COUNT) + (datasets.length % PAGE_DATASET_COUNT !== 0 ? 1 : 0), [datasets]);

    React.useEffect(() => {
        const cachedDatasets = getPageCache().read(currentPage);
        if (cachedDatasets) {
            // Page found in the cache; just switch in the cached datasets instead of doing a
            // request.
            setVisibleDatasets(cachedDatasets);
        } else {
            // Page not found in the cache. Request the datasets for the currently displayed page.
            const pageStartIndex = currentPage * PAGE_DATASET_COUNT;
            const visibleDatasetIds = datasets.slice(pageStartIndex, pageStartIndex + PAGE_DATASET_COUNT);
            requestObjects(visibleDatasetIds, '/search/?type=Dataset&limit=all&status!=deleted&status!=revoked&status!=replaced').then((requestedDatasets) => {
                setVisibleDatasets(requestedDatasets);
                getPageCache().write(currentPage, requestedDatasets);
            });
        }
    }, [datasets, currentPage]);

    return (
        <React.Fragment>
            {visibleDatasets.length > 0 ?
                <SortTablePanel
                    header={<DatasetTableHeader title="Datasets" elements={datasets} currentPage={currentPage} totalPageCount={totalPageCount} updateCurrentPage={updateCurrentPage} />}
                    subheader={<div className="table-paged__count">{`${datasets.length} dataset${datasets.length === 1 ? '' : 's'}`}</div>}
                    css="table-paged"
                >
                    <SortTable list={visibleDatasets} columns={datasetsColumns} />
                </SortTablePanel>
            : null}
        </React.Fragment>
    );
};

DatasetTable.propTypes = {
    /** Array of dataset @ids to display */
    datasets: PropTypes.array.isRequired,
};


/**
 * Renders a table of PublicationData file sets included in this publication.
 */
const PublicationDataTable = ({ publicationDataIds }) => {
    const [publicationData, setPublicationData] = React.useState([]);

    React.useEffect(() => {
        requestObjects(publicationDataIds, '/search/?type=PublicationData&limit=all&status!=deleted&status!=revoked&status!=replaced&field=accession&field=files&field=description&field=status').then((requestedPublicationData) => {
            setPublicationData(requestedPublicationData);
        });
    }, [publicationDataIds]);

    return (
        <React.Fragment>
            {publicationData.length > 0 ?
                <SortTablePanel
                    title="File sets"
                    subheader={<div className="table-paged__count">{`${publicationDataIds.length} file set${publicationDataIds.length === 1 ? '' : 's'}`}</div>}
                >
                    <SortTable list={publicationData} columns={publicationDataColumns} />
                </SortTablePanel>
            : null}
        </React.Fragment>
    );
};

PublicationDataTable.propTypes = {
    /** Array of publication_data @ids to display */
    publicationDataIds: PropTypes.array.isRequired,
};


// Display a publication object.
const PublicationComponent = (props, reactContext) => {
    const context = props.context;
    const itemClass = globals.itemClass(context, 'view-item');

    // Set up breadcrumbs
    const categoryTerms = context.categories && context.categories.map(category => `categories=${category}`);
    const crumbs = [
        { id: 'Publications' },
        {
            id: context.categories ? context.categories.join(' + ') : null,
            query: (categoryTerms && categoryTerms.join('&')),
            tip: context.categories && context.categories.join(' + '),
        },
    ];

    const crumbsReleased = (context.status === 'released');
    return (
        <div className={itemClass}>
            <Breadcrumbs root="/search/?type=Publication" crumbs={crumbs} crumbsReleased={crumbsReleased} />
            <h2>{context.title}</h2>
            <ItemAccessories item={context} audit={{ auditIndicators: props.auditIndicators, auditId: 'publication-audit' }} />
            {props.auditDetail(context.audit, 'publication-audit', { session: reactContext.session, sessionProperties: reactContext.session_properties, except: context['@id'] })}
            {context.authors ? <div className="authors">{context.authors}.</div> : null}
            <div className="journal">
                <Citation context={context} />
            </div>

            {context.abstract || context.data_used || (context.identifiers && context.identifiers.length > 0) ?
                <Panel>
                    <PanelBody>
                        <Abstract context={context} />
                    </PanelBody>
                </Panel>
            : null}

            {context.publication_data && context.publication_data.length > 0 ?
                <PublicationDataTable publicationDataIds={context.publication_data} />
            : null}

            {context.datasets && context.datasets.length > 0 ?
                <DatasetTable datasets={context.datasets} />
            : null }

            {context.supplementary_data && context.supplementary_data.length > 0 ?
                <Panel>
                    <PanelHeading>
                        <h4>Related data</h4>
                    </PanelHeading>
                    <PanelBody>
                        {context.supplementary_data.map((data, i) => <SupplementaryData data={data} key={i} />)}
                    </PanelBody>
                </Panel>
            : null}
        </div>
    );
};

PublicationComponent.propTypes = {
    context: PropTypes.object.isRequired,
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired,
};

PublicationComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
    session_properties: PropTypes.object,
};

// Note that Publication needs to be exported for Jest tests.
const Publication = auditDecor(PublicationComponent);
export default Publication;

globals.contentViews.register(Publication, 'Publication');


const Citation = (props) => {
    const context = props.context;
    return (
        <span>
            {context.journal ? <i>{context.journal}. </i> : ''}{context.date_published ? `${context.date_published};` : <span>&nbsp;</span>}
            {context.volume ? context.volume : ''}{context.issue ? `(${context.issue})` : '' }{context.page ? `:${context.page}.` : <span>&nbsp;</span>}
        </span>
    );
};

Citation.propTypes = {
    context: PropTypes.object.isRequired, // Citation object being displayed
};


const Abstract = (props) => {
    const context = props.context;
    return (
        <dl className="key-value">
            {context.abstract ?
                <div data-test="abstract">
                    <dt>Abstract</dt>
                    <dd>{context.abstract}</dd>
                </div>
            : null}

            {context.data_used ?
                <div data-test="dataused">
                    <dt>Consortium data used in this publication</dt>
                    <dd>{context.data_used}</dd>
                </div>
            : null}

            {context.identifiers && context.identifiers.length > 0 ?
                <div data-test="references">
                    <dt>References</dt>
                    <dd><DbxrefList context={context} dbxrefs={context.identifiers} addClasses="multi-value" /></dd>
                </div>
            : null}
        </dl>
    );
};

Abstract.propTypes = {
    context: PropTypes.object.isRequired, // Abstract being displayed
};


const SupplementaryData = (props) => {
    const data = props.data;
    return (
        <section className="supplementary-data">
            <dl className="key-value">
                {data.supplementary_data_type ?
                    <div data-test="availabledata">
                        <dt>Available data</dt>
                        <dd>{data.supplementary_data_type}</dd>
                    </div>
                : null}

                {data.file_format ?
                    <div data-test="fileformat">
                        <dt>File format</dt>
                        <dd>{data.file_format}</dd>
                    </div>
                : null}

                {data.url ?
                    <div data-test="url">
                        <dt>URL</dt>
                        <dd><a href={data.url}>{data.url}</a></dd>
                    </div>
                : null}

                {data.data_summary ?
                    <div data-test="datasummary">
                        <dt>Data summary</dt>
                        <dd>{data.data_summary}</dd>
                    </div>
                : null}
            </dl>
        </section>
    );
};

SupplementaryData.propTypes = {
    data: PropTypes.object.isRequired,
};


class SupplementaryDataListing extends React.Component {
    constructor() {
        super();

        // Set initial React state.
        this.state = { excerptExpanded: false };

        // Bind this to non-React methods.
        this.handleClick = this.handleClick.bind(this);
    }

    handleClick() {
        this.setState(prevState => ({
            excerptExpanded: !prevState.excerptExpanded,
        }));
    }

    render() {
        const { data, id, index } = this.props;
        const summary = data.data_summary;
        const excerpt = (summary && (summary.length > 100) ? globals.truncateString(summary, 100) : undefined);

        // Make unique ID for ARIA identification
        const nodeId = id.replace(/\//g, '') + index;

        return (
            <div className="list-supplementary__item">
                {data.supplementary_data_type ?
                    <div><strong>Available supplemental data: </strong>{data.supplementary_data_type}</div>
                : null}

                {data.file_format ?
                    <div><strong>File format: </strong>{data.file_format}</div>
                : null}

                {data.url ?
                    <div><strong>URL: </strong><a href={data.url}>{data.url}</a></div>
                : null}

                {summary ?
                    <div id={nodeId} aria-expanded={excerpt ? this.state.excerptExpanded : true}>
                        <strong>Data summary: </strong>
                        {excerpt ?
                            <React.Fragment>
                                {this.state.excerptExpanded ? summary : excerpt}
                                <button className="btn btn-default btn-xs" aria-controls={nodeId} onClick={this.handleClick}>
                                    {this.state.excerptExpanded ? <span>See less</span> : <span>See more</span>}
                                </button>
                            </React.Fragment>
                        : summary}
                    </div>
                : null}
            </div>
        );
    }
}

SupplementaryDataListing.propTypes = {
    data: PropTypes.object.isRequired,
    id: PropTypes.string.isRequired,
    index: PropTypes.number,
};

SupplementaryDataListing.defaultProps = {
    index: 0,
};


const ListingComponent = (props, context) => {
    const result = props.context;
    const authorList = result.authors && result.authors.length > 0 ? result.authors.split(', ', 4) : [];
    const authors = authorList.length === 4 ? `${authorList.splice(0, 3).join(', ')}, et al` : result.authors;

    return (
        <li className={resultItemClass(result)}>
            <div className="result-item">
                <div className="result-item__data">
                    <a href={result['@id']} className="result-item__link">{result.title}</a>
                    <div className="result-item__data-row">
                        {authors ? <p className="list-author">{authors}.</p> : null}
                        <p className="list-citation"><Citation context={result} /></p>
                        {result.identifiers && result.identifiers.length ? <DbxrefList context={result} dbxrefs={result.identifiers} addClasses="list-reference" /> : '' }
                        {result.supplementary_data && result.supplementary_data.length ?
                            <React.Fragment>
                                {result.supplementary_data.map((data, i) =>
                                    <section className="list-supplementary" key={i}>
                                        <SupplementaryDataListing data={data} id={result['@id']} index={i} />
                                    </section>
                                )}
                            </React.Fragment>
                        : null}
                    </div>
                </div>
                <div className="result-item__meta">
                    <div className="result-item__meta-title">Publication</div>
                    <Status item={result.status} badgeSize="small" css="result-table__status" />
                    {props.auditIndicators(result.audit, result['@id'], { session: context.session, sessionProperties: context.session_properties, search: true })}
                </div>
                <PickerActions context={result} />
            </div>
            {props.auditDetail(result.audit, result['@id'], { session: context.session, sessionProperties: context.session_properties, forcedEditLink: true })}
        </li>
    );
};

ListingComponent.propTypes = {
    context: PropTypes.object.isRequired,
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

ListingComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
    session_properties: PropTypes.object,
};

const Listing = auditDecor(ListingComponent);

globals.listingViews.register(Listing, 'Publication');
