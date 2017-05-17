import React from 'react';
import PropTypes from 'prop-types';
import url from 'url';
import globals from './globals';
import StickyHeader from './StickyHeader';


// Get the value of the column whose property name is passed in `column`. Column can hold a dotted
// embedded field specification. Pass the object to search in `result`. The `column` property's
// value, if found in `result`, gets returned. This could be an individual value, an object, or an
// array.

function lookupColumn(result, column) {
    let value = result;

    // Make an array of column property elements. It could be an embedded property with elements
    // separated by dots, so make an array of strings of each element between the dots. For a
    // column property with no dots, you get a single-element array with just the given column
    // property.
    const names = column.split('.');

    // Search the object given in `result` for a property matching an element of the `names` array,
    // going through emebedded properties if needed.
    for (let i = 0, len = names.length; i < len && value !== undefined; i += 1) {
        value = value[names[i]];
    }
    return value !== undefined ? value : null;
}


const Collection = (props) => {
    const context = props.context;
    return (
        <div>
            <header className="row">
                <div className="col-sm-12">
                    <h2>{context.title}</h2>
                </div>
            </header>
            <p className="description">{context.description}</p>
            <Table {...props} />
        </div>
    );
};

Collection.propTypes = {
    context: PropTypes.object.isRequired, // Collection context object to be rendered
};

globals.content_views.register(Collection, 'Collection');


class Cell {
    constructor(value, name, sortable) {
        this.value = value;
        this.name = name;
        this.sortable = sortable;
    }
}


class Row {
    constructor(item, cells, text) {
        this.item = item;
        this.cells = cells;
        this.text = text;
    }
}


class Data {
    constructor(rows) {
        this.rows = rows;
        this.sortedOn = null;
        this.reversed = false;
    }

    sort(sortColumn, reverse) {
        if (this.sortedOn === sortColumn && this.reversed === !!reverse) return;
        this.sortedOn = sortColumn;
        this.reversed = !!reverse;
        this.rows.sort((rowA, rowB) => {
            const a = String(rowA.cells[sortColumn].sortable);
            const b = String(rowB.cells[sortColumn].sortable);
            if (a < b) {
                return reverse ? 1 : -1;
            } else if (a > b) {
                return reverse ? -1 : 1;
            }
            return 0;
        });
    }
}

const RowView = (props) => {
    const { row, hidden } = props;
    const id = row.item['@id'];
    const tds = row.cells.map((cell, index) => {
        let cellValue;
        if (typeof cell.value === 'object') {
            // Cell contains an array or object, so render specially.
            if (Array.isArray(cell.value)) {
                // The cell contains an array. Determine if it's empty or not.
                if (cell.value.length) {
                    // Non-empty array. Arrays of simple values get comma separated. Arrays of
                    // objects get displayed as "[Objects]".
                    cellValue = (typeof cell.value[0] === 'object') ? '[Objects]' : cell.value.join();
                }
            } else {
                // The cell contains an object. Display "[Object]"
                cellValue = '[Object]';
            }
        } else {
            // Cell contains a simple value; just display it.
            cellValue = cell.value;
        }

        // Render a cell, but Make the first column in the row a link to the object.
        return (
            <td key={cell.name}>
                {index === 0 ?
                    <a href={row.item['@id']}>{cellValue}</a>
                :
                    <span>{cellValue}</span>
                }
            </td>
        );
    });
    return <tr key={id} hidden={hidden} data-href={id}>{tds}</tr>;
};

RowView.propTypes = {
    row: PropTypes.object.isRequired, // Properties to render in the row
    hidden: PropTypes.bool, // True if row is hidden; usually because of entered search terms
};

RowView.defaultProps = {
    hidden: false,
};


export default class Table extends React.Component {
    static extractParams(props, context) {
        const params = url.parse(context.location_href, true).query;
        let sorton = parseInt(params.sorton, 10);
        if (isNaN(sorton)) {
            sorton = props.defaultSortOn;
        }
        const state = {
            sortOn: sorton,
            reversed: params.reversed || false,
            searchTerm: params.q || '',
        };
        return state;
    }

    static guessColumns(props) {
        const columnList = props.columns || props.context.columns;
        const columns = [];
        if (!columnList || Object.keys(columnList).length === 0) {
            Object.keys(props.context['@graph'][0]).forEach((key) => {
                if (key.slice(0, 1) !== '@' && key.search(/(uuid|_no|accession)/) === -1) {
                    columns.push(key);
                }
            });
            columns.sort();
            columns.unshift('@id');
        } else {
            Object.keys(columnList).forEach((column) => {
                columns.push(column);
            });
        }
        return columns;
    }

