import React from 'react';
import PropTypes from 'prop-types';
import dayjs from 'dayjs';
import _ from 'underscore';
import url from 'url';
import QueryString from '../../libs/query_string';
import FacetRegistry from './registry';


/**
 * All the default facet rendering components reside in this file, including ones that aren't
 * technically default in that they don't get registered as a default component, but other custom
 * components can use them. Default facet components get exported so that custom components that
 * simply alter the appearance of default components can call the default components.
 */


// Sanitize user input and facet terms for comparison: convert to lowercase, remove white space and asterisks (which cause regular expression error)
const sanitizedString = inputString => inputString.toLowerCase()
    .replace(/ /g, '') // remove spaces (to allow multiple word searches)
    .replace(/[*?()+[\]\\/]/g, ''); // remove certain special characters (these cause console errors)


/**
 * Render a tri-state boolean facet with "true," "false," and "either." This doesn't get registered
 * as a default facet component, but is provided so we have one component to render all boolean
 * facets consistently. For future expansion, note that all properties available to facet-rendering
 * components are available, but this particular implementation only uses a subset of them.
 */
export const DefaultBooleanFacet = ({ facet, relevantFilters, queryString }, reactContext) => {
    // Based on the current filter for this facet, determine which radio button should appear
    // checked. We expect boolean query string parameters expect to have the values 0 or "false,"
    // or 1 or "true." Any other values found check the "either" button. Multiple query-string
    // parameters of this type check the "either" button.
    let currentOption = 'either';
    if (relevantFilters.length === 1) {
        if (relevantFilters[0].term === '1' || relevantFilters[0].term === 'true') {
            currentOption = 'true';
        } else if (relevantFilters[0].term === '0' || relevantFilters[0].term === 'false') {
            currentOption = 'false';
        }
    }

    // We have to build the new query string unless the user clicked the "either" radio button,
    // which uses the `remove` link from the relevant filter. This callback gets memoized to avoid
    // needlessly rerendering this component, and its dependencies should normally not change until
    // the user clicks a term.
    const handleRadioClick = React.useCallback((event) => {
        const { value } = event.target;
        let href;
        if (value === 'either') {
            // If the user can check the "either" button then we know the query string has only one
            // of these "exists" elements, so just get the first relevant filter's `remove`
            // property.
            href = url.parse(relevantFilters[0].remove).search || relevantFilters[0].remove;
        } else {
            // User clicked the "true" or "false" radio buttons. Replace any existing relevant query
            // element with one corresponding to the clicked radio button.
            const clickedElementName = event.target.getAttribute('name');
            const query = new QueryString(queryString);
            query.replaceKeyValue(clickedElementName, value);
            href = `?${query.format()}`;
        }
        reactContext.navigate(href);
    }, [relevantFilters, queryString, reactContext]);

    return (
        <fieldset className="facet">
            <legend>{facet.title}</legend>
            <div className="facet__content--exists">
                {facet.terms.map(term => (
                    <div key={term.key_as_string} className="facet__radio">
                        <input type="radio" name={facet.field} value={term.key_as_string} id={term.key_as_string} checked={currentOption === term.key_as_string} onChange={handleRadioClick} />
                        <label htmlFor={term.key}>
                            <div className="facet__radio-label">{term.key_as_string}</div>
                            <div className="facet__radio-count">{term.doc_count}</div>
                        </label>
                    </div>
                ))}
                <div className="facet__radio">
                    <input type="radio" name={facet.field} value="either" id={`${facet.field}-either`} checked={currentOption === 'either'} onChange={handleRadioClick} />
                    <label htmlFor={`${facet.field}-either`}>
                        <div className="facet__radio-label">either</div>
                        <div className="facet__radio-count">{facet.total}</div>
                    </label>
                </div>
            </div>
        </fieldset>
    );
};

DefaultBooleanFacet.propTypes = {
    /** Relevant `facet` object from `facets` array in `results` */
    facet: PropTypes.object.isRequired,
    /** Filters relevant to the current facet */
    relevantFilters: PropTypes.array.isRequired,
    /** Query-string portion of current URL without initial ? */
    queryString: PropTypes.string,
};

DefaultBooleanFacet.defaultProps = {
    queryString: '',
};

DefaultBooleanFacet.contextTypes = {
    navigate: PropTypes.func,
};


/**
 * Render a tri-state boolean facet for the "exists" facets. This doesn't get registered as a
 * default facet component, but is provided so we have one component to render all "exists" facets
 * consistently. For future expansion, note that all properties available to facet-rendering
 * components are available, but this particular implementation only uses a subset of them.
 */
