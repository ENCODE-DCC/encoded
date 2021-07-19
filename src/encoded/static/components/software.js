import PropTypes from 'prop-types';
import _ from 'underscore';
import url from 'url';
import { Panel, PanelBody, TabPanel } from '../libs/ui/panel';
import * as globals from './globals';
import QueryString from '../libs/query_string';
import pubReferenceList from './reference';
import { PickerActions, resultItemClass, ResultTable } from './search';
import Status from './status';
import { auditDecor } from './audit';
import { ItemAccessories, TopAccessories, useMount } from './objectutils';
import { SortTablePanel, SortTable } from './sorttable';


const SoftwareComponent = ({ context, auditIndicators, auditDetail }, reactContext) => {
    const itemClass = globals.itemClass(context, 'view-item');

    // Set up breadcrumbs.
    const typeTerms = context.software_type && context.software_type.map((type) => `software_type=${type}`);
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
        const versionKey = _(Object.keys(queryParsed)).find((key) => key === 'version');
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
        display: (version) => (version.downloaded_url ? <a href={version.downloaded_url}>{version.version}</a> : <span>{version.version}</span>),
        title: 'Version',
    },
    download_checksum: {
        title: 'Download checksum',
        sorter: false,
    },
};


const SoftwareVersionTable = (props) => {
    // De-dupe items list.
    const items = _(props.items).uniq((version) => version['@id']);

    return (
        <SortTablePanel title="Software versions">
            <SortTable
                list={items}
                columns={softwareVersionColumns}
                rowClasses={(item) => (item.version === props.highlightVersion ? 'highlight-row' : '')}
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
                        <>
                            <strong>Software type: </strong>
                            {result.software_type.join(', ')}
                        </>
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

const currentRegion = (assembly, region) => {
    let lastRegion = {};
    if (assembly && region) {
        lastRegion = {
            assembly,
            region,
        };
    }
    return lastRegion;
};

// The software search page includes the following five tabs
const softwareTabData = {
    All: {
        title: 'All',
        link: '/encode-software/?type=Software',
        key: 'All',
        description: 'All software used or developed by the ENCODE Consortium',
    },
    Portal: {
        title: 'Portal',
        link: '/encode-software/?type=Software&used_by=DCC',
        key: 'DCC',
        description: 'Software implemented and developed by the DCC (Data Coordination Center) for the Portal',
    },
    Encyclopedia: {
        title: 'Encyclopedia',
        link: '/encode-software/?type=Software&used_by=DAC',
        key: 'DAC',
        description: 'Software tools used in integrative analysis for the development of the Encyclopedia and SCREEN',
    },
    Pipeline: {
        title: 'Uniform Processing Pipelines',
        link: '/encode-software/?type=Pipeline&lab.title=ENCODE+Processing+Pipeline&award.rfa=ENCODE4&status=released ',
        key: 'pipeline',
        description: 'Software implemented and developed by the DCC (Data Coordination Center) for uniforming processing of data',
    },
    AWG: {
        title: 'Consortium Analysis',
        link: '/encode-software/?type=Software&used_by=AWG',
        key: 'AWG',
        description: 'Software tools implemented and developed by the consortium for computational analysis',
    },
};

const softwareTabList = {};
Object.keys(softwareTabData).forEach((s) => {
    softwareTabList[s] =
        <div className="tab-inner">
            <a href={softwareTabData[s].link}>
                {softwareTabData[s].title}
            </a>
        </div>;
});

// The ENCODE Software page displays a table of results corresponding to a selected software item
// Buttons for each software item are displayed like tabs or links
const EncodeSoftware = (props, context) => {
    const parsedUrl = url.parse(props.context['@id']);
    const query = new QueryString(parsedUrl.query);
    const searchBase = url.parse(context.location_href).search || '';
    const usedByKey = query.getKeyValues('used_by');
    let selectedSoftwareKey = null;
    const softwareTabDataKeys = Object.keys(softwareTabData);
    const acceptedQueryTypes = ['Software', 'Pipeline'];
    let selectedSoftwareTab = null;

    // Props is cloned so the clone can be modified and the props object itself unaltered.
    // It is bad practice to modify parameters and that is why props itself is not modified
    const encodeSoftwareProps = { ...props };

    // Determine what tab is selected
    // for-loop used because it has a nice 'break' option to kill the loop prematurely
    for (let i = 0; i < softwareTabDataKeys.length; i += 1) {
        const key = softwareTabDataKeys[i];
        const currentTab = softwareTabData[key];

        if (currentTab.key === usedByKey[0]) {
            selectedSoftwareKey = key;
            break;
        }

        if (query.getKeyValues('type')[0] === 'Pipeline') {
            selectedSoftwareKey = 'Pipeline';
            break;
        }

        if (!usedByKey || usedByKey.length === 0) {
            selectedSoftwareKey = 'All';
            break;
        }
    }

    useMount(() => {
        const types = query.getKeyValues('type');
        const type = !types || types.length !== 1 ? null : types[0];

        // If type is not in acceptedQueryTypes, then request is
        // invalid. The request is resent with Portal tab selected.
        if (!acceptedQueryTypes.includes(type)) {
            query.deleteKeyValue('type');
            query.addKeyValue('type', 'Software');
            query.addKeyValue('used_by', 'DCC');
            const href = `?${query.format()}`;
            context.navigate(href);
        }
    });

    if (selectedSoftwareKey) {
        selectedSoftwareTab = softwareTabData[selectedSoftwareKey];

        // Remove facets that are part of the generated data the user needs. It is counterproductive to allow users
        // to filter out data they came to the page to access
        if (selectedSoftwareKey === 'Pipeline') {
            const removedFacets = ['lab.title', 'award.rfa', 'status'];
            encodeSoftwareProps.context.facets = encodeSoftwareProps.context.facets.filter((prop) => !removedFacets.includes(prop.field));
        } else {
            encodeSoftwareProps.context.facets = encodeSoftwareProps.context.facets.filter((prop) => prop.field !== 'used_by');
        }

        // "Clear Filters" changed from default provided by the backend to the tab's pristine state-URL
        encodeSoftwareProps.context.clear_filters = selectedSoftwareTab.link;
    }

    return (
        <div className="encode-software">
            <div className="layout">
                <div className="layout__block layout__block--100">
                    <div className="block series-search" data-pos="0,0,0">
                        <h1>ENCODE Software</h1>
                        <div className="outer-tab-container">
                            <TabPanel
                                tabs={softwareTabList}
                                selectedTab={selectedSoftwareKey}
                                tabCss="tab-button"
                                tabPanelCss="tab-container series-tabs"
                            >
                                <div className="tab-body">
                                    <div className="tab-description">{selectedSoftwareTab ? selectedSoftwareTab.description : ''}</div>
                                    <div className="series-wrapper">
                                        <Panel>
                                            <PanelBody>
                                                <ResultTable
                                                    {...encodeSoftwareProps}
                                                    searchBase={searchBase}
                                                    onChange={context.navigate}
                                                    currentRegion={currentRegion}
                                                    hideDocType
                                                />
                                            </PanelBody>
                                        </Panel>
                                    </div>
                                </div>
                            </TabPanel>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

EncodeSoftware.propTypes = {
    context: PropTypes.object.isRequired,
};

EncodeSoftware.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
};

globals.contentViews.register(EncodeSoftware, 'EncodeSoftware');


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