    // Return `true` if this Javascript supports the Event constructor. True for all modern
    // browsers, but false for node on the server.
    static hasEvent() { return typeof Event !== 'undefined'; }

    constructor(props, context) {
        super(props);
        this.state = Table.extractParams(this.props, context);
        this.state.columns = Table.guessColumns(this.props);
        this.state.data = new Data([]);  // Tables may be long so render empty first
        this.state.communicating = true;

        // Bind `this` to class non-React functions.
        this.extractData = this.extractData.bind(this);
        this.fetchAll = this.fetchAll.bind(this);
        this.handleClickHeader = this.handleClickHeader.bind(this);
        this.handleKeyUp = this.handleKeyUp.bind(this);
        this.submit = this.submit.bind(this);
        this.clearFilter = this.clearFilter.bind(this);
    }

    componentDidMount() {
        this.setState({
            data: this.extractData(this.props),
            communicating: this.fetchAll(this.props),
            mounted: true,
        });
    }

    componentWillReceiveProps(nextProps, nextContext) {
        let updateData = false;
        if (nextProps.context !== this.props.context) {
            updateData = true;
            this.setState({
                communicating: this.fetchAll(nextProps),
            });
        }
        if (nextProps.columns !== this.props.columns) {
            updateData = true;
        }
        if (updateData) {
            const columns = Table.guessColumns(nextProps);
            this.extractData(nextProps, columns);
            this.setState({ columns: columns });
        }
        if (nextContext.location_href !== this.context.location_href) {
            const newState = Table.extractParams(nextProps, nextContext);
            this.setState(newState);
        }
    }

    componentWillUnmount() {
        if (typeof this.submitTimer !== 'undefined') {
            clearTimeout(this.submitTimer);
        }
        const request = this.state.allRequest;
        if (request) {
            request.abort();
        }
    }

    extractData(props, columnsOverride) {
        const context = props.context;
        const columns = columnsOverride || this.state.columns;
        const rows = context['@graph'].map((item) => {
            const cells = columns.map((column) => {
                let factory;
                let value = lookupColumn(item, column);
                if (column === '@id') {
                    factory = globals.listing_titles.lookup(item);
                    value = factory({ context: item });
                } else if (value === null) {
                    value = '';
                } else if (!Array.isArray(value) && value['@type']) {
                    factory = globals.listing_titles.lookup(value);
                    value = factory({ context: value });
                }
                const sortable = (String(value)).toLowerCase();
                return new Cell(value, column, sortable);
            });
            const text = cells.map(cell => cell.value).join(' ').toLowerCase();
            return new Row(item, cells, text);
        });
        const data = new Data(rows);
        this.setState({ data: data });
        return data;
    }

    fetchAll(props) {
        const context = props.context;
        let communicating;
        let request = this.state.allRequest;
        if (request) {
            request.abort();
        }
        if (context.all) {
            communicating = true;
            request = this.context.fetch(context.all, {
                headers: { Accept: 'application/json' },
            });
            request.then((response) => {
                if (!response.ok) throw response;
                return response.json();
            })
            .then((data) => {
                this.extractData({ context: data });
                this.setState({ communicating: false });
            }, globals.parseAndLogError.bind(undefined, 'allRequest'));
            this.setState({
                allRequest: request,
                communicating: true,
            });
        }
        return communicating;
    }

    handleClickHeader(event) {
        let target = event.target;
        while (target.tagName !== 'TH') {
            target = target.parentElement;
        }
        const cellIndex = target.cellIndex;
        let reversed = '';
        const sorton = this.sorton;
        if (this.props.defaultSortOn !== cellIndex) {
            sorton.value = cellIndex;
        } else {
            sorton.value = '';
        }
        if (this.state.sortOn === cellIndex) {
            reversed = !this.state.reversed || '';
        }
        this.reversed.value = reversed;
        event.preventDefault();
        event.stopPropagation();
        this.submit();
    }

    handleKeyUp(event) {
        if (typeof this.submitTimer !== 'undefined') {
            clearTimeout(this.submitTimer);
        }
        // Skip when enter key is pressed
        if (event.nativeEvent.keyCode === 13) return;
        // IE8 should only submit on enter as page reload is triggered
        this.submitTimer = setTimeout(this.submit, 200);
    }

