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

    getDefaultProps: function () {
        return {defaultSortOn: 0};
    },

    getInitialState: function () {
        var state = this.extractParams(this.props, this.context);
        state.columns = this.guessColumns(this.props);
        state.data = this.extractData(this.props, state.columns);
        return state;
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
        };
        this.setState(state);
        return state;
    },

    guessColumns: function (props) {
        if (props.columns) {
            return props.columns;
        }

        var column_list = props.context.columns;
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
        return new Data(rows);
    },

    render: function () {
        var context = this.props.context;
        var columns = this.state.columns;
        var defaultSortOn = this.props.defaultSortOn;
        var sortOn = this.state.sortOn;
        var reversed = this.state.reversed;
        var titles = context.columns || {};
        var data = this.state.data;
        var params = url.parse(this.context.location_href, true).query;
        var total = context.count || data.rows.length;
        data.sort(sortOn, reversed);
        var self = this;
        var headers = columns.map(function (column, index) {
            var className = "sortdirection icon";
            if (index === sortOn) {
                className += reversed ? " icon-chevron-down" : " icon-chevron-up";
            }
            return (
                <th onClick={self.handleClickHeader} key={index}>
                    {titles[column] && titles[column]['title'] || column}
                    <i className={className}></i>
                </th>
            );
        });
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
    contextTypes: {
        navigate: React.PropTypes.func,
    },

    getInitialState: function() {
        var schema = this.props.schemas[this.props.type];
        return {
            open: false,
            schema: schema,
            columns: this.props.columns || Object.keys(schema.columns),
        };
    },

    render: function() {
        return (
            <div>
                <a className={'btn btn-info btn-sm' + (this.state.open ? ' active' : '')} href="#" onClick={this.toggle} title="Choose columns"><i className="icon icon-columns"></i></a>
                {this.state.open && <div style={{position: 'absolute', right: 0, backgroundColor: '#fff', padding: '.5em', border: 'solid 1px #ccc', borderRadius: 3, zIndex: 1}}>
                    {_.mapObject(this.state.schema.columns, function(column, name) {
                        if (name == '@id') {
                            return false;
                        }
                        var checked = _.contains(this.state.columns, name);
                        return <div>
                            <input type="checkbox" defaultChecked={checked} onChange={this.onChange.bind(this, name)} /> {column.title}
                        </div>;
                    }.bind(this))}
                </div>}
            </div>
        );
    },

    toggle: function(e) {
        e.preventDefault();
        this.setState({open: !this.state.open});
    },

    onChange: function(column, e) {
        var location = this.props.location;
        var checked = e.target.checked;
        location.query.field = Object.keys(this.state.schema.columns).filter(function(c) {
            return c == column ? checked : _.contains(this.state.columns, c);
        }.bind(this));
        delete location.search;
        this.context.navigate(url.format(location));
    }
});


var Report = module.exports.Report = React.createClass({
    contextTypes: {
        location_href: React.PropTypes.string,
    },

    render: function () {
        var context = this.props.context;
        var results = context['@graph'];
        var parsed_url = url.parse(this.context.location_href, true);
        var searchBase = parsed_url.search || '';
        searchBase = searchBase + (searchBase ? '&' : '?');

        var type = parsed_url.query.type;
        var columns = parsed_url.query.field;
        if (columns) {
            columns = ['@id'].concat(columns);
        }

        return (
            <div>
                <div className="panel data-display main-panel">
                    <div className="row">
                        <div className="col-sm-5 col-md-4 col-lg-3">
                            <FacetList facets={context.facets} filters={context.filters} searchBase={searchBase} />
                        </div>
                        <div className="col-sm-7 col-md-8 col-lg-9">
                            <span className="pull-right">
                                <fetched.FetchedData>
                                    <fetched.Param name="schemas" url="/profiles/" />
                                    <ColumnSelector type={type} location={parsed_url} columns={columns} />
                                </fetched.FetchedData>
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
    }
});

globals.content_views.register(Report, 'Report');