export const DefaultExistsFacet = ({ facet, relevantFilters, queryString }, reactContext) => {
    // Based on the current filter for this "exists" facet, determine which radio button should
    // appear checked. Note that if the user put some non "*" value for this "exists" query string
    // element, then we check the "either" radio button because a non-"*" value has no defined
    // meaning, nor does having more than one "exists" term in the query string.
    let currentOption = 'either';
    if (relevantFilters.length === 1 && relevantFilters[0].term === '*') {
        if (facet.field === relevantFilters[0].field) {
            currentOption = 'yes';
        } else if (relevantFilters[0].field === `${facet.field}!`) {
            currentOption = 'no';
        }
    }

    // Sort yes/no facet terms into yes - no order.
    const sortedTerms = _(facet.terms.filter(term => term.doc_count > 0)).sortBy(term => ['yes', 'no'].indexOf(term.key));

    // We have to build the new query string unless the user clicked the "either" radio button,
    // which uses the `remove` link from the relevant filter. This callback gets memoized to avoid
    // needlessly rerendering this component, and its dependencies should normally not change until
    // the user clicks a term.
    const handleRadioClick = React.useCallback((event) => {
        const { value } = event.target;
        let href;
        if (value === 'either') {
            // If the user can check the "either" button then we know the query string has only one
            // of these "exists" elements, so just get the first relevant filter's `remove`
            // property.
            href = url.parse(relevantFilters[0].remove).search || relevantFilters[0].remove;
        } else {
            // User clicked the "yes" or "no" radio buttons. Replace any existing relevant query
            // element with one corresponding to the clicked radio button.
            const query = new QueryString(queryString);
            query.replaceKeyValue(facet.field, '*', value === 'no');
            href = `?${query.format()}`;
        }
        reactContext.navigate(href);
    }, [facet.field, queryString, reactContext, relevantFilters]);

    const query = new QueryString(queryString);
    const isFieldPartOfSearchQuery = !!query.getKeyValuesIfPresent(facet.field)[0];

    // this field show display if it is part of the search query even if there are no results. Otherwise hide
    return (
        facet.total > 0 || isFieldPartOfSearchQuery ?
            <fieldset className="facet">
                <legend>{facet.title}</legend>
                <div className="facet__content--exists">
                    {sortedTerms.map(term => (
                        <div key={term.key} className="facet__radio">
                            <input type="radio" name={facet.field} value={term.key} id={term.key} checked={currentOption === term.key} onChange={handleRadioClick} />
                            <label htmlFor={term.key}>
                                <div className="facet__radio-label">{term.key}</div>
                                <div className="facet__radio-count">{term.doc_count}</div>
                            </label>
                        </div>
                    ))}
                    <div className="facet__radio">
                        <input type="radio" name={facet.field} value="either" id={`${facet.field}-either`} checked={currentOption === 'either'} onChange={handleRadioClick} />
                        <label htmlFor={`${facet.field}-either`}>
                            <div className="facet__radio-label">either</div>
                            <div className="facet__radio-count">{facet.total}</div>
                        </label>
                    </div>
                </div>
            </fieldset>
        : null
    );
};

DefaultExistsFacet.propTypes = {
    /** Relevant `facet` object from `facets` array in `results` */
    facet: PropTypes.object.isRequired,
    /** Filters relevant to the current facet */
    relevantFilters: PropTypes.array.isRequired,
    /** Query-string portion of current URL without initial ? */
    queryString: PropTypes.string,
};

DefaultExistsFacet.defaultProps = {
    queryString: '',
};

DefaultExistsFacet.contextTypes = {
    navigate: PropTypes.func,
};


const allMonths = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'];

export class DefaultDateSelectorFacet extends React.Component {
    constructor() {
        super();

        // Set initial React component state.
        this.state = {
            possibleYears: [], // all years with results
            startYears: [], // possible years for the start year drop-down
            endYears: [], // possible years for the end year drop-down
            startMonths: [], // possible months for the start month drop-down
            endMonths: [], // possible months for the end month drop-down
            startYear: undefined, // chosen start year
            startMonth: undefined, // chosen start month
            endYear: undefined, // chosen end year
            endMonth: undefined, // chosen end month
            activeFacet: '', // for toggle, either 'date_released' or 'date_submitted'
        };

        this.selectYear = this.selectYear.bind(this);
        this.selectMonth = this.selectMonth.bind(this);
        this.checkForSameYear = this.checkForSameYear.bind(this);
        this.toggleDateFacet = this.toggleDateFacet.bind(this);
        this.setActiveFacetParameters = this.setActiveFacetParameters.bind(this);
        this.handleReset = this.handleReset.bind(this);
        this.resetMonthDropDowns = this.resetMonthDropDowns.bind(this);
    }

    componentDidMount() {
        this.setState({ activeFacet: this.props.facet.field }, () => {
            this.setActiveFacetParameters(true);
        });
    }

