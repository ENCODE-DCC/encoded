import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import url from 'url';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../libs/ui/modal';
import { encodedURIComponent } from '../libs/query_encoding';
import * as Pager from '../libs/ui/pager';
import QueryString from '../libs/query_string';
import * as globals from './globals';
import { TableItemCount } from './objectutils';
import { FacetList } from './search';
import { ViewControls } from './view_controls';


/**
 * Default number of results when no "limit=x" specified in the query string. Determined by our
 * back-end search code.
 */
const DEFAULT_PAGE_LIMIT = 25;

/**
 * Maximum number of results we can set "from=x" that elasticsearch allows.
 */
const MAX_VIEWABLE_RESULTS = 99999;


/**
 * A single instance of this class gets used to register special-case displays of data in a cell in
 * cases where the default renderer won't do. You can register rendering components for a specific
 * field regardless of the "type=x" type, or you can register one for a specific field only when
 * a specific "type=x" type gets displayed.
 */
class ReportDataRegistryCore {
    constructor() {
        this._registry = {};
    }

    /**
     * Utility to convert a field and type to a key used to retrieve a rendering component. For
     * fields used regardless of the type, use "*" as the type.
     * @param {string} field: search result `field` value to match.
     * @param {string} type: "type=" type to optionally match.
     *
     * @return {string} Key corresponding to the given field and type.
     */
    static _generateKey(field, type) {
        return `${field}-${type || '*'}`;
    }

    /**
     * Register a React component to render a type-field or *-field pair.
     * @param {object} {field, type} Field and type to register component for; type optional
     * @param {array} component Rendering component to call for this field-type value
     */
    register({ field, type }, component) {
        const key = ReportDataRegistryCore._generateKey(field, type);
        if (this._registry[key]) {
            // Registering key already exists.
            console.warn('ReportDataRegistry collision %s:%s', field, type);
        } else {
            this._registry[key] = component;
        }
    }

    /**
     * Look up the view registered for the given search-result field and type. If no rendering
     * components have been registered to match the given field and type, it then searches for
     * registered for the field for any type.
     * @param {string} field Field to match
     * @param {string} type to match
     *
     * @return {array} Array of available/registered views for the given type.
     */
    lookup(field, type) {
        return this._registry[ReportDataRegistryCore._generateKey(field, type)] || this._registry[ReportDataRegistryCore._generateKey(field, '*')];
    }
}

const ReportDataRegistry = new ReportDataRegistryCore();


/**
 * @id cell renderer that displays the accession and links to the object.
 */
const AtIdRenderer = ({ value }) => (
    <a href={value}>{globals.atIdToAccession(value)}</a>
);

AtIdRenderer.propTypes = {
    /** @id value to render */
    value: PropTypes.any.isRequired,
};

ReportDataRegistry.register({ field: '@id' }, AtIdRenderer);
ReportDataRegistry.register({ field: 'dataset', type: 'File' }, AtIdRenderer);


/**
 * Accession renderer that links to the object.
 */
const AccessionRenderer = ({ value, item }) => (
    <>{value ? <a href={item['@id']}>{value}</a> : null}</>
);

AccessionRenderer.propTypes = {
    /** Accession to render */
    value: PropTypes.string,
    /** Object being rendered in the row */
    item: PropTypes.object.isRequired,
};

AccessionRenderer.defaultProps = {
    value: '',
};

ReportDataRegistry.register({ field: 'accession' }, AccessionRenderer);
ReportDataRegistry.register({ field: 'title', type: 'File' }, AccessionRenderer);


/**
 * `related_series` renderer for type=Experiment. Displays a comma-separated list of their @ids.
 */
const ExperimentRelatedSeriesRenderer = ({ value }) => {
    if (value && typeof value === 'object' && Array.isArray(value) && value.length > 0) {
        return value.map(relatedSeries => relatedSeries['@id']).join();
    }
    return null;
};

ReportDataRegistry.register({ field: 'related_series', type: 'Experiment' }, ExperimentRelatedSeriesRenderer);


