'use strict';
var React = require('react');
var url = require('url');
var globals = require('./globals');
var StickyHeader = require('./StickyHeader');


var lookup_column = function (result, column) {
    var value = result;
    var names = column.split('.');
    for (var i = 0, len = names.length; i < len && value !== undefined; i++) {
        value = value[names[i]];
    }
    return value;
};

var Collection = module.exports.Collection = React.createClass({
    render: function () {
        var context = this.props.context;
        return (
            <div>
                <header className="row">
                    <div className="col-sm-12">
                        <h2>{context.title}</h2>
                    </div>
                </header>
                <p className="description">{context.description}</p>
                <Table {...this.props} />
            </div>
        );
    }
});

globals.content_views.register(Collection, 'Collection');


class Cell {
    constructor(value, sortable) {
        this.value = value;
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
        reverse = !!reverse;
        if (this.sortedOn === sortColumn && this.reversed === reverse) return;
        this.sortedOn = sortColumn;
        this.reversed = reverse;            
        this.rows.sort(function (rowA, rowB) {
            var a = '' + rowA.cells[sortColumn].sortable;
            var b = '' + rowB.cells[sortColumn].sortable;
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
            <td key={row.item['@id']}>
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
    row: React.PropTypes.object.isRequired, // Properties to render in the row
    hidden: React.PropTypes.bool, // True if row is hidden; usually because of entered search terms
};

RowView.defaultProps = {
    hidden: false,
};


var Table = module.exports.Table = React.createClass({
    contextTypes: {
        fetch: React.PropTypes.func,
        location_href: React.PropTypes.string
    },


    getDefaultProps: function () {
        return {
            defaultSortOn: 0,
            showControls: true,
        };
    },

    getInitialState: function () {
        var state = this.extractParams(this.props, this.context);
        state.columns = this.guessColumns(this.props);
        state.data = new Data([]);  // Tables may be long so render empty first
        state.communicating = true;
        return state;
    },

    componentWillReceiveProps: function (nextProps, nextContext) {
        var updateData = false;
        if (nextProps.context !== this.props.context) {
            updateData = true;
            this.setState({
                communicating: this.fetchAll(nextProps)
            });
        }
        if (nextProps.columns !== this.props.columns) {
            updateData = true;
        }
        if (updateData) {
            var columns = this.guessColumns(nextProps);
            this.extractData(nextProps, columns);
            this.setState({ columns: columns });
        }
        if (nextContext.location_href !== this.context.location_href) {
            const newState = this.extractParams(nextProps, nextContext);
            this.setState(newState);
        }

    },

    extractParams: function(props, context) {
        var params = url.parse(context.location_href, true).query;
        var sorton = parseInt(params.sorton, 10);
        if (isNaN(sorton)) {
            sorton = props.defaultSortOn;
        }
        var state = {
            sortOn: sorton,
            reversed: params.reversed || false,
            searchTerm: params.q || ''
        };
        return state;
    },

    guessColumns: function (props) {
        var column_list = props.columns || props.context.columns;
        var columns = [];
        if (!column_list || Object.keys(column_list).length === 0) {
            for (var key in props.context['@graph'][0]) {
                if (key.slice(0, 1) != '@' && key.search(/(uuid|_no|accession)/) == -1) {
                    columns.push(key);
                }
            }
            columns.sort();
            columns.unshift('@id');
        } else {
            for(var column in column_list) {
                columns.push(column);
            }
        }
        return columns;
    },

    extractData: function (props, columns) {
        var context = props.context;
        columns = columns || this.state.columns;
        var rows = context['@graph'].map(function (item) {
            var cells = columns.map(function (column) {
                var factory;
                // cell factories
                //if (factory) {
                //    return factory({context: item, column: column});
                //}
                var value = lookup_column(item, column);
                if (column == '@id') {
                    factory = globals.listing_titles.lookup(item);
                    value = factory({context: item});
                } else if (value == null) {
                    value = '';
                } else if (value instanceof Array) {
                    value = value;
                } else if (value['@type']) {
                    factory = globals.listing_titles.lookup(value);
                    value = factory({context: value});
                }
                var sortable = ('' + value).toLowerCase();
                return new Cell(value, sortable);
            });
            var text = cells.map(function (cell) {
                return cell.value;
            }).join(' ').toLowerCase();
            return new Row(item, cells, text);
        });
        var data = new Data(rows);
        this.setState({data: data});
        return data;
    },

    fetchAll: function (props) {
        var context = props.context;
        var communicating;
        var request = this.state.allRequest;
        var self = this;
        if (context.all) {
            communicating = true;
            request = this.context.fetch(context.all, {
                headers: {'Accept': 'application/json'}
            });
            request.then(response => {
                if (!response.ok) throw response;
                return response.json();
            })
            .then(data => {
                self.extractData({context: data});
                self.setState({communicating: false});
            }, globals.parseAndLogError.bind(undefined, 'allRequest'));
            this.setState({
                allRequest: request,
                communicating: true
            });
        }
        return communicating;
    },

    render: function () {
        var columns = this.state.columns;
        var context = this.props.context;
        var defaultSortOn = this.props.defaultSortOn;
        var sortOn = this.state.sortOn;
        var reversed = this.state.reversed;
        var searchTerm = this.state.searchTerm;
        this.state.searchTerm = searchTerm;
        var titles = context.columns || {};
        var data = this.state.data;
        var params = url.parse(this.context.location_href, true).query;
        var total = context.count || data.rows.length;
        data.sort(sortOn, reversed);
        var self = this;
        var headers = columns.map(function (column, index) {
            var className = "icon";
            if (index === sortOn) {
                className += reversed ? " icon-chevron-down" : " icon-chevron-up";
            }
            return (
                <th onClick={self.handleClickHeader} key={column}>
                    {titles[column] && titles[column]['title'] || column}
                    <i className={className}></i>
                </th>
            );
        });
        var actions = (context.actions || []).map(action =>
            <span className="table-actions" key={action.name}>
                <a href={action.href}>
                    <button className={'btn ' + action.className || ''}>{action.title}</button>
                </a>
            </span>
        );
        var searchTermLower = this.state.searchTerm.trim().toLowerCase();
        var matching = [];
        var not_matching = [];
        // Reorder rows so that the nth-child works
        if (searchTerm) {
            data.rows.forEach(function (row) {
                if (row.text.indexOf(searchTermLower) == -1) {
                    not_matching.push(row);
                } else {
                    matching.push(row);
                }
            });
        } else {
            matching = data.rows;
        }
        var rows = matching.map(function (row) {
            return RowView({row: row});
        });
        rows.push.apply(rows, not_matching.map(function (row) {
            return RowView({row: row, hidden: true});
        }));
        var table_class = "sticky-area collection-table";
        var loading_or_total;
        if (this.state.communicating) {
            table_class += ' communicating';
            loading_or_total = (
                <span className="table-count label label-warning spinner-warning">Loading...</span>
            );
        } else {
            loading_or_total = (
                <span className="table-meta-data">
                    <span className="table-count label label-default">{matching.length}</span>
                    <span id="total-records">of {total} records</span>
                </span>
            );
        }
        return (
            <div className="table-responsive">            
                <table className={table_class + " table table-striped table-hover table-panel"}>
                    <StickyHeader>
                    <thead className="sticky-header">
                        {this.props.showControls ? <tr className="nosort table-controls">
                            <th colSpan={columns.length}>
                                {loading_or_total}
                                {actions}
                                <form ref="form" className="table-filter" onKeyUp={this.handleKeyUp} 
                                    data-skiprequest="true" data-removeempty="true">
                                    <input ref="q" disabled={this.state.communicating || undefined} 
                                        name="q" type="search" defaultValue={searchTerm} 
                                        placeholder="Filter table by..." className="filter form-control" 
                                        id="table-filter" /> 
                                    <i className="icon icon-times-circle-o clear-input-icon" hidden={!searchTerm} onClick={this.clearFilter}></i>
                                    <input ref="sorton" type="hidden" name="sorton" defaultValue={sortOn !== defaultSortOn ? sortOn : ''} />
                                    <input ref="reversed" type="hidden" name="reversed" defaultValue={!!reversed || ''} />
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
    },

    componentDidMount: function () {
        this.setState({
            data: this.extractData(this.props),
            communicating: this.fetchAll(this.props),
            mounted: true,
        });
    },

    handleClickHeader: function (event) {
        var target = event.target;
        while (target.tagName != 'TH') {
            target = target.parentElement;
        }
        var cellIndex = target.cellIndex;
        var reversed = '';
        var sorton = this.refs.sorton;
        if (this.props.defaultSortOn !== cellIndex) {
            sorton.value = cellIndex;
        } else {
            sorton.value = '';
        }
        if (this.state.sortOn == cellIndex) {
            reversed = !this.state.reversed || '';
        }
        this.refs.reversed.value = reversed;
        event.preventDefault();
        event.stopPropagation();
        this.submit();
    },

    handleKeyUp: function (event) {
        if (typeof this.submitTimer != 'undefined') {
            clearTimeout(this.submitTimer);
        }
        // Skip when enter key is pressed
        if (event.nativeEvent.keyCode == 13) return;
        // IE8 should only submit on enter as page reload is triggered
        if (!this.hasEvent) return;
        this.submitTimer = setTimeout(this.submit, 200);
    },

    hasEvent: typeof Event !== 'undefined',

    submit: function () {
        // form.submit() does not fire onsubmit handlers...
        var target = this.refs.form;

        // IE8 does not support the Event constructor
        if (!this.hasEvent) {
            target.submit();
            return;
        }

        var event = new Event('submit', {bubbles: true, cancelable: true});
        target.dispatchEvent(event);
    },
    
    clearFilter: function (event) {
        this.refs.q.value = '';
        this.submitTimer = setTimeout(this.submit);
    }, 

    componentWillUnmount: function () {
        if (typeof this.submitTimer != 'undefined') {
            clearTimeout(this.submitTimer);
        }
        var request = this.state.allRequest;
    }

});
