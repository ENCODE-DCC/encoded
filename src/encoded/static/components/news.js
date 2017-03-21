import React from 'react';
import moment from 'moment';
import querystring from 'querystring';
import _ from 'underscore';
import url from 'url';
import globals from './globals';
import { Panel, PanelBody } from '../libs/bootstrap/panel';


// Display a news preview item from a search result @graph object.
const NewsPreviewItem = React.createClass({
    propTypes: {
        item: React.PropTypes.object, // News search result object to display
    },

    render: function () {
        const { item } = this.props;
        return (
            <div key={item['@id']} className="news-listing-item">
                <h3>{item.title}</h3>
                <h4>{moment.utc(item.date_created).format('MMMM D, YYYY')}</h4>
                <div className="news-excerpt">{item.news_excerpt}</div>
                <div className="news-listing-readmore">
                    <a className="btn btn-info btn-sm" href={item['@id']} title={`View news post for ${item.title}`} key={item['@id']}>Read more</a>
                </div>
            </div>
        );
    },
});


// Display a list of news preview items from search results.
const NewsPreviews = React.createClass({
    propTypes: {
        items: React.PropTypes.array, // Items from search result @graph
    },

    render: function () {
        const { items } = this.props;
        if (items && items.length) {
            return (
                <div className="news-listing">
                    {items.map(item => (
                        <NewsPreviewItem key={item['@id']} item={item} />
                    ))}
                </div>
            );
        }
        return <div className="news-empty">No news available at this time</div>;
    },
});
export default NewsPreviews;


// Default news facet-rendering component for any type of facet not specifically registered to render
// in its own component, so the vast majority of news facets use this component.
const DefaultFacet = React.createClass({
    propTypes: {
        facet: React.PropTypes.object.isRequired, // One facet from search results
        baseUri: React.PropTypes.string.isRequired, // Current URI and query string
        searchFilters: React.PropTypes.object.isRequired, // Search-result filter object; see <NewsFacets />
    },

    render: function () {
        const { facet, baseUri, searchFilters } = this.props;

        // Get the query string portion of the base URI, if any. This tells us if we need to append
        // new query string parameters with a '?' or a '&'.
        const query = url.parse(baseUri).search;

        return (
            <div key={facet.field} className="news-facet">
                <div className="news-facet__title">
                    {facet.title}
                </div>
                <ul className="news-facet__items">
                    {facet.nonEmptyTerms.map((term) => {
                        // Make the facet term link either the current URI appended with
                        // the facet field and term, or from any matching filter’s `remove`
                        // URI. Have to parse the `remove` URI to trim any vestiges of add
                        // query string.
                        let termFilter = searchFilters[facet.field] && searchFilters[facet.field][term.key] && searchFilters[facet.field][term.key].remove;
                        if (termFilter && termFilter[termFilter.length - 1] === '?') {
                            termFilter = termFilter.slice(0, -1);
                        }
                        const qs = globals.encodedURIComponent(`${facet.field}=${term.key}`);
                        const termHref = termFilter || `${baseUri}${query ? '&' : '?'}${qs}`;

                        return (
                            <li key={term.key} className="news-facet__item">
                                <a href={termHref} className={termFilter ? 'selected' : ''}>
                                    <span className="news-facet__item-title">
                                        {term.key}&nbsp;
                                    </span>
                                    <span className="news-facet__item-count">
                                        ({term.doc_count})
                                    </span>
                                </a>
                            </li>
                        );
                    })}
                </ul>
            </div>
        );
    },
});

// Register this component to be the fallback facet-display component used when no other facet
// field has been registered to specifically render that kind of facet.
globals.facet_view.register(DefaultFacet, '');
globals.facet_view.fallback = () => DefaultFacet;