    setActiveFacetParameters(initializationFlag) {
        let activeFacet = null;
        let activeFilter = null;
        let startYear = null;
        let endYear = null;
        // If there is a date filter applied, we'll use that filter to set state when the component is mounted
        if (initializationFlag) {
            // if a date range has already been selected, we will use that date range to populate drop-downs
            const existingFilter = this.props.results.filters.filter(filter => (filter.field === 'advancedQuery' && filter.term.includes('date')));
            if (existingFilter[0]) {
                activeFilter = true;
                const filterString = existingFilter[0].term;
                activeFacet = (filterString.indexOf('date_released') !== -1) ? 'date_released' : 'date_submitted';
                startYear = filterString.split('[')[1].split('-')[0];
                const startMonth = filterString.split('[')[1].split('-')[1];
                endYear = filterString.split('TO ')[1].split('-')[0];
                const endMonth = filterString.split('TO ')[1].split('-')[1];
                // Set dropdown lists to match existing query
                this.setState({
                    activeFacet,
                    startYear,
                    endYear,
                    startMonth,
                    endMonth,
                });
            }
        }
        if (activeFacet === null) {
            activeFacet = this.state.activeFacet;
        }

        // Set possible years to be 2009 -> current year for 'date_released'
        // Set possible years to be 2008 -> current year for 'date_submitted'
        const currentYear = dayjs().format('YYYY');
        let firstYear = 2007;
        if (activeFacet === 'date_released') {
            firstYear = 2008;
        }
        const numberOfYears = +currentYear - firstYear;
        const possibleYears = Array.from({ length: numberOfYears }, (e, i) => (i + firstYear + 1));

        if (!initializationFlag || !activeFilter) {
            // Set dropdown lists to be full lists of possiblities and initialize to boundaries of full range
            this.setState({
                startYear: possibleYears[0],
                endYear: possibleYears[possibleYears.length - 1],
                startMonth: '01',
                endMonth: '12',
                startYears: possibleYears,
                endYears: possibleYears,
            });
        } else {
            const startYears = possibleYears.filter(year => +year <= endYear);
            const endYears = possibleYears.filter(year => +year >= startYear);
            this.setState({
                startYears,
                endYears,
            });
        }

        // Set dropdown options to include all possibilities
        this.setState({
            possibleYears,
            startMonths: allMonths,
            endMonths: allMonths,
        }, () => this.checkForSameYear());
    }

    selectYear(event) {
        // We are changing the start year, which means we need to change the possibilities for the end years and also the possible start months
        if (event.target.id === 'select-start-year') {
            // Set startYear to be user choice
            this.setState({ startYear: event.target.value }, () => {
                // Check if now the years match and month lists need to be limited
                this.checkForSameYear();
            });
            // Possibilities for endYears must now all be greater than the new startYear
            const endYears = this.state.possibleYears.filter(year => +year >= event.target.value);
            this.setState({ endYears });
        // We are changing the end year, which means we need to change the possiblities for the starting year and also the possible end months
        } else {
            // Set endYear to be user choice
            this.setState({ endYear: event.target.value }, () => {
                // Check if now the years match and month lists need to be limited
                this.checkForSameYear();
            });
            // Possiblities for startYears must now all be less than the new endYears
            const startYears = this.state.possibleYears.filter(year => +year <= event.target.value);
            this.setState({ startYears });
        }
    }

    resetMonthDropDowns() {
        this.setState({
            startMonths: allMonths,
            startMonth: '01',
            endMonths: allMonths,
            endMonth: '12',
        });
    }

    // If the start year and the end year match, we have to be careful to not allow the user to pick an end month that is earlier than the start month
    checkForSameYear() {
        if (+this.state.startYear === +this.state.endYear) {
            // If start month is later than the end month and years match, this is not allowed, so we reset
            if (+this.state.endMonth < +this.state.startMonth) {
                this.resetMonthDropDowns();
            // If start and end months are allowed, we still need to filter dropdown possible lists so they can't select an unallowed combination
            } else {
                // endMonths can only display months that are after the chosen startMonth
                const endMonths = allMonths.filter(month => +month >= +this.state.startMonth);
                // startMonths can only display months that are before the chosen endMonth
                const startMonths = allMonths.filter(month => +month <= +this.state.endMonth);
                this.setState({
                    endMonths,
                    startMonths,
                });
            }
        // If the start and end years previously matched (but now they don't), an incomplete list of months may be set and we need to update
        } else {
            if (allMonths.length !== this.state.startMonths.length) {
                this.setState({ startMonths: allMonths });
            }
            if (allMonths.length !== this.state.endMonths.length) {
                this.setState({ endMonths: allMonths });
            }
        }
    }

    selectMonth(event) {
        // When a month changes, we need to check if the years match and filter the month dropdown possibilities if they do
        if (event.target.id === 'select-start-month') {
            this.setState({ startMonth: event.target.value }, () => {
                this.checkForSameYear();
            });
        } else {
            this.setState({ endMonth: event.target.value }, () => {
                this.checkForSameYear();
            });
        }
    }

    // Toggle the 'activeFacet' state and also reset the drop down options by calling 'setActiveFacetParameters'
    toggleDateFacet() {
        this.setState(prevState => ({ activeFacet: prevState.activeFacet === 'date_released' ? 'date_submitted' : 'date_released' }), this.setActiveFacetParameters);
    }

    // Reset the dropdowns and state, and clear query
    handleReset(resetString) {
        this.setState({ activeFacet: 'date_released' }, () => {
            this.setActiveFacetParameters();

            // * Strip trailing & for the ENCD-4803 branch because it keeps the training ampersand.
            let processedResetString = resetString;
            if (resetString[resetString.length - 1] === '&') {
                processedResetString = resetString.substring(0, resetString.length - 1);
            }

            this.context.navigate(processedResetString);
        });
    }

    // Set dropdowns to match quick link query and nagivate to quick link
    handleQuickLink(searchBaseForDateRange, field) {
        const currentYear = dayjs().format('YYYY');
        const currentMonth = dayjs().format('MM');
        const currentDay = dayjs().format('DD');
        const quickLinkString = `${searchBaseForDateRange}advancedQuery=${field}:[${currentYear - 1}-${currentMonth}-${currentDay} TO ${currentYear}-${currentMonth}-${currentDay}]`;
        this.setState({
            startMonth: currentMonth,
            endMonth: currentMonth,
            startYear: (currentYear - 1),
            endYear: currentYear,
            startMonths: allMonths,
            endMonths: allMonths,
            startYears: this.state.possibleYears.filter(year => +year <= currentYear),
            endYears: this.state.possibleYears.filter(year => +year >= (currentYear - 1)),
        }, () => {
            this.context.navigate(quickLinkString);
        });
    }

