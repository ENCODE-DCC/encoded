import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import url from 'url';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../libs/ui/modal';
import { Panel, PanelBody } from '../libs/ui/panel';
import { FetchedData, Param } from './fetched';
import * as globals from './globals';
import { FacetList } from './search';
import { ViewControls } from './view_controls';


function columnChoices(schema, selected) {
    // start with id
    const columns = {};
    columns['@id'] = {
        title: 'ID',
        visible: true,
    };
    // default selected columns are the schema's `columns`,
    // or whichever of title, description, name, accession & aliases
    // are found in the schema's properties
    // (note, this has to match the defaults sent from the server)
    let schemaColumns = schema.columns;
    const defaultColumns = { title: 'Title', description: 'Description', name: 'Name', accession: 'Accession', aliases: 'Aliases' };
    if (schemaColumns === undefined) {
        schemaColumns = {};
        Object.keys(defaultColumns).forEach((name) => {
            if (schema.properties[name] !== undefined) {
                schemaColumns[name] = { title: defaultColumns[name], type: 'string' };
            }
        });
    }
    // add embedded columns
    _.each(schemaColumns, (column, path) => {
        columns[path] = {
            title: column.title,
            visible: !selected,
        };
    });

    // add all properties (with a few exceptions)
    const schemaColumnTitles = Object.keys(schemaColumns).map(schemaColumnsProperty => schemaColumns[schemaColumnsProperty].title);
    const filteredSchemaProperties = Object.keys(schema.properties).filter((schemaProperty) => {
        const schemaPropertyTitle = schema.properties[schemaProperty].title;
        return schemaColumnTitles.indexOf(schemaPropertyTitle) === -1 && ['@id', '@type', 'uuid', 'replicates'].indexOf(schemaProperty) === -1;
    });
    filteredSchemaProperties.forEach((schemaProperty) => {
        const title = schema.properties[schemaProperty].title;
        if (!Object.prototype.hasOwnProperty.call(columns, schemaProperty) && title) {
            columns[schemaProperty] = {
                title,
                visible: false,
            };
        }
    });

    // if selected fields are specified, update visibility
    if (selected) {
        // Reset @id to not visible if not in selected
        if (!selected['@id'] && columns['@id']) {
            columns['@id'].visible = false;
        }
        _.each(selected, (path) => {
            if (columns[path] === undefined) {
                columns[path] = {
                    title: path,
                    visible: true,
                };
            } else {
                columns[path].visible = true;
            }
        });
    }

    return columns;
}


function getVisibleColumns(columns) {
    const visibleColumns = [];
    _.mapObject(columns, (column, path) => {
        if (column.visible) {
            visibleColumns.push({
                path,
                title: column.title,
            });
        }
    });
    return visibleColumns;
}


function lookupColumn(result, column) {
    let nodes = [result];
    const names = column.split('.');

    // Get the column's custom display function and call it if it exists
    const colViewer = globals.reportCell.lookup(result, column);
    if (colViewer) {
        const colViewResult = colViewer(result, column);
        if (colViewResult) {
            return <div>{colViewResult}</div>;
        }
    }

    for (let i = 0, len = names.length; i < len && nodes.length > 0; i += 1) {
        let nextnodes = [];
        _.each(nodes.map(node => node[names[i]]), (v) => {
            if (v === undefined) return;
            if (Array.isArray(v)) {
                nextnodes = nextnodes.concat(v);
            } else {
                nextnodes.push(v);
            }
        });
        if (names[i + 1] === 'length' || names[i + 1] === 'uuid') {
            // Displaying the length of an array. That's not a property of each array element so we
            // can't get it that way. Just return the length of the array.
            nodes = [nextnodes.length];
            break;
        } else {
            // Moving on to the next node defined by the `names` array.
            nodes = nextnodes;
        }
    }
    // if we ended with an embedded object, show the @id
    if (nodes.length > 0 && nodes[0]['@id'] !== undefined) {
        nodes = nodes.map(node => node['@id']);
    }

    // Stringify any nodes that are objects or arrays. Objects and arrays have typeof `object`.
    if (nodes.length > 0) {
        nodes = nodes.map(item => (typeof item === 'object' ? JSON.stringify(item) : item));
    }

    return _.uniq(nodes).join(', ');
}


