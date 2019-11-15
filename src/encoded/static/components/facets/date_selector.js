import React from 'react';
import PropTypes from 'prop-types';
import dayjs from 'dayjs';
import FacetRegistry from './registry';


const allMonths = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'];

class DateSelectorFacet extends React.Component {
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
            activeFacet: 'date_released', // for toggle, either 'date_released' or 'date_submitted'
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
        this.setActiveFacetParameters(true);
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

        if (((activeFacet.terms.length > 0) && activeFacet.terms.some(term => term.doc_count)) || (field.charAt(field.length - 1) === '!')) {
            return (
                <div className={`facet date-selector-facet ${facet.field === 'date_released' ? 'display-date-selector' : ''}`}>
                    <h5>Date range selection</h5>
                    {existingFilter.length > 0 ?
                        <div className="selected-date-range">
                            <div>Selected range: </div>
                            {existingFilter.map(filter =>
                                <div key={filter.term}>{dateRangeString}</div>
                            )}
                        </div>
                    : null}

                    <div className="date-selector-toggle-wrapper">
                        <div className="date-selector-toggle"><input
                            type="radio"
                            name="released"
                            value="released"
                            checked={this.state.activeFacet === 'date_released'}
                            onChange={this.toggleDateFacet}
                        />Released
                        </div>
                        <div className="date-selector-toggle"><input
                            type="radio"
                            name="submitted"
                            value="submitted"
                            checked={this.state.activeFacet === 'date_submitted'}
                            onChange={this.toggleDateFacet}
                        />Submitted
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

DateSelectorFacet.propTypes = {
    /** Relevant `facet` object in `facets` array in `results` */
    facet: PropTypes.object.isRequired,
    /** Complete search-results object */
    results: PropTypes.object.isRequired,
    /** Query-string portion of current URL without initial ? */
    queryString: PropTypes.string.isRequired,
};

DateSelectorFacet.contextTypes = {
    navigate: PropTypes.func,
};


FacetRegistry.Facet.register('date_released', DateSelectorFacet);
FacetRegistry.Facet.register('date_submitted', null);
