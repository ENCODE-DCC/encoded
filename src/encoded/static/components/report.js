import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import url from 'url';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../libs/bootstrap/modal';
import { svgIcon } from '../libs/svg-icons';
import { FetchedData, Param } from './fetched';
import * as globals from './globals';
import { FacetList } from './search';
import StickyHeader from './StickyHeader';


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
    _.each(schema.properties, (property, name) => {
        if (name === '@id' || name === '@type' || name === 'uuid' || name === 'replicates') return;
        if (!Object.prototype.hasOwnProperty.call(columns, name) && property.title) {
            columns[name] = {
                title: property.title,
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

    for (let i = 0, len = names.length; i < len && nodes.length; i += 1) {
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
    if (nodes.length && nodes[0]['@id'] !== undefined) {
        nodes = nodes.map(node => node['@id']);
    }
    return _.uniq(nodes).join(', ');
}


class Cell {
    constructor(value) {
        this.value = value;
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
        if (index === 0) {
            return (
                <td key={index}><a href={row.item['@id']}>{cell.value}</a></td>
            );
        }
        return (
            <td key={index}>{cell.value}</td>
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
                return new Cell(value);
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
            let className = 'icon';
            if (column.path === sort.column) {
                className += sort.reversed ? ' icon-chevron-up' : ' icon-chevron-down';
            }
            return <ColumnHeader key={index} setSort={this.setSort} column={column} className={className} />;
        });

        const data = this.extractData(context['@graph']).concat(this.extractData(this.props.more));
        const rows = data.map(row => RowView({ row }));
        const tableClass = 'sticky-area collection-table';
        return (
            <div className="table-responsive">
                <table className={`${tableClass} table table-striped table-hover table-panel`}>
                    <StickyHeader>
                        <thead className="sticky-header">
                            <tr className="col-headers">{headers}</tr>
                        </thead>
                    </StickyHeader>
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
        this.props.setSort(this.props.column.path);
    }

    render() {
        const { column, className } = this.props;

        return (
            <th onClick={this.setSort}>
                {column.title}&nbsp;<i className={className} />
            </th>
        );
    }
}

ColumnHeader.propTypes = {
    setSort: PropTypes.func, // Parent function to handle a click in a column header
    column: PropTypes.object,
    className: PropTypes.string, // CSS class string for column title
};


class ColumnSelector extends React.Component {
    constructor(props) {
        super();

        // Set the initial React states.
        this.state = {
            columns: props.columns, // Make (effectively) a local mutatable copy of the columns
        };

        // Bind `this` to non-React methods.
        this.submitHandler = this.submitHandler.bind(this);
        this.toggleColumn = this.toggleColumn.bind(this);
    }

    toggleColumn(columnPath) {
        this.setState((prevState) => {
            prevState.columns[columnPath].visible = !prevState.columns[columnPath].visible;
            return { columns: prevState.columns };
        });
    }

    submitHandler(e) {
    }

    render() {
        const { columns } = this.props;
        const columnPaths = Object.keys(columns);

        return (
            <Modal
                actuator={
                    <button className="btn btn-info btn-sm" title="Choose columns">
                        <i className="icon icon-columns" /> Columns
                    </button>
                }
                addClasses="column-selector"
            >
                <ModalHeader title="Select columns to view" closeModal />
                <ModalBody>
                    <div className="column-selector__selectors">
                        {columnPaths.map((columnPath) => {
                            const column = this.state.columns[columnPath];
                            return <ColumnItem key={columnPath} columnPath={columnPath} column={column} toggleColumn={this.toggleColumn} />;
                        })}
                    </div>
                </ModalBody>
                <ModalFooter
                    closeModal
                    submitBtn={<button className="btn btn-info" onClick={this.submitHandler}>Set</button>}
                />
            </Modal>
        );
    }
}

ColumnSelector.propTypes = {
    columns: PropTypes.object.isRequired,
    toggleColumn: PropTypes.func.isRequired,
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

        return (
            <div className="column-selector__selector-item">
                <input type="checkbox" onChange={this.toggleColumn} checked={column.visible} />&nbsp;
                <span onClick={this.toggleColumn} style={{ cursor: 'pointer' }}>{column.title}</span>
            </div>
        );
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
            loading: false,
            more: [],
        };

        // Bind this to non-React methods.
        this.setSort = this.setSort.bind(this);
        this.toggleColumn = this.toggleColumn.bind(this);
        this.loadMore = this.loadMore.bind(this);
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

    toggleColumn(toggledPath) {
        const parsedUrl = url.parse(this.context.location_href, true);
        const type = parsedUrl.query.type;
        const schema = this.props.schemas[type];
        const queryFields = parsedUrl.query.field ? (typeof parsedUrl.query.field === 'object' ? parsedUrl.query.field : [parsedUrl.query.field]) : undefined;
        const columns = columnChoices(schema, queryFields);

        const fields = [];
        _.mapObject(columns, (column, path) => {
            if (path === toggledPath ? !column.visible : column.visible) {
                fields.push(path);
            }
        });
        parsedUrl.query.field = fields;
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
        })
        .catch(globals.parseAndLogError.bind(undefined, 'loadMore'))
        .then((data) => {
            this.setState({
                more: this.state.more.concat(data['@graph']),
                loading: false,
                request: null,
            });
        });

        this.setState({
            request,
            to: this.state.to + this.state.size,
            loading: true,
        });
    }

    render() {
        const parsedUrl = url.parse(this.context.location_href, true);
        if (parsedUrl.pathname.indexOf('/report') !== 0) return false;  // avoid breaking on re-render when navigate changes href before context is changed
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

        // Map view icons to svg icons
        const view2svg = {
            'list-alt': 'search',
            th: 'matrix',
        };

        return (
            <div>
                <div className="panel data-display main-panel">
                    <div className="row">
                        <div className="col-sm-5 col-md-4 col-lg-3">
                            <FacetList facets={context.facets} filters={context.filters} searchBase={searchBase} />
                        </div>
                        <div className="col-sm-7 col-md-8 col-lg-9">
                            <h4>
                                Showing results {this.state.from + 1} to {Math.min(context.total, this.state.to)} of {context.total}
                            </h4>
                            <div className="results-table-control">
                                <div className="btn-attached">
                                    {context.views && context.views.map((view, i) => {
                                        // Strip any `field` properties out of the view's href as
                                        // they don't apply to search or matrix
                                        const parsedViewUrl = url.parse(view.href, true);
                                        delete parsedViewUrl.query.field;
                                        delete parsedViewUrl.search;
                                        const href = url.format(parsedViewUrl);
                                        return <a href={href} className="btn btn-info btn-sm btn-svgicon" title={view.title} key={i}>{svgIcon(view2svg[view.icon])}</a>;
                                    })}
                                </div>
                                <ColumnSelector columns={columns} toggleColumn={this.toggleColumn} />
                                <a className="btn btn-info btn-sm" href={context.download_tsv} data-bypass>Download TSV</a>
                            </div>
                            <Table context={context} more={this.state.more} columns={columns} setSort={this.setSort} />
                            {this.state.to < context.total &&
                                <h4 className={this.state.loading ? 'communicating' : ''}>
                                    {this.state.loading ?
                                        <div className="loading-spinner" />
                                    : <a className="btn btn-info btn-sm" onClick={this.loadMore}>Load more</a>} Showing
                                    results {this.state.from + 1} to {Math.min(context.total, this.state.to)} of {context.total}
                                </h4>
                            }
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

Report.propTypes = {
    context: PropTypes.object,
    schemas: PropTypes.object,
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
    context: PropTypes.object,
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