class Cell {
    constructor(value, type) {
        this.value = value;
        this.type = type;
    }
}


class Row {
    constructor(item, cells) {
        this.item = item;
        this.cells = cells;
    }
}


function RowView(rowInfo) {
    const row = rowInfo.row;
    const id = row.item['@id'];
    const tds = row.cells.map((cell, index) => {
        const cellValue = cell.value;
        if (cell.type === 'thumb_nail') {
            return (
                <td key={index}>
                    <div className="tcell-thumbnail">
                        <a href={cellValue} target="_blank" rel="noopener noreferrer">
                            <img src={cellValue} alt={cellValue} />
                        </a>
                    </div>
                </td>
            );
        } else if (cell.type === 'download_url') {
            return (
                <td key={index}>
                    <a href={cellValue}>{`${window.location.origin}${cellValue}`}</a>
                </td>
            );
        } else if (index === 0) {
            return (
                <td key={index}><a href={row.item['@id']}>{cellValue}</a></td>
            );
        }

        return (
            <td key={index}>{cellValue}</td>
        );
    });
    return (
        <tr key={id}>{tds}</tr>
    );
}


class Table extends React.Component {
    constructor() {
        super();

        // Bind this to non-React methods.
        this.setSort = this.setSort.bind(this);
        this.extractData = this.extractData.bind(this);
        this.getSort = this.getSort.bind(this);
    }

    setSort(path) {
        const sort = this.getSort();
        const column = sort.column === path && !sort.reversed ? `-${path}` : path;
        this.props.setSort(column);
    }

    getSort() {
        if (this.props.context.sort) {
            const sortColumn = Object.keys(this.props.context.sort)[0];
            return {
                column: sortColumn,
                reversed: this.props.context.sort[sortColumn].order === 'desc',
            };
        }
        return {};
    }

    extractData(items) {
        const columns = getVisibleColumns(this.props.columns);
        const rows = items.map((item) => {
            const cells = columns.map((column) => {
                let factory;
                let value = lookupColumn(item, column.path);
                if (column.path === '@id') {
                    factory = globals.listingTitles.lookup(item);
                    value = factory({ context: item });
                } else if (value === null || value === undefined) {
                    value = '';
                } else if (!(value instanceof Array) && value['@type']) {
                    factory = globals.listingTitles.lookup(value);
                    value = factory({ context: value });
                }
                return new Cell(value, column.path);
            });
            return new Row(item, cells);
        });
        return rows;
    }

    render() {
        const context = this.props.context;
        const columns = getVisibleColumns(this.props.columns);
        const sort = this.getSort();

        const headers = columns.map((column, index) => {
            const sortable = context.non_sortable.indexOf(column.path) === -1;
            return <ColumnHeader key={index} setSort={this.setSort} sortable={sortable} column={column} sort={sort} reversed={sort.reversed} />;
        });

        const data = this.extractData(context['@graph']).concat(this.extractData(this.props.more));
        const rows = data.map(row => RowView({ row }));
        const tableClass = 'collection-table';
        return (
            <div className="report__table">
                <table className={`${tableClass} table table-panel table-striped`}>
                    <thead>
                        <tr className="col-headers">{headers}</tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>
        );
    }
}

Table.propTypes = {
    setSort: PropTypes.func.isRequired,
    context: PropTypes.object.isRequired,
    columns: PropTypes.object.isRequired,
    more: PropTypes.array.isRequired,
};

Table.contextTypes = {
    location_href: PropTypes.string,
};


class ColumnHeader extends React.Component {
    constructor() {
        super();

        // Bind this to non-React methods.
        this.setSort = this.setSort.bind(this);
    }