/**
 * `thumb_nail` renderer for type=Image. Displays an image thumbnail that links to a full-size
 * image.
 */
const ImageThumbnailRenderer = ({ value }) => (
    <div className="tcell-thumbnail">
        <a href={value} target="_blank" rel="noopener noreferrer">
            <img src={value} alt={value} />
        </a>
    </div>
);

ImageThumbnailRenderer.propTypes = {
    /** Path of image to display */
    value: PropTypes.string.isRequired,
};

ReportDataRegistry.register({ field: 'thumb_nail', type: 'Image' }, ImageThumbnailRenderer);


/**
 * Displays the image download_url path as a link to the image.
 */
const ImageDownloadRenderer = ({ value }, reactContext) => {
    const parsedUrl = url.parse(reactContext.location_href);
    return <a href={`${parsedUrl.protocol}//${parsedUrl.host}${value}`}>{value}</a>;
};

ImageDownloadRenderer.propTypes = {
    /** path to image */
    value: PropTypes.string.isRequired,
};

ImageDownloadRenderer.contextTypes = {
    location_href: PropTypes.string,
};

ReportDataRegistry.register({ field: 'download_url', type: 'Image' }, ImageDownloadRenderer);


/**
 * `files` renderer for type=Experiment. Displays a comma separated list of accessions that link to
 * the corresponding file page.
 */
const ExperimentFilesRenderer = ({ value }) => {
    if (value && typeof value === 'object' && Array.isArray(value) && value.length > 0) {
        return value.map(file => <a key={file} href={file}>{globals.atIdToAccession(file)}</a>).reduce((prev, curr) => [prev, ', ', curr]);
    }
    return null;
};

ReportDataRegistry.register({ field: 'files.@id', type: 'Experiment' }, ExperimentFilesRenderer);


/**
 * Make complete URLs from the file download paths.
 */
const FileDownloadHref = ({ value }, reactContext) => {
    const parsedUrl = url.parse(reactContext.location_href);
    return `${parsedUrl.protocol}//${parsedUrl.host}${value}`;
};

FileDownloadHref.contextTypes = {
    location_href: PropTypes.string,
};

ReportDataRegistry.register({ field: 'href', type: 'File' }, FileDownloadHref);


/**
 * Extract the value of an object property based on a dotted-notation field,
 * e.g. { a: 1, b: { c: 5 }} you could retrieve the 5 by passing 'b.c' in `field`. Cannot use the
 * simple one in the cart code as this one has to handle more complicated objects in a way that
 * works for reports.
 * Based on https://stackoverflow.com/questions/6393943/convert-javascript-string-in-dot-notation-into-an-object-reference#answer-6394168
 * @param {object} object Object containing the value you want to extract.
 * @param {string} field  Dotted notation for the property to extract.
 *
 * @return {value} Whatever value the dotted notation specifies, or undefined.
 */
const getObjectPropValue = (object, field) => {
    let rawValue;

    // Break the specified property into its dot-separated components.
    const propNameParts = field.split('.');
    if (propNameParts.length > 1) {
        // Extract from an embedded array or object. Use the property name parts to drill into
        // `object`.
        rawValue = propNameParts.reduce((extractedObject, propNamePart) => {
            if (extractedObject && Array.isArray(extractedObject)) {
                // Get the requested property out of each of the objects within the extracted array.
                return extractedObject.map(partObjectElement => partObjectElement[propNamePart] || '');
            }

            // The requested property has a primitive type or an object.
            return extractedObject && extractedObject[propNamePart];
        }, object);
    } else {
        // Extract a top-level property.
        rawValue = object[field];
    }

    return rawValue;
};


/**
 * Reduces an array, object, or array of objects into something generically displayable.
 * @param {value,object,array} rawValue Value to reduce to a displayable form.
 */
