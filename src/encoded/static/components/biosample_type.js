import React from 'react';
import PropTypes from 'prop-types';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import { DbxrefList } from './dbxref';
import { PickerActions } from './search';
import { auditDecor } from './audit';
import pubReferenceList from './reference';
import BiosampleTermId from './biosample';
import { DisplayAsJson } from './objectutils';


const BiosampleTypeComponenet = (props, reactContext) => {
    const context = props.context;
    const itemClass = globals.itemClass(context, 'view-detail key-value');

    // Set up breadcrumbs
    const crumbs = [
        { id: 'BiosampleTypes' },
        { id: context.classification, query: `classification=${context.classification}`, tip: context.classification },
        { id: context.term_name, query: `term_name=${context.term_name}`, tip: context.term_name },
    ];

    const crumbsReleased = (context.status === 'released');

    // Get a list of reference links, if any
    const references = pubReferenceList(context.references);

    return (
        <div className={itemClass}>
            <header className="row">
                <div className="col-sm-12">
                    <Breadcrumbs root="/search/?type=BiosampleType" crumbs={crumbs} crumbsReleased={crumbsReleased} />
                    <h2>
                        <span className="sentence-case">
                            {context.term_name} / {context.classification}
                        </span>
                    </h2>
                    {props.auditIndicators(context.audit, 'biosample-type-audit')}
                    <DisplayAsJson />
                </div>
            </header>
            {props.auditDetail(context.audit, 'biosample-type-audit', { except: context['@id'] })}
            <div className="panel">
                <dl className="key-value">
                    <div data-test="term-name">
                        <dt>Term name</dt>
                        <dd>{context.term_name}</dd>
                    </div>

                    <div data-test="term-id">
                        <dt>Term ID</dt>
                        <dd><BiosampleTermId termId={context.term_id} /></dd>
                    </div>

                    {context.notes ?
                        <div data-test="note">
                            <dt>Notes</dt>
                            <dd>{context.notes}</dd>
                        </div>
                    : null}

                    {context.dbxrefs && context.dbxrefs.length ?
                        <div data-test="externalresources">
                            <dt>External resources</dt>
                            <dd><DbxrefList context={context} dbxrefs={context.dbxrefs} /></dd>
                        </div>
                    : null}

                    {references ?
                        <div data-test="references">
                            <dt>References</dt>
                            <dd>{references}</dd>
                        </div>
                    : null}

                    {context.aliases.length ?
                        <div data-test="aliases">
                            <dt>Aliases</dt>
                            <dd>
                                <ul>
                                    {context.aliases.map(alias =>
                                        <li key={alias}>
                                            <span>{alias}</span>
                                        </li>
                                    )}
                                </ul>
                            </dd>
                        </div>
                    : null}
                </dl>
            </div>
        </div>
    );
};

BiosampleTypeComponenet.propTypes = {
    context: PropTypes.object.isRequired,
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

const BiosampleType = auditDecor(BiosampleTypeComponenet);

globals.contentViews.register(BiosampleType, 'BiosampleType');


const ListingComponent = (props, reactContext) => {
    const result = props.context;
    return (
        <li>
            <div className="clearfix">
                <PickerActions {...props} />
                <div className="pull-right search-meta">
                    <p className="type meta-title">Biosample Type</p>
                    {props.auditIndicators(result.audit, result['@id'], { search: true })}
                </div>
                <div className="accession">
                    <a href={result['@id']}>
                        {result.term_name} ({result.classification})
                    </a>
                </div>
                <div className="data-row">
                    <strong>Ontology ID: </strong><BiosampleTermId termId={result.term_id} />
                </div>
            </div>
            {props.auditDetail(result.audit, result['@id'], { except: result['@id'], forcedEditLink: true })}
        </li>
    );
};

ListingComponent.propTypes = {
    context: PropTypes.object.isRequired,
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

const Listing = auditDecor(ListingComponent);

globals.listingViews.register(Listing, 'BiosampleType');
