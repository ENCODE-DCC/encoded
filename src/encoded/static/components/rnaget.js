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
import { FacetList, TextFilter } from './search';
import { FetchedData, Param } from './fetched';


const AutocompleteBox = (props) => {
    const terms = props.suggestions['@graph'];
    const { handleClick } = props;

    /* eslint-disable jsx-a11y/no-noninteractive-element-interactions, jsx-a11y/no-noninteractive-tabindex, jsx-a11y/click-events-have-key-events, arrow-body-style */

    return (terms && terms.length > 0) ?
        (
            <ul className="rnaseq-search-autocomplete">
                {terms.map((term) => {
                    return (
                        <li tabIndex="0" key={term.text} onClick={() => handleClick(term.text)}>
                            { term.text }
                        </li>
                    );
                }, this)}
            </ul>
         ) : null;

    /* eslint-enable jsx-a11y/no-noninteractive-element-interactions, jsx-a11y/no-noninteractive-tabindex, jsx-a11y/click-events-have-key-events, arrow-body-style */
};

AutocompleteBox.propTypes = {
    suggestions: PropTypes.object,
    handleClick: PropTypes.func,
};

AutocompleteBox.defaultProps = {
    suggestions: {},
    handleClick: null,
};


/**
 * Default number of results when no "limit=x" specified in the query string. Determined by our
 * back-end search code.
 */
const DEFAULT_PAGE_LIMIT = 100;

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
class RNAGetDataRegistryCore {
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
        const key = RNAGetDataRegistryCore._generateKey(field, type);
        if (this._registry[key]) {
            // Registering key already exists.
            console.warn('RNAGetDataRegistry collision %s:%s', field, type);
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
        return this._registry[RNAGetDataRegistryCore._generateKey(field, type)] || this._registry[RNAGetDataRegistryCore._generateKey(field, '*')];
    }
}

const RNAGetDataRegistry = new RNAGetDataRegistryCore();


/**
 * @id cell renderer that displays the accession and links to the object.
 */
const AtIdRenderer = ({ value }) => (
    <a href={value}>{value.split('/').pop()}</a>
);

AtIdRenderer.propTypes = {
    /** @id value to render */
    value: PropTypes.any.isRequired,
};

RNAGetDataRegistry.register({ field: '@id' }, AtIdRenderer);
RNAGetDataRegistry.register({ field: 'libraryPrepProtocol' }, AtIdRenderer);
RNAGetDataRegistry.register({ field: 'expressionID' }, AtIdRenderer);
RNAGetDataRegistry.register({ field: 'analysis' }, AtIdRenderer);


/**
 * @id cell renderer that displays links to genes from the RNAGet API.
 */
const RNAGetIdRenderer = ({ value }) => (
    <a href={`/genes/${value.split('/')[1]}`}>{value.split('/')[0]}</a>
);

RNAGetIdRenderer.propTypes = {
    /** @id value to render */
    value: PropTypes.any.isRequired,
};

RNAGetDataRegistry.register({ field: 'featureID' }, RNAGetIdRenderer);


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

RNAGetDataRegistry.register({ field: 'accession' }, AccessionRenderer);
RNAGetDataRegistry.register({ field: 'title', type: 'File' }, AccessionRenderer);


/**
 * `related_series` renderer for type=Experiment. Displays a comma-separated list of their @ids.
 */
const ExperimentRelatedSeriesRenderer = ({ value }) => {
    if (value && typeof value === 'object' && Array.isArray(value) && value.length > 0) {
        return value.map((relatedSeries) => relatedSeries['@id']).join();
    }
    return null;
};

RNAGetDataRegistry.register({ field: 'related_series', type: 'Experiment' }, ExperimentRelatedSeriesRenderer);


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

RNAGetDataRegistry.register({ field: 'thumb_nail', type: 'Image' }, ImageThumbnailRenderer);


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

RNAGetDataRegistry.register({ field: 'download_url', type: 'Image' }, ImageDownloadRenderer);


/**
 * `files` renderer for type=Experiment. Displays a comma separated list of accessions that link to
 * the corresponding file page.
 */
const ExperimentFilesRenderer = ({ item }) => {
    if (item.files && item.files.length > 0) {
        return item.files.map((file) => <a key={file['@id']} href={file['@id']}>{globals.atIdToAccession(file['@id'])}</a>).reduce((prev, curr) => [prev, ', ', curr]);
    }
    return null;
};

ExperimentFilesRenderer.propTypes = {
    /** Object (row) currently rendered */
    item: PropTypes.object.isRequired,
};

