import React from 'react';
import * as globals from './globals';
import {InputSuggest} from './home';


const topHitsUrl = '/top-hits-raw/';


export class TopHitsSearch extends React.Component {
    constructor() {
        super();
        this.state = {
            currentSearchTerm: '',
            suggestedSearchTerms: [],
        };
        this.lastSearchTerm = '';
        this.throttlingTimer = null;
        this.handleTimerExpiry = this.handleTimerExpiry.bind(this);
        this.startDelayTimer = this.startDelayTimer.bind(this);
        this.searchTermChange = this.searchTermChange.bind(this);
        this.searchTermClick = this.searchTermClick.bind(this);
        this.termSelectHandler = this.termSelectHandler.bind(this);
        this.inputBlur = this.inputBlur.bind(this);
    }

    componentWillUnmount() {
        if (this.throttlingTimer) {
            clearTimeout(this.throttlingTimer);
            this.throttlingTimer = null;
        }
    }

    parseHit(hit) {
        const embedded = hit._source.embedded;
        return `${embedded.accession || embedded["@id"]} - ${embedded.description || embedded.title || embedded.biosample_summary}`
    }

    parseHits(hits, type) {
        return hits.map(
            hit => `${this.parseHit(hit)} - ${type}`
        );
    }

    parseResults(results) {
        let parsedResults = results.aggregations.types.types.buckets.map(
            result => this.parseHits(result.top_hits.hits.hits, result.key)
        );
        return parsedResults.flat();
    }

    fetchTopHits(newSearchTerm) {
        let topHitsUrlWithParams = (
            `${topHitsUrl}?searchTerm=${newSearchTerm}&field=description&field=accession&field=title&field=biosample_summary&format=json`
        );
        return fetch(
            topHitsUrlWithParams,
            {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            }
        ).then(
            response => (response.ok ? response.json() : [])
        ).then(
            results => {
                return this.parseResults(results).flat();
            }
        );
    }

    updateTopHits(newSearchTerm) {
        this.startDelayTimer();
        this.lastSearchTerm = newSearchTerm;
        this.fetchTopHits(newSearchTerm).then(
            results => this.setState(
                {suggestedSearchTerms: results}
            )
        );
    }

    handleTimerExpiry() {
        this.throttlingTimer = null;
        if (this.state.currentSearchTerm !== this.lastSearchTerm) {
            this.updateTopHits(this.state.currentSearchTerm);
        }
    }

    startDelayTimer() {
        this.throttlingTimer = setTimeout(this.handleTimerExpiry, 1000);
    }

    searchTermChange(newSearchTerm) {
        if (newSearchTerm !== this.currentSearchTerm) {
            this.setState({currentSearchTerm: newSearchTerm});
            if (!this.throttlingTimer) {
                this.updateTopHits(newSearchTerm);
            }
        }
    }

    termSelectHandler(term) {
        this.setState({currentSearchTerm: term, suggestedSearchTerms: []});
    }

    clearTerms () {
        this.setState({suggestedSearchTerms: []});
    }

    searchTermClick() {
        this.clearTerms();
    }

    inputBlur() {
        this.clearTerms();
    }

    render() {
        const context = this.props.context;
        const isSearchDisabled = this.state.currentSearchTerm.length === 0;
        return (
            <div className="site-search__screen">
                <form>
                    <fieldset>
                        <legend className="sr-only">Top hits search</legend>
                        <div className="site-search__input">
                            <label htmlFor="top-hits-search" id="top-hits-search-label">
                                Search for top hits by type
                            </label>
                            <InputSuggest
                                value={this.state.currentSearchTerm}
                                items={this.state.suggestedSearchTerms}
                                inputId="top-hits-search"
                                labelledById="top-hits-search-label"
                                inputChangeHandler={this.searchTermChange}
                                inputClickHandler={this.searchTermClick}
                                inputBlurHandler={this.inputBlur}
                                itemSelectHandler={this.termSelectHandler}
                            />
                        </div>
                        <div className="site-search__submit">
                            <a
                                disabled={isSearchDisabled}
                                aria-label="Human GRCh38 search"
                                title="Human GRCh38 search"
                                className="btn btn-info btn-sm site-search__submit-element"
                                role="button"
                                href={`/search/?searchTerm=${this.state.currentSearchTerm}`}
                            >
                                Search<i className="icon icon-search" />
                            </a>
                        </div>
                    </fieldset>
                </form>
            </div>
        );
    }
}


globals.contentViews.register(TopHitsSearch, 'TopHitsSearch');