const reduceComplexValue = (rawValue) => {
    let result = rawValue;
    if (typeof rawValue === 'object') {
        if (Array.isArray(rawValue)) {
            // Flatten and dedupe arrays.
            const flattenedValue = _.chain(rawValue)
                .flatten()
                .uniq()
                .value();

            // Take care of arrays by concatenting their elements into one string.
            result = flattenedValue.map((item) => {
                if (typeof item === 'object') {
                    // The array contains objects. If each object has an @id, display that.
                    if (item['@id']) {
                        return item['@id'];
                    }

                    // Objects don't contain an @id, so display a stringified object.
                    return JSON.stringify(item);
                }

                // Item has a simple value.
                return item;
            }).join(', ');
        } else if (rawValue['@id']) {
            // For objects with @ids, just display the @id of that object.
            result = rawValue['@id'];
        } else {
            // For objects without @ids, stringify the object.
            result = JSON.stringify(rawValue);
        }
    }
    return result;
};


/**
 * Render each cell of the table header. This exists as a component mostly to reduce code
 * duplication in the parent.
 */
const ReportHeaderCell = ({ title, sortable, sortIcon }) => (
    <React.Fragment>
        {title}
        {sortable && sortIcon ?
            <i className={`icon ${sortIcon}`} />
        : null}
    </React.Fragment>
);

ReportHeaderCell.propTypes = {
    /** Display title in header cell */
    title: PropTypes.string.isRequired,
    /** True if column is sortable */
    sortable: PropTypes.bool.isRequired,
    /** CSS class for sorting icon to display */
    sortIcon: PropTypes.string,
};

ReportHeaderCell.defaultProps = {
    sortIcon: '',
};


/**
 * Display the header row of the report table.
 */
const NAV_HEIGHT = 40;
const ReportHeader = ({ context, allColumns, visibleFields, tableRef }) => {
    /** Ref for the table <thead> */
    const headerRef = React.useRef(null);

    // Extract the sorting field and direction from the report results.
    const sortField = context.sort ? Object.keys(context.sort)[0] : '';
    const sortDirection = sortField ? context.sort[sortField].order : '';

    // Extract current query string so we can use it for each of the column headers for sorting.
    const parsedUrl = url.parse(context['@id']);
    const query = new QueryString(parsedUrl.query);

    React.useEffect(() => {
        // Implements the sticky header for the table. On scroll events, check if the top
        // coordinate of the table is above the bottom of the navigation bar. If it is, set the
        // translation of the thead to hold it in place. Support sticky header only if
        // screen_lg_min breakpoint or wider met.
        const handleScroll = () => {
            if (tableRef.current && headerRef.current && globals.isMediaQueryBreakpointActive('MD')) {
                const tableTop = tableRef.current.getBoundingClientRect().top - NAV_HEIGHT;
                if (tableTop < 0) {
                    // Table top above the bottom of the navigation bar; keep the thead pinned
                    // there.
                    headerRef.current.style.cssText = `transform: translateY(${-tableTop}px)`;
                } else {
                    // Table top below the bottom of the navigation bar; put the thead in its
                    // natural place.
                    headerRef.current.style.cssText = '';
                }
            }
        };

        window.addEventListener('scroll', handleScroll, { passive: true });

        return () => window.removeEventListener('scroll', handleScroll);
    });

    return (
        <thead ref={headerRef}>
            <tr>
                {visibleFields.map((field) => {
                    // Determine whether the column is sortable or not.
                    const sortable = !context.non_sortable.includes(field);

                    // Determine the column header title from `allColumns`, or from any available
                    // columns in `context.columns` if `allColumns` has not yet loaded.
                    let title;
                    if (allColumns) {
                        title = allColumns[field];
                    } else if (context.columns[field]) {
                        title = context.columns[field].title;
                    } else {
                        // Display no title until `allColumns` eventually loads.
                        title = '';
                    }

                    // Generate a sorting href for this column header.
                    let sortIcon;
                    const fieldQuery = query.clone();
                    if (sortable) {
                        if (field === sortField) {
                            // Current column is the sorting column. Clicks on this header change the
                            // sort direction.
                            fieldQuery.replaceKeyValue('sort', sortDirection === 'desc' ? field : `-${field}`);
                            sortIcon = `icon-sort-${sortDirection}`;
                        } else {
                            // Not the sorting column, so this href sorts on this field.
                            fieldQuery.replaceKeyValue('sort', field);
                            sortIcon = 'icon-sort';
                        }
                    }

                    return (
                        <th key={field}>
                            {sortable ?
                                <a href={`?${fieldQuery.format()}`} className={`report-header-cell${sortable ? ' report-header-cell--sortable' : ''}`}>
                                    <ReportHeaderCell title={title} sortable={sortable} sortIcon={sortIcon} />
                                </a>
                            :
                                <div className="report-header-cell">
                                    <ReportHeaderCell title={title} sortable={sortable} />
                                </div>
                            }
                        </th>
                    );
                })}
            </tr>
        </thead>
    );
};

