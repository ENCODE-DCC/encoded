'use strict';
var React = require('react');
import PropTypes from 'prop-types';
import createReactClass from 'create-react-class';
var svgIcon = require('../libs/svg-icons').svgIcon;
var fetched = require('./fetched');
var search = require('./search');
var url = require('url');
var globals = require('./globals');
var StickyHeader = require('./StickyHeader');
var _ = require('underscore');

var FacetList = search.FacetList;


var columnChoices = function(schema, selected) {
    // start with id
    var columns = {};
    columns['@id'] = {
        title: 'ID',
        visible: true
    };
    // default selected columns are the schema's `columns`,
    // or whichever of title, description, name, accession & aliases
    // are found in the schema's properties
    // (note, this has to match the defaults sent from the server)
    var schemaColumns = schema.columns;
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
        if (name == '@id' || name == '@type' || name == 'uuid' || name == 'replicates') return;
        if (!columns.hasOwnProperty(name) && property.title) {
            columns[name] = {
                title: property.title,
                visible: false
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
                    visible: true
                };
            } else {
                columns[path].visible = true;
            }
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
                title: column.title
            });
        }
    });
    return visible_columns;
};


var lookupColumn = function (result, column) {
    var nodes = [result];
    var names = column.split('.');

    // Get the column's custom display function and call it if it exists
    var colViewer = globals.report_cell.lookup(result, column);
    if (colViewer) {
        var colViewResult = colViewer(result, column);
        if (colViewResult) {
            return <div>{colViewResult}</div>;
        }
    }

    for (var i = 0, len = names.length; i < len && nodes.length; i++) {
        var nextnodes = [];
        _.each(nodes.map(node => node[names[i]]), v => {
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
};


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

var Table = module.exports.Table = createReactClass({
    contextTypes: {
        location_href: PropTypes.string
    },

    extractData: function (items) {
        var columns = visibleColumns(this.props.columns);
        var rows = items.map(function (item) {
            var cells = columns.map(column => {
                var factory;
                var value = lookupColumn(item, column.path);
                if (column.path == '@id') {
                    factory = globals.listing_titles.lookup(item);
                    value = factory({context: item});
                } else if (value === null || value === undefined) {
                    value = '';
                } else if (value instanceof Array) {
                    value = value;
                } else if (value['@type']) {
                    factory = globals.listing_titles.lookup(value);
                    value = factory({context: value});
                }
                return new Cell(value);
            });
            return new Row(item, cells);
        });
        return rows;
    },

    getSort: function() {
        if (this.props.context.sort) {
            var sortColumn = Object.keys(this.props.context.sort)[0];
            return {
                column: sortColumn,
                reversed: this.props.context.sort[sortColumn].order == 'desc'
            };
        } else {
            return {};
        }
    },

    render: function () {
        var context = this.props.context;
        var columns = visibleColumns(this.props.columns);
        var sort = this.getSort();

        var headers = columns.map((column, index) => {
            var className = "icon";
            if (column.path === sort.column) {
                className += sort.reversed ? " icon-chevron-up" : " icon-chevron-down";
            }
            return (
                <th key={index} onClick={this.setSort.bind(this, column.path)}>
                    {column.title}&nbsp;<i className={className}></i>
                </th>
            );
        });

        var data = this.extractData(context['@graph']).concat(this.extractData(this.props.more));
        var rows = data.map(row => RowView({row: row}));
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
    },

    setSort: function(path) {
        const sort = this.getSort();
        const column = sort.column == path && !sort.reversed ? '-' + path : path;
        this.props.setSort(column);
    }

});


var ColumnSelector = createReactClass({
    getInitialState: function() {
        return {
            open: false
        };
    },

    render: function() {
        return (
            <div style={{display: 'inline-block', position: 'relative'}}>
                <a className={'btn btn-info btn-sm' + (this.state.open ? ' active' : '')} href="#" onClick={this.toggle} title="Choose columns"><i className="icon icon-columns"></i> Columns</a>
                {this.state.open && <div style={{position: 'absolute', top: '30px', width: '230px', backgroundColor: '#fff', padding: '.5em', border: 'solid 1px #ccc', borderRadius: 3, zIndex: 1}}>
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
    }
});


var Report = createReactClass({
    contextTypes: {
        location_href: PropTypes.string,
        navigate: PropTypes.func,
        fetch: PropTypes.func
    },

    getInitialState: function() {
        var parsed_url = url.parse(this.context.location_href, true);
        var from = parseInt(parsed_url.query.from) || 0;
        var size = parseInt(parsed_url.query.limit) || 25;
        return {
            from,
            size,
            to: from + size,
            loading: false,
            more: []
        };
    },

    componentWillReceiveProps: function(nextProps, nextContext) {
        // reset pagination when filter is changed
        if (nextContext.location_href != this.context.location_href) {
            var parsed_url = url.parse(this.context.location_href, true);
            var from = parseInt(parsed_url.query.from) || 0;
            var size = parseInt(parsed_url.query.limit) || 25;
            this.setState({
                from: from,
                to: from + size,
                more: []
            });
        }
    },

    render: function () {
        var parsed_url = url.parse(this.context.location_href, true);
        if (parsed_url.pathname.indexOf('/report') !== 0) return false;  // avoid breaking on re-render when navigate changes href before context is changed
        var context = this.props.context;
        var results = context['@graph'];
        var searchBase = parsed_url.search || '';
        searchBase = searchBase + (searchBase ? '&' : '?');

        var type = parsed_url.query.type;
        var schema = this.props.schemas[type];
        var query_fields = parsed_url.query.field;
        if (typeof query_fields === 'string') {
            query_fields = [query_fields];
        }
        var columns = columnChoices(schema, query_fields);

        // Map view icons to svg icons
        var view2svg = {
            'list-alt': 'search',
            'th': 'matrix'
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
                                        var parsedUrl = url.parse(view.href, true);
                                        delete parsedUrl.query.field;
                                        delete parsedUrl.search;
                                        var href = url.format(parsedUrl);
                                        return <a href={href} className="btn btn-info btn-sm btn-svgicon" title={view.title} key={i}>{svgIcon(view2svg[view.icon])}</a>;
                                    })}
                                </div>
                                <ColumnSelector columns={columns} toggleColumn={this.toggleColumn} />
                                <a className="btn btn-info btn-sm" href={context.download_tsv} data-bypass>Download TSV</a>
                            </div>
                            <Table context={context} more={this.state.more}
                                   columns={columns} setSort={this.setSort} />
                            {this.state.to < context.total &&
                                <h4 className={this.state.loading ? 'communicating' : ''}>
                                    {this.state.loading ?
                                        <div className="loading-spinner"></div>
                                    : <a className="btn btn-info btn-sm" onClick={this.loadMore}>Load more</a>} Showing
                                    results {this.state.from + 1} to {Math.min(context.total, this.state.to)} of {context.total}
                                </h4>
                            }
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
        var query_fields = parsed_url.query.field ? (typeof parsed_url.query.field === 'object' ? parsed_url.query.field : [parsed_url.query.field]) : undefined;
        var columns = columnChoices(schema, query_fields);

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

    setSort: function(sort) {
        var parsed_url = url.parse(this.context.location_href, true);
        parsed_url.query.sort = sort;
        delete parsed_url.search;
        this.context.navigate(url.format(parsed_url));        
    },

    loadMore: function() {
        if (this.state.request) {
            this.state.request.abort();
        }
        var parsed_url = url.parse(this.context.location_href, true);
        parsed_url.query.from = this.state.to;
        delete parsed_url.search;
        var request = this.context.fetch(url.format(parsed_url), {
            headers: {'Accept': 'application/json'}
        });
        request.then(response => {
            if (!response.ok) throw response;
            return response.json();
        })
        .catch(globals.parseAndLogError.bind(undefined, 'loadMore'))
        .then(data => {
            this.setState({
                more: this.state.more.concat(data['@graph']),
                loading: false,
                request: null
            });
        });

        this.setState({
            request: request,
            to: this.state.to + this.state.size,
            loading: true
        });
    },

    componentWillUnmount: function () {
        if (this.state.request) this.state.request.abort();
    }
});


var ReportLoader = createReactClass({
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
// globals.report_cell.register(CustomCellDisplay, @type[0] in quotes, column property name in quotes);