    render() {
        const { facet, results, queryString } = this.props;
        const searchBase = `?${queryString}&`;
        const field = this.state.activeFacet;
        const activeFacet = results.facets.filter(f => f.field === this.state.activeFacet)[0];
        let disableDateReleased = false;
        let disableDateSubmitted = false;
        // filterFlag is true to indicate that we need to display filters
        let filterFlag = false;
        // missingField indicates which field to disable (date_released or date_submitted) if one field is not disabled
        let missingField = null;

        // Check which of date released and date submitted might be disabled, either for lack of data or because of !=* filter
        if ((queryString.indexOf('date_released!=*') > -1) || !(results.facets.filter(f => f.field === 'date_released').length > 0)) {
            disableDateReleased = true;
            missingField = 'date_released';
        }
        if ((queryString.indexOf('date_submitted!=*') > -1) || !(results.facets.filter(f => f.field === 'date_submitted').length > 0)) {
            disableDateSubmitted = true;
            missingField = 'date_submitted';
        }

        // If date released and/or date submitted has a !=* filter, determine link(s) to delete the filter(s)
        let deleteSubmittedFilter = '';
        let deleteReleasedFilter = '';
        let missingFilter = '';
        let searchBaseCopy = searchBase;
        if (queryString.indexOf('date_submitted!=*') > -1) {
            filterFlag = true;
            missingFilter = 'date_submitted';
            const parsedUrl = url.parse(searchBaseCopy);
            const query = new QueryString(parsedUrl.query);
            query.deleteKeyValue('date_submitted');
            deleteSubmittedFilter = `?${query.format()}`;
            searchBaseCopy = deleteSubmittedFilter;
        }
        if (queryString.indexOf('date_released!=*') > -1) {
            filterFlag = true;
            missingFilter = 'date_released';
            const parsedUrl = url.parse(searchBaseCopy);
            const query = new QueryString(parsedUrl.query);
            query.deleteKeyValue('date_released');
            deleteReleasedFilter = `?${query.format()}`;
        }

        // If both date released and date submitted are disabled and at least one is disabled by a !=* filter, display the filter(s) only
        if (disableDateReleased && disableDateSubmitted && (facet.field === missingFilter) && filterFlag) {
            return (
                <div className="facet date-selector-facet">
                    <h5>Date range selection</h5>
                    <div className="filter-container">
                        {deleteReleasedFilter ?
                            <React.Fragment>
                                <div className="filter-hed">Selected filter for date released:</div>
                                <a href={deleteReleasedFilter} className="negation-filter">
                                    <div className="filter-link"><i className="icon icon-times-circle" /> *</div>
                                </a>
                            </React.Fragment>
                        : null}
                        {deleteSubmittedFilter ?
                            <React.Fragment>
                                <div className="filter-hed">Selected filter for date submitted:</div>
                                <a href={deleteSubmittedFilter} className="negation-filter">
                                    <div className="filter-link"><i className="icon icon-times-circle" /> *</div>
                                </a>
                            </React.Fragment>
                        : null}
                    </div>
                </div>
            );
        // If both date released and date submitted are disabled but there are no filters (both have no data), display no facet
        } else if (disableDateReleased && disableDateSubmitted && !filterFlag) {
            return null;
        }

        // If we are not disabling either date released nor date submitted, only display the facet for date released
        if (!disableDateReleased && !disableDateSubmitted && facet.field === 'date_submitted') {
            return null;
        }
        // If one of date_released and date_submitted is disabled, only display the facet for the one that is not disabled
        if ((disableDateReleased && facet.field === 'date_released') || (disableDateSubmitted && facet.field === 'date_submitted')) {
            return null;
        }

        const daysInEndMonth = dayjs(`${this.state.endYear}-${this.state.endMonth}`, 'YYYY-MM').daysInMonth();

        // if a date range has already been selected, we want to over-write that date range with a new one
        const existingFilter = this.props.results.filters.filter(filter => (filter.field === 'advancedQuery' && filter.term.includes('date')));
        let resetString = '';
        let searchBaseForDateRange = searchBase;
        if (existingFilter.length > 0) {
            resetString = `${existingFilter[0].remove}&`;
            searchBaseForDateRange = `${existingFilter[0].remove}&`;
        } else {
            resetString = searchBase;
        }

        const searchString = `${searchBaseForDateRange}advancedQuery=${this.state.activeFacet}:[${this.state.startYear}-${this.state.startMonth}-01 TO ${this.state.endYear}-${this.state.endMonth}-${daysInEndMonth}]`;

        // Print selected date range next to date selector facet
        let dateRangeString = '';
        if (existingFilter.length > 0) {
            if (existingFilter[0].term.indexOf('date_released') > -1) {
                dateRangeString = `Data released between ${existingFilter[0].term.substring(existingFilter[0].term.indexOf('[') + 1, existingFilter[0].term.indexOf(']')).replace('TO', 'and')}`;
            } else {
                dateRangeString = `Data submitted between ${existingFilter[0].term.substring(existingFilter[0].term.indexOf('[') + 1, existingFilter[0].term.indexOf(']')).replace('TO', 'and')}`;
            }
        }

        if ((activeFacet && (activeFacet.terms.length > 0) && activeFacet.terms.some(term => term.doc_count)) || (field.charAt(field.length - 1) === '!')) {
            return (
                <div className={`facet date-selector-facet ${facet.field === 'date_released' ? 'display-date-selector' : ''}`}>
                    <h5>Date range selection</h5>
                    {(queryString.indexOf('date_released!=*') > -1) ?
                        <div className="filter-container">
                            <div className="filter-hed">Selected filter for date released:</div>
                            <a href={deleteReleasedFilter} className="negation-filter">
                                <div className="filter-link"><i className="icon icon-times-circle" /> *</div>
                            </a>
                        </div>
                    : null}
                    {(queryString.indexOf('date_submitted!=*') > -1) ?
                        <div className="filter-container">
                            <div className="filter-hed">Selected filter for date submitted:</div>
                            <a href={deleteSubmittedFilter} className="negation-filter">
                                <div className="filter-link"><i className="icon icon-times-circle" /> *</div>
                            </a>
                        </div>
                    : null}
                    {existingFilter.length > 0 ?
                        <div className="selected-date-range">
                            <div>Selected range: </div>
                            {existingFilter.map(filter =>
                                <div key={filter.term}>{dateRangeString}</div>
                            )}
                        </div>
                    : null}

                    <div className="date-selector-toggle-wrapper">
                        <div className="date-selector-toggle">
                            <input
                                type="radio"
                                name="released"
                                value="released"
                                id="released-radio-button"
                                checked={this.state.activeFacet === 'date_released'}
                                onChange={this.toggleDateFacet}
                                disabled={missingField === 'date_released'}
                            />
                            <label htmlFor="released-radio-button" id="released-radio-button-label">Released</label>
                        </div>
                        <div className="date-selector-toggle">
                            <input
                                type="radio"
                                name="submitted"
                                value="submitted"
                                id="submitted-radio-button"
                                checked={this.state.activeFacet === 'date_submitted'}
                                onChange={this.toggleDateFacet}
                                disabled={missingField === 'date_submitted'}
                            />
                            <label htmlFor="submitted-radio-button" id="submitted-radio-button-label">Submitted</label>
                        </div>
                    </div>
                    <button className="date-selector-btn" onClick={() => this.handleQuickLink(searchBaseForDateRange, field)}>
                        <i className="icon icon-caret-right" />
                        See results for the past year
                    </button>
                    <div className="date-container">
                        <div className="date-selector-module">
                            <h6>Start date:</h6>
                            <div className="date-selector">
                                <select id="select-start-month" value={this.state.startMonth} onChange={this.selectMonth}>
                                    {this.state.startMonths.map(month =>
                                        <option value={month} key={month}>{month}</option>
                                    )}
                                </select>
                                <select id="select-start-year" value={this.state.startYear} onChange={this.selectYear}>
                                    {this.state.startYears.map(year =>
                                        <option value={year} key={year}>{year}</option>
                                    )}
                                </select>
                            </div>
                        </div>
                        <div className="date-arrow">
                            <i className="icon icon-arrow-right" />
                        </div>
                        <div className="date-selector-module">
                            <h6>End date:</h6>
                            <div className="date-selector">
                                <select id="select-end-month" value={this.state.endMonth} onChange={this.selectMonth}>
                                    {this.state.endMonths.map(month =>
                                        <option value={month} key={month}>{month}</option>
                                    )}
                                </select>
                                <select id="select-end-year" value={this.state.endYear} onChange={this.selectYear}>
                                    {this.state.endYears.map(year =>
                                        <option value={year} key={year}>{year}</option>
                                    )}
                                </select>
                            </div>
                        </div>
                    </div>
                    <div className="date-selector-facet__controls">
                        <a className="btn btn-info btn-sm apply-date-selector" href={searchString}>Apply changes</a>
                        <button className="btn btn-info btn-sm reset-date-selector" onClick={() => this.handleReset(resetString)}>
                            Reset
                        </button>
                    </div>
                </div>
            );
        }

        // Facet had all zero terms and was not a "not" facet.
        return null;
    }
}