RNAGetDataRegistry.register({ field: 'files.@id', type: 'Experiment' }, ExperimentFilesRenderer);


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

RNAGetDataRegistry.register({ field: 'href', type: 'File' }, FileDownloadHref);


/**
 * Get the property specified by a field from the search results and return a string from that.
 */
const lookupColumn = (result, column) => {
    let nodes = [result];
    const names = column.split('.');

    for (let i = 0, len = names.length; i < len && nodes.length > 0; i += 1) {
        let nextnodes = [];
        _.each(nodes.map((node) => node[names[i]]), (v) => {
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
    if (nodes.length > 0 && nodes[0]['@id'] !== undefined) {
        nodes = nodes.map((node) => node['@id']);
    }

    // Stringify any nodes that are objects or arrays. Objects and arrays have typeof `object`.
    if (nodes.length > 0) {
        nodes = nodes.map((item) => (typeof item === 'object' ? JSON.stringify(item) : item));
    }

    return _.uniq(nodes).join(', ');
};


/**
 * Render each cell of the table header. This exists as a component mostly to reduce code
 * duplication in the parent.
 */
const RNAGetHeaderCell = ({ title, sortable, sortIcon }) => (
    <>
        {title}
        {sortable && sortIcon ?
            <i className={`icon ${sortIcon}`} />
        : null}
    </>
);

RNAGetHeaderCell.propTypes = {
    /** Display title in header cell */
    title: PropTypes.string.isRequired,
    /** True if column is sortable */
    sortable: PropTypes.bool.isRequired,
    /** CSS class for sorting icon to display */
    sortIcon: PropTypes.string,
};

RNAGetHeaderCell.defaultProps = {
    sortIcon: '',
};


/**
 * Display the header row of the report table.
 */
const NAV_HEIGHT = 40;
const RNAGetHeader = ({ context, allColumns, visibleFields, tableRef }) => {
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
                        ({ title } = context.columns[field]);
                    }

                    // No title available because allColumns not loaded or no column defined in
                    // schema (might be calculated property), then use field as title.
                    if (!title) {
                        title = field;
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
                                    <RNAGetHeaderCell title={title} sortable={sortable} sortIcon={sortIcon} />
                                </a>
                            :
                                <div className="report-header-cell">
                                    <RNAGetHeaderCell title={title} sortable={sortable} />
                                </div>
                            }
                        </th>
                    );
                })}
            </tr>
        </thead>
    );
};

RNAGetHeader.propTypes = {
    /** RNAGet data JSON */
    context: PropTypes.object.isRequired,
    /** All column fields and titles; loaded with separate GET request */
    allColumns: PropTypes.object,
    /** Indicates visibility of each column of report */
    visibleFields: PropTypes.array.isRequired,
    /** Ref for the <table> DOM element */
    tableRef: PropTypes.object,
};

RNAGetHeader.defaultProps = {
    allColumns: null,
    tableRef: null,
};


/**
 * Display all the data rows of the report table.
 */
const RNAGetData = ({ context, visibleFields, type }) => (
    <tbody>
        {context['@graph'].map((item) => (
            <tr key={item['@id']}>
                {visibleFields.map((field) => {
                    // Get the value of the property in `item` and see if the current field and
                    // type have a registered renderer.
                    const value = lookupColumn(item, field, type);
                    const RNAGetCellRenderer = RNAGetDataRegistry.lookup(field, type);
                    if (RNAGetCellRenderer) {
                        // Registered renderer available, so use that to render the value of the
                        // cell.
                        return (
                            <td key={field}>
                                <RNAGetCellRenderer value={value} field={field} item={item} />
                            </td>
                        );
                    }

                    // No registered renderer. Convert any complex values to a displayable string
                    // and display that.
                    return (
                        <td key={field}>
                            {value}
                        </td>
                    );
                })}
            </tr>
        ))}
    </tbody>
);

RNAGetData.propTypes = {
    /** RNAGet data JSON */
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
                <button type="button" onClick={handleSelectAll} className="btn btn-info">Select all</button>
                <button type="button" onClick={handleSelectOne} className="btn btn-info">Select {firstColumnTitle} only</button>
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
const getColumnFields = (columns, sorted) => {
    const columnPaths = Object.keys(columns);
    if (sorted) {
        columnPaths.sort((aKey, bKey) => {
            const aTitle = columns[aKey].toLowerCase();
            const bTitle = columns[bKey].toLowerCase();
            return (aTitle < bTitle ? -1 : (bTitle < aTitle ? 1 : 0));
        });
    }
    return columnPaths;
};


/**
 * Get any fields not in the schema for the displayed type, typically calculated fields.
 * @param {object} allColumns Fields mapping to titles
 * @param {array} visibleFields Fields included in the report query string
 *
 * @return {array} sorted array of fields not included in the schema
 */
const getExtraFields = (allColumns, visibleFields) => {
    const schemaFields = Object.keys(allColumns);
    const extraFields = visibleFields.filter((visibleField) => !schemaFields.includes(visibleField));
    if (extraFields.length > 0) {
        return _.sortBy(extraFields);
    }
    return [];
};


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
            <label htmlFor={field}>{title || field}</label>
        </div>
    );
};