    submit() {
        // form.submit() does not fire onsubmit handlers...
        const target = this.form;

        // Node does not support the Event constructor -- no server rendering.
        if (!Table.hasEvent()) {
            target.submit();
            return;
        }

        const event = new Event('submit', { bubbles: true, cancelable: true });
        target.dispatchEvent(event);
    }

    clearFilter() {
        this.q.value = '';
        this.submitTimer = setTimeout(this.submit);
    }

    render() {
        const columns = this.state.columns;
        const context = this.props.context;
        const defaultSortOn = this.props.defaultSortOn;
        const sortOn = this.state.sortOn;
        const reversed = this.state.reversed;
        const searchTerm = this.state.searchTerm;
        const titles = context.columns || {};
        const data = this.state.data;
        const total = context.count || data.rows.length;
        data.sort(sortOn, reversed);
        const headers = columns.map((column, index) => {
            let className = 'icon';
            if (index === sortOn) {
                className += reversed ? ' icon-chevron-down' : ' icon-chevron-up';
            }
            return (
                <th onClick={this.handleClickHeader} key={column}>
                    {(titles[column] && titles[column].title) || column}
                    <i className={className} />
                </th>
            );
        });
        const actions = (context.actions || []).map(action =>
            <span className="table-actions" key={action.name}>
                <a href={action.href}>
                    <button className={`btn ${action.className}` || ''}>{action.title}</button>
                </a>
            </span>
        );
        const searchTermLower = this.state.searchTerm.trim().toLowerCase();
        const notMatching = [];
        let matching = [];
        // Reorder rows so that the nth-child works
        if (searchTerm) {
            data.rows.forEach((row) => {
                if (row.text.indexOf(searchTermLower) === -1) {
                    notMatching.push(row);
                } else {
                    matching.push(row);
                }
            });
        } else {
            matching = data.rows;
        }
        const rows = matching.map(row => RowView({ row: row }));
        const mappedNotMatching = notMatching.map(row => RowView({ row: row, hidden: true }));
        rows.push(...mappedNotMatching);
        let tableClass = 'sticky-area collection-table';
        let loadingOrTotal;
        if (this.state.communicating) {
            tableClass += ' communicating';
            loadingOrTotal = (
                <span className="table-count label label-warning spinner-warning">Loading...</span>
            );
        } else {
            loadingOrTotal = (
                <span className="table-meta-data">
                    <span className="table-count label label-default">{matching.length}</span>
                    <span id="total-records">of {total} records</span>
                </span>
            );
        }
        return (
            <div className="table-responsive">
                <table className={`${tableClass} table table-striped table-hover table-panel`}>
                    <StickyHeader>
                    <thead className="sticky-header">
                        {this.props.showControls ? <tr className="nosort table-controls">
                            <th colSpan={columns.length}>
                                {loadingOrTotal}
                                {actions}
                                <form
                                    ref={(form) => { this.form = form; }}
                                    className="table-filter"
                                    onKeyUp={this.handleKeyUp}
                                    data-skiprequest="true"
                                    data-removeempty="true"
                                >
                                    <input
                                        ref={(input) => { this.q = input; }}
                                        disabled={this.state.communicating || undefined}
                                        name="q"
                                        type="search"
                                        defaultValue={searchTerm}
                                        placeholder="Filter table by..."
                                        className="filter form-control"
                                        id="table-filter"
                                    />
                                    <i className="icon icon-times-circle-o clear-input-icon" hidden={!searchTerm} onClick={this.clearFilter} />
                                    <input ref={(input) => { this.sorton = input; }} type="hidden" name="sorton" defaultValue={sortOn !== defaultSortOn ? sortOn : ''} />
                                    <input ref={(input) => { this.reversed = input; }} type="hidden" name="reversed" defaultValue={!!reversed || ''} />
                                </form>
                            </th>
                        </tr> : ''}
                        <tr className="col-headers">
                            {headers}
                        </tr>
                    </thead>
                    </StickyHeader>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        );
    }

}

Table.propTypes = {
    context: PropTypes.object.isRequired,
    columns: PropTypes.string,
    defaultSortOn: PropTypes.number,
    showControls: PropTypes.bool,
};

Table.defaultProps = {
    columns: '',
    defaultSortOn: 0,
    showControls: true,
};

Table.contextTypes = {
    fetch: PropTypes.func,
    location_href: PropTypes.string,
};