DefaultDateSelectorFacet.propTypes = {
    /** Relevant `facet` object in `facets` array in `results` */
    facet: PropTypes.object.isRequired,
    /** Complete search-results object */
    results: PropTypes.object.isRequired,
    /** Query-string portion of current URL without initial ? */
    queryString: PropTypes.string.isRequired,
};

DefaultDateSelectorFacet.contextTypes = {
    navigate: PropTypes.func,
};


/**
 * Default component to render the title of a facet.
 */
export const DefaultTitle = ({ facet }) => (
    <h5>{facet.title}</h5>
);

DefaultTitle.propTypes = {
    /** results.facets object for the facet whose title we're rendering */
    facet: PropTypes.object.isRequired,
};


/**
 * Default component to render the name of a term within the default term component.
 */
export const DefaultTermName = ({ term }) => (
    <span>{term.key}</span>
);

DefaultTermName.propTypes = {
    /** facet.terms object for the term we're rendering */
    term: PropTypes.object.isRequired,
};


/**
 * Default component to render the name of a selected term from the search result filters. Used for
 * the "Selected filters" links, and the term gets rendered inside an <a>.
 */
export const DefaultSelectedTermName = ({ filter }) => (
    <span>{filter.term}</span>
);

DefaultSelectedTermName.propTypes = {
    /** facet.filters object for the selected term we're rendering */
    filter: PropTypes.object.isRequired,
};


