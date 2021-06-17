/**
 * @fileOverview Provides a generic component for displaying a table of data where you can
 *               individually style each cell and row. You need to convert the data you want to
 *               display in a table to a format this component can understand, and that could
 *               mean simply providing a table of values to display, or as much as providing a
 *               table of React components and CSS styles to display.
 *
 * For syntax (approximate) usage, see:
 * https://developer.mozilla.org/en-US/docs/Web/CSS/Value_definition_syntax
 *
 * tableData:
 * {
 *     rows: array of [
 *         arrays (rows) of [ <individual values> || <objects containing content and metadata> ] ||
 *         <object:
 *             rowContent: array of [ <individual values> || <objects containing content and metadata> ]
 *             css?: <string> - CSS classes to add to this <tr>; overrides "rowCss" below
 *         >
 *     ]
 *     rowKeys?: <array> - Unique values to consistently identify each row's React key
 *     tableCss?: <string> - CSS classes to add to enclosing <table>
 *     rowCss?: <string> - CSS classes to add to all <tr> in table except where overridden
 * }
 *
 * Objects containing content and metadata:
 * {
 *     content: [ <individual value> | <content function returning jsx> | <jsx> ] into a <td>
 *     header: [ <individual value> | <content function returning jsx> | <jsx> ] into a <th>
 *             Note: If both `content` and `header` given, `header` gets ignored.
 *     css?: <string> - CSS classes to add to <td> or <th>
 *     style?: <object> - CSS styles (not classes) to add to <td> or <th>
 *     colSpan?: <number> - Number of columns this cell should span; 0 for full table width
 * }
 *
 * Content function returning jsx:
 * function contentFunc(
 *     col,    // Zero-based column number of cell; colSpan columns count as 1
 *     row,    // Zero-based row number of cell
 *     value,  // Value to display
 *     meta)   // Extra data in whatever format the content function understands
 *
 * Example tableData object and content function:
 * const contentFunc = (col, row, value, meta) => (
 *     <span><i>{col}</i>:<strong>{row}</strong>:<span style={{ backgroundColor: meta ? meta.color : '#00FF00' }}>{value + (meta ? meta.adder : 0)}</span></span>
 * );
 * const tableData = {
 *     rows: [
 *         [1, 2, { content: 3, style: { fontWeight: 100 } }, 4, { content: <span style={{ fontWeight: 'bold' }}>5</span> }, 6],
 *         [{ content: 7, css: 'cell-override' }, 8, { content: 'Special case', colSpan: 3 }, { content: contentFunc, value: 8 }],
 *         { rowContent: [13, { content: () => <i>5</i> }, null, { content: contentFunc, value: 16 }, 17, 18], css: 'row-class' },
 *         [19, 20, { content: contentFunc, value: 20, meta: { adder: 1, color: '#FFFF00' }}, 22, 23, 24]
 *         [{ content: 'Full Width', colSpan: 0, style: { textAlign: 'center', backgroundColor: '#c0c0ff' } }],
 *     ],
 *     rowCss: 'overall-row',
 *     tableCss: 'overall-table',
 * };
 *
 * Displays:
 * 1  2  3      4      5    6
 * 7  8  Special case       3:1:8
 * 13 5         3:2:16 17   18
 * 19 20 2:3:21 22     23   24
 *         Full Width
 *
 * ...where the "5" in the first row is bold as is the middle number in the two cells with
 * `contentFunc` output, and the "3" appears lightweight. The first number in `contentFunc` output
 * is italic, the middle is bold, and the last has a colored background. Each <tr> in the table has
 * a CSS class of "overall-row" except the third which has "row-class". The "7" in the second row's
 * <td> has a css class of "cell-override", and the "5" in the third row is italic. The third
 * column of the third row is an empty <td> because of the null value in the `rowContent` array.
 *
 * Notes:
 * - `rows` array is the only required property of `tableData`.
 * - Each element of `row` must be either an array of elements to display in a single row, or an
 *   object that must have a `rowContent` property.
 * - The `rowContent` property must be an array of elements to display in a single row -- just like
 *   a single element of the parent `rows` property.
 *
 * Why use `content` instead of a simple value?
 *   - to add a CSS class or style to a specific cell
 *   - to add a colSpan to a specific cell
 *   - to have a cell rendered by a function returning jsx, or jsx itself
 *
 * Why use `rowContent` instead of an array of values and functions?
 *   - to add a CSS class to the <tr> for a specific row
 */

import PropTypes from 'prop-types';


/**
  * Determine the maximum number of columns of all rows in `DataTable` data.
  * @param {object} tableData Same table data you pass to `DataTable`.
  */
