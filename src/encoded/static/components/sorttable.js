'use strict';
var React = require('react');
var _ = require('underscore');
var moment = require('moment');


var SortTablePanel = module.exports.SortTablePanel = React.createClass({
    render: function() {
        return (
            <div className="table-panel table-file">
                <div className="table-responsive">
                    {this.props.children}
                </div>
            </div>
        );
    }
});


var SortTable = module.exports.SortTable = React.createClass({
    propTypes: {
        list: React.PropTypes.array.isRequired, // Array of objects to display in the table
        config: React.PropTypes.object.isRequired, // Defines the columns of the table
        sortColumn: React.PropTypes.string // ID of column to sort by default; first column if not given
    },

    getInitialState: function() {
        var sortColumn;

        // Get the given sort column ID, or the default (first key in columns object) if none given
        if (this.props.sortColumn) {
            sortColumn = this.props.sortColumn;
        } else {
            sortColumn = Object.keys(this.props.config.columns)[0];
        }

        return {
            sortColumn: sortColumn, // ID of currently sorting column
            reversed: false // True if sorting of current sort column is reversed
        };
    },

    // Handle clicks in the column headers for sorting columns
    sortDir: function(column) {
        var reversed = column === this.state.sortColumn ? !this.state.reversed : false;
        this.setState({sortColumn: column, reversed: reversed});
    },

    // Called when any column needs sorting. If the column's config has a sorter function, call it
    // to handle its sorting. Otherwise assume the values can be retrieved from the currently sorted column ID.
    sortColumn: function(a, b) {
        var result;
        var columnId = this.state.sortColumn;
        var sorter = this.props.config.columns[columnId].sorter;
        if (sorter) {
            result = sorter(a, b);
        } else {
            if (a[columnId] && b[columnId]) {
                result = a[columnId] > b[columnId] ? 1 : -1;
            } else {
                result = a[columnId] ? -1 : (b[columnId] ? 1 : 0);
            }
        }
        return this.state.reversed ? -result : result;
    },

    render: function() {
        var list = this.props.list;
        var config = this.props.config;
        var columns = config.columns;
        var columnIds = Object.keys(columns);
        var colCount = columnIds.length;

        return (
            <table className="table table-striped">

                <thead>
                    <tr className="table-section"><th colSpan={colCount}>{config.title}</th></tr>
                    <tr>
                        {columnIds.map(columnId => {
                            var columnClass = columnId === this.state.sortColumn ? (this.state.reversed ? 'tcell-desc' : 'tcell-asc') : 'tcell-sort';

                            return (
                                <th key={columnId} className="tcell-sortable" onClick={this.sortDir.bind(null, columnId)}>
                                    <span>{columns[columnId].title}<i className={columnClass}></i></span>
                                </th>
                            );
                        })}
                    </tr>
                </thead>

                <tbody>
                    {list.sort(this.sortColumn).map(item => {
                        return (
                            <tr key={item.uuid}>
                                {columnIds.map(columnId => {
                                    if (columns[columnId].display) {
                                        return <td key={columnId}>{columns[columnId].display(item)}</td>;
                                    }

                                    // No custom display function; just display the standard way
                                    var itemValue = columns[columnId].getValue ? columns[columnId].getValue(item) : item[columnId];
                                    return (
                                        <td key={columnId}>{itemValue}</td>
                                    );
                                })}
                            </tr>
                        );
                    })}
                </tbody>

            </table>
        );
    }
});
