import React from 'react';
import PropTypes from 'prop-types';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import { DbxrefList, dbxrefHref } from './dbxref';
import { PickerActions } from './search';
import { auditDecor } from './audit';
import { DisplayAsJson } from './objectutils';
import { ExperimentTable } from './dataset';
import { RelatedItems } from './item';


const Gene = (props) => {
    const context = props.context;
    const itemClass = globals.itemClass(context, 'view-detail key-value');

    // Set up breadcrumbs
    const crumbs = [
        { id: 'Genes' },
        {
            id: <i>{context.organism.scientific_name}</i>,
            query: `organism.scientific_name=${context.organism.scientific_name}`,
            tip: `${context.organism.scientific_name}`,
        },
    ];

    return (
        <div className={globals.itemClass(context, 'view-item')}>
            <header className="row">
                <div className="col-sm-12">
                    <Breadcrumbs root="/search/?type=gene" crumbs={crumbs} />
                    <h2>{context.symbol} (<em>{context.organism.scientific_name}</em>)</h2>
                    <DisplayAsJson />
                </div>
            </header>

            <div className="panel">
                <dl className={itemClass}>
                    {/* TODO link to NCBI Entrez page? */}
                    <div data-test="gendid">
                        <dt>Entrez GeneID</dt>
                        <dd>
                            <a href={dbxrefHref('GeneID', context.geneid)}>{context.geneid}</a>
                        </dd>
                    </div>

                    {/* TODO link to NADB page? */}
                    <div data-test="symbol">
                        <dt>Gene symbol</dt>
                        <dd>{context.symbol}</dd>
                    </div>

                    {context.name ?
                        <div data-test="name">
                            <dt>Official gene name</dt>
                            <dd>{context.name}</dd>
                        </div>
                    : null}

                    {context.synonyms ?
                      <div data-test="synonyms">
                          <dt>Synonyms</dt>
                          <dd>
                              <ul>
                                  {context.synonyms.map(synonym =>
                                      <li key={synonym}>
                                          <span>{synonym}</span>
                                      </li>
                                  )}
                              </ul>
                          </dd>
                      </div>
                    : null}

                    <div data-test="external">
                        <dt>External resources</dt>
                        <dd>
                            {context.dbxrefs.length ?
                                <DbxrefList context={context} dbxrefs={context.dbxrefs} />
                            : <em>None submitted</em> }
                        </dd>
                    </div>

                    {context.go_annotations && context.go_annotations.length > 0 ?
                        <div data-test="go_ids">
                            <dt>Gene Ontology</dt>
                            <dd>
                                <DbxrefList context={context} dbxrefs={context.go_annotations.map(goAnnotation => goAnnotation.go_id)} />
                            </dd>
                        </div>
                    : null}
                </dl>
            </div>

            <RelatedItems
                title={`Experiments targeting gene ${context.symbol}`}
                url={`/search/?type=Experiment&target.genes.uuid=${context.uuid}`}
                Component={ExperimentTable}
            />
        </div>
    );
};

Gene.propTypes = {
    context: PropTypes.object, // Target object to display
};

Gene.defaultProps = {
    context: null,
};

globals.contentViews.register(Gene, 'Gene');


const ListingComponent = (props, reactContext) => {
    const result = props.context;
    return (
        <li>
            <div className="clearfix">
                <PickerActions {...props} />
                <div className="pull-right search-meta">
                    <p className="type meta-title">Gene</p>
                    {props.auditIndicators(result.audit, result['@id'], { session: reactContext.session, search: true })}
                </div>
                <div className="accession">
                    <a href={result['@id']}>
                        {result.symbol}
                        {result.organism && result.organism.scientific_name ? <em>{` (${result.organism.scientific_name})`}</em> : null}
                    </a>
                </div>
                <div className="data-row">
                    <strong>External resources: </strong>
                    {result.dbxrefs && result.dbxrefs.length ?
                        <DbxrefList context={result} dbxrefs={result.dbxrefs} />
                    : <em>None submitted</em> }
                </div>
            </div>
            {props.auditDetail(result.audit, result['@id'], { session: reactContext.session, except: result['@id'], forcedEditLink: true })}
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
};

const Listing = auditDecor(ListingComponent);

globals.listingViews.register(Listing, 'Gene');
