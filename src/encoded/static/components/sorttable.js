// This module displays a table that can be sorted by any column. You can set one up for display with:
//     <SortTablePanel>
//         <SortTable list={array of objects} columns={object describing table columns} meta={table-specific data} />
//     </SortTablePanel>
//
// <SortTablePanel> supports multiple <SortTable> components as children, so you can have multiple tables,
// each with their own header, inside the table panel.
//
// The list array (required) must be an array of objects whose properties get displayed in each cell of the
// table. The meta object (optional) has any extra data relevant to the specific table and doesn't get
// processed -- only passed on -- by the SortTable code.
//
// The columns object (required) describes the columns of the table, and optionally how they get displayed,
// sorted, and hidden.
//
// 'columns' has one sub-object per table column. The key for each sub-object must be unique as the code uses
// them to loop through the columns, though they never get displayed. Each sub-object has these properties:
// key: {
//     title -- (string or function): Displays column title. Can be a function that returns JSX if anything
//                                    dynamic needs to happen. It receives three parameters in this order:
//                                        list: array of objects passed in the `list` property to <SortTable>.
//                                        columns: this columns object.
//                                        meta: the object passed in the `meta` parameter to <SortTable>.
//                                    If the item to display is a simple property (string, integer) of the
//                                    objects passed in, this is the only required property of columns.key,
//                                    as it then displays the value of the object with a key matching
//                                    columns.key. In this case, columns.key *has* to match the object's
//                                    property name.
//
//     display -- (function): If the property to display has a more complicated display than just a single
//                            value, this function returns JSX to display the property in any way it needs to.
//                            It receives one parameter that's the single object of `list` being displayed in
//                            a cell. If `display` is specified, the following `getValue` doesn't get called.
//
//     getValue -- (function): If the property to display can't be retrieved directly through item[columns.key],
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
//                         list, columns, and meta that <SortTable> itself gets.
// }

import React from 'react';
import PropTypes from 'prop-types';
import { Panel, PanelHeading } from '../libs/bootstrap/panel';


// Required sortable table wrapper component. Takes no parameters but puts the table in a Bootstrap panel
// and makes it responsive. You can place multiple <SortTable />s as children of this component.
const SortTablePanel = (props) => {
    const { title, header, noDefaultClasses } = props;

    return (
        <Panel addClasses={`table-file + ${noDefaultClasses ? '' : ' table-panel'}`} noDefaultClasses={noDefaultClasses}>
            {title ?
                <PanelHeading key="heading">
                    <h4>{title ? <span>{this.props.title}</span> : null}</h4>
                </PanelHeading>
            : (header ?
                <PanelHeading key="heading" addClasses="clearfix">{this.props.header}</PanelHeading>
            : null)}

            <div className="table-responsive" key="table">
                {this.props.children}
            </div>
        </Panel>
    );
};

SortTablePanel.propTypes = {
    // Note: `title` overrides `header`
    title: PropTypes.oneOfType([ // Title to display in table panel header
        PropTypes.string, // When title is a simple string
        PropTypes.object, // When title is JSX
    ]),
    header: PropTypes.object, // React component to render inside header
    noDefaultClasses: PropTypes.bool, // T to skip default <Panel> classes
};

SortTablePanel.defaultProps = {
    title: '',
    header: null,
    noDefaultClasses: false,
};


const SortTableComponent = props => (
    <div className="tableFiles">
        {props.title ?
            <PanelHeading key="heading">
                <h4>{props.title ? <span>{props.title}</span> : null}</h4>
            </PanelHeading>
        : (props.header ?
            <PanelHeading key="heading" addClasses="clearfix">{this.props.header}</PanelHeading>
        : null)}

        <div className="table-responsive" key="table">
            {props.children}
        </div>
    </div>
);

SortTableComponent.propTypes = {
    // Note: `title` overrides `header`
    title: PropTypes.oneOfType([ // Title to display in table panel header
        PropTypes.string, // When title is a simple string
        PropTypes.object, // When title is JSX
    ]),
    header: PropTypes.object, // React component to render inside header
    children: PropTypes.node,
};

SortTableComponent.defaultProps = {
    title: null,
    header: null,
    children: null,
};


// Mostly this is a click handler for the column sorting direction icon. It ties the ID of the
// clicked header to the parent's click handler.
class ColumnSortDir extends React.Component {
    constructor() {
        super();

        // Bind this to non-React methods.
        this.handleClick = this.handleClick.bind(this);
    }

    // Called when the column sort direction icon gets clicked. Passes it up to the parent component
    // along with the ID of the column the icon belongs to.
    handleClick() {
        this.props.sortDir(this.props.columnId);
    }

    render() {
        const { columnId, thClass, title, columnClass } = this.props;

        return (
            <th key={columnId} className={thClass} onClick={this.handleClick}>
                <span>{title}<i className={columnClass} /></span>
            </th>
        );
    }
}

ColumnSortDir.propTypes = {
    sortDir: PropTypes.func.isRequired, // Parent function to handle the sorting-direction click
    columnId: PropTypes.string.isRequired, // ID of the column containing the sort-direction icon
    thClass: PropTypes.string, // CSS class for the column header <th>
    title: PropTypes.oneOfType([ // Title to display in table header
        PropTypes.string, // When title is a simple string
        PropTypes.object, // When title is JSX
    ]),
    columnClass: PropTypes.string, // CSS class for the sorting icon; pointing up, down, or both
};

ColumnSortDir.defaultProps = {
    thClass: '',
    title: null,
    columnClass: '',
};


