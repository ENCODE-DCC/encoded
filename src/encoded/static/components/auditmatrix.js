import React from 'react';
import PropTypes from 'prop-types';
import color from 'color';
import pluralize from 'pluralize';
import _ from 'underscore';
import url from 'url';
import { svgIcon } from '../libs/svg-icons';
import * as globals from './globals';
import { BrowserSelector } from './objectutils';
import { BatchDownload, FacetList, TextFilter } from './search';


class GroupMoreButton extends React.Component {
    constructor() {
        super();

        // Bind this to non-React components.
        this.localHandleClick = this.localHandleClick.bind(this);
    }

    localHandleClick() {
        this.props.handleClick(this.props.id);
    }

    render() {
        return <button className="group-more-cell__button" onClick={this.localHandleClick}>{this.props.displayText}</button>;
    }
}

GroupMoreButton.propTypes = {
    id: PropTypes.string, // ID for the handleClick function to know which control was clicked
    handleClick: PropTypes.func.isRequired, // Call this parent function to handle the click in the button
    displayText: PropTypes.string, // Text to display in the button while closed
};

GroupMoreButton.defaultProps = {
    id: '',
    displayText: '',
};


class AuditMatrix extends React.Component {
    static generateYGroupOpen(matrix) {
        // Make a state for each of the Y groups (each Y group currently shows an audit category).
        // To do that, we have to get each of the bucket keys, which will be the keys into the
        // object that keeps track of whether the group shows all or not. If a group has fewer than
        // the maximum number of items to show a See More button, it doesn't get included in the
        // state.
        const primaryYGrouping = matrix.y.group_by[0];
        const secondaryYGrouping = matrix.y.group_by[1];
        const yLimit = matrix.y.limit;
        const yGroups = matrix.y[primaryYGrouping].buckets;
        const yGroupOpen = {};
        yGroups.forEach((group) => {
            if (group[secondaryYGrouping].buckets.length > yLimit) {
                yGroupOpen[group.key] = false;
            }
        });
        return yGroupOpen;
    }

    constructor(props) {
        super(props);

        // Set initial React state.
        const yGroupOpen = AuditMatrix.generateYGroupOpen(this.props.context.matrix);
        this.state = {
            yGroupOpen,
            allYGroupsOpen: false,
        };

        // Bind this to non-React methods.
        this.onChange = this.onChange.bind(this);
        this.onFilter = this.onFilter.bind(this);
        this.updateElement = this.updateElement.bind(this);
        this.handleClick = this.handleClick.bind(this);
        this.handleSeeAllClick = this.handleSeeAllClick.bind(this);
    }

    componentWillReceiveProps(nextProps) {
        // This callback makes possible updating the See More buttons when the user clicks a facet,
        // which could cause these buttons to not be needed. This resets all the buttons to the See
        // More state.
        const yGroupOpen = AuditMatrix.generateYGroupOpen(nextProps.context.matrix);
        this.setState({
            yGroupOpen,
            allYGroupsOpen: false,
        });
    }

    onChange(href) {
        this.context.navigate(href);
    }

    onFilter(e) {
        const search = e.currentTarget.getAttribute('href');
        this.context.navigate(search);
        e.stopPropagation();
        e.preventDefault();
    }

    // Called when the Visualize button dropdown menu gets opened or closed. `dropdownEl` is the
    // DOM node for the dropdown menu. This sets inline CSS to set the height of the wrapper <div>
    // to make room for the dropdown.
    updateElement(dropdownEl) {
        const wrapperEl = this.hubscontrols;
        const dropdownHeight = dropdownEl.clientHeight;
        if (dropdownHeight === 0) {
            // The dropdown menu has closed
            wrapperEl.style.height = 'auto';
        } else {
            // The menu has dropped down
            wrapperEl.style.height = `${wrapperEl.clientHeight}${dropdownHeight}px`;
        }
    }

    // Handle a click in a See More link within the matrix (not for the facets)
    handleClick(groupKey) {
        const groupOpen = _.clone(this.state.yGroupOpen);
        groupOpen[groupKey] = !groupOpen[groupKey];
        this.setState({ yGroupOpen: groupOpen });
    }

    handleSeeAllClick() {
        this.setState((prevState) => {
            const newState = {};

            // If the See All button wasn't open (meaning this function was called because the user
            // wanted to see all), forget all the individual ones the user had opened so that
            // they're all closed when the user clicks See Fewer.
            if (!prevState.allYGroupsOpen) {
                const groupOpen = {};
                Object.keys(prevState.yGroupOpen).forEach((key) => {
                    groupOpen[key] = false;
                });
                newState.yGroupOpen = groupOpen;
            }

            // Toggle the state of allYGroupsOpen.
            newState.allYGroupsOpen = !prevState.allYGroupsOpen;
            return newState;
        });
    }