    setSort() {
        if (this.props.sortable) {
            this.props.setSort(this.props.column.path);
        }
    }

    render() {
        const { column, sort, reversed, sortable } = this.props;

        let columnClass;
        if (sortable) {
            if (column.path === sort.column) {
                columnClass = reversed ? 'tcell-desc' : 'tcell-asc';
            } else {
                columnClass = 'tcell-sort';
            }
        } else {
            columnClass = null;
        }

        return (
            <th onClick={this.setSort} className={sortable ? 'tcell-sortable' : null}>
                <div className={sortable ? 'tcell-sortable__column-header' : null}>
                    {column.title}
                    <i className={columnClass} />
                </div>
            </th>
        );
    }
}

ColumnHeader.propTypes = {
    /** Column whose header is being displayed */
    column: PropTypes.object.isRequired,
    /** Column sort information */
    sort: PropTypes.object.isRequired,
    /** Parent function to handle a click in a column header */
    setSort: PropTypes.func,
    /** True if column sort is reversed */
    reversed: PropTypes.bool,
    /** True if column is sortable */
    sortable: PropTypes.bool,
};

ColumnHeader.defaultProps = {
    setSort: null,
    reversed: false,
    sortable: true,
};


class ColumnSelectorControls extends React.Component {
    constructor() {
        super();

        // Set initial React state.
        this.state = {
            selectedSort: 'default',
        };

        // Bind `this` to non-React methods.
        this.handleSortChange = this.handleSortChange.bind(this);
    }

    handleSortChange(e) {
        // Called when the user changes the sorting option. Sets a component state so that the
        // controlled <select> component renders properly. It then calls the parent's callback to
        // react to the new sorting option.
        this.setState({ selectedSort: e.target.value });
        this.props.handleSortChange(e.target.value);
    }

    render() {
        const { handleSelectAll, handleSelectOne, firstColumnTitle } = this.props;

        return (
            <div className="column-selector__controls">
                <div className="column-selector__utility-buttons">
                    <button onClick={handleSelectAll} className="btn btn-info">Select all</button>
                    <button onClick={handleSelectOne} className="btn btn-info">Select {firstColumnTitle} only</button>
                </div>
                <div className="column-selector__sort-selector">
                    <select className="form-control--select" value={this.state.selectedSort} onChange={this.handleSortChange}>
                        <option value="default">Default sort</option>
                        <option value="alpha">Alphabetical sort</option>
                    </select>
                </div>
            </div>
        );
    }
}

ColumnSelectorControls.propTypes = {
    handleSelectAll: PropTypes.func.isRequired, // Callback when Select All button clicked
    handleSelectOne: PropTypes.func.isRequired, // Callback when SelectOne button clicked
    handleSortChange: PropTypes.func.isRequired, // Callback when sorting option changed
    firstColumnTitle: PropTypes.string.isRequired, // Title of first column
};


/**
 * Extract the list of column paths from `columns`, with an order according to the given sorting
 * option.
 *
 * @param {object} columns - Object with column states controlled by <Report> component.
 * @param {string} sortOption - Current sort option; 'default' or 'alpha' currently.
 * @return (array) - List of column paths, optionally sorted.
 */
function getColumnPaths(columns, sortOption) {
    const columnPaths = Object.keys(columns);
    if (sortOption === 'alpha') {
        columnPaths.sort((aKey, bKey) => {
            const aTitle = columns[aKey].title.toLowerCase();
            const bTitle = columns[bKey].title.toLowerCase();
            return (aTitle < bTitle ? -1 : (bTitle < aTitle ? 1 : 0));
        });
    }
    return columnPaths;
}


// Displays a modal dialog with every possible column for the type of object being displayed.
// This lets you choose which columns you want to appear in the report.
class ColumnSelector extends React.Component {
    constructor(props) {
        super(props);

        // Set the initial React states.
        this.state = {
            columns: props.columns, // Make (effectively) a local mutatable copy of the columns
            sortOption: 'default', // Default sorting option
        };

        // Bind `this` to non-React methods.
        this.submitHandler = this.submitHandler.bind(this);
        this.toggleColumn = this.toggleColumn.bind(this);
        this.handleSelectAll = this.handleSelectAll.bind(this);
        this.handleSelectOne = this.handleSelectOne.bind(this);
        this.handleSortChange = this.handleSortChange.bind(this);
    }

