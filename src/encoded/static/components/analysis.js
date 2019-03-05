import React from 'react';
import PropTypes from 'prop-types';
import { auditDecor } from './audit';
import * as globals from './globals';
import Status from './status';
import { PickerActions } from './search';


const ListingComponent = (props, reactContext) => {
    const result = props.context;
    return (
        <li>
            <div className="result-item">
                <div className="result-item__data">
                    <PickerActions {...props} />
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Analysis</p>
                        <p className="type">{` ${result.accession}`}</p>
                        <Status item={result.status} badgeSize="small" css="result-table__status" />
                        {props.auditIndicators(result.audit, result['@id'], { session: reactContext.session, search: true })}
                    </div>
                    <div className="accession">
                        <a href={result['@id']}>{result.accession}</a>
                    </div>
                    <div className="data-row">
                        <div>
                            <strong>Analyzed: </strong>
                            <a href={result.dataset}>{result.dataset}</a>
                        </div>
                    </div>
                </div>
            </div>
            {props.auditDetail(result.audit, result['@id'], { session: reactContext.session, except: result['@id'], forcedEditLink: true })}
        </li>
    );
};

ListingComponent.propTypes = {
    context: PropTypes.object.isRequired, // Analysis search results
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

ListingComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
};

const Listing = auditDecor(ListingComponent);

globals.listingViews.register(Listing, 'Analysis');
