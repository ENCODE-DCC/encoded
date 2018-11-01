import React from 'react';
import PropTypes from 'prop-types';
import queryString from 'query-string';
import _ from 'underscore';
import url from 'url';
import { svgIcon } from '../libs/svg-icons';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../libs/bootstrap/modal';
import { TabPanel, TabPanelPane } from '../libs/bootstrap/panel';
import { auditDecor } from './audit';
import { FetchedData, Param } from './fetched';
import GenomeBrowser from './genome_browser';
import * as globals from './globals';
import { Attachment } from './image';
import { BrowserSelector } from './objectutils';
import { DbxrefList } from './dbxref';
import Status from './status';
import { BiosampleSummaryString, BiosampleOrganismNames } from './typeutils';

export function List(reactProps) {
    // XXX not all panels have the same markup
    let context;
    let viewProps = reactProps;
    if (reactProps['@id']) {
        context = reactProps;
        viewProps = { context, key: context['@id'] };
    }
    const TableView = globals.tableViews.lookup(viewProps.context);
    console.log("ALERT");
    console.log(viewProps);
    return <TableView {...viewProps} />;
}

/* eslint-disable react/prefer-stateless-function */
class ItemComponent extends React.Component {
    render() {
        const result = this.props.context;
        const title = globals.listingTitles.lookup(result)({ context: result });
        const itemType = result['@type'][0];
        return (
            <li>
                <div className="clearfix">
                    <PickerActions {...this.props} />
                    <div className="accession">
                        <a href={result['@id']}>{title}</a>
                    </div>
                    <div className="data-row">
                        {result.description}
                    </div>
                    <div className="data-row">This is a test.</div>
                </div>
                {this.props.auditDetail(result.audit, result['@id'], { session: this.context.session, except: result['@id'], forcedEditLink: true })}
            </li>
        );
    }
}

ItemComponent.propTypes = {
    context: PropTypes.object.isRequired, // Component to render in a List view
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

ItemComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
};

const Item = auditDecor(ItemComponent);

globals.listingViews.register(Item, 'Item');