    /* eslint-disable no-loop-func */
    render() {
        const context = this.props.context;
        const matrix = context.matrix;
        const parsedUrl = url.parse(this.context.location_href);
        const matrixBase = parsedUrl.search || '';
        const matrixSearch = matrixBase + (matrixBase ? '&' : '?');
        const notification = context.notification;
        const visualizeLimit = 500;
        if (notification === 'Success' || notification === 'No results found') {
            const xFacets = matrix.x.facets.map(f => _.findWhere(context.facets, { field: f })).filter(f => f);
            let yFacets = matrix.y.facets.map(f => _.findWhere(context.facets, { field: f })).filter(f => f);
            yFacets = yFacets.concat(_.reject(context.facets, f => _.contains(matrix.x.facets, f.field) || _.contains(matrix.y.facets, f.field)));
            const xGrouping = matrix.x.group_by;
            const primaryYGrouping = matrix.y.group_by[0];
            const secondaryYGrouping = matrix.y.group_by[1];
            const xBuckets = matrix.x.buckets;
            const xLimit = matrix.x.limit || xBuckets.length;
            let yGroups = matrix.y[primaryYGrouping].buckets;
            // The following lines are to make sure that the audit categories are in the correct
            // order and to assign a proper title to each colored row.
            const orderKey = ['no_audits', 'audit.WARNING.category', 'audit.NOT_COMPLIANT.category',
                'audit.ERROR.category', 'audit.INTERNAL_ACTION.category'];
            const titleKey = ['No audits', 'Warning', 'Not Compliant', 'Error', 'Internal Action'];
            const noAuditKey = ['no errors, compliant, and no warnings', 'no errors and compliant',
                'no errors', 'no audits'];
            // For each group, compare against the key arrays above and format yGroups so that
            // it has the same order as the keys and each group in yGroups has the correct title.
            let orderIndex = 0;
            let rowIndex = 0;
            const tempYGroups = [];
            const tempNoAudits = [];
            while (orderIndex < orderKey.length) {
                yGroups.forEach((group) => {
                    if (group.key === orderKey[orderIndex]) {
                        if (group.key === 'no_audits') {
                            while (rowIndex < noAuditKey.length) {
                                group.audit_label.buckets.forEach((row) => {
                                    if (row.key === noAuditKey[rowIndex]) {
                                        tempNoAudits.push(row);
                                    }
                                });
                                rowIndex += 1;
                            }
                            group.audit_label.buckets = tempNoAudits;
                        }
                        group.title = titleKey[orderIndex];
                        tempYGroups.push(group);
                    }
                });
                orderIndex += 1;
            }
            yGroups = tempYGroups;
            const yGroupFacet = _.findWhere(context.facets, { field: primaryYGrouping });
            const yGroupOptions = yGroupFacet ? yGroupFacet.terms.map(term => term.key) : [];
            yGroupOptions.sort();
            const searchBase = context.matrix.search_base;
            const visualizeDisabled = matrix.doc_count > visualizeLimit;
            const colCount = Math.min(xBuckets.length, xLimit + 1);

            // Get a sorted list of batch hubs keys with case-insensitive sort
            // NOTE: Tim thinks this is overkill as opposed to simple sort()
            let visualizeKeys = [];
            if (context.visualize_batch && Object.keys(context.visualize_batch).length) {
                visualizeKeys = Object.keys(context.visualize_batch).sort((a, b) => {
                    const aLower = a.toLowerCase();
                    const bLower = b.toLowerCase();
                    return (aLower > bLower) ? 1 : ((aLower < bLower) ? -1 : 0);
                });
            }

            // Map view icons to svg icons
            const view2svg = {
                'list-alt': 'search',
                table: 'table',
            };

            // Make an array of colors corresponding to the ordering of audits
            // The last color doesn't appear unless you are logged in (DCC Action)
            // In order: Green, Yellow, Orange, Red, Gray
            const biosampleTypeColors = ['#009802', '#e0e000', '#ff8000', '#cc0700', '#a0a0a0'];
            const parsed = url.parse(matrixBase, true);
            const queryStringType = parsed.query.type || '';
            const type = pluralize(queryStringType.toLocaleLowerCase());

            return (
                <div>
                    <div className="panel data-display main-panel">
                        <div className="row matrix__facet--horizontal">
                            <div className="col-sm-5 col-md-4 col-lg-3 sm-no-padding" style={{ paddingRight: 0 }}>
                                <div className="row">
                                    <div className="col-sm-11">
                                        <div>
                                            <h1>{context.title}</h1>
                                            <div>
                                                <p>Enter search terms to filter the {type} included in the matrix.</p>
                                                <TextFilter filters={context.filters} searchBase={matrixSearch} onChange={this.onChange} />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="col-sm-7 col-md-8 col-lg-9 sm-no-padding" style={{ paddingLeft: 0 }}>
                                <FacetList
                                    facets={xFacets}
                                    filters={context.filters}
                                    orientation="horizontal"
                                    searchBase={matrixSearch}
                                    onFilter={this.onFilter}
                                />
                            </div>
                        </div>
                        <div className="row">
                            <div className="col-sm-5 col-md-4 col-lg-3 sm-no-padding" style={{ paddingRight: 0 }}>
                                <FacetList facets={yFacets} filters={context.filters} searchBase={matrixSearch} onFilter={this.onFilter} />
                            </div>
                            <div className="col-sm-7 col-md-8 col-lg-9 sm-no-padding">
                                <div className="matrix-wrapper">
                                    <div className="matrix-group-heading">
                                        <div className="matrix-group-heading__content">
                                            {matrix.y.label.toUpperCase()}
                                        </div>
                                    </div>
                                    <table className="matrix">
                                        <tbody>
                                            {matrix.doc_count ?
                                                <tr>
                                                    <th style={{ width: 20 }} />
                                                    <th colSpan={colCount + 1} style={{ padding: '5px', borderBottom: 'solid 1px #ddd', textAlign: 'center' }}>{matrix.x.label.toUpperCase()}</th>
                                                </tr>
                                            : null}
                                            <tr style={{ borderBottom: 'solid 1px #ddd' }}>
                                                <th style={{ textAlign: 'center', width: 200 }}>
                                                    <h3>
                                                        {matrix.doc_count} results
                                                    </h3>
                                                    <div className="btn-attached">
                                                        {matrix.doc_count && context.views ? context.views.map(view => <a href={view.href} key={view.icon} className="btn btn-info btn-sm btn-svgicon" title={view.title}>{svgIcon(view2svg[view.icon])}</a>) : ''}
                                                    </div>
                                                    {context.filters.length ?
                                                        <div className="clear-filters-control-matrix">
                                                            <a href={context.matrix.clear_matrix}>Clear Filters <i className="icon icon-times-circle" /></a>
                                                        </div>
                                                    : null}
                                                </th>
                                                {xBuckets.map((xb, i) => {
                                                    if (i < xLimit) {
                                                        const href = `${searchBase}&${xGrouping}=${globals.encodedURIComponent(xb.key)}`;
                                                        return <th key={i} className="rotate30" style={{ width: 10 }}><div><a title={xb.key} href={href}>{xb.key}</a></div></th>;
                                                    } else if (i === xLimit) {
                                                        const parsed = url.parse(matrixBase, true);
                                                        parsed.query['x.limit'] = null;
                                                        delete parsed.search; // this makes format compose the search string out of the query object
                                                        const unlimitedHref = url.format(parsed);
                                                        return <th key={i} className="rotate30" style={{ width: 10 }}><div><span><a href={unlimitedHref}>...and {xBuckets.length - xLimit} more</a></span></div></th>;
                                                    }
                                                    return null;
                                                })}
                                            </tr>
                                            {yGroups.map((group, i) => {
                                                const groupColor = biosampleTypeColors[i];
                                                const seriesColor = color(groupColor);
                                                const parsed = url.parse(matrixBase, true);
                                                const searchTerm = '*'; // shows all of certain audit category
                                                parsed.query[group.key] = searchTerm;
                                                parsed.query['y.limit'] = null;
                                                delete parsed.search; // this makes format compose the search string out of the query object
                                                let groupHref = url.format(parsed);
                                                // Change groupHref to the proper url if it is the no_audits row.
                                                if (group.key === 'no_audits') {
                                                    groupHref = '?type=Experiment&status=released&audit.ERROR.category!=*&audit.NOT_COMPLIANT.category!=*&audit.WARNING.category!=*&audit.INTERNAL_ACTION.category!=*&y.limit=';
                                                }
                                                // The next 2 lines make the category title text
                                                // color white or black based on the background
                                                // color.
                                                const rowColor = seriesColor.clone();
                                                const categoryTextColor = rowColor.luminosity() > 0.5 ? '#000' : '#fff';
                                                const rows = [
                                                    <tr key={group.key}>
                                                        <th colSpan={colCount + 1} style={{ textAlign: 'left', backgroundColor: groupColor }}>
                                                            <a href={groupHref} style={{ color: categoryTextColor }}>{group.title}</a>
                                                        </th>
                                                    </tr>,
                                                ];
                                                const groupBuckets = group[secondaryYGrouping].buckets;
                                                const yLimit = matrix.y.limit || groupBuckets.length;

                                                // If this group isn't open (noted by
                                                // this.state.yGroupOpen[key]), extract just the
                                                // group rows that are under the display limit.
                                                const groupRows = (this.state.yGroupOpen[group.key] || this.state.allYGroupsOpen) ? groupBuckets : groupBuckets.slice(0, yLimit);
                                                rows.push(...groupRows.map((yb) => {
                                                    let href = `${searchBase}&${group.key}=${globals.encodedURIComponent(yb.key)}`;
                                                    // The following lines give the proper urls to the no audits sub rows.
                                                    if (yb.key === 'no errors') {
                                                        href = `${searchBase}&audit.ERROR.category!=*`;
                                                    }
                                                    if (yb.key === 'no errors and compliant') {
                                                        href = `${searchBase}&audit.ERROR.category!=*&audit.NOT_COMPLIANT.category!=*`;
                                                    }
                                                    if (yb.key === 'no errors, compliant, and no warnings') {
                                                        href = `${searchBase}&audit.ERROR.category!=*&audit.NOT_COMPLIANT.category!=*&audit.WARNING.category!=*`;
                                                    }
                                                    if (yb.key === 'no audits') {
                                                        href = `${searchBase}&audit.ERROR.category!=*&audit.NOT_COMPLIANT.category!=*&audit.WARNING.category!=*&audit.INTERNAL_ACTION.category!=*`;
                                                    }
                                                    return (
                                                        <tr key={yb.key}>
                                                            <th style={{ backgroundColor: '#ddd', border: 'solid 1px white' }}><a href={href}>{yb.key}</a></th>
                                                            {xBuckets.map((xb, k) => {
                                                                if (k < xLimit) {
                                                                    const value = yb[xGrouping][k];
                                                                    const cellColor = seriesColor.clone();
                                                                    // scale color between white and the series color
                                                                    cellColor.lightness(cellColor.lightness() + ((1 - (value / matrix.max_cell_doc_count)) * (100 - cellColor.lightness())));
                                                                    const textColor = cellColor.luminosity() > 0.5 ? '#000' : '#fff';
                                                                    const cellHref = `${href}&${xGrouping}=${globals.encodedURIComponent(xb.key)}`;
                                                                    const title = `${yb.key} / ${xb.key}: ${value}`;
                                                                    return (
                                                                        <td key={xb.key} style={{ backgroundColor: cellColor.hexString() }}>
                                                                            {value ? <a href={cellHref} style={{ color: textColor }} title={title}>{value}</a> : null}
                                                                        </td>
                                                                    );
                                                                }
                                                                return null;
                                                            })}
                                                            {xBuckets.length > xLimit && <td />}
                                                        </tr>
                                                    );
                                                }));
                                                if (groupBuckets.length > yLimit && !this.state.allYGroupsOpen) {
                                                    rows.push(
                                                        <tr>
                                                            <th className="group-more-cell">
                                                                <GroupMoreButton
                                                                    id={group.key}
                                                                    handleClick={this.handleClick}
                                                                    displayText={this.state.yGroupOpen[group.key] ? '- See fewer' : `+ See ${groupBuckets.length - yLimit} more…`}
                                                                />
                                                            </th>
                                                            {_.range(colCount - 1).map(n => <td key={n} />)}
                                                        </tr>
                                                    );
                                                }
                                                return rows;
                                            })}

                                            {/* Display the See Fewer/See All button controlling
                                                the whole table if at least one biosample_ontology has
                                                more than the limit. We know this is the case if at
                                                least one yGroupOpen state member exists. */}
                                            {Object.keys(this.state.yGroupOpen).length ?
                                                <tr>
                                                    <th className="group-all-groups-cell">
                                                        <button className="group-all-groups-cell__button" onClick={this.handleSeeAllClick}>
                                                            {this.state.allYGroupsOpen ? 'See fewer audits' : 'See all audits'}
                                                        </button>
                                                    </th>
                                                </tr>
                                            : null}
                                        </tbody>
                                    </table>
                                </div>
                                <div className="hubs-controls" ref={(div) => { this.hubscontrols = div; }}>
                                    {context.batch_download ?
                                        <BatchDownload context={context} />
                                    : null}
                                    {' '}
                                    {visualizeKeys.length ?
                                        <BrowserSelector
                                            visualizeCfg={context.visualize_batch}
                                            disabled={visualizeDisabled}
                                            title={visualizeDisabled ? `Filter to ${visualizeLimit} to visualize` : 'Visualize'}
                                        />
                                    : null}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            );
        }
        return <h4>{notification}</h4>;
    }
    /* eslint-enable no-loop-func */
}

AuditMatrix.propTypes = {
    context: React.PropTypes.object.isRequired,
};

AuditMatrix.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    biosampleTypeColors: PropTypes.object, // DataColor instance for experiment project
    auditCategoryColors: PropTypes.object,
};

globals.contentViews.register(AuditMatrix, 'AuditMatrix');