ReportHeader.propTypes = {
    /** Report data JSON */
    context: PropTypes.object.isRequired,
    /** All column fields and titles; loaded with separate GET request */
    allColumns: PropTypes.object,
    /** Indicates visibility of each column of report */
    visibleFields: PropTypes.array.isRequired,
    /** Ref for the <table> DOM element */
    tableRef: PropTypes.object,
};

ReportHeader.defaultProps = {
    allColumns: null,
    tableRef: null,
};


/**
 * Display all the data rows of the report table.
 */
const ReportData = ({ context, visibleFields, type }) => (
    <tbody>
        {context['@graph'].map(item => (
            <tr key={item['@id']}>
                {visibleFields.map((field) => {
                    // Get the value of the property in `item` and see if the currenet field and
                    // type have a registered renderer.
                    const value = getObjectPropValue(item, field);
                    const ReportCellRenderer = ReportDataRegistry.lookup(field, type);
                    if (ReportCellRenderer) {
                        // Registered renderer available, so use that to render the value of the
                        // cell.
                        return (
                            <td key={field}>
                                <ReportCellRenderer value={value} field={field} item={item} />
                            </td>
                        );
                    }

                    // No registered renderer. Convert any complex values to a displayable string
                    // and display that.
                    const reducedValue = reduceComplexValue(value);
                    return (
                        <td key={field}>
                            {reducedValue}
                        </td>
                    );
                })}
            </tr>
        ))}
    </tbody>
);

ReportData.propTypes = {
    /** Report data JSON */
    context: PropTypes.object.isRequired,
    /** Indicates visibility of each column of report */
    visibleFields: PropTypes.array.isRequired,
    /** Currently selected type for the report */
    type: PropTypes.string.isRequired,
};


/**
 * Displays the controls at the top of the column selection modal.
 */
const ColumnSelectorControls = ({ handleSelectAll, handleSelectOne, handleSortChange, firstColumnTitle }) => {
    const [selectedSort, setSelectedSort] = React.useState('default');

    // Called when the user changes the sorting option. Sets a component state so that the
    // controlled <select> component renders properly. It then calls the parent's callback to react
    // to the new sorting option.
    const handleOnChange = (e) => {
        setSelectedSort(e.target.value);
        handleSortChange(e.target.value);
    };

    return (
        <div className="column-selector__controls">
            <div className="column-selector__utility-buttons">
                <button onClick={handleSelectAll} className="btn btn-info">Select all</button>
                <button onClick={handleSelectOne} className="btn btn-info">Select {firstColumnTitle} only</button>
            </div>
            <div className="column-selector__sort-selector">
                <select className="form-control--select" value={selectedSort} onChange={handleOnChange}>
                    <option value="default">Default sort</option>
                    <option value="alpha">Alphabetical sort</option>
                </select>
            </div>
        </div>
    );
};

ColumnSelectorControls.propTypes = {
    /** Callback when Select All button clicked */
    handleSelectAll: PropTypes.func.isRequired,
    /** Callback when SelectOne button clicked */
    handleSelectOne: PropTypes.func.isRequired,
    /** Callback when sorting option changed */
    handleSortChange: PropTypes.func.isRequired,
    /** Title of first column */
    firstColumnTitle: PropTypes.string.isRequired,
};