const tableDataMaxWidth = (tableData) => {
    const widths = tableData.rows.map((row) => (Array.isArray(row) ? row.length : row.rowContent.length));
    return Math.max(...widths);
};


/**
 * Display a table of data with customizable styles per cell and per row, and with column spans.
 */
const DataTable = ({ tableData }) => {
    let colNumber;
    let cellContent;
    let maxWidth;

    return (
        <table className={tableData.tableCss || null}>
            <tbody>
                {tableData.rows.map((row, rowNumber) => {
                    // Get array of values representing a row or the `rowContent` array if the row
                    // is an object.
                    const cells = Array.isArray(row) ? row : row.rowContent;
                    const rowKey = tableData.rowKeys ? tableData.rowKeys[rowNumber] : rowNumber;
                    colNumber = 0;
                    return (
                        <tr key={rowKey} className={row.css || tableData.rowCss || null} style={row.style || null}>
                            {cells.map((cell, colIndex) => {
                                // Extract the cell's content from itself, its object, or its
                                // function. JS says `typeof null` is "object."
                                const cellType = typeof cell;
                                const cellValue = (cell !== null) && (cell.content || cell.header);
                                if (cellType === 'object' && cell !== null) {
                                    if (typeof cellValue === 'function') {
                                        // Need to call a function to get the cell's content.
                                        cellContent = cellValue(colNumber, rowNumber, cell.value, cell.meta);
                                    } else {
                                        // The cell content is right in the `content` or `header`.
                                        cellContent = cellValue;
                                    }
                                } else {
                                    // The array element itself is the value.
                                    cellContent = cell;
                                }
                                colNumber += 1;

                                // Cell's colSpan can be a specific number, 0 (full width), or
                                // undefined (default of 1).
                                let cellColSpan = (typeof cell === 'object' && cell !== null) && cell.colSpan;
                                if (cellColSpan === 0) {
                                    // Request for colSpan to be whatever the maximum width of the
                                    // table. Use or get cached value.
                                    if (maxWidth === undefined) {
                                        maxWidth = tableDataMaxWidth(tableData);
                                    }
                                    cellColSpan = maxWidth;
                                } else if (cellColSpan === undefined) {
                                    // No colSpan defined for this cell, so it's 1.
                                    cellColSpan = 1;
                                }

                                // Render the cell, which could have a column span.
                                const cellCss = (cell && cell.css) || null;
                                const cellStyle = (cell && cell.style) || null;
                                if (cellColSpan > 1) {
                                    if (cell && cell.header) {
                                        return <th key={colIndex} colSpan={cellColSpan} className={cellCss} style={cellStyle}>{cellContent}</th>;
                                    }
                                    return <td key={colIndex} colSpan={cellColSpan} className={cellCss} style={cellStyle}>{cellContent}</td>;
                                }
                                if (cell && cell.header) {
                                    return <th key={colIndex} className={cellCss} style={cellStyle}>{cellContent}</th>;
                                }
                                return <td key={colIndex} className={cellCss} style={cellStyle}>{cellContent}</td>;
                            })}
                        </tr>
                    );
                })}
            </tbody>
        </table>
    );
};

DataTable.propTypes = {
    /** Whole table data */
    tableData: PropTypes.object.isRequired,
};

/**
 * This generates a table but built with div-tags rather than table-tag
 *
 * @param {tableData} Data for the table. It should be an array of arrays of object. For example-
 * [
 *  [{className: id: 'an-id', 'a-class', style: 'a-style', content: <span>text</span>}],
 *  [{className: id: 'an-id2', 'a-class-2', style: 'a-style-2', content: <span>text 2</span>}],
 * ]
 *
 * For entires, id is the key for react. className is the class or classes associated with entry. The style should be an object (key/value pair)
 * of styles. The content should be be markup to display in the table
 *
 * @returns Div-based table
 */
const DivTable = ({ tableData }) => (
    <div className="div-table-matrix">
        {tableData.map((row, rowIndex) => (
            <div key={rowIndex} className="div-table-matrix__row">
                {row.map((rowItem) => (
                    <div key={rowItem.id} className={rowItem.className || (rowIndex === 0 ? 'div-table-matrix__row__header-item' : 'div-table-matrix__row__data-row-item')} style={rowItem.style || null}>
                        {rowItem.content}
                    </div>))}
            </div>))}
    </div>
);

DivTable.propTypes = {
    /** Whole table data */
    tableData: PropTypes.array.isRequired,
};

export {
    DataTable,
    DivTable,
};