// Special news facet-rendering component to render facets with facet.field==='month_released'.
const DateFacet = React.createClass({
    propTypes: {
        facet: React.PropTypes.object.isRequired, // One facet from search results
        baseUri: React.PropTypes.string.isRequired, // Current URI and query string
        searchFilters: React.PropTypes.object.isRequired, // Search-result filter object; see <NewsFacets />
    },

    render: function () {
        const { facet, baseUri, searchFilters } = this.props;
        let allYearsUri = '';
        let inMonthUri = '';
        let queryParms = {};
        let yearsSelected;
        let selectedMonthYears = []; // Array of years for which a month is selected

        // Generate the href for the "All years" facet term if we need one. This involves removing
        // all (normally one) year_released parameters from the query string. Start by getting the
        // query string portion of the base URI, if any.
        const baseUriComps = url.parse(baseUri);
        if (baseUriComps.search) {
            // A query string exists. Parse it to see if it has one or more year_released
            // parameters. If it does, delete it. Have to strip the first character off the query
            // string because it's always a question mark which querystring.parse can't handle.
            queryParms = querystring.parse(baseUriComps.search.substring(1));

            // Generate the "All years" facet term link, but only if one or more years is currently
            // selected.
            if (queryParms.year_released) {
                // At least one "year_released" query string parameter found. First get what their
                // values are so we can display it in the facet title.
                yearsSelected = (typeof queryParms.year_released === 'string') ? [queryParms.year_released] : queryParms.year_released;

                // Now delete the year_released query string parameters and generate an href
                // without them to use to clear the year while leaving other query string
                // parameters intact. Use this for the 'All years' static facet item.
                const allYearsQueries = _(queryParms).omit('year_released');
                const allYearsQS = querystring.stringify(allYearsQueries);
                allYearsUri = `${baseUriComps.pathname}${allYearsQS ? `?${allYearsQS}` : ''}`;
            }

            // Now calculate a URI with month_released removed, for individual month facet term
            // hrefs while another individual month is selected.
            if (queryParms.month_released) {
                // One of more month_released in the given query string. Generate a new query
                // without any months selected. When we render the link, we'll just add the current
                // facet term month.
                const monthRemovedQueries = _(queryParms).omit('month_released');
                inMonthUri = `${baseUriComps.pathname}?${querystring.stringify(monthRemovedQueries)}`;

                // If at least one month is selected, we'll only show "All {year}" facets for those
                // selected months. So make an array of years that cover the currently selected
                // months. Of course through the UI only one month_released can occur -- this
                // covers the case where the user directly manipulated the URL.
                if (typeof queryParms.month_released === 'string') {
                    // Only one month selected. Just get its year.
                    selectedMonthYears = [queryParms.month_released.substr(0, 4)];
                } else {
                    // Multiple months selected in an array, so get all their years.
                    selectedMonthYears = queryParms.month_released.map(monthReleased => monthReleased.substr(0, 4));
                }
            } else {
                inMonthUri = baseUri;
            }
        }
        // If no baseUriComps.search exists, then no query string exists.

        // If >= 12 (a year) of facets to display, set a flag to know that we need to coalesce
        // older months into years. Don't coalesce if a year is currently selected.
        const coalesce = !yearsSelected && facet.nonEmptyTerms.length > 12;

        // Generate lists of facet terms to render based on whether we have to coalesce past years
        // or not.
        let trimmedMonthTerms = [];
        let coYearGroups = {};
        let inYearGroups = {};
        let years = [];
        if (coalesce) {
            // We have enough months in a facet to justify coalescing past years. First make a
            // YYYY-MM string for 11 months before now for something to compare against.
            const earliestMonth = moment().subtract(11, 'months').format('YYYY-MM');

            // Break terms into two keys in an object: one with the key `in` that's an array of all
            // terms that get rendered as individual months within the past 11 months, and one with
            // the key `co` with all the terms that need to be coalesced into years.
            const trimmedMonthGroups = _(facet.nonEmptyTerms).groupBy(term => ((term.key >= earliestMonth) ? 'in' : 'co'));

            // Get the terms from the past 11 months we individually render.
            trimmedMonthTerms = trimmedMonthGroups.in;

            // Group the coalesced terms into an object keyed by year, and also make a reverse-
            // sorted list of years. Also group the individual terms in case we need to sum up
            // overlapping years.
            coYearGroups = _(trimmedMonthGroups.co).groupBy(term => term.key.substr(0, 4));
            inYearGroups = _(trimmedMonthGroups.in).groupBy(term => term.key.substr(0, 4));
            years = Object.keys(coYearGroups).sort((a, b) => ((a < b) ? 1 : (b < a ? -1 : 0)));

            // If at least one individual month is selected, only include years for those selected
            // months.
            if (selectedMonthYears.length) {
                years = _(years).filter(year => selectedMonthYears.indexOf(year) !== -1);
            }
        } else {
            // Not enough months to display in a facet to justify coalescing past years. Just sort
            // and display all available facet terms.
            trimmedMonthTerms = facet.nonEmptyTerms;
        }

        // Sort the individual month terms by date.
        trimmedMonthTerms = trimmedMonthTerms.sort((a, b) => ((a.key < b.key) ? 1 : (b.key < a.key ? -1 : 0)));

        return (
            <div key={facet.field} className="news-facet">
                <div className="news-facet__title">
                    Months
                    {yearsSelected ? <span> for {yearsSelected.join(', ')}</span> : null}
                </div>
                <ul className="news-facet__items">
                    {trimmedMonthTerms.map((term) => {
                        // Loop to display the individual month terms. Make the facet term link
                        // either the current URI appended with the facet field and term, or from
                        // any matching filter’s `remove` URI. Have to parse the `remove` URI to
                        // trim any vestiges of add query string.
                        let termFilter = searchFilters[facet.field] && searchFilters[facet.field][term.key] && searchFilters[facet.field][term.key].remove;
                        if (termFilter && termFilter[termFilter.length - 1] === '?') {
                            termFilter = termFilter.slice(0, -1);
                        }

                        const qs = globals.encodedURIComponent(`${facet.field}=${term.key}`);
                        const termHref = termFilter || `${inMonthUri}${baseUriComps.search ? '&' : '?'}${qs}`;

                        return (
                            <li key={term.key} className="news-facet__item">
                                <a href={termHref} className={termFilter ? 'selected' : ''}>
                                    <span className="news-facet__item-title">
                                        {term.key}&nbsp;
                                    </span>
                                    <span className="news-facet__item-count">
                                        ({term.doc_count})
                                    </span>
                                </a>
                            </li>
                        );
                    })}

                    {years.map((year) => {
                        // Loop to display the coalesced year terms. Sum up the doc_counts for the
                        // year being rendered. If we have overlapping term years, we have to add
                        // those to the total too.
                        let yearTotal = coYearGroups[year].reduce((total, term) => total + term.doc_count, 0);
                        if (inYearGroups[year]) {
                            yearTotal += inYearGroups[year].reduce((total, term) => total + term.doc_count, 0);
                        }

                        // Calculate the href. Works differently for coalesced facet terms because
                        // only one can be selected at a time.
                        const qs = globals.encodedURIComponent(`year_released=${year}`);
                        const termHref = `${baseUri}${baseUriComps.search ? '&' : '?'}${qs}`;

                        return (
                            <li key={year} className="news-facet__item">
                                <a href={termHref}>
                                    <span className="news-facet__item-title">
                                        All {year}&nbsp;
                                    </span>
                                    <span className="news-facet__item-count">
                                        ({yearTotal})
                                    </span>
                                </a>
                            </li>
                        );
                    })}

                    {yearsSelected ?
                        <li className="news-facet__item">
                            <a href={allYearsUri}>
                                <span className="news-facet__item-title">All years</span>
                            </a>
                        </li>
                    : null}
                </ul>
            </div>
        );
    },
});