    toggleColumn(columnPath) {
        // Called every time a column's checkbox gets clicked on or off in the modal. `columnPath`
        // is the query-string term corresponding to each column. First, if the column is getting
        // turned off, make sure we have at least one other column selected, because at least one
        // column has to be selected.
        if (this.state.columns[columnPath].visible) {
            // The clicked column is currently visible, so before we make it invisible, make sure
            // at least one other column is also visible.
            const allColumnKeys = Object.keys(this.state.columns);
            const anotherVisible = allColumnKeys.some(key => key !== columnPath && this.state.columns[key].visible);
            if (!anotherVisible) {
                // A checkbox is being turned off, and no other checkbox is checked, so ignore the
                // click.
                return;
            }
        }

        // Either a checkbox is being turned on, or it's being turned off and another checkbox is
        // still checked. Change the component state to reflect the new checkbox states. Presumably
        // if the setState callback returned no properties setState becomes a null op, so the above
        // test could be done inside the setState callback. The React docs don't say what happens
        // if you return no properties (https://reactjs.org/docs/react-component.html#setstate) so
        // I avoided doing this.
        this.setState((prevState) => {
            // Toggle the `visible` state corresponding to the column whose checkbox was toggled.
            // Then set that as the new React state which causes a redraw of the modal with all the
            // checkboxes in the correct state.
            const columns = Object.assign({}, prevState.columns);
            columns[columnPath] = Object.assign({}, columns[columnPath]);
            columns[columnPath].visible = !columns[columnPath].visible;
            return { columns };
        });
    }

    submitHandler() {
        // Called when the user clicks the Select button in the column checkbox modal, which
        // sets a new state for all checked report columns.
        this.props.setColumnState(this.state.columns);
    }

    handleSelectAll() {
        // Called when the "Select all" button is clicked.
        this.setState((prevState) => {
            // For every column in this.state.columns, set its `visible` property to true.
            const columns = Object.assign({}, prevState.columns);
            Object.keys(columns).forEach((columnPath) => {
                columns[columnPath] = Object.assign({}, columns[columnPath]);
                columns[columnPath].visible = true;
            });
            return { columns };
        });
    }

    handleSelectOne() {
        // Called when the "Select (first) only" button is clicked.
        this.setState((prevState) => {
            // Set all columns to invisible first.
            const columns = Object.assign({}, prevState.columns);
            const columnPaths = Object.keys(columns);
            columnPaths.forEach((columnPath) => {
                columns[columnPath] = Object.assign({}, columns[columnPath]);
                columns[columnPath].visible = false;
            });

            // Now set the column for the first key to true so that only it's selected.
            columns[columnPaths[0]].visible = true;
            return { columns };
        });
    }

    // Called when the sorting option gets changed.
    handleSortChange(sortOption) {
        this.setState({ sortOption });
    }

    render() {
        const { columns } = this.state;
        const firstColumnKey = Object.keys(columns)[0];

        // Get the column paths, sorting them by the corresponding column title if the user asked
        // for that.
        const columnPaths = getColumnPaths(columns, this.state.sortOption);

        return (
            <Modal addClasses="column-selector">
                <ModalHeader title="Select columns to view" closeModal={this.props.closeSelector} />
                <ColumnSelectorControls
                    handleSelectAll={this.handleSelectAll}
                    handleSelectOne={this.handleSelectOne}
                    handleSortChange={this.handleSortChange}
                    firstColumnTitle={columns[firstColumnKey].title}
                />
                <ModalBody>
                    <div className="column-selector__selectors">
                        {columnPaths.map((columnPath) => {
                            const column = columns[columnPath];
                            return <ColumnItem key={columnPath} columnPath={columnPath} column={column} toggleColumn={this.toggleColumn} />;
                        })}
                    </div>
                </ModalBody>
                <ModalFooter
                    closeModal={this.props.closeSelector}
                    submitBtn={this.submitHandler}
                    submitTitle="View selected columns"
                />
            </Modal>
        );
    }
}

