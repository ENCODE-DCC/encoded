import React from 'react';
import PropTypes from 'prop-types';
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

    return (
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
    <div className="facet-term__text">{term.key}</div>
);

DefaultTermName.propTypes = {
    /** facet.terms object for the term we're rendering */
    term: PropTypes.object.isRequired,
};


/**
 * Default component to render a single term within the default facet.
 */
export const DefaultTerm = ({ term, facet, results, mode, relevantFilters, pathname, queryString, onFilter }) => {
    const TermNameComponent = FacetRegistry.TermName.lookup(facet.field);
    let href;
    let negHref;
    let negated = false;

    // Find the search-results filter matching this term, which if found indicates this term is
    // selected; also check if the selection is for negation.
    const selectedTermFilter = relevantFilters.find((filter) => {
        let filterField = filter.field;
        const negatedFilter = filterField.slice(-1) === '!';
        if (negatedFilter) {
            filterField = filterField.slice(0, -1);
        }
        const selected = filterField === facet.field && filter.term === term.key.toString();
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
        query.addKeyValue(facet.field, term.key);
        href = `?${query.format()}`;

        // Also build the negation URI.
        negQuery.addKeyValue(facet.field, term.key, true);
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
            <a href={href} onClick={href ? onFilter : null} className={`facet-term__item${termCss}`}>
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
                {negated ? null : <div className="facet-term__count">{term.doc_count}</div>}
                {(selectedTermFilter || negated) ? null : <div className="facet-term__bar" style={barStyle} />}
            </a>
            <div className="facet-term__negator">
                {selectedTermFilter ? null : <a href={negHref} title={'Do not include items with this term'}><i className="icon icon-minus-circle" /></a>}
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
    /** Special search-result click handler */
    onFilter: PropTypes.func,
};

DefaultTerm.defaultProps = {
    mode: '',
    queryString: '',
    onFilter: null,
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
const SelectedFilters = ({ selectedTerms }) => (
    <React.Fragment>
        {(selectedTerms.length > 0) ?
            <div className="filter-container">
                <div className="filter-hed">Selected filters:</div>
                {selectedTerms.map(filter =>
                    <a href={filter.remove} key={filter.term} className={(filter.field.indexOf('!') !== -1) ? 'negation-filter' : ''}>
                        <div className="filter-link"><i className="icon icon-times-circle" /> {filter.term}</div>
                    </a>
                )}
            </div>
        : null}
    </React.Fragment>
);

SelectedFilters.propTypes = {
    /** Search-result filters relevant to the facet */
    selectedTerms: PropTypes.array.isRequired,
};


/**
 * Render the terms within a facet, calling the currently registered term-rendering component.
 * This component gets memoized so it only renders when the facet data unequivocally changes,
 * avoiding needless rerenders when a different facet needs to rerender.
 */
const FacetTerms = React.memo(({ facet, results, mode, relevantFilters, pathname, queryString, filteredTerms, onFilter }) => {
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
    /** Special search-result click handler */
    onFilter: PropTypes.func,
};

FacetTerms.defaultProps = {
    mode: '',
    queryString: '',
    onFilter: null,
};


/**
 * Display the default text facet with optional typeahead field.
 */
export const DefaultFacet = ({ facet, results, mode, relevantFilters, pathname, queryString, onFilter }) => {
    const [topShadingVisible, setTopShadingVisible] = React.useState(false);
    const [bottomShadingVisible, setBottomShadingVisible] = React.useState(false);
    const [typeaheadTerm, setTypeaheadTerm] = React.useState('');
    const scrollingElement = React.useRef(null);

    // Retrieve reference to the registered facet title component for this facet.
    const TitleComponent = FacetRegistry.Title.lookup(facet.field);

    // Filter out terms with a zero doc_count, as seen in region-search results.
    const significantTerms = facet.terms.filter(term => term.doc_count > 0);

    // Sort numerical terms by value not by frequency
    // This should ultimately be accomplished in the back end, but the front end fix is much simpler so we are starting with that
    // We have to check the full list for now (until schema change) because some lists contain both numerical and string terms ('Encyclopedia version' under Annotations) and we do not want to sort those by value
    const numericalTest = a => !isNaN(a.key);
    // For straightforward numerical facets, just sort by value
    const processedTerms = significantTerms.every(numericalTest) ? _.sortBy(significantTerms, obj => obj.key) : significantTerms;

    // Filter the list of facet terms to those allowed by the optional typeahead field. Memoize the
    // resulting list to avoid needlessly rerendering the facet-term list that can get very long.
    const filteredTerms = React.useMemo(() => (
        facet.type === 'typeahead' ?
            processedTerms.filter(
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
            )
        : processedTerms
    ), [processedTerms, facet.type, typeaheadTerm]);

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

    // Callback to force reevaulation of scroll shading *after* a DOM change completes (so
    // useLayoutEffect instead of the more usual useEffect), normally caused by typing something
    // into the typeahead buffer which can cause the height of the facet to change. This also gets
    // called on component mount to set the initial top and bottom shading state.
    React.useLayoutEffect(() => {
        handleScrollShading();
    });

    // Callback to handle typeahead input events.
    const handleTypeAhead = (event) => {
        setTypeaheadTerm(event.target.value);
    };

    return (
        <div className="facet">
            <TitleComponent facet={facet} results={results} mode={mode} pathname={pathname} queryString={queryString} />
            <SelectedFilters selectedTerms={relevantFilters} />
            {facet.type === 'typeahead' ? <Typeahead typeaheadTerm={typeaheadTerm} facet={facet} handleTypeAhead={handleTypeAhead} /> : null}
            <div className={`facet__content${facet.type === 'typeahead' ? ' facet__content--typeahead' : ''}`}>
                <ul onScroll={handleScroll} ref={scrollingElement}>
                    <FacetTerms
                        facet={facet}
                        results={results}
                        mode={mode}
                        relevantFilters={relevantFilters}
                        pathname={pathname}
                        queryString={queryString}
                        filteredTerms={filteredTerms}
                        onFilter={onFilter}
                    />
                </ul>
                <div className={`top-shading${topShadingVisible ? '' : ' hide-shading'}`} />
                <div className={`bottom-shading${bottomShadingVisible ? '' : ' hide-shading'}`} />
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
    /** Special search-result click handler */
    onFilter: PropTypes.func,
};

DefaultFacet.defaultProps = {
    mode: '',
    queryString: '',
    onFilter: null,
};
