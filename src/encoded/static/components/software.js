import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import url from 'url';
import globals from './globals';
import { Breadcrumbs } from './navigation';
import { PickerActions } from './search';
import { pubReferenceList } from './reference';
import StatusLabel from './statuslabel';
import { auditDecor } from './audit';


class SoftwareComponent extends React.Component {
    render() {
        const { context } = this.props;
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
        const queryParsed = this.context.location_href && url.parse(this.context.location_href, true).query;
        if (queryParsed && Object.keys(queryParsed).length) {
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
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs root="/search/?type=software" crumbs={crumbs} />
                        <h2>{context.title}</h2>
                        <div className="characterization-status-labels">
                            <StatusLabel title="Status" status={context.status} />
                        </div>
                        {this.props.auditIndicators(context.audit, 'software-audit', { session: this.context.session })}
                    </div>
                </header>
                {this.props.auditDetail(context.audit, 'software-audit', { session: this.context.session, except: context['@id'] })}

                <div className="panel">
                    <dl className="key-value">
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

                        {context.software_type && context.software_type.length ?
                            <div data-test="type">
                                <dt>Software type</dt>
                                <dd>{context.software_type.join(', ')}</dd>
                            </div>
                        : null}

                        {context.purpose && context.purpose.length ?
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
                </div>

                {context.versions && context.versions.length ?
                    <div>
                        <h3>Software Versions</h3>
                        <SoftwareVersionTable items={context.versions} highlightVersion={highlightVersion} />
                    </div>
                : null}
            </div>
        );
    }
}

SoftwareComponent.propTypes = {
    context: PropTypes.object.isRequired, // Software object being rendered
    auditIndicators: PropTypes.func.isRequired,
    auditDetail: PropTypes.func.isRequired,
};

SoftwareComponent.contextTypes = {
    location_href: PropTypes.string,
    session: PropTypes.object,
};


// Note: need to export for Jest tests even though no other module imports it.
export const Software = auditDecor(SoftwareComponent);

globals.content_views.register(Software, 'Software');


const SoftwareVersionTable = (props) => {
    // Dedupe items list.
    const items = _(props.items).uniq(version => version['@id']);

    return (
        <div className="table-responsive">
            <table className="table table-panel table-striped table-hover">
                <thead>
                    <tr>
                        <th>Version</th>
                        <th>Download checksum</th>
                    </tr>
                </thead>
                <tbody>
                    {items.map(version =>
                        <tr key={version.uuid} className={props.highlightVersion === version.version ? 'highlight-row' : null}>
                            <td>
                                {version.downloaded_url ?
                                    <a href={version.downloaded_url}>{version.version}</a>
                                :
                                    <span>{version.version}</span>
                                }
                            </td>
                            <td>{version.download_checksum}</td>
                        </tr>
                    )}
                </tbody>
                <tfoot />
            </table>
        </div>
    );
};

SoftwareVersionTable.propTypes = {
    items: PropTypes.array.isRequired, // Software versions to render in the table
    highlightVersion: PropTypes.string, // Version number of row to highlight
};

SoftwareVersionTable.defaultProps = {
    highlightVersion: '',
};


class ListingComponent extends React.Component {
    render() {
        const result = this.props.context;
        return (
            <li>
                <div className="clearfix">
                    <PickerActions {...this.props} />
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Software</p>
                        {result.status ? <p className="type meta-status">{` ${result.status}`}</p> : ''}
                        {this.props.auditIndicators(result.audit, result['@id'], { session: this.context.session, search: true })}
                    </div>
                    <div className="accession">
                        <a href={result['@id']}>{result.title}</a>
                        {result.source_url ? <span className="accession-note"> &mdash; <a href={result.source_url}>source</a></span> : ''}
                    </div>
                    <div className="data-row">
                        <div>{result.description}</div>
                        {result.software_type && result.software_type.length ?
                            <div>
                                <strong>Software type: </strong>
                                {result.software_type.join(', ')}
                            </div>
                        : null}
                    </div>
                </div>
                {this.props.auditDetail(result.audit, result['@id'], { session: this.context.session, except: result['@id'], forcedEditLink: true })}
            </li>
        );
    }
}

ListingComponent.propTypes = {
    context: PropTypes.object.isRequired, // Software object being rendered as a search result.
    auditIndicators: PropTypes.func.isRequired, // From auditDecor
    auditDetail: PropTypes.func.isRequired, // From auditDecor
};

ListingComponent.contextTypes = {
    session: PropTypes.object,
};

const Listing = auditDecor(ListingComponent);

globals.listing_views.register(Listing, 'Software');


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