ColumnSelector.propTypes = {
    columns: PropTypes.object.isRequired,
    setColumnState: PropTypes.func.isRequired,
    closeSelector: PropTypes.func.isRequired,
};


// Render one column selector item.
class ColumnItem extends React.Component {
    constructor() {
        super();

        // Bind this to non-React methods.
        this.toggleColumn = this.toggleColumn.bind(this);
    }

    toggleColumn() {
        this.props.toggleColumn(this.props.columnPath);
    }

    render() {
        const { column } = this.props;

        /* eslint-disable jsx-a11y/click-events-have-key-events, jsx-a11y/no-static-element-interactions */
        return (
            <div className="column-selector__selector-item">
                <input type="checkbox" onChange={this.toggleColumn} checked={column.visible} />&nbsp;
                <span onClick={this.toggleColumn} style={{ cursor: 'pointer' }}>{column.title}</span>
            </div>
        );
        /* eslint-enable jsx-a11y/click-events-have-key-events, jsx-a11y/no-static-element-interactions */
    }
}

ColumnItem.propTypes = {
    columnPath: PropTypes.string.isRequired, // encoded path for the column
    column: PropTypes.object.isRequired, // Column information
    toggleColumn: PropTypes.func.isRequired, // Parent function to call when item is clicked
};


class Report extends React.Component {
    constructor(props, context) {
        super(props, context);

        // Set initial React state.
        const parsedUrl = url.parse(context.location_href, true);
        const from = parseInt(parsedUrl.query.from, 10) || 0;
        const size = parseInt(parsedUrl.query.limit, 10) || 25;
        this.state = {
            from,
            size,
            to: from + size,
            more: [],
            selectorOpen: false, // True if column selector modal is open
        };

        // Bind this to non-React methods.
        this.setSort = this.setSort.bind(this);
        this.setColumnState = this.setColumnState.bind(this);
        this.loadMore = this.loadMore.bind(this);
        this.handleSelectorClick = this.handleSelectorClick.bind(this);
        this.closeSelector = this.closeSelector.bind(this);
    }

    componentWillReceiveProps(nextProps, nextContext) {
        // reset pagination when filter is changed
        if (nextContext.location_href !== this.context.location_href) {
            const parsedUrl = url.parse(this.context.location_href, true);
            const from = parseInt(parsedUrl.query.from, 10) || 0;
            const size = parseInt(parsedUrl.query.limit, 10) || 25;
            this.setState({
                from,
                to: from + size,
                more: [],
            });
        }
    }

    componentWillUnmount() {
        if (this.state.request) this.state.request.abort();
    }

    setSort(sort) {
        const parsedUrl = url.parse(this.context.location_href, true);
        parsedUrl.query.sort = sort;
        delete parsedUrl.search;
        this.context.navigate(url.format(parsedUrl));
    }

    setColumnState(newColumns) {
        // Gets called when the user clicks the Select button in the ColumnSelector modal.
        // `newColumns` has the same format as `columns` returned from `columnChoices`, but
        // `newColumns` has the user's chosen columns from the modal, while `columns` has the
        // columns selected by the query string.
        const parsedUrl = url.parse(this.context.location_href, true);
        parsedUrl.query.field = Object.keys(newColumns).filter(columnPath => newColumns[columnPath].visible);
        delete parsedUrl.search;
        this.context.navigate(url.format(parsedUrl));
    }

