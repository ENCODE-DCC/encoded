/** @jsx React.DOM */
define(['exports', 'jquery', 'class', 'react', 'globals'],
function (collection, $, class_, React, globals) {
    'use strict';

    var Collection = collection.Collection = React.createClass({
        render: function () {
            var context = this.props.context;
            var location = this.props.location;
            return (
                <div>
                    <header class="row">
                        <div class="span12">
                            <h2>{context.title}</h2>
                        </div>
                    </header>
                    <p class="description">{context.description}</p>
                    <Table context={context} location={location} />
                </div>
            );
        }
    });

    globals.content_views.register(Collection, 'collection');



    var Cell = class_({
        constructor: function(value, sortable) {
            this.value = value;
            this.sortable = sortable;
        }
    });


    var Row = class_({
        constructor: function(item, cells, text) {
            this.item = item;
            this.cells = cells;
            this.text = text;
        }
    });


    var Data = class_({
        constructor: function(rows) {
            this.rows = rows;
            this.sortedOn = null;
            this.reversed = false;
        },
        sort: function(sortColumn, reverse) {
            reverse = !!reverse;
            if (this.sortedOn === sortColumn && this.reversed === reverse) return;
            this.sortedOn = sortColumn;
            this.reversed = reverse;            
            this.rows.sort(function (rowA, rowB) {
                var a = '' + rowA.cells[sortColumn].sortable;
                var b = '' + rowB.cells[sortColumn].sortable;
                if (a < b) {
                    return reverse ? -1 : 1;
                } else if (a > b) {
                    return reverse ? 1 : -1;
                }
                return 0;
            });
        }
    });

    var Table = collection.Table = React.createClass({
        getDefaultProps: function () {
            return {
                defaultSortOn: 0
            };
        },

        getInitialState: function () {
            var state = this.extractParams(this.props);
            var columns = state.columns = this.guessColumns(this.props);
            state.data = this.extractData(this.props, columns);
            state.communicating = this.fetchAll(this.props);
            return state;
        },

        componentWillReceiveProps: function (nextProps) {
            var updateData = false;
            if (nextProps.context !== this.props.context) {
                updateData = true;
                this.fetchAll(nextProps);
            }
            if (nextProps.columns !== this.props.columns) {
                updateData = true;
            }
            if (updateData) {
                var columns = this.guessColumns(nextProps);
                this.extractData(nextProps, columns);
            }
            if (nextProps.location.href !== this.props.location.href) {
                this.extractParams(nextProps);
            }

        },

        extractParams: function(props) {
            var params = props.location.params();
            var sorton = parseInt(params.sorton, 10);
            if (isNaN(sorton)) {
                sorton = props.defaultSortOn;
            }
            var state = {
                sortOn: sorton,
                reversed: params.reversed || false,
                searchTerm: params.q || ''
            };
            this.setState(state);
            return state;
        },

        guessColumns: function (props) {
            var column_list = props.context.columns;
            var columns = []
            if (Object.keys(column_list).length === 0) {
                for (var key in props.context['@graph'][0]) {
                    if (key.slice(0, 1) != '@' && key.search(/(uuid|_no|accession)/) == -1) {
                        columns.push(key);
                    }
                }
                columns.sort();
                columns.unshift('@id');
            } else {
                for(var column in column_list) {
                    columns.push(column)
                }
            }
            this.setState({columns: columns});
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
                    var value = item[column];
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
                    return Cell(value, sortable);
                });
                var text = cells.map(function (cell) {
                    return cell.value;
                }).join(' ').toLowerCase();
                return Row(item, cells, text);
            });
            var data = Data(rows);
            this.setState({data: data})
            return data;
        },

        fetchAll: function (props) {
            var context = props.context;
            var communicating;
            if (this.allRequest && this.allRequest.state() == 'pending') {
                this.allRequest.abort();
            }
            var self = this;
            if (context.all) {
                communicating = true;
                this.setState({communicating: true});
                this.allRequest = $.ajax({
                    url: context.all,
                    type: 'GET',
                    dataType: 'json'
                }).done(function (data) {
                    self.extractData({context: data});
                    self.setState({communicating: false});
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
            var titles = context.columns;
            var data = this.state.data;
            var params = this.props.location.params();
            var total = context.count || data.rows.length;
            data.sort(sortOn, reversed);
            var self = this;
            var headers = columns.map(function (column, index) {
                var className = "sortdirection icon-";
                if (index === sortOn) {
                    className += reversed ? " icon-chevron-up" : " icon-chevron-down";
                }
                return (
                    <th onClick={self.handleClickHeader} key={index}>
                        {titles[column] || column}
                        <i class={className}></i>
                    </th>
                );
            });
            var searchTermLower = this.state.searchTerm.toLowerCase();
            var found = 0;
            var rows = data.rows.map(function (row) {
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
                var id = row.item['@id'];
                // Keep DOM nodes around but hidden
                var hidden = (searchTerm && row.text.indexOf(searchTermLower) == -1) || undefined;
                if (!hidden) found += 1;
                return (
                    <tr key={id} hidden={hidden} data-href={id}>{tds}</tr>
                );
            });
            var table_class = "sticky-area collection-table";
            var loading_or_total;
            if (this.state.communicating) {
                table_class += ' communicating';
                loading_or_total = (
                    <span class="table-count label label-warning spinner-warning">Loading...</span>
                );
            } else {
                loading_or_total = (
                    <span>
                        <span class="table-count label label-invert">{found}</span>
                        <span id="total-records">of {total} records</span>
                    </span>
                );
            }
            return (
                <table class={table_class}>
                    <thead class="sticky-header">
                        <tr class="nosort table-controls">
                            <th colSpan={columns.length}>
                                {loading_or_total}
                                <form ref="form" class="table-filter" onKeyUp={this.handleKeyUp} 
                                	data-skiprequest="true" data-removeempty="true">
                                    <input ref="q" disabled={this.state.communicating || undefined} 
                                    	name="q" type="search" defaultValue={searchTerm} 
                                    	placeholder="Filter table by..." class="filter" 
                                    	id="table-filter" /> 
                                    <i class="icon-remove-sign clear-input-icon" hidden={!searchTerm} onClick={this.clearFilter}></i>
                                    <input ref="sorton" type="hidden" name="sorton" defaultValue={sortOn !== defaultSortOn ? sortOn : ''} />
                                    <input ref="reversed" type="hidden" name="reversed" defaultValue={!!reversed || ''} />
                                </form>
                            </th>
                        </tr>
                        <tr>
                            {headers}
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            );
        },

        componentDidUpdate: function (prevProps, prevState, domNode) {
            // Switching between collections may leave component in place
            if (prevProps.context != this.props.context) {
                this.refs.q.getDOMNode().value = this.state.searchTerm;
            }
        },

        handleClickHeader: function (event) {
            var target = event.target;
            while (target.tagName != 'TH') {
                target = target.parentElement;
            }
            var cellIndex = target.cellIndex;
            var reversed = '';
            var sorton = this.refs.sorton.getDOMNode()
            if (this.props.defaultSortOn !== cellIndex) {
                sorton.value = cellIndex;
            } else {
                sorton.value = '';
            }
            if (this.state.sortOn == cellIndex) {
                reversed = !this.state.reversed || ''
            }
            this.refs.reversed.getDOMNode().value = reversed;
            event.preventDefault();
            this.submit();
        },

        handleKeyUp: function (event) {
            if (typeof this.submitTimer != 'undefined') {
                clearTimeout(this.submitTimer);
            }
            // Skip when enter key is pressed
            if (event.nativeEvent.keyCode == 13) return;
            this.submitTimer = setTimeout(this.submit, 200);
        },

        submit: function () {
            // form.submit() does not fire onsubmit handlers...
            var event = new Event('submit', {bubbles: true, cancelable: true});
            this.refs.form.getDOMNode().dispatchEvent(event);
        },
        
        clearFilter: function (event) {
            this.refs.q.getDOMNode().value = '';
            this.submitTimer = setTimeout(this.submit);
        }, 

        componentWillUnmount: function () {
            if (typeof this.submitTimer != 'undefined') {
                clearTimeout(this.submitTimer);
            }
            if (this.allRequest && this.allRequest.state() == 'pending') {
                this.allRequest.abort();
            }
        }

    });


    return collection;
});
