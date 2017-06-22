import React from 'react';
import PropTypes from 'prop-types';
import { auditDecor } from './audit';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import { DbxrefList } from './dbxref';
import { PickerActions } from './search';


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
            tip: context.categories && context.categories.join(' + ') },
    ];

    return (
        <div className={itemClass}>
            <Breadcrumbs root="/search/?type=Publication" crumbs={crumbs} />
            <h2>{context.title}</h2>
            {props.auditIndicators(context.audit, 'publication-audit', { session: reactContext.session })}
            {props.auditDetail(context.audit, 'publication-audit', { session: reactContext.session, except: context['@id'] })}
            {context.authors ? <div className="authors">{context.authors}.</div> : null}
            <div className="journal">
                <Citation {...props} />
            </div>

            {context.abstract || context.data_used || (context.datasets && context.datasets.length) || (context.identifiers && context.identifiers.length) ?
                <div className="view-detail panel">
                    <Abstract {...props} />
                </div>
            : null}

            {context.supplementary_data && context.supplementary_data.length ?
                <div>
                    <h3>Related data</h3>
                    <div className="panel view-detail" data-test="supplementarydata">
                        {context.supplementary_data.map((data, i) => <SupplementaryData data={data} key={i} />)}
                    </div>
                </div>
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
};

// Note that Publication needs to be exported for Jest tests.
const Publication = auditDecor(PublicationComponent);
export default Publication;

globals.contentViews.register(Publication, 'Publication');


const Citation = (props) => {
    const context = props.context;
    return (
        <span>
            {context.journal ? <i>{context.journal}. </i> : ''}{context.date_published ? `${context.date_published};` : ''}
            {context.volume ? context.volume : ''}{context.issue ? `(${context.issue})` : '' }{context.page ? `:${context.page}.` : ''}
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

            {context.datasets && context.datasets.length ?
                <div data-test="datasets">
                    <dt>Datasets</dt>
                    <dd>
                        {context.datasets.map((dataset, i) => (
                            <span key={i}>
                                {i > 0 ? ', ' : ''}
                                <a href={dataset['@id']}>{dataset.accession}</a>
                            </span>
                        ))}
                    </dd>
                </div>
            : null}

            {context.identifiers && context.identifiers.length ?
                <div data-test="references">
                    <dt>References</dt>
                    <dd><DbxrefList values={context.identifiers} className="multi-value" /></dd>
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
            <div className="list-supplementary">
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
                    <span id={nodeId} aria-expanded={excerpt ? this.state.excerptExpanded : true}>
                        <strong>Data summary: </strong>{excerpt ?
                            <span>
                                {this.state.excerptExpanded ? summary : excerpt}
                                <button className="btn btn-link" aria-controls={nodeId} onClick={this.handleClick}>
                                    {this.state.excerptExpanded ? <span>See less</span> : <span>See more</span>}
                                </button>
                            </span>
                        : summary}
                    </span>
                : null}
            </div>
        );
    }
}

SupplementaryDataListing.propTypes = {
    data: PropTypes.object.isRequired,
};


const ListingComponent = (props, context) => {
    const result = props.context;
    const authorList = result.authors && result.authors.length ? result.authors.split(', ', 4) : [];
    const authors = authorList.length === 4 ? `${authorList.splice(0, 3).join(', ')}, et al` : result.authors;

    return (
        <li>
            <div className="clearfix">
                <PickerActions {...props} />
                <div className="pull-right search-meta">
                    <p className="type meta-title">Publication</p>
                    <p className="type meta-status">{` ${result.status}`}</p>
                    {props.auditIndicators(result.audit, result['@id'], { session: context.session, search: true })}
                </div>
                <div className="accession"><a href={result['@id']}>{result.title}</a></div>
                <div className="data-row">
                    {authors ? <p className="list-author">{authors}.</p> : null}
                    <p className="list-citation"><Citation {...props} /></p>
                    {result.identifiers && result.identifiers.length ? <DbxrefList values={result.identifiers} className="list-reference" /> : '' }
                    {result.supplementary_data && result.supplementary_data.length ?
                        <div>
                            {result.supplementary_data.map((data, i) =>
                                <SupplementaryDataListing data={data} id={result['@id']} index={i} key={i} />
                            )}
                        </div>
                    : null}
                </div>
            </div>
            {props.auditDetail(result.audit, result['@id'], { session: context.session, forcedEditLink: true })}
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
};

const Listing = auditDecor(ListingComponent);

globals.listingViews.register(Listing, 'Publication');