/**
 * Extract the list of column fields from `columns`, with an order according to the given sorting
 * option.
 * @param {object} columns - Object mapping column fields to titles
 * @param {bool} sorted - True to retrieve fields sorted by their titles
 *
 * @return (array) - List of column paths, optionally sorted.
 */
function getColumnFields(columns, sorted) {
    const columnPaths = Object.keys(columns);
    if (sorted) {
        columnPaths.sort((aKey, bKey) => {
            const aTitle = columns[aKey].toLowerCase();
            const bTitle = columns[bKey].toLowerCase();
            return (aTitle < bTitle ? -1 : (bTitle < aTitle ? 1 : 0));
        });
    }
    return columnPaths;
}


/**
 * Render one column selector item.
 */
const ColumnItem = ({ field, title, selected, toggleColumn }) => {
    const handleChange = () => {
        toggleColumn(field);
    };

    return (
        <div className="column-selector__selector-item">
            <input id={field} type="checkbox" onChange={handleChange} checked={selected} />
            <label htmlFor={field}>{title}</label>
        </div>
    );
};

ColumnItem.propTypes = {
    /** encoded field name for the column */
    field: PropTypes.string.isRequired,
    /** Title for the checkbox; same as column header title */
    title: PropTypes.string.isRequired,
    /** True for selected columns; i.e. checked checkboxes */
    selected: PropTypes.bool.isRequired,
    /** Parent function to call when item is clicked */
    toggleColumn: PropTypes.func.isRequired,
};


/**
 * Displays a modal dialog with every possible column for the type of object being displayed. This
 * lets you choose which columns you want to appear in the report.
 */
const ColumnSelector = ({ allColumns, visibleFields, setVisibleFields, closeSelector }) => {
    /** Field names of columns currently selected for display */
    const [selectedFields, setSelectedFields] = React.useState(visibleFields);
    /** True if column list appears sorted */
    const [sorted, setSorted] = React.useState(false);

    // Get all the the column field names, sorting them by the corresponding column title if the
    // user asked for that.
    const columnFields = getColumnFields(allColumns, sorted === 'alpha');

    const toggleColumn = (clickedField) => {
        let updatedColumns;

        // Called every time a column's checkbox gets clicked on or off in the modal.
        if (selectedFields.includes(clickedField)) {
            // The clicked column is currently visible, so before we make it invisible, make sure
            // at least one other column is also visible.
            if (Object.keys(selectedFields).length === 1) {
                // Unchecking the the only checked checkbox, so ignore the click.
                return;
            }

            // Remove selected column field from selectedColumns.
            updatedColumns = selectedFields.filter(field => field !== clickedField);
        } else {
            updatedColumns = selectedFields.concat(clickedField);
        }

        // Either a checkbox is being turned on, or it's being turned off and another checkbox is
        // still checked. Change the component state to reflect the new checkbox states. Presumably
        // if the setState callback returned no properties setState becomes a null op, so the above
        // test could be done inside the setState callback. The React docs don't say what happens
        // if you return no properties (https://reactjs.org/docs/react-component.html#setstate) so
        // I avoided doing this.
        setSelectedFields(updatedColumns);
    };

    const submitHandler = () => {
        // Called when the user clicks the Select button in the column checkbox modal, which
        // sets a new state for all checked report columns.
        setVisibleFields(selectedFields);
    };

    const handleSelectAll = () => {
        // Called when the user clicks "Select all."
        setSelectedFields(Object.keys(allColumns));
    };

    const handleSelectOne = () => {
        setSelectedFields(['@id']);
    };

    // Called when the sorting option gets changed.
    const handleSortChange = (selectedSortOption) => {
        setSorted(selectedSortOption);
    };

    return (
        <Modal addClasses="column-selector" closeModal={closeSelector}>
            <ModalHeader title="Select columns to view" closeModal={closeSelector} />
            <ColumnSelectorControls
                handleSelectAll={handleSelectAll}
                handleSelectOne={handleSelectOne}
                handleSortChange={handleSortChange}
                firstColumnTitle={Object.keys(allColumns)[0]}
            />
            <ModalBody>
                <div className="column-selector__selectors">
                    {columnFields.map(field => <ColumnItem key={field} field={field} title={allColumns[field]} selected={selectedFields.includes(field)} toggleColumn={toggleColumn} />)}
                </div>
            </ModalBody>
            <ModalFooter
                closeModal={closeSelector}
                submitBtn={submitHandler}
                submitTitle="View selected columns"
            />
        </Modal>
    );
};

