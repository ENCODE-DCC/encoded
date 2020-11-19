import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import url from 'url';
import { Panel, PanelBody } from '../libs/ui/panel';
import * as globals from './globals';
import pubReferenceList from './reference';
import { PickerActions, resultItemClass } from './search';
import Status from './status';
import { auditDecor } from './audit';
import { ItemAccessories, TopAccessories } from './objectutils';
import { SortTablePanel, SortTable } from './sorttable';


const SoftwareComponent = ({ context, auditIndicators, auditDetail }, reactContext) => {
    const itemClass = globals.itemClass(context, 'view-item');

    // Set up breadcrumbs.
    const typeTerms = context.software_type && context.software_type.map(type => `software_type=${type}`);
    const crumbs = [
        { id: 'Software' },
        {
            id: context.software_type ? context.software_type.join(' + ') : null,
            query: typeTerms && typeTerms.join('&'),
            tip: context.software_type && context.software_type.join(' + '),
        },
    ];

    // See if there’s a version number to highlight
    let highlightVersion;
    const queryParsed = reactContext.location_href && url.parse(reactContext.location_href, true).query;
    if (queryParsed && Object.keys(queryParsed).length > 0) {
        // Find the first 'version' query string item, if any
        const versionKey = _(Object.keys(queryParsed)).find(key => key === 'version');
        if (versionKey) {
            highlightVersion = queryParsed[versionKey];
            if (typeof highlightVersion === 'object') {
                highlightVersion = highlightVersion[0];
            }
        }
    }

    // Get a list of reference links, if any
    const references = pubReferenceList(context.references);

    return (
        <div className={itemClass}>
            <header>
                <TopAccessories context={context} crumbs={crumbs} />
                <h1>{context.title}</h1>
                <ItemAccessories item={context} audit={{ auditIndicators, auditId: 'software-audit' }} />
            </header>
            {auditDetail(context.audit, 'software-audit', { session: reactContext.session, sessionProperties: reactContext.session_properties, except: context['@id'] })}

            <Panel>
                <PanelBody>
                    <dl className="key-value">
                        <div data-test="status">
                            <dt>Status</dt>
                            <dd><Status item={context} inline /></dd>
                        </div>

                        <div data-test="title">
                            <dt>Title</dt>
                            {context.source_url ?
                                <dd><a href={context.source_url}>{context.title}</a></dd> :
                                <dd>{context.title}</dd>
                            }
                        </div>

                        <div data-test="description">
                            <dt>Description</dt>
                            <dd>{context.description}</dd>
                        </div>

                        {context.software_type && context.software_type.length > 0 ?
                            <div data-test="type">
                                <dt>Software type</dt>
                                <dd>{context.software_type.join(', ')}</dd>
                            </div>
                        : null}

                        {context.purpose && context.purpose.length > 0 ?
                            <div data-test="purpose">
                                <dt>Used for</dt>
                                <dd>{context.purpose.join(', ')}</dd>
                            </div>
                        : null}

                        {references ?
                            <div data-test="references">
                                <dt>Publications</dt>
                                <dd>{references}</dd>
                            </div>
                        : null}
                    </dl>
                </PanelBody>
            </Panel>

            {context.versions && context.versions.length > 0 ?
                <SoftwareVersionTable items={context.versions} highlightVersion={highlightVersion} />
            : null}
        </div>
    );
};

SoftwareComponent.propTypes = {
    context: PropTypes.object.isRequired, // Software object being rendered
    auditIndicators: PropTypes.func.isRequired,
    auditDetail: PropTypes.func.isRequired,
};

SoftwareComponent.contextTypes = {
    location_href: PropTypes.string,
    session: PropTypes.object,
    session_properties: PropTypes.object,
};


// Note: need to export for Jest tests even though no other module imports it.
export const Software = auditDecor(SoftwareComponent);

globals.contentViews.register(Software, 'Software');


const softwareVersionColumns = {
    version: {
        display: version => (version.downloaded_url ? <a href={version.downloaded_url}>{version.version}</a> : <span>{version.version}</span>),
        title: 'Version',
    },
    download_checksum: {
        title: 'Download checksum',
        sorter: false,
    },
};


const SoftwareVersionTable = (props) => {
    // Dedupe items list.
    const items = _(props.items).uniq(version => version['@id']);

    return (
        <SortTablePanel title="Software versions">
            <SortTable
                list={items}
                columns={softwareVersionColumns}
                rowClasses={item => (item.version === props.highlightVersion ? 'highlight-row' : '')}
            />
        </SortTablePanel>
    );
};

SoftwareVersionTable.propTypes = {
    items: PropTypes.array.isRequired, // Software versions to render in the table
    highlightVersion: PropTypes.string, // Version number of row to highlight
};

SoftwareVersionTable.defaultProps = {
    highlightVersion: '',
};


const ListingComponent = ({ context: result, auditIndicators, auditDetail }, reactContext) => (
    <li className={resultItemClass(result)}>
        <div className="result-item">
            <div className="result-item__data">
                <a href={result['@id']} className="result-item__link">{result.title}</a>
                {result.source_url ? <span className="accession-note"> &mdash; <a href={result.source_url}>source</a></span> : ''}
                <div className="result-item__data-row">
                    <div>{result.description}</div>
                    {result.software_type && result.software_type.length > 0 ?
                        <React.Fragment>
                            <strong>Software type: </strong>
                            {result.software_type.join(', ')}
                        </React.Fragment>
                    : null}
                </div>
            </div>
            <div className="result-item__meta">
                <div className="result-item__meta-title">Software</div>
                <Status item={result.status} badgeSize="small" css="result-table__status" />
                {auditIndicators(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties, search: true })}
            </div>
            <PickerActions context={result} />
        </div>
        {auditDetail(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties, except: result['@id'], forcedEditLink: true })}
    </li>
);

ListingComponent.propTypes = {
    context: PropTypes.object.isRequired, // Software object being rendered as a search result.
    auditIndicators: PropTypes.func.isRequired, // From auditDecor
    auditDetail: PropTypes.func.isRequired, // From auditDecor
};

ListingComponent.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
};

const Listing = auditDecor(ListingComponent);

globals.listingViews.register(Listing, 'Software');


// Display a list of software versions from the given software_version list. This is meant to be displayed
// in a panel.
export function softwareVersionList(softwareVersions) {
    return (
        <span className="software-version-list">
            {softwareVersions.map((version) => {
                const versionNum = version.version === 'unknown' ? 'version unknown' : version.version;
                return (
                    <a href={`${version.software['@id']}?version=${version.version}`} key={version.uuid} className="software-version">
                        <span className="software">{version.software.name}</span>
                        {version.version ?
                            <span className="version">{versionNum}</span>
                        : null}
                    </a>
                );
            })}
        </span>
    );
}
