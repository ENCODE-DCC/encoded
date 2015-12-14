'use strict';
// This module displays a table that can be sorted by any column. You can set one up for display with:
//     <SortTablePanel>
//         <SortTable list={array of objects} config={object describing table} meta={table-specific data} />
//     </SortTablePanel>
//
// <SortTablePanel> supports multiple <SortTable> components as children, so you can have multiple tables,
// each with their own header, inside the table panel.
//
// The list array (required) must be an array of objects whose properties get displayed in each cell of the
// table. The meta object (optional) has any extra data relevant to the specific table and doesn't get
// processed -- only passed on -- by the SortTable code.
//
// The config object (required) describes the columns of the table, and optionally how they get displayed,
// sorted, and hidden.
//
// 'config' has one sub-object per table column. The key for each sub-object must be unique as the code uses
// them to loop through the columns, though they never get displayed. Each sub-object has these properties:
// key: {
//     title -- (string or function): Displays column title. Can be a function that returns JSX if anything
//                                    dynamic needs to happen. It receives three parameters in this order:
//                                        list: array of objects passed in the `list` property to <SortTable>.
//                                        config: this config object.
//                                        meta: the object passed in the `meta` parameter to <SortTable>.
//                                    If the item to display is a simple property (string, integer) of the
//                                    objects passed in, this is the only required property of config.key,
//                                    as it then displays the value of the object with a key matching
//                                    config.key. In this case, config.key *has* to match the object's property
//                                    name.
//
//     display -- (function): If the property to display has a more complicated display than just a single
//                            value, this function returns JSX to display the property in any way it needs to.
//                            It receives one parameter that's the single object of `list` being displayed in
//                            a cell. If `display` is specified, the following `getValue` doesn't get called.
//
//     getValue -- (function): If the property to display can't be retrieved directly through item[config.key],
//                             this function retrieves and returns the value to be displayed in the cell. It
//                             must be a simple value, or you should use `display` above instead. This value
//                             is used for sorting, either with default sorting or the `sorter` method.
//
//     sorter -- (function or boolean): <SortTable> can handle basic sorting of two values. But if something
//                                      more complex needs to happen, this function gets called with the same
//                                      two parameters the Javascript sorting function gets. This function must
//                                      return neg, 0, or pos the same way the JS sorting function returns.
//                                      If `sorter` specifically gets the value FALSE, that causes this
//                                      column to not be sortable at all. Note that if you have a getValue
//                                      function defined, it gets called for the two comparison values, and
//                                      they get passed in to this function
//
//     objSorter -- (function or boolean): Same as `sorter` above, but instead of passing the result of
//                                         getValue as the two values, it passes the objects from `list`.
//                                         This is useful when you have getValue() returning one kind of value
//                                         while you need to sort on another. You should not specify both
//                                         `sorter` and `objSorter`.
//
//     hide -- (function): In some cases a column might need to be hidden. This function, if given, returns
//                         TRUE to hide this column based on some criteria. This function gets passed the same
//                         list, config, and meta that <SortTable> itself gets.
// }

var React = require('react');
var _ = require('underscore');
var moment = require('moment');


// Required sortable table wrapper component. Takes no parameters but puts the table in a Bootstrap panel
// and makes it responsive. You can place multiple <SortTable />s as children of this component.
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