/**
 * Default component to render a single term within the default facet.
 */
export const DefaultTerm = ({ term, facet, results, mode, relevantFilters, pathname, queryString, onFilter, allowNegation }) => {
    const TermNameComponent = FacetRegistry.TermName.lookup(facet.field);
    let href;
    let negHref;
    let negated = false;

    // Find the search-results filter matching this term, which if found indicates this term is
    // selected; also check if the selection is for negation. Boolean terms have a
    // term.key_as_string "true" and "false" values, preferable to the "1" and "0" values in
    // term.key.
    const selectedTermFilter = relevantFilters.find((filter) => {
        let filterField = filter.field;
        const negatedFilter = filterField.slice(-1) === '!';
        if (negatedFilter) {
            filterField = filterField.slice(0, -1);
        }
        const selected = filterField === facet.field && (filter.term === term.key_as_string || filter.term === term.key.toString());
        if (selected) {
            negated = negatedFilter;
        }
        return selected;
    });

    // Build the term href as well as its negation href, or the `remove` link for selected terms.
    if (selectedTermFilter) {
        // Term is selected, so its link URI is the `remove` property of the matching filter.
        // Process this URI to remove the "/search/" path.
        href = url.parse(selectedTermFilter.remove).search || selectedTermFilter.remove;
    } else {
        // Term isn't selected, so build the link URI by adding this term to the existing URL.
        const query = new QueryString(queryString);
        const negQuery = query.clone();
        const key = term.key_as_string || term.key;
        query.addKeyValue(facet.field, key);
        href = `?${query.format()}`;

        // Also build the negation URI.
        negQuery.addKeyValue(facet.field, key, true);
        negHref = `?${negQuery.format()}`;
    }

    // Build the CSS class for selected terms.
    let termCss = '';
    if (selectedTermFilter) {
        termCss = ` facet-term__item--${negated ? 'negated' : 'selected'}`;
    }

    // Calculate the width of the term bar graph.
    const barStyle = {
        width: `${Math.ceil((term.doc_count / facet.total) * 100)}%`,
    };

    return (
        <li className="facet-term">
            <a href={href} onClick={mode === 'picker' ? onFilter : null} className={`facet-term__item${termCss}`}>
                <div className="facet-term__text">
                    <TermNameComponent
                        termName={term.key}
                        selected={!!selectedTermFilter}
                        term={term}
                        facet={facet}
                        results={results}
                        mode={mode}
                        pathname={pathname}
                        queryString={queryString}
                    />
                </div>
                {negated ? null : <div className="facet-term__count">{term.doc_count}</div>}
                {(selectedTermFilter || negated) ? null : <div className="facet-term__bar" style={barStyle} />}
            </a>
            <div className="facet-term__negator">
                {allowNegation ?
                    <React.Fragment>
                        {selectedTermFilter ? null : <a href={negHref} title={'Do not include items with this term'}><i className="icon icon-minus-circle" /></a>}
                    </React.Fragment>
                : null}
            </div>
        </li>
    );
};

DefaultTerm.propTypes = {
    /** facet.terms object for the term we're rendering */
    term: PropTypes.object.isRequired,
    /** results.facets object for the facet whose term we're rendering */
    facet: PropTypes.object.isRequired,
    /** Search results object */
    results: PropTypes.object.isRequired,
    /** Facet display mode */
    mode: PropTypes.string,
    /** Search-result filters relevant to the current facet */
    relevantFilters: PropTypes.array.isRequired,
    /** Search results path without query-string portion */
    pathname: PropTypes.string.isRequired,
    /** Query-string portion of current URL without initial ? */
    queryString: PropTypes.string,
    /** Special facet-term click handler for edit forms */
    onFilter: PropTypes.func,
    /** True to display negation control */
    allowNegation: PropTypes.bool,
};

DefaultTerm.defaultProps = {
    mode: '',
    queryString: '',
    onFilter: null,
    allowNegation: true,
};


/**
 * Display the optional typeahead search field. This component always displays this field so the
 * parent component needs to determine whether to display it or not.
 */
const Typeahead = ({ typeaheadTerm, facet, handleTypeAhead }) => (
    <div className="typeahead-entry" role="search">
        <i className="icon icon-search" />
        <div className="searchform">
            <input
                type="search"
                aria-label={`search to filter list of terms for facet ${facet.title}`}
                placeholder="Search"
                value={typeaheadTerm}
                onChange={handleTypeAhead}
                name={`search${facet.title.replace(/\s+/g, '')}`}
            />
        </div>
    </div>
);

Typeahead.propTypes = {
    /** Current entered search term */
    typeaheadTerm: PropTypes.string.isRequired,
    /** Current facet typeahead box applies to */
    facet: PropTypes.object.isRequired,
    /** Callback when user changes search text */
    handleTypeAhead: PropTypes.func.isRequired,
};


/**
 * Display links to clear the terms currently selected in the facet. Display nothing if no terms
 * have been selected.
 */