globals.facet_view.register(DateFacet, 'month_released');


// Display the news facets.
const NewsFacets = React.createClass({
    propTypes: {
        facets: React.PropTypes.array.isRequired, // Array of facets, each containing an array of facet items
        filters: React.PropTypes.array.isRequired, // Array of filters from the search results
        baseUri: React.PropTypes.string.isRequired, // Current URI and query string
    },

    render: function () {
        const { facets, filters, baseUri } = this.props;

        // Filter out facets that have all-zero term counts. Also attach a filtered list of non-
        // empty terms to each facet so that we only display those.
        const nonEmptyFacets = facets.filter((facet) => {
            // Filter out terms with zero counts.
            const nonEmptyTerms = facet.terms.filter(term => term.doc_count);

            // Attach the filtered term list to the facet, and return whether there were any terms
            // left after filtering. Also set @type of the facet so that we can use the view
            // registry lookup.
            facet.nonEmptyTerms = nonEmptyTerms;
            facet['@type'] = [facet.field];
            return !!nonEmptyTerms.length;
        });

        // Now generate an object representing the search-result filters that's dereferenceable
        // as filters[facet.field][term.key] to avoid doing a search of the filters array for each
        // inner iteration of the facet display loop. If we have no query string, filters can have
        // zero elements in it.
        const searchFilters = {};
        if (filters.length) {
            filters.forEach((filter) => {
                if (!searchFilters[filter.field]) {
                    // A key for the filter's field doesn't exist, so make it an empty object we can add to
                    // on the next line.
                    searchFilters[filter.field] = {};
                }
                searchFilters[filter.field][filter.term] = filter;
            });
        }

        return (
            <div className="news-facets">
                {nonEmptyFacets.map((facet) => {
                    const FacetView = globals.facet_view.lookup(facet);

                    return <FacetView facet={facet} baseUri={baseUri} searchFilters={searchFilters} />;
                })}
            </div>
        );
    },
});


// Rendering component for the stand-alone news preview page.
const News = React.createClass({
    propTypes: {
        context: React.PropTypes.object, // Search results
    },

    render: function () {
        const { context } = this.props;
        const items = context['@graph'];
        const facets = context.facets;

        // Only display the full news page if the current query string and data give us news items
        // to display.
        if (context['@graph'].length && facets) {
            return (
                <Panel>
                    <PanelBody>
                        <div className="news-page">
                            <div className="news-page__previews">
                                <div className="news-page__previews-title">
                                    <h1>News</h1>
                                </div>
                                <NewsPreviews items={items} />
                            </div>
                            <div className="news-page__facets">
                                <NewsFacets facets={facets} filters={context.filters} baseUri={context['@id']} />
                            </div>
                        </div>
                    </PanelBody>
                </Panel>
            );
        }

        // Either the query string or the current data aren't giving us any news items to display.
        // Just show a message.
        return (
            <Panel>
                <h2>No news items to display</h2>
                <a href="/news/">Latest ENCODE News</a>
            </Panel>
        );
    },
});

globals.content_views.register(News, 'News');