// Displays one table within a <SortTablePanel></SortTablePanel>.
class SortTable extends React.Component {
    constructor(props) {
        super(props);

        let sortColumn;

        // Get the given sort column ID, or the default (first key in columns object) if none given
        if (this.props.sortColumn) {
            sortColumn = this.props.sortColumn;
        } else {
            sortColumn = Object.keys(this.props.columns)[0];
        }

        // Set initial React state.
        this.state = {
            sortColumn, // ID of currently sorting column
            reversed: false, // True if sorting of current sort column is reversed
        };

        // Bind this to non-React methods.
        this.sortDir = this.sortDir.bind(this);
        this.sortColumn = this.sortColumn.bind(this);
    }

    // Handle clicks in the column headers for sorting columns
    sortDir(column) {
        const reversed = column === this.state.sortColumn ? !this.state.reversed : false;
        this.setState({ sortColumn: column, reversed });
    }

    // Called when any column needs sorting. If the column has a sorter function, call it
    // to handle its sorting. Otherwise assume the values can be retrieved from the currently sorted column ID.
    sortColumn(a, b) {
        const columnId = this.state.sortColumn;
        const sorter = this.props.columns[columnId].sorter;

        if (sorter !== false) {
            let aVal;
            let bVal;
            let result;
            const objSorter = this.props.columns[columnId].objSorter;
            const getValue = this.props.columns[columnId].getValue;

            // If the columns for this column has `getValue` defined, use it to get the cell's value. Otherwise
            // just get it from the passed objects directly.
            if (getValue) {
                aVal = getValue(a);
                bVal = getValue(b);
            } else {
                aVal = a[columnId];
                bVal = b[columnId];
            }

            // If we have a custom sorting function, call it with the cell values to handle sorting. Otherwise
            if (sorter) {
                result = sorter(aVal, bVal);
            } else if (objSorter) {
                result = objSorter(a, b);
            } else if (aVal && bVal) {
                result = aVal > bVal ? 1 : -1;
            } else {
                result = aVal ? -1 : (bVal ? 1 : 0);
            }
            return this.state.reversed ? -result : result;
        }

        // Column doesn't sort
        return 0;
    }

    render() {
        const { list, columns, rowClasses, meta } = this.props;
        const columnIds = Object.keys(columns);
        const hiddenColumns = {};
        let hiddenCount = 0;

        // See if any columns hidden by making an array keyed by column ID that's true for each hidden column.
        // Also keep a count of hidden columns so we can calculate colspan later.
        columnIds.forEach((columnId) => {
            const hidden = !!(columns[columnId].hide && columns[columnId].hide(list, columns, meta));
            hiddenColumns[columnId] = hidden;
            hiddenCount += hidden ? 1 : 0;
        });

        // Calculate the colspan for the table
        const colCount = columnIds.length - hiddenCount;

        // Now display the table, but only if we were passed a non-empty list
        if (list && list.length) {
            return (
                <table className="table table-sortable">

                    <thead>
                        {this.props.title ? <tr className="table-section" key="title"><th colSpan={colCount}>{this.props.title}</th></tr> : null}

                        {!this.props.collapsed ?
                            <tr key="header">
                                {columnIds.map((columnId) => {
                                    if (!hiddenColumns[columnId]) {
                                        let columnClass;

                                        if (columns[columnId].sorter !== false) {
                                            columnClass = columnId === this.state.sortColumn ? (this.state.reversed ? 'tcell-desc' : 'tcell-asc') : 'tcell-sort';
                                        } else {
                                            columnClass = null;
                                        }
                                        const title = (typeof columns[columnId].title === 'function') ? columns[columnId].title(list, columns, meta) : columns[columnId].title;
                                        const thClass = (columns[columnId].sorter !== false) ? 'tcell-sortable' : null;

                                        return <ColumnSortDir sortDir={this.sortDir} columnId={columnId} thClass={thClass} title={title} columnClass={columnClass} />;
                                    }

                                    // Column hidden
                                    return null;
                                })}
                            </tr>
                        : null}
                    </thead>

                    {!this.props.collapsed ?
                        <tbody>
                            {list.sort(this.sortColumn).map((item, i) => {
                                const rowClassStr = rowClasses ? rowClasses(item, i) : '';
                                return (
                                    <tr key={i} className={rowClassStr}>
                                        {columnIds.map((columnId) => {
                                            if (!hiddenColumns[columnId]) {
                                                if (columns[columnId].display) {
                                                    return <td key={columnId}>{columns[columnId].display(item, meta)}</td>;
                                                }

                                                // No custom display function; just display the standard way
                                                const itemValue = columns[columnId].getValue ? columns[columnId].getValue(item, meta) : item[columnId];
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
                    : null}

                    <tfoot>
                        <tr>
                            <td className={`file-table-footer${this.props.collapsed ? ' hiding' : ''}`} colSpan={colCount}>
                                {this.props.footer}
                            </td>
                        </tr>
                    </tfoot>
                </table>
            );
        }

        // Empty list; render nothing.
        return null;
    }
}

SortTable.propTypes = {
    title: PropTypes.oneOfType([ // Title to display in table header
        PropTypes.string, // When title is a simple string
        PropTypes.object, // When title is JSX
    ]),
    meta: PropTypes.object, // Extra information to display items.
    list: PropTypes.array, // Array of objects to display in the table
    columns: PropTypes.object.isRequired, // Defines the columns of the table
    rowClasses: PropTypes.func, // If provided, gets called for each row of table to generate per-row CSS classes
    sortColumn: PropTypes.string, // ID of column to sort by default; first column if not given
    footer: PropTypes.object, // Optional component to display in the footer
    collapsed: PropTypes.bool, // T if only title bar should be displayed
};

SortTable.defaultProps = {
    title: null,
    meta: null,
    list: null,
    rowClasses: null,
    sortColumn: '',
    footer: null,
    collapsed: false,
};