const SelectedFilters = ({ facet, selectedTerms }) => {
    const SelectedTermNameComponent = FacetRegistry.SelectedTermName.lookup(facet.field);
    return (
        <React.Fragment>
            {(selectedTerms.length > 0) ?
                <div className="filter-container">
                    <div className="filter-hed">Selected filters:</div>
                    {selectedTerms.map(filter =>
                        <a href={filter.remove} key={filter.term} className={(filter.field.indexOf('!') !== -1) ? 'negation-filter' : ''}>
                            <div className="filter-link"><i className="icon icon-times-circle" /> <SelectedTermNameComponent filter={filter} /></div>
                        </a>
                    )}
                </div>
            : null}
        </React.Fragment>
    );
};

SelectedFilters.propTypes = {
    /** Relevant `facet` object from `facets` array in `results` */
    facet: PropTypes.object.isRequired,
    /** Search-result filters relevant to the facet */
    selectedTerms: PropTypes.array.isRequired,
};


/**
 * Render the terms within a facet, calling the currently registered term-rendering component.
 * This component gets memoized so it only renders when the facet data unequivocally changes,
 * avoiding needless rerenders when a different facet needs to rerender.
 */
const FacetTerms = React.memo(({ facet, results, mode, relevantFilters, pathname, queryString, filteredTerms, onFilter, allowNegation }) => {
    const TermComponent = FacetRegistry.Term.lookup(facet.field);
    const facetTitle = facet.title.replace(/\s+/g, '');
    return (
        <div className={`facet__term-list search${facetTitle}`}>
            {filteredTerms.map(term => (
                <TermComponent
                    key={term.key}
                    term={term}
                    facet={facet}
                    results={results}
                    mode={mode}
                    relevantFilters={relevantFilters}
                    pathname={pathname}
                    queryString={queryString}
                    onFilter={onFilter}
                    allowNegation={allowNegation}
                />
            ))}
        </div>
    );
});

FacetTerms.propTypes = {
    /** Relevant `facet` object from `facets` array in `results` */
    facet: PropTypes.object.isRequired,
    /** Complete search-results object */
    results: PropTypes.object.isRequired,
    /** Facet display mode */
    mode: PropTypes.string,
    /** Filters relevant to the current facet */
    relevantFilters: PropTypes.array.isRequired,
    /** Search results path without query-string portion */
    pathname: PropTypes.string.isRequired,
    /** Query-string portion of current URL without initial ? */
    queryString: PropTypes.string,
    /** Array of terms to render */
    filteredTerms: PropTypes.array.isRequired,
    /** Special facet-term click handler for edit forms */
    onFilter: PropTypes.func,
    /** True to display negation control */
    allowNegation: PropTypes.bool,
};

FacetTerms.defaultProps = {
    mode: '',
    queryString: '',
    onFilter: null,
    allowNegation: true,
};


/**
 * Display the default text facet with optional typeahead field.
 */