ColumnItem.propTypes = {
    /** encoded field name for the column */
    field: PropTypes.string.isRequired,
    /** Title for the checkbox; same as column header title */
    title: PropTypes.string,
    /** True for selected columns; i.e. checked checkboxes */
    selected: PropTypes.bool.isRequired,
    /** Parent function to call when item is clicked */
    toggleColumn: PropTypes.func.isRequired,
};

ColumnItem.defaultProps = {
    title: null,
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
    const extraFields = getExtraFields(allColumns, visibleFields);

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
            updatedColumns = selectedFields.filter((field) => field !== clickedField);
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
                    {columnFields.map((field) => <ColumnItem key={field} field={field} title={allColumns[field]} selected={selectedFields.includes(field)} toggleColumn={toggleColumn} />)}
                </div>
                <div className="column-selector__selectors column-selector__selectors--extra">
                    {extraFields.map((field) => <ColumnItem key={field} field={field} selected={selectedFields.includes(field)} toggleColumn={toggleColumn} />)}
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
 * RNA-Seq Matrix search
 *
 *  Important to extend TextFilter because this class has functionality it lacks like
 *  knowing when to clear text book via Pubsub subscription
 *
 * @class RNASeqMatrixSearch
 * @extends {TextFilter}
 */
class RNASeqMatrixSearch extends TextFilter {
    constructor(props) {
        super();

        this.onUnitsChange = this.onUnitsChange.bind(this);
        this.onKeyDown = this.onKeyDown.bind(this);
        this.handleInputChange = this.handleInputChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.handleAutocompleteClick = this.handleAutocompleteClick.bind(this);
        this.lastGene = this.lastGene.bind(this);

        this.state = {
            unitsOption: props.query.getKeyValuesIfPresent('units').join(','),
            genes: props.query.getKeyValuesIfPresent('genes').join(','),
            showAutoSuggest: false,
        };
    }

    onUnitsChange(e) {
        this.setState({ unitsOption: e.target.value });
    }

    lastGene() {
        const inputNode = this.geneInput;

        if (!inputNode) {
            return '';
        }

        const geneTerms = inputNode.value.split(',');
        return (geneTerms[geneTerms.length - 1].trim());
    }

    handleInputChange() {
        this.setState({ showAutoSuggest: (this.lastGene() !== ''), genes: this.geneInput.value });
    }

    onKeyDown() {
        this.setState({ showAutoSuggest: (this.lastGene() !== '') });
    }

    handleSubmit(e) {
        e.preventDefault();
        window.location.href = `/rnaget?genes=${this.state.genes}&units=${this.state.unitsOption}`;
    }

    handleAutocompleteClick(term) {
        const inputNode = this.geneInput;

        let geneTerms = inputNode.value.split(',');
        geneTerms[geneTerms.length - 1] = term;

        geneTerms = geneTerms.map((gene) => gene.trim()).join(', ');

        this.setState({ showAutoSuggest: false, genes: geneTerms });
        inputNode.focus();
    }

    render() {
        return (
            <form onSubmit={this.handleSubmit} autoComplete="off">
                <div className="rna_seq_matrix">
                    {this.state.showAutoSuggest ?
                        <FetchedData loadingComplete>
                            <Param name="suggestions" url={`/rnaget-autocomplete?q=${this.lastGene()}`} type="json" />
                            <AutocompleteBox handleClick={this.handleAutocompleteClick} />
                        </FetchedData>
                    : null}
                    <input
                        type="search"
                        id="geneInput"
                        className="search-query"
                        placeholder="Enter Gene IDs..."
                        value={this.state.genes}
                        onKeyDown={this.onKeyDown}
                        onChange={this.handleInputChange}
                        ref={(input) => { this.geneInput = input; }}
                    />
                    <select name="searchOption" onChange={this.onUnitsChange} value={this.state.unitsOption}>
                        <option value="tpm">TPM</option>
                        <option value="fpkm">FPKM</option>
                    </select>
                    <button type="submit">Search</button>
                </div>
            </form>
        );
    }
}


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
const RNAGet = ({ context }, reactContext) => {
    /** All possible columns for the current type */
    const [allColumns] = React.useState(null);
    /** True if column selector modal visible */
    const [selectorOpen, setSelectorOpen] = React.useState(false);
    /** True if we have requested a redirect; prevents state changes from multiple redirects */
    const redirectInProgress = React.useRef(false);
    /** Table DOM element to handle its sticky header */
    const tableRef = React.useRef(null);

    // Calculate values from the search results and query string useable by the rest of the
    // component. The back end report code allows exactly one "type=x" parameter.
    const parsedUrl = React.useMemo(() => url.parse(context['@id']), [context]);
    const query = React.useMemo(() => new QueryString(parsedUrl.query), [parsedUrl]);
    const fieldOrder = React.useMemo(() => (allColumns ? Object.keys(allColumns) : Object.keys(context.columns)), [allColumns, context.columns]);
    const typeFilter = context.filters.find((filter) => filter.field === 'type');
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

    const pageLimit = DEFAULT_PAGE_LIMIT;

    // Calculate the current page number and total number of pages. The current page number relies
    // on the current "from=x" query string parameter, which the back end allows exactly zero or
    // one of.
    const pageIndices = query.getKeyValues('page');
    const currentPage = pageIndices.length === 1 ? Number(pageIndices[0]) : 1;

    const viewableTotal = Math.min(context.total, MAX_VIEWABLE_RESULTS - pageLimit);
    const totalPages = Math.trunc(viewableTotal / pageLimit) + (viewableTotal % pageLimit > 0 ? 1 : 0);

    // Called when the user closes the column-selector modal.
    const closeColumnSelector = () => {
        setSelectorOpen(false);
    };

    // Called when the user selects a new set of visible columns. Generate a new set of "field="
    // queries based on the newly selected visible columns and navigate to the new query.
    const handleColumnSelection = React.useCallback((selectedColumns) => {
        const sortedColumns = _(selectedColumns).sortBy((field) => fieldOrder.indexOf(field));

        // Convert the newly selected columns to a "field=x&field=y..." query.
        const fieldQuery = sortedColumns.map((field) => `field=${encodedURIComponent(field)}`).join('&');

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
        const indexQuery = query.clone();
        indexQuery.replaceKeyValue('page', newPageNumber);

        const href = `?${indexQuery.format()}`;
        reactContext.navigate(href);
    };

    React.useEffect(() => {
        // If a facet selection leaves fewer pages than the current page, redirect to the same url
        // but on the first page, by removing the "page=x" query-string parameter.
        if (currentPage > totalPages && !redirectInProgress.current) {
            redirectInProgress.current = true;
            const noPageQuery = query.clone();
            noPageQuery.deleteKeyValue('page');
            reactContext.navigate(`?${noPageQuery.format()}`);
        }
    }, [currentPage, totalPages, query, reactContext]);

    // No filled facets means no results, and we should display the notification from the back end
    // instead of the report.
    const facetdisplay = context.facets && context.facets.some((facet) => facet.total > 0);
    if (facetdisplay) {
        return (
            <div className="search-results">
                <div className="title-facets">
                    <h1>RNA Get (beta)</h1>
                    <RNASeqMatrixSearch query={query} />
                    <FacetList context={context} facets={context.facets} filters={context.filters} docTypeTitleSuffix="report" />
                </div>
                <div className="search-results__report-list">
                    <div className="results-table-control__pager">
                        {totalPages > 1 ?
                            <Pager.Multi currentPage={currentPage} total={totalPages} clickHandler={handlePagerClick} />
                        : null}
                    </div>
                    {viewableTotal < context.total ?
                        <div className="report-max-warning">Not all items viewable. Download TSV for all items.</div>
                    : null}
                    <TableItemCount count={`Showing results ${(currentPage - 1) * pageLimit + 1} to ${Math.min(context.total, (currentPage - 1) * pageLimit + pageLimit)} of ${context.total} for ${context.selected_genes}`} />
                    <div className="report__table">
                        <table className="table table-striped" ref={tableRef}>
                            <RNAGetHeader context={context} visibleFields={visibleFields} allColumns={allColumns} tableRef={tableRef} />
                            <RNAGetData context={context} visibleFields={visibleFields} type={type} />
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

RNAGet.propTypes = {
    /** RNAGet search results */
    context: PropTypes.object.isRequired,
};

RNAGet.contextTypes = {
    navigate: PropTypes.func,
};

globals.contentViews.register(RNAGet, 'rnaseq');
