'use strict';
var React = require('react');
var fetched = require('./fetched');
var search = require('./search');
var url = require('url');
var globals = require('./globals');
var parseAndLogError = require('./mixins').parseAndLogError;
var StickyHeader = require('./StickyHeader');
var _ = require('underscore');

var FacetList = search.FacetList;


var columnChoices = function(schema, selected) {
    var columns = {};
    // use 'columns' if explicitly defined,
    // otherwise all properties
    if (schema.columns !== undefined) {
        _.each(schema.columns, (column, path) => {
            columns[path] = {
                title: column.title,
                visible: true,
            };
        });
    } else {
        _.each(schema.properties, (property, name) => {
            columns[name] = {
                title: property.title,
                visible: true,
            };
        });
    }

    // if fields are selected, update visibility
    if (selected) {
        _.each(columns, (column, path) => {
            column.visible = _.contains(selected, path);
        });
    }

    return columns;
};


var visibleColumns = function(columns) {
    var visible_columns = [];
    _.mapObject(columns, (column, path) => {
        if (column.visible) {
            visible_columns.push({
                path: path,
                title: column.title,
            });
        }
    });
    return visible_columns;
};


var lookup_column = function (result, column) {
    var value = result;
    var names = column.split('.');
    for (var i = 0, len = names.length; i < len && value !== undefined; i++) {
        value = value[names[i]];
    }
    return value;
};


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

var RowView = function (props) {
    var row = props.row;
    var id = row.item['@id'];
    var tds = row.cells.map( function (cell, index) {
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
};

var Table = module.exports.Table = React.createClass({
    contextTypes: {
        location_href: React.PropTypes.string
    },

    extractData: function (columns) {
        var context = this.props.context;
        var rows = context['@graph'].map(function (item) {
            var cells = columns.map(column => {
                var factory;
                var value = lookup_column(item, column.path);
                if (column.path == '@id') {
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
            var text = cells.map(cell => cell.value).join(' ').toLowerCase();
            return new Row(item, cells, text);
        });
        return new Data(rows);
    },

    render: function () {
        var context = this.props.context;

        var columns = visibleColumns(this.props.columns);
        var sortOn = context.sort;
        var sortReversed = false;

        var headers = columns.map((column, index) => {
            var className = "sortdirection icon";
            if (column.path === sortOn) {
                className += sortReversed ? " icon-chevron-down" : " icon-chevron-up";
            }
            return (
                <th key={index}>
                    {column.title}
                    <i className={className}></i>
                </th>
            );
        });

        var data = this.extractData(columns);
        var rows = data.rows.map(row => RowView({row: row}));
        var table_class = "sticky-area collection-table";
        return (
            <div className="table-responsive">            
                <table className={table_class + " table table-striped table-hover table-panel"}>
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

});


var ColumnSelector = React.createClass({
    getInitialState: function() {
        return {
            open: false,
        };
    },

    render: function() {
        return (
            <div>
                <a className={'btn btn-info btn-sm' + (this.state.open ? ' active' : '')} href="#" onClick={this.toggle} title="Choose columns"><i className="icon icon-columns"></i></a>
                {this.state.open && <div style={{position: 'absolute', right: 0, backgroundColor: '#fff', padding: '.5em', border: 'solid 1px #ccc', borderRadius: 3, zIndex: 1}}>
                    <h4>Columns</h4>
                    {_.mapObject(this.props.columns, (column, path) => <div onClick={this.toggleColumn.bind(this, path)} style={{cursor: 'pointer'}}>
                        <input type="checkbox" checked={column.visible} /> {column.title}
                    </div>)}
                </div>}
            </div>
        );
    },

    toggle: function(e) {
        e.preventDefault();
        this.setState({open: !this.state.open});
    },

    toggleColumn: function(path) {
        this.props.toggleColumn(path);
    },
});


var Report = React.createClass({
    contextTypes: {
        location_href: React.PropTypes.string,
        navigate: React.PropTypes.func,
    },

    render: function () {
        var context = this.props.context;
        var results = context['@graph'];
        var parsed_url = url.parse(this.context.location_href, true);
        var searchBase = parsed_url.search || '';
        searchBase = searchBase + (searchBase ? '&' : '?');

        var type = parsed_url.query.type;
        var schema = this.props.schemas[type];
        var columns = columnChoices(schema, parsed_url.query.field);

        return (
            <div>
                <div className="panel data-display main-panel">
                    <div className="row">
                        <div className="col-sm-5 col-md-4 col-lg-3">
                            <FacetList facets={context.facets} filters={context.filters} searchBase={searchBase} />
                        </div>
                        <div className="col-sm-7 col-md-8 col-lg-9">
                            <span className="pull-right">
                                <ColumnSelector columns={columns} toggleColumn={this.toggleColumn} />
                            </span>
                            <h4>
                                Showing {results.length} of {context.total} results
                                {context.views && context.views.map(view => <span> <a href={view.href} title={view.title}><i className={'icon icon-' + view.icon}></i></a></span>)}
                            </h4>
                            <Table context={context} columns={columns} />
                        </div>
                    </div>
                </div>
            </div>
        );
    },

    toggleColumn: function(toggled_path) {
        var parsed_url = url.parse(this.context.location_href, true);
        var type = parsed_url.query.type;
        var schema = this.props.schemas[type];
        var columns = columnChoices(schema, parsed_url.query.field);

        var fields = [];
        _.mapObject(columns, (column, path) => {
            if (path == toggled_path ? !column.visible : column.visible) {
                fields.push(path);
            }
        });
        parsed_url.query.field = fields;
        delete parsed_url.search;
        this.context.navigate(url.format(parsed_url));
    },
});


var ReportLoader = React.createClass({
    render: function() {
        return (
            <fetched.FetchedData>
                <fetched.Param name="schemas" url="/profiles/" />
                <Report context={this.props.context} />
            </fetched.FetchedData>
        );
    }
});


globals.content_views.register(ReportLoader, 'Report');