export const DefaultFacet = ({ facet, results, mode, relevantFilters, pathname, queryString, onFilter, allowNegation, isExpanded, handleExpanderClick, handleKeyDown, isExpandable }) => {
    const [initialState, setInitialState] = React.useState(true);
    const [topShadingVisible, setTopShadingVisible] = React.useState(false);
    const [bottomShadingVisible, setBottomShadingVisible] = React.useState(false);
    const [typeaheadTerm, setTypeaheadTerm] = React.useState('');
    const scrollingElement = React.useRef(null);

    // Retrieve reference to the registered facet title component for this facet.
    const TitleComponent = FacetRegistry.Title.lookup(facet.field);

    // Filter out terms with a zero doc_count, as seen in region-search results.
    const significantTerms = !facet.appended ? facet.terms.filter(term => term.doc_count > 0) : facet.terms;

    // Sort numerical terms by value not by frequency
    // This should ultimately be accomplished in the back end, but the front end fix is much simpler so we are starting with that
    // We have to check the full list for now (until schema change) because some lists contain both numerical and string terms ('Encyclopedia version' under Annotations) and we do not want to sort those by value
    const numericalTest = a => !isNaN(a.key);
    // For straightforward numerical facets, just sort by value
    const processedTerms = significantTerms.every(numericalTest) ? _.sortBy(significantTerms, obj => obj.key) : significantTerms;

    const disabledCss = filters => filters.some(f => f.field.indexOf('!') !== -1 && f.term.trim() === '*');

    // Filter the list of facet terms to those allowed by the optional typeahead field. Memoize the
    // resulting list to avoid needlessly rerendering the facet-term list that can get very long.
    const filteredTerms = React.useMemo(() => {
        if (facet.type === 'typeahead') {
            const passingTerms = processedTerms.filter(
                (term) => {
                    if (term.doc_count > 0) {
                        const termKey = sanitizedString(term.key);
                        const typeaheadVal = String(sanitizedString(typeaheadTerm));
                        if (termKey.match(typeaheadVal)) {
                            return term;
                        }
                        return null;
                    }
                    return null;
                }
            );

            // Typeahead facets only render a truncated list of terms until initialState becomes
            // false, which happens when the component mounts.
            return initialState ? passingTerms.slice(0, 50) : passingTerms;
        }
        return processedTerms;
    }, [processedTerms, facet.type, typeaheadTerm, initialState]);

    // Called to set the top and bottom shading for scrollable facets based on where the user has
    // scrolled the facet as well as its height. This function needs memoization as new instances
    // of itself can cause needless rerendering of dependent components.
    const handleScrollShading = React.useCallback(() => {
        const element = scrollingElement.current;
        if (element.scrollTop === 0 && topShadingVisible) {
            // Top edge of the facet scrolled into view.
            setTopShadingVisible(false);
        } else if (element.scrollTop > 0 && !topShadingVisible) {
            // Top edge of the facet scrolls out of view.
            setTopShadingVisible(true);
        } else {
            const scrollDiff = Math.abs((element.scrollHeight - element.scrollTop) - element.clientHeight);
            if (scrollDiff === 0 && bottomShadingVisible) {
                // Bottom edge of the facet scrolled into view.
                setBottomShadingVisible(false);
            } else if (scrollDiff > 0 && !bottomShadingVisible) {
                // Bottom edge of thefgh facet scrolled out of view.
                setBottomShadingVisible(true);
            }
        }
    }, [topShadingVisible, bottomShadingVisible, scrollingElement]);

    // Callback to handle facet scroll events. This function serves as an event handler so a
    // reference to the scrollable element gets passed as a parameter, but we ignore it because
    // `handleScrollShading` uses the `scrollingElement` ref instead so that it runs when the
    // filtered list height changes.
    const handleScroll = () => {
        handleScrollShading();
    };

    // Reset shading after facet region is expanded
    React.useEffect(() => {
        if (isExpanded) {
            handleScrollShading();
        }
    }, [isExpanded, handleScrollShading]);

    // Callback to force reevaulation of scroll shading, normally caused by typing something into
    // the typeahead buffer which can cause the height of the facet to change. This also gets
    // called on component mount to set the initial top and bottom shading state. Also set
    // `initialState` false so we can render complete typeahead facets.
    React.useEffect(() => {
        handleScrollShading();
        setInitialState(false);
    }, [handleScrollShading, facet, typeaheadTerm]);

    // Callback to handle typeahead input events.
    const handleTypeAhead = (event) => {
        setTypeaheadTerm(event.target.value);
    };

    return (
        <div className="facet">
            <div
                className="facet__expander--header"
                tabIndex="0"
                role="button"
                aria-label={facet.field}
                aria-pressed={isExpanded}
                onClick={e => handleExpanderClick(e, isExpanded, facet.field)}
                onKeyDown={e => handleKeyDown(e, isExpanded, facet.field)}
            >
                <TitleComponent facet={facet} results={results} mode={mode} pathname={pathname} queryString={queryString} />
                {isExpandable ? <i className={`facet-chevron icon icon-chevron-${isExpanded ? 'up' : 'down'}`} /> : null}
            </div>
            <SelectedFilters facet={facet} selectedTerms={relevantFilters} />
            <div className={`${disabledCss(relevantFilters) ? 'facet-list-disabled' : ''}`}>
                <div className={`facet-content facet-${(isExpanded || !isExpandable) ? 'open' : 'close'}`}>
                    {facet.type === 'typeahead' ? <Typeahead typeaheadTerm={typeaheadTerm} facet={facet} handleTypeAhead={handleTypeAhead} /> : null}
                    <div className={`facet__content${facet.type === 'typeahead' ? ' facet__content--typeahead' : ''}`}>
                        <ul onScroll={handleScroll} ref={scrollingElement}>
                            {(filteredTerms.length === 0) ?
                                <div className="searcherror">
                                    Try a different search term for results.
                                </div>
                            :
                                <React.Fragment>
                                    <FacetTerms
                                        facet={facet}
                                        results={results}
                                        mode={mode}
                                        relevantFilters={relevantFilters}
                                        pathname={pathname}
                                        queryString={queryString}
                                        filteredTerms={filteredTerms}
                                        onFilter={onFilter}
                                        allowNegation={allowNegation}
                                    />
                                    <div className={`top-shading${topShadingVisible ? '' : ' hide-shading'}`} />
                                    <div className={`bottom-shading${bottomShadingVisible ? '' : ' hide-shading'}`} />
                                </React.Fragment>
                            }
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
};

DefaultFacet.propTypes = {
    /** Relevant `facet` object from `facets` array in `results` */
    facet: PropTypes.object.isRequired,
    /** Complete search-results object */
    results: PropTypes.object.isRequired,
    /** Facet display mode */
    mode: PropTypes.string,
    /** Filters relevant to the current facet */
    relevantFilters: PropTypes.array.isRequired,
    /** Search results path without query-string portion */
    pathname: PropTypes.string.isRequired,
    /** Query-string portion of current URL without initial ? */
    queryString: PropTypes.string,
    /** Special facet-term click handler for edit forms */
    onFilter: PropTypes.func,
    /** True to display negation control */
    allowNegation: PropTypes.bool,
    /** True if facet is to be expanded */
    isExpanded: PropTypes.bool,
    /** Expand or collapse facet */
    handleExpanderClick: PropTypes.func,
    /** Handles key-press and toggling facet */
    handleKeyDown: PropTypes.func,
    /** True if expandable, false otherwise */
    isExpandable: PropTypes.bool,
};

DefaultFacet.defaultProps = {
    mode: '',
    queryString: '',
    onFilter: null,
    allowNegation: true,
    isExpanded: false,
    handleExpanderClick: () => {},
    handleKeyDown: () => {},
    isExpandable: true,
};