ColumnSelector.propTypes = {
    /** All possible columns for the current type, and their titles */
    allColumns: PropTypes.object.isRequired,
    /** Specifies currently selected columns and their titles */
    visibleFields: PropTypes.array.isRequired,
    /** Function to call when user has specified the selected columns */
    setVisibleFields: PropTypes.func.isRequired,
    /** Called when the user wants to close the selector modal without change */
    closeSelector: PropTypes.func.isRequired,
};


/**
 * Load the schema corresponding to the given type, where `type` contains an encode @type.
 * @param type {string} Selects schema based on @type
 *
 * @return {promise} Schema corresponding to selected `type`; null if error.
 */
const loadSchemaColumns = type => (
    fetch('/profiles/', {
        method: 'GET',
        headers: { Accept: 'application/json' },
    }).then((response) => {
        // Convert the response to JSON.
        if (response.ok) {
            return response.json();
        }
        return Promise.resolve(null);
    }).then(responseJson => (responseJson ? responseJson[type] : null))
);


/**
 * Generate an object containing the title and visibility status of every possible column for the
 * current type. These get collected from the returned JSON `columns` property as well as the
 * `properties` of the matching schema.
 */
const generateColumns = (context, schema) => {
    const generatedColumns = {};

    // Convert `columns` from returned JSON to our columns object, and make an array of column
    // titles for each deduping later.
    const columnTitles = [];
    Object.keys(context.columns).forEach((column) => {
        generatedColumns[column] = context.columns[column].title;
        columnTitles.push(generatedColumns[column]);
    });

    // Convert the schema properties to our columns object.
    Object.keys(schema.properties).forEach((column) => {
        // Only include if the search result columns doesn't already have the property, and only if
        // the schema property title doesn't match an existing search result columns title.
        if (!generatedColumns[column] && !columnTitles.includes(schema.properties[column].title)) {
            generatedColumns[column] = schema.properties[column].title;
        }
    });
    return generatedColumns;
};


/**
 * Displays a control allowing the user to select the maximum number of items to display on one page.
 */
const pageLimitOptions = [25, 50, 100, 200];
const PageLimitSelector = ({ pageLimit, query }) => (
    <div className="page-limit-selector">
        <div className="page-limit-selector__label">Items per page:</div>
        <div className="page-limit-selector__options">
            {pageLimitOptions.map((limit) => {
                // When changing the number of items per page, also go back to the first page by
                // removing the "from=x" query-string parameter.
                const limitQuery = query.clone();
                limitQuery.deleteKeyValue('from');
                if (limit === DEFAULT_PAGE_LIMIT) {
                    limitQuery.deleteKeyValue('limit');
                } else {
                    limitQuery.replaceKeyValue('limit', limit);
                }

                return (
                    <a
                        key={limit}
                        href={`?${limitQuery.format()}`}
                        className={`page-limit-selector__option${limit === pageLimit ? ' page-limit-selector__option--selected' : ''}`}
                        aria-label={`Show ${limit} items per page`}
                    >
                        {limit}
                    </a>
                );
            })}
        </div>
    </div>
);

PageLimitSelector.propTypes = {
    /** New page limit to display */
    pageLimit: PropTypes.number.isRequired,
    /** Current page's QueryString query */
    query: PropTypes.object.isRequired,
};


/**
 * Renderer for the entire /report/ page.
 */
