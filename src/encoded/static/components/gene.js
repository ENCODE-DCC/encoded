import React from 'react';
import PropTypes from 'prop-types';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import { DbxrefList, dbxrefHref } from './dbxref';
import { PickerActions, resultItemClass } from './search';
import { auditDecor } from './audit';
import { ItemAccessories } from './objectutils';
import { RelatedItems } from './item';
import { ExperimentTable } from './typeutils';


class Gene extends React.Component {
    constructor() {
        super();

        this.state = {
            goIDs: [],
        };
        this.baseGOUrl = 'http://api.geneontology.org/api/bioentity/gene/{0}/function';
    }

    componentDidMount() {
        const nadbIDs = [];
        const uniprotIDs = [];
        this.props.context.dbxrefs.forEach((dbxref) => {
            if (dbxref.startsWith('HGNC:')) {
                nadbIDs.push('HGNC:'.concat(dbxref));
            }
        });
        Promise.all((nadbIDs.length > 0 ? nadbIDs : uniprotIDs).map(
            goID => this.context.fetch(
                this.baseGOUrl.replace(/\{0\}/g, goID), {
                    method: 'GET',
                }
            ).then((response) => {
                if (response.ok) {
                    return response.json();
                }
                return { numFound: 0 };
            }).then((annotation) => {
                if (annotation.numFound > 0) {
                    return goID;
                }
                return Promise.resolve(null);
            })
        )).then((validGOs) => {
            this.setState({
                goIDs: validGOs.filter(validGO => validGO !== null).map(goID => 'GOGene:'.concat(goID)),
            });
        });
    }

    render() {
        const context = this.props.context;
        const itemClass = globals.itemClass(context, 'view-detail key-value');

        // Set up breadcrumbs
        const crumbs = [
            { id: 'Genes' },
        ];

        const crumbsReleased = (context.status === 'released');

        return (
            <div className={globals.itemClass(context, 'view-item')}>
                <header>
                    <Breadcrumbs root="/search/?type=Gene" crumbs={crumbs} crumbsReleased={crumbsReleased} />
                    <h2>{context.symbol} (<em>{context.assembly}</em>)</h2>
                    <ItemAccessories item={context} />
                </header>

                <div className="panel">
                    <dl className={itemClass}>
                        {/* TODO link to external page? */}
                        <div data-test="gene_id">
                            <dt>Ensembl Gene ID</dt>
                            <dd>
                                <a href={dbxrefHref('Gene ID', context.gene_id)}>{context.gene_id}</a>
                            </dd>
                        </div>

                        {/* TODO link to NADB page? */}
                        <div data-test="symbol">
                            <dt>Gene symbol</dt>
                            <dd>{context.symbol}</dd>
                        </div>

                        {context.assembly ?
                            <div data-test="assembly">
                                <dt>Assembly</dt>
                                <dd>{context.assembly}</dd>
                            </div>
                        : null}

                        {context.gene_biotype ?
                            <div data-test="gene_biotype">
                                <dt>Biotype</dt>
                                <dd>{context.gene_biotype}</dd>
                            </div>
                        : null}

                        <div data-test="external">
                            <dt>External resources</dt>
                            <dd>
                                {context.dbxrefs.length > 0 ?
                                    <DbxrefList context={context} dbxrefs={context.dbxrefs} />
                                : <em>None submitted</em> }
                            </dd>
                        </div>
                    </dl>
                </div>
            </div>
        );
    }
}

Gene.propTypes = {
    context: PropTypes.object, // Target object to display
};

Gene.defaultProps = {
    context: null,
};

Gene.contextTypes = {
    fetch: PropTypes.func,
};

globals.contentViews.register(Gene, 'Gene');


const ListingComponent = (props, reactContext) => {
    const result = props.context;
    return (
        <li className={resultItemClass(result)}>
            <div className="result-item">
                <div className="result-item__data">
                    <a href={result['@id']} className="result-item__link">
                        {result.symbol}
                        {result.assembly} : null}
                    </a>
                    <div className="result-item__data-row">
                        <strong>External resources: </strong>
                        {result.dbxrefs && result.dbxrefs.length ?
                            <DbxrefList context={result} dbxrefs={result.dbxrefs} />
                        : <em>None submitted</em> }
                    </div>
                </div>
                <div className="result-item__meta">
                    <div className="result-item__meta-title">Gene</div>
                    {props.auditIndicators(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties, search: true })}
                </div>
                <PickerActions context={result} />
            </div>
            {props.auditDetail(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties })}
        </li>
    );
};

ListingComponent.propTypes = {
    context: PropTypes.object.isRequired, // Target search results
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

ListingComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
    session_properties: PropTypes.object,
};

const Listing = auditDecor(ListingComponent);

globals.listingViews.register(Listing, 'Gene');