    loadMore() {
        if (this.state.request) {
            this.state.request.abort();
        }
        const parsedUrl = url.parse(this.context.location_href, true);
        parsedUrl.query.from = this.state.to;
        delete parsedUrl.search;
        const request = this.context.fetch(url.format(parsedUrl), {
            headers: { Accept: 'application/json' },
        });
        request.then((response) => {
            if (!response.ok) throw response;
            return response.json();
        }).catch(globals.parseAndLogError.bind(undefined, 'loadMore')).then((data) => {
            this.setState({
                more: this.state.more.concat(data['@graph']),
                request: null,
            });
        });

        this.setState({
            request,
            to: this.state.to + this.state.size,
        });
    }

    handleSelectorClick() {
        // Handle click on the column selector button by opening the modal.
        this.setState({ selectorOpen: true });
    }

    closeSelector() {
        // Close the column selector modal.
        this.setState({ selectorOpen: false });
    }

    render() {
        const parsedUrl = url.parse(this.context.location_href, true);
        if (parsedUrl.pathname.indexOf('/report') !== 0) return false; // avoid breaking on re-render when navigate changes href before context is changed
        const context = this.props.context;
        let searchBase = parsedUrl.search || '';
        searchBase += searchBase ? '&' : '?';

        const type = parsedUrl.query.type;
        const schema = this.props.schemas[type];
        let queryFields = parsedUrl.query.field;
        if (typeof queryFields === 'string') {
            queryFields = [queryFields];
        }
        const columns = columnChoices(schema, queryFields);

        // Compose download-TSV link.
        const downloadTsvPath = `/report.tsv${parsedUrl.path.slice(parsedUrl.pathname.length)}`;

        /* eslint-disable jsx-a11y/click-events-have-key-events, jsx-a11y/no-static-element-interactions */
        return (
            <Panel>
                <PanelBody>
                    <div className="search-results">
                        <div className="search-results__facets">
                            <FacetList context={context} facets={context.facets} filters={context.filters} searchBase={searchBase} docTypeTitleSuffix="report" />
                        </div>
                        <div className="search-results__report-list">
                            <h4>Showing results {this.state.from + 1} to {Math.min(context.total, this.state.to)} of {context.total}</h4>
                            <div className="results-table-control">
                                <div className="results-table-control__main">
                                    <ViewControls results={context} />
                                    <button className="btn btn-info btn-sm" title="Choose columns" onClick={this.handleSelectorClick}>
                                        <i className="icon icon-columns" /> Columns
                                    </button>
                                    <a className="btn btn-info btn-sm" href={downloadTsvPath} data-bypass data-test="download-tsv">Download TSV</a>
                                </div>
                            </div>
                            <Table context={context} more={this.state.more} columns={columns} setSort={this.setSort} />
                            {this.state.to < context.total ?
                                <button className="btn btn-info btn-sm" onClick={this.loadMore}>Load more</button>
                            : null}
                        </div>
                        {this.state.selectorOpen ?
                            <ColumnSelector
                                columns={columns}
                                setColumnState={this.setColumnState}
                                closeSelector={this.closeSelector}
                            />
                        : null}
                    </div>
                </PanelBody>
            </Panel>
        );
        /* eslint-enable jsx-a11y/click-events-have-key-events, jsx-a11y/no-static-element-interactions */
    }
}

Report.propTypes = {
    context: PropTypes.object.isRequired,
    schemas: PropTypes.object, // Actually required, but comes from a GET request.
};

Report.defaultProps = {
    schemas: null,
};

Report.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    fetch: PropTypes.func,
};


const ReportLoader = props => (
    <FetchedData>
        <Param name="schemas" url="/profiles/" />
        <Report context={props.context} />
    </FetchedData>
);

ReportLoader.propTypes = {
    context: PropTypes.object.isRequired,
};

globals.contentViews.register(ReportLoader, 'Report');


// Custom cell-display function example.
// var CustomCellDisplay = function(item, column property name) {
//     if (displayCondition) {
//        return (
//            <span>{display}</span>
//        );
//     }
//
//     // No custom display necessary for the requested column
//     return null;
// };


// Register cell-display components
// globals.reportCell.register(CustomCellDisplay, @type[0] in quotes, column property name in quotes);