// Displays one table within a <SortTablePanel></SortTablePanel>.
var SortTable = module.exports.SortTable = React.createClass({
    propTypes: {
        title: React.PropTypes.oneOfType([ // Title to display in table header
            React.PropTypes.string, // When title is a simple string
            React.PropTypes.object // When title is JSX
        ]),
        list: React.PropTypes.array, // Array of objects to display in the table
        config: React.PropTypes.object.isRequired, // Defines the columns of the table
        sortColumn: React.PropTypes.string // ID of column to sort by default; first column if not given
    },

    getInitialState: function() {
        var sortColumn;

        // Get the given sort column ID, or the default (first key in columns object) if none given
        if (this.props.sortColumn) {
            sortColumn = this.props.sortColumn;
        } else {
            sortColumn = Object.keys(this.props.config)[0];
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
        var aVal, bVal, result;
        var columnId = this.state.sortColumn;
        var sorter = this.props.config[columnId].sorter;
        var objSorter = this.props.config[columnId].objSorter;
        var getValue = this.props.config[columnId].getValue;

        // If the config for this column has `getValue` defined, use it to get the cell's value. Otherwise
        // just get it from the passed objects directly.
        if (getValue) {
            aVal = getValue(a);
            bVal = getValue(b);
        } else {
            aVal = a[columnId];
            bVal = b[columnId];
        }

        // If we have a custom sorting function, call it with the cell values to handle sorting. Otherwise
        if (sorter && (sorter !== false)) {
            result = sorter(aVal, bVal);
        } else if (objSorter) {
            result = objSorter(a, b);
        } else {
            if (aVal && bVal) {
                result = aVal > bVal ? 1 : -1;
            } else {
                result = aVal ? -1 : (bVal ? 1 : 0);
            }
        }
        return this.state.reversed ? -result : result;
    },

    render: function() {
        var list = this.props.list;
        var config = this.props.config;
        var meta = this.props.meta;
        var columnIds = Object.keys(config);
        var hiddenColumns = {};
        var hiddenCount = 0;

        // See if any columns hidden by making an array keyed by column ID that's true for each hidden column.
        // Also keep a count of hidden columns so we can calculate colspan later.
        columnIds.forEach(function(columnId) {
            var hidden = !!(config[columnId].hide && config[columnId].hide(list, config, meta));
            hiddenColumns[columnId] = hidden;
            hiddenCount += hidden ? 1 : 0;
        });

        // Calculate the colspan for the table
        var colCount = columnIds.length - hiddenCount;

        // Now display the table, but only if we were passed a non-empty list
        if (list && list.length) {
            return (
                <table className="table table-striped">

                    <thead>
                        {this.props.title ? <tr className="table-section"><th colSpan={colCount}>{this.props.title}</th></tr> : null}
                        <tr>
                            {columnIds.map(columnId => {
                                if (!hiddenColumns[columnId]) {
                                    var columnClass;

                                    if (config[columnId].sorter !== false) {
                                        columnClass = columnId === this.state.sortColumn ? (this.state.reversed ? 'tcell-desc' : 'tcell-asc') : 'tcell-sort';
                                    } else {
                                        columnClass = null;
                                    }
                                    var title = (typeof config[columnId].title === 'function') ? config[columnId].title(list, config, meta) : config[columnId].title;
                                    var thClass = (config[columnId].sorter !== false) ? 'tcell-sortable' : null;

                                    return (
                                        <th key={columnId} className={thClass} onClick={this.sortDir.bind(null, columnId)}>
                                            <span>{title}<i className={columnClass}></i></span>
                                        </th>
                                    );
                                }

                                // Column hidden
                                return null;
                            })}
                        </tr>
                    </thead>

                    <tbody>
                        {list.sort(this.sortColumn).map(item => {
                            return (
                                <tr key={item.uuid}>
                                    {columnIds.map(columnId => {
                                        if (!hiddenColumns[columnId]) {
                                            if (config[columnId].display) {
                                                return <td key={columnId}>{config[columnId].display(item)}</td>;
                                            }

                                            // No custom display function; just display the standard way
                                            var itemValue = config[columnId].getValue ? config[columnId].getValue(item) : item[columnId];
                                            return (
                                                <td key={columnId}>{itemValue}</td>
                                            );
                                        }

                                        // Column hidden
                                        return null;
                                    })}
                                </tr>
                            );
                        })}
                    </tbody>

                    <tfoot>
                        <tr><td colSpan={colCount}></td></tr>
                    </tfoot>

                </table>
            );
        }

        // Empty list; render nothing.
        return null;
    }
});