const Report = ({ context }, reactContext) => {
    /** All possible columns for the current type */
    const [allColumns, setAllColumns] = React.useState(null);
    /** True if column selector modal visible */
    const [selectorOpen, setSelectorOpen] = React.useState(false);
    /** True if request for schema in progress */
    const schemaLoadInProgress = React.useRef(false);
    /** True if we have requested a redirect; prevents state changes from multiple redirects */
    const redirectInProgress = React.useRef(false);
    /** Table DOM element to handle its sticky header */
    const tableRef = React.useRef(null);

    // Calculate values from the search results and query string usuable by the rest of the
    // component. The back end report code allows exactly one "type=x" parameter.
    const parsedUrl = React.useMemo(() => url.parse(context['@id']), [context]);
    const query = React.useMemo(() => new QueryString(parsedUrl.query), [parsedUrl]);
    const fieldOrder = React.useMemo(() => (allColumns ? Object.keys(allColumns) : Object.keys(context.columns)), [allColumns, context.columns]);
    const typeFilter = context.filters.find(filter => filter.field === 'type');
    const type = typeFilter.term;

    // Based on the query string's "field=x" elements, generate an array of visible columns
    // properties. If no "field=x" elements exist in the query string, use the search results'
    // `columns` property instead as default columns.
    const visibleFields = React.useMemo(() => {
        const fieldValues = query.getKeyValues('field');
        const fields = fieldValues.length > 0 ? fieldValues : Object.keys(context.columns);

        // Sort the fields according to the order in the schema or result columns.
        const result = _(fields).sortBy((field) => {
            const index = fieldOrder.indexOf(field);
            return index >= 0 ? index : fieldOrder.length + 1;
        });
        return result;
    }, [context.columns, query, fieldOrder]);

    // Get the current value of the "limit=x" query string parameter. No "limit=x" means the
    // default value applies. The back end allows exactly zero or one "limit=x" parameter.
    const pageLimit = React.useMemo(() => {
        const limitValues = query.getKeyValues('limit');
        return limitValues.length === 1 ? Number(limitValues[0]) || DEFAULT_PAGE_LIMIT : DEFAULT_PAGE_LIMIT;
    }, [query]);

    // Calculate the current page number and total number of pages. The current page number relies
    // on the current "from=x" query string parameter, which the back end allows exactly zero or
    // one of.
    const fromIndices = query.getKeyValues('from');
    const fromIndex = fromIndices.length === 1 ? Number(fromIndices[0]) : 0;
    const currentPage = (fromIndex / pageLimit) + 1;
    const viewableTotal = Math.min(context.total, MAX_VIEWABLE_RESULTS - pageLimit);
    const totalPages = Math.trunc(viewableTotal / pageLimit) + (viewableTotal % pageLimit > 0 ? 1 : 0);

    // Called when the user requests the column-selector modal.
    const openColumnSelector = () => {
        setSelectorOpen(true);
    };

    // Called when the user closes the column-selector modal.
    const closeColumnSelector = () => {
        setSelectorOpen(false);
    };

    // Called when the user selects a new set of visible columns. Generate a new set of "field="
    // queries based on the newly selected visible columns and navigate to the new query.
    const handleColumnSelection = React.useCallback((selectedColumns) => {
        const sortedColumns = _(selectedColumns).sortBy(field => fieldOrder.indexOf(field));

        // Convert the newly selected columns to a "field=x&field=y..." query.
        const fieldQuery = sortedColumns.map(field => `field=${encodedURIComponent(field)}`).join('&');

        // Get the existing query string and strip out any existing "field=x" elements.
        const columnQuery = query.clone();
        const strippedQuery = columnQuery.deleteKeyValue('field');

        // Navigate to the stripped query concatenated with the new field query.
        const href = `?${strippedQuery.format()}&${fieldQuery}`;
        reactContext.navigate(href);
    }, [query, reactContext, fieldOrder]);

    // Called when the user selects a new page number from the pagination control. Generate a
    // query string using a "first=x" query string parameter for the page and navigate to it.
    const handlePagerClick = (newPageNumber) => {
        // Map the page number to the corresponding "first=x" query string parameter.
        const firstSearchIndex = (newPageNumber - 1) * pageLimit;

        // Add the new "first=x" query string parameter, or remove it for the first page.
        const indexQuery = query.clone();
        if (firstSearchIndex === 0) {
            indexQuery.deleteKeyValue('from');
        } else {
            indexQuery.replaceKeyValue('from', firstSearchIndex);
        }

        // Navigate to the new query string.
        const href = `?${indexQuery.format()}`;
        reactContext.navigate(href);
    };

    React.useEffect(() => {
        // If we haven't yet, load the schema matching the given "type=" type to generate the
        // columns object.
        if (!schemaLoadInProgress.current && !allColumns) {
            schemaLoadInProgress.current = true;
            loadSchemaColumns(type).then((schema) => {
                schemaLoadInProgress.current = false;

                // Use the search results and the loaded schema's `properties` to generate a list
                // of columns to display.
                const generatedColumns = generateColumns(context, schema);
                setAllColumns(generatedColumns);
            });
        }
    }, [context, schemaLoadInProgress, allColumns, type]);

    React.useEffect(() => {
        // If a facet selection leaves fewer pages than the current page, redirect to the same url
        // but on the first page, by removing the "from=x" query-string parameter.
        if (currentPage > totalPages && !redirectInProgress.current) {
            redirectInProgress.current = true;
            const noFromQuery = query.clone();
            noFromQuery.deleteKeyValue('from');
            reactContext.navigate(`?${noFromQuery.format()}`);
        }
    }, [currentPage, totalPages, query, reactContext]);

    // Compose download-TSV link by keeping the query string and replacing the path with /report.tsv.
    const downloadTsvPath = `/report.tsv${parsedUrl.path.slice(parsedUrl.pathname.length)}`;

    // No filled facets means no results, and we should display the notification from the back end
    // instead of the report.
    const facetdisplay = context.facets && context.facets.some(facet => facet.total > 0);
    if (facetdisplay) {
        return (
            <div className="search-results">
                <FacetList context={context} facets={context.facets} filters={context.filters} docTypeTitleSuffix="report" />
                <div className="search-results__report-list">
                    <div className="results-table-control">
                        <div className="results-table-control__main">
                            <ViewControls results={context} />
                            <button className="btn btn-info btn-sm" title="Choose columns" onClick={openColumnSelector} disabled={!allColumns}>
                                <i className="icon icon-columns" /> Columns
                            </button>
                            <a className="btn btn-info btn-sm" href={downloadTsvPath} data-bypass data-test="download-tsv">Download TSV</a>
                        </div>
                    </div>
                    <div className="results-table-control__pager">
                        <PageLimitSelector pageLimit={pageLimit} query={query} />
                        {totalPages > 1 ?
                            <Pager.Multi currentPage={currentPage} total={totalPages} clickHandler={handlePagerClick} />
                        : null}
                    </div>
                    {viewableTotal < context.total ?
                        <div className="report-max-warning">Not all items viewable. Download TSV for all items.</div>
                    : null}
                    <TableItemCount count={`Showing results ${fromIndex + 1} to ${Math.min(context.total, fromIndex + pageLimit)} of ${context.total}`} />
                    <div className="report__table">
                        <table className="table table-striped" ref={tableRef}>
                            <ReportHeader context={context} visibleFields={visibleFields} allColumns={allColumns} tableRef={tableRef} />
                            <ReportData context={context} visibleFields={visibleFields} type={type} />
                        </table>
                    </div>
                </div>
                {selectorOpen ?
                    <ColumnSelector
                        allColumns={allColumns}
                        visibleFields={visibleFields}
                        setVisibleFields={handleColumnSelection}
                        closeSelector={closeColumnSelector}
                    />
                : null}
            </div>
        );
    }
    return <h4>{context.notification}</h4>;
};

Report.propTypes = {
    /** Report search results */
    context: PropTypes.object.isRequired,
};

Report.contextTypes = {
    navigate: PropTypes.func,
};

globals.contentViews.register(Report, 'Report');
